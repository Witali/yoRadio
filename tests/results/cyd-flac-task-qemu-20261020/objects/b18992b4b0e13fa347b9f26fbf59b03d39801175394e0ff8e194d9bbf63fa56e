"""Run three public-API CYD audio lifecycle cases in local ESP32 QEMU.

Build the unchanged complete audio_service.c, native_state.c, native_health.c
and decoder_registration.c with the real SDK tasks, adaptive input, PCM ring,
custom FLAC and allocators. Compare output bytes with independent FFmpeg PCM
oracles. HTTP transport and the public output/LED backend are explicit seams;
HTTP client init/cleanup remain real SDK calls. This checkpoint covers ordered
EOF, Stop/reopen and maintenance/resume, without private phase/ACK writes.
HTTP request-TX release is explicitly disabled because the synthetic transport
does not enter the SDK's connected/header state; its real HTTP gate is separate.
It does not inject OOM, exercise output backpressure, use a physical device,
or establish radio performance or production resource margins.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / 'tests/target/cyd_flac_task_qemu'
MAIN = Path('idf/esp32-cyd2usb-native/main')
SDK_COMMIT = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
MAIN_TUS = ['audio_service.c', 'native_state.c', 'native_health.c',
            'decoder_registration.c']
EXPECTED_CASES = ['T0', 'T1', 'T2']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def nearest_installed(relative):
    return next((base / relative for base in (ROOT, *ROOT.parents)
                 if (base / relative).exists()), None)


def overlaps(first, second):
    return first == second or first.is_relative_to(second) or second.is_relative_to(first)


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='New directory below .build/ or outside source/install trees')
    parser.add_argument('--idf', type=Path,
                        default=os.environ.get('IDF_PATH') or nearest_installed('.idf/v6.0.2'))
    parser.add_argument('--idf-tools', type=Path,
                        default=os.environ.get('IDF_TOOLS_PATH') or nearest_installed('.idf/tools-v6.0.2'))
    parser.add_argument('--idf-python', type=Path,
                        help='SDK virtualenv Python; defaults below --idf-tools')
    parser.add_argument('--vendor-component', type=Path,
                        default=nearest_installed('.idf/esp-adf-libs/esp_audio_codec'),
                        help='Installed esp_audio_codec component, including lib/esp32')
    parser.add_argument('--qemu', type=Path,
                        default=shutil.which('qemu-system-xtensa.exe') or shutil.which('qemu-system-xtensa'))
    parser.add_argument('--rom-directory', type=Path, help='Defaults to QEMU ../pc-bios')
    parser.add_argument('--ffmpeg', type=Path, default=shutil.which('ffmpeg'))
    parser.add_argument('--powershell', type=Path,
                        default=shutil.which('pwsh.exe') or shutil.which('pwsh'))
    parser.add_argument('--build-timeout', type=int, default=600)
    parser.add_argument('--qemu-timeout', type=int, default=180)
    parser.add_argument('--preflight-only', action='store_true',
                        help='Validate paths and fresh-output protection; create no output and run no build/emulator')
    args = parser.parse_args()
    if sys.platform != 'win32':
        parser.error('This installed ESP-IDF/QEMU launcher currently supports Windows only')
    if not 1 <= args.build_timeout <= 3600 or not 1 <= args.qemu_timeout <= 3600:
        parser.error('Build and QEMU timeouts must be 1..3600 seconds')
    for name in ('idf', 'idf_tools', 'vendor_component', 'qemu', 'ffmpeg', 'powershell'):
        if not getattr(args, name):
            parser.error('--' + name.replace('_', '-') + ' is required when it cannot be discovered')
        setattr(args, name, Path(getattr(args, name)).resolve())
    args.output = args.output.resolve()
    args.idf_python = (args.idf_python or args.idf_tools /
                       'python_env/idf6.0_py3.12_env/Scripts/python.exe').resolve()
    args.rom_directory = (args.rom_directory or args.qemu.parent.parent / 'pc-bios').resolve()
    out = args.output
    if out.exists():
        parser.error('Output already exists; preserve completed/partial campaigns and choose a fresh directory')
    if out == ROOT or out in ROOT.parents or (out.is_relative_to(ROOT) and
                                             not out.is_relative_to(ROOT / '.build')):
        parser.error('Repository output must be below .build/; source directories are protected')
    protected = [args.idf, args.idf_tools, args.vendor_component, args.idf_python.parent,
                 Path(sys.executable).resolve().parent, args.qemu.parent, args.rom_directory,
                 args.ffmpeg.parent, args.powershell.parent]
    if any(overlaps(out, path) for path in protected):
        parser.error('Output must not overlap SDK, vendor, Python, PowerShell, FFmpeg, QEMU or ROM installations')
    if any((parent / 'execution-bundle.json').exists() or (parent / 'report.json').exists()
           for parent in out.parents):
        parser.error('Output must not be nested inside an existing evidence campaign')
    if not out.is_relative_to(ROOT / '.build'):
        enclosing = next((path for path in out.parents if (path / '.git').exists()), None)
        if enclosing and not out.is_relative_to(enclosing / '.build'):
            parser.error('Output inside another repository must be below its .build/ directory')
    required = [args.idf / 'tools/idf.py', args.idf / 'export.ps1',
                args.idf / 'tools/tools.json', args.idf_tools / 'idf-env.json',
                args.idf_python, args.qemu, args.ffmpeg, args.powershell,
                args.rom_directory / 'esp32-v3-rom.bin',
                args.rom_directory / 'esp32-v3-rom-app.bin',
                args.vendor_component / 'CMakeLists.txt',
                args.vendor_component / 'lib/esp32/libesp_audio_codec.a',
                args.vendor_component / 'lib/esp32/libesp_audio_simple_dec.a',
                HARNESS / 'sdk-build.ps1', HARNESS / 'project/main/main.cpp',
                ROOT / MAIN / 'audio_service.c',
                ROOT / 'tools/audio_test_server/generate_flac_depths.py']
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        parser.error('Missing installed/source inputs: ' + ', '.join(missing))
    return args


class Campaign:
    def __init__(self, args):
        self.args = args
        self.out = args.output
        self.sources = {}
        self.inputs = {}
        self.artifacts = {}
        self.runtime = {}
        self.report = {'passed': False, 'scope': __doc__, 'commands': [],
                       'actual_audio_service_tu': True, 'actual_rtos': True,
                       'physical_hardware': False, 'oom_injection': False,
                       'output_backpressure': False,
                       'performance_or_radio_resource_claim': False}
        self.environment = os.environ.copy()
        self.environment.update(GIT_OPTIONAL_LOCKS='0', PYTHONUTF8='1',
                                PYTHONIOENCODING='utf-8', PYTHONNOUSERSITE='1')

    def save(self):
        write_json(self.out / 'report.json', self.report)

    def execute(self, name, command, timeout=60, binary=False):
        command = list(map(str, command))
        started = time.monotonic()
        child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 env=self.environment, creationflags=subprocess.CREATE_NO_WINDOW)
        timed_out = False
        try:
            log, _ = child.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            # Kill only this campaign's child and descendants, retaining partial logs.
            killed = subprocess.run(['taskkill.exe', '/PID', str(child.pid), '/T', '/F'],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            (self.out / (name + '-timeout-cleanup.log')).write_bytes(killed.stdout)
            log, _ = child.communicate(timeout=15)
        if not binary:
            (self.out / (name + '.log')).write_bytes(log)
        self.report['commands'].append({'name': name, 'command': command,
                                        'exit_status': child.returncode, 'timed_out': timed_out,
                                        'elapsed_seconds': time.monotonic() - started,
                                        'output_sha256': hashlib.sha256(log).hexdigest()})
        self.save()
        if timed_out or child.returncode:
            raise RuntimeError(name + (' timed out' if timed_out else ' failed') + ': ' +
                               log.decode(errors='replace')[-6000:])
        return log if binary else log.decode(errors='replace').replace('\r\n', '\n')

    def snapshot(self, original, relative, role):
        original = original.resolve()
        target = self.out / relative
        data = original.read_bytes()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        assert sha(original) == digest, 'Source changed while being frozen: ' + str(original)
        self.sources[str(original)] = {'sha256': digest, 'snapshot': str(relative), 'role': role}

    def freeze_sources(self):
        main = ROOT / MAIN
        compiled = {main / name for name in MAIN_TUS}
        metadata = {main / name for name in ['native_audio_output.c', 'network_service.c',
                                             'CMakeLists.txt', 'Kconfig.projbuild']}
        paths = compiled | metadata | set(main.rglob('*.h'))
        for component in ['native_stream', 'native_network_power', 'custom_flac', 'custom_codec_support']:
            paths.update(path for path in (ROOT / 'idf/components' / component).rglob('*') if path.is_file())
        paths.update(path for path in (ROOT / 'idf/components/native_wifi_store/include').rglob('*') if path.is_file())
        paths.update(path for path in (ROOT / 'yoRadio/src/audioI2S/flac_decoder').glob('*') if path.is_file())
        paths.update(ROOT / 'yoRadio/src/audioI2S' / name for name in ['CodecMemoryArena.cpp', 'CodecMemoryArena.h'])
        paths.update([ROOT / 'idf/components/audio_level_led/audio_level_led.h',
                      ROOT / 'tools/audio_test_server/generate_flac_depths.py'])
        for path in sorted(paths):
            self.snapshot(path, Path('sources/repository') / path.relative_to(ROOT),
                          'whole production TU' if path in compiled else 'repository input; actual use recorded by compiler closure')
        vendor = self.args.vendor_component
        vendor_files = {path for path in vendor.iterdir() if path.is_file()}
        for folder in ['src', 'include', 'lib/esp32']:
            vendor_files.update(path for path in (vendor / folder).rglob('*') if path.is_file())
        for path in sorted(vendor_files):
            self.snapshot(path, Path('sources/vendor/esp_audio_codec') / path.relative_to(vendor),
                          'installed esp_audio_codec input')
        for path in sorted(HARNESS.rglob('*')):
            if path.is_file():
                self.snapshot(path, Path('sources/harness') / path.relative_to(HARNESS), 'test harness')
        runner = Path(__file__).resolve()
        self.snapshot(runner, Path('sources/runner') / runner.name, 'campaign runner')
        write_json(self.out / 'source-manifest.json', self.sources)

    def verify_sdk(self, suffix=''):
        args = ['git', '-c', 'core.longpaths=true', '-C', self.args.idf]
        assert self.execute('sdk-head' + suffix, args + ['rev-parse', 'HEAD']).strip() == SDK_COMMIT
        assert not self.execute('sdk-tracked' + suffix,
                                args + ['status', '--porcelain', '--untracked-files=no']).strip()

    def fixtures(self):
        generator_path = self.out / 'sources/repository/tools/audio_test_server/generate_flac_depths.py'
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location('frozen_flac_fixtures', generator_path)
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        small = generator.generate(self.out / 'fixtures/small')
        large = generator.generate(self.out / 'fixtures/large', large_blocks=True)
        rows = [(self.out / 'fixtures/small', row) for row in small['fixtures']]
        rows += [(self.out / 'fixtures/large', row) for row in large['fixtures']]
        assert len(rows) == 130 and len({row['name'] for _, row in rows}) == 130
        data = bytearray(16 + len(rows) * 96)
        struct.pack_into('<4I', data, 0, 0x514c4643, 1, len(rows), 96)
        manifest = []
        for index, (folder, row) in enumerate(rows):
            encoded = folder / row['file']
            assert sha(encoded) == row['sha256']
            pcm = self.execute('ffmpeg-' + str(index),
                               [self.args.ffmpeg, '-v', 'error', '-xerror', '-i', encoded,
                                '-f', 's16le', '-acodec', 'pcm_s16le', '-'], binary=True)
            assert len(pcm) == row['pcm_bytes']
            assert hashlib.sha256(pcm).hexdigest() == row['pcm_sha256'], row['name']
            encoded.with_suffix('.pcm').write_bytes(pcm)
            data.extend(bytes((-len(data)) % 4))
            encoded_offset = len(data)
            data.extend(encoded.read_bytes())
            data.extend(bytes((-len(data)) % 4))
            pcm_offset = len(data)
            data.extend(pcm)
            name = row['name'].encode('ascii')
            assert len(name) < 64
            struct.pack_into('<8I64s', data, 16 + index * 96, index, row['bits'], row['channels'],
                             row['rate'], encoded_offset, row['bytes'], pcm_offset, row['pcm_bytes'], name)
            manifest.append({'id': index, **row, 'encoded_offset': encoded_offset,
                             'pcm_offset': pcm_offset, 'ffmpeg_byte_oracle': True})
        assert len(data) <= 0x200000
        (self.out / 'fixtures.bin').write_bytes(data)
        write_json(self.out / 'fixture-manifest.json', manifest)
        self.report['fixture_count'] = len(manifest)
        self.report['fixture_blob_bytes'] = len(data)
        self.report['executed_fixtures'] = ['flac-24bit-mid-verbatim',
                                            'flac-16bit-stereo-verbatim',
                                            'flac-24bit-mid-verbatim-block8192']
        print('Frozen 130 independent PCM oracles; this checkpoint executes three lifecycle cases', flush=True)

    def compiler_closure(self, commands, ninja):
        lookup = {str((self.out / meta['snapshot']).resolve()).casefold(): original
                  for original, meta in self.sources.items()}
        dependencies = {}
        used = []
        for row in commands:
            source = Path(row['file']).resolve()
            if not source.is_relative_to(self.out / 'sources'):
                continue
            row = dict(row)
            used.append(row)
            text = self.execute('compiler-deps-' + str(len(used)),
                                [ninja, '-C', self.out / 'build', '-t', 'deps',
                                 row['output'].replace('\\', '/')])
            assert '(VALID)' in text and '#deps ' in text, row['output']
            actual = []
            for line in text.splitlines():
                if not line.startswith('    '):
                    continue
                path = Path(line.strip())
                path = path.resolve() if path.is_absolute() else (self.out / 'build' / path).resolve()
                assert path.is_file(), str(path)
                actual.append(str(path))
                original = lookup.get(str(path).casefold())
                if original is None:
                    original = str(path)
                    if original not in self.sources:
                        relative = Path('sources/compiler-dependencies') / hashlib.sha256(str(path).encode()).hexdigest()[:16] / path.name
                        self.snapshot(path, relative, 'actual compiler dependency')
                dependencies[str(path)] = {'sha256': sha(path), 'manifest_original': original}
            assert actual
            row['actual_dependency_paths'] = actual
        assert used and any(Path(row['file']).name == 'audio_service.c' for row in used)
        write_json(self.out / 'source-manifest.json', self.sources)
        write_json(self.out / 'actual-compiler-closure.json',
                   {'scope': 'Actual Ninja/GCC dependencies of complete production/codec/harness TUs; additional headers are metadata only',
                    'translation_units': used, 'dependencies': dependencies})
        self.report['actual_translation_units'] = len(used)
        self.report['actual_compiler_dependencies'] = len(dependencies)

    def qualify(self):
        out = self.out
        build = out / 'build'
        desc = json.loads((build / 'project_description.json').read_text())
        assert desc['target'] == 'esp32' and Path(desc['idf_path']).resolve() == self.args.idf
        config = json.loads((build / 'config/sdkconfig.json').read_text())
        for key in ['HEAP_POISONING_LIGHT', 'FREERTOS_CHECK_STACKOVERFLOW_CANARY',
                    'COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE', 'YORADIO_FLAC_DECODER_CUSTOM',
                    'YORADIO_ADAPTIVE_INPUT_BUFFER', 'YORADIO_FRAME_ROUTER',
                    'YORADIO_STREAM_CONFIRM', 'YORADIO_INPUT_TAIL_COALESCE']:
            assert config[key], key
        assert not config['FREERTOS_UNICORE'] and config['FREERTOS_HZ'] == 1000
        assert config.get('YORADIO_INPUT_PREFILL_MS', 0) == 0
        assert not config.get('YORADIO_HTTP_REQUEST_BUFFER_RELEASE', False)
        commands = json.loads((build / 'compile_commands.json').read_text())
        for name in MAIN_TUS:
            source = out / 'sources/repository' / MAIN / name
            selected = [row for row in commands if Path(row['file']).resolve() == source.resolve()]
            assert len(selected) == 1 and '-include' not in selected[0]['command'], name
            if name == 'audio_service.c':
                self.report['whole_audio_service_command'] = selected[0]
        compiler = Path(desc['c_compiler'])
        nm = compiler.with_name('xtensa-esp32-elf-nm.exe')
        self.runtime.update({str(path): sha(path) for path in [compiler, nm]})
        self.execute('compiler-version', [compiler, '--version'])
        cache = (build / 'CMakeCache.txt').read_text()
        installed = {}
        for name, key in [('ninja', 'CMAKE_MAKE_PROGRAM'), ('cmake', 'CMAKE_COMMAND')]:
            path = Path(re.search(r'^' + key + r':[A-Z_]+=(.+)$', cache, re.M).group(1).strip())
            installed[name] = path
            self.runtime[str(path)] = sha(path)
            self.execute(name + '-version', [path, '--version'])
        self.compiler_closure(commands, installed['ninja'])
        elf = build / desc['app_elf']
        app = build / desc['app_bin']
        image = app.read_bytes()
        assert elf.read_bytes()[:4] == b'\x7fELF' and struct.unpack_from('<H', elf.read_bytes(), 18)[0] == 94
        assert image[0] == 0xe9 and struct.unpack_from('<H', image, 12)[0] == 0
        assert app.stat().st_size <= 0x1f0000
        symbols = self.execute('nm-defined', [nm, '--defined-only', elf])
        for symbol in ['decoder_task', 'stream_task', 'output_task', 'audio_service_start',
                       'custom_flac_decoder_feed', '__wrap_custom_flac_decoder_feed',
                       'adaptive_input_receive', 'xRingbufferReceive']:
            assert re.search(r'\b' + re.escape(symbol) + r'$', symbols, re.M), symbol
        parts = (build / 'partition_table/partition-table.bin').read_bytes()
        ranges = []
        for pos in range(0, len(parts), 32):
            magic = struct.unpack_from('<H', parts, pos)[0]
            if magic == 0xffff:
                break
            if magic == 0xebeb:
                assert parts[pos + 16:pos + 32] == hashlib.md5(parts[:pos]).digest()
                break
            assert magic == 0x50aa
            _, kind, subtype, offset, size, label, flags = struct.unpack_from('<HBBII16sI', parts, pos)
            assert size and offset + size <= 0x400000
            ranges.append({'offset': offset, 'size': size, 'type': kind,
                           'label': label.rstrip(b'\0').decode()})
        ranges.sort(key=lambda row: row['offset'])
        assert all(a['offset'] + a['size'] <= b['offset'] for a, b in zip(ranges, ranges[1:]))
        assert any(row['label'] == 'factory' and row['offset'] == 0x10000 and row['size'] == 0x1f0000 for row in ranges)
        assert any(row['label'] == 'fixtures' and row['offset'] == 0x200000 and row['size'] == 0x200000 for row in ranges)
        recipe = json.loads((build / 'flasher_args.json').read_text())
        assert recipe['extra_esptool_args']['chip'] == 'esp32'
        assert recipe['bootloader']['offset'] == '0x1000' and recipe['app']['offset'] == '0x10000'
        flash_files = [(int(offset, 0), build / path) for offset, path in recipe['flash_files'].items()]
        flash_files.append((0x200000, out / 'fixtures.bin'))
        flash = out / 'qemu-flash.bin'
        command = [self.args.idf_python, '-m', 'esptool', '--chip', 'esp32', 'merge-bin',
                   '--output', flash, '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
        for offset, path in sorted(flash_files):
            command += [hex(offset), path]
        self.execute('merge', command + ['--pad-to-size', '4MB'])
        merged = flash.read_bytes()
        assert len(merged) == 0x400000
        assert all(merged[offset:offset + path.stat().st_size] == path.read_bytes() for offset, path in flash_files)
        self.inputs = {str(path.relative_to(out)): sha(path) for folder in ['sources', 'fixtures']
                       for path in (out / folder).rglob('*') if path.is_file()}
        self.inputs.update({name: sha(out / name) for name in ['source-manifest.json',
                            'actual-compiler-closure.json', 'fixtures.bin', 'fixture-manifest.json']})
        artifacts = {elf, app, flash, build / 'project_description.json', build / 'flasher_args.json',
                     build / 'compile_commands.json', build / 'config/sdkconfig.json', out / 'sdkconfig',
                     build / 'partition_table/partition-table.bin', build / 'CMakeCache.txt', build / 'build.ninja'}
        artifacts.update(path for _, path in flash_files)
        artifacts.update(path for path in (build / 'toolchain').rglob('*') if path.is_file())
        self.artifacts = {str(path.relative_to(out)): sha(path) for path in sorted(artifacts)}
        assert self.verify_sources(), 'Inputs changed before QEMU'
        assert all(sha(name) == digest for name, digest in self.runtime.items()), 'A runtime tool changed before QEMU'
        bundle = {'frozen_input_sha256': self.inputs, 'runtime_sha256': self.runtime,
                  'artifact_sha256': self.artifacts, 'sdk_commit': SDK_COMMIT,
                  'whole_audio_service_compile_command': self.report['whole_audio_service_command'],
                  'partitions': ranges, 'expected_cases': EXPECTED_CASES, 'scope': __doc__}
        write_json(out / 'execution-bundle.json', bundle)
        self.report['execution_bundle_sha256'] = sha(out / 'execution-bundle.json')
        self.report['source_manifest_sha256'] = sha(out / 'source-manifest.json')
        self.report['app_bytes'] = app.stat().st_size
        self.report['bound_source_inputs'] = len(self.sources)
        self.save()
        return flash

    def verify_sources(self):
        return all(sha(original) == meta['sha256'] and sha(self.out / meta['snapshot']) == meta['sha256']
                   for original, meta in self.sources.items())

    def verification_after(self):
        def check(path, expected):
            try:
                actual = sha(path)
            except OSError:
                actual = None
            return {'sha256': actual, 'unchanged': actual == expected}
        self.report['post_run_verification'] = {
            'live_sources': {original: check(original, meta['sha256']) for original, meta in self.sources.items()},
            'frozen_sources': {meta['snapshot']: check(self.out / meta['snapshot'], meta['sha256'])
                               for meta in self.sources.values()},
            'runtime': {name: check(name, digest) for name, digest in self.runtime.items()},
            'inputs_and_artifacts': {name: check(self.out / name, digest)
                                     for group in [self.inputs, self.artifacts] for name, digest in group.items()}}
        self.report['all_bound_inputs_current'] = all(row['unchanged'] for group in
                                                     self.report['post_run_verification'].values()
                                                     for row in group.values())
        return self.report['all_bound_inputs_current']

    def run(self):
        self.out.mkdir(parents=True, exist_ok=False)
        try:
            self.freeze_sources()
            self.runtime = {str(path): sha(path) for path in [self.args.idf_python,
                            Path(sys.executable).resolve(), self.args.qemu, self.args.ffmpeg,
                            self.args.powershell, self.args.rom_directory / 'esp32-v3-rom.bin',
                            self.args.rom_directory / 'esp32-v3-rom-app.bin', self.args.idf / 'tools/tools.json']}
            self.report['runtime_sha256'] = self.runtime
            self.verify_sdk()
            self.report['sdk_commit'] = SDK_COMMIT
            self.report['repository_head_at_freeze'] = self.execute('repository-head',
                ['git', '-c', 'core.longpaths=true', '-C', ROOT, 'rev-parse', 'HEAD']).strip()
            self.execute('ffmpeg-version', [self.args.ffmpeg, '-version'])
            powershell_version = self.execute('powershell-version', [self.args.powershell, '-NoLogo', '-NoProfile',
                         '-NonInteractive', '-Command', '$PSVersionTable.PSVersion.ToString()'])
            assert int(powershell_version.strip().split('.')[0]) >= 7, 'PowerShell 7 or newer is required'
            self.execute('qemu-version', [self.args.qemu, '--version'])
            self.fixtures()
            print('Building actual whole production TUs with installed ESP-IDF 6.0.2', flush=True)
            self.execute('build', [self.args.powershell, '-NoLogo', '-NoProfile', '-NonInteractive',
                         '-File', self.out / 'sources/harness/sdk-build.ps1', '-OutputDirectory', self.out,
                         '-IdfDirectory', self.args.idf, '-IdfToolsDirectory', self.args.idf_tools,
                         '-IdfPythonExecutable', self.args.idf_python], timeout=self.args.build_timeout)
            flash = self.qualify()
            print('Frozen sources/compiler closure/tools/images; starting three actual-task QEMU cases', flush=True)
            log = self.execute('qemu', [self.args.qemu, '-M', 'esp32', '-smp', '2', '-L', self.args.rom_directory,
                               '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot',
                               '-snapshot', '-nic', 'none', '-drive',
                               'file=' + str(flash).replace(',', ',,') + ',if=mtd,format=raw'],
                               timeout=self.args.qemu_timeout)
            actual = re.findall(r'^CYD_FLAC_TASK_CASE id=(T\d)\b.*$', log, re.M)
            assert actual == EXPECTED_CASES, actual
            assert len(re.findall(r'^CYD_FLAC_TASK_BOOT actual_audio_service_tu=1 sdk=v6\.0\.2 core0_stream=1 core1_decode_output=1 hardware=0$', log, re.M)) == 1
            assert len(re.findall(r'^CYD_FLAC_TASK_COMPLETE cases=3 actual_audio_service_tu=1 created=5 destroyed=5 real_http_cleanup=5 core_bindings=1 hardware=0 oom_injection=0$', log, re.M)) == 1
            assert not re.search(r'CYD_FLAC_TASK_FAILURE|Guru Meditation|assert failed|panic.ed|watchdog.*triggered|stack smashing|CORRUPT HEAP', log, re.I)
            self.report['cases'] = actual
            self.verify_sdk('-after')
            assert self.verification_after(), 'A bound input changed during execution'
            self.report['passed'] = True
        except BaseException as error:
            self.report['error'] = type(error).__name__ + ': ' + str(error)
            raise
        finally:
            if not self.verification_after():
                self.report['passed'] = False
            self.save()
        if not self.report['passed']:
            raise RuntimeError('A bound input changed during final verification')
        print('PASS three actual CYD task lifecycle cases; no OOM/backpressure/hardware/resource claim', flush=True)


def main():
    args = arguments()
    if args.preflight_only:
        print(json.dumps({'preflight_passed': True, 'build_or_qemu_started': False,
                          'output_created': False,
                          'resolved': {key: str(value) for key, value in vars(args).items()}}, indent=2))
        return
    Campaign(args).run()


if __name__ == '__main__':
    main()
