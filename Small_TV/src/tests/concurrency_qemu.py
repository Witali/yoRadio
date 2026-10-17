"""Exercise real concurrent Small TV clients, weather, uploads and restarts.

Only a disposable persistent flash copy is writable. The immutable production
images, guest instructions, registers and RAM are never modified by the host.
This is a bounded native H09 scenario, not complete concurrency or H10 coverage.
"""
import argparse
import concurrent.futures
import hashlib
from http import client as http_client
import json
from pathlib import Path
import sys
import threading
from types import SimpleNamespace
from urllib.parse import urlsplit

from photo_protocol import multipart_chunk


def main():
    """Drive paired clients and verify their stored results across warm/cold boot."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yoradio', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, required=True)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, deps = args.yoradio.resolve(), args.dependency_root.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(root / 'Small_TV/src/tests'), str(root / 'Small_TV/qemu/parity'),
                   str(deps / '.build/small-tv-parity/oracle-deps'), str(args.qemu_root / 'tools')]
    import small_tv_vm as vm
    from small_tv_http_test import wait_http, wait_for, clean_uart
    import weather_qemu as weather
    import time_qemu as clock
    import compare
    weather.vm, weather.wait_for = vm, wait_for
    fixture = weather.WeatherFixture(['Shenzhen,CN', 'Fixture,CN'])
    fixture.set_response(200)
    archive = root / 'firmware/development/small-tv-esp32c2-reconstructed'
    elf = root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    app_sha, elf_sha = sha(archive / 'app.bin'), sha(elf)
    if (archive / 'app.bin').read_bytes()[176:208] != bytes.fromhex(elf_sha):
        raise ValueError('Inspected ELF does not match the archived application')
    time_layout, weather_layout = clock.clock_layout(), weather.native_layout()
    if time_layout['elf_sha256'] != elf_sha or weather_layout['elf_sha256'] != elf_sha:
        raise ValueError('Observation helpers resolved a different ELF')
    jpeg_path = root / 'Small_TV/src/tests/fixtures/jpeg/rgb-420.jpg'
    jpeg = jpeg_path.read_bytes()
    chunks = (len(jpeg) + 4095) // 4096
    files = [Path(__file__), Path(__file__).with_name('photo_protocol.py'), elf, jpeg_path]
    files += [path for path in (root / 'Small_TV/src/tests').rglob('*') if path.is_file() and
              path.suffix in ('.py', '.c', '.h', '.inc', '.mjs', '.ps1', '.txt')]
    files += [root / 'Small_TV/qemu/parity/compare.py']
    files += [archive / name for name in ('app.bin', 'bootloader.bin', 'partition-table.bin', 'assets.bin', 'manifest.json', 'source-manifest.json')]
    files += [args.qemu_root / 'tools' / name for name in ('small_tv_vm.py', 'small_tv_http_test.py',
              'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py')]
    files += [root / 'Small_TV/qemu/profiles/small-tv-c2.json', args.qemu_root / 'bin/qemu-system-riscv32.exe']
    pins = {str(path): sha(path) for path in files}
    report = {'passed': False, 'all_functionality_verified': False, 'scope': __doc__,
              'app_sha256': app_sha, 'native_elf_sha256': elf_sha,
              'source_sha256': json.loads((archive / 'manifest.json').read_text())['source_sha256'],
              'qemu_sha256': sha(args.qemu_root / 'bin/qemu-system-riscv32.exe'),
              'checks': {}, 'requests': [], 'paired_batches': [], 'inputs_sha256': pins}
    options = SimpleNamespace(yoradio=str(root), qemu=str(args.qemu_root / 'bin/qemu-system-riscv32.exe'),
        rom_elf=str(deps / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(root / 'Small_TV/qemu/profiles/small-tv-c2.json'), network='clock',
        display='none', persistent=True, paused=True, gdb_port=0, firmware='reconstructed', service_port=fixture.port)
    previous_seed = vm.seed_clock_network
    vm.seed_clock_network = compare.seed_settings
    compare.CURRENT_THEME = 'simple'
    state, session = args.output / 'vm', None
    qmp = url = None

    def check(name, value):
        """Save every acceptance condition before raising, including a failure."""
        report['checks'][name] = bool(value)
        vm.save_json(args.output / 'report.json', report)
        if not value:
            raise AssertionError(name)

    def wire(path, payload=None, content_type='application/json'):
        """Use a fresh direct loopback connection; workers never access QMP."""
        endpoint = urlsplit(url)
        if endpoint.hostname != '127.0.0.1':
            raise ValueError('Only this VM loopback forward is allowed')
        body = json.dumps(payload, separators=(',', ':')).encode() if isinstance(payload, dict) else payload
        connection = http_client.HTTPConnection(endpoint.hostname, endpoint.port, timeout=20)
        try:
            connection.request('GET' if payload is None else 'POST', path, body,
                               {'Origin': url, 'Content-Type': content_type, 'Connection': 'close'})
            response = connection.getresponse()
            data = response.read(262145)
            if len(data) > 262144:
                raise ValueError('Oversized HTTP response')
            return response.status, data
        finally:
            connection.close()

    def request(path, payload=None, content_type='application/json', expected=200):
        """Record a sequential request's real guest time without retaining its body."""
        started = weather.virtual_seconds(qmp)
        status, data = wire(path, payload, content_type)
        elapsed = weather.virtual_seconds(qmp) - started
        report['requests'].append({'path': path, 'status': status, 'guest_seconds': elapsed})
        if status != expected or not 0 <= elapsed <= 6:
            raise AssertionError('Unexpected HTTP response or unchanged six-second bound: ' + path)
        return data

    def pair(label, calls):
        """Release two real clients together and bound the whole batch by guest time."""
        barrier = threading.Barrier(3)
        def send(call):
            barrier.wait(timeout=5)
            return wire(*call)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            pending = [pool.submit(send, call) for call in calls]
            started = weather.virtual_seconds(qmp)
            barrier.wait(timeout=5)
            results = [future.result(timeout=25) for future in pending]
            elapsed = weather.virtual_seconds(qmp) - started
        report['paired_batches'].append({'label': label, 'paths': [call[0] for call in calls],
                                        'statuses': [row[0] for row in results], 'guest_seconds': elapsed})
        if not 0 <= elapsed <= 6:
            raise AssertionError('Concurrent batch exceeded the unchanged six-second bound: ' + label)
        return results

    def chunk_call(slot, index, block):
        """Keep protocol conversion separate from HTTP orchestration."""
        body, content_type = multipart_chunk(slot, index, chunks, block)
        return ('/upload_chunk', body, content_type)

    def metadata(slot):
        """Read only the published length/existence contract."""
        return json.loads(request(f'/get_Photo_File?file={slot}&chunk=0&size=0'))

    def download(slot):
        """Compare every uploaded byte through the public chunked download API."""
        output = b''.join(request(f'/get_Photo_File?file={slot}&chunk={index}&size=4096')
                          for index in range(chunks))
        return output == jpeg

    def begin(slot):
        """Start the exact public image and chunk count for a single slot."""
        return ('/start_upload', {'file_number': slot, 'file_size': len(jpeg), 'total_chunks': chunks})

    def boot_count():
        """Count immutable ROM boot markers, independent of application log level."""
        return (state / 'uart.log').read_text(errors='replace').count('ESP-ROM:esp32c2')

    protected = {'boot_and_partitions': (0, 0x9000), 'application_and_gap': (0x10000, 0x200000),
                 'photos_1_to_3': (0x200000, 0x24B000), 'animations_and_weather': (0x27D000, 0x3E7000),
                 'unused_tail': (0x3E8000, 0x400000)}
    try:
        session, prepared = vm.launch(options, state)
        report['sources'] = prepared['sources']
        initial_flash = (state / 'flash.bin').read_bytes()
        report['protected_before'] = {name: vm.digest(initial_flash[a:b]) for name, (a, b) in protected.items()}
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            clock.service(qmp, 1781265600, 0, False)
            qmp.execute('cont')
            url = session['web_urls']['station']
            wait_http(url, '/getclocktype', expected=b'1')
            weather.wait_display(qmp)
            before = clock.snapshot(qmp, 'reconstructed', time_layout)
            fixture.hold_response()
            request('/updateCity', {'city': 'Fixture,CN'})
            wait_for(fixture.response_held.is_set, 'No real weather request was held', seconds=15)
            wait_for(lambda: clock.snapshot(qmp, 'reconstructed', time_layout)['second'] != before['second'],
                     'Renderer cache stopped while weather was held', seconds=15)
            check('clock_cache_advances_during_weather', clock.snapshot(qmp, 'reconstructed', time_layout)['synced'])
            started_uploads = pair('competing-upload-starts', [begin(4), begin(5)])
            statuses = [row[0] for row in started_uploads]
            check('exactly_one_upload_session', sorted(statuses) == [200, 400])
            winner = 4 + statuses.index(200)
            loser = 9 - winner
            report['winner_slot'], report['loser_slot'] = winner, loser
            check('active_photo_unpublished', metadata(winner) == {'exists': False, 'size': 0})
            first = jpeg[:4096]
            request(*chunk_call(winner, 0, first))
            duplicates = pair('identical-chunk-retries', [chunk_call(winner, 0, first)] * 2)
            check('concurrent_exact_retries_accepted', all(row[0] == 200 for row in duplicates))
            altered = first[:-1] + bytes([first[-1] ^ 1])
            conflict = pair('exact-and-conflicting-retries', [chunk_call(winner, 0, first), chunk_call(winner, 0, altered)])
            check('concurrent_conflicting_retry_rejected', [row[0] for row in conflict] == [200, 400])
            scan = pair('scan-and-settings-during-upload', [('/scan',), ('/getsettings',)])
            check('scan_and_settings_during_upload', all(row[0] == 200 for row in scan) and
                  isinstance(json.loads(scan[0][1]), list) and isinstance(json.loads(scan[1][1]), dict))
            changed = pair('independent-setting-writes', [('/SetTimeModeValue', {'timemode': 0}), ('/setgifvalue', {'gif': 4})])
            check('concurrent_settings_both_accepted', all(row[0] == 200 for row in changed))
            check('independent_fields_preserved', request('/GetTimeModeValue') == b'0' and request('/getgifvalue') == b'4')
            worker_state = int.from_bytes(weather.read_bytes(qmp, weather_layout['request_state_address'], 4), 'little')
            report['held_weather_worker_state'] = worker_state
            check('weather_still_in_flight_during_upload', fixture.response_held.is_set() and worker_state & 1)
            fixture.release_response()
            for index in range(1, chunks):
                block = jpeg[index * 4096:(index + 1) * 4096]
                rows = pair('chunk-and-get-' + str(index), [chunk_call(winner, index, block), ('/getgifvalue',)])
                check('chunk_and_get_' + str(index), rows[0][0] == rows[1][0] == 200 and rows[1][1] == b'4')
            blocked_clock = clock.snapshot(qmp, 'reconstructed', time_layout)
            request('/finish_upload', {'file_number': winner, 'file_name': f'file{winner}.jpg'})
            check('completed_photo_exact', metadata(winner) == {'exists': True, 'size': len(jpeg)} and download(winner))
            request('/setclocktype', {'clocktype': 1})
            wait_for(lambda: clock.snapshot(qmp, 'reconstructed', time_layout) != blocked_clock,
                     'Clock did not resume after upload', seconds=15)
            resumed_clock = clock.snapshot(qmp, 'reconstructed', time_layout)
            report['renderer_resume'] = {'before_finish': blocked_clock, 'after_finish': resumed_clock}
            check('clock_resumes_after_upload', resumed_clock['synced'] and resumed_clock != blocked_clock)
            request(*begin(loser))
            request(*chunk_call(loser, 0, first))
            changed = pair('settings-before-restart', [('/SetTimeModeValue', {'timemode': 1}), ('/setgifvalue', {'gif': 3})])
            check('pre_restart_settings_accepted', all(row[0] == 200 for row in changed))
            count = boot_count()
            reboot = pair('duplicate-restart-requests', [('/restart', {}), ('/restart', {})])
            check('both_restart_requests_acknowledged', all(row[0] == 200 for row in reboot))
            wait_for(lambda: boot_count() >= count + 1, 'No software restart occurred', seconds=30)
            wait_http(url, '/getclocktype', expected=b'1')
            target = weather.virtual_seconds(qmp) + 3
            wait_for(lambda: weather.virtual_seconds(qmp) >= target, 'Guest time stalled after restart', seconds=15)
            check('one_observed_restart_for_pair', boot_count() == count + 1)
            check('settings_survive_warm_restart', request('/GetTimeModeValue') == b'1' and request('/getgifvalue') == b'3')
            check('partial_photo_hidden_after_restart', metadata(loser) == {'exists': False, 'size': 0})
            check('complete_photo_survives_restart', download(winner))
        check('first_vm_no_panic', clean_uart(state))
        old_name = session['name']
        vm.control(state, 'stop')
        vm.ensure_stopped(state)
        session = None
        session, _ = vm.launch(options, state)
        check('cold_boot_uses_new_vm', session['name'] != old_name)
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            clock.service(qmp, 1781265600, 0, False)
            qmp.execute('cont')
            url = session['web_urls']['station']
            wait_http(url, '/getclocktype', expected=b'1')
            check('settings_survive_cold_boot', request('/GetTimeModeValue') == b'1' and request('/getgifvalue') == b'3')
            check('partial_photo_hidden_after_cold_boot', metadata(loser) == {'exists': False, 'size': 0})
            check('complete_photo_survives_cold_boot', download(winner))
            request(*begin(loser))
            for index in range(chunks):
                request(*chunk_call(loser, index, jpeg[index * 4096:(index + 1) * 4096]))
            request('/finish_upload', {'file_number': loser, 'file_name': f'file{loser}.jpg'})
            check('new_upload_after_interrupted_restart', download(loser))
        check('cold_boot_no_panic', clean_uart(state))
        vm.control(state, 'stop')
        vm.ensure_stopped(state)
        session = None
        final_flash = (state / 'flash.bin').read_bytes()
        report['protected_after'] = {name: vm.digest(final_flash[a:b]) for name, (a, b) in protected.items()}
        check('protected_regions_unchanged', report['protected_after'] == report['protected_before'])
        report['passed'] = all(report['checks'].values())
        print(json.dumps({'passed': report['passed'], 'checks': len(report['checks']),
                          'paired_batches': len(report['paired_batches'])}), flush=True)
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        fixture.release_response()
        try:
            if session:
                try:
                    vm.control(state, 'stop')
                finally:
                    vm.ensure_stopped(state)
        except Exception as error:
            report['cleanup_error'] = type(error).__name__
            report['passed'] = False
        finally:
            fixture.close()
            vm.seed_clock_network = previous_seed
            report['inputs_unchanged'] = all(sha(Path(path)) == digest for path, digest in pins.items())
            report['passed'] &= report['inputs_unchanged']
            vm.save_json(args.output / 'report.json', report)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
