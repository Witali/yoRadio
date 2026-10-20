"""Select the photo theme again during a fade and compare the next complete photograph."""
import argparse
from concurrent.futures import ThreadPoolExecutor
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


def first_photo_before_fade_finishes(observer, variant, symbols, loop_end):
    """Observe the first real photo draw, keeping three fade steps unexecuted."""
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
        if event and state[0] == 2:
            if list(observer.memory(pointer, 2)) != [3, 1]:
                raise AssertionError('First photo did not complete before the active fade window')
            return pointer


def exercise(options, folder, variant, symbols, loop_end):
    """Observe the factory blank-screen defect and require C to complete a fresh fade instead."""
    import compare
    from small_tv_http_test import http, clean_uart
    previous_seed = vm.seed_clock_network
    old_theme, old_mask = compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK
    compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = 'photo', 3

    def seed(data, firmware, state, yoradio, station_ssid=None):
        """Seed only an owned flash copy; automatic photo events cannot hide a lost command."""
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
    result = {'passed': False, 'checks': {}, 'photo_interval': 60}
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
            pointer = first_photo_before_fade_finishes(observer, variant, symbols, loop_end)
            result['state_before_request'] = list(observer.memory(pointer, 2))
            address = (scene.cstring(observer, 0x3fcb7b84, 20) if variant == 'original' else
                       socket.inet_ntoa(observer.memory(symbols['last_station_address'], 4)))
            reference = PhotoMachine('factory', (ROOT/'Small_TV/full-flash.bin').read_bytes(),
                                     json.loads((ROOT/'Small_TV/assets/manifest.json').read_text()))
            reference.advance(2, 1, 3, address)
            expected = panel_rgb(reference.panel, 1000)
            url = session['web_urls']['station']
            command = 0x4200d850 if variant == 'original' else symbols['settings_select_theme']
            command_code = observer.memory(command, 4)
            observer.breakpoint(command)
            requested = weather.virtual_seconds(qmp)
            with ThreadPoolExecutor(max_workers=1) as executor:
                pending = executor.submit(http, url, '/setclocktype', {'clocktype': '2'}, origin=url, timeout=30)
                observer.continue_to(command)
                result['state_when_command_executes'] = list(observer.memory(pointer, 2))
                observer.breakpoint(command, False)
                if observer.memory(command, 4) != command_code:
                    raise AssertionError('Command breakpoint changed instructions')
                observer.resume()
                status, body = pending.result(timeout=35)
            result['http_status'] = status
            result['checks']['active_fade_command'] = result['state_when_command_executes'][0] in (3, 4, 5)
            result['checks']['first_photo_complete'] = result['state_before_request'] == [3, 1]
            result['checks']['http_command_accepted'] = status == 200
            if not all(result['checks'].values()):
                raise AssertionError('Did not exercise a valid command during an active fade')
            deadline = requested+2
            while True:
                current = list(weather.read_bytes(qmp, pointer, 2))
                if current == [0, 2] or weather.virtual_seconds(qmp) >= deadline:
                    break
                time.sleep(.02)
            result['guest_seconds'] = weather.virtual_seconds(qmp)-requested
            observer.interrupt()
            actual = scene.picture(qmp, folder, 'after-active-command')
            result['state_after'] = current
            result['backlight'] = scene.backlight(observer)
            result['compared_pixels'] = 57600
            result['different_pixels'] = sum(actual[i:i+3] != expected[i:i+3] for i in range(0, len(actual), 3))
            result['all_pixels_black'] = not any(actual)
            result['qemu_rgb_sha256'], result['replayed_rgb_sha256'] = vm.digest(actual), vm.digest(expected)
            result['literal_output_matches_fixed_requirement'] = current == [0, 2] and result['different_pixels'] == 0
            if variant == 'original':
                result['checks']['known_factory_blank_screen'] = (
                    current == [0, 1] and result['all_pixels_black'] and result['different_pixels'] > 0 and
                    result['backlight']['high_duty'] == 0)
            else:
                result['checks']['complete_next_photo'] = result['literal_output_matches_fixed_requirement']
                result['checks']['bounded_response'] = result['guest_seconds'] <= 2
                result['checks']['full_backlight'] = result['backlight']['high_duty'] == 0
            result['checks']['hardware_breakpoints_only'] = True
            result['checks']['no_guest_state_writes'] = True
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
            result['checks']['no_panic'] = clean_uart(folder)
            result['passed'] &= all(result['checks'].values())
        vm.seed_clock_network = previous_seed
        compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = old_theme, old_mask
        vm.save_json(folder/'photo-reinit-report.json', result)
    print('Photo active reinit:', variant, result['passed'], result.get('state_when_command_executes'),
          result.get('state_after'), result.get('different_pixels'), flush=True)
    return result


def main():
    """Bind the identical before/after observer to executable, profile and helper hashes."""
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
        ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'esp_elf.py', 'small_tv_display.py')}
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
            vm.digest((ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()) == result['native_elf_sha256'] and
            vm.digest(Path(options.qemu).read_bytes()) == result['qemu_sha256'] and
            all(vm.digest((ROOT/row['file']).read_bytes()) == row['sha256'] for row in inputs) and
            all(vm.digest((args.qemu_root/'tools'/name).read_bytes()) == sha for name, sha in helpers.items()))
        result['passed'] &= result['inputs_unchanged']
        vm.save_json(args.output/'report.json', result)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
