"""Verify saved NTP attributes through the real SDK HTTP server, including chunked HTML."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from qemu_storage import direct_flash_backing

ROOT = Path(__file__).resolve().parents[3]
VALUES = ['time-test.invalid', 'time\"><img id=ntp-injected>.invalid', '\"'*64, '']


class Inputs(HTMLParser):
    """Decode actual HTML attributes independently of the C attribute encoder."""
    def __init__(self):
        super().__init__()
        self.fields, self.ids = {}, []

    def handle_starttag(self, tag, pairs):
        values = dict(pairs)
        if 'id' in values:
            self.ids.append(values['id'])
        if tag == 'input' and 'id' in values:
            self.fields[values['id']] = values.get('value', '')


def validate_advanced(data):
    """Require the saved value, all bounded escaped cases and explicit integrity checks."""
    required = {'initial_saved_ntp', 'all_saved_attributes', 'no_key_disclosure',
                'no_markup_injection', 'complete_html', 'no_panic',
                'executable_media_unchanged', 'source_inputs_unchanged', 'direct_flash_backing'}
    if not (data['passed'] and data['inputs_unchanged'] and set(data['checks']) == required and
            all(data['checks'].values()) and data['initial_value'] == '10.0.2.2' and
            len(data['cases']) == len(VALUES)):
        raise ValueError('Advanced editor: missing initial value, cases or integrity checks')
    for row, value in zip(data['cases'], VALUES):
        if not (row['passed'] and row['requested_ntp'] == row['parsed_ntp'] == value and
                row['post_status'] == row['get_status'] == 200 and row['complete_html'] and
                not row['key_disclosed'] and not row['injected_node']):
            raise ValueError('Advanced editor: saved attribute differs or changes document markup')


def main():
    """Use an owned snapshot flash and close the VM after the exact same before/after probe."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dependency-root', type=Path, default=ROOT)
    parser.add_argument('--artifact-root', type=Path, default=ROOT)
    parser.add_argument('--native-elf', type=Path)
    parser.add_argument('--qemu-root', type=Path, default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path[:0] = [str(args.qemu_root/'tools'), str(ROOT/'Small_TV/qemu/parity')]
    import small_tv_vm as vm
    from small_tv_http_test import http, wait_http, clean_uart
    import compare
    previous_seed = vm.seed_clock_network
    vm.seed_clock_network = compare.seed_settings
    archive = args.artifact_root/'firmware/development/small-tv-esp32c2-reconstructed'
    native_elf = args.native_elf or args.artifact_root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    profile = ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'
    paths = [Path(__file__), Path(__file__).with_name('qemu_storage.py'), ROOT/'Small_TV/qemu/parity/compare.py', profile]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    inputs = [{'file': path.relative_to(ROOT).as_posix(), 'sha256': digest(path)} for path in paths]
    helpers = {name: digest(args.qemu_root/'tools'/name) for name in
        ('small_tv_vm.py', 'small_tv_http_test.py', 'small_tv_network.py', 'small_tv_web.py', 'esp_board.py', 'esp_services.py', 'esp_elf.py')}
    args.output.mkdir(parents=True, exist_ok=False)
    options = SimpleNamespace(yoradio=str(args.artifact_root), qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        firmware='reconstructed', hardware_profile=str(profile), network='clock',
        persistent=True, display='none', paused=False, gdb_port=0)
    artifact_inputs = [{'file':name, 'sha256':digest(archive/name)} for name in
        ('app.bin', 'bootloader.bin', 'partition-table.bin', 'assets.bin', 'manifest.json',
         'source-manifest.json', 'assets-manifest.json')]
    result = {'passed': False, 'checks': {}, 'cases': [], 'app_sha256': digest(archive/'app.bin'),
        'native_elf_sha256': digest(native_elf), 'qemu_sha256': digest(Path(options.qemu)),
        'profile_sha256': digest(profile), 'test_inputs': inputs, 'helper_sha256': helpers,
        'artifact_inputs':artifact_inputs, 'scope': __doc__}
    session = None
    immutable = None
    state = args.output/'guest'
    ranges = ((0, 0x9000), (0x10000, 0x3e7000))
    key = 'fixture-key-never-render'
    try:
        session, prepared = vm.launch(options, state)
        result['sources'] = prepared['sources']
        result['source_sha256'] = prepared['sources']['source_sha256']
        with vm.QMP(session['qmp_port'], session['name']) as qmp:
            result['checks']['direct_flash_backing'] = direct_flash_backing(qmp, state)
        if not result['checks']['direct_flash_backing']:
            raise AssertionError('Flash evidence refers to a base file behind a snapshot overlay')
        flash = (state/'flash.bin').read_bytes()
        immutable = [vm.digest(flash[a:b]) for a, b in ranges]
        url = session['web_urls']['station']
        body = wait_http(url, '/advanced', b'Advanced settings', seconds=90)
        document = Inputs(); document.feed(body.decode('utf-8'))
        result['initial_value'] = document.fields.get('ntp')
        result['checks']['initial_saved_ntp'] = result['initial_value'] == '10.0.2.2'
        if not result['checks']['initial_saved_ntp']:
            raise AssertionError('Editor shows a fixed default instead of the seeded saved NTP server')
        for value in VALUES:
            status, _ = http(url, '/advancedset', {'ntp':value, 'openweathermapKey':key, 'clickCount':0}, origin=url)
            get_status, body = http(url, '/advanced')
            document = Inputs(); document.feed(body.decode('utf-8'))
            row = {'requested_ntp':value, 'parsed_ntp':document.fields.get('ntp'),
                'post_status':status, 'get_status':get_status, 'key_disclosed':key.encode() in body,
                'injected_node':'ntp-injected' in document.ids, 'complete_html':body.endswith(b'</body></html>')}
            row['passed'] = status == get_status == 200 and row['parsed_ntp'] == value and not row['key_disclosed'] and not row['injected_node'] and row['complete_html']
            result['cases'].append(row)
        result['checks'].update(all_saved_attributes=all(row['passed'] for row in result['cases']),
            no_key_disclosure=all(not row['key_disclosed'] for row in result['cases']),
            no_markup_injection=all(not row['injected_node'] for row in result['cases']),
            complete_html=all(row['complete_html'] for row in result['cases']))
        result['passed'] = all(result['checks'].values())
    except Exception as error:
        result['error'] = str(error)
    finally:
        if session:
            vm.control(state, 'stop'); vm.ensure_stopped(state)
            flash = (state/'flash.bin').read_bytes()
            result['checks']['executable_media_unchanged'] = immutable is not None and all(vm.digest(flash[a:b]) == sha for (a, b), sha in zip(ranges, immutable))
            result['checks']['no_panic'] = clean_uart(state)
        result['inputs_unchanged'] = (digest(archive/'app.bin') == result['app_sha256'] and
            digest(native_elf) == result['native_elf_sha256'] and digest(Path(options.qemu)) == result['qemu_sha256'] and
            all(digest(ROOT/row['file']) == row['sha256'] for row in inputs) and
            all(digest(archive/row['file']) == row['sha256'] for row in artifact_inputs) and
            all(digest(args.qemu_root/'tools'/name) == sha for name, sha in helpers.items()))
        result['checks']['source_inputs_unchanged'] = result['inputs_unchanged']
        result['passed'] &= all(result['checks'].values())
        vm.seed_clock_network = previous_seed
        if result['passed']:
            validate_advanced(result)
        vm.save_json(args.output/'report.json', result)
    print('Advanced editor HTTP:', result['passed'], result.get('initial_value'), len(result['cases']), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
