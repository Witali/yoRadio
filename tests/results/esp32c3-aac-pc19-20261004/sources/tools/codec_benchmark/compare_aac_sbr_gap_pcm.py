#!/usr/bin/env python3
"""Compare raw native PCM through parser-verified missing/resumed SBR frames."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import struct
from compare_aac_late_sbr_pcm import read_log,parse_capture

ROOT=Path(__file__).resolve().parents[2]
FIXTURES=ROOT/'tests/fixtures/aac_sbr_gap'


def verified_manifest():
    manifest=json.loads((FIXTURES/'manifest.json').read_text())
    for name,meta in manifest['cases'].items():
        for kind in ('source','missing'):
            if hashlib.sha256((FIXTURES/(kind+'-'+name+'.aac')).read_bytes()).hexdigest()!=meta[kind+'_sha256']:
                raise ValueError('Changed AAC fixture: '+name)
    return manifest


def parse_gaps(log):
    parse_capture(log) # also require prior controller, retention and complete image checks
    manifest=verified_manifest();frames=[];expected=[]
    for name,meta in manifest['cases'].items():
        case=name.replace('-','_')
        channels=2 # The native SDK duplicates HE mono; verified below against its original controller.
        for phase in range(3):
            for frame in range(meta['frames']):expected.append((case,phase,frame,meta['rate'],channels,4096*channels))
        marker=f"AAC_GAP_PASS case={case} frames_per_phase={meta['frames']} phases=3 reset_vs_fresh=exact partial_close=9"
        if log.count(marker)!=1:raise ValueError('Missing or duplicate lifecycle result: '+case)
    if log.count('AAC_GAP_MONO_CONTROL_PASS source_channels=1 pcm_channels=2 rate=32000 duplicated_pairs=exact controller_pcm=exact')!=1:
        raise ValueError('Missing unmodified-controller mono upmix evidence')
    samples=sum(row[-1]//2 for row in expected)
    if log.count(f'AAC_GAP_SUITE_PASS cases=4 capture_channel_samples={samples} heap=valid')!=1:
        raise ValueError('Missing or duplicate gap completion')
    for line in log.splitlines():
        if line.startswith('AAC_GAP_PCM_FRAME '):
            m=re.fullmatch(r'AAC_GAP_PCM_FRAME case=(\w+) phase=(\d+) frame=(\d+) rate=(\d+) channels=(\d+) bytes=(\d+)',line)
            if not m:raise ValueError('Malformed gap frame')
            row=(m[1],*map(int,m.groups()[1:]))
            if len(frames)>=len(expected) or row!=expected[len(frames)]:raise ValueError('Missing/duplicate/reordered gap frame or wrong format')
            if frames and len(frames[-1]['pcm'])!=frames[-1]['bytes']:raise ValueError('Incomplete gap frame')
            frames.append(dict(zip(('case','phase','frame','rate','channels','bytes'),row),pcm=bytearray()))
        elif line.startswith('AAC_GAP_PCM_DATA '):
            m=re.fullmatch(r'AAC_GAP_PCM_DATA offset=(\d+) hex=([0-9a-f]+)',line)
            if not m or not frames:raise ValueError('Malformed gap chunk')
            offset=int(m[1]);data=bytes.fromhex(m[2]);row=frames[-1]
            if offset!=len(row['pcm']) or len(data)!=256 or offset+len(data)>row['bytes']:
                raise ValueError('Missing/duplicate/reordered/oversize gap chunk')
            row['pcm']+=data
    if len(frames)!=len(expected) or any(len(r['pcm'])!=r['bytes'] for r in frames):raise ValueError('Incomplete gap capture')
    return frames


def compare(reference,candidate):
    left=parse_gaps(reference);right=parse_gaps(candidate);hist=Counter();cases={};rows=[]
    a_pcm=bytearray();b_pcm=bytearray()
    for a,b in zip(left,right):
        counts=Counter(abs(x[0]-y[0]) for x,y in zip(struct.iter_unpack('<h',a['pcm']),struct.iter_unpack('<h',b['pcm'])))
        hist.update(counts);cases.setdefault((a['case'],a['phase']),Counter()).update(counts)
        rows.append(dict(case=a['case'],phase=a['phase'],frame=a['frame'],max_error_lsb=max(counts),
                         different=sum(counts.values())-counts[0],samples=sum(counts.values())))
        a_pcm+=a['pcm'];b_pcm+=b['pcm']
    if not any(a_pcm):raise ValueError('Silent reference')
    def summary(counts):
        samples=sum(counts.values())
        return dict(channel_samples=samples,different=samples-counts[0],max_error_lsb=max(counts),
            over_three=sum(n for e,n in counts.items() if e>3),rms_error_lsb=math.sqrt(sum(e*e*n for e,n in counts.items())/samples),
            histogram={str(e):n for e,n in sorted(counts.items())})
    result=dict(**summary(hist),precision_limit_lsb=3,precision_pass=max(hist)<=3,
        phases=[dict(case=c,phase=p,**summary(h)) for (c,p),h in cases.items()],frames=rows,
        reference_pcm_sha256=hashlib.sha256(a_pcm).hexdigest(),candidate_pcm_sha256=hashlib.sha256(b_pcm).hexdigest(),
        scope='Compact vs full-precision native history; no alignment, resampling, gain matching or skipped startup',
        production_qualified=False)
    return result,bytes(a_pcm),bytes(b_pcm)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-log',type=Path,required=True);parser.add_argument('--candidate-log',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result,left,right=compare(read_log(args.reference_log),read_log(args.candidate_log))
    args.output.mkdir(parents=True,exist_ok=True)
    for name,pcm in (('reference',left),('candidate',right)):
        (args.output/(name+'.pcm.gz')).write_bytes(gzip.compress(pcm,mtime=0))
    result['log_sha256']={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in
                         (('reference',args.reference_log),('candidate',args.candidate_log))}
    (args.output/'comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('frames','phases','histogram')},indent=2))
    raise SystemExit(0 if result['precision_pass'] else 2)
