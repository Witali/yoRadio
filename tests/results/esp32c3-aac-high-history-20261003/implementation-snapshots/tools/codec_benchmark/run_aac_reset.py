#!/usr/bin/env python3
"""Safely reproduce vendor reset overflow and compare repaired subsequent PCM."""
import sys
import re
import run_aac_bfp16 as common


def records(log, kind):
    return [{k:int(v) if v.isdecimal() else v for k,v in
             re.findall(r'(\w+)=([\w.-]+)',line.split(f'AACRESET_{kind} ',1)[1])}
            for line in log.splitlines() if f'AACRESET_{kind} ' in line]


def parse_log(log):
    for marker in ('AACRESET_COMPLETE','QEMU_AAC_FORMAT_PASS','QEMU_SMOKE_PASS'):
        if marker not in log: raise ValueError('Missing marker: '+marker)
    rows=records(log,'PASS')
    expected={'lc44':147456,'lc22':39936,'lc48':159744,'he44':172032,'he48':184320,'hev2':184320}
    if len(rows)!=6 or {r['case'] for r in rows}!=set(expected):
        raise ValueError('Missing or duplicate reset fixture')
    for r in rows:
        if (r['cycles'],r['resets'],r['samples'],r['PCM'],r['guards'],r['cleanup']) != (3,2,expected[r['case']],'exact','pass','complete'):
            raise ValueError('Incomplete reset or PCM/guard/cleanup failure')
    end=records(log,'COMPLETE')
    if end!=[dict(baseline_oob_writes=6,paired_reset_calls=24,core_bytes=35460,old_offset=87004)]:
        raise ValueError('Vendor overflow was not reproduced safely')
    return dict(experiment='guarded_aac_reset',precision_limit_lsb=0,precision_pass=True,
                summaries=[],cases=rows,complete=end[0])


if __name__=='__main__':
    args=common.make_parser(__doc__,'reset').parse_args()
    sys.exit(common.run(args,log_parser=parse_log,config_key='YORADIO_QEMU_AAC_RESET_TEST'))
