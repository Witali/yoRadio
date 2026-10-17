"""Change real HTTP photo masks and intervals during an active fade without rewriting guest state."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import socket
import struct
import sys
from types import SimpleNamespace

from control_oracle import verify_inputs
from frame_replay import panel_rgb
from gdb_observer import Observer
from machine_oracle import ROOT, layout
from photo_frame_replay import PhotoMachine
from photo_frames_qemu import native_entries
from qemu_storage import direct_flash_backing
from photo_settings_contract import validate_photo_settings, contract_rejection_checks
import scene_qemu as scene
import weather_qemu as weather

CASES = [dict(name='disable-before-image', mask=3, interval=3, phase=0, slot=0, enabled=False, expected_mask=2),
         dict(name='disable-after-image', mask=3, interval=3, phase=2, slot=1, enabled=False, expected_mask=1),
         dict(name='disable-all', mask=1, interval=3, phase=2, slot=0, enabled=False, expected_mask=0),
         dict(name='enable-next', mask=1, interval=3, phase=2, slot=1, enabled=True, expected_mask=3),
         dict(name='shorten-interval', mask=3, interval=60, phase=2, new_interval=3, expected_mask=3),
         dict(name='lengthen-interval', mask=3, interval=5, phase=2, new_interval=9, expected_mask=3)]


def step(observer, variant, symbols, loop_end):
    """Execute one actual coordinator pass through hardware breakpoints and return its semantic state."""
    entry = 0x4200bc36 if variant == 'original' else symbols['factory_photo_step']
    observer.breakpoint(entry); observer.continue_to(entry)
    entry_code = observer.memory(entry, 4)
    pointer = 0x3fcc3a50 if variant == 'original' else observer.register(10)
    before = list(observer.memory(pointer, 2))
    event = bool(observer.memory(0x3fcc39f8, 1)[0]) if variant == 'original' else bool(observer.register(13))
    target = observer.register(1) if variant == 'original' else loop_end
    target_code = observer.memory(target, 4)
    observer.breakpoint(entry, False)
    observer.breakpoint(target); observer.continue_to(target); observer.breakpoint(target, False)
    if observer.memory(entry, 4) != entry_code or observer.memory(target, 4) != target_code:
        raise AssertionError('Hardware breakpoint changed executable bytes')
    return dict(pointer=pointer, before=before, after=list(observer.memory(pointer, 2)), event=event)


def timer(observer, variant, symbols):
    """Read the actual ISR counters without depending on native structure packing."""
    if variant == 'original':
        return dict(photo=observer.memory(0x3fcc39ca, 1)[0], subsecond=observer.memory(0x3fcc39cc, 1)[0])
    size, fields = layout('factory_timer_t')
    data = observer.memory(symbols['timer_state'], size)
    return dict(photo=data[fields['photo_seconds']], subsecond=data[fields['subsecond_ticks']])


def apply_command(observer, qmp, session, variant, symbols, pointer, case, capture):
    """Observe the command at its actual publication instruction, including the fade and timer counters."""
    from small_tv_http_test import http
    interval = 'new_interval' in case
    path = '/set_display_time' if interval else '/set_checkbox_state'
    payload = {'display_time': case['new_interval']} if interval else {
        'checkbox_id': 'file'+str(case['slot']+1)+'-switch', 'checked': case['enabled']}
    # Original addresses are the interval store and the shared post-mask-store
    # path. Native settings_replace publishes both fields under its real mutex.
    command = (0x4200f78a if interval else 0x4200e3b2) if variant == 'original' else symbols['settings_replace']
    code = observer.memory(command, 4)
    observer.breakpoint(command)
    row = {'path': path, 'payload': payload, 'requested_at': weather.virtual_seconds(qmp)}
    with ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(http, session['web_urls']['station'], path, payload,
                                  origin=session['web_urls']['station'], timeout=40)
        observer.continue_to(command)
        row['state_at_command'] = list(observer.memory(pointer, 2))
        row['timer_before'] = timer(observer, variant, symbols)
        observer.breakpoint(command, False)
        if variant == 'reconstructed' or interval:
            target = observer.register(1) if variant == 'reconstructed' else 0x4200f78e
            target_code = observer.memory(target, 4)
            observer.breakpoint(target); observer.continue_to(target); observer.breakpoint(target, False)
            if observer.memory(target, 4) != target_code:
                raise AssertionError('Publication breakpoint changed instructions')
        row['state_after_command'] = list(observer.memory(pointer, 2))
        row['timer_after'] = timer(observer, variant, symbols)
        row['published_at'] = weather.virtual_seconds(qmp)
        if observer.memory(command, 4) != code:
            raise AssertionError('Command breakpoint changed instructions')
        # Keep the hardware-stop sequence active through both frames. Waiting
        # for HTTP here would let a descheduled host thread miss the first
        # fade completion while the guest continued normally in the meantime.
        row['capture_started_at'] = weather.virtual_seconds(qmp)
        try:
            capture(row)
        except BaseException:
            observer.resume()
            raise
        row['capture_finished_at'] = weather.virtual_seconds(qmp)
        observer.resume()
        row['http_status'], _ = pending.result(timeout=45)
        get_path = '/get_display_time' if interval else '/get_checkbox_state'
        status, body = http(session['web_urls']['station'], get_path, timeout=30)
        row['get_status'], row['saved_value'] = status, json.loads(body)
        observer.interrupt()
        row['http_observed_at'] = weather.virtual_seconds(qmp)
    return row


def exercise(options, folder, variant, case, symbols, loop_end):
    """Require in-flight changes to preserve the current fade, future selection and timer progress."""
    import compare
    from small_tv_http_test import clean_uart
    previous_seed = vm.seed_clock_network
    old_theme, old_mask = compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK
    compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = 'photo', case['mask']

    def seed(data, firmware, state, yoradio, station_ssid=None):
        """Seed only a fresh owned copy with synthetic settings and public fixture photos."""
        data = bytearray(compare.seed_settings(data, firmware, state, yoradio, station_ssid))
        for offset, value in ((0x180, 0), (0x190, 0), (0x1a0, case['interval'])):
            struct.pack_into('<I', data, 0x3e7000+offset, value)
        return data

    vm.seed_clock_network = seed
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0)); port = reservation.getsockname()[1]
    options = SimpleNamespace(**{**vars(options), 'firmware': variant, 'network': 'clock',
                                'persistent': True, 'paused': True, 'gdb_port': port})
    folder.mkdir(parents=True, exist_ok=False)
    result = {'passed': False, 'case': case, 'checks': {}, 'frames': []}
    session = observer = None
    ranges = ((0, 0x9000), (0x10000, 0x3e7000))
    immutable = None
    try:
        session, prepared = vm.launch(options, folder)
        result['sources'] = prepared['sources']
        flash = (folder/'flash.bin').read_bytes()
        immutable = [vm.digest(flash[a:b]) for a, b in ranges]
        observer = Observer(port)
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            result['checks']['direct_flash_backing'] = direct_flash_backing(qmp, folder)
            if not result['checks']['direct_flash_backing']:
                raise AssertionError('Guest flash is hidden behind a snapshot overlay')
            for _ in range(500):
                observed = step(observer, variant, symbols, loop_end)
                if observed['event'] and observed['before'][0] == case['phase']:
                    break
            else:
                raise AssertionError('No initial active fade')
            result['state_before_request'] = observed['after']
            address = (scene.cstring(observer, 0x3fcb7b84, 20) if variant == 'original' else
                       socket.inet_ntoa(observer.memory(symbols['last_station_address'], 4)))
            reference = PhotoMachine('factory', (ROOT/'Small_TV/full-flash.bin').read_bytes(),
                                     json.loads((ROOT/'Small_TV/assets/manifest.json').read_text()))
            mask = case['expected_mask']
            first_slot = 1 if case['phase'] == 0 else 0
            reference.advance(2, first_slot, mask if case['phase'] == 0 else case['mask'], address)

            def capture(command):
                """Observe both exact fade completions before any asynchronous HTTP-response wait."""
                result['command'] = command
                allowed = (1, 2) if case['phase'] == 0 else (3, 4, 5)
                result['checks']['command_during_requested_fade'] = command['state_at_command'][0] in allowed
                result['checks']['no_fade_reset'] = command['state_after_command'] == command['state_at_command']
                if 'new_interval' in case:
                    result['checks']['timer_not_reset'] = command['timer_after'] == command['timer_before']
                if not all(result['checks'].values()):
                    raise AssertionError('Command did not apply inside the requested fade window')
                next_slot = first_slot+1
                for frame in range(2):
                    deadline = weather.virtual_seconds(qmp)+case.get('new_interval', case['interval'])*1.1+4
                    while True:
                        observed = step(observer, variant, symbols, loop_end)
                        if frame and observed['event'] and observed['before'][0] == 0:
                            result['next_fade_started_at'] = weather.virtual_seconds(qmp)
                        if observed['event'] and observed['before'][0] == 5:
                            break
                        if weather.virtual_seconds(qmp) > deadline:
                            raise AssertionError('No completed photo within the active interval')
                    if frame:
                        replay = reference.advance(2, next_slot, mask, address)
                        next_slot = replay['next_slot']
                    actual = scene.picture(qmp, folder, 'complete-'+str(frame))
                    expected = panel_rgb(reference.panel, 1000)
                    light = scene.backlight(observer)
                    different = sum(actual[i:i+3] != expected[i:i+3] for i in range(0, len(actual), 3))
                    row = {'state_after': observed['after'], 'expected_state': [0, next_slot],
                        'guest_seconds': weather.virtual_seconds(qmp), 'compared_pixels': 57600,
                        'different_pixels': different, 'qemu_rgb_sha256': vm.digest(actual),
                        'replayed_rgb_sha256': vm.digest(expected), 'backlight': light}
                    row['passed'] = observed['after'] == [0, next_slot] and different == 0 and light['high_duty'] == 0
                    result['frames'].append(row)
                    if not frame:
                        # Factory seconds are eleven 100-ms ticks. The current
                        # hardware-timer phase makes the next event predictable
                        # without resetting counters or advancing virtual time.
                        interval = case.get('new_interval', case['interval'])
                        period_address = 0x3fcb7d3c if variant == 'original' else symbols['photo_interval']
                        row['active_interval'] = int.from_bytes(observer.memory(period_address, 4), 'little')
                        row['timer'] = timer(observer, variant, symbols)
                        if row['active_interval'] != interval or not 0 <= row['timer']['photo'] <= 255:
                            raise AssertionError('Timer did not apply the saved interval')
                        # A newly shortened interval can be below the retained
                        # counter. Its >= test then fires at the next second,
                        # rather than restarting or waiting for byte overflow.
                        ticks = max(1, interval-row['timer']['photo'])*11-row['timer']['subsecond']
                        result['next_event_window'] = [row['guest_seconds']+(ticks-1)*.1,
                                                       row['guest_seconds']+ticks*.1+.3]
                    if not row['passed']:
                        raise AssertionError('Complete image or round-robin state differs after the setting change')
                result['checks'].update(two_complete_frames=True, hardware_breakpoints_only=True, no_guest_state_writes=True)
                lower, upper = result['next_event_window']
                result['checks']['next_event_keeps_counter_phase'] = lower <= result.get('next_fade_started_at', -1) <= upper

            command = apply_command(observer, qmp, session, variant, symbols, observed['pointer'], case, capture)
            result['command'] = command
            result['checks']['http_accepted'] = command['http_status'] == command['get_status'] == 200
            if 'new_interval' in case:
                result['checks']['saved_value'] = command['saved_value'] == {'displaytime': case['new_interval']}
            else:
                saved_mask = sum(1 << slot for slot in range(5) if command['saved_value']['file'+str(slot+1)+'_switch'])
                result['checks']['saved_value'] = saved_mask == case['expected_mask']
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
        vm.save_json(folder/'photo-settings-report.json', result)
    print('Photo setting during fade:', variant, case['name'], result['passed'], flush=True)
    return result


def main():
    """Run six independent live HTTP scenarios on both immutable executable images."""
    global vm
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--dependency-root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--variants', nargs='+', choices=('original', 'reconstructed'), default=['original', 'reconstructed'])
    parser.add_argument('--cases', nargs='+', choices=[case['name'] for case in CASES])
    args = parser.parse_args()
    sys.path[:0] = [str(args.qemu_root/'tools'), str(ROOT/'Small_TV/qemu/parity')]
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
        ('photo_frames_qemu.py', 'photo_frame_replay.py', 'photo_frame_contract.py', 'photo_settings_contract.py', 'qemu_storage.py', 'jpeg_oracle.py',
         'scene_qemu.py', 'frame_replay.py', 'machine_oracle.py', 'classic_oracle.py', 'control_oracle.py',
         'weather_render_oracle.py', 'weather_qemu.py', 'gdb_observer.py')],
         ROOT/'Small_TV/qemu/parity/compare.py', Path(options.hardware_profile)]
    archive = ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    paths += [archive/name for name in ('app.bin', 'bootloader.bin', 'partition-table.bin', 'assets.bin',
                                      'manifest.json', 'source-manifest.json', 'assets-manifest.json')]
    fingerprints = [{'file': path.relative_to(ROOT).as_posix(), 'sha256': vm.digest(path.read_bytes())} for path in paths]
    helpers = {name: vm.digest((args.qemu_root/'tools'/name).read_bytes()) for name in
        ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'esp_elf.py')}
    result = {'passed': False, 'app_sha256': verify_inputs(),
        'source_sha256': json.loads((archive/'manifest.json').read_text())['source_sha256'],
        'native_elf_sha256': vm.digest((ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()),
        'factory_elf_sha256': vm.digest((ROOT/'.build/small-tv-reverse/factory-analysis.elf').read_bytes()),
        'qemu_sha256': vm.digest(Path(options.qemu).read_bytes()), 'helper_sha256': helpers,
        'profile_sha256': vm.digest(Path(options.hardware_profile).read_bytes()), 'test_inputs': fingerprints,
        'flows': {}, 'scope': __doc__}
    rom_relative = Path('.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf')
    result['rom_sha256'] = vm.digest((ROOT/rom_relative).read_bytes())
    if vm.digest((args.dependency_root/rom_relative).read_bytes()) != result['rom_sha256']:
        raise ValueError('QEMU and instruction replay ROM bytes differ')
    try:
        for variant in args.variants:
            result['flows'][variant] = {}
            for case in CASES:
                if not args.cases or case['name'] in args.cases:
                    result['flows'][variant][case['name']] = exercise(options, args.output/(variant+'-'+case['name']),
                                                                    variant, case, symbols, loop_end)
        result['passed'] = all(flow['passed'] for flows in result['flows'].values() for flow in flows.values())
    finally:
        fixture.close()
        result['inputs_unchanged'] = (verify_inputs() == result['app_sha256'] and
            vm.digest((ROOT/rom_relative).read_bytes()) == result['rom_sha256'] and
            vm.digest((args.dependency_root/rom_relative).read_bytes()) == result['rom_sha256'] and
            vm.digest((ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()) == result['native_elf_sha256'] and
            vm.digest((ROOT/'.build/small-tv-reverse/factory-analysis.elf').read_bytes()) == result['factory_elf_sha256'] and
            vm.digest(Path(options.qemu).read_bytes()) == result['qemu_sha256'] and
            all(vm.digest((ROOT/row['file']).read_bytes()) == row['sha256'] for row in fingerprints) and
            all(vm.digest((args.qemu_root/'tools'/name).read_bytes()) == sha for name, sha in helpers.items()))
        result['passed'] &= result['inputs_unchanged']
        if result['passed'] and not args.cases and set(args.variants) == {'original', 'reconstructed'}:
            try:
                validate_photo_settings(result)
                result['contract_checks'] = contract_rejection_checks(result)
            except ValueError as error:
                result['passed'], result['error'] = False, str(error)
        vm.save_json(args.output/'report.json', result)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
