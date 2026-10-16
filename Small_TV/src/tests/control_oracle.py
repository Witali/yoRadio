"""Execute factory and compiled-C timer/slideshow transitions with synthetic state.

The original instructions remain unchanged. Only startup/SPI/image/backlight
output boundaries are captured; counters, flags, fade steps and photo selection
execute in the two RV32 programs. This does not validate the SDK task scheduler.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import struct

from machine_oracle import DUMP_SHA, ELFFile, Machine, Panel, ROOT, SCRATCH

FLAGS = [(0x3fcc39f6, 1), (0x3fcc39f7, 2), (0x3fcc39f8, 4),
         (0x3fcc39f5, 8), (0x3fcc39f0, 16), (0x3fcc39f4, 32), (0x3fcc39f3, 64)]
PHOTO_OFFSETS = [0x200000, 0x219000, 0x232000, 0x24b000, 0x264000]


def verify_inputs(root=ROOT,dependency_root=None):
    """Check factory payload identity and the archived native ELF/binary pair."""
    dependencies=Path(dependency_root) if dependency_root is not None else root
    dump = (root / 'Small_TV/full-flash.bin').read_bytes()
    if hashlib.sha256(dump).hexdigest() != DUMP_SHA:
        raise ValueError('Factory dump hash mismatch')
    position = 0x10000 + 24
    expected = {}
    for _ in range(dump[0x10001]):
        address, size = struct.unpack_from('<II', dump, position)
        position += 8
        expected[address] = dump[position:position + size]
        position += size
    with (dependencies / '.build/small-tv-reverse/factory-analysis.elf').open('rb') as stream:
        actual = {segment['p_vaddr']:segment.data() for segment in ELFFile(stream).iter_segments()
                  if segment['p_type'] == 'PT_LOAD' and segment['p_filesz']}
    if actual != expected:
        raise ValueError('Prepared factory ELF differs from the immutable image')
    archive = root / 'firmware/development/small-tv-esp32c2-reconstructed'
    binary = (archive / 'app.bin').read_bytes()
    if binary != (root / '.build/small-tv-esp32c2/small_tv_reconstructed.bin').read_bytes():
        raise ValueError('Archived firmware is stale')
    native_sha = hashlib.sha256((root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()).digest()
    if binary[176:208] != native_sha:
        raise ValueError('Native ELF digest differs from the firmware descriptor')
    return hashlib.sha256(binary).hexdigest()


def timer_state(machine):
    """Read semantic counter/flag values from each program's actual RAM layout."""
    if not machine.is_factory:
        weather, pending, tick, description, photo, minute, slow, progress, active = struct.unpack(
            '<II7Bx', machine.cpu.mem_read(SCRATCH, 16))
        return [weather, pending & 127, tick, description, photo, minute, slow, progress, active]
    weather = struct.unpack('<I', machine.cpu.mem_read(0x3fcc39c4, 4))[0]
    slow, minute, photo, description, tick = machine.cpu.mem_read(0x3fcc39c8, 5)
    pending = sum(mask for address, mask in FLAGS if machine.cpu.mem_read(address, 1)[0])
    return [weather, pending, tick, description, photo, minute, slow,
            machine.cpu.mem_read(0x3fcc3a56, 1)[0], machine.cpu.mem_read(0x3fcc39eb, 1)[0]]


def consume(machine, mask):
    """Apply identical main-loop flag consumption to both live machine states."""
    if machine.is_factory:
        pending = timer_state(machine)[1] & mask
        for address, flag in FLAGS:
            if mask & flag:
                machine.cpu.mem_write(address, b'\0')
        return pending
    return machine.call(machine.symbols['factory_timer_take'], SCRATCH, mask)


