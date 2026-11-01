"""Observe independent documented public Opus handles on creator-qualified packets.

No Ogg decoder, production adaptation, private state or forced results. Original
AppendixB segments and independently validated common-framing controls are
separate fresh cases. Full PCM remains local; numeric comparison adds no new
tolerance or universal conformance claim.
"""
import argparse
from array import array
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import struct
import sys
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent.parent if ROOT.parent.name=='.worktree' else ROOT
PROJECT=ROOT/'tests/target/cyd_opus_multistream_public_qemu'
BASE=ROOT/'tests/run-cyd-ogg-playback-qemu.py'
BASE_SHA='6c1ffd611c7c10982d8c3ad6eb2b633c26139355d1996096ec9d2b4a0b120dfd'
FAMILY=ROOT/'tests/run-cyd-opus-family1-qemu.py'
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
need(sha(BASE)==BASE_SHA,'pinned reviewed native runtime/closure helper')
spec=importlib.util.spec_from_file_location('public_multi_native_helper',BASE);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);common=base.common
# Reuse the frozen reviewed numeric data comparison only; its SDK main is not run.
family_pin=json.loads((ROOT/'tests/results/cyd-opus-family1-20261101/manifest.json').read_bytes())['canonical_source_sha256']['tests/run-cyd-opus-family1-qemu.py']
need(sha(FAMILY)==family_pin,'frozen reviewed PCM data comparison')
spec=importlib.util.spec_from_file_location('public_multi_pcm_data',FAMILY);family=importlib.util.module_from_spec(spec);spec.loader.exec_module(family)


