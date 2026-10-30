"""Run actual CYD audio-service tasks with unchanged Espressif Vorbis in QEMU.

Synthetic HTTP transport and output/LED hardware are explicit seams. SDK HTTP
allocation/cleanup, RTOS scheduling, production translation units and shared
queues remain real. The PCM oracle is the frozen direct-vendor integration
checkpoint, not an independent codec-quality or universal conformance oracle.
No physical board, external network, private codec ABI or custom decoder is used.
"""
import argparse
import hashlib
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
HARNESS = ROOT / 'tests/target/cyd_espressif_vorbis_task_qemu'
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


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def validate_log(log):
    """Read only the exact whole-task protocol; never start native tools."""
    log = log.replace('\r\n', '\n')
    need(not re.search(r'CYD_VORBIS_TASK_FAILURE|Guru Meditation|abort\(\)|Backtrace:|assert failed|'
                       r'CORRUPT HEAP|watchdog.*triggered|stack (?:smashing|overflow)|panic.ed', log, re.I),
         'no target failure, panic, watchdog, stack or heap corruption')
    prefix = 'CYD_VORBIS_TASK_'
    need(not any(prefix in line and not line.startswith(prefix) for line in log.splitlines()),
         'no torn or foreign task records')
    lines = [line for line in log.splitlines() if line.startswith(prefix)]
    need(len(lines) == 8, 'exact BOOT, three profiles, three cases and COMPLETE records')
    need(lines[0] == 'CYD_VORBIS_TASK_BOOT actual_audio_service_tu=1 sdk=v6.0.2 coordinator=0 fixture=703584 hardware=0',
         'whole unchanged CYD task and known encoded fixture')
    profiles = [('stream', 0, 3, 6144), ('decode', 1, 5, 16384), ('output', 1, 6, 4096)]
    for line, (role, core, priority, stack) in zip(lines[1:4], profiles):
        need(line == f'CYD_VORBIS_TASK_PROFILE role={role} core={core} priority={priority} stack={stack}',
             'original actual task core, priority and stack: ' + role)
    positive = r'[1-9][0-9]*'

    def record(line, pattern, description):
        match = re.fullmatch(pattern, line)
        need(match, 'strict canonical ' + description + ' record')
        return {key: int(value) for key, value in match.groupdict().items()}

    t0 = record(lines[4], 'CYD_VORBIS_TASK_CASE id=T0 ordered_eof=1 pcm_bytes=2112000 sha256=' + PCM_SHA +
                rf' opens=1 closes=1 http_cleanup=1 writes=(?P<writes>{positive}) metadata=1', 'ordered EOF')
    t1 = record(lines[5], rf'CYD_VORBIS_TASK_CASE id=T1 stop_reopen=1 partial_pcm=(?P<partial_pcm>{positive}) '
                rf'stop_generation=(?P<stop_generation>{positive}) discard_generation=(?P<discard_generation>{positive}) '
                'pcm_bytes=2112000 sha256=' + PCM_SHA +
                rf' opens=3 closes=3 http_cleanup=3 writes=(?P<writes>{positive}) metadata=1', 'Stop/reopen')
    need(t1['partial_pcm'] < PCM_BYTES and t1['stop_generation'] == t1['discard_generation'],
         'actual partial Stop and output discard barrier for its exact generation')
    t2 = record(lines[6], rf'CYD_VORBIS_TASK_CASE id=T2 maintenance_resume=1 partial_pcm=(?P<partial_pcm>{positive}) '
                'held_quiet=1 play_blocked=1 token_consumed=1 stale_rejected=1 pcm_bytes=2112000 sha256=' + PCM_SHA +
                rf' opens=5 closes=5 http_cleanup=5 writes=(?P<writes>{positive}) metadata=1', 'maintenance/resume')
    need(t2['partial_pcm'] < PCM_BYTES, 'maintenance interrupts an actual partial stream before automatic full resume')
    complete = record(lines[7], 'CYD_VORBIS_TASK_COMPLETE cases=3 actual_audio_service_tu=1 opens=5 closes=5 '
                rf'live_decoders=0 real_http_cleanup=5 live_clients=0 process_calls=(?P<process_calls>{positive}) '
                rf'resize_requests=0 core_bindings=1 stream_stack_free=(?P<stream_stack_free>{positive}) '
                rf'decode_stack_free=(?P<decode_stack_free>{positive}) output_stack_free=(?P<output_stack_free>{positive}) '
                rf'heap_free=(?P<heap_free>{positive}) heap_min=(?P<heap_min>{positive}) heap_integrity=1 hardware=0', 'terminal cleanup')
    for role, _, _, stack in profiles:
        need(complete[role + '_stack_free'] <= stack, 'observed stack headroom within original task allocation: ' + role)
    need(complete['heap_min'] <= complete['heap_free'], 'observed minimum/free heap relation')
    return dict(cases={'T0': t0, 'T1': t1, 'T2': t2}, profiles=[dict(role=role, core=core, priority=priority, stack=stack)
                for role, core, priority, stack in profiles], complete=complete, full_pcm_bytes=PCM_BYTES,
                full_pcm_sha256=PCM_SHA, opened_and_closed=5, real_http_cleanup=5,
                independent_numeric_oracle=False, physical_device=False)


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--build-timeout', type=int, default=1200)
    parser.add_argument('--qemu-timeout', type=int, default=180)
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
                HARNESS / 'sdk-build.ps1', HARNESS / 'project/main/main.cpp',
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
    return args