def timer_checks(factory, native):
    """Verify every tick through weather rollover, stalls and interval changes."""
    results = []
    draw_calls = []
    factory.adapt(0x4200c1c8, 'startup-output', lambda: draw_calls.append(1))
    randomizer = random.Random(20261013)
    for interval, startup in [(3, True), (5, False), (60, True), (10, False)]:
        factory.cpu.mem_write(0x3fcc39c4, bytes(9))
        factory.cpu.mem_write(0x3fcc3a56, b'\0')
        factory.cpu.mem_write(0x3fcc39eb, bytes([startup]))
        for address, _ in FLAGS:
            factory.cpu.mem_write(address, b'\0')
        native.call(native.symbols['factory_timer_init'], SCRATCH, int(startup))
        draws = 0
        for tick in range(19824):
            # Change the photo interval without resetting its existing counter.
            period = 7 if interval == 10 and 5100 <= tick < 13000 else interval
            factory.cpu.mem_write(0x3fcb7b9c + 416, struct.pack('<I', period))
            before = len(draw_calls)
            factory.call(0x4200826a)
            draw = native.call(native.symbols['factory_timer_tick'], SCRATCH, period)
            if draw != len(draw_calls) - before or timer_state(factory) != timer_state(native):
                raise AssertionError(f'Timer mismatch at interval={interval}, tick={tick}')
            draws += draw
            # Long gaps in consumption simulate blocking HTTP/media work. Only
            # selected flags are cleared, so coalescing is checked explicitly.
            if tick % 37 == 0:
                mask = randomizer.randrange(128)
                if consume(factory, mask) != consume(native, mask):
                    raise AssertionError('Consumed event mask differs')
            if timer_state(factory) != timer_state(native):
                raise AssertionError('Post-consumption timer state differs')
        results.append({'photo_interval':interval, 'startup':startup, 'ticks':19824,
                        'startup_draw_requests':draws, 'passed':True})
        print('Timer trace passed:', interval, startup, flush=True)
    return results


def slideshow_checks(factory, native):
    """Compare duty, decoded-image requests, footer, fade and round-robin order."""
    outputs = []
    factory.adapt(0x42008bd2, 'backlight-output', lambda: outputs.append(('duty', factory.reg(10))))
    factory.adapt(0x4200c518, 'jpeg-output', lambda: outputs.append(
        ('photo', PHOTO_OFFSETS.index(factory.reg(12)))))
    factory.adapt(0x42009a0a, 'clear-output', lambda: outputs.append(('photo', -1)))
    factory.adapt(0x4200aa1e, 'footer-output', lambda: outputs.append(('footer',)))
    steps = 0
    for mask in range(32):
        for initial_fade in range(6):
            for initial_slot in range(5):
                factory.cpu.mem_write(0x3fcc3a50, bytes([initial_fade, initial_slot]))
                native.cpu.mem_write(SCRATCH + 0x100, bytes([initial_fade, initial_slot]))
                photo_event = True
                for step in range(14):
                    # Repeated events remain a single flag; blocked steps do
                    # not advance the fade. Mask changes retain next-slot state.
                    enabled = mask if step < 8 else (mask ^ 9)
                    if step == 9:
                        photo_event = True
                    blocked = step in (1, 4)
                    factory.cpu.mem_write(0x3fcb7b9c + 420, struct.pack('<I', enabled))
                    factory.cpu.mem_write(0x3fcc39f8, bytes([photo_event]))
                    factory.cpu.mem_write(0x3fcc39d8, bytes([blocked]))
                    outputs.clear()
                    factory.call(0x4200bc36)
                    native.call(native.symbols['factory_photo_step'], SCRATCH + 0x100,
                                enabled, 31, int(photo_event), int(blocked), SCRATCH + 0x200)
                    duty, photo, set_duty, finished = struct.unpack(
                        '<Hb??', native.cpu.mem_read(SCRATCH + 0x200, 5))
                    expected = [('duty', duty)] if set_duty else []
                    if photo >= -1:
                        expected += [('photo', photo), ('footer',)]
                    if outputs != expected:
                        raise AssertionError(f'Slideshow output mismatch {mask}, {initial_fade}, {initial_slot}, {step}: {outputs} != {expected}')
                    native_state = bytes(native.cpu.mem_read(SCRATCH + 0x100, 2))
                    if native_state != bytes(factory.cpu.mem_read(0x3fcc3a50, 2)):
                        raise AssertionError('Fade or round-robin state differs')
                    if finished:
                        photo_event = False
                    if photo_event != bool(factory.cpu.mem_read(0x3fcc39f8, 1)[0]):
                        raise AssertionError('Slideshow completion flag differs')
                    steps += 1
    print('Slideshow transitions passed:', steps, flush=True)
    return {'masks':32, 'initial_fades':6, 'initial_slots':5,
            'steps':steps, 'passed':True, 'present_mask':31}


