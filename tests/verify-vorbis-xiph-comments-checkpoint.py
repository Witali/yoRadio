"""Replay saved independent metadata evidence without executing a tool.

Verifies source transformations, host process receipts, the preceding public
query failure, metadata-only native symbols/protocol and saved Clang streams.
No archive extraction, subprocess, SDK, decoder or DSP execution occurs.
"""
import argparse,hashlib,json,re,struct,types,zipfile
from pathlib import Path,PurePosixPath

BASE='897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14'
PORT='decee153fa4d2a02802e13eaf5bb527afc6e2346e0a020265cad7531b97e2e6d'
GENERATOR='4ea38a55c69bb4c8dec086972f87b62ef32ca24b9bcf9ef25709b5bdf2bb9928'
CONTROLLER='3e82fba33e238bd97594c728b6049e791289832094dae6bea3931bb1a6836016'
FIXTURE='fa56ed8ed50f58507babca311e81b49c57c8973ea4e995e7c2fe176d1dfe7d3f'
FIRST_FIXTURE='b19953408ab9a09a14c4d74f83118a5e3436bc4dc3a24aa1540900ed645fb121'
QUERY_FIXTURE='b091beaa750b56156cb875ffd72c9b1a14b4fd2968723009fef68cfb1850d595'
PRECEDING_INFO='8f48326e261177b58319edf7d043b72bd5ad63909dfdebdece3506ca249a48ed'
QEMU='4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d'
SDK='7101770dc6db2667b3c477cc31365dd1acd6db4e'
PRIVATE_HEADERS=('native_vorbis_xiph_header_error.h','native_vorbis_xiph_dsp_error.h','native_vorbis_xiph_comment_error.h')
PORTED_UNITS={'upstream/libvorbis/lib/'+name+'.c'for name in('block','sharedbook','codebook','floor0','floor1','res0','mapping0','info','mdct')}|{'upstream/libogg/src/bitwise.c'}

def need(ok,reason):
    if not ok:raise ValueError(reason)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def owned_command(read,prefix,command,argv,status):
    name=command['name'];request_raw=read(prefix+name+'.request.json');request=json.loads(request_raw);observed=command['supervisor']
    need(command['transport_exit']==0 and not command.get('forced_stop')and not command.get('forced_transport_stop'),'normal owned transport '+prefix+name)
    need(observed==json.loads(read(prefix+name+'.receipt.json'))and observed['state']=='terminal'and observed['child_returncode']==status and observed['child_reaped']and observed['group_gone']and observed['new_session']and observed['final'],'actual owned command/group terminal '+prefix+name)
    need(type(observed['child_pid'])is int and observed['child_pid']>0 and observed['child_pid']==observed['owned_pgid'],'owned child is process-group leader')
    need(sha(request_raw)==observed['request_sha256']==command['request_sha256']and observed['nonce']==command['nonce']==request['nonce']and request['argv']==argv and request['timeout']==60,'nonce-bound actual request '+prefix+name)
    for stream in('stdout','stderr'):need(sha(read(prefix+name+'.'+stream+'.log'))==command[stream+'_sha256'],'actual owned stream '+prefix+name)

def source_inputs(read,prefix,report):
    for pin in report['inputs'].values():
        body=read(prefix+pin['snapshot']);need(sha(body)==pin['sha256']and('bytes'not in pin or len(body)==pin['bytes']),'frozen input '+prefix+pin['snapshot'])

