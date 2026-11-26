"""Private, dry-run-default owner for one qualified continuous CYD WS/WSS guest.

No source/build changes. --check-options starts nothing; --execute is explicit.
Repository outputs contain metadata and the existing RFC client's JSON only.
Secret-bearing flash/NVS and raw process logs stay in an external private temp.
"""
import argparse
import contextlib
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import ssl
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / '.build/cws-close26'
CLIENT = ROOT / '.build/cws-stream26/client-draft/rfc-target-client.py'
CONTROLLER = ROOT / 'tests/run-cyd-full-app-openeth.py'
SOURCE = '95672e8f673ec977b6f61b78eeba6958d0d992ac'
CHECKOUT = '162bdb72407e3aaae5c69c8ecc135a6bf129ad40'
PINS = {
    CONTROLLER: 'ca236ed51cbb54e06391e7cfb5b88ef465594ccfbd122e52ddcade64f479cc4f',
    CLIENT: '3dcfc669de604238fd237ee5490e794f9988e547aa7de3a8c343d8fa57bae9f0',
    ROOT / '.build/cpbuf24/rfc-target-design.md': '81aa3c6f26923cc882d2d8ed545644e5d5dbe0a69b11b1463af2e6b526b14b6b',
    ROOT / 'idf/components/native_web_transport/tools/pack_tls_bundle.py':
        'e9986a083e0e08de45662b3012b6e3c912f2ace75dce33676e012f749615e6f8',
}
QEMU_SHA256 = '28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4'
PCM_SHA256 = '44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362'
SDK_DEFAULT = Path('C:/Work/yoRadio/.idf/v6.0.2')
SDK_COMMIT = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
BOOT_SECONDS, MODE_SECONDS, OUTER_SECONDS = 100, 1200, 1400


class Reject(Exception):
    pass


def require(condition, category):
    if not condition:
        raise Reject(category)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def pin(path):
    body = path.read_bytes()
    return dict(bytes=len(body), sha256=sha(body))


def load(path):
    return json.loads(path.read_bytes())


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def repository_roots():
    return tuple(p for p in ROOT.parents if (p / '.git').exists()) + (ROOT,)


def external(path):
    resolved = path.resolve(strict=True)
    require(not any(resolved.is_relative_to(p) for p in repository_roots()),
            'private-material-must-be-outside-repositories')
    return resolved


def outside_repository_option(path):
    require(not any(path.resolve().is_relative_to(p) for p in repository_roots()),
            'private-material-must-be-outside-repositories')


def options(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    action = p.add_mutually_exclusive_group()
    action.add_argument('--execute', action='store_true')
    action.add_argument('--check-options', action='store_true', help='Validate arguments only; no processes or writes')
    p.add_argument('--transport', choices=('ws', 'wss'), required=True)
    p.add_argument('--qualification', type=Path, default=BASE/'target/sdk/continuous/qualification.json')
    p.add_argument('--memory-gate', type=Path, default=BASE/'native-matrix-progress.json')
    p.add_argument('--qemu', type=Path, default=ROOT/'.build/cdac-model24/fixed-self-clear/qemu-system-xtensa.exe')
    p.add_argument('--rom', type=Path, default=Path('C:/Work/QEMU-ESP32/pc-bios'))
    p.add_argument('--sdk', type=Path, default=SDK_DEFAULT)
    p.add_argument('--output', type=Path, required=True, help='New result directory under .build/cpbuf24')
    p.add_argument('--ca', type=Path)
    p.add_argument('--certificate', type=Path)
    p.add_argument('--key', type=Path)
    p.add_argument('--openssl', type=Path, help='Existing local OpenSSL executable; required for WSS')
    p.add_argument('--private-parent', type=Path, help='Existing external user-private directory; default OS temp')
    p.add_argument('--keep-private', action='store_true', help='Retain owned external flash/NVS/raw logs for local review')
    a = p.parse_args(argv)
    supplied = [a.ca, a.certificate, a.key, a.openssl]
    require(all(supplied) if a.transport == 'wss' else not any(supplied), 'tls-options-must-match-transport')
    a.output = a.output.resolve()
    allowed = (ROOT/'.build/cpbuf24').resolve()
    require(a.output != allowed and a.output.is_relative_to(allowed), 'new-cpbuf24-output-required')
    require(not a.output.exists(), 'output-already-exists')
    require(not any(a.output.is_relative_to(p.resolve()) for p in (a.qualification.parent,)),
            'output-overlaps-qualified-input')
    for path in (a.ca, a.certificate, a.key, a.private_parent):
        if path is not None:
            outside_repository_option(path)
    return a


def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', '-c', 'core.longpaths=true', *args], cwd=cwd,
                                   stderr=subprocess.DEVNULL, timeout=15).decode().strip()


