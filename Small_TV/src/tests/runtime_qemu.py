"""Observe native Small TV heap/stack during real HTTP/weather/photo activity.

The requested cycle count or guest duration defines this workload's scope.
Short runs do not establish the 24-hour H10 or physical-board acceptance.
The guest runs its unmodified archived application. Hardware breakpoints and
read-only RSP inspect SDK counters; no guest functions are called by the host.
"""
import argparse
import concurrent.futures
import hashlib
import http.client
import json
import math
from pathlib import Path
import socket
import sys
from types import SimpleNamespace
from urllib.parse import urlsplit

from runtime_memory import MemorySnapshot, native_layout
from runtime_state import GuestMicroseconds, RuntimeJournal
from runtime_weather import WeatherSnapshot


def main():
    """Run one owned disposable VM and preserve evidence even if a check fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yoradio', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, help='Shared SDK/ROM/oracle packages for an isolated worktree')
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--qemu', type=Path, help='Explicit candidate executable; preserve the tool bundle')
    parser.add_argument('--output', type=Path, required=True)
    length = parser.add_mutually_exclusive_group()
    length.add_argument('--cycles', type=int)
    length.add_argument('--duration-seconds', type=int)
    parser.add_argument('--interval-seconds', type=float, default=1.2)
    parser.add_argument('--outage-every', type=int, default=0)
    parser.add_argument('--outage-seconds', type=float, default=1)
    args = parser.parse_args()
    if args.cycles is None and args.duration_seconds is None:
        args.cycles = 20
    if args.cycles is not None and not 1 <= args.cycles <= 100000:
        raise ValueError('Expected 1..100000 bounded workload cycles')
    if args.duration_seconds is not None and not 1 <= args.duration_seconds <= 604800:
        raise ValueError('Expected a duration of 1 second through seven days')
    if not math.isfinite(args.interval_seconds) or not .1 <= args.interval_seconds <= 60:
        raise ValueError('Expected a guest interval of 0.1..60 seconds')
    if not 0 <= args.outage_every <= 100000 or not math.isfinite(args.outage_seconds) or not 0 < args.outage_seconds <= 5:
        raise ValueError('Expected bounded short virtual AP outages')
    root = args.yoradio.resolve()
    deps = args.dependency_root.resolve() if args.dependency_root else root
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(deps / '.build/small-tv-parity/oracle-deps'),
                   str(root / 'Small_TV/src/tests'), str(root / 'Small_TV/qemu/parity'),
                   str(args.qemu_root / 'tools')]
    import small_tv_vm as vm
    from small_tv_http_test import http as guest_http, wait_http, wait_for, clean_uart
    from gdb_observer import Observer
    import weather_qemu as weather
    import time_qemu as clock
    from compare import seed_settings
    import compare
    from runtime_heap_rom import RomHeapCounters
    from esp_elf import object_symbols

    weather.vm, weather.wait_for = vm, wait_for
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    elf = root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    app = root / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin'
    profile = root / 'Small_TV/qemu/profiles/small-tv-c2.json'
    layout = native_layout(elf)
    weather_layout = weather.native_layout()
    weather_objects = object_symbols(elf.read_bytes(), ('cached_weather', 'request_state'))
    rom = deps / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
    counters = RomHeapCounters(rom)
    if app.read_bytes()[176:208] != bytes.fromhex(layout['elf_sha256']):
        raise ValueError('Archived app and inspected ELF do not match')
    files = [Path(__file__), Path(__file__).with_name('runtime_memory.py'),
             Path(__file__).with_name('runtime_heap_rom.py'), Path(__file__).with_name('runtime_state.py'),
             Path(__file__).with_name('runtime_weather.py'), elf, app, profile, rom,
             root / 'Small_TV/qemu/parity/compare.py',
             root / 'Small_TV/src/tests/fixtures/jpeg/rgb-420.jpg']
    files += [root / 'Small_TV/src/tests' / name for name in ('gdb_observer.py', 'weather_qemu.py', 'time_qemu.py')]
    archive = app.parent
    files += [archive / name for name in ('bootloader.bin', 'partition-table.bin', 'assets.bin', 'source-manifest.json')]
    files += [deps / '.idf/v6.1-9a97f6c54ec6' / name for name in (
        'components/heap/heap_private.h', 'components/heap/multi_heap.c', 'components/heap/heap_caps.c',
        'components/freertos/FreeRTOS-Kernel/tasks.c',
        'components/freertos/FreeRTOS-Kernel/portable/riscv/include/freertos/portmacro.h')]
    files += [args.qemu_root / 'tools' / name for name in
              ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'small_tv_display.py', 'esp_elf.py')]
    # FIXED_TEST: qualify a candidate without replacing the frozen tool bundle's binary.
    executable = (args.qemu or args.qemu_root / 'bin/qemu-system-riscv32.exe').resolve()
    files.append(executable)
    inputs = {str(path.resolve()): digest(path) for path in files}
    result = {'schema_version': 5, 'passed': False, 'all_functionality_verified': False,
              'scope': __doc__, 'native_elf_sha256': layout['elf_sha256'],
              'app_sha256': digest(app), 'qemu_sha256': digest(executable),
              'qemu_executable': str(executable), 'cycles_requested': args.cycles,
              'duration_requested_guest_seconds': args.duration_seconds,
              'interval_guest_seconds': args.interval_seconds,
              'outage_every_cycles': args.outage_every, 'outage_guest_seconds': args.outage_seconds,
              'completed_cycles': 0, 'inputs_sha256': inputs, 'weather_layout': weather_layout,
              'limitations': ['Native firmware only; no factory heap/stack equivalence claim.',
                              'Short workload is not the 24-hour H10 or physical-board acceptance.',
                              'Stack fill is a historical SDK watermark; sampled frames do not prove all execution peaks.',
                              'Sum of per-heap minimum counters follows SDK semantics, not a simultaneous global minimum.']}
    fixture = weather.WeatherFixture(['Shenzhen,CN', 'Fixture,CN'])
    fixture.set_response(200)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        gdb_port = reservation.getsockname()[1]
    options = SimpleNamespace(yoradio=str(root), qemu=str(executable),
        rom_elf=str(rom),
        hardware_profile=str(profile), network='clock', display='none', persistent=False,
        paused=True, gdb_port=gdb_port, firmware='reconstructed', service_port=fixture.port)
    state = args.output / 'vm'
    previous_seed = vm.seed_clock_network
    vm.seed_clock_network = seed_settings
    compare.CURRENT_THEME = 'simple'
    session = observer = weather_reader = None
    guest_clock = GuestMicroseconds()
    journal_path = args.output / 'events.jsonl'
    journal = RuntimeJournal(journal_path)
    try:
        session, prepared = vm.launch(options, state)
        result['sources'] = prepared['sources']
        observer = Observer(gdb_port)
        observer.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        observer.socket.settimeout(20)
        reader = MemorySnapshot(observer.memory, layout, counters.validate)
        weather_reader = WeatherSnapshot(reader.memory, weather_layout, weather_objects, layout['elf_sha256'])
        symbols = {name: row['address'] for name, row in layout['symbols'].items()}
        if layout['symbols']['connected']['size'] != 1:
            raise ValueError('Expected a one-byte atomic station connection flag')
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            def guest_seconds():
                """Unwrap the radio's low 32 bits without changing guest clock state."""
                raw = int.from_bytes(weather.read_bytes(qmp, 0x6004d000, 4), 'little')
                return guest_clock.update(raw) / 1000000

            clock.service(qmp, 1781265600, 0, False)
            observer.resume()
            url = session['web_urls']['station']
            wait_http(url, '/getclocktype')
            weather.wait_display(qmp)
            result['workload_start_guest_seconds'] = guest_seconds()
            until = (result['workload_start_guest_seconds'] + args.duration_seconds
                     if args.duration_seconds is not None else None)

            def capture(label):
                """Pause at an SDK entry where allocator/state-list edits are complete."""
                observer.interrupt()
                try:
                    address = symbols['vTaskDelay']
                    if observer.register(32) != address:
                        observer.breakpoint(address)
                        observer.continue_to(address)
                        observer.breakpoint(address, False)
                    row = {'label': label, 'guest_seconds': guest_seconds(),
                           'heap': reader.heaps(), 'tasks': reader.tasks()}
                    row['weather'] = weather_reader.sample(row['guest_seconds'])
                    journal.append('snapshot', row)
                    result['summary'] = journal.summary()
                    if row['heap']['minimum_free_bytes'] == 0 or any(
                            task['stack_high_water_free_bytes'] == 0 for task in row['tasks']):
                        raise AssertionError('Zero runtime heap or task stack headroom')
                finally:
                    observer.resume()
                vm.save_json(args.output / 'report.json', result)

            def request(path, payload=None, content_type='application/json'):
                """Record only method/path/status/timing, never HTTP contents."""
                started = guest_seconds()
                if isinstance(payload, bytes):
                    endpoint = urlsplit(url)
                    if endpoint.hostname != '127.0.0.1':
                        raise ValueError('Only owned loopback endpoints are allowed')
                    connection = http.client.HTTPConnection(endpoint.hostname, endpoint.port, timeout=20)
                    try:
                        connection.request('POST', path, payload, {'Origin': url, 'Content-Type': content_type,
                                                                  'Connection': 'close'})
                        response = connection.getresponse()
                        status, body = response.status, response.read(262145)
                    finally:
                        connection.close()
                else:
                    status, body = guest_http(url, path, payload, 20, url)
                elapsed = guest_seconds() - started
                journal.append('http', {'path': path, 'status': status, 'guest_seconds': elapsed})
                if status != 200 or len(body) > 262144 or elapsed > 6:
                    raise AssertionError('HTTP status, size or unchanged six-second latency bound failed')
                return body

            def upload_photo():
                """Repeat one public JPEG upload through the real chunk protocol."""
                image = (root / 'Small_TV/src/tests/fixtures/jpeg/rgb-420.jpg').read_bytes()
                chunks = (len(image) + 4095) // 4096
                request('/start_upload', {'file_number': 5, 'file_size': len(image), 'total_chunks': chunks})
                for index in range(chunks):
                    boundary = 'small-tv-runtime-fixture'
                    fields = [('chunk', image[index * 4096:(index + 1) * 4096]), ('file_number', b'5'),
                              ('chunk_index', str(index).encode()), ('total_chunks', str(chunks).encode())]
                    body = b''.join(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
                                    + value + b'\r\n' for name, value in fields)
                    body += f'--{boundary}--\r\n'.encode()
                    request('/upload_chunk', body, 'multipart/form-data; boundary=' + boundary)
                request('/finish_upload', {'file_number': 5, 'file_name': 'file5.jpg'})

            capture('ready')
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                cycle = 0
                while (cycle < args.cycles if args.cycles is not None else guest_seconds() < until):
                    request('/setclocktype', {'clocktype': cycle % 4})
                    request('/setgifvalue', {'gif': cycle % 5})
                    request('/updateCity', {'city': ['Shenzhen,CN', 'Fixture,CN'][cycle % 2]})
                    # Two clients are real concurrent network requests; their results
                    # are recorded outside this worker pool to keep QMP framing serial.
                    started = guest_seconds()
                    pending = [pool.submit(guest_http, url, path, None, 20, url)
                               for path in ('/getsettings', '/get_checkbox_state')]
                    for request_result in pending:
                        status, body = request_result.result()
                        if status != 200 or not isinstance(json.loads(body), dict):
                            raise AssertionError('Concurrent settings GET failed')
                    elapsed = guest_seconds() - started
                    journal.append('http', {'paths': ['/getsettings', '/get_checkbox_state'],
                                            'request_count': 2, 'guest_seconds': elapsed})
                    if elapsed > 6:
                        raise AssertionError('Concurrent settings GET exceeded the response bound')
                    if cycle % 4 == 2:
                        upload_photo()
                    if args.outage_every and (cycle + 1) % args.outage_every == 0:
                        def station_connected():
                            """Read the guest's actual atomic flag, independent of UART verbosity."""
                            value = weather.read_bytes(qmp, symbols['connected'], 1)[0]
                            if value not in (0, 1):
                                raise AssertionError('Invalid observed station connection flag')
                            return bool(value)

                        wait_for(station_connected, 'Guest station was not connected before outage')
                        offline_started = guest_seconds()
                        qmp.execute('qom-set', path='/machine/wifi', property='station-ap-online', value=False)
                        try:
                            if qmp.execute('qom-get', path='/machine/wifi', property='station-ap-online'):
                                raise AssertionError('Virtual AP did not go offline')
                            wait_for(lambda: not station_connected(), 'Guest did not handle AP disconnect')
                            disconnected = not station_connected()
                            wait_for(lambda: guest_seconds() >= offline_started + args.outage_seconds,
                                     'Guest clock stalled during external AP outage')
                        finally:
                            qmp.execute('qom-set', path='/machine/wifi', property='station-ap-online', value=True)
                        wait_http(url, '/getclocktype', seconds=30)
                        wait_for(station_connected, 'Guest did not reconnect after AP recovery')
                        reconnected = station_connected()
                        ap_online = qmp.execute('qom-get', path='/machine/wifi', property='station-ap-online')
                        journal.append('outage', {'offline_started_guest_seconds': offline_started,
                            'requested_offline_guest_seconds': args.outage_seconds,
                            'recovered_guest_seconds': guest_seconds(),
                            'ap_online_after': ap_online, 'guest_disconnected': disconnected,
                            'guest_reconnected': reconnected})
                        if not ap_online or not disconnected or not reconnected:
                            raise AssertionError('No real guest disconnect/reconnect observed')
                    target = guest_seconds() + args.interval_seconds
                    if until is not None:
                        target = min(target, until)
                    wait_for(lambda: guest_seconds() >= target, 'Guest clock stalled')
                    capture('cycle-' + str(cycle))
                    result['completed_cycles'] = cycle + 1
                    print('runtime cycle', cycle + 1, 'heap', result['summary']['snapshot_tail'][-1]['heap']['free_bytes'], flush=True)
                    cycle += 1
            result['workload_end_guest_seconds'] = guest_seconds()
            result['elapsed_guest_seconds'] = result['workload_end_guest_seconds'] - result['workload_start_guest_seconds']
            result['radio_clock_wraps'] = guest_clock.wraps
            if args.duration_seconds is not None and result['elapsed_guest_seconds'] < args.duration_seconds:
                raise AssertionError('Requested guest duration was not reached')
            result['passed'] = True
    except Exception as error:
        result['error'] = str(error)
        raise
    finally:
        try:
            if observer:
                observer.close()
            if session:
                try:
                    vm.control(state, 'stop')
                finally:
                    vm.ensure_stopped(state)
                result['no_panic'] = clean_uart(state)
        except Exception as error:
            result['cleanup_error'] = type(error).__name__
            result['passed'] = False
        finally:
            fixture.close()
            journal.close()
            vm.seed_clock_network = previous_seed
            result['summary'] = journal.summary()
            result['journal'] = {'file': 'events.jsonl', 'sha256': digest(journal_path)}
            result['rom_counter_crosscheck'] = {'rom_elf_sha256': counters.sha256, 'checks': counters.checks,
                'scope': 'Exact two ROM getters executed outside the VM on copied typed headers, not invoked in the guest.'}
            result['inputs_unchanged'] = all(digest(Path(path)) == sha for path, sha in inputs.items())
            with fixture.lock:
                requests = list(fixture.requests)
            result['weather_fixture'] = {'requests': len(requests),
                'responses_ok': sum(row['status'] == 200 for row in requests),
                'all_synthetic_locations': all(row['synthetic_location'] for row in requests),
                'all_synthetic_keys': all(row['synthetic_key'] for row in requests)}
            result['weather_observation'] = weather_reader.summary() if weather_reader else {}
            result['weather_coverage_passed'] = bool(weather_reader and weather_reader.valid and
                result['weather_fixture']['responses_ok'] and result['weather_fixture']['all_synthetic_locations'] and
                result['weather_fixture']['all_synthetic_keys'])
            if not result['weather_coverage_passed']:
                result.setdefault('error', 'No parsed synthetic weather response was observed')
            result['passed'] &= result['weather_coverage_passed']
            result['passed'] &= result['inputs_unchanged'] and result.get('no_panic', False)
            vm.save_json(args.output / 'report.json', result)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
