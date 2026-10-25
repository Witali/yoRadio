"""Independent Vorbis identification/full-setup oracle, fields and context links.

Primary: Vorbis I sections3/4/6/7/8. Greedy codebook assignment reuses the
independently reviewed interval formulation, never the production parser.
"""
import argparse
import ast
import hashlib
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
DRIVER=ROOT/'tests/native/vorbis_setup_test.c'
PUBLIC_FIXTURE=ROOT/'tests/target/cyd_vorbis_format_qemu/main/fixture.h'
PUBLIC_SHA='839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378'
CONTROL_COUNT=60
IDFIELDS=('channels','sample_rate','bitrate_maximum_bits','bitrate_nominal_bits','bitrate_minimum_bits','blocksize_0','blocksize_1')
QFIELDS=('dimensions','entries','lookup_type','minimum_bits','delta_bits','value_bits','sequence_p','multiplicand_count','start_bit','multiplicand_bit','end_bit')
LFIELDS=('book_count','time_count','floor_count','residue_count','mapping_count','mode_count','configuration_count','floor_table','residue_table','mapping_table','mode_table')
SENTINEL=0xffffffff
POLICY=dict(schema='native-vorbis-setup-policy-v1',exact_comparison=True,oracle='Independent raw-bit/context parser and greedy lexical codebook intervals',
    floor0_zero_fields='Preserved descriptors; active curve zero-domain is unqualified',inverted_residue_ranges='Preserved descriptors',
    ignored_mapping_time_bytes='Preserved without rejecting nonzero',host_all_bit_truncations=True,native_repeats_host_truncations=False,
    selected_before_measurement=True,full_decoder_or_PCM_qualification=False)
class Invalid(ValueError):pass
class Truncated(ValueError):pass
def need(ok,reason):
    if not ok:raise Invalid(reason)
def sha(body):return hashlib.sha256(body).hexdigest()
class Bits:
    def __init__(self,body,extent,position=0):
        need(type(extent)is int and type(position)is int and 0<=position<=extent<=8*len(body),'valid explicit bit extent')
        self.body=body;self.raw=int.from_bytes(body,'little');self.extent=extent;self.position=position
    def take(self,width):
        need(type(width)is int and 0<=width<=64,'valid raw width')
        if self.position+width>self.extent:raise Truncated('raw field crosses valid bit extent')
        result=(self.raw>>self.position)&((1<<width)-1);self.position+=width;return result
