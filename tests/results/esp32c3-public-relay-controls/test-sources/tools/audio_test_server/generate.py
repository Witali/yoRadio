"""Generate continuous original fixtures for any board; requires ffmpeg/ffprobe.

Use >=43 seconds for CPU/load tests, >=3603 for a one-hour file soak. Existing
FDK fixtures cover HE-AAC; ffmpeg's native encoder here generates AAC-LC only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ENCODERS = {
    'mp3': ('mp3','audio/mpeg',['-c:a','libmp3lame','-b:a','192k','-write_xing','0']),
    'aac': ('aac','audio/aac',['-c:a','aac','-profile:a','aac_low','-b:a','128k','-f','adts']),
    'flac': ('flac','audio/flac',['-c:a','flac','-compression_level','8']),
    'vorbis': ('ogg','audio/ogg',['-c:a','libvorbis','-q:a','6']),
    'opus': ('ogg','audio/ogg',['-c:a','libopus','-b:a','192k','-vbr','off']),
}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--seconds',type=int,default=60)
    parser.add_argument('--rate',type=int,nargs='+',default=[44100,48000])
    parser.add_argument('--channels',type=int,choices=(1,2),nargs='+',default=[1,2])
    parser.add_argument('--codec',choices=tuple(ENCODERS),nargs='+',default=list(ENCODERS))
    parser.add_argument('--ffmpeg',default='ffmpeg')
    parser.add_argument('--ffprobe',default='ffprobe')
    args=parser.parse_args()
    if args.seconds<5 or any(r not in (16000,22050,24000,32000,44100,48000) for r in args.rate):
        parser.error('Use >=5 seconds and a supported fixture rate')
    args.output.mkdir(parents=True,exist_ok=True)
    manifest=args.output/'manifest.json'
    if manifest.exists():
        parser.error('Use a new output directory to preserve existing fixture provenance')
    rows=[]
    version=subprocess.check_output([args.ffmpeg,'-version'],text=True).splitlines()[0]
    for codec in args.codec:
        extension,mime,options=ENCODERS[codec]
        for rate in args.rate:
            for channels in args.channels:
                name=f'{codec}-{rate}-{channels}ch-{args.seconds}s'
                output=args.output/(name+'.'+extension)
                waveform='0.20*sin(2*PI*997*t)'
                if channels==2:
                    waveform+='|0.20*sin(2*PI*1511*t)'
                subprocess.run([args.ffmpeg,'-n','-hide_banner','-loglevel','error','-f','lavfi','-i',
                                f'aevalsrc={waveform}:s={rate}:d={args.seconds}',
                                '-ac',str(channels),*options,str(output)],check=True)
                probe=json.loads(subprocess.check_output([args.ffprobe,'-v','error','-select_streams','a:0',
                    '-show_entries','stream=sample_rate,channels,profile,bits_per_raw_sample:format=duration',
                    '-of','json',str(output)]))
                stream=probe['streams'][0]
                # Opus commonly decodes at 48 kHz even when the input differs.
                actual_rate=int(stream['sample_rate'])
                bits=int(stream.get('bits_per_raw_sample') or 16) if codec=='flac' else 16
                rows.append(dict(name=name,file=output.name,seconds=float(probe['format']['duration']),
                    rate=actual_rate,channels=int(stream['channels']),bits=bits,codec=codec,mime=mime,
                    profile='AAC-LC' if codec=='aac' else codec,
                    sha256=hashlib.sha256(output.read_bytes()).hexdigest()))
                manifest.write_text(json.dumps(dict(generator=version,fixtures=rows),indent=2)+'\n')
                print(name,flush=True)


if __name__ == '__main__':
    main()
