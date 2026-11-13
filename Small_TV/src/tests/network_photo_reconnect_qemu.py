"""Resume a multi-chunk photo upload after both virtual AP peers disconnect."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import socket
import sys
import time
from types import SimpleNamespace

from gdb_observer import Observer
from network_activity_qemu import peers
from network_clients_qemu import Events, sha, symbols
from photo_owner_qemu import multipart, process_handle
from runtime_failure_capture import FailureCapture
from runtime_failure_layout import failure_layout
from runtime_memory import native_layout
from weather_qemu import read_bytes


ROOT = Path(__file__).resolve().parents[3]
WIFI = '/machine/wifi'
CHUNK = 4096
REQUEST_TIMEOUT = 20
FINISH_TIMEOUT = 240  # Existing host bound for the RV32 photo worker in QEMU.


def transition(qmp, trace, mask, wait_for, initial=False):
    """Wait for actual guest peer events, then for each surviving DHCP lease."""
    observer = trace.observer
    if not initial:
        observer.interrupt()
    qmp.execute('qom-set', path=WIFI, property='softap-client-mask', value=mask)
    assert qmp.execute('qom-get', path=WIFI, property='softap-client-mask') == mask
    trace.until(peers(mask), 1)
    observer.resume()

    def ready():
        rows = json.loads(qmp.execute('qom-get', path=WIFI, property='softap-clients'))
        live = [row for row in rows if row['online']]
        return (set(row['mac'] for row in live) == peers(mask) and
                all(row['model_state'] == 5 and row['offered_ipv4'] != '0.0.0.0' for row in live) and
                len(set(row['offered_ipv4'] for row in live)) == len(live))

    wait_for(ready, 'Virtual clients failed to obtain distinct DHCP leases', seconds=60)


def upload_cycle(trace, qmp, failure, pool, url, http, wait_for, image, cycle, report):
    """Upload normally, interrupt connectivity, retry a chunk, and verify every byte."""
    chunks = [image[offset:offset + CHUNK] for offset in range(0, len(image), CHUNK)]

    def checked(path, payload=None, expected=None, timeout=REQUEST_TIMEOUT):
        failure.operation = {'kind': 'http', 'path': path, 'cycle': cycle}
        status, body = http(url, path, payload, timeout=timeout, origin=url)
        assert status == 200 and (expected is None or body == expected), (path, status)
        report['http_requests'] += 1
        return body

    def chunk(index):
        failure.operation = {'kind': 'http', 'path': '/upload_chunk', 'cycle': cycle, 'chunk': index}
        assert multipart(url, 5, index, len(chunks), chunks[index]) == (200, b'OK')
        report['http_requests'] += 1

    def change(mask):
        failure.operation = {'kind': 'ap-transition', 'mask': mask, 'cycle': cycle}
        transition(qmp, trace, mask, wait_for)
        report['masks'].append(mask)

    # Both peers have distinct leases. Keep a separate host HTTP connection in
    # flight during the start request to exercise the shared HTTP server.
    concurrent_get = pool.submit(http, url, '/getclocktype', timeout=REQUEST_TIMEOUT, origin=url)
    started = time.monotonic()
    checked('/start_upload', dict(file_number=5, file_size=len(image), total_chunks=len(chunks)), b'OK')
    report['upload_starts'].append(time.monotonic() - started)
    failure.operation = {'kind': 'http', 'path': '/getclocktype', 'cycle': cycle}
    assert concurrent_get.result()[0] == 200
    report['http_requests'] += 1
    chunk(0)
    survivor = 1 if cycle % 2 == 0 else 2
    change(survivor)
    checked('/getclocktype')
    change(0)
    change(survivor)
    checked('/getclocktype')
    chunk(0)
    report['chunk_retries'] += 1
    metadata = json.loads(checked('/get_Photo_File?file=5&chunk=0&size=0'))
    assert metadata == {'exists': False, 'size': 0}
    for index in range(1, len(chunks)):
        chunk(index)
    change(3)
    started = time.monotonic()
    guest_start = int.from_bytes(read_bytes(qmp, 0x6004d000, 4), 'little')
    checked('/finish_upload', dict(file_number=5, file_name='file5.jpg'), b'OK', timeout=FINISH_TIMEOUT)
    guest_end = int.from_bytes(read_bytes(qmp, 0x6004d000, 4), 'little')
    report['finishes'].append(dict(host_seconds=time.monotonic() - started,
                                   guest_seconds=((guest_end - guest_start) % 2**32) / 1_000_000))
    for index, expected in enumerate(chunks):
        checked(f'/get_Photo_File?file=5&chunk={index}&size={CHUNK}', expected=expected)
    report['verified_photo_bytes'] += len(image)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('qemu-root', 'qemu', 'abi', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, default=Path('C:/Work/yoRadio'))
    parser.add_argument('--cycles', type=int, choices=range(2, 21), default=4)
    args = parser.parse_args()
    sys.path.insert(0, str(args.qemu_root / 'tools'))
    import small_tv_vm as vm
    from small_tv_http_test import clean_uart, http, wait_for, wait_http

    bundle = json.loads((args.qemu_root / 'frozen-inputs.json').read_text())
    abi = json.loads(args.abi.read_text())
    assert abi['passed']
    for row in bundle['files']:
        assert sha(args.qemu_root / row['file']) == row['sha256']
    for name, digest in abi['inputs_sha256'].items():
        assert sha(Path(name)) == digest

    app = ROOT / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin'
    elf = ROOT / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    fixture = ROOT / 'Small_TV/src/tests/fixtures/jpeg/rgb-420.jpg'
    app_digest, elf_digest = sha(app), sha(elf)
    assert (app_digest, elf_digest) == (abi['app_sha256'], abi['elf_sha256'])
    assert app.read_bytes()[176:208].hex() == elf_digest
    image = fixture.read_bytes()
    layout, photo_layout = native_layout(elf), failure_layout(elf)
    entries, base = symbols(elf)
    rom = args.dependency_root / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
    profile = ROOT / 'Small_TV/qemu/profiles/small-tv-c2.json'
    inputs = [app, elf, fixture, args.qemu, args.abi, Path(__file__), rom, profile]
    inputs.extend(app.parent / name for name in ('manifest.json', 'bootloader.bin', 'partition-table.bin', 'assets.bin'))
    inputs.extend(Path(__file__).with_name(name) for name in (
        'gdb_observer.py', 'network_activity_qemu.py', 'network_clients_qemu.py',
        'photo_owner_qemu.py', 'runtime_failure_capture.py', 'runtime_failure_layout.py',
        'runtime_memory.py', 'weather_qemu.py'))
    pins = {str(path.resolve()): sha(path) for path in inputs}
    report = dict(passed=False, app_sha256=app_digest, native_elf_sha256=elf_digest,
                  qemu_sha256=sha(args.qemu), fixture_sha256=sha(fixture),
                  inputs_sha256=pins, tools_snapshot=bundle,
                  cycles=args.cycles, completed_cycles=0, masks=[], finishes=[],
                  request_host_timeout=REQUEST_TIMEOUT, finish_host_timeout=FINISH_TIMEOUT,
                  http_requests=0, upload_starts=[], chunk_retries=0, verified_photo_bytes=0,
                  owners_stopped=False)

    args.output.mkdir(parents=True, exist_ok=False)
    state = args.output / 'vm'
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        gdb_port = reservation.getsockname()[1]
    options = SimpleNamespace(yoradio=str(ROOT), firmware='reconstructed', qemu=str(args.qemu.resolve()),
        rom_elf=str(rom), hardware_profile=str(profile),
        network='setup', display='none', persistent=True, paused=True, gdb_port=gdb_port)
    session = observer = trace = kernel = handle = None
    try:
        session, prepared = vm.launch(options, state)
        report['sources'] = prepared['sources']
        kernel, handle = process_handle(session['pid'])
        observer = Observer(gdb_port)
        trace = Events(observer, entries, base, abi['wire'], False)
        # Capture a failed start before waiting for the concurrent HTTP probe.
        with ThreadPoolExecutor(max_workers=1) as pool, vm.QMP(session['qmp_port'], session['name']) as qmp, \
                FailureCapture(observer, qmp, layout, photo_layout, args.output, report, session) as failure:
            transition(qmp, trace, 3, wait_for, initial=True)
            report['masks'].append(3)
            url = session['web_urls']['setup']
            wait_http(url, '/getclocktype')
            for cycle in range(args.cycles):
                upload_cycle(trace, qmp, failure, pool, url, http, wait_for, image, cycle, report)
                assert len(trace.handles) == 1 and not any(row['function'] == 'httpd_stop' for row in trace.rows)
                report['completed_cycles'] += 1
                vm.save_json(args.output / 'report.json', report)
                print(f'Cycle {cycle + 1}: both peers returned, upload bytes verified', flush=True)
        assert all(sha(Path(name)) == digest for name, digest in pins.items())
        assert all(sha(args.qemu_root / row['file']) == row['sha256'] for row in bundle['files'])
        report['passed'] = True
    except Exception as error:
        report['error_type'] = type(error).__name__
        raise
    finally:
        if trace:
            report['events'] = trace.rows
            report['http_server_starts'] = len(trace.handles)
            report['http_server_stops'] = sum(row['function'] == 'httpd_stop' for row in trace.rows)
        if observer:
            observer.close()
        try:
            if session:
                vm.control(state, 'stop')
                if handle:
                    assert kernel.WaitForSingleObject(handle, 10000) == 0
                    report['owners_stopped'] = True
                report['no_panic'] = clean_uart(state)
        finally:
            if handle:
                kernel.CloseHandle(handle)
            report['passed'] &= report['owners_stopped'] and report.get('no_panic', False)
            vm.save_json(args.output / 'report.json', report)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
