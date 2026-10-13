from pathlib import Path
import hashlib
import json
import shutil

root = Path.cwd()
run = root/'.build/early-owner-public-suite-01'
destination = root/'tests/results/esp32c3-stream-probe-20261013/early-owner-public-suite-01'
controller = json.loads((run/'controller.json').read_text())
report = json.loads((run/'physical/report.json').read_text())
health = json.loads((run/'physical/health.json').read_text())
restore = controller['restoration']
assert restore['image']['app_elf_sha256'] == controller['original']['app_elf_sha256']
assert not restore['status']['audio']
assert all(restore[k] is True for k in ('wifi_unchanged','playlist_unchanged','settings_unchanged'))
assert controller['candidate'] == report['image']
assert controller['installed']['app_elf_sha256'] == report['image']['app_elf_sha256']

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for rel, digest in report['test_sources_sha256'].items():
    assert sha(root/rel) == digest, rel
destination.mkdir(parents=True,exist_ok=False)
(destination/'.gitattributes').write_text('* -text\n')
for p in run.rglob('*'):
    if p.is_file():
        target=destination/p.relative_to(run)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,target)
for rel in report['test_sources_sha256']:
    target=destination/'sources'/rel
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(root/rel,target)
shutil.copyfile(root/'.build/run-early-owner-public-suite.py',destination/'controller.py')
shutil.copyfile(__file__,destination/'archive.py')
trace=[]
for line in (run/'physical/request-phases.jsonl').read_text().splitlines():
    item=json.loads(line)
    if item.get('result')=='FAIL':trace.append(item)
summary=dict(passed=controller['test_exit_code']==0, cases=[{k:c[k] for k in ('name','result','reason') if k in c} for c in report['cases']],
    failed_request_phases=trace, restoration_verified=True,
    health=dict(boot_ids=sorted({h['boot_id'] for h in health}),
        allocation_failures=max(h['allocation_failures'] for h in health),
        decoder_failures=max(h['decoder_failure']['sequence'] for h in health),
        task_watchdog_events=max(h['task_watchdog_events'] for h in health)),
    public_observation_seconds=report['public_seconds'], production_qualified=False,
    scope='Five public HTTPS variants plus HTTP source failures and WebSocket checks on the exact public-root image. Preserve incomplete observations and failed requests; successful later cases do not establish their cause or a fix. No analog continuity or full production qualification claim.')
(destination/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(destination/'sha256.json').write_text(json.dumps({p.relative_to(destination).as_posix():sha(p) for p in sorted(destination.rglob('*')) if p.is_file()},indent=2)+'\n')
print(json.dumps(summary,indent=2))