def greedy_words(lengths):
    """Allocate the first aligned free interval, without Xiph markers/lengthsort."""
    gaps=[(0,1<<32)];words=[]
    for entry,length in enumerate(lengths):
        if not length:continue
        need(1<=length<=32,'legal used codeword length');span=1<<(32-length)
        for i,(low,high) in enumerate(gaps):
            start=((low+span-1)//span)*span
            if start+span<=high:
                replacement=[]
                if low<start:replacement.append((low,start))
                if start+span<high:replacement.append((start+span,high))
                gaps[i:i+1]=replacement;words.append(dict(code=start,entry=entry,length=length));break
        else:raise ValueError('oversubscribed lexical tree')
    if len(words)==1:need(words[0]['length']==1,'singleton length1 erratum')
    elif words:need(not gaps,'complete nonsingleton prefix tree')
    return sorted(words,key=lambda row:row['code'])

def integer_root(entries,dimension):
    need(dimension>0,'lookup1 has positive dimension');low,high=0,1<<((entries.bit_length()+dimension-1)//dimension)
    while low+1<high:
        middle=(low+high)//2
        if middle**dimension<=entries:low=middle
        else:high=middle
    return high if high**dimension<=entries else low

def parse_book(case):
    r=Bits(bytes.fromhex(case['packet_hex']),case['packet_bits'],case['start_bit'])
    need(r.take(24)==0x564342,'Vorbis codebook sync');dimension,entries=r.take(16),r.take(24);ordered=r.take(1);lengths=[]
    if ordered:
        length=r.take(5)+1
        while len(lengths)<entries:
            need(length<=32,'maximum ordered codeword length32');count=r.take((entries-len(lengths)).bit_length())
            need(count<=entries-len(lengths),'ordered run fits declared entries');lengths.extend([length]*count);length+=1
    else:
        sparse=r.take(1)
        for _ in range(entries):lengths.append(r.take(5)+1 if not sparse or r.take(1) else 0)
    words=greedy_words(lengths);quant_start=r.position;lookup=r.take(4);need(lookup<=2,'public lookup type')
    minimum=delta=width=sequence=count=0;weights=[]
    if lookup:
        minimum,delta,width,sequence=r.take(32),r.take(32),r.take(4)+1,r.take(1)
        count=integer_root(entries,dimension) if lookup==1 else entries*dimension
    mult_start=r.position
    for _ in range(count):weights.append(r.take(width))
    q=dict(zip(QFIELDS,(dimension,entries,lookup,minimum,delta,width,sequence,count,quant_start,mult_start,r.position)))
    layout=dict(start_bit=case['start_bit'],used_entries=len(words),maximum_length=max(lengths,default=0),quantization=q)
    return layout,words,weights


def signature(r,kind):
    need(r.take(8)==kind and bytes(r.take(8)for _ in range(6))==b'vorbis','complete Vorbis header signature/type')
def identification(body,extent):
    r=Bits(body,extent);signature(r,1);need(r.take(32)==0,'version0');channels,rate=r.take(8),r.take(32)
    maximum,nominal,minimum=r.take(32),r.take(32),r.take(32);small,large=r.take(4),r.take(4)
    need(channels>0 and rate>0 and 6<=small<=large<=13 and r.take(1)==1,'identification channels/rate/blocks/framing')
    return dict(zip(IDFIELDS,(channels,rate,maximum,nominal,minimum,1<<small,1<<large)))
def parse_setup(body,extent,id_info):
    r=Bits(body,extent);signature(r,5);book_count=r.take(8)+1;books=[];words=[];weights=[]
    for _ in range(book_count):
        book,own_words,own_weights=parse_book(dict(packet_hex=body.hex(),packet_bits=extent,start_bit=r.position));r.position=book['quantization']['end_bit']
        books.append(dict(layout=book,words=own_words,multiplicands=own_weights));words+=own_words;weights+=own_weights
    time_count=r.take(6)+1
    for _ in range(time_count):need(r.take(16)==0,'time transform placeholder must0')
    config=[];floors=[];residues=[];mappings=[];modes=[]
    def table(count):at=len(config);config.extend([0]*count);return at
    def append(values):at=len(config);config.extend(values);return at
    def book_id(index,vq=False):
        need(0<=index<book_count,'configured book reference');q=books[index]['layout']['quantization']
        if vq:need(q['lookup_type']in(1,2)and q['dimensions']>0,'positive-dimension VQ context')
        return q
    floor_count=r.take(6)+1;floor_table=table(floor_count)
    for i in range(floor_count):
        kind=r.take(16);need(kind<=1,'supported floor type')
        if kind==0:
            order,rate,bark,abits,offset,count=r.take(8),r.take(16),r.take(16),r.take(6),r.take(8),r.take(4)+1
            ids=[r.take(8)for _ in range(count)]
            for index in ids:book_id(index,True)
            record=[0,order,rate,bark,abits,offset,count]+ids;floor=dict(type=0,order=order,rate=rate,bark_map_size=bark,amplitude_bits=abits,amplitude_offset=offset,books=ids)
        else:
            partitions=[r.take(4)for _ in range(r.take(5))];class_count=max(partitions,default=-1)+1;classes=[];class_offsets=[]
            for _ in range(class_count):
                dim,sub=r.take(3)+1,r.take(2);master=r.take(8)if sub else SENTINEL
                if sub:book_id(master)
                subs=[r.take(8)-1 for _ in range(1<<sub)]
                for index in subs:
                    if index>=0:book_id(index)
                encoded=[SENTINEL if index<0 else index for index in subs]
                class_offsets.append(append([dim,sub,master]+encoded));classes.append(dict(dimensions=dim,subclass_bits=sub,masterbook=master,books=encoded))
            multiplier,range_bits=r.take(2)+1,r.take(4);post_count=2+sum(classes[c]['dimensions']for c in partitions)
            need(post_count<=65,'floor1 has at most65 total posts');x=[0,1<<range_bits]+[r.take(range_bits)for _ in range(post_count-2)]
            need(len(set(x))==len(x),'floor1 X posts unique')
            record=[1,len(partitions),class_count,multiplier,range_bits,post_count]+partitions+class_offsets+x
            floor=dict(type=1,partitions=partitions,classes=classes,class_offsets=class_offsets,multiplier=multiplier,range_bits=range_bits,x=x)
        config[floor_table+i]=append(record);floors.append(floor)
    residue_count=r.take(6)+1;residue_table=table(residue_count)
    for i in range(residue_count):
        kind=r.take(16);need(kind<=2,'supported residue type');begin,end,partition,classes,phrase=r.take(24),r.take(24),r.take(24)+1,r.take(6)+1,r.take(8)
        q=book_id(phrase);need(q['dimensions']>0 and classes**q['dimensions']<=q['entries'],'phrasebook classification capacity')
        cascades=[]
        for _ in range(classes):
            low=r.take(3);high=r.take(5)if r.take(1)else 0;cascades.append(low+8*high)
        active=[];offsets=[]
        for cascade in cascades:
            offsets.append(len(active))
            for stage in range(8):
                if cascade&(1<<stage):
                    index=r.take(8);q=book_id(index,True);need(partition%q['dimensions']==0,'partition divisible by active VQ dimensions');active.append(index)
        record=[kind,begin,end,partition,classes,phrase,len(active)]+cascades+offsets+active;config[residue_table+i]=append(record)
        residues.append(dict(type=kind,begin=begin,end=end,partition_size=partition,classifications=classes,classbook=phrase,cascades=cascades,book_offsets=offsets,books=active))
    mapping_count=r.take(6)+1;mapping_table=table(mapping_count);channels=id_info['channels'];width=(channels-1).bit_length()
    for i in range(mapping_count):
        need(r.take(16)==0,'mapping type0');submaps=r.take(4)+1 if r.take(1)else 1;coupling=r.take(8)+1 if r.take(1)else 0;pairs=[]
        for _ in range(coupling):
            mag,angle=r.take(width),r.take(width);need(mag!=angle and mag<channels and angle<channels,'distinct valid coupling channels');pairs.extend((mag,angle))
        need(r.take(2)==0,'mapping reserved bits0');mux=[r.take(4)for _ in range(channels)]if submaps>1 else[0]*channels;need(all(x<submaps for x in mux),'channel mux submap range')
        triples=[]
        for _ in range(submaps):
            ignored,floor,residue=r.take(8),r.take(8),r.take(8);need(floor<floor_count and residue<residue_count,'mapping floor/residue references');triples.extend((ignored,floor,residue))
        config[mapping_table+i]=append([submaps,coupling,channels]+pairs+mux+triples);mappings.append(dict(submap_count=submaps,coupling_count=coupling,channels=channels,coupling_pairs=pairs,mux=mux,submaps=triples))
    mode_count=r.take(6)+1;mode_table=table(mode_count)
    for i in range(mode_count):
        block=r.take(1);need(r.take(16)==0 and r.take(16)==0,'window/transform type0');mapping=r.take(8);need(mapping<mapping_count,'mode mapping reference')
        config[mode_table+i]=append([block,mapping]);modes.append(dict(blockflag=block,mapping=mapping))
    need(r.take(1)==1,'setup framing1')
    layout=dict(identification=id_info,end_bit=r.position,codeword_count=len(words),multiplicand_count=len(weights),book_count=book_count,time_count=time_count,
        floor_count=floor_count,residue_count=residue_count,mapping_count=mapping_count,mode_count=mode_count,configuration_count=len(config),
        floor_table=floor_table,residue_table=residue_table,mapping_table=mapping_table,mode_table=mode_table)
    return dict(layout=layout,books=books,configuration=config,getter_values=getter_values(floors,residues,mappings,modes),modes=modes)

def getter_values(floors,residues,mappings,modes):
    result=[]
    for floor in floors:
        result.append(floor['type'])
        if floor['type']==0:result +=[floor[k]for k in ('order','rate','bark_map_size','amplitude_bits','amplitude_offset')]+[len(floor['books'])]+floor['books']
        else:
            result +=[len(floor['partitions']),len(floor['classes']),floor['multiplier'],floor['range_bits'],len(floor['x'])]+floor['partitions']+floor['class_offsets']+floor['x']
            for cls in floor['classes']:result +=[cls['dimensions'],cls['subclass_bits'],cls['masterbook'],len(cls['books'])]+cls['books']
    for residue in residues:result +=[residue[k]for k in ('type','begin','end','partition_size','classifications','classbook')]+[len(residue['books'])]+residue['cascades']+residue['book_offsets']+residue['books']
    for mapping in mappings:result +=[mapping[k]for k in ('submap_count','coupling_count','channels')]+mapping['coupling_pairs']+mapping['mux']+mapping['submaps']
    for mode in modes:result +=[mode['blockflag'],mode['mapping']]
    return result

def audio_prefix(case,id_info,modes):
    r=Bits(bytes.fromhex(case['audio_hex']),case['audio_bits'],case['audio_start']);need(r.take(1)==0,'audio packet type0');mode=r.take((len(modes)-1).bit_length());need(mode<len(modes),'audio mode range')
    block=modes[mode]['blockflag'];previous,next_flag=(r.take(1),r.take(1))if block else(0,0)
    return dict(mode=mode,blockflag=block,previous_window=previous,next_window=next_flag,mapping=modes[mode]['mapping'],blocksize=id_info['blocksize_1'if block else'blocksize_0'],position=r.position,end_of_packet=0)
class Writer:
    def __init__(self):self.bits=[];self.labels={}
    def put(self,value,width,label=None):
        if label:self.labels[label]=(len(self.bits),width)
        self.bits.extend((value>>i)&1 for i in range(width))
    def octets(self):
        body=bytearray((len(self.bits)+7)//8)
        for i,value in enumerate(self.bits):body[i//8]|=value<<(i%8)
        return body.hex()
    def sig(self,kind):
        self.put(kind,8,'type')
        for i,value in enumerate(b'vorbis'):self.put(value,8,f'signature{i}')
def book_bits(w,book,prefix):
    lengths=book['lengths'];w.put(0x564342,24,prefix+'.sync');w.put(book['dimensions'],16,prefix+'.dimensions');w.put(len(lengths),24,prefix+'.entries');w.put(0,1);sparse=0 in lengths;w.put(int(sparse),1)
    for length in lengths:
        if sparse:w.put(int(bool(length)),1)
        if length:w.put(length-1,5)
    lookup=book.get('lookup',0);w.put(lookup,4,prefix+'.lookup')
    if lookup:
        width=book.get('value_bits',16);w.put(book.get('minimum_bits',0x80000000),32);w.put(book.get('delta_bits',0x62800001),32);w.put(width-1,4);w.put(book.get('sequence',0),1)
        count=integer_root(len(lengths),book['dimensions'])if lookup==1 and book['dimensions'] else len(lengths)*book['dimensions']if lookup==2 else 0
        for i in range(count):w.put(((1<<width)-1)-i%((1<<width)),width)
def identification_writer(spec):
    w=Writer();w.sig(1);w.put(spec.get('version',0),32,'version');w.put(spec['channels'],8,'channels');w.put(spec['rate'],32,'rate')
    for key in ('maximum','nominal','minimum'):w.put(spec.get(key,0),32,key)
    w.put(spec['small'],4,'small');w.put(spec['large'],4,'large');w.put(1,1,'framing');return w

def setup_writer(spec):
    w=Writer();w.sig(5);w.put(len(spec['books'])-1,8,'book_count')
    for i,book in enumerate(spec['books']):book_bits(w,book,f'book{i}')
    w.put(spec.get('times',1)-1,6,'time_count')
    for i in range(spec.get('times',1)):w.put(0,16,f'time{i}')
    w.put(len(spec['floors'])-1,6,'floor_count')
    for i,floor in enumerate(spec['floors']):
        p=f'floor{i}';w.put(floor['type'],16,p+'.type')
        if floor['type']==0:
            for key,width in (('order',8),('rate',16),('bark',16),('amplitude_bits',6),('amplitude_offset',8)):w.put(floor[key],width,p+'.'+key)
            w.put(len(floor['books'])-1,4,p+'.book_count')
            for j,value in enumerate(floor['books']):w.put(value,8,p+f'.book{j}')
        else:
            partitions=floor['partitions'];classes=floor['classes'];w.put(len(partitions),5,p+'.partitions')
            for j,value in enumerate(partitions):w.put(value,4,p+f'.partition{j}')
            for j,cls in enumerate(classes):
                q=p+f'.class{j}';w.put(cls['dimensions']-1,3,q+'.dimensions');w.put(cls['subclass_bits'],2,q+'.subclass_bits')
                if cls['subclass_bits']:w.put(cls['masterbook'],8,q+'.masterbook')
                for k,value in enumerate(cls['books']):w.put(value+1,8,q+f'.book{k}')
            w.put(floor['multiplier']-1,2,p+'.multiplier');w.put(floor['range_bits'],4,p+'.range_bits')
            for j,value in enumerate(floor['x']):w.put(value,floor['range_bits'],p+f'.x{j}')
    w.put(len(spec['residues'])-1,6,'residue_count')
    for i,residue in enumerate(spec['residues']):
        p=f'residue{i}';w.put(residue['type'],16,p+'.type')
        for key,width,offset in (('begin',24,0),('end',24,0),('partition_size',24,1),('classifications',6,1),('classbook',8,0)):w.put(residue[key]-offset,width,p+'.'+key)
        for j,cascade in enumerate(residue['cascades']):
            w.put(cascade&7,3,p+f'.cascade{j}.low');w.put(int(cascade>7),1,p+f'.cascade{j}.flag')
            if cascade>7:w.put(cascade>>3,5,p+f'.cascade{j}.high')
        for j,value in enumerate(residue['books']):w.put(value,8,p+f'.book{j}')
    w.put(len(spec['mappings'])-1,6,'mapping_count');channels=spec['identification']['channels']
    for i,mapping in enumerate(spec['mappings']):
        p=f'mapping{i}';w.put(0,16,p+'.type');submaps=len(mapping['submaps']);w.put(int(submaps>1),1,p+'.submap_flag')
        if submaps>1:w.put(submaps-1,4,p+'.submap_count')
        pairs=mapping['pairs'];w.put(int(bool(pairs)),1,p+'.coupling_flag')
        if pairs:
            w.put(len(pairs)-1,8,p+'.coupling_count')
            for j,(mag,angle)in enumerate(pairs):w.put(mag,(channels-1).bit_length(),p+f'.mag{j}');w.put(angle,(channels-1).bit_length(),p+f'.angle{j}')
        w.put(0,2,p+'.reserved')
        if submaps>1:
            for j,value in enumerate(mapping['mux']):w.put(value,4,p+f'.mux{j}')
        for j,(timebyte,floor,residue)in enumerate(mapping['submaps']):w.put(timebyte,8,p+f'.time{j}');w.put(floor,8,p+f'.floor{j}');w.put(residue,8,p+f'.residue{j}')
    w.put(len(spec['modes'])-1,6,'mode_count')
    for i,mode in enumerate(spec['modes']):
        w.put(mode['blockflag'],1,f'mode{i}.blockflag');w.put(0,16,f'mode{i}.window');w.put(0,16,f'mode{i}.transform');w.put(mode['mapping'],8,f'mode{i}.mapping')
    w.put(1,1,'framing');return w

def baseline():
    return dict(identification=dict(channels=2,rate=44101,small=6,large=13,maximum=0x80000000,nominal=0xffffffff,minimum=0),
        books=[dict(dimensions=1,lengths=[1],lookup=0),dict(dimensions=1,lengths=[1],lookup=1,sequence=1)],times=1,
        floors=[dict(type=0,order=3,rate=44101,bark=512,amplitude_bits=63,amplitude_offset=255,books=[1]),dict(type=1,partitions=[],classes=[],multiplier=1,range_bits=0,x=[])],
        residues=[dict(type=0,begin=0,end=16,partition_size=1,classifications=1,classbook=0,cascades=[1],books=[1])],
        mappings=[dict(pairs=[],mux=[0,0],submaps=[(255,0,0)])],modes=[dict(blockflag=0,mapping=0)])
def clone(spec):return json.loads(json.dumps(spec))
def make_case(identifier,spec,mode=0,previous=1,next_flag=0):
    iw=identification_writer(spec['identification']);sw=setup_writer(spec);aw=Writer();aw.put(0,1,'type');aw.put(mode,(len(spec['modes'])-1).bit_length(),'mode')
    if spec['modes'][mode]['blockflag']:aw.put(previous,1,'previous');aw.put(next_flag,1,'next')
    aw.put(5,3,'tail')
    row=dict(id=identifier,identification_hex=iw.octets(),identification_bits=len(iw.bits),setup_hex=sw.octets(),setup_bits=len(sw.bits),audio_hex=aw.octets(),audio_bits=len(aw.bits),audio_start=0)
    return row,iw,sw,aw

def mutate(row,writer,stem,label,value,identifier):
    result=dict(row,id=identifier);start,width=writer.labels[label];body=bytearray.fromhex(result[stem+'_hex'])
    for i in range(width):
        mask=1<<((start+i)%8);at=(start+i)//8
        if(value>>i)&1:body[at]|=mask
        else:body[at]&=255-mask
    result[stem+'_hex']=body.hex();return result

def expected_case(case):
    exact=dict(id_status=-99,measure_status=-99,materialize_status=-99,audio_status=-99,identification=None,layout=None,books=[],configuration=[],getter_values=[],audio=None,position=case['audio_start'],end_of_packet=False)
    cuts=dict(identification=0,setup=0,audio=0)
    try:id_info=identification(bytes.fromhex(case['identification_hex']),case['identification_bits'])
    except (Invalid,Truncated)as error:exact['id_status']=-3 if isinstance(error,Truncated)else -1;return dict(id=case['id'],exact=exact,cuts=cuts)
    exact.update(id_status=0,identification=id_info);cuts['identification']=233
    try:setup=parse_setup(bytes.fromhex(case['setup_hex']),case['setup_bits'],id_info)
    except (Invalid,Truncated)as error:
        status=-3 if isinstance(error,Truncated)else -1;exact.update(measure_status=status,materialize_status=status);return dict(id=case['id'],exact=exact,cuts=cuts)
    exact.update(measure_status=0,materialize_status=0,**{key:value for key,value in setup.items()if key!='modes'});cuts['setup']=setup['layout']['end_bit']
    try:audio=audio_prefix(case,id_info,setup['modes'])
    except (Invalid,Truncated)as error:exact.update(audio_status=-3 if isinstance(error,Truncated)else -1,end_of_packet=isinstance(error,Truncated))
    else:
        exact.update(audio_status=0,audio={key:value for key,value in audio.items()if key not in ('position','end_of_packet')},position=audio['position']);cuts['audio']=audio['position']-case['audio_start']
    return dict(id=case['id'],exact=exact,cuts=cuts)

def public_cases(body):
    need(sha(body)==PUBLIC_SHA,'unchanged public raw fixture literal source');source=body.decode('ascii')
    def array(name,kind):
        found=re.findall(r'static const '+kind+r' '+name+r'\[\]\s*=\s*\{(.*?)\};',source,re.S);need(len(found)==1,'one public literal array '+name)
        need(re.fullmatch(r'\s*(?:0|[1-9][0-9]*)(?:\s*,\s*(?:0|[1-9][0-9]*))*\s*,?\s*',found[0]),'strict public decimal literal separators')
        values=[int(x)for x in re.findall(r'[0-9]+',found[0])];need(all(x<=(255 if kind=='uint8_t'else 0xffffffff)for x in values),'public literal field widths');return values
    info,setup,packets=(bytes(array(name,'uint8_t'))for name in ('fixture_info','fixture_setup','fixture_packets'));offsets=array('fixture_offsets','uint32_t');long_modes=array('fixture_long_mode','uint8_t')
    need(len(info)==23 and len(offsets)==len(long_modes)+1 and offsets[0]==0 and offsets[-1]==len(packets) and all(a<b for a,b in zip(offsets,offsets[1:])),'complete unmodified raw header bodies/packet boundaries')
    result=[]
    for i in range(2):
        identification_body=b'\x01vorbis'+info;setup_body=b'\x05vorbis'+setup;audio=packets[offsets[i]:offsets[i+1]]
        result.append(dict(id=f'public-xiph-raw-prefix{i}',identification_hex=identification_body.hex(),identification_bits=8*len(identification_body),setup_hex=setup_body.hex(),setup_bits=8*len(setup_body),audio_hex=audio.hex(),audio_bits=8*len(audio),audio_start=0))
    return result

def cases(public_fixture=None):
    good=[];bad=[];base=baseline();row,iw,sw,aw=make_case('baseline',base);good.append(row)
    for label,value in (('type',3),('signature0',0),('version',1),('channels',0),('rate',0),('small',5),('large',14),('small',14),('framing',0)):
        bad.append(mutate(row,iw,'identification',label,value,'bad-ident-'+label+'-'+str(value)))
    for label,value in (('type',3),('signature0',0),('book0.sync',0),('time0',1),('floor0.type',2),('floor0.book0',0),('floor0.book0',2),
        ('residue0.type',3),('residue0.classbook',2),('residue0.classifications',1),('residue0.book0',0),('residue0.book0',2),
        ('mapping0.type',1),('mapping0.reserved',1),('mapping0.floor0',2),('mapping0.residue0',1),('mode0.window',1),('mode0.transform',1),('mode0.mapping',1),('framing',0)):
        bad.append(mutate(row,sw,'setup',label,value,'bad-setup-'+label.replace('.','-')+'-'+str(value)))
    bad.append(mutate(row,aw,'audio','type',1,'bad-audio-type'))
    for channels in (1,2,3,255):
        for rate in (1,44101,0x80000000,0xffffffff):
            spec=baseline();spec['identification'].update(channels=channels,rate=rate);spec['mappings'][0]['mux']=[0]*channels
            good.append(make_case(f'ident-fields-{channels}-{rate}',spec)[0])
    for small in range(6,14):
        for large in range(small,14):
            spec=baseline();spec['identification'].update(small=small,large=large);spec['modes'][0]['blockflag']=(small+large)%2
            good.append(make_case(f'block-pair-{small}-{large}',spec)[0])
    spec=baseline();spec['floors'][0].update(order=0,rate=0,bark=0,amplitude_bits=0,amplitude_offset=0);good.append(make_case('floor0-zero-descriptors',spec)[0])
    spec=baseline();spec['floors'][0].update(order=255,rate=65535,bark=65535,books=[1]*16);good.append(make_case('floor0-full-fields',spec)[0])
    spec=baseline();spec['books'][0]['dimensions']=65535;good.append(make_case('phrase-class1-dim65535',spec)[0])
    for kind in range(3):
        spec=baseline();spec['residues'][0].update(type=kind,begin=0xffffff,end=0,partition_size=1<<24);good.append(make_case(f'residue-{kind}-reversed-max-group',spec)[0])
    spec=baseline();spec['books'][1]['dimensions']=3;spec['residues'][0]['partition_size']=3
    gr,gi,gs,ga=make_case('residue-divisible-dim3',spec);good.append(gr);bad.append(mutate(gr,gs,'setup','residue0.partition_size',3,'bad-residue-nonmultiple'))
    spec=baseline();spec['books'][0]['lengths']=[6]*64;spec['residues'][0].update(classifications=64,cascades=[255]*64,books=[1]*512)
    good.append(make_case('residue-full64-cascades',spec)[0])
    spec=baseline();spec['floors'][1].update(partitions=[15],classes=[dict(dimensions=1,subclass_bits=0,masterbook=0,books=[-1])for _ in range(16)],range_bits=15,x=[32767])
    gr,gi,gs,ga=make_case('floor1-class15-gap',spec);good.append(gr);bad.append(mutate(gr,gs,'setup','floor1.class0.book0',3,'bad-floor1-unused-class-link'))
    spec=baseline();spec['floors'][1].update(partitions=[0]*30+[1],classes=[dict(dimensions=2,subclass_bits=0,masterbook=0,books=[-1]),dict(dimensions=3,subclass_bits=0,masterbook=0,books=[-1])],range_bits=7,x=list(range(1,64)))
    gr,gi,gs,ga=make_case('floor1-total65-posts',spec);good.append(gr);bad.append(mutate(gr,gs,'setup','floor1.class1.dimensions',3,'bad-floor1-total66-posts'));bad.append(mutate(gr,gs,'setup','floor1.x0',0,'bad-floor1-duplicate-post'))
    spec=baseline();spec['floors'][1].update(partitions=[0],classes=[dict(dimensions=1,subclass_bits=0,masterbook=0,books=[-1])],range_bits=0,x=[0]);bad.append(make_case('bad-floor1-range0-duplicate',spec)[0])
    spec=baseline();spec['books']=[dict(dimensions=1,lengths=[1],lookup=0)]+[dict(dimensions=0,lengths=[1],lookup=0)for _ in range(254)]+[dict(dimensions=1,lengths=[1],lookup=1)]
    spec['floors'][0]['books']=[255];spec['residues'][0]['books']=[255];spec['floors'][1].update(partitions=[0],classes=[dict(dimensions=1,subclass_bits=1,masterbook=255,books=[254,-1])],range_bits=1,x=[1])
    good.append(make_case('books256-master255-subbook254',spec)[0])
    spec=baseline();spec['times']=64;good.append(make_case('time-count64',spec)[0])
    for stem in ('floors','residues','mappings','modes'):
        spec=baseline();spec[stem]=[clone(spec[stem][0])for _ in range(64)];good.append(make_case(stem+'-count64',spec,mode=63 if stem=='modes'else 0)[0])
    spec=baseline();spec['identification']['channels']=255;spec['mappings'][0].update(mux=[i%16 for i in range(255)],submaps=[(255,0,0)]*16,pairs=[(254,0),(0,253)])
    gr,gi,gs,ga=make_case('mapping255-channels16-submaps',spec);good.append(gr);bad.append(mutate(gr,gs,'setup','mapping0.mag0',255,'bad-coupling-channel255'));bad.append(mutate(gr,gs,'setup','mapping0.angle0',254,'bad-coupling-equal'))
    spec=baseline();spec['mappings'][0]['pairs']=[(0,1)]*256;good.append(make_case('mapping256-couplings',spec)[0])
    spec=baseline();spec['identification']['channels']=1;spec['mappings'][0].update(pairs=[(0,0)],mux=[0]);bad.append(make_case('bad-mono-coupling-zero-width',spec)[0])
    spec=baseline();spec['books'].append(dict(dimensions=0,lengths=[1],lookup=0));spec['floors'][1].update(partitions=[0],classes=[dict(dimensions=1,subclass_bits=1,masterbook=2,books=[2,-1])],range_bits=1,x=[1]);good.append(make_case('floor1-scalar-dim0-book',spec)[0])
    spec=baseline();spec['books'][0]['dimensions']=0;bad.append(make_case('bad-phrasebook-dimension0',spec)[0])
    spec=baseline();spec['modes']=[dict(blockflag=0,mapping=0),dict(blockflag=1,mapping=0),dict(blockflag=0,mapping=0)];gr,gi,gs,ga=make_case('audio-three-modes-long',spec,mode=1);good.append(gr);bad.append(mutate(gr,ga,'audio','mode',3,'bad-audio-mode3'))
    gr=dict(row,id='full-byte-header-extents');gr['identification_bits']=4*len(gr['identification_hex']);gr['setup_bits']=4*len(gr['setup_hex']);good.append(gr)
    gr=dict(row,id='audio-offset3');shifted=Writer();shifted.put(3,3)
    for i in range(row['audio_bits']):shifted.put((bytes.fromhex(row['audio_hex'])[i//8]>>(i%8))&1,1)
    gr.update(audio_hex=shifted.octets(),audio_bits=len(shifted.bits),audio_start=3);good.append(gr)
    rng=random.Random(0x5E7A091)
    for i in range(180):
        spec=baseline();channels=rng.choice((1,2,3,7,255));spec['identification'].update(channels=channels,rate=rng.randrange(1,1<<32),maximum=rng.getrandbits(32),nominal=rng.getrandbits(32),minimum=rng.getrandbits(32))
        dim=rng.choice((1,2,3,7));spec['books'][1].update(dimensions=dim,lookup=1+i%2,value_bits=1+i%16,sequence=i%2,minimum_bits=rng.getrandbits(32),delta_bits=rng.getrandbits(32))
        spec['floors'][0].update(order=i%256,rate=rng.randrange(65536),bark=rng.randrange(65536),amplitude_bits=i%64,amplitude_offset=i%256)
        spec['residues'][0].update(type=i%3,begin=rng.randrange(1<<24),end=rng.randrange(1<<24),partition_size=dim*(1+i%13),cascades=[1<<(i%8)])
        spec['mappings'][0].update(mux=[0]*channels,pairs=[(0,channels-1)]if channels>1 and i%2 else[])
        spec['modes']=[dict(blockflag=j%2,mapping=0)for j in range(1+i%7)];good.append(make_case(f'generated-{i}',spec,mode=i%len(spec['modes']))[0])
    for stem in ('identification','setup','audio'):
        gr=dict(row,id='truncated-'+stem);gr[stem+'_bits']=(233 if stem=='identification'else row['setup_bits']if stem=='setup'else 1)-1;bad.append(gr)
    real=public_cases(PUBLIC_FIXTURE.read_bytes()if public_fixture is None else public_fixture)
    all_rows=good+bad+real;model=dict(schema='native-vorbis-setup-cases-v1',cases=all_rows);validate_model(model)
    target_rows=[]
    for case in good:
        expected=expected_case(case)['exact'];layout=expected['layout']
        if expected['audio_status']==0 and layout and layout['book_count']<=256 and layout['codeword_count']<=512 and layout['multiplicand_count']<=1024 and layout['configuration_count']<=8192 and len(expected['getter_values'])<=8192 and max(len(case[k])for k in ('identification_hex','setup_hex','audio_hex'))<=32768:target_rows.append(case)
    target=dict(schema=model['schema'],cases=target_rows[:200]);need(len(target['cases'])==200,'predeclared200 native setup cases');return model,target
def validate_model(model):
    need(model['schema']=='native-vorbis-setup-cases-v1'and isinstance(model['cases'],list)and 1<=len(model['cases'])<=10000,'finite setup corpus')
    keys={'id','identification_hex','identification_bits','setup_hex','setup_bits','audio_hex','audio_bits','audio_start'};names=set()
    for case in model['cases']:
        need(set(case)==keys and isinstance(case['id'],str)and re.fullmatch('[A-Za-z0-9_-]{1,63}',case['id'])and case['id']not in names,'exact unique case identity/shape');names.add(case['id'])
        for stem in ('identification','setup','audio'):
            need(isinstance(case[stem+'_hex'],str)and re.fullmatch('(?:[0-9a-f]{2})*',case[stem+'_hex'])and len(case[stem+'_hex'])<=2*1048576 and
                 type(case[stem+'_bits'])is int and 0<=case[stem+'_bits']<=4*len(case[stem+'_hex']),'bounded literal packet and valid bit extent')
        need(type(case['audio_start'])is int and 0<=case['audio_start']<=case['audio_bits'],'audio cursor start')
        reference=expected_case(case)['exact']
        if reference['layout']:
            layout=reference['layout'];need(layout['codeword_count']<=1048576 and layout['multiplicand_count']<=1048576 and layout['configuration_count']<=262144,'concrete host materialization fixture bound, not a format restriction')
    return model['cases']
class Reader:
    def __init__(self,body):self.body,self.at=body,0
    def take(self,fmt):
        size=struct.calcsize(fmt);need(self.at+size<=len(self.body),'complete binary field');values=struct.unpack_from(fmt,self.body,self.at);self.at+=size
        return values[0]if len(values)==1 else values

def encode_input(model):
    data=bytearray(b'SETTEST1'+struct.pack('<I',len(validate_model(model))))
    for case in model['cases']:
        name=case['id'].encode();data+=struct.pack('<I',len(name))+name
        for stem in ('identification','setup','audio'):
            body=bytes.fromhex(case[stem+'_hex']);data+=struct.pack('<I',len(body))+body+struct.pack('<Q',case[stem+'_bits'])
        data+=struct.pack('<Q',case['audio_start'])
    return bytes(data)
def decode_input(body):
    r=Reader(body);need(r.take('<8s')==b'SETTEST1','setup input magic');count=r.take('<I');need(1<=count<=10000,'finite binary count');cases_rows=[]
    for _ in range(count):
        n=r.take('<I');need(1<=n<=63,'bounded identifier');case=dict(id=r.take('<'+str(n)+'s').decode('ascii'))
        for stem in ('identification','setup','audio'):
            n=r.take('<I');need(n<=1048576,'bounded packet body');case[stem+'_hex']=r.take('<'+str(n)+'s').hex();case[stem+'_bits']=r.take('<Q')
        case['audio_start']=r.take('<Q');cases_rows.append(case)
    need(r.at==len(body),'every complete input byte');model=dict(schema='native-vorbis-setup-cases-v1',cases=cases_rows);validate_model(model);return model

def read_id(r):return dict(zip(IDFIELDS,r.take('<IIIIIII')))
def read_book(r):
    start,used,maximum=r.take('<QII');q=dict(zip(QFIELDS,r.take('<IIIIIIIQQQQ')));count=r.take('<I');need(count<=1048576,'captured active words')
    words=[dict(zip(('code','entry','length'),r.take('<III')))for _ in range(count)];count=r.take('<I');need(count<=1048576,'captured raw q count')
    return dict(layout=dict(start_bit=start,used_entries=used,maximum_length=maximum,quantization=q),words=words,multiplicands=[r.take('<H')for _ in range(count)])
def decode_output(body,model):
    cases_rows=validate_model(model);r=Reader(body);need(r.take('<8s')==b'SETOUT01'and r.take('<I')==len(cases_rows),'complete setup output header');controls=r.take('<I')
    need(CONTROL_COUNT>0 and controls==CONTROL_COUNT,'all reviewed fixed API controls');rows=[]
    for i,case in enumerate(cases_rows):
        need(r.take('<I')==i,'ordered setup case');ids,ms,mt,as_=r.take('<iiii');id_info=read_id(r)if ids==0 else None
        layout=None;books=[];configuration=[];getters=[]
        if mt==0:
            copied=read_id(r);end,word_count,qcount=r.take('<QQQ');layout=dict(identification=copied,end_bit=end,codeword_count=word_count,multiplicand_count=qcount,**dict(zip(LFIELDS,r.take('<IIIIIIIIIII'))))
            need(layout['book_count']<=256,'captured book view count');books=[read_book(r)for _ in range(layout['book_count'])]
            count=r.take('<I');need(count<=262144,'captured configuration count');configuration=[r.take('<I')for _ in range(count)]
            count=r.take('<I');need(count<=263168,'captured getter count');getters=[r.take('<I')for _ in range(count)]
        audio=dict(zip(('mode','blockflag','previous_window','next_window','mapping','blocksize'),r.take('<IIIIII')))if as_==0 else None
        position,eop,ic,sc,ac=r.take('<QIQQQ');need(eop in(0,1)and r.take('<I')==7,'actual cursor/canary/input-preservation guards')
        rows.append(dict(case=i,id=case['id'],id_status=ids,measure_status=ms,materialize_status=mt,audio_status=as_,identification=id_info,layout=layout,books=books,configuration=configuration,getter_values=getters,audio=audio,position=position,end_of_packet=bool(eop),id_truncation_checks=ic,setup_truncation_checks=sc,audio_truncation_checks=ac,guards=1,unchanged=1))
    need(r.at==len(body),'whole output bytes');return dict(metadata_controls=controls,rows=rows)

def compare_all(model,observed,expected=None,native=False):
    cases_rows=validate_model(model);need(len(cases_rows)==len(observed),'complete setup comparison')
    if expected is not None:need(expected['schema']=='native-vorbis-setup-expected-v1'and expected['policy']==POLICY and len(expected['cases'])==len(cases_rows),'fixed independent setup policy')
    metrics=[];failures=[]
    for i,(case,actual)in enumerate(zip(cases_rows,observed)):
        try:
            need(actual['case']==i and actual['id']==case['id']and actual['guards']==actual['unchanged']==1,'complete original guarded case identity');wanted=expected_case(case)
            if expected is not None:need(wanted==expected['cases'][i],'regenerated original expected metadata')
            reasons=[];part={key:actual[key]for key in wanted['exact']}
            for key,value in wanted['exact'].items():
                if actual[key]!=value:reasons.append('exact '+key)
            for stem,key in (('identification','id_truncation_checks'),('setup','setup_truncation_checks'),('audio','audio_truncation_checks')):
                if actual[key]!=(0 if native else wanted['cuts'][stem]):reasons.append('actual '+stem+' truncation count')
            if case['id'].startswith('public-xiph-')and any(wanted['exact'][key]!=0 for key in ('id_status','measure_status','materialize_status','audio_status')):reasons.append('real encoder fixture rejected by independent specification oracle')
            metric=dict(id=case['id'],qualified=not reasons,failure_reasons=reasons,books=len(wanted['exact']['books']),configuration_words=len(wanted['exact']['configuration']),getter_words=len(wanted['exact']['getter_values']),id_status=actual['id_status'],measure_status=actual['measure_status'],audio_status=actual['audio_status'],id_truncation_checks=actual['id_truncation_checks'],setup_truncation_checks=actual['setup_truncation_checks'],audio_truncation_checks=actual['audio_truncation_checks'],expected_sha256=sha(json.dumps(wanted['exact'],sort_keys=True).encode()),actual_sha256=sha(json.dumps(part,sort_keys=True).encode()))
            if reasons:metric.update(expected=wanted,actual=actual);failures.append(dict(index=i,**metric))
            metrics.append(metric)
        except (ValueError,KeyError,TypeError)as error:failures.append(dict(index=i,id=case['id'],nonmeasurement_error=str(error),actual=actual))
    return dict(measurement_completed=len(metrics)==len(cases_rows),passed=not failures and len(metrics)==len(cases_rows),cases=len(cases_rows),metrics=metrics,failures=failures,
        books=sum(row['books']for row in metrics),configuration_words=sum(row['configuration_words']for row in metrics),getter_words=sum(row['getter_words']for row in metrics),
        id_truncation_checks=sum(row['id_truncation_checks']for row in metrics),setup_truncation_checks=sum(row['setup_truncation_checks']for row in metrics),audio_truncation_checks=sum(row['audio_truncation_checks']for row in metrics))
def compare_target_rows(model,expected,observed):return compare_all(model,observed,expected,native=True)

def target_header(model):
    cases_rows=validate_model(model);lines=['#pragma once','#include <stddef.h>','#include <stdint.h>','#define SETUP_CASE_COUNT '+str(len(cases_rows)),
        'typedef struct { const char *id; const uint8_t *identification; uint32_t identification_bytes; uint64_t identification_bits;',
        ' const uint8_t *setup; uint32_t setup_bytes; uint64_t setup_bits; const uint8_t *audio; uint32_t audio_bytes;',
        ' uint64_t audio_bits,audio_start; } setup_case_t;']
    for i,case in enumerate(cases_rows):
        for stem in ('identification','setup','audio'):
            body=bytes.fromhex(case[stem+'_hex'])
            if body:lines.append('static const uint8_t setup_'+stem+'_'+str(i)+'[] = {'+','.join('UINT8_C(0x'+f'{value:02x}'+')'for value in body)+'};')
    lines.append('static const setup_case_t setup_cases[SETUP_CASE_COUNT] = {')
    for i,case in enumerate(cases_rows):
        values=['"'+case['id']+'"']
        for stem in ('identification','setup','audio'):values.extend(['setup_'+stem+'_'+str(i)if case[stem+'_hex']else'NULL',str(len(case[stem+'_hex'])//2),'UINT64_C('+str(case[stem+'_bits'])+')'])
        values.append('UINT64_C('+str(case['audio_start'])+')');lines.append('    {'+','.join(values)+'},')
    return '\n'.join(lines+['};',''])
def self_checks():
    need(greedy_words([2,1,2])[1]['entry']==2,'independent lexical codebook reference witness')
    row,iw,sw,aw=make_case('oracle-only',baseline());expected=expected_case(row)['exact']
    need(expected['id_status']==expected['measure_status']==expected['audio_status']==0 and len(iw.bits)==233 and expected['audio']['blocksize']==64,'full grammar/prefix witness')
    need(identification(bytes.fromhex(row['identification_hex']),233)['bitrate_nominal_bits']==0xffffffff,'signed hint bits remain raw')
    return dict(passed=True,oracle_only=True,component_executed=False)
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
        freeze(Path(__file__),'test-vorbis-setup.py');source=freeze(COMPONENT/'floor0.c','floor0.c')
        freeze(COMPONENT/'setup.c','setup.c');freeze(COMPONENT/'include/native_vorbis_setup.h','native_vorbis_setup.h');freeze(COMPONENT/'codebook.c','codebook.c');freeze(COMPONENT/'include/native_vorbis_codebook.h','native_vorbis_codebook.h');freeze(COMPONENT/'quant.c','quant.c');freeze(COMPONENT/'include/native_vorbis_floor0.h','native_vorbis_floor0.h')
        freeze(COMPONENT/'include/native_vorbis_quant.h','native_vorbis_quant.h');freeze(COMPONENT/'CMakeLists.txt','CMakeLists.txt');freeze(DRIVER,'driver.c')
        owner=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-owner.py')
        nodes=[node for node in ast.parse(owner).body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(nodes)==1,'one existing nonce-owned supervisor literal');(out/'supervisor.py').write_text(ast.literal_eval(nodes[0].value),encoding='utf-8',newline='\n')
        report['oracle_self_checks']=self_checks()
        public_body=freeze(PUBLIC_FIXTURE,'public-fixture.h');model,target=cases(public_fixture=public_body);inputs=encode_input(model);need(decode_input(inputs)==model,'complete exact raw packet/affine input roundtrip')
        (out/'cases.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');(out/'inputs.bin').write_bytes(inputs)
        directory=out/'target-cases';expected=dict(schema='native-vorbis-setup-expected-v1',policy=POLICY,cases=[expected_case(row) for row in target['cases']])
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
        so,se=run('compile',flags+['-I'+host(out/'sources'),host(out/'sources/driver.c'),host(out/'sources/floor0.c'),host(out/'sources/quant.c'),host(out/'sources/codebook.c'),host(out/'sources/setup.c'),'-lm','-o',host(out/'test')])
        need(not so and not se,'clean strict whole-component compile');current()
        so,se=run('execute',[host(out/'test'),host(out/'inputs.bin'),host(out/'outputs.bin')]);report['component_executed']=True;need(not so and not se,'clean actual sanitized quantization execution')
        output=(out/'outputs.bin').read_bytes();decoded=decode_output(output,model);measured=compare_all(model,decoded['rows']);current()
        report.update(completed=True,passed=measured['passed'],source_inputs_unchanged=True,numerical=measured,metadata_controls=decoded['metadata_controls'],output_sha256=sha(output),
            result='OWNED_SETUP_EXACT_QUALIFIED' if measured['passed'] else 'OWNED_SETUP_EXACT_REJECTED')
        save();print(json.dumps(dict(completed=True,passed=report['passed'],cases=report['cases'],target_cases=report['target_cases'],result=report['result'],books=measured['books'],configuration_words=measured['configuration_words'],getter_words=measured['getter_words'],id_truncation_checks=measured['id_truncation_checks'],setup_truncation_checks=measured['setup_truncation_checks'],audio_truncation_checks=measured['audio_truncation_checks'])));return 0 if report['passed'] else 1
    except BaseException as error:report.update(completed=False,passed=False,error=repr(error));save();raise

if __name__=='__main__':sys.exit(main())


