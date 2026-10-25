"""Replay saved resource/PCM evidence without launching a decoder or tool.

Checks all ZIP members, exact source deviations, raw native protocol and both
host/native PCM vectors. Only the pinned owned pure protocol reader is reused.
"""
import argparse,hashlib,json,struct,types,zipfile
from pathlib import Path,PurePosixPath
READER='949a3a8aa2baec7bc8d2de1f9a1df2cfa23ea7edaa47fcdae1c41466c1a51b5b'
BASE='897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14'
PORT='9103e35103d6a19fc3532a82eacc48a9c951685033cb7759f6c79a517af4a079'
MODEL='a12fcb6fea905027f9af4b1d1e5b5b561fa447f457d236cd5d004fd948b07883'
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def verify(path):
    with zipfile.ZipFile(path)as archive:
        names=archive.namelist();need(len(names)==len(set(names)),'unique archive members')
        need(all(not PurePosixPath(n).is_absolute()and '..'not in PurePosixPath(n).parts and ':'not in n and '\\'not in n for n in names),'relative member paths')
        read=archive.read;inventory=json.loads(read('manifest.json'))
        need(inventory['schema']=='vorbis-xiph-resources-checkpoint-v1'and set(names)==set(inventory['files'])|{'manifest.json'},'complete member inventory')
        for name,pin in inventory['files'].items():
            body=read(name);need(len(body)==pin['bytes']and sha(body)==pin['sha256'],'saved member '+name)
        host=json.loads(read('host/report.json'));native=json.loads(read('native/report.json'));comparison=json.loads(read('comparison/report.json'))
        need(host['completed']and host['passed']and host['sanitizers']==['address','undefined']and host['max_abs_error']==0,'complete sanitizer host result')
        need(native['completed']and native['resource_tests_completed']and native['exact_source_port_validated']and native['whole_module_compiled'],'complete native port result')
        for name in('host-retry','native','generation','protocol-retry','pcm-units','comparison','lint'):
            terminal=json.loads(read('receipts/'+name+'.json'));need(terminal['status']=='TERMINAL'and type(terminal['returncode'])is int and terminal['returncode']==0,'actual outer terminal '+name)
            for old,pin in terminal['logs'].items():need(sha(read('receipts/'+old.replace('\\','/').rsplit('/',1)[-1]))==pin['sha256'],'actual outer stream '+name)
        for command in host['commands']:
            observed=command['supervisor'];need(command['transport_exit']==0 and observed['state']=='terminal'and observed['child_returncode']==0 and observed['child_reaped']and observed['group_gone']and observed['final']and observed['nonce']==command['nonce']and observed['request_sha256']==command['request_sha256'],'owned sanitizer process/group terminal')
            for stream in('stdout','stderr'):need(sha(read('host/'+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],'actual host stream')
        need(not read('host/execute.stderr.log'),'sanitizer execution has no diagnostics')
        need(read('host/execute.stdout.log').decode().splitlines()==[
            'RESOURCE_CHECKS arena=11 books=200864 bits=124754 live=0',
            'RESOURCE_PASS arena=11 books=200864 cases=31 packets=434 pcm_bytes=738560 live=0'],
            'actual complete host resource markers')
        need(sha(read('host/resource-tests'))==host['binary_sha256'],'saved actual sanitizer executable')
        for command in native['commands']:
            need(command['state']=='complete'and command['exit_status']==0 and not command['timed_out']and not command['interrupted'],'owned native command terminal')
            for stream in('stdout','stderr'):need(sha(read('native/'+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],'actual native stream')
        for name,digest in native['build_outputs'].items():need(sha(read('native/'+name))==digest,'actual build output '+name)
        base='native/sources/components/native_vorbis_xiph/';port='native/sources/components/native_vorbis_xiph_port/'
        need(sha(read(base+'component-manifest.json'))==BASE and sha(read(port+'port-manifest.json'))==PORT,'exact baseline and resource-port identity')
        for prefix,manifest_name in((base,'component-manifest.json'),(port,'port-manifest.json')):
            record=json.loads(read(prefix+manifest_name))
            for name,digest in record['files'].items():need(sha(read(prefix+name))==digest,'unchanged source identity '+name)
        generated=native['generated_porting'];record=generated['record'];root='native/'+generated['path'].rsplit('/',1)[0]+'/'
        need(sha(read('native/'+generated['path']))==generated['sha256'],'actual generated record')
        need(read('host/generated/PORTING.json')==read('native/'+generated['path']),
             'same host/native exact port record')
        originals=json.loads(read(base+'component-manifest.json'));expected={'base/'+name:read(base+name)for name in originals['files']};expected['base/component-manifest.json']=read(base+'component-manifest.json');modified={}
        edits=json.loads(read(port+'edits.json'))['edits'];need(len(edits)==8,'all eight reviewed source edits')
        for edit in edits:
            source=edit['source'];before,after=read(port+edit['before']),read(port+edit['after']);body=modified.get(source,read(base+source));need(body.count(before)==1,'unique exact before fragment');modified[source]=body.replace(before,after,1)
        need(set(modified)=={'upstream/libvorbis/lib/block.c','upstream/libvorbis/lib/sharedbook.c','upstream/libogg/src/bitwise.c'},'exact three ported units')
        expected.update({'ported/'+PurePosixPath(n).name:b for n,b in modified.items()})
        need(record['files']=={n:sha(b)for n,b in expected.items()}and len(expected)==119 and len(record['compiled_units'])==22,'complete generated file map')
        for name,body in expected.items():need(read(root+name)==body and read('host/generated/'+name)==body,'same exact host/native generated source')
        model=json.loads(read('native/sources/cases/cases.json'));need(sha(json.dumps(model,sort_keys=True,separators=(',',':')).encode())==MODEL,'unchanged original31 model')
        raw=read('sources/tests/run-vorbis-xiph-port-qemu.py');need(sha(raw)==READER,'pinned owned pure protocol reader');module=types.ModuleType('saved_xiph_resource_protocol');module.__file__=str(Path(__file__).resolve().parent/'run-vorbis-xiph-port-qemu.py');exec(compile(raw,module.__file__,'exec'),module.__dict__)
        cases=module.validate_cases(model,read('native/sources/cases/cases.h').decode('ascii'));log=read('native/qemu.stdout.log').decode('utf-8',errors='replace')+'\n'+read('native/qemu.stderr.log').decode('utf-8',errors='replace');replayed=module.validate_log(log,cases,'esp32',native['source_sha256']['cases'],BASE);rows=replayed.pop('rows');need(rows==native['rows']and replayed==native['observed'],'whole original31 native protocol')
        resources=module.validate_resource_log(log,cases,BASE,PORT);need(resources==native['resource_observed']and resources['arena_checks']==11 and resources['book_checks']==200864 and resources['bit_checks']==124754 and resources['final_live']==resources['final_bytes']==0,'all38 resource and per-case cleanup records')
        data=read('host/pcm.bin');need(sha(data)==host['capture_sha256']and data[:8]==b'XIPHRES1','actual host binary PCM');at=8
        def u32():
            nonlocal at
            need(at+4<=len(data),'whole host capture field');value=struct.unpack_from('<I',data,at)[0];at+=4;return value
        need(u32()==31,'all31 host cases');tables={'host':{},'native':{},'reference':{}};total=packets=maximum=0
        for index,(case,row)in enumerate(zip(cases,rows)):
            need([u32()for _ in range(4)]==[index,case['rate'],case['channels'],14],'whole host case metadata');parts=[]
            for p,frames in enumerate(case['frames']):
                need([u32()for _ in range(3)]==[p,frames,frames*4],'whole host packet metadata');body=data[at:at+frames*4];at+=frames*4;need(len(body)==frames*4,'whole host packet PCM');parts.append(body);packets+=1
            host_pcm=b''.join(parts);native_pcm=bytes.fromhex(row['pcm_hex']);reference=read('host/sources/cases/'+case['reference_path']);need(sha(reference)==case['reference_pcm_sha256'],'same qualified reference')
            need(len(host_pcm)==len(native_pcm)==len(reference)==case['pcm_bytes'],'full zero-lag untrimmed sample lengths')
            values=lambda b:struct.unpack('<'+'h'*(len(b)//2),b)
            for name,body in(('host',host_pcm),('native',native_pcm)):
                error=max((abs(a-b)for a,b in zip(values(body),values(reference))),default=0);maximum=max(maximum,error);need(error<=2,'unchanged fixed2-S16 bound');tables[name][case['id']]=body
            need(native_pcm==read('native/pcm/'+f"{index:02d}-{case['id']}.s16le"),'saved native PCM equality');tables['reference'][case['id']]=reference;total+=len(reference)
        need(at==len(data)and packets==434 and total==738560 and len(rows)==31,'complete original31 measurement')
        for table in tables.values():
            for relation in model['relations']:
                ids=relation['cases'];equal=all(table[n]==table[ids[0]]for n in ids[1:]);need(equal==(relation['kind']=='equal'),'all14 exact original PCM relations')
        need(comparison['completed']and comparison['passed']and comparison['comparison']['passed']and maximum==0,'separate numerical result and independent exact PCM')
        return dict(verified=True,arena=11,books=200864,bits=124754,cases=31,packets=434,pcm_bytes=total,max_abs_error=maximum,physical_device=False,general_OOM_qualified=False,general_16KiB_stack_bound=False)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive',type=Path);args=parser.parse_args();print(json.dumps(verify(args.archive)))
if __name__=='__main__':main()
