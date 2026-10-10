"""Validate bounded codec allocation logs and retain a requested-payload timeline."""
import argparse
import json
from pathlib import Path
import re

EVENT = re.compile(r'PERF ALLOC: phase=(\S+) op=([+!\-]) id=(\d+) module=(\S+) size=(\d+) live=(\d+) pointer=(\S+)')
SUMMARY = re.compile(r'PERF ALLOC: phase=(\S+) live=(\d+) peak=(\d+) lost=(\d+) storage=(\d+)')


def analyze(text):
    active, timeline, summaries = {}, [], []
    peak = 0
    for line in text.splitlines():
        match = SUMMARY.search(line)
        if match:
            phase, live, high, lost, storage = match.groups()
            if int(lost):
                raise ValueError('Allocation trace overflowed; lifetime evidence is incomplete')
            summaries.append(dict(phase=phase, live=int(live), peak=int(high), storage=int(storage)))
        match = EVENT.search(line)
        if not match:
            continue
        phase, operation, identity, module, size, reported, pointer = match.groups()
        identity, size, reported = int(identity), int(size), int(reported)
        if operation == '+':
            if identity in active or not identity:
                raise ValueError('Duplicate/invalid allocation identity')
            active[identity] = dict(bytes=size, module=module)
        elif operation == '-':
            old = active.pop(identity, None)
            if old != dict(bytes=size, module=module):
                raise ValueError('Free without matching allocation')
        current = sum(item['bytes'] for item in active.values())
        if current != reported:
            raise ValueError('Incomplete trace or incorrect live accounting')
        peak = max(peak, current)
        timeline.append(dict(phase=phase, operation=operation, identity=identity,
                             module=module, bytes=size, live=current))
    if not timeline or not summaries:
        raise ValueError('No allocation evidence')
    if peak != max(row['peak'] for row in summaries):
        raise ValueError('Peak does not match recorded events')
    return dict(scope='Requested payload through codec media allocation shims; excludes allocator overhead, transient realloc copies, caller PCM, ADTS and non-codec heap',
                peak_bytes=peak, final_live_bytes=sum(item['bytes'] for item in active.values()),
                final_allocations=active, summaries=summaries, events=timeline)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = analyze(args.log.read_text(encoding='utf-8', errors='replace'))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: peak requested payload', report['peak_bytes'], 'final live', report['final_live_bytes'])
