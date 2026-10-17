"""Exercise actual native photo HTTP writes, safe publication, download and cold boot."""
import argparse
import http.client
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from urllib.parse import urlsplit
import uuid

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--yoradio', type=Path, default=ROOT)
parser.add_argument('--dependency-root', type=Path)
parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
dependencies = args.dependency_root or args.yoradio
sys.path.insert(0, str(args.qemu_root / 'tools'))
import small_tv_vm as vm
from small_tv_http_test import wait_http, wait_for, clean_uart
import weather_qemu as weather
from jpeg_test_fixtures import gray_huffman_fixture

weather.vm = vm
weather.wait_for = wait_for
args.output.mkdir(parents=True, exist_ok=False)
fixture = weather.WeatherFixture(['Shenzhen,CN'])
fixture.set_response(200)
profile = args.yoradio / 'Small_TV/qemu/profiles/small-tv-c2.json'
archive = args.yoradio / 'firmware/development/small-tv-esp32c2-reconstructed'
options = SimpleNamespace(
    yoradio=str(args.yoradio), qemu=str(args.qemu_root / 'bin/qemu-system-riscv32.exe'),
    rom_elf=str(dependencies / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
    hardware_profile=str(profile), network='clock', display='none', persistent=True,
    paused=False, gdb_port=0, firmware='reconstructed', service_port=fixture.port)
state = args.output / 'vm'
qmp = url = None
good_path = Path(__file__).parent / 'fixtures/jpeg/rgb-420.jpg'
good = good_path.read_bytes()
bad = gray_huffman_fixture([3] + [0] * 15, [0, 1, 2], [1] + [0] * 15, [0])
safe_gray = gray_huffman_fixture([1] + [0] * 15, [0], [1] + [0] * 15, [0])
image = archive / 'app.bin'
elf = args.yoradio / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
paths = [Path(__file__), Path(__file__).with_name('jpeg_test_fixtures.py'),
         Path(__file__).with_name('weather_qemu.py'), good_path]
inputs = [{'file': path.relative_to(ROOT).as_posix(), 'sha256': vm.digest(path.read_bytes())} for path in paths]
helpers = {name: vm.digest((args.qemu_root / 'tools' / name).read_bytes()) for name in
           ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py',
            'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'esp_elf.py')}
result = {'passed': False, 'scope': __doc__, 'checks': {}, 'requests': [], 'test_inputs': inputs,
          'app_sha256': vm.digest(image.read_bytes()), 'native_elf_sha256': vm.digest(elf.read_bytes()),
          'qemu_sha256': vm.digest(Path(options.qemu).read_bytes()), 'profile_sha256': vm.digest(profile.read_bytes()),
          'helper_sha256': helpers, 'valid_jpeg_sha256': vm.digest(good), 'invalid_jpeg_sha256': vm.digest(bad)}
if image.read_bytes()[176:208] != bytes.fromhex(result['native_elf_sha256']):
    raise ValueError('App/ELF mismatch')


def request(path, payload=None, content_type='application/json'):
    """Send bounded binary/JSON HTTP only to this VM's owned loopback listener."""
    endpoint = urlsplit(url)
    if endpoint.hostname != '127.0.0.1':
        raise ValueError('Only loopback is allowed')
    body = json.dumps(payload, separators=(',', ':')).encode() if isinstance(payload, dict) else payload
    started = weather.virtual_seconds(qmp)
    connection = http.client.HTTPConnection(endpoint.hostname, endpoint.port, timeout=20)
    try:
        connection.request('GET' if payload is None else 'POST', path, body,
                           {'Origin': url, 'Content-Type': content_type, 'Connection': 'close'})
        response = connection.getresponse()
        data = response.read(262145)
        if len(data) > 262144:
            raise ValueError('Oversized guest response')
        result['requests'].append({'path': path, 'status': response.status,
                                   'guest_seconds': weather.virtual_seconds(qmp) - started,
                                   'response_bytes': len(data)})
        return response.status, data
    finally:
        connection.close()


def metadata():
    """Read the slot's published length from the real guest API."""
    status, data = request('/get_Photo_File?file=5&chunk=0&size=0')
    if status != 200:
        raise AssertionError('Cannot read photo metadata')
    return json.loads(data)


def multipart(block, index, total):
    """Encode the original multipart fields without transforming JPEG bytes."""
    boundary = 'qemu-photo-' + uuid.uuid4().hex
    if boundary.encode() in block:
        raise AssertionError('Boundary collides with fixture')
    body = bytearray()
    for name, value in [('chunk', block), ('file_number', b'5'),
                        ('chunk_index', str(index).encode()), ('total_chunks', str(total).encode())]:
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'.encode() + value + b'\r\n'
    body += f'--{boundary}--\r\n'.encode()
    return request('/upload_chunk', bytes(body), 'multipart/form-data; boundary=' + boundary)[0]


def upload(data, retry_checks=False):
    """Test ordered chunks, premature completion, busy sessions and exact/conflicting retries."""
    chunks = (len(data) + 4095) // 4096
    if request('/start_upload', {'file_number': 5, 'file_size': len(data), 'total_chunks': chunks})[0] != 200:
        raise AssertionError('Upload start failed')
    if metadata() != dict(exists=False, size=0):
        raise AssertionError('Incomplete slot is still published')
    if retry_checks:
        if request('/start_upload', {'file_number': 4, 'file_size': 100, 'total_chunks': 1})[0] != 400:
            raise AssertionError('Concurrent upload was accepted')
        if request('/finish_upload', {'file_number': 5, 'file_name': 'file5.jpg'})[0] != 400:
            raise AssertionError('Premature finish was accepted')
        if multipart(data[4096:8192], 1, chunks) != 400:
            raise AssertionError('Out-of-order block was accepted')
    for index in range(chunks):
        block = data[index * 4096:(index + 1) * 4096]
        if multipart(block, index, chunks) != 200:
            raise AssertionError('Valid block failed')
        if retry_checks and index == 0:
            if multipart(block, index, chunks) != 200:
                raise AssertionError('Identical retry failed')
            changed = bytearray(block)
            changed[-1] ^= 1
            if multipart(bytes(changed), index, chunks) != 400:
                raise AssertionError('Conflicting retry was accepted')
    if retry_checks:
        result['checks']['busy_and_retry_policy'] = True
    return request('/finish_upload', {'file_number': 5, 'file_name': 'file5.jpg'})[0]


def download(length):
    """Recover all original bytes through bounded GET chunks."""
    output = bytearray()
    for index in range((length + 4095) // 4096):
        status, data = request('/get_Photo_File?file=5&chunk=' + str(index) + '&size=4096')
        if status != 200:
            raise AssertionError('Photo download failed')
        output += data
    return bytes(output)


try:
    session, prepared = vm.launch(options, state)
    result['sources'] = prepared['sources']
    first_name = session['name']
    url = session['web_urls']['station']
    wait_http(url, '/getclocktype', expected=b'0')
    with vm.QMP(session['qmp_port'], session['name']) as qmp:
        if upload(safe_gray) != 200:
            raise AssertionError('Valid one-bit grayscale JPEG was rejected')
        result['checks']['valid_gray_published'] = (
            metadata() == dict(exists=True, size=len(safe_gray)) and download(len(safe_gray)) == safe_gray)
        invalid_status = upload(bad)
        invalid_metadata = metadata()
        result['invalid'] = {'finish_status': invalid_status, 'metadata': invalid_metadata}
        result['checks']['malformed_huffman_rejected'] = invalid_status == 400 and invalid_metadata == dict(exists=False, size=0)
        if invalid_status not in (200, 400):
            raise AssertionError('Unexpected malformed upload status')
        if upload(good, retry_checks=True) != 200:
            raise AssertionError('Valid JPEG was rejected')
        result['checks']['valid_published'] = metadata() == dict(exists=True, size=len(good))
        result['checks']['download_exact'] = download(len(good)) == good
    result['checks']['first_boot_no_panic'] = clean_uart(state)
    vm.control(state, 'stop')
    vm.ensure_stopped(state)
    result['checks']['owned_flash_changed'] = vm.digest((state / 'flash.bin').read_bytes()) != prepared['prepared_flash_sha256']
    session, _ = vm.launch(options, state)
    result['checks']['cold_boot_new_vm'] = session['name'] != first_name
    url = session['web_urls']['station']
    wait_http(url, '/getclocktype', expected=b'0')
    with vm.QMP(session['qmp_port'], session['name']) as qmp:
        result['checks']['cold_boot_metadata'] = metadata() == dict(exists=True, size=len(good))
        result['checks']['cold_boot_download_exact'] = download(len(good)) == good
        # The persisted RGB file is a known, different length from this gray
        # replacement. Stop immediately after finish, before any quiet-time save.
        if upload(safe_gray) != 200:
            raise AssertionError('Gray replacement failed')
        finished = weather.virtual_seconds(qmp)
        qmp.execute('stop')
        result['finish_response_to_stop_guest_seconds'] = weather.virtual_seconds(qmp) - finished
        result['checks']['immediate_finish_cut_bounded'] = result['finish_response_to_stop_guest_seconds'] < .5
    result['checks']['cold_boot_no_panic'] = clean_uart(state)
    previous_name = session['name']
    vm.control(state, 'stop')
    vm.ensure_stopped(state)
    session, _ = vm.launch(options, state)
    result['checks']['immediate_finish_new_vm'] = session['name'] != previous_name
    url = session['web_urls']['station']
    wait_http(url, '/getclocktype', expected=b'0')
    with vm.QMP(session['qmp_port'], session['name']) as qmp:
        result['checks']['immediate_finish_persisted'] = (
            metadata() == dict(exists=True, size=len(safe_gray)) and download(len(safe_gray)) == safe_gray)
        chunks = (len(good) + 4095) // 4096
        if request('/start_upload', {'file_number': 5, 'file_size': len(good), 'total_chunks': chunks})[0] != 200:
            raise AssertionError('Interrupted upload could not start')
        started = weather.virtual_seconds(qmp)
        result['checks']['interrupted_slot_unpublished'] = metadata() == dict(exists=False, size=0)
        qmp.execute('stop')
        result['start_response_to_stop_guest_seconds'] = weather.virtual_seconds(qmp) - started
        result['checks']['interrupted_start_cut_bounded'] = result['start_response_to_stop_guest_seconds'] < .5
    result['checks']['immediate_finish_no_panic'] = clean_uart(state)
    previous_name = session['name']
    vm.control(state, 'stop')
    vm.ensure_stopped(state)
    session, _ = vm.launch(options, state)
    result['checks']['interrupted_boot_new_vm'] = session['name'] != previous_name
    url = session['web_urls']['station']
    wait_http(url, '/getclocktype', expected=b'0')
    with vm.QMP(session['qmp_port'], session['name']) as qmp:
        result['checks']['interrupted_photo_hidden'] = (
            metadata() == dict(exists=False, size=0) and
            request('/get_Photo_File?file=5&chunk=0&size=4096')[0] == 400)
        if upload(safe_gray) != 200:
            raise AssertionError('Upload stayed busy after interrupted cold boot')
        result['checks']['new_upload_after_interruption'] = (
            metadata() == dict(exists=True, size=len(safe_gray)) and download(len(safe_gray)) == safe_gray)
    result['checks']['interrupted_boot_no_panic'] = clean_uart(state)
    result['passed'] = all(result['checks'].values())
    print(json.dumps({'passed': result['passed'], 'checks': result['checks'], 'invalid': result['invalid']}), flush=True)
except Exception as error:
    result['error'] = str(error)
    raise
finally:
    if (state / 'session.json').exists():
        try:
            vm.control(state, 'stop')
        finally:
            vm.ensure_stopped(state)
    fixture.close()
    result['inputs_unchanged'] = (
        result['app_sha256'] == vm.digest(image.read_bytes()) and result['native_elf_sha256'] == vm.digest(elf.read_bytes()) and
        result['qemu_sha256'] == vm.digest(Path(options.qemu).read_bytes()) and
        result['profile_sha256'] == vm.digest(profile.read_bytes()) and
        all(vm.digest((ROOT / row['file']).read_bytes()) == row['sha256'] for row in inputs) and
        all(vm.digest((args.qemu_root / 'tools' / name).read_bytes()) == sha for name, sha in helpers.items()))
    result['passed'] &= result['inputs_unchanged']
    vm.save_json(args.output / 'report.json', result)
raise SystemExit(0 if result['passed'] else 1)
