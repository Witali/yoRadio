"""Replay saved resource/PCM evidence without launching a decoder or tool.

Checks all ZIP members, exact source deviations, raw native protocol and both
host/native PCM vectors. Also binds the original-info regression witness
to the same fixture and object-link recipe. Only the pinned owned pure protocol
reader is reused. No decoder, compiler, SDK or subprocess is launched.
"""
import argparse,hashlib,json,re,struct,types,zipfile
from pathlib import Path,PurePosixPath
READER='82f88446f00fe4e56b3116831f50f56f5b5bc05866bf2a9d04c9d6c8cba02848'
BASE='897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14'
PORT='a5e00f16d4584cd16d5da327e552163002dfbc494a4b47ca309738c9201ae894'
MODEL='a12fcb6fea905027f9af4b1d1e5b5b561fa447f457d236cd5d004fd948b07883'
GENERATOR='8a67802770fe4bc6cbe0f85514041ee811596466f28a65cd12e28f5cbc3c03d4'
RESIDUE_FIXTURE='2d6455dc5e0d0eae33f6ee0cebc7cdf7162664bb316927ae7707bf30175ae45f'
HEADER_FIXTURE='0681da33fb618d91dd22bcb7e809523d0d830f6184659c77e38d9a387cffa03e'
FIRST_PORT='0e6cf11d40aa044156ef903be7dbb9b66e742c7ce294227396461856d43f5509'
PRIVATE_HEADER='native_vorbis_xiph_header_error.h'
PORTED_UNITS={'upstream/libvorbis/lib/'+name+'.c'for name in('block','sharedbook','codebook','floor0','floor1','res0','mapping0','info')}|{'upstream/libogg/src/bitwise.c'}
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()

def owned_command(read,prefix,command,argv,returncode):
    name=command['name'];observed=command['supervisor'];request_raw=read(prefix+name+'.request.json');request=json.loads(request_raw)
    need(command['transport_exit']==0 and not command.get('forced_stop')and not command.get('forced_transport_stop'),'owned command transport terminal '+prefix+name)
    need(observed==json.loads(read(prefix+name+'.receipt.json'))and observed['state']=='terminal'and observed['child_returncode']==returncode and observed['child_reaped']and observed['group_gone']and observed['new_session']and observed['final'],'actual owned child/group terminal '+prefix+name)
    need(type(observed['child_pid'])is int and observed['child_pid']>0 and observed['child_pid']==observed['owned_pgid'],'owned child is session/process-group leader')
    need(sha(request_raw)==observed['request_sha256']==command['request_sha256']and observed['nonce']==command['nonce']==request['nonce']and request['argv']==argv and request['timeout']==60,'nonce-bound actual command request '+prefix+name)
    for stream in('stdout','stderr'):need(sha(read(prefix+name+'.'+stream+'.log'))==command[stream+'_sha256'],'actual owned command stream '+prefix+name)