def preflight(a):
    require(git('rev-parse', 'HEAD') == CHECKOUT, 'released-checkout-changed')
    require(git('merge-base', SOURCE, CHECKOUT) == SOURCE, 'qualified-source-not-ancestor')
    changes = git('diff', '--name-only', SOURCE, CHECKOUT).splitlines()
    require(all(name == '.gitattributes' or name.startswith(('docs/', 'tests/results/'))
                for name in changes), 'non-evidence-change-after-qualification')
    require(not git('diff', '--name-only', 'HEAD') and not git('diff', '--cached', '--name-only'),
            'tracked-source-or-index-changed')
    for path, expected in PINS.items():
        require(pin(path)['sha256'] == expected, 'released-helper-pin-changed')
    q = load(a.qualification)
    require(q.get('passed') and q.get('source_commit') == SOURCE, 'qualification-not-released')
    fixture = (BASE/'target/sdk/continuous/fixture').resolve(strict=True)
    require(fixture == (BASE/'target/sdk/continuous/fixture').resolve(), 'continuous-qualified-fixture-required')
    image = fixture/'yoradio_cyd2usb_native.bin'
    config_path = fixture/'config/sdkconfig.json'
    input_files = set(PINS) | {a.qualification, a.memory_gate, image, config_path,
                               a.qualification.parent/'compiled/yoradio_cyd2usb_native.elf', a.qemu}
    require(pin(image) == q['image'] and pin(config_path) == q['config'], 'qualified-input-pin-changed')
    require(pin(a.qualification.parent/'compiled/yoradio_cyd2usb_native.elf') == q['elf'], 'qualified-elf-changed')
    candidate_path = BASE/'target/candidate-inputs.json'
    candidate = load(candidate_path)
    require(candidate['source_commit'] == SOURCE, 'candidate-source-mismatch')
    input_files.add(candidate_path)
    for name, expected in candidate['sources'].items():
        require(pin(ROOT/name) == expected, 'qualified-source-pin-changed')
        input_files.add(ROOT/name)
    config = load(config_path)
    require(config.get('FREERTOS_UNICORE') is False and config.get('YORADIO_WS_STATUS_RTC_SLOW') is False,
            'qualified-core-or-rtc-policy-changed')
    for name in ('ESP_TLS_USING_MBEDTLS', 'HTTPD_WS_SUPPORT', 'MBEDTLS_TLS_SERVER',
                 'MBEDTLS_RSA_C', 'MBEDTLS_PEM_PARSE_C', 'MBEDTLS_PK_PARSE_C', 'MBEDTLS_X509_CRT_PARSE_C'):
        require(config.get(name) is True, 'qualified-wss-support-missing')
    rows = load(a.memory_gate)
    require(isinstance(rows, list) and len(rows) == 3 and
            {r.get('backend') for r in rows} == {'legacy', 'pdm', 'continuous'}, 'three-output-memory-gate-required')
    for r in rows:
        require(r.get('state') == 'TERMINAL_PASS' and r.get('final_allocation_failures') == 0 and
                r.get('pbuf_prefix', {}).get('total') == 0 and r.get('pcm_sha256') == PCM_SHA256 and
                r.get('pcm_flushes') == [dict(frames=614400, status=0)] and r.get('webui_after_eof') is True and
                r.get('final_post_eof_health') is True, 'three-output-memory-gate-nonpass')
        require(bool(re.fullmatch('[a-zA-Z0-9-]+', r.get('label', ''))), 'memory-run-label-invalid')
        original_path = BASE/'native'/r['backend']/r['label']/'report.json'
        original = load(original_path)
        require(original.get('passed') is True and original.get('state') == 'TERMINAL_PASS',
                'original-memory-report-nonpass')
        memory_binding_path = BASE/'native'/r['backend']/(r['label']+'-input-binding.json')
        memory_binding = load(memory_binding_path)
        analysis_path = BASE/'native'/r['backend']/r['label']/'pbuf-analysis.json'
        analysis = load(analysis_path)
        require(analysis.get('attribution_available') is True and
                analysis.get('pbuf_pcm_flush_prefix') == r['pbuf_prefix'], 'memory-attribution-binding-mismatch')
        backend_q_path = BASE/'target/sdk'/r['backend']/'qualification.json'
        backend_q = load(backend_q_path)
        require(backend_q.get('passed') is True and backend_q.get('source_commit') == SOURCE and
                memory_binding.get('source_commit') == SOURCE and memory_binding.get('backend') == r['backend'] and
                memory_binding.get('image') == backend_q['image'] and
                memory_binding.get('qualification') == pin(backend_q_path), 'memory-gate-input-binding-mismatch')
        input_files.update((original_path, memory_binding_path, backend_q_path, analysis_path))
    require(pin(a.qemu)['sha256'] == QEMU_SHA256, 'qemu-pin-changed')
    require(a.sdk.resolve(strict=True) == SDK_DEFAULT.resolve(strict=True), 'pinned-sdk-required')
    sdk_commit = git('rev-parse', 'HEAD', cwd=a.sdk)
    require(sdk_commit == SDK_COMMIT and not git('diff', '--name-only', 'HEAD', cwd=a.sdk), 'sdk-commit-or-inputs-changed')
    rom_files = [p for p in sorted(a.rom.rglob('*')) if p.is_file()]
    rom_manifest = {p.relative_to(a.rom).as_posix(): pin(p) for p in rom_files}
    require(bool(rom_manifest), 'rom-inventory-empty')
    controller = runpy.run_path(str(CONTROLLER), run_name='rfc_launcher_controller_helpers')
    flash, parts = controller['flash_parts'](fixture)
    input_files.update(fixture/p['file'] for p in parts)
    input_files.update((fixture/'flasher_args.json', fixture/'fixture.json', *rom_files))
    require(flash[0x9000:0xe000] == b'\xff'*0x5000, 'qualified-nvs-not-empty')
    client = runpy.run_path(str(CLIENT), run_name='rfc_launcher_independent_client')
    require(len(client['CASE_IDS']) == 85, 'client-case-count-changed')
    binding = dict(source_commit=SOURCE, checkout_commit=CHECKOUT, sdk_commit=sdk_commit, app_sha256=q['image']['sha256'],
                   qemu_sha256=QEMU_SHA256, sdkconfig_sha256=q['config']['sha256'], backend='continuous',
                   fixture_sha256=sha(json.dumps(dict(parts=parts, config=q['config']), sort_keys=True).encode()),
                   rom_manifest_sha256=sha(json.dumps(rom_manifest, sort_keys=True).encode()))
    input_pins = {p:pin(p) for p in input_files}
    return q, config, flash, parts, controller, client, binding, input_pins


