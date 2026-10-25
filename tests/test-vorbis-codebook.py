"""Complete owned Vorbis codebooks: independent greedy-interval/tree oracle.

Primary: Vorbis I sections2/3, singleton erratum; Xiph v1.3.7 sharedbook.c.
Empty/all-unused retention is explicit Xiph compatibility, not a normative proof.
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
DRIVER=ROOT/'tests/native/vorbis_codebook_test.c'
OPS={'decode':1,'vector':2,'floor':3}
QFIELDS=('dimensions','entries','lookup_type','minimum_bits','delta_bits','value_bits','sequence_p','multiplicand_count','start_bit','multiplicand_bit','end_bit')
AFFINE=('minimum_bits','delta_bits','minimum_multiplier','delta_multiplier')
POLICY=dict(schema='native-vorbis-codebook-policy-v1',oracle='Greedy aligned free lexical intervals in declared entry order; independent bit/tree traversal',
    exact_comparison=True,singleton_length=1,singleton_accepts_both_bits=True,empty_books='Explicit Xiph compatibility retention; decode remains invalid',
    host_all_setup_bit_truncations=True,native_repeats_host_truncation_campaign=False,selected_before_measurement=True,
    decoder_or_PCM_qualification=False)

def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(data):return hashlib.sha256(data).hexdigest()
class Bits:
    def __init__(self,body,extent,position):
        need(type(extent)is int and type(position)is int and 0<=position<=extent<=8*len(body),'valid exact bit extent')
        self.raw=int.from_bytes(body,'little');self.extent=extent;self.position=position
    def take(self,width):
        need(0<=width<=64 and self.position+width<=self.extent,'complete independent raw field')
        value=(self.raw>>self.position)&((1<<width)-1);self.position+=width;return value

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

def parse_setup(case):
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

def decode_one(words,reader):
    need(words,'empty book has no entropy value')
    if len(words)==1:reader.take(1);return words[0]['entry']
    path=0;index={(w['code'],w['length']):w['entry'] for w in words}
    for length in range(1,33):
        path|=reader.take(1)<<(32-length)
        if (path,length)in index:return index[(path,length)]
    raise ValueError('no codeword in complete tree')

def vector(q,weights,entry,prefix):
    need(q['lookup_type']in(1,2) and q['dimensions']>0 and 0<=entry<q['entries'] and 0<=prefix<=q['dimensions'],'valid VQ entry/prefix')
    out=[];m=d=0
    for i in range(prefix):
        at=(entry//q['multiplicand_count']**i)%q['multiplicand_count'] if q['lookup_type']==1 else entry*q['dimensions']+i
        if q['sequence_p']:m+=1;d+=weights[at]
        else:m=1;d=weights[at]
        out.append(dict(zip(AFFINE,(q['minimum_bits'],q['delta_bits'],m,d))))
    return out

def exact_case(case):
    layout,words,weights=parse_setup(case);q=layout['quantization'];length=case['length'];op=case['operation']
    count=length if op=='decode' else (1 if length else 0) if op=='vector' else (length+q['dimensions']-1)//q['dimensions']
    reader=Bits(bytes.fromhex(case['payload_hex']),case['payload_bits'],case['payload_start']);decoded=[]
    for _ in range(count):entry=decode_one(words,reader);decoded.append(dict(entry=entry,position=reader.position))
    values=[]
    if op=='vector':values=vector(q,weights,decoded[0]['entry'],length) if length else []
    elif op=='floor':
        carry_min=carry_delta=0
        for row in decoded:
            current=vector(q,weights,row['entry'],min(q['dimensions'],length-len(values)))
            for value in current:value['minimum_multiplier']+=carry_min;value['delta_multiplier']+=carry_delta
            values.extend(current)
            if current:carry_min,carry_delta=current[-1]['minimum_multiplier'],current[-1]['delta_multiplier']
    return dict(layout=layout,words=words,multiplicands=weights,decoded=decoded,values=values,position=reader.position,end_of_packet=0)

def field(bits,value,width):bits.extend((value>>i)&1 for i in range(width))
def octets(bits):
    data=bytearray((len(bits)+7)//8)
    for i,value in enumerate(bits):data[i//8]|=value<<(i%8)
    return data.hex()
def setup_bits(lengths,dimension,lookup,width,sequence,minimum,delta,ordered=False,zero_runs=False):
    bits=[];field(bits,0x564342,24);field(bits,dimension,16);field(bits,len(lengths),24);field(bits,int(ordered),1)
    if ordered:
        need(lengths==sorted(lengths) and all(lengths),'ordered used lengths');length=1 if zero_runs else min(lengths);field(bits,length-1,5);at=0
        while at<len(lengths):
            count=0
            while at+count<len(lengths) and lengths[at+count]==length:count+=1
            field(bits,count,(len(lengths)-at).bit_length());at+=count;length+=1
    else:
        sparse=0 in lengths;field(bits,int(sparse),1)
        for length in lengths:
            if sparse:field(bits,int(bool(length)),1)
            if length:field(bits,length-1,5)
    field(bits,lookup,4)
    if lookup:
        field(bits,minimum,32);field(bits,delta,32);field(bits,width-1,4);field(bits,sequence,1)
        count=integer_root(len(lengths),dimension) if lookup==1 else len(lengths)*dimension
        for i in range(count):field(bits,((1<<width)-1-i*11)&((1<<width)-1),width)
    return bits

def make_case(identifier,lengths,operation='decode',length=4,dimension=3,lookup=1,width=16,sequence=0,
              ordered=False,zero_runs=False,start=0,singleton_one=False,tail=True,minimum=0x80000000,delta=0x62800001):
    own=setup_bits(lengths,dimension,lookup,width,sequence,minimum,delta,ordered,zero_runs);prefix=[i%2 for i in range(start)];bits=prefix+own
    words=greedy_words(lengths);used=[w['entry'] for w in sorted(words,key=lambda w:w['entry'])]
    reads=length if operation=='decode' else (1 if length else 0) if operation=='vector' else (length+dimension-1)//dimension
    need(not reads or used,'nonempty payload decode');payload=[1,0,1][:start%4];payload_start=len(payload);by_entry={w['entry']:w for w in words}
    for i in range(reads):
        word=by_entry[used[i%len(used)]]
        if len(words)==1:payload.append(int(singleton_one))
        else:payload.extend((word['code']>>(31-j))&1 for j in range(word['length']))
    if tail:payload.extend((1,0,1))
    return dict(id=identifier,operation=operation,packet_hex=octets(bits),packet_bits=len(bits),start_bit=len(prefix),
                payload_hex=octets(payload),payload_bits=len(payload),payload_start=payload_start,length=length)

def cases():
    rows=[]
    for one in (False,True):
        for sparse in (False,True):rows.append(make_case(f'singleton-{int(one)}-{int(sparse)}',[0,1,0]if sparse else[1],length=8,singleton_one=one,tail=False))
    rows.append(make_case('entry-order-backfill-212',[2,1,2],length=6,tail=False))
    rows.append(make_case('prefix-without-max-lookahead',[1]+list(range(2,32))+[32,32],length=1,lookup=0,tail=False))
    comb=list(range(1,32))+[32,32]
    for op in OPS:
        rows.append(make_case('comb32-'+op,comb,op,255 if op=='floor' else 3,lookup=1,sequence=1,start=7,tail=False))
    rows.append(make_case('ordered-zero-runs',[2]*4,length=8,ordered=True,zero_runs=True,start=5))
    rows.append(make_case('sparse257-wide-dimension',[1]+[0]*255+[1],operation='vector',length=255,dimension=65535,lookup=1,sequence=1,start=3))
    for lookup in (0,1,2):
        rows.append(make_case(f'empty-declared-{lookup}',[],length=0,dimension=3,lookup=lookup,tail=False))
        rows.append(make_case(f'empty-all-unused-{lookup}',[0]*7,length=0,dimension=3,lookup=lookup,tail=False))
    for lookup in (0,2):rows.append(make_case(f'dim0-entropy-{lookup}',[1,1],length=6,dimension=0,lookup=lookup,tail=False))
    # Three setup books share one packet and successive, deliberately unaligned starts.
    chain_lengths=([2,1,2],[2]*4,[1,1]);chain_bits=[];chain=[]
    for i,lengths in enumerate(chain_lengths):
        start=len(chain_bits);chain_bits+=setup_bits(lengths,3,1,5+i,i%2,0x7fffffff,0x80000001,i==1,i==1)
        chain.append((start,make_case(f'chained-setup-{i}',lengths,length=4,lookup=1)))
    for start,row in chain:row.update(packet_hex=octets(chain_bits),packet_bits=len(chain_bits),start_bit=start);rows.append(row)
    rng=random.Random(0xCB3117)
    for i in range(360):
        lengths=[0]
        for _ in range(1+rng.randrange(63)):
            choice=rng.randrange(len(lengths));depth=lengths.pop(choice);lengths.extend((depth+1,depth+1))
        op=('decode','vector','floor')[i%3];lookup=0 if op=='decode' and i%4==0 else 1+i%2;dim=(1,2,3,7,255,65535)[i%6]
        if lookup==2 and dim>7:dim=3
        ordered=i%5==0
        if ordered:lengths.sort()
        else:
            rng.shuffle(lengths)
            if i%4==1:
                for _ in range(rng.randrange(1,8)):lengths.insert(rng.randrange(len(lengths)+1),0)
        length=rng.randrange(1,9) if op=='decode' else rng.randrange(min(dim,255)+1) if op=='vector' else (1,2,3,7,254,255)[i%6]
        rows.append(make_case(f'generated-{i}',lengths,op,length,dim,lookup,1+i%16,i%2,ordered,ordered,i%8,
            minimum=rng.getrandbits(32),delta=rng.getrandbits(32),tail=i%3!=0))
    model=dict(schema='native-vorbis-codebook-cases-v1',cases=rows);validate_model(model)
    bounded=[row for row in rows if (lambda x:x[0]['used_entries']<=255 and x[0]['quantization']['multiplicand_count']<=255)(parse_setup(row)) and len(row['packet_hex'])<=8192 and len(row['payload_hex'])<=8192]
    target=dict(schema=model['schema'],cases=bounded[:200]);need(len(target['cases'])==200,'predeclared200 native rows');return model,target

def validate_model(model):
    need(model['schema']=='native-vorbis-codebook-cases-v1' and isinstance(model['cases'],list) and 1<=len(model['cases'])<=10000,'finite owned-book corpus')
    names=set();keys={'id','operation','packet_hex','packet_bits','start_bit','payload_hex','payload_bits','payload_start','length'}
    for row in model['cases']:
        need(set(row)==keys and isinstance(row['id'],str) and re.fullmatch('[A-Za-z0-9_-]{1,63}',row['id']) and row['id']not in names and row['operation']in OPS,'exact unique case shape/id');names.add(row['id'])
        need(all(type(row[k])is int and row[k]>=0 for k in ('packet_bits','start_bit','payload_bits','payload_start','length')) and row['length']<=255,'unsigned metadata')
        for stem in ('packet','payload'):need(isinstance(row[stem+'_hex'],str) and re.fullmatch('(?:[0-9a-f]{2})*',row[stem+'_hex']) and row[stem+'_bits']<=4*len(row[stem+'_hex']),'complete exact raw packet')
        layout,words,q=parse_setup(row);need(len(words)<=4096 and len(q)<=65535,'bounded host materialization')
        if row['operation']!='decode':need(layout['quantization']['lookup_type']in(1,2) and layout['quantization']['dimensions']>0 and (row['length']>0 if row['operation']=='floor' else row['length']<=layout['quantization']['dimensions']),'valid scientific VQ operation')
        exact_case(row)
    return model['cases']

class Reader:
    def __init__(self,body):self.body,self.at=body,0
    def take(self,fmt):
        size=struct.calcsize(fmt);need(self.at+size<=len(self.body),'complete binary field');values=struct.unpack_from(fmt,self.body,self.at);self.at+=size
        return values[0]if len(values)==1 else values

def encode_input(model):
    data=bytearray(b'CBTEST01'+struct.pack('<I',len(validate_model(model))))
    for row in model['cases']:
        name=row['id'].encode();data+=struct.pack('<I',len(name))+name+struct.pack('<I',OPS[row['operation']])
        for stem,start in (('packet','start_bit'),('payload','payload_start')):
            body=bytes.fromhex(row[stem+'_hex']);data+=struct.pack('<I',len(body))+body+struct.pack('<QQ',row[stem+'_bits'],row[start])
        data+=struct.pack('<I',row['length'])
    return bytes(data)
def decode_input(body):
    r=Reader(body);need(r.take('<8s')==b'CBTEST01','input magic');count=r.take('<I');need(1<=count<=10000,'finite count');rows=[]
    for _ in range(count):
        n=r.take('<I');need(1<=n<=63,'bounded id');row=dict(id=r.take('<'+str(n)+'s').decode('ascii'));op=r.take('<I');need(op in OPS.values(),'valid operation');row['operation']=next(k for k,v in OPS.items()if v==op)
        for stem,start in (('packet','start_bit'),('payload','payload_start')):
            n=r.take('<I');need(n<=65536,'bounded raw packet');row[stem+'_hex']=r.take('<'+str(n)+'s').hex();row[stem+'_bits'],row[start]=r.take('<QQ')
        row['length']=r.take('<I');rows.append(row)
    need(r.at==len(body),'exact complete inputs');model=dict(schema='native-vorbis-codebook-cases-v1',cases=rows);validate_model(model);return model

def decode_output(body,model):
    r=Reader(body);rows=validate_model(model);need(r.take('<8s')==b'CBOUT001' and r.take('<I')==len(rows),'complete output header');controls=r.take('<I');need(controls==719,'all719 fixed API controls');observed=[]
    for i,case in enumerate(rows):
        need(r.take('<I')==i,'ordered case index');ms,mt,status=r.take('<iii');start,used,maximum=r.take('<QII');q=dict(zip(QFIELDS,r.take('<IIIIIIIQQQQ')))
        layout=dict(start_bit=start,used_entries=used,maximum_length=maximum,quantization=q)
        count=r.take('<I');need(count<=4096,'bounded word count');words=[dict(zip(('code','entry','length'),r.take('<III')))for _ in range(count)]
        count=r.take('<I');need(count<=65535,'bounded q count');weights=[r.take('<H')for _ in range(count)]
        count=r.take('<I');need(count<=255,'bounded decode count');decoded=[dict(zip(('entry','position'),r.take('<IQ')))for _ in range(count)]
        count=r.take('<I');need(count<=255,'bounded affine count');values=[dict(zip(AFFINE,r.take('<IIII')))for _ in range(count)]
        position,eop,truncations,payload_cuts=r.take('<QIQQ');need(r.take('<I')==7,'actual canary/input/consistency guards')
        observed.append(dict(case=i,id=case['id'],operation=case['operation'],measure_status=ms,materialize_status=mt,operation_status=status,layout=layout,words=words,multiplicands=weights,decoded=decoded,values=values,position=position,end_of_packet=eop,truncation_checks=truncations,payload_truncation_checks=payload_cuts,guards=1,unchanged=1))
    need(r.at==len(body),'all output bytes');return dict(metadata_controls=controls,rows=observed)

def expected_case(case):return dict(id=case['id'],exact=exact_case(case))
def compare_all(model,observed,expected=None,native=False):
    rows=validate_model(model);need(len(rows)==len(observed),'complete comparison')
    if expected is not None:need(expected['schema']=='native-vorbis-codebook-expected-v1' and expected['policy']==POLICY and len(expected['cases'])==len(rows),'fixed independent policy')
    metrics=[];failures=[]
    for i,(case,actual)in enumerate(zip(rows,observed)):
        try:
            need(actual['case']==i and actual['id']==case['id'] and actual['operation']==case['operation'] and actual['guards']==actual['unchanged']==1,'original ordered guarded case')
            wanted=expected_case(case)
            if expected is not None:need(wanted==expected['cases'][i],'regenerated exact expected outputs')
            reasons=[];part={key:actual[key]for key in wanted['exact']}
            for key,value in wanted['exact'].items():
                if actual[key]!=value:reasons.append('exact '+key)
            if any(actual[k]!=0 for k in ('measure_status','materialize_status','operation_status')):reasons.append('operation status')
            cuts=0 if native else wanted['exact']['layout']['quantization']['end_bit']-case['start_bit']
            if actual['truncation_checks']!=cuts:reasons.append('actual setup truncation count')
            payload_cuts=0 if native else wanted['exact']['position']-case['payload_start']
            if actual['payload_truncation_checks']!=payload_cuts:reasons.append('actual payload truncation count')
            metric=dict(id=case['id'],qualified=not reasons,failure_reasons=reasons,words=len(wanted['exact']['words']),decoded=len(wanted['exact']['decoded']),affine_values=len(wanted['exact']['values']),truncation_checks=actual['truncation_checks'],payload_truncation_checks=actual['payload_truncation_checks'],expected_sha256=sha(json.dumps(wanted['exact'],sort_keys=True).encode()),actual_sha256=sha(json.dumps(part,sort_keys=True).encode()))
            if reasons:metric.update(expected=wanted,actual=actual);failures.append(dict(index=i,**metric))
            metrics.append(metric)
        except (ValueError,KeyError,TypeError)as error:failures.append(dict(index=i,id=case['id'],nonmeasurement_error=str(error),actual=actual))
    return dict(measurement_completed=len(metrics)==len(rows),passed=not failures and len(metrics)==len(rows),cases=len(rows),metrics=metrics,failures=failures,
        words=sum(x['words']for x in metrics),decoded=sum(x['decoded']for x in metrics),affine_values=sum(x['affine_values']for x in metrics),truncation_checks=sum(x['truncation_checks']for x in metrics),payload_truncation_checks=sum(x['payload_truncation_checks']for x in metrics))
def compare_target_rows(model,expected,observed):return compare_all(model,observed,expected,native=True)

def target_header(model):
    rows=validate_model(model);lines=['#pragma once','#include <stddef.h>','#include <stdint.h>','#define CODEBOOK_CASE_COUNT '+str(len(rows)),
        'typedef struct { const char *id; uint32_t operation; const uint8_t *packet; uint32_t packet_bytes; uint64_t packet_bits,start_bit;',
        ' const uint8_t *payload; uint32_t payload_bytes; uint64_t payload_bits,payload_start; uint32_t length; } codebook_case_t;']
    for i,row in enumerate(rows):
        for stem in ('packet','payload'):
            body=bytes.fromhex(row[stem+'_hex'])
            if body:lines.append('static const uint8_t codebook_'+stem+'_'+str(i)+'[] = {'+','.join('UINT8_C(0x'+f'{x:02x}'+')'for x in body)+'};')
    lines.append('static const codebook_case_t codebook_cases[CODEBOOK_CASE_COUNT] = {')
    for i,row in enumerate(rows):
        values=['"'+row['id']+'"',str(OPS[row['operation']])]
        for stem,start in (('packet','start_bit'),('payload','payload_start')):values.extend(['codebook_'+stem+'_'+str(i)if row[stem+'_hex']else'NULL',str(len(row[stem+'_hex'])//2),'UINT64_C('+str(row[stem+'_bits'])+')','UINT64_C('+str(row[start])+')'])
        values.append(str(row['length']));lines.append('    {'+','.join(values)+'},')
    return '\n'.join(lines+['};',''])
def self_checks():
    need(greedy_words([2,1,2])==[dict(code=0,entry=0,length=2),dict(code=0x40000000,entry=2,length=2),dict(code=0x80000000,entry=1,length=1)],'entry-order lexical backfill witness')
    reader=Bits(bytes.fromhex('14'),5,0);words=greedy_words([2,1,2]);need([decode_one(words,reader)for _ in range(3)]==[0,1,2]and reader.position==5,'independent literal entropy witness')
    need(greedy_words([])==greedy_words([0,0])==[],'explicit empty compatibility descriptor')
    need(len(greedy_words(list(range(1,32))+[32,32]))==33,'maximum32bit complete comb')
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
        freeze(Path(__file__),'test-vorbis-codebook.py');source=freeze(COMPONENT/'floor0.c','floor0.c')
        freeze(COMPONENT/'codebook.c','codebook.c');freeze(COMPONENT/'include/native_vorbis_codebook.h','native_vorbis_codebook.h');freeze(COMPONENT/'quant.c','quant.c');freeze(COMPONENT/'include/native_vorbis_floor0.h','native_vorbis_floor0.h')
        freeze(COMPONENT/'include/native_vorbis_quant.h','native_vorbis_quant.h');freeze(COMPONENT/'CMakeLists.txt','CMakeLists.txt');freeze(DRIVER,'driver.c')
        owner=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-owner.py')
        nodes=[node for node in ast.parse(owner).body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(nodes)==1,'one existing nonce-owned supervisor literal');(out/'supervisor.py').write_text(ast.literal_eval(nodes[0].value),encoding='utf-8',newline='\n')
        report['oracle_self_checks']=self_checks()
        model,target=cases();inputs=encode_input(model);need(decode_input(inputs)==model,'complete exact raw packet/affine input roundtrip')
        (out/'cases.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');(out/'inputs.bin').write_bytes(inputs)
        directory=out/'target-cases';expected=dict(schema='native-vorbis-codebook-expected-v1',policy=POLICY,cases=[expected_case(row) for row in target['cases']])
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
        so,se=run('compile',flags+['-I'+host(out/'sources'),host(out/'sources/driver.c'),host(out/'sources/floor0.c'),host(out/'sources/quant.c'),host(out/'sources/codebook.c'),'-lm','-o',host(out/'test')])
        need(not so and not se,'clean strict whole-component compile');current()
        so,se=run('execute',[host(out/'test'),host(out/'inputs.bin'),host(out/'outputs.bin')]);report['component_executed']=True;need(not so and not se,'clean actual sanitized quantization execution')
        output=(out/'outputs.bin').read_bytes();decoded=decode_output(output,model);measured=compare_all(model,decoded['rows']);current()
        report.update(completed=True,passed=measured['passed'],source_inputs_unchanged=True,numerical=measured,metadata_controls=decoded['metadata_controls'],output_sha256=sha(output),
            result='OWNED_CODEBOOK_EXACT_QUALIFIED' if measured['passed'] else 'OWNED_CODEBOOK_EXACT_REJECTED')
        save();print(json.dumps(dict(completed=True,passed=report['passed'],cases=report['cases'],target_cases=report['target_cases'],result=report['result'],words=measured['words'],decoded=measured['decoded'],affine_values=measured['affine_values'],truncation_checks=measured['truncation_checks'],payload_truncation_checks=measured['payload_truncation_checks'])));return 0 if report['passed'] else 1
    except BaseException as error:report.update(completed=False,passed=False,error=repr(error));save();raise

if __name__=='__main__':sys.exit(main())

