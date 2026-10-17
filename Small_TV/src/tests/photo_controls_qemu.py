"""Repeat photo-theme commands through real HTTP and observe each resulting complete image."""
import argparse
import json
from pathlib import Path
import socket
import struct
import sys
import time
from types import SimpleNamespace

from control_oracle import verify_inputs
from frame_replay import panel_rgb
from gdb_observer import Observer
from machine_oracle import ROOT
from photo_frame_replay import PhotoMachine
from photo_frames_qemu import native_entries
from qemu_storage import direct_flash_backing
import scene_qemu as scene
import weather_qemu as weather


def first_idle(observer, variant, symbols, loop_end):
    """Observe the actual first complete six-step fade, leaving the CPU normally paused."""
    entry = 0x4200bc36 if variant == 'original' else symbols['factory_photo_step']
    while True:
        observer.breakpoint(entry); observer.continue_to(entry)
        code = observer.memory(entry, 4)
        pointer = 0x3fcc3a50 if variant == 'original' else observer.register(10)
        state = list(observer.memory(pointer, 2))
        event = bool(observer.memory(0x3fcc39f8, 1)[0]) if variant == 'original' else bool(observer.register(13))
        target = observer.register(1) if variant == 'original' else loop_end
        target_code = observer.memory(target, 4)
        observer.breakpoint(entry, False)
        observer.breakpoint(target); observer.continue_to(target); observer.breakpoint(target, False)
        if observer.memory(entry, 4) != code or observer.memory(target, 4) != target_code:
            raise AssertionError('Hardware breakpoint changed executable bytes')
        if event and state[0] == 5:
            return pointer


def exercise(options, folder, variant, symbols, loop_end):
    """Require repeated identical commands to retain round-robin position and trigger new fades."""
    import compare
    from small_tv_http_test import http, clean_uart
    previous_seed = vm.seed_clock_network
    old_theme, old_mask = compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK
    compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = 'photo', 3

    def seed(data, firmware, state, yoradio, station_ssid=None):
        """Seed only an owned flash copy, suppressing automatic timer events during each command."""
        data = bytearray(compare.seed_settings(data, firmware, state, yoradio, station_ssid))
        for offset, value in ((0x180, 0), (0x1a0, 60)):
            struct.pack_into('<I', data, 0x3e7000+offset, value)
        return data

    vm.seed_clock_network = seed
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0)); port = reservation.getsockname()[1]
    options = SimpleNamespace(**{**vars(options), 'firmware': variant, 'network': 'clock',
                                'persistent': True, 'paused': True, 'gdb_port': port})
    folder.mkdir(parents=True, exist_ok=False)
    result = {'passed': False, 'checks': {}, 'reselects': []}
    session = observer = None
    immutable = None
    ranges = ((0, 0x9000), (0x10000, 0x3e7000))
    try:
        session, prepared = vm.launch(options, folder)
        result['sources'] = prepared['sources']
        flash = (folder/'flash.bin').read_bytes()
        immutable = [vm.digest(flash[a:b]) for a, b in ranges]
        observer = Observer(port)
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            result['checks']['direct_flash_backing'] = direct_flash_backing(qmp, folder)
            if not result['checks']['direct_flash_backing']:
                raise AssertionError('Flash integrity cannot be checked behind a snapshot overlay')
            pointer = first_idle(observer, variant, symbols, loop_end)
            initial = list(observer.memory(pointer, 2))
            result['checks']['first_photo_complete'] = initial == [0, 1]
            address = (scene.cstring(observer, 0x3fcb7b84, 20) if variant == 'original' else
                       socket.inet_ntoa(observer.memory(symbols['last_station_address'], 4)))
            reference = PhotoMachine('factory', (ROOT/'Small_TV/full-flash.bin').read_bytes(),
                                     json.loads((ROOT/'Small_TV/assets/manifest.json').read_text()))
            url = session['web_urls']['station']
            generation = symbols.get('generation') if variant == 'reconstructed' else None
            revision = symbols.get('theme_selection_generation') if variant == 'reconstructed' else None
            if generation:
                result['configuration_generation_before'] = int.from_bytes(observer.memory(generation, 4), 'little')
            if revision:
                result['theme_requests_before'] = int.from_bytes(observer.memory(revision, 4), 'little')
            for index, selected in enumerate((1, 0, 1)):
                reference.advance(2, selected, 3, address)
                expected = panel_rgb(reference.panel, 1000)
                observer.resume()
                status, body = http(url, '/get_display_time', timeout=20)
                if status != 200 or json.loads(body) != {'displaytime': 60}:
                    raise AssertionError('Photo interval did not load')
                requested = weather.virtual_seconds(qmp)
                status, _ = http(url, '/setclocktype', {'clocktype': '2'}, origin=url, timeout=20)
                status_get, body = http(url, '/getclocktype', timeout=20)
                if status != 200 or status_get != 200 or body != b'2':
                    raise AssertionError('Original same-theme HTTP form failed')
                target_state = [0, selected+1]
                deadline = weather.virtual_seconds(qmp)+2
                while True:
                    current = list(weather.read_bytes(qmp, pointer, 2))
                    if current == target_state or weather.virtual_seconds(qmp) >= deadline:
                        break
                    time.sleep(.02)
                elapsed = weather.virtual_seconds(qmp)-requested
                observer.interrupt()
                actual = scene.picture(qmp, folder, 'repeat-'+str(index))
                light = scene.backlight(observer)
                different = sum(actual[i:i+3] != expected[i:i+3] for i in range(0, len(actual), 3))
                row = {'selected_slot': selected, 'state_after': current, 'expected_state': target_state,
                       'post_status': status, 'guest_seconds': elapsed, 'different_pixels': different,
                       'compared_pixels': 57600, 'qemu_rgb_sha256': vm.digest(actual),
                       'replayed_rgb_sha256': vm.digest(expected), 'backlight': light,
                       'passed': current == target_state and different == 0 and elapsed <= 2 and
                                 light['high_duty'] == 0 and light['brightness'] == 1000}
                result['reselects'].append(row)
                print('Photo repeated theme:', variant, index, row['passed'], current, different, elapsed, flush=True)
                if not row['passed']:
                    break
            result['checks']['three_same_theme_commands'] = len(result['reselects']) == 3 and all(
                row['passed'] for row in result['reselects'])
            if generation:
                result['configuration_generation_after'] = int.from_bytes(observer.memory(generation, 4), 'little')
                result['checks']['no_redundant_configuration_revision'] = (
                    result['configuration_generation_before'] == result['configuration_generation_after'])
            if revision:
                result['theme_requests_after'] = int.from_bytes(observer.memory(revision, 4), 'little')
                result['checks']['explicit_theme_requests'] = result['theme_requests_after']-result['theme_requests_before'] == 3
            result['checks']['hardware_breakpoints_only'] = True
            result['checks']['no_guest_state_writes'] = True
        result['passed'] = all(result['checks'].values())
    except Exception as error:
        result['error'] = str(error)
        raise
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
            result['checks']['no_panic'] = clean_uart(folder)
            result['passed'] &= all(result['checks'].values())
        vm.seed_clock_network = previous_seed
        compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = old_theme, old_mask
        vm.save_json(folder/'photo-controls-report.json', result)
    return result


