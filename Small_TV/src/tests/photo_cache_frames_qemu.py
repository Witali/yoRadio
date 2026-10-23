"""Compare real cache-backed main LCD frames with literal factory instruction replay.

This gate observes asynchronous cache readiness without changing guest state.
Network fixtures only permit ordinary startup; HTTP/RF acceptance is separate.
"""
import argparse
import datetime as dt
import gzip
import json
from pathlib import Path
import socket
import struct
import sys
from types import SimpleNamespace

from control_oracle import verify_inputs
from gdb_observer import Observer
from machine_oracle import ROOT, ELFFile, Panel
from photo_frame_replay import PhotoMachine
from photo_owner_qemu import process_handle
from photo_cache_frame_contract import validate, rejection_checks
from qemu_storage import direct_flash_backing
from frame_replay import panel_rgb, write_rgb_png
import scene_qemu as scene
import weather_qemu as weather

CASES = [dict(name='all-photos', mask=31, cycles=5, day=0, night_mode=0, night=500),
         dict(name='masked-night', mask=10, cycles=2, day=100, night_mode=1, night=500),
         dict(name='none-dark', mask=0, cycles=1, day=1000, night_mode=0, night=500),
         dict(name='bad-first', mask=31, cycles=4, day=0, night_mode=0, night=500, bad_slots=1)]


def native_entries():
    """Locate the actual step/state symbols and final clock-task delay call from this ELF."""
    path = ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = {symbol.name: symbol for symbol in elf.get_section_by_name('.symtab').iter_symbols()
                   if symbol['st_value']}
        symbol = symbols['clock_task']
        section = elf.get_section(symbol['st_shndx'])
        start, length = symbol['st_value'], symbol['st_size']
        code = section.data()[start-section['sh_addr']:start-section['sh_addr']+length]
        calls, offset = [], 0
        while offset < length:
            half = int.from_bytes(code[offset:offset+2], 'little')
            size = 4 if half & 3 == 3 else 2
            if size == 4:
                word = int.from_bytes(code[offset:offset+4], 'little')
                if word & 0x7f == 0x6f:
                    immediate = ((word >> 31) << 20 | ((word >> 12) & 255) << 12 |
                                 ((word >> 20) & 1) << 11 | ((word >> 21) & 1023) << 1)
                    if immediate & (1 << 20):
                        immediate -= 1 << 21
                    if (start+offset+immediate) & 0xffffffff == symbols['vTaskDelay']['st_value']:
                        calls.append(start+offset)
            offset += size
        if len(calls) != 1:
            raise AssertionError('Expected the current coordinator\'s sole final yield')
        return {name: symbol['st_value'] for name, symbol in symbols.items()}, max(calls)


