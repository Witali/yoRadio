"""Exact residue0/1/2 and mapping coupling tests, without floor or PCM claims.

Independent Fraction arithmetic, literal residue scatter, and sign-branch
coupling follow Vorbis I4.3.3-5/8/9.2.2. Setup grammar is explicitly pinned.
"""
import argparse
import ast
from fractions import Fraction
from functools import lru_cache
import hashlib
import importlib.util
import json
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
DRIVER=ROOT/'tests/native/vorbis_residue_test.c'
REFERENCE_PATH=ROOT/'tests/test-vorbis-setup.py'
REFERENCE_SHA='ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff'
REFERENCE=None
CONTROL_COUNT=37
LFIELDS=('mapping','bins','channels','limbs','magnitude_bits','exponent','sample_count','limb_count','classification_count')
POLICY=dict(schema='native-vorbis-residue-policy-v1',exact_fraction_and_limb_comparison=True,
    classwords='Low-dimensional base digits; ignore leftover high quotient',zero_cascades='Pass0 still reads phrase words',
    nominal_EOP='Commit earlier complete VQ words and last complete codeword cursor',type2='Absolute flat index modulo/divide by bundle channels',
    propagation='One forward coupling-pair pass',coupling='All pairs in reverse order; exact signs; nonexpansive magnitude',
    common_grid='All cascade books in assigned mapping bundles, independent of flags and clipped spans',
    host_payload_cuts_are_explicit_rows=True,setup_header_cut_campaign_repeated=False,selection_before_measurement=True,
    floor_or_G6_or_PCM_qualified=False)
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(body):return hashlib.sha256(body).hexdigest()
def ref():need(REFERENCE is not None,'explicit independent setup reference required');return REFERENCE
def load_reference(path):
    need(sha(path.read_bytes())==REFERENCE_SHA,'reviewed independent setup source')
    spec=importlib.util.spec_from_file_location('residue_setup_reference',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
@lru_cache(maxsize=None)
def context(ih,ib,sh,sb):
    identity=ref().identification(bytes.fromhex(ih),ib);setup=ref().parse_setup(bytes.fromhex(sh),sb,identity);return setup,sha(json.dumps(setup,sort_keys=True).encode())
def mapping_info(ctx,index):
    layout=ctx['layout'];pool=ctx['configuration'];need(0<=index<layout['mapping_count'],'selected mapping');at=pool[layout['mapping_table']+index];submaps,coupling,channels=pool[at:at+3];at+=3;pairs=[tuple(pool[at+2*i:at+2*i+2])for i in range(coupling)];at+=2*coupling;mux=pool[at:at+channels];at+=channels;triples=[pool[at+3*i:at+3*i+3]for i in range(submaps)]
    return dict(channels=channels,pairs=pairs,mux=mux,submaps=triples)
def residue_info(ctx,index):
    layout=ctx['layout'];pool=ctx['configuration'];at=pool[layout['residue_table']+index];kind,begin,end,partition,classes,phrase,count=pool[at:at+7];at+=7;cascades=pool[at:at+classes];offsets=pool[at+classes:at+2*classes];books=pool[at+2*classes:at+2*classes+count]
    return dict(type=kind,begin=begin,end=end,partition_size=partition,classifications=classes,classbook=phrase,cascades=cascades,book_offsets=offsets,books=books)
def propagated(mapping,flags):
    result=list(flags)
    for m,a in mapping['pairs']:
        if result[m]or result[a]:result[m]=result[a]=1
    return result
def bundles(ctx,mapping,bins,flags):
    for sub,(_,_,residue_id)in enumerate(mapping['submaps']):
        channels=[ch for ch,mux in enumerate(mapping['mux'])if mux==sub]
        if not channels:continue
        residue=residue_info(ctx,residue_id);size=bins*(len(channels)if residue['type']==2 else 1);begin=min(size,residue['begin']);end=min(size,residue['end']);parts=max(0,end-begin)//residue['partition_size'];active=[ch for ch in channels if flags[ch]]
        yield residue,channels,active,begin,parts

def measure(case,ctx):
    mapping=mapping_info(ctx,case['mapping']);flags=propagated(mapping,case['floor_present']);lowest=[];uppers=[];scratch=0
    for residue,channels,active,_,parts in bundles(ctx,mapping,case['bins'],flags):
        if residue['classifications']>1:scratch=max(scratch,parts*(int(bool(active))if residue['type']==2 else len(active)))
        for bookid in residue['books']:
            q=ctx['books'][bookid]['layout']['quantization'];terms=[]
            for stem in('minimum','delta'):
                word=q[stem+'_bits'];mant=word&0x1fffff;exponent=((word>>21)&1023)-788
                if mant:lowest.append(exponent+(mant&-mant).bit_length()-1);terms.append(exponent+mant.bit_length())
            if terms:
                weight=(q['dimensions']if q['sequence_p']else 1)*(int(bool(q['minimum_bits']&0x1fffff))+(((1<<q['value_bits'])-1)if q['delta_bits']&0x1fffff else 0));need(weight>0,'nonzero exact VQ weight');uppers.append(max(terms)+(weight-1).bit_length())
    exponent=min(lowest)if lowest else 0;magnitude=max(uppers)+3-exponent if uppers else 0;limbs=(magnitude+32)//32 if magnitude else 0;samples=mapping['channels']*case['bins']
    return dict(zip(LFIELDS,(case['mapping'],case['bins'],mapping['channels'],limbs,magnitude,exponent,samples,samples*limbs,scratch)))
def unpack(word):
    mant=word&0x1fffff;exponent=((word>>21)&1023)-788;value=Fraction(mant)*(Fraction(2)**exponent);return -value if word&0x80000000 else value
@lru_cache(maxsize=None)
def packed(word):return unpack(word)
def vector(book,entry):
    q=book['layout']['quantization'];result=[];last=Fraction(0);divisor=1
    for component in range(q['dimensions']):
        index=(entry//divisor)%q['multiplicand_count']if q['lookup_type']==1 else entry*q['dimensions']+component
        value=packed(q['minimum_bits'])+packed(q['delta_bits'])*book['multiplicands'][index]+last;result.append(value)
        if q['sequence_p']:last=value
        if q['lookup_type']==1:divisor*=q['multiplicand_count']
    return result
class EndOfPacket(Exception):pass
def decode_word(book,reader,sticky):
    if sticky[0]:raise EndOfPacket
    if not book['words']:raise ValueError('active empty entropy book')
    start=reader.position;words=book['words']
    try:
        if len(words)==1:reader.take(1);return words[0]['entry']
        path=0;lookup={(word['code'],word['length']):word['entry']for word in words}
        for length in range(1,33):
            path|=reader.take(1)<<(32-length)
            if(path,length)in lookup:return lookup[(path,length)]
    except ref().Truncated:reader.position=start;sticky[0]=True;raise EndOfPacket
    raise ValueError('invalid entropy codeword')
def couple(spectrum,mapping):
    output=[list(channel)for channel in spectrum]
    for m,a in reversed(mapping['pairs']):
        for i,(mag,angle)in enumerate(zip(output[m],output[a])):
            if mag>0:pair=(mag,mag-angle)if angle>0 else(mag+angle,mag)
            else:pair=(mag,mag+angle)if angle>0 else(mag-angle,mag)
            need(max(abs(pair[0]),abs(pair[1]))<=max(abs(mag),abs(angle)),'exact inverse coupling nonexpansive invariant');output[m][i],output[a][i]=pair
    return output

def limb_array(spectrum,layout):
    limbs=layout['limbs'];result=[];unit=Fraction(2)**layout['exponent'];modulus=1<<(32*limbs)
    for channel in spectrum:
        for value in channel:
            if not limbs:need(value==0,'canonical implicit zero spectrum');continue
            integer=value/unit;need(integer.denominator==1 and abs(integer.numerator)<1<<layout['magnitude_bits'],'exact bounded shared-grid sample');raw=integer.numerator%modulus
            result.extend((raw>>(32*i))&0xffffffff for i in range(limbs))
    return result

def expected_case(case):
    ctx,pin=context(case['identification_hex'],case['identification_bits'],case['setup_hex'],case['setup_bits']);layout=measure(case,ctx);mapping=mapping_info(ctx,case['mapping']);flags=propagated(mapping,case['floor_present']);reader=ref().Bits(bytes.fromhex(case['packet_hex']),case['packet_bits'],case['start_bit']);sticky=[case['initial_eop']];spectrum=[[Fraction(0)]*case['bins']for _ in range(mapping['channels'])];state=dict(classwords=0,vectors=0,values=0,stopped_on_eop=0);invalid=None
    try:
        for residue,channels,active,begin,parts in bundles(ctx,mapping,case['bins'],flags):
            if not active or not parts:continue
            targets=[None]if residue['type']==2 else active;classes=residue['classifications'];phrase=ctx['books'][residue['classbook']];dimensions=phrase['layout']['quantization']['dimensions'];classifications={channel:[0]*parts for channel in targets}
            for stage in range(8):
                for group in range(0,parts,dimensions):
                    if stage==0:
                        for channel in targets:
                            word=decode_word(phrase,reader,sticky);state['classwords']+=1
                            if classes>1:
                                # Base reduction is independent of any expanded
                                # classification map and ignores high quotient.
                                digits=[0]*dimensions
                                for at in range(dimensions-1,-1,-1):digits[at]=word%classes;word//=classes
                                classifications[channel][group:min(parts,group+dimensions)]=digits[:min(dimensions,parts-group)]
                    for partition in range(group,min(parts,group+dimensions)):
                        for channel in targets:
                            cls=classifications[channel][partition];cascade=residue['cascades'][cls]
                            if not cascade&(1<<stage):continue
                            bookid=residue['books'][residue['book_offsets'][cls]+(cascade&((1<<stage)-1)).bit_count()];book=ctx['books'][bookid];dim=book['layout']['quantization']['dimensions'];offset=begin+partition*residue['partition_size'];step=residue['partition_size']//dim
                            for entry_number in range(step):
                                entry=decode_word(book,reader,sticky);values=vector(book,entry);state['vectors']+=1;state['values']+=len(values)
                                for component,value in enumerate(values):
                                    position=offset+(entry_number+component*step if residue['type']==0 else entry_number*dim+component)
                                    if residue['type']==2:ch=channels[position%len(channels)];position//=len(channels)
                                    else:ch=channel
                                    spectrum[ch][position]+=value
    except EndOfPacket:state['stopped_on_eop']=1
    except ValueError as error:invalid=str(error)
    if invalid:
        exact=dict(measure_status=0,layout=layout,packet_status=-1,state=None,decoded_limbs=[],coupling_status=-99,coupled_limbs=[],position=case['start_bit'],end_of_packet=case['initial_eop'])
    else:
        decoded=limb_array(spectrum,layout);coupled=limb_array(couple(spectrum,mapping),layout);exact=dict(measure_status=0,layout=layout,packet_status=0,state=state,decoded_limbs=decoded,coupling_status=0,coupled_limbs=coupled,position=reader.position,end_of_packet=sticky[0])
    need(sha(json.dumps(ctx,sort_keys=True).encode())==pin,'cached independent setup input remains unchanged')
    return dict(id=case['id'],exact=exact)

# Packet fixtures use a separate writer walk and explicit chosen entry numbers.
ONE=(788<<21)|1
HUGE=(1023<<21)|(1<<20)
def book(dim=1,minimum=ONE,delta=0,sequence=0,width=16,lookup=1,lengths=None):return dict(dimensions=dim,lengths=[1]if lengths is None else lengths,lookup=lookup,minimum_bits=minimum,delta_bits=delta,sequence=sequence,value_bits=width)
def base_spec(kind=1,channels=2,bins=4,dimension=1,sequence=0,passes=1,classes=1,phrase_dimension=1,phrase_lengths=None):
    spec=ref().baseline();spec['identification']['channels']=channels;spec['identification']['large']=6
    if phrase_lengths is None:
        count=classes**phrase_dimension;need(count<=256,'bounded fixture phrase alphabet');size=1<<(count-1).bit_length();phrase_lengths=[1]if size==1 else[size.bit_length()-1]*size
    spec['books']=[dict(dimensions=phrase_dimension,lengths=phrase_lengths,lookup=0),book(dimension,sequence=sequence)]
    spec['floors']=[dict(type=1,partitions=[],classes=[],multiplier=1,range_bits=0,x=[])]
    spec['residues']=[dict(type=kind,begin=0,end=bins*(channels if kind==2 else 1),partition_size=dimension,classifications=classes,classbook=0,cascades=[(1<<passes)-1]*classes,books=[1]*(passes*classes))]
    spec['mappings']=[dict(pairs=[],mux=[0]*channels,submaps=[(255,0,0)])];return spec

def put_word(writer,book_spec,entry):
    words=ref().greedy_words(book_spec['lengths'])
    if not words:return False
    word=next(word for word in words if word['entry']==entry)
    for bit in range(word['length']):writer.put((word['code']>>(31-bit))&1,1)
    return True

def build_case(identifier,spec,bins=4,flags=None,mapping=0,start=0,initial_eop=False,seed=1,phrase_entry=None,stage_entry=None):
    r=ref();old,_,_,_=r.make_case(identifier,spec);flags=[1]*spec['identification']['channels']if flags is None else list(flags);w=r.Writer();w.put((1<<start)-1,start)
    m=spec['mappings'][mapping];prop=list(flags)
    for mag,angle in m['pairs']:
        if prop[mag]or prop[angle]:prop[mag]=prop[angle]=1
    rng=random.Random(seed);stop=False
    for sub,(_,_,rid)in enumerate(m['submaps']):
        channels=[ch for ch,mux in enumerate(m['mux'])if mux==sub]
        if not channels:continue
        residue=spec['residues'][rid];size=bins*(len(channels)if residue['type']==2 else 1);begin=min(size,residue['begin']);end=min(size,residue['end']);parts=max(0,end-begin)//residue['partition_size'];active=[ch for ch in channels if prop[ch]]
        if not active or not parts:continue
        targets=[None]if residue['type']==2 else active;phrase=spec['books'][residue['classbook']];dimensions=phrase['dimensions'];choices=[word['entry']for word in r.greedy_words(phrase['lengths'])];codes={target:[0]*parts for target in targets};classes=residue['classifications']
        for stage in range(8):
            for group in range(0,parts,dimensions):
                if stage==0:
                    for ch in targets:
                        if not choices:stop=True;break
                        entry=phrase_entry(ch,group,rid)if phrase_entry is not None else rng.choice(choices)
                        if not put_word(w,phrase,entry):stop=True;break
                        if classes>1:
                            # Construct the low-dimensional digit tuple directly
                            # from the original entry, including high quotient.
                            digits=[(entry//classes**(dimensions-1-i))%classes for i in range(dimensions)]
                            codes[ch][group:min(parts,group+dimensions)]=digits[:min(dimensions,parts-group)]
                    if stop:break
                for part in range(group,min(parts,group+dimensions)):
                    for ch in targets:
                        cls=codes[ch][part];cascade=residue['cascades'][cls]
                        if not cascade&(1<<stage):continue
                        before=sum(value.bit_count()for value in residue['cascades'][:cls]);index=before+(cascade&((1<<stage)-1)).bit_count();vq=spec['books'][residue['books'][index]];entries=[word['entry']for word in r.greedy_words(vq['lengths'])]
                        for number in range(residue['partition_size']//vq['dimensions']):
                            if not entries:stop=True;break
                            entry=stage_entry(ch,part,stage,number,rid)if stage_entry is not None else rng.choice(entries)
                            if not put_word(w,vq,entry):stop=True;break
                        if stop:break
                    if stop:break
                if stop:break
            if stop:break
        if stop:break
    return dict(id=identifier,identification_hex=old['identification_hex'],identification_bits=old['identification_bits'],setup_hex=old['setup_hex'],setup_bits=old['setup_bits'],packet_hex=w.octets(),packet_bits=len(w.bits),start_bit=start,initial_eop=initial_eop,mapping=mapping,bins=bins,floor_present=flags)

def cases():
    r=ref();original=[]
    def add(identifier,spec,**kwargs):original.append(build_case(identifier,spec,**kwargs))
    for kind in range(3):
        for passes in(1,2,8):
            for sequence in(0,1):
                for dimension in(1,2,3):
                    spec=base_spec(kind,bins=6,dimension=dimension,sequence=sequence,passes=passes);spec['books'][1].update(lengths=[2,1,2],lookup=2,delta_bits=ONE,value_bits=4)
                    add(f'format-{kind}-passes-{passes}-seq-{sequence}-dim-{dimension}',spec,bins=6,start=3,seed=kind+passes+sequence)
    # Cover the packed exponent/sign extremes without inheriting Xiph's float clamp.
    words=(1,0x80000001,ONE,ONE|0x80000000,HUGE,HUGE|0x80000000,0x7fffffff,0xffffffff)
    for kind in range(3):
        for i,word in enumerate(words):
            spec=base_spec(kind,bins=2,passes=8);spec['books'][1].update(minimum_bits=word,delta_bits=words[(i+3)%len(words)],value_bits=16)
            add(f'named-packed-{kind}-{i}',spec,bins=2)
    for kind in range(3):
        for flags in([0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,1,1]):
            spec=base_spec(kind,channels=3,bins=3);spec['mappings'][0]['pairs']=[(1,2),(0,1)]
            add('named-forward-'+str(kind)+'-'+''.join(map(str,flags)),spec,bins=3,flags=flags)
    for kind in range(3):
        for classes,dim,entry in((1,1,0),(1,65535,0),(2,1,3),(2,2,7),(2,3,15),(3,1,7),(3,2,15),(64,1,63)):
            entries=1<<(max(classes**dim,entry+1)-1).bit_length()if classes>1 else 1;lengths=[1]if entries==1 else[entries.bit_length()-1]*entries
            spec=base_spec(kind,bins=5,classes=classes,phrase_dimension=dim,phrase_lengths=lengths);spec['residues'][0]['cascades']=[0 if i%2 else 1 for i in range(classes)];spec['residues'][0]['books']=[1 for value in spec['residues'][0]['cascades']if value]
            add(f'named-phrase-{kind}-{classes}-{dim}-{entry}',spec,bins=5,phrase_entry=lambda ch,group,rid,e=entry:e)
    for channels in(2,3,7):
        for begin in(1,2):
            for partition in(1,3,6):
                spec=base_spec(2,channels=channels,bins=5);spec['residues'][0].update(begin=begin,end=channels*5-1,partition_size=partition);spec['books'][1].update(dimensions=1,lengths=[2,1,2],lookup=2,delta_bits=ONE)
                add(f'named-unaligned-{channels}-{begin}-{partition}',spec,bins=5,seed=begin+partition)
    for kind in range(3):
        for begin,end,partition in((0xffffff,0xffffff,1),(0xffffff,0,1),(0,0xffffff,0x1000000),(1,1,1),(3,2,1),(1,31,3)):
            spec=base_spec(kind,bins=7);spec['residues'][0].update(begin=begin,end=end,partition_size=partition)
            add(f'named-extent-{kind}-{begin}-{end}-{partition}',spec,bins=7)
        for state in('zero','zero-cascade','empty'):
            spec=base_spec(kind,bins=2)
            if state=='zero':spec['books'][1].update(minimum_bits=0x80000000,delta_bits=0)
            if state=='zero-cascade':spec['residues'][0].update(cascades=[0],books=[])
            if state=='empty':spec['books'][1]['lengths']=[0]
            add('named-'+state+'-'+str(kind),spec,bins=2)
            add('named-'+state+'-'+str(kind)+'-sticky',spec,bins=2,initial_eop=True)
    for kind in range(3):
        spec=base_spec(kind,bins=2);add('named-sticky-all-skipped-'+str(kind),spec,bins=2,flags=[0,0],initial_eop=True)
        spec['residues'][0].update(begin=2,end=2);add('named-sticky-empty-span-'+str(kind),spec,bins=2,initial_eop=True)
        spec=base_spec(kind,bins=2);spec['books'][0]['lengths']=[0]
        add('named-empty-phrase-'+str(kind),spec,bins=2);add('named-empty-phrase-sticky-'+str(kind),spec,bins=2,initial_eop=True)
    spec=base_spec(1,channels=16,bins=1);spec['residues']=[dict(spec['residues'][0])for _ in range(64)]
    mapping=dict(pairs=[(0,15)],mux=list(range(16)),submaps=[(255-i,0,48+i)for i in range(16)])
    spec['mappings']=[r.clone(mapping)for _ in range(64)]
    add('named-mapping63-residue63-submaps16',spec,bins=1,mapping=63)
    # Four sign branches and zeros, plus256 reverse steps at the full channel field.
    for mvalue in(0,ONE,ONE|0x80000000):
        for avalue in(0,ONE,ONE|0x80000000):
            spec=base_spec(1,bins=1,classes=2);spec['books'][1]['minimum_bits']=mvalue;spec['books'].append(book(minimum=avalue));spec['residues'][0].update(cascades=[1,1],books=[1,2]);spec['mappings'][0]['pairs']=[(0,1)]
            add(f'named-signs-{mvalue}-{avalue}',spec,bins=1,phrase_entry=lambda ch,group,rid:ch)
    spec=base_spec(1,channels=255,bins=1);spec['mappings'][0]['pairs']=[(i%254,(i%254)+1)for i in range(256)]
    add('named-channels255-coupling256',spec,bins=1,flags=[1]+[0]*254)
    # Coupling across independently decoded submaps, including an unassigned one.
    spec=base_spec(1,channels=4,bins=3);spec['books'].append(book(minimum=ONE|0x80000000));spec['residues'].append(dict(spec['residues'][0],books=[2]));spec['residues'].append(dict(spec['residues'][0],books=[1]));spec['books'].append(book(minimum=1,delta=HUGE));spec['residues'][2]['books']=[3]
    spec['mappings'][0]=dict(pairs=[(0,1),(3,2)],mux=[1,0,1,0],submaps=[(255,0,0),(128,0,1),(7,0,2)])
    add('named-cross-submap-and-unassigned',spec,bins=3)
    for sign in(0,0x80000000):
        spec=base_spec(1,bins=1,classes=2,passes=1);spec['books']=[spec['books'][0],book(minimum=HUGE),book(minimum=1|sign),book(minimum=HUGE|0x80000000),book()];spec['residues'][0].update(cascades=[7,1],books=[1,2,3,4]);spec['mappings'][0]['pairs']=[(0,1)]
        add('named-three-pass-cancel-'+str(sign),spec,bins=1,phrase_entry=lambda ch,group,rid:ch)
        spec=base_spec(1,bins=1,classes=2);spec['books']=[spec['books'][0],book(minimum=1|sign,delta=HUGE),book(minimum=0,delta=HUGE|0x80000000),book()];spec['residues'][0].update(cascades=[3,1],books=[1,2,3]);spec['mappings'][0]['pairs']=[(0,1)]
        add('named-affine-cancel-width34-'+str(sign),spec,bins=1,phrase_entry=lambda ch,group,rid:ch)
    spec=base_spec(1,bins=1,passes=2);spec['books']=[spec['books'][0],book(minimum=HUGE,delta=0x80000001,width=1),book(minimum=1,width=1)];spec['residues'][0]['books']=[1,2]
    add('named-long-borrow-then-carry',spec,bins=1)
    spec=base_spec(2,bins=1,dimension=65535,sequence=1);spec['books'][1].update(minimum_bits=1,delta_bits=HUGE);spec['residues'][0]['partition_size']=65535
    add('named-max-dim-width34-no-partition',spec,bins=1)
    spec=base_spec(1,bins=1,classes=64,passes=8);add('named-classifications64-all-passes',spec,bins=1,phrase_entry=lambda ch,group,rid:63)
    spec=base_spec(1,bins=1);spec['books']=[spec['books'][0]]+[book(minimum=ONE+i)for i in range(255)];spec['residues'][0]['books']=[255]
    add('named-books256-last-stage',spec,bins=1)
    spec=base_spec(1,channels=1,bins=4096);spec['residues'][0].update(begin=0xffffff,end=0xffffff);add('named-bins4096-clipped',spec,bins=4096)
    # A real complete65535-component VQ word fits this host's measured fixture
    # limit; native selection excludes its139264 limbs explicitly.
    spec=base_spec(2,channels=17,bins=4096,dimension=65535,sequence=1);spec['books'][1].update(minimum_bits=ONE,delta_bits=ONE);spec['residues'][0].update(end=17*4096,partition_size=65535)
    add('host-full-dimension65535',spec,bins=4096)
    rng=random.Random(0x8E51D0)
    for i in range(100):
        kind=i%3;channels=1+i%4;bins=(1,3,7,16)[i%4];dim=(1,2,3)[i%3];spec=base_spec(kind,channels=channels,bins=bins,dimension=dim,sequence=i%2,passes=(1,2,8)[i%3]);spec['books'][1].update(minimum_bits=rng.getrandbits(32),delta_bits=rng.getrandbits(32),value_bits=1+i%16,lookup=2 if i%2 else 1)
        if channels>1:spec['mappings'][0]['pairs']=[(0,ch)for ch in range(1,channels)]
        add('random-'+str(i),spec,bins=bins,flags=[int(rng.randrange(3)!=0)for _ in range(channels)],start=i%8,seed=i)
    # Transport padding is part of the immutable packet, not extra residue words.
    row=original[0];body=bytes.fromhex(row['packet_hex'])+b'\xff';original.append(dict(row,id='named-ignored-trailing-bits',packet_hex=body.hex(),packet_bits=len(body)*8))
    suitable=[row for row in original if measure(row,context(row['identification_hex'],row['identification_bits'],row['setup_hex'],row['setup_bits'])[0])['limb_count']<=4096 and len(row['setup_hex'])<=65536]
    critical=[row for row in suitable if row['id'].startswith('named-')];other=[row for row in suitable if not row['id'].startswith('named-')];need(len(critical)<=200<=len(suitable),'predeclared native200 budget');remaining=200-len(critical);selected=critical+[other[i*len(other)//remaining]for i in range(remaining)]if remaining else critical
    host=[]
    for row in original:
        host.append(row);wanted=expected_case(row)['exact']
        if wanted['packet_status']==0 and not wanted['state']['stopped_on_eop']and not row['initial_eop']:
            for cut in range(row['start_bit'],wanted['position']):host.append(dict(row,id=row['id']+'-cut'+str(cut),packet_bits=cut))
    return dict(schema='native-vorbis-residue-cases-v1',cases=host),dict(schema='native-vorbis-residue-cases-v1',cases=selected)

CASE_KEYS={'id','identification_hex','identification_bits','setup_hex','setup_bits','packet_hex','packet_bits','start_bit','initial_eop','mapping','bins','floor_present'}
def validate_model(model):
    need(set(model)=={'schema','cases'}and model['schema']=='native-vorbis-residue-cases-v1','residue model schema');rows=model['cases'];need(type(rows)is list and 1<=len(rows)<=40000,'finite scientific rows');seen=set()
    for case in rows:
        need(set(case)==CASE_KEYS and re.fullmatch(r'[A-Za-z0-9_-]{1,63}',case['id'])and case['id']not in seen,'unique original case fields');seen.add(case['id'])
        for stem in('identification','setup','packet'):
            body=case[stem+'_hex'];bits=case[stem+'_bits'];need(type(body)is str and re.fullmatch(r'(?:[0-9a-f]{2})*',body)and len(body)<=2097152 and type(bits)is int and 0<=bits<=4*len(body),'bounded complete bytes/explicit bit extent')
        need(type(case['start_bit'])is int and 0<=case['start_bit']<=case['packet_bits']and type(case['initial_eop'])is bool and type(case['mapping'])is int and 0<=case['mapping']<=63 and type(case['bins'])is int and 1<=case['bins']<=4096,'cursor/mapping/bins fields')
        need(type(case['floor_present'])is list and 1<=len(case['floor_present'])<=255 and all(type(value)is int and value in(0,1)for value in case['floor_present']),'exact boolean floor presence bytes')
    return rows
class Reader:
    def __init__(self,body):self.body,self.at=body,0
    def take(self,fmt):
        size=struct.calcsize(fmt);need(self.at+size<=len(self.body),'complete binary field');values=struct.unpack_from(fmt,self.body,self.at);self.at+=size;return values[0]if len(values)==1 else values

def encode_input(model):
    body=bytearray(b'RESTEST1'+struct.pack('<I',len(validate_model(model))))
    for case in model['cases']:
        name=case['id'].encode('ascii');body+=struct.pack('<I',len(name))+name
        for stem in('identification','setup','packet'):
            raw=bytes.fromhex(case[stem+'_hex']);body+=struct.pack('<I',len(raw))+raw+struct.pack('<Q',case[stem+'_bits'])
        body+=struct.pack('<QIIII',case['start_bit'],int(case['initial_eop']),case['mapping'],case['bins'],len(case['floor_present']))+bytes(case['floor_present'])
    return bytes(body)
def decode_input(body):
    reader=Reader(body);need(reader.take('<8s')==b'RESTEST1','residue input magic');count=reader.take('<I');need(1<=count<=40000,'finite binary count');rows=[]
    for _ in range(count):
        n=reader.take('<I');need(1<=n<=63,'bounded case id');row=dict(id=reader.take('<'+str(n)+'s').decode('ascii'))
        for stem in('identification','setup','packet'):
            n=reader.take('<I');need(n<=1048576,'bounded raw packet');row[stem+'_hex']=reader.take('<'+str(n)+'s').hex();row[stem+'_bits']=reader.take('<Q')
        start,eop,mapping,bins,n=reader.take('<QIIII');need(eop in(0,1)and 1<=n<=255,'cursor/flag count');row.update(start_bit=start,initial_eop=bool(eop),mapping=mapping,bins=bins,floor_present=[reader.take('<B')for _ in range(n)]);rows.append(row)
    need(reader.at==len(body),'all input bytes consumed');model=dict(schema='native-vorbis-residue-cases-v1',cases=rows);validate_model(model);return model

def decode_output(body,model):
    rows=validate_model(model);reader=Reader(body);need(reader.take('<8s')==b'RESOUT01'and reader.take('<I')==len(rows),'exact output magic/count');controls=reader.take('<I');need(controls==CONTROL_COUNT,'actual fixed control count');observed=[]
    def array():
        count=reader.take('<I');need(count<=1048576,'concrete captured limb count');return[reader.take('<I')for _ in range(count)]
    for i,case in enumerate(rows):
        need(reader.take('<I')==i,'ordered case ordinal');ms=reader.take('<i');layout=dict(zip(LFIELDS,reader.take('<IIIIIiQQQ')))if ms==0 else None;ps=reader.take('<i');state=dict(zip(('classwords','vectors','values','stopped_on_eop'),reader.take('<QQQI')))if ps==0 else None;decoded=array();cs=reader.take('<i');coupled=array();position,eop,guards=reader.take('<QII');need(eop in(0,1)and guards==7,'actual guarded input preservation')
        observed.append(dict(case=i,id=case['id'],measure_status=ms,layout=layout,packet_status=ps,state=state,decoded_limbs=decoded,coupling_status=cs,coupled_limbs=coupled,position=position,end_of_packet=bool(eop),guards=1,unchanged=1))
    need(reader.at==len(body),'complete output stream');return dict(metadata_controls=controls,rows=observed)

def compare_all(model,observed,expected=None,native=False):
    rows=validate_model(model);need(len(rows)==len(observed),'every original result compared')
    if expected is not None:need(expected['schema']=='native-vorbis-residue-expected-v1'and expected['policy']==POLICY and len(expected['cases'])==len(rows),'fixed independent expected policy')
    metrics=[];failures=[]
    for i,(case,actual)in enumerate(zip(rows,observed)):
        try:
            need(actual['case']==i and actual['id']==case['id']and actual['guards']==actual['unchanged']==1,'actual guarded case identity');wanted=expected_case(case)
            if expected is not None:need(wanted==expected['cases'][i],'regenerated expected exact values')
            reasons=['exact '+key for key,value in wanted['exact'].items()if actual[key]!=value];state=actual['state'];part={key:actual[key]for key in wanted['exact']};metric=dict(id=case['id'],qualified=not reasons,failure_reasons=reasons,packet_status=actual['packet_status'],samples=wanted['exact']['layout']['sample_count'],limbs=wanted['exact']['layout']['limbs'],limb_values_compared=len(actual['decoded_limbs'])+len(actual['coupled_limbs']),classwords=0 if state is None else state['classwords'],vectors=0 if state is None else state['vectors'],values=0 if state is None else state['values'],nominal_EOP=state is not None and state['stopped_on_eop']==1,expected_sha256=sha(json.dumps(wanted['exact'],sort_keys=True).encode()),actual_sha256=sha(json.dumps(part,sort_keys=True).encode()))
            if reasons:metric.update(expected=wanted,actual=actual);failures.append(dict(index=i,**metric))
            metrics.append(metric)
        except(ValueError,KeyError,TypeError,struct.error)as error:failures.append(dict(index=i,id=case['id'],nonmeasurement_error=str(error),actual=actual))
    return dict(measurement_completed=len(metrics)==len(rows),passed=not failures and len(metrics)==len(rows),cases=len(rows),metrics=metrics,failures=failures,limb_values_compared=sum(v['limb_values_compared']for v in metrics),classwords=sum(v['classwords']for v in metrics),vectors=sum(v['vectors']for v in metrics),values=sum(v['values']for v in metrics),nominal_EOP_rows=sum(v['nominal_EOP']for v in metrics),maximum_limb_width=max((v['limbs']for v in metrics),default=0),floor_or_G6_or_PCM_qualified=False)
def compare_target_rows(model,expected,observed):return compare_all(model,observed,expected,native=True)

def target_header(model):
    rows=validate_model(model);lines=['#pragma once','#include <stddef.h>','#include <stdint.h>','#define RESIDUE_CASE_COUNT '+str(len(rows)),
        'typedef struct { const char *id; const uint8_t *identification; uint32_t identification_bytes; uint64_t identification_bits;',
        ' const uint8_t *setup; uint32_t setup_bytes; uint64_t setup_bits; const uint8_t *packet; uint32_t packet_bytes; uint64_t packet_bits;',
        ' uint64_t start_bit; uint32_t initial_eop,mapping,bins; const uint8_t *floor_present; uint32_t flag_count; } residue_case_t;']
    for i,case in enumerate(rows):
        for stem in('identification','setup','packet'):
            body=bytes.fromhex(case[stem+'_hex'])
            if body:lines.append('static const uint8_t residue_'+stem+'_'+str(i)+'[] = {'+','.join('UINT8_C(0x'+f'{value:02x}'+')'for value in body)+'};')
        lines.append('static const uint8_t residue_flags_'+str(i)+'[] = {'+','.join('UINT8_C(0x'+f'{value:02x}'+')'for value in case['floor_present'])+'};')
    lines.append('static const residue_case_t residue_cases[RESIDUE_CASE_COUNT] = {')
    for i,case in enumerate(rows):
        values=['"'+case['id']+'"']
        for stem in('identification','setup','packet'):values.extend(['residue_'+stem+'_'+str(i)if case[stem+'_hex']else'NULL',str(len(case[stem+'_hex'])//2),'UINT64_C('+str(case[stem+'_bits'])+')'])
        values+=['UINT64_C('+str(case['start_bit'])+')',str(int(case['initial_eop'])),str(case['mapping']),str(case['bins']),'residue_flags_'+str(i),str(len(case['floor_present']))];lines.append('    {'+','.join(values)+'},')
    return '\n'.join(lines+['};',''])

def self_checks():
    tiny=Fraction(1,1<<788);large=Fraction(1<<255);need(packed(1)==tiny and packed(HUGE)==large,'independent packed extreme witnesses')
    need((large+tiny)-large==tiny and float(float(large)+float(tiny))-float(large)==0,'exact cancellation counterexample')
    mapping=dict(pairs=[(0,1)]);need(couple([[tiny],[Fraction(1)]],mapping)==[[tiny],[tiny-1]],'tiny positive magnitude chooses correct branch')
    need(couple([[Fraction(0)],[Fraction(1)]],mapping)==[[0],[1]],'zero magnitude has a different legal branch')
    layout=dict(limbs=34,exponent=-788,magnitude_bits=1079);words=limb_array([[-tiny]],layout);need(words==[0xffffffff]*34,'negative quantum sign extension across all limbs')
    need(propagated(dict(pairs=[(1,2),(0,1)]),[1,0,0])==[1,1,0],'one forward propagation pass is not closure')
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
        freeze(Path(__file__),'test-vorbis-residue.py');need(sha(freeze(REFERENCE_PATH,'reference-setup.py'))==REFERENCE_SHA,'frozen independent reference identity');freeze(COMPONENT/'floor0.c','floor0.c')
        freeze(COMPONENT/'residue.c','residue.c');freeze(COMPONENT/'include/native_vorbis_residue.h','native_vorbis_residue.h');freeze(COMPONENT/'floor_packet.c','floor_packet.c');freeze(COMPONENT/'include/native_vorbis_floor_packet.h','native_vorbis_floor_packet.h');freeze(COMPONENT/'setup.c','setup.c');freeze(COMPONENT/'include/native_vorbis_setup.h','native_vorbis_setup.h');freeze(COMPONENT/'codebook.c','codebook.c');freeze(COMPONENT/'include/native_vorbis_codebook.h','native_vorbis_codebook.h');freeze(COMPONENT/'quant.c','quant.c');freeze(COMPONENT/'include/native_vorbis_floor0.h','native_vorbis_floor0.h')
        freeze(COMPONENT/'include/native_vorbis_quant.h','native_vorbis_quant.h');freeze(COMPONENT/'CMakeLists.txt','CMakeLists.txt');freeze(DRIVER,'driver.c')
        owner=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-owner.py')
        nodes=[node for node in ast.parse(owner).body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(nodes)==1,'one existing nonce-owned supervisor literal');(out/'supervisor.py').write_text(ast.literal_eval(nodes[0].value),encoding='utf-8',newline='\n')
        report['oracle_self_checks']=self_checks()
        model,target=cases();inputs=encode_input(model);need(decode_input(inputs)==model,'complete exact raw packet/affine input roundtrip')
        (out/'cases.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');(out/'inputs.bin').write_bytes(inputs)
        directory=out/'target-cases';expected=dict(schema='native-vorbis-residue-expected-v1',policy=POLICY,cases=[expected_case(row) for row in target['cases']])
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
        so,se=run('compile',flags+['-I'+host(out/'sources'),host(out/'sources/driver.c'),host(out/'sources/floor0.c'),host(out/'sources/quant.c'),host(out/'sources/codebook.c'),host(out/'sources/setup.c'),host(out/'sources/floor_packet.c'),host(out/'sources/residue.c'),'-lm','-o',host(out/'test')])
        need(not so and not se,'clean strict whole-component compile');current()
        so,se=run('execute',[host(out/'test'),host(out/'inputs.bin'),host(out/'outputs.bin')]);report['component_executed']=True;need(not so and not se,'clean actual sanitized residue execution')
        output=(out/'outputs.bin').read_bytes();decoded=decode_output(output,model);measured=compare_all(model,decoded['rows']);current()
        report.update(completed=True,passed=measured['passed'],source_inputs_unchanged=True,numerical=measured,metadata_controls=decoded['metadata_controls'],output_sha256=sha(output),
            result='OWNED_RESIDUE_EXACT_QUALIFIED' if measured['passed'] else 'OWNED_RESIDUE_EXACT_REJECTED')
        save();print(json.dumps(dict(completed=True,passed=report['passed'],cases=report['cases'],target_cases=report['target_cases'],result=report['result'],limb_values_compared=measured['limb_values_compared'],values=measured['values'],nominal_EOP_rows=measured['nominal_EOP_rows'],maximum_limb_width=measured['maximum_limb_width'])));return 0 if report['passed'] else 1
    except BaseException as error:report.update(completed=False,passed=False,error=repr(error));save();raise

if __name__=='__main__':sys.exit(main())


