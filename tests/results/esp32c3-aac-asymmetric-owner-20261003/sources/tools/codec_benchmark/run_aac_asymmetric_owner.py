#!/usr/bin/env python3
"""Qualify unequal SBR channel extents against the audited symmetric owner."""
import json,re,sys
from pathlib import Path
import run_aac_bfp16 as common
import run_aac_high_adapter as high
import run_aac_low_workspace as low

def parse_log(log):
    result=low.parse_log(log,owner_bytes=32744,block_bytes=32768,
                         previous_owner_bytes=35900,previous_block_bytes=36864)
    rows=re.findall(r'AAC_ASYMMETRIC_OWNER_PASS owner_bytes=(\d+) left_bytes=(\d+) right_bytes=(\d+) frame_offset=(\d+)',log)
    if len(rows)!=1 or tuple(map(int,rows[0]))!=(32744,14776,17956,96):
        raise ValueError('Missing or wrong asymmetric owner layout')
    return dict(result,experiment='aac_asymmetric_owner',
                channel_extents={'left':14776,'right':17956},frame_offset=96)

if __name__=='__main__':
    parser=common.make_parser(__doc__,'asymmetric-owner')
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--previous-wav',type=Path,required=True)
    args=parser.parse_args()
    baseline=json.loads(args.baseline.read_text(encoding='utf-8'))
    def check(log):
        result=parse_log(log)
        if bool(args.input)!=('capture' in result):raise ValueError('Requested capture was not tested')
        pcm=high.compare_pcm(args.previous_wav,args.output/'audio.wav')
        capture_equal=None
        if args.input:
            if common.sha256(args.input)!=baseline['provenance']['recording']['sha256']:
                raise ValueError('Baseline capture is a different recording')
            capture_equal=all(result['capture'][k]==baseline['capture'][k]
                              for k in ('bytes','rate','channels','samples','frames','pcm_hash'))
        result.update(pcm_vs_previous=pcm,capture_identical=capture_equal,
                      precision_pass=pcm['different']==0 and capture_equal is not False,
                      precision_limit_lsb=0,summaries=[],baseline_sha256=common.sha256(args.baseline),
                      baseline_capture=baseline.get('capture'))
        return result
    sys.exit(common.run(args,log_parser=check,config_key='YORADIO_QEMU_AAC_ASYMMETRIC_OWNER'))
