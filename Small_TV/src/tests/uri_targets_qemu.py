"""Compare real factory/native path dispatch with query and absolute HTTP targets.

Native photo uploads additionally exercise all three write handlers and exact
binary downloads. Only disposable VM flash copies are modified; no live services.
"""
import argparse
import hashlib
from http import client
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from urllib.parse import urlsplit

from photo_protocol import multipart_chunk


def target(path, form):
    """Vary request-target syntax while preserving its path and existing query."""
    prefix = 'http://clock.example.invalid' if form >= 2 else ''
    suffix = ('&' if '?' in path else '?') + 'probe=%2Fphoto' if form % 2 else ''
    return prefix + path + suffix


def main():
    """Verify response/action equivalence, fingerprint inputs and close owned VMs."""
    root_default = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yoradio', type=Path, default=root_default)
    parser.add_argument('--dependency-root', type=Path)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, deps = args.yoradio.resolve(), (args.dependency_root or args.yoradio).resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.qemu_root / 'tools'))
    import small_tv_vm as vm
    from small_tv_http_test import wait_http, clean_uart
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    archive = root / 'firmware/development/small-tv-esp32c2-reconstructed'
    profile = root / 'Small_TV/qemu/profiles/small-tv-c2.json'
    executable = args.qemu_root / 'bin/qemu-system-riscv32.exe'
    jpeg_path = Path(__file__).parent / 'fixtures/jpeg/rgb-420.jpg'
    paths = [Path(__file__), Path(__file__).with_name('photo_protocol.py'), jpeg_path, profile, executable,
             root / 'Small_TV/full-flash.bin']
    paths += [archive / name for name in ('app.bin', 'bootloader.bin', 'partition-table.bin',
                                         'assets.bin', 'manifest.json', 'source-manifest.json')]
    paths += [args.qemu_root / 'tools' / name for name in ('small_tv_vm.py', 'small_tv_http_test.py',
              'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'esp_elf.py')]
    pins = {str(path): sha(path) for path in paths}
    report = {'passed': False, 'all_functionality_verified': False, 'scope': __doc__,
              'app_sha256': sha(archive / 'app.bin'), 'qemu_sha256': sha(executable),
              'source_sha256': json.loads((archive / 'manifest.json').read_text())['source_sha256'],
              'inputs_sha256': pins, 'variants': {}}
    options = SimpleNamespace(yoradio=str(root), qemu=str(executable),
        rom_elf=str(deps / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(profile), network='setup', display='none', persistent=False, paused=False, gdb_port=0)
    output = args.output / 'report.json'
    try:
        for variant in ('original', 'reconstructed'):
            options.firmware = variant
            state, session = args.output / variant, None
            row = {'checks': {}, 'requests': []}
            report['variants'][variant] = row

            def check(name, value):
                """Persist each acceptance condition before reporting a failure."""
                row['checks'][name] = bool(value)
                vm.save_json(output, report)
                if not value:
                    raise AssertionError(f'{variant}: {name}')

            def request(path, payload=None, content_type='application/json'):
                """Send a bounded direct loopback request; authority text causes no DNS."""
                endpoint = urlsplit(url)
                if endpoint.hostname != '127.0.0.1':
                    raise ValueError('Only owned loopback endpoints are allowed')
                body = json.dumps(payload, separators=(',', ':')).encode() if isinstance(payload, dict) else payload
                connection = client.HTTPConnection(endpoint.hostname, endpoint.port, timeout=20)
                try:
                    connection.request('GET' if payload is None else 'POST', path, body,
                        {'Host': endpoint.netloc, 'Origin': url, 'Content-Type': content_type, 'Connection': 'close'})
                    response = connection.getresponse()
                    data = response.read(262145)
                    if len(data) > 262144:
                        raise ValueError('Oversized guest response')
                    row['requests'].append({'target': path, 'status': response.status, 'bytes': len(data),
                                            'sha256': hashlib.sha256(data).hexdigest()})
                    return response.status, data
                finally:
                    connection.close()

            try:
                session, prepared = vm.launch(options, state)
                row['sources'] = prepared['sources']
                url = session['web_urls']['setup']
                wait_http(url, expected=b'/configure')
                for path in ('/getclocktype', '/getgifvalue', '/getsettings', '/', '/photo',
                             '/get_Photo_File?file=1&chunk=0&size=0',
                             '/get_Photo_File?file=1&chunk=0&size=1024'):
                    baseline = request(path)
                    check(path + ':base', baseline[0] == 200)
                    for form in range(1, 4):
                        check(f'{path}:form{form}', request(target(path, form)) == baseline)
                for form in range(4):
                    check(f'settings-post:{form}', request(target('/setgifvalue', form), {'gif': str(form + 1)}) == (200, b'OK'))
                    check(f'settings-readback:{form}', request('/getgifvalue') == (200, str(form + 1).encode()))
                if variant == 'reconstructed':
                    jpeg = jpeg_path.read_bytes()
                    chunks = (len(jpeg) + 4095) // 4096
                    for form in range(4):
                        check(f'photo-start:{form}', request(target('/start_upload', form),
                              {'file_number': 5, 'file_size': len(jpeg), 'total_chunks': chunks}) == (200, b'OK'))
                        for index in range(chunks):
                            block, content_type = multipart_chunk(5, index, chunks, jpeg[index * 4096:(index + 1) * 4096])
                            check(f'photo-chunk:{form}:{index}', request(target('/upload_chunk', form), block, content_type) == (200, b'OK'))
                        check(f'photo-finish:{form}', request(target('/finish_upload', form),
                              {'file_number': 5, 'file_name': 'file5.jpg'}) == (200, b'OK'))
                        for index in range(chunks):
                            path = f'/get_Photo_File?file=5&chunk={index}&size=4096'
                            check(f'photo-download:{form}:{index}', request(target(path, form)) ==
                                  (200, jpeg[index * 4096:(index + 1) * 4096]))
                print(json.dumps({'variant': variant, 'checks': len(row['checks']), 'passed': True}), flush=True)
            finally:
                if session:
                    try:
                        vm.control(state, 'stop')
                    finally:
                        vm.ensure_stopped(state)
                    row['vm_stopped'] = True
                    row['no_panic'] = clean_uart(state)
                vm.save_json(output, report)
        report['passed'] = all(row.get('vm_stopped') and row.get('no_panic') and
                               all(row['checks'].values()) for row in report['variants'].values())
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        report['inputs_unchanged'] = all(sha(Path(path)) == digest for path, digest in pins.items())
        report['passed'] &= report['inputs_unchanged']
        vm.save_json(output, report)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
