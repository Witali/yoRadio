"""Compare real factory/native captive HTTP callbacks without an LCD device.

Only owned disposable VMs, loopback HTTP and synthetic settings are used.
No debugger, guest memory writes, display readiness or physical hardware.
"""
import argparse
import datetime as dt
import hashlib
from http.client import HTTPConnection
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]


def digest(path):
    """Record byte identities independently of Git paths and timestamps."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def request(url, path, host):
    """Send a literal Host, or HTTP/1.0 without it; never follow redirects."""
    endpoint = urlsplit(url)
    if endpoint.hostname != '127.0.0.1':
        raise ValueError('Only owned loopback endpoints are allowed')
    connection = HTTPConnection(endpoint.hostname, endpoint.port, timeout=10)
    if host is None:
        connection._http_vsn, connection._http_vsn_str = 10, 'HTTP/1.0'
    try:
        connection.putrequest('GET', path, skip_host=True, skip_accept_encoding=True)
        if host is not None:
            connection.putheader('Host', host)
        connection.putheader('Connection', 'close')
        connection.endheaders()
        response = connection.getresponse()
        body = response.read(262145)
        if len(body) > 262144:
            raise ValueError('Guest response exceeds bound')
        return dict(status=response.status, location=response.getheader('Location'),
                    bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
    finally:
        connection.close()


def main():
    """Exercise AP parity and explicitly separate intended authority/STA corrections."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.qemu_root/'tools'))
    import small_tv_vm as vm
    from small_tv_http_test import wait_http, clean_uart
    profile_source = ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'
    profile = json.loads(profile_source.read_text())
    if [node['id'] for node in profile['devices']] != ['lcd']:
        raise ValueError('Unexpected source device profile')
    profile['name'], profile['devices'] = 'small-tv-captive-without-lcd', []
    target = args.output/'network-only-profile.json'
    target.write_text(json.dumps(profile, indent=2)+'\n', encoding='utf-8', newline='\n')
    archive = ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    elf = ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    if (archive/'app.bin').read_bytes()[176:208] != bytes.fromhex(digest(elf)):
        raise ValueError('App/ELF mismatch')
    rom = args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
    paths = [Path(__file__), profile_source, target, elf, rom, ROOT/'Small_TV/full-flash.bin']
    paths += [archive/name for name in ('app.bin', 'bootloader.bin', 'partition-table.bin',
                                      'assets.bin', 'manifest.json', 'source-manifest.json')]
    snapshot = json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    paths += [args.qemu_root/row['file'] for row in snapshot['files']]
    paths.append(args.qemu_root/'frozen-inputs.json')
    pins = {str(path.resolve()): digest(path) for path in paths}
    report = dict(passed=False, all_functionality_verified=False, scope=__doc__, inputs_sha256=pins,
                  app_sha256=digest(archive/'app.bin'), native_elf_sha256=digest(elf),
                  source_sha256=json.loads((archive/'manifest.json').read_text())['source_sha256'],
                  display=dict(executed=False, passed=None), flows={},
                  started_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    active = None
    try:
        for variant, role in (('original', 'setup'), ('reconstructed', 'setup'), ('reconstructed', 'clock')):
            name = variant+'-'+role
            folder = args.output/name
            folder.mkdir()
            options = SimpleNamespace(yoradio=str(ROOT), firmware=variant,
                qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'), rom_elf=str(rom),
                hardware_profile=str(target), network=role, display='none', persistent=False,
                paused=False, gdb_port=0, http_base_port=0)
            session, _ = vm.launch(options, folder)
            active = folder
            row = dict(passed=False, session=session, requests=[])
            report['flows'][name] = row
            if session['hardware_profile']['arguments'] != []:
                raise AssertionError('Unexpected external device')
            url = session['web_urls']['setup' if role == 'setup' else 'station']
            wait_http(url, expected=b'/configure' if role == 'setup' else b'/getsettings')
            root = request(url, '/', '192.168.43.1')
            cases = [('ap', '192.168.43.1'), ('port', '192.168.43.1:18400'),
                     ('no-host', None), ('foreign', 'probe.example.invalid'),
                     ('lookalike', '192.168.43.1.example.invalid')]
            for label, host in cases:
                observed = request(url, '/generate_204?audit=1', host)
                row['requests'].append(dict(case=label, host=host, **observed))
                if role == 'clock':
                    expected = (302, '/')
                elif label in ('ap', 'port', 'no-host') or (variant == 'original' and label == 'lookalike'):
                    expected = (200, None)
                else:
                    expected = (302, 'http://192.168.43.1/')
                if (observed['status'], observed['location']) != expected:
                    raise AssertionError(f'{name}/{label}: {observed} != {expected}')
                if expected[0] == 200 and observed['sha256'] != root['sha256']:
                    raise AssertionError('Unknown local path did not serve the exact root page')
            row['factory_lookalike_bug_corrected'] = variant == 'reconstructed' and role == 'setup'
            row['root'] = root
            vm.control(folder, 'stop')
            vm.ensure_stopped(folder)
            active = None
            row['uart_no_panic'] = clean_uart(folder)
            row['passed'] = row['uart_no_panic']
            if not row['passed']:
                raise AssertionError('Guest UART failure')
            print('PASS captive network:', name, flush=True)
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        if active:
            vm.control(active, 'stop')
            vm.ensure_stopped(active)
        report['inputs_unchanged'] = all(digest(path) == value for path, value in pins.items())
        report['passed'] &= report['inputs_unchanged']
        report['ended_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        vm.save_json(args.output/'report.json', report)


if __name__ == '__main__':
    main()