def simple_event_checks():
    """Verify independent colon/minute flags on complete successive framebuffers."""
    factory, native, corrected = Machine('factory'), Machine('native'), Machine('factory')
    sequence = [(7, 14, 0, True, True), (7, 14, 1, False, False),
                (7, 14, 2, False, False), (7, 15, 3, False, False),
                (7, 15, 3, True, False), (7, 15, 4, False, True),
                (8, 0, 5, False, False), (8, 0, 5, True, False),
                (8, 0, 6, False, False), (8, 0, 6, True, True)]
    checked = 0
    literal_differences = []
    for mode in range(3):
        for hour12 in range(2):
            factory.panel, native.panel, corrected.panel = Panel(), Panel(), Panel()
            previous = None
            for index, (hour, minute, second, second_flag, minute_flag) in enumerate(sequence):
                for machine in (factory, native):
                    machine.seed(hour, minute, second, 2, mode, hour12)
                    machine.simple(reset=index == 0, minute_update=minute_flag,
                                   second_update=second_flag)
                corrected.seed(hour, minute, second, 2, mode, hour12)
                rollover = previous is None or previous != (hour, minute)
                corrected.simple(reset=index == 0, minute_update=minute_flag or rollover,
                                 second_update=second_flag)
                difference = sum(left != right for left, right in
                                 zip(factory.panel.pixels, native.panel.pixels))
                literal_differences.append({'date_format':mode, 'hour12':hour12, 'step':index,
                                            'different_pixels':difference})
                if corrected.panel.pixels != native.panel.pixels:
                    raise AssertionError(f'Independent simple-clock flags differ from corrected minute rollover: {mode}, {hour12}, {index}')
                checked += 1
                previous = (hour, minute)
    print('Independent simple-clock flag frames passed:', checked, flush=True)
    return {'frames':checked, 'all_pixels_compared':57600, 'passed':True,
            'approved_fix':'simple-real-minute-rollover', 'literal_factory_differences':literal_differences,
            'reference':'Separate unchanged factory renderer with minute flag raised on real hour/minute changes'}


def main():
    """Save an explicit successful control report, failing on any divergence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.build/small-tv-parity/control-report.json')
    args = parser.parse_args()
    app_sha = verify_inputs()
    factory, native = Machine('factory'), Machine('native')
    from backlight_oracle import run_checks as backlight_checks
    backlight = backlight_checks()
    if not backlight['passed']:
        raise AssertionError('Executed backlight call traces differ')
    report = {'factory_elf_sha256':factory.source_sha, 'native_elf_sha256':native.source_sha,
              'app_sha256':app_sha, 'timer_traces':timer_checks(factory, native),
              'slideshow':slideshow_checks(factory, native),
              'simple_events':simple_event_checks(), 'backlight':backlight, 'passed':True,
              'adapters':{'factory':factory.executed_adapters, 'native':native.executed_adapters},
              'scope':'Exact machine-code timer/slideshow control transitions and LEDC initialization/schedule traces; output boundaries adapted; task scheduling, electrical PWM and pixel decoding unverified here'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
