"""Actual public AAC-Plus application tasks with complete same-vendor PCM contracts.

Preparation can run while production evolves. No production source is frozen
until a full native invocation; coordinate that invocation with the source
owners. No independent codec-conformance or physical-audio claim is made.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent if ROOT.parent.name == '.worktree' else ROOT
HARNESS = ROOT / 'tests/target/cyd_aac_playback_task_qemu'
MAIN = Path('idf/esp32-cyd2usb-native/main')
MAIN_TUS = ('audio_service.c', 'native_state.c', 'native_health.c', 'decoder_registration.c', 'native_audio_output.c', 'native_output_metrics.c')
SDK_COMMIT = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
VENDOR_COMMIT = '67b8d0e98f58c774b8652480893037273190e8dc'
ARCHIVE_PINS = {
    'libesp_audio_codec.a': '92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58',
    'libesp_audio_simple_dec.a': 'ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6',
}
QEMU_SHA = '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d'
PUBLIC=ROOT/'tests/results/cyd-aac-public-config-20261101'
PUBLIC_MANIFEST_SHA='f22687d4e404e0c45672f225322827ffb54061795b21acb96ff3045f4928a23d'
PUBLIC_ARCHIVE_SHA='3a8b1eceb58eb5b2560d1bf763823b1378177780d151d60bc5d167225c17c1af'
CONTRACT=ROOT/'tests/prepare-cyd-aac-playback-contract.py'
SOURCE_RELEASE_SHA='73599ab651a72f153e777bc47dec5d816e1e38224e0795195db426da11c1d3e7'

def need(value,reason):
    if not value:raise ValueError(reason)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def prepare_contract():
    spec=importlib.util.spec_from_file_location('current_public_AAC_task_contract',CONTRACT)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.contracts()


def reference_header(contract):
    header=['#pragma once','extern const uint8_t aac_fixture_start[] asm("_binary_fixtures_bin_start");','extern const uint8_t aac_fixture_end[] asm("_binary_fixtures_bin_end");']
    entries=[]
    for row in contract['fixtures']:
        entries.append('{"'+row['name']+'",aac_fixture_start+'+str(row['blob_offset'])+','+str(row['bytes'])+','+str(row['hold_offset'])+','+str(row['pcm_bytes'])+','+str(row['rate'])+','+str(row['channels'])+','+str(row['bits'])+',"'+row['pcm_sha256']+'"}')
    header.append('static const entry_t entries[]={'+','.join(entries)+'};')
    base=[]
    for row in contract['fixtures']:
        base.append('{"AAC'+str(row['id'])+'",{'+str(row['id'])+',0},1,0,'+str(row['id'])+',false}')
    header.append('static const fixture_t base_fixtures[]={'+','.join(base)+'};')
    observe=[]
    for index,row in enumerate(contract['continuous_observations']):
        observe.append('{"'+row['name']+'",{'+','.join(str(value) for value in row['parts'])+'},2,0,'+str(6+index)+',true}')
    header.append('static const fixture_t observation_fixtures[]={'+','.join(observe)+'};')
    return '\n'.join(header)+'\n'


def fields(line,tag):
    pairs=[part.split('=',1) for part in line[len(tag)+1:].split()]
    need(pairs and all(len(pair)==2 for pair in pairs) and len({pair[0] for pair in pairs})==len(pairs),'complete unique public observation fields')
    words={'fixture','name','id','sha256','stage'}
    row={}
    for key,value in pairs:
        if key in words:row[key]=value
        else:
            need(re.fullmatch(r'-?\d+',value),'strict actual integer observation');row[key]=int(value)
    return row


def validate_log(log,contract):
    """Recount whole actual public API/task observations, without codec claims."""
    log=log.replace('\r\n','\n')
    need(not re.search(r'CYD_AAC_TASK_FAILURE|Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack (?:smashing|overflow)',log,re.I),
         'no unexpected reference/task/runtime fault')
    prefix='CYD_AAC_'
    need(not any(prefix in line and not line.startswith(prefix) for line in log.splitlines()),'intact actual observation records')
    lines=[line for line in log.splitlines() if line.startswith(prefix)]
    need(lines and lines[0]=='CYD_AAC_TASK_BOOT sdk=v6.0.2 actual_tasks=1 actual_output=1 public_config_only=1 hardware=0',
         'actual current complete application/public-reference scope')
    references=[];reference_runs=[];reference_complete=None;profiles=[];cases=[];pcm_runs=[];controls=[];infos=[];state_infos=[];memory=[];fixtures=[];observers=[];complete=None
    for line in lines[1:]:
        tag=line.split(' ',1)[0]
        if tag=='CYD_AAC_TASK_PROFILE':profiles.append(line);continue
        row=fields(line,tag)
        if tag=='CYD_AAC_REFERENCE_CASE':references.append(row)
        elif tag=='CYD_AAC_REFERENCE_RUN':reference_runs.append(row)
        elif tag=='CYD_AAC_REFERENCE_COMPLETE':need(reference_complete is None,'one genuine reference cleanup');reference_complete=row
        elif tag=='CYD_AAC_TASK_CASE':cases.append(row)
        elif tag=='CYD_AAC_TASK_PCM_RUN':pcm_runs.append(row)
        elif tag=='CYD_AAC_TASK_INFO':infos.append(row)
        elif tag=='CYD_AAC_TASK_STATE_INFO':state_infos.append(row)
        elif tag=='CYD_AAC_TASK_MEMORY':memory.append(row)
        elif tag=='CYD_AAC_TASK_FIXTURE':fixtures.append(row)
        elif tag.startswith('CYD_AAC_TASK_CONTROL_'):controls.append((tag.removeprefix('CYD_AAC_TASK_CONTROL_'),row))
        elif tag.startswith('CYD_AAC_TASK_OBS_'):observers.append((tag.removeprefix('CYD_AAC_TASK_OBS_'),row))
        elif tag=='CYD_AAC_TASK_COMPLETE':need(complete is None and line==lines[-1],'one genuine final task record');complete=row
        else:need(False,'known current public AAC observation')
    need(profiles==['CYD_AAC_TASK_PROFILE role=stream core=0 priority=3 stack=6144','CYD_AAC_TASK_PROFILE role=decode core=1 priority=5 stack=16384','CYD_AAC_TASK_PROFILE role=output core=1 priority=6 stack=4096'],
         'all original application task creation bindings')
    need(reference_complete is not None and next(i for i,line in enumerate(lines) if line.startswith('CYD_AAC_REFERENCE_COMPLETE '))<
         next(i for i,line in enumerate(lines) if line.startswith('CYD_AAC_TASK_PROFILE ')),
         'continuous public reference ownership and cleanup precede all application tasks')
    need([row['index'] for row in references]==list(range(10)) and reference_complete and reference_complete['cases']==10 and
         reference_complete['production_tasks']==reference_complete['private_abi']==reference_complete['reset_hooks']==0 and
         reference_complete['heap_integrity']==1 and reference_complete['retained']==reference_complete['registry_before']-reference_complete['heap_free'],
         'ten genuine public references and exact public registration ownership/retention')
    need(0<reference_complete['stack_free']<=16384 and reference_complete['heap_free']>0,'actual reference worker resources')
    names=['AAC'+str(i) for i in range(6)]+[row['name'] for row in contract['continuous_observations']]
    encoded={i:row['bytes'] for i,row in enumerate(contract['fixtures'])}
    encoded.update({i+6:row['bytes'] for i,row in enumerate(contract['continuous_observations'])})
    by_reference={row['index']:row for row in references}
    for ref in references:
        index=ref['index'];runs=[row for row in reference_runs if row['index']==index]
        need(ref['name']==names[index] and ref['observed_only']==int(index>=6) and ref['core']==1 and ref['priority']==3 and
             0<=ref['input']<=encoded[index] and ref['calls']>0 and ref['runs']==len(runs) and
             [row['run'] for row in runs]==list(range(len(runs))) and sum(row['pcm_bytes'] for row in runs)==ref['pcm_bytes'] and
             re.fullmatch('[a-f0-9]{64}',ref['sha256']),'complete genuine continuous-reference geometry/hash record')
        need(all(row['rate']>0 and row['channels'] in (1,2) and row['bits']==16 and row['pcm_bytes']>0 and
                 row['pcm_bytes']%(row['channels']*2)==0 and re.fullmatch('[a-f0-9]{64}',row['sha256']) for row in runs),
             'complete per-geometry continuous public PCM runs')
        if ref['success']:need(ref['drained']==1 and ref['input']==encoded[index] and ref['result']==0,'genuine whole-input public EOS/drain')
        if index<6:
            source=contract['fixtures'][index]
            need(ref['success']==1 and len(runs)==1 and ref['pcm_bytes']==source['pcm_bytes'] and ref['sha256']==source['pcm_sha256'] and
                 runs[0]['rate']==source['rate'] and runs[0]['channels']==source['channels'],'all6 complete bases match committed same-vendor contracts')
    expected=[]
    for index in range(6):expected.extend([('AAC'+str(index),'T0',0),('AAC'+str(index),'T1',0),('AAC'+str(index),'T2',0),
        ('AAC'+str(index),'FULL',1),('AAC'+str(index),'FULL',2),('AAC'+str(index),'FULL',3)])
    expected.extend((row['name'],'OBSERVATION',schedule) for row in contract['continuous_observations'] for schedule in range(3))
    need([(row['fixture'],row['id'],row['schedule']) for row in cases]==expected and len(cases)==48,'all36 complete base/lifecycle and12 continuous public observations')
    expected_runs=[]
    for case in cases:
        index=case['reference'];ref=by_reference[index]
        need(case['fixture']==names[index] and case['observed_only']==int(index>=6) and case['expected_success']==ref['success'] and
             case['pcm_bytes']==ref['pcm_bytes'] and case['sha256']==ref['sha256'] and case['runs']==ref['runs'] and
             case['header_zero']==1 and case['opens']==case['closes']==case['http_cleanup'] and 0<=case['input_delivered']<=encoded[index],
             'actual complete PCM/geometry/owners match their continuous public reference')
        if ref['success']:need(case['input_delivered']==encoded[index] and case['writes']>0 and case['driver_pcm_bytes']>0,'entire successful original input and real forwarded rendering')
        if case['id']=='T0':need(case['ordered_eof']==1,'real ordered base EOF')
        if case['id']=='T1':need(case['stop_reopen']==case['discard_after_request']==case['stop_quiet']==1 and 0<case['partial_pcm']<ref['pcm_bytes'],'genuine partial Stop/discard/quiet/reopen')
        if case['id']=='T2':need(all(case[key]==1 for key in ('maintenance_resume','held_quiet','play_blocked','token_consumed','stale_rejected')) and 0<case['partial_pcm']<ref['pcm_bytes'],'genuine partial maintenance/token/stale/resume')
        expected_runs.extend(dict(fixture=case['fixture'],index=run['run'],rate=run['rate'],channels=run['channels'],bits=run['bits'],pcm_bytes=run['pcm_bytes'],sha256=run['sha256']) for run in reference_runs if run['index']==index)
    need(pcm_runs==expected_runs,'every actual queued source PCM run matches the genuine continuous public-handle run')
    need(complete and all(complete[key]==value for key,value in [('cases',48),('base_cases',36),('public_observations',12),('reference_cases',10),
         ('opens',60),('closes',60),('http_cleanup',60),('initial_capacity_checks',60),('output_flushes',48),('heap_integrity',1),('hardware',0),
         ('independent_codec_conformance',0),('private_abi',0),('reset_hooks',0)]) and complete['resizes']==complete['retries'] and
         complete['driver_created']==complete['driver_deleted']>0 and complete['driver_writes']>0 and complete['preloads']>0 and complete['header_zero_stamps']==complete['legacy_layout_stamps']>0,
         'actual full application/public ownership, zero-header metadata and hardware-seam census')
    need(len(infos)==complete['public_infos'] and len(state_infos)==complete['public_state_infos'] and 0<len(state_infos)<=len(infos) and
         all(row['format_is_pcm']==1 and row['source_AOT_inferred']==0 and (not row['state_current'] or row['pcm_label']==1) for row in state_infos) and
         any(row['state_current']==row['pcm_label']==1 for row in state_infos),'truthful actual confirmed-PCM state/formatter publication, separate from queued output geometry')
    observed_failures=sum(not by_reference[case['reference']]['success'] for case in cases)
    need(complete['observed_public_failures']==observed_failures,'stock public limitations observed without nominal conformance claims')
    for role,size in [('stream',6144),('decode',16384),('output',4096)]:need(0<complete[role+'_stack_free']<=size,'actual original owner stack margin')
    need(0<complete['heap_min']<=complete['heap_free'] and 0<complete['largest_internal']<=complete['heap_free'],'actual global heap/block observations')
    need(len(memory)==60 and all(0<row['heap_min']<=row['heap_free'] and 0<row['largest_internal']<=row['heap_free'] for row in memory),'every EOF/Stop/HELD resource observation')
    need(len(fixtures)==6,'all original fixture/early-frame boundary observations')
    for row,source in zip(fixtures,contract['fixtures']):need(row==dict(fixture='AAC'+str(source['id']),encoded=source['bytes'],hold_offset=source['hold_offset'],hold_after_frame=3),'independent original ADTS hold boundary')
    discards=[row for tag,row in controls if tag=='DISCARD']
    need([row['sequence'] for row in discards]==list(range(1,len(discards)+1)) and all(row['core']==1 and row['priority']==6 and row['real_returned']==1 for row in discards),'genuine unique real output-owner discard completions')
    held=[row for tag,row in controls if tag=='TRANSPORT_HELD']
    need(len(held)==12 and [row['fixture'] for row in held]==[name for name in names[:6] for _ in range(2)],'both cancellations genuinely hold every short original stream before HTTP EOF')
    for row in held:
        source=contract['fixtures'][int(row['fixture'][3:])]
        need(row['position']==row['boundary']==source['hold_offset'] and row['encoded']==source['bytes'] and row['position']<row['encoded'] and
             row['genuine_read']==1 and row['core']==0 and row['priority']==3,'actual stream-owner held read at independently counted ADTS boundary')
    for name in names[:6]:
        parts={tag:[row for found,row in controls if found==tag and row['fixture']==name] for tag in ('STOP_REQUEST','STOP_RETURN','STOP_QUIET')}
        need(all(len(rows)==1 for rows in parts.values()),'one exact public Stop request/return/quiet interval')
        request,returned,quiet=(parts[tag][0] for tag in ('STOP_REQUEST','STOP_RETURN','STOP_QUIET'))
        matching=[row for row in discards if row['sequence']==request['before_sequence']+1]
        need(len(matching)==1,'one real discard completes after Stop request');discard=matching[0]
        need(request['before_generation']+1==returned['stop_generation']==quiet['stop_generation'] and request['time_us']<=returned['time_us']<=quiet['time_us'] and
             request['time_us']<=discard['time_us']<=quiet['time_us'] and discard['fixture']==name and quiet['discard_sequence']==discard['sequence'] and
             quiet['discard_snapshot_generation']==discard['snapshot_generation'],'real discard sequence/timing ownership without invented generation labels')
        need(quiet['live_clients']==quiet['live_decoders']==quiet['input_ready']==quiet['input_reading']==quiet['input_writing']==0 and
             quiet['input_available']==quiet['input_leased']==quiet['no_eof']==1 and quiet['quiet_ticks']>=25 and
             all(quiet[key]==discard[key] for key in ('pcm_bytes','driver_pcm_bytes','writes','driver_writes')),'all owners and actual PCM/driver counters remain quiet before reopening')
    active=None;pending=None;handles=[];last_calls=0;resizes=[];retries=[];public_errors=[]
    for tag,row in observers:
        if tag=='OPEN':
            need(active is None and pending is None and row['instance']==len(handles)+1 and row['generation']>0 and row['cfg_size']>0 and row['aac_plus']==1 and row['no_adts_header']==0,'one genuine public AAC-Plus configured owner')
            active=dict(fixture=row['fixture'],instance=row['instance'],generation=row['generation'],offset=last_calls,initial=None,resizes=0,retries=0)
        else:
            need(active and row['instance']==active['instance'] and row['fixture']==active['fixture'],'public process observation belongs to real live handle')
            if tag=='INITIAL':
                need(active['initial'] is None and row['call']==1 and row['global_call']==active['offset']+1 and row['capacity']==12288,'unchanged production initial output capacity')
                active['initial']=row['capacity']
            elif tag=='RESIZE':
                need(pending is None and row['result']==-8 and row['decoded_size']==0 and 0<=row['consumed']<=row['raw_len'] and row['needed_size']>row['capacity'],'genuine public buffer growth')
                pending=row;active['resizes']+=1;resizes.append(row)
            elif tag=='RETRY':
                need(pending and row['call']==pending['call']+1 and row['global_call']==pending['global_call']+1 and row['capacity']==pending['needed_size'] and row['raw_len']==pending['raw_len']-pending['consumed'] and row['eos']==pending['eos'] and row['arguments_advanced_once']==1 and row['result']==0,'real next-call retry advances consumed bytes once')
                pending=None;active['retries']+=1;retries.append(row)
            elif tag=='PROCESS_ERROR':
                need(row['result']==row['reference_result']!=0,'genuine observed stock public error matches the continuous reference');public_errors.append(row)
            elif tag=='CLOSE':
                need(pending is None and active['initial'] and row['calls']>0 and row['global_calls']==active['offset']+row['calls'] and row['resizes']==active['resizes']==row['retries']==active['retries'],'complete real public close/process/retry census')
                active.update({key:row[key] for key in ('calls','input_consumed','eos_calls','drained','last_capacity')});handles.append(active);last_calls=row['global_calls'];active=None
            else:need(False,'known current public process observation')
    need(active is None and pending is None and len(handles)==60 and last_calls==complete['process_calls'] and len(resizes)==complete['resizes'] and len(retries)==complete['retries'],'all60 actual public decoders close with exact process counts')
    expected_owners=[name for name in names[:6] for _ in range(8)]+[name for name in names[6:] for _ in range(3)]
    need([row['fixture'] for row in handles]==expected_owners,'actual lifecycle/full/observation decoder ownership order')
    for index,handle in enumerate(handles):
        ref_index=names.index(handle['fixture'])
        cancelled=index<48 and index%8 in (1,3)
        if not cancelled and by_reference[ref_index]['success']:
            need(handle['input_consumed']==encoded[ref_index] and handle['eos_calls']>0 and handle['drained']==1,'all original encoded bytes consumed and genuine public EOS drained')
    return dict(cases=cases,pcm_runs=pcm_runs,public_references=references,public_reference_runs=reference_runs,
        reference_complete=reference_complete,complete=complete,fixtures=fixtures,memory=memory,public_handles=handles,
        public_controls=controls,public_infos=infos,public_state_infos=state_infos,public_errors=public_errors,
        resize_observations=resizes,retry_observations=retries,same_vendor_integration_oracle=True,
        independent_codec_conformance=False,private_abi=False,compact_owner_ported=False,physical_output_qualified=False)

class Campaign:
    def __init__(self, args):
        self.args, self.out = args, args.output
        self.sources, self.runtime, self.artifacts = {}, {}, {}
        self.runtime_paths = {}
        self.report = dict(passed=False, completed=False, commands=[], actual_audio_service_tu=True, actual_output_tu=True,
                           actual_rtos=True, target_executed=False, production_firmware=False,
                           physical_device=False, external_network=False, private_codec_abi=False,
                           custom_decoder=False, oom_injection=False, output_backpressure=False, same_vendor_AAC_integration_oracle=True,
                           full_pcm_independent_oracle=False, performance_or_radio_resource_claim=False)
        self.environment = os.environ.copy()
        self.environment.update(GIT_OPTIONAL_LOCKS='0', PYTHONNOUSERSITE='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8')


    def save(self):
        write_json(self.out / 'report.json', self.report)


    def bind_runtime(self, path):
        path=Path(path)
        key='runtime-path-redacted:'+path.name if re.search(r'(?i)[/\\]Users[/\\]',str(path)) else str(path)
        self.runtime[key]=sha(path)
        self.runtime_paths[key]=path


    def freeze(self, original, relative, role='frozen source input'):
        original = Path(original).resolve()
        destination = self.out / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        body = original.read_bytes()
        destination.write_bytes(body)
        digest = hashlib.sha256(body).hexdigest()
        need(sha(original) == digest, 'source immutable while freezing')
        self.sources[str(original)] = dict(snapshot=relative.as_posix(), sha256=digest, bytes=len(body), role=role)


    def run_command(self, name, argv, timeout=60):
        argv = list(map(str, argv))
        def redacted(value):
            return 'runtime-path-redacted:' + Path(value).name if re.search(r'(?i)[/\\]Users[/\\]', value) else value
        row = dict(name=name, argv=[redacted(v) for v in argv], state='starting', timeout_seconds=timeout)
        self.report['commands'].append(row)
        self.save()
        child, started = None, time.monotonic()
        try:
            with (self.out / (name + '.stdout.log')).open('xb') as stdout, (self.out / (name + '.stderr.log')).open('xb') as stderr:
                child = subprocess.Popen(argv, cwd=self.out, env=self.environment, stdin=subprocess.DEVNULL,
                                         stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(state='running', pid=child.pid)
                if name == 'qemu': self.report['target_executed'] = True
                self.save()
                child.wait(timeout=timeout)
                row.update(state='complete', exit_status=child.returncode)
        except BaseException as error:
            row.update(state='failed', error_type=type(error).__name__, winerror=getattr(error, 'winerror', None))
            raise RuntimeError('owned native command failed: ' + name) from None
        finally:
            if child is not None and child.poll() is None:
                stopped = subprocess.run(['taskkill.exe', '/PID', str(child.pid), '/T', '/F'], capture_output=True,
                                         timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(state='forced_stop_nonpass', tree_stop_returncode=stopped.returncode)
                if child.poll() is None: child.kill()
                child.wait(timeout=15)
            row['elapsed_seconds'] = time.monotonic() - started
            if child is not None: row['exit_status'] = child.poll()
            for stream in ('stdout', 'stderr'):
                path = self.out / (name + '.' + stream + '.log')
                row[stream + '_sha256'] = sha(path) if path.exists() else None
            self.save()
        need(row['state'] == 'complete' and row['exit_status'] == 0, 'actual command terminal zero: ' + name)
        return (self.out / (name + '.stdout.log')).read_text('utf-8', errors='replace').replace('\r\n', '\n')


    def freeze_sources(self):
        release=json.loads(self.args.source_release.read_bytes())
        need(sha(self.args.source_release)==SOURCE_RELEASE_SHA and len(release['files'])==12,
             'exact root-authorized final source/API release')
        for relative,pin in release['files'].items():
            path=ROOT/relative
            need(sha(path)==pin['sha256'] and path.stat().st_size==pin['bytes'],
                 'every released production source is current before snapshot')
        self.freeze(self.args.source_release,Path('sources/reference/production-source-release.json'),
                    'root-authorized complete source/API release, captured without modifying production')
        main = ROOT / MAIN
        paths = {main / name for name in MAIN_TUS}
        paths.update(main / name for name in ('CMakeLists.txt', 'Kconfig.projbuild', 'network_service.c', 'native_audio_output.c'))
        paths.update(p for p in main.rglob('*.h') if 'vorbis_repair' not in p.parts and not p.name.startswith(('vorbis_repair', 'aac_')))
        for component in ('native_stream', 'native_network_power', 'native_audio_settings', 'native_audio_normalizer'):
            paths.update(p for p in (ROOT / 'idf/components' / component).rglob('*') if p.is_file())
        paths.update(p for p in (ROOT / 'idf/components/native_wifi_store/include').rglob('*') if p.is_file())
        paths.add(ROOT / 'idf/components/audio_level_led/audio_level_led.h')
        paths.add(main / 'aac_public_config.h')
        paths.update(ROOT/'yoRadio/src/audioI2S'/name for name in ('AudioNormalizer.cpp','AudioNormalizer.h'))
        for path in sorted(paths):
            self.freeze(path, Path('sources/repository') / path.relative_to(ROOT),
                        'whole production TU' if path.name in MAIN_TUS else 'repository helper/header; actual use established by compiler closure')
        vendor = self.args.vendor
        vendor_paths = {p for p in vendor.iterdir() if p.is_file()}
        for folder in ('src', 'include'):
            vendor_paths.update(p for p in (vendor / folder).rglob('*') if p.is_file())
        vendor_paths.update(vendor / 'lib/esp32' / name for name in ARCHIVE_PINS)
        for path in sorted(vendor_paths):
            self.freeze(path, Path('sources/vendor/esp_audio_codec') / path.relative_to(vendor), 'public vendor input or exact target archive')
        for path in sorted(HARNESS.rglob('*')):
            if path.is_file(): self.freeze(path, Path('sources/harness') / path.relative_to(HARNESS), 'task harness')
        self.freeze(Path(__file__), Path('sources/controller.py'), 'campaign controller')
        self.reference()
        for relative,pin in release['files'].items():
            bound=self.sources[str((ROOT/relative).resolve())]
            need(bound['sha256']==pin['sha256'] and bound['bytes']==pin['bytes'],
                 'all twelve released source bytes joined to the actual frozen input manifest')
        self.report['production_source_release_sha256']=SOURCE_RELEASE_SHA
        write_json(self.out / 'source-manifest.json', self.sources)


    def verify_repositories(self, suffix=''):
        for name, directory, revision in (('sdk', self.args.idf, SDK_COMMIT), ('vendor', self.args.vendor.parent, VENDOR_COMMIT)):
            git = [self.args.git, '-c', 'core.longpaths=true', '-C', directory]
            need(self.run_command(name + '-head' + suffix, git + ['rev-parse', 'HEAD']).strip() == revision, 'pinned ' + name + ' revision')
            need(not self.run_command(name + '-clean' + suffix, git + ['status', '--porcelain', '--untracked-files=no']).strip(),
                 'clean installed ' + name + ' repository')


    def compiler_closure(self, commands, ninja):
        lookup = {str((self.out / row['snapshot']).resolve()).casefold(): original for original, row in self.sources.items()}
        used, dependencies = [], {}
        for row in commands:
            source = Path(row['file']).resolve()
            if not source.is_relative_to(self.out / 'sources'): continue
            copied = dict(row)
            text = self.run_command('compiler-deps-' + str(len(used)), [ninja, '-C', self.out / 'build', '-t', 'deps', row['output'].replace('\\', '/')])
            need('(VALID)' in text and '#deps ' in text, 'actual GCC/Ninja dependency record')
            actual = []
            for line in text.splitlines():
                if not line.startswith('    '): continue
                path = Path(line.strip())
                path = path.resolve() if path.is_absolute() else (self.out / 'build' / path).resolve()
                need(path.is_file(), 'actual compiler dependency exists')
                original = lookup.get(str(path).casefold())
                if original is None:
                    original = str(path)
                    if original not in self.sources:
                        relative = Path('sources/compiler-dependencies') / hashlib.sha256(str(path).encode()).hexdigest()[:16] / path.name
                        self.freeze(path, relative, 'actual SDK/toolchain/compiler dependency')
                dependencies[str(path)] = dict(sha256=sha(path), manifest_original=original)
                actual.append(str(path))
            need(actual, 'nonempty actual compiler dependency closure')
            copied['actual_dependency_paths'] = actual
            used.append(copied)
            object_path = Path(row['output'])
            if not object_path.is_absolute(): object_path = self.out / 'build' / object_path
            need(object_path.is_file() and object_path.resolve().is_relative_to(self.out / 'build'), 'actual selected object file')
            self.artifacts[object_path.relative_to(self.out).as_posix()] = sha(object_path)
            stack = object_path.with_suffix('.su')
            if stack.exists(): self.artifacts[stack.relative_to(self.out).as_posix()] = sha(stack)
        need(all(any(Path(row['file']).name == name for row in used) for name in MAIN_TUS), 'all six complete production translation units')
        write_json(self.out / 'source-manifest.json', self.sources)
        write_json(self.out / 'actual-compiler-closure.json', dict(translation_units=used, dependencies=dependencies,
            scope='Actual GCC/Ninja dependencies of every selected production, shared component, public vendor and harness TU'))
        self.report.update(actual_translation_units=len(used), actual_compiler_dependencies=len(dependencies))


    def qualify_build(self):
        build = self.out / 'build'
        desc = json.loads((build / 'project_description.json').read_bytes())
        need(desc['target'] == 'esp32' and Path(desc['idf_path']).resolve() == self.args.idf, 'actual pinned ESP32 SDK target')
        config = json.loads((build / 'config/sdkconfig.json').read_bytes())
        for key in ('HEAP_POISONING_LIGHT', 'FREERTOS_CHECK_STACKOVERFLOW_CANARY', 'COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE',
                    'ESP_TASK_WDT_EN', 'ESP_TASK_WDT_INIT', 'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0', 'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1',
                    'YORADIO_ADAPTIVE_INPUT_BUFFER', 'YORADIO_FRAME_ROUTER', 'YORADIO_STREAM_CONFIRM', 'YORADIO_INPUT_TAIL_COALESCE',
                    'AUDIO_DECODER_AAC_SUPPORT', 'YORADIO_AAC_DECODER_ESPRESSIF', 'YORADIO_AAC_PLUS', 'YORADIO_NATIVE_AUDIO_OUTPUT_PDM', 'YORADIO_OGG_TIMELINE'):
            need(config.get(key) is True, 'actual diagnostic configuration: ' + key)
        for key in ('FREERTOS_UNICORE', 'YORADIO_FLAC_DECODER_CUSTOM', 'YORADIO_VORBIS_REPAIR', 'YORADIO_HTTP_REQUEST_BUFFER_RELEASE'):
            need(not config.get(key, False), 'unselected incompatible/custom feature: ' + key)
        need(config['FREERTOS_HZ'] == 1000 and config.get('YORADIO_INPUT_PREFILL_MS', 0) == 0, 'original scheduler and explicit test prefill profile')
        commands = json.loads((build / 'compile_commands.json').read_bytes())
        need(not any(any(part == 'vorbis_repair' or part == 'custom_flac' or part.startswith('native_vorbis')
                         for part in Path(row['file']).parts) for row in commands),
             'no private repair or custom decoder translation unit selected')
        for name in MAIN_TUS:
            source = (self.out / 'sources/repository' / MAIN / name).resolve()
            rows = [row for row in commands if Path(row['file']).resolve() == source]
            need(len(rows) == 1 and '-include' not in rows[0]['command'], 'whole unchanged production TU: ' + name)
        compiler = Path(desc['c_compiler'])
        nm = compiler.with_name(compiler.name.replace('gcc', 'nm'))
        cache = (build / 'CMakeCache.txt').read_text()
        ninja = Path(re.search(r'^CMAKE_MAKE_PROGRAM:[A-Z_]+=(.+)$', cache, re.M).group(1).strip())
        for path in (compiler, nm, ninja): self.bind_runtime(path)
        self.run_command('compiler-version', [compiler, '--version'])
        self.compiler_closure(commands, ninja)
        closure=json.loads((self.out/'actual-compiler-closure.json').read_bytes())
        used_headers={Path(path).name for path in closure['dependencies']}
        need({'ogg_playback.h','ogg_page_input.h','opus_pcm_trim.h','ogg_opus_timeline.h','aac_public_config.h','pcm_header_gain.h','pcm_channel_layout.h','pcm_speaker_mix.h','native_audio_settings.h','native_audio_normalizer.h','AudioNormalizer.h'}<=used_headers,
             'actual GCC closure consumes public AAC configuration and actual output/settings/normalizer headers')
        elf = (build / desc['app_elf']).resolve()
        app = (build / desc['app_bin']).resolve()
        need(elf.is_relative_to(build) and app.is_relative_to(build) and elf.read_bytes()[:6] == b'\x7fELF\x01\x01' and
             int.from_bytes(elf.read_bytes()[18:20], 'little') == 94, 'actual LX6 ELF32 image')
        symbols = self.run_command('symbols', [nm, '-n', '--defined-only', elf])
        for name in ('decoder_task', 'stream_task', 'output_task', 'audio_service_start', 'decoder_register_codecs',
                     'adaptive_input_receive', 'xRingbufferReceive', 'esp_audio_simple_dec_process',
                     '__wrap_esp_audio_simple_dec_open', '__wrap_esp_audio_simple_dec_process', '__wrap_esp_audio_simple_dec_close'):
            need(re.search(r'\b' + name + r'$', symbols, re.M), 'linked actual task/public interface: ' + name)
        need(not re.search(r'\b(?:native_vorbis_|custom_flac_|__wrap_(?:vorbis_|floor[01]_|esp_vorbis_|esp_ogg_|media_lib_))[A-Za-z0-9_]*$', symbols, re.M),
             'no private codec repair or custom decoder linked')
        recipe = json.loads((build / 'flasher_args.json').read_bytes())
        need(recipe['extra_esptool_args']['chip'] == 'esp32', 'ESP32 flash recipe')
        flashes = {int(offset, 0): (build / name).resolve() for offset, name in recipe['flash_files'].items()}
        need(set(flashes) == {4096, 32768, 65536} and all(p.is_relative_to(build) for p in flashes.values()),
             'diagnostic bootloader/partition/app only; fixture is embedded')
        flash = self.out / 'qemu-flash.bin'
        argv = [self.args.idf_python, '-m', 'esptool', '--chip', 'esp32', 'merge-bin', '--output', flash,
                '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
        for offset, path in sorted(flashes.items()): argv += [hex(offset), path]
        self.run_command('merge', argv + ['--pad-to-size', '4MB'])
        merged = flash.read_bytes()
        need(len(merged) == 4194304 and all(merged[offset:offset + path.stat().st_size] == path.read_bytes() for offset, path in flashes.items()),
             'exact immutable merged flash bytes')
        artifacts = [elf, app, elf.with_suffix('.map'), flash, self.out / 'sdkconfig',
                     build / 'project_description.json', build / 'flasher_args.json', build / 'compile_commands.json',
                     build / 'config/sdkconfig.json', build / 'config/sdkconfig.h', build / 'CMakeCache.txt', build / 'build.ninja',
                     self.out / 'source-manifest.json', self.out / 'actual-compiler-closure.json', *flashes.values()]
        child = self.out / 'sdk-child.json'
        need(child.is_file(), 'actual SDK child status retained')
        child_result = json.loads(child.read_text('utf-8-sig'))
        need(child_result['exit_status'] == 0 and child_result['pid'] > 0, 'actual SDK child terminal zero')
        artifacts.append(child)
        self.artifacts.update({p.relative_to(self.out).as_posix(): sha(p) for p in artifacts})
        for path in (self.out / 'sources').rglob('*'):
            if path.is_file() and not any(row['snapshot'] == path.relative_to(self.out).as_posix() for row in self.sources.values()):
                self.artifacts[path.relative_to(self.out).as_posix()] = sha(path)
        write_json(self.out / 'execution-bundle.json', dict(sources=self.sources, artifacts=self.artifacts, runtime=self.runtime,
            sdk_commit=SDK_COMMIT, vendor_commit=VENDOR_COMMIT, pcm_reference=self.report['pcm_reference'],
            scope=__doc__, expected_cases=self.report['pcm_reference']))
        self.artifacts['execution-bundle.json'] = sha(self.out / 'execution-bundle.json')
        need(self.verify_inputs(), 'every bound source/tool/image unchanged before target execution')
        self.report['app_bytes'] = app.stat().st_size
        return flash


    def verify_inputs(self):
        failures = []
        for original, row in self.sources.items():
            for path in (Path(original), self.out / row['snapshot']):
                try: unchanged = sha(path) == row['sha256']
                except OSError: unchanged = False
                if not unchanged: failures.append('source:' + row['snapshot'])
        for group, root in ((self.runtime, None), (self.artifacts, self.out)):
            for name, expected in group.items():
                try: unchanged = sha(self.runtime_paths.get(name,Path(name)) if root is None else root / name) == expected
                except OSError: unchanged = False
                if not unchanged: failures.append('runtime-or-artifact:' + Path(name).name)
        self.report['bound_input_failures'] = sorted(set(failures))
        self.report['all_bound_inputs_current'] = not failures
        return not failures


    def execute(self):
        self.out.mkdir(parents=True)
        self.save()
        try:
            self.freeze_sources()
            for path in (self.args.idf_python, self.args.qemu, self.args.powershell, self.args.git, Path(sys.executable).resolve(),
                         self.args.rom / 'esp32-v3-rom.bin', self.args.rom / 'esp32-v3-rom-app.bin', self.args.idf / 'tools/tools.json'):
                self.bind_runtime(path)
            self.verify_repositories()
            self.report['repository_head_at_freeze'] = self.run_command('repository-head',
                [self.args.git, '-c', 'core.longpaths=true', '-C', ROOT, 'rev-parse', 'HEAD']).strip()
            print('Building complete CYD public AAC stream/decoder/output tasks', flush=True)
            self.run_command('build', [self.args.powershell, '-NoProfile', '-NonInteractive', '-File',
                self.out / 'sources/harness/sdk-build.ps1', '-OutputDirectory', self.out, '-IdfDirectory', self.args.idf,
                '-IdfToolsDirectory', self.args.idf_tools, '-IdfPythonExecutable', self.args.idf_python], self.args.build_timeout)
            flash = self.qualify_build()
            print('Starting public AAC continuous reference and actual application tasks', flush=True)
            log = self.run_command('qemu', [self.args.qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet', '-smp', '2',
                '-L', self.args.rom, '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none',
                '-drive', 'file=' + str(flash).replace(',', ',,') + ',if=mtd,format=raw'], self.args.qemu_timeout)
            self.report['measurements']=validate_log(log+'\n'+(self.out/'qemu.stderr.log').read_text(errors='replace'),self.report['pcm_reference'])
            self.verify_repositories('-after')
            need(self.verify_inputs(), 'every bound input unchanged after target execution')
            self.report.update(passed=True, completed=True)
            print('PASS actual public AAC task integration and truthful continuous public observations; independent codec/hardware qualification remains separate', flush=True)
        except BaseException as error:
            self.report.update(passed=False, completed=False, failure_type=type(error).__name__, failure=str(error))
            print(json.dumps(dict(passed=False, failure_type=type(error).__name__, failure=str(error))), file=sys.stderr)
        finally:
            if not self.verify_inputs(): self.report['passed'] = False
            self.save()
        return 0 if self.report['passed'] else 1


    def reference(self):
        contract,blob=prepare_contract()
        need(contract['passed'] and not contract['production_sources_frozen'] and contract['same_vendor_pcm_integration_oracle'],'public same-vendor reference preparation scope')
        self.freeze(CONTRACT,Path('sources/reference/contract-preparer.py'),'read-only committed public AAC contract preparation')
        self.freeze(PUBLIC/'manifest.json',Path('sources/reference/public-manifest.json'),'committed36-case same-vendor native contract manifest')
        self.freeze(PUBLIC/'captures.zip',Path('sources/reference/public-captures.zip'),'original public checkpoint data; not executed as a program')
        for row in contract['fixtures']:
            self.freeze(ROOT/row['path'],Path('sources/fixtures')/row['name'],'complete original public FDK synthetic fixture')
        for name,content in [('reference.h',reference_header(contract).encode()),('fixtures.bin',blob)]:
            path=self.out/'sources/harness/project/main'/name;path.write_bytes(content)
            self.freeze(path,path.relative_to(self.out),'derived exact original fixture view and same-vendor contracts')
        path=self.out/'reference-contract.json';write_json(path,contract)
        self.freeze(path,Path('sources/reference/reference-contract.json'),'actual pure-data contract; no production source freeze in preparation')
        self.report['pcm_reference']=contract


def arguments():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--preflight-only',action='store_true')
    parser.add_argument('--build-timeout',type=int,default=1200)
    parser.add_argument('--qemu-timeout',type=int,default=600)
    parser.add_argument('--source-release',type=Path,default=ROOT/'.build/cyd-aac-source-release-20261101-01.json')
    args=parser.parse_args();args.output=args.output.resolve()
    args.source_release=args.source_release.resolve()
    need(args.output.is_relative_to(ROOT/'.build') and args.output!=ROOT/'.build' and not args.output.exists(),'fresh output strictly in task-local ignored build directory')
    need(1<=args.build_timeout<=1200 and args.qemu_timeout==600,'bounded SDK and fixed600s whole-QEMU diagnostic deadline')
    args.idf=REPO/'.idf/v6.0.2';args.idf_tools=REPO/'.idf/tools-v6.0.2'
    args.idf_python=args.idf_tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    args.vendor=REPO/'.idf/esp-adf-libs/esp_audio_codec';args.qemu=ROOT/'.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
    args.rom=Path('C:/Work/QEMU-ESP32/pc-bios');args.powershell=Path(shutil.which('pwsh.exe') or '');args.git=Path(shutil.which('git.exe') or shutil.which('git') or '')
    contract,unused=prepare_contract()
    if not args.prepare_only:
        need(args.source_release.is_file() and sha(args.source_release)==SOURCE_RELEASE_SHA,
             'exact root-authorized source/API release exists')
        release=json.loads(args.source_release.read_bytes())
        need(len(release['files'])==12 and all(sha(ROOT/relative)==pin['sha256'] and
             (ROOT/relative).stat().st_size==pin['bytes'] for relative,pin in release['files'].items()),
             'all twelve source/API release files are unchanged before any native action')
        need(sys.platform=='win32','installed Windows SDK/QEMU launcher')
        required=[args.idf/'export.ps1',args.idf/'tools/idf.py',args.idf_python,args.qemu,args.powershell,args.git,args.rom/'esp32-v3-rom.bin',args.rom/'esp32-v3-rom-app.bin',HARNESS/'project/main/main.cpp',HARNESS/'sdk-build.ps1']
        need(all(path.is_file() for path in required),'complete installed native dependencies and prepared target')
        need(sha(args.qemu)==QEMU_SHA and all(sha(args.vendor/'lib/esp32'/name)==digest for name,digest in ARCHIVE_PINS.items()),'exact pinned LX6 emulator and unchanged vendor archives')
        for protected in (args.idf,args.idf_tools,args.vendor,args.rom,args.qemu.parent,args.powershell.parent,Path(sys.executable).resolve().parent):
            need(not (args.output==protected or args.output.is_relative_to(protected) or protected.is_relative_to(args.output)),'output cannot overlap installed runtimes')
    return args


def main():
    args=arguments()
    if args.prepare_only:
        contract,blob=prepare_contract();args.output.mkdir(parents=True)
        write_json(args.output/'contract.json',contract);(args.output/'reference.h').write_text(reference_header(contract),encoding='utf-8',newline='\n');(args.output/'fixtures.bin').write_bytes(blob)
        print(json.dumps(dict(passed=True,prepared_only=True,production_sources_frozen=False,target_executed=False,base_complete_cases=36,continuous_public_observations=12)))
        return 0
    if args.preflight_only:
        print(json.dumps(dict(preflight=True,output_created=False,production_sources_frozen=False,target_executed=False)))
        return 0
    return Campaign(args).execute()


if __name__=='__main__':
    sys.dont_write_bytecode=True
    sys.exit(main())