def baseline_witness(read,names,host,original_info):
    baseline=json.loads(read('baseline/report.json'))
    need(baseline['completed']is True and baseline['expected_regression']is True and sha(read('host/report.json'))==baseline['host_report_sha256'],'baseline bound to actual successful host report')
    need(read('baseline/info.c')==original_info and sha(original_info)==baseline['source_sha256'],'baseline uses the unchanged pinned Xiph info unit')
    fixture=read('host/sources/native/vorbis_xiph_headers.c');need(sha(fixture)==HEADER_FIXTURE,'same executed header failure fixture')
    need(original_info.decode().splitlines()[44].strip()=='*buf++=oggpack_read(o,8);','original sanitizer source location is its unchecked output store')
    need(fixture.decode().splitlines()[115].strip()=='xiph_port_test_reset(ordinal);int status=stream_open(stream,&info,&comment);','actual fixture arms an allocation refusal before the failing public header call')
    error=read('baseline/execute.stderr.log').decode()
    need(re.search(r'/info\.c:45:11: runtime error: store to null pointer of type \'char\'',error)is not None and all(name in error for name in('_v_readstring','_vorbis_unpack_comment','vorbis_synthesis_headerin','header_sweep','xiph_header_tests')),'actual UBSan header-allocation regression with the expected caller chain')
    need(not read('baseline/execute.stdout.log')and 'baseline/unexpected-pcm.bin'not in names,'original witness stopped before publishing PCM')
    commands=baseline['commands'];need([row['name']for row in commands]==['compile','link','execute'],'three actual baseline commands')
    for index,command in enumerate(commands):owned_command(read,'baseline/',command,command['argv'],0 if index<2 else 1)
    successful={row['name']:row['child_argv']for row in host['commands']}
    expected_compile=list(successful['compile-library-10']);compile_argv=commands[0]['argv']
    source_index,object_index=expected_compile.index('-c')+1,expected_compile.index('-o')+1
    need(expected_compile[source_index].endswith('/generated/ported/info.c')and expected_compile[object_index].endswith('/objects/library-10.o'),'actual repaired info compile slot')
    baseline_source=compile_argv[source_index];need(baseline_source.endswith('/info.c'),'actual baseline info source operand');directory=baseline_source.rsplit('/',1)[0]
    expected_compile[source_index]=directory+'/info.c';expected_compile[object_index]=directory+'/info.o'
    need(compile_argv==expected_compile,'only original info source/object replaces the successful host compile recipe')
    expected_link=[directory+'/info.o'if item==successful['compile-library-10'][object_index]else item for item in successful['link']]
    expected_link[expected_link.index('-o')+1]=directory+'/baseline-tests'
    need(commands[1]['argv']==expected_link and expected_link.count(directory+'/info.o')==1,'same actual host fixtures and other objects in baseline link')
    execute_argv=commands[2]['argv'];need(len(execute_argv)==5 and execute_argv[:2]==['python3','-c']and execute_argv[3:]==[directory+'/baseline-tests',directory+'/unexpected-pcm.bin'],'actual baseline executable and output operands')
    need('resource.setrlimit(resource.RLIMIT_CORE,(0,0))'in execute_argv[2]and 'os.execve(sys.argv[1],sys.argv[1:]'in execute_argv[2]and 'UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1"'in execute_argv[2],'sanitizer witness exec preserves owned PID and disables core files')
    need(read('baseline/info.o')!=read('host/objects/library-10.o')and read('baseline/baseline-tests')!=read('host/resource-tests')and sha(read('baseline/baseline-tests'))==baseline['binary_sha256'],'separate captured original source object and executable')
    need(read('baseline/supervisor.py')==read('host/supervisor.py'),'same owned process supervisor')
    outer=json.loads(read('receipts/baseline.json'));need(outer['status']=='TERMINAL'and outer['returncode']==0,'actual successful outer baseline witness')
    for old,pin in outer['logs'].items():need(sha(read('receipts/'+old.replace('\\','/').rsplit('/',1)[-1]))==pin['sha256'],'actual original outer witness stream')
    need(not read('receipts/baseline.stderr.log'),'baseline witness collector completed without diagnostics')

def first_marker_rejection(read,port,original_info):
    manifest_raw=read('marker-first/port-manifest.json');manifest=json.loads(manifest_raw)
    need(sha(manifest_raw)==FIRST_PORT,'retained first materializer input manifest')
    for name in('info-comments.before.c','info-books.before.c'):
        old=read('marker-first/'+name);fixed=read(port+'edits/'+name)
        need(sha(old)==manifest['files']['edits/'+name]and fixed.endswith(b'\n')and old==fixed[:-1]+b'\r\n','first marker differs only at its final line terminator')
        need(original_info.count(old)==0 and original_info.count(fixed)==1,'first exact marker rejects and corrected marker matches uniquely')

