"""Qualify the bounded FIL parser against the native library and AAC regressions."""
from pathlib import Path
import sys

import run_aac_bfp16 as common
from run_aac_faults import parse_log as parse_faults
from run_aac_metadata import parse_log as parse_metadata


def parse_log(log, *, plain=False):
    regression = parse_metadata(log) if plain else parse_faults(log)
    markers = (
        'QEMU_SMOKE_PASS', 'QEMU_OLED_PASS', 'QEMU_AUDIO_PASS',
        'AAC_FIL_NATIVE_OVERRUN sbr_cursor=2164 fill_cursor=2164 frame_bits=16 checked_cursor=16',
        'AAC_FIL_PARSER_PASS valid_cases=69376 count_encodings=271 alignments=8 extension_types=16 slot_states=2',
    )
    for marker in markers:
        if log.count(marker) != 1 or log.count(marker.split()[0]+' ') != 1:
            raise ValueError('Missing/duplicate FIL comparison or native failure reproduction')
    return dict(fill_pass=True, precision_qualified=False, hardware_tested=False, summaries=[],
                valid_comparisons=69376, native_overrun_bits=2148, regression=regression)


if __name__ == '__main__':
    parser=common.make_parser(__doc__,'fill-pc19')
    parser.add_argument('--plain',action='store_true',help='Require a build without compact SBR')
    args=parser.parse_args()
    config=(Path(args.build)/'config/sdkconfig.h').read_text()
    compact='#define CONFIG_YORADIO_AAC_COMPACT_SBR 1\n' in config
    if args.plain==compact:raise ValueError('Plain/compact selection does not match the build')
    sys.exit(common.run(args,log_parser=lambda log:parse_log(log,plain=args.plain),
                       config_key='YORADIO_QEMU_AAC_TEST',pass_key='fill_pass',
                       validation_label='Bounded FIL parsing'))
