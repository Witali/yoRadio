"""Observe complete public family1 3/6/8-channel decoding, stock before wrapper.

This is a diagnostic, not a supported-format certification. Real format/header
and allocation refusals are measured without declaring them standards-compliant.
Full PCM is reconstructed locally from exact native UART records; only numeric
measurements and content identities are candidates for publication.
"""
import argparse
from array import array
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent.parent if ROOT.parent.name=='.worktree' else ROOT
PROJECT=ROOT/'tests/target/cyd_opus_family1_qemu'
BASE=ROOT/'tests/run-cyd-ogg-playback-qemu.py'
BASE_SHA='6c1ffd611c7c10982d8c3ad6eb2b633c26139355d1996096ec9d2b4a0b120dfd'
WRAPPER_SHA='2090861f891aa299fac3a90f4e35d13a6e6412f63b7293c4ed56bbd43d7482a6'
MAIN=ROOT/'idf/esp32-cyd2usb-native/main'
SHARED=ROOT/'idf/components/native_stream/include'


def need(value,why):
    if not value:raise ValueError(why)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


need(sha(BASE)==BASE_SHA,'pinned reviewed native command/closure helper')
spec=importlib.util.spec_from_file_location('family1_reviewed_native_helper',BASE)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);common=base.common


def compare_pcm(actual,reference):
    need(len(actual)==len(reference) and len(actual)>0 and len(actual)%2==0,'complete equal PCM geometry for numeric observation')
    a=array('h');a.frombytes(actual);b=array('h');b.frombytes(reference)
    error=sum((x-y)**2 for x,y in zip(a,b));energy=sum(y*y for y in b)
    return dict(samples=len(a),equal_bytes=actual==reference,max_absolute_lsb=max(abs(x-y) for x,y in zip(a,b)),
        rms_error_lsb=math.sqrt(error/len(a)),reference_energy=energy,error_energy=error,
        signal_to_error_db=10*math.log10(energy/error) if error and energy else None,
        new_tolerance_applied=False,numeric_conformance_claim=False)


