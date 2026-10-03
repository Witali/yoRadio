#!/usr/bin/env python3
"""Check AAC address ownership in QEMU and retain PCM equivalence evidence."""
import re
import sys
from pathlib import Path
import run_aac_bfp16 as common
import run_aac_high_adapter as high
import run_aac_smoothing_adapter as smoothing


def parse_log(log):
    result = smoothing.parse_log(log)
    keys = ('checks', 'core', 'frames', 'ps', 'smoothing', 'allocations', 'frees',
            'negative_cases', 'envelopes', 'resets', 'io', 'copies')
    pattern = 'AAC_POINTER_PASS ' + ' '.join(key+r'=(\d+)' for key in keys)
    rows = re.findall(pattern, log)
    if len(rows) != 1:
        raise ValueError('Missing or duplicated pointer audit completion')
    audit = dict(zip(keys, map(int, rows[0])))
    if any(value <= 0 for value in audit.values()) or audit['checks'] < 10000:
        raise ValueError('Incomplete pointer audit coverage')
    if audit['allocations'] != audit['frees'] or audit['negative_cases'] != 10:
        raise ValueError('Pointer lifetime or negative-test coverage failed')
    if re.search(r'aac_pointer: field=|assert failed|Guru Meditation|CORRUPT HEAP', log):
        raise ValueError('Pointer/heap/panic diagnostic present')
    result.update(experiment='aac_pointer_ownership_audit', pointers=audit)
    captures = re.findall(r'AAC_POINTER_CAPTURE bytes=(\d+) rate=(\d+) channels=(\d+) '
                          r'samples=(\d+) frames=(\d+) pcm_hash=([0-9a-f]{8}) checks=(\d+)', log)
    if len(captures) > 1:
        raise ValueError('Duplicated capture completion')
    if captures:
        values = captures[0]
        if any(int(values[i]) <= 0 for i in (0, 1, 2, 3, 4, 6)):
            raise ValueError('Empty captured stream audit')
        result['capture'] = dict(zip(('bytes', 'rate', 'channels', 'samples', 'frames'), map(int, values[:5])),
                                 pcm_hash=values[5], checks=int(values[6]))
    return result


if __name__ == '__main__':
    parser = common.make_parser(__doc__, 'pointer-audit')
    parser.add_argument('--reference-wav', type=Path, required=True)
    parser.add_argument('--previous-wav', type=Path, required=True)
    args = parser.parse_args()
    def check(log):
        result = parse_log(log)
        if bool(args.input) != ('capture' in result):
            raise ValueError('Requested capture was not audited')
        pcm = high.compare_pcm(args.reference_wav, args.output/'audio.wav')
        previous = high.compare_pcm(args.previous_wav, args.output/'audio.wav')
        result.update(pcm=pcm, pcm_without_audit=previous, summaries=[],
                      precision_pass=pcm['max_pcm_error_lsb'] <= 3 and previous['different'] == 0,
                      precision_limit_lsb=3)
        return result

    sys.exit(common.run(args, log_parser=check, config_key='YORADIO_QEMU_AAC_POINTER_AUDIT'))
