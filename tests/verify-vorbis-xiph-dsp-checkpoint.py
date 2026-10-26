"""Replay saved resource/PCM evidence without launching a decoder or tool.

Checks all ZIP members, exact source deviations, raw native watchdog diagnostics and the complete
host PCM vectors. Native PCM remains numerically unqualified. Also binds the preceding-block regression witness
to the same fixture and object-link recipe. Only the pinned owned pure protocol
reader is reused. No decoder, compiler, SDK or subprocess is launched.
"""
import argparse,hashlib,json,re,struct,types,zipfile
from pathlib import Path,PurePosixPath
READER='e39a34fb8146b4de67fe3ef2ec81107cddb1717c72c1a0efc7e5e8434da1fa81'
BASE='897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14'
PORT='33931bdee52616bfcd87b10d9dbe6e872d1648e718ea0b3ff93e460240d2482f'
MODEL='a12fcb6fea905027f9af4b1d1e5b5b561fa447f457d236cd5d004fd948b07883'
GENERATOR='8e48c251b3df4feda8bc1753db332dae0d9a4d4ed4e7eaca530cfbeff36a1e3d'
RESIDUE_FIXTURE='2d6455dc5e0d0eae33f6ee0cebc7cdf7162664bb316927ae7707bf30175ae45f'
HEADER_FIXTURE='0681da33fb618d91dd22bcb7e809523d0d830f6184659c77e38d9a387cffa03e'
DSP_FIXTURE='09dc6f13d7034ba2f26068aac79947756ae4804de8e67aabd756a5799433fde5'
BASELINE_BLOCK='e558e1d131e9be108d5e6e19543a70cb960769009f7e09aa6e179d6387c5fcdb'
PRIVATE_HEADERS=('native_vorbis_xiph_header_error.h','native_vorbis_xiph_dsp_error.h')
PORTED_UNITS={'upstream/libvorbis/lib/'+name+'.c'for name in('block','sharedbook','codebook','floor0','floor1','res0','mapping0','info','mdct')}|{'upstream/libogg/src/bitwise.c'}
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

