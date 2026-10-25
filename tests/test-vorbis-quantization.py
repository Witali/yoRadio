"""Owned Vorbis quantization: exact packet/VQ oracle and independent affine-floor math.

Primary equations: Vorbis I 3.2, 6.2.2 and 9.2.2. Xiph v1.3.7
sharedbook.c/floor0.c/codebook.c confirm lookup, carry and final-prefix use.
No vendor decoder runs. Root owns actual compiler/SDK/QEMU executions.
"""
import argparse
import ast
from decimal import Context,Decimal,ROUND_CEILING,ROUND_FLOOR,localcontext
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

ROOT=Path(__file__).resolve().parents[1]
COMPONENT=ROOT/'idf/components/native_vorbis_numeric'
DRIVER=ROOT/'tests/native/vorbis_quantization_test.c'
AFFINE=('minimum_bits','delta_bits','minimum_multiplier','delta_multiplier')
LAYOUT=('dimensions','entries','lookup_type','minimum_bits','delta_bits','value_bits','sequence_p',
        'multiplicand_count','start_bit','multiplicand_bit','end_bit')
OPS={'vector':1,'floor':2,'affine':3,'scalar':4}
POLICY=dict(schema='native-vorbis-quantization-policy-v1',exact_symbolic_comparison=True,
    packed_float_equation='signed mantissa21 * 2^(exponent10-788)',
    floor_oracle='Exact Fraction angles; independent Chudnovsky pi and direct Decimal cosine P/Q',
    minimum_decimal_precision=1440,stored_scaled_precision=120,denominator_relative_bound='2e-12',
    gain_abs_relative_bound='2e-12',literal_db_coefficient='0.11512925',selected_before_measurement=True,
    threshold_fitted_to_output=False,decoder_or_PCM_qualification=False)

def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(data):return hashlib.sha256(data).hexdigest()
def context(precision=1440,rounding=None):
    args=dict(prec=precision,Emax=1000000,Emin=-1000000)
    if rounding is not None:args['rounding']=rounding
    return Context(**args)
def number(value):
    need(isinstance(value,str) and re.fullmatch('[0-9a-f]{16}',value),'exact binary64 bits')
    return struct.unpack('>d',bytes.fromhex(value))[0]
def unpack(word):
    need(type(word)is int and 0<=word<=0xffffffff,'complete packed word')
    mantissa=word&0x1fffff;exponent=((word>>21)&1023)-788
    if word&0x80000000:mantissa=-mantissa
    return Fraction(mantissa*(1<<exponent),1) if exponent>=0 else Fraction(mantissa,1<<-exponent)
