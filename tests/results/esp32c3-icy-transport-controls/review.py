"""Replay completed physical controls before freezing the evidence."""
import ast
import json
import sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Failure, fixtures, sha, check_playback
from production_health import check_health
from sustained_output import sustained_window, check_output, check_memory
ROOT=Path(__file__).resolve().parent
P=ROOT/'physical'
load=lambda name:json.loads((P/name).read_text())
initial=load('initial.json')
assert sha((ROOT/'physical.py').read_bytes())==initial['controller_sha256']
for name,digest in initial['test_sources'].items():assert sha((ROOT/'test-sources'/name).read_bytes())==digest,name
# Final module also retains the pre-existing standalone AAC IcyServer API.
# The new framer used on the board must remain identical.
module='tools/audio_test_server/icy.py'
framer=lambda p:ast.dump(next(n for n in ast.parse(p.read_text()).body if isinstance(n,ast.ClassDef) and n.name=='IcyFramer'))
assert framer(Path(module))==framer(ROOT/'test-sources'/module)
specs=fixtures(Path('tests/results/esp32c3-mp3-transport-controls-20261010/fixtures/manifest.json'))
batches={b['case']:b for b in load('status.json')}
rows=load('health.json')
def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except Failure as error:return dict(result='FAIL',reason=str(error))
summary={}
for name,result in load('results.json').items():
    batch=batches[name]
    states=batch['samples']
    selected=[h for h in rows if batch['started_at']<=h['at']<=batch['ended_at']]
    steady,health=sustained_window(states,selected,90)
    spec=specs[result['fixture']]
    assert spec['sha256']==result['fixture_sha256']
    checks=dict(format=evaluate(lambda:check_playback(states,spec,minimum=45,warmup=15)),
                output=evaluate(lambda:check_output(health)),memory=evaluate(lambda:check_memory(health)))
    assert all(checks[k]==result[k] for k in checks)
    event=load(name+'-server.json')[0]
    if result['interval']:
        assert event['icy_interval']==result['interval'] and event['icy_insertions']>0
        assert event['wire_sent']==event['sent']+event['icy_metadata_bytes']
    assert sum(w['bytes'] for w in event['delivery']['windows'])==event.get('wire_sent',event['sent'])
    summary[name]=dict(checks=checks,audio_bytes=event['sent'],icy_insertions=event.get('icy_insertions',0))
assert len(summary)==3
restored=load('restoration.json')
assert restored['identity']==initial['identity'] and restored['same_station']
assert all(restored['persistence'].values()) and all(s['audio']==initial['status']['audio'] for s in restored['states'])
assert restored['health']==check_health(rows)
(ROOT/'review.json').write_text(json.dumps(dict(review='PASS',cases=summary,restoration=True),indent=2)+'\n')
print('Replay PASS:',{name:{k:v['result'] for k,v in row['checks'].items()} for name,row in summary.items()})
