# Appended to the established passive clock/flash capture and app-only OTA guard.
from public_streams import no_runtime_faults

require(not OUT.exists(), 'Preserve physical evidence')
OUT.mkdir()
IMAGE = Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-integer4/app.bin')
expected = image_info(IMAGE.read_bytes())
quiet = image_info(QUIET.read_bytes())
require(expected['sha256'] == '28d24c6f7e1dd59ff2908f9e53d658f30eaf012a8af94ee34e3174cb5d75bc00', 'Candidate changed')
require(quiet['sha256'] == '21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a', 'Restore changed')
audit = json.loads((ROOT/'build-audit.json').read_text())['4']
require(audit['result'] == 'PASS' and audit['image'] == expected, 'Build unaudited')
manifest = json.loads(IMAGE.with_name('manifest.json').read_text())
require(manifest['clock_mode'] == 'integer' and manifest['laboratory_only'], 'Wrong controls')
require(manifest['extra_trust_ca_sha256'] == sha((TRUST/'ca.pem').read_bytes()), 'Wrong trust')
cert = ssl._ssl._test_decode_cert(str(TRUST/'server.pem'))
require(ssl.cert_time_to_seconds(cert['notBefore']) < time.time() and
        ssl.cert_time_to_seconds(cert['notAfter']) > time.time()+3600, 'Certificate must cover campaign')
identity, initial = BOARD.info(), BOARD.status()
require(identity['app_elf_sha256'] == quiet['app_elf_sha256'], 'Unexpected initial image')
before = snapshot(BOARD)
sources = {p.as_posix():sha(p.read_bytes()) for folder in
           ('tools/esp32c3_tests', 'tools/audio_test_server') for p in sorted(Path(folder).glob('*.py'))}
require(sources == json.loads((ROOT/'sources.json').read_text()), 'Prepared sources changed')
script_sha = sha(Path(__file__).read_bytes())
save('initial.json', dict(identity=identity, status=initial, candidate=expected, quiet=quiet,
    source_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    controller_sha256=script_sha, test_sources_sha256=sources,
    host_clock=dict(api='time.perf_counter', **vars(time.get_clock_info('perf_counter'))),
    ca_sha256=sha((TRUST/'ca.pem').read_bytes()), leaf_sha256=sha((TRUST/'server.pem').read_bytes())))
phases = []
shared = ['--board', BOARD.origin, '--host', HOST, '--serial-port', PORT]
tls = ['--https-origin', 'https://'+HOST+':8771', '--tls-cert', str(TRUST/'server.pem'), '--tls-key', str(TRUST/'server.key')]


def run_phase(label, suites=(), extra=(), timeout=800):
    require(sha(Path(__file__).read_bytes()) == script_sha, 'Controller changed during campaign')
    for relative, digest in sources.items():
        require(sha(Path(relative).read_bytes()) == digest, 'Runner changed during campaign')
    require(BOARD.info()['app_elf_sha256'] == expected['app_elf_sha256'], 'Wrong image before phase')
    command = [sys.executable, '-X', 'utf8', 'tools/esp32c3_tests/trace_transport.py']
    if label == 'tls-record-grow':
        command += ['--runner', 'tls_records', '--', *shared, '--firmware', str(IMAGE),
            '--ca', str(TRUST/'ca.pem'), '--cert', str(TRUST/'server.pem'), '--key', str(TRUST/'server.key'),
            '--mode', 'grow', '--seconds', '600', '--pacing-ratio', '1.0']
    else:
        command += ['--runner', 'diagnostic', '--', 'run', *shared,
            '--sdkconfig', str(IMAGE.with_name('sdkconfig')), '--leave-stopped',
            '--unpaced-files', '--delivery-stats', '--pacing-ratio', '1.0']
        for suite in suites:
            command += ['--suite', suite]
    command += ['--output', str(OUT/label), *map(str, extra)]
    started = time.perf_counter()
    print('START', label, flush=True)
    with (OUT/(label+'.log')).open('xb') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        save('running.json', dict(phase=label, pid=process.pid, started_at=started))
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(); code = 124
    result = dict(name=label, code=code, seconds=time.perf_counter()-started)
    phases.append(result)
    save('phases.json', phases)
    print('END', label, code, flush=True)
    require(code != 124, 'Physical phase timed out')
    require(BOARD.info()['app_elf_sha256'] == expected['app_elf_sha256'], 'Wrong image after phase')
    rows = json.loads((OUT/label/'performance.json').read_text())
    try:
        require(bool(rows), 'Empty runtime capture')
        no_runtime_faults(rows)
        runtime = dict(result='PASS')
    except (AssertionError, ValueError) as error:
        runtime = dict(result='FAIL', reason=str(error))
    save(label+'-runtime-after-close.json', runtime)


attempted = False
try:
    attempted = True
    print('INSTALL integer-clock expanded FLAC candidate', flush=True)
    save('installed.json', dict(identity=install(IMAGE, 'integer', 'candidate'),
                                persistence=verify_snapshot(BOARD, before)))
    BOARD.stop()
    run_phase('matrix-https', ['https'], tls)
    run_phase('transitions-switch', ['transitions', 'websocket', 'switch'], ['--cycles', '3'], timeout=650)
    run_phase('tls-record-grow', timeout=720)
    save('settings-after-tests.json', verify_snapshot(BOARD, before))
except Exception as error:
    save('controller-failure.json', dict(exception_chain=exception_details(error)))
    raise
finally:
    if attempted:
        print('RESTORE production application', flush=True)
        try:
            restored = install(QUIET)
            if not initial['audio']:
                BOARD.stop()
            states = []
            for _ in range(3):
                time.sleep(5); states.append(BOARD.status())
            save('restoration.json', dict(identity=restored, persistence=verify_snapshot(BOARD, before), states=states))
            require(all(s['audio'] == initial['audio'] for s in states), 'Initial playback not restored')
            print('RESTORED production and settings', flush=True)
        except Exception as error:
            save('restoration-failure.json', dict(exception_chain=exception_details(error)))
            raise
