"""Run the actual CYD audio tasks against a measured public-vendor Opus reference.

Transport and output hardware are synthetic. Complete production translation
units, real SDK client allocation, RTOS tasks and queues remain enabled. The
reference is an integration regression, not independent Opus conformance.
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
HARNESS = ROOT / 'tests/target/cyd_espressif_opus_task_qemu'
COMMON = ROOT / 'tests/run-cyd-espressif-vorbis-task-qemu.py'
COMMON_SHA = '633043d1cb61a27009f655c48f42deec198b33c556a8a73712f401aa0490bf6c'
FIXTURE_SHA = '53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11'
FIXTURE_BYTES = 706319


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


need(sha(COMMON) == COMMON_SHA, 'reviewed common native campaign implementation')
common = load_module(COMMON, 'reviewed_cyd_task_campaign')


def validate_reference_witness(report, folder, args):
    """Require actual compiler/image/command witnesses, not vacuous inventories."""
    expected_commands = ('vendor-head', 'vendor-clean', 'sdk-head', 'sdk-clean', 'build', 'symbols', 'merge', 'qemu')
    need([row['name'] for row in report['commands']] == list(expected_commands),
         'unique complete direct native command inventory')
    mandatory = {'build/cyd_espressif_opus_qemu.elf', 'build/cyd_espressif_opus_qemu.bin',
                 'build/cyd_espressif_opus_qemu.map', 'qemu-flash.bin', 'sdkconfig', 'sdk-child.json',
                 'build/bootloader/bootloader.bin', 'build/partition_table/partition-table.bin',
                 'build/compile_commands.json', 'build/project_description.json', 'build/flasher_args.json'}
    need(mandatory <= set(report['build_outputs']), 'complete original direct build artifact inventory')
    child = json.loads((folder / 'sdk-child.json').read_text('utf-8-sig'))
    need(child['pid'] > 0 and child['exit_status'] == 0, 'actual direct SDK child terminal zero')
    description = json.loads((folder / 'build/project_description.json').read_bytes())
    need(description['target'] == 'esp32' and Path(description['idf_path']).resolve() == args.idf,
         'actual direct SDK target and installed SDK identity')
    argv = report['commands'][-1]['argv']
    need(Path(argv[0]).resolve() == args.qemu and report['tools']['qemu']['sha256'] == common.QEMU_SHA and
         sha(args.qemu) == common.QEMU_SHA and '-snapshot' in argv and '-no-reboot' in argv,
         'pinned direct QEMU executable and nonpersistent diagnostic invocation')
    flash = folder / 'qemu-flash.bin'
    need(argv[argv.index('-drive') + 1] == 'file=' + str(flash) + ',if=mtd,format=raw' and
         argv[argv.index('-smp') + 1] == '2' and argv[argv.index('-nic') + 1] == 'none',
         'actual QEMU command uses the exact bound dual-core diagnostic flash')
    required_inputs = [ROOT / 'tests/run-cyd-espressif-opus-qemu.py', args.fixture,
                       ROOT / common.MAIN / 'decoder_registration.c', ROOT / common.MAIN / 'decoder_registration.h',
                       ROOT / 'idf/components/native_stream/include/decoder_pending_input.h',
                       ROOT / 'idf/components/native_stream/include/decoder_eof_input.h']
    required_inputs += [args.vendor / 'lib/esp32' / name for name in common.ARCHIVE_PINS]
    required_inputs += [path for path in (ROOT / 'tests/target/cyd_espressif_opus_qemu').rglob('*') if path.is_file()]
    need(all(str(path.resolve()) in report['inputs'] for path in required_inputs),
         'required unchanged decoder, shared adapters, fixture and archive source bindings')
    for name, digest in common.ARCHIVE_PINS.items():
        need(report['inputs'][str((args.vendor / 'lib/esp32' / name).resolve())]['sha256'] == digest,
             'pinned direct vendor archive bytes')


def validate_log(log, reference):
    """Strictly validate original target records without executing native tools."""
    log = log.replace('\r\n', '\n')
    need(not re.search(r'CYD_OPUS_TASK_FAILURE|Guru Meditation|abort\(\)|Backtrace:|assert failed|'
                       r'CORRUPT HEAP|watchdog.*triggered|stack (?:smashing|overflow)|panic.ed', log, re.I),
         'no target assertion, panic, watchdog, stack or heap failure')
    prefix = 'CYD_OPUS_TASK_'
    need(not any(prefix in line and not line.startswith(prefix) for line in log.splitlines()), 'intact target records')
    lines = [line for line in log.splitlines() if line.startswith(prefix)]
    need(len(lines) == 8 and lines[0] ==
         'CYD_OPUS_TASK_BOOT actual_audio_service_tu=1 sdk=v6.0.2 coordinator=0 fixture=706319 hardware=0',
         'one complete unchanged production task transcript and full fixture')
    profiles = [('stream', 0, 3, 6144), ('decode', 1, 5, 16384), ('output', 1, 6, 4096)]
    for line, (role, core, priority, stack) in zip(lines[1:4], profiles):
        need(line == f'{prefix}PROFILE role={role} core={core} priority={priority} stack={stack}',
             'original task affinity, priority and stack: ' + role)
    positive = r'[1-9][0-9]*'
    identity = f"pcm_bytes={reference['pcm_bytes']} sha256={reference['pcm_sha256']}"

    def record(line, pattern):
        match = re.fullmatch(pattern, line)
        need(match, 'exact target result record')
        return {name: int(value) for name, value in match.groupdict().items()}

    t0 = record(lines[4], prefix + 'CASE id=T0 ordered_eof=1 ' + identity +
                rf' opens=1 closes=1 http_cleanup=1 writes=(?P<writes>{positive}) metadata=1')
    t1 = record(lines[5], prefix + rf'CASE id=T1 stop_reopen=1 partial_pcm=(?P<partial_pcm>{positive}) '
                rf'stop_generation=(?P<stop_generation>{positive}) discard_generation=(?P<discard_generation>{positive}) ' +
                identity + rf' opens=3 closes=3 http_cleanup=3 writes=(?P<writes>{positive}) metadata=1')
    need(t1['partial_pcm'] < reference['pcm_bytes'] and t1['stop_generation'] == t1['discard_generation'],
         'genuine partial Stop and exact output-owner discard barrier')
    t2 = record(lines[6], prefix + rf'CASE id=T2 maintenance_resume=1 partial_pcm=(?P<partial_pcm>{positive}) '
                'held_quiet=1 play_blocked=1 token_consumed=1 stale_rejected=1 ' + identity +
                rf' opens=5 closes=5 http_cleanup=5 writes=(?P<writes>{positive}) metadata=1')
    need(t2['partial_pcm'] < reference['pcm_bytes'], 'maintenance interrupts actual partial audio')
    complete = record(lines[7], prefix + 'COMPLETE cases=3 actual_audio_service_tu=1 opens=5 closes=5 '
                rf'live_decoders=0 real_http_cleanup=5 live_clients=0 process_calls=(?P<process_calls>{positive}) '
                rf'resize_requests=0 core_bindings=1 stream_stack_free=(?P<stream_stack_free>{positive}) '
                rf'decode_stack_free=(?P<decode_stack_free>{positive}) output_stack_free=(?P<output_stack_free>{positive}) '
                rf'heap_free=(?P<heap_free>{positive}) heap_min=(?P<heap_min>{positive}) heap_integrity=1 hardware=0')
    need(complete['heap_min'] <= complete['heap_free'], 'valid observed minimum heap')
    for role, _, _, stack in profiles:
        need(complete[role + '_stack_free'] <= stack, 'valid observed stack watermark: ' + role)
    return dict(cases=dict(T0=t0, T1=t1, T2=t2), complete=complete, full_pcm_bytes=reference['pcm_bytes'],
                full_pcm_sha256=reference['pcm_sha256'], independent_numeric_oracle=False, physical_device=False)


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--build-timeout', type=int, default=1200)
    parser.add_argument('--qemu-timeout', type=int, default=180)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    need(sys.platform == 'win32', 'installed Windows native runtime required')
    need(1 <= args.build_timeout <= 1200 and 1 <= args.qemu_timeout <= 1200, 'bounded native deadlines')
    args.output, args.reference = args.output.resolve(), args.reference.resolve()
    need(args.output.is_relative_to(ROOT / '.build') and args.output != ROOT / '.build' and not args.output.exists(),
         'fresh campaign strictly under current worktree .build')
    need(args.reference.is_relative_to(ROOT / '.build') and args.reference.is_dir() and
         not args.output.is_relative_to(args.reference) and not args.reference.is_relative_to(args.output),
         'separate existing direct-vendor reference campaign')
    need(not any((p / 'report.json').exists() for p in args.output.parents), 'no nested evidence campaign')
    args.idf = REPO / '.idf/v6.0.2'
    args.idf_tools = REPO / '.idf/tools-v6.0.2'
    args.idf_python = args.idf_tools / 'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    args.vendor = REPO / '.idf/esp-adf-libs/esp_audio_codec'
    args.qemu = ROOT / '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
    args.rom = Path('C:/Work/QEMU-ESP32/pc-bios')
    args.powershell = Path(shutil.which('pwsh.exe') or '')
    args.git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    args.fixture = ROOT / 'tests/fixtures/esp32c3_calibration/opus-510.ogg'
    required = [args.idf / 'tools/idf.py', args.idf_python, args.qemu, args.powershell, args.git, args.fixture,
                args.rom / 'esp32-v3-rom.bin', args.rom / 'esp32-v3-rom-app.bin',
                HARNESS / 'sdk-build.ps1', HARNESS / 'project/main/main.cpp',
                args.reference / 'report.json', args.reference / 'baseline.json',
                *[args.vendor / 'lib/esp32' / name for name in common.ARCHIVE_PINS]]
    need(all(path.is_file() for path in required), 'all installed tools, fixture, reference and harness exist')
    need(sha(args.qemu) == common.QEMU_SHA and sha(args.fixture) == FIXTURE_SHA and
         args.fixture.stat().st_size == FIXTURE_BYTES, 'pinned QEMU and complete Opus fixture')
    need(all(sha(args.vendor / 'lib/esp32' / name) == digest for name, digest in common.ARCHIVE_PINS.items()),
         'unchanged LX6 vendor archives')
    for protected in (args.idf, args.idf_tools, args.vendor, args.idf_python.parent, args.qemu.parent,
                      args.rom, args.powershell.parent, Path(sys.executable).resolve().parent):
        need(not (args.output == protected or args.output.is_relative_to(protected) or protected.is_relative_to(args.output)),
             'campaign cannot overlap an installed runtime')
    return args


class Campaign(common.Campaign):
    def __init__(self, args):
        super().__init__(args)
        self.report['codec'] = 'Opus in Ogg'
        self.runtime_paths = {}

    def bind_runtime(self, path):
        key = 'runtime-path-redacted:' + path.name if re.search(r'(?i)[/\\]Users[/\\]', str(path)) else str(path)
        self.runtime[key] = sha(path)
        self.runtime_paths[key] = path

    def verify_inputs(self):
        failures = []
        for original, pin in self.sources.items():
            for path in (Path(original), self.out / pin['snapshot']):
                try:
                    unchanged = sha(path) == pin['sha256']
                except OSError:
                    unchanged = False
                if not unchanged:
                    failures.append('source:' + pin['snapshot'])
        for group, root in ((self.runtime, None), (self.artifacts, self.out)):
            for name, expected in group.items():
                path = self.runtime_paths.get(name, Path(name)) if root is None else root / name
                try:
                    unchanged = sha(path) == expected
                except OSError:
                    unchanged = False
                if not unchanged:
                    failures.append('runtime-or-artifact:' + Path(name).name)
        self.report['bound_input_failures'] = sorted(set(failures))
        self.report['all_bound_inputs_current'] = not failures
        return not failures

    def reference(self):
        # The direct controller is canonical repository code, never code loaded
        # from the reference archive or campaign output.
        reader_path = ROOT / 'tests/run-cyd-espressif-opus-qemu.py'
        need(reader_path.is_file(), 'canonical direct Opus transcript reader')
        reader = load_module(reader_path, 'canonical_direct_opus_reader')
        folder = self.args.reference
        report = json.loads((folder / 'report.json').read_bytes())
        baseline = json.loads((folder / 'baseline.json').read_bytes())
        need(report['passed'] and report['completed'] and report['target_executed'], 'complete direct native reference')
        need(report['target'] == 'esp32' and report['vendor_revision'] == common.VENDOR_COMMIT and
             report['sdk_revision'] == common.SDK_COMMIT and not report['private_abi_used'] and
             not report['custom_decoder'] and not report['production_firmware'],
             'unchanged public LX6 vendor reference scope')
        need(report['fixture_sha256'] == FIXTURE_SHA and report['fixture_bytes'] == FIXTURE_BYTES,
             'same full encoded fixture in direct reference')
        validate_reference_witness(report, folder, self.args)
        need(str(reader_path.resolve()) in report['inputs'] and str(self.args.fixture.resolve()) in report['inputs'],
             'canonical reference controller and exact fixture were frozen by executed direct campaign')
        for command in report['commands']:
            need(command['state'] == 'complete' and command['pid'] > 0 and command['exit_status'] == 0,
                 'every original reference command terminal zero')
            for stream in ('stdout', 'stderr'):
                path = folder / (command['name'] + '.' + stream + '.log')
                need(sha(path) == command[stream + '_sha256'], 'original reference command output identity')
                self.freeze(path, Path('sources/reference') / path.name, 'direct native command output')
        measured = reader.validate_log((folder / 'qemu.stdout.log').read_text('utf-8') + '\n' +
                                       (folder / 'qemu.stderr.log').read_text('utf-8'))
        need(measured == report['measurements'] and measured['reference'] == baseline == report['baseline'],
             'independently re-read original direct transcript and exact generated reference')
        need(baseline['reference_kind'] == 'unchanged_vendor_inline_eos' and
             baseline['input_consumed'] == FIXTURE_BYTES and baseline['sample_rate'] == 48000 and
             baseline['channels'] == 2 and baseline['bits_per_sample'] == 16 and
             baseline['pcm_bytes'] > 0 and baseline['pcm_bytes'] % 4 == 0 and
             re.fullmatch('[a-f0-9]{64}', baseline['pcm_sha256']), 'complete measured Opus PCM geometry')
        native = measured['baseline']
        need(native['pcm'] == baseline['pcm_bytes'] and native['sha256'] == baseline['pcm_sha256'] and
             native['input'] == baseline['input_consumed'], 'inline-data-EOS vendor result binds generated oracle')
        for original, pin in report['inputs'].items():
            path = (folder / pin['snapshot']).resolve()
            need(path.is_relative_to(folder) and sha(path) == pin['sha256'] == sha(original),
                 'original direct reference source is unchanged')
            self.bind_runtime(Path(original))
            self.bind_runtime(path)
        for name, digest in report['build_outputs'].items():
            path = (folder / name).resolve()
            need(path.is_relative_to(folder) and sha(path) == digest, 'original direct build artifact identity')
            self.bind_runtime(path)
        self.freeze(reader_path, Path('sources/reference/direct-controller.py'), 'canonical direct transcript reader')
        for name in ('report.json', 'baseline.json'):
            self.freeze(folder / name, Path('sources/reference') / name, 'direct reference identity and native measurements')
        self.report['pcm_reference'] = baseline
        return baseline

    def freeze_sources(self):
        main = ROOT / common.MAIN
        paths = {main / name for name in common.MAIN_TUS}
        paths.update(main / name for name in ('CMakeLists.txt', 'Kconfig.projbuild', 'network_service.c', 'native_audio_output.c'))
        paths.update(p for p in main.rglob('*.h') if 'vorbis_repair' not in p.parts and not p.name.startswith(('vorbis_repair', 'aac_')))
        for component in ('native_stream', 'native_network_power'):
            paths.update(p for p in (ROOT / 'idf/components' / component).rglob('*') if p.is_file())
        paths.update(p for p in (ROOT / 'idf/components/native_wifi_store/include').rglob('*') if p.is_file())
        paths.add(ROOT / 'idf/components/audio_level_led/audio_level_led.h')
        for path in sorted(paths):
            self.freeze(path, Path('sources/repository') / path.relative_to(ROOT), 'whole production source or helper')
        vendor = self.args.vendor
        vendor_paths = {p for p in vendor.iterdir() if p.is_file()}
        for folder in ('src', 'include'):
            vendor_paths.update(p for p in (vendor / folder).rglob('*') if p.is_file())
        vendor_paths.update(vendor / 'lib/esp32' / name for name in common.ARCHIVE_PINS)
        for path in sorted(vendor_paths):
            self.freeze(path, Path('sources/vendor/esp_audio_codec') / path.relative_to(vendor), 'unchanged public vendor input')
        for path in sorted(HARNESS.rglob('*')):
            if path.is_file():
                self.freeze(path, Path('sources/harness') / path.relative_to(HARNESS), 'actual-task harness')
        self.freeze(self.args.fixture, Path('sources/harness/project/main/fixture.ogg'), 'complete encoded-only Opus fixture')
        self.freeze(Path(__file__), Path('sources/controller.py'), 'Opus campaign controller')
        self.freeze(COMMON, Path('sources/common-task-controller.py'), 'pinned common build and dependency validation')
        reference = self.reference()
        header = self.out / 'sources/harness/project/main/reference.h'
        header.write_text('#pragma once\nstatic constexpr size_t FULL_PCM = ' + str(reference['pcm_bytes']) +
                          ';\nstatic constexpr char FULL_SHA[] = "' + reference['pcm_sha256'] + '";\n', encoding='utf-8')
        self.freeze(header, header.relative_to(self.out), 'derived from bound measured direct-vendor reference')
        common.write_json(self.out / 'source-manifest.json', self.sources)

    def qualify_build(self):
        flash = super().qualify_build()
        config = json.loads((self.out / 'build/config/sdkconfig.json').read_bytes())
        need(config['AUDIO_DECODER_OPUS_SUPPORT'] is True, 'actual native Opus registration enabled')
        bundle = self.out / 'execution-bundle.json'
        evidence = json.loads(bundle.read_bytes())
        evidence.update(scope=__doc__, common_controller_sha256=COMMON_SHA, codec='Opus in Ogg')
        common.write_json(bundle, evidence)
        self.artifacts['execution-bundle.json'] = sha(bundle)
        need(self.verify_inputs(), 'complete Opus binding before execution')
        return flash

    def execute(self):
        self.out.mkdir(parents=True)
        self.save()
        try:
            self.freeze_sources()
            for path in (self.args.idf_python, self.args.qemu, self.args.powershell, self.args.git,
                         Path(sys.executable).resolve(), self.args.rom / 'esp32-v3-rom.bin',
                         self.args.rom / 'esp32-v3-rom-app.bin', self.args.idf / 'tools/tools.json'):
                self.bind_runtime(path)
            self.verify_repositories()
            self.report['repository_head_at_freeze'] = self.run_command('repository-head',
                [self.args.git, '-c', 'core.longpaths=true', '-C', ROOT, 'rev-parse', 'HEAD']).strip()
            print('Building complete CYD tasks with public Espressif Opus', flush=True)
            self.run_command('build', [self.args.powershell, '-NoProfile', '-NonInteractive', '-File',
                self.out / 'sources/harness/sdk-build.ps1', '-OutputDirectory', self.out, '-IdfDirectory', self.args.idf,
                '-IdfToolsDirectory', self.args.idf_tools, '-IdfPythonExecutable', self.args.idf_python], self.args.build_timeout)
            flash = self.qualify_build()
            print('Starting actual Opus task EOF, Stop/reopen and maintenance cases', flush=True)
            log = self.run_command('qemu', [self.args.qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet',
                '-smp', '2', '-L', self.args.rom, '-display', 'none', '-monitor', 'none', '-serial', 'stdio',
                '-no-reboot', '-snapshot', '-nic', 'none', '-drive',
                'file=' + str(flash).replace(',', ',,') + ',if=mtd,format=raw'], self.args.qemu_timeout)
            self.report['measurements'] = validate_log(log + '\n' +
                (self.out / 'qemu.stderr.log').read_text(errors='replace'), self.report['pcm_reference'])
            self.verify_repositories('-after')
            need(self.verify_inputs(), 'every source, tool and image unchanged after actual task run')
            self.report.update(passed=True, completed=True)
            print('PASS actual CYD Opus lifecycle; independent conformance and radio/hardware remain separate', flush=True)
        except BaseException as error:
            self.report.update(passed=False, completed=False, failure_type=type(error).__name__, failure=str(error))
            print(json.dumps(dict(passed=False, failure_type=type(error).__name__, failure=str(error))), file=sys.stderr)
        finally:
            if not self.verify_inputs():
                self.report['passed'] = False
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
