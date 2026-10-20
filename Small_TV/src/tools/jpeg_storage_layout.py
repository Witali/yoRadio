"""Plan native Small_TV JPEG scratch/cache sectors without modifying flash images."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import struct

PROJECT = Path(__file__).resolve().parents[1]
SECTOR = 4096
FLASH_BYTES = 4 * 1024 * 1024
SETTINGS_BASE = 0x3e7000
ANIMATIONS, WEATHER, STATUS = 5, 18, 4
MEASURED_BACKING_BYTES = 460800


def digest(data):
    """Identify exact packed resources; never infer ownership from FF bytes alone."""
    return hashlib.sha256(data).hexdigest()


def align(value):
    """Reserve complete erase sectors, including each asset's final partial sector."""
    return (value + SECTOR - 1) // SECTOR * SECTOR


def parse_board(text):
    """Read only numeric board constants, rejecting expressions rather than eval-ing C."""
    return {name: int(number, 0) for name, number in re.findall(
        r"^#define\s+(\w+)\s+(0x[0-9a-fA-F]+|[0-9]+)[uUlL]*\s*$", text, re.MULTILINE)}


def parse_partitions(text):
    """Read explicit ESP-IDF offsets/sizes; no guessed auto-offset partitions."""
    result = []
    for row in csv.reader(line for line in text.splitlines() if line.strip() and not line.lstrip().startswith('#')):
        if len(row) < 5:
            raise ValueError('Incomplete partition record')
        name, kind, subtype, offset, size = [value.strip() for value in row[:5]]
        result.append(dict(name=name, kind=kind, subtype=subtype, offset=int(offset, 0), size=int(size, 0)))
    return result


def extents(sectors):
    """Coalesce sorted physical sector addresses without changing logical order."""
    result = []
    for address in sectors:
        if result and result[-1]['offset'] + result[-1]['bytes'] == address:
            result[-1]['bytes'] += SECTOR
        else:
            result.append(dict(offset=address, bytes=SECTOR))
    return result


