#!/usr/bin/env python3
"""Compare exact signed-16 transition PCM, without resampling or gain matching."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import struct


def read_log(path):
    data=path.read_bytes()
    return (gzip.decompress(data) if path.suffix=='.gz' else data).decode('utf-8')


def parse_capture(log):
    if re.search(r'assert failed|Guru Meditation|CORRUPT HEAP|aac_pointer: field=',log):
        raise ValueError('Decoder, buffer or heap failure')
    for marker in ('QEMU_SMOKE_PASS','QEMU_AAC_FORMAT_PASS','AACCOMPACT_ADAPTER_PASS',
                   'AAC_LATE_SBR_OUTPUT_PASS frames=56 channel_samples=189440 poison_patterns=2'):
        if log.count(marker)!=1:raise ValueError('Missing or duplicate completion: '+marker)
    if len(re.findall(r'AAC_LATE_SBR_RETAIN_PASS missing_frames=13 resumed_frames=15 rate=44100 channels=2',log))!=2:
        raise ValueError('Missing SBR retention in both history-bank phases')
    frames=[]
    for line in log.splitlines():
        if line.startswith('AAC_LATE_PCM_FRAME '):
            match=re.fullmatch(r'AAC_LATE_PCM_FRAME frame=(\d+) rate=(\d+) channels=(\d+) bytes=(\d+)',line)
            if not match:raise ValueError('Malformed PCM frame header')
            frame,rate,channels,size=map(int,match.groups())
            if frame!=len(frames)+1 or frame>56:raise ValueError('Duplicate or skipped PCM frame')
            expected=(22050,1,2048) if frame<=13 else (44100,2,8192)
            if (rate,channels,size)!=expected:raise ValueError('Wrong transition PCM shape')
            if frames and len(frames[-1]['pcm'])!=frames[-1]['bytes']:
                raise ValueError('Incomplete previous PCM frame')
            frames.append(dict(frame=frame,rate=rate,channels=channels,bytes=size,pcm=bytearray()))
        elif line.startswith('AAC_LATE_PCM_DATA '):
            match=re.fullmatch(r'AAC_LATE_PCM_DATA frame=(\d+) offset=(\d+) hex=([0-9a-f]+)',line)
            if not match or not frames:raise ValueError('Malformed PCM data')
            frame,offset=int(match[1]),int(match[2]); data=bytes.fromhex(match[3]); row=frames[-1]
            if (frame!=row['frame'] or offset!=len(row['pcm']) or len(data)!=256 or
                    offset+len(data)>row['bytes']):
                raise ValueError('PCM chunk missing, duplicated, reordered or oversized')
            row['pcm']+=data
    if len(frames)!=56 or any(len(r['pcm'])!=r['bytes'] for r in frames):
        raise ValueError('Incomplete transition capture')
    return frames


def compare(reference,candidate):
    left,right=parse_capture(reference),parse_capture(candidate)
    hist=Counter(); rows=[]; left_pcm=bytearray();right_pcm=bytearray()
    for a,b in zip(left,right):
        assert (a['frame'],a['rate'],a['channels'])==(b['frame'],b['rate'],b['channels'])
        errors=[y[0]-x[0] for x,y in zip(struct.iter_unpack('<h',a['pcm']),struct.iter_unpack('<h',b['pcm']))]
        absolute=Counter(map(abs,errors));hist.update(absolute)
        rows.append(dict(frame=a['frame'],rate=a['rate'],channels=a['channels'],samples=len(errors),
                         max_error_lsb=max(absolute),different=sum(absolute.values())-absolute[0],
                         over_three=sum(n for e,n in absolute.items() if e>3)))
        left_pcm+=a['pcm'];right_pcm+=b['pcm']
    if not any(left_pcm):raise ValueError('Silent reference cannot establish accuracy')
    samples=sum(hist.values())
    result=dict(frames=rows,channel_samples=samples,precision_limit_lsb=3,
                max_error_lsb=max(hist),different=samples-hist[0],
                over_three=sum(n for e,n in hist.items() if e>3),
                rms_error_lsb=math.sqrt(sum(e*e*n for e,n in hist.items())/samples),
                histogram={str(k):v for k,v in sorted(hist.items())},
                reference_pcm_sha256=hashlib.sha256(left_pcm).hexdigest(),
                candidate_pcm_sha256=hashlib.sha256(right_pcm).hexdigest(),
                precision_pass=max(hist)<=3,production_qualified=False,
                scope='Compact vs full-precision native history with the same controller; synthetic transition corpus only')
    return result,bytes(left_pcm),bytes(right_pcm)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-log',type=Path,required=True)
    parser.add_argument('--candidate-log',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result,left,right=compare(read_log(args.reference_log),read_log(args.candidate_log))
    result['log_sha256']={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in
                         [('reference',args.reference_log),('candidate',args.candidate_log)]}
    args.output.mkdir(parents=True,exist_ok=True)
    for name,data in [('reference',left),('candidate',right)]:
        (args.output/(name+'.pcm.gz')).write_bytes(gzip.compress(data,mtime=0))
    (args.output/'comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('frames','histogram')},indent=2))
    raise SystemExit(0 if result['precision_pass'] else 2)
