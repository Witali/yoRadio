"""Persistent public raw434 decoder on pinned native ESP32/C3 QEMU.

The original31 contract remains unchanged: all738560 PCM bytes, error<=2,
all14 relations, original packet spans, no alignment/scale/channel fitting.
"""
import argparse
import hashlib
import io
import json
import re
import shutil
import struct
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent
PROJECT = ROOT / 'tests/target/vorbis_decoder_qemu'
COMPONENTS = ('native_vorbis_numeric', 'native_vorbis_setup_owner', 'native_vorbis_packet_frame',
    'native_vorbis_floor1_product', 'native_vorbis_floor0_spectrum', 'native_vorbis_transform',
    'native_vorbis_window', 'native_vorbis_window_exact', 'native_vorbis_pcm_exact',
    'native_vorbis_timing', 'native_vorbis_synthesis', 'native_vorbis_decoder')
SDK_HEAD = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e',
            'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
QEMU_SHA = {'esp32': '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d',
            'esp32c3': 'a74f3324430b306618aa88a52649dbb93c32eac6d0b87926d335754346abbf0b'}
ORIGINAL_SHA = '32ba4c7e401fcfd05238f929fa6874c3048237792d78f36b05a8fade5b861e24'
ORIGINAL_ARCHIVE_SHA = '3b74cc7425b315997011040b6b6a8924b908cdff0404e0d0601cbb81a68a93ea'
REFERENCE_ARCHIVE_SHA = 'f31167f2a52e8e8a8f01e20cbadb3597d1394931bd2dfd2ac67a0381e2d6985b'
REFERENCE_CONTROLLER_SHA = 'ce4859daf4f9a0bd59a1c023b3b01b3e015d7a76a14acca98c8f6e27ce91222b'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


def original_inputs():
    archive = (ROOT / 'tests/results/vorbis-floor1-product-20261026/captures.zip').read_bytes()
    need(sha(archive) == ORIGINAL_ARCHIVE_SHA, 'pinned original source archive')
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        body = source.read('frame03/sources/original31.json')
    need(sha(body) == ORIGINAL_SHA, 'unchanged original31 raw model')
    model = json.loads(body)
    rows = model['cases']
    need(len(rows) == 31 and [r['case'] for r in rows] == list(range(31)), 'complete ordered31')
    need(model['policy']['max_abs_error'] == 2 and len(model['relations']) == 14, 'unchanged bound and relations')
    need(sum(r['pcm_bytes'] for r in rows) == 738560 and sum(len(r['frames']) for r in rows) == 434,
         'complete original PCM and packets')
    reference_archive = (ROOT / 'tests/results/vorbis-xiph-packets-20261026/captures.zip').read_bytes()
    need(sha(reference_archive) == REFERENCE_ARCHIVE_SHA, 'pinned retained reference archive')
    references = {}
    with zipfile.ZipFile(io.BytesIO(reference_archive)) as source:
        for row in rows:
            reference = source.read('host/sources/cases/' + row['reference_path'])
            need(len(reference) == row['pcm_bytes'] and sha(reference) == row['reference_pcm_sha256'],
                 'complete original reference: ' + row['id'])
            need(row['channels'] == 2 and row['long_block'] <= 2048 and row['frames'][0] == 0 and
                 len(row['offsets']) == 15 and len(row['granules']) == len(row['modes']) == 14,
                 'original bounded stereo shape')
            need(row['offsets'][0] == 0 and row['offsets'][-1] == len(bytes.fromhex(row['audio_hex'])) and
                 all(a < b for a, b in zip(row['offsets'], row['offsets'][1:])), 'exact packet byte extents')
            need([sum(row['frames'][:i+1]) for i in range(14)] == row['granules'], 'original packet granules')
            references[row['id']] = reference
    need(sum(len(bytes.fromhex(r[k + '_hex'])) for r in rows for k in ('identification', 'setup', 'audio')) == 7376 and
         sum(len(bytes.fromhex(r['comment_hex'])) for r in rows) == 1798, 'all raw header/audio bytes')
    return body, model, references


def transport(model):
    """Freeze the existing raw-fixture contract, not recovered container metadata."""
    return dict(schema='owned-decoder-fixture-transport-v1', original_sha256=ORIGINAL_SHA,
        reference_controller_sha256=REFERENCE_CONTROLLER_SHA,
        policy='Original raw fixture: complete octet extents, preserved granules, terminal EOS, no gap; not HTTP/container inference',
        cases=[dict(id=row['id'], packets=[dict(bits=8*(row['offsets'][i+1]-row['offsets'][i]),
            granule=row['granules'][i], eos=int(i+1==len(row['modes'])), gap=0)
            for i in range(len(row['modes']))]) for row in model['cases']])


def transport_bytes(model):
    return (json.dumps(transport(model),sort_keys=True,separators=(',',':'))+'\n').encode()