def verify(path):
    with zipfile.ZipFile(path)as archive:
        names=archive.namelist();need(len(names)==len(set(names)),'unique archive members')
        need(all(not PurePosixPath(n).is_absolute()and '..'not in PurePosixPath(n).parts and ':'not in n and '\\'not in n for n in names),'relative member paths')
        read=archive.read;inventory=json.loads(read('manifest.json'))
        need(inventory['schema']=='vorbis-xiph-headers-checkpoint-v1'and set(names)==set(inventory['files'])|{'manifest.json'},'complete member inventory')
        for name,pin in inventory['files'].items():
            body=read(name);need(len(body)==pin['bytes']and sha(body)==pin['sha256'],'saved member '+name)
        host=json.loads(read('host/report.json'));native=json.loads(read('native/report.json'));comparison=json.loads(read('comparison/report.json'))
        need(host['completed']and host['passed']and host['sanitizers']==['address','undefined']and host['max_abs_error']==0,'complete sanitizer host result')
        need(host['header_scenarios']==1598 and host['residue_scenarios']==3997 and host['arena_scenarios']==11 and host['book_assertions']==200864 and host['bitreader_assertions']==124754,'all focused host resource counts')
        need([row['name']for row in host['commands']]==['compiler-version','compiler-machine']+['compile-library-'+str(i).zfill(2)for i in range(22)]+['compile-fixture-'+name for name in('alloc','arena','books','bits','residue','headers','host')]+['link','execute'],'all thirty-three actual host commands')
        need(native['completed']and native['resource_tests_completed']and native['exact_source_port_validated']and native['whole_module_compiled'],'complete native port result')
        for name in('host','native','generation','protocol','pcm-units','comparison','lint','baseline'):
            terminal=json.loads(read('receipts/'+name+'.json'));need(terminal['status']=='TERMINAL'and type(terminal['returncode'])is int and terminal['returncode']==0,'actual outer terminal '+name)
            for old,pin in terminal['logs'].items():need(sha(read('receipts/'+old.replace('\\','/').rsplit('/',1)[-1]))==pin['sha256'],'actual outer stream '+name)
        for command in host['commands']:
            owned_command(read,'host/',command,command['child_argv'],0)
            observed=command['supervisor'];need(command['transport_exit']==0 and observed['state']=='terminal'and observed['child_returncode']==0 and observed['child_reaped']and observed['group_gone']and observed['final']and observed['nonce']==command['nonce']and observed['request_sha256']==command['request_sha256'],'owned sanitizer process/group terminal')
            for stream in('stdout','stderr'):need(sha(read('host/'+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],'actual host stream')
        need(not read('host/execute.stderr.log'),'sanitizer execution has no diagnostics')
        need(read('host/execute.stdout.log').decode().splitlines()==[
            'RESOURCE_CHECKS arena=11 books=200864 bits=124754 residue=3997 headers=1598 live=0',
            'RESOURCE_PASS arena=11 books=200864 cases=31 packets=434 pcm_bytes=738560 live=0'],
            'actual complete host resource markers')
        need(sha(read('host/resource-tests'))==host['binary_sha256'],'saved actual sanitizer executable')
        need([row['name']for row in native['commands']]==['sdk-head','sdk-clean','build','dependencies','symbols','merge','qemu','sdk-head-after','sdk-clean-after'],'nine actual owned SDK/QEMU commands')
        for command in native['commands']:
            need(command['state']=='complete'and command['exit_status']==0 and not command['timed_out']and not command['interrupted'],'owned native command terminal')
            for stream in('stdout','stderr'):need(sha(read('native/'+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],'actual native stream')
        for name,digest in native['build_outputs'].items():need(sha(read('native/'+name))==digest,'actual build output '+name)
        for prefix,report in(('host/',host),('native/',native)):
            for pin in report['inputs'].values():
                body=read(prefix+pin['snapshot']);need(sha(body)==pin['sha256']and('bytes'not in pin or len(body)==pin['bytes']),'all frozen input snapshots '+prefix+pin['snapshot'])
        base='native/sources/components/native_vorbis_xiph/';port='native/sources/components/native_vorbis_xiph_port/'
        need(sha(read(base+'component-manifest.json'))==BASE and sha(read(port+'port-manifest.json'))==PORT,'exact baseline and resource-port identity')
        need(sha(read(port+'prepare.py'))==GENERATOR,'exact reviewed materializer source')
        for prefix,manifest_name in((base,'component-manifest.json'),(port,'port-manifest.json')):
            record=json.loads(read(prefix+manifest_name))
            for name,digest in record['files'].items():need(sha(read(prefix+name))==digest,'unchanged source identity '+name)
        generated=native['generated_porting'];record=generated['record'];root='native/'+generated['path'].rsplit('/',1)[0]+'/'
        need(sha(read('native/'+generated['path']))==generated['sha256'],'actual generated record')
        need(read('host/generated/PORTING.json')==read('native/'+generated['path']),
             'same host/native exact port record')
        originals=json.loads(read(base+'component-manifest.json'));expected={'base/'+name:read(base+name)for name in originals['files']};expected['base/component-manifest.json']=read(base+'component-manifest.json');modified={}
        edits=json.loads(read(port+'edits.json'))['edits'];need(len(edits)==16,'all sixteen reviewed source edits')
        applied=[]
        for edit in edits:
            source=edit['source'];before,after=read(port+edit['before']),read(port+edit['after']);body=modified.get(source,read(base+source));need(body.count(before)==1,'unique exact before fragment');modified[source]=body.replace(before,after,1)
            applied.append(dict(source=source,before=edit['before'],after=edit['after'],before_sha256=sha(before),after_sha256=sha(after)))
        need(set(modified)==PORTED_UNITS,'exact nine ported units')
        expected.update({'ported/'+PurePosixPath(n).name:b for n,b in modified.items()})
        private=read(port+'include/'+PRIVATE_HEADER);expected['ported/'+PRIVATE_HEADER]=private
        need(record['files']=={n:sha(b)for n,b in expected.items()}and len(expected)==126 and len(record['compiled_units'])==22,'complete generated file map including the owned private header')
        units=[dict(original=name,compiled='ported/'+PurePosixPath(name).name if name in modified else'base/'+name)for name in originals['compile_sources']]
        need(record['schema']=='native-vorbis-xiph-generated-port-v1'and record['base_manifest_sha256']==BASE and record['port_manifest_sha256']==PORT and record['edits']==applied and record['compiled_units']==units and host['porting']==record,'complete exact edit identities and selected compiled source map')
        need(sum(row['compiled'].startswith('ported/')for row in record['compiled_units'])==9,'nine selected modified library units')
        generated_prefix=generated['path'].rsplit('/',1)[0]+'/'
        wanted_sources={generated_prefix+name:sha(body)for name,body in expected.items()};wanted_sources[generated['path']]=generated['sha256']
        need(native['generated_sources']==wanted_sources and len(wanted_sources)==127,'all127 actual generated outputs')
        for name,body in expected.items():need(read(root+name)==body and read('host/generated/'+name)==body,'same exact host/native generated source')
        baseline_witness(read,set(names),host,read(base+'upstream/libvorbis/lib/info.c'))
        first_marker_rejection(read,port,read(base+'upstream/libvorbis/lib/info.c'))
        residue=read('host/sources/native/vorbis_xiph_residue.c');need(sha(residue)==RESIDUE_FIXTURE and residue==read('native/sources/helpers/vorbis_xiph_residue.c')==read('native/project/main/vorbis_xiph_residue.c'),'same host/native executed residue fixture')
        headers=read('host/sources/native/vorbis_xiph_headers.c');need(sha(headers)==HEADER_FIXTURE and headers==read('native/sources/helpers/vorbis_xiph_headers.c')==read('native/project/main/vorbis_xiph_headers.c'),'same host/native executed header failure fixture')
        model=json.loads(read('native/sources/cases/cases.json'));need(sha(json.dumps(model,sort_keys=True,separators=(',',':')).encode())==MODEL,'unchanged original31 model')
        raw=read('sources/tests/run-vorbis-xiph-port-qemu.py');need(sha(raw)==READER,'pinned owned pure protocol reader');module=types.ModuleType('saved_xiph_resource_protocol');module.__file__=str(Path(__file__).resolve().parent/'run-vorbis-xiph-port-qemu.py');exec(compile(raw,module.__file__,'exec'),module.__dict__)
        cases=module.validate_cases(model,read('native/sources/cases/cases.h').decode('ascii'));log=read('native/qemu.stdout.log').decode('utf-8',errors='replace')+'\n'+read('native/qemu.stderr.log').decode('utf-8',errors='replace');replayed=module.validate_log(log,cases,'esp32',native['source_sha256']['cases'],BASE);rows=replayed.pop('rows');need(rows==native['rows']and replayed==native['observed'],'whole original31 native protocol')
        fixture_rows={'fixture':'main.c',**{name:name for name in module.HELPERS if name.endswith('.c')}}
        need(len(fixture_rows)==7 and len(native['compile_rows'])==29 and set(native['compile_rows'])==set(fixture_rows)|set(originals['compile_sources']),'all29 actual selected native compilation rows')
        suffix='/project/main/main.c';fixture_path=module.normalize(native['compile_rows']['fixture']['file']);need(fixture_path.endswith(suffix),'actual main compile source path');capture_root=fixture_path[:-len(suffix)]
        database=json.loads(read('native/build/compile_commands.json'))
        for name,row in native['compile_rows'].items():
            expected_path=capture_root+'/project/main/'+fixture_rows[name]if name in fixture_rows else capture_root+'/'+generated_prefix+next(unit['compiled']for unit in units if unit['original']==name)
            need(sum(entry==row for entry in database)==1 and module.normalize(row['file'])==expected_path,'actual selected compiler database row '+name)
            need(all(flag in row['command']for flag in('-fno-fast-math','-ffp-contract=off','-fstack-usage')),'actual selected arithmetic and stack flags')
        frames=[]
        need(len(native['stack_usage']['paths'])==22 and len(set(native['stack_usage']['paths']))==22,'all22 library compiler stack records')
        for path in native['stack_usage']['paths']:
            for line in read('native/'+path).decode().splitlines():
                fields=line.rsplit('\t',2);need(len(fields)==3 and fields[1].isdigit(),'actual compiler stack row')
                frames.append(dict(function=fields[0].rsplit(':',1)[-1],bytes=int(fields[1]),qualifier=fields[2],path=path))
        need(frames==native['stack_usage']['rows'],'saved compiler stack rows replayed')
        helper=[row for row in frames if row['function']=='vorbis_book_decodevs_add'];need(len(helper)==1 and helper[0]['bytes']==32 and helper[0]['qualifier']=='static','repaired residue0 helper has observed32byte static own frame')
        lint=json.loads(read('lint/report.json'));need(lint['completed']and lint['errors']==0 and len(lint['commands'])==29 and lint['native_report_sha256']==sha(read('native/report.json')),'complete Clang observation on the same29actual units')
        warnings=errors=0
        for index,command in enumerate(lint['commands']):
            stem=str(index).zfill(2)+'-'+PurePosixPath(command['name']).stem;streams=[]
            need(command['returncode']==0 and not command.get('forced_stop'),'normal actual Clang terminal')
            for stream in('stdout','stderr'):
                body=read('lint/'+stem+'.'+stream+'.log');need(sha(body)==command[stream+'_sha256'],'actual Clang stream bytes');streams.append(body.decode('utf-8',errors='replace'))
            text='\n'.join(streams);wc=len(re.findall(r': warning:',text));ec=len(re.findall(r': (?:error|fatal error):',text))
            need(wc==command['warnings']and ec==command['errors'],'actual Clang diagnostic counts');warnings+=wc;errors+=ec
        need(warnings==lint['warnings']and errors==lint['errors']==0,'complete replayed Clang counts without error')
        resources=module.validate_resource_log(log,cases,BASE,PORT);need(resources==native['resource_observed']and resources['arena_checks']==11 and resources['book_checks']==200864 and resources['bit_checks']==124754 and resources['residue_checks']==3997 and resources['header_checks']==1598 and resources['records']==42 and resources['final_live']==resources['final_bytes']==0,'all42 resource and per-case cleanup records')
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
        return dict(verified=True,arena=11,books=200864,bits=124754,residue=3997,headers=1598,baseline_regression_reproduced=True,source_marker_rejection_replayed=True,residue0_own_static_frame=32,clang_units=29,clang_warnings=warnings,cases=31,packets=434,pcm_bytes=total,max_abs_error=maximum,physical_device=False,general_OOM_qualified=False,general_16KiB_stack_bound=False)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive',type=Path);args=parser.parse_args();print(json.dumps(verify(args.archive)))
if __name__=='__main__':main()