def provision(a, private):
    """Existing external identity only; utilities/raw stderr never enter repository outputs."""
    ca, cert, key = (external(p) for p in (a.ca, a.certificate, a.key))
    require(all(p.is_file() for p in (ca, cert, key)), 'tls-input-file-required')
    openssl = a.openssl.resolve(strict=True)
    generator = a.sdk/'components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py'
    packer = ROOT/'idf/components/native_web_transport/tools/pack_tls_bundle.py'
    checks = [
        [str(openssl), 'verify', '-CAfile', str(ca), '-purpose', 'sslserver', '-verify_hostname', 'localhost', str(cert)],
        [str(openssl), 'verify', '-CAfile', str(ca), '-purpose', 'sslserver', '-verify_ip', '127.0.0.1', str(cert)],
        [str(openssl), 'x509', '-in', str(cert), '-outform', 'DER'],
    ]
    outputs = []
    for i, command in enumerate(checks):
        r = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        (private/('tls-check-'+str(i)+'.stdout')).write_bytes(r.stdout)
        (private/('tls-check-'+str(i)+'.stderr')).write_bytes(r.stderr)
        require(r.returncode == 0, 'offline-certificate-validation-failed')
        outputs.append(r.stdout)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key, password=lambda: b'')
    csv, nvs = private/'web-tls.csv', private/'nvs.bin'
    for tag, command in [
        ('pack', [sys.executable, '-B', str(packer), '--certificate', str(cert), '--key', str(key),
                  '--format', 'nvs-csv', '--output', str(csv)]),
        ('nvs', [sys.executable, '-B', str(generator), 'generate', str(csv), str(nvs), '0x5000']),
    ]:
        with (private/(tag+'.log')).open('xb') as log:
            r = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=30)
        require(r.returncode == 0, 'private-provisioning-tool-failed')
    require(nvs.stat().st_size == 0x5000, 'generated-nvs-size')
    return nvs.read_bytes(), dict(certificate_sha256=sha(outputs[2]),
                                 host_offline_chain_name_date_verified=True,
                                 openssl=pin(openssl), nvs_generator=pin(generator))


