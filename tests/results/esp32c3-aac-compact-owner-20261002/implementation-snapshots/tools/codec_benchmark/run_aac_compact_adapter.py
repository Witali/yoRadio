#!/usr/bin/env python3
"""Validate the production compact SBR adapter against retained native PCM."""
import re
import sys
from pathlib import Path
import run_aac_bfp16 as common
import run_aac_reserve as formats


def parse_log(log):
    result = formats.parse_log(log)
    rows = re.findall(r'AACCOMPACT_ADAPTER_PASS failures=(\d+) tasks=(\d+) resets=(\d+) '
                      r'samples=(\d+) cleanup=complete heap=valid', log)
    if len(rows) != 1 or tuple(map(int, rows[0][:3])) != (2, 2, 2) or int(rows[0][3]) <= 0:
        raise ValueError('Missing adapter failure/task/reset validation')
    result['adapter'] = dict(failures=2, tasks=2, resets=2, samples=int(rows[0][3]),
                             cleanup='complete', heap='valid')
    result['experiment'] = 'production_compact_sbr_adapter'
    return result


if __name__ == '__main__':
    parser = common.make_parser(__doc__, 'compact-adapter')
    parser.add_argument('--reference-wav', type=Path, required=True)
    args = parser.parse_args()
    if args.input:
        parser.error('This test uses the retained format/lifecycle sequence')

    def check(log):
        result = parse_log(log)
        result.update(pcm=formats.compare_pcm(args.reference_wav, args.output/'audio.wav'),
                      precision_pass=True, precision_limit_lsb=0, summaries=[])
        return result

    sys.exit(common.run(args, log_parser=check,
                         config_key='YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST'))
