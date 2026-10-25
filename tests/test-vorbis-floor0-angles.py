"""Original-angle floor0 tests: independent Chudnovsky/Decimal direct cos P+Q.

No production phase/sine algorithm is used as the oracle. All finite binary64
angles are allowed; exact mathematical theta=pi*bin/map is retained. The fixed
engineering bounds qualify this finite numeric layer, not a decoder or PCM.
"""
import argparse
import ast
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
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

ROOT=Path(__file__).resolve().parents[1]
COMPONENT=ROOT/'idf/components/native_vorbis_numeric'
DRIVER=ROOT/'tests/native/vorbis_floor0_angles_test.c'
POLICY=dict(schema='native-vorbis-floor0-angles-policy-v1',
    oracle='Independent Chudnovsky pi intervals and direct Decimal cosine P/Q',
    minimum_decimal_precision=800,stored_scaled_precision=120,
    denominator_relative_bound='2e-12',gain_abs_relative_bound='2e-12',
    literal_db_coefficient='0.11512925',selected_before_measurement=True,
    threshold_fitted_to_output=False,full_finite_binary64_angles=True,
    decoder_or_PCM_qualification=False)


def need(ok,reason):
    if not ok:raise ValueError(reason)


def sha(data):return hashlib.sha256(data).hexdigest()
def bits(value):return struct.pack('>d',value).hex()
def number(value):
    need(isinstance(value,str) and re.fullmatch('[0-9a-f]{16}',value),'literal IEEE64 bits')
    return struct.unpack('>d',bytes.fromhex(value))[0]
def context(precision=800,rounding=None):
    kwargs=dict(prec=precision,Emax=1000000,Emin=-1000000)
    if rounding is not None:kwargs['rounding']=rounding
    return Context(**kwargs)


@lru_cache(maxsize=None)
def pi_interval(precision):
    """Chudnovsky recurrence with directed rational sums and an integer sqrt.

    A=13591409, B=545140134, X multiplier=-640320^3. The remaining
    absolute series tail is <2*abs(next term): every subsequent term ratio
    is <=1728*(A+B)/(A*abs(X multiplier))<1/2. No libm/Machin pi is used.
    """
    floor,ceiling=context(precision,ROUND_FLOOR),context(precision,ROUND_CEILING)
    a,b,scale=13591409,545140134,262537412640768000
    need(2*1728*(a+b)<a*scale,'global geometric tail bound')
    lower=upper=Decimal(0);m,l,x,k=1,a,1,6
    terms=precision//14+8
    for index in range(terms):
        numerator=Decimal(m*l);denominator=Decimal(x)
        lower=floor.add(lower,floor.divide(numerator,denominator))
        upper=ceiling.add(upper,ceiling.divide(numerator,denominator))
        divisor=(index+1)**3;product=m*(k*k*k-16*k)
        need(product%divisor==0,'exact Chudnovsky integer recurrence')
        m=product//divisor;l+=b;x*=-scale;k+=12
    tail=ceiling.multiply(Decimal(2),ceiling.divide(Decimal(abs(m*l)),Decimal(abs(x))))
    lower=floor.subtract(lower,tail);upper=ceiling.add(upper,tail)
    digits=precision+20;unit=10**digits
    root=math.isqrt(10005*unit*unit)
    exact=context(precision+40)
    sqrt_lo=Decimal(root).scaleb(-digits,context=exact)
    sqrt_hi=Decimal(root+1).scaleb(-digits,context=exact)
    return (floor.divide(floor.multiply(Decimal(426880),sqrt_lo),upper),
            ceiling.divide(ceiling.multiply(Decimal(426880),sqrt_hi),lower))


@lru_cache(maxsize=None)
def pi(precision):
    lo,hi=pi_interval(precision+32)
    with localcontext(context(precision)):return (lo+hi)/2


