"""Measure selected feedback RC-PDM at the SAME five rates as saved controls."""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import numpy as np
import measure_pdm_matrix as model

ROOT=model.ROOT

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'radio_output/rcpdm-feedback-quality')
    parser.add_argument('--archive',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    previous_path=ROOT/'docs/benchmarks/esp8266-pdm-frequency-matrix-2026-09-06/results.json'
    previous=json.loads(previous_path.read_text(encoding='utf-8'))
    executable=Path(subprocess.check_output(['node',str(ROOT/'tools/esp8266_audio_profile/build_rcpdm8_quality.js'),
                    str(args.output/'build'),'rcpdm_feedback_quality'],text=True).strip())
    configs={f'feedback{bits}':dict(bits=bits,shift=shift,alpha=1/(1<<shift),
                bit_rate_hz=48000*bits,feedback_shift=0,dither=2,interpolate=True)
             for bits,shift in zip(model.BITS,range(2,7))}
    sources=['esp8266/rtos-sdk-native/main/rc_pdm_feedback.h',
             'tools/esp8266_audio_profile/rcpdm_feedback_quality.cpp',
             'tools/esp8266_audio_profile/measure_rcpdm_feedback.py',
             'tools/esp8266_audio_profile/measure_pdm_matrix.py',
             'tools/esp8266_audio_profile/measure_rcpdm8_quality.py']
    result=dict(measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                source_sha256={p:model.original.sha(ROOT/p) for p in sources},
                baseline_sha256=model.original.sha(previous_path),configs=configs,
                pcm_rate=48000,common_grid_rate=model.GRID_RATE,physical_rc_us=10,
                seed=2654435769,state_bytes=16,firmware_flashed=False,
                note='Numerical model only. Baselines use identical PCM, carriers, RC filters, grid, windows and band. Causal interpolation adds delay; no gain/delay alignment.',cases=[])
    for old in previous['cases']:
        file=ROOT/old['pcm'];assert model.original.sha(file)==old['pcm_sha256']
        paths={}
        for name,cfg in configs.items():
            paths[name]=args.output/f"{old['id']}.{name}.bin"
            subprocess.run([str(executable),str(file),str(paths[name]),str(cfg['bits']),str(cfg['shift']),
                            '0','2','1',str(result['seed'])],check=True,stdout=subprocess.DEVNULL)
        bridge=ROOT/'radio_output/pdm-frequency-matrix-20260906'/f"{old['id']}.rc32-a16.bin"
        assert model.original.sha(bridge)==old['bitstream_sha256']['rc32-a16']
        paths['baseline_rc32']=bridge
        quality=model.analyze(np.fromfile(file,dtype='<i2'),paths,{**configs,'baseline_rc32':dict(bits=32)},old.get('hz'),
                              lambda n:print(f"{len(result['cases'])+1}/9 {old['id']}: window {n}",flush=True))
        bridge_quality=quality['models'].pop('baseline_rc32')
        for filt,row in bridge_quality.items():
            for key,value in row.items():
                baseline=old['quality']['models']['rc32-a16'][filt][key]
                if value is None or isinstance(value,bool):assert value==baseline
                else:assert abs(value-baseline)<1e-8
        row={key:old[key] for key in ['id','type','pcm','pcm_sha256','hz','level_dbfs'] if key in old}
        row['quality']=quality
        row['bitstream_sha256']={name:model.original.sha(path) for name,path in paths.items() if name!='baseline_rc32'}
        row['baselines']={name:values for name,values in old['quality']['models'].items()
                          if previous['variants'][name]['role']=='comparison'}
        result['cases'].append(row)
        (args.output/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        print('Completed',old['id'],flush=True)
    for file,sha in result['source_sha256'].items():assert model.original.sha(ROOT/file)==sha
    if args.archive:
        args.archive.mkdir(parents=True,exist_ok=True)
        (args.archive/'quality.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')

if __name__=='__main__':main()
