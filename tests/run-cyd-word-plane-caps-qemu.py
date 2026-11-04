"""Isolated actual SDK/QEMU public-capability word-storage observation.

No decoder, private heap state, production memory-fit claim, hardware or network.
The shared helper must be separately qualified and explicitly released first.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
sys.dont_write_bytecode=True

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent.parent if ROOT.parent.name=='.worktree' else ROOT
TARGET=ROOT/'tests/target/cyd_word_plane_caps_qemu'
HEADER=ROOT/'idf/components/native_stream/include/pcm_word_plane.h'
HEADER_SHA='8b3c80edffd3298e2ccd1816fe20aa1cf6cbf30c367aad7035448f35ce868b6b'
BASE=ROOT/'tests/run-cyd-family1-playback-task-qemu.py'


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


base=module('reviewed_current_process_capture_utilities',BASE)
need=base.need;sha=base.sha;write_json=base.write_json


def identity(path):return dict(bytes=path.stat().st_size,sha256=sha(path))


def fields(line):
    tag,*parts=line.split();pairs=[part.split('=',1) for part in parts]
    need(pairs and all(len(part)==2 for part in pairs) and len({p[0] for p in pairs})==len(pairs),'complete unique public observation fields')
    words={'sdk','kind','phase'};row={}
    for key,value in pairs:
        if key in words:row[key]=value
        else:need(re.fullmatch('[0-9]+',value),'strict actual public integer field');row[key]=int(value)
    return tag,row


def parse(log):
    need(not re.search(r'CYD_WORD_FAILURE|Guru Meditation|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack (?:overflow|smashing)',log,re.I),'no real access/resource/runtime assertion failure')
    lines=[line for line in log.replace('\r\n','\n').splitlines() if line.startswith('CYD_WORD_')]
    rows=[fields(line) for line in lines]
    def select(tag):return [row for found,row in rows if found=='CYD_WORD_'+tag]
    known={'BOOT','LIMITS','HEAP','ALLOC','POINTER','ACCESS','FREE','CASE','COMPLETE'}
    need(all(tag.removeprefix('CYD_WORD_') in known for tag,_ in rows),'only declared complete public records')
    need(select('BOOT')==[dict(sdk='v6.0.2',public_caps=1,physical_hardware=0,decoder=0,private_heap=0)],'isolated actual pinned SDK boot')
    limits=select('LIMITS');need(len(limits)==1,'actual public SoC/capability definitions');limits=limits[0]
    need({k:limits[k] for k in ('iram_low','pure_iram_high','iram_high','diram_iram_low','diram_iram_high','diram_dram_low','diram_dram_high','dram_low','dram_high')}==dict(
        iram_low=0x40080000,pure_iram_high=0x400a0000,iram_high=0x400aa000,diram_iram_low=0x400a0000,diram_iram_high=0x400c0000,
        diram_dram_low=0x3ffe0000,diram_dram_high=0x40000000,dram_low=0x3ffae000,dram_high=0x40000000),'pinned classic ESP32 public regions')
    need({k:limits[k] for k in ('cap_internal','cap32','cap8','cap_exec')}==dict(cap_internal=2048,cap32=2,cap8=4,cap_exec=1),'actual public capability bits')
    boot=[]
    for match in re.finditer(r'heap_init: At ([0-9A-Fa-f]{8}) len ([0-9A-Fa-f]{8}) .*: (DRAM|D/IRAM|IRAM)\r?$',log,re.M):
        start=int(match[1],16);size=int(match[2],16);boot.append(dict(start=start,bytes=size,end=start+size,kind=match[3]))
    pure_extent=sum(max(0,min(row['end'],limits['pure_iram_high'])-max(row['start'],limits['iram_low'])) for row in boot if row['kind']=='IRAM')
    need(boot and pure_extent>0,'probe initial pure-IRAM boot extent is observed separately from native06 and current free')
    cases=select('CASE');need([row['kind'] for row in cases]==['WORDS32','EXEC32'],'both separately labelled capability cases')
    observations=[]
    for case in cases:
        kind=case['kind'];caps=limits['cap_internal']|limits['cap32']|(limits['cap_exec'] if kind=='EXEC32' else 0)
        allocated=case['allocated'];attempted=case['attempted'];refused=case['refused']
        need(0<allocated<=8 and refused in (0,1) and attempted==allocated+refused and (attempted==8 or refused==1) and
             case['bytes_per_plane']==11520 and case['byte_control']==23040 and case['exact_cleanup']==1 and
             case['extra_RAM_inferred']==case['application_qualified']==0,'honest allocation/access scope; no extra-memory/application inference')
        alloc=[row for row in select('ALLOC') if row['kind']==kind];access=[row for row in select('ACCESS') if row['kind']==kind];freed=[row for row in select('FREE') if row['kind']==kind]
        need(len(alloc)==attempted and [row['slot'] for row in alloc]==list(range(attempted)) and all(row['caps']==caps and row['bytes']==11520 for row in alloc),'every real public plane allocation request retained')
        need([row['success'] for row in alloc]==[1]*allocated+[0]*refused and all(bool(row['pointer'])==bool(row['success']) for row in alloc),'actual successful and refused allocation results')
        pointers=[row for row in select('POINTER') if row['kind']==kind]
        need(len(pointers)==len(access)==len(freed)==allocated,'every successful plane classified/accessed/freed once')
        physical=[]
        for index,(request,pointer,checked,closed) in enumerate(zip(alloc,pointers,access,freed)):
            p=pointer['pointer'];size=pointer['bytes'];last=p+size-4
            need(pointer['slot']==checked['slot']==closed['slot']==index and p==request['pointer']==closed['pointer'] and
                 pointer['caps']==caps and pointer['internal']==1 and not p%4 and size==11520 and pointer['alias_dereferenced']==0 and closed['real_returned']==1,'original aligned public word-plane ownership and no alias access')
            pure=limits['iram_low']<=p and p+size<=limits['pure_iram_high']
            diram_i=limits['diram_iram_low']<=p and p+size<=limits['diram_iram_high'];diram_d=limits['diram_dram_low']<=p and p+size<=limits['diram_dram_high']
            dram=limits['dram_low']<=p<limits['dram_high'];iram=limits['iram_low']<=p<limits['iram_high']
            need(pointer['pure_iram']==pure and pointer['diram_iram']==diram_i and pointer['diram_dram']==diram_d and pointer['in_dram']==dram and pointer['in_iram']==iram and pointer['byte_accessible']==dram,
                 'actual pointer classes match independent public address definitions')
            # SDK6.0.2's public address predicate stops at SOC_IRAM_HIGH.
            # EXEC-capable heap aliases can extend to SOC_DIRAM_IRAM_HIGH;
            # preserve the actual predicate result rather than infer it from
            # the allocation request. No instruction execution is tested.
            need(pointer['executable']==iram,'actual public executable-address query matches its pinned SDK windows')
            if diram_i:
                first_alias=limits['diram_dram_high']-(p-limits['diram_iram_low'])-4;last_alias=limits['diram_dram_high']-(last-limits['diram_iram_low'])-4
                canonical=min(first_alias,last_alias)
            elif diram_d:
                first_alias=limits['diram_iram_low']+limits['diram_dram_high']-p-4;last_alias=limits['diram_iram_low']+limits['diram_dram_high']-last-4;canonical=p
            else:first_alias=last_alias=0;canonical=p
            need((pure or dram or diram_i) and pointer['alias_first_word']==first_alias and pointer['alias_last_word']==last_alias,'D/IRAM aliases are independently identified, never counted as extra physical RAM')
            need(all(canonical+size<=left or canonical>=right for left,right in physical),'no two live planes overlap in physical address space');physical.append((canonical,canonical+size))
            need(checked==dict(kind=kind,slot=index,samples=5760,clear=1,whole_pattern=1,odd_rmw=1,volatile32_only=1),'complete actual word helper clear/store/load/RMW access')
        heaps=[row for row in select('HEAP') if row['kind']==kind]
        expected=[('BEFORE',0),('SCRATCH',0)]+[(phase,index) for index in range(attempted) for phase in ('ALLOC_BEFORE','ALLOC_AFTER')]+[('HELD',0),('CLEANUP',0)]
        need([(row['phase'],row['slot']) for row in heaps]==expected,'public resources measured around every actual allocation and complete cleanup')
        keys=('free8','largest8','free32','largest32','free_exec','largest_exec')
        need(all(row['integrity']==1 and 0<=row['largest8']<=row['free8'] and 0<=row['largest32']<=row['free32'] and 0<=row['largest_exec']<=row['free_exec'] for row in heaps),'actual public capability resources and heap integrity')
        need(all(heaps[0][key]==heaps[-1][key] for key in keys),'all original public free/largest values restored after real cleanup')
        observations.append(dict(case=case,pointers=pointers,heap=heaps,pure_iram_requested_bytes=sum(row['bytes'] for row in pointers if row['pure_iram']),
            diram_alias_requested_bytes=sum(row['bytes'] for row in pointers if row['diram_dram'] or row['diram_iram'])))
    controls=select('POINTER');controls=[row for row in controls if row['kind']=='DRAM_CONTROL']
    need(len(controls)==2 and all(row['bytes']==23040 and row['caps']==limits['cap_internal']|limits['cap8'] and
         row['in_dram']==row['byte_accessible']==row['internal']==1 and limits['dram_low']<=row['pointer'] and row['pointer']+row['bytes']<=limits['dram_high'] for row in controls),
         'separate control workspace remains byte-capable DRAM')
    need(select('COMPLETE')==[dict(cases=2,word_plane_bytes=11520,plane_slots=8,diagnostic_yield_between_planes=1,all_planes_byte_or_FP_access=0,hardware=0,application_memory_qualified=0,integrity=1)] and rows[-1][0]=='CYD_WORD_COMPLETE','one complete isolated public-capability access observation')
    return dict(cases=observations,limits=limits,DRAM_controls=controls,probe_initial_boot_regions=boot,probe_initial_pure_IRAM_extent=pure_extent,
        initial_extent_is_not_current_free=True,full_application_memory_qualified=False,extra_RAM_inferred=False)


class Campaign:
    save=base.Campaign.save;bind_runtime=base.Campaign.bind_runtime;freeze=base.Campaign.freeze
    run_command=base.Campaign.run_command;verify_inputs=base.Campaign.verify_inputs

    def __init__(self,args):
        self.args=args;self.out=args.output;self.sources={};self.runtime={};self.runtime_paths={};self.artifacts={}
        self.environment=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONNOUSERSITE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
        self.report=dict(passed=False,completed=False,commands=[],target_executed=False,physical_device=False,external_network=False,
            private_heap_state=False,decoder=False,production_firmware=False,application_memory_qualified=False,extra_RAM_inferred=False,
            historical_comparison_requested=args.historical_capture is not None)

    def freeze_sources(self):
        need(sha(HEADER)==HEADER_SHA,'exact separately qualified word helper')
        for path in TARGET.rglob('*'):
            if path.is_file():self.freeze(path,Path('sources/harness')/path.relative_to(TARGET),'new isolated public word-capability probe')
        self.freeze(HEADER,Path('sources/harness/project/main/pcm_word_plane.h'),'exact shared qualified integer word helper')
        self.freeze(Path(__file__),Path('sources/controller.py'),'new isolated controller')
        self.freeze(BASE,Path('sources/current-process-capture-utilities.py'),'current reviewed process/hash/snapshot utilities; no old capture executed')
        for name in ('components/heap/port/esp32/memory_layout.c','components/heap/heap_caps.c','components/heap/include/esp_heap_caps.h',
                     'components/heap/heap_caps_base.c','components/soc/esp32/include/soc/soc.h',
                     'components/esp_hw_support/include/esp_memory_utils.h','components/esp_hw_support/esp_memory_utils.c'):
            self.freeze(self.args.idf/name,Path('sources/public-sdk')/name,'pinned primary public memory definitions/allocator source')
        if self.args.historical_capture is not None:
            historical=self.args.historical_capture
            log=historical/'qemu.stdout.log';mapping=historical/'build/cyd_family1_playback_task_qemu.map'
            for path in (log,mapping,historical/'report.json'):self.bind_runtime(path)
            raw=log.read_bytes();boot=[];at=0
            for line in raw.splitlines(keepends=True):
                if b'heap_init:' in line:boot.append(dict(offset=at,bytes=len(line),sha256=hashlib.sha256(line).hexdigest(),line=line.decode().rstrip('\r\n')))
                at+=len(line)
            pure=[row for row in boot if re.search(r'At 4008C49C len 00013B64 .*: IRAM$',row['line'])]
            need(len(pure)==1 and 0x4008c49c+0x13b64==0x400a0000,'native06 historical pure-IRAM initial region extent80740, not free')
            text=mapping.read_text();need(re.search(r'0x4008c49c\s+_iram_end\s*=',text) and re.search(r'iram0_0_seg\s+0x40080000\s+0x00020000',text),'exact historical native06 map confirms pure-IRAM region boundary')
            self.report['historical_native06']=dict(whole_console=dict(path=log.relative_to(ROOT).as_posix(),**identity(log),publication='omit whole PCM-bearing console'),
                whole_map=dict(path=mapping.relative_to(ROOT).as_posix(),**identity(mapping)),boot_records=boot,pure_iram_initial_extent=80740,
                initial_allocator_region_not_current_free=True,does_not_describe_minimal_probe_capacity=True)
        write_json(self.out/'source-manifest.json',self.sources)

    def sdk_identity(self,suffix=''):
        git=[self.args.git,'-c','core.longpaths=true','-C',self.args.idf]
        need(self.run_command('sdk-head'+suffix,git+['rev-parse','HEAD']).strip()==base.SDK_COMMIT,'pinned primary SDK revision')
        need(not self.run_command('sdk-clean'+suffix,git+['status','--porcelain','--untracked-files=no']).strip(),'unchanged installed primary SDK')

    def qualify_build(self):
        build=self.out/'build';desc=json.loads((build/'project_description.json').read_bytes());config=json.loads((build/'config/sdkconfig.json').read_bytes())
        need(desc['target']=='esp32' and Path(desc['idf_path']).resolve()==self.args.idf,'actual installed classic ESP32 SDK target')
        for key in ('HEAP_POISONING_LIGHT','FREERTOS_CHECK_STACKOVERFLOW_CANARY','COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE','ESP_TASK_WDT_EN','ESP_TASK_WDT_INIT','ESP_TASK_WDT_PANIC','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1'):
            need(config.get(key) is True,'actual access diagnostic safeguards: '+key)
        need(not any(config.get(key,False) for key in ('FREERTOS_UNICORE','SPIRAM','ESP32_IRAM_AS_8BIT_ACCESSIBLE_MEMORY','ESP_SYSTEM_ALLOW_RTC_FAST_MEM_AS_HEAP')) and config['ESP_TASK_WDT_TIMEOUT_S']==20,'no special byte-access, external-memory or watchdog alteration')
        commands=json.loads((build/'compile_commands.json').read_bytes());main=(self.out/'sources/harness/project/main/main.c').resolve();selected=[row for row in commands if Path(row['file']).resolve()==main]
        need(len(selected)==1,'whole actual new public-capability TU')
        compiler=Path(desc['c_compiler']);ninja=Path(re.search(r'^CMAKE_MAKE_PROGRAM:[A-Z_]+=(.+)$',(build/'CMakeCache.txt').read_text(),re.M).group(1).strip())
        objdump=compiler.with_name(compiler.name.replace('gcc','objdump'))
        for path in (compiler,ninja,objdump):self.bind_runtime(path)
        row=selected[0];deps=self.run_command('compiler-deps',[ninja,'-C',build,'-t','deps',row['output'].replace('\\','/')]);need('(VALID)' in deps,'actual GCC/Ninja dependency record')
        actual=[]
        for line in deps.splitlines():
            if not line.startswith('    '):continue
            path=Path(line.strip());path=path.resolve() if path.is_absolute() else (build/path).resolve();need(path.is_file(),'every actual compiler dependency exists')
            self.freeze(path,Path('sources/compiler-dependencies')/hashlib.sha256(str(path).encode()).hexdigest()[:16]/path.name,'actual public SDK/compiler dependency');actual.append(str(path))
        need({'pcm_word_plane.h','esp_heap_caps.h','esp_memory_utils.h','soc.h'}<={Path(path).name for path in actual},'actual qualified helper/public-capability definitions consumed')
        write_json(self.out/'actual-compiler-closure.json',dict(translation_unit=row,actual_dependencies=actual));write_json(self.out/'source-manifest.json',self.sources)
        obj=Path(row['output']);obj=obj if obj.is_absolute() else build/obj
        assembly=self.run_command('word-object-disassembly',[objdump,'-d',obj]);functions={}
        for name in ('probe_word_clear','probe_word_store','probe_word_load'):
            found=re.search(r'^[0-9a-f]+ <'+name+r'>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',assembly,re.M|re.S);need(found is not None,'actual linked-object named helper entrypoint')
            body=found.group(1);need(not re.search(r'\b(?:l8ui|l16ui|l16si|s8i|s16i|lsi|ssi|l32f|s32f|float\.s|ufloat\.s)\b',body),'word helper has no byte/halfword/FP memory instruction')
            need(('l32i' in body or name=='probe_word_clear') and ('s32i' in body or name=='probe_word_load'),'actual helper memory operations remain integer32');functions[name]=body
        self.report['word_helper_assembly']=dict(functions=functions,byte_halfword_FP_access=False)
        own_map=build/'cyd_word_plane_caps_qemu.map';found=re.search(r'^\s*(0x[0-9a-f]+)\s+_iram_end\s*=',own_map.read_text(),re.M)
        need(found is not None,'actual new probe map exposes its public IRAM image extent')
        iram_end=int(found[1],16);self.report['probe_map']=dict(iram_end=iram_end,pure_iram_initial_extent=max(0,0x400a0000-max(0x40080000,iram_end)))
        recipe=json.loads((build/'flasher_args.json').read_bytes());need(recipe['extra_esptool_args']['chip']=='esp32','actual classic ESP32 image recipe')
        files={int(offset,0):(build/name).resolve() for offset,name in recipe['flash_files'].items()};need(set(files)=={0x1000,0x8000,0x10000},'isolated bootloader/partition/app image')
        flash=self.out/'qemu-flash.bin';argv=[self.args.idf_python,'-m','esptool','--chip','esp32','merge-bin','--output',flash,'--flash-mode','dio','--flash-size','4MB','--flash-freq','40m']
        for offset,path in sorted(files.items()):argv.extend((hex(offset),path))
        self.run_command('merge',argv+['--pad-to-size','4MB']);body=flash.read_bytes();need(len(body)==4194304 and all(body[offset:offset+path.stat().st_size]==path.read_bytes() for offset,path in files.items()),'exact immutable diagnostic flash')
        child=json.loads((self.out/'sdk-child.json').read_text('utf-8-sig'));need(child['pid']>0 and child['exit_status']==0,'real SDK child authoritative terminal zero')
        artifacts=[flash,obj,build/'cyd_word_plane_caps_qemu.elf',build/'cyd_word_plane_caps_qemu.map',*files.values(),self.out/'sdkconfig',self.out/'sdk-child.json',build/'compile_commands.json',self.out/'source-manifest.json',self.out/'actual-compiler-closure.json']
        self.artifacts.update({path.relative_to(self.out).as_posix():sha(path) for path in artifacts})
        write_json(self.out/'execution-bundle.json',dict(sources=self.sources,runtime=self.runtime,artifacts=self.artifacts,sdk_commit=base.SDK_COMMIT,scope=__doc__))
        self.artifacts['execution-bundle.json']=sha(self.out/'execution-bundle.json');need(self.verify_inputs(),'all inputs/images immutable before access probe');return flash

    def execute(self):
        self.out.mkdir(parents=True);self.save()
        try:
            self.freeze_sources()
            for path in (self.args.idf_python,self.args.qemu,self.args.git,self.args.powershell,Path(sys.executable).resolve(),self.args.rom/'esp32-v3-rom.bin',self.args.rom/'esp32-v3-rom-app.bin',self.args.idf/'tools/tools.json'):self.bind_runtime(path)
            self.sdk_identity();print('Building isolated public word-storage capability probe',flush=True)
            self.run_command('build',[self.args.powershell,'-NoProfile','-NonInteractive','-File',self.out/'sources/harness/sdk-build.ps1','-OutputDirectory',self.out,'-IdfDirectory',self.args.idf,'-IdfToolsDirectory',self.args.idf_tools,'-IdfPythonExecutable',self.args.idf_python],1200)
            flash=self.qualify_build();print('Starting real public-capability word-storage access probe',flush=True)
            log=self.run_command('qemu',[self.args.qemu,'-audiodev','none,id=quiet','-M','esp32,audiodev=quiet','-smp','2','-L',self.args.rom,'-display','none','-monitor','none','-serial','stdio','-no-reboot','-snapshot','-nic','none','-drive','file='+str(flash).replace(',',',,')+',if=mtd,format=raw'],120)
            self.report['measurements']=parse(log+'\n'+(self.out/'qemu.stderr.log').read_text(errors='replace'))
            need(self.report['measurements']['probe_initial_pure_IRAM_extent']==self.report['probe_map']['pure_iram_initial_extent'],'actual probe boot and its own map agree; native06 capacity is a separate historical image')
            self.sdk_identity('-after');need(self.verify_inputs(),'all selected helper/source/runtime/image inputs unchanged')
            self.report.update(passed=True,completed=True);print('PASS isolated actual word-storage access; full application fit remains unqualified',flush=True)
        except BaseException as error:
            self.report.update(failure_type=type(error).__name__,failure=str(error));print(json.dumps(dict(passed=False,failure=str(error))),file=sys.stderr)
        finally:
            if not self.verify_inputs():self.report['passed']=False
            self.save()
        return 0 if self.report['passed'] else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--preflight-only',action='store_true')
    parser.add_argument('--historical-capture',type=Path,help='Optional retained native06 capture for the exact 80740-byte historical boot/map comparison; not required for the probe')
    args=parser.parse_args();args.output=args.output.resolve();need(sys.platform=='win32' and args.output.is_relative_to(ROOT/'.build') and not args.output.exists(),'fresh isolated Windows capture')
    if args.historical_capture is not None:
        args.historical_capture=args.historical_capture.resolve()
        history=args.historical_capture
        need(history.is_relative_to(ROOT/'.build') and history.is_dir() and
             not history.is_relative_to(args.output) and not args.output.is_relative_to(history) and
             all((history/name).is_file() for name in ('qemu.stdout.log','report.json','build/cyd_family1_playback_task_qemu.map')),
             'optional history requires a complete distinct local native06 capture')
    args.idf=REPO/'.idf/v6.0.2';args.idf_tools=REPO/'.idf/tools-v6.0.2';args.idf_python=args.idf_tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    args.qemu=ROOT/'.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe';args.rom=Path('C:/Work/QEMU-ESP32/pc-bios');args.git=Path(shutil.which('git.exe') or shutil.which('git') or '');args.powershell=Path(shutil.which('pwsh.exe') or '')
    need(re.fullmatch('[a-f0-9]{64}',HEADER_SHA) and sha(HEADER)==HEADER_SHA,'helper qualification/source release required before any native action')
    need(all(path.is_file() for path in (args.idf/'tools/idf.py',args.idf/'export.ps1',args.idf_python,args.qemu,args.git,args.powershell,args.rom/'esp32-v3-rom.bin',args.rom/'esp32-v3-rom-app.bin')),'actual installed public SDK and isolated emulator')
    need(sha(args.qemu)==base.QEMU_SHA,'pinned known QEMU executable')
    if args.preflight_only:print(json.dumps(dict(preflight=True,output_created=False,SDK_started=False,QEMU_started=False,helper_released=True,historical_comparison_requested=args.historical_capture is not None)));return 0
    return Campaign(args).execute()


if __name__=='__main__':sys.dont_write_bytecode=True;raise SystemExit(main())
