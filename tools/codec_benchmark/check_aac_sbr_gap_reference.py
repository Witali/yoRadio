#!/usr/bin/env python3
"""Check missing/resumed SBR in the previously pinned pristine FAAD builds."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from run_faad_history_comparison import host_command,host_path

ROOT=Path(__file__).resolve().parents[2]


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    fixtures=ROOT/'tests/fixtures/aac_sbr_gap'
    manifest=json.loads((fixtures/'manifest.json').read_text())
    provenance=json.loads((ROOT/'tests/results/esp32c3-aac-sbr-retention-20261004/faad/provenance.json').read_text())
    results=[]
    for name,meta in manifest['cases'].items():
        original=(fixtures/('source-'+name+'.aac')).read_bytes()
        missing=(fixtures/('missing-'+name+'.aac')).read_bytes()
        for data,key in ((original,'source_sha256'),(missing,'missing_sha256')):
            if hashlib.sha256(data).hexdigest()!=meta[key]:raise ValueError('Changed fixture')
        sequence=original+missing+original;input_path=output/(name+'.aac');input_path.write_bytes(sequence)
        for mode,exe_info in provenance['executables'].items():
            exe=Path(exe_info['path'])
            if hashlib.sha256(exe.read_bytes()).hexdigest()!=exe_info['sha256']:
                raise ValueError('Changed pristine FAAD '+mode)
            prefix=output/(name+'-'+mode)
            result=subprocess.run(host_command([host_path(exe),host_path(input_path),host_path(prefix),'1']),capture_output=True)
            prefix.with_suffix('.log').write_bytes(result.stdout+result.stderr);result.check_returncode()
            frames=[list(map(int,s.split())) for s in prefix.with_suffix('.frames').read_text().splitlines()]
            states=[list(map(int,s.split())) for s in prefix.with_suffix('.state').read_text().splitlines()]
            if len(frames)!=3*meta['frames'] or len(states)!=len(frames):raise ValueError('Missing frames')
            for index,(frame,state) in enumerate(zip(frames,states)):
                size,samples,rate,channels,sbr,ps=frame
                expected_samples=0 if index==0 else 2048*meta['channels']
                if (samples,rate,channels,sbr,ps)!=(expected_samples,meta['rate'],meta['channels'],1,int(meta['aot']==29)):
                    raise ValueError(f'FAAD format/state mismatch: {name}/{mode}/{index}')
                if state[0]!=0 or state[1]<1:raise ValueError('FAAD SBR parsing/reconstruction error')
            pcm=prefix.with_suffix('.pcm').read_bytes()
            prefix.with_suffix('.pcm.gz').write_bytes(gzip.compress(pcm,mtime=0))
            # Keep raw temporary PCM too; evidence collector selects gzip only.
            results.append(dict(case=name,mode=mode,frames=len(frames),rate=meta['rate'],channels=meta['channels'],
                missing_frames=meta['frames'],sbr_all_frames=True,ps_all_frames=meta['aot']==29,
                pcm_sha256=hashlib.sha256(pcm).hexdigest(),sequence_sha256=hashlib.sha256(sequence).hexdigest()))
            print(name,mode,'PASS',len(frames),'frames',flush=True)
    record=dict(provenance=provenance,fixture_manifest_sha256=hashlib.sha256((fixtures/'manifest.json').read_bytes()).hexdigest(),
                cases=results,scope='Reference state/format only; not PCM equality between different decoder algorithms')
    (output/'result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
