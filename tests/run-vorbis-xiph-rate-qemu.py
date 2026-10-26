"""Independent unsigned32 identification/comment metadata qualification.

This new project executes only the pinned rate fixture's H0/H1 metadata and
granule-time APIs. No setup, DSP initialization or audio packet decode runs.
All deferred packet/DSP/amplitude scopes retain their separate status.
"""
import argparse
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
PROJECT=ROOT/'tests/target/vorbis_xiph_rate_qemu'
BASE=ROOT/'idf/components/native_vorbis_xiph'
PORT=ROOT/'idf/components/native_vorbis_xiph_port'
HELPERS=('vorbis_xiph_alloc.h','vorbis_xiph_alloc_inject.h','vorbis_xiph_alloc.c','vorbis_xiph_rate.c')
PRIVATE_HEADERS=('native_vorbis_xiph_header_error.h','native_vorbis_xiph_dsp_error.h','native_vorbis_xiph_comment_error.h','native_vorbis_xiph_packet_error.h')
PUBLIC_HEADER='upstream/libvorbis/include/vorbis/codec.h'
PUBLIC_HEADERS=('codec.h','vorbisenc.h','vorbisfile.h')
HEADER_PROBES=tuple('probe_'+str(index)+'.'+extension for extension in ('c','cpp') for index in range(6))
VORBIS_UNITS=('mdct','smallft','block','envelope','window','lsp','lpc','analysis','synthesis','psy','info','floor1','floor0','res0','mapping0','registry','codebook','sharedbook','lookup','bitrate')
PORTED_UNITS={'upstream/libvorbis/lib/'+name+'.c'for name in('block','sharedbook','codebook','floor0','floor1','res0','mapping0','info','mdct','synthesis')}|{'upstream/libogg/src/bitwise.c'}
PUBLIC=('vorbis_info_init','vorbis_info_clear','vorbis_comment_init','vorbis_comment_clear','vorbis_synthesis_headerin','vorbis_info_blocksize','vorbis_granule_time','xiph_rate_tests','xiph_port_test_malloc','xiph_port_test_free')
SDK_HEAD='7101770dc6db2667b3c477cc31365dd1acd6db4e'

def need(ok,reason):
    if not ok:raise ValueError(reason)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def normalize(value):return str(value).replace('\\','/').rstrip('/')

def source_tree(root,manifest_name,pin,schema):
    need(sha(root/manifest_name)==pin,'reviewed source manifest identity')
    document=json.loads((root/manifest_name).read_bytes());need(document['schema']==schema and isinstance(document['files'],dict),'manifest schema')
    for name,digest in document['files'].items():
        path=PurePosixPath(name)
        need(name==path.as_posix()and path.parts and not path.is_absolute()and '..'not in path.parts and ':'not in name and '\\'not in name and name!=manifest_name and re.fullmatch('[0-9a-f]{64}',digest),'canonical source identity')
    paths=list(root.rglob('*'));need(not any(path.is_symlink()for path in paths),'regular source inventory')
    need({path.relative_to(root).as_posix()for path in paths if path.is_file()}==set(document['files'])|{manifest_name},'complete source inventory')
    need(all(sha(root/name)==digest for name,digest in document['files'].items()),'every source byte matches manifest')
    return document

def validate_base(document):
    wanted={'upstream/libvorbis/lib/'+name+'.c'for name in VORBIS_UNITS}|{'upstream/libogg/src/bitwise.c','upstream/libogg/src/framing.c'}
    need(len(document['compile_sources'])==22 and set(document['compile_sources'])==wanted and wanted<=document['files'].keys(),'all22 unchanged core library units')

