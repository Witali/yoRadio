"""Read-only partition/geometry/magic audit of the two preserved replay inputs."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.build/cyd-production-boot-replay-20261030-filesystem-audit-01.json'
need_new = not OUT.exists()
assert need_new


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


result = dict(source_or_image_modified=False, filesystem_generated=False, format_requested=False,
              firmware_or_nvs_imported=False, native_process_started=False, profiles={})
for profile, folder in (('pdm', 'gvp'), ('disabled-pdm', 'goff')):
    build = ROOT / '.build/srx01' / folder
    data = (build / 'spiffs.bin').read_bytes()
    table = (build / 'partition_table/partition-table.bin').read_bytes()
    partitions = []
    for position in range(0, len(table), 32):
        row = table[position:position + 32]
        if row[:2] == b'\xaa\x50':
            _, typ, subtype, offset, size, label, flags = struct.unpack('<HBBII16sI', row)
            partitions.append(dict(type=typ, subtype=subtype, offset=offset, size=size,
                                   label=label.rstrip(b'\0').decode('ascii'), flags=flags))
    selected = next(row for row in partitions if row['label'] == 'spiffs')
    config = (build / 'sdkconfig').read_text('utf-8')
    values = {}
    for name in ('PAGE_SIZE', 'OBJ_NAME_LEN', 'META_LENGTH', 'USE_MAGIC', 'USE_MAGIC_LENGTH'):
        match = re.search(r'^CONFIG_SPIFFS_' + name + r'=(.+)$', config, re.M)
        assert match
        values[name.lower()] = int(match.group(1)) if match.group(1).isdecimal() else match.group(1) == 'y'
    assert values == dict(page_size=256, obj_name_len=32, meta_length=0, use_magic=True, use_magic_length=True)
    block_size, block_count = 4096, len(data) // 4096
    magics = []
    for block in range(block_count):
        offset = block * block_size + values['page_size'] - 4
        expected = (0x20140529 ^ values['page_size'] ^ (block_count - block)) & 0xffff
        actual = int.from_bytes(data[offset:offset + 2], 'little')
        magics.append(dict(block=block, byte_offset=offset, actual=actual, expected=expected, matches=actual == expected))
    recipe = json.loads((build / 'flasher_args.json').read_bytes())
    invocation = [line.strip() for line in (build / 'build.ninja').read_text('utf-8').splitlines()
                  if 'spiffsgen.py' in line and 'COMMAND' in line]
    assert len(invocation) == 1
    replay = ROOT / ('.build/cyd-production-boot-replay-20261030-' + profile + '-01')
    replay_report = json.loads((replay / 'report.json').read_bytes())
    image = (replay / 'qemu-flash.bin').read_bytes()
    log = (replay / 'qemu.log').read_text('utf-8', errors='replace')
    assert selected == dict(type=1, subtype=130, offset=0x370000, size=0x90000, label='spiffs', flags=0)
    assert image[selected['offset']:selected['offset'] + selected['size']] == data
    assert 'SPIFFS: mount failed, -10025' in log and 'SPIFFS mount failed without format: ESP_FAIL' in log
    result['profiles'][profile] = dict(partition=selected, recipe_spiffs=recipe['flash_files']['0x370000'],
        spiffs_bytes=len(data), spiffs_sha256=digest(build / 'spiffs.bin'), non_ff_bytes=len(data)-data.count(255),
        image_contains_exact_spiffs_bytes=True, geometry=values, block_size=block_size, block_count=block_count,
        valid_magic_blocks=sum(row['matches'] for row in magics), block_magic_checks=magics,
        generation_command=invocation[0], source_volume_present=True,
        mount_error_code=-10025, mount_error_name='SPIFFS_ERR_NOT_A_FS', format_if_mount_failed=False,
        replay_report_sha256=digest(replay / 'report.json'), replay_log_sha256=digest(replay / 'qemu.log'),
        old_flash_boundary_passed=replay_report['old_flash_boundary_passed'],
        early_mpi_return_log_observed=replay_report['early_mpi_return_log_observed'])
sdk = ROOT.parent.parent / '.idf/v6.0.2'
result['source_pins'] = {name: digest(sdk / name) for name in (
    'components/spiffs/spiffsgen.py', 'components/spiffs/spiffs/src/spiffs.h',
    'components/spiffs/spiffs/src/spiffs_nucleus.h')}
result['policy_source'] = dict(path='idf/esp32-cyd2usb-native/main/app_main.c',
                              sha256=digest(ROOT / 'idf/esp32-cyd2usb-native/main/app_main.c'))
result['source_volume_absence_hypothesis_supported'] = False
result['emulated_spi_readback_qualified'] = False
OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(profiles=2, source_volume_present=True, geometry_matches_generator=True,
    valid_magic_blocks_each=min(row['valid_magic_blocks'] for row in result['profiles'].values()),
    block_count=144, mount_error_code=-10025, source_volume_absence_hypothesis_supported=False)))
