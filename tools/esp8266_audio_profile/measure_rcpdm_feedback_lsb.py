"""Coherent +/-1 PCM LSB and DC tests, including zero-input/noise controls.

Checks recovered signal, not merely a PRNG changing output bits. Three seeds,
exact zero-mean periodic input, eight-second coherent windows at 1.536 MHz.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import numpy as np
import measure_pdm_matrix as model

ROOT=model.ROOT

def summarize(values):
    return dict(real=float(values.real),imag=float(values.imag))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'radio_output/rcpdm-feedback-lsb')
    parser.add_argument('--archive',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    executable=Path(subprocess.check_output(['node',str(ROOT/'tools/esp8266_audio_profile/build_rcpdm8_quality.js'),
                    str(args.output/'build'),'rcpdm_feedback_quality'],text=True).strip())
    half=np.round(np.sin(2*np.pi*(np.arange(24)+.5)/48)).astype('<i2');period=np.r_[half,-half]
    assert period.sum()==0 and max(period)==1 and min(period)==-1
    nframes=480000
    signals={ 'zero':np.zeros(nframes,dtype='<i2'), 'dc-plus':np.ones(nframes,dtype='<i2'),
              'dc-minus':-np.ones(nframes,dtype='<i2'), 'tone-plus':np.tile(period,10000),
              'tone-minus':-np.tile(period,10000)}
    files={}
    for name,pcm in signals.items():
        files[name]=args.output/f'{name}.s16le';pcm.tofile(files[name])
    # Exact coherent 1-kHz coefficient; same bit/PCM aperture and physical RC.
    phase=np.exp(-2j*np.pi*np.arange(1536)/1536)
    aperture=np.sinc(1000/1536000)*np.exp(-1j*np.pi*1000/1536000)
    transfer=aperture/(1+2j*np.pi*1000*1e-5)
    reference=2*np.dot(np.repeat(period.astype(np.float64)/32768,32),phase)/1536*aperture
    result=dict(measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                algorithm_sha256=model.original.sha(ROOT/'esp8266/rtos-sdk-native/main/rc_pdm_feedback.h'),
                source_sha256=model.original.sha(Path(__file__)),pcm_rate=48000,bit_rate=1536000,
                bits=32,shift=4,feedback_shift=0,dither=2,interpolate=True,window_seconds=8,
                reference=summarize(reference),seeds=[],pcm_sha256={k:model.original.sha(v) for k,v in files.items()})
    coherent={name:[] for name in signals};means={name:[] for name in signals}
    for seed in [1,8266,2654435769]:
        rows={}
        for name,file in files.items():
            out=args.output/f'{name}-{seed}.bin'
            subprocess.run([str(executable),str(file),str(out),'32','4','0','2','1',str(seed)],check=True,stdout=subprocess.DEVNULL)
            words=np.fromfile(out,dtype='<u4')[12000:396000] # 250ms startup, eight seconds
            bits=((words[:,None]>>np.arange(31,-1,-1,dtype=np.uint32))&1).astype(np.uint8).reshape(-1)
            average=bits.reshape(-1,1536).mean(axis=0)*2-1
            coefficient=2*np.dot(average,phase)/1536*transfer
            mean=float((bits.mean()*2-1)*32768)
            coherent[name].append(coefficient);means[name].append(mean)
            rows[name]=dict(coherent=summarize(coefficient),mean_pcm_lsb=mean,bitstream_sha256=model.original.sha(out))
        gain=(coherent['tone-plus'][-1]-coherent['tone-minus'][-1])/(2*reference)
        rows['differential_gain']=summarize(gain)
        result['seeds'].append(dict(seed=seed,measurements=rows))
        print('LSB seed',seed,'gain',gain,'zero noise relative tone',abs(coherent['zero'][-1]/reference),flush=True)
    average={name:complex(np.mean(values)) for name,values in coherent.items()}
    gain=(average['tone-plus']-average['tone-minus'])/(2*reference)
    zero_noise=abs(average['zero']/reference)
    dc_plus=float(np.mean(means['dc-plus'])-np.mean(means['zero']))
    dc_minus=float(np.mean(means['dc-minus'])-np.mean(means['zero']))
    checks=dict(gain_magnitude=float(abs(gain)),gain_phase_degrees=float(np.angle(gain,deg=True)),
                zero_coherent_noise_relative_tone=float(zero_noise),dc_plus_lsb=dc_plus,dc_minus_lsb=dc_minus)
    checks['pass']=bool(.9<abs(gain)<1.1 and abs(np.angle(gain,deg=True))<10 and zero_noise<.1 and
                        abs(dc_plus-1)<.1 and abs(dc_minus+1)<.1)
    result['checks']=checks
    text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    (args.output/'results.json').write_text(text,encoding='utf-8')
    print('LSB checks',checks,flush=True)
    if not checks['pass']:raise ValueError('LSB transfer regression')
    if args.archive:
        args.archive.mkdir(parents=True,exist_ok=True);(args.archive/'lsb.json').write_text(text,encoding='utf-8')

if __name__=='__main__':main()
