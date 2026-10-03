#!/usr/bin/env python3
"""Test discarded QMF rows with the actual native AAC readers and PCM output."""
import json
from pathlib import Path
import re
import sys
import run_aac_bfp16 as common
import run_aac_high_adapter as high
import run_aac_pointer_audit as pointers


def parse_log(log):
    result=pointers.parse_log(log)
    keys=('first_row','rows','bands','calls','real','complex','ps','poisoned_words')
    rows=re.findall('AAC_LOW_LIFETIME '+' '.join(k+r'=(\d+)' for k in keys),log)
    if len(rows)!=1:
        raise ValueError('Missing or duplicated low-QMF lifetime report')
    stats=dict(zip(keys,map(int,rows[0])))
    if stats['first_row'] not in (7,8) or stats['rows']!=40-stats['first_row'] or stats['bands']!=32:
        raise ValueError('Unexpected poisoned QMF region')
    if min(stats[k] for k in ('calls','real','complex','ps'))<=0:
        raise ValueError('Missing real/complex/PS lifetime coverage')
    if stats['calls']!=stats['real']+stats['complex'] or stats['ps']>stats['complex']:
        raise ValueError('Invalid lifetime call counts')
    if stats['calls']*2!=result['pointers']['frames']:
        raise ValueError('Some audited SBR frames were not poisoned')
    if stats['poisoned_words']!=stats['calls']*2*stats['rows']*stats['bands']:
        raise ValueError('Incomplete transient-row poisoning')
    return dict(result,experiment='aac_low_qmf_lifetime',low_lifetime=stats)


if __name__=='__main__':
    parser=common.make_parser(__doc__,'low-lifetime')
    parser.add_argument('--baseline',type=Path,required=True,help='Matching unpoisoned pointer-audit result JSON')
    parser.add_argument('--previous-wav',type=Path,required=True)
    args=parser.parse_args()
    baseline=json.loads(args.baseline.read_text(encoding='utf-8'))
    def check(log):
        result=parse_log(log)
        if bool(args.input)!=('capture' in result):
            raise ValueError('Requested capture was not tested')
        pcm=high.compare_pcm(args.previous_wav,args.output/'audio.wav')
        capture_equal=None
        if args.input:
            expected=baseline['capture']
            actual=result['capture']
            capture_equal=all(actual[k]==expected[k] for k in ('bytes','rate','channels','samples','frames','pcm_hash'))
            if common.sha256(args.input)!=baseline['provenance']['recording']['sha256']:
                raise ValueError('Baseline capture is a different recording')
        exact=pcm['different']==0 and capture_equal is not False
        result.update(pcm_without_poison=pcm,capture_identical=capture_equal,
                      precision_pass=exact,precision_limit_lsb=0,summaries=[],
                      baseline_sha256=common.sha256(args.baseline),
                      baseline_capture=baseline.get('capture'))
        return result
    sys.exit(common.run(args,log_parser=check,config_key='YORADIO_QEMU_AAC_LOW_LIFETIME'))
