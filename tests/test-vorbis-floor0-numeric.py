"""Independent Decimal oracle for the real standalone floor0 numeric component.

The exact-coefficient layer uses direct P/Q products, not the component's scaled
product algorithm. Trig/Bark approximation is a separate layer. No decoder,
private handle, SDK, QEMU, physical board or linear-gain clipping is involved.
"""
import argparse
import ast
from collections import Counter
from decimal import Context, Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import struct
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT/'idf/components/native_vorbis_numeric'
DRIVER = ROOT/'tests/native/vorbis_floor0_numeric_test.c'
DECIMAL_CONTEXT = Context(prec=120, Emax=1000000, Emin=-1000000)
POLICY = dict(schema='native-vorbis-floor0-policy-v1', oracle='stdlib Decimal direct polynomial',
              oracle_precision_digits=120, denominator_relative_bound='2e-12',
              gain_abs_relative_bound='2e-12', cosine_absolute_bound='4e-15',
              bark_integer_exact=True, literal_db_coefficient='0.11512925',
              amplitude63_deficit_one_D1='negative, nonzero, relative error <=2e-12',
              selected_before_component_measurement=True, threshold_fitted_to_output=False,
              decoder_or_PCM_qualification=False)
TARGET_KEYS = ('id', 'operation', 'raw_amplitude', 'amplitude_bits', 'amplitude_offset',
               'coefficients_hex', 'w_hex', 'denominator_mantissa_hex', 'denominator_exponent')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def double_hex(value):
    return struct.pack('>d', value).hex()


def from_hex(value):
    need(isinstance(value, str) and re.fullmatch(r'[0-9a-f]{16}', value), 'IEEE64 literal bits')
    return struct.unpack('>d', bytes.fromhex(value))[0]


def dec(value):
    return Decimal.from_float(value)


@lru_cache(maxsize=None)
def decimal_pi(precision=160):
    def series(value):
        total = term = value
        square = value*value
        k = 1
        while True:
            term *= -square
            updated = total + term/Decimal(2*k+1)
            if updated == total:
                return total
            total = updated
            k += 1
    with localcontext() as context:
        context.prec = precision+12
        value = 16*series(Decimal(1)/5)-4*series(Decimal(1)/239)
        context.prec = precision
        return +value


@lru_cache(maxsize=None)
def decimal_cos(value):
    """Independent Taylor/Machin computation, including large finite angles."""
    need(value.is_finite(), 'finite oracle angle')
    with localcontext() as context:
        context.prec = max(160, max(0, value.copy_abs().adjusted())+160)
        pi = decimal_pi(context.prec)
        x = value % (2*pi)
        if x > pi:
            x -= 2*pi
        if x < -pi:
            x += 2*pi
        total = term = Decimal(1)
        square = x*x
        k = 1
        while True:
            term *= -square/Decimal((2*k-1)*(2*k))
            updated = total+term
            if updated == total:
                return total
            total = updated
            k += 1


def decimal_atan(value):
    with localcontext(DECIMAL_CONTEXT):
        need(value >= 0, 'nonnegative Bark frequency')
        reflected = value > 1
        if reflected:
            value = 1/value
        scale = 1
        while value > Decimal('0.1'):
            value /= 1+(1+value*value).sqrt()
            scale *= 2
        total = term = value
        square = value*value
        k = 1
        while True:
            term *= -square
            updated = total+term/Decimal(2*k+1)
            if updated == total:
                result = total*scale
                return decimal_pi()/2-result if reflected else result
            total = updated
            k += 1


def bark(value):
    with localcontext(DECIMAL_CONTEXT):
        return (Decimal('13.1')*decimal_atan(Decimal('0.00074')*value) +
                Decimal('2.24')*decimal_atan(Decimal('0.0000000185')*value*value) +
                Decimal('0.0001')*value)


@lru_cache(maxsize=None)
def bark_map(rate, bins, size):
    with localcontext(DECIMAL_CONTEXT):
        nyquist = bark(Decimal(rate)/2)
        return tuple(min(size-1, int((bark(Decimal(rate)*i/(2*bins))*size/nyquist)
                                    .to_integral_value(rounding=ROUND_FLOOR))) for i in range(bins))


@lru_cache(maxsize=None)
def bin_cosine(bin_index, size):
    with localcontext(DECIMAL_CONTEXT):
        # Cardinal values are mathematically exact, not a libm prediction.
        if not bin_index:
            return Decimal(2)
        if 2*bin_index == size:
            return Decimal(0)
        if 3*bin_index == size:
            return Decimal(1)
        if 3*bin_index == 2*size:
            return Decimal(-1)
        return 2*decimal_cos(decimal_pi()*bin_index/size)