def resource_vector():
    """Retained independently decoded legal255-channel/8192 host vector."""
    return dict(schema='owned-decoder-native-resource-v1',
        source='vorbis-decoder-preflight-20261028-01/sources/supplements.json',
        source_sha256='dedd6b504a97cb2b31c728fa18ac440833d36dadd41498c1467efcfe0c409d39',
        builder='tests/test-vorbis-decoder.py:supplementary',
        builder_sha256='16166095e826b1dfd95cff357c6d97671a501d13813f7febd2b18ce9e6298763',
        row=dict(id='decoder-resource-255x8192',
            identification_hex='01766f7262697300000000ff45ac000000000080ffffffff00000000dd01',identification_bits=233,
            setup_hex='05766f7262697300424356010001000000000000800000000100000000000000000000000000000000f00f0000000000000008',setup_bits=404,
            packet_hex='00'*32,packet_bits=256,start_bit=0,initial_eop=False,index=13,
            prime_hex='00'*32,prime_bits=256,expected_status=0,extreme=True,
            rate=44101,channels=255,short_block=8192,long_block=8192),
        policy='Real native malloc refusal and full cleanup, then complete original31 recovery; no allocator budget or format cap')


def resource_bytes():
    return (json.dumps(resource_vector(),sort_keys=True,separators=(',',':'))+'\n').encode()


def header(model):
    metadata=transport(model)
    rows=model['cases']
    lines=['#pragma once','#include "decoder_case.h"','#define DEC_CASE_COUNT 31',
        '#define DEC_MAX_IDENTIFICATION_BYTES '+str(max(len(bytes.fromhex(r['identification_hex'])) for r in rows)),
        '#define DEC_MAX_SETUP_BYTES '+str(max(len(bytes.fromhex(r['setup_hex'])) for r in rows)),
        '#define DEC_MAX_PACKET_BYTES '+str(max(b-a for r in rows for a,b in zip(r['offsets'],r['offsets'][1:]))),
        '#define DEC_TRANSPORT_SHA256 "'+sha(transport_bytes(model))+'"',
        '#define DEC_RESOURCE_SHA256 "'+sha(resource_bytes())+'"']
    resource=resource_vector()['row']
    for key in ('identification','setup'):
        lines.append('static const uint8_t dec_resource_'+key+'[]={'+
            ','.join(str(x) for x in bytes.fromhex(resource[key+'_hex']))+'};')
        lines.append('#define DEC_RESOURCE_'+key.upper()+'_BITS '+str(resource[key+'_bits']))
    for i,row in enumerate(rows):
        for key in ('identification','setup','audio'):
            lines.append('static const uint8_t dec_'+key+str(i)+'[]={'+
                ','.join(str(x) for x in bytes.fromhex(row[key+'_hex']))+'};')
        values=dict(offsets=row['offsets'],bits=[p['bits'] for p in metadata['cases'][i]['packets']],
            granules=[p['granule'] for p in metadata['cases'][i]['packets']],
            eos=[p['eos'] for p in metadata['cases'][i]['packets']],gaps=[p['gap'] for p in metadata['cases'][i]['packets']])
        for key,ctype in (('offsets','uint32_t'),('bits','uint64_t'),('granules','int64_t'),('eos','uint8_t'),('gaps','uint8_t')):
            lines.append('static const '+ctype+' dec_'+key+str(i)+'[]={'+','.join(str(x) for x in values[key])+'};')
    lines.append('static const char *const dec_names[DEC_CASE_COUNT]={'+','.join('"'+r['id']+'"' for r in rows)+'};')
    lines.append('static const decoder_case_t dec_cases[DEC_CASE_COUNT]={')
    for i,row in enumerate(rows):
        fields=['dec_'+k+str(i) for k in ('identification','setup','audio')]
        fields += [str(len(bytes.fromhex(row[k+'_hex']))) for k in ('identification','setup','audio')]
        fields += ['dec_'+k+str(i) for k in ('offsets','bits','granules','eos','gaps')]
        fields += [str(len(row['modes']))]
        lines.append('{'+','.join(fields)+'},')
    return ('\n'.join(lines+['};',''])).encode('ascii')


def saved_xiph(model):
    body=(ROOT/'tests/results/vorbis-xiph-packets-20261026/captures.zip').read_bytes()
    need(sha(body)==REFERENCE_ARCHIVE_SHA,'pinned saved Xiph PCM archive')
    with zipfile.ZipFile(io.BytesIO(body)) as z:captured=z.read('host/pcm.bin')
    at=0
    def take(fmt):
        nonlocal at
        size=struct.calcsize('<'+fmt);need(size<=len(captured)-at,'complete saved Xiph field')
        values=struct.unpack_from('<'+fmt,captured,at);at+=size
        return values[0] if len(values)==1 else values
    need(take('8s')==b'XIPHRES1' and take('I')==31,'all saved Xiph cases')
    output={}
    for i,row in enumerate(model['cases']):
        need(take('4I')==(i,row['rate'],row['channels'],len(row['frames'])),'saved Xiph stream identities')
        parts=[]
        for p,count in enumerate(row['frames']):
            size=count*row['channels']*2
            need(take('3I')==(p,count,size) and size<=len(captured)-at,'saved Xiph packet extents')
            parts.append(captured[at:at+size]);at+=size
        output[row['id']]=b''.join(parts)
        need(len(output[row['id']])==row['pcm_bytes'],'all saved Xiph PCM bytes')
    need(at==len(captured),'complete saved Xiph capture')
    return captured,output


def fnv(body):
    value=14695981039346656037
    for byte in body:value=((value^byte)*1099511628211)&((1<<64)-1)
    return value


