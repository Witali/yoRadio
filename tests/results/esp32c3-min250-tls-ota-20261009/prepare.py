"""Prepare a bounded candidate qualification with unconditional restoration."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
repo = Path.cwd()
old = Path('tests/results/esp32c3-tls-final-gates-20261009/physical.py').read_text()
prefix = old.split("require(not OUT.exists()", 1)[0]
prefix = prefix.replace('Qualify PCM tail submission and playback', 'Qualify minimum-prefill TLS, EOF and OTA')
prefix = prefix.replace(".build/c3-tls-final-gates-20261009", ".build/c3-min250-tls-ota-20261009")
body = old[old.index("require(not OUT.exists()"):]
body = body.replace('esp32c3-idf-6.1-r9a97-pcm-tail', 'esp32c3-idf-6.1-r9a97-prefill-min250')
body = body.replace("UNTRUSTED=ROOT/'untrusted'", "UNTRUSTED=Path('.build/c3-tls-final-gates-20261009/untrusted')")
body = body.replace('e7d19f98719bb2f8b244096dffe73f57a98794d53fcb63ad918ff3ffbf3c1853',
                    '89d320f663bda6439456c95b6f47d09cd5cac2d434ff9fe85df568fa07fbae9c')
body = '\n'.join(line for line in body.splitlines() if not line.startswith("sources['.build/"))+'\n'
start = body.index("    print('INSTALL previously qualified PCM-tail image'")
end = body.index("    save('settings-after-tests.json'", start)
body = body[:start]+'''    print('INSTALL minimum-prefill candidate',flush=True)
    save('installed.json',dict(identity=install(IMAGE,'fractional'),persistence=verify_snapshot(BOARD,before)))
    BOARD.stop()
    run_phase('framing','tools/esp32c3_tests/trace_transport.py',[
        '--runner','tls_framing','--',*shared,*tls,'--output',OUT/'framing'],240)
    run_phase('certificate-rejection','tools/esp32c3_tests/trace_transport.py',[
        '--runner','diagnostic','--','run',*shared,'--suite','tls-rejection',
        '--https-origin','https://'+HOST+':8771','--tls-cert',UNTRUSTED/'cert.pem',
        '--tls-key',UNTRUSTED/'key.pem','--pacing-ratio','1.0','--leave-stopped',
        '--output',OUT/'certificate-rejection'],90)
    run_phase('eof-https-all','tools/esp32c3_tests/trace_transport.py',[
        '--runner','diagnostic','--','run',*shared,'--suite','eof','--eof-protocol','https',
        '--https-origin','https://'+HOST+':8771','--tls-cert',TRUST/'server.pem',
        '--tls-key',TRUST/'server.key','--unpaced-files','--delivery-stats','--pacing-ratio','1.0',
        '--sdkconfig',IMAGE.with_name('sdkconfig'),'--leave-stopped','--output',OUT/'eof-https-all'],720)
    run_phase('ota','tools/esp32c3_tests/ota_diagnostic.py',[
        *shared,'--firmware',IMAGE,'--case','hev2-44100-stereo',
        '--https-origin','https://'+HOST+':8771','--tls-cert',TRUST/'server.pem',
        '--tls-key',TRUST/'server.key','--output',OUT/'ota'],480)
    BOARD.stop()
    run_phase('records-after-ota','tools/esp32c3_tests/trace_transport.py',[
        '--runner','tls_records','--',*shared,*tls,'--seconds','75','--mode','grow',
        '--pacing-ratio','1.0','--output',OUT/'records-after-ota'],160)
'''+body[end:]
(root/'physical.py').write_text(prefix+body)

sources = {}
paths = [p for directory in ('tools/esp32c3_tests','tools/audio_test_server')
         for p in sorted(Path(directory).glob('*.py'))]
paths += [Path(p) for p in ('tests/test-ota-timeline.py','tests/test-ota-playback-format.py',
          'tests/test-esp32c3-ota-serial-health.py',
          'tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py')]
for p in paths:
    blob = p.read_bytes()
    dest = root/'sources'/p
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(blob)
    sources[p.as_posix()] = hashlib.sha256(blob).hexdigest()
(root/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
for name in ('case-catalog.json','flow_windows.py','eof_replay.py'):
    (root/name).write_bytes((Path('tests/results/esp32c3-prefill-matched-20261009')/name).read_bytes())
artifacts = root/'artifacts'
artifacts.mkdir(exist_ok=True)
for name in ('sdkconfig','manifest.json'):
    (artifacts/name).write_bytes((Path('firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250')/name).read_bytes())
print('Prepared controller and',len(sources),'source snapshots')
