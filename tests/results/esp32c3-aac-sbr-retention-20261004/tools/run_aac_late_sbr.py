#!/usr/bin/env python3
"""Check the QEMU-only late-SBR experiment; never qualify transition PCM."""
import re
import sys
import run_aac_bfp16 as common

CASES = {
    'lc_44100_stereo': (72, 147456), 'lc_22050_mono': (39, 39936),
    'lc_48000_stereo': (78, 159744), 'he_44100_stereo': (42, 172032),
    'he_48000_stereo': (45, 184320), 'hev2_44100_stereo': (45, 184320),
}


def one(log, pattern):
    rows = re.findall(pattern, log)
    if len(rows) != 1:
        raise ValueError('Missing or duplicate completion: ' + pattern.split(' ')[0])
    return rows[0]


def parse_log(log, *, require_retention=False):
    if re.search(r'assert failed|Guru Meditation|CORRUPT HEAP|aac_pointer: field=', log):
        raise ValueError('Decoder, pointer or heap failure')
    for marker in ('QEMU_AAC_LATE_SBR_FORMAT_PASS', 'QEMU_AAC_FORMAT_PASS', 'QEMU_SMOKE_PASS',
                   'AAC_LATE_SBR_REGRESSION_PASS ordinary_cases=6 parities=2 transition_pcm_quality=unqualified'):
        one(log, re.escape(marker))
    rows = re.findall(r'AAC_LATE_SBR_PCM_PASS case=(\w+) repeats=(\d+) frames=(\d+) '
                      r'channel_samples=(\d+) max_error_lsb=(\d+) pcm_hash=([0-9a-f]{8})', log)
    if len(rows) != len(CASES) or {r[0] for r in rows} != set(CASES):
        raise ValueError('Incomplete or duplicate ordinary-stream PCM coverage')
    pcm = []
    for name, repeats, frames, samples, error, digest in rows:
        if (int(repeats), int(frames), int(samples), int(error)) != (3, *CASES[name], 0):
            raise ValueError('Wrong PCM sample coverage or changed PCM: ' + name)
        pcm.append(dict(case=name, repeats=3, frames=int(frames), channel_samples=int(samples),
                        max_error_lsb=0, pcm_fnv1a=digest))
    parities = re.findall(r'AAC_LATE_SBR_PARITY_PASS lc_frames=(\d+) he_frames=(\d+) rate=(\d+) channels=(\d+)', log)
    if sorted(tuple(map(int, r)) for r in parities) != [(13, 15, 44100, 2), (26, 15, 44100, 2)]:
        raise ValueError('Missing one of the LC bank phases or wrong transition format')
    lifecycle = one(log, r'AACCOMPACT_ADAPTER_PASS failures=(\d+) tasks=(\d+) resets=(\d+) samples=(\d+) cleanup=complete heap=valid')
    if tuple(map(int, lifecycle)) != (2, 2, 2, 61440):
        raise ValueError('Incomplete allocation, reset or task-isolation coverage')
    concurrent = one(log, r'AACCOMPACT_CONCURRENT_PASS decoders=2 samples=(\d+) pcm_hash=([0-9a-f]{8})')
    if int(concurrent[0]) != 61440:
        raise ValueError('Incomplete concurrent PCM coverage')
    stack = tuple(map(int, one(log, r'AACSMOOTHING_STACK task_stack_bytes=(\d+) min_free_bytes=(\d+) concurrent_peak=(\d+)')))
    if stack[0] != 16384 or stack[1] < 1024 or stack[2] != 2:
        raise ValueError('Unsafe or incomplete decoder stack evidence')
    keys = ('checks', 'core', 'frames', 'ps', 'smoothing', 'allocations', 'frees',
            'negative_cases', 'envelopes', 'resets', 'io', 'copies')
    audit = dict(zip(keys, map(int, one(log, 'AAC_POINTER_PASS ' + ' '.join(k+r'=(\d+)' for k in keys)))))
    if (any(v <= 0 for v in audit.values()) or audit['checks'] < 10000 or
            audit['allocations'] != audit['frees'] or audit['negative_cases'] != 10):
        raise ValueError('Incomplete pointer lifetime evidence')
    boundary_keys = ('applied', 'decode_io', 'ps_bits', 'release_negative_cases', 'boundary_negative_cases')
    boundary = dict(zip(boundary_keys, map(int, one(log, 'AAC_POINTER_BOUNDARY_PASS ' +
                        ' '.join(k+r'=(\d+)' for k in boundary_keys)))))
    if (any(v <= 0 for v in boundary.values()) or boundary['decode_io'] != audit['frames'] or
            boundary['release_negative_cases'] != 6 or boundary['boundary_negative_cases'] != 5):
        raise ValueError('Incomplete buffer-boundary evidence')
    result=dict(experiment='qemu_late_sbr', ordinary_pcm=pcm,
                ordinary_channel_samples=sum(r['channel_samples'] for r in pcm),
                precision_pass=True, precision_limit_lsb=0, summaries=[],
                precision_scope='Ordinary LC/HE/HEv2 streams vs unchanged controller with identical compact storage',
                transition_pcm_qualified=False, reverse_transition_qualified=False,
                production_qualified=False, pointers=audit, pointer_boundaries=boundary,
                stack_bytes=stack[0], stack_min_free_bytes=stack[1], parities=[13, 26])
    retention=re.findall(r'AAC_LATE_SBR_RETAIN_PASS missing_frames=(\d+) resumed_frames=(\d+) rate=(\d+) channels=(\d+)',log)
    if require_retention or retention:
        if [tuple(map(int,r)) for r in retention]!=[(13,15,44100,2)]*2:
            raise ValueError('Incomplete SBR retention or resume coverage')
        output=one(log,r'AAC_LATE_SBR_OUTPUT_PASS frames=(\d+) channel_samples=(\d+) poison_patterns=(\d+)')
        if tuple(map(int,output))!=(56,189440,2):
            raise ValueError('Incomplete output-buffer independence coverage')
        result.update(retention_format_pass=True,retention_parities=2,
                      output_poison_independent=True,output_poison_channel_samples=189440)
    return result


if __name__ == '__main__':
    parser = common.make_parser(__doc__, 'late-sbr')
    args = parser.parse_args()
    if args.input:
        parser.error('This suite uses the six pinned fixtures; external recordings are not covered')
    sys.exit(common.run(args, log_parser=lambda log:parse_log(log,require_retention=True),
                       config_key='YORADIO_QEMU_AAC_LATE_SBR_TEST'))