@lru_cache(maxsize=None)
def denominator_oracle(coefficients, w_bits):
    """Direct squared products on exact supplied binary64 numbers."""
    with localcontext(DECIMAL_CONTEXT):
        w = dec(from_hex(w_bits))
        products = [Decimal(1), Decimal(1)]
        for index, bits in enumerate(coefficients):
            products[index % 2] *= w-dec(from_hex(bits))
        even, odd = products
        if len(coefficients) % 2:
            return +(even*even+(4-w*w)*odd*odd)/4
        return +((2+w)*even*even+(2-w)*odd*odd)/4


def scaled_value(value):
    with localcontext(DECIMAL_CONTEXT):
        return dec(from_hex(value['mantissa_hex']))*(Decimal(2)**value['exponent'])


def decimal_scaled(value):
    with localcontext(DECIMAL_CONTEXT):
        if not value:
            return dict(mantissa='0', exponent=0)
        exponent = int((value.copy_abs().ln()/Decimal(2).ln())
                       .to_integral_value(rounding=ROUND_FLOOR))+1
        mantissa = value/(Decimal(2)**exponent)
        while abs(mantissa) >= 1:
            mantissa /= 2
            exponent += 1
        while abs(mantissa) < Decimal('0.5'):
            mantissa *= 2
            exponent -= 1
        return dict(mantissa=str(mantissa), exponent=exponent)


def expected_value(value):
    with localcontext(DECIMAL_CONTEXT):
        return Decimal(value['mantissa'])*(Decimal(2)**value['exponent'])


@lru_cache(maxsize=None)
def gain_oracle(raw, bits, offset, denominator):
    with localcontext(DECIMAL_CONTEXT):
        if raw == 0:
            return 1, Decimal(0)
        if denominator == 0:
            return (2 if offset else 3), Decimal(0)
        amplitude = Decimal(raw)*offset/((1 << bits)-1)
        value = (amplitude/denominator.sqrt()-offset)*Decimal('0.11512925')/Decimal(2).ln()
        return 0, +value


def oracle_case(case):
    with localcontext(DECIMAL_CONTEXT):
        denominator = (denominator_oracle(tuple(case['coefficients_hex']), case['w_hex'])
                       if case['operation'] == 'curve' else
                       scaled_value(dict(mantissa_hex=case['denominator_mantissa_hex'],
                                         exponent=case['denominator_exponent'])))
        kind, gain = gain_oracle(int(case['raw_amplitude']), case['amplitude_bits'],
                                 case['amplitude_offset'], denominator)
        return dict(id=case['id'], kind=kind, denominator=decimal_scaled(denominator),
                    log2_gain=decimal_scaled(gain),
                    strict_nonzero_negative=case['id'] == 'amp63-deficit-one-D1')


def curve_case(identifier, coefficients, w, raw=63, bits=6, offset=60, target=False):
    return dict(id=identifier, operation='curve', raw_amplitude=str(raw), amplitude_bits=bits,
                amplitude_offset=offset, coefficients_hex=[double_hex(x) for x in coefficients],
                w_hex=double_hex(w), denominator_mantissa_hex=double_hex(0.0),
                denominator_exponent=0, _target=target)


def gain_case(identifier, mantissa, exponent, raw, bits, offset, target=False):
    return dict(id=identifier, operation='gain', raw_amplitude=str(raw), amplitude_bits=bits,
                amplitude_offset=offset, coefficients_hex=[], w_hex=double_hex(0.0),
                denominator_mantissa_hex=double_hex(mantissa), denominator_exponent=exponent,
                _target=target)


