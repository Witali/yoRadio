"""Check compiled logging modes using real firmware, HTTP, LCD and UDP SNTP.

Only a disposable VM flash copy is writable. No guest instructions, registers,
RAM or clocks are assigned. QMP configures the external synthetic NTP server.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from types import SimpleNamespace


def main():
    """Verify functionality without depending on deliberately disabled messages."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yoradio', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--qemu', type=Path, required=True)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--expect-firmware-debug', choices=('on', 'off'), required=True)
    parser.add_argument('--expect-qemu-debug', choices=('on', 'off'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, deps, archive = args.yoradio.resolve(), args.dependency_root.resolve(), args.archive.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(deps / '.build/small-tv-parity/oracle-deps'), str(args.qemu_root / 'tools')]
    from elftools.elf.elffile import ELFFile
    import small_tv_vm as vm
    from small_tv_http_test import http, wait_http, wait_for, clean_uart
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = json.loads((archive / 'manifest.json').read_text(encoding='utf-8'))
    firmware_debug, qemu_debug = args.expect_firmware_debug == 'on', args.expect_qemu_debug == 'on'
    if manifest.get('debug_logging') is not firmware_debug:
        raise ValueError('Unexpected archive logging mode')
    if (archive / 'app.bin').read_bytes()[176:208] != bytes.fromhex(sha(args.elf)):
        raise ValueError('Archived app and observed ELF differ')
    with args.elf.open('rb') as stream:
        symbols = {row.name: row['st_value'] for row in ELFFile(stream).get_section_by_name('.symtab').iter_symbols()}
    files = [Path(__file__), args.elf, args.qemu, root / 'Small_TV/qemu/profiles/small-tv-c2.json']
    files += [archive / name for name in ('manifest.json', 'source-manifest.json', 'sdkconfig',
              'app.bin', 'bootloader.bin', 'partition-table.bin', 'assets.bin', 'assets-manifest.json')]
    files += [args.qemu_root / 'tools' / name for name in ('small_tv_vm.py', 'small_tv_http_test.py',
              'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'esp_elf.py')]
    pins = {str(path.resolve()): sha(path) for path in files}
    report = {'passed': False, 'all_functionality_verified': False, 'scope': __doc__,
              'firmware_debug': firmware_debug, 'qemu_debug': qemu_debug, 'checks': {},
              'app_sha256': sha(archive / 'app.bin'), 'native_elf_sha256': sha(args.elf),
              'source_sha256': manifest['source_sha256'], 'qemu_sha256': sha(args.qemu),
              'inputs_sha256': pins}
    view = args.output / 'view'
    shutil.copytree(archive, view / 'firmware/development/small-tv-esp32c2-reconstructed')
    state, session = args.output / 'vm', None
    original_seed = vm.seed_clock_network

    def seed_without_weather(*arguments):
        """Use only disposable synthetic settings and genuinely disable weather."""
        data = bytearray(original_seed(*arguments))
        data[0x3e711c:0x3e715d] = bytes(65)
        return data

    vm.seed_clock_network = seed_without_weather
    options = SimpleNamespace(yoradio=str(view), qemu=str(args.qemu), firmware='reconstructed',
        rom_elf=str(deps / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(root / 'Small_TV/qemu/profiles/small-tv-c2.json'),
        network='clock', display='none', paused=True, persistent=False, gdb_port=0)

    def check(name, value):
        """Keep every acceptance assertion, including the first failed condition."""
        report['checks'][name] = bool(value)
        if not value:
            raise AssertionError(name)

    def flag(qmp, name):
        """Observe actual atomic/sync flags without debugger writes or log parsing."""
        output = qmp.execute('human-monitor-command', **{'command-line': f'xp /1bx 0x{symbols[name]:x}'})
        return int(output.rsplit(':', 1)[1].strip(), 16) == 1

    try:
        session, _ = vm.launch(options, state)
        url = session['web_urls']['station']
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            check('qemu_compiled_mode', qmp.execute('qom-get', path='/machine/wifi', property='debug-logging') is qemu_debug)
            qmp.execute('qom-set', path='/machine/wifi', property='ntp-unix-seconds', value=1781265600)
            qmp.execute('cont')
            wait_http(url, '/getsettings')
            wait_for(lambda: flag(qmp, 'connected') and flag(qmp, 'time_synced'), 'Actual station/SNTP readiness missing')
            check('real_station_and_sntp', flag(qmp, 'connected') and flag(qmp, 'time_synced'))
            for theme in range(4):
                status, _ = http(url, '/setclocktype', {'clocktype': str(theme)}, origin=url)
                check(f'theme_{theme}_http', status == 200)
                check(f'theme_{theme}_readback', json.loads(wait_http(url, '/getclocktype')) == theme)
            status, _ = http(url, '/logging-test-missing-uri')
            check('missing_uri_captive_redirect', status == 302)
            status, _ = http(url, '/setclocktype', {'clocktype': '0'}, origin=url)
            check('return_to_classic', status == 200)

            def visible_clock():
                """Wait past the legitimate clear/reinitialization frame after HTTP ACK."""
                vm.capture_png(qmp, args.output / 'screen.png')
                pixels = vm.ppm_pixels(args.output / 'screen.ppm')
                colors = len(set(pixels[index:index + 3] for index in range(0, len(pixels), 3)))
                nonzero = sum(value != 0 for value in pixels)
                report['lcd_observation'] = {'colors': colors, 'nonzero_components': nonzero}
                return colors >= 2 and nonzero > 1000

            wait_for(visible_clock, 'No visible clock frame after theme initialization', seconds=30)
            check('lcd_has_content', visible_clock())
        check('guest_clock_from_udp_server', abs(vm.read_guest_clock(state) - 1781265600) < 300)
        uart = (state / 'uart.log').read_text(errors='replace')
        levels = {level: len(re.findall(r'(?m)^' + level + r' \(', uart)) for level in 'EWIDV'}
        report['uart_level_counts'] = levels
        check('logging_mode_visible', levels['D'] > 0 if firmware_debug else levels['I'] == levels['D'] == levels['V'] == 0)
        check('warnings_retained', levels['W'] > 0)
        check('startup_message_compiled_mode', (b'Reconstructed ESP32-C2 clock started' in (archive / 'app.bin').read_bytes()) is firmware_debug)
        log = (state / 'qemu.log').read_text(errors='replace')
        check('qemu_ntp_diagnostics_mode', ('C2 NTP reply' in log) is qemu_debug)
        check('no_panic', clean_uart(state))
        check('inputs_unchanged', all(sha(Path(name)) == value for name, value in pins.items()))
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
    finally:
        vm.seed_clock_network = original_seed
        if session:
            try:
                vm.control(state, 'stop')
                vm.ensure_stopped(state)
            except Exception as error:
                report['cleanup_error'], report['passed'] = str(error), False
        vm.save_json(args.output / 'report.json', report)
    print(json.dumps({key: report.get(key) for key in ('passed', 'checks', 'uart_level_counts', 'error', 'cleanup_error')}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
