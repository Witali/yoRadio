"""Analytical FIR candidates for integer-clock compensation, not firmware tests.

Sweep all 625 rational phases of 48 kHz -> 625000/13 Hz. Model Blackman-windowed
sinc coefficients, Q19 table storage and linear interpolation between table
phases. Frequency response and worst-case coefficient error are calculated;
runtime, DMA continuity, EOF handling and analog output are not measured.
"""
import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path


def weights(taps, fraction):
    offsets = range(1-taps//2, 1+taps//2)
    values = []
    for k in offsets:
        x = k-fraction
        sinc = math.sin(math.pi*x)/(math.pi*x) if x else 1.0
        window = .42+.5*math.cos(math.pi*x/(taps/2))+.08*math.cos(2*math.pi*x/(taps/2))
        values.append(sinc*window)
    total = sum(values)
    return [v/total for v in values]


def compare(taps, phases):
    scale = 1 << 19
    table = []
    for p in range(phases+1):
        w = weights(taps, p/phases)
        quantized = [round(v*scale) for v in w]
        # Preserve exact DC after quantization. Later interpolation also
        # preserves it if done on the two convolution accumulators.
        peak = max(range(taps),key=lambda i:abs(w[i]))
        quantized[peak] += scale-sum(quantized)
        table.append(quantized)
    tones = (100,1000,10000,18000,20000)
    response = {hz:[] for hz in tones}
    basis = {hz:[cmath.exp(2j*math.pi*hz*k/48000) for k in range(1-taps//2,1+taps//2)] for hz in tones}
    max_bound, max_l1 = 0,0
    for p in range(625):
        fraction=p/625
        quotient,remainder=divmod(p*phases,625)
        w=[(a*(625-remainder)+b*remainder)/(625*scale) for a,b in zip(table[quotient],table[quotient+1])]
        exact=weights(taps,fraction)
        assert abs(sum(w)-1)<1e-12
        max_bound=max(max_bound,32768*sum(abs(a-b) for a,b in zip(w,exact)))
        max_l1=max(max_l1,sum(abs(v) for v in w))
        for hz in tones:
            h=sum(v*b for v,b in zip(w,basis[hz]))*cmath.exp(-2j*math.pi*hz*fraction/48000)
            response[hz].append(h)
    return dict(taps=taps,table_phases=phases,coefficient_bits=19,
        coefficient_flash_bytes=(phases+1)*taps*4,stereo_history_bytes=taps*4,
        worst_coefficient_error_bound_pcm_lsb=max_bound,max_l1=max_l1,
        conceptual_tap_macs_per_second=2*taps*2*625000/13,
        tones=[dict(hz=hz,min_gain_db=min(20*math.log10(abs(h)) for h in values),
                    max_gain_db=max(20*math.log10(abs(h)) for h in values),
                    worst_complex_response_error_db=20*math.log10(max(abs(h-1) for h in values)))
               for hz,values in response.items()])


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert not args.output.exists(), 'Preserve evidence'
    cases=[compare(taps,phases) for taps in (16,24,32) for phases in (128,256)]
    report=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        cases=cases,scope=__doc__,rounding_scope='Coefficient bound excludes final convolution/interpolation rounding and filter approximation.',
        warning='16-bit output can clip on intersample overshoot; a firmware implementation must define saturation and test headroom.')
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    for c in cases:
        tone=c['tones'][-1]
        print(json.dumps({k:c[k] for k in ('taps','table_phases','coefficient_flash_bytes','stereo_history_bytes','worst_coefficient_error_bound_pcm_lsb')}|dict(tone_20khz=tone)))
