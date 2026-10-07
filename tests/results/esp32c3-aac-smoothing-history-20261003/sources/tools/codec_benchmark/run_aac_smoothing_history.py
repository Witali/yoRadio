#!/usr/bin/env python3
"""Qualify four retained FIR rows, unchanged native arithmetic and smaller owner."""
import sys
import re
import run_aac_bfp16 as common
import run_aac_high_history as high

def parse_log(log):
    result=high.parse_log(log,smoothing_rows=4)
    marker='SMOOTHING_HISTORY_FIR_PASS '
    fir=[{k:int(v) if v.isdecimal() else v for k,v in re.findall(r'(\w+)=([\w.-]+)',line.split(marker,1)[1])}
         for line in log.splitlines() if marker in line]
    expected=dict(cases=144,frames=7,qmf_values=562464,scratch_bytes=1024,
                  retained_rows=4,taps=5,guards='pass')
    if fir!=[expected]:
        raise ValueError('Missing/incorrect four-row direct FIR qualification')
    result.update(experiment='four_persistent_smoothing_rows',fir=fir,
                  additional_stack_payload_bytes=1024,
                  owner_request_saving_vs_pc18_bytes=47980-45932)
    return result

if __name__=='__main__':
    args=common.make_parser(__doc__,'smoothing-history-c3').parse_args()
    sys.exit(common.run(args,log_parser=parse_log,
        config_key='YORADIO_QEMU_AAC_SMOOTHING_HISTORY_TEST',axis='variant'))