def baseline_witness(read,names,host,original_block,port):
    baseline=json.loads(read('baseline/report.json'))
    need(baseline['completed']is True and baseline['expected_regression']is True and sha(read('host/report.json'))==baseline['host_report_sha256'],'baseline bound to actual successful host report')
    preceding=original_block;excluded={'edits/block-dsp-init.after.c','edits/block-dsp-clear.after.c'};retained=[]
    for edit in json.loads(read(port+'edits.json'))['edits']:
        if edit['source']!='upstream/libvorbis/lib/block.c' or edit['after']in excluded:continue
        before,after=read(port+edit['before']),read(port+edit['after'])
        need(preceding.count(before)==1,'one exact preceding block edit');preceding=preceding.replace(before,after,1);retained.append(edit['after'])
    need(retained==['edits/block-ripcord.after.c'],'only the preceding arena repair remains in the baseline block')
    need(read('baseline/block.c')==preceding and sha(preceding)==BASELINE_BLOCK==baseline['source_sha256'],'baseline retains the qualified arena repair and excludes only new DSP init/clear edits')
    fixture=read('host/sources/native/vorbis_xiph_dsp.c');need(sha(fixture)==DSP_FIXTURE,'same executed DSP failure fixture')
    need(preceding.decode().splitlines()[196].strip()=='b->modebits=ov_ilog(ci->modes-1);','original sanitizer source location is the unchecked backend use')
    need(fixture.decode().splitlines()[125].strip()=='stream_open(stream,&info,&comment);memset(&dsp,0,sizeof(dsp));xiph_port_test_reset(ordinal);','actual fixture arms an allocation refusal before the failing DSP init')
    need(fixture.decode().splitlines()[126].strip()=='CHECK(vorbis_synthesis_init(&dsp,&info)==1);','failure is observed through the unchanged public DSP init API')
    error=read('baseline/execute.stderr.log').decode()
    need(re.search(r"/block\.c:197:14: runtime error: member access within null pointer of type 'struct private_state'",error)is not None and all(name in error for name in('_vds_shared_init','vorbis_synthesis_init','dsp_sweep','xiph_dsp_tests')),'actual UBSan DSP-allocation regression with expected caller chain')
    need(not read('baseline/execute.stdout.log')and 'baseline/unexpected-pcm.bin'not in names,'preceding witness stopped before publishing PCM')
    commands=baseline['commands'];need([row['name']for row in commands]==['compile','link','execute'],'three actual baseline commands')
    for index,command in enumerate(commands):owned_command(read,'baseline/',command,command['argv'],0 if index<2 else 1)
    successful={row['name']:row['child_argv']for row in host['commands']}
    expected_compile=list(successful['compile-library-02']);compile_argv=commands[0]['argv']
    source_index,object_index=expected_compile.index('-c')+1,expected_compile.index('-o')+1
    need(expected_compile[source_index].endswith('/generated/ported/block.c')and expected_compile[object_index].endswith('/objects/library-02.o'),'actual repaired block compile slot')
    baseline_source=compile_argv[source_index];need(baseline_source.endswith('/block.c'),'actual baseline block source operand');directory=baseline_source.rsplit('/',1)[0]
    expected_compile[source_index]=directory+'/block.c';expected_compile[object_index]=directory+'/block.o'
    need(compile_argv==expected_compile,'only preceding block source/object replaces the successful host compile recipe')
    expected_link=[directory+'/block.o'if item==successful['compile-library-02'][object_index]else item for item in successful['link']]
    expected_link[expected_link.index('-o')+1]=directory+'/baseline-tests'
    need(commands[1]['argv']==expected_link and expected_link.count(directory+'/block.o')==1,'same actual host fixtures and other objects in baseline link')
    execute_argv=commands[2]['argv'];need(len(execute_argv)==5 and execute_argv[:2]==['python3','-c']and execute_argv[3:]==[directory+'/baseline-tests',directory+'/unexpected-pcm.bin'],'actual baseline executable and output operands')
    need('resource.setrlimit(resource.RLIMIT_CORE,(0,0))'in execute_argv[2]and 'os.execve(sys.argv[1],sys.argv[1:]'in execute_argv[2]and 'UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1"'in execute_argv[2],'sanitizer witness exec preserves owned PID and disables core files')
    need(read('baseline/block.o')!=read('host/objects/library-02.o')and read('baseline/baseline-tests')!=read('host/resource-tests')and sha(read('baseline/baseline-tests'))==baseline['binary_sha256'],'separate captured preceding source object and executable')
    need(read('baseline/supervisor.py')==read('host/supervisor.py'),'same owned process supervisor')
    outer=json.loads(read('receipts/baseline.json'));need(outer['status']=='TERMINAL'and outer['returncode']==0,'actual successful outer baseline witness')
    for old,pin in outer['logs'].items():need(sha(read('receipts/'+old.replace('\\','/').rsplit('/',1)[-1]))==pin['sha256'],'actual preceding outer witness stream')
    need(not read('receipts/baseline.stderr.log'),'baseline witness collector completed without diagnostics')


