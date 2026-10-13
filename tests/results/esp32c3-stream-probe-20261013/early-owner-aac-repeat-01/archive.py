from pathlib import Path
import hashlib
import json
import shutil
import sys

root=Path.cwd()
sys.path.insert(0,str(root/'tools/esp32c3_tests'))
from production_health import output_window
source=root/'.build/early-owner-public-aac-repeat-01'
destination=root/'tests/results/esp32c3-stream-probe-20261013/early-owner-aac-repeat-01'
controller=json.loads((source/'controller.json').read_text())
assert controller['planned_repetitions']==3 and len(controller['runs'])==3
restore=controller['restoration']
assert restore['image']['app_elf_sha256']==controller['original']['app_elf_sha256']
assert not restore['status']['audio']
assert all(restore[k] for k in ('wifi_unchanged','playlist_unchanged','settings_unchanged'))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

reports=[]
summary=dict(planned_repetitions=3,restoration_verified=True,runs=[],production_qualified=False)
boots=set()
for attempt in range(1,4):
    directory=source/f'physical-{attempt}'
    report=json.loads((directory/'report.json').read_text())
    health=json.loads((directory/'health.json').read_text())
    assert report['image']==controller['candidate']
    assert report['public_seconds']==120
    assert list(report['public_urls'])==['groovesalad-128-aac']
    for rel,digest in report['test_sources_sha256'].items():assert sha(root/rel)==digest,rel
    reports.append(report)
    boots.update(h['boot_id'] for h in health)
    row=dict(attempt=attempt,cases=[{k:c[k] for k in ('name','result','reason') if k in c} for c in report['cases']],
        allocation_failures=max(h['allocation_failures'] for h in health),
        decoder_failures=max(h['decoder_failure']['sequence'] for h in health),
        watchdog_events=max(h['task_watchdog_events'] for h in health),
        failure_snapshots=report.get('failure_snapshots',{}))
    row['failed_request_phases']=[event for line in (directory/'request-phases.jsonl').read_text().splitlines()
        if (event:=json.loads(line)).get('result')=='FAIL']
    brackets={}
    for name,snapshot in report.get('failure_snapshots',{}).items():
        before=[h for h in health if h['at']<snapshot['started_at']]
        after=snapshot['health']
        if before and after:
            try:
                brackets[name]=dict(before=before[-1],after=after[-1],output=output_window([before[-1],after[-1]]))
            except Exception as error:
                brackets[name]=dict(unavailable=type(error).__name__)
    row['diagnostic_output_brackets']=brackets
    summary['runs'].append(row)
summary['boot_ids']=sorted(boots)
summary['scope']='Three preplanned two-minute AAC-LC observations on one installed candidate. Original failures remain failures; diagnostic endpoint counters do not establish analog continuity or attribute TCP packet loss.'
destination.mkdir(parents=True,exist_ok=False)
(destination/'.gitattributes').write_text('* -text\n')
for p in source.rglob('*'):
    if p.is_file():
        target=destination/p.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
for rel in ('tools/esp32c3_tests/quiet_acceptance.py','tools/esp32c3_tests/production_health.py',
            'tools/esp32c3_tests/sustained_output.py','tools/esp32c3_tests/trace_transport.py',
            'tools/esp32c3_tests/common.py','tools/esp32c3_tests/run.py',
            'tools/esp32c3_tests/public_streams.py','tools/esp32c3_tests/aac_reference.py',
            'tools/esp32c3_tests/ota.py','tests/test-production-health.py',
            'tools/esp32c3_tests/public_streams.json'):
    target=destination/'sources'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,target)
shutil.copyfile(root/'.build/run-early-owner-public-aac-repeat.py',destination/'controller.py')
shutil.copyfile(__file__,destination/'archive.py')
(destination/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(destination/'sha256.json').write_text(json.dumps({p.relative_to(destination).as_posix():sha(p) for p in sorted(destination.rglob('*')) if p.is_file()},indent=2)+'\n')
print(json.dumps(summary,indent=2))
