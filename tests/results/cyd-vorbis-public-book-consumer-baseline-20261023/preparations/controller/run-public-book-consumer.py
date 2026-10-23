"""Run only exact canonical owned publication plus the retained public consumer baseline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
from owned_qmp import capture
from protocol import validate_sdk
from windows_compile_command import macro_command, check_macro_inputs

SDK_HEAD = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
CONTRACT_FILE_SHA = 'a50a9350ac681f58d18774455127714b8d2ce195430b873c746d7b2b79374c48'
MODEL_SHA = '92a9c6ba03892f6e6637b5e6cf5889e5cf0defe92e6d5357e40120acad66d8ff'
RUNTIME_READINESS_SHA = 'c5b554bc0df7c566742c0d9ceeb157fdf81116d93426c22e73adf04af9d8cc77'
SOURCE_READINESS_SHA = '6d009ae122974c4993ab88e8befc350f40077d9095d14e85f784c8a9ef40e6bc'
PINS = {
    "project/main/consumer_unit.c": "728b46c501d26c70ac8de37374e6b1d98a34bd62035c01e8a257030cbad88471",
    "project/main/consumer_data.h": "0e7fe555d413f82419a7688e549cb6d153cf5867fc67a0e2ec5c394a5735ce67",
    "project/main/consumer_port.inc": "2660e256f14857b0aaa0f7104071796bc8095fa01c8eb1f87da82bdd116b696f",
    "project/main/pinned/production/vorbis_repair/setup.c": "6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c",
    "project/main/pinned/production/vorbis_repair_abi.h": "e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60",
    "protocol.py": "a28abe38bf7f8f757073dd9d56d6c1f41679d23dca0125a1f61dc090ac1d9f72",
    "oracle.py": "38ed33532e8cf0e4f7a76aad6650ab144b72e7df4d54168c807e39f2f9ea97d5",
    "contract.json": "a50a9350ac681f58d18774455127714b8d2ce195430b873c746d7b2b79374c48",
    "generated-runtime-readiness.json": "c5b554bc0df7c566742c0d9ceeb157fdf81116d93426c22e73adf04af9d8cc77",
    "unit-source/readiness.json": "6d009ae122974c4993ab88e8befc350f40077d9095d14e85f784c8a9ef40e6bc",
    "windows_compile_command.py": "1c9a8a7349e60481ef71e0a1dc92d600753b4c7cc72d472de83d63b10452121d"
}
TOOL_PINS = {
    'host_python': '4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a',
    'idf_python': '0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14',
    'powershell': '362a356ce7f0940ec74f73a8fc2c990a2cc24a38a11c90bbd8eca947110ad139',
    'qemu': 'f6a5f29315d1bea5c99b74890a99c86c70886fdc0d50f24f62c24cdda43abc35',
    'git': '81ef35ae005ca9318018d18e3327578ce939fb99feaad6b2d7c8ab15f3de8db5',
    'taskkill': '1249717315fc8f4d2df17d5db9da0444795fdb9fb83dfb1f763c3f39282244f7',
    'rom': '9115bbcd03da9f54d3baca5ad94d588a43da54ed332347137ba3dc9010df258b',
    'rom_app': '6d3240e7cdb1ec9c1d683515e0a8578e9fb8ece3e7736cb9a996512c656e8442',
    'compiler': '20e70278d1fa041c1305e0e70e6f35dde01b7eb21f2c7bbc0013456493a011a5',
    'nm': '20e70278d1fa041c1305e0e70e6f35dde01b7eb21f2c7bbc0013456493a011a5',
}
FORBIDDEN_LINK = re.compile(r'libesp_audio_(?:codec|simple_dec)\.a|esp-adf-libs|--wrap[=, ]+esp_vorbis|lib(?:i?vorbis(?:file)?|ogg)\.a', re.I)
FORBIDDEN_SYMBOL = re.compile(r'(?:__wrap_|__real_)?(?:esp_vorbis_dec_\w+|esp_audio_(?:simple_)?dec_\w+)|repair_(?:vorbis_open|vorbis_register)|vorbis_synthesis_\w+|ov_\w+')


def need(value, reason):
    if not value:
        raise RuntimeError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_contract(path):
    need(sha(path) == CONTRACT_FILE_SHA, 'Exact generated contract file bytes')
    value = json.loads(Path(path).read_bytes())
    digest = hashlib.sha256(json.dumps(value['model'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    need(value['contract_sha256'] == digest == MODEL_SHA, 'Exact canonical model digest separate from raw contract file SHA')
    model = value['model']
    need(model['schema'] == 'public-owned-book-consumer-model-v1' and
         (model['case_count'], model['codeword_probes'], model['vector_calls']) == (36, 123, 365) and
         all(model[k] is False for k in ('physical_device', 'vendor_decoder', 'PCM', 'full_G6_qualified')),
         'Exact finite36/123/365 owned public consumer model')
    return value


def dependency_paths(raw, cwd):
    """Read GCC -M output; preserve Windows drive colons and ordinary slashes."""
    raw = raw.replace('\\\r\n', '').replace('\\\n', '')
    need(': ' in raw and '$' not in raw and '\x00' not in raw, 'Review unsupported GCC make dependency syntax')
    body = raw.split(': ', 1)[1]
    parts, token = [], []
    i = 0
    while i < len(body):
        char = body[i]
        if char == '\\' and i + 1 < len(body) and body[i + 1] in ' \t\\#:':
            token.append(body[i + 1]); i += 2
        elif char.isspace():
            if token:
                parts.append(''.join(token)); token = []
            i += 1
        else:
            token.append(char); i += 1
    if token:
        parts.append(''.join(token))
    need(parts, 'Actual dependency list must be nonempty')
    return [(Path(cwd) / p).resolve() for p in parts]


def main():
    here = Path(__file__).resolve().parent
    repo = next(p for p in here.parents if (p / 'idf/esp32-cyd2usb-native/main').is_dir())
    nearest = lambda rel: next((p / rel for p in (repo, *repo.parents) if (p / rel).exists()), None)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--readiness-sha256', required=True)
    parser.add_argument('--idf', type=Path, default=nearest('.idf/v6.0.2'))
    parser.add_argument('--idf-tools', type=Path)
    parser.add_argument('--qemu', type=Path, required=True)
    parser.add_argument('--powershell', type=Path, required=True)
    args = parser.parse_args()
    if sys.platform != 'win32' or not re.fullmatch('[0-9a-f]{64}', args.readiness_sha256):
        parser.error('Require the reviewed Windows runtime and independent readiness SHA256')
    if not args.idf:
        parser.error('Specify the pinned SDK6.0.2 path')
    sdk = args.idf.resolve()
    tools = (args.idf_tools or sdk.parent / 'tools-v6.0.2').resolve()
    out, qemu, ps = args.output.resolve(), args.qemu.resolve(), args.powershell.resolve()
    py = tools / 'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    git = Path(shutil.which('git.exe') or shutil.which('git') or '').resolve()
    taskkill = Path(os.environ['SystemRoot']) / 'System32/taskkill.exe'
    rom = qemu.parent.parent / 'pc-bios'
    protected = (here, sdk, tools, qemu.parent, ps.parent, rom)
    if (not out.is_relative_to(repo / '.build') or out == repo / '.build' or out.exists()
        or any(out == p or out.is_relative_to(p) or p.is_relative_to(out) for p in protected)
        or any((p / 'report.json').exists() for p in out.parents if p != repo)):
        parser.error('Use a fresh, separate campaign directory under this worktree .build')
    readiness = here / 'readiness.json'
    need(sha(readiness) == args.readiness_sha256, 'Independently reviewed source readiness differs')
    manifest = json.loads(readiness.read_bytes())
    need(manifest['schema'] == 'public-book-consumer-runtime-source-only-readiness-v1'
         and manifest['runtime_executed'] is False, 'Require the reviewed source-only readiness')
    actual_files = {p.relative_to(here).as_posix() for p in here.rglob('*') if p.is_file()}
    need(actual_files == set(manifest['files']) | {'readiness.json'}, 'Complete source preparation file set changed')
    for name, item in manifest['files'].items():
        path = (here / name).resolve()
        need(path.is_relative_to(here) and path.is_file() and sha(path) == item['sha256']
             and path.stat().st_size == item['bytes'], 'Reviewed preparation source changed: ' + name)
    for name, expected in PINS.items():
        need(sha(here / name) == expected, 'Unchanged owned parser/unit/helper pin: ' + name)
    need(not any(p.suffix.lower() in ('.a', '.elf', '.bin', '.exe') for p in (here / 'project').rglob('*')),
         'Unit project must contain no binary/archive input')
    runtime_tools = dict(host_python=Path(sys.executable), idf_python=py, powershell=ps, qemu=qemu,
                         git=git, taskkill=taskkill, rom=rom / 'esp32-v3-rom.bin', rom_app=rom / 'esp32-v3-rom-app.bin')
    for name, path in runtime_tools.items():
        need(path.is_file() and sha(path) == TOOL_PINS[name], 'Reviewed public tool identity differs: ' + name)
    out.mkdir(parents=True, exist_ok=False)
    report = dict(schema='public-book-consumer-SDK-runtime-v1', result='INCOMPLETE', completed=False,
        source_compile_link_qualified=False, actual_canonical_SDK_publication_completed=False,
        complete_Fraction_comparison=False, all_Fraction_vectors_equal=False,
        host_sanitizers_qualified=False, host_sanitizer_facts='NOT_EVALUATED_BY_THIS_SDK_CONTROLLER',
        public_arithmetic_portability_qualified=False, full_standard_qualified=False, vendor_cause_diagnosed=False,
        vendor_backend_qualified=False, PCM_qualified=False, full_G6_qualified=False,
        physical_qualified=False, production_radio_integration=False,
        source_readiness_sha256=SOURCE_READINESS_SHA, generated_runtime_readiness_sha256=RUNTIME_READINESS_SHA,
        contract_file_sha256=CONTRACT_FILE_SHA, canonical_model_sha256=MODEL_SHA,
        readiness_sha256=args.readiness_sha256, inputs={}, tools={}, commands=[], build_outputs={})
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1',
               PYTHONNOUSERSITE='1', GIT_OPTIONAL_LOCKS='0')
    for name in ('YORADIO_AUDIO_CODEC_COMPONENT', 'CYD_VORBIS_CANDIDATE', 'EXTRA_COMPONENT_DIRS'):
        env.pop(name, None)

    def save():
        path = out / 'report.json.tmp'
        path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        path.replace(out / 'report.json')

    def freeze(path, relative):
        path = Path(path).resolve()
        target = out / 'sources' / relative
        need(target.resolve().is_relative_to(out / 'sources'), 'Snapshot path escaped sources')
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = path.read_bytes()
        if target.exists():
            need(target.read_bytes() == raw, 'Snapshot collision')
        else:
            target.write_bytes(raw)
        fact = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), snapshot=target.relative_to(out).as_posix())
        if str(path) in report['inputs']:
            need(report['inputs'][str(path)] == fact, 'Changed input or duplicate snapshot binding')
        report['inputs'][str(path)] = fact

    def current():
        for path, item in report['inputs'].items():
            need(sha(path) == item['sha256'] == sha(out / item['snapshot'])
                 and Path(path).stat().st_size == item['bytes'], 'Declared input changed: ' + path)
        for path, expected in report['tools'].items():
            need(sha(path) == expected, 'Declared tool changed: ' + path)
        for name, expected in report['build_outputs'].items():
            need(sha(out / name) == expected, 'Bound build output/config changed: ' + name)

    def execute(name, argv, timeout=60, cwd=None):
        row = dict(name=name, argv=list(map(str, argv)), cwd=str(cwd or out), state='starting',
                   exit_status=None, timed_out=False, interrupted=False, force_stopped=False)
        report['commands'].append(row); save()
        proc = None
        try:
            with (out / (name + '.stdout.log')).open('xb') as stdout, (out / (name + '.stderr.log')).open('xb') as stderr:
                try:
                    proc = subprocess.Popen(row['argv'], cwd=row['cwd'], stdout=stdout, stderr=stderr,
                        stdin=subprocess.DEVNULL, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
                    row.update(pid=proc.pid, state='running'); save()
                    proc.wait(timeout=timeout)
                    row.update(exit_status=proc.returncode, state='complete')
                except BaseException as exc:
                    row.update(state='interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed', error=repr(exc),
                        timed_out=isinstance(exc, subprocess.TimeoutExpired), interrupted=isinstance(exc, KeyboardInterrupt))
                    if proc is not None and proc.poll() is None:
                        row['force_stopped'] = True
                        try:
                            cleanup = subprocess.run([str(taskkill), '/PID', str(proc.pid), '/T', '/F'],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15,
                                creationflags=subprocess.CREATE_NO_WINDOW)
                            (out / (name + '.cleanup.log')).write_bytes(cleanup.stdout)
                            row['tree_cleanup_exit_status'] = cleanup.returncode
                        except BaseException as cleanup_error:
                            row['cleanup_error'] = repr(cleanup_error)
                        if proc.poll() is None:
                            proc.kill()
                        proc.wait(timeout=15)
                    raise
        finally:
            if proc is not None:
                row['exit_status'] = proc.poll()
            for stream in ('stdout', 'stderr'):
                path = out / (name + '.' + stream + '.log')
                if path.is_file():
                    row[stream + '_sha256'] = sha(path)
            save()
        need(row['exit_status'] == 0 and not row['timed_out'] and not row['interrupted']
             and not row['force_stopped'], name + ' requires actual normal terminal0')
        return (out / (name + '.stdout.log')).read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n')

    def bind_output(path):
        path = Path(path).resolve()
        need(path.is_relative_to(out) and path.is_file(), 'Missing/scoped output required')
        report['build_outputs'][path.relative_to(out).as_posix()] = sha(path)

    def sdk_action(action):
        execute('sdk-' + action + '-launcher', [ps, '-NoProfile', '-NonInteractive', '-File', out / 'sources/project/sdk-build.ps1',
            '-Action', action, '-Campaign', out, '-Repository', repo, '-SdkDirectory', sdk, '-ToolsDirectory', tools], 1200)
        receipt = json.loads((out / ('sdk-' + action + '-process.json')).read_text(encoding='utf-8-sig'))
        need(receipt['action'] == action and receipt['terminal'] is True and type(receipt['pid']) is int
             and receipt['pid'] > 0 and receipt['exit_status'] == 0 and Path(receipt['argv'][0]).resolve() == py.resolve()
             and Path(receipt['cwd']).resolve() == out, 'Actual SDK child process terminal0 receipt required')
        for name in ('sdk-' + action + '.stdout.log', 'sdk-' + action + '.stderr.log',
                     'sdk-' + action + '-process.json', action + '-compiler-identity.json', action + '-compiler-environment.json'):
            bind_output(out / name)
        activated = json.loads((out / (action + '-compiler-environment.json')).read_text(encoding='utf-8-sig'))
        need(set(activated) == {'PATH', 'IDF_PATH', 'IDF_TOOLS_PATH', 'IDF_PYTHON_ENV_PATH'}
             and Path(activated['IDF_PATH']).resolve() == sdk and Path(activated['IDF_TOOLS_PATH']).resolve() == tools,
             'Actual isolated SDK compiler environment required')
        env.update(activated)
        return json.loads((out / (action + '-compiler-identity.json')).read_text(encoding='utf-8-sig'))

    save()
    try:
        for path in sorted(here.rglob('*')):
            if path.is_file():
                rel = path.relative_to(here)
                # Runtime project remains at sources/project. Other files are
                # snapshots only, and are never imported from campaign sources.
                freeze(path, rel)
        for path in runtime_tools.values():
            report['tools'][str(path.resolve())] = sha(path)
        contract = load_contract(out / 'sources/contract.json')
        runtime_readiness = json.loads((out / 'sources/generated-runtime-readiness.json').read_bytes())
        need(sha(out / 'sources/generated-runtime-readiness.json') == RUNTIME_READINESS_SHA and
             runtime_readiness['schema'] == 'public-book-consumer-generated-runtime-readiness-v1' and
             runtime_readiness['source_readiness_sha256'] == SOURCE_READINESS_SHA and
             all(runtime_readiness[k] is False for k in ('compiled', 'target_executed', 'host_executed')),
             'Exact source-only generated runtime readiness')
        for item in runtime_readiness['files']:
            path = out / 'sources' / item['path']
            need(path.resolve().is_relative_to(out / 'sources') and sha(path) == item['sha256'] and
                 path.stat().st_size == item['bytes'], 'Every frozen actual generated-runtime member')
        origins = json.loads((out / 'sources/source-origins.json').read_bytes())
        for index, item in enumerate(origins['inputs']):
            path = out / 'sources' / item['snapshot']
            need(path.resolve().is_relative_to(out / 'sources') and sha(path) == item['sha256']
                 and path.stat().st_size == item['bytes'], 'Frozen source origin identity differs')
            original_path = Path(item['source']).resolve()
            need(original_path.is_relative_to(repo) and original_path.is_file() and
                 sha(original_path) == item['sha256'] and original_path.stat().st_size == item['bytes'],
                 'Pinned immutable original source origin differs')
            if str(original_path) not in report['inputs']:
                freeze(original_path, Path('original-origins') / f'{index:04d}' / original_path.name)
        for name in ('export.ps1', 'tools/idf.py', 'tools/cmake/version.cmake', 'tools/cmake/toolchain-esp32.cmake',
                     'tools/cmake/toolchain.cmake', 'components/freertos/Kconfig', 'components/freertos/CMakeLists.txt'):
            freeze(sdk / name, Path('sdk') / name)
        # Freeze the exact local merge implementation before it is invoked.
        esptool = py.parent.parent / 'Lib/site-packages/esptool'
        need(esptool.is_dir(), 'Expected SDK environment esptool source package')
        for path in sorted(esptool.rglob('*.py')):
            freeze(path, Path('esptool') / path.relative_to(esptool))
        need(execute('sdk-head', [git, '-C', sdk, 'rev-parse', 'HEAD']).strip() == SDK_HEAD, 'Wrong SDK revision')
        need(not execute('sdk-clean', [git, '-C', sdk, 'status', '--porcelain', '--untracked-files=no']).strip(), 'Dirty SDK')
        current(); save()
        before = sdk_action('configure')
        current()
        build = out / 'build'
        description = build / 'project_description.json'
        desc = json.loads(description.read_bytes())
        need(desc['project_name'] == 'cyd_vorbis_owned_book_unit'
             and Path(desc['project_path']).resolve() == out / 'sources/project', 'Wrong isolated configured project')
        need(not any('esp_audio' in name for name in desc['build_components'])
             and all(not p or Path(p).resolve().is_relative_to(sdk) or Path(p).resolve().is_relative_to(out / 'sources/project')
                     for p in desc['build_component_paths']), 'Vendor/foreign component entered the isolated project')
        cc = Path(desc['c_compiler']).resolve()
        nm, ninja = Path(before['nm']).resolve(), Path(before['ninja']).resolve()
        need(cc == Path(before['compiler']).resolve(), 'Configured compiler differs from activated compiler')
        for name, path in (('compiler', cc), ('nm', nm), ('ninja', ninja)):
            expected = before[name + '_sha256']
            need(sha(path) == expected and (name == 'ninja' or expected == TOOL_PINS[name]), 'Actual pre-build tool identity')
            report['tools'][str(path)] = expected
        rows = json.loads((build / 'compile_commands.json').read_bytes())
        source = out / 'sources/project/main/consumer_unit.c'
        source_for = lambda row: (Path(row['directory']) / row['file']).resolve()
        own = [row for row in rows if source_for(row).is_relative_to(out / 'sources/project')]
        need(len(own) == 1 and source_for(own[0]) == source, 'Only our frozen unit TU may compile in the project')
        need(not FORBIDDEN_LINK.search(json.dumps(rows)), 'Unexpected vendor archive/decode compile dependency')
        argv, cwd, original, generated = macro_command(own[0], cc, source)
        need('-fno-inline' in original and '-ffunction-sections' in original and '-fdata-sections' in original
             and len(generated) == 2 and sum(p.startswith('@') for p in original) == 1,
             'Actual unit compile flags and reviewed generated cflags/specs required')
        report['compile_context'] = dict(actual_row=own[0], original_argv=original, macro_argv=argv, cwd=str(cwd))
        for path, data in generated.items():
            need(path.is_relative_to(build) and path.read_bytes() == data, 'Generated compiler input identity')
            freeze(path, Path('generated') / path.relative_to(build))
        for name in ('sdkconfig', 'build/config/sdkconfig.h', 'build/compile_commands.json', 'build/project_description.json',
                     'build/CMakeCache.txt', 'build/build.ninja'):
            freeze(out / name, Path('configured') / name)
        macros = execute('unit-macros-before', argv, cwd=cwd)
        macro_values = dict(re.findall(r'^#define ([A-Za-z_0-9]+)(?: (.*))?$', macros, re.M))
        expected_macros = dict(__SIZEOF_INT__='4', __SIZEOF_LONG__='4', __SIZEOF_POINTER__='4', __XTENSA__='1',
            __BYTE_ORDER__='__ORDER_LITTLE_ENDIAN__', CONFIG_IDF_TARGET_ESP32='1', CONFIG_IDF_TARGET_ARCH_XTENSA='1',
            CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ='240', CONFIG_FREERTOS_NUMBER_OF_CORES='2',
            CONFIG_ESP_MAIN_TASK_AFFINITY_CPU0='1', CONFIG_ESP_MAIN_TASK_AFFINITY='0x0', CONFIG_ESP_MAIN_TASK_STACK_SIZE='16384')
        need(all(macro_values.get(k) == v for k, v in expected_macros.items())
             and 'CONFIG_FREERTOS_UNICORE' not in macro_values, 'Actual ILP32/ESP32/240MHz/dual-core/maincore0 macro context')
        dependency_argv = argv[:-2] + ['-M']
        dep_text = execute('unit-dependencies-before', dependency_argv, cwd=cwd)
        dependencies = dependency_paths(dep_text, cwd)
        needed = {source, out / 'sources/project/main/consumer_data.h', out / 'sources/project/main/consumer_port.inc',
            out / 'sources/project/main/pinned/production/vorbis_repair/setup.c',
            out / 'sources/project/main/pinned/production/vorbis_repair_abi.h', build / 'config/sdkconfig.h'}
        needed.update((out / 'sources/project/main/pinned/codec/include' / name).resolve() for name in
            ('esp_audio_types.h', 'decoder/esp_audio_dec.h', 'decoder/esp_audio_dec_reg.h', 'decoder/impl/esp_vorbis_dec.h'))
        need(needed <= set(dependencies), 'Actual GCC include dependency proof must consume parser/ABI/unit/data/all public headers')
        allowed = (sdk, tools, out / 'sources/project', build)
        for index, path in enumerate(dependencies):
            need(path.is_file() and any(path.is_relative_to(base) for base in allowed), 'Unexpected compiler input outside isolated closure')
            if str(path) not in report['inputs']:
                freeze(path, Path('compile-dependencies') / f'{index:04d}' / path.name)
        report['compile_context'].update(dependency_argv=dependency_argv,
            actual_dependencies=[dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p)) for p in dependencies],
            expected_macros=expected_macros, macros_before_sha256=sha(out / 'unit-macros-before.stdout.log'))
        check_macro_inputs(generated); current(); save()
        after = sdk_action('build')
        need(after == before, 'Activated build compiler/nm/ninja changed after configure')
        check_macro_inputs(generated); current()
        need(execute('unit-macros-after', argv, cwd=cwd) == macros, 'Actual unit macros changed during build')
        need(execute('unit-dependencies-after', dependency_argv, cwd=cwd) == dep_text, 'Actual include dependencies changed during build')
        check_macro_inputs(generated); current()
        elf, app = build / desc['app_elf'], build / desc['app_bin']
        raw_elf = elf.read_bytes()
        need(raw_elf[:7] == b'\x7fELF\x01\x01\x01' and struct.unpack_from('<H', raw_elf, 18)[0] == 94,
             'Actual ELF32 little-endian Xtensa machine94 required')
        symbols = execute('symbols', [nm, '-n', '-S', elf])
        for symbol in ('repair_vorbis_book_unpack', 'repair_vorbis_book_clear', 'decode_packed_entry_number', 'public_decode_map', 'app_main'):
            need(re.search(r'^[0-9a-f]+\s+[0-9a-f]+\s+[tT]\s+' + symbol + r'$', symbols, re.M), 'Actual retained unit/parser symbol: ' + symbol)
        actual_names = [line.split()[-1] for line in symbols.splitlines() if line.split()]
        need(not any(FORBIDDEN_SYMBOL.fullmatch(name) for name in actual_names), 'Vendor decoder/register/wrapper symbol entered linked ELF')
        map_path = elf.with_suffix('.map')
        map_text = map_path.read_text(encoding='utf-8', errors='replace')
        need('consumer_unit.c.obj' in map_text and 'public_decode_map' in map_text and
             'repair_vorbis_book_unpack' in map_text and not FORBIDDEN_LINK.search(map_text), 'Actual map must bind our TU without vendor archives/link wraps')
        commands = execute('ninja-commands', [ninja, '-C', build, '-t', 'commands', desc['app_elf']])
        need(not FORBIDDEN_LINK.search(commands) and '--gc-sections' in commands
             and 'consumer_unit.c' in commands and desc['app_elf'] in commands, 'Actual generated compile/link command closure')
        verbose = (out / 'sdk-build.stdout.log').read_text(encoding='utf-8', errors='replace')
        need('consumer_unit.c' in verbose and desc['app_elf'] in verbose and '--gc-sections' in verbose
             and not FORBIDDEN_LINK.search(verbose), 'Verbose actual build must retain unit compile and link execution commands')
        report['compiler_diagnostics'] = {
            stream: re.findall(r'^.*(?:warning:|error:).*$' , (out / ('sdk-build.' + stream + '.log')).read_text(encoding='utf-8', errors='replace'), re.M)
            for stream in ('stdout', 'stderr')}
        for path in (elf, app, map_path, build / 'flasher_args.json'):
            bind_output(path)
        recipe = json.loads((build / 'flasher_args.json').read_bytes())
        need({k:recipe.get('flash_settings', {}).get(k) for k in ('flash_mode', 'flash_size', 'flash_freq')}
             == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m'), 'Actual isolated DIO/40MHz/4MB flash settings')
        expected_flash = {0x1000:build / 'bootloader/bootloader.bin',
                          0x8000:build / 'partition_table/partition-table.bin', 0x10000:app}
        observed_flash = {int(offset, 0):(build / path).resolve() for offset, path in recipe['flash_files'].items()}
        need(len(recipe['flash_files']) == 3 and observed_flash == {o:p.resolve() for o,p in expected_flash.items()},
             'Actual bootloader1000/partition8000/application10000 recipe')
        flash = out / 'qemu-flash.bin'
        merge = [py, '-m', 'esptool', '--chip', 'esp32', 'merge-bin', '--output', flash,
                 '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
        for offset, path in sorted(observed_flash.items()):
            need(path.is_relative_to(build), 'Flash input escaped build')
            bind_output(path)
            merge += [hex(offset), path]
        execute('merge', merge + ['--pad-to-size', '4MB'])
        need(flash.stat().st_size == 4 * 1024 * 1024, 'Actual padded 4MB emulator image')
        bind_output(flash)
        report['source_compile_link_qualified'] = True
        current(); save()
        serial, row = capture(argv=[qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet', '-smp', '2', '-L', rom,
            '-display', 'none', '-monitor', 'none', '-serial', 'file:' + str(out / 'qemu.serial.log'), '-qmp', 'stdio',
            '-no-reboot', '-snapshot', '-nic', 'none', '-drive', 'file=' + str(flash) + ',if=mtd,format=raw'],
            cwd=out, env=env, report=report, save=save, taskkill=taskkill)
        need(row['lifecycle_qualified'] is True and row['exit_status'] == 0 and not row['force_stopped'],
             'Real QMP shutdown/owned terminal closure required before any full unit validation')
        stderr = (out / 'qemu.stderr.log').read_text(encoding='utf-8', errors='replace')
        observed = validate_sdk(serial + '\n' + stderr, contract)
        need(observed['actual_canonical_SDK_publication_completed'] is True and
             observed['complete_Fraction_comparison'] is True and len(observed['fields']) == 36 and
             len(observed['vectors']) == 365 and observed['protocol_events'] == 439 and
             observed['host_sanitizers_qualified'] is False and observed['vendor_cause_diagnosed'] is False,
             'Exact36 publications/123 probes/365 Fraction calls/439records after actual QMP terminal0')
        report['observed'] = observed
        need(execute('sdk-head-after', [git, '-C', sdk, 'rev-parse', 'HEAD']).strip() == SDK_HEAD, 'SDK revision changed')
        need(not execute('sdk-clean-after', [git, '-C', sdk, 'status', '--porcelain', '--untracked-files=no']).strip(), 'SDK changed')
        current()
        need(all(c['exit_status'] == 0 and not c['timed_out'] and not c['interrupted'] and not c['force_stopped']
                 for c in report['commands']), 'Every owned actual command must finish normally')
        equal = observed['all_Fraction_vectors_equal']
        need(type(equal) is bool, 'Actual complete numerical equality classification')
        report.update(result='PUBLIC_BOOK_CONSUMER_SDK_DIAGNOSTICS_RECORDED', completed=True,
            actual_canonical_SDK_publication_completed=True, complete_Fraction_comparison=True,
            all_Fraction_vectors_equal=equal, unequal_calls=observed['unequal_calls'],
            numerical_result='EXACT_FRACTION_EQUAL' if equal else 'EXACT_FRACTION_NONPASS',
            declared_inputs_tools_configs_unchanged=True)
        save()
        print(json.dumps({k:report[k] for k in ('result', 'completed', 'source_compile_link_qualified',
            'actual_canonical_SDK_publication_completed', 'complete_Fraction_comparison', 'all_Fraction_vectors_equal',
            'host_sanitizers_qualified', 'public_arithmetic_portability_qualified', 'vendor_backend_qualified',
            'PCM_qualified', 'full_G6_qualified', 'physical_qualified')}))
        return 0 if equal else 1
    except BaseException as exc:
        report.update(result='INTERRUPTED' if isinstance(exc, KeyboardInterrupt) else 'NONPASS',
            completed=False, actual_canonical_SDK_publication_completed=False, complete_Fraction_comparison=False,
            all_Fraction_vectors_equal=False, error=repr(exc))
        try:
            current()
            report['declared_inputs_tools_configs_unchanged'] = True
        except BaseException as integrity_error:
            report['declared_inputs_tools_configs_unchanged'] = False
            report['integrity_error'] = repr(integrity_error)
        save()
        raise


if __name__ == '__main__':
    sys.exit(main())
