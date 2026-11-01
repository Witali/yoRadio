"""Standalone real-SDK family1/Tags adapter vs independent documented direct-native synthesis.

Same-vendor full logical PCM SHA256 equality is an integration oracle, not an
independent creator numeric conformance claim. All original120ms packets and
actual public statuses/consumption/close/resource measurements are retained.
No production audio task, hardware, private codec ABI or injected native OOM.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent.parent if ROOT.parent.name=='.worktree' else ROOT
PROJECT=ROOT/'tests/target/cyd_opus_family1_playback_qemu'
PREP=ROOT/'tests/fixtures/opus_family1_playback_native/prepare.py'
PARENT=ROOT/'tests/run-cyd-opus-multistream-public-qemu.py'
MAIN=ROOT/'idf/esp32-cyd2usb-native/main'
SHARED=ROOT/'idf/components/native_stream/include'
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
old_manifest=json.loads((ROOT/'tests/results/cyd-opus-multistream-public-20261101/manifest.json').read_bytes())
need(sha(PARENT)==old_manifest['canonical_source_sha256'][PARENT.relative_to(ROOT).as_posix()],'unchanged reviewed standalone SDK/closure runtime')
old=module('family1_adapter_native_runtime',PARENT);common=old.common
prepare=module('family1_adapter_input_preparation',PREP)

def parse_log(text,reference):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack overflow',text,re.I),'no native panic/assertion/watchdog/heap corruption')
    lines=[line for line in text.replace('\r\n','\n').splitlines() if line.startswith('AF_')];need(lines and lines[0].startswith('AF_BEGIN '),'actual diagnostic begin')
    records=[]
    for line in lines:
        pieces=line.split();fields=dict(p.split('=',1) for p in pieces[1:]);need(len(fields)==len(pieces)-1,'unique actual event fields')
        records.append(dict(tag=pieces[0],**{k:v if k in ('sdk','sha') else int(v) for k,v in fields.items()}))
    begin=records[0];need(begin['sdk']=='6.0.2' and begin['coordinator']==0 and begin['worker']==1 and begin['priority']==5 and begin['stack']==16384 and begin['fixtures']==12 and begin['hardware']==0,'exact standalone dual-core decoder worker profile')
    need(begin['adapter_bytes']>0 and begin['decoder_bytes']>0 and begin['tags_bytes']>0 and begin['zero_bytes']==2048,'actual target type/static storage measurements')
    controls=[r for r in records if r['tag']=='AF_HASH_CONTROL'];need([r['group'] for r in controls]==[0,1] and all(r['iterations']==32 and r['before']>0 and r['after']>0 for r in controls),'two genuine repeated-empty-hash heap controls, without inferred codec attribution')
    results=[r for r in records if r['tag']=='AF_RESULT'];failures=[r for r in records if r['tag']=='AF_FAILURE'];cases=[];references={}
    for row in results:
        key=(row['kind'],row['fixture'],row['schedule']);source=reference['fixtures'][row['fixture']]
        events=[r for r in records if r['tag'] in ('AF_OPEN','AF_CALL','AF_CLOSE','AF_FRAMES') and (r['kind'],r['fixture'],r['schedule'])==key]
        opens=[r for r in events if r['tag']=='AF_OPEN'];calls=[r for r in events if r['tag']=='AF_CALL'];closes=[r for r in events if r['tag']=='AF_CLOSE'];frames=[r for r in events if r['tag']=='AF_FRAMES']
        selected=source['needed_streams'] if row['kind'] else list(range(source['streams']));expected_input=sum(p['parts'][stream]['bytes'] for p in source['packets'] for stream in selected)
        need(row['opens']==len(opens) and row['calls']==len(calls) and row['closes']==len(closes) and row['close_errors']==sum(r['result']!=0 for r in closes) and
            row['consumed']==sum(r['consumed'] for r in calls) and row['decoded']==sum(r['decoded'] for r in calls) and row['outputs']==sum(r['decoded']>0 for r in calls),'genuine public event accounting')
        need([r['call'] for r in calls]==list(range(1,len(calls)+1)) and all(r['consumed']<=r['len'] and r['decoded']<=r['capacity'] for r in calls),'real call sequence and byte/capacity bounds')
        complete=bool(row['complete'])
        if complete:
            need(not row['driver'] and not row['live'] and not row['close_errors'] and row['integrity']==row['lifetime']==1 and row['core']==1 and row['priority']==5 and
                0<row['stack_free']<=16384 and row['before']>0 and row['after']>0 and row['heap_min']>0,'actual complete-case resources/cleanup/output lease')
            need([r['stream'] for r in opens]==selected and all(r['result']==0 and r['handle']==1 and r['rate']==48000 and r['channels']==(2 if r['stream']<source['coupled'] else 1) and
                r['self_delimited']==int(r['stream']+1<source['streams']) for r in opens),'documented native cfg/real opens with original stream numbering')
            need(len(closes)==len(opens) and all(not r['result'] and not r['pending'] for r in closes) and row['consumed']==expected_input,'complete original selected encoded input and real close')
            need([r['stream'] for r in frames]==selected and all(r['frames']==source['raw'] for r in frames),'complete actual PCM frame counts per selected stream')
            need(row['pcm']==source['logical']*source['channels']*2 and row['max_chunk']<=128*source['channels']*2 and re.fullmatch('[a-f0-9]{64}',row['sha']),'complete actual trim geometry/digest')
            need(all(r['result'] in (0,-8) for r in calls) and all(not r['decoded'] and r['needed']>r['capacity'] and r['needed']<=23040 for r in calls if r['result']==-8),'genuine public resize protocol')
            for stream in selected:
                own=[r for r in calls if r['stream']==stream];width=2 if stream<source['coupled'] else 1
                need(sum(r['consumed'] for r in own)==sum(p['parts'][stream]['bytes'] for p in source['packets']) and
                    sum(r['decoded'] for r in own)==source['raw']*width*2,'per-stream complete byte/sample accounting')
            if row['kind']:
                shape=source['split' if row['style'] else 'whole'];need(row['input_used']==shape['bytes'] and row['acks']==len(shape['pages']),'all actual original page input/ACK events')
                need(row['fixture'] in references and row['sha']==references[row['fixture']]['sha'] and row['pcm']==references[row['fixture']]['pcm'],'byte-exact independent direct-public-native logical PCM integration oracle')
            else:references[row['fixture']]=row
        cases.append(dict(measurements=row,opens=opens,calls=calls,closes=closes,frames=frames,same_vendor_integration_oracle=True,independent_creator_numeric_conformance=False))
    terminal=records[-1];need(terminal['tag']=='AF_COMPLETE','actual diagnostic terminal record');expected=[(0,f,0) for f in range(12)]
    for f in range(12):expected.extend((1,f,s) for s in (range(4) if f<3 else range(2) if f==11 else range(1)))
    actual={(r['kind'],r['fixture'],r['schedule']) for r in results};complete=actual==set(expected) and len(results)==34 and len(references)==12 and not failures and all(r['complete'] for r in results) and terminal['complete']==1 and terminal['references']==12 and terminal['adapters']==22 and not terminal['live'] and terminal['integrity']==1
    return dict(gate_passed=bool(complete),begin=begin,cases=cases,failures=failures,hash_controls=controls,terminal=terminal,
        reference_kind='independent direct documented public-native handle implementation; same-vendor integration oracle',creator_numeric_conformance_claim=False,new_tolerance_applied=False,
        production_audio_service_tu=False,production_selected=False,native_oom_injected=False,resource_refusal_is_format_allowance=False)

class Campaign(old.Campaign):
    def __init__(self,args):
        old.base.Campaign.__init__(self,args);self.report.update(actual_audio_service_tu=False,actual_family1_adapter=True,actual_rtos=True,public_raw_handles=True,production_selected=False,native_oom_injected=False)
        self.report.pop('fixtures',None)
    def freeze_sources(self):
        for p in sorted(PROJECT.rglob('*')):
            if p.is_file():self.freeze(p,Path('project')/p.relative_to(PROJECT),'new standalone adapter/direct-reference diagnostic')
        for name in ('opus_family1_playback.h','opus_family1_decoder.h'):self.freeze(MAIN/name,Path('project/main')/name,'completed frozen public component')
        for name in ('opus_tags_stream.h','ogg_opus_audio_packets.h','opus_family1_mapping.h','opus_multistream_framing.h','ogg_page_input.h','ogg_opus_timeline.h','opus_pcm_trim.h'):
            self.freeze(SHARED/name,Path('project/main')/name,'completed frozen public component')
        for p in (Path(__file__),PREP,prepare.FRAMING,prepare.READER,PARENT,old.BASE,old.base.COMMON,old.FAMILY):self.freeze(p,Path('sources/controllers')/p.name,'new preparation or pinned reviewed runtime/data helper')
        for c in (3,6,8):self.freeze(self.args.reference/('channels'+str(c)+'.packets'),Path('sources/originals')/('channels'+str(c)+'.packets'),'complete original creator-qualified encoded input')
        self.freeze(prepare.LONG,Path('sources/originals')/prepare.LONG.name,'complete original92-packet120ms encoded input')
        body,reference=prepare.build(self.args.reference);self.reference=reference;blob=self.out/'project/main/fixtures.bin';blob.write_bytes(body);self.artifacts[blob.relative_to(self.out).as_posix()]=sha(blob)
        common.write_json(self.out/'fixture-preparation.json',reference);self.artifacts['fixture-preparation.json']=sha(self.out/'fixture-preparation.json');self.report['fixture_preparation_sha256']=sha(self.out/'fixture-preparation.json');self.report['fixture_names']=[r['name'] for r in reference['fixtures']]
        vendor=self.args.vendor;paths={p for p in vendor.iterdir() if p.is_file()}
        for folder in ('include','src'):paths.update(p for p in (vendor/folder).rglob('*') if p.is_file())
        paths.update(vendor/'lib/esp32'/name for name in common.ARCHIVE_PINS)
        for p in sorted(paths):self.freeze(p,Path('sources/vendor/esp_audio_codec')/p.relative_to(vendor),'unchanged documented vendor input/archive')
        common.write_json(self.out/'source-manifest.json',self.sources)
    def qualify(self):
        flash=super().qualify();closure=json.loads((self.out/'actual-compiler-closure.json').read_bytes());deps={Path(p).name for p in closure['dependencies']}
        need({'opus_family1_playback.h','opus_family1_decoder.h','opus_tags_stream.h','ogg_opus_audio_packets.h','opus_multistream_framing.h','opus_family1_mapping.h','opus_pcm_trim.h'}<=deps,'actual selected complete component dependency closure')
        direct=[r for r in closure['translation_units'] if Path(r['file']).name=='direct_reference.c'];need(len(direct)==1 and not {'opus_family1_playback.h','opus_family1_decoder.h','opus_family1_mapping.h','opus_multistream_framing.h','opus_pcm_trim.h','ogg_page_input.h'} & {Path(p).name for p in direct[0]['actual_dependency_paths']},'independent direct reference excludes production synthesis/framing/mapping/trim helpers')
        desc=json.loads((self.out/'build/project_description.json').read_bytes());compiler=Path(desc['c_compiler']);nm=compiler.with_name(compiler.name.replace('gcc','nm'));symbols=self.run_command('symbols-sizes',[nm,'-S','--defined-only',self.out/'build'/desc['app_elf']])
        match=re.search(r'^[0-9a-f]+\s+([0-9a-f]+)\s+r\s+ofp_zero_chunk$',symbols,re.M);need(match and int(match[1],16)==2048,'actual target immutable zero storage')
        self.report.update(direct_reference_independent_component_closure=True,target_static_zero_bytes=2048);return flash

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--reference',required=True,type=Path);parser.add_argument('--preflight-only',action='store_true')
    parser.add_argument('--build-timeout',type=int,default=1200);parser.add_argument('--qemu-timeout',type=int,default=1200);args=parser.parse_args();args.output=args.output.resolve();args.reference=args.reference.resolve()
    need(sys.platform=='win32' and args.output.is_relative_to(ROOT/'.build') and not args.output.exists() and args.reference.is_relative_to(ROOT/'.build'),'fresh standalone Windows campaign')
    need(1<=args.build_timeout<=1200 and 1<=args.qemu_timeout<=1200,'bounded native command deadlines')
    for folder in ('cyd-opus-tags-stream-20261101','cyd-opus-family1-playback-tags-20261101'):
        manifest=json.loads((ROOT/'tests/results'/folder/'manifest.json').read_bytes())
        for path,digest in manifest['canonical_source_sha256'].items():need(sha(ROOT/path)==digest,'completed component source remains frozen '+path)
    args.idf=REPO/'.idf/v6.0.2';args.idf_tools=REPO/'.idf/tools-v6.0.2';args.idf_python=args.idf_tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe';args.vendor=REPO/'.idf/esp-adf-libs/esp_audio_codec'
    args.qemu=ROOT/'.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe';args.rom=Path('C:/Work/QEMU-ESP32/pc-bios');args.git=Path(shutil.which('git.exe') or shutil.which('git') or '');args.powershell=Path(shutil.which('pwsh.exe') or '')
    need(all(p.is_file() for p in (args.idf/'export.ps1',args.idf_python,args.qemu,args.git,args.powershell,PROJECT/'sdk-build.ps1')) and sha(args.qemu)==common.QEMU_SHA and
        all(sha(args.vendor/'lib/esp32'/name)==digest for name,digest in common.ARCHIVE_PINS.items()),'exact installed SDK/QEMU/vendor prerequisites')
    if args.preflight_only:
        blob,reference=prepare.build(args.reference);print(json.dumps(dict(preflight=True,target_executed=False,fixtures=len(reference['fixtures']),blob_bytes=len(blob),blob_sha256=hashlib.sha256(blob).hexdigest(),components_frozen=True)));return 0
    args.output.mkdir(parents=True);campaign=Campaign(args)
    try:
        campaign.save();campaign.verify_repositories();campaign.freeze_sources();text=(args.output/'project/sdkconfig.common.defaults').read_text()
        (args.output/'project/sdkconfig.defaults').write_text('CONFIG_IDF_TARGET="esp32"\nCONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y\n# CONFIG_FREERTOS_UNICORE is not set\n'+text,encoding='utf-8')
        for p in (args.idf_python,args.qemu,args.git,args.powershell,*args.rom.glob('esp32-v3-rom*.bin')):campaign.bind_runtime(p)
        print('FROZEN new public adapter/direct reference; starting SDK build',flush=True);campaign.run_command('build',[args.powershell,'-NoProfile','-NonInteractive','-File',args.output/'project/sdk-build.ps1',
            '-Campaign',args.output,'-SdkDirectory',args.idf,'-ToolsDirectory',args.idf_tools,'-PythonExecutable',args.idf_python,'-Target','esp32'],args.build_timeout)
        flash=campaign.qualify();print('SDK driver/child terminal zero; starting standalone QEMU adapter gate',flush=True)
        log=campaign.run_command('qemu',[args.qemu,'-audiodev','none,id=quiet','-M','esp32,audiodev=quiet','-smp','2','-L',args.rom,'-display','none','-monitor','none','-serial','stdio',
            '-no-reboot','-snapshot','-nic','none','-drive','file='+str(flash)+',if=mtd,format=raw'],args.qemu_timeout)
        campaign.report['measurements']=parse_log(log+'\n'+(args.output/'qemu.stderr.log').read_text(errors='replace'),campaign.reference)
        need(campaign.verify_inputs(),'all initial/final consumed source/runtime/artifact bindings current');need(campaign.report['measurements']['gate_passed'],'all required actual direct-native/adapter cases complete and byte-exact')
        campaign.report.update(passed=True,completed=True);print(json.dumps(dict(passed=True,references=12,adapter_cases=22,production_selected=False)));return 0
    except Exception as error:
        campaign.report.update(passed=False,completed=False,failure_type=type(error).__name__,failure=str(error));print(json.dumps(dict(passed=False,failure=str(error))));return 1
    finally:campaign.save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
