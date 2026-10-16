"""Replay complete factory photo/fade output with genuine JPEG, glyph and LEDC code.

Only flash, allocation, mutex, LEDC driver and LCD transport boundaries are
adapted. Photo selection, fade state, JPEG decoding and footer glyphs execute
from the immutable RV32 firmware. Native scene helpers also execute their real
ELF bytes; their coordinator calls are composed explicitly for isolated checks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from jpeg_oracle import JpegMachine, assets_list, patterned_panel
from machine_oracle import ROOT, SCRATCH, UC_HOOK_CODE, layout
from control_oracle import verify_inputs


class PhotoMachine(JpegMachine):
    """Retain the complete photo pipeline and record only SDK boundary effects."""
    def __init__(self, variant, dump, manifest):
        super().__init__(variant, dump)
        self.photos = [item for item in assets_list(manifest) if item['file'].startswith('photos/')]
        if len(self.photos) != 5:
            raise AssertionError('Expected all five public photo fixtures')
        self.events = []
        self.selected = []
        self.duty = None
        addresses = (0x4201550c, 0x42014e68) if self.is_factory else (
            self.symbols['ledc_set_duty'], self.symbols['ledc_update_duty'])
        self.adapt(addresses[0], 'photo-ledc-set', self.set_duty)
        self.adapt(addresses[1], 'photo-ledc-latch', self.latch)
        entry = 0x4200c518 if self.is_factory else self.symbols['media_draw_photo']
        self.cpu.hook_add(UC_HOOK_CODE, self.select_asset, begin=entry, end=entry)
        if not self.is_factory:
            size, fields = layout('tv_settings_t')
            settings = bytearray(size)
            for index, item in enumerate(self.photos):
                length = (ROOT/'Small_TV/assets'/item['file']).stat().st_size
                struct.pack_into('<I', settings, fields['photo_size']+index*4, length)
            self.cpu.mem_write(self.symbols['current_settings'], bytes(settings))
            self.cpu.mem_write(self.symbols['settings_mutex'], struct.pack('<I', SCRATCH+0x2200))

    def set_duty(self):
        """Capture exact hardware duty arithmetic without replacing the fade setter."""
        if (self.reg(10), self.reg(11)) != (0, 0):
            raise AssertionError('Unexpected photo LEDC channel')
        self.duty = self.reg(12)
        self.events.append(['set', self.duty])
        return 0

    def latch(self):
        """Require the separate duty update operation to use the same channel."""
        if (self.reg(10), self.reg(11)) != (0, 0):
            raise AssertionError('Unexpected photo LEDC latch')
        self.events.append(['update'])
        return 0

    def select_asset(self, cpu, pc, size, context):
        """Observe the actual selected asset; leave renderer and decoder instructions intact."""
        if self.is_factory:
            offset = self.reg(12)
            slot = next((index for index, item in enumerate(self.photos)
                         if int(item['flash_offset'], 16) == offset), None)
            if slot is None:
                raise AssertionError('Photo renderer selected a non-photo flash range')
        else:
            slot = self.reg(10)
        if not 0 <= slot < 5:
            raise AssertionError('Unexpected photo slot')
        self.selected.append(slot)
        self.active_asset = self.photos[slot]
        self.native_length = (ROOT/'Small_TV/assets'/self.active_asset['file']).stat().st_size

    def prepare(self, fade, next_slot, address):
        """Supply explicit typed input to isolated replay, never a running QEMU guest."""
        self.events.clear()
        self.selected.clear()
        self.reads.clear()
        self.decompression_started = False
        self.prepare_reads = 0
        self.address = address
        if self.is_factory:
            self.cpu.mem_write(0x3fcc3a50, bytes([fade, next_slot]))
            self.cpu.mem_write(0x3fcb7b84, address.encode('ascii')+b'\0')
        else:
            self.cpu.mem_write(SCRATCH+0x100, bytes([fade, next_slot]))
            self.cpu.mem_write(SCRATCH+0x300, address.encode('ascii')+b'\0')

    def advance(self, fade, next_slot, mask, address='10.0.2.15', event=True, blocked=False):
        """Execute a literal factory step, or native step plus its explicit output helpers."""
        self.prepare(fade, next_slot, address)
        if self.is_factory:
            self.cpu.mem_write(0x3fcb7b9c+420, struct.pack('<I', mask))
            self.cpu.mem_write(0x3fcc39f8, bytes([bool(event)]))
            self.cpu.mem_write(0x3fcc39d8, bytes([bool(blocked)]))
            self.call(0x4200bc36, instruction_limit=100000000)
            state = bytes(self.cpu.mem_read(0x3fcc3a50, 2))
            pending = bool(self.cpu.mem_read(0x3fcc39f8, 1)[0])
        else:
            self.call(self.symbols['factory_photo_step'], SCRATCH+0x100, mask, 31,
                      int(event), int(blocked), SCRATCH+0x200)
            duty, photo, set_duty, finished = struct.unpack('<Hb??', self.cpu.mem_read(SCRATCH+0x200, 5))
            if set_duty:
                self.call(self.symbols['backlight_set_level'], duty)
            if photo >= 0:
                self.call(self.symbols['factory_draw_photo'], photo, SCRATCH+0x300,
                          instruction_limit=100000000)
            elif photo == -1:
                self.call(self.symbols['display_fill'], 0, 0, 240, 240, 0)
                self.call(self.symbols['display_factory_text'], 5, 225, SCRATCH+0x300,
                          16, 0xffff, 0, 1)
            state = bytes(self.cpu.mem_read(SCRATCH+0x100, 2))
            pending = bool(event and not finished)
        if self.allocations:
            raise AssertionError('Photo renderer leaked its decoder workspace')
        return {'fade': state[0], 'next_slot': state[1], 'pending': pending,
                'selected': self.selected[:], 'events': self.events[:], 'duty': self.duty}


def normalized_checks():
    """Compare raw full panels for every photo, mask skips, wraparound and no-photo output."""
    app_sha = verify_inputs()
    dump = (ROOT/'Small_TV/full-flash.bin').read_bytes()
    manifest = json.loads((ROOT/'Small_TV/assets/manifest.json').read_text(encoding='utf-8'))
    factory, native = [PhotoMachine(variant, dump, manifest) for variant in ('factory', 'native')]
    cases = [(1 << slot, (slot+1) % 5, '10.0.2.15') for slot in range(5)]
    cases += [(31, 4, '192.168.43.1'), (10, 4, '255.255.255.255'),
              (0, 0, '10.0.2.15'), (0, 4, '192.168.43.1')]
    rows = []
    for mask, slot, address in cases:
        for machine in (factory, native):
            machine.panel = patterned_panel()
        left = factory.advance(2, slot, mask, address)
        right = native.advance(2, slot, mask, address)
        different = sum(a != b for a, b in zip(factory.panel.pixels, native.panel.pixels))
        row = {'mask': mask, 'next_slot': slot, 'address': address,
               'factory': left, 'native': right, 'compared_pixels': 57600,
               'different_pixels': different, 'passed': not different and left == right}
        rows.append(row)
        print('Photo full frame:', mask, slot, 'different pixels', different, 'passed', row['passed'], flush=True)
    return {'passed': all(row['passed'] for row in rows), 'cases': rows,
            'app_sha256': app_sha, 'native_elf_sha256': native.source_sha,
            'factory_elf_sha256': factory.source_sha, 'scope': __doc__}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    paths = [Path(__file__), *[Path(__file__).with_name(name) for name in
             ('jpeg_oracle.py', 'machine_oracle.py', 'control_oracle.py')]]
    fingerprints = [{'file': path.relative_to(ROOT).as_posix(),
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]
    report = normalized_checks()
    report['test_inputs'] = fingerprints
    report['inputs_unchanged'] = all(hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest() == row['sha256']
                                     for row in fingerprints) and verify_inputs() == report['app_sha256']
    report['passed'] &= report['inputs_unchanged']
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    raise SystemExit(0 if report['passed'] else 1)
