"""Summarize bounded heap metadata; never infer TCP ownership from size alone."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def summarize(path):
    records = json.loads(path.read_text())
    snapshots, tcp_events, allocation_events = [], [], []
    for record in records:
        line = record['line']
        fields = dict(re.findall(r'(\w+)=([\w.-]+)', line))
        if 'PERF TCP_' in line:
            tcp_events.append(dict(at=record['at'], operation='free' if 'TCP_FREE' in line else 'alloc',
                address=fields['address'], state=int(fields['state']) if 'state' in fields else None))
        elif 'PERF CODEC_ALLOC:' in line:
            allocation_events.append(dict(at=record['at'], requested=int(fields['requested']),
                                          address=fields['address']))
        elif 'PERF HEAP:' in line:
            snapshots.append(dict(at=record['at'], stage=fields.pop('stage'),
                **{k:int(v) for k,v in fields.items()}, rows=[]))
        elif 'PERF BLOCK:' in line:
            assert snapshots and snapshots[-1]['stage'] == fields['stage'], 'Missing heap header'
            snapshots[-1]['rows'].append(dict(heap=fields['heap'], address=fields['address'],
                                             bytes=int(fields['bytes']), used=bool(int(fields['used']))))
    assert snapshots, 'No heap evidence'
    for s in snapshots:
        s['received'] = len(s['rows'])
        s['selection_complete'] = s['dropped'] == 0 and s['received'] == s['selected']
        s['dividers'] = []
        eligible = s['rows'] if s['selection_complete'] else []
        for before, middle, after in zip(eligible, eligible[1:], eligible[2:]):
            if (before['heap'] == middle['heap'] == after['heap'] and
                not before['used'] and middle['used'] and not after['used'] and
                before['bytes'] >= 4096 and after['bytes'] >= 4096 and middle['bytes'] <= 512 and
                int(before['address'],16)+before['bytes']+4 == int(middle['address'],16) and
                int(middle['address'],16)+middle['bytes']+4 == int(after['address'],16)):
                # A later free corroborates TCP ownership only if there is no
                # intervening allocation of another TCP object at this address.
                next_tcp = next((e for e in tcp_events if e['address'] == middle['address'] and e['at'] > s['at']), None)
                s['dividers'].append(dict(before=before, block=middle, after=after,
                    next_tcp_event=next_tcp, tcp_free_seen=bool(next_tcp and next_tcp['operation']=='free')))
        s['raw_largest_free'] = max((r['bytes'] for r in eligible if not r['used']), default=None)
        # Keep the full raw metadata in performance.json; report the large
        # retention region explicitly for reproducible allocation comparisons.
        s['retention_rows'] = [r for r in s.pop('rows') if r['heap']=='0x3fcc0000']
    return dict(raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                note='Raw block lengths; not TLSF rounded maximum allocation. TCP lifetime correlation is separate from structure-size equality.',
                snapshots=snapshots, tcp_events=tcp_events, codec_allocations=allocation_events)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.input)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('snapshots:',len(result['snapshots']), 'incomplete:',
          sum(not s['selection_complete'] for s in result['snapshots']),
          'TCP events:',len(result['tcp_events']))
