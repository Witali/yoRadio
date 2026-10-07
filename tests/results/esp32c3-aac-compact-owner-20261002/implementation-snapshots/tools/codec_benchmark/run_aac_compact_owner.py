#!/usr/bin/env python3
"""Check the combined lossless SBR owner, guarded lifecycle and repaired reset."""
import sys
import run_aac_bfp16 as common
import run_aac_sbr_layout as layout
import run_aac_reset as reset


def parse_log(log):
    if 'SBRLAYOUT_INITIALIZERS_PASS channel_rows=5 modes=2 PS=checked' not in log:
        raise ValueError('Missing compact table initializer comparison')
    if 'compact_smoothing_tables=5 channel=24848 owner=49708' not in log:
        raise ValueError('Missing combined owner ABI marker')
    result=layout.parse_log(log,candidate_size=49708)
    probe=layout.records(log,'ALLOCATOR')
    if len(probe)!=1 or (probe[0]['reference_request'],probe[0]['candidate_request'])!=(55128,49708):
        raise ValueError('Missing combined allocation probe')
    if not 49708<=probe[0]['candidate_block']<probe[0]['reference_block']:
        raise ValueError('No measured block saving')
    fir=layout.records(log,'FIR_PASS')
    if fir!=[dict(cases=24,slots=32,frames=3,max_index=4,qmf_equal=1)]:
        raise ValueError('Missing enabled/disabled smoothing coverage')
    result['unguarded_allocator_probe']=probe[0]
    result['reset']=reset.parse_log(log)
    result['experiment']='lossless_compact_tables_and_relocated_ps'
    return result


if __name__=='__main__':
    args=common.make_parser(__doc__,'compact-owner').parse_args()
    sys.exit(common.run(args,log_parser=parse_log,
                       config_key='YORADIO_QEMU_AAC_COMPACT_OWNER_TEST',axis='variant'))
