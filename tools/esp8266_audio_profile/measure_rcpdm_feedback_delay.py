"""Separate fixed-delay analysis; never fit a delay or gain to a recording."""
import argparse
import json
from pathlib import Path
import numpy as np
import measure_pdm_matrix as model

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--capture',type=Path,default=model.ROOT/'radio_output/rcpdm-feedback-final-20260906')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=json.loads((args.capture/'results.json').read_text(encoding='utf-8'))
    bits=32;n=48000*128;frequency=np.arange(20,20001)
    window=.5-.5*np.cos(2*np.pi*np.arange(n)/n)
    aperture=np.sinc(frequency/model.GRID_RATE)*np.exp(-1j*np.pi*frequency/model.GRID_RATE)
    h=model.original.filters(frequency)['rc10us']
    # A ramp implemented as a length-N moving average has this EXACT linear
    # phase. The small amplitude droop is deliberately not equalized away.
    delay=(bits-1)/(2*48000*bits)
    delayed=np.exp(-2j*np.pi*frequency*delay)
    result=dict(bits=bits,bit_rate=1536000,fixed_delay_seconds=delay,
                rule='Fixed (N-1)/(2*f_bit) interpolation delay; no fitted delay or gain; RC10us',
                source_sha256=model.original.sha(Path(__file__)),cases=[])
    for row in report['cases']:
        if row['type']!='radio':continue
        file=model.ROOT/row['pcm'];assert model.original.sha(file)==row['pcm_sha256']
        pcm=np.fromfile(file,dtype='<i2')
        file=args.capture/f"{row['id']}.feedback32.bin"
        assert model.original.sha(file)==row['bitstream_sha256']['feedback32']
        words=np.fromfile(file,dtype='<u4')
        signal=raw=aligned=0.
        for start in range(12000,len(pcm)-12000-48000+1,48000):
            x=np.fft.rfft(np.repeat(pcm[start:start+48000].astype(np.float64)/32768,128)*window)[20:20001]*aperture
            y=np.fft.rfft(model.bits_to_grid(words[start:start+48000],32)*window)[20:20001]*aperture*h
            signal+=float((abs(x)**2).sum());raw+=float((abs(y-x)**2).sum());aligned+=float((abs(y-x*delayed)**2).sum())
        values=dict(id=row['id'],raw_db=model.original.db_ratio(signal,raw),
                    fixed_delay_compensated_db=model.original.db_ratio(signal,aligned))
        assert abs(values['raw_db']-row['quality']['models']['feedback32']['rc10us']['snr_to_input_db'])<1e-8
        result['cases'].append(values);print(values,flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
