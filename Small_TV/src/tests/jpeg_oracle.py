"""Execute original and rebuilt RV32 JPEG decoders through the LCD transport."""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import struct

from classic_oracle import layout
from control_oracle import verify_inputs
from machine_oracle import Machine, Panel, ROOT, SCRATCH, UC_HOOK_CODE


class JpegMachine(Machine):
    """Keep JPEG input, IDCT, output callbacks and LCD blitters as machine code."""
    def __init__(self, variant, dump, *, dependency_root=None):
        super().__init__(variant, dependency_root=dependency_root)
        self.dump = dump
        self.native_assets = (ROOT/'firmware/development/small-tv-esp32c2-reconstructed/assets.bin').read_bytes()
        self.reads = []
        self.fail_read_number = None
        self.allocations = set()
        self.fail_allocation = False
        self.active_asset = None
        self.decompression_started = False
        self.prepare_reads = 0
        if self.is_factory:
            self.adapt(0x40392326, 'jpeg-flash-read', self.flash_read)
        else:
            size, fields = layout('esp_partition_t')
            partition = bytearray(size)
            struct.pack_into('<I', partition, fields['address'], 0x200000)
            struct.pack_into('<I', partition, fields['size'], len(self.native_assets))
            self.cpu.mem_write(SCRATCH+0x2000, bytes(partition))
            self.adapt(self.symbols['esp_partition_find_first'], 'asset-partition', lambda: SCRATCH+0x2000)
            self.adapt(self.symbols['xQueueCreateMutex'], 'media-mutex-create', lambda: SCRATCH+0x2100)
            self.adapt(self.symbols['xQueueSemaphoreTake'], 'media-mutex-take', lambda: 1)
            self.adapt(self.symbols['xQueueGenericSend'], 'media-mutex-give', lambda: 1)
            self.adapt(self.symbols['esp_partition_read'], 'jpeg-partition-read', self.partition_read)
            self.adapt(self.symbols['malloc'], 'jpeg-workspace-malloc', self.allocate)
            self.adapt(self.symbols['free'], 'jpeg-workspace-free', self.release)
            if self.call(self.symbols['media_init']) != 0:
                raise AssertionError('Native media initialization failed')
        entry = 0x42011fd8 if self.is_factory else self.symbols['jd_decomp']
        self.cpu.hook_add(UC_HOOK_CODE, self.observe_decompression, begin=entry, end=entry)

    def observe_decompression(self, cpu, pc, size, context):
        """Observe the actual transition from header preparation to MCU decoding."""
        self.decompression_started = True
        self.prepare_reads = len(self.reads)

    def allocate(self):
        """Provide the decoder's actual workspace, checking ownership on every call."""
        if self.reg(10) != 8192 or self.allocations:
            raise AssertionError('Unexpected JPEG workspace allocation')
        if self.fail_allocation:
            return 0
        pointer = SCRATCH+0x4000
        self.allocations.add(pointer)
        return pointer

    def release(self):
        """Require exactly one release of each workspace, including failures."""
        self.allocations.remove(self.reg(10))

    def read(self, offset, destination, size, data):
        """Supply only the active public asset and inject one SDK read error."""
        start = int(self.active_asset['flash_offset'], 16) if self.is_factory else self.active_asset['native_offset']
        if not start <= offset < start+self.active_asset['source_length']+512 or size > 512:
            raise AssertionError('JPEG read left its declared asset fixture')
        if not self.is_factory and offset+size > start+self.native_length:
            raise AssertionError('Native decoder read beyond its declared JPEG length')
        self.reads.append([offset, size])
        if len(self.reads) == self.fail_read_number:
            return 0x105
        if size:
            self.cpu.mem_write(destination, data)
        return 0

    def flash_read(self):
        """Serve immutable factory flash through its actual ESP-IDF read boundary."""
        offset, size = self.reg(12), self.reg(13)
        return self.read(offset, self.reg(11), size, self.dump[offset:offset+size])

    def partition_read(self):
        """Serve the unchanged archived asset partition, with bounded read addresses."""
        if self.reg(10) != SCRATCH+0x2000:
            raise AssertionError('Unexpected native partition')
        offset, size = self.reg(11), self.reg(13)
        return self.read(offset+0x200000, self.reg(12), size, self.native_assets[offset:offset+size])

    def draw(self, asset, x=0, y=0, length=None):
        """Run the complete JPEG entry from bytes in the verified firmware ELF."""
        self.active_asset = asset
        self.reads = []
        self.decompression_started = False
        self.prepare_reads = 0
        offset = int(asset['flash_offset'], 16) if self.is_factory else asset['native_offset']
        if self.is_factory:
            return self.call(0x4200c518, x, y, offset, instruction_limit=100000000)
        if length is None:
            length = len((ROOT/'Small_TV/assets'/asset['file']).read_bytes())
        self.native_length = length
        result = self.call(self.symbols['media_draw_jpeg'], offset, length, x, y, instruction_limit=100000000)
        if self.allocations:
            raise AssertionError('JPEG decoder leaked its workspace')
        return result

    def validate(self, asset, width, height, length=None):
        """Execute the real discard-only decoder, with no drawing or fake validation."""
        self.active_asset = asset
        self.reads = []
        self.decompression_started = False
        self.prepare_reads = 0
        self.native_length = length if length is not None else len((ROOT/'Small_TV/assets'/asset['file']).read_bytes())
        result = self.call(self.symbols['media_validate_jpeg_unlocked'], asset['native_offset'],
                           self.native_length, width, height, instruction_limit=100000000)
        if self.allocations:
            raise AssertionError('JPEG validation leaked its workspace')
        return result