def affine_value(value):return unpack(value['minimum_bits'])*value['minimum_multiplier']+unpack(value['delta_bits'])*value['delta_multiplier']
def integer_root(entries,dimensions):
    need(dimensions>0,'positive lookup1 dimension')
    lo,hi=0,1<<((entries.bit_length()+dimensions-1)//dimensions)
    while lo+1<hi:
        middle=(lo+hi)//2
        if middle**dimensions<=entries:lo=middle
        else:hi=middle
    return hi if hi**dimensions<=entries else lo

def packet(lookup,minimum,delta,width,sequence,values,start):
    bits=[(i*3+1)&1 for i in range(start)]
    def field(value,count):bits.extend((value>>i)&1 for i in range(count))
    field(lookup,4)
    if lookup:
        field(minimum,32);field(delta,32);field(width-1,4);field(sequence,1)
        for value in values:field(value,width)
    extent=len(bits);result=bytearray((extent+7)//8)
    for i,value in enumerate(bits):result[i//8]|=value<<(i%8)
    # Unused byte padding is deliberately nonzero, outside the declared extent.
    for i in range(extent,len(result)*8):result[i//8]|=1<<(i%8)
    return result.hex(),extent

def read_packet(case):
    data=bytes.fromhex(case['packet_hex']);extent=case['packet_bits'];at=case['start_bit']
    need(0<=at<=extent<=8*len(data),'declared complete packet bit extent')
    raw=int.from_bytes(data,'little')
    def field(width):
        nonlocal at
        need(at+width<=extent,'complete raw quantization field')
        value=(raw>>at)&((1<<width)-1);at+=width;return value
    lookup=field(4);need(lookup in (0,1,2),'public lookup type')
    minimum=delta=width=sequence=count=0;values=[]
    if lookup:
        minimum=field(32);delta=field(32);width=field(4)+1;sequence=field(1)
        count=integer_root(case['entries'],case['dimensions']) if lookup==1 else case['entries']*case['dimensions']
    multiplicand_bit=at
    if lookup:
        values=[field(width) for _ in range(count)]
    return dict(zip(LAYOUT,(case['dimensions'],case['entries'],lookup,minimum,delta,width,sequence,
                           count,case['start_bit'],multiplicand_bit,at))),values

def vector(layout,values,entry,prefix):
    need(0<=entry<layout['entries'] and 0<=prefix<=layout['dimensions'],'valid declared entry/prefix')
    output=[];last_min=last_delta=0;root=layout['multiplicand_count']
    for i in range(prefix):
        index=(entry//(root**i))%root if layout['lookup_type']==1 else entry*layout['dimensions']+i
        q=values[index]
        value=dict(minimum_bits=layout['minimum_bits'],delta_bits=layout['delta_bits'],
                   minimum_multiplier=1+last_min,delta_multiplier=q+last_delta)
        output.append(value)
        if layout['sequence_p']:last_min,last_delta=value['minimum_multiplier'],value['delta_multiplier']
    return output

def exact_case(case):
    if case['operation']=='affine':return dict(layout=None,multiplicands=[],values=case['affine'])
    layout,values=read_packet(case)
    if case['operation']=='vector':result=vector(layout,values,case['entry_numbers'][0],case['length'])
    elif case['operation']=='scalar':result=vector(layout,values,case['entry_numbers'][0],case['component']+1)[-1:]
    else:
        result=[];last_min=last_delta=0
        for entry in case['entry_numbers']:
            take=min(layout['dimensions'],case['length']-len(result))
            row=vector(layout,values,entry,take)
            for value in row:value['minimum_multiplier']+=last_min;value['delta_multiplier']+=last_delta
            result.extend(row)
            if row:last_min,last_delta=row[-1]['minimum_multiplier'],row[-1]['delta_multiplier']
        need(len(result)==case['length'],'whole floor0 prefix')
    return dict(layout=layout,multiplicands=values,values=result)

@lru_cache(maxsize=None)
def pi_interval(precision):
    floor,ceiling=context(precision,ROUND_FLOOR),context(precision,ROUND_CEILING)
    a,b,scale=13591409,545140134,262537412640768000
    need(2*1728*(a+b)<a*scale,'Chudnovsky global geometric tail bound')
    lo=hi=Decimal(0);m,l,x,k=1,a,1,6
    for index in range(precision//14+8):
        lo=floor.add(lo,floor.divide(Decimal(m*l),Decimal(x)))
        hi=ceiling.add(hi,ceiling.divide(Decimal(m*l),Decimal(x)))
        product=m*(k*k*k-16*k);divisor=(index+1)**3
        need(product%divisor==0,'exact Chudnovsky recurrence');m=product//divisor;l+=b;x*=-scale;k+=12
    tail=ceiling.multiply(Decimal(2),ceiling.divide(Decimal(abs(m*l)),Decimal(abs(x))))
    lo=floor.subtract(lo,tail);hi=ceiling.add(hi,tail)
    digits=precision+20;unit=10**digits;root=math.isqrt(10005*unit*unit);exact=context(precision+40)
    lower=Decimal(root).scaleb(-digits,context=exact);upper=Decimal(root+1).scaleb(-digits,context=exact)
    return floor.divide(floor.multiply(Decimal(426880),lower),hi),ceiling.divide(ceiling.multiply(Decimal(426880),upper),lo)
@lru_cache(maxsize=None)
def pi():
    lo,hi=pi_interval(1472)
    with localcontext(context(1440)):return (lo+hi)/2
@lru_cache(maxsize=None)
def cosine(value):
    with localcontext(context(1472)):
        x=Decimal(value.numerator)/Decimal(value.denominator);p=pi();x%=2*p
        if x>p:x-=2*p
        if x<-p:x+=2*p
        total=term=Decimal(1);square=x*x;i=1
        while True:
            term*=-square/Decimal((2*i-1)*(2*i));next_value=total+term
            if next_value==total:
                with localcontext(context(1440)):return +total
            total=next_value;i+=1
@lru_cache(maxsize=None)
def theta_cosine(bin_index,size):
    if not bin_index:return Decimal(1)
    if 2*bin_index==size:return Decimal(0)
    if 3*bin_index==size:return Decimal('.5')
    if 3*bin_index==2*size:return Decimal('-.5')
    with localcontext(context(1440)):
        x=pi()*bin_index/size;total=term=Decimal(1);square=x*x;i=1
        while True:
            term*=-square/Decimal((2*i-1)*(2*i));next_value=total+term
            if next_value==total:return +total
            total=next_value;i+=1

def scaled(value):
    with localcontext(context(120)):
        if not value:return dict(mantissa='0',exponent=0)
        exponent=int((abs(value).ln()/Decimal(2).ln()).to_integral_value(rounding=ROUND_FLOOR))+1
        mantissa=value/Decimal(2)**exponent
        while abs(mantissa)>=1:mantissa/=2;exponent+=1
        while abs(mantissa)<Decimal('.5'):mantissa*=2;exponent-=1
        return dict(mantissa=str(mantissa),exponent=exponent)
def expected_value(value):
    with localcontext(context(160)):return Decimal(value['mantissa'])*Decimal(2)**value['exponent']
def actual_value(bits_value,exponent):
    value=number(bits_value)
    need(math.isfinite(value) and type(exponent)is int and abs(exponent)<=1000000 and
         ((bits_value=='0000000000000000' and exponent==0) or .5<=abs(value)<1),'normalized finite actual scaled value')
    with localcontext(context(160)):return Decimal.from_float(value)*Decimal(2)**exponent

def floor_expected(case,affines):
    with localcontext(context(1440)):
        w=2*theta_cosine(case['bin'],case['map_size']);even=odd=Decimal(1)
        for i,value in enumerate(affines):
            factor=w-2*cosine(affine_value(value))
            if i%2:odd*=factor
            else:even*=factor
        d=(even*even+(4-w*w)*odd*odd)/4 if len(affines)%2 else ((2+w)*even*even+(2-w)*odd*odd)/4
        raw,bits_count,offset=int(case['raw_amplitude']),case['amplitude_bits'],case['amplitude_offset']
        if not raw:kind,gain=1,Decimal(0)
        elif not d:kind,gain=(2 if offset else 3),Decimal(0)
        else:kind,gain=0,(Decimal(raw)*offset/((1<<bits_count)-1)/d.sqrt()-offset)*Decimal('0.11512925')/Decimal(2).ln()
        return dict(kind=kind,denominator=scaled(d),log2_gain=scaled(gain),oracle_precision=1440)

def check_phase_table(source):
    arrays=re.findall(r'static const uint32_t floor0_two_over_pi\[PHASE_TABLE_WORDS\]\s*=\s*\{(.*?)\};',source,re.S)
    need(len(arrays)==1,'one owned phase table');words=[int(x,16) for x in re.findall(r'UINT32_C\(0x([0-9a-fA-F]{8})\)',arrays[0])]
    need(len(words)==128,'all128 new table limbs');lo,hi=pi_interval(1440)
    floor,ceiling=context(1440,ROUND_FLOOR),context(1440,ROUND_CEILING);scale=Decimal(1<<4096)
    left=int(floor.multiply(floor.divide(Decimal(2),hi),scale).to_integral_value(rounding=ROUND_FLOOR))
    right=int(ceiling.multiply(ceiling.divide(Decimal(2),lo),scale).to_integral_value(rounding=ROUND_FLOOR))
    need(left==right==sum(word<<(32*i) for i,word in enumerate(words)),'independent1440digit interval proves every4096bit limb')
    return dict(limbs=128,bits=4096,independent_interval_floor_unique=True,pi_lower=str(lo),pi_upper=str(hi))

def make_book(identifier,lookup=1,sequence=0,width=16,dimensions=3,entries=27,prefix=3,
              minimum=0x80000000,delta=0x62800001,start=0,operation='vector',q=None,bridge=False):
    count=integer_root(entries,dimensions) if lookup==1 else entries*dimensions
    if q is None:q=[(i*17+((1<<width)-1))&((1<<width)-1) for i in range(count)]
    body,extent=packet(lookup,minimum,delta,width,sequence,q,start)
    indexes=[entries-1] if operation=='vector' else [i%entries for i in range((prefix+dimensions-1)//dimensions)]
    return dict(id=identifier,operation=operation,dimensions=dimensions,entries=entries,start_bit=start,
        packet_bits=extent,packet_hex=body,entry_numbers=indexes,length=prefix,component=0,affine=[],bridge=bridge,
        bin=1,map_size=3,raw_amplitude='63',amplitude_bits=6,amplitude_offset=60)
def make_affine(identifier,values,bin_index=0,size=1,raw=63,width=6,offset=60):
    return dict(id=identifier,operation='affine',dimensions=0,entries=0,start_bit=0,packet_bits=0,
        packet_hex='',entry_numbers=[],length=len(values),component=0,affine=values,bridge=True,bin=bin_index,map_size=size,
        raw_amplitude=str(raw),amplitude_bits=width,amplitude_offset=offset)
def a(minimum,delta=0,m=1,q=0):return dict(zip(AFFINE,(minimum,delta,m,q)))
def cases():
    critical=[];floors=[];fields=[];direct=[]
    for lookup in (1,2):
        for sequence in (0,1):
            for width in range(1,17):
                for prefix in (0,1,3):
                    critical.append(make_book(f'book-{lookup}-{sequence}-{width}-{prefix}',lookup,sequence,width,
                        entries=27 if lookup==1 else 3,prefix=prefix,start=(width+prefix)%8))
    for lookup in (1,2):
        for sequence in (0,1):
            for dim in (1,2,3,4,7,255,256,65535):
                floors.append(make_book(f'floor-{lookup}-{sequence}-{dim}',lookup,sequence,16,dim,
                    3 if dim<255 else 1,255 if dim<255 else 3,operation='floor',start=7,
                    bridge=dim<8))
    for sign in (0,0x80000000):
        for exponent in range(1024):
            mantissa=(1,2,(1<<20)-1,1<<20,(1<<20)+1,(1<<21)-1)[exponent%6]
            word=sign|(exponent<<21)|mantissa
            fields.append(make_book(f'field-min-{sign>>31}-{exponent}',dimensions=1,entries=1,prefix=1,minimum=word,delta=0,q=[65535]))
            fields.append(make_book(f'field-delta-{sign>>31}-{exponent}',dimensions=1,entries=1,prefix=1,minimum=0,delta=word,q=[65535]))
            fields.append(make_book(f'field-zero-{sign>>31}-{exponent}',dimensions=1,entries=1,prefix=1,minimum=sign|(exponent<<21),delta=0,q=[65535]))
    for bit in range(32):fields.append(make_book(f'field-single-bit-{bit}',dimensions=1,entries=1,prefix=1,minimum=1<<bit,delta=(1<<bit)^0x80000000,q=[1]))
    # Remainder rows are ordinary base-root permutations; q0 deliberately nonzero.
    critical.append(make_book('lookup1-leftover-entry16',dimensions=2,entries=17,prefix=2,q=[7,3,5,1]))
    critical.append(make_book('full-dimension-sequence-sum',2,1,16,65535,1,65535,q=[65535]*65535))
    scalars=[]
    for sequence in (0,1):
        row=make_book(f'scalar-full-dimension-{sequence}',1,sequence,16,65535,1,1,q=[65535])
        row.update(operation='scalar',component=65534);scalars.append(row)
    for sign in (0,0x80000000):
        for exponent in (0,1,63,64,767,768,787,788,789,851,852,1022,1023):
            direct.append(make_affine(f'affine-field-{sign>>31}-{exponent}',[a(sign|(exponent<<21)|0x1fffff,0x62800001,0xffffffff,1)],1,65535))
    for shift in (0,1,20,100,235):
        positive=((shift+788)<<21)|1;negative=positive|0x80000000
        direct.append(make_affine(f'affine-cancel-{shift}',[a(negative,positive,0xffffffff,0xffffffff),a(1,0,1,0)],0,1))
        direct.append(make_affine(f'affine-two-scale-{shift}',[a(positive,1,1,1)],0,1))
    direct.extend([
        make_affine('affine-minimum-dyadic',[a(1)],0,1),make_affine('affine-negative-dyadic',[a(0x80000001)],0,1),
        make_affine('affine-signed-packed-zero',[a(0xffe00000,0x80000000,0xffffffff,0xffffffff)],0,1),
        make_affine('affine-zero-multipliers',[a(0x7fffffff,0xffffffff,0,0)],0,1),
        make_affine('affine-max-minus-one-amplitude',[a(0x62800001)],1,3,(1<<63)-2,63,255),
        make_affine('affine-absent-bits0',[a(1)],0,1,0,0,255),
        make_affine('affine-zero-offset-pole',[a(0)],0,1,1,1,0),
        make_affine('affine-positive-pole',[a(0)],0,1,1,1,255),
    ])
    rng=random.Random(0x51AFF1)
    while len(direct)<72:
        i=len(direct);order=(1,2,3,7,31,254,255)[i%7]
        values=[a(rng.getrandbits(32),rng.getrandbits(32),rng.getrandbits(32),rng.getrandbits(32)) for _ in range(order)]
        direct.append(make_affine(f'affine-random-{i}',values,i%17,17,(1<<63)-1,63,255))
    for i in range(96):
        dim=rng.choice((1,2,3,7,31));lookup=1 if i%2 else 2;entries=2 if lookup==2 else 1<<min(dim,8)
        critical.append(make_book(f'book-random-{i}',lookup,i%2,1+i%16,dim,entries,rng.randrange(dim+1),
            rng.getrandbits(32),rng.getrandbits(32),i%8))
    # Target captures remain compact; full65535 outputs are a host-only exact gate.
    target=critical[:190:2]+[row for row in floors if read_packet(row)[0]['multiplicand_count']<=255]+direct+scalars+[fields[6141],fields[3070],critical[192]]
    need(len(target)==200,'predeclared200 native cases')
    all_rows=critical+floors+fields+direct+scalars
    model=dict(schema='native-vorbis-quantization-cases-v1',cases=all_rows)
    target_model=dict(schema=model['schema'],cases=target)
    validate_model(model);validate_model(target_model);return model,target_model

def validate_model(model):
    need(model['schema']=='native-vorbis-quantization-cases-v1' and isinstance(model['cases'],list) and 1<=len(model['cases'])<=100000,'finite mixed corpus')
    ids=set();common={'id','operation','dimensions','entries','start_bit','packet_bits','packet_hex','entry_numbers','length','component','affine','bridge','bin','map_size','raw_amplitude','amplitude_bits','amplitude_offset'}
    for row in model['cases']:
        need(set(row)==common and isinstance(row['id'],str) and re.fullmatch('[A-Za-z0-9_-]{1,63}',row['id']) and row['id'] not in ids,'exact unique case fields/id');ids.add(row['id'])
        need(row['operation'] in OPS and type(row['bridge'])is bool and type(row['length'])is int and 0<=row['length']<=65535,'operation/length')
        need(all(type(row[k])is int for k in ('dimensions','entries','start_bit','packet_bits','component','bin','map_size','amplitude_bits','amplitude_offset')),'exact numeric field types')
        need(0<=row['component']<=65534 and (row['operation']=='scalar' or row['component']==0),'scalar component')
        need(0<=row['dimensions']<=65535 and 0<=row['entries']<=0xffffff and re.fullmatch('(?:[0-9a-f]{2})*',row['packet_hex']),'complete raw book data')
        need(isinstance(row['entry_numbers'],list) and all(type(x)is int and 0<=x<=0xffffffff for x in row['entry_numbers']),'uint32 entry list')
        need(isinstance(row['affine'],list) and all(set(value)==set(AFFINE) and all(type(value[k])is int and 0<=value[k]<=0xffffffff for k in AFFINE) for value in row['affine']),'complete original affine words/multipliers')
        need(isinstance(row['raw_amplitude'],str) and re.fullmatch('0|[1-9][0-9]*',row['raw_amplitude']) and 0<=row['amplitude_bits']<=63 and
             0<=int(row['raw_amplitude'])<(1<<row['amplitude_bits']) and 0<=row['amplitude_offset']<=255 and 1<=row['map_size']<=65535 and 0<=row['bin']<row['map_size'],'public amplitude/bin fields')
        if row['bridge']:need(1<=row['length']<=255,'bridge order')
        if row['operation']=='affine':need(row['dimensions']==row['entries']==row['start_bit']==row['packet_bits']==0 and not row['packet_hex'] and not row['entry_numbers'] and row['length']==len(row['affine']),'direct affine descriptor')
        else:
            need(row['dimensions']>0 and row['entries']>0 and not row['affine'],'valid VQ book')
            if row['operation']=='vector':need(len(row['entry_numbers'])==1 and row['length']<=row['dimensions'],'vector prefix')
            elif row['operation']=='scalar':need(len(row['entry_numbers'])==1 and row['length']==1 and row['component']<row['dimensions'],'scalar declared component')
            else:need(1<=row['length']<=255 and len(row['entry_numbers'])==(row['length']+row['dimensions']-1)//row['dimensions'],'floor prefix entries')
            need(all(x<row['entries'] for x in row['entry_numbers']),'declared entries');read_packet(row)
    return model['cases']

class Reader:
    def __init__(self,data):self.data,self.cursor=data,0
    def take(self,fmt):
        size=struct.calcsize(fmt);need(self.cursor+size<=len(self.data),'complete binary field');values=struct.unpack_from(fmt,self.data,self.cursor);self.cursor+=size
        return values[0] if len(values)==1 else values
    def affine(self):return dict(zip(AFFINE,self.take('<IIII')))

def encode_input(model):
    data=bytearray(b'VQTEST01'+struct.pack('<I',len(validate_model(model))))
    for row in model['cases']:
        name=row['id'].encode();body=bytes.fromhex(row['packet_hex']);data+=struct.pack('<I',len(name))+name
        data+=struct.pack('<IIIQQI',OPS[row['operation']],row['dimensions'],row['entries'],row['packet_bits'],row['start_bit'],len(body))+body
        data+=struct.pack('<I',len(row['entry_numbers']))+b''.join(struct.pack('<I',x) for x in row['entry_numbers'])
        data+=struct.pack('<III',row['length'],row['component'],len(row['affine']))+b''.join(struct.pack('<IIII',*(x[k] for k in AFFINE)) for x in row['affine'])
        data+=struct.pack('<IQIIII',row['bridge'],int(row['raw_amplitude']),row['amplitude_bits'],row['amplitude_offset'],row['bin'],row['map_size'])
    return bytes(data)
def decode_input(data):
    reader=Reader(data);need(reader.take('<8s')==b'VQTEST01','input magic');count=reader.take('<I');need(1<=count<=100000,'finite binary count');rows=[]
    for _ in range(count):
        n=reader.take('<I');need(1<=n<=63,'bounded id');name=reader.take('<'+str(n)+'s').decode('ascii')
        op,dim,total,extent,start,n=reader.take('<IIIQQI');need(op in OPS.values() and n<=131100,'binary operation/packet');body=reader.take('<'+str(n)+'s')
        n=reader.take('<I');need(n<=255,'finite entry count');entries=[reader.take('<I') for _ in range(n)]
        length,component,n=reader.take('<III');need(n<=255,'finite direct affine count');values=[reader.affine() for _ in range(n)]
        bridge,raw,width,offset,bin_index,size=reader.take('<IQIIII');need(bridge in (0,1),'bridge flag')
        rows.append(dict(id=name,operation=next(k for k,v in OPS.items() if v==op),dimensions=dim,entries=total,start_bit=start,packet_bits=extent,packet_hex=body.hex(),entry_numbers=entries,length=length,component=component,affine=values,bridge=bool(bridge),bin=bin_index,map_size=size,raw_amplitude=str(raw),amplitude_bits=width,amplitude_offset=offset))
    need(reader.cursor==len(data),'exact complete input bytes');model=dict(schema='native-vorbis-quantization-cases-v1',cases=rows);validate_model(model);return model

def decode_output(data,model):
    cases_rows=validate_model(model);r=Reader(data);need(r.take('<8s')==b'VQOUT001' and r.take('<I')==len(cases_rows),'complete output header');controls=r.take('<I');need(controls==152,'all152 actual API controls');rows=[]
    for i,case in enumerate(cases_rows):
        need(r.take('<I')==i,'ordered output index');ms,mt,vs=r.take('<iii');layout=dict(zip(LAYOUT,r.take('<IIIIIIIQQQQ')))
        n=r.take('<I');need(n<=65535,'captured storage count');multiplicands=[r.take('<H') for _ in range(n)]
        n=r.take('<I');need(n==case['length'],'captured output count');values=[r.affine() for _ in range(n)]
        ds,gs,kind,db,de,gb,ge=r.take('<iiiQiQi');need(r.take('<I')==7,'actual input/canary/consistency guards')
        if case['operation']=='affine':need(not any(layout.values()),'unused direct layout zero');layout=None
        rows.append(dict(case=i,id=case['id'],operation=case['operation'],measure_status=ms,materialize_status=mt,decode_status=vs,layout=layout,multiplicands=multiplicands,values=values,ds=ds,gs=gs,kind=kind,denominator_bits=f'{db:016x}',denominator_exponent=de,log2_bits=f'{gb:016x}',log2_exponent=ge,guards=1,unchanged=1))
    need(r.cursor==len(data),'whole output bytes');return dict(metadata_controls=controls,rows=rows)

def expected_case(case):
    exact=exact_case(case)
    return dict(id=case['id'],exact=exact,numerical=floor_expected(case,exact['values']) if case['bridge'] else None)
def compare_case(case,row,expected=None):
    expected=expected or expected_case(case);wanted=expected['exact'];reasons=[]
    for key in ('layout','multiplicands','values'):
        if row[key]!=wanted[key]:reasons.append('exact '+key)
    status=-99 if case['operation']=='affine' else 0
    if any(row[k]!=status for k in ('measure_status','materialize_status','decode_status')):reasons.append('book operation status')
    metric=dict(id=case['id'],qualified=False,failure_reasons=reasons,exact_values=len(wanted['values']),exact_multiplicands=len(wanted['multiplicands']),expected_exact_sha256=sha(json.dumps(wanted,sort_keys=True).encode()),actual_exact_sha256=sha(json.dumps({k:row[k] for k in ('layout','multiplicands','values')},sort_keys=True).encode()))
    if case['bridge']:
        need(row['ds']==row['gs']==0,'bridge numerical values available')
        with localcontext(context(160)):
            d=actual_value(row['denominator_bits'],row['denominator_exponent']);g=actual_value(row['log2_bits'],row['log2_exponent'])
            wd=expected_value(expected['numerical']['denominator']);wg=expected_value(expected['numerical']['log2_gain']);de,ge=abs(d-wd),abs(g-wg)
            if (de/wd>Decimal('2e-12') if wd else d!=0):reasons.append('affine denominator bound')
            if ge>Decimal('2e-12')*max(Decimal(1),abs(wg)):reasons.append('affine gain bound')
            if row['kind']!=expected['numerical']['kind']:reasons.append('affine floor kind')
            metric.update(denominator_relative_error=str(de/wd) if wd else None,denominator_absolute_error=str(de),gain_absolute_error=str(ge),gain_relative_error=str(ge/abs(wg)) if wg else None,expected_numerical=expected['numerical'],actual_numerical={key:row[key] for key in ('ds','gs','kind','denominator_bits','denominator_exponent','log2_bits','log2_exponent')})
    else:
        if not(row['ds']==row['gs']==row['kind']==-99 and row['denominator_bits']==row['log2_bits']=='0000000000000000' and row['denominator_exponent']==row['log2_exponent']==0):reasons.append('unused bridge fields')
    metric['qualified']=not reasons
    if reasons:metric.update(actual=row,expected=expected)
    return metric

def compare_all(model,observed,expected=None):
    rows=validate_model(model);need(len(rows)==len(observed),'whole quantization comparison')
    if expected is not None:need(expected['schema']=='native-vorbis-quantization-expected-v1' and expected['policy']==POLICY and len(expected['cases'])==len(rows),'predeclared exact/numerical policy')
    metrics=[];failures=[]
    for i,(case,row) in enumerate(zip(rows,observed)):
        try:
            need(row['case']==i and row['id']==case['id'] and row['operation']==case['operation'] and row['guards']==row['unchanged']==1,'original complete case identity/guards')
            wanted=expected_case(case)
            if expected is not None:need(wanted==expected['cases'][i],'all regenerated original expected values')
            metric=compare_case(case,row,wanted);metrics.append(metric)
            if not metric['qualified']:failures.append(dict(index=i,**metric))
        except (ValueError,KeyError,TypeError) as error:failures.append(dict(index=i,id=case['id'],nonmeasurement_error=str(error),actual=row))
    def maximum(key):return str(max((Decimal(row[key]) for row in metrics if row.get(key)is not None),default=Decimal(0)))
    return dict(measurement_completed=len(metrics)==len(rows),passed=not failures and len(metrics)==len(rows),cases=len(rows),metrics=metrics,failures=failures,
        exact_values=sum(row['exact_values'] for row in metrics),exact_multiplicands=sum(row['exact_multiplicands'] for row in metrics),numerical_cases=sum('gain_absolute_error'in row for row in metrics),max_denominator_relative_error=maximum('denominator_relative_error'),max_gain_absolute_error=maximum('gain_absolute_error'),max_gain_relative_error_including_near_zero=maximum('gain_relative_error'))
def compare_target_rows(model,expected,observed):return compare_all(model,observed,expected)

def target_header(model):
    rows=validate_model(model)
    lines=['#pragma once','#include <stddef.h>','#include <stdint.h>','#include "native_vorbis_quant.h"',
        '#define QUANTIZATION_CASE_COUNT '+str(len(rows)),
        'typedef struct { const char *id; uint32_t operation,dimensions,entries; uint64_t packet_bits,start_bit;',
        ' const uint8_t *packet; uint32_t packet_bytes; const uint32_t *entry_numbers; uint32_t entry_count,length,component;',
        ' const native_vorbis_affine_t *affine; uint32_t affine_count,bridge,bin,map_size; uint64_t raw_amplitude;',
        ' uint32_t amplitude_bits,amplitude_offset; } quantization_case_t;']
    for i,row in enumerate(rows):
        body=bytes.fromhex(row['packet_hex'])
        if body:lines.append('static const uint8_t quant_packet_'+str(i)+'[] = {'+','.join('UINT8_C(0x'+f'{x:02x}'+')' for x in body)+'};')
        if row['entry_numbers']:lines.append('static const uint32_t quant_entries_'+str(i)+'[] = {'+','.join('UINT32_C('+str(x)+')' for x in row['entry_numbers'])+'};')
        if row['affine']:lines.append('static const native_vorbis_affine_t quant_affine_'+str(i)+'[] = {'+','.join('{'+','.join('UINT32_C('+str(value[k])+')' for k in AFFINE)+'}' for value in row['affine'])+'};')
    lines.append('static const quantization_case_t quantization_cases[QUANTIZATION_CASE_COUNT] = {')
    for i,row in enumerate(rows):
        body=bytes.fromhex(row['packet_hex'])
        fields=['"'+row['id']+'"',str(OPS[row['operation']]),str(row['dimensions']),str(row['entries']),
            'UINT64_C('+str(row['packet_bits'])+')','UINT64_C('+str(row['start_bit'])+')',
            'quant_packet_'+str(i) if body else 'NULL',str(len(body)),
            'quant_entries_'+str(i) if row['entry_numbers'] else 'NULL',str(len(row['entry_numbers'])),str(row['length']),str(row['component']),
            'quant_affine_'+str(i) if row['affine'] else 'NULL',str(len(row['affine'])),str(int(row['bridge'])),str(row['bin']),str(row['map_size']),
            'UINT64_C('+row['raw_amplitude']+')',str(row['amplitude_bits']),str(row['amplitude_offset'])]
        lines.append('    {'+','.join(fields)+'},')
    return '\n'.join(lines+['};',''])

def self_checks():
    need(unpack(1)==Fraction(1,1<<788) and unpack(0x80000001)==-Fraction(1,1<<788),'full packed negative exponent')
    need(unpack(0x7fffffff)==Fraction(((1<<21)-1)*(1<<235)),'full packed positive exponent')
    need(all(unpack(sign|(exp<<21))==0 for sign in (0,0x80000000) for exp in range(1024)),'all signed/exponent zero words')
    need(integer_root(2,65535)==1 and integer_root(17,2)==4 and integer_root(0xffffff,1)==0xffffff,'independent exact roots')
    need(packet(1,0,0,1,0,[1],0)==('010000000000000000fe',74),'independent literal bitpacking witness with one-filled unused padding')
    need(affine_value(a(0xffffffff,0x7fffffff,0xffffffff,0xffffffff))==0,'exact cancellation before cosine')
    need(((1<<21)-1)*0xffffffff<1<<53,'every raw term exactly representable in binary64')
    lo,hi=pi_interval(1440);need(str(lo).startswith('3.14159265358979323846264338327950288419716939937510') and lo<hi,'directed independent pi interval')
    return dict(passed=True,packed_zero_patterns=2048,minimum_decimal_precision=1440,oracle_only=True,component_executed=False)

def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    parser.add_argument('--prepare-only',action='store_true');parser.add_argument('--oracle-self-test',action='store_true');args=parser.parse_args()
    if args.oracle_self_test:print(json.dumps(self_checks()));return 0
    need(args.output is not None,'explicit fresh output');out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh task-local output')
    out.mkdir(parents=True);(out/'sources').mkdir();(out/'target-cases').mkdir()
    report=dict(completed=False,passed=False,prepared=False,component_executed=False,policy=POLICY,commands=[],sources={},
        full_floor0_qualified=False,full_G6_qualified=False,PCM_qualified=False,decoder_executed=False,SDK_or_QEMU_executed=False,physical_device=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path,name):
        data=path.read_bytes();(out/'sources'/name).write_bytes(data);report['sources'][str(path.resolve())]=dict(snapshot='sources/'+name,sha256=sha(data));return data
    def current():
        need(all(sha(Path(path).read_bytes())==pin['sha256']==sha((out/pin['snapshot']).read_bytes()) for path,pin in report['sources'].items()),'whole actual C/header/test sources unchanged')
        if report.get('prepared'):
            need(sha((out/'cases.json').read_bytes())==report['model_sha256'] and sha((out/'inputs.bin').read_bytes())==report['input_sha256'],'model/input immutable')
            need(all(sha((out/'target-cases'/name).read_bytes())==digest for name,digest in report['target_input_sha256'].items()),'target model/header/expected immutable')
    save()
    try:
        freeze(Path(__file__),'test-vorbis-quantization.py');source=freeze(COMPONENT/'floor0.c','floor0.c')
        freeze(COMPONENT/'quant.c','quant.c');freeze(COMPONENT/'include/native_vorbis_floor0.h','native_vorbis_floor0.h')
        freeze(COMPONENT/'include/native_vorbis_quant.h','native_vorbis_quant.h');freeze(COMPONENT/'CMakeLists.txt','CMakeLists.txt');freeze(DRIVER,'driver.c')
        owner=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-owner.py')
        nodes=[node for node in ast.parse(owner).body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(nodes)==1,'one existing nonce-owned supervisor literal');(out/'supervisor.py').write_text(ast.literal_eval(nodes[0].value),encoding='utf-8',newline='\n')
        report['phase_table']=check_phase_table(source.decode());report['oracle_self_checks']=self_checks()
        model,target=cases();inputs=encode_input(model);need(decode_input(inputs)==model,'complete exact raw packet/affine input roundtrip')
        (out/'cases.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');(out/'inputs.bin').write_bytes(inputs)
        directory=out/'target-cases';expected=dict(schema='native-vorbis-quantization-expected-v1',policy=POLICY,cases=[expected_case(row) for row in target['cases']])
        (directory/'cases.json').write_text(json.dumps(target,indent=2)+'\n',encoding='utf-8');(directory/'cases.h').write_text(target_header(target),encoding='ascii',newline='\n')
        (directory/'expected.json').write_text(json.dumps(expected,indent=2)+'\n',encoding='utf-8')
        report.update(prepared=True,cases=len(model['cases']),target_cases=len(target['cases']),input_sha256=sha(inputs),model_sha256=sha((out/'cases.json').read_bytes()),
            target_input_sha256={name:sha((directory/name).read_bytes()) for name in ('cases.json','cases.h','expected.json')})
        current();save()
        if args.prepare_only:print(json.dumps(dict(prepared=True,passed=False,component_executed=False,cases=report['cases'],target_cases=report['target_cases'])));return 0
        def run(name,argv):
            nonce=uuid.uuid4().hex;request=out/(name+'.request.json');receipt=out/(name+'.receipt.json');stop=out/(name+'.stop')
            request.write_text(json.dumps(dict(nonce=nonce,argv=argv,timeout=60,receipt=host(receipt),stop=host(stop))),encoding='utf-8')
            command=(['wsl.exe','--exec','python3'] if sys.platform=='win32' else [sys.executable])+[host(out/'supervisor.py'),host(request)]
            entry=dict(name=name,argv=command,child_argv=argv,nonce=nonce);report['commands'].append(entry);save()
            child=None;error=None;start=time.monotonic();stdout=out/(name+'.stdout.log');stderr=out/(name+'.stderr.log')
            try:
                with stdout.open('xb') as so,stderr.open('xb') as se:
                    child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=so,stderr=se,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                    entry['transport_pid']=child.pid;save();child.wait(timeout=80)
            except BaseException as exc:error=exc
            finally:
                if child is not None and child.poll() is None:
                    stop.write_text(nonce,encoding='utf-8')
                    try:child.wait(timeout=15)
                    except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);entry['forced_transport_stop']=True
                actual=json.loads(receipt.read_bytes()) if receipt.exists() else {}
                entry.update(supervisor=actual,transport_returncode=None if child is None else child.poll(),elapsed_seconds=time.monotonic()-start,
                    stdout_sha256=sha(stdout.read_bytes()) if stdout.exists() else None,stderr_sha256=sha(stderr.read_bytes()) if stderr.exists() else None);save()
            need(actual.get('nonce')==nonce and actual.get('request_sha256')==sha(request.read_bytes()) and all(actual.get(key)is True for key in ('final','new_session','child_reaped','group_gone')) and actual.get('state')=='terminal' and actual.get('child_returncode')==0 and entry['transport_returncode']==0 and not entry.get('forced_transport_stop') and 'cleanup_error' not in actual,'owned terminal/cleanup '+name)
            if error is not None:raise error
            return stdout.read_bytes(),stderr.read_bytes()
        run('compiler-version',['gcc','--version']);run('compiler-machine',['gcc','-dumpmachine'])
        flags=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pedantic','-fno-fast-math','-ffp-contract=off','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-fno-pie','-no-pie']
        so,se=run('compile',flags+['-I'+host(out/'sources'),host(out/'sources/driver.c'),host(out/'sources/floor0.c'),host(out/'sources/quant.c'),'-lm','-o',host(out/'test')])
        need(not so and not se,'clean strict whole-component compile');current()
        so,se=run('execute',[host(out/'test'),host(out/'inputs.bin'),host(out/'outputs.bin')]);report['component_executed']=True;need(not so and not se,'clean actual sanitized quantization execution')
        output=(out/'outputs.bin').read_bytes();decoded=decode_output(output,model);measured=compare_all(model,decoded['rows']);current()
        report.update(completed=True,passed=measured['passed'],source_inputs_unchanged=True,numerical=measured,metadata_controls=decoded['metadata_controls'],output_sha256=sha(output),
            result='EXACT_QUANTIZATION_AFFINE_NUMERIC_QUALIFIED' if measured['passed'] else 'EXACT_QUANTIZATION_AFFINE_NUMERIC_REJECTED')
        save();print(json.dumps(dict(completed=True,passed=report['passed'],cases=report['cases'],target_cases=report['target_cases'],result=report['result'],exact_values=measured['exact_values'],numerical_cases=measured['numerical_cases'],max_denominator_relative_error=measured['max_denominator_relative_error'],max_gain_absolute_error=measured['max_gain_absolute_error'],max_gain_relative_error_including_near_zero=measured['max_gain_relative_error_including_near_zero'])));return 0 if report['passed'] else 1
    except BaseException as error:report.update(completed=False,passed=False,error=repr(error));save();raise

if __name__=='__main__':sys.exit(main())
