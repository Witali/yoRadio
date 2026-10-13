"""Generate full-precision 24-bit FLAC stress streams with FFmpeg for any board."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import subprocess


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--seconds',type=int,default=64)
    parser.add_argument('--block-size',type=int,choices=(1024,4096,4608,8192),default=4608)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    rng=random.Random(9639);rate=48000;raw=bytearray();pcm=bytearray()
    for i in range(rate*args.seconds):
        noise=rng.randrange(-(1<<20),1<<20)
        for frequency,sign in ((997,1),(1601,-1)):
            value=int((1<<21)*math.sin(2*math.pi*frequency*i/rate))+noise*sign
            raw.extend(struct.pack('<i',value*256))
            pcm.extend(struct.pack('<h',value>>8))
    source=args.output/'source-s32le.pcm';source.write_bytes(raw)
    digest=lambda data:hashlib.sha256(data).hexdigest()
    manifest=dict(generator=subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],
        source_sha256=digest(raw),source_bits=24,seed=9639,fixtures=[])
    for mode in ('indep','left_side','right_side','mid_side'):
        name='flac-24bit-48000-'+mode+(f'-block{args.block_size}' if args.block_size!=4608 else '')
        path=args.output/(name+'.flac')
        options=['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24',
                 '-compression_level','8','-ch_mode',mode,'-frame_size',str(args.block_size)]
        subprocess.run(['ffmpeg','-n','-v','error','-f','s32le','-ar',str(rate),'-ac','2',
            '-i',str(source),*options,str(path)],check=True)
        data=path.read_bytes()
        bits=(((data[20]&1)<<4)|(data[21]>>4))+1
        assert bits==24
        assert int.from_bytes(data[10:12],'big')==args.block_size
        manifest['fixtures'].append(dict(name=name,file=path.name,codec='flac',mime='audio/flac',
            rate=rate,channels=2,bits=bits,seconds=args.seconds,profile='flac',
            sha256=digest(data),bytes=len(data),mode=mode,encoder_options=options,
            pcm_bytes=len(pcm),pcm_sha256=digest(pcm)))
        print(name,flush=True)
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()
