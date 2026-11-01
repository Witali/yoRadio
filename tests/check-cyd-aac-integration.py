"""Compile the current CYD audio TU with six actual production GCC profiles.

Reuses saved SDK6.0.2 PDM/continuous/legacy commands and generated configuration.
Only AAC-Plus selection and new object/dependency destinations vary. This is
whole-TU compilation, not a linked firmware export or actual pipeline execution.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'idf/esp32-cyd2usb-native/main/audio_service.c'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def windows_argv(command):
    count = ctypes.c_int()
    parse = ctypes.windll.shell32.CommandLineToArgvW
    parse.argtypes = (ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int))
    parse.restype = ctypes.POINTER(ctypes.c_wchar_p)
    pointer = parse(command, ctypes.byref(count))
    assert pointer
    try:
        return [pointer[i] for i in range(count.value)]
    finally:
        ctypes.windll.kernel32.LocalFree.argtypes = (ctypes.c_void_p,)
        ctypes.windll.kernel32.LocalFree(pointer)


def dependencies(path):
    text = path.read_text().replace('\\\n', ' ')
    body = text.split(': ', 1)[1]
    # GCC on Windows emits ordinary backslash path separators, not POSIX
    # shell strings. Only escaped whitespace is special in these make tokens.
    names = re.findall(r'(?:\\\s|[^\s])+', body)
    result = [Path(name.replace('\\ ', ' ').replace('\\\t', '\t')).resolve() for name in names]
    assert result and all(p.is_file() for p in result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    assert sys.platform == 'win32' and out.is_relative_to(ROOT / '.build') and not out.exists()
    out.mkdir(parents=True)
    report = dict(passed=False, commands=[], profiles=[], sources={}, production_image=False,
                  source_sha256=sha(SOURCE), native_pipeline_executed=False)
    report_path = out / 'report.json'

    def save():
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def bind(path):
        path = Path(path).resolve()
        digest = sha(path)
        if str(path) in report['sources']:
            assert digest == report['sources'][str(path)]['sha256']
            return
        relative = Path('sources') / digest[:16] / path.name
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        report['sources'][str(path)] = dict(snapshot=relative.as_posix(), sha256=digest, bytes=path.stat().st_size)

    def command(name, argv, cwd):
        row = dict(name=name, argv=list(map(str, argv)), cwd=str(cwd), state='starting')
        report['commands'].append(row); save()
        start = time.monotonic()
        with (out / (name + '.stdout.log')).open('xb') as stdout, (out / (name + '.stderr.log')).open('xb') as stderr:
            child = subprocess.Popen(argv, cwd=cwd, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            row.update(pid=child.pid, state='running'); save()
            try:
                row['exit_status'] = child.wait(timeout=120)
                row['state'] = 'complete'
            except subprocess.TimeoutExpired:
                child.kill(); child.wait()
                row.update(state='timed-out', exit_status=child.returncode)
            row['elapsed_seconds'] = round(time.monotonic() - start, 3)
        for kind in ('stdout', 'stderr'):
            path = out / (name + '.' + kind + '.log')
            row[kind] = dict(path=path.name, sha256=sha(path), bytes=path.stat().st_size)
        save()
        assert row['state'] == 'complete' and row['exit_status'] == 0, name + ' terminal zero required'

    save()
    try:
        bind(Path(__file__)); bind(SOURCE)
        for backend in ('pdm', 'continuous', 'legacy'):
            manifest_path = ROOT / ('firmware/development/esp32-cyd2usb-native-static-rx-' + backend + '/manifest.json')
            manifest = json.loads(manifest_path.read_bytes())
            build = Path(manifest['build_directory'])
            command_path = build / 'compile_commands.json'
            cfg = build / 'config/sdkconfig.h'
            cfg_json = json.loads((build / 'config/sdkconfig.json').read_bytes())
            assert manifest['backend'] == backend and manifest['target'] == 'esp32'
            assert 'CONFIG_YORADIO_AAC_PLUS' not in cfg.read_text()
            key = {'pdm': 'PDM', 'continuous': 'DAC', 'legacy': 'LEGACY_DAC'}[backend]
            assert cfg_json['YORADIO_NATIVE_AUDIO_OUTPUT_' + key] is True
            rows = [row for row in json.loads(command_path.read_bytes()) if Path(row['file']).name == 'audio_service.c']
            assert len(rows) == 1 and Path(rows[0]['file']).resolve() == SOURCE
            original = windows_argv(rows[0]['command'])
            compiler = Path(original[0])
            assert 'xtensa-esp32-elf-gcc' in compiler.name and sha(compiler) == manifest['compiler_sha256']
            bind(manifest_path); bind(command_path); bind(cfg); bind(build / 'config/sdkconfig.json'); bind(compiler)
            for value in original:
                if value.startswith('@'):
                    response = Path(value[1:]); response = response if response.is_absolute() else build / response
                    bind(response)
            base, skip = [], False
            for value in original:
                if skip:
                    skip = False; continue
                if value in ('-o', '-MF', '-MT'):
                    skip = True; continue
                if value in ('-c', '-MD', '-MMD') or value == rows[0]['file']:
                    continue
                base.append(value)
            for enabled in (False, True):
                name = backend + ('-plus-on' if enabled else '-plus-off')
                obj, deps_before, deps_after = out / (name + '.o'), out / (name + '.pre.d'), out / (name + '.d')
                option = '-DCONFIG_YORADIO_AAC_PLUS=1' if enabled else '-UCONFIG_YORADIO_AAC_PLUS'
                command(name + '-dependencies', base + [option, '-M', '-MF', str(deps_before), '-MT', str(obj), str(SOURCE)], build)
                before = dependencies(deps_before)
                assert SOURCE in before and ROOT / 'idf/esp32-cyd2usb-native/main/aac_public_config.h' in before
                for path in before: bind(path)
                command(name + '-compile', base + [option, '-MD', '-MF', str(deps_after), '-MT', str(obj),
                        '-fstack-usage', '-o', str(obj), '-c', str(SOURCE)], build)
                assert set(dependencies(deps_after)) == set(before) and obj.read_bytes().startswith(b'\x7fELF')
                assert int.from_bytes(obj.read_bytes()[18:20], 'little') == 94
                assert all(sha(path) == report['sources'][str(path)]['sha256'] for path in before)
                report['profiles'].append(dict(backend=backend, aac_plus=enabled, source_sha256=sha(SOURCE),
                    inherited_command_sha256=hashlib.sha256(rows[0]['command'].encode()).hexdigest(),
                    compiler_sha256=sha(compiler), dependencies=[str(path) for path in before],
                    object=dict(path=obj.name, sha256=sha(obj), bytes=obj.stat().st_size, local_only=True),
                    stack_usage=dict(path=obj.with_suffix('.su').name, sha256=sha(obj.with_suffix('.su')))))
                save()
        assert len(report['profiles']) == 6 and sha(SOURCE) == report['source_sha256']
        assert all(sha(original) == pin['sha256'] == sha(out / pin['snapshot']) for original, pin in report['sources'].items())
        report['passed'] = report['all_source_bindings_current'] = True
    except Exception as error:
        report['failure'] = dict(type=type(error).__name__, reason=str(error))
    finally:
        save()
    print(json.dumps(dict(passed=report['passed'], profiles=len(report['profiles']),
                         capture=out.relative_to(ROOT).as_posix(), failure=report.get('failure'))))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
