import hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from production_health import check_health,check_decoder_health
run=sys.argv[1]
base=Path('.build/c3-production-qualification-20261014')
src=base/run;dst=Path('tests/results/esp32c3-production-qualification-20261014')/run
r=json.loads((src/'report.json').read_text())
assert any(c['name']=='all-decoder-health' for c in r['cases'])
assert not dst.exists();shutil.copytree(src,dst)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((dst.parent/'http-eof-01/test-source-reference.json').read_text());mapping={}
for name,digest in r['test_sources_sha256'].items():
    saved=Path(old[name]['path']) if name in old else Path(name)
    if not saved.is_file() or sha(saved)!=digest:
        p=Path(name);assert sha(p)==digest,name
        saved=dst/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved)
    mapping[name]=dict(path=saved.as_posix(),sha256=digest)
(dst/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
if not run.endswith('01'):
    saved=dst/'sources/tests/test-quiet-idle-gates.py'
    saved.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile('tests/test-quiet-idle-gates.py',saved)
shutil.copyfile(base/('run-network-ws.py' if run.endswith('01') else 'run-network-ws-02.py'),dst/'controller.py')
shutil.copyfile(base/'freeze-network.py',dst/'freeze.py')
shutil.copyfile('firmware/development/esp32c3-idf61-production-20261013/manifest.json',dst/'firmware-manifest.json')
health=json.loads((src/'health.json').read_text())
states=json.loads((src/'status.json').read_text())
phases=[json.loads(l) for l in (src/'request-phases.jsonl').read_text().splitlines()]
summary=dict(image=r['image'],counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},
    failures=[c for c in r['cases'] if c['result']!='PASS'],health=check_health(health),decoder_health=check_decoder_health(health),
    failed_request_phases=[p for p in phases if p['result']!='PASS'],idle=r['idle'],
    scope='Original gates retained, including failures. Recovery after each network fault uses explicit Stop/Play, not automatic reconnect. No exact watchdog deadline or acoustic claim.')
summary['fault_observations']=[dict(case=s['case'],observations=len(s['samples']),
    played=any(v['audio'] for v in s['samples']),
    last_three=s['samples'][-3:],
    all_last_three_stopped=len(s['samples'])>=3 and all(v['audio'] is False for v in s['samples'][-3:]))
    for s in states if s['case'].startswith('fault:')]
(dst/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
(dst/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
checks={p.relative_to(dst).as_posix():sha(p) for p in sorted(dst.rglob('*')) if p.is_file()}
(dst/'sha256.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(dict(run=run,counts=summary['counts'],health=summary['health'])))
