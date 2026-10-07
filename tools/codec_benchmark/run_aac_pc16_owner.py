#!/usr/bin/env python3
"""Check the production PC16 hooks and PS relocation in QEMU, without a board."""
from array import array
import hashlib
from pathlib import Path
import sys
import wave
import run_aac_bfp16 as common
import aac_precision
from run_aac_reserve import parse_log


def compare_pcm(reference, candidate):
    maximum=different=over_two=over_five=0
    digest=hashlib.sha256()
    nonzero=False
    with wave.open(str(reference)) as a,wave.open(str(candidate)) as b:
        if a.getparams()!=b.getparams() or not a.getnframes() or a.getsampwidth()!=2:
            raise ValueError('PCM shape/duration changed, empty output or unsupported width')
        while True:
            left,right=a.readframes(4096),b.readframes(4096)
            if not left:break
            x,y=array('h',left),array('h',right)
            if sys.byteorder!='little':x.byteswap();y.byteswap()
            nonzero |= any(x)
            digest.update(right)
            for r,c in zip(x,y):
                error=abs(r-c)
                maximum=max(maximum,error)
                different+=error!=0;over_two+=error>2;over_five+=error>5
        if not nonzero:raise ValueError('Silent output is not quality evidence')
        return dict(frames=a.getnframes(),channels=a.getnchannels(),rate=a.getframerate(),
                    sample_width=2,max_pcm_error_lsb=maximum,different_samples=different,
                    over_two=over_two,over_five=over_five,pcm_sha256=digest.hexdigest(),
                    reference_wav_sha256=common.sha256(reference),
                    note='Post-conversion output; paired raw decoder PCM is tested separately.')


if __name__=='__main__':
    parser=common.make_parser(__doc__,'ps-pc16-owner')
    parser.add_argument('--reference-wav',type=Path,required=True)
    args=parser.parse_args()
    if args.input:parser.error('This suite uses the retained format sequence')
    def check(log):
        result=parse_log(log)
        pcm=compare_pcm(args.reference_wav,args.output/'audio.wav')
        result.update(pcm=pcm,precision_pass=not pcm['over_five'],precision_limit_lsb=5,
                      production_precision_pass=pcm['max_pcm_error_lsb'] <= aac_precision.PRODUCTION_LIMIT,
                      production_precision_limit_lsb=aac_precision.PRODUCTION_LIMIT,
                      summaries=[])
        return result
    sys.exit(common.run(args,log_parser=check,config_key='YORADIO_AAC_PS_PC16'))
