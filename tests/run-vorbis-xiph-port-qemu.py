"""Isolated declared Xiph resource port and original31 PCM capture."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'tests/target/vorbis_xiph_port_qemu'
COMPONENT=ROOT/'idf/components/native_vorbis_xiph'
MANIFEST=COMPONENT/'component-manifest.json'
PORT=ROOT/'idf/components/native_vorbis_xiph_port'
PORT_MANIFEST=PORT/'port-manifest.json'
BASE_READER=ROOT/'tests/run-vorbis-xiph-qemu.py'
BASE_READER_SHA256='837847878b19e352db8188b6927a3b3a91449bee74be9b59e93a9a110066c1d9'
HELPERS=('vorbis_xiph_alloc.h','vorbis_xiph_alloc_inject.h','vorbis_xiph_alloc.c','vorbis_xiph_arena.c','vorbis_xiph_books.c','vorbis_xiph_bits.c','vorbis_xiph_residue.c','vorbis_xiph_headers.c','vorbis_xiph_dsp.c')
BOOK_CHECKS=200864
BIT_CHECKS=124754
RESIDUE_CHECKS=3997
HEADER_CHECKS=1598
DSP_CHECKS=3584
PRIVATE_HEADER='native_vorbis_xiph_header_error.h'
DSP_PRIVATE_HEADER='native_vorbis_xiph_dsp_error.h'
PRIVATE_HEADERS=(PRIVATE_HEADER,DSP_PRIVATE_HEADER)
PORTED_UNITS={'upstream/libvorbis/lib/'+name+'.c'for name in('block','sharedbook','codebook','floor0','floor1','res0','mapping0','info','mdct')}|{'upstream/libogg/src/bitwise.c'}
SDK_HEAD={'esp32':'7101770dc6db2667b3c477cc31365dd1acd6db4e'}
VORBIS_UNITS=('mdct','smallft','block','envelope','window','lsp','lpc','analysis','synthesis','psy','info','floor1','floor0','res0','mapping0','registry','codebook','sharedbook','lookup','bitrate')
PUBLIC=('vorbis_synthesis_headerin','vorbis_synthesis_init','vorbis_block_init','vorbis_synthesis','vorbis_synthesis_blockin','vorbis_synthesis_pcmout','vorbis_synthesis_read','vorbis_block_clear','vorbis_dsp_clear','vorbis_comment_clear','vorbis_info_clear','vorbis_version_string')
CONTROL_COUNT=17

def need(ok,reason):
    if not ok:raise ValueError(reason)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def normalize(value):return str(value).replace('\\','/').rstrip('/')

def sequence(body,pattern):
    matches,cursor=list(pattern.finditer(body)),0
    for index,match in enumerate(matches):
        need(re.fullmatch(r'\s*'if not index else r'\s*,\s*',body[cursor:match.start()]),'literal C comma separators');cursor=match.end()
    need(re.fullmatch(r'\s*,?\s*',body[cursor:]),'literal C tail');return matches

def validate_manifest(document):
    need(document['schema']=='native-vorbis-xiph-source-v1'and isinstance(document['files'],dict),'complete component manifest schema')
    for name,digest in document['files'].items():
        path=PurePosixPath(name);need(name==path.as_posix()and not path.is_absolute()and '..'not in path.parts and ':'not in name and '\\'not in name and name!='component-manifest.json'and re.fullmatch('[0-9a-f]{64}',digest),'exact relative component identity')
    expected={'upstream/libvorbis/lib/'+name+'.c'for name in VORBIS_UNITS}|{'upstream/libogg/src/bitwise.c','upstream/libogg/src/framing.c'}
    need(isinstance(document['compile_sources'],list)and len(document['compile_sources'])==22 and set(document['compile_sources'])==expected and expected<=document['files'].keys(),'all twenty-two unchanged core translation units')
    need({'CMakeLists.txt','SOURCE.json','platform/ogg/config_types.h','upstream/libvorbis/include/vorbis/codec.h','upstream/libogg/include/ogg/ogg.h'}<=document['files'].keys(),'component/platform/public-source closure')
    return document

def validate_cases(document,header):
    need(document['schema']=='xiph-original31-raw-v1'and re.fullmatch('[0-9a-f]{64}',document['contract_sha256'])and isinstance(document['cases'],list)and len(document['cases'])==31,'unchanged complete original31 contract')
    rows,ids=document['cases'],set()
    for i,row in enumerate(rows):
        need(row['case']==i and isinstance(row['id'],str)and re.fullmatch('[A-Za-z0-9_-]{1,63}',row['id'])and row['id']not in ids,'ordered unique original identities');ids.add(row['id'])
        need(all(type(row[k])is int and 0<row[k]<=0xffffffff for k in ('rate','channels','short_block','long_block','pcm_bytes'))and row['channels']<=255,'original declared format fields')
        for stem,signature in (('identification','01766f72626973'),('comment','03766f72626973'),('setup','05766f72626973'),('audio','')):
            body=row[stem+'_hex'];need(isinstance(body,str)and re.fullmatch('(?:[0-9a-f]{2})+',body)and len(body)<=2097152 and body.startswith(signature),'exact nonempty original raw packets')
        for key,n,limit in (('offsets',15,0xffffffff),('modes',14,1),('frames',14,0xffffffff)):
            need(isinstance(row[key],list)and len(row[key])==n and all(type(x)is int and 0<=x<=limit for x in row[key]),'exact original packet metadata')
        need(isinstance(row['granules'],list)and len(row['granules'])==14 and all(type(x)is int and -(1<<63)<=x<(1<<63)for x in row['granules']),'original signed64 granules')
        need(row['offsets'][0]==0 and row['offsets'][-1]==len(row['audio_hex'])//2 and all(a<b for a,b in zip(row['offsets'],row['offsets'][1:])),'all original audio packet spans')
        need(sum(row['frames'])*row['channels']*2==row['pcm_bytes']and re.fullmatch('[0-9a-f]{64}',row['reference_pcm_sha256']),'retained PCM byte contract')
    need(sum(r['pcm_bytes']for r in rows)==738560,'original whole31 PCM size')
    for define,value in (('XIPH_CASE_COUNT',31),('XIPH_TOTAL_PACKETS',434),('XIPH_EXPECTED_PCM_BYTES',738560)):
        need(re.findall(r'^#define\s+'+define+r'\s+(\d+)\s*$',header,re.M)==[str(value)],'one original count macro')
    specs=[(stem,'uint8_t',r'UINT8_C\(0x([0-9a-f]{2})\)',16)for stem in ('identification','comment','setup','audio','modes')]+[(stem,'uint32_t',r'UINT32_C\((0|[1-9][0-9]*)\)',10)for stem in ('offsets','frames')]+[('granules','int64_t',r'INT64_C\((0|-?[1-9][0-9]*)\)',10)]
    for stem,ctype,pattern,base in specs:
        found={}
        for match in re.finditer(r'static\s+const\s+'+ctype+r'\s+xiph_'+stem+r'_(\d+)\[\]\s*=\s*\{(.*?)\};',header,re.S):
            i=int(match[1]);need(i not in found,'unique literal input array');found[i]=[int(m[1],base)for m in sequence(match[2],re.compile(pattern))]
        wanted={i:list(bytes.fromhex(r[stem+'_hex']))if stem in('identification','comment','setup','audio')else r[stem]for i,r in enumerate(rows)};need(found==wanted,'all original input/metadata bytes read back')
    arrays=re.findall(r'xiph_cases\[[^]]*\]\s*=\s*\{(.*?)\};',header,re.S);need(len(arrays)==1,'one original descriptor array');descriptors=sequence(arrays[0],re.compile(r'\{([^{}]*)\}'));need(len(descriptors)==31,'all original descriptors')
    for i,(row,match)in enumerate(zip(rows,descriptors)):
        expected=['"'+row['id']+'"']+[str(row[k])for k in ('rate','channels','short_block','long_block')]
        for stem in ('identification','comment','setup','audio'):expected+=['xiph_'+stem+'_'+str(i),str(len(row[stem+'_hex'])//2)]
        expected+=['xiph_'+stem+'_'+str(i)for stem in ('offsets','modes','granules','frames')]+['14',str(row['pcm_bytes'])]
        need([re.sub(r'\s+','',x)for x in match[1].split(',')]==expected,'all nineteen literal descriptor fields')
    return rows

def validate_log(log,rows,target,data_sha256,component_sha256):
    need(target=='esp32','first upstream baseline is ESP32')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|stack overflow|timed out',log,re.I),'native panic/corruption/timeout')
    lines=log.splitlines();need(not any('XIPH_'in line and not line.startswith('XIPH_')for line in lines),'foreign/torn capture event');events=[line for line in lines if line.startswith('XIPH_')];cursor,captured=0,[]
    def take(kind,expected,extra=()):
        nonlocal cursor
        need(cursor<len(events),'missing ordered Xiph event');tokens=events[cursor].split(' ');cursor+=1;need(tokens[0]=='XIPH_'+kind and all(t.count('=')==1 for t in tokens[1:]),'event syntax/kind');fields=dict(t.split('=')for t in tokens[1:])
        need(len(fields)+1==len(tokens)and set(fields)==set(expected)|set(extra)and all(fields[k]==str(v)for k,v in expected.items()),'unique exact event fields');return fields
    def integer(value,maximum=0xffffffff,minimum=0):
        need(re.fullmatch('0|-?[1-9][0-9]*'if minimum<0 else'0|[1-9][0-9]*',value),'canonical captured integer');n=int(value);need(minimum<=n<=maximum,'bounded captured integer');return n
    def status(value):return integer(value,2147483647,-2147483648)
    take('BEGIN',dict(cases=len(rows),coordinator=0,worker=1,data=data_sha256,component=component_sha256));take('WORKER',dict(core=1,priority=3,stack=16384));take('CONTROLS',dict(checks=CONTROL_COUNT,core=1))
    f=take('VERSION',dict(core=1),('hex',));need(re.fullmatch('(?:[0-9a-f]{2}){1,256}',f['hex']),'actual public library version bytes');version=bytes.fromhex(f['hex']).decode('ascii');need(version=='Xiph.Org libVorbis 1.3.7','actual upstream version')
    for i,row in enumerate(rows):
        take('CASE',dict(case=i,id=row['id'],packets=14,core=1));header_statuses=[]
        for h in range(3):header_statuses.append(status(take('HEADER',dict(case=i,header=h,guards=1,unchanged=1,core=1),('status',))['status']))
        f=take('INIT',dict(case=i,core=1),('synthesis_status','block_status'));si,bi=status(f['synthesis_status']),status(f['block_status']);info=None
        if si==0:
            keys=('rate','channels','short_block','long_block');f=take('INFO',dict(case=i,core=1),keys);info={k:integer(f[k])for k in keys};need(1<=info['channels']<=255 and info['rate']>0,'usable actual public stream metadata')
        packets,fragments,total_frames,total_samples=[],[],0,0
        for p in range(14):
            take('PACKET_BEGIN',dict(case=i,packet=p,granule=row['granules'][p],eos=int(p==13),core=1));packet_parts=[];packet_frames=0
            while cursor<len(events)and events[cursor].startswith('XIPH_PCM '):
                f=take('PCM',dict(case=i,packet=p,start=total_samples,guards=1,core=1),('frames','samples','hex'));frames=integer(f['frames'],256);samples=integer(f['samples'],256)
                need(info is not None and frames>0 and samples==frames*info['channels']and re.fullmatch('[0-9a-f]{'+str(4*samples)+'}',f['hex']),'complete aligned finite PCM byte chunk')
                packet_frames+=frames;total_frames+=frames;total_samples+=samples;need(total_samples<=8388608,'bounded finite capture');packet_parts.append(f['hex']);fragments.append(f['hex'])
            f=take('PACKET_END',dict(case=i,packet=p,frames=packet_frames,guards=1,unchanged=1,core=1),('synthesis_status','blockin_status','read_status'));ss,bs,rs=status(f['synthesis_status']),status(f['blockin_status']),status(f['read_status'])
            need(not packet_frames or ss==bs==rs==0,'PCM follows successful synthesis/blockin/read')
            packets.append(dict(packet=p,granule=row['granules'][p],eos=p==13,synthesis_status=ss,blockin_status=bs,read_status=rs,frames=packet_frames,pcm_hex=''.join(packet_parts)))
        resources=('free_before','free_open','free_after','minimum_free','largest_before','largest_after','stack_before','stack_after');f=take('CASE_END',dict(case=i,frames=total_frames,pcm_bytes=2*total_samples,guards=1,unchanged=1,core=1),('api_ok',*resources));api_ok=bool(integer(f['api_ok'],1));observations={k:integer(f[k])for k in resources}
        expected_ok=all(x==0 for x in header_statuses)and si==bi==0 and all(p['synthesis_status']==p['blockin_status']==0 for p in packets);need(api_ok==expected_ok,'actual API summary matches all captured returns')
        need(observations['stack_after']<=observations['stack_before']<=16384 and observations['minimum_free']<=observations['free_after']and observations['largest_before']<=observations['free_before']and observations['largest_after']<=observations['free_after'],'coherent cumulative runtime observations')
        captured.append(dict(case=i,id=row['id'],header_statuses=header_statuses,synthesis_init_status=si,block_init_status=bi,info=info,packets=packets,pcm_hex=''.join(fragments),frames=total_frames,pcm_bytes=2*total_samples,api_ok=api_ok,guards=1,unchanged=1,resources=observations,core=1))
    take('COMPLETE',dict(cases=len(rows),controls=CONTROL_COUNT,core=1));take('STOP',dict(status='CAPTURED'));need(cursor==len(events),'no extra/trailing capture event')
    return dict(cases=len(rows),packets=sum(len(r['packets'])for r in captured),pcm_bytes=sum(r['pcm_bytes']for r in captured),protocol_lines=len(events),conversion_controls=CONTROL_COUNT,coordinator_core=0,worker_core=1,priority=3,configured_stack=16384,library_version=version,rows=captured)

def validate_port_manifest(document,base_sha256):
    need(document['schema']=='native-vorbis-xiph-resource-port-v1'and document['base_manifest_sha256']==base_sha256 and isinstance(document['files'],dict),'matching resource-port manifest')
    for name,digest in document['files'].items():
        path=PurePosixPath(name);need(name==path.as_posix()and path.parts and not path.is_absolute()and '..'not in path.parts and ':'not in name and '\\'not in name and name!='port-manifest.json'and re.fullmatch('[0-9a-f]{64}',digest),'exact relative resource-port identity')
    need({'CMakeLists.txt','prepare.py','edits.json'}|{'include/'+name for name in PRIVATE_HEADERS}<=document['files'].keys(),'complete port generator/edit inputs');return document

def validate_resource_log(log,rows,base_sha256,port_sha256,book_checks=BOOK_CHECKS,bit_checks=BIT_CHECKS,residue_checks=RESIDUE_CHECKS,header_checks=HEADER_CHECKS,dsp_checks=DSP_CHECKS):
    need(book_checks>0 and bit_checks>0 and residue_checks>0 and header_checks>0 and dsp_checks>0,'declared measured resource-test counts')
    lines=log.splitlines();need(not any('PORT_RESOURCE'in line and not line.startswith('PORT_RESOURCE ')for line in lines),'foreign/torn resource record')
    events=[(i,line)for i,line in enumerate(lines)if line.startswith('PORT_RESOURCE ')];need(len(events)==len(rows)+13,'all ordered resource/cleanup records')
    def marker(prefix):
        found=[i for i,line in enumerate(lines)if line.startswith(prefix)];need(len(found)==1,'unique public event boundary');return found[0]
    def take(index,expected):
        tokens=events[index][1].split(' ');need(tokens[0]=='PORT_RESOURCE'and all(t.count('=')==1 for t in tokens[1:]),'resource record syntax');fields=dict(t.split('=')for t in tokens[1:])
        wanted=dict(expected,live=0,bytes=0,core=1);need(len(fields)+1==len(tokens)and set(fields)==set(wanted)and all(fields[k]==str(v)for k,v in wanted.items()),'exact resource record/count/cleanup identity')
    phases=[dict(phase='arena_before',base=base_sha256,port=port_sha256),dict(phase='arena_after',checks=11),dict(phase='books_before'),dict(phase='books_after',checks=book_checks),dict(phase='bits_before'),dict(phase='bits_after',checks=bit_checks),dict(phase='residue_before'),dict(phase='residue_after',checks=residue_checks),dict(phase='headers_before'),dict(phase='headers_after',checks=header_checks),dict(phase='dsp_before'),dict(phase='dsp_after',checks=dsp_checks)]
    worker,controls=marker('XIPH_WORKER '),marker('XIPH_CONTROLS ')
    for i,expected in enumerate(phases):take(i,expected);need(worker<events[i][0]<controls,'resource tests precede original31 conversion controls')
    for i,row in enumerate(rows):
        take(i+12,dict(phase='case',case=i));start=marker('XIPH_CASE_END case='+str(i)+' ');end=marker('XIPH_CASE case='+str(i+1)+' ')if i+1<len(rows)else marker('XIPH_COMPLETE ')
        need(start<events[i+12][0]<end,'zero live allocation check follows each public close')
    take(len(rows)+12,dict(phase='complete'));need(events[-2][0]<events[-1][0]<marker('XIPH_COMPLETE '),'final cleanup precedes public completion')
    return dict(arena_checks=11,book_checks=book_checks,bit_checks=bit_checks,residue_checks=residue_checks,header_checks=header_checks,dsp_checks=dsp_checks,records=len(events),per_case_zero_live=len(rows),final_live=0,final_bytes=0,core=1)

def validate_generated(path,base,port,base_root,port_root,base_sha256,port_sha256):
    raw=path.read_bytes();record=json.loads(raw);original={name:(base_root/name).read_bytes()for name in (*base['files'],'component-manifest.json')};changes=json.loads((port_root/'edits.json').read_bytes())
    need(changes['schema']=='native-vorbis-xiph-exact-edits-v1'and len(changes['edits'])==23,'twenty-three explicit exact-fragment changes');modified,applied={},[]
    for change in changes['edits']:
        source,before_name,after_name=(change[k]for k in ('source','before','after'));need(source in base['compile_sources']and before_name in port['files']and after_name in port['files'],'declared compiled source/edit fragments')
        before,after=(port_root/before_name).read_bytes(),(port_root/after_name).read_bytes();body=modified.get(source,original[source]);need(before and after and before!=after and body.count(before)==1,'one exact original fragment');modified[source]=body.replace(before,after,1)
        applied.append(dict(source=source,before=before_name,after=after_name,before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest()))
    need(set(modified)==PORTED_UNITS,'only ten declared translation units differ')
    generated={'base/'+name:body for name,body in original.items()};generated.update({'ported/'+PurePosixPath(name).name:body for name,body in modified.items()})
    for name in PRIVATE_HEADERS:
        private_name='include/'+name;private_body=(port_root/private_name).read_bytes()
        need(hashlib.sha256(private_body).hexdigest()==port['files'].get(private_name),'declared private header identity')
        generated['ported/'+name]=private_body
    units=[dict(original=name,compiled='ported/'+PurePosixPath(name).name if name in modified else'base/'+name)for name in base['compile_sources']]
    wanted=dict(schema='native-vorbis-xiph-generated-port-v1',base_manifest_sha256=base_sha256,port_manifest_sha256=port_sha256,edits=applied,compiled_units=units,files={name:hashlib.sha256(body).hexdigest()for name,body in sorted(generated.items())})
    need(record==wanted and raw==(json.dumps(wanted,indent=2,sort_keys=True)+'\n').encode(),'actual PORTING.json matches independently replayed exact edits')
    paths=list(path.parent.rglob('*'));need(not any(p.is_symlink()for p in paths)and {p.relative_to(path.parent).as_posix()for p in paths if p.is_file()}==set(generated)|{'PORTING.json'},'complete regular generated source inventory')
    need(all((path.parent/name).read_bytes()==body for name,body in generated.items()),'every actual generated source byte matches the declared transformation');return record


def validate_compile_sources(database,fixture_sources,porting,generated_root):
    need(len(fixture_sources)==8 and len({name for name,_ in fixture_sources})==8,'all eight distinct fixture translation units')
    need(len(porting['compiled_units'])==22 and sum(unit['compiled'].startswith('ported/')for unit in porting['compiled_units'])==10,'all twenty-two library units including ten declared ports')
    expected=fixture_sources+[(unit['original'],generated_root/unit['compiled'])for unit in porting['compiled_units']]
    need(len({name for name,_ in expected})==30 and len({path for _,path in expected})==30,'all thirty distinct selected source rows')
    selected={}
    for name,source in expected:
        found=[row for row in database if Path(row['file']).resolve()==source]
        need(len(found)==1,'exact native compile row '+name);selected[name]=found[0]
    return selected

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--target',choices=SDK_HEAD,required=True)
    for name in ('output','cases','idf','idf-tools','powershell','sdk-python','qemu','rom'):parser.add_argument('--'+name,type=Path,required=True)
    pins=('base-manifest','port-manifest','cases','cases-header','qemu')
    for name in pins:parser.add_argument('--'+name+'-sha256',required=True)
    a=parser.parse_args();need(sys.platform=='win32','pinned Windows SDK launcher');pin={name:getattr(a,name.replace('-','_')+'_sha256')for name in pins}
    need(all(re.fullmatch('[0-9a-f]{64}',x)for x in pin.values()),'explicit lowercase reviewed hashes')
    out,cases,sdk,tools,ps,py,qemu,rom=[getattr(a,name).resolve()for name in ('output','cases','idf','idf_tools','powershell','sdk_python','qemu','rom')]
    git=Path(shutil.which('git.exe')or shutil.which('git')or'');manifest=validate_manifest(json.loads(MANIFEST.read_bytes()))
    need(sha(MANIFEST)==pin['base-manifest'],'reviewed complete unchanged base manifest')
    inventory={p.relative_to(COMPONENT).as_posix()for p in COMPONENT.rglob('*')if p.is_file()and p!=MANIFEST};need(inventory==set(manifest['files']),'exact complete source/config/license inventory')
    need(all(sha(COMPONENT/name)==digest for name,digest in manifest['files'].items()),'every component file matches reviewed manifest')
    need(sha(PORT_MANIFEST)==pin['port-manifest'],'reviewed resource-port manifest');port=validate_port_manifest(json.loads(PORT_MANIFEST.read_bytes()),pin['base-manifest'])
    port_paths=list(PORT.rglob('*'));need(not any(p.is_symlink()for p in port_paths)and {p.relative_to(PORT).as_posix()for p in port_paths if p.is_file()}==set(port['files'])|{'port-manifest.json'},'exact complete port source inventory')
    need(all(sha(PORT/name)==digest for name,digest in port['files'].items()),'every exact fragment/generator/build input matches its manifest')
    need(sha(BASE_READER)==BASE_READER_SHA256,'pinned original31 reader provenance')
    old=ast.parse(BASE_READER.read_text());new=ast.parse(Path(__file__).read_text());pure=('need','sha','normalize','sequence','validate_manifest','validate_cases','validate_log')
    for name in pure:
        definitions=[[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name]for tree in (old,new)]
        need(all(len(d)==1 for d in definitions)and ast.dump(definitions[0][0],include_attributes=False)==ast.dump(definitions[1][0],include_attributes=False),'unchanged original reader definition '+name)
    need(BOOK_CHECKS>0 and BIT_CHECKS>0 and RESIDUE_CHECKS>0 and HEADER_CHECKS>0 and DSP_CHECKS>0,'fixed measured resource-test counts')
    required=[*[COMPONENT/name for name in manifest['files']],*[PORT/name for name in port['files']],*[ROOT/'tests/native'/name for name in HELPERS],MANIFEST,PORT_MANIFEST,BASE_READER,cases/'cases.json',cases/'cases.h',sdk/'export.ps1',sdk/'tools/idf.py',ps,py,qemu,git]
    need(all(p.is_file()for p in required)and rom.is_dir()and any(rom.glob('esp32*rom*.bin')),'required sources/tools/explicit ROM')
    need(out.is_relative_to(ROOT/'.build')and out!=ROOT/'.build'and not out.exists(),'fresh task-local output')
    need(not any(out==p or out.is_relative_to(p)or p.is_relative_to(out)for p in (COMPONENT,PORT,PROJECT,ROOT/'tests/native',cases,sdk,tools,ps.parent,py.parent,qemu.parent,rom)),'source/runtime/output separation')
    for path,key in ((cases/'cases.json','cases'),(cases/'cases.h','cases-header'),(qemu,'qemu')):need(sha(path)==pin[key],'reviewed data/tool '+str(path))
    rows=validate_cases(json.loads((cases/'cases.json').read_bytes()),(cases/'cases.h').read_text(encoding='ascii'));out.mkdir(parents=True)
    report=dict(completed=False,capture_completed=False,math_capture_completed=False,passed=False,target=a.target,result='NONPASS',numerical_reference_compared=False,numerical_qualified=False,
        full_decoder_qualified=False,production_firmware=False,production_radio_integration=False,physical_device=False,whole_module_compiled=False,source_inputs_unchanged=False,
        sdk_revision=SDK_HEAD[a.target],commands=[],inputs={},tools={},build_outputs={},rows=[],source_sha256=pin,component_compile_sources=manifest['compile_sources'],
        resource_tests_completed=False,exact_source_port_validated=False,input_domain='Focused resource-port tests and unchanged original31 raw public synthesis/PCM conversion')
    env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0')
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path,relative):
        dest=out/'sources'/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes());report['inputs'][str(path.resolve())]=dict(snapshot=dest.relative_to(out).as_posix(),bytes=dest.stat().st_size,sha256=sha(dest))
    def current():
        need(all(sha(path)==value['sha256']==sha(out/value['snapshot'])for path,value in report['inputs'].items()),'original/frozen source changed')
        need(all(sha(path)==digest for path,digest in report['tools'].items()),'recorded tool changed')
        need(all(sha(out/path)==digest for path,digest in report.get('project_sources',{}).items()),'configured fixture changed')
        need(all(sha(out/path)==digest for path,digest in report.get('generated_sources',{}).items()),'actual generated exact-port source changed')
    def run(name,argv,timeout=60):
        argv=list(map(str,argv));row=dict(name=name,argv=argv,cwd=str(out),state='starting',timeout_seconds=timeout,timed_out=False,interrupted=False);report['commands'].append(row);save();so,se=out/(name+'.stdout.log'),out/(name+'.stderr.log');child,start=None,time.monotonic()
        try:
            with so.open('xb')as stdout,se.open('xb')as stderr:
                child=subprocess.Popen(argv,cwd=out,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL,env=env,creationflags=subprocess.CREATE_NO_WINDOW);row.update(pid=child.pid,state='running');save();child.wait(timeout=timeout);row.update(state='complete',exit_status=child.returncode)
        except BaseException as error:row.update(state='failed',error=repr(error),timed_out=isinstance(error,subprocess.TimeoutExpired),interrupted=isinstance(error,KeyboardInterrupt));raise
        finally:
            if child is not None and child.poll()is None:
                row['state']='forced_stop_nonpass'
                try:
                    stopped=subprocess.run(['taskkill.exe','/PID',str(child.pid),'/T','/F'],capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW);row['tree_stop_returncode']=stopped.returncode
                except Exception as error:row['tree_stop_error']=repr(error)
                finally:
                    if child.poll()is None:child.kill()
                    child.wait(timeout=15)
            row.update(elapsed_seconds=time.monotonic()-start,stdout_sha256=sha(so)if so.is_file()else None,stderr_sha256=sha(se)if se.is_file()else None)
            if child is not None:row['exit_status']=child.poll()
            save()
        need(row['state']=='complete'and row['exit_status']==0,name+' did not terminate normally/successfully');return so.read_text(encoding='utf-8',errors='replace').replace('\r\n','\n')
    save()
    try:
        for path in (py,ps,qemu,git,*sorted(rom.glob('esp32*rom*.bin'))):report['tools'][str(path)]=sha(path)
        need(run('sdk-head',[git,'-c','core.longpaths=true','-C',sdk,'rev-parse','HEAD']).strip()==SDK_HEAD[a.target],'SDK revision')
        need(not run('sdk-clean',[git,'-c','core.longpaths=true','-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'SDK clean')
        for name in (*manifest['files'],'component-manifest.json'):freeze(COMPONENT/name,Path('components/native_vorbis_xiph')/name)
        for name in (*port['files'],'port-manifest.json'):freeze(PORT/name,Path('components/native_vorbis_xiph_port')/name)
        freeze(BASE_READER,Path('baseline-controller.py'))
        for name in HELPERS:freeze(ROOT/'tests/native'/name,Path('helpers')/name)
        freeze(Path(__file__),Path('controller.py'))
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file():freeze(path,Path('project')/path.relative_to(PROJECT))
        for name in ('cases.json','cases.h'):freeze(cases/name,Path('cases')/name)
        shutil.copytree(out/'sources/project',out/'project');shutil.copyfile(out/'sources/cases/cases.h',out/'project/main/cases.h');shutil.copyfile(out/'sources/project/sdkconfig.esp32.defaults',out/'project/sdkconfig.defaults')
        for name in HELPERS:shutil.copyfile(out/'sources/helpers'/name,out/'project/main'/name)
        report['project_sources']={p.relative_to(out).as_posix():sha(p)for p in (out/'project').rglob('*')if p.is_file()};current()
        run('build',[ps,'-NoProfile','-NonInteractive','-File',out/'sources/project/sdk-build.ps1','-Campaign',out,'-SdkDirectory',sdk,'-ToolsDirectory',tools,'-PythonExecutable',py,'-Target',a.target,'-BaseManifestSha256',pin['base-manifest'],'-PortManifestSha256',pin['port-manifest'],'-CasesSha256',pin['cases']],1200)
        child=json.loads((out/'sdk-child.json').read_text(encoding='utf-8-sig'));need(type(child['pid'])is int and child['pid']>0 and child['exit_status']==0,'actual SDK child terminal');report['sdk_child']=child
        build=out/'build';description=json.loads((build/'project_description.json').read_bytes());elf=build/description['app_elf'];elf_bytes=elf.read_bytes()
        need(elf.resolve().is_relative_to(build)and struct.unpack_from('<H',elf_bytes,18)[0]==94,'native Xtensa ELF machine');report['elf_machine']=94;(out/'elf-header.bin').write_bytes(elf_bytes[:52])
        porting_paths=list(build.rglob('PORTING.json'));need(len(porting_paths)==1,'one actual generated-port record');porting_path=porting_paths[0]
        porting=validate_generated(porting_path,manifest,port,out/'sources/components/native_vorbis_xiph',out/'sources/components/native_vorbis_xiph_port',pin['base-manifest'],pin['port-manifest']);generated_root=porting_path.parent
        generated_paths=[generated_root/name for name in porting['files']]+[porting_path];report['generated_sources']={p.relative_to(out).as_posix():sha(p)for p in generated_paths}
        report['generated_porting']=dict(path=porting_path.relative_to(out).as_posix(),sha256=sha(porting_path),record=porting);report['exact_source_port_validated']=True;current()
        compiler=Path(description['c_compiler']);nm=compiler.with_name(compiler.name.replace('gcc','nm'));make=re.findall(r'^CMAKE_MAKE_PROGRAM:FILEPATH=(.+)$',(build/'CMakeCache.txt').read_text(encoding='utf-8'),re.M);need(len(make)==1,'one configured Ninja');ninja=Path(make[0].strip())
        for path in (compiler,nm,ninja):need(path.is_file(),'actual configured tool');report['tools'][str(path)]=sha(path)
        database=json.loads((build/'compile_commands.json').read_bytes());units=manifest['compile_sources']
        fixture_sources=[('fixture',out/'project/main/main.c')]+[(name,out/'project/main'/name)for name in HELPERS if name.endswith('.c')]
        selected=validate_compile_sources(database,fixture_sources,porting,generated_root)
        report['compile_rows']=selected
        need(all(all(flag in selected[name]['command']for flag in ('-fno-fast-math','-ffp-contract=off','-fstack-usage'))for name in selected),'actual unchanged arithmetic/stack compiler flags')
        inject=normalize(out/'project/main/vorbis_xiph_alloc_inject.h').casefold()
        need(all('-include' in selected[name]['command']and inject in normalize(selected[name]['command']).casefold()for name in units),'actual allocator injection on all22 library units')
        need(all(inject not in normalize(selected[name]['command']).casefold()for name,_ in fixture_sources),'allocator hooks do not rewrite their own implementation/caller')
        objects=[normalize(row['output'])for row in selected.values()];need(all((build/p).is_file()for p in objects),'actual compiled objects')
        dependencies=normalize(run('dependencies',[ninja,'-C',build,'-t','deps',*objects])).casefold()
        for unit in porting['compiled_units']:need(normalize(generated_root/unit['compiled']).casefold()in dependencies,'actual original/ported compile dependency')
        for name in ('upstream/libvorbis/include/vorbis/codec.h','upstream/libogg/include/ogg/ogg.h','platform/ogg/config_types.h'):
            need(normalize(generated_root/'base'/name).casefold()in dependencies,'actual unchanged public/platform header dependency')
        for name in PRIVATE_HEADERS:need(normalize(generated_root/'ported'/name).casefold()in dependencies,'actual explicit checked interface dependency')
        for name in HELPERS:need(normalize(out/'project/main'/name).casefold()in dependencies,'actual frozen test/helper dependency')
        need(normalize(out/'project/main/cases.h').casefold()in dependencies,'actual original31 data dependency');report['whole_module_compiled']=True
        symbols=run('symbols',[nm,'-n','-S',elf]);need(all(re.search(r'\b'+name+r'$',symbols,re.M)for name in PUBLIC),'public Xiph synthesis symbols')
        need(all(re.search(r'\b'+name+r'$',symbols,re.M)for name in ('xiph_arena_tests','xiph_book_tests','xiph_bitreader_tests','xiph_residue_tests','xiph_header_tests','xiph_dsp_tests','xiph_port_test_malloc','xiph_port_test_calloc','xiph_port_test_realloc','xiph_port_test_free')),'actual focused resource tests/allocator symbols')
        need(not re.search(r'\b__wrap_(?:vorbis|ogg)\w*$',symbols,re.M),'no private library wrappers')
        need(not re.search(r'\b(?:__wrap_)?esp_vorbis_dec_\w+$',symbols,re.M),'no Espressif decoder/private wrapper symbols');map_file=elf.with_suffix('.map');need(map_file.is_file()and b'libesp_audio_codec.a'not in map_file.read_bytes(),'no vendor audio archive')
        need(b'libnative_vorbis_xiph.a'not in map_file.read_bytes(),'the unchanged sibling is a source input, not a second linked decoder')
        usage=[build/Path(selected[name]['output']).with_suffix('.su')for name in units];need(len(set(usage))==22 and all(p.is_file()for p in usage),'all22 declared library compiler stack-usage files');frames=[]
        for path in usage:
            for line in path.read_text(encoding='utf-8').splitlines():
                fields=line.rsplit('\t',2);need(len(fields)==3 and fields[1].isdigit(),'actual compiler stack row');frames.append(dict(function=fields[0].rsplit(':',1)[-1],bytes=int(fields[1]),qualifier=fields[2],path=path.relative_to(out).as_posix()))
        report['stack_usage']=dict(paths=[p.relative_to(out).as_posix()for p in usage],rows=frames,scope='Compiler per-function frames only; measured task high-water is separate. No physical timing or full dynamic call-tree bound.')
        recipe=json.loads((build/'flasher_args.json').read_bytes());need(recipe['flash_settings']==dict(flash_mode='dio',flash_size='4MB',flash_freq='40m'),'isolated flash profile');flash_files={int(offset,0):(build/name).resolve()for offset,name in recipe['flash_files'].items()}
        need(set(flash_files)=={4096,32768,65536}and all(p.is_relative_to(build)for p in flash_files.values()),'isolated native boot/image recipe');flash=out/'qemu-flash.bin';argv=[py,'-m','esptool','--chip','esp32','merge-bin','--output',flash,'--flash-mode','dio','--flash-size','4MB','--flash-freq','40m']
        for offset,path in sorted(flash_files.items()):argv+=[hex(offset),path]
        run('merge',argv+['--pad-to-size','4MB']);config=(out/'sdkconfig').read_text(encoding='utf-8');need(not re.search(r'^CONFIG_FREERTOS_UNICORE=y$',config,re.M)and re.search(r'^CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ=240$',config,re.M),'native dual-core240MHz profile')
        qargs=[qemu,'-audiodev','none,id=quiet','-M','esp32,audiodev=quiet','-smp','2','-L',rom,'-display','none','-monitor','none','-serial','stdio','-no-reboot','-snapshot','-nic','none','-drive','file='+str(flash)+',if=mtd,format=raw'];current();log=run('qemu',qargs,600)
        full_log=log+'\n'+(out/'qemu.stderr.log').read_text(encoding='utf-8',errors='replace')
        observed=validate_log(full_log,rows,a.target,pin['cases'],pin['base-manifest']);report['rows']=observed.pop('rows');report['observed']=observed
        report['resource_observed']=validate_resource_log(full_log,rows,pin['base-manifest'],pin['port-manifest']);report['resource_tests_completed']=True
        (out/'pcm').mkdir();pcm_paths=[]
        for row in report['rows']:
            path=out/'pcm'/('%02d-'%row['case']+row['id']+'.s16le');path.write_bytes(bytes.fromhex(row['pcm_hex']));pcm_paths.append(path)
        need(run('sdk-head-after',[git,'-c','core.longpaths=true','-C',sdk,'rev-parse','HEAD']).strip()==SDK_HEAD[a.target],'SDK revision after')
        need(not run('sdk-clean-after',[git,'-c','core.longpaths=true','-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'SDK clean after')
        files=[elf,map_file,flash,*usage,*pcm_paths,*generated_paths,out/'sdkconfig',out/'elf-header.bin',out/'sdk-child.json',out/'sdk-build.stdout.log',out/'sdk-build.stderr.log',*flash_files.values()]+[build/name for name in ('compile_commands.json','project_description.json','flasher_args.json','CMakeCache.txt','config/sdkconfig.h','build.ninja','CMakeFiles/rules.ninja')]
        report['build_outputs']={p.relative_to(out).as_posix():sha(p)for p in files};report['build_warning_lines']=[line for name in ('sdk-build.stdout.log','sdk-build.stderr.log')for line in (out/name).read_text(encoding='utf-8',errors='replace').splitlines()if re.search(r'\bwarning:',line)]
        current();need(all(sha(out/path)==digest for path,digest in report['build_outputs'].items()),'selected actual build/capture bytes changed')
        report.update(completed=True,capture_completed=True,math_capture_completed=True,source_inputs_unchanged=True,result='CHECKED_XIPH_PORT_CAPTURED',limitations='Focused arena/codebook/bitreader/residue/header/DSP resource checks plus complete original31 raw capture; independent PCM comparison pending. No whole-decoder OOM or stack bound, production integration, Ogg EOF/reset extension, physical timing, or full SDK binary dependency closure. Heap minimum and task high-water are cumulative emulator observations, not per-case transient peaks.')
        save();print(json.dumps(dict(completed=True,capture_completed=True,cases=len(rows),pcm_bytes=report['observed']['pcm_bytes'],numerical_qualified=False,result=report['result'])));return 0
    except BaseException as error:report.update(completed=False,capture_completed=False,math_capture_completed=False,result='NONPASS',error=repr(error));save();raise

if __name__=='__main__':sys.exit(main())