def validate_generated(path,base,port,base_root,port_root,base_sha,port_sha):
    originals={name:(base_root/name).read_bytes()for name in (*base['files'],'component-manifest.json')}
    edits=json.loads((port_root/'edits.json').read_bytes());need(edits['schema']=='native-vorbis-xiph-exact-edits-v1'and len(edits['edits'])==35,'all35 declared exact edits')
    modified,applied={},[]
    for edit in edits['edits']:
        source,before_name,after_name=(edit[key]for key in('source','before','after'))
        need((source in base['compile_sources']or source==PUBLIC_HEADER)and before_name in port['files']and after_name in port['files'],'compiled source/rate public header and declared fragments')
        before,after=(port_root/before_name).read_bytes(),(port_root/after_name).read_bytes();body=modified.get(source,originals[source])
        need(before and after and before!=after and body.count(before)==1,'unique exact source fragment')
        modified[source]=body.replace(before,after,1)
        applied.append(dict(source=source,before=before_name,after=after_name,before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest()))
    need(set(modified)==PORTED_UNITS|{PUBLIC_HEADER},'exactly eleven C units and the rate public header change')
    expected={'base/'+name:body for name,body in originals.items()}
    expected.update({'ported/'+PurePosixPath(name).name:body for name,body in modified.items()if name!=PUBLIC_HEADER})
    public_headers=[]
    for name in PUBLIC_HEADERS:
        origin='upstream/libvorbis/include/vorbis/'+name;destination='ported/include/vorbis/'+name
        expected[destination]=modified.get(origin,originals[origin]);public_headers.append(dict(original=origin,generated=destination,modified=origin in modified))
    for name in PRIVATE_HEADERS:
        body=(port_root/'include'/name).read_bytes();need(hashlib.sha256(body).hexdigest()==port['files']['include/'+name],'owned private header identity');expected['ported/'+name]=body
    units=[dict(original=name,compiled='ported/'+PurePosixPath(name).name if name in modified else'base/'+name)for name in base['compile_sources']]
    record=dict(schema='native-vorbis-xiph-generated-port-v1',base_manifest_sha256=base_sha,port_manifest_sha256=port_sha,edits=applied,compiled_units=units,public_headers=public_headers,files={name:hashlib.sha256(body).hexdigest()for name,body in sorted(expected.items())})
    raw=(json.dumps(record,indent=2,sort_keys=True)+'\n').encode();need(path.read_bytes()==raw,'independently replayed PORTING record')
    paths=list(path.parent.rglob('*'));need(not any(p.is_symlink()for p in paths)and {p.relative_to(path.parent).as_posix()for p in paths if p.is_file()}==set(expected)|{'PORTING.json'}and len(paths)>=135,'complete generated source inventory')
    need(len(expected)==134 and all((path.parent/name).read_bytes()==body for name,body in expected.items()),'all135 exact generated files including record')
    return record

def validate_compile_sources(database,fixture_sources,porting,generated_root):
    need(len(fixture_sources)==15 and len(porting['compiled_units'])==22,'three metadata fixture, twelve public header probe and22library units')
    need(sum(row['compiled'].startswith('ported/')for row in porting['compiled_units'])==11,'eleven selected modified library units')
    expected=fixture_sources+[(unit['original'],generated_root/unit['compiled'])for unit in porting['compiled_units']]
    need(len({name for name,_ in expected})==37 and len({path for _,path in expected})==37,'all37 distinct source rows')
    selected={}
    for name,path in expected:
        found=[row for row in database if Path(row['file']).resolve()==path]
        need(len(found)==1,'unique actual metadata compile row '+name);selected[name]=found[0]
    return selected

