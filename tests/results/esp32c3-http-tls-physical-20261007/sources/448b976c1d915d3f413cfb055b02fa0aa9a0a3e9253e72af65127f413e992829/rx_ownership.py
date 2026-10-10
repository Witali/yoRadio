"""Validate live RX allocation snapshots; no payload bytes are inspected."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import struct
import zlib

OWNER_FIELDS = 'seq live peak allocs frees lost unmatched payload metadata missing walk_us'.split()
BLOCK_FIELDS = 'seq id payload payload_bytes metadata metadata_bytes'.split()


def fields(line, marker):
    if line.count('PERF ') != 1:
        raise ValueError('Merged/truncated telemetry line')
    required = OWNER_FIELDS if marker.startswith('PERF RX_OWNER') else BLOCK_FIELDS
    tail = line.split(marker, 1)[1]
    if marker.endswith('2:'):
        tokens = re.sub(r'\x1b\[[0-9;]*m', '', tail).strip().split(',')
        hex_fields = {'payload', 'metadata'} if required == BLOCK_FIELDS else set()
        if len(tokens) != len(required)+1 or not re.fullmatch(r'[0-9a-f]{8}', tokens[-1]):
            raise ValueError('Incomplete checksummed RX record')
        values = []
        for key, token in zip(required, tokens):
            hexadecimal = key in hex_fields
            if not re.fullmatch(r'[0-9a-f]{8}' if hexadecimal else r'\d+', token):
                raise ValueError('Invalid checksummed RX field')
            value = int(token, 16 if hexadecimal else 10)
            if not 0 <= value <= 0xffffffff:
                raise ValueError('RX field outside uint32 range')
            values.append(value)
        if zlib.crc32(struct.pack('<'+'I'*len(values), *values)) != int(tokens[-1], 16):
            raise ValueError('RX record checksum mismatch')
        return dict(zip(required, values))
    value = {k:int(v,0) for k,v in re.findall(r'(\w+)=(0x[0-9a-fA-F]+|\d+)',tail)}
    if set(value) != set(required):
        raise ValueError('Incomplete telemetry fields')
    return value


def analyze(records):
    snapshots = []
    for row in records:
        line = row['line']
        if 'serial capture interrupted' in line:
            raise ValueError('Interrupted telemetry capture')
        if 'PERF RX_OWNER:' in line or 'PERF RX_OWNER2:' in line:
            marker = 'PERF RX_OWNER2:' if 'PERF RX_OWNER2:' in line else 'PERF RX_OWNER:'
            value = fields(line,marker)
            if snapshots and value['seq'] != snapshots[-1]['seq'] + 1:
                raise ValueError('Missing/reset/duplicate snapshot sequence')
            if snapshots and any(value[k] < snapshots[-1][k] for k in ('allocs','frees','peak','unmatched')):
                raise ValueError('Regressing ownership counter')
            snapshots.append(dict(value, at=row['at'], blocks=[]))
        elif 'PERF RX_BLOCK:' in line or 'PERF RX_BLOCK2:' in line:
            marker = 'PERF RX_BLOCK2:' if 'PERF RX_BLOCK2:' in line else 'PERF RX_BLOCK:'
            value = fields(line,marker)
            if not snapshots or value['seq'] != snapshots[-1]['seq']:
                raise ValueError('RX block without its snapshot')
            snapshots[-1]['blocks'].append(value)
    if not snapshots: raise ValueError('Missing RX ownership telemetry')
    histogram = Counter()
    for snap in snapshots:
        blocks = snap['blocks']
        if snap['lost'] or snap['missing']: raise ValueError('Incomplete ownership/range evidence')
        if len(blocks) != snap['live'] or len({b['id'] for b in blocks}) != len(blocks):
            raise ValueError('Missing/duplicate live RX owners')
        if snap['allocs']-snap['frees'] != snap['live']:
            raise ValueError('RX allocation/free accounting mismatch')
        if snap['peak'] < snap['live'] or any(not 0 < b['id'] <= snap['allocs'] for b in blocks):
            raise ValueError('Invalid lifetime/peak counter')
        seen = {}; totals = dict(payload=0,metadata=0)
        for block in blocks:
            for kind in totals:
                address,size = block[kind],block[kind+'_bytes']
                if not address or not size: raise ValueError('Missing allocated range')
                if address in seen:
                    if seen[address] != size: raise ValueError('Conflicting allocation sizes')
                else:
                    seen[address]=size;totals[kind]+=size;histogram[size]+=1
        if any(totals[k] != snap[k] for k in totals):
            raise ValueError('RX sum double counted or incomplete')
        snap['unique_blocks']=len(seen)
        snap['allocated_payload_bytes']=sum(seen.values())
    return dict(scope='Live netif RX heap payload capacity; excludes allocator block headers, TCP copies and all other owners',
                snapshots=snapshots, complete=True,
                maximum_live=max(s['live'] for s in snapshots),
                maximum_allocated_payload_bytes=max(s['allocated_payload_bytes'] for s in snapshots),
                maximum_walk_us=max(s['walk_us'] for s in snapshots),
                observed_size_histogram={str(size): count for size,count in sorted(histogram.items())})


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('performance',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();report=analyze(json.loads(args.performance.read_text()))
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='snapshots'}))
