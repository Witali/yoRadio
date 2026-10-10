"""Validate the new SDK capture against retained full-precision and PC19 PCM."""
from collections import Counter
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

sys.path.insert(0, 'tools/codec_benchmark')
from compare_aac_late_sbr_pcm import parse_capture
from compare_aac_sbr_gap_pcm import parse_gaps
from run_aac_late_sbr import parse_log
from run_aac_fill import parse_log as parse_fill

parser=argparse.ArgumentParser()
parser.add_argument('--label',default='6.1-compact')
args=parser.parse_args()
out = Path('.build/idf-upgrade')/('qemu-'+args.label)
log = (out/'qemu.log').read_text(errors='replace')
result = {'lifecycle': parse_log(log, require_retention=True),
          'fill': parse_fill(log), 'comparisons': []}
for marker in (
    'AAC_PC19_METADATA_PASS pairs_per_channel=288 channels=2 real_clear=exact full_clear=exact reopen=zero side_bytes=144',
    'AAC_PC19_REOPEN_PASS channels=distinct channel_cursor=preserved sbr_open=zero ps_overlay=preserved',
):
    if log.count(marker) != 1:
        raise ValueError('Missing PC19 metadata lifecycle marker: '+marker)
retained = Path('tests/results/esp32c3-aac-metadata-20261004')
for name, parser in (('late', parse_capture), ('gaps', parse_gaps)):
    frames = parser(log)
    candidate = b''.join(row['pcm'] for row in frames)
    (out/(name+'.pcm.gz')).write_bytes(gzip.compress(candidate, mtime=0))
    for profile in ('reference', 'pc19'):
        path = retained/profile/(name+'.pcm.gz')
        reference = gzip.decompress(path.read_bytes())
        if len(reference) != len(candidate) or not any(reference):
            raise ValueError('Wrong PCM size or silent reference')
        errors = Counter(abs(a[0]-b[0]) for a,b in zip(
            struct.iter_unpack('<h', reference), struct.iter_unpack('<h', candidate)))
        count = sum(errors.values())
        limit = 3 if profile == 'reference' else 0
        row = dict(case=name, reference=str(path), channel_samples=count,
                   reference_sha256=hashlib.sha256(reference).hexdigest(),
                   candidate_sha256=hashlib.sha256(candidate).hexdigest(),
                   limit_lsb=limit, max_error_lsb=max(errors),
                   different=count-errors[0],
                   rms_error_lsb=math.sqrt(sum(e*e*n for e,n in errors.items())/count),
                   histogram=dict(sorted(errors.items())), passed=max(errors)<=limit)
        result['comparisons'].append(row)
result['passed'] = all(row['passed'] for row in result['comparisons'])
result['scope'] = 'Pinned synthetic transition and absent/resumed-SBR corpus; no all-input guarantee or physical PCM capture.'
(out/'pcm-comparison.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({'passed': result['passed'], 'comparisons': result['comparisons']}, indent=2))
sys.exit(0 if result['passed'] else 1)
