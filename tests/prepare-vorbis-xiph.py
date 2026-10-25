"""Export the unchanged original31 raw Vorbis cases and retained Xiph PCM.

Reads existing evidence only. No codec, compiler, SDK, generator or subprocess
runs. Ogg pages are checked solely to retain original packet metadata.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import sys
import wave
ROOT=Path(__file__).resolve().parents[1]
PREP=ROOT/'.build/vorbis-format31-current-prep-01'
PINS={'contract.json':'ef8823f169d08b98fe5586221a7ab9a64904373e3be4f212631a58d1fcdc24ff','source-map.json':'f81cfc76044f7d4d1ad9949b8376945afd82815d001b9a4af1672acbb63f0c16','reference-binding31.json':'a13275e2663a428895b326fbfbf9d38458f23b0eeee0811406f39e6dab3874b5','data.h':'433ffdc59206485e0650c9fbbb0796bf053725c9dacf0cbdd6c3ebf826318cdf'}
CONTRACT='419efac93fc69c65dc162f6b45017b0eb81a276f8de95d50d6f9d1bd06e5aa02'
COMMENT='e44f437158767cf8fdbaae25daa1f04ad1227d7adfc542e27e85d1586b22caba'
PCM_POLICY=dict(schema='xiph-float-to-s16le-v1',finite_required=True,scale=32768,rounding='nearest; ties to even',clip=[-32768,32767],interleave='original L/R',dither=False,
    drain='pcmout/read after every original packet; no lapout or synthetic flush',reference='Retained FFmpeg8.1.1 libvorbis -> pcm_s16le +bitexact',
    source='https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/libswresample/audioconvert.c#L72')
POLICY=dict(scope='unchanged original31 bounded regression, not complete conformance',max_abs_error=2,required_cases=31,required_audio_packets=434,required_pcm_bytes=738560,
    alignment='All original zero-lag L/R samples and packet spans; no trim, shift, gain fit, swap, resampling or subset',required_relations=14)
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(body):return hashlib.sha256(body).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def wav_pcm(body,rate,frames):
    with wave.open(io.BytesIO(body),'rb')as stream:
        need(stream.getcomptype()=='NONE'and stream.getnchannels()==2 and stream.getsampwidth()==2 and stream.getframerate()==rate and stream.getnframes()==frames,'complete original stereo S16 reference WAV')
        pcm=stream.readframes(frames+1)
    need(len(pcm)==frames*4,'whole untrimmed reference PCM');return pcm

def pages(body):
    """Restricted original carrier reader: one complete packet on each page."""
    result=[];offset=0;serial=None
    while offset<len(body):
        need(body[offset:offset+4]==b'OggS'and offset+27<=len(body),'original page header');version,flags,gp,sn,seq,checksum,count=struct.unpack_from('<BBQIIIB',body,offset+4);need(version==0 and seq==len(result)and (serial is None or serial==sn),'original version/serial/page ordering');serial=sn
        laces=body[offset+27:offset+27+count];need(len(laces)==count and count>0 and laces[-1]<255 and all(value==255 for value in laces[:-1]),'one complete original packet per page');stop=offset+27+count+sum(laces);need(stop<=len(body),'whole page bytes');page=bytearray(body[offset:stop]);page[22:26]=b'\0'*4;crc=0
        for value in page:
            crc^=value<<24
            for _ in range(8):crc=((crc<<1)^0x04c11db7 if crc&0x80000000 else crc<<1)&0xffffffff
        need(crc==checksum,'original page CRC');result.append(dict(packet=body[offset+27+count:stop],flags=flags,granule=gp,packetno=seq));offset=stop
    need(offset==len(body)and len(result)==17,'all original3headers/14audio pages');return result

def validate_model(model):
    need(model['schema']=='xiph-original31-raw-v1'and model['contract_sha256']==CONTRACT and model['pcm_policy']==PCM_POLICY and model['policy']==POLICY,'fixed raw31 model/policies');rows=model['cases'];need(len(rows)==31 and [row['case']for row in rows]==list(range(31)),'complete ordered original31');seen=set()
    for row in rows:
        need(re.fullmatch(r'[A-Za-z0-9_-]{1,63}',row['id'])and row['id']not in seen,'unique original id');seen.add(row['id']);need(row['channels']==2 and row['rate']in(48000,192000),'original reference channel/rate layout')
        for stem,kind in(('identification',1),('comment',3),('setup',5)):
            body=bytes.fromhex(row[stem+'_hex']);need(body[:7]==bytes([kind])+b'vorbis','original complete header envelope')
        need(len(bytes.fromhex(row['identification_hex']))==30 and sha(bytes.fromhex(row['comment_hex']))==COMMENT,'original identification/comment bytes')
        need(len(row['offsets'])==15 and row['offsets'][0]==0 and row['offsets'][-1]==len(bytes.fromhex(row['audio_hex']))and all(a<b for a,b in zip(row['offsets'],row['offsets'][1:])),'all14 original packet spans')
        need(len(row['modes'])==len(row['granules'])==len(row['frames'])==14 and row['frames'][0]==0 and all(value in(0,1)for value in row['modes']),'original modes/frames/granules')
        total=0
        for size,granule in zip(row['frames'],row['granules']):total+=size;need(total==granule,'original cumulative granules')
        need(total*4==row['pcm_bytes']and re.fullmatch('[0-9a-f]{64}',row['reference_pcm_sha256']),'original full PCM byte count')
    need(sum(len(row['frames'])for row in rows)==434 and sum(row['pcm_bytes']for row in rows)==738560 and len(model['relations'])==14,'whole31 packet/PCM/relation scope');return rows

def target_header(model):
    rows=validate_model(model);lines=['#pragma once','#include <stdint.h>','#define XIPH_CASE_COUNT 31','#define XIPH_TOTAL_PACKETS 434','#define XIPH_EXPECTED_PCM_BYTES 738560',
        '#define XIPH_MODEL_SHA256 "'+sha(canonical(model))+'"','#define XIPH_PCM_POLICY_SHA256 "'+sha(canonical(PCM_POLICY))+'"',
        'typedef struct { const char *id; uint32_t rate,channels,short_block,long_block;',
        ' const uint8_t *identification; uint32_t identification_bytes; const uint8_t *comment; uint32_t comment_bytes;',
        ' const uint8_t *setup; uint32_t setup_bytes; const uint8_t *audio; uint32_t audio_bytes;',
        ' const uint32_t *offsets; const uint8_t *modes; const int64_t *granules; const uint32_t *frames; uint32_t packet_count,pcm_bytes; } xiph_case_t;']
    for i,row in enumerate(rows):
        for stem in('identification','comment','setup','audio'):
            body=bytes.fromhex(row[stem+'_hex']);lines.append('static const uint8_t xiph_'+stem+'_'+str(i)+'[] = {'+','.join('UINT8_C(0x'+f'{x:02x}'+')'for x in body)+'};')
        for stem,ctype,macro in(('offsets','uint32_t','UINT32_C'),('modes','uint8_t','UINT8_C'),('granules','int64_t','INT64_C'),('frames','uint32_t','UINT32_C')):
            lines.append('static const '+ctype+' xiph_'+stem+'_'+str(i)+'[] = {'+','.join(macro+'('+('0x'+f'{x:02x}'if stem=='modes'else str(x))+')'for x in row[stem])+'};')
    lines.append('static const xiph_case_t xiph_cases[XIPH_CASE_COUNT] = {')
    for i,row in enumerate(rows):
        values=['"'+row['id']+'"']+[str(row[key])for key in('rate','channels','short_block','long_block')]
        for stem in('identification','comment','setup','audio'):values+=['xiph_'+stem+'_'+str(i),str(len(row[stem+'_hex'])//2)]
        values+=['xiph_'+stem+'_'+str(i)for stem in('offsets','modes','granules','frames')]+['14',str(row['pcm_bytes'])];lines.append('    {'+','.join(values)+'},')
    return '\n'.join(lines+['};',''])

def reference_argv(ffmpeg,folder):
    return [ffmpeg,'-nostdin','-n','-hide_banner','-loglevel','error','-xerror','-err_detect','explode','-c:a','libvorbis','-i',str(folder/'input.ogg'),'-map','0:a:0','-map_metadata','-1','-fflags','+bitexact','-flags:a','+bitexact','-c:a','pcm_s16le','-f','wav',str(folder/'libvorbis.wav'),'-map','0:a:0','-map_metadata','-1','-flags:a','+bitexact','-c:a','pcm_s16le','-f','framemd5','-']
def frame_md5(body,pcm,rate,frames):
    text=body.decode('utf-8').replace('\r\n','\n');need('#codec_id 0: pcm_s16le'in text and '#sample_rate 0: '+str(rate)in text,'reference framemd5 metadata');rows=[line for line in text.splitlines()if line and not line.startswith('#')];need(len(rows)==13 and frames[0]==0,'reference13nonprimer frame rows');offset=timestamp=0
    for line,count in zip(rows,frames[1:]):
        fields=[x.strip()for x in line.split(',')];need(len(fields)==6 and list(map(int,fields[:5]))==[0,timestamp,timestamp,count,count*4]and hashlib.md5(pcm[offset:offset+count*4]).hexdigest()==fields[5],'every original reference packet PTS/count/MD5');offset+=count*4;timestamp+=count
    need(offset==len(pcm),'whole reference packet coverage')

def prepare(out):
    need(out.is_relative_to(ROOT/'.build')and out!=ROOT/'.build'and not out.exists(),'fresh task-local output');out.mkdir(parents=True);(out/'inputs').mkdir();(out/'reference').mkdir();ledger={}
    def read(path,pin=None):
        path=path.resolve();need(path.is_relative_to(ROOT),'task corpus source boundary');body=path.read_bytes();digest=sha(body);need(pin is None or digest==pin,'frozen source identity: '+str(path));name='inputs/'+digest
        if not(out/name).exists():(out/name).write_bytes(body)
        row=dict(sha256=digest,bytes=len(body),snapshot=name);need(str(path)not in ledger or ledger[str(path)]==row,'one source identity');ledger[str(path)]=row;return body
    read(Path(__file__));contract=json.loads(read(PREP/'contract.json',PINS['contract.json']));mapping=json.loads(read(PREP/'source-map.json',PINS['source-map.json']));binding=json.loads(read(PREP/'reference-binding31.json',PINS['reference-binding31.json']));read(PREP/'data.h',PINS['data.h']);need(sha(canonical(contract['model']))==contract['contract_sha256']==CONTRACT and len(mapping['cases'])==len(binding['cases'])==31,'original complete31 contract/source/reference binding')
    sources={}
    for scope in binding['source_scopes']:
        path=ROOT/scope['host_path'];host=json.loads(read(path,scope['host_sha256']));qualified=json.loads(read(ROOT/scope['qualification_path'],scope['qualification_sha256']));receipt=json.loads(read(ROOT/scope['receipt_path'],scope['receipt_sha256']));need(receipt['status']=='TERMINAL'and receipt['returncode']==scope['original_returncode']==1 and not receipt.get('timed_out')and not receipt.get('interrupted')and not receipt.get('error_type'),'actual historical reference campaign terminal');sources[scope['qualification_sha256']]=(path.parent,host,qualified)
    cases=[];book_matrices={}
    for index,(row,origin,accepted)in enumerate(zip(contract['model']['cases'],mapping['cases'],binding['cases'])):
        need(index==accepted['case']==origin['case']and row['id']==origin['id']==accepted['id']and accepted['xiph_qualified_existing']is True,'original ordered case/reference roles');matrix_path=Path(origin['original_matrix']['path']);matrix=json.loads(read(matrix_path,origin['original_matrix']['sha256']));fields=origin['original_case_fields'];need(fields in matrix['cases'],'original matrix case');book_matrices[origin['original_group']]=matrix;raw={stem:read(matrix_path.parent/fields[stem])for stem in('identification','comment','setup','audio','ogg')}
        for stem in('identification','setup','audio'):need(sha(raw[stem])==row['raw_sha256'][stem]==accepted['raw_sha256'][stem],'unchanged original raw bytes')
        need(sha(raw['comment'])==COMMENT,'unchanged original58byte comment');carrier=pages(raw['ogg']);packets=[raw['identification'],raw['comment'],raw['setup']]+[raw['audio'][a:b]for a,b in zip(row['offsets'],row['offsets'][1:])]
        need([p['packet']for p in carrier]==packets and [p['flags']for p in carrier]==[2]+[0]*15+[4]and [p['granule']for p in carrier]==[0,0,0]+fields['packet_granules'],'exact original page packets/BOS/EOS/granules')
        folder,host,qualified=sources[accepted['qualification_sha256']];reference_id=accepted['original_reference_id'];host_case=next(c for c in host['cases']if c['id']==reference_id);qualified_case=next(c for c in qualified['cases']if c['id']==reference_id);need(qualified_case['pcm_sha256']==accepted['reference_pcm_sha256'],'retained qualified Xiph PCM');info=host_case['decoded']['libvorbis'];case_folder=folder/'cases'/reference_id;command=next(c for c in host['commands']if c['name']=='cases/'+reference_id+'/decode-libvorbis');child=json.loads(read(folder/command['receipt'],command['sha256']));ffmpeg=next(p for p in host['tools']if Path(p).name=='ffmpeg.exe')
        need(child['status']=='TERMINAL'and type(child['returncode'])is int and child['returncode']==0 and child['argv']==reference_argv(ffmpeg,case_folder)and child['executable_sha256']==host['tools'][ffmpeg]and child['runner_sha256']==host['capture_sha256']and not child.get('timed_out')and not child.get('interrupted')and not child.get('error_type'),'actual retained untransformed Xiph decoder child')
        need(read(case_folder/'input.ogg',host_case['ogg_sha256'])==raw['ogg'],'actual reference input carrier equals original');streams={}
        for stem in('stdout','stderr'):
            name='decode-libvorbis.'+stem+'.log';pins=[pin for p,pin in child['logs'].items()if Path(p).name==name];need(len(pins)==1,'unique actual reference stream');streams[stem]=read(case_folder/name,pins[0]['sha256'])
        need(not streams['stderr'],'strict accepted reference error stream');wav=read(case_folder/'libvorbis.wav',accepted['reference_wav_sha256']);need(sha(wav)==info['wav_sha256'],'actual reference WAV identity');pcm=wav_pcm(wav,row['rate'],sum(row['frames']));need(sha(pcm)==accepted['reference_pcm_sha256']==info['pcm_sha256']and len(pcm)==row['total_pcm'],'whole original reference PCM');frame_md5(streams['stdout'],pcm,row['rate'],row['frames']);filename='reference/'+str(index).zfill(2)+'-'+row['id']+'.s16le';(out/filename).write_bytes(pcm)
        cases.append(dict(case=index,id=row['id'],rate=row['rate'],channels=row['channels'],short_block=row['short'],long_block=row['long'],identification_hex=raw['identification'].hex(),comment_hex=raw['comment'].hex(),setup_hex=raw['setup'].hex(),audio_hex=raw['audio'].hex(),offsets=row['offsets'],modes=row['modes'],granules=fields['packet_granules'],frames=row['frames'],pcm_bytes=row['total_pcm'],reference_pcm_sha256=sha(pcm),reference_path=filename))
    relations=[]
    for group in('books8','newbooks8'):
        matrix=book_matrices[group]
        relations +=[dict(kind='equal',cases=ids)for ids in matrix['expected_same_decoder_pcm_equal_groups']]
        relations +=[dict(kind='different',cases=ids)for ids in matrix.get('expected_same_decoder_pcm_different_pairs',[])]
    relations +=[dict(kind='equal',cases=[cases[19+i]['id'],cases[25+i]['id']])for i in range(6)]
    model=dict(schema='xiph-original31-raw-v1',contract_sha256=CONTRACT,pcm_policy=PCM_POLICY,policy=POLICY,relations=relations,cases=cases);validate_model(model);(out/'cases.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');(out/'cases.h').write_text(target_header(model),encoding='ascii',newline='\n')
    need(all(sha(Path(path).read_bytes())==pin['sha256']for path,pin in ledger.items()),'every consumed historical source unchanged');report=dict(completed=True,passed=False,prepared=True,codec_or_compiler_or_SDK_executed=False,model_sha256=sha(canonical(model)),files={name:sha((out/name).read_bytes())for name in('cases.json','cases.h')},inputs=ledger,cases=31,packets=434,pcm_bytes=738560,policy=POLICY)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();print(json.dumps(prepare(args.output.resolve())));return 0
if __name__=='__main__':sys.exit(main())