def main():
    """Bind negative and positive same-command observations to exact executable and observer inputs."""
    global vm
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dependency-root', type=Path, default=ROOT)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.qemu_root/'tools'))
    sys.path.insert(0, str(ROOT/'Small_TV/qemu/parity'))
    import small_tv_vm as vm
    from small_tv_http_test import wait_for
    scene.vm, weather.vm, weather.wait_for = vm, vm, wait_for
    fixture = weather.WeatherFixture(['Shenzhen,CN']); fixture.set_response(200)
    options = SimpleNamespace(yoradio=str(ROOT), qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'), display='none',
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        service_port=fixture.port)
    args.output.mkdir(parents=True, exist_ok=False)
    symbols, loop_end = native_entries()
    paths = [Path(__file__), *[Path(__file__).with_name(name) for name in
        ('photo_frames_qemu.py', 'photo_frame_replay.py', 'photo_frame_contract.py', 'photo_controls_contract.py', 'qemu_storage.py', 'jpeg_oracle.py',
         'scene_qemu.py', 'frame_replay.py', 'machine_oracle.py', 'classic_oracle.py', 'control_oracle.py',
         'weather_render_oracle.py', 'weather_qemu.py', 'gdb_observer.py')],
         ROOT/'Small_TV/qemu/parity/compare.py', Path(options.hardware_profile)]
    inputs = [{'file': path.relative_to(ROOT).as_posix(), 'sha256': vm.digest(path.read_bytes())} for path in paths]
    helpers = {name: vm.digest((args.qemu_root/'tools'/name).read_bytes()) for name in
        ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'esp_elf.py')}
    result = {'passed': False, 'app_sha256': verify_inputs(),
        'source_sha256': json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())['source_sha256'],
        'native_elf_sha256': vm.digest((ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()),
        'qemu_sha256': vm.digest(Path(options.qemu).read_bytes()), 'helper_sha256': helpers,
        'profile_sha256': vm.digest(Path(options.hardware_profile).read_bytes()), 'test_inputs': inputs,
        'flows': {}, 'scope': __doc__}
    try:
        for variant in ('original', 'reconstructed'):
            result['flows'][variant] = exercise(options, args.output/variant, variant, symbols, loop_end)
        result['passed'] = all(flow['passed'] for flow in result['flows'].values())
    finally:
        fixture.close()
        result['inputs_unchanged'] = (verify_inputs() == result['app_sha256'] and
            vm.digest(Path(options.qemu).read_bytes()) == result['qemu_sha256'] and
            all(vm.digest((ROOT/row['file']).read_bytes()) == row['sha256'] for row in inputs) and
            all(vm.digest((args.qemu_root/'tools'/name).read_bytes()) == sha for name, sha in helpers.items()))
        result['passed'] &= result['inputs_unchanged']
        vm.save_json(args.output/'report.json', result)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
