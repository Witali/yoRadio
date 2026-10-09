"""Repeat the original framing-to-certificate sequence, then verify full AAC recovery."""
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parent
repo=Path.cwd()
old=repo/'tests/results/esp32c3-min250-tls-ota-20261009/physical.py'
source=old.read_text().replace('c3-min250-tls-ota-20261009','c3-certificate-recovery-20261009')
start=source.index("    run_phase('eof-https-all'")
end=source.index("    save('settings-after-tests.json'",start)
source=source[:start]+'''    require(all(p['code']==0 for p in phases),'Preserve failure before later recovery checks')
    BOARD.stop()
    run_phase('records-after-rejection','tools/esp32c3_tests/trace_transport.py',[
        '--runner','tls_records','--',*shared,*tls,'--seconds','75','--mode','grow',
        '--pacing-ratio','1.0','--output',OUT/'records-after-rejection'],160)
'''+source[end:]
source=source.replace('attempted=False\ntry:',
    'from failure_monitor import FailureMonitor\nmonitor=FailureMonitor(OUT)\nattempted=False\ntry:')
start=source.index('attempted=False\ntry:')
source=source[:start]+'try:\n'+''.join('    '+line+'\n' for line in source[start:].splitlines())+'finally:\n    monitor.close()\n'
(root/'physical.py').write_text(source)
compile(source,str(root/'physical.py'),'exec')
for name in ('failure_monitor.py','capture-sockets.ps1'):
    (root/name).write_bytes((repo/'tests/results/esp32c3-min250-tls-ota-20261009'/name).read_bytes())
dependency='tests/results/esp32c3-reboot-tls-20261009/sources'
sources={}
for folder in ('tools/esp32c3_tests','tools/audio_test_server'):
    for path in sorted((repo/folder).glob('*.py')):
        name=path.relative_to(repo).as_posix()
        blob=path.read_bytes()
        assert blob==(repo/dependency/name).read_bytes(),name
        sources[name]=hashlib.sha256(blob).hexdigest()
(root/'sources.json').write_text(json.dumps(dict(dependency=dependency,files=sources),indent=2)+'\n')
for name in ('case-catalog.json','sdk-error-codes.json'):
    (root/name).write_bytes((repo/'tests/results/esp32c3-min250-tls-ota-20261009'/name).read_bytes())
artifacts=root/'artifacts'
artifacts.mkdir(exist_ok=True)
for name in ('manifest.json','sdkconfig'):
    (artifacts/name).write_bytes((repo/'firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250'/name).read_bytes())
print('Prepared original sequence and post-rejection HE-AACv2; verified',len(sources),'frozen source dependencies')