def validate_log(log,base_sha,port_sha,fixture_sha,expected_cases):
    need(type(expected_cases)is int and expected_cases>0,'explicit measured metadata scenario count')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|task_wdt|stack overflow|timed out',log,re.I),'native diagnostic rejects metadata qualification')
    lines=log.splitlines();need(not any('RATE_'in line and not line.startswith('RATE_')for line in lines),'foreign/torn metadata event')
    events=[line for line in lines if line.startswith('RATE_')];need(len(events)==5,'exactly five ordered rate metadata events')
    def take(index,kind,wanted,extra=()):
        tokens=events[index].split(' ');need(tokens[0]=='RATE_'+kind and all(t.count('=')==1 for t in tokens[1:]),'metadata event syntax/order')
        fields=dict(token.split('=')for token in tokens[1:]);need(len(fields)+1==len(tokens)and set(fields)==set(wanted)|set(extra)and all(fields[k]==str(v)for k,v in wanted.items()),'unique exact metadata event fields');return fields
    take(0,'BEGIN',dict(coordinator=0,worker=1,base=base_sha,port=port_sha,fixture=fixture_sha,expected=expected_cases))
    take(1,'WORKER',dict(core=1,priority=0,stack=16384))
    take(2,'ABI',dict(long_bits=32,rate_bits=32,info_bytes=32,alignment=4,rate_offset=8,unsigned=1,overlay=1))
    fields=take(3,'PASS',dict(cases=expected_cases,live=0,bytes=0,core=1),('minimum_free','remaining_stack'))
    values={}
    for name,limit in(('minimum_free',0xffffffff),('remaining_stack',16384)):
        need(re.fullmatch('0|[1-9][0-9]*',fields[name])is not None,'canonical metadata resource value');values[name]=int(fields[name]);need(0<values[name]<=limit,'bounded metadata resource observation')
    take(4,'STOP',dict(status='PASSED'))
    return dict(cases=expected_cases,live=0,bytes=0,coordinator_core=0,worker_core=1,priority=0,configured_stack=16384,protocol_lines=5,rate_source_unsigned=True,long_bits=32,rate_bits=32,info_bytes=32,info_alignment=4,rate_offset=8,**values)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('output','idf','idf-tools','powershell','sdk-python','qemu','rom'):parser.add_argument('--'+name,required=True,type=Path)
    for name in('base-manifest','port-manifest','fixture','qemu'):parser.add_argument('--'+name+'-sha256',required=True)
    parser.add_argument('--expected-cases',required=True,type=int);args=parser.parse_args()
    need(sys.platform=='win32','pinned Windows SDK launcher')
    pins={name:getattr(args,name.replace('-','_')+'_sha256')for name in('base-manifest','port-manifest','fixture','qemu')}
    need(all(re.fullmatch('[0-9a-f]{64}',value)for value in pins.values())and 0<args.expected_cases<=2147483647,'explicit reviewed input identities/count')
    out,sdk,tools,ps,py,qemu,rom=[getattr(args,name).resolve()for name in('output','idf','idf_tools','powershell','sdk_python','qemu','rom')]
    git=Path(shutil.which('git.exe')or shutil.which('git')or'')
    base=source_tree(BASE,'component-manifest.json',pins['base-manifest'],'native-vorbis-xiph-source-v1');validate_base(base)
    port=source_tree(PORT,'port-manifest.json',pins['port-manifest'],'native-vorbis-xiph-resource-port-v1')
    need(port['base_manifest_sha256']==pins['base-manifest']and len(port['files'])==79,'reviewed metadata port and immutable sibling')
    need(sha(ROOT/'tests/native/vorbis_xiph_rate.c')==pins['fixture']and sha(qemu)==pins['qemu'],'reviewed fixture/QEMU identities')
    need(out.is_relative_to(ROOT/'.build')and out!=ROOT/'.build'and not out.exists(),'fresh task-local metadata output')
    need(not any(out==p or out.is_relative_to(p)or p.is_relative_to(out)for p in(BASE,PORT,PROJECT,ROOT/'tests/native',sdk,tools,ps.parent,py.parent,qemu.parent,rom)),'source/runtime/output separation')
    required=[sdk/'export.ps1',sdk/'tools/idf.py',ps,py,qemu,git,*[ROOT/'tests/native'/name for name in HELPERS]]
    need(all(path.is_file()for path in required)and rom.is_dir()and any(rom.glob('esp32*rom*.bin')),'required local tools/helpers/explicit ROM')
    out.mkdir(parents=True)
    report=dict(completed=False,passed=False,metadata_qualified=False,identification_rate_qualified=False,ILP32_runtime_qualified=False,result='NONPASS',target='esp32',sdk_revision=SDK_HEAD,source_sha256=pins,expected_cases=args.expected_cases,
        identification_header_executed=None,comment_header_executed=None,setup_header_executed=False,packet_decoder_executed=False,decoder_executed=False,decoder_scope='audio_packet_decode',dsp_tests_executed=False,full_decoder_qualified=False,dsp_gate_qualified=False,packet_target_gate_qualified=False,wide_amplitude_qualified=False,encoder_rate_qualified=False,convenience_library_qualified=False,production_firmware=False,production_radio_integration=False,physical_device=False,
        commands=[],inputs={},tools={},build_outputs={},whole_module_compiled=False,source_inputs_unchanged=False,exact_source_port_validated=False,component_compile_sources=base['compile_sources'])
    env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0')
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,relative):
        destination=out/'sources'/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(path.read_bytes());report['inputs'][str(path.resolve())]=dict(snapshot=destination.relative_to(out).as_posix(),bytes=destination.stat().st_size,sha256=sha(destination))
    def current():
        need(all(sha(path)==pin['sha256']==sha(out/pin['snapshot'])for path,pin in report['inputs'].items()),'original/frozen metadata inputs unchanged')
        need(all(sha(path)==digest for path,digest in report['tools'].items()),'recorded tool identity unchanged')
        for key in('project_sources','generated_sources'):need(all(sha(out/path)==digest for path,digest in report.get(key,{}).items()),'configured/generated metadata bytes unchanged')
    def run(name,argv,timeout=60):
        argv=list(map(str,argv));row=dict(name=name,argv=argv,cwd=str(out),state='starting',timeout_seconds=timeout,timed_out=False,interrupted=False);report['commands'].append(row);save();so,se=out/(name+'.stdout.log'),out/(name+'.stderr.log');child=None;start=time.monotonic()
        try:
            with so.open('xb')as stdout,se.open('xb')as stderr:
                child=subprocess.Popen(argv,cwd=out,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL,env=env,creationflags=subprocess.CREATE_NO_WINDOW);row.update(pid=child.pid,state='running');save();child.wait(timeout=timeout);row.update(state='complete',exit_status=child.returncode)
        except BaseException as error:row.update(state='failed',error=repr(error),timed_out=isinstance(error,subprocess.TimeoutExpired),interrupted=isinstance(error,KeyboardInterrupt));raise
        finally:
            if child is not None and child.poll()is None:
                row['state']='forced_stop_nonpass'
                try:row['tree_stop_returncode']=subprocess.run(['taskkill.exe','/PID',str(child.pid),'/T','/F'],capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW).returncode
                except Exception as error:row['tree_stop_error']=repr(error)
                finally:
                    if child.poll()is None:child.kill()
                    child.wait(timeout=15)
            row.update(elapsed_seconds=time.monotonic()-start,stdout_sha256=sha(so)if so.is_file()else None,stderr_sha256=sha(se)if se.is_file()else None)
            if child is not None:row['exit_status']=child.poll()
            save()
        need(row['state']=='complete'and row['exit_status']==0,'normal owned metadata command terminal '+name)
        return so.read_text(encoding='utf-8',errors='replace').replace('\r\n','\n')
    save()
    try:
        for path in(py,ps,qemu,git,*sorted(rom.glob('esp32*rom*.bin'))):report['tools'][str(path)]=sha(path)
        need(run('sdk-head',[git,'-c','core.longpaths=true','-C',sdk,'rev-parse','HEAD']).strip()==SDK_HEAD,'pinned SDK revision')
        need(not run('sdk-clean',[git,'-c','core.longpaths=true','-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'SDK clean before metadata build')
        for root,name,document,manifest in((BASE,'native_vorbis_xiph',base,'component-manifest.json'),(PORT,'native_vorbis_xiph_port',port,'port-manifest.json')):
            for member in(*document['files'],manifest):freeze(root/member,Path('components')/name/member)
        for name in HELPERS:freeze(ROOT/'tests/native'/name,Path('helpers')/name)
        freeze(Path(__file__),Path('controller.py'))
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file():freeze(path,Path('project')/path.relative_to(PROJECT))
        shutil.copytree(out/'sources/project',out/'project');shutil.copyfile(out/'sources/project/sdkconfig.esp32.defaults',out/'project/sdkconfig.defaults')
        for name in HELPERS:shutil.copyfile(out/'sources/helpers'/name,out/'project/main'/name)
        report['project_sources']={path.relative_to(out).as_posix():sha(path)for path in(out/'project').rglob('*')if path.is_file()};current()
        run('build',[ps,'-NoProfile','-NonInteractive','-File',out/'sources/project/sdk-build.ps1','-Campaign',out,'-SdkDirectory',sdk,'-ToolsDirectory',tools,'-PythonExecutable',py,'-Target','esp32','-BaseManifestSha256',pins['base-manifest'],'-PortManifestSha256',pins['port-manifest'],'-FixtureSha256',pins['fixture'],'-ExpectedCases',args.expected_cases],1200)
        child=json.loads((out/'sdk-child.json').read_text(encoding='utf-8-sig'));need(type(child['pid'])is int and child['pid']>0 and child['exit_status']==0,'actual SDK child terminal');report['sdk_child']=child
        build=out/'build';description=json.loads((build/'project_description.json').read_bytes());elf=build/description['app_elf'];raw=elf.read_bytes()
        need(elf.resolve().is_relative_to(build)and len(raw)>=52 and raw[:7]==b'\x7fELF\x01\x01\x01'and struct.unpack_from('<H',raw,18)[0]==94,'actual Xtensa ELF');report['elf_machine']=94;(out/'elf-header.bin').write_bytes(raw[:52])
        found=list(build.rglob('PORTING.json'));need(len(found)==1,'one generated metadata-port record');porting_path=found[0]
        porting=validate_generated(porting_path,base,port,out/'sources/components/native_vorbis_xiph',out/'sources/components/native_vorbis_xiph_port',pins['base-manifest'],pins['port-manifest']);generated_root=porting_path.parent
        generated_paths=[generated_root/name for name in porting['files']]+[porting_path];report['generated_sources']={path.relative_to(out).as_posix():sha(path)for path in generated_paths};report['generated_porting']=dict(path=porting_path.relative_to(out).as_posix(),sha256=sha(porting_path),record=porting);report['exact_source_port_validated']=True;current()
        compiler=Path(description['c_compiler']);cxx=compiler.with_name(compiler.name.replace('gcc','g++'));nm=compiler.with_name(compiler.name.replace('gcc','nm'));make=re.findall(r'^CMAKE_MAKE_PROGRAM:FILEPATH=(.+)$',(build/'CMakeCache.txt').read_text(),re.M);need(len(make)==1,'one configured Ninja');ninja=Path(make[0].strip())
        for path in(compiler,cxx,nm,ninja):need(path.is_file(),'actual configured tool');report['tools'][str(path)]=sha(path)
        database=json.loads((build/'compile_commands.json').read_bytes());fixtures=[('fixture',out/'project/main/main.c')]+[(name,out/'project/main'/name)for name in HELPERS if name.endswith('.c')]+[(name,out/'project/main'/name)for name in HEADER_PROBES]
        selected=validate_compile_sources(database,fixtures,porting,generated_root);report['compile_rows']=selected
        need(all(all(flag in row['command']for flag in('-fno-fast-math','-ffp-contract=off','-fstack-usage'))for row in selected.values()),'actual arithmetic/stack compiler flags')
        inject=normalize(out/'project/main/vorbis_xiph_alloc_inject.h').casefold();units=base['compile_sources']
        need(all('-include'in selected[name]['command']and inject in normalize(selected[name]['command']).casefold()for name in units),'allocator injection on all22 library units')
        need(all(inject not in normalize(selected[name]['command']).casefold()for name,_ in fixtures),'allocation hooks do not rewrite their own caller/implementation')
        objects=[normalize(row['output'])for row in selected.values()];need(all((build/name).is_file()for name in objects),'actual compiled objects')
        dependencies=normalize(run('dependencies',[ninja,'-C',build,'-t','deps',*objects])).casefold()
        for unit in porting['compiled_units']:need(normalize(generated_root/unit['compiled']).casefold()in dependencies,'actual selected library dependency')
        for name in PRIVATE_HEADERS:need(normalize(generated_root/'ported'/name).casefold()in dependencies,'actual private interface dependency')
        for name in PUBLIC_HEADERS:need(normalize(generated_root/'ported/include/vorbis'/name).casefold()in dependencies,'actual public overlay dependency')
        need(normalize(generated_root/'base/upstream/libvorbis/include/vorbis/codec.h').casefold()not in dependencies,'original signed public header never shadows overlay')
        need(all(normalize(cxx).casefold()in normalize(selected[name]['command']).casefold()for name in HEADER_PROBES if name.endswith('.cpp')),'actual C++ header probe driver')
        report['public_header_probes']=list(HEADER_PROBES)
        for name in HELPERS:need(normalize(out/'project/main'/name).casefold()in dependencies,'actual frozen metadata helper dependency')
        need(normalize(out/'project/main/layout_probe.h').casefold()in dependencies,'actual C/C++ layout assertion header dependency')
        report['whole_module_compiled']=True
        symbols=run('symbols',[nm,'-n','-S',elf]);need(all(re.search(r'\b'+name+r'$',symbols,re.M)for name in PUBLIC),'linked public/private metadata functions and test hooks')
        # Header dispatch keeps registry references; unused decoder symbols may remain.
        fixture=(out/'project/main/vorbis_xiph_rate.c').read_text()
        need(not re.search(r'\b(?:vorbis_synthesis|vorbis_synthesis_init|vorbis_synthesis_blockin|vorbis_synthesis_trackonly|vorbis_dsp_clear|vorbis_block_init|xiph_dsp_tests|xiph_header_tests)\s*\(',fixture),'actual rate caller has no DSP/audio execution')
        report['decoder_symbols_may_be_retained']=True
        need(not re.search(r'\b(?:__wrap_)?esp_vorbis_dec_\w+$',symbols,re.M),'no vendor decoder symbols');map_file=elf.with_suffix('.map');need(map_file.is_file()and b'libesp_audio_codec.a'not in map_file.read_bytes()and b'libnative_vorbis_xiph.a'not in map_file.read_bytes(),'no vendor or second baseline decoder archive')
        usage=[build/Path(selected[name]['output']).with_suffix('.su')for name in units];need(len(set(usage))==22 and all(path.is_file()for path in usage),'all22 actual library stack records');frames=[]
        for path in usage:
            for line in path.read_text().splitlines():
                fields=line.rsplit('\t',2);need(len(fields)==3 and fields[1].isdigit(),'actual compiler stack row');frames.append(dict(function=fields[0].rsplit(':',1)[-1],bytes=int(fields[1]),qualifier=fields[2],path=path.relative_to(out).as_posix()))
        report['stack_usage']=dict(paths=[path.relative_to(out).as_posix()for path in usage],rows=frames,scope='Compiler own frames, not a full call-tree or production stack bound.')
        recipe=json.loads((build/'flasher_args.json').read_bytes());need(recipe['flash_settings']==dict(flash_mode='dio',flash_size='4MB',flash_freq='40m'),'isolated metadata flash profile');flash_files={int(offset,0):(build/name).resolve()for offset,name in recipe['flash_files'].items()}
        need(set(flash_files)=={4096,32768,65536}and all(path.is_relative_to(build)for path in flash_files.values()),'contained metadata boot/image recipe');flash=out/'qemu-flash.bin';argv=[py,'-m','esptool','--chip','esp32','merge-bin','--output',flash,'--flash-mode','dio','--flash-size','4MB','--flash-freq','40m']
        for offset,path in sorted(flash_files.items()):argv+=[hex(offset),path]
        run('merge',argv+['--pad-to-size','4MB']);config=(out/'sdkconfig').read_text()
        need(not re.search(r'^CONFIG_FREERTOS_UNICORE=y$',config,re.M)and re.search(r'^CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ=240$',config,re.M),'dual-core240MHz metadata profile')
        need(all(re.search(r'^'+name+'=y$',config,re.M)for name in('CONFIG_ESP_TASK_WDT_EN','CONFIG_ESP_TASK_WDT_INIT','CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0','CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1')),'task watchdog and both idle checks stay enabled')
        current();log=run('qemu',[qemu,'-audiodev','none,id=quiet','-M','esp32,audiodev=quiet','-smp','2','-L',rom,'-display','none','-monitor','none','-serial','stdio','-no-reboot','-snapshot','-nic','none','-drive','file='+str(flash)+',if=mtd,format=raw'],120)
        full=log+'\n'+(out/'qemu.stderr.log').read_text(errors='replace');report['observed']=validate_log(full,pins['base-manifest'],pins['port-manifest'],pins['fixture'],args.expected_cases)
        need(run('sdk-head-after',[git,'-c','core.longpaths=true','-C',sdk,'rev-parse','HEAD']).strip()==SDK_HEAD,'SDK revision after metadata gate')
        need(not run('sdk-clean-after',[git,'-c','core.longpaths=true','-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'SDK clean after metadata gate')
        files=[elf,map_file,flash,*usage,*generated_paths,out/'sdkconfig',out/'elf-header.bin',out/'sdk-child.json',out/'sdk-build.stdout.log',out/'sdk-build.stderr.log',*flash_files.values()]+[build/name for name in('compile_commands.json','project_description.json','flasher_args.json','CMakeCache.txt','config/sdkconfig.h','build.ninja','CMakeFiles/rules.ninja')]
        report['build_outputs']={path.relative_to(out).as_posix():sha(path)for path in files};report['build_warning_lines']=[line for name in('sdk-build.stdout.log','sdk-build.stderr.log')for line in(out/name).read_text(errors='replace').splitlines()if re.search(r'\bwarning:',line)]
        current();need(all(sha(out/name)==digest for name,digest in report['build_outputs'].items()),'actual metadata build/capture bytes unchanged')
        report.update(completed=True,passed=True,metadata_qualified=True,identification_rate_qualified=True,ILP32_runtime_qualified=True,identification_header_executed=True,comment_header_executed=True,source_inputs_unchanged=True,result='RATE_METADATA_ONLY_QUALIFIED',limitations='Only pinned unsigned-rate identification/comment metadata, granule_time and finite C/C++ header probes qualify. No setup/DSP/audio execution, deferred packet/DSP/amplitude gate, encoder/convenience rate, PCM, production integration or physical performance qualification. No full external tool/SDK dependency closure.')
        save();print(json.dumps(dict(completed=True,passed=True,metadata_qualified=True,ILP32_runtime_qualified=True,cases=args.expected_cases,decoder_executed=False,dsp_gate_qualified=False)));return 0
    except BaseException as error:report.update(completed=False,passed=False,metadata_qualified=False,result='NONPASS',error=repr(error));save();raise

if __name__=='__main__':sys.exit(main())