def assets_list(manifest):
    """Enumerate all public photo, animation and status JPEGs in stable order."""
    packed = (ROOT/'firmware/development/small-tv-esp32c2-reconstructed/assets.bin').read_bytes()
    rows = []
    for row in [*manifest['status'], *manifest['photos']]:
        data = (ROOT/'Small_TV/assets'/row['file']).read_bytes()
        offset = int(row['flash_offset'], 16)-0x200000
        if packed[offset:offset+len(data)] != data or hashlib.sha256(data).hexdigest() != row['export_sha256']:
            raise AssertionError('Public JPEG differs from its archived fixture')
        rows.append({**row, 'native_offset':int(row['flash_offset'], 16)})
    for animation in manifest['animations']:
        base = int(animation['flash_offset'], 16)
        for row in animation['frames']:
            length, relative = struct.unpack_from('<II', packed, base-0x200000+11+row['index']*8)
            data = (ROOT/'Small_TV/assets'/row['file']).read_bytes()
            if length != len(data) or packed[base-0x200000+relative:base-0x200000+relative+length] != data:
                raise AssertionError('Sanitized animation frame differs from archived bytes')
            rows.append({**row, 'native_offset':base+relative})
    return [*rows[:4], *rows[9:], *rows[4:9]]


def patterned_panel():
    """Make every guard pixel nonzero, so an omitted erase cannot pass accidentally."""
    panel = Panel()
    panel.pixels = array('H', (((i*37)%65534)+1 for i in range(57600)))
    return panel


