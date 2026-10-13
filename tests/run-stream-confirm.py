"""Sanitized bounded lookahead experiment; no firmware queue integration yet."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def command(args):
    return subprocess.check_output(args,stderr=subprocess.STDOUT)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    main=ROOT/'idf/esp32c3-oled-native/main'
    test=ROOT/'tests/native/stream_confirm_test.c'
    binary=out/'test'
    (out/'build.log').write_bytes(run(['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
        '-fsanitize=address,undefined','-fno-pie','-no-pie','-I',host(main),host(test),'-o',host(binary)]))
    log=run([host(binary)]);(out/'unit.log').write_bytes(log);print(log.decode(),end='')
    corpus=[]
    for folder in ('esp32c3_calibration','aac_stream_format'):
        base=ROOT/'tests/fixtures'/folder;manifest=json.loads((base/'manifest.json').read_text())
        files=manifest.get('files') or {x['file']:x for x in manifest['fixtures'] if x['codec'] in ('aac','mp3')}
        for name,spec in files.items():
            data=(base/name).read_bytes();assert hashlib.sha256(data).hexdigest()==spec['sha256']
            corpus.append((name,data,None))
    for rate in (8000,11025,12000,16000,22050,24000,32000,44100,48000):
        for channels in (1,2):
            path=out/f'mp3-{rate}-{channels}.mp3'
            cmd=['ffmpeg','-v','error','-y','-f','lavfi','-i',f'sine=frequency=997:sample_rate={rate}:duration=0.35',
                 '-ac',str(channels),'-c:a','libmp3lame',
                 *(['-b:a','24k' if rate<32000 else '128k'] if channels==1 else ['-q:a','3']),
                 '-write_xing','0','-id3v2_version','0','-write_id3v1','0',str(path)]
            command(cmd);corpus.append((path.name,path.read_bytes(),cmd))
    records=[];clean={}
    for name,data,cmd in corpus:
        while data.startswith(b'ID3'):
            skip=10+(data[6]<<21)+(data[7]<<14)+(data[8]<<7)+data[9]
            if data[3]==4 and data[5]&16:skip+=10
            data=data[skip:]
        clean[name]=data
        path=out/(name+'.elementary');path.write_bytes(data)
        oracle=json.loads(command(['ffprobe','-v','error','-show_packets','-show_entries','packet=size',
                                   '-of','json',str(path)]))
        records.append((name,data,1 if name.endswith('.mp3') else 2,0,int(oracle['packets'][0]['size']),cmd))
    aac=clean['he-48000-stereo.aac'];mp3=clean['mp3-320.mp3']
    aac_frame=((aac[3]&3)<<11)|(aac[4]<<3)|(aac[5]>>5)
    mp3_frame=next(x[4] for x in records if x[0]=='mp3-320.mp3')
    records.extend([
        ('false-mp3-before-he-aac',b'\xff\xfb\x90\0'+bytes(28)+aac,2,32,aac_frame,None),
        ('false-aac-before-mp3',b'\xff\xf1\x4c\x80\x01\x9f\xfc'+bytes(25)+mp3,1,32,mp3_frame,None),
        ('single-he-aac',aac[:aac_frame],2,0,aac_frame,None),
        ('single-mp3',mp3[:mp3_frame],1,0,mp3_frame,None),
        ('mp3-to-he-aac',mp3[:mp3_frame]+aac,1,0,mp3_frame,None),
    ])
    report=dict(scope=__doc__,cases=[],ffprobe=command(['ffprobe','-version']).decode().splitlines()[0])
    pattern=re.compile(r'READY chunk=(\d+) codec=(\d+) discard=(\d+) retained=(\d+) frame=(\d+) single=(\d+)')
    for name,data,codec,offset,frame,cmd in records:
        path=out/(name+'.input');path.write_bytes(data)
        log=run([host(binary),host(path)]);(out/(name+'.log')).write_bytes(log)
        rows=[tuple(map(int,m)) for m in pattern.findall(log.decode())]
        assert [x[0] for x in rows]==[1,7,2048],name
        for chunk,actual,start,retained,first,single in rows:
            assert (actual,start,first)==(codec,offset,frame),(name,rows)
            # A rejected earlier candidate can have requested a longer window
            # than the valid frame eventually found inside it.
            assert retained<=8191+10
            if not offset: assert retained<=frame+10
            assert bool(single)==name.startswith('single-')
        report['cases'].append(dict(name=name,sha256=hashlib.sha256(data).hexdigest(),
            codec=codec,discard=offset,frame_bytes=frame,chunk_results=rows,generation_command=cmd,passed=True))
        print(name,'PASS',rows,flush=True)
    sources=[test,Path(__file__).resolve(),*[main/x for x in ('stream_confirm.h','stream_frames.h','stream_probe.h','stream_tags.h')]]
    report['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    report['passed']=True
    for p in sources:
        dst=out/'sources'/p.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
