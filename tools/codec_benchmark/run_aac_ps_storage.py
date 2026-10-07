#!/usr/bin/env python3
"""Compare actual PS writes with shared, separate and high-bit metadata storage."""
import sys
import run_aac_bfp16 as common
import run_aac_pc16_write as original

FORMATS={7:'native_source_control',1:'shared16',2:'split16',3:'shared17_five',4:'shared17_four',5:'shared18_four',0:'binary_bypass'}
PAYLOADS={1:2780,2:3088,3:2964,4:3088,5:3088}

def parse_log(log):
    count=original.storage_format_count(log,'PSSTORAGE')
    formats={k:v for k,v in FORMATS.items() if k!=5 or count==5}
    payloads={k:v for k,v in PAYLOADS.items() if k<=count}
    result=original.parse_log(log,variants=formats,payloads=payloads,label='PSSTORAGE')
    result['experiment']='ps_storage_actual_writes'
    # Metadata layout alone must not change either 17-bit representation's PCM.
    for a in (r for r in result['runs'] if r['variant']==3):
        b=next(r for r in result['runs'] if (r['case'],r['variant'],r['run'])==(a['case'],4,a['run']))
        for field in ('samples','frames','max_l','max_r','different','over_one','over_two','over_limit'):
            if a[field]!=b[field]:raise ValueError('PC17 layout changes PCM statistics')
    return result

if __name__=='__main__':
    args=common.make_parser(__doc__,'ps-storage').parse_args()
    sys.exit(common.run(args,log_parser=parse_log,config_key='YORADIO_QEMU_AAC_PS_STORAGE_TEST',axis='variant'))
