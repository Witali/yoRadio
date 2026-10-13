"""Validate complete idle heap-owner snapshots; never infer a missing owner."""
import argparse
import json
from pathlib import Path
import re

HEADER=re.compile(r'PERF HEAP_WATCH: seq=(\d+) first=(0x[0-9a-f]+) last=(0x[0-9a-f]+) live=(\d+) peak=(\d+) lost=(\d+) alloc_events=(\d+) free_events=(\d+) rows=(\d+) dropped=(\d+) unknown=(\d+) walk_us=(\d+)$')
ROW=re.compile(r'PERF HEAP_OWNER: seq=(\d+) row=(\d+) address=(0x[0-9a-f]+) bytes=(\d+) id=(\d+) requested=(\d+) task=(\S+)$')


def analyze(records):
    snapshots=[]
    current=None
    for record in records:
        line=record['line']
        if 'PERF HEAP_WATCH:' in line:
            match=HEADER.search(line)
            if not match: raise ValueError('Malformed heap snapshot header')
            if current and len(current['blocks'])!=current['rows']:
                raise ValueError('Missing heap snapshot rows')
            keys=('seq','first','last','live','peak','lost','alloc_events','free_events','rows','dropped','unknown','walk_us')
            current=dict(zip(keys,(int(v,16) if v.startswith('0x') else int(v) for v in match.groups())))
            if snapshots and current['seq']!=snapshots[-1]['seq']+1:
                raise ValueError('Missing heap snapshot sequence')
            if current['first']>=current['last']:
                raise ValueError('Invalid watched heap range')
            if not current['rows'] or current['peak']<current['live']:
                raise ValueError('Invalid heap snapshot counts')
            if snapshots and (current['first'],current['last'])!=(snapshots[0]['first'],snapshots[0]['last']):
                raise ValueError('Watched heap range changed')
            current.update(at=record['at'],blocks=[])
            snapshots.append(current)
        elif 'PERF HEAP_OWNER:' in line:
            match=ROW.search(line)
            if not match or not current: raise ValueError('Malformed/unframed heap row')
            seq,row,address,size,identity,requested,task=match.groups()
            if int(seq)!=current['seq'] or int(row)!=len(current['blocks']):
                raise ValueError('Missing/duplicate heap row')
            item=dict(address=int(address,16),bytes=int(size),id=int(identity),requested=int(requested),task=task)
            if item['bytes']<=0 or item['address']>=current['last'] or item['address']+item['bytes']<=current['first']:
                raise ValueError('Heap block outside watched range')
            if task=='free' and (item['id'] or item['requested']):
                raise ValueError('Free block carries live ownership')
            if task not in ('free','unknown') and not item['id']:
                raise ValueError('Missing allocation identity')
            if current['blocks']:
                previous=current['blocks'][-1]
                if previous['address']+previous['bytes']>item['address']:
                    raise ValueError('Overlapping or unordered heap blocks')
            current['blocks'].append(item)
    if not snapshots or len(current['blocks'])!=current['rows']:
        raise ValueError('Missing/incomplete heap snapshots')
    identities={}
    for snapshot in snapshots:
        known=[b for b in snapshot['blocks'] if b['id']]
        unknown=sum(b['task']=='unknown' for b in snapshot['blocks'])
        if snapshot['lost'] or snapshot['dropped'] or snapshot['unknown'] or unknown:
            raise ValueError('Heap ownership capture overflowed or contains unknown allocations')
        if len(known)!=snapshot['live'] or len({b['id'] for b in known})!=len(known):
            raise ValueError('Live ownership does not match heap walk')
        for block in known:
            description=(block['address'],block['requested'],block['task'])
            if block['id'] in identities and identities[block['id']]!=description:
                raise ValueError('Allocation identity changed its owner or address')
            identities[block['id']]=description
        snapshot['largest_raw_free']=max((b['bytes'] for b in snapshot['blocks'] if b['task']=='free'),default=0)
    return dict(complete=True,scope='Live allocation task/lifetime metadata within one initially free heap region; not a complete all-heap event trace',snapshots=snapshots)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('performance',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    records=json.loads(args.performance.read_text())
    try: result=analyze(records)
    except ValueError as error: result=dict(complete=False,reason=str(error))
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['complete'] else 1)
