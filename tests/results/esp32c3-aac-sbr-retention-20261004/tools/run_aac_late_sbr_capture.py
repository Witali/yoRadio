#!/usr/bin/env python3
"""Capture transition PCM from either compact or full-precision QEMU storage."""
import re
import sys
import run_aac_bfp16 as common
from run_aac_late_sbr import CASES, parse_log
from compare_aac_late_sbr_pcm import parse_capture


def parse_reference(log):
    frames=parse_capture(log)
    rows=re.findall(r'AAC_LATE_SBR_PCM_PASS case=(\w+) repeats=(\d+) frames=(\d+) '
                    r'channel_samples=(\d+) max_error_lsb=(\d+) pcm_hash=([0-9a-f]{8})',log)
    if len(rows)!=len(CASES) or {r[0] for r in rows}!=set(CASES):
        raise ValueError('Incomplete ordinary-stream controller comparison')
    for name,repeats,count,samples,error,_ in rows:
        if tuple(map(int,(repeats,count,samples,error)))!=(3,*CASES[name],0):
            raise ValueError('Ordinary PCM changed: '+name)
    return dict(precision_pass=True,precision_limit_lsb=0,summaries=[],
                precision_scope='Ordinary PCM vs unchanged controller in this image only',
                capture_frames=len(frames),capture_channel_samples=sum(r['bytes']//2 for r in frames),
                transition_storage_precision_qualified=False,production_qualified=False)


if __name__=='__main__':
    parser=common.make_parser(__doc__,'late-capture')
    parser.add_argument('--full-precision',action='store_true',help='Require full-precision native history')
    args=parser.parse_args()
    if args.input:parser.error('The capture uses the pinned transition fixtures')
    config=(args.build/'config/sdkconfig.h').read_text()
    def enabled(name):return '#define CONFIG_'+name+' 1\n' in config
    storage=('YORADIO_AAC_HIGH_HISTORY','YORADIO_AAC_SMOOTHING_HISTORY',
             'YORADIO_AAC_LOW_WORKSPACE','YORADIO_AAC_ASYMMETRIC_OWNER')
    if args.full_precision:
        if any(enabled(k) for k in (*storage,'YORADIO_AAC_PS_PC16',
                                    'YORADIO_QEMU_AAC_BFP16_TEST','YORADIO_QEMU_AAC_PACKED_HISTORY_TEST')):
            parser.error('Reference history contains storage/quantization experiments')
    elif not all(enabled(k) for k in (*storage,'YORADIO_QEMU_AAC_POINTER_AUDIT')):
        parser.error('Candidate must use the audited compact production storage')
    def check(log):
        result=parse_reference(log)
        if not args.full_precision:result.update(parse_log(log,require_retention=True))
        result['full_precision_history']=args.full_precision
        return result
    sys.exit(common.run(args,log_parser=check,config_key='YORADIO_QEMU_AAC_LATE_SBR_CAPTURE'))
