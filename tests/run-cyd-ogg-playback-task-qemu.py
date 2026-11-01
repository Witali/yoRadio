"""Run actual CYD Ogg playback tasks: logical Opus, Vorbis and sequential chaining.

Synthetic HTTP transport and output/LED hardware are explicit seams. SDK HTTP
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
HARNESS = ROOT / 'tests/target/cyd_ogg_playback_task_qemu'
MAIN = Path('idf/esp32-cyd2usb-native/main')
MAIN_TUS = ('audio_service.c', 'native_state.c', 'native_health.c', 'decoder_registration.c')
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
    text_fields={'fixture','id','codec','stage','sha256'}
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
    need(not re.search(r'CYD_OGG_PLAYBACK_TASK_FAILURE|Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack (?:smashing|overflow)|panic.ed',log,re.I),'no actual runtime fault')
    prefix='CYD_OGG_PLAYBACK_'
    need(not any(prefix in line and not line.startswith(prefix) for line in log.splitlines()),'intact observation records')
    lines=[line for line in log.splitlines() if line.startswith(prefix)]
    need(lines and lines[0]=='CYD_OGG_PLAYBACK_TASK_BOOT actual_audio_service_tu=1 sdk=v6.0.2 coordinator=0 fixtures=3 chain_links=3 hardware=0','current complete production task diagnostic')
    for line,(role,core,priority,stack) in zip(lines[1:4],[('stream',0,3,6144),('decode',1,5,16384),('output',1,6,4096)]):
        need(line==f'CYD_OGG_PLAYBACK_TASK_PROFILE role={role} core={core} priority={priority} stack={stack}','unchanged actual task creation')
    cases=[];links=[];memory=[];observations=[];chain=None;complete=None;fixtures=[]
    for line in lines[4:]:
        if line.startswith('CYD_OGG_PLAYBACK_TASK_CASE '): cases.append(fields(line,'CYD_OGG_PLAYBACK_TASK_CASE'))
        elif line.startswith('CYD_OGG_PLAYBACK_LINK '): links.append(fields(line,'CYD_OGG_PLAYBACK_LINK'))
        elif line.startswith('CYD_OGG_PLAYBACK_MEMORY '): memory.append(fields(line,'CYD_OGG_PLAYBACK_MEMORY'))
        elif line.startswith('CYD_OGG_PLAYBACK_OBS_'):
            tag=line.split(' ',1)[0];observations.append((tag.removeprefix('CYD_OGG_PLAYBACK_OBS_'),fields(line,tag)))
        elif line.startswith('CYD_OGG_PLAYBACK_TASK_FIXTURE '): fixtures.append(fields(line,'CYD_OGG_PLAYBACK_TASK_FIXTURE'))
        elif line.startswith('CYD_OGG_PLAYBACK_TASK_CHAIN '):
            need(chain is None,'one actual chain result');chain=fields(line,'CYD_OGG_PLAYBACK_TASK_CHAIN')
        elif line.startswith('CYD_OGG_PLAYBACK_TASK_COMPLETE '):
            need(complete is None and line==lines[-1],'one final terminal observation');complete=fields(line,'CYD_OGG_PLAYBACK_TASK_COMPLETE')
        else: need(False,'known full task transcript record')
    need([(row['fixture'],row['id']) for row in cases]==[(name,case) for name in FIXTURES for case in ('T0','T1','T2')],'all nine ordered lifecycle cases')
    for index,(name,source) in enumerate(references['fixtures'].items()):
        for number,row in enumerate(cases[index*3:index*3+3]):
            need(row['pcm_bytes']==source['pcm_bytes']==2112000 and row['sha256']==source['pcm_sha256'] and row['writes']>0 and row['metadata']==1,'exact complete logical output and actual metadata')
            owners=index*5+(1 if number==0 else 3 if number==1 else 5)
            need(row['opens']==row['closes']==row['http_cleanup']==owners,'real cumulative public owner cleanup')
            if number==0: need(row['ordered_eof']==1,'ordered full EOF')
            else:
                need(0<row['partial_pcm']<2112000,'actual partial playback cancellation')
                if number==1: need(row['stop_reopen']==1 and row['stop_generation']==row['discard_generation']>0,'exact Stop/discard generation')
                else: need(all(row[key]==1 for key in ('maintenance_resume','held_quiet','play_blocked','token_consumed','stale_rejected')),'actual three-owner maintenance and tokens')
    expected_links=[(name,0,name) for name in FIXTURES for _ in range(3)]+[('CHAIN',0,'OPUS20'),('CHAIN',1,'VORBIS'),('CHAIN',2,'OPUS120')]
    need([(row['fixture'],row['index'],row['codec']) for row in links]==expected_links,'every complete logical link independently hashed in actual order')
    for row in links: need(row['bytes']==2112000 and row['sha256']==references['fixtures'][row['codec']]['pcm_sha256'],'exact individual logical-link hash')
    need(chain and chain['links']==3 and all(chain[key]==1 for key in ('one_http','same_generation','single_eof')) and
         chain['cross_link_reads']>0 and chain['pcm_bytes']==6336000 and re.fullmatch('[a-f0-9]{64}',chain['sha256']) and
         chain['opens']==chain['closes']==18 and chain['http_cleanup']==16,'three links in one HTTP session/generation without intermediate PCM terminal')
    need(complete and complete['cases']==10 and complete['actual_audio_service_tu']==1 and complete['opens']==complete['closes']==18 and
         complete['live_decoders']==complete['live_clients']==0 and complete['real_http_cleanup']==16 and complete['output_flushes']==10 and
         complete['initial_capacity_checks']==18 and complete['resize_requests']==complete['resize_retries'] and complete['core_bindings']==1 and
         complete['process_calls']>0 and complete['heap_integrity']==1 and complete['hardware']==0,'all actual final public owners and single-EOF census')
    for role,size in [('stream',6144),('decode',16384),('output',4096)]: need(0<complete[role+'_stack_free']<=size,'actual owner stack watermark')
    need(0<complete['heap_min']<=complete['heap_free'] and 0<complete['largest_internal']<=complete['heap_free'],'actual global heap/free-block observations')
    need(len(memory)==16 and all(0<row['heap_min']<=row['heap_free'] and 0<row['largest_internal']<=row['heap_free'] for row in memory),'EOF/Stop/HELD/chain resource observations')
    need([row['fixture'] for row in fixtures]==list(FIXTURES),'complete fixture/page census')
    for row in fixtures: need(row['encoded']==FIXTURES[row['fixture']]['bytes'] and row['max_page']==references['fixtures'][row['fixture']]['max_page_bytes'],'actual maximum encoded page bound')
    active=None;handles=[];pending=None;last_calls=0;resizes=[];retries=[]
    for tag,row in observations:
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
    need(active is None and pending is None and len(handles)==18 and last_calls==complete['process_calls'] and len(resizes)==complete['resize_requests'] and len(retries)==complete['resize_retries'],'all eighteen public handles close with exact process/resize totals')
    need([row['fixture'] for row in handles]==['OPUS20']*5+['OPUS120']*5+['VORBIS']*5+['CHAIN']*3,'expected actual logical decoder ownership census')
    need(len({row['generation'] for row in handles[-3:]})==1,'same actual generation across all chained logical links')
    need(all(row['initial']==12288 for row in handles[:15]),'new station lifecycles retain initial production allocation')
    need(all(row['resizes']==1 and row['last_capacity']==23040 for row in handles[5:10]),'every real120ms lifecycle handle grows once to23040')
    return dict(cases=cases,chain=chain,links=links,memory=memory,fixtures=fixtures,complete=complete,
                public_handles=handles,resize_observations=resizes,retry_observations=retries,
                independent_position_reference=True,numeric_conformance_claim=False,physical_device=False)


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


# Strict playback transcript reader is defined below.


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--build-timeout', type=int, default=1200)
    parser.add_argument('--qemu-timeout', type=int, default=600)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    need(sys.platform == 'win32', 'Installed Windows SDK/QEMU launcher required')
    need(1 <= args.build_timeout <= 1200 and 1 <= args.qemu_timeout <= 1200, 'bounded native command deadlines')
    args.output = args.output.resolve()
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
        self.report = dict(passed=False, completed=False, commands=[], actual_audio_service_tu=True,
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
        for component in ('native_stream', 'native_network_power'):
            paths.update(p for p in (ROOT / 'idf/components' / component).rglob('*') if p.is_file())
        paths.update(p for p in (ROOT / 'idf/components/native_wifi_store/include').rglob('*') if p.is_file())
        paths.add(ROOT / 'idf/components/audio_level_led/audio_level_led.h')
        paths.add(main / 'aac_public_config.h')
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

    def reference(self):
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
        need(all(any(Path(row['file']).name == name for row in used) for name in MAIN_TUS), 'all four complete production translation units')
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
        need({'ogg_playback.h','ogg_page_input.h','opus_pcm_trim.h','ogg_opus_timeline.h','aac_public_config.h'}<=used_headers,
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
            scope=__doc__, expected_cases=['T0', 'T1', 'T2']))
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
            self.report['measurements'] = validate_log(log + '\n' + (self.out / 'qemu.stderr.log').read_text(errors='replace'), self.report['pcm_reference'])
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
