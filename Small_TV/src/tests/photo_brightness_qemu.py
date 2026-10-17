"""Apply real HTTP brightness changes while photos wait for a 60-second timer."""
import argparse
import http.client
import json
from pathlib import Path
import socket
import struct
import sys
import time
from types import SimpleNamespace
from urllib.parse import urlsplit

from control_oracle import verify_inputs
from gdb_observer import Observer
from machine_oracle import ROOT
from photo_frame_replay import PhotoMachine
from photo_frames_qemu import native_entries
from qemu_storage import direct_flash_backing
from frame_replay import panel_rgb
import scene_qemu as scene
import weather_qemu as weather


def request(url, path, body=None):
    """Use the real form endpoint through an owned loopback listener without proxies."""
    endpoint = urlsplit(url)
    if endpoint.hostname != '127.0.0.1':
        raise ValueError('Only loopback is allowed')
    connection = http.client.HTTPConnection(endpoint.hostname, endpoint.port, timeout=20)
    try:
        connection.request('GET' if body is None else 'POST', path, body,
                           {'Content-Type': 'application/x-www-form-urlencoded', 'Connection': 'close', 'Origin': url})
        response = connection.getresponse()
        data = response.read(4097)
        if len(data) > 4096:
            raise AssertionError('Oversized brightness response')
        return response.status, data
    finally:
        connection.close()


def exercise(options, folder, variant, symbols, loop_end):
    """Observe a completed first fade, then require the slider to work during idle."""
    import compare
    from small_tv_http_test import clean_uart
    previous_seed = vm.seed_clock_network
    theme, mask = compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK
    compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = 'photo', 1

    def seed(data, firmware, state, yoradio, station_ssid=None):
        """Seed only a fresh owned flash copy, with a long photo interval and day duty100."""
        data = bytearray(compare.seed_settings(data, firmware, state, yoradio, station_ssid))
        struct.pack_into('<I', data, 0x3e7000+0x180, 100)
        struct.pack_into('<I', data, 0x3e7000+0x1a0, 60)
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
        entry = 0x4200bc36 if variant == 'original' else symbols['factory_photo_step']
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            result['checks']['direct_flash_backing'] = direct_flash_backing(qmp, folder)
            if not result['checks']['direct_flash_backing']:
                raise AssertionError('Flash integrity cannot be checked behind a snapshot overlay')
            while True:
                observer.breakpoint(entry); observer.continue_to(entry)
                code = observer.memory(entry, 4)
                state_pointer = 0x3fcc3a50 if variant == 'original' else observer.register(10)
                state = list(observer.memory(state_pointer, 2))
                event = bool(observer.memory(0x3fcc39f8, 1)[0]) if variant == 'original' else bool(observer.register(13))
                target = observer.register(1) if variant == 'original' else loop_end
                observer.breakpoint(entry, False)
                target_code = observer.memory(target, 4)
                observer.breakpoint(target); observer.continue_to(target); observer.breakpoint(target, False)
                if observer.memory(entry, 4) != code or observer.memory(target, 4) != target_code:
                    raise AssertionError('Breakpoint changed guest instructions')
                if event and state[0] == 5:
                    break
            address = (scene.cstring(observer, 0x3fcb7b84, 20) if variant == 'original' else
                       socket.inet_ntoa(observer.memory(symbols['last_station_address'], 4)))
            reference = PhotoMachine('factory', (ROOT/'Small_TV/full-flash.bin').read_bytes(),
                                     json.loads((ROOT/'Small_TV/assets/manifest.json').read_text()))
            reference.advance(2, 0, 1, address)
            expected = panel_rgb(reference.panel, 501)  # 50% endpoint -> duty4095 -> active-low501/1000.
            result['idle_state_before'] = list(observer.memory(state_pointer, 2))
            result['checks']['first_photo_complete'] = result['idle_state_before'] == [0, 1]
            observer.resume()
            url = session['web_urls']['station']
            started = weather.virtual_seconds(qmp)
            status, body = request(url, '/set_led_brightness', b'ledBrightness=50')
            result['http_status'] = status
            result['http_guest_seconds'] = weather.virtual_seconds(qmp)-started
            if status != 200:
                raise AssertionError('Brightness endpoint rejected the original form request')
            status, body = request(url, '/get_led_brightness')
            result['checks']['settings_changed'] = status == 200 and json.loads(body) == {'brightness': 50}

            class Memory:
                def memory(self, address, length):
                    """Read running MMIO/RAM through QMP without pausing or writing the guest."""
                    return weather.read_bytes(qmp, address, length)

            deadline = weather.virtual_seconds(qmp)+.5
            light = scene.backlight(Memory())
            while light['high_duty'] != 4095 and weather.virtual_seconds(qmp) < deadline:
                time.sleep(.02)
                light = scene.backlight(Memory())
            result['backlight'] = light
            result['after_request_guest_seconds'] = weather.virtual_seconds(qmp)-started-result['http_guest_seconds']
            result['checks']['idle_brightness_bounded'] = light['high_duty'] == 4095 and light['brightness'] == 501
            # Stop normally for a complete surface read; no target state is assigned.
            observer.interrupt()
            actual = scene.picture(qmp, folder, 'idle-brightness')
            result['different_pixels'] = sum(actual[i:i+3] != expected[i:i+3] for i in range(0, len(actual), 3))
            result['checks']['complete_photo_frame'] = result['different_pixels'] == 0
            result['checks']['no_new_fade'] = list(observer.memory(state_pointer, 2)) == [0, 1]
            result['qemu_rgb_sha256'], result['replayed_rgb_sha256'] = vm.digest(actual), vm.digest(expected)
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
        compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = theme, mask
        vm.save_json(folder/'photo-brightness-report.json', result)
    print('Photo idle brightness:', variant, result['passed'], result.get('backlight'), flush=True)
    return result


def main():
    """Keep identical observer bytes for negative/positive firmware comparisons."""
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
    fingerprints = [{'file': path.relative_to(ROOT).as_posix(), 'sha256': vm.digest(path.read_bytes())} for path in paths]
    helpers = {name: vm.digest((args.qemu_root/'tools'/name).read_bytes()) for name in
        ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'esp_elf.py')}
    result = {'passed': False, 'app_sha256': verify_inputs(),
        'source_sha256': json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())['source_sha256'],
        'native_elf_sha256': vm.digest((ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()),
        'qemu_sha256': vm.digest(Path(options.qemu).read_bytes()), 'helper_sha256': helpers,
        'profile_sha256': vm.digest(Path(options.hardware_profile).read_bytes()), 'test_inputs': fingerprints,
        'flows': {}, 'scope': __doc__}
    try:
        for variant in ('original', 'reconstructed'):
            result['flows'][variant] = exercise(options, args.output/variant, variant, symbols, loop_end)
        result['passed'] = all(row['passed'] for row in result['flows'].values())
    finally:
        fixture.close()
        result['inputs_unchanged'] = (verify_inputs() == result['app_sha256'] and
            vm.digest(Path(options.qemu).read_bytes()) == result['qemu_sha256'] and
            all(vm.digest((ROOT/row['file']).read_bytes()) == row['sha256'] for row in fingerprints) and
            all(vm.digest((args.qemu_root/'tools'/name).read_bytes()) == sha for name, sha in helpers.items()))
        result['passed'] &= result['inputs_unchanged']
        vm.save_json(args.output/'report.json', result)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