def host_result(read,prefix,cases,fixture_sha):
    report=json.loads(read(prefix+'report.json'))
    need(report['completed']and report['passed']and report['cases']==cases and report['sanitizers']==['address','undefined']and report['library_units']==22 and report['fixture_units']==3,'complete metadata-only sanitizer result '+prefix)
    for key in('raw_header_decoder_executed','dsp_executed','packet_decoder_executed','deferred_DSP_gate_resumed','full_decoder_qualified','production_radio_integration','physical_device'):need(report[key]is False,'host scope remains metadata-only '+key)
    expected=['compiler-version','compiler-machine']+['compile-library-'+str(i).zfill(2)for i in range(22)]+['compile-fixture-'+name for name in('alloc','comments','comments_host')]+['link','execute']
    need([row['name']for row in report['commands']]==expected,'all29 actual host commands '+prefix)
    for command in report['commands']:owned_command(read,prefix,command,command['child_argv'],0)
    commands={row['name']:row['child_argv']for row in report['commands']};first=commands['compile-library-00'];suffix='/generated/'+report['porting']['compiled_units'][0]['compiled'];source=first[first.index('-c')+1]
    need(source.endswith(suffix),'actual host generated compile root');directory=source[:-len(suffix)];objects=[]
    for index,unit in enumerate(report['porting']['compiled_units']):
        argv=commands['compile-library-'+str(index).zfill(2)];obj=directory+'/objects/library-'+str(index).zfill(2)+'.o';objects.append(obj)
        need(argv[argv.index('-c')+1]==directory+'/generated/'+unit['compiled']and argv[argv.index('-o')+1]==obj and argv.count('-include')==1 and argv[argv.index('-include')+1]==directory+'/sources/native/vorbis_xiph_alloc_inject.h','actual selected/injected host library compile '+str(index))
    for stem in('alloc','comments','comments_host'):
        argv=commands['compile-fixture-'+stem];obj=directory+'/objects/fixture-'+stem+'.o';objects.append(obj)
        need(argv[argv.index('-c')+1]==directory+'/sources/native/vorbis_xiph_'+stem+'.c'and argv[argv.index('-o')+1]==obj and '-include'not in argv,'actual non-injected host fixture compile '+stem)
    for name,argv in commands.items():
        if name.startswith('compile-'):need(all(flag in argv for flag in('-UNDEBUG','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-fast-math','-ffp-contract=off'))and not any(flag.startswith('-DNDEBUG')for flag in argv),'actual host sanitizer/assertion/arithmetic flags '+name)
    need(commands['link']==['gcc','-fsanitize=address,undefined','-fno-sanitize-recover=all','-no-pie','-Wl,--gc-sections',*objects,'-lm','-o',directory+'/comment-tests'],'actual complete host object/link recipe')
    need(commands['execute']==['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',directory+'/comment-tests'],'actual metadata-only sanitizer executable invocation')
    need(not read(prefix+'execute.stderr.log')and read(prefix+'execute.stdout.log').decode().strip()=='COMMENT_PASS cases='+str(cases)+' live=0 bytes=0','complete asserted metadata-only marker '+prefix)
    need(sha(read(prefix+'comment-tests'))==report['binary_sha256'],'saved actual metadata executable '+prefix)
    source_inputs(read,prefix,report)
    fixture=read(prefix+'sources/native/vorbis_xiph_comments.c');need(sha(fixture)==fixture_sha,'pinned metadata fixture '+prefix)
    need(not re.search(rb'\b(?:vorbis_synthesis\w*|vorbis_dsp_clear|xiph_dsp_tests|xiph_header_tests|vTaskDelay|taskYIELD)\s*\(',fixture),'metadata fixture has no decoder/DSP/scheduling calls')
    caller=read(prefix+'sources/native/vorbis_xiph_comments_host.c');need(b'xiph_comment_tests()'in caller and not re.search(rb'\b(?:vorbis_synthesis\w*|vorbis_dsp_clear|xiph_dsp_tests|xiph_header_tests)\s*\(',caller),'actual host caller remains metadata-only')
    return report

