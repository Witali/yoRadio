"""Qualify actual verified-page Ogg playback wrapper with public Espressif synthesis.

The diagnostic is not the complete production audio service or hardware output.
Public observers forward identical arguments/results. All SDK/QEMU commands,
selected compiler dependencies, source snapshots and terminal statuses survive
failures. Firmware, executable and PCM payloads remain local diagnostics.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent if ROOT.parent.name == '.worktree' else ROOT
HARNESS = ROOT / 'tests/target/cyd_ogg_playback_qemu'
COMMON = ROOT / 'tests/run-cyd-espressif-vorbis-task-qemu.py'
COMMON_SHA = '633043d1cb61a27009f655c48f42deec198b33c556a8a73712f401aa0490bf6c'
MAIN = ROOT / 'idf/esp32-cyd2usb-native/main'
SHARED = ROOT / 'idf/components/native_stream/include'
FIXTURES = [
    ('fixture20.ogg','tests/fixtures/esp32c3_calibration/opus-510.ogg','53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11'),
    ('fixture120.ogg','tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg','b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679'),
    ('fixturevorbis.ogg','tests/fixtures/esp32c3_calibration/vorbis-q10.ogg','09d6cfa599f2c4a25f5745e5c8a605b5a1583a42d7990b9e5242b8990adff12f'),
]
REFERENCES = {
    'opus20': (2115840,'a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b','b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f'),
    'opus120': (2119680,'670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684','4110db997c16a05c329284bb6105468752c25d67818e3a99b8c9d47c5f481fd0'),
    'vorbis': (2112000,'e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910','e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910'),
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


need(sha(COMMON) == COMMON_SHA, 'pinned reviewed native command/freeze helper')
spec = importlib.util.spec_from_file_location('ogg_playback_native_common',COMMON)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)


def validate_log(text):
    text = text.replace('\r\n','\n')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack overflow',text,re.I), 'no actual panic/assertion/heap/watchdog failure')
    lines = [line for line in text.splitlines() if line.startswith('OGP_')]
    need(lines and lines[0] == 'OGP_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 initial_capacity=12288 fixtures=3 hardware=0', 'actual known native worker profile')
    links, cases, resizes, guards, failures = [], [], [], [], []
    for line in lines[1:-1]:
        parts = line.split(); tag = parts[0]; fields = dict(pair.split('=',1) for pair in parts[1:])
        need(len(fields) == len(parts)-1, 'unique native record fields')
        for key in list(fields):
            if key not in ('case','id','fixture','raw_sha','sha','window_sha'): fields[key] = int(fields[key])
        if tag == 'OGP_LINK': links.append(fields)
        elif tag == 'OGP_CASE': cases.append(fields)
        elif tag == 'OGP_RESIZE': resizes.append(fields)
        elif tag == 'OGP_GUARD': guards.append(fields)
        elif tag == 'OGP_FAILURE': failures.append(fields)
        else: need(False,'known native observation record')
    expected = [f'{fixture}_{chunk}' for fixture in REFERENCES for chunk in (0,4096,257,1)] + ['opus20_offset_preskip','opus120_offset_preskip','opus_vorbis_opus_chain']
    need([row['id'] for row in cases] == expected and len(links) == 17, 'all complete fixture/split/offset/chained cases')
    for row in links:
        raw_bytes, raw_sha, pcm_sha = REFERENCES[row['fixture']]
        need(row['raw'] == raw_bytes and row['raw_sha'] == raw_sha and row['match'] == row['close_before_ack'] == 1 and
             re.fullmatch('[a-f0-9]{64}',row['sha']) and row['sha'] == row['window_sha'], 'full unchanged raw vendor and actual clipped output identity')
        modified = row['case'].endswith('_offset_preskip')
        begin = 512 if modified else 312
        if row['fixture'] == 'vorbis': begin = 0
        end = 528000 if row['fixture'] == 'vorbis' else 528312
        need(row['begin'] == begin*4 and row['end'] == end*4 and row['pcm'] == (end-begin)*4 and
             (modified or row['sha'] == pcm_sha), 'actual stream-specific playback range')
        need(row['calls'] > 0 and row['outputs'] > 0 and row['resizes'] == int(row['fixture']=='opus120'), 'real public calls and legal long-packet resize')
    for row in cases:
        own = [link for link in links if link['case'] == row['id']]
        need(len(own) == row['links'] == (3 if row['id'].endswith('_chain') else 1) and
             sum(link['pcm'] for link in own) == row['pcm'] and sum(link['calls'] for link in own) == row['calls'] and
             sum(link['resizes'] for link in own) == row['resizes'] and row['core'] == 1 and row['priority'] == 3 and
             0 < row['stack_free'] <= 16384 and row['before'] > 0 and row['after'] > 0, 'actual case accounting and worker/resource observations')
    need(len(resizes) == 6 and all(row['capacity']==12288 and row['needed']==23040 and row['consumed']==row['decoded']==0 and row['result']==-8 for row in resizes), 'six actual long-packet public buffer errors')
    need(len(guards) == 1 and guards[0]['id']=='bad_crc_never_vendor' and guards[0]['calls_before']==guards[0]['calls_after'] and
         guards[0]['outputs']==0 and guards[0]['rejected']==1 and len(failures)==1 and failures[0]['case']=='bad_crc_never_vendor' and
         failures[0]['status']==3 and failures[0]['cause']==-1, 'real CRC rejection precedes any vendor submission')
    terminal = re.fullmatch(r'OGP_COMPLETE cases=(\d+) heap_free=(\d+) heap_min=(\d+) stack_free=(\d+) core=1 priority=3 heap_integrity=1',lines[-1])
    need(terminal and int(terminal[1]) == 16 and all(int(terminal[i]) > 0 for i in (2,3,4)), 'complete native gate and observed integrity/resources')
    return dict(cases=cases, links=links, resizes=resizes, guards=guards,
                heap_free=int(terminal[2]),heap_min=int(terminal[3]),stack_free=int(terminal[4]),
                actual_wrapper=True, production_audio_service_tu=False, production_selected=False,
                decoded_pcm_independent_numeric_conformance=False)


class Campaign(common.Campaign):
    def __init__(self,args):
        super().__init__(args)
        self.runtime_paths={}
        self.report.update(actual_audio_service_tu=False, actual_wrapper=True, actual_rtos=True,
                           production_selected=False, fixtures={name:pin for name,_,pin in FIXTURES})

    def bind_runtime(self,path):
        path=Path(path).resolve()
        key='runtime-path-redacted:'+path.name if re.search(r'(?i)[/\\]Users[/\\]',str(path)) else str(path)
        need(key not in self.runtime_paths or self.runtime_paths[key]==path,'unique local runtime alias')
        self.runtime_paths[key]=path
        self.runtime[key]=sha(path)

    def verify_inputs(self):
        published=self.runtime
        self.runtime={str(self.runtime_paths.get(key,key)):digest for key,digest in published.items()}
        try:
            return super().verify_inputs()
        finally:
            self.runtime=published

    def freeze_sources(self):
        for path in sorted(HARNESS.rglob('*')):
            if path.is_file(): self.freeze(path,Path('project')/path.relative_to(HARNESS),'canonical diagnostic')
        for name in ('decoder_registration.c','decoder_registration.h','ogg_playback.h'):
            self.freeze(MAIN/name,Path('project/main')/name,'actual application public wrapper/registration')
        for name in ('ogg_page_input.h','opus_pcm_trim.h','ogg_opus_timeline.h','decoder_pending_input.h'):
            self.freeze(SHARED/name,Path('project/main')/name,'actual shared input/timeline/trim owner')
        for name,relative,_ in FIXTURES:
            self.freeze(ROOT/relative,Path('project/main')/name,'complete original encoded fixture')
        for path in [COMMON,Path(__file__)]: self.freeze(path,Path('sources/controllers')/path.name,'reviewed native controller')
        vendor=self.args.vendor
        paths={p for p in vendor.iterdir() if p.is_file()}
        for folder in ('include','src'): paths.update(p for p in (vendor/folder).rglob('*') if p.is_file())
        paths.update(vendor/'lib/esp32'/name for name in common.ARCHIVE_PINS)
        for path in sorted(paths): self.freeze(path,Path('sources/vendor/esp_audio_codec')/path.relative_to(vendor),'exact public vendor input')
        common.write_json(self.out/'source-manifest.json',self.sources)

    def qualify(self):
        build=self.out/'build'
        desc=json.loads((build/'project_description.json').read_bytes())
        need(desc['target']=='esp32' and Path(desc['idf_path']).resolve()==self.args.idf,'actual SDK/target')
        config=json.loads((build/'config/sdkconfig.json').read_bytes())
        for key in ('HEAP_POISONING_LIGHT','FREERTOS_CHECK_STACKOVERFLOW_CANARY','COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE','ESP_TASK_WDT_EN','ESP_TASK_WDT_INIT','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1','AUDIO_DECODER_OPUS_SUPPORT','AUDIO_DECODER_VORBIS_SUPPORT','AUDIO_SIMPLE_DEC_OGG_SUPPORT'):
            need(config.get(key) is True,'actual runtime setting: '+key)
        need(not config['FREERTOS_UNICORE'] and config['FREERTOS_HZ']==1000,'actual dual-core scheduler')
        compiler=Path(desc['c_compiler']);nm=compiler.with_name(compiler.name.replace('gcc','nm'))
        cache=(build/'CMakeCache.txt').read_text()
        ninja=Path(re.search(r'^CMAKE_MAKE_PROGRAM:[A-Z_]+=(.+)$',cache,re.M).group(1).strip())
        for path in (compiler,nm,ninja): self.bind_runtime(path)
        self.run_command('compiler-version',[compiler,'--version'])
        commands=json.loads((build/'compile_commands.json').read_bytes())
        selected=[];dependencies={}
        lookup={str((self.out/row['snapshot']).resolve()).casefold():original for original,row in self.sources.items()}
        for row in commands:
            source=Path(row['file']).resolve()
            if not source.is_relative_to(self.out/'project') and not source.is_relative_to(self.out/'sources'): continue
            text=self.run_command('compiler-deps-'+str(len(selected)),[ninja,'-C',build,'-t','deps',row['output'].replace('\\','/')])
            need('(VALID)' in text and '#deps ' in text,'actual GCC/Ninja dependency record')
            paths=[]
            for line in text.splitlines():
                if not line.startswith('    '): continue
                path=Path(line.strip());path=path.resolve() if path.is_absolute() else (build/path).resolve()
                need(path.is_file(),'actual compiler dependency exists')
                original=lookup.get(str(path).casefold(),str(path))
                if original not in self.sources:
                    self.freeze(path,Path('sources/compiler-dependencies')/hashlib.sha256(str(path).encode()).hexdigest()[:16]/path.name,'actual SDK/compiler dependency')
                dependencies[str(path)]=dict(sha256=sha(path),manifest_original=original);paths.append(str(path))
            need(paths,'nonempty actual selected dependency closure')
            copied=dict(row,actual_dependency_paths=paths);selected.append(copied)
            obj=Path(row['output']);obj=obj if obj.is_absolute() else build/obj
            need(obj.is_file() and obj.resolve().is_relative_to(build),'actual selected compiler object')
            self.artifacts[obj.relative_to(self.out).as_posix()]=sha(obj)
            if obj.with_suffix('.su').exists(): self.artifacts[obj.with_suffix('.su').relative_to(self.out).as_posix()]=sha(obj.with_suffix('.su'))
        need({'main.c','decoder_registration.c'} <= {Path(row['file']).name for row in selected} and
             {'ogg_playback.h','ogg_page_input.h','opus_pcm_trim.h','ogg_opus_timeline.h','decoder_pending_input.h'} <= {Path(p).name for p in dependencies},'actual wrapper and all shared owners compiled')
        common.write_json(self.out/'source-manifest.json',self.sources)
        common.write_json(self.out/'actual-compiler-closure.json',dict(translation_units=selected,dependencies=dependencies))
        self.report.update(actual_translation_units=len(selected),actual_compiler_dependencies=len(dependencies))
        elf=(build/desc['app_elf']).resolve()
        need(elf.read_bytes()[:6]==b'\x7fELF\x01\x01' and int.from_bytes(elf.read_bytes()[18:20],'little')==94,'actual LX6 ELF32')
        symbols=self.run_command('symbols',[nm,'-n','--defined-only',elf])
        for name in ('esp_audio_simple_dec_process','esp_opus_dec_decode','esp_vorbis_dec_decode','decoder_register_codecs','__wrap_esp_audio_simple_dec_open','__wrap_esp_audio_simple_dec_process','__wrap_esp_audio_simple_dec_close'):
            need(re.search(r'\b'+name+r'$',symbols,re.M),'actual linked public interface: '+name)
        need(not re.search(r'\b(?:native_vorbis_|custom_flac_|__wrap_(?:vorbis_|floor[01]_|esp_vorbis_|esp_ogg_|media_lib_))[A-Za-z0-9_]*$',symbols,re.M),'no private decoder repair or synthesis wrapper')
        recipe=json.loads((build/'flasher_args.json').read_bytes())
        flashes={int(offset,0):(build/name).resolve() for offset,name in recipe['flash_files'].items()}
        need(set(flashes)=={4096,32768,65536} and all(p.is_relative_to(build) for p in flashes.values()),'bounded exact diagnostic flash recipe')
        flash=self.out/'qemu-flash.bin'
        argv=[self.args.idf_python,'-m','esptool','--chip','esp32','merge-bin','--output',flash,'--flash-mode','dio','--flash-size','4MB','--flash-freq','40m']
        for offset,path in sorted(flashes.items()):argv += [hex(offset),path]
        self.run_command('merge',argv+['--pad-to-size','4MB'])
        body=flash.read_bytes()
        need(len(body)==4194304 and all(body[offset:offset+path.stat().st_size]==path.read_bytes() for offset,path in flashes.items()),'exact original merged component bytes')
        child=self.out/'sdk-child.json';status=json.loads(child.read_text('utf-8-sig'))
        need(status['pid']>0 and status['exit_status']==0,'actual SDK child terminal zero')
        artifacts=[elf,elf.with_suffix('.bin'),elf.with_suffix('.map'),flash,self.out/'sdkconfig',child,
                   build/'compile_commands.json',build/'project_description.json',build/'flasher_args.json',
                   build/'config/sdkconfig.json',build/'CMakeCache.txt',self.out/'source-manifest.json',
                   self.out/'actual-compiler-closure.json',*flashes.values()]
        self.artifacts.update({p.relative_to(self.out).as_posix():sha(p) for p in artifacts})
        common.write_json(self.out/'execution-bundle.json',dict(sources=self.sources,runtime=self.runtime,artifacts=self.artifacts,
                          sdk_commit=common.SDK_COMMIT,vendor_commit=common.VENDOR_COMMIT,scope=__doc__))
        self.artifacts['execution-bundle.json']=sha(self.out/'execution-bundle.json')
        need(self.verify_inputs(),'all source/runtime/artifact bindings current before execution')
        return flash


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--build-timeout',type=int,default=1200)
    parser.add_argument('--qemu-timeout',type=int,default=1200)
    parser.add_argument('--preflight-only',action='store_true')
    args=parser.parse_args();args.output=args.output.resolve()
    need(sys.platform=='win32' and args.output.is_relative_to(ROOT/'.build') and not args.output.exists(),'fresh Windows diagnostic output')
    need(1<=args.build_timeout<=1200 and 1<=args.qemu_timeout<=1200,'bounded native deadlines')
    args.idf=REPO/'.idf/v6.0.2';args.idf_tools=REPO/'.idf/tools-v6.0.2'
    args.idf_python=args.idf_tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    args.vendor=REPO/'.idf/esp-adf-libs/esp_audio_codec';args.qemu=ROOT/'.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
    args.rom=Path('C:/Work/QEMU-ESP32/pc-bios');args.git=Path(shutil.which('git.exe') or shutil.which('git') or '')
    args.powershell=Path(shutil.which('pwsh.exe') or '')
    need(all(p.is_file() for p in (args.idf/'tools/idf.py',args.idf/'export.ps1',args.idf_python,args.qemu,args.git,args.powershell,HARNESS/'sdk-build.ps1')),'installed native dependencies')
    need(sha(args.qemu)==common.QEMU_SHA and all(sha(args.vendor/'lib/esp32'/name)==pin for name,pin in common.ARCHIVE_PINS.items()),'exact QEMU and LX6 vendor archives')
    need(all(sha(ROOT/relative)==pin for _,relative,pin in FIXTURES),'all three original complete fixtures')
    if args.preflight_only:
        print(json.dumps(dict(preflight=True,target_executed=False)));return 0
    args.output.mkdir(parents=True);campaign=Campaign(args)
    try:
        campaign.save();campaign.verify_repositories();campaign.freeze_sources()
        common_text=(args.output/'project/sdkconfig.common.defaults').read_text()
        (args.output/'project/sdkconfig.defaults').write_text('CONFIG_IDF_TARGET="esp32"\nCONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y\n# CONFIG_FREERTOS_UNICORE is not set\n'+common_text,encoding='utf-8')
        for path in (args.idf_python,args.qemu,args.git,args.powershell,*args.rom.glob('esp32-v3-rom*.bin')):campaign.bind_runtime(path)
        campaign.run_command('build',[args.powershell,'-NoProfile','-NonInteractive','-File',args.output/'project/sdk-build.ps1',
                                     '-Campaign',args.output,'-SdkDirectory',args.idf,'-ToolsDirectory',args.idf_tools,
                                     '-PythonExecutable',args.idf_python,'-Target','esp32'],args.build_timeout)
        flash=campaign.qualify()
        log=campaign.run_command('qemu',[args.qemu,'-audiodev','none,id=quiet','-M','esp32,audiodev=quiet','-smp','2','-L',args.rom,
            '-display','none','-monitor','none','-serial','stdio','-no-reboot','-snapshot','-nic','none',
            '-drive','file='+str(flash)+',if=mtd,format=raw'],args.qemu_timeout)
        campaign.report['measurements']=validate_log(log+'\n'+(args.output/'qemu.stderr.log').read_text(errors='replace'))
        need(campaign.verify_inputs(),'all source/runtime/artifact bindings current after execution')
        campaign.report.update(passed=True,completed=True)
        print(json.dumps(dict(passed=True,cases=16,capture=args.output.relative_to(ROOT).as_posix())))
        return 0
    except Exception as error:
        campaign.report.update(passed=False,completed=False,failure_type=type(error).__name__,failure=str(error))
        print(json.dumps(dict(passed=False,failure=str(error),capture=args.output.relative_to(ROOT).as_posix())))
        return 1
    finally:
        campaign.save()


if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
