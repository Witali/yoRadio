"""Observe real HTTP city commands reaching all four native theme initializers.

This checks command/renderer transitions and completed output, not factory pixel
equivalence, physical RF or 24h acceptance. photo_reinit_qemu --command city
separately compares the active-fade case with literal factory pixels.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
from pathlib import Path
import socket
import struct
import sys
from types import SimpleNamespace

from control_oracle import verify_inputs
from gdb_observer import Observer
from machine_oracle import ROOT
from photo_frames_qemu import native_entries
from photo_controls_qemu import first_idle
from qemu_storage import direct_flash_backing
import scene_qemu as scene
import weather_qemu as weather

THEMES = {
    'classic': ('factory_draw_classic', 15),
    'simple': ('factory_draw_simple', 13),
    'photo': ('factory_photo_step', None),
    'dial': ('factory_draw_dial', 12),
}


def completed_reset(observer, symbols, loop_end, theme):
    """Check the first initialization event and complete its coordinator iteration."""
    symbol, reset_register = THEMES[theme]
    entry = symbols[symbol]
    observer.breakpoint(entry)
    try:
        # The first event after a city command must be initialization, not a
        # later periodic repaint that could hide a dropped transient revision.
        observer.continue_to(entry)
        # FIXED_TEST: at the boot stop the app's flash mapping is not installed.
        # Sample executable bytes after reaching the instruction, as the existing
        # photo observers do; compare them again after removing the breakpoint.
        code = observer.memory(entry, 4)
        if reset_register is None:
            state = list(observer.memory(observer.register(10), 2))
            reset = state[0] == 0 and bool(observer.register(13))
        else:
            state = None
            reset = bool(observer.register(reset_register))
        if not reset:
            raise AssertionError(f'{theme}: first renderer event lost the city reset')
    finally:
        observer.breakpoint(entry, False)
    end_code = observer.memory(loop_end, 4)
    observer.breakpoint(loop_end)
    try:
        observer.continue_to(loop_end)
    finally:
        observer.breakpoint(loop_end, False)
    if observer.memory(entry, 4) != code or observer.memory(loop_end, 4) != end_code:
        raise AssertionError('Hardware breakpoint modified code')
    return dict(initializer=symbol, reset=True, photo_state_before=state)


def exercise(vm, options, folder, theme, symbols, loop_end):
    """Use only disposable flash and this flow's own QMP/RSP sessions."""
    import compare
    from small_tv_http_test import http, clean_uart
    old_seed = vm.seed_clock_network
    old_theme, old_mask = compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK
    compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = theme, 3

    def seed(data, firmware, state, yoradio, station_ssid=None):
        """Keep automatic photo intervals from masking a dropped city command."""
        data = bytearray(compare.seed_settings(data, firmware, state, yoradio, station_ssid))
        struct.pack_into('<I', data, 0x3e7000+0x1a0, 60)
        return data

    vm.seed_clock_network = seed
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    flow_options = SimpleNamespace(**{**vars(options), 'firmware': 'reconstructed',
        'network': 'clock', 'persistent': True, 'paused': True, 'gdb_port': port})
    folder.mkdir(parents=True, exist_ok=False)
    result = dict(passed=False, theme=theme, commands=[], checks={})
    session = observer = None
    immutable = None
    ranges = ((0, 0x9000), (0x10000, 0x3e7000))
    try:
        session, prepared = vm.launch(flow_options, folder)
        result['sources'] = prepared['sources']
        flash = (folder/'flash.bin').read_bytes()
        immutable = [vm.digest(flash[a:b]) for a, b in ranges]
        observer = Observer(port)
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            result['checks']['direct_flash_backing'] = direct_flash_backing(qmp, folder)
            if not result['checks']['direct_flash_backing']:
                raise AssertionError('Unobservable snapshot overlay')
            result['initial_render'] = completed_reset(observer, symbols, loop_end, theme)
            url = session['web_urls']['station']
            command = symbols['settings_update_city']
            command_code = observer.memory(command, 4)
            for label, city in (('same-city', 'Shenzhen,CN'), ('new-city', 'Budapest,HU')):
                observer.breakpoint(command)
                with ThreadPoolExecutor(max_workers=1) as executor:
                    pending = executor.submit(http, url, '/updateCity', {'city': city},
                                              origin=url, timeout=30)
                    observer.continue_to(command)
                    observer.breakpoint(command, False)
                    row = completed_reset(observer, symbols, loop_end, theme)
                    if theme == 'photo':
                        # The first fade iteration deliberately blanks the LCD.
                        # Require the real six-step transition to finish before
                        # testing completed output, as in the existing photo gate.
                        pointer = first_idle(observer, 'reconstructed', symbols, loop_end)
                        row['photo_state_after'] = list(observer.memory(pointer, 2))
                    pixels = scene.picture(qmp, folder, label)
                    row.update(case=label, city=city, completed_rgb_sha256=vm.digest(pixels),
                               pixels=len(pixels)//3)
                    if len(pixels) != 240*240*3 or not any(pixels):
                        raise AssertionError('Missing completed display output')
                    observer.resume()
                    row['http_status'], _ = pending.result(timeout=35)
                    observer.interrupt()
                if row['http_status'] != 200:
                    raise AssertionError('City command rejected')
                result['commands'].append(row)
            if observer.memory(command, 4) != command_code:
                raise AssertionError('Command breakpoint changed code')
            result['checks'].update(every_city_reinitializes=True, completed_output=True,
                hardware_breakpoints_only=True, no_guest_state_writes=True)
        result['passed'] = all(result['checks'].values())
    finally:
        if observer:
            observer.close()
        if session:
            try:
                vm.control(folder, 'stop')
            finally:
                vm.ensure_stopped(folder)
            flash = (folder/'flash.bin').read_bytes()
            result['checks']['executable_media_unchanged'] = immutable is not None and all(
                vm.digest(flash[a:b]) == sha for (a, b), sha in zip(ranges, immutable))
            result['checks']['uart_no_panic'] = clean_uart(folder)
            result['passed'] &= all(result['checks'].values())
        vm.seed_clock_network = old_seed
        compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = old_theme, old_mask
        vm.save_json(folder/'city-theme-report.json', result)
    if not result['passed']:
        raise AssertionError(f'City theme checks failed: {theme}')
    print('PASS city theme:', theme, flush=True)
    return result


def main():
    """Bind each observed transition to the exact build and frozen QEMU inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dependency-root', type=Path, default=ROOT)
    parser.add_argument('--qemu-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.qemu_root/'tools'))
    sys.path.insert(0, str(ROOT/'Small_TV/qemu/parity'))
    import small_tv_vm as vm
    from small_tv_http_test import wait_for
    scene.vm, weather.vm, weather.wait_for = vm, vm, wait_for
    args.output.mkdir(parents=True, exist_ok=False)
    app_sha = verify_inputs(dependency_root=args.dependency_root)
    symbols, loop_end = native_entries()
    profile = ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'
    rom = args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
    archive = ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    paths = [Path(__file__), profile, rom, ROOT/'Small_TV/full-flash.bin',
             ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf']
    paths += list(Path(__file__).parent.glob('*.py'))
    paths += [ROOT/'Small_TV/qemu/parity/compare.py']
    paths += [archive/name for name in ('app.bin', 'bootloader.bin', 'partition-table.bin',
                                      'assets.bin', 'manifest.json', 'source-manifest.json')]
    frozen = args.qemu_root/'frozen-inputs.json'
    paths += [frozen] + [args.qemu_root/row['file'] for row in json.loads(frozen.read_text())['files']]
    pins = {str(path.resolve()): vm.digest(path.read_bytes()) for path in paths}
    report = dict(passed=False, all_functionality_verified=False, scope=__doc__,
        app_sha256=app_sha, inputs_sha256=pins, flows={},
        source_sha256=json.loads((archive/'manifest.json').read_text())['source_sha256'],
        started_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    fixture = weather.WeatherFixture(['Shenzhen,CN', 'Budapest,HU'])
    fixture.set_response(200)
    options = SimpleNamespace(yoradio=str(ROOT), qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        hardware_profile=str(profile), display='none', rom_elf=str(rom), service_port=fixture.port)
    try:
        for theme in THEMES:
            report['flows'][theme] = exercise(vm, options, args.output/theme, theme, symbols, loop_end)
        report['passed'] = all(row['passed'] for row in report['flows'].values())
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        fixture.close()
        report['inputs_unchanged'] = all(vm.digest(Path(path).read_bytes()) == sha for path, sha in pins.items())
        report['passed'] &= report['inputs_unchanged']
        report['ended_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        vm.save_json(args.output/'report.json', report)


if __name__ == '__main__':
    main()
