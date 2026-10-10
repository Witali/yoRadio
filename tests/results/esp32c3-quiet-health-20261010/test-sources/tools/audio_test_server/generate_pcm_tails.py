"""Generate tiny lossless FLAC fixtures for any board's output-boundary tests."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--ffmpeg',default='ffmpeg')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    version=subprocess.check_output([args.ffmpeg,'-version'],text=True).splitlines()[0]
    manifest=dict(generator=version,reference='FFmpeg lossless round trip',
        specification='https://www.rfc-editor.org/rfc/rfc9639.html#section-4.1',fixtures=[])
    for rate in (8000,44100,48000):
        for channels in (1,2):
            for frames in (1,127,511,512,513):
                name=f'tail-flac-{rate}-{channels}ch-{frames}frames'
                values=[((i*97+13)%8192-4096)*(1 if ch==0 else -1)
                        for i in range(frames) for ch in range(channels)]
                pcm=struct.pack('<'+'h'*len(values),*values)
                output=args.output/(name+'.flac')
                command=[args.ffmpeg,'-n','-v','error','-f','s16le','-ar',str(rate),
                    '-ac',str(channels),'-i','pipe:0','-c:a','flac','-compression_level','8',
                    '-fflags','+bitexact','-flags:a','+bitexact',str(output)]
                subprocess.run(command,input=pcm,check=True)
                decoded=subprocess.check_output([args.ffmpeg,'-v','error','-i',str(output),
                    '-f','s16le','-acodec','pcm_s16le','pipe:1'])
                assert decoded==pcm, 'Lossless reference mismatch: '+name
                blob=output.read_bytes()
                assert blob[:4]==b'fLaC' and blob[4]&127==0
                minimum=int.from_bytes(blob[8:10],'big');maximum=int.from_bytes(blob[10:12],'big')
                # STREAMINFO bounds stay >=16 even when the final frame has
                # one sample, as permitted by RFC 9639 sections 4.1/8.2/9.1.6.
                assert 16<=minimum<=maximum<=65535
                packed=int.from_bytes(blob[18:26],'big')
                assert packed>>44==rate and ((packed>>41)&7)+1==channels
                assert ((packed>>36)&31)+1==16 and packed&((1<<36)-1)==frames
                row=dict(name=name,file=output.name,seconds=frames/rate,rate=rate,
                    channels=channels,bits=16,codec='flac',profile='flac',mime='audio/flac',
                    frames=frames,sha256=hashlib.sha256(blob).hexdigest(),
                    pcm_sha256=hashlib.sha256(pcm).hexdigest(),pcm_bytes=len(pcm),
                    streaminfo_min_block=minimum,streaminfo_max_block=maximum,
                    round_trip_exact=True)
                manifest['fixtures'].append(row)
                (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('PASS lossless tail fixtures:',len(manifest['fixtures']))


if __name__=='__main__': main()
