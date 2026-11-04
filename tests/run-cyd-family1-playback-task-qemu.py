"""Complete actual CYD family1 tasks against independent direct-public PCM and Decimal output.

New target/controller only. Native action is blocked until root pins its final
integration release. No private ABI, hardware, external network or tolerance.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent.parent if ROOT.parent.name=='.worktree' else ROOT
HARNESS=ROOT/'tests/target/cyd_family1_playback_task_qemu'
MAIN=Path('idf/esp32-cyd2usb-native/main')
MAIN_TUS=('audio_service.c','native_state.c','native_health.c','decoder_registration.c','native_audio_output.c','native_output_metrics.c')
SDK_COMMIT='7101770dc6db2667b3c477cc31365dd1acd6db4e'
VENDOR_COMMIT='67b8d0e98f58c774b8652480893037273190e8dc'
ARCHIVE_PINS={'libesp_audio_codec.a':'92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58',
    'libesp_audio_simple_dec.a':'ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6'}
QEMU_SHA='4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d'
SOURCE_RELEASE_SHA='745e7482cd90517c4e5778717dd7e1016d4e8c692d125f4a3cf15302e7dc9381'
SOURCE_RELEASE_FILES=35
CONTRACT=ROOT/'tests/prepare-cyd-family1-task-contract.py'
ASSETS=ROOT/'tests/prepare-cyd-family1-task-assets.py'
READER=ROOT/'tests/read-cyd-family1-task-log.py'
WORD_READER=ROOT/'tests/read-cyd-family1-word-alloc.py'
FAULT_READER=ROOT/'tests/read-cyd-family1-allocation-faults.py'
OUTPUT=ROOT/'tests/prepare-cyd-family1-task-output.py'

def need(value,reason):
    if not value:raise ValueError(reason)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def assets():return module('current_family1_task_assets',ASSETS)
def reader():return module('current_family1_task_log_reader',READER)

def word_reader():return module('current_family1_word_allocation_reader',WORD_READER)
def output_oracle():return module('independent_family1_task_Decimal',OUTPUT)

class Campaign:
    def __init__(self, args):
        self.args, self.out = args, args.output
        self.sources, self.runtime, self.artifacts = {}, {}, {}
        self.runtime_paths = {}
        self.report = dict(passed=False, completed=False, commands=[], actual_audio_service_tu=True, actual_output_tu=True,
                           actual_rtos=True, target_executed=False, production_firmware=False,
                           physical_device=False, external_network=False, private_codec_abi=False,
                           custom_decoder=False, oom_injection=False, output_backpressure=False, same_vendor_family1_integration_oracle=True,
                           full_pcm_independent_oracle=False, performance_or_radio_resource_claim=False)
        self.report.update(public_raw_handles=True,actual_family1_adapter=True,production_selected_in_frozen_task=True,
                           native_resource_refusal_is_format_allowance=False,new_numeric_tolerance=False)
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
        need(sha(self.args.source_release)==SOURCE_RELEASE_SHA and len(release['files'])==SOURCE_RELEASE_FILES,
             'exact root-authorized final source/API release')
        need(release['production_sources_frozen'] and not release['full_task_qualified'] and not release['hardware_qualified'] and
             release['task_profiles']=={'stream_task':dict(core=0,priority=3,stack_bytes=6144),
                'decoder_task':dict(core=1,priority=5,stack_bytes=16384),'output_task':dict(core=1,priority=6,stack_bytes=4096)},
             'released original task profiles and unqualified native/hardware scope')
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
                 'all root-released source bytes joined to the actual frozen input manifest')
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
                    'AUDIO_DECODER_OPUS_SUPPORT', 'AUDIO_DECODER_VORBIS_SUPPORT', 'AUDIO_SIMPLE_DEC_OGG_SUPPORT', 'YORADIO_NATIVE_AUDIO_OUTPUT_PDM', 'YORADIO_OGG_TIMELINE'):
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
        need({'ogg_playback.h','ogg_page_input.h','opus_pcm_trim.h','ogg_opus_timeline.h','aac_public_config.h','opus_family1_playback.h','opus_family1_decoder.h','opus_tags_stream.h','ogg_opus_audio_packets.h','opus_multistream_framing.h','opus_family1_mapping.h','pcm_header_gain.h','pcm_channel_layout.h','pcm_speaker_mix.h','native_audio_settings.h','native_audio_normalizer.h','AudioNormalizer.h','stream_fairness.h'}<=used_headers,
             'actual GCC closure consumes public family1 dispatch and actual output/settings/normalizer headers')
        for unit in closure['translation_units']:
            if Path(unit['file']).name in ('direct_reference.c','reference_control.c'):
                need(not set(self.report['pcm_reference']['independent_public_reference_helpers_excluded']) &
                     {Path(path).name for path in unit['actual_dependency_paths']},
                     'independent direct-public reference excludes production framing/map/trim/page/mix helpers')
        independent=[unit for unit in closure['translation_units'] if Path(unit['file']).name in ('direct_reference.c','reference_control.c')]
        need(len(independent)==2,'both independent direct-public reference TUs actually compiled whole')
        elf = (build / desc['app_elf']).resolve()
        app = (build / desc['app_bin']).resolve()
        need(config.get('ESPTOOLPY_FLASHSIZE_4MB') and app.stat().st_size<=0x3f0000,
             'actual complete app plus immutable diagnostic fixtures fits original4MB profile')
        need(elf.is_relative_to(build) and app.is_relative_to(build) and elf.read_bytes()[:6] == b'\x7fELF\x01\x01' and
             int.from_bytes(elf.read_bytes()[18:20], 'little') == 94, 'actual LX6 ELF32 image')
        symbols = self.run_command('symbols', [nm, '-n', '--defined-only', elf])
        for name in ('decoder_task', 'stream_task', 'output_task', 'audio_service_start', 'decoder_register_codecs',
                     'adaptive_input_receive', 'xRingbufferReceive', 'esp_audio_simple_dec_process',
                     '__wrap_esp_audio_simple_dec_open', '__wrap_esp_audio_simple_dec_process', '__wrap_esp_audio_simple_dec_close',
                     '__wrap_esp_opus_dec_open','__wrap_esp_opus_dec_decode','__wrap_esp_opus_dec_close'):
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
            print('Building complete CYD public family1 stream/decoder/output tasks', flush=True)
            self.run_command('build', [self.args.powershell, '-NoProfile', '-NonInteractive', '-File',
                self.out / 'sources/harness/sdk-build.ps1', '-OutputDirectory', self.out, '-IdfDirectory', self.args.idf,
                '-IdfToolsDirectory', self.args.idf_tools, '-IdfPythonExecutable', self.args.idf_python], self.args.build_timeout)
            flash = self.qualify_build()
            print('Starting direct public family1 reference and actual application tasks', flush=True)
            log = self.run_command('qemu', [self.args.qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet', '-smp', '2',
                '-L', self.args.rom, '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none',
                '-drive', 'file=' + str(flash).replace(',', ',,') + ',if=mtd,format=raw'], self.args.qemu_timeout)
            complete_log=log+'\n'+(self.out/'qemu.stderr.log').read_text(errors='replace')
            # Keep a truthful partial allocation trace even if the actual task
            # fails. A complete native PASS still requires the terminal census.
            try:self.report['word_allocation_prefix']=word_reader().parse_word_allocation_log(complete_log,require_terminal=False)
            except ValueError as word_error:self.report['word_allocation_prefix_error']=str(word_error)
            measured,pcm=reader().validate(complete_log,self.report['pcm_reference'])
            self.report['measurements']=measured
            self.report['word_allocations']=word_reader().parse_word_allocation_log(complete_log,require_terminal=True)
            self.report['post_output_oracle']=output_oracle().qualify(self.report['pcm_reference'],measured,pcm,self.out)
            write_json(self.out/'post-output-oracle.json',self.report['post_output_oracle'])
            post_paths=[self.out/'post-output-oracle.json',*(self.out/('reference-'+str(index)+'.pcm') for index in range(13))]
            self.report['post_output_artifacts']={path.relative_to(self.out).as_posix():dict(bytes=path.stat().st_size,sha256=sha(path)) for path in post_paths}
            self.artifacts.update({name:pin['sha256'] for name,pin in self.report['post_output_artifacts'].items()})

            self.verify_repositories('-after')
            need(self.verify_inputs(), 'every bound input unchanged after target execution')
            self.report.update(passed=True, completed=True)
            print('PASS actual family1 task integration and exact independent Decimal final output; codec/hardware conformance remains separate', flush=True)
        except BaseException as error:
            self.report.update(passed=False, completed=False, failure_type=type(error).__name__, failure=str(error))
            print(json.dumps(dict(passed=False, failure_type=type(error).__name__, failure=str(error))), file=sys.stderr)
        finally:
            if not self.verify_inputs(): self.report['passed'] = False
            self.save()
        return 0 if self.report['passed'] else 1


    def reference(self):
        contract,blob,header,size_header,source=assets().prepare()
        self.report['pcm_reference']=contract
        data=module('current_family1_task_data_sources',CONTRACT)
        fixture_preparer=module('completed_family1_native_fixture_sources',data.PREP)
        for path in (CONTRACT,ASSETS,READER,WORD_READER,FAULT_READER,OUTPUT,data.PREP,fixture_preparer.FRAMING,fixture_preparer.READER,
                     ROOT/'tests/fixtures/opus_family1_120ms/prepare.py'):
            self.freeze(path,Path('sources/reference/controllers')/path.relative_to(ROOT),'reviewed independent fixture/data helper or current canonical reader')
        for c in (3,6,8):
            self.freeze(data.REFERENCE/('channels'+str(c)+'.packets'),Path('sources/reference/originals')/('channels'+str(c)+'.packets'),'complete original creator-qualified20ms input')
        self.freeze(fixture_preparer.LONG,Path('sources/reference/originals')/fixture_preparer.LONG.name,'all92 original120ms packets, unchanged')
        for path in data.STRESS.parent.rglob('*'):
            if path.is_file():self.freeze(path,Path('sources/reference/creator120')/path.relative_to(data.STRESS.parent),'real creator public repacketization provenance; not executed as archived code')
        for pin in data.LEGACY.values():
            self.freeze(ROOT/pin['path'],Path('sources/reference/originals')/Path(pin['path']).name,'complete unchanged family0/Vorbis successor')
        for index,pin in output_oracle().LEGACY_PCM.items():
            path=ROOT/pin['path'];need(sha(path)==pin['sha256'] and path.stat().st_size==pin['bytes'],'earlier full stock PCM identity')
            self.freeze(path,Path('sources/reference/stock')/(str(index)+'.pcm'),'earlier complete stock integer PCM, local-only whole payload')
        for folder in ('cyd-opus-position-20261101','cyd-ogg-gain-task-20261101'):
            self.freeze(ROOT/'tests/results'/folder/'manifest.json',Path('sources/reference/checkpoints')/(folder+'.json'),'original stock/reference public checkpoint identity')
        for name,body in [('reference.h',header.encode()),('asset_size.h',size_header.encode()),('fixtures.bin',blob)]:
            path=self.out/'sources/harness/project/main'/name;path.write_bytes(body);self.freeze(path,path.relative_to(self.out),'lossless immutable encoded body/span storage and exact descriptor view')
        for name,value in [('reference-contract.json',contract),('fixture-preparation.json',source)]:
            path=self.out/name;write_json(path,value);self.freeze(path,Path('sources/reference')/name,'complete pure-data preparation/packet provenance')


def arguments():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--preflight-only',action='store_true')
    parser.add_argument('--source-release',type=Path,default=ROOT/'.build/cyd-family1-source-release-20261103-02.json')
    parser.add_argument('--build-timeout',type=int,default=1200)
    parser.add_argument('--qemu-timeout',type=int,default=600)
    args=parser.parse_args();args.output=args.output.resolve();args.source_release=args.source_release.resolve()
    need(args.output.is_relative_to(ROOT/'.build') and args.output!=ROOT/'.build' and not args.output.exists(),'fresh contained local output')
    need(1<=args.build_timeout<=1200 and args.qemu_timeout==600,'bounded SDK and unchanged fixed600s whole-QEMU limit')
    args.idf=REPO/'.idf/v6.0.2';args.idf_tools=REPO/'.idf/tools-v6.0.2';args.vendor=REPO/'.idf/esp-adf-libs/esp_audio_codec'
    args.idf_python=args.idf_tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    args.qemu=ROOT/'.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe';args.rom=Path('C:/Work/QEMU-ESP32/pc-bios')
    args.powershell=Path(shutil.which('pwsh.exe') or '');args.git=Path(shutil.which('git.exe') or shutil.which('git') or '')
    if not args.prepare_only:
        need(sys.platform=='win32','installed Windows compiler/QEMU runtime')
        required=(args.idf/'export.ps1',args.idf/'tools/idf.py',args.idf_python,args.qemu,args.git,args.powershell,
                  args.rom/'esp32-v3-rom.bin',args.rom/'esp32-v3-rom-app.bin',HARNESS/'project/main/main.cpp',HARNESS/'sdk-build.ps1')
        need(all(path.is_file() for path in required),'complete installed runtime and prepared new target')
        need(sha(args.qemu)==QEMU_SHA and all(sha(args.vendor/'lib/esp32'/name)==digest for name,digest in ARCHIVE_PINS.items()),'exact pinned QEMU/vendor archives')
        for protected in (args.idf,args.idf_tools,args.vendor,args.rom,args.qemu.parent,args.git.parent,args.powershell.parent,Path(sys.executable).resolve().parent):
            need(not (args.output==protected or args.output.is_relative_to(protected) or protected.is_relative_to(args.output)),'output cannot overlap an installed runtime')
        if not args.preflight_only or SOURCE_RELEASE_SHA!='UNRELEASED':
            need(re.fullmatch('[a-f0-9]{64}',SOURCE_RELEASE_SHA or '') and args.source_release.is_file() and sha(args.source_release)==SOURCE_RELEASE_SHA,'root integration release is explicitly pinned before any SDK action')
            release=json.loads(args.source_release.read_bytes())
            need(len(release['files'])==SOURCE_RELEASE_FILES and all(sha(ROOT/relative)==pin['sha256'] and (ROOT/relative).stat().st_size==pin['bytes'] for relative,pin in release['files'].items()),'all35 released production bytes current before native action')
    return args

def main():
    args=arguments()
    if args.prepare_only:
        contract,blob,header,size_header,source=assets().prepare();args.output.mkdir(parents=True)
        for name,value in [('contract.json',contract),('fixture-preparation.json',source)]:write_json(args.output/name,value)
        for name,body in [('reference.h',header.encode()),('asset_size.h',size_header.encode()),('fixtures.bin',blob)]: (args.output/name).write_bytes(body)
        print(json.dumps(dict(passed=True,prepared_only=True,cases=48,HTTP_sessions=58,direct_references=13,asset_bytes=len(blob),target_executed=False,actual_image_fit_measured=False)));return 0
    if args.preflight_only:
        contract,blob,header,size_header,source=assets().prepare()
        print(json.dumps(dict(preflight=True,installed_pins_current=True,output_created=False,production_sources_frozen=False,source_release_pinned=SOURCE_RELEASE_SHA!='UNRELEASED',target_executed=False)));return 0
    return Campaign(args).execute()

if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