def error_checks(factory, native, fixtures):
    """Check preparation/MCU errors, exact erase bounds, retries and discard mode."""
    rows = []
    for asset in (fixtures[4], fixtures[-1]):
        native.fail_read_number = None
        native.draw(asset)
        total, prepared = len(native.reads), native.prepare_reads
        x, y = (23, 37) if asset['width'] < 240 else (0, 0)
        factory.panel = patterned_panel()
        factory.draw(asset, x, y)
        clean = factory.panel.pixels[:]
        for fail in sorted({1, prepared, prepared+1, (prepared+total+1)//2, total}):
            native.panel = patterned_panel()
            initial = native.panel.pixels[:]
            native.fail_read_number = fail
            result = native.draw(asset, x, y)
            expected = initial[:]
            decoding = native.decompression_started
            if decoding:
                for line in range(y, y+asset['height']):
                    expected[line*240+x:line*240+x+asset['width']] = array('H', [0])*asset['width']
            difference = sum(a != b for a,b in zip(native.panel.pixels, expected))
            rows.append({'kind':'read-error', 'file':asset['file'], 'read_number':fail,
                         'result':result, 'different_pixels':difference, 'decompression_started':decoding,
                         'x':x, 'y':y, 'passed':result == 0x102 and not difference})
            native.fail_read_number = None
            retry = native.draw(asset, x, y)
            difference = sum(a != b for a,b in zip(native.panel.pixels, clean))
            rows.append({'kind':'retry', 'file':asset['file'], 'after_read_number':fail,
                         'different_pixels':difference, 'passed':retry == 0 and not difference})
        native.panel = patterned_panel()
        initial = native.panel.pixels[:]
        native.fail_allocation = True
        result = native.draw(asset, x, y)
        rows.append({'kind':'allocation-error', 'file':asset['file'], 'result':result,
                     'passed':result == 0x101 and native.panel.pixels == initial and not native.reads})
        native.fail_allocation = False
        for fail, width in ((None, asset['width']), (1, asset['width']), (total, asset['width']),
                            (None, asset['width']-1)):
            native.fail_read_number = fail
            native.panel = patterned_panel()
            initial = native.panel.pixels[:]
            result = native.validate(asset, width, asset['height'])
            expected_result = 0 if fail is None and width == asset['width'] else 0x102
            rows.append({'kind':'discard-validation', 'file':asset['file'], 'read_error':fail,
                         'required_width':width, 'result':result,
                         'passed':result == expected_result and native.panel.pixels == initial})
        native.fail_read_number = None
        for length in (20, native.native_length//2):
            native.panel = patterned_panel()
            expected = native.panel.pixels[:]
            result = native.draw(asset, x, y, length=length)
            if native.decompression_started:
                for line in range(y, y+asset['height']):
                    expected[line*240+x:line*240+x+asset['width']] = array('H', [0])*asset['width']
            difference = sum(a != b for a,b in zip(native.panel.pixels, expected))
            rows.append({'kind':'truncated-stream', 'file':asset['file'], 'length':length,
                         'result':result, 'decompression_started':native.decompression_started,
                         'different_pixels':difference, 'passed':result == 0x102 and not difference})
    # The original callback returns success even when esp_flash_read fails.
    # Execute that callback directly; do not substitute a synthetic decoder.
    asset = fixtures[4]
    offset = int(asset['flash_offset'], 16)
    factory.active_asset = asset
    factory.reads = []
    factory.fail_read_number = 1
    factory.cpu.mem_write(SCRATCH+0x1000, bytes(0x78))
    factory.cpu.mem_write(SCRATCH+0x1074, struct.pack('<I', SCRATCH+0x1200))
    factory.cpu.mem_write(SCRATCH+0x1200, struct.pack('<I', offset))
    returned = factory.call(0x4200c33e, SCRATCH+0x1000, SCRATCH+0x1400, 512)
    position = struct.unpack('<I', factory.cpu.mem_read(SCRATCH+0x1200, 4))[0]
    rows.append({'kind':'literal-factory-read-error', 'sdk_result':0x105,
                 'callback_returned':returned, 'position_advanced':position-offset,
                 'passed':returned == 512 and position == offset+512 and len(factory.reads) == 1})
    factory.fail_read_number = None
    return rows


def placement_checks(factory, native, fixtures):
    """Verify production positions and clipped MCU strides against decoded factory pixels."""
    rows = []
    asset = fixtures[4]
    for x,y in ((160,160), (23,37)):
        for machine in (factory, native):
            machine.panel = patterned_panel()
            result = machine.draw(asset, x, y)
            if not machine.is_factory and result:
                raise AssertionError('Translated JPEG failed')
        difference = sum(a != b for a,b in zip(factory.panel.pixels, native.panel.pixels))
        rows.append({'kind':'translated', 'x':x, 'y':y, 'different_pixels':difference, 'passed':not difference})
    factory.panel = Panel()
    factory.draw(asset)
    decoded = factory.panel.pixels[:]
    for x,y in ((-5,-6), (220,225), (240,240)):
        native.panel = patterned_panel()
        expected = native.panel.pixels[:]
        for source_y in range(asset['height']):
            for source_x in range(asset['width']):
                if 0 <= x+source_x < 240 and 0 <= y+source_y < 240:
                    expected[(y+source_y)*240+x+source_x] = decoded[source_y*240+source_x]
        result = native.draw(asset, x, y)
        difference = sum(a != b for a,b in zip(native.panel.pixels, expected))
        rows.append({'kind':'clipped', 'x':x, 'y':y, 'different_pixels':difference,
                     'passed':result == 0 and not difference})
    fail = (native.prepare_reads+len(native.reads)+1)//2
    for x,y in ((-5,-6), (220,225)):
        native.panel = patterned_panel()
        expected = native.panel.pixels[:]
        for line in range(max(y,0), min(y+asset['height'],240)):
            left, right = max(x,0), min(x+asset['width'],240)
            expected[line*240+left:line*240+right] = array('H',[0])*(right-left)
        native.fail_read_number = fail
        result = native.draw(asset, x, y)
        difference = sum(a != b for a,b in zip(native.panel.pixels, expected))
        rows.append({'kind':'clipped-read-error', 'x':x, 'y':y, 'read_number':fail,
                     'different_pixels':difference, 'passed':result == 0x102 and not difference})
    native.fail_read_number = None
    return rows


def main():
    """Compare every RGB565 pixel, binding results to verified input binaries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    app = verify_inputs()
    dump = (ROOT/'Small_TV/full-flash.bin').read_bytes()
    assets = json.loads((ROOT/'Small_TV/assets/manifest.json').read_text(encoding='utf-8'))
    factory, native = JpegMachine('factory', dump), JpegMachine('native', dump)
    fixtures = assets_list(assets)
    rows = []
    for asset in fixtures[:args.limit]:
        for machine in (factory, native):
            machine.panel = Panel()
            result = machine.draw(asset)
            if not machine.is_factory and result:
                raise AssertionError(f'Native JPEG failed: {asset["file"]}, result={result}')
        difference = sum(a != b for a, b in zip(factory.panel.pixels, native.panel.pixels))
        rows.append({'file':asset['file'], 'different_pixels':difference,
                     'factory_reads':len(factory.reads), 'native_reads':len(native.reads),
                     'compared_pixels':57600, 'factory_decoder_started':factory.decompression_started,
                     'native_decoder_started':native.decompression_started,
                     'passed':difference == 0 and factory.decompression_started and native.decompression_started})
        if difference:
            factory.panel.png(args.output.parent/f'{len(rows)}-factory.png')
            native.panel.png(args.output.parent/f'{len(rows)}-native.png')
        print(asset['file'], 'different pixels:', difference, flush=True)
    errors = error_checks(factory, native, fixtures)
    placements = placement_checks(factory, native, fixtures)
    manifest = json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text(encoding='utf-8'))
    report = {'passed':all(row['passed'] for row in rows+errors+placements), 'cases':rows, 'errors':errors,
              'placements':placements, 'complete_asset_set':len(rows) == len(fixtures) == 107,
              'app_sha256':app,
              'source_sha256':manifest['source_sha256'], 'factory_elf_sha256':factory.source_sha,
              'native_elf_sha256':native.source_sha,
              'adapters':{'factory':factory.executed_adapters, 'native':native.executed_adapters},
              'approved_fixes':['erase-known-jpeg-rectangle-after-decode-error', 'clip-visible-display-region'],
              'scope':'Actual RV32 JPEG input, Huffman/IDCT/color conversion, output callbacks and LCD blitters; SDK flash/allocation/mutex and LCD transport only are adapted. All 57600 pixels compared; clipped placement uses independently placed pixels from the actual factory decoder. Factory flash callback error is executed literally; native failure erasure is a declared correction. No physical or throughput claim.'}
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('JPEG RV32:', len(rows), 'images;', len(errors), 'error/validation checks;', len(placements),
          'placement checks; passed=', report['passed'], flush=True)
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