def validate_log(log,model,references,xiph,target,output=None):
    """Pure when output=None; decode every primary PCM byte and lifecycle event."""
    need(target in SDK_HEAD, 'explicit native decoder target')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|stack overflow|timed out',log,re.I),
        'native panic/corruption/timeout')
    need(not any('DEC_' in line and not line.startswith('DEC_') for line in log.splitlines()),'foreign/torn decoder event')
    events=iter(line for line in log.splitlines() if line.startswith('DEC_'))
    core=1 if target=='esp32' else 0;event_count=0
    def take(kind,fixed,extra=()):
        nonlocal event_count
        line=next(events,None);need(line is not None,'missing decoder event')
        fields=line.split(' ')
        need(fields[0]=='DEC_'+kind and all(x.count('=')==1 for x in fields[1:]),'ordered decoder event syntax')
        row=dict(x.split('=') for x in fields[1:])
        need(len(row)+1==len(fields) and set(row)==set(fixed)|set(extra) and
            all(row[key]==str(value) for key,value in fixed.items()),'unique exact decoder fields: '+kind)
        event_count+=1;return row
    def integer(text,maximum=(1<<64)-1):
        need(re.fullmatch(r'0|[1-9][0-9]*',text) is not None,'canonical unsigned integer')
        value=int(text);need(value<=maximum,'bounded decoder extent');return value
    take('BEGIN',dict(cases=31,coordinator=0,worker=core,data=ORIGINAL_SHA,
        transport=sha(transport_bytes(model)),resource=sha(resource_bytes())))
    take('WORKER',dict(core=core,priority=3,stack=16384))
    resource_control=take('RESOURCE',dict(status=-4,channels=255,short=8192,long=8192,
        identification_bits=233,setup_bits=404,failed_bytes=8355840,failures=1,live=0,bytes=0,
        handle_null=1,core=core),('attempts','allocations','releases','peak_allocations','peak_bytes','overhead'))
    resource_control={k:integer(v) for k,v in resource_control.items() if k not in ('status',)}
    need(resource_control['allocations']>0 and resource_control['attempts']==resource_control['allocations']+1 and
        resource_control['allocations']==resource_control['releases'] and
        0<resource_control['peak_allocations']<=resource_control['allocations'] and
        0<resource_control['peak_bytes']<resource_control['failed_bytes'] and 0<resource_control['overhead']<=256,
        'actual native large request fails without leaked payload')
    captured={};metrics=[];metadata=transport(model)
    for index,case in enumerate(model['cases']):
        take('CASE',dict(row=index,id=case['id'],core=core))
        opened=take('OPEN',dict(row=index,status=0,rate=case['rate'],channels=case['channels'],
            short=case['short_block'],long=case['long_block'],allocator_copy=1,headers_poisoned=1,core=core),
            ('allocations','releases','live','bytes'))
        a,r,live,payload=(integer(opened[k]) for k in ('allocations','releases','live','bytes'))
        need(a>0 and live>0 and a-r==live and payload>0,'live owner construction accounting')
        maximum=case['channels']*(case['long_block']//2)
        buffer=take('BUFFER',dict(row=index,samples=maximum,caller_allocations=2,caller_bytes=maximum*4,core=core),('overhead',))
        overhead=integer(buffer['overhead'],256);need(overhead>0,'separate tracking overhead')
        parts=[];previous=untrimmed=0;floor0=2 if case['id'].startswith('floor0-') else 0
        observed_peak_live,observed_peak_bytes=live,payload
        for ordinal,count in enumerate(case['frames']):
            n=case['long_block'] if case['modes'][ordinal] else case['short_block']
            available=(previous+n)//4 if previous else 0;samples=count*2
            meta=metadata['cases'][index]['packets'][ordinal]
            refusal=take('REFUSAL',dict(row=index,packet=ordinal,status=-5 if samples else -2,required=samples,
                supplied=samples-1 if samples else (1<<32)-1,output_equal=1,result_equal=1,info_equal=1,core=core),
                ('allocations_before','allocations_after','releases_before','releases_after'))
            need([integer(refusal[k]) for k in ('allocations_before','allocations_after','releases_before','releases_after')]==[a,a,r,r],
                'actual capacity refusal precedes owner allocation/release and state advancement')
            packet=take('PACKET',dict(row=index,packet=ordinal,block=n,channels=2,floor0=floor0,floor1=2-floor0,
                available=available,discard_start=0,discard_end=available-count,frames=count,position=1,
                end=case['granules'][ordinal],samples=samples,granule=meta['granule'],eos=meta['eos'],gap=meta['gap'],core=core),
                ('bits','eop','allocations','releases','live','bytes'))
            need(integer(packet['bits'])<=meta['bits'] and packet['eop'] in ('0','1'),'actual packet cursor/EOP')
            na,nr,live,payload=(integer(packet[k]) for k in ('allocations','releases','live','bytes'))
            need(na>=a and nr>=r and live>0 and na-nr==live and payload>0,'persistent owner allocation accounting')
            a,r=na,nr;observed_peak_live=max(observed_peak_live,live);observed_peak_bytes=max(observed_peak_bytes,payload)
            untrimmed+=available
            take('INFO',dict(row=index,packet=ordinal,previous=n,known=1,eos=meta['eos'],
                sample_count=untrimmed,prediction=meta['granule'],terminal=meta['eos'],core=core))
            data=bytearray();position=0
            while position<samples:
                length=min(128,samples-position)
                chunk=take('PCM',dict(row=index,packet=ordinal,start=position,count=length,core=core),('runs',))
                words=[];last=None
                for run in chunk['runs'].split(','):
                    match=re.fullmatch(r'([0-9a-f]{4}):([1-9][0-9]*)',run);need(match is not None,'literal S16 decoder RLE')
                    value,length_run=int(match[1],16),integer(match[2],128)
                    need(value!=last and 0<length_run<=length-len(words),'maximal bounded decoder RLE')
                    words.extend([value]*length_run);last=value
                need(len(words)==length,'complete decoder PCM chunk')
                data.extend(struct.pack('<'+'H'*length,*words));position+=length
            parts.append(bytes(data));previous=n
        take('EOS',dict(row=index,measure=-11,process=-11,allocations_delta=0,releases_delta=0,
            output_equal=1,result_equal=1,requirements_equal=1,info_equal=1,core=core))
        take('RESET',dict(row=index,allocations_delta=0,releases_delta=0,primed=0,terminal=0,core=core))
        for ordinal in range(2):
            take('RETRY',dict(row=index,packet=ordinal,samples=len(parts[ordinal])//2,result_equal=1,pcm_equal=1,
                pcm_hash=fnv(parts[ordinal]),allocations_delta=0,releases_delta=0,core=core))
        take('CLEAR',dict(row=index,handle_null=1,allocations=a,releases=a,live=0,bytes=0,caller_live=2,null_noops=1,core=core))
        end=take('END',dict(row=index,status=0,packets=len(case['frames']),frames=sum(case['frames']),
            samples=sum(case['frames'])*2,floor0=floor0*len(case['frames']),floor1=(2-floor0)*len(case['frames']),
            capacity_refusals=len(case['frames']),terminal_refusals=2,resets=1,retries=2,clears=1,
            owner_allocations=a,owner_releases=a,owner_live=0,owner_bytes=0,caller_allocations=2,caller_releases=2,
            caller_live=0,caller_bytes=0,caller_peak_allocations=2,caller_peak_bytes=maximum*4,overhead=overhead,core=core),
            ('owner_peak_allocations','owner_peak_bytes','stack_free','heap_free','heap_min'))
        resource={k:integer(end[k],(1<<32)-1) for k in
            ('owner_peak_allocations','owner_peak_bytes','stack_free','heap_free','heap_min')}
        need(resource['owner_peak_allocations']>=observed_peak_live and resource['owner_peak_bytes']>=observed_peak_bytes and
            0<resource['stack_free']<=16384 and 0<resource['heap_min']<=resource['heap_free'],'native resource observations')
        actual=b''.join(parts);need(len(actual)==case['pcm_bytes'],'every primary decoder PCM byte captured')
        captured[case['id']]=actual
        errors={}
        for label,expected in (('original',references[case['id']]),('xiph',xiph[case['id']])):
            need(len(expected)==len(actual),'complete independent reference PCM')
            differences=[abs(a[0]-b[0]) for a,b in zip(struct.iter_unpack('<h',actual),struct.iter_unpack('<h',expected))]
            errors[label]=max(differences,default=0);need(errors[label]<=2,'unchanged bound2 against '+label+': '+case['id'])
        if output is not None:(output/(f'{index:02}-'+case['id']+'.s16le')).write_bytes(actual)
        metrics.append(dict(id=case['id'],pcm_bytes=len(actual),pcm_sha256=sha(actual),
            maximum_original_error=errors['original'],maximum_xiph_error=errors['xiph'],
            owner_allocations=a,owner_releases=a,caller_allocations=2,caller_releases=2,
            caller_peak_payload_bytes=maximum*4,tracking_overhead_per_allocation=overhead,**resource))
    take('COMPLETE',dict(cases=31,packets=434,frames=184640,samples=369280,capacity_refusals=434,
        terminal_refusals=62,resets=31,retries=62,clears=31,live_owner=0,live_caller=0,core=core))
    take('STOP',dict(status='CAPTURED'));need(next(events,None) is None,'no extra decoder events')
    for relation in model['relations']:
        values=[captured[name] for name in relation['cases']]
        need(all(v==values[0] for v in values[1:])==(relation['kind']=='equal'),'all14 original decoder relations')
    return dict(passed=True,cases=31,packets=434,pcm_bytes=738560,pcm_samples=369280,relations=14,
        maximum_original_error=max(r['maximum_original_error'] for r in metrics),
        maximum_xiph_error=max(r['maximum_xiph_error'] for r in metrics),
        capacity_refusals=434,terminal_refusals=62,no_allocation_resets=31,warm_packet_retries=62,balanced_clears=31,
        warm_PCM_compared_by_memcmp=True,caller_PCM_payload_accounted_separately=True,
        large_resource_control=dict(**resource_control,status=-4,recovered_by_complete_original31=True,
            allocator_budget_used=False),
        pcm_sha256=sha(b''.join(captured[r['id']] for r in model['cases'])),
        coordinator_core=0,worker_core=core,protocol_lines=event_count,rows=metrics)


def protocol_controls(model,references,target):
    core=1 if target=='esp32' else 0;lines=[]
    def event(kind,**values):lines.append('DEC_'+kind+' '+' '.join(str(k)+'='+str(v) for k,v in values.items()))
    event('BEGIN',cases=31,coordinator=0,worker=core,data=ORIGINAL_SHA,
        transport=sha(transport_bytes(model)),resource=sha(resource_bytes()))
    event('WORKER',core=core,priority=3,stack=16384)
    event('RESOURCE',status=-4,channels=255,short=8192,long=8192,identification_bits=233,setup_bits=404,
        failed_bytes=8355840,failures=1,attempts=6,allocations=5,releases=5,live=0,bytes=0,
        handle_null=1,peak_allocations=5,peak_bytes=100,overhead=32,core=core)
    metadata=transport(model)
    for index,row in enumerate(model['cases']):
        event('CASE',row=index,id=row['id'],core=core)
        event('OPEN',row=index,status=0,rate=row['rate'],channels=2,short=row['short_block'],long=row['long_block'],
            allocator_copy=1,headers_poisoned=1,allocations=5,releases=0,live=5,bytes=100,core=core)
        maximum=row['long_block'];event('BUFFER',row=index,samples=maximum,caller_allocations=2,caller_bytes=maximum*4,overhead=32,core=core)
        previous=untrimmed=at=0;parts=[];f0=2 if row['id'].startswith('floor0-') else 0
        for ordinal,count in enumerate(row['frames']):
            n=row['long_block'] if row['modes'][ordinal] else row['short_block'];available=(previous+n)//4 if previous else 0
            samples=count*2;meta=metadata['cases'][index]['packets'][ordinal]
            event('REFUSAL',row=index,packet=ordinal,status=-5 if samples else -2,required=samples,
                supplied=samples-1 if samples else (1<<32)-1,allocations_before=5,allocations_after=5,
                releases_before=0,releases_after=0,output_equal=1,result_equal=1,info_equal=1,core=core)
            event('PACKET',row=index,packet=ordinal,block=n,channels=2,floor0=f0,floor1=2-f0,bits=1,eop=0,
                available=available,discard_start=0,discard_end=available-count,frames=count,position=1,end=meta['granule'],
                samples=samples,granule=meta['granule'],eos=meta['eos'],gap=meta['gap'],allocations=5,releases=0,live=5,bytes=100,core=core)
            untrimmed+=available
            event('INFO',row=index,packet=ordinal,previous=n,known=1,eos=meta['eos'],sample_count=untrimmed,
                prediction=meta['granule'],terminal=meta['eos'],core=core)
            body=references[row['id']][at:at+samples*2];parts.append(body);at+=len(body)
            words=[x[0] for x in struct.iter_unpack('<H',body)]
            for start in range(0,len(words),128):
                chunk=words[start:start+128];runs=[];j=0
                while j<len(chunk):
                    stop=j+1
                    while stop<len(chunk) and chunk[stop]==chunk[j]:stop+=1
                    runs.append(f'{chunk[j]:04x}:{stop-j}');j=stop
                event('PCM',row=index,packet=ordinal,start=start,count=len(chunk),core=core,runs=','.join(runs))
            previous=n
        event('EOS',row=index,measure=-11,process=-11,allocations_delta=0,releases_delta=0,
            output_equal=1,result_equal=1,requirements_equal=1,info_equal=1,core=core)
        event('RESET',row=index,allocations_delta=0,releases_delta=0,primed=0,terminal=0,core=core)
        for ordinal in range(2):event('RETRY',row=index,packet=ordinal,samples=len(parts[ordinal])//2,
            result_equal=1,pcm_equal=1,pcm_hash=fnv(parts[ordinal]),allocations_delta=0,releases_delta=0,core=core)
        event('CLEAR',row=index,handle_null=1,allocations=5,releases=5,live=0,bytes=0,caller_live=2,null_noops=1,core=core)
        event('END',row=index,status=0,packets=14,frames=sum(row['frames']),samples=sum(row['frames'])*2,
            floor0=f0*14,floor1=(2-f0)*14,capacity_refusals=14,terminal_refusals=2,resets=1,retries=2,clears=1,
            owner_allocations=5,owner_releases=5,owner_live=0,owner_bytes=0,owner_peak_allocations=5,owner_peak_bytes=100,
            caller_allocations=2,caller_releases=2,caller_live=0,caller_bytes=0,caller_peak_allocations=2,
            caller_peak_bytes=maximum*4,overhead=32,stack_free=1024,heap_free=4096,heap_min=2048,core=core)
    event('COMPLETE',cases=31,packets=434,frames=184640,samples=369280,capacity_refusals=434,
        terminal_refusals=62,resets=31,retries=62,clears=31,live_owner=0,live_caller=0,core=core)
    event('STOP',status='CAPTURED');valid='\n'.join(lines)+'\n'
    validate_log(valid,model,references,references,target)
    first_pcm=next(line for line in lines if line.startswith('DEC_PCM '));match=re.search(r'runs=([0-9a-f]{4}):',first_pcm)
    altered=first_pcm[:match.start(1)]+f'{int(match[1],16)^0x8000:04x}'+first_pcm[match.end(1):]
    first_packet=next(line for line in lines if line.startswith('DEC_PACKET '))
    reset=next(line for line in lines if line.startswith('DEC_RESET '))
    retry=next(line for line in lines if line.startswith('DEC_RETRY '));hm=re.search(r'pcm_hash=([0-9]+)',retry)
    retry_bad=retry[:hm.start(1)]+str(int(hm[1])^1)+retry[hm.end(1):]
    malformed=[
        valid.replace(f'worker={core}',f'worker={1-core}',1),valid.rsplit('DEC_STOP',1)[0],valid+'DEC_STOP status=CAPTURED\n',
        valid.replace('DEC_CASE ','prefix DEC_CASE ',1),valid.replace('count=128 ','count=127 ',1),
        valid.replace('runs=','runs=0000:129,',1),valid.replace('owner_live=0','owner_live=1',1),valid+'watchdog\n',
        valid.replace('DEC_PACKET ','DEC_ERROR ',1),valid.replace(first_pcm,altered,1),
        valid.replace(first_packet,first_packet+'\n'+first_packet,1),
        valid.replace('allocations_after=5','allocations_after=6',1),valid.replace('output_equal=1','output_equal=0',1),
        valid.replace('measure=-11','measure=-5',1),valid.replace(reset,reset.replace('allocations_delta=0','allocations_delta=1'),1),
        valid.replace(retry,retry_bad,1),valid.replace('handle_null=1','handle_null=0',1),
        valid.replace('transport='+sha(transport_bytes(model)),'transport='+'0'*64,1),
        valid.replace('terminal=1','terminal=0',1),
        valid.replace('failed_bytes=8355840','failed_bytes=8355839',1),
        valid.replace('attempts=6','attempts=5',1),
        valid.replace('RESOURCE status=-4','RESOURCE status=0',1),
        valid.replace('allocations=5 releases=5 live=0','allocations=5 releases=4 live=1',1),
        valid.replace('resource='+sha(resource_bytes()),'resource='+'0'*64,1)]
    for index,text in enumerate(malformed):
        need(text!=valid,'every malformed transcript is a genuine mutation')
        try:validate_log(text,model,references,references,target)
        except ValueError:continue
        raise ValueError('malformed persistent decoder protocol accepted: '+str(index))
    return dict(valid_full_corpus=True,malformed_refused=len(malformed),
        synthetic_protocol_reference_only=True,lifecycle_controls=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=SDK_HEAD, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--protocol-only', action='store_true')
    parser.add_argument('--qemu-timeout', type=int, default=1200)
    args = parser.parse_args()
    need(sys.platform == 'win32' and 1 <= args.qemu_timeout <= 1200, 'pinned native Windows launcher')
    out = args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out != ROOT/'.build' and not out.exists(), 'fresh local campaign')
    out.mkdir(parents=True)
    report = dict(completed=False, passed=False, target=args.target, commands=[], inputs={}, tools={},
                  target_executed=False, production_firmware=False, physical_device=False,
                  Xiph_decoder_executed=False, deferred_scopes_resumed=False, numerical_qualified=False,
                  old_batch_helper_executed=False, persistent_public_decoder=True,
                  transport_origin='frozen raw-fixture metadata; not recovered Ogg/container or HTTP inference')
    def save():
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    def freeze(path, relative):
        target = out/'sources'/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(Path(path).read_bytes())
        report['inputs'][str(Path(path).resolve())] = dict(snapshot=target.relative_to(out).as_posix(), sha256=file_sha(target))
        return target
    private_executables = set()
    def run(name, argv, timeout=60):
        argv = list(map(str, argv))
        row = dict(name=name, argv=[('runtime-path-redacted:'+Path(v).name) if v in private_executables else v for v in argv],
                   state='starting', timeout_seconds=timeout)
        report['commands'].append(row); save()
        child = None; started = time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as stdout, (out/(name+'.stderr.log')).open('xb') as stderr:
                child = subprocess.Popen(argv, cwd=out, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                         creationflags=subprocess.CREATE_NO_WINDOW)
                if name == 'qemu': report['target_executed'] = True
                row.update(state='running', pid=child.pid); save()
                child.wait(timeout=timeout)
                row.update(state='complete', exit_status=child.returncode)
        except BaseException as error:
            row.update(state='failed', error_type=type(error).__name__)
            raise RuntimeError('owned native command failed: '+name) from None
        finally:
            if child is not None and child.poll() is None:
                stopped = subprocess.run(['taskkill.exe', '/PID', str(child.pid), '/T', '/F'], capture_output=True,
                                         timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(state='forced_stop_nonpass', tree_stop_returncode=stopped.returncode)
                if child.poll() is None: child.kill()
                child.wait(timeout=15)
            row['elapsed_seconds'] = time.monotonic()-started
            for stream in ('stdout', 'stderr'):
                path = out/(name+'.'+stream+'.log')
                row[stream+'_sha256'] = file_sha(path) if path.exists() else None
            if child is not None: row['exit_status'] = child.poll()
            save()
        need(row['state'] == 'complete' and row['exit_status'] == 0, 'native command terminal0: '+name)
        return (out/(name+'.stdout.log')).read_text('utf-8', errors='replace').replace('\r\n', '\n')
    save()
    try:
        original, model, references = original_inputs()
        xiph_capture, xiph = saved_xiph(model)
        (out/'original31.json').write_bytes(original)
        (out/'saved-Xiph-PCM.bin').write_bytes(xiph_capture)
        (out/'transport.json').write_bytes(transport_bytes(model))
        (out/'resource.json').write_bytes(resource_bytes())
        (out/'cases.h').write_bytes(header(model))
        (out/'reference').mkdir()
        for row in model['cases']:
            (out/'reference'/Path(row['reference_path']).name).write_bytes(references[row['id']])
        report['protocol_controls'] = protocol_controls(model, references, args.target)
        report.update(original_sha256=ORIGINAL_SHA, original_archive_sha256=ORIGINAL_ARCHIVE_SHA,
                      reference_archive_sha256=REFERENCE_ARCHIVE_SHA, cases=31, packets=434,
                      pcm_bytes=738560, original_relations=14, max_abs_error_bound=2,
                      saved_Xiph_capture_sha256=sha(xiph_capture), transport_sha256=sha(transport_bytes(model)),
                      resource_sha256=sha(resource_bytes()),
                      reference_controller_sha256=REFERENCE_CONTROLLER_SHA,
                      direct_public_APIs=['replace','measure','process','info','reset','clear'],
                      runtime_profile=dict(coordinator_core=0,worker_core=1 if args.target=='esp32' else 0,
                          worker_priority=3,worker_stack_bytes=16384,watchdog_enabled=True,idle_watchdog_enabled=True))
        if args.protocol_only:
            report.update(completed=True, protocol_only=True); save()
            print(json.dumps(report['protocol_controls'])); return 0
        freeze(Path(__file__), Path('controller.py'))
        design_reference = ROOT/'tests/test-vorbis-synthesis-qemu.py'
        need(file_sha(design_reference) == REFERENCE_CONTROLLER_SHA, 'pinned frozen native design reference')
        freeze(design_reference, Path('design-reference/synthesis-controller.py'))
        for name in COMPONENTS:
            for path in sorted((ROOT/'idf/components'/name).rglob('*')):
                if path.is_file(): freeze(path, Path('components')/name/path.relative_to(ROOT/'idf/components'/name))
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file(): freeze(path, Path('project')/path.relative_to(PROJECT))
        shutil.copytree(out/'sources/project', out/'project')
        shutil.copyfile(out/'cases.h', out/'project/main/cases.h')
        shutil.copyfile(out/'project'/('sdkconfig.'+args.target+'.defaults'), out/'project/sdkconfig.defaults')
        report.update(prepared=True, cases_header_sha256=file_sha(out/'cases.h')); save()
        if args.prepare_only:
            print(json.dumps(dict(prepared=True, cases=31, packets=434))); return 0
        if args.target == 'esp32':
            sdk = REPO/'.idf/v6.0.2'; tools = REPO/'.idf/tools-v6.0.2'
            py = tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe'
            qemu = ROOT/'.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
        else:
            sdk = REPO/'.idf/v6.1-9a97f6c54ec6'; tools = REPO/'.idf/tools-v6.1'
            py = tools/'python_env/idf6.1_py3.12_env/Scripts/python.exe'
            qemu = Path('C:/Work/QEMU-ESP32/bin/qemu-system-riscv32.exe')
        ps = Path(shutil.which('pwsh.exe') or '')
        git = Path(shutil.which('git.exe') or shutil.which('git') or '')
        rom = Path('C:/Work/QEMU-ESP32/pc-bios')
        for alias, path in (('powershell', ps), ('python', py), ('qemu', qemu), ('git', git)):
            need(path.is_file(), 'installed native tool: '+alias)
            private = bool(re.search(r'(?i)[/\\]Users[/\\]', str(path)))
            if private: private_executables.add(str(path))
            report['tools'][alias] = dict(sha256=file_sha(path), path='runtime-path-redacted' if private else str(path),
                                         personal_path_redacted=private)
        need(file_sha(qemu) == QEMU_SHA[args.target], 'pinned target QEMU executable')
        report['roms'] = {p.name: file_sha(p) for p in sorted(rom.glob(args.target+'*rom*.bin'))}
        need(report['roms'], 'explicit target ROM')
        need(run('sdk-head', [git, '-c', 'core.longpaths=true', '-C', sdk, 'rev-parse', 'HEAD']).strip() == SDK_HEAD[args.target],
             'pinned SDK revision')
        need(not run('sdk-clean', [git, '-c', 'core.longpaths=true', '-C', sdk, 'status', '--porcelain', '--untracked-files=no']).strip(),
             'clean SDK')
        report['sdk_revision'] = SDK_HEAD[args.target]
        run('build', [ps, '-NoProfile', '-NonInteractive', '-File', out/'sources/project/sdk-build.ps1', '-Campaign', out,
            '-SdkDirectory', sdk, '-ToolsDirectory', tools, '-PythonExecutable', py, '-Target', args.target,
            '-CasesSha256', ORIGINAL_SHA, '-CasesHeaderSha256', file_sha(out/'cases.h')], 1200)
        child = json.loads((out/'sdk-child.json').read_text('utf-8-sig'))
        need(child['exit_status'] == 0 and child['pid'] > 0, 'actual SDK child terminal')
        report['sdk_child'] = child
        build = out/'build'; description = json.loads((build/'project_description.json').read_bytes())
        elf = build/description['app_elf']; elf_body = elf.read_bytes()
        need(elf.resolve().is_relative_to(build) and elf_body[:6] == b'\x7fELF\x01\x01' and
             int.from_bytes(elf_body[18:20], 'little') == (94 if args.target == 'esp32' else 243), 'native ELF32 machine')
        compiler = Path(description['c_compiler']); nm = compiler.with_name(compiler.name.replace('gcc', 'nm'))
        report['tools']['compiler'] = dict(path=str(compiler), sha256=file_sha(compiler))
        report['tools']['nm'] = dict(path=str(nm), sha256=file_sha(nm))
        database = json.loads((build/'compile_commands.json').read_bytes())
        selected = [row for row in database if Path(row['file']).resolve().is_relative_to(out/'sources/components') or
                    Path(row['file']).resolve().is_relative_to(out/'project/main')]
        need(len(selected) == 22, 'all21 public component units and direct owner fixture')
        need(not any('vorbis_synthesis_pipeline' in row['file'] for row in database), 'old batch helper not compiled')
        need(all(all(flag in row['command'] for flag in ('-fstack-usage', '-fno-fast-math', '-ffp-contract=off'))
                 for row in selected), 'actual numeric compiler flags')
        report['compile_rows'] = selected
        symbols = run('symbols', [nm, '-n', '-S', elf])
        for symbol in ('native_vorbis_decoder_replace', 'native_vorbis_decoder_measure', 'native_vorbis_decoder_process',
                       'native_vorbis_decoder_info', 'native_vorbis_decoder_reset', 'native_vorbis_decoder_clear',
                       'native_vorbis_setup_owner_replace', 'native_vorbis_frame_decode',
                       'native_vorbis_frame_floor0_prepare', 'native_vorbis_imdct_transform_binary64', 'native_vorbis_synthesis_push',
                       'native_vorbis_pcm_s16_product_pair'):
            need(re.search(r'\b'+symbol+r'$', symbols, re.M), 'linked exercised symbol: '+symbol)
        need(not re.search(r'\b(?:vorbis_synthesis|esp_vorbis_dec_open|vorbis_synthesis_pipeline_run)$', symbols, re.M),
             'owned public decoder only; no old batch helper')
        usage = []
        for row in selected:
            path = build/Path(row['output']).with_suffix('.su')
            need(path.is_file(), 'actual stack record'); usage.append(path)
        report['stack_records'] = {p.relative_to(out).as_posix(): p.read_text('utf-8').splitlines() for p in usage}
        recipe = json.loads((build/'flasher_args.json').read_bytes())
        need(recipe['flash_settings'] == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m'), 'isolated DIO profile')
        flashes = {int(offset, 0): (build/name).resolve() for offset, name in recipe['flash_files'].items()}
        need(set(flashes) == ({4096, 32768, 65536} if args.target == 'esp32' else {0, 32768, 65536}) and
             all(path.is_relative_to(build) for path in flashes.values()), 'bounded image recipe')
        flash = out/'qemu-flash.bin'
        argv = [py, '-m', 'esptool', '--chip', args.target, 'merge-bin', '--output', flash,
                '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
        for offset, path in sorted(flashes.items()): argv += [hex(offset), path]
        run('merge', argv+['--pad-to-size', '4MB'])
        config = (out/'sdkconfig').read_text().replace('\r\n', '\n')
        need(bool(re.search(r'^CONFIG_FREERTOS_UNICORE=y$', config, re.M)) == (args.target == 'esp32c3'), 'native core profile')
        for setting in ('CONFIG_ESP_TASK_WDT_EN=y', 'CONFIG_ESP_TASK_WDT_INIT=y', 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0=y'):
            need(setting in config, 'watchdog and idle0 remain enabled')
        if args.target == 'esp32': need('CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=y' in config, 'idle1 remains enabled')
        qargs = [qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet'] if args.target == 'esp32' else [qemu, '-M', 'esp32c3']
        qargs += ['-smp', '2' if args.target == 'esp32' else '1', '-L', rom, '-display', 'none', '-monitor', 'none',
                  '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none', '-drive', 'file='+str(flash)+',if=mtd,format=raw']
        report['target_launch_attempted'] = True; save()
        log = run('qemu', qargs, args.qemu_timeout)
        (out/'pcm').mkdir()
        measured = validate_log(log+'\n'+(out/'qemu.stderr.log').read_text('utf-8', errors='replace'),
                                model, references, xiph, args.target, out/'pcm')
        (out/'measurement.json').write_text(json.dumps(measured, indent=2)+'\n', encoding='utf-8')
        need(all(file_sha(path) == pin['sha256'] == file_sha(out/pin['snapshot']) for path, pin in report['inputs'].items()),
             'all original and frozen source inputs unchanged')
        outputs = [elf, elf.with_suffix('.map'), flash, out/'sdkconfig', out/'sdk-child.json', *usage, *flashes.values()]
        outputs += [build/name for name in ('compile_commands.json', 'project_description.json', 'flasher_args.json',
                    'CMakeCache.txt', 'config/sdkconfig.h', 'build.ninja', 'CMakeFiles/rules.ninja')]
        outputs += [p for p in build.rglob('*.obj') if p.is_file()]
        report['build_outputs'] = {p.relative_to(out).as_posix(): file_sha(p) for p in outputs}
        report.update(completed=True, passed=True, numerical_qualified=True,
                      measurements={k: v for k, v in measured.items() if k != 'rows'},
                      measurement_sha256=file_sha(out/'measurement.json'))
        save(); print(json.dumps(dict(completed=True, target=args.target, **report['measurements']))); return 0
    except BaseException as error:
        report.update(error_type=type(error).__name__, error=str(error)); save(); raise


if __name__ == '__main__':
    raise SystemExit(main())