def parse_log(text,reference,directory,out):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack overflow',text,re.I),'no native panic/assertion/watchdog/heap failure')
    lines=[v for v in text.replace('\r\n','\n').splitlines() if v.startswith('MS_')]
    need(lines and lines[0]=='MS_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 fixtures=3 modes=2 public_raw_handles=1','actual public raw-handle worker')
    cases=[];allocs={};opens={};calls={};closes={};streams={};pcm={}
    for line in lines[1:-1]:
        parts=line.split();tag=parts[0];values=dict(p.split('=',1) for p in parts[1:]);need(len(values)==len(parts)-1,'unique complete native fields')
        if tag=='MS_PCM':
            need(set(values)=={'id','stream','offset','bytes','hex'},'exact PCM record');key=(int(values['id']),int(values['stream']))
            body=pcm.setdefault(key,bytearray());data=bytes.fromhex(values['hex']);need(len(body)==int(values['offset']) and len(data)==int(values['bytes']) and 0<len(data)<=128,'continuous full native PCM bytes')
            body.extend(data);continue
        row={k:int(v) for k,v in values.items()};id=row['id']
        if tag=='MS_CASE':cases.append(row);continue
        need(tag in ('MS_ALLOC','MS_OPEN','MS_CALL','MS_CLOSE','MS_STREAM'),'known actual public event')
        lookup={'MS_ALLOC':allocs,'MS_OPEN':opens,'MS_CALL':calls,'MS_CLOSE':closes,'MS_STREAM':streams}[tag];lookup.setdefault(id,[]).append(row)
    need(len(cases)==6 and [v['id'] for v in cases]==list(range(6)),'all complete fresh fixture/framing cases')
    measured=[]
    for id,row in enumerate(cases):
        channels=(3,6,8)[id//2];mode=id%2;name='channels'+str(channels);fixture=reference['fixtures'][name];info=fixture['framing'];n=info['streams'];m=info['coupled']
        need((row['encoded_channels'],row['streams'],row['coupled'],row['mode'])==(channels,n,m,mode),'exact creator-valid selected layouts and framing modes')
        own=streams.get(id,[]);own_calls=calls.get(id,[]);own_opens=opens.get(id,[]);own_closes=closes.get(id,[])
        need([v['stream'] for v in own]==list(range(n)) and row['opens']==sum(v['result']==0 for v in own_opens) and
            row['close_calls']==len(own_closes) and row['close_errors']==sum(v['result']!=0 for v in own_closes),'genuine stream/handle/close inventory')
        need(row['core']==1 and row['priority']==3 and 0<row['stack_free']<=16384 and row['heap_min']>0 and row['before']>0 and row['after']>0,'actual worker and resources')
        need([v['stream'] for v in own_opens]==list(range(len(own_opens))) and all(v['channels']==(2 if v['stream']<m else 1) and
            v['rate']==48000 and v['self_delimited']==int(mode==0 and v['stream']+1<n) for v in own_opens),'documented explicit public decoder config')
        result=dict(measurements=row,allocations=allocs.get(id,[]),open_events=own_opens,close_events=own_closes,public_calls=own_calls,streams=[])
        complete=not row['driver_status'] and bool(row['geometry_valid']);decoded=[]
        for s,summary in enumerate(own):
            width=2 if s<m else 1;selected=[v for v in own_calls if v['stream']==s];close=[v for v in own_closes if v['stream']==s]
            data=bytes(pcm.get((id,s),b''));need(summary['calls']==len(selected) and [v['call'] for v in selected]==list(range(1,len(selected)+1)) and
                summary['configured_channels']==width and summary['consumed']==sum(v['consumed'] for v in selected) and
                summary['pcm_bytes']==len(data)==sum(v['decoded'] for v in selected) and summary['outputs']==sum(v['decoded']>0 for v in selected) and
                summary['closes']==len(close) and summary['process_result_known']==int(bool(selected)),'actual complete per-stream consumption/output/cleanup accounting')
            if selected:need(summary['last_result']==selected[-1]['result'],'last process status is actual')
            if close:need(summary['close_result']==close[-1]['result'],'last close status is actual')
            need(all(v['consumed']<=v['len'] and v['decoded']<=v['capacity'] and 0<=v['packet']<11 for v in selected),'public byte/capacity/packet bounds')
            if any(v['stream']==s and v['result']==0 for v in own_opens):
                expected=sum(p['streams'][s]['common_bytes' if mode else 'original_bytes'] for p in info['packets'])
                need(summary['expected_input']==expected,'exact selected original/common input bytes')
            frames=sum(v['decoded']//(width*2) for v in selected if v['decoded'] and v['rate']==48000 and v['channels']==width and v['bits']==16 and v['decoded']%(width*2)==0)
            need(summary['frames']==frames,'frame counts follow actual reported layout')
            stream_complete=(summary['frames']==10560 and summary['consumed']==summary['expected_input'] and summary['outputs']==11 and summary['closes']==1 and summary['close_result']==0)
            complete=complete and stream_complete;path=out/f'case{id}-stream{s}.pcm';path.write_bytes(data)
            item=dict(measurements=summary,full_pcm=dict(path=path.name,bytes=len(data),sha256=sha(path),local_only=True))
            if data:
                expected=(directory/(name+f'-stream{s}.pcm')).read_bytes()
                if len(data)<=len(expected):item['comparison']=dict(complete_geometry=len(data)==len(expected),**family.compare_pcm(data,expected[:len(data)]))
            result['streams'].append(item);samples=array('h');samples.frombytes(data);decoded.append(samples)
        need(row['complete']==int(complete),'native completion follows real per-stream frames/input/close, never a forced ACK')
        if complete:
            mapped=array('h');positions=[]
            for index in info['mapping']:
                positions.append((index//2,index%2) if index<2*m else (index-m,0))
            for frame in range(10560):
                for s,ch in positions:mapped.append(decoded[s][frame*(2 if s<m else 1)+ch])
            body=mapped.tobytes();path=out/f'case{id}-mapped.pcm';path.write_bytes(body)
            result['full_mapped_pcm']=dict(path=path.name,bytes=len(body),sha256=sha(path),local_only=True)
            result['mapped_comparison']=family.compare_pcm(body,(directory/(name+'-mapped.pcm')).read_bytes())
        result['public_composition_complete_for_this_fixture']=bool(complete);measured.append(result)
    final=lines[-1].split();need(final[0]=='MS_COMPLETE','actual terminal record');terminal={k:int(v) for k,v in (p.split('=',1) for p in final[1:])}
    need(terminal['cases']==6 and terminal['core']==1 and terminal['priority']==3 and terminal['heap_integrity']==1 and
        terminal['retained']==terminal['heap_before']-terminal['heap_after'] and 0<terminal['stack_free']<=16384,'honest final heap/stack/integrity')
    return dict(cases=measured,complete=terminal,diagnostic_completed=True,production_integration=False,mandatory_family1_playback_complete=False,
        universal_conformance_claim=False,new_tolerance_applied=False,private_abi_used=False)


class Campaign(base.Campaign):
    def __init__(self,args,reference):
        super().__init__(args);self.reference=reference
        self.report.update(actual_wrapper=False,actual_audio_service_tu=False,public_raw_handles=True,production_integration=False,mandatory_family1_playback_complete=False)
    def freeze_sources(self):
        for p in sorted(PROJECT.rglob('*')):
            if p.is_file():self.freeze(p,Path('project')/p.relative_to(PROJECT),'new public raw-handle diagnostic')
        for p in (BASE,base.COMMON,FAMILY,Path(__file__)):
            self.freeze(p,Path('sources/controllers')/p.name,'reviewed frozen data/runtime controller')
        for p in sorted((self.args.reference/'sources').rglob('*')):
            if p.is_file():self.freeze(p,Path('sources/reference-sources')/p.relative_to(self.args.reference/'sources'),'creator-qualified framing input')
        self.freeze(self.args.reference/'report.json',Path('sources/reference/report.json'),'actual creator framing oracle report')
        table=[];bodies=[];offset=112
        for channels in (3,6,8):
            name='channels'+str(channels);fixture=self.reference['fixtures'][name];info=fixture['framing'];p=self.args.reference/fixture['transport']['path']
            need(sha(p)==fixture['transport']['sha256'],'exact creator-qualified native packet transport');body=p.read_bytes()
            self.freeze(p,Path('sources/reference')/p.name,'complete independently qualified packet transport')
            table.append(struct.pack('<8I',channels,offset,len(body),info['streams'],info['coupled'],11,10560,9600));bodies.append(body);offset+=len(body)
            for name,pin in fixture['pcm'].items():
                p=self.args.reference/name;need(sha(p)==pin['sha256'],'exact complete creator PCM reference');self.freeze(p,Path('sources/reference')/name,'local-only reference PCM')
        blob=self.out/'project/main/streams.bin';blob.write_bytes(struct.pack('<4I',0x4d535055,1,3,32)+b''.join(table)+b''.join(bodies));self.artifacts[blob.relative_to(self.out).as_posix()]=sha(blob)
        vendor=self.args.vendor;paths={p for p in vendor.iterdir() if p.is_file()}
        for folder in ('include','src'):paths.update(p for p in (vendor/folder).rglob('*') if p.is_file())
        paths.update(vendor/'lib/esp32'/name for name in common.ARCHIVE_PINS)
        for p in sorted(paths):self.freeze(p,Path('sources/vendor/esp_audio_codec')/p.relative_to(vendor),'unchanged public vendor source/archive')
        common.write_json(self.out/'source-manifest.json',self.sources)
    def qualify(self):
        build=self.out/'build';desc=json.loads((build/'project_description.json').read_bytes());need(desc['target']=='esp32' and Path(desc['idf_path']).resolve()==self.args.idf,'real SDK6.0.2 LX6')
        config=json.loads((build/'config/sdkconfig.json').read_bytes())
        for key in ('HEAP_POISONING_LIGHT','FREERTOS_CHECK_STACKOVERFLOW_CANARY','COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE','ESP_TASK_WDT_EN','ESP_TASK_WDT_INIT','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1','AUDIO_DECODER_OPUS_SUPPORT'):
            need(config.get(key) is True,'actual native runtime setting '+key)
        need(not config['FREERTOS_UNICORE'] and config['FREERTOS_HZ']==1000,'dual-core scheduler')
        compiler=Path(desc['c_compiler']);nm=compiler.with_name(compiler.name.replace('gcc','nm'));cache=(build/'CMakeCache.txt').read_text()
        ninja=Path(re.search(r'^CMAKE_MAKE_PROGRAM:[A-Z_]+=(.+)$',cache,re.M).group(1).strip())
        for p in (compiler,nm,ninja):self.bind_runtime(p)
        self.run_command('compiler-version',[compiler,'--version']);commands=json.loads((build/'compile_commands.json').read_bytes());selected=[];dependencies={}
        lookup={str((self.out/v['snapshot']).resolve()).casefold():k for k,v in self.sources.items()}
        for row in commands:
            source=Path(row['file']).resolve()
            if not source.is_relative_to(self.out/'project') and not source.is_relative_to(self.out/'sources/vendor'):continue
            text=self.run_command('compiler-deps-'+str(len(selected)),[ninja,'-C',build,'-t','deps',row['output'].replace('\\','/')]);need('(VALID)' in text and '#deps ' in text,'real GCC dependency record');paths=[]
            for line in text.splitlines():
                if not line.startswith('    '):continue
                p=Path(line.strip());p=p.resolve() if p.is_absolute() else (build/p).resolve();need(p.is_file(),'actual compiler dependency')
                original=lookup.get(str(p).casefold(),str(p))
                if original not in self.sources:self.freeze(p,Path('sources/compiler-dependencies')/hashlib.sha256(str(p).encode()).hexdigest()[:16]/p.name,'actual SDK dependency')
                dependencies[str(p)]=dict(sha256=sha(p),manifest_original=original);paths.append(str(p))
            need(paths,'nonempty compiler closure');selected.append(dict(row,actual_dependency_paths=paths));obj=Path(row['output']);obj=obj if obj.is_absolute() else build/obj
            need(obj.is_file() and obj.resolve().is_relative_to(build),'actual compiler object');self.artifacts[obj.relative_to(self.out).as_posix()]=sha(obj)
            if obj.with_suffix('.su').is_file():self.artifacts[obj.with_suffix('.su').relative_to(self.out).as_posix()]=sha(obj.with_suffix('.su'))
        need(any(Path(v['file']).name=='main.c' for v in selected),'whole diagnostic TU actually compiled')
        need(not {'audio_service.c','native_audio_output.c','ogg_playback.h','decoder_registration.c','pcm_header_gain.h'} & {Path(p).name for p in dependencies},'public raw composition consumes no production wrapper/private path')
        common.write_json(self.out/'source-manifest.json',self.sources);closure=self.out/'actual-compiler-closure.json';common.write_json(closure,dict(translation_units=selected,dependencies=dependencies))
        self.report.update(actual_translation_units=len(selected),actual_compiler_dependencies=len(dependencies));elf=(build/desc['app_elf']).resolve()
        need(elf.read_bytes()[:6]==b'\x7fELF\x01\x01' and int.from_bytes(elf.read_bytes()[18:20],'little')==94,'real LX6 ELF')
        symbols=self.run_command('symbols',[nm,'-n','--defined-only',elf])
        for name in ('esp_opus_dec_open','esp_opus_dec_decode','esp_opus_dec_close'):need(re.search(r'\b'+name+r'$',symbols,re.M),'linked exact documented public API '+name)
        need(not re.search(r'\b(?:esp_audio_simple_dec_process|__wrap_esp_opus_dec_[A-Za-z0-9_]*|custom_flac_[A-Za-z0-9_]*|native_vorbis_[A-Za-z0-9_]*)$',symbols,re.M),'no Ogg process or private decoder adaptation')
        recipe=json.loads((build/'flasher_args.json').read_bytes());flashes={int(offset,0):(build/name).resolve() for offset,name in recipe['flash_files'].items()}
        need(set(flashes)=={4096,32768,65536} and all(p.is_relative_to(build) for p in flashes.values()),'bounded diagnostic recipe');flash=self.out/'qemu-flash.bin'
        argv=[self.args.idf_python,'-m','esptool','--chip','esp32','merge-bin','--output',flash,'--flash-mode','dio','--flash-size','4MB','--flash-freq','40m']
        for offset,p in sorted(flashes.items()):argv += [hex(offset),p]
        self.run_command('merge',argv+['--pad-to-size','4MB']);body=flash.read_bytes();need(len(body)==4194304 and all(body[offset:offset+p.stat().st_size]==p.read_bytes() for offset,p in flashes.items()),'exact original merged bytes')
        child=json.loads((self.out/'sdk-child.json').read_text('utf-8-sig'));need(child['pid']>0 and child['exit_status']==0,'actual SDK child terminal0')
        paths=[elf,elf.with_suffix('.bin'),elf.with_suffix('.map'),flash,self.out/'sdkconfig',self.out/'sdk-child.json',self.out/'source-manifest.json',closure,
            build/'compile_commands.json',build/'project_description.json',build/'flasher_args.json',build/'config/sdkconfig.json',build/'CMakeCache.txt',*flashes.values()]
        self.artifacts.update({p.relative_to(self.out).as_posix():sha(p) for p in paths});common.write_json(self.out/'execution-bundle.json',dict(sources=self.sources,runtime=self.runtime,artifacts=self.artifacts,
            sdk_commit=common.SDK_COMMIT,vendor_commit=common.VENDOR_COMMIT,scope=__doc__));self.artifacts['execution-bundle.json']=sha(self.out/'execution-bundle.json')
        need(self.verify_inputs(),'all real inputs/tools/artifacts unchanged before native execution');return flash


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--reference',required=True,type=Path)
    parser.add_argument('--build-timeout',type=int,default=1200);parser.add_argument('--qemu-timeout',type=int,default=1200);parser.add_argument('--preflight-only',action='store_true')
    args=parser.parse_args();args.output=args.output.resolve();args.reference=args.reference.resolve()
    need(sys.platform=='win32' and args.output.is_relative_to(ROOT/'.build') and not args.output.exists() and args.reference.is_relative_to(ROOT/'.build'),'fresh local Windows native capture')
    need(1<=args.build_timeout<=1200 and 1<=args.qemu_timeout<=1200,'bounded deadlines');reference=json.loads((args.reference/'report.json').read_bytes())
    need(reference['passed'] and reference['completed'] and reference['all_source_bindings_current'] and reference['framing_tests']['cases']==32,'actual creator-qualified framing references')
    for row in reference['sources']:need(sha(row['path'])==sha(args.reference/row['snapshot'])==row['sha256'],'current original/frozen source bindings')
    args.idf=REPO/'.idf/v6.0.2';args.idf_tools=REPO/'.idf/tools-v6.0.2';args.idf_python=args.idf_tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe';args.vendor=REPO/'.idf/esp-adf-libs/esp_audio_codec'
    args.qemu=ROOT/'.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe';args.rom=Path('C:/Work/QEMU-ESP32/pc-bios');args.git=Path(shutil.which('git.exe') or shutil.which('git') or '');args.powershell=Path(shutil.which('pwsh.exe') or '')
    need(all(p.is_file() for p in (args.idf/'export.ps1',args.idf_python,args.qemu,args.git,args.powershell,PROJECT/'sdk-build.ps1')) and
        sha(args.qemu)==common.QEMU_SHA and all(sha(args.vendor/'lib/esp32'/n)==s for n,s in common.ARCHIVE_PINS.items()),'exact installed native runtimes/archives')
    if args.preflight_only:print(json.dumps(dict(preflight=True,target_executed=False)));return 0
    args.output.mkdir(parents=True);campaign=Campaign(args,reference)
    try:
        campaign.save();campaign.verify_repositories();campaign.freeze_sources();text=(args.output/'project/sdkconfig.common.defaults').read_text()
        (args.output/'project/sdkconfig.defaults').write_text('CONFIG_IDF_TARGET="esp32"\nCONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y\n# CONFIG_FREERTOS_UNICORE is not set\n'+text,encoding='utf-8')
        for p in (args.idf_python,args.qemu,args.git,args.powershell,*args.rom.glob('esp32-v3-rom*.bin')):campaign.bind_runtime(p)
        print('FROZEN public composition sources; starting SDK build',flush=True);campaign.run_command('build',[args.powershell,'-NoProfile','-NonInteractive','-File',args.output/'project/sdk-build.ps1',
            '-Campaign',args.output,'-SdkDirectory',args.idf,'-ToolsDirectory',args.idf_tools,'-PythonExecutable',args.idf_python,'-Target','esp32'],args.build_timeout)
        flash=campaign.qualify();print('SDK terminal zero; starting public multi-handle observations',flush=True)
        log=campaign.run_command('qemu',[args.qemu,'-audiodev','none,id=quiet','-M','esp32,audiodev=quiet','-smp','2','-L',args.rom,'-display','none','-monitor','none','-serial','stdio',
            '-no-reboot','-snapshot','-nic','none','-drive','file='+str(flash)+',if=mtd,format=raw'],args.qemu_timeout)
        campaign.report['measurements']=parse_log(log+'\n'+(args.output/'qemu.stderr.log').read_text(errors='replace'),reference,args.reference,args.output)
        need(campaign.verify_inputs(),'all consumed bindings unchanged after execution');campaign.report.update(passed=True,completed=True);print(json.dumps(dict(passed=True,diagnostic_only=True,cases=6)));return 0
    except Exception as error:
        campaign.report.update(passed=False,completed=False,failure_type=type(error).__name__,failure=str(error));print(json.dumps(dict(passed=False,failure=str(error))));return 1
    finally:campaign.save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