def baseline_result(read,host,ported_info,port_prefix):
    baseline=json.loads(read('baseline/report.json'));need(baseline['completed']and baseline['expected_regression']and baseline['metadata_only']and baseline['dsp_executed']is False,'public query baseline remains metadata-only')
    need(baseline['host_report_sha256']==sha(read('host/report.json')),'baseline bound to final host recipe')
    before=read(port_prefix+'edits/info-comment-api.before.c');after=read(port_prefix+'edits/info-comment-api.after.c')
    need(ported_info.count(after)==1,'unique metadata source edit for baseline reversal');preceding=ported_info.replace(after,before,1)
    need(read('baseline/info.c')==preceding and sha(preceding)==PRECEDING_INFO==baseline['source_sha256'],'only metadata edit reversed from preceding qualified source')
    query=read('baseline/query.c');need(sha(query)==QUERY_FIXTURE==baseline['query_fixture_sha256'],'standalone public query baseline fixture')
    need(query.decode().splitlines()[7].strip()=='int count=vorbis_comment_query_count(&value,"title");'and b'xiph_port_test_reset(1)'in query,'refusal occurs at the public lookup call')
    need(not re.search(rb'\b(?:vorbis_synthesis\w*|vorbis_dsp_clear|xiph_dsp_tests|xiph_header_tests)\s*\(',query),'baseline does not invoke decoding or DSP')
    error=read('baseline/execute.stderr.log').decode();need('/info.c:119:3: runtime error: null pointer passed as argument 1'in error and 'vorbis_comment_query_count'in error and '/query.c:8'in error,'actual preceding query allocation diagnostic')
    need(not read('baseline/execute.stdout.log'),'failed preceding query emits no success marker')
    commands=baseline['commands'];need([row['name']for row in commands]==['compile-old-info','compile-query','link','execute'],'four actual query witness commands')
    for index,command in enumerate(commands):owned_command(read,'baseline/',command,command['argv'],0 if index<3 else 1)
    successful={row['name']:row['child_argv']for row in host['commands']}
    expected=list(successful['compile-library-10']);compile_args=commands[0]['argv'];ci,oi=expected.index('-c')+1,expected.index('-o')+1
    need(expected[ci].endswith('/generated/ported/info.c')and expected[oi].endswith('/objects/library-10.o'),'actual metadata info library slot')
    directory=compile_args[ci].rsplit('/',1)[0];expected[ci]=directory+'/info.c';expected[oi]=directory+'/info.o';need(compile_args==expected,'only preceding info source/object substitutes host recipe')
    expected=list(successful['compile-fixture-comments_host']);expected[expected.index('-c')+1]=directory+'/query.c';expected[expected.index('-o')+1]=directory+'/query.o';need(commands[1]['argv']==expected,'standalone query uses actual host fixture compile flags')
    old_object=successful['compile-library-10'][oi];removed={successful['compile-fixture-comments'][successful['compile-fixture-comments'].index('-o')+1],successful['compile-fixture-comments_host'][successful['compile-fixture-comments_host'].index('-o')+1]}
    expected=[directory+'/info.o'if item==old_object else item for item in successful['link']if item not in removed];expected[expected.index('-lm'):expected.index('-lm')]=[directory+'/query.o'];expected[expected.index('-o')+1]=directory+'/query-tests'
    need(commands[2]['argv']==expected,'same other library/allocation objects and standalone query link recipe')
    execute=commands[3]['argv'];need(len(execute)==4 and execute[:2]==['python3','-c']and execute[3]==directory+'/query-tests'and 'os.execve(sys.argv[1],sys.argv[1:]'in execute[2]and 'UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1"'in execute[2],'actual sanitizer query witness invocation')
    need(sha(read('baseline/query-tests'))==baseline['binary_sha256']and read('baseline/info.o')!=read('host/objects/library-10.o')and read('baseline/supervisor.py')==read('host/supervisor.py'),'retained preceding-source executable/object and owned supervisor')

