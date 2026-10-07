#!/usr/bin/env python3
"""Compare actual compact SBR pointer tables against the unmodified RV32 decoder."""
import sys
import run_aac_bfp16 as common
import run_aac_sbr_layout as layout


def parse_log(log):
    if 'SBRLAYOUT_INITIALIZERS_PASS channel_rows=5 modes=2 PS=checked' not in log:
        raise ValueError('Missing complete initializer comparison')
    if 'compact_smoothing_tables=5 channel=24848 owner=53240' not in log:
        raise ValueError('Missing compact-table ABI marker')
    if any(marker in log for marker in ('panic\'ed', 'assert failed', 'Guru Meditation')):
        raise ValueError('Decoder fault in evidence')
    # The 32 guard bytes can move this payload across the allocator's bin
    # boundary. Retain that measured zero rather than call it a heap saving.
    result = layout.parse_log(log, candidate_size=53240, require_block_saving=False)
    probes = layout.records(log, 'ALLOCATOR')
    if len(probes)!=1 or probes[0]['reference_request']!=55128 or probes[0]['candidate_request']!=53240:
        raise ValueError('Missing unguarded allocator probe')
    probe=probes[0]
    if (probe.get('guard_bytes')!=0 or probe['reference_block']<55128 or
            not 53240<=probe['candidate_block']<probe['reference_block']):
        raise ValueError('Unguarded block saving not measured')
    for m in result['memory']:
        if m['variant']==1 and m['calls']:
            if m['physical_candidate']>m['physical_reference'] or m.get('smoothing_modes') not in (1,2,3):
                raise ValueError('Invalid compact allocation/mode evidence')
    result['unguarded_allocator_probe'] = probes[0]
    tests = layout.records(log, 'FIR_PASS')
    if tests != [dict(cases=24, slots=32, frames=3, max_index=4, qmf_equal=1)]:
        raise ValueError('Missing smoothing-mode/band/tone FIR coverage')
    result['experiment'] = 'lossless_five_entry_sbr_smoothing_tables'
    return result


if __name__ == '__main__':
    args = common.make_parser(__doc__, 'smoothing').parse_args()
    sys.exit(common.run(args, log_parser=parse_log,
                       config_key='YORADIO_QEMU_AAC_SMOOTHING_TEST', axis='variant'))
