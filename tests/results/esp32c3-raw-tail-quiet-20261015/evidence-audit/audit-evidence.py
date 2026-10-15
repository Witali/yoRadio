"""Recheck retained AAC numerical evidence and tie its codec archive to this image."""
import hashlib,json,subprocess,sys
from pathlib import Path
base=Path('.build/c3-raw-tail-quiet-20261015')
out=base/'evidence-audit';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[Path('tests/results/esp32c3-raw-tail-quiet-20261015/build/aac-audit.json'),
       Path('tests/results/esp32c3-aac-asymmetric-production-20261004/physical-patch-audit.json'),
       Path('tests/results/esp32c3-aac-asymmetric-production-20261004/qemu/audit.json')]
audits=[json.loads(p.read_text()) for p in paths]
report={'inputs':{p.as_posix():sha(p) for p in paths},'tests':[],
        'codec_sha256':audits[0]['codec_sha256'],
        'scope':'Revalidates archived PCM statistics, pointer/lifetime evidence and precision policy. Does not re-decode music PCM or replace physical qualification.'}
for path,audit in zip(paths[1:],audits[1:]):
    assert audit['codec_sha256']==report['codec_sha256'],str(path)
report['same_codec_archive']=True
for name in ('test-aac-recording-evidence.py','test-aac-asymmetric-production.py',
             'test-aac-precision-policy.py','test-aac-network-build-layout.py'):
    source=Path('tests')/name
    with (out/(name+'.log')).open('wb') as log:
        result=subprocess.run([sys.executable,'-B','-X','utf8',str(source)],stdout=log,stderr=subprocess.STDOUT,timeout=120)
    report['tests'].append(dict(path=source.as_posix(),sha256=sha(source),exit_code=result.returncode))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(name,result.returncode,flush=True)
report['passed']=all(t['exit_code']==0 for t in report['tests'])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
