"""Apply prepared profile/docs only after all exact-image physical gates pass."""
import hashlib,json
from pathlib import Path
base=Path('.build/c3-raw-tail-quiet-20261015');prepared=base/'promotion-candidates'
image=json.loads(Path('firmware/development/esp32c3-idf61-raw-tail-quiet/manifest.json').read_text())['image']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={'qualification':['public-files','http','transitions','network','websocket','ota'],
          'https-radio':['aac-heavy','other-public'],'sustained':['flac','vorbis','opus'],
          'https-lc-repeat':['aac-lc']}
evidence=[]
for campaign,suites in expected.items():
    control=base/campaign/'controller.json';c=json.loads(control.read_text())
    assert c['candidate']==image and 'failure' not in c and 'restoration_failure' not in c
    assert c['restored']['stopped'] and all(c['restored']['settings'].values())
    assert c['restored']['identity']['app_elf_sha256']==c['original']['app_elf_sha256']
    assert [t['suite'] for t in c['tests']]==suites and all(t['exit_code']==0 for t in c['tests'])
    for suite in suites:
        path=base/campaign/suite/'report.json';r=json.loads(path.read_text())
        assert r['cases'] and all(case['result']=='PASS' for case in r['cases']),(campaign,suite)
        evidence.append(dict(report=path.as_posix(),sha256=sha(path),checks=len(r['cases'])))
inputs=json.loads((prepared/'inputs.json').read_text())
for name,hashes in inputs.items():
    assert sha(Path(name))==hashes['original_sha256'],'Concurrent source change: '+name
    assert sha(prepared/name)==hashes['candidate_sha256'],'Prepared edit changed: '+name
for name in inputs:Path(name).write_bytes((prepared/name).read_bytes())
(base/'profile-promotion.json').write_text(json.dumps(dict(image=image,evidence=evidence,files=inputs,
    scope='Source profile promotion only. Fresh/cached configuration equivalence and final deployment are still required.'),indent=2)+'\n')
print('Applied reviewed profile/docs after all physical gates passed')
