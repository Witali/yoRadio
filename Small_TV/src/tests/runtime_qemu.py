"""Observe native Small TV heap/stack during real HTTP/weather/photo activity.

This bounded workload is a runtime preflight, not the 24-hour H10 acceptance.
The guest runs its unmodified archived application. Hardware breakpoints and
read-only RSP inspect SDK counters; no guest functions are called by the host.
"""
import argparse
import concurrent.futures
import hashlib
import http.client
import json
from pathlib import Path
import socket
import sys
from types import SimpleNamespace
from urllib.parse import urlsplit

from runtime_memory import MemorySnapshot, native_layout


def main():
    """Run one owned disposable VM and preserve evidence even if a check fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yoradio', type=Path, required=True)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cycles', type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.cycles <= 10000:
        raise ValueError('Expected 1..10000 bounded workload cycles')
    root = args.yoradio.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(root / '.build/small-tv-parity/oracle-deps'),
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

    weather.vm, weather.wait_for = vm, wait_for
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    elf = root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    app = root / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin'
    profile = root / 'Small_TV/qemu/profiles/small-tv-c2.json'
    layout = native_layout(elf)
    rom = root / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
    counters = RomHeapCounters(rom)
    if app.read_bytes()[176:208] != bytes.fromhex(layout['elf_sha256']):
        raise ValueError('Archived app and inspected ELF do not match')
    files = [Path(__file__), Path(__file__).with_name('runtime_memory.py'),
             Path(__file__).with_name('runtime_heap_rom.py'), elf, app, profile, rom,
             root / 'Small_TV/qemu/parity/compare.py',
             root / 'Small_TV/src/tests/fixtures/jpeg/rgb-420.jpg']
    files += [root / 'Small_TV/src/tests' / name for name in ('gdb_observer.py', 'weather_qemu.py', 'time_qemu.py')]
    archive = app.parent
    files += [archive / name for name in ('bootloader.bin', 'partition-table.bin', 'assets.bin', 'source-manifest.json')]
    files += [root / '.idf/v6.1' / name for name in (
        'components/heap/heap_private.h', 'components/heap/multi_heap.c', 'components/heap/heap_caps.c',
        'components/freertos/FreeRTOS-Kernel/tasks.c',
        'components/freertos/FreeRTOS-Kernel/portable/riscv/include/freertos/portmacro.h')]
    files += [args.qemu_root / 'tools' / name for name in
              ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py')]
    executable = args.qemu_root / 'bin/qemu-system-riscv32.exe'
    files.append(executable)
    inputs = {str(path.resolve()): digest(path) for path in files}
    result = {'passed': False, 'scope': __doc__, 'native_elf_sha256': layout['elf_sha256'],
              'app_sha256': digest(app), 'qemu_sha256': digest(executable), 'cycles_requested': args.cycles,
              'completed_cycles': 0, 'snapshots': [], 'requests': [], 'inputs_sha256': inputs,
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
        rom_elf=str(root / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(profile), network='clock', display='none', persistent=False,
        paused=True, gdb_port=gdb_port, firmware='reconstructed', service_port=fixture.port)
    state = args.output / 'vm'
    previous_seed = vm.seed_clock_network
    vm.seed_clock_network = seed_settings
    compare.CURRENT_THEME = 'simple'
    session = observer = None
    try:
        session, prepared = vm.launch(options, state)
        result['sources'] = prepared['sources']
        observer = Observer(gdb_port)
        observer.socket.settimeout(20)
        reader = MemorySnapshot(observer.memory, layout, counters.validate)
        symbols = {name: row['address'] for name, row in layout['symbols'].items()}
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            clock.service(qmp, 1781265600, 0, False)
            observer.resume()
            url = session['web_urls']['station']
            wait_http(url, '/getclocktype')
            weather.wait_display(qmp)
            result['workload_start_guest_seconds'] = weather.virtual_seconds(qmp)

            def capture(label):
                """Pause at an SDK entry where allocator/state-list edits are complete."""
                observer.interrupt()
                try:
                    address = symbols['vTaskDelay']
                    if observer.register(32) != address:
                        observer.breakpoint(address)
                        observer.continue_to(address)
                        observer.breakpoint(address, False)
                    row = {'label': label, 'guest_seconds': weather.virtual_seconds(qmp),
                           'heap': reader.heaps(), 'tasks': reader.tasks()}
                    result['snapshots'].append(row)
                    if row['heap']['minimum_free_bytes'] == 0 or any(
                            task['stack_high_water_free_bytes'] == 0 for task in row['tasks']):
                        raise AssertionError('Zero runtime heap or task stack headroom')
                finally:
                    observer.resume()
                vm.save_json(args.output / 'report.json', result)

            def request(path, payload=None, content_type='application/json'):
                """Record only method/path/status/timing, never HTTP contents."""
                started = weather.virtual_seconds(qmp)
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
                elapsed = weather.virtual_seconds(qmp) - started
                result['requests'].append({'path': path, 'status': status, 'guest_seconds': elapsed})
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
                for cycle in range(args.cycles):
                    request('/setclocktype', {'clocktype': cycle % 4})
                    request('/setgifvalue', {'gif': cycle % 5})
                    request('/updateCity', {'city': ['Shenzhen,CN', 'Fixture,CN'][cycle % 2]})
                    # Two clients are real concurrent network requests; their results
                    # are recorded outside this worker pool to keep QMP framing serial.
                    pending = [pool.submit(guest_http, url, path, None, 20, url)
                               for path in ('/getsettings', '/get_checkbox_state')]
                    for request_result in pending:
                        status, body = request_result.result()
                        if status != 200 or not isinstance(json.loads(body), dict):
                            raise AssertionError('Concurrent settings GET failed')
                    if cycle % 4 == 2:
                        upload_photo()
                    target = weather.virtual_seconds(qmp) + 1.2
                    wait_for(lambda: weather.virtual_seconds(qmp) >= target, 'Guest clock stalled')
                    capture('cycle-' + str(cycle))
                    result['completed_cycles'] = cycle + 1
                    print('runtime cycle', cycle + 1, 'heap', result['snapshots'][-1]['heap']['free_bytes'], flush=True)
            result['workload_end_guest_seconds'] = weather.virtual_seconds(qmp)
            result['passed'] = True
    except Exception as error:
        result['error'] = str(error)
        raise
    finally:
        if observer:
            observer.close()
        if session:
            vm.control(state, 'stop')
            vm.ensure_stopped(state)
            result['no_panic'] = clean_uart(state)
        fixture.close()
        vm.seed_clock_network = previous_seed
        result['rom_counter_crosscheck'] = {'rom_elf_sha256': counters.sha256, 'checks': counters.checks,
            'scope': 'Exact two ROM getters executed outside the VM on copied typed headers, not invoked in the guest.'}
        result['inputs_unchanged'] = all(digest(Path(path)) == sha for path, sha in inputs.items())
        result['passed'] &= result['inputs_unchanged'] and result.get('no_panic', False)
        vm.save_json(args.output / 'report.json', result)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
