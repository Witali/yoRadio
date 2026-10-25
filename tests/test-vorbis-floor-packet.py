"""Independent floor0/floor1 packet and integer-curve tests; no PCM claim.

Vorbis I6.2.2/7.2.3/7.2.4/9.2.6-7. Setup grammar reuses explicitly pinned
independent source definitions; production packet/prediction code is never read.
"""
import argparse
import ast
from functools import lru_cache
import hashlib
import importlib.util
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
DRIVER=ROOT/'tests/native/vorbis_floor_packet_test.c'
REFERENCE_PATH=ROOT/'tests/test-vorbis-setup.py'
REFERENCE_SHA='ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff'
REFERENCE=None
CONTROL_COUNT=46
OPS={'packet':1,'raw':2}
AFFINE=('minimum_bits','delta_bits','minimum_multiplier','delta_multiplier')
PREFIX=('mode','blockflag','previous_window','next_window','mapping','blocksize')
POLICY=dict(schema='native-vorbis-floor-packet-policy-v1',exact_packet_and_integer_comparison=True,
    floor0_selector='bit_length(book_count)',floor_EOP='OK UNUSED; last complete field/word cursor; arrays unchanged',
    invalid_or_capacity='Whole floor state/arrays/cursor preserved',floor1_clamp='After complete original-order prediction',
    curve_oracle='Closed rational per-bin sign*floor(abs(dy)*offset/span)',host_each_floor_cut_is_a_model_row=True,
    setup_cut_campaign_repeated=False,general_floor0_gain_reference_compared=False,selected_before_measurement=True,
    full_floor0_or_G6_or_PCM_qualified=False)
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(body):return hashlib.sha256(body).hexdigest()
def ref():need(REFERENCE is not None,'explicit frozen independent setup reference required');return REFERENCE
def load_reference(path):
    need(sha(path.read_bytes())==REFERENCE_SHA,'reviewed setup reference source')
    spec=importlib.util.spec_from_file_location('floor_packet_setup_reference',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
@lru_cache(maxsize=None)
def context(info_hex,info_bits,setup_hex,setup_bits):
    r=ref();identity=r.identification(bytes.fromhex(info_hex),info_bits);setup=r.parse_setup(bytes.fromhex(setup_hex),setup_bits,identity)
    return setup,sha(json.dumps(setup,sort_keys=True).encode())
def floor_info(ctx,index):
    layout=ctx['layout'];need(0<=index<layout['floor_count'],'selected configured floor');pool=ctx['configuration'];at=pool[layout['floor_table']+index];kind=pool[at]
    if kind==0:
        order,rate,bark,bits,offset,count=pool[at+1:at+7]
        return dict(type=0,order=order,rate=rate,bark=bark,bits=bits,offset=offset,books=pool[at+7:at+7+count])
    p,c,m,b,n=pool[at+1:at+6];partitions=pool[at+6:at+6+p];offsets=pool[at+6+p:at+6+p+c];x=pool[at+6+p+c:at+6+p+c+n];classes=[]
    for pos in offsets:
        dim,sub,master=pool[pos:pos+3];classes.append(dict(dimensions=dim,subclass_bits=sub,masterbook=master,books=pool[pos+3:pos+3+(1<<sub)]))
    return dict(type=1,partitions=partitions,classes=classes,multiplier=m,x=x)
def decode_word(book,reader):
    r=ref();start=reader.position;words=book['words']
    if not words:raise r.Invalid('active empty entropy book')
    try:
        if len(words)==1:reader.take(1);return words[0]['entry']
        path=0;lookup={(w['code'],w['length']):w['entry']for w in words}
        for length in range(1,33):
            path|=reader.take(1)<<(32-length)
            if(path,length)in lookup:return lookup[(path,length)]
    except r.Truncated:reader.position=start;raise
    raise r.Invalid('no entropy codeword')
def vector(book,entry,prefix):
    q=book['layout']['quantization'];need(q['lookup_type']in(1,2)and q['dimensions']>0,'positive VQ dimensions')
    result=[];minimum=delta=0
    for i in range(prefix):
        index=(entry//q['multiplicand_count']**i)%q['multiplicand_count']if q['lookup_type']==1 else entry*q['dimensions']+i
        if q['sequence_p']:minimum+=1;delta+=book['multiplicands'][index]
        else:minimum=1;delta=book['multiplicands'][index]
        result.append(dict(zip(AFFINE,(q['minimum_bits'],q['delta_bits'],minimum,delta))))
    return result

def reconstruct(floor,raw):
    x=floor['x'];limit=(256,128,86,64)[floor['multiplier']-1];need(len(raw)==len(x)and all(type(v)is int and 0<=v<=0xffffffff for v in raw),'full raw unsigned scalar inputs')
    values=list(raw);active=[1,1]+[0]*(len(x)-2)
    for i in range(2,len(x)):
        low=max((j for j in range(i)if x[j]<x[i]),key=lambda j:x[j]);high=min((j for j in range(i)if x[j]>x[i]),key=lambda j:x[j])
        dy=values[high]-values[low];offset=abs(dy)*(x[i]-x[low])//(x[high]-x[low]);predicted=values[low]+(-offset if dy<0 else offset)
        val=raw[i];highroom,lowroom=limit-predicted,predicted;room=2*min(highroom,lowroom)
        if val:
            active[i]=active[low]=active[high]=1
            if val>=room:values[i]=val-lowroom+predicted if highroom>lowroom else predicted-val+highroom-1
            elif val&1:values[i]=predicted-(val+1)//2
            else:values[i]=predicted+val//2
        else:values[i]=predicted
    return [min(limit-1,max(0,v))for v in values],active

def curve(floor,final,active,bins):
    need(1<=bins<=4096 and len(final)==len(active)==len(floor['x'])and active[0]==active[1]==1,'present floor curve metadata')
    points=sorted((x,final[i]*floor['multiplier'])for i,x in enumerate(floor['x'])if active[i]);result=[];segment=0
    for x in range(bins):
        while segment+1<len(points)and x>=points[segment+1][0]:segment+=1
        if segment+1==len(points):value=points[segment][1]
        else:
            x0,y0=points[segment];x1,y1=points[segment+1];dy=y1-y0;off=abs(dy)*(x-x0)//(x1-x0);value=y0+(-off if dy<0 else off)
        need(0<=value<=255,'inverse dB table index');result.append(value)
    return result

def expected_case(case):
    r=ref();ctx,pin=context(case['identification_hex'],case['identification_bits'],case['setup_hex'],case['setup_bits']);floor=floor_info(ctx,case['floor_index']);reader=r.Bits(bytes.fromhex(case['packet_hex']),case['packet_bits'],case['start_bit'])
    exact=dict(prefix_status=-99,prefix=None,floor_status=-99,state=None,coefficients=[],raw_y=[],reconstruct_status=-99,final_y=[],active=[],curve_status=-99,indices=[],gain_status=-99,position=case['start_bit'],end_of_packet=False)
    gain_rule='not_called'
    if case['operation']=='raw':
        need(floor['type']==1,'raw reconstruction floor1 only');raw=case['raw_y'];final,flags=reconstruct(floor,raw)
        exact.update(raw_y=list(raw),reconstruct_status=0,final_y=final,active=flags,curve_status=0,indices=curve(floor,final,flags,case['curve_n']))
    else:
        try:
            need(reader.take(1)==0,'audio type0');mode=reader.take((ctx['layout']['mode_count']-1).bit_length());need(mode<ctx['layout']['mode_count'],'audio mode range');mode_info=ctx['modes'][mode];block=mode_info['blockflag'];previous,next_flag=(reader.take(1),reader.take(1))if block else(0,0)
        except r.Truncated:exact.update(prefix_status=-3,end_of_packet=True);return dict(id=case['id'],exact=exact,gain_rule=gain_rule)
        except ValueError:exact.update(prefix_status=-1);return dict(id=case['id'],exact=exact,gain_rule=gain_rule)
        identity=ctx['layout']['identification'];exact.update(prefix_status=0,prefix=dict(zip(PREFIX,(mode,block,previous,next_flag,mode_info['mapping'],identity['blocksize_1'if block else'blocksize_0']))));floor_start=reader.position
        state=dict(floor_index=case['floor_index'],type=floor['type'],present=0,value_count=0,selected_book=0xffffffff,
            amplitude=dict(raw_amplitude='0',amplitude_bits=floor['bits']if floor['type']==0 else 0,amplitude_offset=floor['offset']if floor['type']==0 else 0))
        coeff=[];raw=[]
        try:
            if floor['type']==0:
                amp=reader.take(floor['bits']);state['amplitude']['raw_amplitude']=str(amp)
                if amp:
                    selector=reader.take(len(floor['books']).bit_length());need(selector<len(floor['books']),'floor0 selector range');book_id=floor['books'][selector];state['selected_book']=book_id;book=ctx['books'][book_id];dim=book['layout']['quantization']['dimensions'];carry_min=carry_delta=0
                    while True:
                        entry=decode_word(book,reader);take=min(dim,floor['order']-len(coeff));current=vector(book,entry,take)
                        for value in current:value['minimum_multiplier']+=carry_min;value['delta_multiplier']+=carry_delta
                        coeff+=current
                        if current:carry_min,carry_delta=current[-1]['minimum_multiplier'],current[-1]['delta_multiplier']
                        if len(coeff)>=floor['order']:break
                    state.update(present=1,value_count=len(coeff))
            else:
                if reader.take(1):
                    limit=(256,128,86,64)[floor['multiplier']-1];width=(limit-1).bit_length();raw=[reader.take(width),reader.take(width)]
                    for cls_id in floor['partitions']:
                        cls=floor['classes'][cls_id];sub=cls['subclass_bits'];word=decode_word(ctx['books'][cls['masterbook']],reader)if sub else 0;mask=(1<<sub)-1
                        for _ in range(cls['dimensions']):
                            book=cls['books'][word&mask];word>>=sub;raw.append(0 if book==0xffffffff else decode_word(ctx['books'][book],reader))
                    state.update(present=1,value_count=len(raw))
        except r.Truncated:coeff=[];raw=[];state.update(present=0,value_count=0);exact['end_of_packet']=True
        except ValueError:
            exact.update(floor_status=-1,position=floor_start);need(sha(json.dumps(ctx,sort_keys=True).encode())==pin,'cached setup reference remains immutable');return dict(id=case['id'],exact=exact,gain_rule=gain_rule)
        exact.update(floor_status=0,state=state,coefficients=coeff,raw_y=raw,position=reader.position)
        if floor['type']==1 and state['present']:
            final,flags=reconstruct(floor,raw);exact.update(reconstruct_status=0,final_y=final,active=flags,curve_status=0,indices=curve(floor,final,flags,case['curve_n']))
        if floor['type']==0:
            if not state['present']:exact['gain_status']=0;gain_rule='absent'
            elif not floor['rate']or not floor['bark']:exact['gain_status']=-1;gain_rule='invalid'
            else:
                exact['gain_status']=0;gain_rule='unity'if floor['order']==0 and (int(state['amplitude']['raw_amplitude'])==(1<<floor['bits'])-1 or floor['offset']==0)else'composition_only'
    need(sha(json.dumps(ctx,sort_keys=True).encode())==pin,'cached setup reference remains immutable')
    return dict(id=case['id'],exact=exact,gain_rule=gain_rule)

# Fixture construction is independent of production packet traversal.
def put_word(writer,lengths,entry,singleton_bit=0):
    words=ref().greedy_words(lengths);word=next(word for word in words if word['entry']==entry)
    if len(words)==1:writer.put(singleton_bit,1)
    else:
        for i in range(word['length']):writer.put((word['code']>>(31-i))&1,1)
def floor1_spec(multiplier=1,x=(),range_bits=4,subclass_bits=0,missing=False,empty=False):
    spec=ref().baseline();spec['books']=[dict(dimensions=1,lengths=[0]if empty else[1],lookup=0)]
    count=len(x);classes=[];parts=[]
    if count:
        # Up to eight posts per partition; all class records exist consecutively.
        for at in range(0,count,8):
            dim=min(8,count-at);parts.append(len(classes));classes.append(dict(dimensions=dim,subclass_bits=subclass_bits,masterbook=0,books=[-1 if missing else 0]*(1<<subclass_bits)))
    spec['floors']=[dict(type=1,partitions=parts,classes=classes,multiplier=multiplier,range_bits=range_bits,x=list(x))]
    spec['residues']=[dict(type=0,begin=0,end=0,partition_size=1,classifications=1,classbook=0,cascades=[0],books=[])]
    return spec

def build_case(identifier,spec,floor_index=0,amp=None,selector=0,entries=None,raw=None,present=True,mode=0,start=0,bins=32,operation='packet',singleton_bit=0,invalid_selector=False,master_entry=0):
    r=ref();old,_,_,_=r.make_case(identifier,spec);packet=r.Writer();packet.put((1<<start)-1,start);packet.put(0,1);packet.put(mode,(len(spec['modes'])-1).bit_length())
    if spec['modes'][mode]['blockflag']:packet.put(1,1);packet.put(0,1)
    floor=spec['floors'][floor_index]
    if operation=='raw':
        return dict(id=identifier,operation=operation,identification_hex=old['identification_hex'],identification_bits=old['identification_bits'],setup_hex=old['setup_hex'],setup_bits=old['setup_bits'],packet_hex='',packet_bits=0,start_bit=0,floor_index=floor_index,curve_n=bins,raw_y=list(raw))
    if floor['type']==0:
        width=floor['amplitude_bits'];value=(1<<width)-1 if amp is None else amp;packet.put(value,width)
        if value:
            packet.put(selector,len(floor['books']).bit_length())
            if not invalid_selector:
                book=spec['books'][floor['books'][selector]];count=max(1,(floor['order']+book['dimensions']-1)//book['dimensions']);sequence=entries if entries is not None else[0]*count
                need(len(sequence)==count,'fixture vector count')
                if any(book['lengths']):
                    for entry in sequence:put_word(packet,book['lengths'],entry,singleton_bit)
    else:
        packet.put(int(present),1)
        if present:
            limit=(256,128,86,64)[floor['multiplier']-1];width=(limit-1).bit_length();values=list(raw)if raw is not None else[limit-1,0]+[0]*len(floor['x']);packet.put(values[0],width);packet.put(values[1],width);at=2
            for cls_id in floor['partitions']:
                cls=floor['classes'][cls_id];sub=cls['subclass_bits'];selector_word=master_entry if sub else 0
                if sub:
                    # The fixtures initially use entry0; dedicated sparse cases
                    # replace its book or encode explicit high scalar posts.
                    master=spec['books'][cls['masterbook']]
                    if any(master['lengths']):put_word(packet,master['lengths'],selector_word,singleton_bit)
                for _ in range(cls['dimensions']):
                    bookid=cls['books'][selector_word&((1<<sub)-1)];selector_word>>=sub
                    if bookid>=0 and any(spec['books'][bookid]['lengths']):put_word(packet,spec['books'][bookid]['lengths'],values[at],singleton_bit)
                    at+=1
    row=dict(id=identifier,operation=operation,identification_hex=old['identification_hex'],identification_bits=old['identification_bits'],setup_hex=old['setup_hex'],setup_bits=old['setup_bits'],packet_hex=packet.octets(),packet_bits=len(packet.bits),start_bit=start,floor_index=floor_index,curve_n=bins,raw_y=[])
    if operation=='raw':row.update(packet_hex='',packet_bits=0,start_bit=0,raw_y=list(raw))
    return row

def cases():
    r=ref();original=[]
    def add(identifier,spec,**kwargs):original.append(build_case(identifier,spec,**kwargs))
    # Every six-bit amplitude width; both absent and nonzero. Alternate source
    # book formats, sequence flags and signed packed fields without rounding.
    for bits in range(64):
        spec=r.baseline();f=spec['floors'][0];f.update(amplitude_bits=bits,order=(1,3,7)[bits%3],amplitude_offset=0 if bits%7==0 else 255)
        spec['residues'][0]['partition_size']=3
        b=spec['books'][1];b.update(dimensions=3,lookup=1 if bits%2 else 2,sequence=bits%2,minimum_bits=(0x80000000,0x62800001,0xffe00001)[bits%3],delta_bits=(0,0x62800001,0xe2800001)[bits%3])
        add('f0-width-'+str(bits)+'-absent',spec,amp=0,bins=1)
        if bits:add('f0-width-'+str(bits)+'-present',spec,amp=(1<<bits)-1,singleton_bit=bits%2,bins=64)
    for order in(0,1,2,3,4,7,254,255):
        for sequence in(0,1):
            spec=r.baseline();spec['floors'][0].update(order=order,amplitude_bits=6);spec['books'][1].update(dimensions=3,lengths=[2,1,2],lookup=2,sequence=sequence)
            spec['residues'][0]['partition_size']=3
            count=max(1,(order+2)//3);add('f0-order-'+str(order)+'-seq-'+str(sequence),spec,entries=[i%3 for i in range(count)],start=3)
    for count in(1,2,3,16):
        spec=r.baseline();spec['floors'][0].update(books=[1]*count,amplitude_bits=3,order=2)
        add('f0-books-'+str(count)+'-last',spec,selector=count-1)
        add('f0-books-'+str(count)+'-invalid',spec,selector=count,invalid_selector=True)
    for rate,bark in((0,512),(44101,0),(0,0)):
        spec=r.baseline();spec['floors'][0].update(rate=rate,bark=bark,order=0)
        add('f0-zero-domain-'+str(rate)+'-'+str(bark)+'-present',spec);add('f0-zero-domain-'+str(rate)+'-'+str(bark)+'-absent',spec,amp=0)
    for raw in((1<<63)-1,(1<<63)-2,1):
        spec=r.baseline();spec['floors'][0]['order']=0;add('f0-order0-raw-'+str(raw),spec,amp=raw)
    for empty in(False,True):
        spec=r.baseline();spec['books'][1]['lengths']=[0]if empty else[1]
        if empty:spec['residues'][0].update(cascades=[0],books=[])
        add('f0-active-empty-'+str(int(empty)),spec)
    # One mode long even when small/large block sizes are equal: it still
    # consumes both window bits, independently of numerical block size.
    spec=r.baseline();spec['identification']['large']=6;spec['modes'][0]['blockflag']=1
    add('f0-equal-blocks-long',spec,start=7)
    # Pure scalar floor1 contexts deliberately require NULL global q storage.
    for mult in range(1,5):
        for rb in(0,1,4,15):
            spec=floor1_spec(mult,range_bits=rb);limit=(256,128,86,64)[mult-1]
            add('f1-two-posts-'+str(mult)+'-'+str(rb)+'-absent',spec,present=False,bins=1)
            add('f1-two-posts-'+str(mult)+'-'+str(rb)+'-descending',spec,raw=[limit-1,0],bins=4096 if rb==15 else 32,start=2)
            add('f1-two-posts-'+str(mult)+'-'+str(rb)+'-ascending',spec,raw=[0,limit-1],bins=33)
    for sub in range(4):
        for missing in(False,True):
            spec=floor1_spec(3,[4,2,6],3,sub,missing);add('f1-class-'+str(sub)+'-'+str(int(missing)),spec,raw=[85,0,0,0,0],bins=10)
    for empty in(False,True):
        spec=floor1_spec(1,range_bits=0,empty=empty);add('f1-no-posts-emptybook-'+str(int(empty)),spec,raw=[255,0])
        spec=floor1_spec(1,[1],2,0,False,empty);add('f1-active-emptybook-'+str(int(empty)),spec,raw=[255,0,0])
    # Sparse decoded scalar 131071: format entry number is not narrowed to16bit.
    spec=floor1_spec(3,[32767,1,16384],15);spec['books'].append(dict(dimensions=0,lengths=[0]*131071+[1],lookup=0));spec['floors'][0]['classes'][0]['books']=[1]
    add('f1-sparse-entry131071',spec,raw=[127,0,131071,131071,131071],bins=64)
    # Raw arithmetic helper exercises values beyond real initial packet widths.
    rng=random.Random(0xF10063)
    raw_specs=[floor1_spec(m,[4,2,6],3)for m in range(1,5)]
    raw_specs.append(floor1_spec(3,[32767,1,16384],15));raw_specs.append(floor1_spec(4,list(range(1,64)),7))
    for n,spec in enumerate(raw_specs):
        count=2+len(spec['floors'][0]['x']);vectors=[[0]*count,[0xffffffff]*count,[0xffffffff,0]+[0]*(count-2),[0,0xffffffff]+[0xffffffff]*(count-2)]
        vectors +=[[rng.randrange(1<<32)for _ in range(count)]for _ in range(4)]
        if n==2:vectors.append([127,0,0,0,1])
        for j,raw in enumerate(vectors):add('raw-wide-'+str(n)+'-'+str(j),spec,raw=raw,operation='raw',bins=10 if n<4 else 4096)
    # A nontrivial original-order shuffled classbook with scalar entries0..3.
    for sub in range(4):
        spec=floor1_spec(2,[7,1,5,3],3,sub);spec['books'][0]['lengths']=[2,2,2,2]
        for j in range(4):add('f1-scalar-four-'+str(sub)+'-'+str(j),spec,raw=[j*31,127-j*31,j,(j+1)%4,(j+2)%4,(j+3)%4],bins=32)
    # Nonzero classword selectors exercise low-mask/shift and missing subclasses.
    for sub in range(1,4):
        spec=floor1_spec(2,[3,1],2,sub,True);cls=spec['floors'][0]['classes'][0];count=1<<(2*sub)
        spec['books'].append(dict(dimensions=1,lengths=[2*sub]*count,lookup=0));cls['masterbook']=1;cls['books'][1]=cls['books'][-1]=0
        add('f1-nonzero-selector-'+str(sub),spec,raw=[127,0,0,0],master_entry=((1<<sub)-1)+(1<<sub),bins=16)
    # Native selection keeps all branch families, rather than truncating the
    # list of width cases. No measured output influences this selection.
    native=[row for row in original if not row['id'].startswith('f0-width-')]
    widths=[row for row in original if row['id'].startswith('f0-width-')]
    needed=200-len(native);need(needed>=0 and needed<=len(widths),'predeclared native budget')
    indices=[i*len(widths)//needed for i in range(needed)]if needed else[];native=widths[:0]+[widths[i]for i in indices]+native
    need(len(native)==200,'finite native200 originals')
    host_rows=[]
    for row in original:
        host_rows.append(row)
        if row['operation']=='packet':
            wanted=expected_case(row)['exact']
            if wanted['prefix_status']==0 and wanted['floor_status']==0:
                for cut in range(row['start_bit'],wanted['position']):host_rows.append(dict(row,id=row['id']+'-cut'+str(cut),packet_bits=cut))
    model=dict(schema='native-vorbis-floor-packet-cases-v1',cases=host_rows);target=dict(schema=model['schema'],cases=native)
    return model,target

CASE_KEYS={'id','operation','identification_hex','identification_bits','setup_hex','setup_bits','packet_hex','packet_bits','start_bit','floor_index','curve_n','raw_y'}
def validate_model(model):
    need(set(model)=={'schema','cases'}and model['schema']=='native-vorbis-floor-packet-cases-v1','floor packet model schema');rows=model['cases'];need(type(rows)is list and 1<=len(rows)<=40000,'finite model rows');seen=set()
    for case in rows:
        need(set(case)==CASE_KEYS and re.fullmatch(r'[A-Za-z0-9_-]{1,63}',case['id'])and case['id']not in seen,'unique exact case fields/id');seen.add(case['id']);need(case['operation']in OPS,'selected operation')
        for stem in('identification','setup','packet'):
            body=case[stem+'_hex'];bits=case[stem+'_bits'];need(type(body)is str and re.fullmatch(r'(?:[0-9a-f]{2})*',body)and len(body)<=2097152 and type(bits)is int and 0<=bits<=4*len(body),'concrete bytes/bit extents')
        need(type(case['start_bit'])is int and 0<=case['start_bit']<=case['packet_bits']and type(case['floor_index'])is int and 0<=case['floor_index']<=63 and type(case['curve_n'])is int and 1<=case['curve_n']<=4096,'selected cursor/floor/bins')
        need(type(case['raw_y'])is list and len(case['raw_y'])<=65 and all(type(v)is int and 0<=v<=0xffffffff for v in case['raw_y']),'raw wide scalar fields')
        need((case['operation']=='packet'and not case['raw_y'])or(case['operation']=='raw'and not case['packet_hex']and case['packet_bits']==case['start_bit']==0),'operation payload binding')
    return rows
class Reader:
    def __init__(self,body):self.body,self.at=body,0
    def take(self,fmt):
        size=struct.calcsize(fmt);need(self.at+size<=len(self.body),'complete binary field');values=struct.unpack_from(fmt,self.body,self.at);self.at+=size;return values[0]if len(values)==1 else values

def encode_input(model):
    data=bytearray(b'FLRTEST1'+struct.pack('<I',len(validate_model(model))))
    for case in model['cases']:
        name=case['id'].encode('ascii');data+=struct.pack('<I',len(name))+name+struct.pack('<I',OPS[case['operation']])
        for stem in('identification','setup','packet'):
            body=bytes.fromhex(case[stem+'_hex']);data+=struct.pack('<I',len(body))+body+struct.pack('<Q',case[stem+'_bits'])
        data+=struct.pack('<QIII',case['start_bit'],case['floor_index'],case['curve_n'],len(case['raw_y']))
        for value in case['raw_y']:data+=struct.pack('<I',value)
    return bytes(data)
def decode_input(body):
    reader=Reader(body);need(reader.take('<8s')==b'FLRTEST1','floor packet inputmagic');count=reader.take('<I');need(1<=count<=40000,'finite input rows');rows=[]
    for _ in range(count):
        n=reader.take('<I');need(1<=n<=63,'bounded id');row=dict(id=reader.take('<'+str(n)+'s').decode('ascii'));operation=reader.take('<I');need(operation in(1,2),'encoded operation');row['operation']={1:'packet',2:'raw'}[operation]
        for stem in('identification','setup','packet'):
            n=reader.take('<I');need(n<=1048576,'bounded bytes');row[stem+'_hex']=reader.take('<'+str(n)+'s').hex();row[stem+'_bits']=reader.take('<Q')
        row['start_bit'],row['floor_index'],row['curve_n'],n=reader.take('<QIII');need(n<=65,'bounded raw array');row['raw_y']=[reader.take('<I')for _ in range(n)];rows.append(row)
    need(reader.at==len(body),'all raw input bytes consumed');model=dict(schema='native-vorbis-floor-packet-cases-v1',cases=rows);validate_model(model);return model

def decode_output(body,model):
    rows=validate_model(model);reader=Reader(body);need(reader.take('<8s')==b'FLROUT01'and reader.take('<I')==len(rows),'exact floor capture count');controls=reader.take('<I');need(controls==CONTROL_COUNT,'actual fixed control count');observed=[]
    def array(fmt,bound):
        count=reader.take('<I');need(count<=bound,'bounded captured array');return[reader.take(fmt)for _ in range(count)]
    for i,case in enumerate(rows):
        need(reader.take('<I')==i,'ordered capture ordinal');ps=reader.take('<i');prefix=dict(zip(PREFIX,reader.take('<IIIIII')))if ps==0 else None;fs=reader.take('<i');state=None
        if fs==0:
            fields=reader.take('<IIIII');raw,bits,offset=reader.take('<QII');state=dict(zip(('floor_index','type','present','value_count','selected_book'),fields));state['amplitude']=dict(raw_amplitude=str(raw),amplitude_bits=bits,amplitude_offset=offset)
        coefficients=[dict(zip(AFFINE,values))for values in array('<IIII',255)];raw=array('<I',65);rs=reader.take('<i');final=array('<I',65);active=array('<B',65);cs=reader.take('<i');indices=array('<B',4096);gs=reader.take('<i');gain=None
        if gs==0:
            kind,bits,exponent=reader.take('<IQi');gain=dict(kind=kind,log2_bits=f'{bits:016x}',log2_exponent=exponent)
        consistent=reader.take('<I');position,eop,guards=reader.take('<QII');need(eop in(0,1)and guards==7,'actual input/canary/preservation checks')
        observed.append(dict(case=i,id=case['id'],operation=case['operation'],prefix_status=ps,prefix=prefix,floor_status=fs,state=state,coefficients=coefficients,raw_y=raw,reconstruct_status=rs,final_y=final,active=active,curve_status=cs,indices=indices,gain_status=gs,gain=gain,gain_consistent=consistent,position=position,end_of_packet=bool(eop),guards=1,unchanged=1))
    need(reader.at==len(body),'whole floor result stream');return dict(metadata_controls=controls,rows=observed)

def compare_all(model,observed,expected=None,native=False):
    rows=validate_model(model);need(len(rows)==len(observed),'complete comparison rows')
    if expected is not None:need(expected['schema']=='native-vorbis-floor-packet-expected-v1'and expected['policy']==POLICY and len(expected['cases'])==len(rows),'fixed independent expected policy')
    metrics=[];failures=[]
    for i,(case,actual)in enumerate(zip(rows,observed)):
        try:
            need(actual['case']==i and actual['id']==case['id']and actual['operation']==case['operation']and actual['guards']==actual['unchanged']==1,'actual guarded identity');wanted=expected_case(case)
            if expected is not None:need(wanted==expected['cases'][i],'regenerated expected case')
            reasons=[]
            for key,value in wanted['exact'].items():
                if actual[key]!=value:reasons.append('exact '+key)
            gs=actual['gain_status'];gain=actual['gain'];rule=wanted['gain_rule']
            if gs==0:
                need(type(gain)is dict and set(gain)=={'kind','log2_bits','log2_exponent'}and type(gain['kind'])is int and gain['kind']in range(4)and re.fullmatch(r'[0-9a-f]{16}',gain['log2_bits'])and type(gain['log2_exponent'])is int,'complete gain capture')
                value=struct.unpack('<d',bytes.fromhex(gain['log2_bits'])[::-1])[0];need(math.isfinite(value)and(value==0 and gain['log2_exponent']==0 or .5<=abs(value)<1),'normalized gain capture')
                if actual['gain_consistent']!=1:reasons.append('existing affine gain composition')
                if rule=='absent'and(gain['kind']!=1 or value!=0 or gain['log2_exponent']!=0):reasons.append('unused exact ABSENT')
                if rule=='unity'and(gain['kind']!=0 or value!=0 or gain['log2_exponent']!=0):reasons.append('order0 D1 exact unity')
            elif gain is not None or actual['gain_consistent']!=0:reasons.append('uncalled gain capture')
            exact_part={key:actual[key]for key in wanted['exact']};metric=dict(id=case['id'],qualified=not reasons,failure_reasons=reasons,operation=case['operation'],prefix_status=actual['prefix_status'],floor_status=actual['floor_status'],present=0 if actual['state']is None else actual['state']['present'],coefficient_count=len(actual['coefficients']),raw_count=len(actual['raw_y']),curve_bins=len(actual['indices']),end_of_packet=actual['end_of_packet'],gain_reference_compared=rule in('absent','unity'),gain_rule=rule,expected_sha256=sha(json.dumps(wanted['exact'],sort_keys=True).encode()),actual_sha256=sha(json.dumps(exact_part,sort_keys=True).encode()))
            if reasons:metric.update(expected=wanted,actual=actual);failures.append(dict(index=i,**metric))
            metrics.append(metric)
        except(ValueError,KeyError,TypeError,struct.error)as error:failures.append(dict(index=i,id=case['id'],nonmeasurement_error=str(error),actual=actual))
    return dict(measurement_completed=len(metrics)==len(rows),passed=not failures and len(metrics)==len(rows),cases=len(rows),metrics=metrics,failures=failures,
        coefficients=sum(v['coefficient_count']for v in metrics),raw_values=sum(v['raw_count']for v in metrics),curve_bins=sum(v['curve_bins']for v in metrics),all_EOP_rows=sum(v['end_of_packet']for v in metrics),prefix_EOP_rows=sum(v['end_of_packet']and v['prefix_status']==-3 for v in metrics),nominal_EOP_rows=sum(v['end_of_packet']and v['floor_status']==0 for v in metrics),gain_exact_absent_or_unity=sum(v['gain_reference_compared']for v in metrics),general_floor0_gain_reference_compared=False)
def compare_target_rows(model,expected,observed):return compare_all(model,observed,expected,native=True)

def target_header(model):
    rows=validate_model(model);lines=['#pragma once','#include <stddef.h>','#include <stdint.h>','#define FLOOR_PACKET_CASE_COUNT '+str(len(rows)),
        'typedef struct { const char *id; uint32_t operation; const uint8_t *identification; uint32_t identification_bytes; uint64_t identification_bits;',
        ' const uint8_t *setup; uint32_t setup_bytes; uint64_t setup_bits; const uint8_t *packet; uint32_t packet_bytes; uint64_t packet_bits;',
        ' uint64_t start_bit; uint32_t floor_index,curve_n; const uint32_t *raw_y; uint32_t raw_count; } floor_packet_case_t;']
    for i,case in enumerate(rows):
        for stem in('identification','setup','packet'):
            body=bytes.fromhex(case[stem+'_hex'])
            if body:lines.append('static const uint8_t floor_packet_'+stem+'_'+str(i)+'[] = {'+','.join('UINT8_C(0x'+f'{value:02x}'+')'for value in body)+'};')
        if case['raw_y']:lines.append('static const uint32_t floor_packet_raw_'+str(i)+'[] = {'+','.join('UINT32_C('+str(value)+')'for value in case['raw_y'])+'};')
    lines.append('static const floor_packet_case_t floor_packet_cases[FLOOR_PACKET_CASE_COUNT] = {')
    for i,case in enumerate(rows):
        values=['"'+case['id']+'"',str(OPS[case['operation']])]
        for stem in('identification','setup','packet'):values.extend(['floor_packet_'+stem+'_'+str(i)if case[stem+'_hex']else'NULL',str(len(case[stem+'_hex'])//2),'UINT64_C('+str(case[stem+'_bits'])+')'])
        values+=['UINT64_C('+str(case['start_bit'])+')',str(case['floor_index']),str(case['curve_n']),'floor_packet_raw_'+str(i)if case['raw_y']else'NULL',str(len(case['raw_y']))];lines.append('    {'+','.join(values)+'},')
    return '\n'.join(lines+['};',''])

def self_checks():
    floor=dict(type=1,multiplier=3,x=[0,8,4,2,6]);values,flags=reconstruct(floor,[127,0,0,0,1]);need(values==[85,0,64,85,31]and flags==[1,1,1,0,1],'independent late-clamp/reactivation golden')
    need(curve(floor,values,flags,10)==[255,240,224,208,192,143,93,47,0,0],'independent original-segment golden')
    need(curve(dict(multiplier=1,x=[0,32768]),[255,0],[1,1],3)==[255,255,255],'clipped negative slope preserves original endpoint')
    row=build_case('self-order0',ref().baseline(),amp=0);want=expected_case(row)['exact'];need(want['state']['present']==0 and want['gain_status']==0,'zero amplitude is unused')
    return dict(passed=True,oracle_only=True,component_executed=False)
def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value

def main():
    global REFERENCE
    REFERENCE=load_reference(REFERENCE_PATH)
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    parser.add_argument('--prepare-only',action='store_true');parser.add_argument('--oracle-self-test',action='store_true');args=parser.parse_args()
    if args.oracle_self_test:print(json.dumps(self_checks()));return 0
    need(args.output is not None,'explicit fresh output');out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh task-local output')
    out.mkdir(parents=True);(out/'sources').mkdir();(out/'target-cases').mkdir()
    report=dict(completed=False,passed=False,prepared=False,component_executed=False,policy=POLICY,commands=[],sources={},
        full_floor0_qualified=False,full_G6_qualified=False,PCM_qualified=False,decoder_executed=False,stream_decoder_executed=False,production_radio_integration=False,SDK_or_QEMU_executed=False,physical_device=False)
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
        freeze(Path(__file__),'test-vorbis-floor-packet.py');need(sha(freeze(REFERENCE_PATH,'reference-setup.py'))==REFERENCE_SHA,'frozen independent reference identity');freeze(COMPONENT/'floor0.c','floor0.c')
        freeze(COMPONENT/'floor_packet.c','floor_packet.c');freeze(COMPONENT/'include/native_vorbis_floor_packet.h','native_vorbis_floor_packet.h');freeze(COMPONENT/'setup.c','setup.c');freeze(COMPONENT/'include/native_vorbis_setup.h','native_vorbis_setup.h');freeze(COMPONENT/'codebook.c','codebook.c');freeze(COMPONENT/'include/native_vorbis_codebook.h','native_vorbis_codebook.h');freeze(COMPONENT/'quant.c','quant.c');freeze(COMPONENT/'include/native_vorbis_floor0.h','native_vorbis_floor0.h')
        freeze(COMPONENT/'include/native_vorbis_quant.h','native_vorbis_quant.h');freeze(COMPONENT/'CMakeLists.txt','CMakeLists.txt');freeze(DRIVER,'driver.c')
        owner=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-owner.py')
        nodes=[node for node in ast.parse(owner).body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(nodes)==1,'one existing nonce-owned supervisor literal');(out/'supervisor.py').write_text(ast.literal_eval(nodes[0].value),encoding='utf-8',newline='\n')
        report['oracle_self_checks']=self_checks()
        model,target=cases();inputs=encode_input(model);need(decode_input(inputs)==model,'complete exact raw packet/affine input roundtrip')
        (out/'cases.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');(out/'inputs.bin').write_bytes(inputs)
        directory=out/'target-cases';expected=dict(schema='native-vorbis-floor-packet-expected-v1',policy=POLICY,cases=[expected_case(row) for row in target['cases']])
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
        so,se=run('compile',flags+['-I'+host(out/'sources'),host(out/'sources/driver.c'),host(out/'sources/floor0.c'),host(out/'sources/quant.c'),host(out/'sources/codebook.c'),host(out/'sources/setup.c'),host(out/'sources/floor_packet.c'),'-lm','-o',host(out/'test')])
        need(not so and not se,'clean strict whole-component compile');current()
        so,se=run('execute',[host(out/'test'),host(out/'inputs.bin'),host(out/'outputs.bin')]);report['component_executed']=True;need(not so and not se,'clean actual sanitized floor packet execution')
        output=(out/'outputs.bin').read_bytes();decoded=decode_output(output,model);measured=compare_all(model,decoded['rows']);current()
        report.update(completed=True,passed=measured['passed'],source_inputs_unchanged=True,numerical=measured,metadata_controls=decoded['metadata_controls'],output_sha256=sha(output),
            result='OWNED_FLOOR_PACKET_EXACT_QUALIFIED' if measured['passed'] else 'OWNED_FLOOR_PACKET_EXACT_REJECTED')
        save();print(json.dumps(dict(completed=True,passed=report['passed'],cases=report['cases'],target_cases=report['target_cases'],result=report['result'],coefficients=measured['coefficients'],raw_values=measured['raw_values'],curve_bins=measured['curve_bins'],nominal_EOP_rows=measured['nominal_EOP_rows'])));return 0 if report['passed'] else 1
    except BaseException as error:report.update(completed=False,passed=False,error=repr(error));save();raise

if __name__=='__main__':sys.exit(main())