def terminate_owned(child):
    if child is not None and child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=10)


def execute(a, prepared):
    q, config, flash, parts, helper, client_api, binding, input_pins = prepared
    parent = external(a.private_parent or Path(tempfile.gettempdir()))
    require(parent.is_dir(), 'external-private-parent-required')
    private = Path(tempfile.mkdtemp(prefix='yoradio-rfc-', dir=parent)).resolve()
    require(private.parent == parent and private.is_relative_to(parent), 'private-temp-owner-mismatch')
    a.output.mkdir(parents=True, exist_ok=False)
    report_path = a.output/'launch.json'
    report = dict(state='STARTING', source_commit=SOURCE, checkout_commit=CHECKOUT, backend='continuous', transport=a.transport,
                  qualification=pin(a.qualification), memory_gate=pin(a.memory_gate),
                  launcher=pin(Path(__file__)), helpers={p.name:pin(p) for p in PINS},
                  source_and_config_changed=False, physical_tested=False,
                  limits=dict(boot_seconds=BOOT_SECONDS, client_seconds=MODE_SECONDS, outer_seconds=OUTER_SECONDS),
                  private_run_basename=private.name, private_material_outside_repository=True,
                  firmware_certificate_date_validation=config.get('MBEDTLS_HAVE_TIME_DATE', False),
                  whole_service_stop='NOT_EXERCISED', case_count=85, processes={})
    guest = peer = health = None
    start = time.monotonic()
    uart = private/'qemu-uart.log'
    def save():
        report['elapsed_seconds'] = round(time.monotonic()-start, 3)
        write(report_path, report)
    def check_guest():
        require(guest.poll() is None, 'owned-guest-exited')
        require(uart.stat().st_size <= 4*1024*1024, 'uart-capture-limit')
        text = uart.read_text(errors='replace')
        require(not helper['FATAL'].search(text), 'guest-fatal-marker')
        require(time.monotonic()-start < OUTER_SECONDS, 'launcher-watchdog-expired')
        return text
    try:
        if a.transport == 'wss':
            nvs, tls = provision(a, private)
            flash[0x9000:0xe000] = nvs
            binding['certificate_sha256'] = tls['certificate_sha256']
            report['tls_offline'] = tls
        flash_path = private/'flash.bin'
        flash_path.write_bytes(flash)
        flash_hash = sha(flash)
        port = helper['local_port']()
        command = [str(a.qemu.resolve()), '-global', 'driver=ssi.esp32.spi,property=input-delay-ns,value=25',
                   '-audiodev', 'none,id=quiet', '-M', 'esp32,st7789=on,audiodev=quiet,dac-rate=48000',
                   '-smp', '2', '-L', str(a.rom.resolve()), '-display', 'none', '-monitor', 'none',
                   '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic',
                   'user,model=open_eth,restrict=on,hostfwd=tcp:127.0.0.1:'+str(port)+'-:'+('443' if a.transport=='wss' else '80'),
                   '-drive', 'file='+str(flash_path).replace(',', ',,')+',if=mtd,format=raw']
        write(private/'actual-command.json', command)
        write(a.output/'binding.json', binding)
        report.update(binding=binding, host_loopback_port=port,
                      command_template=['<PINNED_QEMU>' if x==command[0] else '<PINNED_ROM>' if x==str(a.rom.resolve())
                                        else 'file=<EXTERNAL_PRIVATE_FLASH>,if=mtd,format=raw' if x.startswith('file=') else x for x in command])
        save()
        with uart.open('xb') as log:
            guest = subprocess.Popen(command, cwd=private, stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            report['processes']['qemu_pid'] = guest.pid
            save()
            endpoint = client_api['Endpoint'](a.transport+'://localhost:'+str(port)+'/ws', a.ca,
                                              binding.get('certificate_sha256'))
            health = client_api['Health'](endpoint)
            boot_end = time.monotonic()+BOOT_SECONDS
            while time.monotonic() < boot_end:
                text = check_guest()
                if 'CYD_OPENETH_READY' in text and ('Native HTTPS server started' if a.transport=='wss' else 'Native HTTP server started') in text:
                    try:
                        initial = health.read()
                        status = health.read('/api/native/status')
                    except (OSError, http.client.HTTPException, client_api['CheckFailure']):
                        health.close()
                        time.sleep(0.2)
                        continue
                    require(initial.get('allocation_failures') == 0, 'boot-allocation-failure')
                    require(status.get('audio') is False, 'idle-radio-required')
                    require('ST7789: SPI2 DMA' in text and 'Pipeline ready:' in text, 'production-pipeline-markers-missing')
                    report['initial_health'] = client_api['health_summary'](initial)
                    break
                time.sleep(0.2)
            else:
                raise Reject('guest-boot-deadline')
            health.close()
            health = None
            client_command = [sys.executable, '-B', str(CLIENT), '--execute', '--endpoint', endpoint.url,
                              '--binding', str(a.output/'binding.json'), '--output', str(a.output/'client')]
            if a.transport == 'wss':
                client_command += ['--ca', str(a.ca.resolve())]
            with (private/'client-terminal.log').open('xb') as terminal:
                peer = subprocess.Popen(client_command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=terminal,
                                        stderr=subprocess.STDOUT,
                                        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                report['processes']['client_pid'] = peer.pid
                report['state'] = 'RUNNING_CASES'
                save()
                while peer.poll() is None:
                    check_guest()
                    time.sleep(0.2)
            check_guest()
            result = load(a.output/'client/report.json')
            report.update(client_exit_code=peer.returncode, client_report=pin(a.output/'client/report.json'),
                          client_state=result['state'], complete_matrix=result.get('complete_matrix', False),
                          cases_exercised=len(result['cases']), final_post_close_health=result.get('final_post_close_health'))
            require(peer.returncode == 0 and result.get('complete_matrix') is True and len(result['cases']) == 85,
                    'client-matrix-nonpass')
            report['state'] = 'TERMINAL_PASS'
    except BaseException as error:
        report.update(state='TERMINAL_NONPASS', category=str(error) if isinstance(error, Reject) else type(error).__name__)
    finally:
        if health is not None:
            with contextlib.suppress(Exception):
                health.close()
        for name, child in (('client', peer), ('qemu', guest)):
            try:
                terminate_owned(child)
                report['processes'][name+'_exit_code'] = None if child is None else child.returncode
            except BaseException as error:
                report.update(state='TERMINAL_NONPASS', cleanup_category=type(error).__name__)
        report['private_log_pins'] = {p.name:pin(p) for p in private.iterdir() if p.is_file() and p.suffix in ('.log', '.stdout', '.stderr')}
        if (private/'flash.bin').exists():
            report['flash_unchanged'] = sha((private/'flash.bin').read_bytes()) == flash_hash
            if not report['flash_unchanged']:
                report.update(state='TERMINAL_NONPASS', category='private-flash-changed')
        try:
            report['released_helper_pins_still_match'] = all(pin(p)['sha256']==v for p,v in PINS.items())
            report['all_input_pins_still_match'] = all(pin(p)==expected for p,expected in input_pins.items())
            report['checkout_commit_still_matches'] = git('rev-parse', 'HEAD') == CHECKOUT
            if not all(report[k] for k in ('released_helper_pins_still_match', 'all_input_pins_still_match', 'checkout_commit_still_matches')):
                report.update(state='TERMINAL_NONPASS', category='released-input-changed-during-run')
        except BaseException as error:
            report.update(state='TERMINAL_NONPASS', input_recheck_category=type(error).__name__)
        report['owned_processes_stopped'] = all(child is None or child.poll() is not None for child in (peer, guest))
        report['private_material_retained'] = a.keep_private or not report['owned_processes_stopped']
        if not report['private_material_retained']:
            try:
                require(private.resolve(strict=True) == private and private.parent == parent and
                        private.name.startswith('yoradio-rfc-'), 'cleanup-root-owner-mismatch')
                shutil.rmtree(private)
            except BaseException as error:
                report.update(state='TERMINAL_NONPASS', private_material_retained=True,
                              private_cleanup_category=type(error).__name__)
        save()
    print(json.dumps(dict(state=report['state'], cases_exercised=report.get('cases_exercised', 0),
                          private_material_retained=report['private_material_retained'])))
    return 0 if report['state']=='TERMINAL_PASS' else 1


def main(argv=None):
    a = options(argv)
    if a.check_options:
        print(json.dumps(dict(state='OPTIONS_VALID', transport=a.transport, execution=False, case_count=85)))
        return 0
    prepared = preflight(a)
    if not a.execute:
        print(json.dumps(dict(state='PREFLIGHT_PASS', execution=False, transport=a.transport, case_count=85)))
        return 0
    return execute(a, prepared)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Reject as error:
        print(json.dumps(dict(state='REJECTED', category=str(error))))
        raise SystemExit(2)
    except Exception as error:
        # Arbitrary exception messages may contain private filenames.
        print(json.dumps(dict(state='REJECTED', category=type(error).__name__)))
        raise SystemExit(2)