def make_plan(assets, manifest, board, partitions, backing_bytes=MEASURED_BACKING_BYTES):
    """REQUESTED_CHANGE: reserve scratch plus five cached RGB565 frames safely.

    This is a read-only capacity/ownership proof for the native packed image.
    It is neither a NOR write backend nor permission to erase a factory dump.
    The default backing bound is measured, not a proof of every JPEG layout.
    """
    required = ('LCD_WIDTH', 'LCD_HEIGHT', 'ASSETS_BASE', 'PHOTO_COUNT', 'PHOTO_SLOT_BYTES',
                'ANIMATION_BASE', 'ANIMATION_SLOT_BYTES', 'WEATHER_BASE', 'WEATHER_SLOT_BYTES')
    if any(name not in board for name in required):
        raise ValueError('Missing numeric board constant')
    if (board['LCD_WIDTH'], board['LCD_HEIGHT'], board['PHOTO_COUNT']) != (240, 240, 5):
        raise ValueError('Unsupported board geometry/photo count')
    if any(board[name] <= 0 for name in required) or backing_bytes <= 0:
        raise ValueError('Non-positive board size or backing bound')
    if manifest['sha256'] != digest(assets) or manifest['size'] != len(assets):
        raise ValueError('Packed image hash/size mismatch')
    base = board['ASSETS_BASE']
    if int(manifest['offset'], 0) != base:
        raise ValueError('Asset base mismatch')
    names = {row['name']: row for row in partitions}
    if len(names) != len(partitions) or 'factory' not in names or 'assets' not in names:
        raise ValueError('Missing or duplicate partition')
    previous = 0
    for row in sorted(partitions, key=lambda item: item['offset']):
        if row['offset'] < previous or row['size'] <= 0 or row['offset'] % SECTOR or row['size'] % SECTOR:
            raise ValueError('Overlapping, unaligned or empty partition')
        previous = row['offset'] + row['size']
        if previous > FLASH_BYTES:
            raise ValueError('Partition beyond flash')
    app, media = names['factory'], names['assets']
    app_end = app['offset'] + app['size']
    end = base + len(assets)
    if app['kind'] != 'app' or media['kind'] != 'data' or media['offset'] != base or media['size'] != len(assets) or end != SETTINGS_BASE:
        raise ValueError('Unsupported native partition ownership')
    if app_end > base or any(row['offset'] < base and row['offset'] + row['size'] > app_end
                             for row in partitions if row['name'] not in ('factory', 'assets')):
        raise ValueError('Another partition owns the application/media gap')
    photo_end = base + board['PHOTO_COUNT'] * board['PHOTO_SLOT_BYTES']
    animation_base, animation_slot = board['ANIMATION_BASE'], board['ANIMATION_SLOT_BYTES']
    weather_base, icon_slot = board['WEATHER_BASE'], board['WEATHER_SLOT_BYTES']
    if photo_end != animation_base or animation_base + ANIMATIONS * animation_slot != weather_base:
        raise ValueError('Unexpected photo/animation bank boundary')
    if any(value % SECTOR for value in (base, photo_end, animation_slot, weather_base)):
        raise ValueError('Unaligned photo/animation bank')
    expected = {base + index * board['PHOTO_SLOT_BYTES']: board['PHOTO_SLOT_BYTES']
                for index in range(board['PHOTO_COUNT'])}
    expected.update({animation_base + index * animation_slot: animation_slot for index in range(ANIMATIONS)})
    expected.update({weather_base + index * icon_slot: icon_slot for index in range(WEATHER + STATUS)})
    records = {}
    for record in manifest['records']:
        start, size = int(record['offset'], 0), record['size']
        if start not in expected or start in records or size <= 0 or size > expected[start] or start + expected[start] > end:
            raise ValueError('Missing/duplicate/oversized or unexpected resource record')
        data = assets[start - base:start - base + size]
        if digest(data) != record['sha256']:
            raise ValueError('Resource payload hash mismatch')
        records[start] = record
    if set(records) != set(expected):
        raise ValueError('Incomplete resource manifest')
    candidates = [(app_end, base, 'application-media gap')]
    protected = [(0, app_end, 'boot/NVS/application'), (base, photo_end, 'all five full upload slots')]
    for index in range(ANIMATIONS):
        start = animation_base + index * animation_slot
        record = records[start]
        data = assets[start - base:start - base + record['size']]
        if len(data) < 1024 or data[:3] != b'GIF' or struct.unpack_from('<I', data, 3)[0] != len(data):
            raise ValueError('Animation container length/header mismatch')
        for frame in range(126):
            length, offset = struct.unpack_from('<II', data, 11 + 8 * frame)
            if length and (offset < 1024 or offset > len(data) or length > len(data) - offset):
                raise ValueError('Animation frame exceeds protected payload')
        used_end = align(start + len(data))
        if used_end > start + animation_slot:
            raise ValueError('Animation owns its entire final sector')
        protected.append((start, used_end, f'animation {index} payload and final erase sector'))
        candidates.append((used_end, start + animation_slot, f'animation {index} unused tail'))
    icon_end = align(weather_base + (WEATHER + STATUS) * icon_slot)
    if icon_end > end:
        raise ValueError('Icon slots exceed media partition')
    protected += [(weather_base, icon_end, 'full weather/status slots'), (end, FLASH_BYTES, 'settings and flash tail')]
    candidates.append((icon_end, end, 'unused media tail'))
    free = []
    for start, stop, label in candidates:
        if start > stop or start % SECTOR or stop % SECTOR:
            raise ValueError('Candidate erase boundary is invalid')
        if start >= base and assets[start - base:stop - base] != b'\xff' * (stop - start):
            raise ValueError('Candidate resource tail contains data')
        free.extend(range(start, stop, SECTOR))
    free.sort()
    if len(free) != len(set(free)) or any(a < stop and start < a + SECTOR for a in free for start, stop, _ in protected):
        raise ValueError('Candidate overlaps owned bytes')
    cache_bytes = board['LCD_WIDTH'] * board['LCD_HEIGHT'] * 2
    backing_sectors = align(backing_bytes) // SECTOR
    cache_sectors = align(cache_bytes) // SECTOR
    required_sectors = backing_sectors + board['PHOTO_COUNT'] * cache_sectors + 2
    if len(free) < required_sectors:
        raise ValueError(f'Insufficient safe space: {len(free)} sectors, need {required_sectors}')
    cursor = 0

    def allocate(count, logical_bytes):
        """Assign a disjoint logical store, retaining its possibly sparse mapping."""
        nonlocal cursor
        selected = free[cursor:cursor + count]
        cursor += count
        return dict(logical_bytes=logical_bytes, sector_count=count, extents=extents(selected))

    plan = dict(schema_version=1, status='native_image_capacity_planned', all_functionality_verified=False,
                scope='Read-only native image allocation only. Not a flash backend, wear/power-loss acceptance, factory-dump layout or universal JPEG backing bound.',
                image_sha256=digest(assets), sector_bytes=SECTOR, available_sectors=len(free),
                allocated_sectors=required_sectors,
                candidate_extents=[dict(offset=start, bytes=stop - start, reason=label) for start, stop, label in candidates if start != stop],
                protected_extents=[dict(offset=start, bytes=stop - start, reason=label) for start, stop, label in protected],
                backing=allocate(backing_sectors, backing_bytes), metadata=allocate(2, SECTOR * 2),
                caches=[allocate(cache_sectors, cache_bytes) for _ in range(board['PHOTO_COUNT'])],
                spare_extents=extents(free[required_sectors:]), spare_sectors=len(free) - required_sectors,
                required_remaining=['NOR sector read/modify/erase/program and fault tests',
                                    'atomic cache publication and cold recovery', 'measure erase counts and avoid periodic decode writes',
                                    'invalidate cache on source/codec/layout changes', 'expanded subsampling backing bound',
                                    'production link/total heap/stack and HTTP/LCD/full/soak'])
    plan['layout_id'] = digest(json.dumps(plan, sort_keys=True, separators=(',', ':')).encode())
    return plan


def main():
    """Read sanitized build artifacts and exclusively create a plan JSON, never flash."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir', type=Path, required=True)
    parser.add_argument('--board', type=Path, default=PROJECT / 'app/include/board.h')
    parser.add_argument('--partitions', type=Path, default=PROJECT / 'partitions.csv')
    parser.add_argument('--backing-bytes', type=int, default=MEASURED_BACKING_BYTES)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assets = args.assets_dir / 'assets.bin'
    manifest = args.assets_dir / 'assets-manifest.json'
    plan = make_plan(assets.read_bytes(), json.loads(manifest.read_text()), parse_board(args.board.read_text()),
                     parse_partitions(args.partitions.read_text()), args.backing_bytes)
    plan['inputs_sha256'] = {str(path.resolve()): digest(path.read_bytes())
                            for path in (assets, manifest, args.board, args.partitions, Path(__file__))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(plan, indent=2) + '\n')
    print(f"Native plan: {plan['allocated_sectors']}/{plan['available_sectors']} sectors; {plan['spare_sectors']} spare. No image modified.")


if __name__ == '__main__':
    main()