def verify(path):
    with zipfile.ZipFile(path)as archive:
        names=archive.namelist();need(len(names)==len(set(names))and all(not PurePosixPath(name).is_absolute()and '..'not in PurePosixPath(name).parts and ':'not in name and '\\'not in name for name in names),'unique contained archive members')
        read=archive.read;inventory=json.loads(read('manifest.json'));need(inventory['schema']=='vorbis-xiph-comments-checkpoint-v1'and set(names)==set(inventory['files'])|{'manifest.json'},'complete metadata archive inventory')
        for name,pin in inventory['files'].items():
            body=read(name);need(len(body)==pin['bytes']and sha(body)==pin['sha256'],'saved member '+name)
        host=host_result(read,'host/',399,FIXTURE);first=host_result(read,'host-first/',394,FIRST_FIXTURE)
        native=json.loads(read('native/report.json'));need(native['completed']and native['passed']and native['metadata_qualified']and native['whole_module_compiled']and native['source_inputs_unchanged']and native['exact_source_port_validated'],'complete independent native metadata result')
        need(native['target']=='esp32'and native['sdk_revision']==SDK and native['expected_cases']==399,'actual pinned native target/scenario count')
        for key in('decoder_executed','dsp_tests_executed','full_decoder_qualified','dsp_gate_qualified','production_firmware','production_radio_integration','physical_device'):need(native[key]is False,'native scope remains metadata-only '+key)
        source_inputs(read,'native/',native)
        receipts={PurePosixPath(name).stem for name in names if name.startswith('receipts/')and name.endswith('.json')and '/'not in name[len('receipts/'): ]}
        need({'host','host-final','native','baseline','generation','protocol','lint'}<=receipts,'all actual metadata qualification receipts')
        for name in receipts:
            terminal=json.loads(read('receipts/'+name+'.json'));need(terminal['status']=='TERMINAL'and type(terminal['returncode'])is int and terminal['returncode']==0,'normal retained outer terminal '+name)
            for old,pin in terminal['logs'].items():need(sha(read('receipts/'+old.replace('\\','/').rsplit('/',1)[-1]))==pin['sha256'],'actual outer stream '+name)
        commands=native['commands'];need([row['name']for row in commands]==['sdk-head','sdk-clean','build','dependencies','symbols','merge','qemu','sdk-head-after','sdk-clean-after'],'nine actual native metadata commands')
        for command in commands:
            need(command['state']=='complete'and command['exit_status']==0 and not command['timed_out']and not command['interrupted']and not any(key in command for key in('tree_stop_returncode','tree_stop_error')),'normal native command terminal')
            for stream in('stdout','stderr'):need(sha(read('native/'+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],'actual native command stream')
        need(read('native/sdk-head.stdout.log').decode().strip()==read('native/sdk-head-after.stdout.log').decode().strip()==SDK and not read('native/sdk-clean.stdout.log').strip()and not read('native/sdk-clean-after.stdout.log').strip(),'clean pinned SDK before/after metadata gate')
        base='native/sources/components/native_vorbis_xiph/';port='native/sources/components/native_vorbis_xiph_port/'
        need(sha(read(base+'component-manifest.json'))==BASE and sha(read(port+'port-manifest.json'))==PORT and sha(read(port+'prepare.py'))==GENERATOR,'pinned immutable base and metadata port')
        for prefix,manifest_name,count in((base,'component-manifest.json',116),(port,'port-manifest.json',57)):
            record=json.loads(read(prefix+manifest_name));expected=set(record['files'])|{manifest_name}
            need({name[len(prefix):]for name in names if name.startswith(prefix)}==expected and len(expected)==count,'complete saved component source inventory')
            for name,digest in record['files'].items():need(sha(read(prefix+name))==digest,'saved component source '+name)
        original=json.loads(read(base+'component-manifest.json'));expected={'base/'+name:read(base+name)for name in(*original['files'],'component-manifest.json')};modified={};applied=[]
        edits=json.loads(read(port+'edits.json'));need(edits['schema']=='native-vorbis-xiph-exact-edits-v1'and len(edits['edits'])==24,'all24 exact source edits')
        for edit in edits['edits']:
            source=edit['source'];before,after=read(port+edit['before']),read(port+edit['after']);body=modified.get(source,read(base+source));need(body.count(before)==1,'one exact source fragment');modified[source]=body.replace(before,after,1)
            applied.append(dict(source=source,before=edit['before'],after=edit['after'],before_sha256=sha(before),after_sha256=sha(after)))
        need(set(modified)==PORTED_UNITS,'ten modified C units only');expected.update({'ported/'+PurePosixPath(name).name:body for name,body in modified.items()})
        for name in PRIVATE_HEADERS:expected['ported/'+name]=read(port+'include/'+name)
        generated=native['generated_porting'];record=generated['record'];generated_prefix=generated['path'].rsplit('/',1)[0]+'/'
        units=[dict(original=name,compiled='ported/'+PurePosixPath(name).name if name in modified else'base/'+name)for name in original['compile_sources']]
        wanted=dict(schema='native-vorbis-xiph-generated-port-v1',base_manifest_sha256=BASE,port_manifest_sha256=PORT,edits=applied,compiled_units=units,files={name:sha(body)for name,body in sorted(expected.items())})
        need(record==wanted and host['porting']==record and first['porting']==record and len(expected)==129 and len(units)==22,'complete exact materialization and compile map')
        record_raw=(json.dumps(record,indent=2,sort_keys=True)+'\n').encode();need(read('native/'+generated['path'])==record_raw and sha(record_raw)==generated['sha256']and read('host/generated/PORTING.json')==read('host-first/generated/PORTING.json')==record_raw,'same actual generated record on both hosts/native')
        generated_paths={generated_prefix+name:sha(body)for name,body in expected.items()};generated_paths[generated['path']]=sha(record_raw)
        need(native['generated_sources']==generated_paths and len(generated_paths)==130,'all130 native generated files')
        for name,body in expected.items():need(read('native/'+generated_prefix+name)==read('host/generated/'+name)==read('host-first/generated/'+name)==body,'same exact generated source '+name)
        baseline_result(read,host,modified['upstream/libvorbis/lib/info.c'],port)
        fixture=read('host/sources/native/vorbis_xiph_comments.c');need(sha(fixture)==FIXTURE and fixture==read('native/sources/helpers/vorbis_xiph_comments.c')==read('native/project/main/vorbis_xiph_comments.c'),'same executed final metadata fixture')
        raw=read('sources/tests/run-vorbis-xiph-comments-qemu.py');need(sha(raw)==CONTROLLER and read('native/sources/controller.py')==raw,'pinned owned pure metadata controller')
        module=types.ModuleType('saved_metadata_protocol');module.__file__=str(Path(__file__).resolve().parent/'run-vorbis-xiph-comments-qemu.py');exec(compile(raw,module.__file__,'exec'),module.__dict__)
        need(native['source_sha256']=={'base-manifest':BASE,'port-manifest':PORT,'fixture':FIXTURE,'qemu':QEMU},'actual native input identities')
        log=read('native/qemu.stdout.log').decode('utf-8',errors='replace')+'\n'+read('native/qemu.stderr.log').decode('utf-8',errors='replace');observed=module.validate_log(log,BASE,PORT,FIXTURE,399)
        need(observed==native['observed'],'all four raw metadata-only events independently replayed')
        symbols=read('native/symbols.stdout.log').decode().replace('\r\n','\n');need(all(re.search(r'\b'+name+r'$',symbols,re.M)for name in module.PUBLIC),'actual linked comment APIs and hooks')
        need(not re.search(r'\b(?:vorbis_synthesis(?:_\w+)?|vorbis_dsp_clear|vorbis_block_init|xiph_dsp_tests|xiph_header_tests)\b$',symbols,re.M),'decoder/DSP/header-test symbols absent')
        fixture_rows={'fixture':'main.c','vorbis_xiph_alloc.c':'vorbis_xiph_alloc.c','vorbis_xiph_comments.c':'vorbis_xiph_comments.c'}
        need(len(native['compile_rows'])==25 and set(native['compile_rows'])==set(fixture_rows)|set(original['compile_sources']),'all25 actual metadata compilation rows')
        path=module.normalize(native['compile_rows']['fixture']['file']);suffix='/project/main/main.c';need(path.endswith(suffix),'actual native fixture source');capture_root=path[:-len(suffix)];database=json.loads(read('native/build/compile_commands.json'));inject=(capture_root+'/project/main/vorbis_xiph_alloc_inject.h').casefold()
        for name,row in native['compile_rows'].items():
            expected_path=capture_root+'/project/main/'+fixture_rows[name]if name in fixture_rows else capture_root+'/'+generated_prefix+next(unit['compiled']for unit in units if unit['original']==name)
            command=module.normalize(row['command']).casefold();need(sum(item==row for item in database)==1 and module.normalize(row['file'])==expected_path and all(flag in row['command']for flag in('-fno-fast-math','-ffp-contract=off','-fstack-usage')),'actual source/compiler flags '+name)
            need(('-include'in row['command']and inject in command)if name not in fixture_rows else inject not in command,'allocator injection confined to library '+name)
        frames=[];need(len(native['stack_usage']['paths'])==22 and len(set(native['stack_usage']['paths']))==22,'all22 library compiler stack records')
        for name in native['stack_usage']['paths']:
            for line in read('native/'+name).decode().splitlines():
                fields=line.rsplit('\t',2);need(len(fields)==3 and fields[1].isdigit(),'actual stack record');frames.append(dict(function=fields[0].rsplit(':',1)[-1],bytes=int(fields[1]),qualifier=fields[2],path=name))
        need(frames==native['stack_usage']['rows'],'actual library stack records replayed')
        config=read('native/sdkconfig').decode().replace('\r\n','\n');need(re.search(r'^CONFIG_ESP_TASK_WDT_EN=y$',config,re.M)and re.search(r'^CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=y$',config,re.M),'watchdog/core1 idle checks remain enabled')
        for name,digest in native['build_outputs'].items():need(sha(read('native/'+name))==digest,'saved actual native build output '+name)
        elf_header=read('native/elf-header.bin');need(len(elf_header)==52 and elf_header[:7]==b'\x7fELF\x01\x01\x01'and struct.unpack_from('<H',elf_header,18)[0]==native['elf_machine']==94,'actual ELF32 little-endian Xtensa header')
        description=json.loads(read('native/build/project_description.json'));need(read('native/build/'+description['app_elf'])[:52]==elf_header,'saved executable matches observed ELF header')
        lint=json.loads(read('lint/report.json'));need(lint['completed']and lint['errors']==0 and len(lint['commands'])==25 and lint['native_report_sha256']==sha(read('native/report.json')),'complete Clang observation on actual25 metadata units')
        warnings=errors=0
        for index,command in enumerate(lint['commands']):
            need(command['returncode']==0 and not command.get('forced_stop'),'normal Clang command terminal');stem=str(index).zfill(2)+'-'+PurePosixPath(command['name']).stem;streams=[]
            for stream in('stdout','stderr'):
                body=read('lint/'+stem+'.'+stream+'.log');need(sha(body)==command[stream+'_sha256'],'actual Clang stream');streams.append(body.decode('utf-8',errors='replace'))
            text='\n'.join(streams);wc=len(re.findall(r': warning:',text));ec=len(re.findall(r': (?:error|fatal error):',text));need(wc==command['warnings']and ec==command['errors'],'actual Clang counts');warnings+=wc;errors+=ec
        need(warnings==lint['warnings']and errors==lint['errors']==0,'all Clang diagnostics replayed')
        return dict(verified_evidence=True,metadata_qualified=True,host_cases=399,native_cases=399,initial_host_cases=394,baseline_query_regression_reproduced=True,generated_files=130,native_compile_rows=25,native_protocol_lines=4,clang_units=25,clang_warnings=warnings,decoder_executed=False,dsp_gate_qualified=False,production_radio_integration=False,physical_device=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive',type=Path);args=parser.parse_args();print(json.dumps(verify(args.archive)))
if __name__=='__main__':main()
