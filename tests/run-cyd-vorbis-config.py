#!/usr/bin/env python3
"""Configure-only tests of the canonical CYD Vorbis repair CMake helper.

Run real CMake project(NONE) configuration, never a compiler, SDK export or
decoder. Verify exact source/link properties and 19 named guard rejections.
This gate does not qualify private ABI, playback, OOM or format conformance.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('idf/esp32-cyd2usb-native/main')
SOURCES = ('setup.c', 'simple.c', 'output.c')
REPAIR_FILES = (*SOURCES, 'floor1_render.h')
WRAPS = ('esp_vorbis_dec_open', 'esp_vorbis_dec_register', 'esp_vorbis_dec_decode',
         'floor1_inverse2',
         'esp_audio_simple_dec_open', 'esp_audio_simple_dec_process', 'esp_audio_simple_dec_reset',
         'esp_es_parse_frame', 'esp_ogg_parse_frame', 'media_lib_module_realloc')
ARCHIVES = {
    'codec': '92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58',
    'simple_dec': 'ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6',
}
HEADERS = ('include/decoder/impl/esp_vorbis_dec.h', 'include/decoder/esp_audio_dec.h',
           'include/simple_dec/esp_audio_simple_dec.h', 'include/simple_dec/esp_audio_simple_dec_reg.h')
CASES = {
    'enabled': {}, 'disabled': {'enabled': False}, 'early': {'early': True},
    'wrong-target': {'target': 'esp32c3', 'error': 'requires classic ESP32 Xtensa'},
    'missing-target-bool': {'target_bool': False, 'error': 'requires classic ESP32 Xtensa'},
    'wrong-major': {'major': '5', 'error': 'requires pinned ESP-IDF 6.0.2'},
    'wrong-minor': {'minor': '1', 'error': 'requires pinned ESP-IDF 6.0.2'},
    'wrong-patch': {'patch': '1', 'error': 'requires pinned ESP-IDF 6.0.2'},
    'missing-version': {'major': None, 'error': 'requires pinned ESP-IDF 6.0.2'},
    'malformed-minor': {'minor': 'unknown', 'error': 'requires pinned ESP-IDF 6.0.2'},
    'malformed-patch': {'patch': '2suffix', 'error': 'requires pinned ESP-IDF 6.0.2'},
    'absent-component': {'target_name': 'absent', 'error': 'requires registered component target'},
    'missing-component-env': {'component': '', 'error': 'requires pinned codec component directory'},
    'bad-codec': {'component': 'bad-codec', 'error': 'requires audited ESP32 codec archive'},
    'bad-simple': {'component': 'bad-simple', 'error': 'requires audited ESP32 simple_dec archive'},
    'missing-codec': {'component': 'missing-codec', 'error': 'missing codec archive'},
    'missing-simple': {'component': 'missing-simple', 'error': 'missing simple_dec archive'},
    **{'missing-' + name: {'missing': name, 'error': 'missing canonical ' + name} for name in REPAIR_FILES},
    'missing-abi': {'missing': 'vorbis_repair_abi.h', 'error': 'missing canonical ABI header'},
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def installed(relative, directory=False):
    return next((parent / relative for parent in (ROOT, *ROOT.parents)
                 if ((parent / relative).is_dir() if directory else (parent / relative).is_file())), None)


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.build/cyd-vorbis-config-01')
    parser.add_argument('--codec-component', type=Path,
                        default=installed('.idf/esp-adf-libs/esp_audio_codec', directory=True))
    parser.add_argument('--cmake', type=Path,
                        default=installed('.idf/tools-v6.0.2/tools/cmake/4.0.3/bin/cmake.exe') or shutil.which('cmake'))
    parser.add_argument('--ninja', type=Path,
                        default=installed('.idf/tools-v6.0.2/tools/ninja/1.12.1/ninja.exe') or shutil.which('ninja'))
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    for key in ('cmake', 'ninja', 'codec_component'):
        path = getattr(args, key)
        if not path:
            parser.error('--' + key.replace('_', '-') + ' is required when not discoverable')
        setattr(args, key, Path(path).resolve())
    out = args.output.resolve()
    args.output = out
    if not out.is_relative_to((ROOT / '.build').resolve()):
        parser.error('Output must be inside repository .build')
    if out.exists():
        parser.error('Output already exists; choose a fresh directory')
    if any((parent / 'report.json').exists() for parent in out.parents):
        parser.error('Output must not be nested in an evidence campaign')
    protected = [args.codec_component, args.cmake.parent, args.ninja.parent, Path(sys.executable).resolve().parent]
    if any(out == path or out.is_relative_to(path) or path.is_relative_to(out) for path in protected):
        parser.error('Output must not overlap codec component or installed tool directories')
    required = [args.cmake, args.ninja, ROOT / MAIN / 'compat/vorbis_repair/enable.cmake',
                ROOT / MAIN / 'vorbis_repair_abi.h', *[ROOT / MAIN / 'vorbis_repair' / name for name in REPAIR_FILES],
                *[args.codec_component / name for name in HEADERS],
                *[args.codec_component / ('lib/esp32/libesp_audio_' + name + '.a') for name in ARCHIVES]]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        parser.error('Missing inputs: ' + ', '.join(missing))
    return args


def run(args):
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    report = {'passed': False, 'scope': __doc__, 'configure_only': True,
              'compiler_invoked': False, 'sdk_export_invoked': False, 'runtime_invoked': False,
              'inputs': {}, 'tools': {}, 'cases': {}, 'commands': []}

    def save():
        (out / 'report.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())

    def freeze(source, relative):
        data = source.read_bytes()
        target = out / 'inputs' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        report['inputs'][str(source.resolve())] = {
            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'snapshot': target.relative_to(out).as_posix(),
        }
        return target

    def current():
        return (all(sha(path) == record['sha256'] and sha(out / record['snapshot']) == record['sha256']
                    for path, record in report['inputs'].items())
                and all(sha(path) == digest for path, digest in report['tools'].items()))

    try:
        files = [Path(__file__).resolve(), ROOT / MAIN / 'compat/vorbis_repair/enable.cmake',
                 ROOT / MAIN / 'vorbis_repair_abi.h', *[ROOT / MAIN / 'vorbis_repair' / name for name in REPAIR_FILES]]
        for source in files:
            freeze(source, Path('repo') / source.relative_to(ROOT))
        for header in HEADERS:
            freeze(args.codec_component / header, Path('codec_component') / header)
        good = out / 'components/good'
        for name, expected in ARCHIVES.items():
            relative = Path('lib/esp32/libesp_audio_' + name + '.a')
            source = args.codec_component / relative
            snapshot = freeze(source, Path('codec_component') / relative)
            assert sha(snapshot) == expected, 'Installed archive is outside the audited ESP32 identity: ' + name
            destination = good / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(snapshot, destination)
        for tool in (args.cmake, args.ninja, Path(sys.executable).resolve()):
            report['tools'][str(tool)] = sha(tool)
        for kind in ('bad-codec', 'bad-simple', 'missing-codec', 'missing-simple'):
            component = out / 'components' / kind
            shutil.copytree(good, component)
            archive = 'codec' if kind.endswith('codec') else 'simple_dec'
            path = component / ('lib/esp32/libesp_audio_' + archive + '.a')
            if kind.startswith('missing'):
                path.unlink()
            else:
                path.write_bytes(path.read_bytes() + b'guard-mutation')

        frozen_main = out / 'inputs/repo' / MAIN
        helper = frozen_main / 'compat/vorbis_repair/enable.cmake'
        planned = {}
        for name, overrides in CASES.items():
            values = {'enabled': True, 'early': False, 'target': 'esp32', 'target_bool': True,
                      'major': '6', 'minor': '0', 'patch': '2', 'target_name': 'vorbis_target', 'component': 'good'}
            values.update(overrides)
            if name in ('disabled', 'early'):
                values.update(target='invalid', major=None, target_name='absent', component='')
            directory = out / name
            project = directory / 'project'
            main = project / 'main'
            (main / 'compat/vorbis_repair').mkdir(parents=True)
            shutil.copyfile(helper, main / 'compat/vorbis_repair/enable.cmake')
            for source in [*[Path('vorbis_repair') / entry for entry in REPAIR_FILES], Path('vorbis_repair_abi.h')]:
                if source.name != values.get('missing'):
                    destination = main / source
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(frozen_main / source, destination)
            settings = {'CONFIG_YORADIO_VORBIS_REPAIR': 'ON' if values['enabled'] else 'OFF',
                        'CMAKE_BUILD_EARLY_EXPANSION': 'ON' if values['early'] else 'OFF',
                        'IDF_TARGET': values['target'], 'CONFIG_IDF_TARGET_ESP32': 'ON' if values['target_bool'] else 'OFF',
                        'IDF_VERSION_MAJOR': values['major'], 'IDF_VERSION_MINOR': values['minor'],
                        'IDF_VERSION_PATCH': values['patch'], 'COMPONENT_LIB': values['target_name']}
            lines = ['cmake_minimum_required(VERSION 3.20)', 'project(VorbisGuard NONE)',
                     'add_library(vorbis_target INTERFACE)',
                     'target_link_options(vorbis_target INTERFACE "-Wl,--undefined=preserve_existing")']
            lines += ['set(' + key + ' "' + value + '")' for key, value in settings.items() if value is not None]
            lines += ['include("' + (main / 'compat/vorbis_repair/enable.cmake').as_posix() + '")',
                      'native_enable_vorbis_repair()', 'get_target_property(sources vorbis_target SOURCES)',
                      'get_target_property(options vorbis_target INTERFACE_LINK_OPTIONS)',
                      'file(WRITE "${CMAKE_BINARY_DIR}/captured.txt" "${sources}\\n${options}\\n")',
                      'file(WRITE "${CMAKE_BINARY_DIR}/compilers.txt" "${CMAKE_C_COMPILER}|${CMAKE_CXX_COMPILER}\\n")']
            (project / 'CMakeLists.txt').write_bytes(('\n'.join(lines) + '\n').encode())
            command = [str(args.cmake), '-G', 'Ninja', '-DCMAKE_MAKE_PROGRAM=' + args.ninja.as_posix(),
                       '-DCMAKE_TOOLCHAIN_FILE=', '-S', project.as_posix(), '-B', (directory / 'build').as_posix()]
            (directory / 'command.json').write_bytes((json.dumps(command, indent=2) + '\n').encode())
            planned[name] = {'project': project, 'command': command, 'values': values}
        generated = {path.relative_to(out).as_posix(): sha(path) for base in ('components', *CASES)
                     for path in (out / base).rglob('*') if path.is_file()}
        report['generated_inputs_before_cmake'] = generated
        save()
        assert current()
        temporary = out / 'tool-temp'
        temporary.mkdir()
        for name, plan in planned.items():
            env = os.environ.copy()
            env.pop('CMAKE_TOOLCHAIN_FILE', None)
            env.update(GIT_OPTIONAL_LOCKS='0', TEMP=str(temporary), TMP=str(temporary),
                       YORADIO_AUDIO_CODEC_COMPONENT=str(out / 'components' / plan['values']['component'])
                       if plan['values']['component'] else '')
            directory = out / name
            try:
                result = subprocess.run(plan['command'], env=env, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, timeout=30)
            except subprocess.TimeoutExpired as error:
                data = error.output or b''
                (directory / 'configure.log').write_bytes(data)
                report['commands'].append({'case': name, 'argv': plan['command'], 'exit_status': 'timeout',
                                           'log_sha256': hashlib.sha256(data).hexdigest()})
                save()
                raise RuntimeError(name + ' timed out; timeout is never a successful guard') from error
            (directory / 'configure.log').write_bytes(result.stdout)
            expected = CASES[name].get('error')
            report['commands'].append({'case': name, 'argv': plan['command'], 'exit_status': result.returncode,
                                       'log_sha256': hashlib.sha256(result.stdout).hexdigest()})
            report['cases'][name] = {'passed': False, 'expected_rejection': bool(expected),
                                     'predicate': expected, 'exit_status': result.returncode,
                                     'log_sha256': hashlib.sha256(result.stdout).hexdigest()}
            save()
            if expected:
                assert result.returncode == 1 and ('Vorbis repair ' + expected).encode() in result.stdout, (name, result.stdout)
                assert not (directory / 'build/captured.txt').exists(), name
            else:
                assert result.returncode == 0, (name, result.stdout)
                sources, options = (directory / 'build/captured.txt').read_text().splitlines()
                expected_options = ['-Wl,--undefined=preserve_existing']
                expected_sources = []
                if name == 'enabled':
                    expected_sources = [(plan['project'] / 'main/vorbis_repair' / entry).as_posix() for entry in SOURCES]
                    expected_options += ['-Wl,--wrap=' + symbol for symbol in WRAPS]
                    assert sources.split(';') == expected_sources, (name, sources)
                else:
                    assert sources == 'sources-NOTFOUND', (name, sources)
                assert options.split(';') == expected_options, (name, options)
                assert (directory / 'build/compilers.txt').read_text().strip() == '|', name
                report['cases'][name].update(actual_sources=expected_sources, actual_link_options=options.split(';'))
            assert current() and all(sha(out / relative) == expected_hash for relative, expected_hash in generated.items())
            report['cases'][name]['passed'] = True
            save()
            print('PASS ' + name, flush=True)
        report['all_inputs_unchanged_after'] = current()
        report['all_generated_inputs_unchanged_after'] = all(sha(out / relative) == digest for relative, digest in generated.items())
        assert report['all_inputs_unchanged_after'] and report['all_generated_inputs_unchanged_after']
        report['passed'] = True
        save()
        print(json.dumps({'passed': True, 'cases': len(CASES), 'report': str(out / 'report.json'),
                          'report_sha256': sha(out / 'report.json')}, indent=2))
    except BaseException as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
        save()
        raise


if __name__ == '__main__':
    arguments_ = arguments()
    if arguments_.preflight_only:
        print(json.dumps({'preflight_passed': True, 'output_created': False,
                          'output': str(arguments_.output)}, indent=2))
    else:
        run(arguments_)