def exercise(options, output, case, symbols, loop_end, cold_from=None):
    """Observe complete steps without modifying running guest code, RAM, PC or time.

    FIXED_TEST: fast photo startup may finish two fades before the SDK's first
    randomized SNTP request. Keep all initial frames and continue complete
    cycles, at most six, until the night case actually exercises synchronized
    restoration. Never substitute a calendar or waive the night requirement.
    """
    import compare
    from small_tv_http_test import clean_uart
    variant = 'reconstructed'
    previous_seed = vm.seed_clock_network
    previous_theme, previous_mask = compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK
    compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = 'photo', case['mask']

    def seed(data, firmware, state, yoradio, station_ssid=None):
        """Set only the disposable flash copy's synthetic factory-format preferences."""
        if cold_from is not None:return cold_from.read_bytes()
        data = bytearray(compare.seed_settings(data, firmware, state, yoradio, station_ssid))
        for offset, value in ((0x180, case['day']), (0x190, case['night_mode']),
                              (0x19c, case['night']), (0x1a0, 5)):
            struct.pack_into('<I', data, 0x3e7000+offset, value)
        if case.get('bad_slots'):data[0x200000]=0 # Deliberate invalid source, excluded from immutable guard.
        return data

    vm.seed_clock_network = seed
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    options = SimpleNamespace(**{**vars(options), 'firmware': variant, 'network': 'clock',
                                'persistent': True, 'paused': True, 'gdb_port': port})
    output.mkdir(parents=True, exist_ok=False)
    report = {'passed': False, 'samples': [], 'checks': {}, 'case': case, 'waiting_samples': []}
    report['cold_from_sha256'] = vm.digest(cold_from.read_bytes()) if cold_from is not None else None
    session = observer = None
    kernel = handle = None
    immutable = None
    plan = json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/jpeg-cache-plan.json').read_text())
    mutable = sorted([(0x9000, 0xf000), (0x3e7000, 0x3e8000)] +
                     [(row['offset'], row['offset']+row['bytes']) for row in plan['candidate_extents']])
    ranges, cursor = [], 0
    for start, end in mutable:
        if cursor < start:ranges.append((cursor, start))
        cursor = end
    if cursor < 0x400000:ranges.append((cursor, 0x400000))
    try:
        session, prepared = vm.launch(options, output)
        kernel, handle = process_handle(session['pid'])
        report['sources'] = prepared['sources']
        flash = (output/'flash.bin').read_bytes()
        immutable = [vm.digest(flash[a:b]) for a, b in ranges]
        dump = (ROOT/'Small_TV/full-flash.bin').read_bytes()
        assets = json.loads((ROOT/'Small_TV/assets/manifest.json').read_text(encoding='utf-8'))
        reference = PhotoMachine('factory', dump, assets, dependency_root=Path(options.dependency_root))
        observer = Observer(port)
        observer.socket.settimeout(90)
        if cold_from is not None:
            # These are the JPEG platform's actual raw program/erase callbacks,
            # not NVS writes. Any attempt is an unexpected breakpoint stop and
            # fails the test BEFORE the operation can be issued to flash.
            for name in ('flash_program','flash_erase'):observer.breakpoint(symbols[name])
            report['cold_write_traps'] = {name:symbols[name] for name in ('flash_program','flash_erase')}
        entry = symbols['factory_photo_step']
        expected_state = None
        remaining = 4+(case['cycles']-1)*6
        observed_cycles = case['cycles']
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            report['checks']['direct_flash_backing'] = direct_flash_backing(qmp, output)
            if not report['checks']['direct_flash_backing']:
                raise AssertionError('Flash integrity cannot be checked behind a snapshot overlay')
            qmp.execute('qom-set', path='/machine/wifi', property='ntp-unix-seconds',
                        value=int(dt.datetime(2026, 10, 13, 16, 34, 30, tzinfo=dt.timezone.utc).timestamp()))
            if case['night_mode']:
                # Keep early photo frames genuinely unsynchronized. Releasing
                # the external server after two cycles exercises continuation
                # regardless of the SDK's randomized initial SNTP delay.
                qmp.execute('qom-set', path='/machine/wifi', property='ntp-drop-mask', value=7)
                report['night_ntp_control'] = {'initial_drop_mask': 7}
            while remaining:
                if len(report['waiting_samples']) > 2000 or weather.virtual_seconds(qmp) > 300:
                    raise AssertionError('Photo readiness/fade did not complete within the observation budget')
                observer.breakpoint(entry)
                observer.continue_to(entry)
                before_code = observer.memory(entry, 4)
                state_pointer = observer.register(10)
                state = list(observer.memory(state_pointer, 2))
                mask, present = observer.register(11), observer.register(12)
                event, blocked = bool(observer.register(13)), bool(observer.register(14))
                reference_mask = mask & ~case.get('bad_slots',0)
                order = [(state[1]+step)%5 for step in range(5)]
                wanted = next((slot for slot in order if reference_mask & (1<<slot)),None)
                if event and not blocked and state[0] == 2 and wanted is not None and not present & (1<<wanted):
                    raise AssertionError('The next valid photo is being skipped before its cache is ready')
                address = socket.inet_ntoa(observer.memory(symbols['last_station_address'], 4))
                target = loop_end
                synced = bool(observer.memory(symbols['time_synced'], 1)[0])
                observer.breakpoint(entry, False)
                restoration = None
                if event and not blocked and state[0] == 5:
                    # Photos may start before SNTP. Observe the calendar actually
                    # passed to the real schedule helper, including its preset.
                    schedule = symbols['backlight_update']
                    schedule_code = observer.memory(schedule, 4)
                    observer.breakpoint(schedule)
                    observer.continue_to(schedule)
                    restoration = {'hour': observer.register(11), 'minute': observer.register(12),
                                   'clock_valid': bool(observer.register(13))}
                    observer.breakpoint(schedule, False)
                    if observer.memory(schedule, 4) != schedule_code:
                        raise AssertionError('Schedule breakpoint altered executable bytes')
                return_code = observer.memory(target, 4)
                observer.breakpoint(target)
                observer.continue_to(target)
                observer.breakpoint(target, False)
                if observer.memory(entry, 4) != before_code or observer.memory(target, 4) != return_code:
                    raise AssertionError('Hardware breakpoint altered executable bytes')
                if not event or blocked:
                    after_state = list(observer.memory(state_pointer, 2))
                    if after_state != state:
                        raise AssertionError('Blocked/idle call advanced the slideshow')
                    report['waiting_samples'].append(dict(state=state, present=present, blocked=blocked,
                        event=event, guest_seconds=weather.virtual_seconds(qmp)))
                    continue
                if expected_state is None:
                    if state[0] != 2:
                        continue
                    if state[1] != 0:
                        raise AssertionError('Initial slideshow slot was skipped before the first photo')
                    reference.panel = Panel()
                elif state != expected_state:
                    raise AssertionError('Actual fade/selection sequence differs from literal factory state')
                if mask != case['mask']:
                    raise AssertionError('Guest did not load the requested photo mask')
                # Invalid input is a declared factory correction: skip the
                # synthetic damaged source, not a pixel/difference mask.
                replay = reference.advance(*state, reference_mask, address)
                expected_state = [replay['fade'], replay['next_slot']]
                actual_state = list(observer.memory(state_pointer, 2))
                if actual_state != expected_state:
                    raise AssertionError('Photo step returned the wrong fade/selection state')
                actual = scene.picture(qmp, output, str(len(report['samples']))+'-complete')
                light = scene.backlight(observer)
                expected_duty = replay['duty']
                correction = state[0] == 5
                if correction:
                    minute = restoration['hour']*60+restoration['minute']
                    day = minute < 22*60 and (minute > 720 or minute > 9*60)
                    restoration['night_selected'] = bool(case['night_mode'] and not day)
                    level = case['night'] if restoration['night_selected'] else case['day']
                    expected_duty = level*8191//1000
                expected_brightness = 1000-min(expected_duty, 8192)*1000//8192
                expected = panel_rgb(reference.panel, expected_brightness)
                different = sum(actual[i:i+3] != expected[i:i+3] for i in range(0, len(actual), 3))
                row = {'fade_before': state[0], 'next_slot_before': state[1], 'state_after': actual_state,
                       'selected': replay['selected'], 'address': address, 'backlight': light,
                       'literal_factory_duty': replay['duty'], 'expected_duty': expected_duty,
                       'brightness_restore_correction': correction, 'different_pixels': different,
                       'restore_calendar': restoration, 'time_synced_at_entry': synced,
                       'compared_pixels': 57600, 'guest_seconds': weather.virtual_seconds(qmp),
                       'present_mask': present,
                       'intentional_bad_slots': case.get('bad_slots',0),
                       'code_unchanged': True, 'qemu_rgb_sha256': vm.digest(actual),
                       'replayed_rgb_sha256': vm.digest(expected),
                       'passed': not different and light['high_duty'] == expected_duty and
                                 light['brightness'] == expected_brightness and light['resolution_bits'] == 13}
                report['samples'].append(row)
                print('Photo fade:', variant, case['name'], len(report['samples']),
                      'phase', state[0], 'slots', replay['selected'], 'different pixels', different,
                      'duty', light['high_duty'], '/', expected_duty, flush=True)
                if not row['passed']:
                    write_rgb_png(output/(str(len(report['samples']))+'-expected.png'), expected)
                    raise AssertionError('Real photo/fade frame or brightness differs')
                remaining -= 1
                if (not remaining and case['night_mode'] and
                        not any(sample['restore_calendar'] and sample['restore_calendar']['clock_valid'] and
                                sample['restore_calendar']['night_selected'] for sample in report['samples'])):
                    if observed_cycles == case['cycles']:
                        qmp.execute('qom-set', path='/machine/wifi', property='ntp-drop-mask', value=0)
                        report['night_ntp_control'].update(released_after_cycles=observed_cycles,
                            released_guest_seconds=weather.virtual_seconds(qmp))
                    if observed_cycles >= 6:
                        raise AssertionError('No synchronized night restoration within six photo cycles')
                    remaining = 6
                    observed_cycles += 1
        report['checks'].update({'all_pixels_checked': True, 'expected_fade_steps': set(row['fade_before'] for row in report['samples']) ==
                            ({2, 3, 4, 5} if case['cycles'] == 1 else set(range(6))),
                            'hardware_breakpoints_only': True, 'no_guest_state_writes': True})
        selected = [slot for row in report['samples'] for slot in row['selected']]
        enabled = [slot for slot in range(5) if case['mask'] & ~case.get('bad_slots',0) & (1 << slot)]
        expected_order = [enabled[index % len(enabled)] for index in range(observed_cycles)] if enabled else []
        report['checks']['photo_order'] = selected == expected_order
        report['cycles_observed'] = observed_cycles
        if case['night_mode']:
            report['checks']['synchronized_night_restore'] = any(
                row['restore_calendar'] and row['restore_calendar']['clock_valid'] and
                row['restore_calendar']['night_selected'] for row in report['samples'])
        report['passed'] = all(report['checks'].values())
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        if observer:
            observer.close()
        if session:
            try:
                vm.control(output, 'stop')
            finally:
                if handle:
                    assert kernel.WaitForSingleObject(handle, 10000) == 0
                    kernel.CloseHandle(handle)
                    report['owners_stopped'] = True
            flash = (output/'flash.bin').read_bytes()
            report['checks']['executable_media_unchanged'] = immutable is not None and all(
                vm.digest(flash[a:b]) == sha for (a, b), sha in zip(ranges, immutable))
            report['checks']['no_panic'] = clean_uart(output)
            if cold_from is not None:
                before = cold_from.read_bytes()
                report['checks']['cold_cache_no_program_or_erase_attempts'] = True
                report['checks']['cold_cache_candidates_exact'] = all(
                    before[r['offset']:r['offset']+r['bytes']] == flash[r['offset']:r['offset']+r['bytes']]
                    for r in plan['candidate_extents'])
            report['passed'] &= all(report['checks'].values())
        vm.seed_clock_network = previous_seed
        compare.CURRENT_THEME, compare.CURRENT_PHOTO_MASK = previous_theme, previous_mask
        vm.save_json(output/'photo-frames-report.json', report)
    if not report['passed']:
        raise AssertionError('Photo frame checks failed')
    return report


