#!/usr/bin/env python3
"""Qualify four-row smoothing in the real adapter, including live stack isolation."""
import re
import sys
from pathlib import Path
import run_aac_bfp16 as common
import run_aac_high_adapter as high

def parse_log(log):
    result=high.parse_log(log,owner_bytes=45932)
    stacks=re.findall(r'AACSMOOTHING_STACK task_stack_bytes=(\d+) min_free_bytes=(\d+) concurrent_peak=(\d+)',log)
    if len(stacks)!=1 or int(stacks[0][0])!=8192 or int(stacks[0][1])<1024 or int(stacks[0][2])!=2:
        raise ValueError('Missing simultaneous temporary-row/stack qualification')
    if result['memory']['block_bytes']!=47104-12:
        raise ValueError('Unexpected poisoned-heap owner block size')
    result.update(experiment='production_four_row_smoothing_adapter',
                  stack=dict(zip(('task_stack_bytes','min_free_bytes','concurrent_peak'),map(int,stacks[0]))))
    return result

if __name__=='__main__':
    p=common.make_parser(__doc__,'smoothing-adapter')
    p.add_argument('--reference-wav',required=True,type=Path)
    p.add_argument('--previous-wav',required=True,type=Path)
    a=p.parse_args()
    if a.input:p.error('This suite uses the retained format/lifecycle sequence')
    def check(log):
        result=parse_log(log)
        native=high.compare_pcm(a.reference_wav,a.output/'audio.wav')
        previous=high.compare_pcm(a.previous_wav,a.output/'audio.wav')
        result.update(pcm=native,pcm_vs_previous_pc18=previous,
                      precision_pass=native['max_pcm_error_lsb']<=3 and previous['max_pcm_error_lsb']==0,
                      precision_limit_lsb=3,summaries=[])
        return result
    sys.exit(common.run(a,log_parser=check,config_key='YORADIO_AAC_SMOOTHING_HISTORY'))
