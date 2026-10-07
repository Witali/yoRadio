#!/usr/bin/env python3
"""Compare audited PC18/PC19 decoder work and actual heap allocation in QEMU.

Instruction counts cover only the first decoder's process calls, including
enabled pointer/heap audits and guest interrupts. They exclude PCM printing,
output poisoning, the control decoder and explicit delays. This is not a
physical CPU benchmark or a production qualification gate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from compare_aac_sbr_gap_pcm import parse_gaps, read_log, verified_manifest


def one(log, pattern, name):
    rows = re.findall(pattern, log)
    if len(rows) != 1:
        raise ValueError('Missing or duplicate ' + name)
    return tuple(map(int, rows[0]))


def parse_work(log):
    parse_gaps(log)  # Require full PCM, lifecycle and suite completion too.
    if log.count('AAC_GAP_WORK_COUNTER nop1024=1025') != 1:
        raise ValueError('Unverified guest instruction counter')
    owner, block, context = one(log, r'AACCOMPACT_MEMORY owner_bytes=(\d+) '
        r'block_bytes=(\d+) context_bytes=(\d+)', 'SBR owner size')
    adapter, adapter_block = one(log, r'AAC_GAP_ADAPTER_MEMORY requested=(\d+) '
        r'allocated=(\d+)', 'native adapter size')
    if not 0 < context < adapter <= adapter_block or not 0 < owner <= block:
        raise ValueError('Inconsistent heap footprint')
    expected = [(name.replace('-', '_'), phase, meta['frames'])
                for name, meta in verified_manifest()['cases'].items()
                for phase in range(3)]
    rows = []
    for line in log.splitlines():
        if not line.startswith('AAC_GAP_WORK '):
            continue
        m = re.fullmatch(r'AAC_GAP_WORK case=(\w+) phase=(\d+) frames=(\d+) '
                         r'calls=(\d+) instructions=(\d+)', line)
        if not m:
            raise ValueError('Malformed decoder work row')
        case, phase, frames, calls, instructions = m.groups()
        row = dict(case=case, phase=int(phase), frames=int(frames),
                   calls=int(calls), instructions=int(instructions))
        if row['calls'] < row['frames'] or row['instructions'] <= row['calls']:
            raise ValueError('Invalid decoder work count')
        rows.append(row)
    if [(r['case'], r['phase'], r['frames']) for r in rows] != expected:
        raise ValueError('Missing, duplicate or reordered decoder work row')
    return dict(owner_requested=owner, owner_allocated=block,
                context_requested=context, adapter_requested=adapter,
                adapter_allocated=adapter_block,
                owner_and_adapter_allocated=block + adapter_block,
                instructions=sum(r['instructions'] for r in rows), phases=rows)


def compare_work(baseline_log, candidate_log):
    baseline, candidate = map(parse_work, (baseline_log, candidate_log))
    marker = ('AAC_PC19_METADATA_PASS pairs_per_channel=288 channels=2 '
              'real_clear=exact full_clear=exact reopen=zero side_bytes=144')
    if marker in baseline_log or candidate_log.count(marker) != 1:
        raise ValueError('Expected PC18 control and verified PC19 context storage')
    rows = []
    for before, after in zip(baseline['phases'], candidate['phases']):
        for key in ('case', 'phase', 'frames', 'calls'):
            if before[key] != after[key]:
                raise ValueError('Different decoder workload: ' + key)
        rows.append(dict(case=before['case'], phase=before['phase'],
                         baseline_instructions=before['instructions'],
                         candidate_instructions=after['instructions'],
                         change_percent=100 * (after['instructions'] / before['instructions'] - 1)))
    return dict(baseline=baseline, candidate=candidate, phases=rows,
                extra_owner_and_adapter_bytes=candidate['owner_and_adapter_allocated'] - baseline['owner_and_adapter_allocated'],
                instruction_change_percent=100 * (candidate['instructions'] / baseline['instructions'] - 1),
                memory_scope='Owner plus native adapter only; context is contained in adapter, not added twice',
                work_scope=__doc__, physical_cpu_qualified=False, production_qualified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-log', type=Path, required=True)
    parser.add_argument('--candidate-log', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = compare_work(read_log(args.baseline_log), read_log(args.candidate_log))
    result['log_sha256'] = {name: hashlib.sha256(path.read_bytes()).hexdigest()
                           for name, path in (('baseline', args.baseline_log), ('candidate', args.candidate_log))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('baseline', 'candidate', 'phases')}, indent=2))
