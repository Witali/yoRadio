#!/usr/bin/env python3
"""Validate reordered AAC scratch allocation against the retained reference PCM."""
import sys
from pathlib import Path
import run_aac_bfp16 as common
from run_aac_reserve import parse_log, compare_pcm

if __name__ == '__main__':
    parser=common.make_parser(__doc__, 'scratch')
    parser.add_argument('--reference-wav',type=Path,required=True)
    args=parser.parse_args()
    if args.input:parser.error('This suite uses the retained format sequence')
    def check(log):
        result=parse_log(log)
        result.update(pcm=compare_pcm(args.reference_wav,args.output/'audio.wav'),
                      precision_pass=True,precision_limit_lsb=0,summaries=[])
        return result
    sys.exit(common.run(args,log_parser=check,
                         config_key='YORADIO_AAC_EARLY_SCRATCH_RESERVE'))
