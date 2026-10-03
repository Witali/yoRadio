#!/usr/bin/env python3
"""Qualify actual low-QMF owner reduction against the previous full workspace."""
import json
from pathlib import Path
import re
import sys
import run_aac_bfp16 as common
import run_aac_high_adapter as high
import run_aac_pointer_audit as pointers

def parse_log(log,*,owner_bytes=35900,block_bytes=36864,previous_owner_bytes=45932,previous_block_bytes=47104):
    result=pointers.parse_log(log,require_boundaries=True,owner_bytes=owner_bytes,
                              stack_bytes=16384,block_bytes=block_bytes-12)
    keys=('owner_bytes','work_bytes','stored_bytes','calls')
    rows=re.findall('AAC_LOW_WORKSPACE_PASS '+' '.join(k+r'=(\d+)' for k in keys),log)
    if len(rows)!=1:raise ValueError('Missing or duplicate low-QMF workspace report')
    values=dict(zip(keys,map(int,rows[0])))
    if (values['owner_bytes'],values['work_bytes'],values['stored_bytes'])!=(owner_bytes,10240,4096):
        raise ValueError('Unexpected low-QMF storage dimensions')
    if values['calls']*2!=result['pointers']['frames']:
        raise ValueError('Not every SBR call used the scoped workspace')
    bindings=re.findall(r'AAC_LOW_POINTER_PASS bindings=(\d+) negative_cases=(\d+)',log)
    if len(bindings)!=1 or tuple(map(int,bindings[0]))!=(values['calls'],6):
        raise ValueError('Missing exact low-QMF address/lifetime qualification')
    return dict(result,experiment='aac_low_qmf_scoped_workspace',low_workspace=values,
                low_pointer_bindings=int(bindings[0][0]),low_pointer_negative_cases=6,
                measured_owner_block_saving_bytes=previous_block_bytes-block_bytes,
                requested_owner_saving_bytes=previous_owner_bytes-owner_bytes,production_qualified=False)

if __name__=='__main__':
    parser=common.make_parser(__doc__,'low-workspace')
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--previous-wav',type=Path,required=True)
    parser.add_argument('--production-path',action='store_true',
                        help='Test the physical-build storage path without transient-row poisoning')
    args=parser.parse_args()
    config=(args.build/'sdkconfig').read_text(encoding='utf-8')
    if args.production_path and 'CONFIG_YORADIO_QEMU_AAC_LOW_WORKSPACE=y' in config:
        parser.error('The production storage path must have QEMU low-workspace poisoning disabled')
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
        if args.production_path:
            result.update(production_storage_path=True,transient_row_poisoning=False)
        return result
    key='YORADIO_AAC_LOW_WORKSPACE' if args.production_path else 'YORADIO_QEMU_AAC_LOW_WORKSPACE'
    sys.exit(common.run(args,log_parser=check,config_key=key))
