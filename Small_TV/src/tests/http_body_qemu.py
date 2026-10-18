"""Check real HTTP body deadlines and service of a second Small TV client.

All requests target one disposable VM's loopback forward. No guest RAM, CPU
registers, executable code or timer state is patched by the test.
"""
import argparse
import concurrent.futures
import hashlib
from http import client as http_client
import json
from pathlib import Path
import socket
import sys
from types import SimpleNamespace
from urllib.parse import urlsplit


def main():
    """Collect every selected case, including failing responsiveness observations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yoradio', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, required=True)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--firmware', choices=('original', 'reconstructed'), default='reconstructed')
    parser.add_argument('--case', action='append', choices=('fragmented', 'stalled', 'trickle', 'oversized'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, deps = args.yoradio.resolve(), args.dependency_root.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(deps / 'Small_TV/src/tests'), str(deps / 'Small_TV/qemu/parity'),
                   str(args.qemu_root / 'tools')]
    import small_tv_vm as vm
    from small_tv_http_test import http, wait_http, wait_for, clean_uart
    import weather_qemu as weather
    import time_qemu as clock
    import compare
    weather.vm, weather.wait_for = vm, wait_for
    fixture = weather.WeatherFixture()
    fixture.set_response(200)
    options = SimpleNamespace(yoradio=str(root), qemu=str(args.qemu_root / 'bin/qemu-system-riscv32.exe'),
        rom_elf=str(deps / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(root / 'Small_TV/qemu/profiles/small-tv-c2.json'), network='clock',
        display='none', persistent=False, paused=True, gdb_port=0, firmware=args.firmware,
        service_port=fixture.port)
    files = [Path(__file__), Path(options.qemu), Path(options.hardware_profile)]
    files += [deps / 'Small_TV/src/tests' / name for name in ('weather_qemu.py', 'time_qemu.py')]
    files += [deps / 'Small_TV/qemu/parity/compare.py']
    files += [args.qemu_root / 'tools' / name for name in
              ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'small_tv_display.py', 'esp_elf.py')]
    archive = root / 'firmware/development/small-tv-esp32c2-reconstructed'
    files += ([root / 'Small_TV/full-flash.bin'] if args.firmware == 'original' else
              [archive / name for name in ('app.bin', 'bootloader.bin', 'partition-table.bin', 'assets.bin', 'source-manifest.json')])
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    pins = {str(path): sha(path) for path in files}
    report = {'passed': False, 'scope': __doc__, 'firmware': args.firmware, 'cases': [],
              'qemu_sha256': sha(Path(options.qemu)), 'inputs_sha256': pins,
              'second_client_bound_guest_seconds': 6, 'all_functionality_verified': False}
    session = None
    previous_seed = vm.seed_clock_network
    vm.seed_clock_network = compare.seed_settings
    compare.CURRENT_THEME = 'simple'
    state = args.output / 'vm'
    try:
        session, prepared = vm.launch(options, state)
        report['sources'] = prepared['sources']
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            clock.service(qmp, 1781265600, 0, False)
            qmp.execute('cont')
            url = session['web_urls']['station']
            endpoint = urlsplit(url)
            wait_http(url, '/getclocktype')
            weather.wait_display(qmp)

            def body_response(connection):
                """Read only the status and bounded size of a raw client's reply."""
                try:
                    response = http_client.HTTPResponse(connection)
                    response.begin()
                    body = response.read(4097)
                    if len(body) > 4096:
                        raise ValueError('Oversized bad-body response')
                    return {'status': response.status, 'bytes': len(body)}
                except (OSError, http_client.HTTPException) as error:
                    return {'closed': type(error).__name__}

            for case in args.case or ('fragmented', 'stalled', 'trickle', 'oversized'):
                row = {'name': case}
                body = b'{"clocktype":1}'
                declared = 4097 if case == 'oversized' else len(body)
                headers = (f'POST /setclocktype HTTP/1.1\r\nHost: {endpoint.netloc}\r\nOrigin: {url}\r\n'
                           f'Content-Type: application/json\r\nContent-Length: {declared}\r\n'
                           'Connection: close\r\n\r\n').encode()
                with socket.create_connection((endpoint.hostname, endpoint.port), 5) as connection:
                    connection.settimeout(45)
                    connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    connection.sendall(headers + body[:1])
                    start = weather.virtual_seconds(qmp)
                    if case == 'fragmented':
                        for block in (body[1:5], body[5:9], body[9:]):
                            target = weather.virtual_seconds(qmp) + .15
                            wait_for(lambda: weather.virtual_seconds(qmp) >= target, 'Guest clock stalled')
                            connection.sendall(block)
                        row['body_response'] = body_response(connection)
                        status, data = http(url, '/getclocktype', origin=url, timeout=20)
                        row['passed'] = row['body_response'].get('status') == 200 and status == 200 and data == b'1'
                        row['guest_seconds'] = weather.virtual_seconds(qmp) - start
                    else:
                        target = start + .5
                        wait_for(lambda: weather.virtual_seconds(qmp) >= target, 'Guest clock stalled')
                        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                            bad = pool.submit(body_response, connection)
                            second_start = weather.virtual_seconds(qmp)
                            second = pool.submit(http, url, '/getgifvalue', None, 45, url)
                            if case == 'trickle':
                                for index in range(1, 9):
                                    target = start + index
                                    wait_for(lambda: second.done() or bad.done() or weather.virtual_seconds(qmp) >= target,
                                             'Guest clock stalled')
                                    if second.done() or bad.done():
                                        break
                                    try:
                                        connection.sendall(body[index:index + 1])
                                    except OSError:
                                        break
                            status, data = second.result(timeout=50)
                            row['second_client_guest_seconds'] = weather.virtual_seconds(qmp) - second_start
                            row['second_client_status'] = status
                            row['body_response'] = bad.result(timeout=50)
                            row['passed'] = (status == 200 and data == b'0' and
                                             row['second_client_guest_seconds'] <= 6 and
                                             row['body_response'].get('status') == 400)
                report['cases'].append(row)
                vm.save_json(args.output / 'report.json', report)
                print(json.dumps(row), flush=True)
            report['passed'] = all(row['passed'] for row in report['cases'])
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        if session:
            vm.control(state, 'stop')
            vm.ensure_stopped(state)
            report['no_panic'] = clean_uart(state)
        fixture.close()
        vm.seed_clock_network = previous_seed
        report['inputs_unchanged'] = all(sha(Path(path)) == digest for path, digest in pins.items())
        report['passed'] &= report['inputs_unchanged'] and report.get('no_panic', False)
        vm.save_json(args.output / 'report.json', report)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