def parse_log(text,fixtures,reference,out):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack overflow',text,re.I),
         'no target panic, assertion, watchdog, stack or heap error')
    lines=[line for line in text.replace('\r\n','\n').splitlines() if line.startswith('F1_')]
    need(lines[0]=='F1_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 initial_capacity=12288 fixtures=3','actual diagnostic worker')
    cases=[];calls={};opens={};closes={};infos={};pcms={};record_fields={
        'F1_CALL':{'id','call','len','consumed','capacity','needed','decoded','eos','result'},
        'F1_OPEN':{'id','result','handle'},'F1_CLOSE':{'id'},'F1_INFO':{'id','result','rate','channels','bits'}}
    for line in lines[1:-1]:
        parts=line.split();tag=parts[0];fields=dict(value.split('=',1) for value in parts[1:]);need(len(fields)==len(parts)-1,'unique complete record fields')
        if tag=='F1_PCM':
            need(set(fields)=={'id','kind','offset','bytes','hex'} and fields['kind'] in ('raw','output'),'exact PCM record')
            id=int(fields['id']);data=bytes.fromhex(fields['hex']);key=(id,fields['kind']);body=pcms.setdefault(key,bytearray())
            need(len(data)==int(fields['bytes']) and len(body)==int(fields['offset']) and 0<len(data)<=128,'continuous complete PCM transport')
            body.extend(data);continue
        if tag=='F1_CASE':
            row={k:v if k.endswith('_sha') else int(v) for k,v in fields.items()};cases.append(row);continue
        need(tag in record_fields and set(fields)==record_fields[tag],'known exact public-call record')
        row={k:int(v) for k,v in fields.items()};id=row['id'];lookup={'F1_CALL':calls,'F1_OPEN':opens,'F1_CLOSE':closes,'F1_INFO':infos}[tag]
        lookup.setdefault(id,[]).append(row)
    need(len(cases)==12 and [r['id'] for r in cases]==list(range(12)),'twelve complete stock/wrapper cases')
    outcomes=[]
    for id,row in enumerate(cases):
        channels=(3,6,8)[id//4];mode=id%4//2;chunk=257 if id%2 else 0;fixture=fixtures['channels'+str(channels)];account=fixture['accounting']
        need((row['encoded_channels'],row['mode'],row['chunk'],row['fixture_bytes'])==(channels,mode,chunk,account['bytes']),
             'exact full fixture and independent handle order: stock first, then wrapper')
        own=calls.get(id,[]);open_rows=opens.get(id,[]);close_rows=closes.get(id,[])
        need(len(open_rows)==1 and row['opens']==sum(r['result']==0 for r in open_rows)==row['closes']==len(close_rows) and
             row['open_status']==open_rows[0]['result'] and row['calls']==len(own) and row['consumed']==sum(r['consumed'] for r in own) and
             [r['call'] for r in own]==list(range(1,len(own)+1)) and row['resizes']==sum(r['result']==-8 for r in own),
             'genuine public open/process/close/status and complete consumption accounting')
        need(all(r['consumed']<=r['len'] and r['decoded']<=r['capacity'] for r in own) and
             row['data_eos']==sum(r['eos'] and r['len']>0 for r in own) and row['empty_eos']==sum(r['eos'] and r['len']==0 for r in own),
             'actual EOS, frame capacities and raw consumption')
        need(0<row['offered']<=row['fixture_bytes'] and row['consumed']<=row['fixture_bytes'] and row['core']==1 and row['priority']==3 and
             0<row['stack_free']<=16384 and 0<row['heap_min']<=row['after'] and row['before']>0,'actual resource and input bounds')
        result=dict(measurements=row,public_calls=own,info=infos.get(id,[]),complete_pcm={},independent_comparisons={})
        for kind in ('raw','output'):
            data=bytes(pcms.get((id,kind),b''));need(len(data)==row[kind+'_bytes'] and hashlib.sha256(data).hexdigest()==row[kind+'_sha'],
                 'all native PCM bytes match independently reconstructed hash')
            path=out/('case'+str(id)+'-'+kind+'.pcm');path.write_bytes(data)
            result['complete_pcm'][kind]=dict(path=path.name,local_only=True,bytes=len(data),sha256=sha(path))
            if data and row['channels'] in (2,channels):
                if row['channels']==2:filename='channels'+str(channels)+'-stereo'+('-trim' if kind=='output' else '')+'.pcm'
                else:filename='channels'+str(channels)+'-raw.pcm'
                expected=(reference/filename).read_bytes()
                if kind=='output' and row['channels']==channels:
                    first=account['pre_skip']*channels*2;expected=expected[first:first+9600*channels*2]
                if len(data)==len(expected):
                    result['independent_comparisons'][kind]=dict(complete_geometry=True,**compare_pcm(data,expected))
                elif len(data)<len(expected):
                    result['independent_comparisons'][kind]=dict(complete_geometry=False,expected_full_bytes=len(expected),
                        observed_prefix_bytes=len(data),**compare_pcm(data,expected[:len(data)]))
                else:
                    result['independent_comparisons'][kind]=dict(complete_geometry=False,expected_full_bytes=len(expected),
                        observed_bytes=len(data),numeric_comparison_performed=False)
        if row['status']==0:
            need(row['drained']==1 and row['offered']==row['consumed']==row['fixture_bytes'] and row['raw_bytes']==10560*row['channels']*2 and
                 row['data_eos']>0 and row['empty_eos']>0 and (not mode or row['output_bytes']==9600*row['channels']*2),
                 'successful cases require full input, complete decoded PCM and genuine full EOS drain')
            result['observed_behavior']='complete_pcm_requires_numeric_and_playback_assessment'
        else:
            need(row['cause']!=0 and row['drained']==0,'genuine reported refusal, not a fabricated success')
            result['observed_behavior']={-2:'reported_allocation_refusal',-4:'reported_header_parse_error',-7:'reported_unsupported_format'}.get(row['cause'],'reported_error_requires_assessment')
            result['standards_compliant_refusal']=None
        outcomes.append(result)
    terminal=lines[-1].split();need(terminal[0]=='F1_COMPLETE','actual terminal diagnostic record')
    complete={k:int(v) for k,v in (part.split('=',1) for part in terminal[1:])}
    need(complete['cases']==12 and complete['core']==1 and complete['priority']==3 and complete['heap_integrity']==1 and
         complete['retained']==complete['registry_before']-complete['heap_free'] and 0<complete['stack_free']<=16384,'terminal ownership/integrity observations')
    return dict(cases=outcomes,complete=complete,diagnostic_completed=True,mandatory_family1_playback_qualified=False,
        physical_output_qualified=False,universal_codec_conformance_claim=False,new_tolerance_applied=False)


class Campaign(base.Campaign):
    def __init__(self,args,fixtures):
        super().__init__(args);self.fixtures=fixtures
        self.report.update(fixtures=fixtures,actual_audio_service_tu=False,actual_wrapper=True,
            stock_public_vendor_measured_first=True,mandatory_family1_playback_qualified=False)
    def freeze_sources(self):
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file():self.freeze(path,Path('project')/path.relative_to(PROJECT),'new independent family1 diagnostic')
        for name in ('decoder_registration.c','decoder_registration.h','ogg_playback.h'):
            self.freeze(MAIN/name,Path('project/main')/name,'unchanged actual public playback/registration')
        for name in ('ogg_page_input.h','opus_pcm_trim.h','ogg_opus_timeline.h','decoder_pending_input.h'):
            self.freeze(SHARED/name,Path('project/main')/name,'unchanged actual shared public owner')
        for path in (BASE,base.COMMON,Path(__file__)):
            self.freeze(path,Path('sources/controllers')/path.name,'pinned reviewed controller source')
        for path in sorted((self.args.reference/'sources').rglob('*')):
            if path.is_file():self.freeze(path,Path('sources/host-reference-sources')/path.relative_to(self.args.reference/'sources'),'frozen creator host preparation source')
        self.freeze(self.args.reference/'report.json',Path('sources/reference/report.json'),'exact complete host reference process report')
        table=[];bodies=[];offset=112
        for channels in (3,6,8):
            row=self.fixtures['channels'+str(channels)];e=row['accounting'];path=self.args.reference/('channels'+str(channels)+'.ogg')
            self.freeze(path,Path('sources/reference')/path.name,'complete public multistream fixture')
            table.append(struct.pack('<8I',channels,offset,e['bytes'],10560,9600,e['pre_skip'],e['streams'],e['coupled']))
            bodies.append(path.read_bytes());offset+=e['bytes']
            for filename,pin in row['files'].items():
                need(sha(self.args.reference/filename)==pin['sha256'],'exact measured host fixture/reference identity')
                if filename.endswith('.pcm'):self.freeze(self.args.reference/filename,Path('sources/reference')/filename,'local-only full independent PCM reference')
        blob=self.out/'project/main/family1.bin';blob.write_bytes(struct.pack('<4I',0x46314f47,1,3,32)+b''.join(table)+b''.join(bodies))
        self.artifacts[blob.relative_to(self.out).as_posix()]=sha(blob)
        vendor=self.args.vendor;paths={p for p in vendor.iterdir() if p.is_file()}
        for folder in ('include','src'):paths.update(p for p in (vendor/folder).rglob('*') if p.is_file())
        paths.update(vendor/'lib/esp32'/name for name in common.ARCHIVE_PINS)
        for path in sorted(paths):self.freeze(path,Path('sources/vendor/esp_audio_codec')/path.relative_to(vendor),'exact unchanged public vendor input')
        common.write_json(self.out/'source-manifest.json',self.sources)
    def qualify(self):
        flash=super().qualify();closure=json.loads((self.out/'actual-compiler-closure.json').read_bytes())
        need('pcm_header_gain.h' not in {Path(p).name for p in closure['dependencies']},
             'metadata-only wrapper leaves all synthesis PCM unchanged')
        return flash


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--reference',required=True,type=Path);parser.add_argument('--build-timeout',type=int,default=1200)
    parser.add_argument('--qemu-timeout',type=int,default=1200);parser.add_argument('--preflight-only',action='store_true')
    args=parser.parse_args();args.output=args.output.resolve();args.reference=args.reference.resolve()
    need(sys.platform=='win32' and args.output.is_relative_to(ROOT/'.build') and not args.output.exists(),'fresh native diagnostic output')
    need(args.reference.is_relative_to(ROOT/'.build') and 1<=args.build_timeout<=1200 and 1<=args.qemu_timeout<=1200,'local reference and bounded process deadlines')
    reference=json.loads((args.reference/'report.json').read_bytes());need(reference['passed'] and reference['completed'] and
        reference['all_source_bindings_current'] and reference['data_tests']['cases']==18 and reference.get('libogg_version') and
        all(len(row.get('creator_libogg_checks',[]))==2 for row in reference['fixtures'].values()),
        'complete independently measured host fixtures and creator container controls')
    for row in reference['sources']:
        need(sha(ROOT/row['path'])==sha(args.reference/row['snapshot'])==row['sha256'],'current exact host preparation closure')
    need(sha(MAIN/'ogg_playback.h')==WRAPPER_SHA,'frozen actual metadata-only gain wrapper')
    args.idf=REPO/'.idf/v6.0.2';args.idf_tools=REPO/'.idf/tools-v6.0.2';args.idf_python=args.idf_tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    args.vendor=REPO/'.idf/esp-adf-libs/esp_audio_codec';args.qemu=ROOT/'.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
    args.rom=Path('C:/Work/QEMU-ESP32/pc-bios');args.git=Path(shutil.which('git.exe') or shutil.which('git') or '');args.powershell=Path(shutil.which('pwsh.exe') or '')
    need(all(p.is_file() for p in (args.idf/'tools/idf.py',args.idf/'export.ps1',args.idf_python,args.qemu,args.git,args.powershell,PROJECT/'sdk-build.ps1')),'installed native tools')
    need(sha(args.qemu)==common.QEMU_SHA and all(sha(args.vendor/'lib/esp32'/name)==pin for name,pin in common.ARCHIVE_PINS.items()),'pinned emulator and LX6 public vendor archives')
    if args.preflight_only:print(json.dumps(dict(preflight=True,target_executed=False)));return 0
    args.output.mkdir(parents=True);campaign=Campaign(args,reference['fixtures'])
    try:
        campaign.save();campaign.verify_repositories();campaign.freeze_sources()
        text=(args.output/'project/sdkconfig.common.defaults').read_text()
        (args.output/'project/sdkconfig.defaults').write_text('CONFIG_IDF_TARGET="esp32"\nCONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y\n# CONFIG_FREERTOS_UNICORE is not set\n'+text,encoding='utf-8')
        for path in (args.idf_python,args.qemu,args.git,args.powershell,*args.rom.glob('esp32-v3-rom*.bin')):campaign.bind_runtime(path)
        print('FROZEN family1 sources; starting SDK build',flush=True)
        campaign.run_command('build',[args.powershell,'-NoProfile','-NonInteractive','-File',args.output/'project/sdk-build.ps1','-Campaign',args.output,
            '-SdkDirectory',args.idf,'-ToolsDirectory',args.idf_tools,'-PythonExecutable',args.idf_python,'-Target','esp32'],args.build_timeout)
        flash=campaign.qualify();print('SDK terminal zero; starting public family1 QEMU observations',flush=True)
        log=campaign.run_command('qemu',[args.qemu,'-audiodev','none,id=quiet','-M','esp32,audiodev=quiet','-smp','2','-L',args.rom,'-display','none',
            '-monitor','none','-serial','stdio','-no-reboot','-snapshot','-nic','none','-drive','file='+str(flash)+',if=mtd,format=raw'],args.qemu_timeout)
        campaign.report['measurements']=parse_log(log+'\n'+(args.output/'qemu.stderr.log').read_text(errors='replace'),reference['fixtures'],args.reference,args.output)
        need(campaign.verify_inputs(),'all consumed source/tool/artifact bindings current after execution')
        campaign.report.update(passed=True,completed=True);print(json.dumps(dict(passed=True,diagnostic_only=True,cases=12,capture=args.output.relative_to(ROOT).as_posix())));return 0
    except Exception as error:
        campaign.report.update(passed=False,completed=False,failure_type=type(error).__name__,failure=str(error));print(json.dumps(dict(passed=False,failure=str(error))));return 1
    finally:campaign.save()


if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
