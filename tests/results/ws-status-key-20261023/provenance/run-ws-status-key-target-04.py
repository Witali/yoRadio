"""Compile/lint only the two changed WebSocket units using existing SDK databases."""
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from windows_compile_command import windows_argv


def fact(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def run(argv, cwd, stem):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=180)
    for stream in ('stdout', 'stderr'):
        (out / (stem + '.' + stream + '.log')).write_bytes(getattr(result, stream))
    row = {'argv': argv, 'cwd': str(cwd), 'returncode': result.returncode,
           'executable': fact(Path(argv[0])),
           'logs': {s: fact(out / (stem + '.' + s + '.log')) for s in ('stdout', 'stderr')}}
    commands[stem] = row
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n', encoding='utf-8')
    assert result.returncode == 0, (stem, result.stderr.decode(errors='replace'))
    return result


out = ROOT / '.build/ws-status-key-target-04'
out.mkdir(exist_ok=False)
commands = {}
report = {'scope': __doc__, 'passed': False, 'full_app_configured_or_built': False,
          'physical_device': False, 'firmware_exported': False,
          'script': fact(Path(__file__)), 'profiles': {}}
profiles = {
    'cyd': ('idf/esp32-cyd2usb-native/main/websocket_service.c', '.build/srx01/gvp', '.build/srx01/cvp', 'esp32'),
    'c3': ('idf/esp32c3-oled-native/main/websocket_service.c', 'idf/esp32c3-oled-native/build-c3-transfer',
           'idf/esp32c3-oled-native/build-lint-c3-ap-timeout-01', 'esp32c3'),
}
diagnostic = re.compile(r'^(.*?):(\d+):(\d+): (warning|error): (.*?)(?: \[([^\]]+)\])?$', re.M)
for board, (source_name, gcc_dir, clang_dir, target) in profiles.items():
    source = ROOT / source_name
    snapshot = out / (board + '-websocket_service.c')
    snapshot.write_bytes(source.read_bytes())
    data = {'source': source_name, 'source_fact': fact(source), 'databases': {}, 'analyses': {}}
    for kind, directory in [('gcc', gcc_dir), ('clang', clang_dir)]:
        build = (ROOT / directory).resolve()
        database = build / 'compile_commands.json'
        rows = [r for r in json.loads(database.read_bytes())
                if (Path(r['directory']) / r['file']).resolve() == source.resolve()]
        assert len(rows) == 1, (board, kind, len(rows))
        row = rows[0]
        cwd = Path(row['directory']).resolve()
        assert cwd == build
        argv = row.get('arguments') or windows_argv(row['command'])
        assert argv.count('-c') == 1 and argv.count('-o') == 1
        compiler = Path(argv[0])
        assert compiler.name == ('clang.exe' if kind == 'clang' else
                                 'xtensa-esp32-elf-gcc.exe' if board == 'cyd' else 'riscv32-esp-elf-gcc.exe')
        config = build / 'config/sdkconfig.json'
        configuration = json.loads(config.read_bytes())
        assert configuration['IDF_TARGET'] == target
        data['databases'][kind] = {'path': directory, 'database': fact(database), 'compile_row': row,
                                   'compiler': fact(compiler), 'config': fact(config),
                                   'IDF_TARGET': configuration['IDF_TARGET'],
                                   'CPU_MHz': configuration['ESP_DEFAULT_CPU_FREQ_MHZ'],
                                   'unicore': configuration.get('FREERTOS_UNICORE', False)}
        without_output = argv.copy()
        output_at = without_output.index('-o')
        del without_output[output_at:output_at + 2]
        deps = without_output.copy()
        deps.remove('-c')
        dependency_file = out / (board + '-' + kind + '.d')
        deps += ['-M', '-MT', 'dependency', '-MF', str(dependency_file)]
        # Freeze response/specs and the actual analyzer before the dependency walk.
        context = {database, config, ROOT / '.clang-tidy', compiler}
        if kind == 'clang':
            context.add(compiler.with_name('clang-tidy.exe'))
        responses = [arg for arg in argv if arg.startswith('@')]
        expected_count = 0 if board == 'cyd' and kind == 'clang' else 1
        assert len(responses) == expected_count
        if responses:
            response = (cwd / responses[0][1:]).resolve()
            assert response == build / 'toolchain/cflags'
            specs = build / 'specs/picolibc.specs'
            if kind == 'clang':
                expected = ['--target=riscv32-esp-elf', '-mcpu=esp32c3']
            elif board == 'cyd':
                expected = ['-Wno-frame-address', '-mlongcalls', '-fno-builtin-memcpy',
                            '-fno-builtin-memset', '-fno-builtin-bzero',
                            '"-specs=' + specs.as_posix() + '"']
            else:
                expected = ['-march=rv32imc_zicsr_zifencei', '-mtune=esp-base',
                            '"-specs=' + specs.as_posix() + '"', '-D__PICOLIBC_ERRNO_FUNCTION=__errno']
            assert response.read_text(encoding='utf-8').splitlines() == expected
            context.add(response)
            if kind == 'gcc':
                assert not any(line.startswith('%include') for line in specs.read_text(encoding='utf-8').splitlines())
                context.add(specs)
            for path in (response, *([specs] if kind == 'gcc' else [])):
                saved = out / ('context-' + board + '-' + kind) / path.name
                saved.parent.mkdir(exist_ok=True)
                saved.write_bytes(path.read_bytes())
        context_before = {str(path): fact(path) for path in sorted(context)}
        run(deps, cwd, board + '-' + kind + '-dependencies')
        assert context_before == {name: fact(Path(name)) for name in context_before}

        body = dependency_file.read_text(encoding='utf-8').split(':', 1)[1].replace('\\\n', ' ')
        # Observed Make rows use literal Windows backslashes and no escaped spaces.
        assert "\\ " not in body and "\\#" not in body and "$" not in body
        paths = {(cwd / name).resolve() for name in body.split()}
        assert source.resolve() in paths
        paths.update(context)
        before = {str(path): fact(path) for path in sorted(paths)}
        if kind == 'gcc':
            object_path = out / (board + '-websocket_service.o')
            result = run(without_output + ['-o', str(object_path)], cwd, board + '-gcc-compile')
            assert not result.stderr and not result.stdout, 'Unexpected GCC diagnostics'
            data['analyses'][kind] = {'object': fact(object_path), 'diagnostics': 0}
        else:
            tidy = compiler.with_name('clang-tidy.exe')
            header_filter = re.escape(ROOT.as_posix()).replace('/', r'[/\\]') + r'[/\\]'
            command = [str(tidy), str(source), '-p', str(build), '--config-file=' + str(ROOT / '.clang-tidy'),
                       '--header-filter=' + header_filter, '--export-fixes=' + str(out / (board + '-fixes.yaml'))]
            result = run(command, ROOT, board + '-clang-tidy')
            log = (result.stdout + result.stderr).decode('utf-8', errors='replace')
            diagnostics = [dict(file=m[0], line=int(m[1]), column=int(m[2]), severity=m[3],
                                message=m[4], check=m[5]) for m in diagnostic.findall(log)]
            assert not any(d['severity'] == 'error' for d in diagnostics)
            assert not any('suspicious-memory-comparison' in d['check'] for d in diagnostics)
            data['analyses'][kind] = {'diagnostics': diagnostics, 'warnings': len(diagnostics), 'errors': 0}
        after = {name: fact(Path(name)) for name in before}
        assert before == after, 'An actual source/header/tool/config/database changed during analysis'
        data['analyses'][kind]['inputs'] = before
        data['analyses'][kind]['all_inputs_unchanged'] = True
        data['analyses'][kind]['compiler_context_frozen_before_dependency_walk'] = context_before
    assert source.read_bytes() == snapshot.read_bytes()
    report['profiles'][board] = data
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
report['passed'] = True
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'passed': True, 'GCC_objects': 2, 'focused_clang_units': 2,
                  'warnings': {b: r['analyses']['clang']['warnings'] for b, r in report['profiles'].items()},
                  'full_app_configured_or_built': False}))