def verify(path):
    with zipfile.ZipFile(path)as archive:
        names=archive.namelist();need(len(names)==len(set(names)),'unique archive members')
        need(all(not PurePosixPath(n).is_absolute()and '..'not in PurePosixPath(n).parts and ':'not in n and '\\'not in n for n in names),'relative member paths')
        read=archive.read;inventory=json.loads(read('manifest.json'))
        need(inventory['schema']=='vorbis-xiph-dsp-checkpoint-v1'and set(names)==set(inventory['files'])|{'manifest.json'},'complete member inventory')
        for name,pin in inventory['files'].items():
            raw=read(name);need(len(raw)==pin['bytes']and sha(raw)==pin['sha256'],'saved member '+name)
        host=json.loads(read('host/report.json'));native=json.loads(read('native/report.json'))
        need(host['completed']and host['passed']and host['sanitizers']==['address','undefined']and host['max_abs_error']==0,'complete sanitizer host result')
        need(host['dsp_scenarios']==3584 and host['header_scenarios']==1598 and host['residue_scenarios']==3997 and host['arena_scenarios']==11 and host['book_assertions']==200864 and host['bitreader_assertions']==124754,'all focused host resource counts')
        need([row['name']for row in host['commands']]==['compiler-version','compiler-machine']+['compile-library-'+str(i).zfill(2)for i in range(22)]+['compile-fixture-'+name for name in('alloc','arena','books','bits','residue','headers','dsp','host')]+['link','execute'],'all thirty-four actual host commands')
        for name in('host','generation','protocol','pcm-units','baseline'):
            terminal=json.loads(read('receipts/'+name+'.json'));need(terminal['status']=='TERMINAL'and type(terminal['returncode'])is int and terminal['returncode']==0,'actual outer terminal '+name)
            for old,pin in terminal['logs'].items():need(sha(read('receipts/'+old.replace('\\','/').rsplit('/',1)[-1]))==pin['sha256'],'actual outer stream '+name)
        terminal=json.loads(read('receipts/native.json'));need(terminal['status']=='TERMINAL'and terminal['returncode']==1,'native watchdog NONPASS outer result retained')
        for old,pin in terminal['logs'].items():need(sha(read('receipts/'+old.replace('\\','/').rsplit('/',1)[-1]))==pin['sha256'],'actual rejected native outer stream')
        need('ValueError: native panic/corruption/timeout'in read('receipts/native.stderr.log').decode(),'actual strict-reader failure is preserved')
        for command in host['commands']:owned_command(read,'host/',command,command['child_argv'],0)
        need(not read('host/execute.stderr.log'),'sanitizer execution has no diagnostics')
        need(read('host/execute.stdout.log').decode().splitlines()==[
            'RESOURCE_CHECKS arena=11 books=200864 bits=124754 residue=3997 headers=1598 dsp=3584 live=0',
            'RESOURCE_PASS arena=11 books=200864 cases=31 packets=434 pcm_bytes=738560 live=0'],
            'actual complete host resource markers')
        need(sha(read('host/resource-tests'))==host['binary_sha256'],'saved actual sanitizer executable')
        need(native['completed']is False and native['capture_completed']is False and native['result']=='NONPASS'and native['passed']is False and native['resource_tests_completed']is False and native['numerical_qualified']is False,'native report remains unqualified after watchdog rejection')
        need(native['error']=="ValueError('native panic/corruption/timeout')"and native['whole_module_compiled']and native['exact_source_port_validated'],'actual native failure classification and prior source/build checks')
        need([row['name']for row in native['commands']]==['sdk-head','sdk-clean','build','dependencies','symbols','merge','qemu'],'seven completed commands before strict-reader rejection')
        for command in native['commands']:
            need(command['state']=='complete'and command['exit_status']==0 and not command['timed_out']and not command['interrupted'],'owned native command terminal')
            for stream in('stdout','stderr'):need(sha(read('native/'+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],'actual native stream')
        need(native['build_outputs']=={}and native['rows']==[],'first rejected attempt has no invented final outputs or qualified rows')
        for prefix,report in(('host/',host),('native/',native)):
            for pin in report['inputs'].values():
                raw=read(prefix+pin['snapshot']);need(sha(raw)==pin['sha256']and('bytes'not in pin or len(raw)==pin['bytes']),'all frozen input snapshots '+prefix+pin['snapshot'])
        base='native/sources/components/native_vorbis_xiph/';port='native/sources/components/native_vorbis_xiph_port/'
        need(sha(read(base+'component-manifest.json'))==BASE and sha(read(port+'port-manifest.json'))==PORT,'exact baseline and resource-port identity')
        need(sha(read(port+'prepare.py'))==GENERATOR,'exact reviewed materializer source')
        for location,manifest_name in((base,'component-manifest.json'),(port,'port-manifest.json')):
            for name,digest in json.loads(read(location+manifest_name))['files'].items():need(sha(read(location+name))==digest,'unchanged source identity '+name)
        generated=native['generated_porting'];record=generated['record'];source_root='native/'+generated['path'].rsplit('/',1)[0]+'/'
        need(sha(read('native/'+generated['path']))==generated['sha256']and read('host/generated/PORTING.json')==read('native/'+generated['path']),'same actual host/native generated record')
        originals=json.loads(read(base+'component-manifest.json'));expected={'base/'+name:read(base+name)for name in originals['files']};expected['base/component-manifest.json']=read(base+'component-manifest.json');modified={}
        edits=json.loads(read(port+'edits.json'))['edits'];need(len(edits)==23,'all twenty-three reviewed source edits');applied=[]
        for edit in edits:
            source=edit['source'];before,after=read(port+edit['before']),read(port+edit['after']);raw=modified.get(source,read(base+source));need(raw.count(before)==1,'unique exact before fragment');modified[source]=raw.replace(before,after,1)
            applied.append(dict(source=source,before=edit['before'],after=edit['after'],before_sha256=sha(before),after_sha256=sha(after)))
        need(set(modified)==PORTED_UNITS,'exact ten ported units');expected.update({'ported/'+PurePosixPath(n).name:raw for n,raw in modified.items()})
        for name in PRIVATE_HEADERS:expected['ported/'+name]=read(port+'include/'+name)
        need(record['files']=={n:sha(raw)for n,raw in expected.items()}and len(expected)==128 and len(record['compiled_units'])==22,'complete generated source map including both owned private headers')
        units=[dict(original=name,compiled='ported/'+PurePosixPath(name).name if name in modified else'base/'+name)for name in originals['compile_sources']]
        need(record['schema']=='native-vorbis-xiph-generated-port-v1'and record['base_manifest_sha256']==BASE and record['port_manifest_sha256']==PORT and record['edits']==applied and record['compiled_units']==units and host['porting']==record,'all exact edit identities and selected compile sources')
        need(sum(row['compiled'].startswith('ported/')for row in units)==10,'ten selected modified library units')
        generated_prefix=generated['path'].rsplit('/',1)[0]+'/';wanted={generated_prefix+name:sha(raw)for name,raw in expected.items()};wanted[generated['path']]=generated['sha256']
        need(native['generated_sources']==wanted and len(wanted)==129,'all129 generated source files retained despite failed runtime gate')
        for name,raw in expected.items():need(read(source_root+name)==raw and read('host/generated/'+name)==raw,'same exact host/native generated source')
        baseline_witness(read,set(names),host,read(base+'upstream/libvorbis/lib/block.c'),port)
        for stem,pin in(('residue',RESIDUE_FIXTURE),('headers',HEADER_FIXTURE),('dsp',DSP_FIXTURE)):
            name='vorbis_xiph_'+stem+'.c';raw=read('host/sources/native/'+name)
            need(sha(raw)==pin and raw==read('native/sources/helpers/'+name)==read('native/project/main/'+name),'same original host/native executed fixture '+name)
        model=json.loads(read('native/sources/cases/cases.json'));need(sha(json.dumps(model,sort_keys=True,separators=(',',':')).encode())==MODEL,'unchanged original31 model')
        raw=read('sources/tests/run-vorbis-xiph-port-qemu.py');need(sha(raw)==READER,'frozen strict reader is unchanged');module=types.ModuleType('saved_xiph_dsp_protocol');module.__file__=str(Path(__file__).resolve().parent/'run-vorbis-xiph-port-qemu.py');exec(compile(raw,module.__file__,'exec'),module.__dict__)
        cases=module.validate_cases(model,read('native/sources/cases/cases.h').decode('ascii'))
        log=read('native/qemu.stdout.log').decode('utf-8',errors='replace')+'\n'+read('native/qemu.stderr.log').decode('utf-8',errors='replace')
        need('Task watchdog got triggered'in log and 'IDLE1 (CPU 1)'in log and 'CPU 1: vorbis_xiph'in log,'actual idle-starvation watchdog record')
        try:module.validate_log(log,cases,'esp32',native['source_sha256']['cases'],BASE)
        except ValueError as error:need(str(error)=='native panic/corruption/timeout','same strict runtime rejection')
        else:raise ValueError('watchdog attempt must remain rejected by the strict reader')
        resources=module.validate_resource_log(log,cases,BASE,PORT)
        need(resources==dict(arena_checks=11,book_checks=200864,bit_checks=124754,residue_checks=3997,header_checks=1598,dsp_checks=3584,records=44,per_case_zero_live=31,final_live=0,final_bytes=0,core=1),'complete raw resource markers are retained as diagnostics, not qualification')
        need(sum(line.startswith('XIPH_CASE ')for line in log.splitlines())==31 and 'XIPH_COMPLETE cases=31 controls=17 core=1'in log and 'XIPH_STOP status=CAPTURED'in log,'raw case/completion markers are retained without reclassifying the failed runtime')
        fixture_rows={'fixture':'main.c',**{name:name for name in module.HELPERS if name.endswith('.c')}}
        need(len(fixture_rows)==8 and len(native['compile_rows'])==30 and set(native['compile_rows'])==set(fixture_rows)|set(originals['compile_sources']),'all30 selected native compilation rows')
        suffix='/project/main/main.c';fixture_path=module.normalize(native['compile_rows']['fixture']['file']);need(fixture_path.endswith(suffix),'actual main compile source');capture_root=fixture_path[:-len(suffix)];database=json.loads(read('native/build/compile_commands.json'))
        for name,row in native['compile_rows'].items():
            expected_path=capture_root+'/project/main/'+fixture_rows[name]if name in fixture_rows else capture_root+'/'+generated_prefix+next(unit['compiled']for unit in units if unit['original']==name)
            need(sum(entry==row for entry in database)==1 and module.normalize(row['file'])==expected_path,'actual selected compiler row '+name)
        frames=[];need(len(native['stack_usage']['paths'])==22 and len(set(native['stack_usage']['paths']))==22,'all22 library stack records')
        for name in native['stack_usage']['paths']:
            for line in read('native/'+name).decode().splitlines():
                fields=line.rsplit('\t',2);need(len(fields)==3 and fields[1].isdigit(),'actual compiler stack row');frames.append(dict(function=fields[0].rsplit(':',1)[-1],bytes=int(fields[1]),qualifier=fields[2],path=name))
        need(frames==native['stack_usage']['rows'],'saved compiler stack rows replayed');helper=[row for row in frames if row['function']=='vorbis_book_decodevs_add'];need(len(helper)==1 and helper[0]['bytes']==32 and helper[0]['qualifier']=='static','prior residue helper32byte static frame retained')
        data=read('host/pcm.bin');need(sha(data)==host['capture_sha256']and data[:8]==b'XIPHRES1','actual qualified host PCM');at=8
        def u32():
            nonlocal at
            need(at+4<=len(data),'whole host capture field');value=struct.unpack_from('<I',data,at)[0];at+=4;return value
        need(u32()==31,'all31 host cases');targets={};references={};packets=total=maximum=0
        for index,case in enumerate(cases):
            need([u32()for _ in range(4)]==[index,case['rate'],case['channels'],14],'whole host case metadata');parts=[]
            for packet,frames in enumerate(case['frames']):
                need([u32()for _ in range(3)]==[packet,frames,frames*4],'whole host packet metadata');raw=data[at:at+frames*4];at+=frames*4;need(len(raw)==frames*4,'whole host packet PCM');parts.append(raw);packets+=1
            actual=b''.join(parts);reference=read('host/sources/cases/'+case['reference_path']);need(sha(reference)==case['reference_pcm_sha256']and len(actual)==len(reference)==case['pcm_bytes'],'same full untrimmed host reference')
            values=lambda raw:struct.unpack('<'+'h'*(len(raw)//2),raw);error=max((abs(a-b)for a,b in zip(values(actual),values(reference))),default=0);maximum=max(maximum,error);need(error<=2,'unchanged fixed2-S16 host bound');targets[case['id']]=actual;references[case['id']]=reference;total+=len(reference)
        need(at==len(data)and packets==434 and total==738560 and maximum==0,'complete original31 exact host measurement')
        for table in(targets,references):
            for relation in model['relations']:
                ids=relation['cases'];equal=all(table[name]==table[ids[0]]for name in ids[1:]);need(equal==(relation['kind']=='equal'),'all14 exact host/reference relations')
        return dict(verified_evidence=True,host_qualified=True,native_qualified=False,watchdog_nonpass=True,native_pcm_numerically_qualified=False,arena=11,books=200864,bits=124754,residue=3997,headers=1598,dsp=3584,baseline_regression_reproduced=True,diagnostic_resource_records=44,host_cases=31,host_packets=434,host_pcm_bytes=total,host_max_abs_error=maximum,physical_device=False,general_OOM_qualified=False,general_16KiB_stack_bound=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive',type=Path);args=parser.parse_args();print(json.dumps(verify(args.archive)))
if __name__=='__main__':main()