def precision_for(angle_bits):
    value=Decimal.from_float(number(angle_bits))
    extra=max(0,value.copy_abs().adjusted())
    return 800+128*((extra+127)//128)


@lru_cache(maxsize=None)
def cosine(angle_bits):
    precision=precision_for(angle_bits)
    with localcontext(context(precision+32)):
        value=Decimal.from_float(number(angle_bits))
        p=pi(precision+32);value%=2*p
        if value>p:value-=2*p
        if value<-p:value+=2*p
        total=term=Decimal(1);square=value*value;index=1
        while True:
            term*=-square/Decimal((2*index-1)*(2*index))
            updated=total+term
            if updated==total:
                with localcontext(context(precision)):return +total
            total=updated;index+=1


@lru_cache(maxsize=None)
def theta_cosine(bin_index,map_size,precision):
    if not bin_index:return Decimal(1)
    if 2*bin_index==map_size:return Decimal(0)
    if 3*bin_index==map_size:return Decimal('.5')
    if 3*bin_index==2*map_size:return Decimal('-.5')
    with localcontext(context(precision+32)):
        value=pi(precision+32)*bin_index/map_size
        total=term=Decimal(1);square=value*value;index=1
        while True:
            term*=-square/Decimal((2*index-1)*(2*index))
            updated=total+term
            if updated==total:
                with localcontext(context(precision)):return +total
            total=updated;index+=1


@lru_cache(maxsize=None)
def db_coefficient(precision):
    with localcontext(context(precision)):return Decimal('0.11512925')/Decimal(2).ln()


@lru_cache(maxsize=None)
def denominator(angle_bits,bin_index,map_size):
    precision=max(precision_for(value) for value in angle_bits)
    with localcontext(context(precision)):
        w=2*theta_cosine(bin_index,map_size,precision)
        even=odd=Decimal(1)
        for index,value in enumerate(angle_bits):
            factor=w-2*cosine(value)
            if index%2:odd*=factor
            else:even*=factor
        if len(angle_bits)%2:return +(even*even+(4-w*w)*odd*odd)/4
        return +((2+w)*even*even+(2-w)*odd*odd)/4


def scaled(value):
    with localcontext(context(120)):
        if not value:return dict(mantissa='0',exponent=0)
        exponent=int((abs(value).ln()/Decimal(2).ln()).to_integral_value(rounding=ROUND_FLOOR))+1
        mantissa=value/(Decimal(2)**exponent)
        while abs(mantissa)>=1:mantissa/=2;exponent+=1
        while abs(mantissa)<Decimal('.5'):mantissa*=2;exponent-=1
        return dict(mantissa=str(mantissa),exponent=exponent)


def expected_value(value):
    with localcontext(context(160)):return Decimal(value['mantissa'])*(Decimal(2)**value['exponent'])


def actual_value(mantissa_bits,exponent):
    value=number(mantissa_bits)
    need(math.isfinite(value) and type(exponent) is int and abs(exponent)<=1000000 and
         ((mantissa_bits=='0000000000000000' and exponent==0) or .5<=abs(value)<1),
         'normalized finite actual scaled result')
    with localcontext(context(160)):return Decimal.from_float(value)*(Decimal(2)**exponent)


def oracle_case(case):
    precision=max(precision_for(value) for value in case['angles_hex'])
    with localcontext(context(precision)):
        d=denominator(tuple(case['angles_hex']),case['bin'],case['map_size'])
        raw,bits_count,offset=int(case['raw_amplitude']),case['amplitude_bits'],case['amplitude_offset']
        if not raw:kind,gain=1,Decimal(0)
        elif not d:kind,gain=(2 if offset else 3),Decimal(0)
        else:
            kind=0
            gain=(Decimal(raw)*offset/((1<<bits_count)-1)/d.sqrt()-offset)*db_coefficient(precision)
        return dict(id=case['id'],kind=kind,denominator=scaled(d),log2_gain=scaled(gain),
                    oracle_precision=precision)


def check_phase_table(source):
    dimensions = []
    for name in ('PHASE_FRACTION_WORDS','PHASE_WORDS','PHASE_TABLE_WORDS'):
        values=re.findall(r'\b'+name+r'\s*=\s*(\d+)\b',source)
        need(len(values)==1,'one literal production phase dimension')
        dimensions.append(int(values[0]))
    need(tuple(dimensions) in ((36,37,72),(72,73,128)),'supported production phase dimensions')
    count=dimensions[2];table_bits=32*count;precision=840 if count==72 else 1440
    arrays=re.findall(r'static const uint32_t floor0_two_over_pi\[PHASE_TABLE_WORDS\]\s*=\s*\{(.*?)\};',source,re.S)
    need(len(arrays)==1,'one inline production phase table')
    words=[int(value,16) for value in re.findall(r'UINT32_C\(0x([0-9a-fA-F]{8})\)',arrays[0])]
    need(len(words)==count,'all declared phase table limbs')
    lo,hi=pi_interval(precision)
    floor,ceiling=context(precision,ROUND_FLOOR),context(precision,ROUND_CEILING)
    scale=Decimal(1<<table_bits)
    lower=floor.multiply(floor.divide(Decimal(2),hi),scale)
    upper=ceiling.multiply(ceiling.divide(Decimal(2),lo),scale)
    left=int(lower.to_integral_value(rounding=ROUND_FLOOR))
    right=int(upper.to_integral_value(rounding=ROUND_FLOOR))
    need(left==right==sum(word<<(32*i) for i,word in enumerate(words)),
         'independent directed Chudnovsky interval proves every declared phase limb')
    return dict(limbs=count,bits=table_bits,independent_interval_floor_unique=True,
                pi_lower=str(lo),pi_upper=str(hi),algorithm='Chudnovsky directed rational sums + integer sqrt')


def make_case(identifier,angles,bin_index=0,map_size=1,raw=63,amplitude_bits=6,offset=60):
    return dict(id=identifier,angles_hex=[bits(value) for value in angles],bin=bin_index,map_size=map_size,
                raw_amplitude=str(raw),amplitude_bits=amplitude_bits,amplitude_offset=offset)


def validate_model(model):
    need(model['schema']=='native-vorbis-floor0-angles-cases-v1' and isinstance(model['cases'],list) and
         1<=len(model['cases'])<=10000,'finite original-angle corpus')
    names=set()
    for row in model['cases']:
        need(set(row)=={'id','angles_hex','bin','map_size','raw_amplitude','amplitude_bits','amplitude_offset'} and
             isinstance(row['id'],str) and re.fullmatch('[A-Za-z0-9_-]{1,63}',row['id']) and row['id'] not in names,
             'unique original-angle case fields/id')
        names.add(row['id'])
        need(isinstance(row['angles_hex'],list) and 1<=len(row['angles_hex'])<=255 and
             all(math.isfinite(number(value)) for value in row['angles_hex']),'complete finite binary64 angle arrays')
        need(all(type(row[key]) is int for key in ('bin','map_size','amplitude_bits','amplitude_offset')) and
             1<=row['map_size']<=65535 and 0<=row['bin']<row['map_size'] and
             0<=row['amplitude_bits']<=63 and 0<=row['amplitude_offset']<=255 and
             isinstance(row['raw_amplitude'],str) and re.fullmatch('0|[1-9][0-9]*',row['raw_amplitude']) and
             int(row['raw_amplitude'])<(1<<row['amplitude_bits']),'full public metadata and raw amplitude domain')
    return model['cases']


def cases():
    rows=[];target=[]
    def add(row,selected=False):
        rows.append(row)
        if selected:target.append(row)
    orders=(1,2,3,5,6,16,31,32,127,128,254,255)
    tiny=[0.,-0.,math.ldexp(1.,-1074),-math.ldexp(1.,-1074),math.ldexp(1.,-1073),
          -math.ldexp(1.,-1073),math.ldexp(1.,-1022),-math.ldexp(1.,-1022),
          math.ldexp(1.,-500),-math.ldexp(1.,-500),1e-8,-1e-8]
    for order in orders:
        for index,value in enumerate(tiny):
            add(make_case(f'tiny-m{order}-v{index}',[value]*order),
                order in (1,2,5,6,254,255) and index in (0,1,2,3,6,8))
    pairs=((0,1),(1,2),(1,3),(2,3),(1,65535),(32767,65535),(65534,65535),(19,127))
    for pair_index,(bin_index,size) in enumerate(pairs):
        with localcontext(context(850)):theta=float(pi(850)*bin_index/size)
        near=[theta,math.nextafter(theta,-math.inf),math.nextafter(theta,math.inf)]
        near += [-value for value in near]
        for order in (1,2,5,6,16,254,255):
            for index,value in enumerate(near):
                add(make_case(f'root-p{pair_index}-m{order}-v{index}',[value]*order,bin_index,size),
                    order in (1,2,5,6) and index in (0,2))
    extreme=[sys.float_info.max,-sys.float_info.max,math.ldexp(1.,1023),-math.ldexp(1.,1023),
             math.ldexp(1.,512),-math.ldexp(1.,512),math.ldexp(1.,128),-math.ldexp(1.,128),
             math.pi,-math.pi,2*math.pi,-2*math.pi,1e20,-1e20,1e300,-1e300]
    for order in (1,2,5,6,16,254,255):
        for index,value in enumerate(extreme):
            add(make_case(f'extreme-m{order}-v{index}',[value]*order,19,127),
                order in (1,2,255) and index in (0,1,4,5))
    rng=random.Random(0xA091E)
    pool=[number(format((rng.getrandbits(1)<<63)|(rng.randrange(2047)<<52)|rng.getrandbits(52),'016x'))
          for _ in range(128)]
    for index in range(512):
        order=orders[index%len(orders)];size=rng.randint(1,65535);bin_index=rng.randrange(size)
        add(make_case(f'random-{index}',[rng.choice(pool) for _ in range(order)],bin_index,size),index<72)
    for width in range(64):
        maximum=(1<<width)-1
        for raw in sorted({0,maximum,maximum//2,max(0,maximum-1),min(1,maximum)}):
            for offset in (0,1,60,255):
                add(make_case(f'amplitude-b{width}-r{raw}-o{offset}',[0.0],1,3,raw,width,offset))
    for order in (5,6):
        for bin_index in (0,1,7,63):
            add(make_case(f'typical-m{order}-b{bin_index}',[(i+1)*7/16 for i in range(order)],bin_index,64))
    selected=[make_case('selected-absent-b0',[0.0],1,3,0,0,255),
              make_case('selected-offset0',[0.0],1,3,1,1,0),
              make_case('selected-pole',[0.0],0,1,1,1,255),
              make_case('selected-indeterminate',[0.0],0,1,1,1,0)]
    for width in (1,31,32,63):
        maximum=(1<<width)-1
        for raw,label in ((1,'one'),(maximum-1,'deficit'),(maximum,'full')):
            selected.append(make_case(f'selected-b{width}-{label}',[0.0],1,3,raw,width,255))
    for row in selected:add(row,True)
    model=dict(schema='native-vorbis-floor0-angles-cases-v1',cases=rows)
    validate_model(model)
    need(len(target)==200,'complete predeclared200 target subset')
    return model,dict(schema=model['schema'],cases=target)


def target_header(model):
    rows=validate_model(model)
    lines=['#pragma once','#include <stdint.h>','#define FLOOR0_ANGLES_CASE_COUNT '+str(len(rows)),
           'typedef struct { const char *id; const uint64_t *angles; uint32_t order,bin,map_size;',
           ' uint64_t raw_amplitude; uint32_t amplitude_bits,amplitude_offset; } floor0_angles_case_t;']
    for index,row in enumerate(rows):
        lines.append('static const uint64_t floor0_angles_'+str(index)+'[] = {'+
                     ','.join('UINT64_C(0x'+value+')' for value in row['angles_hex'])+'};')
    lines.append('static const floor0_angles_case_t floor0_angles_cases[FLOOR0_ANGLES_CASE_COUNT] = {')
    lines += ['    {"%s",floor0_angles_%d,%d,%d,%d,UINT64_C(%s),%d,%d},' %
              (row['id'],i,len(row['angles_hex']),row['bin'],row['map_size'],row['raw_amplitude'],
               row['amplitude_bits'],row['amplitude_offset']) for i,row in enumerate(rows)]
    return '\n'.join(lines+['};',''])


class Reader:
    def __init__(self,data):self.data,self.cursor=data,0
    def take(self,fmt):
        size=struct.calcsize(fmt);need(self.cursor+size<=len(self.data),'complete binary field')
        values=struct.unpack_from(fmt,self.data,self.cursor);self.cursor+=size
        return values[0] if len(values)==1 else values
    def scaled(self):
        value,exponent=self.take('<Qi');return dict(mantissa_bits=format(value,'016x'),exponent=exponent)


def encode_input(model):
    rows=validate_model(model);data=bytearray(b'F0ANG001'+struct.pack('<I',len(rows)))
    for row in rows:
        name=row['id'].encode('ascii');data+=struct.pack('<I',len(name))+name
        data+=struct.pack('<QIIIII',int(row['raw_amplitude']),row['amplitude_bits'],row['amplitude_offset'],
                          len(row['angles_hex']),row['bin'],row['map_size'])
        data+=b''.join(bytes.fromhex(value)[::-1] for value in row['angles_hex'])
    return bytes(data)


def decode_input(data):
    reader=Reader(data);need(reader.take('<8s')==b'F0ANG001','original-angle input magic')
    count=reader.take('<I');need(1<=count<=10000,'finite binary input count');rows=[]
    for _ in range(count):
        length=reader.take('<I');need(1<=length<=63,'bounded input identifier')
        name=reader.take('<'+str(length)+'s').decode('ascii')
        raw,width,offset,order,bin_index,size=reader.take('<QIIIII')
        need(1<=order<=255,'binary angle order')
        values=[format(reader.take('<Q'),'016x') for _ in range(order)]
        rows.append(dict(id=name,angles_hex=values,bin=bin_index,map_size=size,
                         raw_amplitude=str(raw),amplitude_bits=width,amplitude_offset=offset))
    need(reader.cursor==len(data),'exact complete input bytes')
    model=dict(schema='native-vorbis-floor0-angles-cases-v1',cases=rows);validate_model(model);return model


def decode_output(data,model):
    rows=validate_model(model);reader=Reader(data)
    need(reader.take('<8s')==b'F0ANGOUT' and reader.take('<I')==len(rows),'complete original-angle output header')
    metadata=reader.take('<I');need(metadata==28,'all28 actual invalid/preservation controls')
    observed=[]
    for index,row in enumerate(rows):
        need(reader.take('<I')==index,'ordered original-angle binary case')
        ds=reader.take('<i');d=reader.scaled();gs,kind=reader.take('<iI');gain=reader.scaled()
        need(reader.take('<I')==7,'all canary/input/consistency guards')
        observed.append(dict(case=index,id=row['id'],order=len(row['angles_hex']),bin=row['bin'],map_size=row['map_size'],
            ds=ds,denominator_bits=d['mantissa_bits'],denominator_exponent=d['exponent'],gs=gs,kind=kind,
            log2_bits=gain['mantissa_bits'],log2_exponent=gain['exponent'],guards=1,unchanged=1))
    need(reader.cursor==len(data),'no missing/extra actual output bytes')
    return dict(metadata_controls=metadata,rows=observed)


def compare_case(case,actual,expected=None):
    expected=expected or oracle_case(case)
    need(actual['ds']==0 and actual['gs']==0,'actual original-angle numerical outputs available')
    with localcontext(context(160)):
        wanted_d,wanted_g=expected_value(expected['denominator']),expected_value(expected['log2_gain'])
        d=actual_value(actual['denominator_bits'],actual['denominator_exponent'])
        g=actual_value(actual['log2_bits'],actual['log2_exponent'])
        de,ge=abs(d-wanted_d),abs(g-wanted_g);reasons=[]
        if actual['kind']!=expected['kind']:reasons.append('floor kind')
        if (de/wanted_d>Decimal('2e-12') if wanted_d else d!=0):reasons.append('original-angle denominator bound')
        if ge>Decimal('2e-12')*max(Decimal(1),abs(wanted_g)):reasons.append('original-angle composed gain bound')
        return dict(id=case['id'],qualified=not reasons,failure_reasons=reasons,
            denominator_relative_error=str(de/wanted_d) if wanted_d else None,denominator_absolute_error=str(de),
            gain_absolute_error=str(ge),gain_relative_error=str(ge/abs(wanted_g)) if wanted_g else None,
            actual_kind=actual['kind'],expected=expected,actual=actual)


def compare_all(model,observed,expected=None):
    cases=validate_model(model);need(len(cases)==len(observed),'whole original-angle comparison')
    if expected is not None:
        need(expected['schema']=='native-vorbis-floor0-angles-expected-v1' and expected['policy']==POLICY and
             len(expected['cases'])==len(cases),'unchanged predeclared original-angle policy')
    metrics=[];failures=[]
    for index,(case,row) in enumerate(zip(cases,observed)):
        try:
            need(row['case']==index and row['id']==case['id'] and row['order']==len(case['angles_hex']) and
                 row['bin']==case['bin'] and row['map_size']==case['map_size'] and
                 row['guards']==row['unchanged']==1,'complete case identity and actual guards')
            wanted=oracle_case(case)
            if expected is not None:need(wanted==expected['cases'][index],'regenerated original-angle expected value')
            metric=compare_case(case,row,wanted);metrics.append(metric)
            if not metric['qualified']:failures.append(dict(index=index,**metric))
        except (ValueError,KeyError,TypeError) as error:
            failures.append(dict(index=index,id=case['id'],nonmeasurement_error=str(error),actual=row))
    def maximum(key):
        return str(max((Decimal(row[key]) for row in metrics if row[key] is not None),default=Decimal(0)))
    return dict(measurement_completed=len(metrics)==len(cases),passed=not failures and len(metrics)==len(cases),
        cases=len(cases),metrics=metrics,failures=failures,
        max_denominator_relative_error=maximum('denominator_relative_error'),
        max_gain_absolute_error=maximum('gain_absolute_error'),
        max_gain_relative_error_including_near_zero=maximum('gain_relative_error'))


def compare_target_rows(model,expected,observed):return compare_all(model,observed,expected)


def self_checks():
    lo,hi=pi_interval(100)
    prefix=Decimal('3.14159265358979323846264338327950288419716939937510')
    with localcontext(context(120)):
        need(prefix<lo<hi<prefix+Decimal('1e-50') and hi-lo<Decimal('1e-90'),
             'directed Chudnovsky interval inside known truncated50-digit pi bracket')
    tiny=bits(math.ldexp(1.,-1074))
    need(denominator((bits(0.),),0,1)==0 and denominator((tiny,),0,1)>0,'zero and minsubnormal angle distinguished')
    simple=make_case('hand-unity',[0.0],1,3)
    need(denominator(tuple(simple['angles_hex']),1,3)==1 and oracle_case(simple)['kind']==0,'hand-derived rational theta polynomial')
    model=dict(schema='native-vorbis-floor0-angles-cases-v1',cases=[simple])
    need(decode_input(encode_input(model))==model,'complete raw IEEE64 input roundtrip')
    return dict(pure_oracle_checks_only=True,component_executed=False,SDK_or_QEMU_executed=False)


def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path);parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--oracle-self-test',action='store_true');args=parser.parse_args()
    if args.oracle_self_test:print(json.dumps(self_checks()));return 0
    need(args.output is not None,'explicit fresh output');out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh task-local output')
    out.mkdir(parents=True);(out/'sources').mkdir();(out/'target-cases').mkdir()
    report=dict(completed=False,passed=False,prepared=False,component_executed=False,policy=POLICY,
        commands=[],sources={},full_floor0_qualified=False,full_G6_qualified=False,PCM_qualified=False,
        decoder_executed=False,SDK_or_QEMU_executed=False,physical_device=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path,name):
        data=path.read_bytes();(out/'sources'/name).write_bytes(data)
        report['sources'][str(path.resolve())]=dict(snapshot='sources/'+name,sha256=sha(data));return data
    def current():
        need(all(sha(Path(path).read_bytes())==pin['sha256']==sha((out/pin['snapshot']).read_bytes())
                 for path,pin in report['sources'].items()),'whole C/header/test source unchanged')
    save()
    try:
        freeze(Path(__file__),'test-vorbis-floor0-angles.py')
        source=freeze(COMPONENT/'floor0.c','floor0.c');freeze(COMPONENT/'include/native_vorbis_floor0.h','native_vorbis_floor0.h')
        freeze(DRIVER,'driver.c')
        owner=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-owner.py')
        nodes=[node for node in ast.parse(owner).body if isinstance(node,ast.Assign) and
               any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(nodes)==1,'one existing nonce-owned supervisor literal')
        (out/'supervisor.py').write_text(ast.literal_eval(nodes[0].value),encoding='utf-8',newline='\n')
        report['phase_table']=check_phase_table(source.decode());self_checks()
        model,target=cases();inputs=encode_input(model)
        need(decode_input(inputs)==model,'all complete original IEEE64 input records')
        (out/'cases.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8')
        (out/'inputs.bin').write_bytes(inputs)
        expected=dict(schema='native-vorbis-floor0-angles-expected-v1',policy=POLICY,
                      cases=[oracle_case(row) for row in target['cases']])
        directory=out/'target-cases'
        (directory/'cases.json').write_text(json.dumps(target,indent=2)+'\n',encoding='utf-8')
        (directory/'cases.h').write_text(target_header(target),encoding='ascii',newline='\n')
        (directory/'expected.json').write_text(json.dumps(expected,indent=2)+'\n',encoding='utf-8')
        report.update(prepared=True,cases=len(model['cases']),target_cases=len(target['cases']),
            input_sha256=sha(inputs),model_sha256=sha((out/'cases.json').read_bytes()),
            target_input_sha256={name:sha((directory/name).read_bytes()) for name in ('cases.json','cases.h','expected.json')})
        current();save()
        if args.prepare_only:
            print(json.dumps(dict(prepared=True,passed=False,component_executed=False,cases=report['cases'],
                                  target_cases=report['target_cases'])));return 0
        def run(name,argv):
            nonce=uuid.uuid4().hex;request=out/(name+'.request.json');receipt=out/(name+'.receipt.json');stop=out/(name+'.stop')
            request.write_text(json.dumps(dict(nonce=nonce,argv=argv,timeout=60,receipt=host(receipt),stop=host(stop))),encoding='utf-8')
            command=(['wsl.exe','--exec','python3'] if sys.platform=='win32' else [sys.executable])+[host(out/'supervisor.py'),host(request)]
            entry=dict(name=name,argv=command,child_argv=argv,nonce=nonce);report['commands'].append(entry);save()
            child=None;error=None;start=time.monotonic();stdout=out/(name+'.stdout.log');stderr=out/(name+'.stderr.log')
            try:
                with stdout.open('xb') as so,stderr.open('xb') as se:
                    child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=so,stderr=se,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                    entry['transport_pid']=child.pid;save();child.wait(timeout=80)
            except BaseException as exc:error=exc
            finally:
                if child is not None and child.poll() is None:
                    stop.write_text(nonce,encoding='utf-8')
                    try:child.wait(timeout=15)
                    except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);entry['forced_transport_stop']=True
                actual=json.loads(receipt.read_bytes()) if receipt.exists() else {}
                entry.update(supervisor=actual,transport_returncode=None if child is None else child.poll(),
                    elapsed_seconds=time.monotonic()-start,stdout_sha256=sha(stdout.read_bytes()) if stdout.exists() else None,
                    stderr_sha256=sha(stderr.read_bytes()) if stderr.exists() else None);save()
            need(actual.get('nonce')==nonce and actual.get('request_sha256')==sha(request.read_bytes()) and
                 all(actual.get(key) is True for key in ('final','new_session','child_reaped','group_gone')) and
                 actual.get('state')=='terminal' and actual.get('child_returncode')==0 and entry['transport_returncode']==0 and
                 not entry.get('forced_transport_stop') and 'cleanup_error' not in actual,'owned child terminal/cleanup '+name)
            if error is not None:raise error
            return stdout.read_bytes(),stderr.read_bytes()
        run('compiler-version',['gcc','--version']);run('compiler-machine',['gcc','-dumpmachine'])
        flags=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pedantic','-fno-fast-math',
               '-ffp-contract=off','-fsanitize=address,undefined','-fno-sanitize-recover=all',
               '-fno-omit-frame-pointer','-fno-pie','-no-pie']
        so,se=run('compile',flags+['-I'+host(out/'sources'),host(out/'sources/driver.c'),host(out/'sources/floor0.c'),
                                 '-lm','-o',host(out/'test')])
        need(not so and not se,'strict clean whole-module compile');current()
        so,se=run('execute',[host(out/'test'),host(out/'inputs.bin'),host(out/'outputs.bin')])
        report['component_executed']=True;need(not so and not se,'clean actual sanitized original-angle run')
        output=(out/'outputs.bin').read_bytes();decoded=decode_output(output,model)
        measured=compare_all(model,decoded['rows']);current()
        need(sha((out/'inputs.bin').read_bytes())==report['input_sha256'],'binary inputs unchanged')
        report.update(completed=True,passed=measured['passed'],source_inputs_unchanged=True,
            numerical=measured,metadata_controls=decoded['metadata_controls'],output_sha256=sha(output),
            result='FINITE_ANGLES_NUMERIC_QUALIFIED' if measured['passed'] else 'FINITE_ANGLES_NUMERIC_REJECTED')
        save();print(json.dumps(dict(completed=True,passed=report['passed'],cases=report['cases'],
            target_cases=report['target_cases'],result=report['result'],
            max_denominator_relative_error=measured['max_denominator_relative_error'],
            max_gain_absolute_error=measured['max_gain_absolute_error'],
            max_gain_relative_error_including_near_zero=measured['max_gain_relative_error_including_near_zero'])))
        return 0 if report['passed'] else 1
    except BaseException as error:
        report.update(completed=False,passed=False,error=repr(error));save();raise


if __name__=='__main__':sys.exit(main())
