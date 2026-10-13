"""Run headless full-firmware checks in isolated, disposable QEMU flash copies."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]


def check(value, message):
    """Fail the suite instead of reporting an observation as a passing check."""
    if not value:
        raise AssertionError(message)


def main():
    """Test real boot/reset/DHCP/SNTP plus all five visible scenes; close every VM."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=30)
    args = parser.parse_args()
    check(5 <= args.seconds <= 3600, 'Invalid boot-test duration')
    args.output.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(args.qemu_root / 'tools'))
    import small_tv_vm as vm
    profile = args.qemu_root / 'configs/boards/small-tv-c2.json'
    options = SimpleNamespace(yoradio=str(ROOT), qemu=str(args.qemu_root / 'bin/qemu-system-riscv32.exe'),
                              rom_elf=str(ROOT / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
                              hardware_profile=str(profile), network='clock', display='none',
                              persistent=False, paused=False, gdb_port=0, seconds=args.seconds)
    report = {'passed': False, 'tested_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'boot_reset': {}, 'http_initial_setup': {}, 'scenes': {}, 'errors': [],
              'scope': 'Real firmware boot/reset/DHCP/SNTP and scene liveness; whole-frame similarity is measured, not a parity gate. No physical hardware or successful guest weather HTTP.'}
    try:
        for variant in ('original', 'reconstructed'):
            options.firmware = variant
            result = vm.test_vm(options, args.output / 'boot-reset' / variant)
            report['boot_reset'][variant] = result
            check(result['passed'], f'{variant}: boot/reset/SNTP checks failed')
            print('PASS QEMU boot/reset/SNTP:', variant, flush=True)
        from small_tv_http_test import run_suite
        report['http_initial_setup'] = run_suite(options, args.output / 'http-initial-setup')
        check(report['http_initial_setup']['passed'], 'Real guest HTTP/AP->STA setup failed')
        scene_output = args.output / 'scenes'
        subprocess.run([sys.executable, str(ROOT / 'Small_TV/qemu/parity/compare.py'),
                        '--qemu-root', str(args.qemu_root), '--yoradio', str(ROOT),
                        '--state', str(args.output / 'scene-vms'), '--output', str(scene_output)], check=True)
        comparison = json.loads((scene_output / 'comparison.json').read_text())
        check(set(comparison['scenes']) == {'setup', 'classic', 'simple', 'photo', 'dial'}, 'Missing scene')
        for scene, rows in comparison['scenes'].items():
            for variant in ('original', 'reconstructed'):
                row = rows[variant]
                check(row['no_panic'], f'{scene}/{variant}: panic')
                check(scene == 'setup' or row['ntp_reply'], f'{scene}/{variant}: missing NTP reply')
                nonempty = False
                for index in range(3):
                    path = scene_output / f'{scene}-{variant}-{index}.png'
                    raw = path.read_bytes()
                    check(raw[:8] == b'\x89PNG\r\n\x1a\n' and raw[16:24] == b'\0\0\0\xf0' * 2,
                          f'{path.name}: invalid 240x240 screenshot')
                    # PNG size alone is insufficient; decode its actual pixels.
                    import zlib
                    cursor, packed = 8, bytearray()
                    while cursor < len(raw):
                        length = int.from_bytes(raw[cursor:cursor + 4], 'big')
                        kind = raw[cursor + 4:cursor + 8]
                        payload = raw[cursor + 8:cursor + 8 + length]
                        check(kind in (b'IHDR', b'IDAT', b'IEND'), 'Screenshot contains unexpected metadata')
                        check(zlib.crc32(kind + payload) == int.from_bytes(raw[cursor + 8 + length:cursor + 12 + length], 'big'), 'PNG CRC mismatch')
                        if kind == b'IDAT': packed.extend(payload)
                        cursor += length + 12
                    pixels = zlib.decompress(packed)
                    check(len(pixels) == 240 * (240 * 3 + 1), 'Unexpected RGB scanline layout')
                    check(all(pixels[y * 721] == 0 for y in range(240)), 'Unsupported scanline filter')
                    nonempty |= sum(byte != 0 for byte in pixels) > 1000
                check(nonempty, f'{scene}/{variant}: all captures are blank')
            report['scenes'][scene] = rows
        report['passed'] = True
    except Exception as error:
        report['errors'].append(str(error))
        raise
    finally:
        report['qemu_sha256'] = hashlib.sha256(Path(options.qemu).read_bytes()).hexdigest()
        report['profile_sha256'] = hashlib.sha256(profile.read_bytes()).hexdigest()
        report['helper_sha256'] = {name: hashlib.sha256((args.qemu_root / 'tools' / name).read_bytes()).hexdigest()
                                  for name in ('small_tv_vm.py', 'small_tv_network.py', 'small_tv_web.py', 'small_tv_http_test.py')}
        (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
