"""Run actual CYD Ogg gain metadata through the complete PDM rendering pipeline.

Synthetic HTTP transport, public PDM driver functions and LED hardware are seams. SDK HTTP
allocation/cleanup, RTOS scheduling, production translation units and shared
queues remain real. The PCM oracle is the frozen direct-vendor integration
checkpoint, not an independent codec-quality or universal conformance oracle.
No physical board, external network, private codec ABI or custom decoder is used.
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
HARNESS = ROOT / 'tests/target/cyd_ogg_gain_task_qemu'
MAIN = Path('idf/esp32-cyd2usb-native/main')
MAIN_TUS = ('audio_service.c', 'native_state.c', 'native_health.c', 'decoder_registration.c', 'native_audio_output.c', 'native_output_metrics.c')
SDK_COMMIT = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
VENDOR_COMMIT = '67b8d0e98f58c774b8652480893037273190e8dc'
ARCHIVE_PINS = {
    'libesp_audio_codec.a': '92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58',
    'libesp_audio_simple_dec.a': 'ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6',
}
QEMU_SHA = '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d'
FIXTURE_SHA = '09d6cfa599f2c4a25f5745e5c8a605b5a1583a42d7990b9e5242b8990adff12f'
PCM_SHA = 'e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910'
PCM_BYTES = 2112000
REFERENCE = ROOT / 'tests/results/cyd-espressif-reuse-20261030'
REFERENCE_MANIFEST_SHA = '96a6b5588413d23e285f7035825541b815bf558c9fdf8f39de5f813d26cba893'
REFERENCE_ARCHIVE_SHA = '31614078d14143c64edeb5f295548226a2014e4c6b68e5110488d1c5be22f818'


POSITION = ROOT / 'tests/results/cyd-opus-position-20261101'
POSITION_MANIFEST_SHA = 'd6b62c34b3ceec10d7f79c3016ffb5888e0a98496efd26bf00f0f7851badb754'
POSITION_VERIFIER_SHA = '0b24d0910df86a539f1092e8cd1e344091d5c1e3c9f232d98b8ce98349a89994'
FIXTURES = {
    'OPUS20':dict(path='tests/fixtures/esp32c3_calibration/opus-510.ogg',file='fixture20.ogg',
                  bytes=706319,sha256='53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11'),
    'OPUS120':dict(path='tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg',file='fixture120.ogg',
                   bytes=707097,sha256='b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679'),
    'VORBIS':dict(path='tests/fixtures/esp32c3_calibration/vorbis-q10.ogg',file='fixturevorbis.ogg',
                  bytes=703584,sha256=FIXTURE_SHA),
}


def encoded_page_max(path):
    body=Path(path).read_bytes();at=0;largest=0
    while at<len(body):
        need(at+27<=len(body) and body[at:at+5]==b'OggS\0','complete original Ogg page')
        count=body[at+26];need(at+27+count<=len(body),'complete original lacing')
        size=27+count+sum(body[at+27:at+27+count]);need(at+size<=len(body),'complete original page extent')
        largest=max(largest,size);at+=size
    need(at==len(body) and largest>0,'full encoded fixture page census')
    return largest


def fields(line,prefix):
    need(line.startswith(prefix+' '),'known exact observation tag')
    pairs=[item.split('=',1) for item in line[len(prefix)+1:].split()]
    need(pairs and all(len(pair)==2 for pair in pairs) and len({pair[0] for pair in pairs})==len(pairs),
         'complete unique public observation fields')
    text_fields={'fixture','id','codec','stage','sha256','source_sha','render_sha'}
    result={}
    for key,value in pairs:
        if key in text_fields:
            result[key]=value
        else:
            need(re.fullmatch('-?\\d+',value),'strict integer observation')
            result[key]=int(value)
    return result


def validate_log(log,references):
    log=log.replace('\r\n','\n')
    need(not re.search(r'CYD_OGG_GAIN_TASK_FAILURE|Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack (?:smashing|overflow)|panic.ed',log,re.I),'no actual renderer/task fault')
    lines=[line for line in log.splitlines() if line.startswith('CYD_OGG_GAIN_')]
    need(lines and lines[0]=='CYD_OGG_GAIN_TASK_BOOT actual_audio_service_tu=1 actual_output_tu=1 sdk=v6.0.2 coordinator=0 hardware=0','whole current audio and output translation units')
    need(not any('CYD_OGG_GAIN_' in line and not line.startswith('CYD_OGG_GAIN_') for line in log.splitlines()),'intact original observations')
    cases=[];renders=[];source_links=[];render_links=[];memory=[];observers=[];controls=[];profiles=[];stock=bytearray();chain=None;complete=None
    for line in lines[1:]:
        if line.startswith('CYD_OGG_GAIN_STOCK '):
            match=re.fullmatch(r'CYD_OGG_GAIN_STOCK offset=(\d+) size=(\d+) hex=([0-9a-f]+)',line);need(match,'complete original stock Vorbis capture record')
            offset,size,hex_body=match.groups();body=bytes.fromhex(hex_body)
            need(int(offset)==len(stock) and int(size)==len(body) and 0<len(body)<=256 and not len(body)%4,'sequential unchanged stereo stock bytes')
            stock+=body;continue
        tag=line.split(' ',1)[0]
        if tag=='CYD_OGG_GAIN_TASK_PROFILE':
            profiles.append(line);continue
        row=fields(line,tag)
        if tag=='CYD_OGG_GAIN_TASK_CASE':cases.append(row)
        elif tag=='CYD_OGG_GAIN_RENDER_CASE':renders.append(row)
        elif tag=='CYD_OGG_GAIN_LINK':source_links.append(row)
        elif tag=='CYD_OGG_GAIN_RENDER_LINK':render_links.append(row)
        elif tag=='CYD_OGG_GAIN_MEMORY':memory.append(row)
        elif tag=='CYD_OGG_GAIN_TASK_CHAIN':need(chain is None,'one actual gain chain');chain=row
        elif tag=='CYD_OGG_GAIN_TASK_COMPLETE':need(complete is None and line==lines[-1],'one final native observation');complete=row
        elif tag.startswith('CYD_OGG_GAIN_OBS_'):observers.append((tag.removeprefix('CYD_OGG_GAIN_OBS_'),row))
        elif tag.startswith('CYD_OGG_GAIN_CONTROL_'):controls.append((tag.removeprefix('CYD_OGG_GAIN_CONTROL_'),row))
        elif tag=='CYD_OGG_GAIN_TASK_FIXTURE':pass
        else:need(False,'known actual gain task record')
    need(profiles==['CYD_OGG_GAIN_TASK_PROFILE role=stream core=0 priority=3 stack=6144','CYD_OGG_GAIN_TASK_PROFILE role=decode core=1 priority=5 stack=16384','CYD_OGG_GAIN_TASK_PROFILE role=output core=1 priority=6 stack=4096'],'all original actual task creation profiles')
    expected=[(row['name'],case) for row in references['lifecycles'] for case in ('T0','T1','T2')]+[(row['name'],'FULL') for row in references['full_cases']]
    need([(row['fixture'],row['id']) for row in cases]==expected and len(renders)==len(cases)==23,'all full gain/lifecycle cases actually execute')
    plans={row['name']:row for row in [*references['lifecycles'],*references['full_cases'],references['chain']]}
    for case,render in zip(cases,renders):
        plan=plans[case['fixture']]
        need(case['pcm_bytes']==2112000 and case['sha256']==plan['links'][0]['source_sha'] and case['writes']>0 and case['metadata']==1,'every unchanged logical source byte precedes real rendering')
        need(render['fixture']==case['fixture'] and render['mono_bytes']==1056000 and render['volume']==plan['volume'] and re.fullmatch('[a-f0-9]{64}',render['sha256']),'actual complete mono driver span')
        if case['id']=='T1':need(0<case['partial_pcm']<2112000 and case['stop_generation']>0 and case['stop_reopen']==case['discard_after_request']==case['stop_quiet']==1,'real partial gain Stop/discard/reopen')
        if case['id']=='T2':need(0<case['partial_pcm']<2112000 and all(case[key]==1 for key in ('maintenance_resume','held_quiet','play_blocked','token_consumed','stale_rejected')),'real gain maintenance/resume and stale-token rejection')
    need(len(stock)==2112000 and hashlib.sha256(stock).hexdigest()==PCM_SHA,'all captured stock Vorbis PCM equals the original complete vendor reference')
    need(chain and chain['links']==9 and all(chain[key]==1 for key in ('one_http','same_generation','single_eof')) and chain['cross_link_reads']>0 and
         chain['pcm_bytes']==19008000 and chain['mono_bytes']==9504000 and chain['opens']==chain['closes']==38 and chain['http_cleanup']==30,'nine gain-changing links, one actual HTTP/generation/final EOF')
    need(len(source_links)==len(render_links)==32,'every complete source/render link observed')
    for source,render in zip(source_links,render_links):
        need(source['fixture']==render['fixture'] and source['index']==render['index'] and source['codec']==render['codec'],'source/render link correspondence across DMA blocks')
        plan=plans[source['fixture']];link=plan['links'][source['index']]
        need(source['bytes']==2112000 and source['sha256']==link['source_sha'] and render['bytes']==1056000 and
             render['gain_q8']==link['gain_q8'] and render['volume']==plan['volume'],'actual gain metadata, complete retained source and mono spans')
        if link['mono_sha'] is not None:need(render['sha256']==link['mono_sha'],'exact independent Decimal combined mono output')
    need(complete and complete['cases']==24 and complete['actual_audio_service_tu']==complete['actual_output_tu']==1 and
         complete['opens']==complete['closes']==38 and complete['http_cleanup']==30 and complete['live_decoders']==complete['live_clients']==0 and
         complete['resizes']==complete['retries']==13 and complete['gain_stamps']>0 and complete['driver_writes']>0 and complete['preloads']>0 and
         complete['driver_created']==complete['driver_deleted']>0 and complete['output_flushes']==24 and complete['heap_integrity']==1,
         'actual decoder/client/driver cleanup and hardware-write/metadata census')
    for role,size in [('stream',6144),('decode',16384),('output',4096)]:need(0<complete[role+'_stack_free']<=size,'actual original owner stack margin')
    need(0<complete['heap_min']<=complete['heap_free'],'actual global minimum heap')
    active=None;handles=[];pending=None;last_calls=0;resizes=[];retries=[]
    for tag,row in observers:
        if tag=='OPEN':
            need(active is None and pending is None and row['instance']==len(handles)+1 and row['generation']>0,'one actual public handle at a time')
            active=dict(fixture=row['fixture'],instance=row['instance'],generation=row['generation'],offset=last_calls,resizes=0,retries=0,initial=None)
        else:
            need(active and row['instance']==active['instance'] and row['fixture']==active['fixture'],'public process observation belongs to live owner')
            if tag=='INITIAL':
                need(active['initial'] is None and row['call']==1 and row['global_call']==active['offset']+1 and row['capacity']>=12288,'actual first-call capacity')
                active['initial']=row['capacity']
            elif tag=='RESIZE':
                need(pending is None and row['result']==-8 and row['decoded_size']==0 and 0<=row['consumed']<=row['raw_len'] and row['needed_size']>row['capacity'] and row['global_call']==active['offset']+row['call'],'genuine public buffer error')
                pending=row;active['resizes']+=1;resizes.append(row)
            elif tag=='RETRY':
                need(pending and row['call']==pending['call']+1 and row['global_call']==pending['global_call']+1 and row['capacity']==pending['needed_size'] and
                     row['raw_len']==pending['raw_len']-pending['consumed'] and row['eos']==pending['eos'] and row['arguments_advanced_once']==1 and row['result']==0,'next real call advances exactly once and uses needed capacity')
                active['retries']+=1;retries.append(row);pending=None
            elif tag=='CLOSE':
                need(pending is None and active['initial'] and row['calls']>0 and row['global_calls']==active['offset']+row['calls'] and row['resizes']==active['resizes']==row['retries']==active['retries'],'actual complete close and retry census')
                active.update(calls=row['calls'],last_capacity=row['last_capacity']);last_calls=row['global_calls'];handles.append(active);active=None
            else: need(False,'known public observation')
    need(active is None and pending is None and len(handles)==38 and last_calls==complete['process_calls'] and len(resizes)==complete['resizes'] and len(retries)==complete['retries'], 'all thirty-eight public handles close with exact process/retry totals')
    expected_owners=[plan['name'] for plan in references['lifecycles'] for _ in range(5)]+[plan['name'] for plan in references['full_cases']]+[references['chain']['name']]*9
    need([row['fixture'] for row in handles]==expected_owners,'actual ownership census follows the complete gain/lifecycle plan')
    need(len({row['generation'] for row in handles[-9:]})==1,'same actual generation across all nine gain-changing links')
    need(all(row['initial']==12288 for row in handles[:-9]),'every new station lifecycle restores initial production capacity')
    need(all(row['resizes']==1 and row['last_capacity']==23040 for row in handles[5:10]),'all long-packet lifecycle handles genuinely grow once')
    expected_links=[(plan['name'],0,plan['links'][0]['name']) for plan in references['lifecycles'] for _ in range(3)]+[(plan['name'],0,plan['links'][0]['name']) for plan in references['full_cases']]+[(references['chain']['name'],index,link['name']) for index,link in enumerate(references['chain']['links'])]
    need([(row['fixture'],row['index'],row['codec']) for row in source_links]==expected_links,'every source and rendered link follows the actual ordered plan')
    need(len(memory)==30 and all(0<row['heap_min']<=row['heap_free'] and 0<row['largest_internal']<=row['heap_free'] for row in memory),'all actual EOF/Stop/maintenance/chain resource observations')
    discard_events=[row for tag,row in controls if tag=='DISCARD']
    need([row['sequence'] for row in discard_events]==list(range(1,len(discard_events)+1)) and all(row['core']==1 and row['priority']==6 and row['real_returned']==1 for row in discard_events),'every actual forwarded discard completion has original output owner and unique sequence')
    for plan in references['lifecycles']:
        name=plan['name'];parts={tag:[row for found,row in controls if found==tag and row['fixture']==name] for tag in ('STOP_REQUEST','STOP_RETURN','STOP_QUIET')}
        need(all(len(rows)==1 for rows in parts.values()),'one complete real Stop request/return/quiet witness')
        request,returned,quiet=(parts[tag][0] for tag in ('STOP_REQUEST','STOP_RETURN','STOP_QUIET'))
        matching=[row for row in discard_events if row['sequence']==request['before_sequence']+1]
        need(len(matching)==1,'one actual discard completes after this Stop request');discard=matching[0]
        need(request['core']==0 and request['before_generation']+1==returned['stop_generation']==quiet['stop_generation'] and returned['before_sequence']==request['before_sequence'] and
             request['time_us']<=returned['time_us']<=quiet['time_us'] and request['time_us']<=discard['time_us']<=quiet['time_us'] and
             discard['fixture']==name and quiet['discard_sequence']==discard['sequence'] and request['before_generation']<=discard['snapshot_generation']<=quiet['stop_generation'] and
             quiet['discard_snapshot_generation']==discard['snapshot_generation'],'real output completion belongs to the Stop interval without inventing a generation label')
        need(quiet['live_clients']==quiet['live_decoders']==quiet['input_ready']==quiet['input_reading']==quiet['input_writing']==0 and
             quiet['input_available']==quiet['input_leased']==quiet['no_eof']==1 and quiet['quiet_ticks']>=25 and
             0<quiet['pcm_bytes']<2112000 and 0<quiet['mono_bytes']<1056000 and
             all(quiet[key]==discard[key] for key in ('pcm_bytes','mono_bytes','writes','driver_writes')),
             'all three owners/input and actual source/driver counters stay quiet after real discard before reopening')
    return dict(public_handles=handles,resize_observations=resizes,retry_observations=retries,cases=cases,render_cases=renders,source_links=source_links,render_links=render_links,chain=chain,
        complete=complete,memory=memory,public_observations=observers,public_controls=controls,stock_vorbis_bytes=len(stock),stock_vorbis_sha256=PCM_SHA,
        actual_output_tu=True,normalization_enabled=False,vorbis_oracle_pending=True),bytes(stock)


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--build-timeout', type=int, default=1200)
    parser.add_argument('--qemu-timeout', type=int, default=600)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--gain-reference',type=Path,default=ROOT/'.build/cyd-opus-gain-playback-reference-20261101-01')
    parser.add_argument('--mono-reference',type=Path,default=ROOT/'.build/cyd-opus-gain-output-reference-20261101-01')
    args = parser.parse_args()
    need(sys.platform == 'win32', 'Installed Windows SDK/QEMU launcher required')
    need(1 <= args.build_timeout <= 1200 and 1 <= args.qemu_timeout <= 1200, 'bounded native command deadlines')
    args.output = args.output.resolve()
    args.gain_reference=args.gain_reference.resolve();args.mono_reference=args.mono_reference.resolve()
    need(all(path.is_relative_to(ROOT/'.build') and (path/'report.json').is_file() for path in (args.gain_reference,args.mono_reference)),'actual complete independent gain reference captures')
    need(args.output.is_relative_to(ROOT / '.build') and args.output != ROOT / '.build' and not args.output.exists(),
         'fresh output strictly below current worktree .build')
    need(not any((p / 'report.json').exists() or (p / 'execution-bundle.json').exists() for p in args.output.parents),
         'output must not be nested inside another evidence campaign')
    args.idf = REPO / '.idf/v6.0.2'
    args.idf_tools = REPO / '.idf/tools-v6.0.2'
    args.idf_python = args.idf_tools / 'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    args.vendor = REPO / '.idf/esp-adf-libs/esp_audio_codec'
    args.qemu = ROOT / '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
    args.rom = Path('C:/Work/QEMU-ESP32/pc-bios')
    args.powershell = Path(shutil.which('pwsh.exe') or '')
    args.git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    args.fixture = ROOT / 'tests/fixtures/esp32c3_calibration/vorbis-q10.ogg'
    required = [args.idf / 'tools/idf.py', args.idf / 'export.ps1', args.idf / 'tools/tools.json',
                args.idf_python, args.qemu, args.powershell, args.git, args.fixture,
                args.rom / 'esp32-v3-rom.bin', args.rom / 'esp32-v3-rom-app.bin',
                HARNESS / 'sdk-build.ps1', HARNESS / 'project/main/main.cpp', POSITION / 'manifest.json', POSITION / 'verify.py',
                ROOT / MAIN / 'aac_public_config.h', ROOT / MAIN / 'ogg_playback.h',
                REFERENCE / 'native-manifest.json', REFERENCE / 'native-captures.zip',
                *[args.vendor / 'lib/esp32' / name for name in ARCHIVE_PINS]]
    need(all(p.is_file() for p in required), 'all installed native dependencies and canonical harness inputs exist')
    for protected in (args.idf, args.idf_tools, args.vendor, args.idf_python.parent, args.qemu.parent,
                      args.rom, args.powershell.parent, Path(sys.executable).resolve().parent):
        need(not (args.output == protected or args.output.is_relative_to(protected) or protected.is_relative_to(args.output)),
             'output cannot overlap installed runtimes')
    need(sha(args.qemu) == QEMU_SHA and sha(args.fixture) == FIXTURE_SHA, 'pinned emulator and encoded fixture')
    need(all(sha(args.vendor / 'lib/esp32' / name) == digest for name, digest in ARCHIVE_PINS.items()),
         'exact original Xtensa vendor archives')
    need(sha(REFERENCE / 'native-manifest.json') == REFERENCE_MANIFEST_SHA and
         sha(REFERENCE / 'native-captures.zip') == REFERENCE_ARCHIVE_SHA, 'frozen direct-vendor PCM reference checkpoint')
    need(sha(POSITION / 'manifest.json')==POSITION_MANIFEST_SHA and sha(POSITION / 'verify.py')==POSITION_VERIFIER_SHA,'independent complete-position checkpoint identity')
    for row in FIXTURES.values():
        need(sha(ROOT / row['path'])==row['sha256'] and (ROOT / row['path']).stat().st_size==row['bytes'],'full unchanged fixture identity')
    return args


class Campaign:
    def __init__(self, args):
        self.args, self.out = args, args.output
        self.sources, self.runtime, self.artifacts = {}, {}, {}
        self.runtime_paths = {}
        self.report = dict(passed=False, completed=False, commands=[], actual_audio_service_tu=True, actual_output_tu=True,
                           actual_rtos=True, target_executed=False, production_firmware=False,
                           physical_device=False, external_network=False, private_codec_abi=False,
                           custom_decoder=False, oom_injection=False, output_backpressure=False,
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
        for key, row in FIXTURES.items():
            self.freeze(ROOT / row['path'], Path('sources/harness/project/main') / row['file'], 'complete original encoded '+key+' fixture')
        self.freeze(Path(__file__), Path('sources/controller.py'), 'campaign controller')
        self.freeze(REFERENCE / 'native-manifest.json', Path('sources/reference/native-manifest.json'), 'pinned direct-vendor reference manifest')
        self.reference()
        write_json(self.out / 'source-manifest.json', self.sources)

    def vorbis_reference(self):
        manifest = json.loads((REFERENCE / 'native-manifest.json').read_bytes())
        need(manifest['passed'] and manifest['native_children_terminal_zero'] and
             not manifest['full_pcm_independent_oracle'] and manifest['cross_architecture_full_pcm_equal'],
             'qualified public vendor integration reference scope')
        lookup = {row['path']: row for row in manifest['files']}
        with zipfile.ZipFile(REFERENCE / 'native-captures.zip') as archive:
            for target in ('esp32', 'esp32c3'):
                prefix = 'captures/espressif-vorbis-' + target + '-20261030-04/'
                for name in ('qemu.stdout.log', 'qemu.stderr.log', 'report.json'):
                    row = lookup[prefix + name]
                    body = archive.read(row['blob'])
                    need(hashlib.sha256(body).hexdigest() == row['sha256'] and len(body) == row['bytes'], 'saved direct native reference bytes')
                    destination = self.out / 'sources/reference' / target / name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(body)
                measured = manifest['measurements'][target]
                for case in [measured['warmup'], *measured['cases']]:
                    need(case['pcm'] == PCM_BYTES and case['sha256'] == PCM_SHA and case['input'] == 703584,
                         'cross-target direct decoder PCM identity')
                report = json.loads((self.out / 'sources/reference' / target / 'report.json').read_bytes())
                need(report['target_executed'] and all(r['state'] == 'complete' and r['exit_status'] == 0 for r in report['commands']),
                     'reference SDK/QEMU children actually terminated zero')
        self.bind_runtime(REFERENCE / 'native-captures.zip')
        self.report['pcm_reference'] = dict(kind='frozen original-vendor integration regression', bytes=PCM_BYTES,
            sha256=PCM_SHA, checkpoint_manifest_sha256=REFERENCE_MANIFEST_SHA,
            checkpoint_archive_sha256=REFERENCE_ARCHIVE_SHA, independent_numeric_oracle=False)

    def old_reference(self):
        self.vorbis_reference()
        need(sha(POSITION/'manifest.json')==POSITION_MANIFEST_SHA and sha(POSITION/'verify.py')==POSITION_VERIFIER_SHA,'original independent position checkpoint')
        spec=importlib.util.spec_from_file_location('reviewed_position_checkpoint',POSITION/'verify.py')
        reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader);reader.verify()
        position=json.loads((POSITION/'evidence/oracle/report.json').read_bytes())
        native=json.loads((POSITION/'evidence/native/report.json').read_bytes())
        refs={}
        for name,key in [('OPUS20','F20'),('OPUS120','F120')]:
            result=position['fixtures'][key]['comparison']; measured=native['measurements']['cases'][key]
            need(result['best_offset']==312 and result['best_ties']==1 and result['logical_frames']==528000 and
                 result['samples_per_candidate']==1056000 and measured['window_bytes']==2112000,'complete independent sample-position proof')
            refs[name]=dict(pcm_bytes=2112000,pcm_sha256=measured['window_sha256'],independent_sample_position=True)
        refs['VORBIS']=dict(pcm_bytes=PCM_BYTES,pcm_sha256=PCM_SHA,independent_sample_position=False)
        for name,row in refs.items(): row['max_page_bytes']=encoded_page_max(ROOT/FIXTURES[name]['path'])
        for path in sorted(POSITION.rglob('*')):
            if path.is_file(): self.freeze(path,Path('sources/reference/position')/path.relative_to(POSITION),'independent position checkpoint text/source evidence; PCM/images omitted')
        header=self.out/'sources/harness/project/main/reference.h'
        text='#pragma once\nstatic constexpr size_t FULL_PCM_SINGLE = 2112000;\n'
        for name,row in refs.items():
            text+='static constexpr char PCM_'+name+'_SHA[] = "'+row['pcm_sha256']+'";\n'
            text+='static constexpr size_t MAX_PAGE_'+name+' = '+str(row['max_page_bytes'])+';\n'
        header.write_text(text,encoding='utf-8',newline='\n')
        self.freeze(header,header.relative_to(self.out),'generated full logical playback references, no raw vendor padding')
        self.report['pcm_reference']=dict(fixtures=refs,position_manifest_sha256=POSITION_MANIFEST_SHA,
            vorbis_manifest_sha256=REFERENCE_MANIFEST_SHA,vorbis_archive_sha256=REFERENCE_ARCHIVE_SHA,
            independent_opus_sample_position=True,numeric_conformance_claim=False)

    def reference(self):
        self.old_reference()
        gain=json.loads((self.args.gain_reference/'report.json').read_bytes())
        mono=json.loads((self.args.mono_reference/'report.json').read_bytes())
        need(gain['passed'] and mono['passed'] and mono['all_source_bindings_current'] and not mono['production_gain_qualified'],'independent complete integer-PCM gain reference data')
        for directory,record,role in [(self.args.gain_reference,gain,'gain-data'),(self.args.mono_reference,mono,'mono-data')]:
            self.freeze(directory/'report.json',Path('sources/reference')/role/'report.json','actual independent reference preparation report')
            for pin in record['sources']:
                source=directory/pin['snapshot'];need(sha(source)==pin['sha256']==sha(ROOT/pin['path']),'exact independent reference source/input binding')
                if source.suffix!='.pcm':self.freeze(source,Path('sources/reference')/role/pin['snapshot'],'independent reference source/data; no production helper')
        self.freeze(ROOT/'tests/prepare-cyd-opus-gain-output-reference.py',Path('sources/reference/final-mono-oracle.py'),'independent Decimal/legacy post-run Vorbis oracle, frozen before execution')
        sources=self.report['pcm_reference']['fixtures'];views={row['id']:row for row in gain['variants']}
        generated=['#pragma once','static constexpr size_t FULL_PCM_SINGLE=2112000;','static constexpr size_t FULL_MONO_SINGLE=1056000;']
        link_records={}
        for name,row in views.items():
            base=row['fixture'];start,end=('opus20_start','opus20_end') if base=='OPUS20' else ('opus120_start','opus120_end')
            patches=[]
            for i,patch in enumerate(row['patches']):
                symbol='patch_'+name+'_'+str(i);body=bytes.fromhex(patch['header_hex'])
                generated.append('static const uint8_t '+symbol+'[]={'+','.join(str(v) for v in body)+'};')
                patches.append('{'+str(patch['offset'])+','+str(len(body))+','+symbol+'}')
            generated.append('static const patch_t patches_'+name+'[]={'+','.join(patches)+'};')
            source=sources[base]
            generated.append('static const link_t '+name+'={'+start+','+end+',"'+name+'","'+base+'","'+source['pcm_sha256']+'",'+str(row['gain_q8'])+',patches_'+name+','+str(len(patches))+','+str(source['max_page_bytes'])+'};')
            link_records[name]=dict(name=name,family=base,gain_q8=row['gain_q8'],source_sha=source['pcm_sha256'])
        generated.append('static const link_t VORBIS={vorbis_start,vorbis_end,"VORBIS","VORBIS","'+PCM_SHA+'",0,nullptr,0,'+str(sources['VORBIS']['max_page_bytes'])+'};')
        link_records['VORBIS']=dict(name='VORBIS',family='VORBIS',gain_q8=0,source_sha=PCM_SHA)
        def plan(name,links,volume,dump=False):
            records=[];monos=[]
            for link in links:
                record=dict(link_records[link]);digest=None
                if link!='VORBIS':
                    matching=[row for row in mono['references'] if row['id']==link and row['volume']==volume and row['balance']==0]
                    need(len(matching)==1,'one independent full mono hash for each exact gain/volume');digest=matching[0]['sha256']
                record['mono_sha']=digest;records.append(record);monos.append('"'+digest+'"' if digest else 'nullptr')
            literal='{"'+name+'",{'+','.join('&'+link for link in links)+'},'+str(len(links))+','+str(volume)+',{'+','.join(monos)+'},'+str(dump).lower()+'}'
            return dict(name=name,links=records,volume=volume,dump_stock=dump),literal
        life=[];life_literals=[]
        for name,link,volume,dump in [('LIFE_PLUS48','OPUS20_PLUS48',1,False),('LIFE_MINUS6','OPUS120_MINUS6',254,False),('LIFE_VORBIS','VORBIS',254,True)]:
            record,literal=plan(name,[link],volume,dump);life.append(record);life_literals.append(literal)
        full=[];full_literals=[]
        selections={'OPUS20':[('ZERO',254),('PLUS6',254),('MINUS6',254),('PLUS20',127),('MAX',254),('MIN',254),('MAX',0)],
                    'OPUS120':[('ZERO',254),('PLUS6',254),('PLUS20',127),('PLUS48',1),('MAX',254),('MIN',254),('MAX',0)]}
        for base,items in selections.items():
            for label,volume in items:
                name=base+'_'+label+'_V'+str(volume);record,literal=plan(name,[base+'_'+label],volume);full.append(record);full_literals.append(literal)
        chain,literal=plan('GAIN_CHAIN',['OPUS20_PLUS48','VORBIS','OPUS120_MINUS6','OPUS20_ZERO','OPUS20_MAX','OPUS120_MIN','OPUS120_ZERO','OPUS20_MINUS6','OPUS120_PLUS6'],1)
        generated+=['static const fixture_t lifecycles[]={'+','.join(life_literals)+'};','static const fixture_t full_cases[]={'+','.join(full_literals)+'};',
                    'static constexpr unsigned FULL_CASE_COUNT='+str(len(full_literals))+';','static const fixture_t chain_fixture='+literal+';']
        header=self.out/'sources/harness/project/main/reference.h';header.write_text('\n'.join(generated)+'\n',encoding='utf-8',newline='\n')
        self.freeze(header,header.relative_to(self.out),'derived complete legal gain views and independent Decimal mono output hashes')
        self.report['pcm_reference']=dict(lifecycles=life,full_cases=full,chain=chain,normalization_enabled=False,
            gain_data_report_sha256=sha(self.args.gain_reference/'report.json'),mono_data_report_sha256=sha(self.args.mono_reference/'report.json'),
            vorbis_mono_oracle_required_after_capture=True,numeric_conformance_claim=False)

    def finish_oracle(self,measurement,stock):
        path=self.out/'stock-vorbis.pcm';path.write_bytes(stock)
        oracle_path=ROOT/'tests/prepare-cyd-opus-gain-output-reference.py'
        need(oracle_path.read_bytes()==(self.out/'sources/reference/final-mono-oracle.py').read_bytes(),'post-run mono oracle is unchanged from pre-execution snapshot')
        spec=importlib.util.spec_from_file_location('independent_final_mono_oracle',oracle_path)
        oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
        expected={volume:oracle.full_mono(stock,0,volume)['sha256'] for volume in (1,254)}
        for row in measurement['render_links']:
            if row['codec']=='VORBIS':need(row['sha256']==expected[row['volume']],'independent captured-stock Vorbis final mono bypass/reset hash')
        for row in measurement['render_cases']:
            if row['fixture']=='LIFE_VORBIS':need(row['sha256']==expected[254],'independent full standalone Vorbis renderer oracle')
        measurement.update(vorbis_oracle_pending=False,stock_vorbis_path=path.name,independent_vorbis_mono_hashes=expected)
        self.report['vorbis_post_oracle']=dict(passed=True,stock_bytes=len(stock),stock_sha256=hashlib.sha256(stock).hexdigest(),
            expected_mono_hashes=expected,oracle_source_sha256=sha(oracle_path),production_helper_reused=False)
        return measurement

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
                    'AUDIO_DECODER_VORBIS_SUPPORT', 'AUDIO_DECODER_OPUS_SUPPORT', 'AUDIO_SIMPLE_DEC_OGG_SUPPORT', 'YORADIO_OGG_TIMELINE'):
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
        need({'ogg_playback.h','ogg_page_input.h','opus_pcm_trim.h','ogg_opus_timeline.h','aac_public_config.h','pcm_header_gain.h','native_audio_settings.h','native_audio_normalizer.h','AudioNormalizer.h'}<=used_headers,
             'actual GCC dependency closure consumes the current playback/trim/page and public AAC headers')
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
            print('Building complete CYD audio-service tasks and unchanged vendor decoder', flush=True)
            self.run_command('build', [self.args.powershell, '-NoProfile', '-NonInteractive', '-File',
                self.out / 'sources/harness/sdk-build.ps1', '-OutputDirectory', self.out, '-IdfDirectory', self.args.idf,
                '-IdfToolsDirectory', self.args.idf_tools, '-IdfPythonExecutable', self.args.idf_python], self.args.build_timeout)
            flash = self.qualify_build()
            print('Starting actual Ogg playback tasks for Opus20/120, Vorbis and same-HTTP chaining', flush=True)
            log = self.run_command('qemu', [self.args.qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet', '-smp', '2',
                '-L', self.args.rom, '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none',
                '-drive', 'file=' + str(flash).replace(',', ',,') + ',if=mtd,format=raw'], self.args.qemu_timeout)
            measured,stock=validate_log(log + '\n' + (self.out / 'qemu.stderr.log').read_text(errors='replace'), self.report['pcm_reference'])
            self.report['measurements']=self.finish_oracle(measured,stock)
            self.verify_repositories('-after')
            need(self.verify_inputs(), 'every bound input unchanged after target execution')
            self.report.update(passed=True, completed=True)
            print('PASS actual CYD Ogg playback lifecycle and chaining; physical/radio resources remain separate', flush=True)
        except BaseException as error:
            self.report.update(passed=False, completed=False, failure_type=type(error).__name__, failure=str(error))
            print(json.dumps(dict(passed=False, failure_type=type(error).__name__, failure=str(error))), file=sys.stderr)
        finally:
            if not self.verify_inputs(): self.report['passed'] = False
            self.save()
        return 0 if self.report['passed'] else 1


def main():
    args = arguments()
    if args.preflight_only:
        print(json.dumps(dict(preflight=True, output_created=False, target_executed=False)))
        return 0
    return Campaign(args).execute()


if __name__ == '__main__':
    sys.exit(main())
