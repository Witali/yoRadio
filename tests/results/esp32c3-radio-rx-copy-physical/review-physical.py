"""Review paired RX/heap evidence without adjusting playback acceptance gates."""
import hashlib,json,statistics,sys
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'test-sources/tools/esp32c3_tests'))
from rx_ownership import analyze, fields
from production_health import check_health
data=root/'physical'
read=lambda name:json.loads((data/name).read_text())
required=('initial.json','installed.json','status.json','health.json','results.json',
          'performance.json','serial-transport.json','restoration.json','recovery.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
initial=read('initial.json')
assert sha(root/'physical.py')==initial['controller_sha256']
for relative,digest in initial['test_sources'].items():
    assert sha(root/'test-sources'/relative)==digest,relative
records=read('performance.json')
try:
    owners=analyze(records)
    owner_summary={k:v for k,v in owners.items() if k!='snapshots'}
except ValueError as error:
    owner_summary=dict(complete=False,reason=str(error))
# Enumerate broken groups for diagnosis only. Never repair the global trace by
# dropping them. Separately bounded phases must independently pass analyze().
groups=[]
for row in records:
    if 'PERF RX_OWNER3:' in row['line']:groups.append([row])
    elif 'PERF RX_BLOCK2:' in row['line'] and groups:groups[-1].append(row)
issues=[]
for group in groups:
    try:analyze(group)
    except ValueError as error:
        header=fields(group[0]['line'],'PERF RX_OWNER3:')
        issues.append(dict(sequence=header['seq'],at=group[0]['at'],live=header['live'],
            block_records=len(group)-1,reason=str(error)))
owner_summary['incomplete_groups']=issues
serial=read('serial-transport.json')
observations=read('status.json')
first=observations[0]['started_at'];last=observations[-1]['ended_at']
interruptions=[row for row in serial if first<=row['at']<=last]
assert not interruptions,interruptions
summary={}
for batch in observations:
    name=batch['case']
    warmup=15 if name.startswith(('opus:','public-he')) else 0
    selected=[s for s in records if batch['started_at']+warmup<=s['at']<batch['ended_at']-1]
    try:phase_owners=analyze(selected)
    except ValueError as error:
        summary[name]=dict(complete=False,reason=str(error));continue
    samples=phase_owners['snapshots']
    assert samples,name
    heaps=[s['heap_free'] for s in samples]
    rx=[s['allocated_payload_bytes'] for s in samples]
    # Explanatory only: allocator headers and all non-RX owners are excluded.
    sums=[h+r for h,r in zip(heaps,rx)]
    paired={key:{'min':min(values),'max':max(values),'first':values[0],
                 'last':values[-1],'population_stddev':statistics.pstdev(values)}
            for key,values in (('heap_free',heaps),('rx_capacity',rx),('heap_plus_rx',sums))}
    correlation=statistics.correlation(heaps,rx) if len(samples)>1 and len(set(heaps))>1 and len(set(rx))>1 else None
    summary[name]=dict(complete=True,samples=len(samples),paired=paired,heap_rx_correlation=correlation,
        largest_minimum=min(s['heap_largest'] for s in samples),
        peak_live=max(s['live'] for s in samples),maximum_walk_us=max(s['walk_us'] for s in samples),
        lost=max(s['lost'] for s in samples),unmatched=max(s['unmatched'] for s in samples))
restored=read('restoration.json')
assert restored['identity']['app_elf_sha256']==initial['baseline']['app_elf_sha256']
assert restored['same_station']
assert all(s['audio']==initial['original']['audio'] for s in restored['states'][-3:])
results=read('results.json')
report=dict(result='PASS',scope='Evidence consistency and ownership attribution; retained gate failures are not waived',
    ownership_result='PASS' if owner_summary['complete'] else 'FAIL',
    laboratory_only=True,production_qualified=False,phases=summary,
    playback_gates=results,health=check_health(read('health.json')),
    owner_summary=owner_summary,
    capture_interruptions_in_observation=interruptions,restoration=restored,
    recovery=read('recovery.json'),
    limitations=['Five-second paired snapshots can miss short largest-block dips.',
        'Instrumentation changes RAM/timing; these results do not qualify the quiet production image.',
        'heap_plus_rx excludes allocator overhead and is explanatory, never a replacement acceptance gate.'],
    input_sha256={name:sha(data/name) for name in required})
(root/'physical-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(result=report['result'],phases=summary,health=report['health'])))