def main():
    """Run isolated station profiles and bind their frame evidence to exact inputs."""
    global vm
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--dependency-root', type=Path, default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cases', nargs='+', choices=[row['name'] for row in CASES])
    args = parser.parse_args()
    frozen = json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    import hashlib
    for row in frozen['files']:
        assert hashlib.sha256((args.qemu_root/row['file']).read_bytes()).hexdigest() == row['sha256']
    sys.path.insert(0, str(args.qemu_root/'tools'))
    sys.path.insert(0, str(ROOT/'Small_TV/qemu/parity'))
    import small_tv_vm as vm
    from small_tv_http_test import wait_for
    scene.vm = vm
    weather.vm, weather.wait_for = vm, wait_for
    fixture = weather.WeatherFixture(['Shenzhen,CN'])
    fixture.set_response(200)
    options = SimpleNamespace(yoradio=str(ROOT), qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'), display='none',
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        service_port=fixture.port, dependency_root=str(args.dependency_root))
    args.output.mkdir(parents=True, exist_ok=False)
    symbols, loop_end = native_entries()
    cases = [row for row in CASES if not args.cases or row['name'] in args.cases]
    paths = [ROOT/'Small_TV/src/tests'/name for name in ('photo_cache_frames_qemu.py', 'photo_cache_frame_contract.py',
        'photo_frame_replay.py', 'photo_owner_qemu.py',
        'qemu_storage.py', 'jpeg_oracle.py', 'machine_oracle.py', 'classic_oracle.py', 'control_oracle.py', 'scene_qemu.py',
        'frame_replay.py', 'weather_qemu.py', 'weather_render_oracle.py', 'gdb_observer.py')]
    paths += [ROOT/'Small_TV/qemu/parity/compare.py', Path(options.hardware_profile)]
    archive = ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    paths += [archive/name for name in ('app.bin', 'bootloader.bin', 'partition-table.bin', 'assets.bin',
                                        'manifest.json', 'source-manifest.json', 'assets-manifest.json', 'jpeg-cache-plan.json')]
    paths += [ROOT/'Small_TV/assets/manifest.json']
    paths += [ROOT/'Small_TV/full-flash.bin']
    timing_proof = ROOT/'Small_TV/qemu/parity/photo-cache-frames-validation-20261023.json'
    timing = json.loads(timing_proof.read_text())
    timing_raw = next(r for r in timing['raw'] if r['source'].endswith('/factory-first/photo-frames-report.json'))
    timing_blob = next(r for r in timing['blobs'] if r['sha256'] == timing_raw['sha256'])
    timing_path = timing_proof.parent/timing_blob['file']
    factory_data = gzip.decompress(timing_path.read_bytes())
    assert vm.digest(factory_data) == timing_raw['sha256']
    factory = json.loads(factory_data);assert factory['passed']
    paths += [timing_proof, timing_path]
    paths += sorted((ROOT/'Small_TV/assets/photos').glob('*.jpg'))
    fingerprints = [{'file': path.relative_to(ROOT).as_posix(), 'sha256': vm.digest(path.read_bytes())} for path in paths]
    helpers = {name: vm.digest((args.qemu_root/'tools'/name).read_bytes()) for name in
        ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'esp_elf.py', 'small_tv_display.py')}
    report = {'passed': False, 'app_sha256': verify_inputs(ROOT, args.dependency_root),
        'source_sha256': json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())['source_sha256'],
        'native_elf_sha256': vm.digest((ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()),
        'factory_elf_sha256': vm.digest((args.dependency_root/'.build/small-tv-reverse/factory-analysis.elf').read_bytes()),
        'qemu_sha256': vm.digest(Path(options.qemu).read_bytes()), 'helper_sha256': helpers,
        'profile_sha256': vm.digest(Path(options.hardware_profile).read_bytes()), 'test_inputs': fingerprints,
        'frozen_inputs': frozen, 'flows': {}, 'scope': __doc__, 'all_functionality_verified': False,
        'complete_display_matrix': len(cases) == len(CASES),
        'factory_first_photo_seconds': factory['samples'][0]['guest_seconds'],
        'network_acceptance': False, 'rf_tested': False, 'hardware_tested': False}
    try:
        report['flows']['reconstructed'] = {}
        for case in cases:
            report['flows']['reconstructed'][case['name']] = exercise(options,
                args.output/('reconstructed-'+case['name']), case, symbols, loop_end)
        if report['complete_display_matrix']:
            warm = args.output/'reconstructed-all-photos/flash.bin'
            report['cold'] = exercise(options,args.output/'reconstructed-cold',CASES[0],symbols,loop_end,cold_from=warm)
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        fixture.close()
        report['inputs_unchanged'] = (verify_inputs(ROOT, args.dependency_root) == report['app_sha256'] and
            vm.digest((args.dependency_root/'.build/small-tv-reverse/factory-analysis.elf').read_bytes()) == report['factory_elf_sha256'] and
            vm.digest(Path(options.qemu).read_bytes()) == report['qemu_sha256'] and
            all(vm.digest((ROOT/row['file']).read_bytes()) == row['sha256'] for row in fingerprints) and
            all(vm.digest((args.qemu_root/'tools'/name).read_bytes()) == sha for name, sha in helpers.items()))
        report['passed'] &= report['inputs_unchanged']
        if report['passed'] and report['complete_display_matrix']:
            try:
                validate(report)
                report['contract_rejections'] = rejection_checks(report)
            except ValueError as error:
                report['passed'] = False
                report['error'] = str(error)
        vm.save_json(args.output/'report.json', report)
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
