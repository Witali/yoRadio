"""Run headless full-firmware checks in isolated, disposable QEMU flash copies."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from http_body_contract import contract_rejection_checks
from concurrency_contract import contract_rejection_checks as concurrency_rejections

ROOT = Path(__file__).resolve().parents[3]


def check(value, message):
    """Fail the suite instead of reporting an observation as a passing check."""
    if not value:
        raise AssertionError(message)


def main():
    """Test real network/calendar transitions and complete scenes; close every owned VM."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=30)
    parser.add_argument('--http-helper-overlay', type=Path,
                        help='Pinned committed HTTP-client snapshot for UTF-8 tests only')
    args = parser.parse_args()
    check(5 <= args.seconds <= 3600, 'Invalid boot-test duration')
    args.output.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(args.qemu_root / 'tools'))
    import small_tv_vm as vm
    profile = ROOT / 'Small_TV/qemu/profiles/small-tv-c2.json'
    options = SimpleNamespace(yoradio=str(ROOT), qemu=str(args.qemu_root / 'bin/qemu-system-riscv32.exe'),
                              rom_elf=str(ROOT / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
                              hardware_profile=str(profile), network='clock', display='none',
                              persistent=False, paused=False, gdb_port=0, seconds=args.seconds,
                              http_helper_overlay=args.http_helper_overlay)
    inputs = {'qemu_sha256': hashlib.sha256(Path(options.qemu).read_bytes()).hexdigest(),
              'profile_sha256': hashlib.sha256(profile.read_bytes()).hexdigest(),
              'helper_sha256': {name: hashlib.sha256((args.qemu_root / 'tools' / name).read_bytes()).hexdigest()
                               for name in ('small_tv_vm.py', 'small_tv_network.py', 'small_tv_web.py', 'small_tv_http_test.py',
                                            'esp_board.py', 'esp_services.py')}}
    report = {'passed': False, 'tested_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              **inputs,
              'boot_reset': {}, 'startup_wait': {}, 'weather_wait': {}, 'advanced_http': {}, 'body_http': {}, 'concurrency_http': {}, 'photo_http': {}, 'photo_frames': {}, 'photo_brightness': {}, 'photo_controls': {}, 'photo_reinit': {}, 'photo_settings': {}, 'http_initial_setup': {}, 'weather_http': {}, 'field_http': {}, 'time_http': {}, 'text_http': {}, 'regional_http': {}, 'calendar_http': {}, 'completed_scenes': {}, 'scenes': {}, 'errors': [],
              'scope': 'Real firmware boot/reset/DHCP/SNTP, localhost HTTP, synthetic weather, natural calendar/DST transitions and complete instruction-replayed frames. The separate unsynchronized scene similarity remains diagnostic. No physical hardware or Internet weather service.'}
    try:
        for variant in ('original', 'reconstructed'):
            options.firmware = variant
            result = vm.test_vm(options, args.output / 'boot-reset' / variant)
            report['boot_reset'][variant] = result
            check(result['passed'], f'{variant}: boot/reset/SNTP checks failed')
            print('PASS QEMU boot/reset/SNTP:', variant, flush=True)
        for name, key in (('startup', 'startup_wait'), ('weather_wait', 'weather_wait'),
                          ('advanced', 'advanced_http'), ('http_body', 'body_http'), ('concurrency', 'concurrency_http'), ('photo', 'photo_http'), ('photo_frames', 'photo_frames'),
                          ('photo_brightness', 'photo_brightness'), ('photo_controls', 'photo_controls'),
                          ('photo_reinit', 'photo_reinit'), ('photo_settings', 'photo_settings')):
            folder = args.output / ({'advanced': 'advanced-http', 'http_body': 'http-body', 'concurrency': 'concurrency-http', 'photo': 'photo-http', 'photo_frames': 'photo-frames',
                                     'photo_brightness': 'photo-brightness',
                                     'photo_controls': 'photo-controls',
                                     'photo_reinit': 'photo-reinit', 'photo_settings': 'photo-settings'}.get(name, name+'-observer'))
            command = [sys.executable, str(Path(__file__).with_name(name + '_qemu.py')),
                       '--qemu-root', str(args.qemu_root), '--output', str(folder)]
            if name in ('http_body', 'concurrency'):
                command += ['--yoradio', str(ROOT), '--dependency-root', str(ROOT)]
            process = subprocess.run(command)
            result = json.loads((folder / 'report.json').read_text(encoding='utf-8-sig'))
            report[key] = result
            check(process.returncode == 0 and result['passed'] and result['inputs_unchanged'],
                  name + ': actual guest regression failed')
            if name == 'http_body':
                archive = ROOT / 'firmware/development/small-tv-esp32c2-reconstructed'
                manifest = json.loads((archive / 'manifest.json').read_text())
                result['contract_checks'] = contract_rejection_checks(result, {
                    'app_sha256': hashlib.sha256((archive / 'app.bin').read_bytes()).hexdigest(),
                    'source_sha256': manifest['source_sha256'], 'qemu_sha256': inputs['qemu_sha256'],
                    'test_sha256': hashlib.sha256(Path(__file__).with_name('http_body_qemu.py').read_bytes()).hexdigest()})
            if name == 'concurrency':
                archive = ROOT / 'firmware/development/small-tv-esp32c2-reconstructed'
                manifest = json.loads((archive / 'manifest.json').read_text())
                result['contract_checks'] = concurrency_rejections(result, {
                    'app_sha256': hashlib.sha256((archive / 'app.bin').read_bytes()).hexdigest(),
                    'source_sha256': manifest['source_sha256'], 'qemu_sha256': inputs['qemu_sha256'],
                    'native_elf_sha256': hashlib.sha256((ROOT / '.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()).hexdigest(),
                    'test_sha256': hashlib.sha256(Path(__file__).with_name('concurrency_qemu.py').read_bytes()).hexdigest(),
                    'formatter_sha256': hashlib.sha256(Path(__file__).with_name('photo_protocol.py').read_bytes()).hexdigest()})
            print('PASS QEMU guest regression:', name, flush=True)
        from small_tv_http_test import run_suite
        report['http_initial_setup'] = run_suite(options, args.output / 'http-initial-setup')
        check(report['http_initial_setup']['passed'], 'Real guest HTTP/AP->STA setup failed')
        from weather_qemu import run_suite as run_weather
        report['weather_http'] = run_weather(options, args.output / 'weather-http')
        check(report['weather_http']['passed'], 'Real guest weather HTTP/value/LCD checks failed')
        from field_qemu import run_suite as run_fields
        report['field_http'] = run_fields(options, args.output / 'field-http')
        check(report['field_http']['passed'], 'Real guest field update/scroll checks failed')
        from time_qemu import run_suite as run_time
        report['time_http'] = run_time(options, args.output / 'time-http')
        check(report['time_http']['passed'], 'Real UDP/SNTP fallback/calendar/reset checks failed')
        from text_qemu import run_suite as run_text
        report['text_http'] = run_text(options, args.output / 'text-http')
        check(report['text_http']['passed'], 'Real UTF-8 HTTP/cache/glyph/scroll checks failed')
        from regional_qemu import run_suite as run_regional
        report['regional_http'] = run_regional(options, args.output / 'regional-http')
        check(report['regional_http']['passed'], 'Regional HTTP/raw/calendar/cold boot checks failed')
        from calendar_qemu import run_suite as run_calendar
        report['calendar_http'] = run_calendar(options, args.output / 'calendar-http')
        check(report['calendar_http']['passed'], 'Natural SNTP calendar/DST/frame transitions failed')
        from scene_qemu import run_suite as run_completed_scenes
        report['completed_scenes'] = run_completed_scenes(options, args.output / 'completed-scenes')
        check(report['completed_scenes']['passed'], 'Completed whole-frame instruction replay failed')
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
        unchanged = (inputs['qemu_sha256'] == hashlib.sha256(Path(options.qemu).read_bytes()).hexdigest()
                     and inputs['profile_sha256'] == hashlib.sha256(profile.read_bytes()).hexdigest()
                     and all(value == hashlib.sha256((args.qemu_root / 'tools' / name).read_bytes()).hexdigest()
                             for name, value in inputs['helper_sha256'].items()))
        report['inputs_unchanged'] = unchanged
        if not unchanged:
            report['passed'] = False
            report['errors'].append('Emulator/profile/helpers changed during execution')
        (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        check(unchanged, 'Emulator/profile/helpers changed during execution')


if __name__ == '__main__':
    main()