class Campaign:
    def __init__(self, args):
        self.args, self.out = args, args.output
        self.sources, self.runtime, self.artifacts = {}, {}, {}
        self.report = dict(passed=False, completed=False, commands=[], actual_audio_service_tu=True,
                           actual_rtos=True, target_executed=False, production_firmware=False,
                           physical_device=False, external_network=False, private_codec_abi=False,
                           custom_decoder=False, oom_injection=False, output_backpressure=False,
                           full_pcm_independent_oracle=False, performance_or_radio_resource_claim=False)
        self.environment = os.environ.copy()
        self.environment.update(GIT_OPTIONAL_LOCKS='0', PYTHONNOUSERSITE='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8')

    def save(self):
        write_json(self.out / 'report.json', self.report)

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
        self.freeze(self.args.fixture, Path('sources/harness/project/main/fixture.ogg'), 'encoded-only known valid fixture')
        self.freeze(Path(__file__), Path('sources/controller.py'), 'campaign controller')
        self.freeze(REFERENCE / 'native-manifest.json', Path('sources/reference/native-manifest.json'), 'pinned direct-vendor reference manifest')
        self.reference()
        write_json(self.out / 'source-manifest.json', self.sources)

    def reference(self):
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
        self.runtime[str(REFERENCE / 'native-captures.zip')] = REFERENCE_ARCHIVE_SHA
        self.report['pcm_reference'] = dict(kind='frozen original-vendor integration regression', bytes=PCM_BYTES,
            sha256=PCM_SHA, checkpoint_manifest_sha256=REFERENCE_MANIFEST_SHA,
            checkpoint_archive_sha256=REFERENCE_ARCHIVE_SHA, independent_numeric_oracle=False)

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
                    'AUDIO_DECODER_VORBIS_SUPPORT', 'AUDIO_SIMPLE_DEC_OGG_SUPPORT'):
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
        for path in (compiler, nm, ninja): self.runtime[str(path)] = sha(path)
        self.run_command('compiler-version', [compiler, '--version'])
        self.compiler_closure(commands, ninja)
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
                try: unchanged = sha(Path(name) if root is None else root / name) == expected
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
                self.runtime[str(path)] = sha(path)
            self.verify_repositories()
            self.report['repository_head_at_freeze'] = self.run_command('repository-head',
                [self.args.git, '-c', 'core.longpaths=true', '-C', ROOT, 'rev-parse', 'HEAD']).strip()
            print('Building complete CYD audio-service tasks and unchanged vendor decoder', flush=True)
            self.run_command('build', [self.args.powershell, '-NoProfile', '-NonInteractive', '-File',
                self.out / 'sources/harness/sdk-build.ps1', '-OutputDirectory', self.out, '-IdfDirectory', self.args.idf,
                '-IdfToolsDirectory', self.args.idf_tools, '-IdfPythonExecutable', self.args.idf_python], self.args.build_timeout)
            flash = self.qualify_build()
            print('Starting actual-task Vorbis EOF, Stop/reopen and maintenance/resume QEMU cases', flush=True)
            log = self.run_command('qemu', [self.args.qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet', '-smp', '2',
                '-L', self.args.rom, '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none',
                '-drive', 'file=' + str(flash).replace(',', ',,') + ',if=mtd,format=raw'], self.args.qemu_timeout)
            self.report['measurements'] = validate_log(log + '\n' + (self.out / 'qemu.stderr.log').read_text(errors='replace'))
            self.verify_repositories('-after')
            need(self.verify_inputs(), 'every bound input unchanged after target execution')
            self.report.update(passed=True, completed=True)
            print('PASS actual CYD task Vorbis lifecycle; physical and radio/TLS resource qualification remains separate', flush=True)
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