def cases(historical=None):
    rows = [
        curve_case('order1-empty-product', [0.0], 0.0, target=True),
        curve_case('order1-positive-gain', [1.5], 1.5, target=True),
        curve_case('order2-unity', [-1.0,1.0], 0.0, target=True),
        curve_case('absent-bits0', [0.0], 0.0, raw=0,bits=0,target=True),
        curve_case('order1-endpoint-pole', [2.0], 2.0, target=True),
        curve_case('order1-endpoint-indeterminate', [2.0], 2.0, offset=0,target=True),
        curve_case('order2-endpoint-pole', [2.0,1.0], 2.0,target=True),
        curve_case('zero-even-product', [0.0,1.0,2.0], 0.0,target=True),
        curve_case('zero-odd-product', [-1.0,0.0,1.0], 0.0,target=True),
        curve_case('both-products-zero', [0.0,0.0], 0.0,target=True),
        curve_case('near-endpoint-positive', [math.nextafter(2.0,0.0),-1.0],
                   math.nextafter(2.0,0.0), target=True)]
    for order in (1,2,3,4,5,6,7,8,15,16,31,32,63,64,127,128,254,255):
        for power in (1,20,500,1074):
            rows.append(curve_case(f'tiny-m{order}-p{power}',
                                   [math.ldexp(1.0,-power)]*order, 0.0,target=True))
        rows.append(curve_case(f'large-m{order}', [-2.0]*order,2.0,target=True))
        values = [((i*37)%113-56)/32 for i in range(order)]
        rows.append(curve_case(f'varied-m{order}', values,0.12345,target=True))
    rng = random.Random(0xF100)
    for index in range(80):
        order = rng.randint(1,255)
        rows.append(curve_case(f'random-{index}', [rng.uniform(-2,2) for _ in range(order)],
                               rng.uniform(-2,2)))
    for bits in (1,2,6,8,16,31,32,52,53,62,63):
        maximum = (1 << bits)-1
        for raw in sorted({0,1,maximum//2,maximum-1,maximum}):
            for offset in (0,1,60,255):
                for mantissa, exponent in ((0.0,0),(.5,1),(.875,0),(.5,2),(.75,-1),
                                           (.5,-550000),(.75,-2048),(.5,2049),(.75,550000)):
                    identifier = f'gain-b{bits}-r{raw}-o{offset}-e{exponent}-m{double_hex(mantissa)}'
                    rows.append(gain_case(identifier,mantissa,exponent,raw,bits,offset))
        for raw, name in ((1,'one'),(maximum-1,'deficit'),(maximum,'full')):
            rows.append(gain_case(f'wide-b{bits}-{name}',.5,1,raw,bits,255,target=True))
    rows.append(gain_case('amp63-deficit-one-D1',.5,1,(1 << 63)-2,63,255,target=True))
    for index,(mantissa, exponent) in enumerate(((0.0,0),(.5,-550000),(.75,-2048),
                                                (.5,2049),(.75,550000),(.875,0))):
        rows.append(gain_case(f'extreme-D-{index}',mantissa,exponent,(1 << 63)-1,63,255,target=True))
    for order in (1,2,5,6,16,254,255):
        angles = [(-3.0+6.0*i/max(1,order-1)) for i in range(order)]
        for inplace in (False,True):
            rows.append(dict(id=f'prepare-{order}-{int(inplace)}',operation='prepare',
                             angles=angles,inplace=inplace))
    rows.append(dict(id='prepare-large-small',operation='prepare',inplace=False,
                     angles=[0.0,-0.0,1e-300,-1e-300,1e20,-1e20,1e300,-1e300]))
    for rate in (1,3,8001,44101,48000,65535):
        for bins,size in ((1,1),(32,64),(128,128),(4096,65535)):
            rows.append(dict(id=f'bark-{rate}-{bins}-{size}',operation='map',
                             rate=rate,bins=bins,bark_size=size))
    for size in (1,2,3,6,64,128,255,65535):
        for bin_index in sorted({0,size//3,size//2,(2*size)//3,size-1}):
            rows.append(dict(id=f'bin-{bin_index}-{size}',operation='bin',bin=bin_index,bark_size=size))
    for order in (1,2,5,6,16,254,255):
        for bin_index in (0,2,3,4):
            c = curve_case(f'compose-bin-{order}-{bin_index}',[.125]*order,0.0)
            c.update(operation='at_bin',bin=bin_index,bark_size=6)
            rows.append(c)
    if historical is not None:
        model = historical['model']
        need(len(model['calls']) == 168, 'all original historical public unit calls')
        for original in model['calls']:
            words, call = original['words'], original['call']
            angles = [Fraction(value) for value in original['lsp_radians_exact']]
            coefficients = [float(2*decimal_cos(Decimal(x.numerator)/x.denominator)) for x in angles]
            n, size, rate = words[3],words[5],words[8]*2
            selected = (call*17) % n
            for index,bark_bin in enumerate(bark_map(rate,n,size)):
                rows.append(curve_case(f'history-{call:03d}-{index:04d}',coefficients,
                                       float(bin_cosine(bark_bin,size)),original['amplitude_raw'],
                                       original['amplitude_bits'],words[7],target=index==selected))
    target = [{key:row[key] for key in TARGET_KEYS} for row in rows if row.get('_target')]
    need(1 <= len(target) <= 512 and len({row['id'] for row in target}) == len(target),
         'finite unique full-coefficient target subset')
    return rows,target


def target_header(rows):
    lines = ['#pragma once','#include <stdint.h>','#include <stddef.h>',
             '#define FLOOR0_NUMERIC_CASE_COUNT '+str(len(rows)),
             'typedef struct { const char *id; uint32_t operation; uint64_t raw_amplitude;',
             ' uint32_t amplitude_bits,amplitude_offset,order; uint64_t w_bits;',
             ' const uint64_t *coefficients; uint64_t denominator_bits; int32_t denominator_exponent;',
             '} floor0_numeric_case_t;']
    for index,row in enumerate(rows):
        need(re.fullmatch(r'[A-Za-z0-9_-]{1,63}', row['id']), 'safe target identifier')
        if row['coefficients_hex']:
            lines.append('static const uint64_t floor0_coefficients_'+str(index)+'[] = {'+
                         ','.join('UINT64_C(0x'+value+')' for value in row['coefficients_hex'])+'};')
    lines.append('static const floor0_numeric_case_t floor0_numeric_cases[FLOOR0_NUMERIC_CASE_COUNT] = {')
    for index,row in enumerate(rows):
        pointer = 'floor0_coefficients_'+str(index) if row['coefficients_hex'] else 'NULL'
        lines.append('    {"%s",%d,UINT64_C(%s),%d,%d,%d,UINT64_C(0x%s),%s,UINT64_C(0x%s),INT32_C(%d)},' %
                     (row['id'],1 if row['operation']=='curve' else 2,row['raw_amplitude'],
                      row['amplitude_bits'],row['amplitude_offset'],len(row['coefficients_hex']),
                      row['w_hex'],pointer,row['denominator_mantissa_hex'],row['denominator_exponent']))
    return '\n'.join(lines+['};',''])


def pack(rows):
    output = bytearray(b'F0NUM001'+struct.pack('<I',len(rows)))
    for row in rows:
        operation = {'curve':1,'gain':2,'prepare':3,'map':4,'bin':5,'at_bin':6}[row['operation']]
        output += struct.pack('<I',operation)
        if operation in (1,2,6):
            output += struct.pack('<QII',int(row['raw_amplitude']),row['amplitude_bits'],row['amplitude_offset'])
            if operation == 2:
                output += bytes.fromhex(row['denominator_mantissa_hex'])[::-1]+struct.pack('<i',row['denominator_exponent'])
            else:
                output += struct.pack('<I',len(row['coefficients_hex']))
                output += (bytes.fromhex(row['w_hex'])[::-1] if operation==1 else
                           struct.pack('<II',row['bin'],row['bark_size']))
                output += b''.join(bytes.fromhex(value)[::-1] for value in row['coefficients_hex'])
        elif operation == 3:
            output += struct.pack('<II',len(row['angles']),int(row['inplace']))
            output += b''.join(struct.pack('<d',value) for value in row['angles'])
        elif operation == 4:
            output += struct.pack('<III',row['rate'],row['bins'],row['bark_size'])
        else:
            output += struct.pack('<II',row['bin'],row['bark_size'])
    return bytes(output)


class Reader:
    def __init__(self, data):
        self.data,self.cursor=data,0
    def read(self, fmt):
        size=struct.calcsize(fmt)
        need(self.cursor+size <= len(self.data),'complete binary output field')
        values=struct.unpack_from(fmt,self.data,self.cursor)
        self.cursor += size
        return values[0] if len(values)==1 else values
    def scaled(self):
        bits,exponent=self.read('<Qi')
        return dict(mantissa_hex=format(bits,'016x'),exponent=exponent)


def unpack(data, rows):
    reader=Reader(data)
    need(reader.read('<8s')==b'F0OUT001' and reader.read('<I')==len(rows),'complete binary output header')
    metadata=reader.read('<I')
    need(metadata>=40,'actual metadata/output-preservation control calls')
    observed=[]
    for index,row in enumerate(rows):
        operation,actual_index=reader.read('<II')
        need(actual_index==index and operation=={'curve':1,'gain':2,'prepare':3,'map':4,'bin':5,'at_bin':6}[row['operation']],
             'ordered complete binary operations')
        item=dict(id=row['id'],operation=row['operation'])
        if operation in (1,2,6):
            item['ds']=reader.read('<i');item['denominator']=reader.scaled()
            item['gs'],item['kind']=reader.read('<iI');item['log2_gain']=reader.scaled()
            item['w_hex']=format(reader.read('<Q'),'016x')
        elif operation == 3:
            status,count=reader.read('<iI')
            need(status==0 and count==len(row['angles']),'complete prepared array')
            item['values']=[format(reader.read('<Q'),'016x') for _ in range(count)]
        elif operation == 4:
            status,count=reader.read('<iI')
            need(status==0 and count==row['bins'],'complete Bark map')
            item['values']=[reader.read('<H') for _ in range(count)]
        else:
            need(reader.read('<i')==0,'actual cosine helper success')
            item['w_hex']=format(reader.read('<Q'),'016x')
        need(reader.read('<I')==7,'all canaries/input/tail checks')
        observed.append(item)
    need(reader.cursor==len(data),'no missing or extra binary output bytes')
    return observed,metadata


def actual_value(scaled):
    value=from_hex(scaled['mantissa_hex']);exponent=scaled['exponent']
    need(math.isfinite(value) and type(exponent) is int and abs(exponent)<=1000000 and
         ((value==0 and exponent==0 and scaled['mantissa_hex']=='0000000000000000') or
          .5<=abs(value)<1), 'normalized finite actual scaled result')
    with localcontext(DECIMAL_CONTEXT):
        return dec(value)*(Decimal(2)**exponent)


def compare_numeric(case, actual, expected=None):
    """Independent predictive comparison, reusable for retained target rows."""
    with localcontext(DECIMAL_CONTEXT):
        expected=expected or oracle_case(case)
        need(actual['gs']==0,'actual numerical result available')
        reasons=[]
        if actual['kind']!=expected['kind']:
            reasons.append('actual floor kind differs')
        expected_den=expected_value(expected['denominator'])
        expected_gain=expected_value(expected['log2_gain'])
        if case['operation']=='gain':
            need(actual['ds']==-99 and actual['denominator']==dict(
                mantissa_hex=case['denominator_mantissa_hex'],exponent=case['denominator_exponent']),
                 'direct gain denominator is unchanged input, not a computed denominator')
            denominator_error=Decimal(0)
        else:
            need(actual['ds']==0,'actual polynomial success')
            actual_den=actual_value(actual['denominator'])
            denominator_error=abs(actual_den-expected_den)
            if not (actual_den==0 if expected_den==0 else denominator_error/expected_den<=Decimal('2e-12')):
                reasons.append('independent exact-coefficient denominator bound')
        value=actual_value(actual['log2_gain'])
        gain_error=abs(value-expected_gain)
        if gain_error>Decimal('2e-12')*max(Decimal(1),abs(expected_gain)):
            reasons.append('independent scaled log2 gain bound')
        relative=gain_error/abs(expected_gain) if expected_gain else None
        if expected['strict_nonzero_negative'] and not (value<0 and relative<=Decimal('2e-12')):
            reasons.append('wide amplitude deficit was lost or inaccurate')
        return dict(id=case['id'],qualified=not reasons,failure_reasons=reasons,
                    denominator_relative_error=str(denominator_error/expected_den) if expected_den else None,
                    denominator_absolute_error=str(denominator_error),
                    gain_absolute_error=str(gain_error),
                    gain_relative_error=str(relative) if relative is not None else None,
                    expected_log2_gain=str(expected_gain),actual_log2_gain=str(value),
                    expected_kind=expected['kind'],actual_kind=actual['kind'],
                    expected_denominator=expected['denominator'],
                    actual_denominator=actual['denominator'],actual_scaled_gain=actual['log2_gain'])


def compare_target_rows(model, expected, observed):
    need(model['schema']=='native-vorbis-floor0-numeric-cases-v1' and
         expected['schema']=='native-vorbis-floor0-expected-v1' and expected['policy']==POLICY and
         len(model['cases'])==len(expected['cases'])==len(observed),'complete unchanged target mathematical scope')
    metrics=[];failures=[]
    for index,(case,wanted,row) in enumerate(zip(model['cases'],expected['cases'],observed)):
        try:
            need(row['case']==index and row['id']==case['id']==wanted['id'] and
                 row['operation']==case['operation'] and row['order']==len(case['coefficients_hex']) and
                 row['guards']==1 and row['unchanged']==1,'actual complete target case identity/guards')
            need(oracle_case(case)==wanted,'unchanged independent expected value for every original case')
            actual=dict(ds=row['ds'],gs=row['gs'],kind=row['kind'],
                        denominator=dict(mantissa_hex=row['denominator_bits'],exponent=row['denominator_exponent']),
                        log2_gain=dict(mantissa_hex=row['log2_bits'],exponent=row['log2_exponent']))
            metric=compare_numeric(case,actual,wanted);metrics.append(metric)
            if not metric['qualified']:
                failures.append(dict(index=index,**metric))
        except (ValueError,KeyError,TypeError) as exc:
            failures.append(dict(index=index,id=case['id'],nonmeasurement_error=str(exc),actual=row))
    return dict(measurement_completed=len(metrics)==len(model['cases']),
                passed=not failures and len(metrics)==len(model['cases']),metrics=metrics,failures=failures)


def oracle_self_checks():
    with localcontext(DECIMAL_CONTEXT):
        for coefficients,w,wanted in (([0.0],0.0,1),([-1.0,1.0],0.0,1),([1.0],1.0,Decimal('.75')),
                                       ([2.0],2.0,0),([0.0,1.0,2.0],0.0,1)):
            need(denominator_oracle(tuple(map(double_hex,coefficients)),double_hex(w))==wanted,
                 'hand-derived parity/order-one polynomial')
        kind,value=gain_oracle((1<<63)-2,63,255,Decimal(1))
        need(kind==0 and value<0 and expected_value(decimal_scaled(value))!=0,'wide exact amplitude deficit')
        need(gain_oracle(0,0,255,Decimal(0))[0]==1 and gain_oracle(1,1,255,Decimal(0))[0]==2 and
             gain_oracle(1,1,0,Decimal(0))[0]==3,'absent/pole/indeterminate mathematical distinction')
        need(bark_map(3,32,1)==(0,)*32 and bark_map(65535,1,65535)==(0,), 'Bark cardinal maps')
        examples=[curve_case('reporting-hand-'+str(i),[0.0],0.0) for i in range(2)]
        model=dict(schema='native-vorbis-floor0-numeric-cases-v1',cases=examples)
        expected=dict(schema='native-vorbis-floor0-expected-v1',policy=POLICY,
                      cases=[oracle_case(case) for case in examples])
        rows=[dict(case=i,id=case['id'],operation='curve',order=1,ds=0,
                   denominator_bits=double_hex(.5),denominator_exponent=1,gs=0,kind=0,
                   log2_bits=double_hex(0.0),log2_exponent=0,guards=1,unchanged=1)
              for i,case in enumerate(examples)]
        need(compare_target_rows(model,expected,rows)['passed'],'hand-derived synthetic comparator control')
        rows[1]['denominator_bits']=double_hex(.75)
        rejected=compare_target_rows(model,expected,rows)
        need(rejected['measurement_completed'] and not rejected['passed'] and
             len(rejected['metrics'])==2 and len(rejected['failures'])==1 and
             Decimal(rejected['failures'][0]['denominator_relative_error'])==Decimal('.5'),
             'complete rejected comparison retains failed numerical metrics')
    return dict(oracle_self_checks_only=True,synthetic_comparator_controls_only=True,
                component_executed=False,SDK_or_QEMU_executed=False)


def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--historical-contract',type=Path)
    parser.add_argument('--historical-sha256')
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--oracle-self-test',action='store_true')
    args=parser.parse_args()
    if args.oracle_self_test:
        print(json.dumps(oracle_self_checks()));return 0
    need(args.output is not None,'explicit fresh output')
    out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh .build output')
    out.mkdir(parents=True);(out/'sources').mkdir();(out/'target-cases').mkdir()
    report=dict(completed=False,passed=False,prepared=False,scope=__doc__,policy=POLICY,
                commands=[],sources={},component_executed=False,decoder_executed=False,
                SDK_or_QEMU_executed=False,full_G6_qualified=False,physical_device=False)
    def save():
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path,name):
        data=path.read_bytes();(out/'sources'/name).write_bytes(data)
        report['sources'][str(path.resolve())]=dict(sha256=sha(data),snapshot='sources/'+name)
        return data
    def current():
        need(all(sha(Path(path).read_bytes())==pin['sha256']==sha((out/pin['snapshot']).read_bytes())
                 for path,pin in report['sources'].items()),'original/frozen entire C/header/controller source unchanged')
    save()
    try:
        freeze(Path(__file__),'test-vorbis-floor0-numeric.py')
        freeze(MODULE/'floor0.c','floor0.c')
        freeze(MODULE/'include/native_vorbis_floor0.h','native_vorbis_floor0.h')
        freeze(DRIVER,'driver.c')
        owner=ROOT/'tests/test-vorbis-floor1-render.py'
        tree=ast.parse(freeze(owner,'owned-supervisor-source.py'))
        assignments=[node for node in tree.body if isinstance(node,ast.Assign) and any(
            isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(assignments)==1,'one existing nonce-owned process supervisor literal')
        supervisor=ast.literal_eval(assignments[0].value)
        need(isinstance(supervisor,str),'literal reviewed supervisor')
        (out/'supervisor.py').write_text(supervisor,encoding='utf-8',newline='\n')
        historical=None
        if args.historical_contract:
            need(args.historical_sha256 and re.fullmatch(r'[0-9a-f]{64}',args.historical_sha256),
                 'explicit recorded historical input-contract identity')
            body=freeze(args.historical_contract.resolve(),'historical-contract.json')
            need(sha(body)==args.historical_sha256,'historical mathematical unit input bytes')
            historical=json.loads(body)
            report['historical_scope']='Recorded owned unit inputs only; no transitive carrier/decoder/reference requalification'
        oracle_self_checks()
        rows,target=cases(historical)
        expected=dict(schema='native-vorbis-floor0-expected-v1',policy=POLICY,cases=[oracle_case(row) for row in target])
        model=dict(schema='native-vorbis-floor0-numeric-cases-v1',cases=target)
        directory=out/'target-cases'
        (directory/'cases.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8')
        (directory/'cases.h').write_text(target_header(target),encoding='ascii',newline='\n')
        (directory/'expected.json').write_text(json.dumps(expected,indent=2)+'\n',encoding='utf-8')
        (out/'inputs.bin').write_bytes(pack(rows))
        report.update(prepared=True,cases=len(rows),target_cases=len(target),case_groups=dict(Counter(row['operation'] for row in rows)),
                      input_sha256=sha((out/'inputs.bin').read_bytes()),
                      target_input_sha256={name:sha((directory/name).read_bytes()) for name in ('cases.json','cases.h','expected.json')},
                      historical_calls=168 if historical is not None else 0,
                      historical_scalar_bins=sum(row['id'].startswith('history-') for row in rows))
        current();save()
        if args.prepare_only:
            print(json.dumps(dict(prepared=True,passed=False,component_executed=False,cases=len(rows),target_cases=len(target))))
            return 0

        def run(name,argv):
            nonce=uuid.uuid4().hex
            request,receipt,stop=(out/(name+suffix) for suffix in ('.request.json','.receipt.json','.stop'))
            request.write_text(json.dumps(dict(nonce=nonce,argv=argv,timeout=60,receipt=host(receipt),stop=host(stop))),encoding='utf-8')
            command=(['wsl.exe','--exec','python3'] if sys.platform=='win32' else [sys.executable])+[host(out/'supervisor.py'),host(request)]
            entry=dict(name=name,argv=command,child_argv=argv,nonce=nonce)
            report['commands'].append(entry);save()
            child=None;error=None;start=time.monotonic()
            stdout,stderr=out/(name+'.stdout.log'),out/(name+'.stderr.log')
            try:
                with stdout.open('xb') as so,stderr.open('xb') as se:
                    child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=so,stderr=se,
                                           creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                    entry['transport_pid']=child.pid;save();child.wait(timeout=80)
            except BaseException as exc:
                error=exc
            finally:
                if child is not None and child.poll() is None:
                    stop.write_text(nonce,encoding='utf-8')
                    try:child.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        child.kill();child.wait(timeout=5);entry['forced_transport_stop']=True
                actual=json.loads(receipt.read_bytes()) if receipt.exists() else {}
                entry.update(supervisor=actual,transport_returncode=None if child is None else child.poll(),
                             elapsed_seconds=time.monotonic()-start,
                             stdout_sha256=sha(stdout.read_bytes()) if stdout.exists() else None,
                             stderr_sha256=sha(stderr.read_bytes()) if stderr.exists() else None);save()
            need(actual.get('nonce')==nonce and actual.get('request_sha256')==sha(request.read_bytes()) and
                 actual.get('final') is True and actual.get('new_session') is True and actual.get('child_reaped') is True and
                 actual.get('group_gone') is True and actual.get('state')=='terminal' and
                 actual.get('child_returncode')==0 and entry['transport_returncode']==0 and
                 not entry.get('forced_transport_stop') and 'cleanup_error' not in actual,'owned terminal/cleanup '+name)
            if error is not None:raise error
            return stdout.read_bytes(),stderr.read_bytes()

        run('compiler-version',['gcc','--version'])
        run('compiler-machine',['gcc','-dumpmachine'])
        flags=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pedantic','-fno-fast-math',
               '-ffp-contract=off','-fsanitize=address,undefined','-fno-sanitize-recover=all',
               '-fno-omit-frame-pointer','-fno-pie','-no-pie']
        so,se=run('compile',flags+['-I'+host(out/'sources'),host(out/'sources/driver.c'),
                                 host(out/'sources/floor0.c'),'-lm','-o',host(out/'test')])
        need(not so and not se,'strict component/adapter compile without diagnostics')
        current()
        so,se=run('execute',[host(out/'test'),host(out/'inputs.bin'),host(out/'outputs.bin')])
        report['component_executed']=True
        need(not so and not se,'actual ASan/UBSan execution without diagnostics')
        observed,metadata=unpack((out/'outputs.bin').read_bytes(),rows)
        metrics=[];cosine_errors=[];bark_bins=0;failures=[];nonmeasurement_errors=[]
        for index,(case,actual) in enumerate(zip(rows,observed)):
            try:
                if case['operation'] in ('curve','gain','at_bin'):
                    selected=dict(case)
                    if selected['operation']=='at_bin':
                        selected.update(operation='curve',w_hex=actual['w_hex'])
                        error=abs(dec(from_hex(actual['w_hex']))-bin_cosine(case['bin'],case['bark_size']))
                        cosine_errors.append(error)
                        if error>Decimal('4e-15'):
                            failures.append(dict(index=index,id=case['id'],reason='composed bin cosine approximation',
                                                 cosine_absolute_error=str(error)))
                    metric=compare_numeric(selected,actual);metrics.append(metric)
                    if not metric['qualified']:
                        failures.append(dict(index=index,**metric))
                elif case['operation']=='prepare':
                    for element,(angle,bits) in enumerate(zip(case['angles'],actual['values'])):
                        error=abs(dec(from_hex(bits))-2*decimal_cos(dec(angle)))
                        cosine_errors.append(error)
                        if error>Decimal('4e-15'):
                            failures.append(dict(index=index,id=case['id'],element=element,
                                                 reason='separate angle cosine approximation',
                                                 cosine_absolute_error=str(error)))
                elif case['operation']=='bin':
                    error=abs(dec(from_hex(actual['w_hex']))-bin_cosine(case['bin'],case['bark_size']))
                    cosine_errors.append(error)
                    if error>Decimal('4e-15'):
                        failures.append(dict(index=index,id=case['id'],reason='separate bin cosine approximation',
                                             cosine_absolute_error=str(error)))
                else:
                    wanted=bark_map(case['rate'],case['bins'],case['bark_size'])
                    bark_bins+=len(wanted)
                    differences=[dict(bin=bin_index,expected=value,actual=actual['values'][bin_index])
                                 for bin_index,value in enumerate(wanted) if actual['values'][bin_index]!=value]
                    if differences:
                        failures.append(dict(index=index,id=case['id'],reason='independent exact Bark integer map',
                                             different_bins=differences))
            except (ValueError,KeyError,TypeError) as exc:
                nonmeasurement_errors.append(dict(index=index,id=case['id'],reason=str(exc),actual=actual))
        with localcontext(DECIMAL_CONTEXT):
            report['numerical']=dict(cases_compared=len(rows),numeric_scalar_comparisons=len(metrics),
                measurement_completed=not nonmeasurement_errors,
                metadata_controls=metadata,cosine_values_compared=len(cosine_errors),bark_bins_compared=bark_bins,
                max_denominator_relative_error=str(max((Decimal(row['denominator_relative_error']) for row in metrics
                                                       if row['denominator_relative_error'] is not None),default=Decimal(0))),
                max_gain_absolute_error=str(max((Decimal(row['gain_absolute_error']) for row in metrics),default=Decimal(0))),
                max_gain_relative_error_including_near_zero=str(max((Decimal(row['gain_relative_error']) for row in metrics
                                                                    if row['gain_relative_error'] is not None),default=Decimal(0))),
                max_cosine_absolute_error=str(max(cosine_errors,default=Decimal(0))),
                failures=failures,nonmeasurement_errors=nonmeasurement_errors,
                passing_numeric_cases=sum(row['qualified'] for row in metrics),
                rejected_numeric_cases=sum(not row['qualified'] for row in metrics),
                passed=not failures and not nonmeasurement_errors)
        current()
        need(sha((out/'inputs.bin').read_bytes())==report['input_sha256'],'actual binary inputs unchanged')
        report['output_sha256']=sha((out/'outputs.bin').read_bytes())
        passed=not failures and not nonmeasurement_errors
        report.update(completed=True,passed=passed,source_inputs_unchanged=True,
                      result='FINITE_FLOOR0_NUMERIC_QUALIFIED' if passed else 'FINITE_FLOOR0_NUMERIC_REJECTED')
        save()
        print(json.dumps({key:report[key] for key in ('completed','passed','cases','target_cases','result','numerical')}))
        return 0 if passed else 1
    except BaseException as exc:
        report.update(completed=False,passed=False,error=repr(exc));save();raise


if __name__=='__main__':
    sys.exit(main())
