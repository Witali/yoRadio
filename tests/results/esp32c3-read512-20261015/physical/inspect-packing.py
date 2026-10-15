import collections,json,statistics
from pathlib import Path
base=Path('.build/c3-read512-20261015/physical');result=[]
for path in sorted(base.rglob('report.json')):
    folder=path.parent;report=json.loads(path.read_text())
    states=json.loads((folder/'status.json').read_text());health=json.loads((folder/'health.json').read_text())
    batch=next(s for s in states if s['case']=='public-flac-reference')
    paired=[h for h in health if batch['started_at']<=h['at']<=batch['ended_at']]
    assert len(paired)==len(batch['samples'])
    selected=[h for s,h in zip(batch['samples'],paired) if s['seconds']>=2]
    payload=[];average_packet=[];partial=[]
    for row in selected:
        q=row['input_queue'];count=q['ready']+q['reading']
        # packet_capacity=2048 payload + 12 bytes of current packet metadata.
        header=q['packet_capacity']-2048;assert header==12
        size=q['ready_bytes']+q['reading_bytes']-header*count
        payload.append(size)
        if count:average_packet.append(size/count);partial.append(size<2048*count)
    def spread(values):return dict(min=min(values),median=statistics.median(values),max=max(values)) if values else None
    item=dict(case=folder.relative_to(base).as_posix(),samples=len(selected),
        input_payload_bytes=spread(payload),mean_payload_per_committed_or_reading_packet=spread(average_packet),
        samples_with_partial_packets=sum(partial),samples_with_committed_or_reading_packets=len(partial),
        process_max_since_boot_us=selected[-1]['pipeline']['process_max_us'],web_memory=report['web_memory'],
        scope='Sampled queue occupancy, excluding writing leases; reading leases can be partially consumed. Not allocated capacity, remaining undecoded bytes, throughput or CPU utilization')
    result.append(item);print(json.dumps(item))
(base/'packing.json').write_text(json.dumps(result,indent=2)+'\n')
