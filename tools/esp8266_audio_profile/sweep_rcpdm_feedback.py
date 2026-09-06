"""Reproducible desktop design sweep, not hardware performance measurement."""
import argparse
import json
from pathlib import Path
import subprocess
import numpy as np
import measure_pdm_matrix as model

ROOT=model.ROOT

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'radio_output/rcpdm-feedback-sweep')
    parser.add_argument('--gains',type=int,nargs='+',default=[0,1,2,3,4])
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    build=args.output/'build'
    executable=Path(subprocess.check_output(['node',str(ROOT/'tools/esp8266_audio_profile/build_rcpdm8_quality.js'),
                    str(build),'rcpdm_feedback_quality'],text=True).strip())
    configs={f'g{gain}-d{dither}-i{interp}':dict(bits=32,gain=gain,dither=dither,interp=interp)
             for gain in args.gains for dither in [0,2,3] for interp in [0,1]}
    cases=[]
    for case,hz in [('tone-1000hz-3db',1000),('tone-1000hz-20db',1000),
                    ('tone-1000hz-40db',1000),('tone-7000hz-3db',7000)]:
        cases.append((case,ROOT/'radio_output/rcpdm8-quality'/f'{case}.s16le',hz))
    half=np.round(np.sin(2*np.pi*(np.arange(24)+.5)/48)).astype('<i2')
    period=np.r_[half,-half]
    assert period.sum()==0 and max(period)==1 and min(period)==-1
    pcm=np.tile(period,3000);tiny=args.output/'tone-1000hz-1lsb.s16le';pcm.tofile(tiny)
    cases.append(('tone-1000hz-1lsb',tiny,1000))
    result=dict(configs=configs,cases=[])
    for case,file,hz in cases:
        paths={}
        for name,cfg in configs.items():
            path=args.output/f'{case}.{name}.bin';paths[name]=path
            subprocess.run([str(executable),str(file),str(path),'32','4',str(cfg['gain']),
                            str(cfg['dither']),str(cfg['interp']),'2654435769'],check=True,stdout=subprocess.DEVNULL)
        quality=model.analyze(np.fromfile(file,dtype='<i2'),paths,configs,hz,
                              lambda n:print(f'{case}: window {n}',flush=True))
        result['cases'].append(dict(id=case,pcm_sha256=model.original.sha(file),quality=quality))
        (args.output/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        print(case,{name: {key: None if row[key] is None else round(row[key],2)
                         for key in ['sinad_db','fundamental_gain_db']}
                    for name,values in quality['models'].items() for row in [values['rc10us']]},flush=True)

if __name__=='__main__':main()
