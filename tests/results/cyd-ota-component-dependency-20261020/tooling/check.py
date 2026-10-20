"""One fresh installed-SDK component check; no project configuration edits."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PW = Path('C:/Users/rudol/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe')
DEPS = Path('C:/Work/yoRadio/.idf')
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def identity(p):
    p = Path(p).resolve()
    raw = p.read_bytes()
    return {'path': str(p), 'bytes': len(raw), 'sha256': sha(raw)}

def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', '-c', 'core.longpaths=true', '-C', str(cwd), *args])

def require(value, message):
    if not value:
        raise AssertionError(message)

def snapshot(project):
    roots = [ROOT / 'idf/components/native_ota', ROOT / 'idf/components/native_stream']
    paths = [p for d in roots for p in d.rglob('*') if p.is_file()]
    paths += [p for p in project.rglob('*') if p.is_file() and
              ('CMakeLists.txt' == p.name or p.name.startswith('Kconfig') or
               p.name.startswith('idf-')) and not any(x.startswith('build') for x in p.relative_to(project).parts)]
    paths += [HERE / 'sdk.ps1', HERE / 'check.py', HERE / 'probe.cmake']
    return [identity(p) for p in sorted(set(paths))]

def main():
    a = argparse.ArgumentParser()
    a.add_argument('--target', choices=['esp32', 'esp32c3'], required=True)
    a.add_argument('--stream', choices=['present', 'absent'], required=True)
    a.add_argument('--expected-head', required=True)
    a.add_argument('--attempt', required=True)
    args = a.parse_args()
    run = HERE / args.attempt
    require(not run.exists(), 'Fresh attempt directory required')
    run.mkdir()
    report = {'schema': 'ota-component-check-v1', 'status': 'RUNNING', 'target': args.target, 'stream': args.stream,
              'scope': 'actual SDK configure and native_ota static component compilation only',
              'full_application': False, 'hardware_tested': False, 'started_unix': time.time()}
    def save():
        (run / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    save()
    try:
        cyd = args.target == 'esp32'
        source_project = ROOT / 'idf' / ('esp32-cyd2usb-native' if cyd else 'esp32c3-oled-native')
        project = source_project
        sdk = DEPS / ('v6.0.2' if cyd else 'v6.1-9a97f6c54ec6')
        expected_sdk = '7101770dc6db2667b3c477cc31365dd1acd6db4e' if cyd else '9a97f6c54ec638111ce55cd36581b3c192f15207'
        baseline = ROOT / 'firmware/development' / ('esp32-cyd2usb-native-early-mpi-pdm' if cyd else 'esp32c3-oled-native-ap-timeout')
        require(git('rev-parse', 'HEAD').decode().strip() == args.expected_head, 'Unexpected repository HEAD')
        report['source_commit'] = args.expected_head
        report['source_status_before'] = git('status', '--porcelain', '-uno').decode()
        report['sdk_before'] = {'path': str(sdk), 'commit': git('rev-parse', 'HEAD', cwd=sdk).decode().strip(),
                                'status': git('status', '--porcelain', '-uno', cwd=sdk).decode()}
        require(report['sdk_before']['commit'] == expected_sdk and not report['sdk_before']['status'], 'SDK pin/clean')
        report['sources_before'] = snapshot(source_project)
        report['sdk_cmake'] = [identity(sdk / p) for p in ['tools/cmake/component.cmake', 'tools/cmake/component_validation.cmake', 'tools/cmake/scripts/component_get_requirements.cmake']]
        report['baseline'] = [identity(baseline / x) for x in ['sdkconfig', 'sdkconfig.json', 'manifest.json', 'project_description.json']]
        build = run / 'b'
        build.mkdir()
        full_cyd = cyd and args.stream == 'present'
        if not full_cyd:
            project = run / 'project'
            (project / 'main').mkdir(parents=True)
            component_names = ['native_ota', 'native_storage', 'native_web_transport']
            if args.stream == 'present': component_names.append('native_stream')
            component_dirs = [ROOT / 'idf/components' / name for name in component_names]
            (project / 'CMakeLists.txt').write_text('cmake_minimum_required(VERSION 3.16)\nset(EXTRA_COMPONENT_DIRS\n' +
                ''.join('  "' + p.as_posix() + '"\n' for p in component_dirs) +
                ')\ninclude($ENV{IDF_PATH}/tools/cmake/project.cmake)\nproject(ota_dependency_component_check)\n', encoding='utf-8')
            (project / 'main/CMakeLists.txt').write_text('idf_component_register(REQUIRES native_ota)\n', encoding='utf-8')
            shutil.copyfile(source_project / 'main/Kconfig.projbuild', project / 'main/Kconfig.projbuild')
            report['isolated_project'] = {'reason': 'Optional component present/absent check. Full C3 project configure invokes excluded donor codec patchers; no such command is run here.',
                'files': [identity(project / x) for x in ['CMakeLists.txt', 'main/CMakeLists.txt', 'main/Kconfig.projbuild']]}
        config = run / 'sdkconfig'
        shutil.copyfile(baseline / 'sdkconfig', config)
        report['sdkconfig_seed'] = identity(config)
        invocation = {'schema': report['schema'], 'target': args.target, 'project': str(project),
                      'sdk': str(sdk), 'tools': str(DEPS / ('tools-v6.0.2' if cyd else 'tools-v6.1')),
                      'build': str(build), 'config': str(config), 'defaults': str(source_project / 'sdkconfig.defaults'), 'run': str(run), 'probe': str(HERE / 'probe.cmake')}
        (run / 'invocation.json').write_text(json.dumps(invocation, indent=2) + '\n', encoding='utf-8')
        cmd = [str(PW), '-NoProfile', '-NonInteractive', '-File', str(HERE / 'sdk.ps1'), '-Invocation', str(run / 'invocation.json')]
        report['command'] = cmd
        save()
        with (run / 'stdout.log').open('wb') as out, (run / 'stderr.log').open('wb') as err:
            result = subprocess.run(cmd, cwd=project, stdout=out, stderr=err)
        report['returncode'] = result.returncode
        require(result.returncode == 0, 'Actual SDK launcher terminal failure')
        cache = (build / 'CMakeCache.txt').read_text(encoding='utf-8')
        cache_values = dict(re.findall(r'^([^#/:][^:=]*):[^=\n]*=(.*)$', cache, re.M))
        report['tools'] = [identity(cache_values[key]) for key in ['PYTHON', 'CMAKE_COMMAND', 'CMAKE_MAKE_PROGRAM', 'CMAKE_C_COMPILER_AR', 'CMAKE_C_COMPILER_RANLIB']]
        report['tools'].append(identity(PW))
        description = json.loads((build / 'project_description.json').read_bytes())
        ota = description['build_component_info']['native_ota']
        stream = description['build_component_info'].get('native_stream')
        properties = dict(x.split('=', 1) for x in (build / 'ota-target-properties.txt').read_text(encoding='utf-8').splitlines())
        require('lwip' in ota['priv_reqs'], 'Existing lwip dependency')
        if args.stream == 'present':
            require(stream is not None and stream['include_dirs'] == ['include'], 'Existing public stream header')
            require('__idf_native_stream' in properties['LINK_LIBRARIES'].split(';'), 'Effective private target dependency')
            require('$<LINK_ONLY:__idf_native_stream>' in properties['INTERFACE_LINK_LIBRARIES'].split(';'), 'PRIVATE link-only export')
            require('__idf_native_stream' not in properties['INTERFACE_LINK_LIBRARIES'].split(';'), 'No PUBLIC header re-export')
            require(properties['NATIVE_STREAM_TYPE'] == 'STATIC_LIBRARY', 'Ordinary static stream archive')
        else:
            require(stream is None and properties['NATIVE_STREAM_TYPE'] == 'absent', 'No stream component discovery')
            require('__idf_native_stream' not in properties['LINK_LIBRARIES'] + properties['INTERFACE_LINK_LIBRARIES'], 'No new stream target dependency')
        report['target_properties'] = properties
        before_config = json.loads((baseline / 'sdkconfig.json').read_bytes())
        after_config = json.loads((build / 'config/sdkconfig.json').read_bytes())
        changes = {key: {'before': before_config.get(key), 'after': after_config.get(key)}
                   for key in before_config.keys() | after_config.keys()
                   if before_config.get(key) != after_config.get(key)}
        report['normalized_config_changes'] = changes
        require(not changes if full_cyd else not any(key in before_config and key in after_config for key in changes),
                'Normalized full CYD config / common isolated C3 symbols unchanged')
        report['normalized_config_scope'] = 'full CYD project' if full_cyd else 'only shared symbols of isolated component project; missing full-radio symbols are recorded, not qualified'
        require(after_config['IDF_TARGET'] == args.target, 'Actual IDF target')
        commands = json.loads((build / 'compile_commands.json').read_bytes())
        rows = [x for x in commands if Path(x['file']).parent == ROOT / 'idf/components/native_ota']
        require(len(rows) == 3, 'Exactly three actual OTA compilation rows')
        expected_compiler = 'xtensa-esp32-elf-gcc.exe' if cyd else 'riscv32-esp-elf-gcc.exe'
        outlog = (run / 'stdout.log').read_text(encoding='utf-8', errors='replace')
        errlog = (run / 'stderr.log').read_text(encoding='utf-8', errors='replace')
        require(not re.search(r'Private include directory[\s\S]{0,300}native_stream', outlog + errlog), 'Original owner warning absent')
        compile_results = []
        headers = {}
        ninja_deps = (run / 'ninja-deps.txt').read_text(encoding='utf-8')
        for row in rows:
            command = row['command']
            require(expected_compiler in command and '/native_stream/include' in command.replace('\\', '/'), 'Actual target compiler and propagated include')
            compiler = command.split(' -D', 1)[0].strip('"')
            if not any(x['path'] == str(Path(compiler).resolve()) for x in report['tools']):
                report['tools'].append(identity(compiler))
            source_name = Path(row['file']).name
            actual_rows = [line for line in outlog.splitlines() if expected_compiler in line and source_name in line and ' -c ' in line]
            require(len(actual_rows) == 1, 'One actual compile invocation: ' + source_name)
            require(str(sdk).replace('\\', '/') in command.replace('\\', '/'), 'Pinned SDK headers in command')
            match = re.search(r'(?:^|\n)([^\n]*native_ota[^\n]*' + re.escape(source_name) + r'\.obj):[^\n]*\n((?:    [^\n]*\n)+)', ninja_deps)
            require(match is not None, 'Actual Ninja consumed dependency closure: ' + source_name)
            dependency_paths = [Path(x.strip()) for x in match.group(2).splitlines()]
            for path in dependency_paths:
                if not path.is_absolute(): path = build / path
                headers[str(path.resolve())] = identity(path)
            require(any(p.name == 'sdkconfig.h' for p in dependency_paths), 'Actual sdkconfig header dependency')
            obj = build / match.group(1)
            raw = obj.read_bytes()
            require(raw[:4] == b'\x7fELF' and struct.unpack_from('<H', raw, 18)[0] == (94 if cyd else 243), 'Actual object target architecture')
            compile_results.append({'source': identity(row['file']), 'command': row, 'actual_stdout_row': actual_rows[0],
                                    'object': identity(obj), 'elf_machine': 94 if cyd else 243,
                                    'dependency_header_count': len(dependency_paths)})
        report['compile_results'] = compile_results
        report['headers'] = list(headers.values())
        require(any('/native_stream/include/json_buffer.h' in p.replace('\\', '/') for p in headers), 'Actual json_buffer.h consumed')
        report['component_graph'] = {'native_ota': ota, 'native_stream': stream}
        report['library'] = identity(build / 'esp-idf/native_ota/libnative_ota.a')
        report['generated'] = [identity(build / x) for x in ['CMakeCache.txt', 'build.ninja', 'compile_commands.json', 'project_description.json', 'config/sdkconfig.json', 'config/sdkconfig.h', 'ota-target-properties.txt']]
        report['response_files'] = [identity(p) for p in (build / 'toolchain').rglob('*') if p.is_file()]
        report['warnings'] = [x for x in (outlog + errlog).splitlines() if re.search(r'warning:|CMake Warning', x, re.I)]
        require(not report['warnings'], 'No new configure/compiler warnings')
        report['notifications'] = [x for x in (outlog + errlog).splitlines() if x.startswith('NOTE:')]
        report['sources_after'] = snapshot(source_project)
        require(report['sources_before'] == report['sources_after'], 'Source and launcher stable before/after')
        report['sdk_after'] = {'path': str(sdk), 'commit': git('rev-parse', 'HEAD', cwd=sdk).decode().strip(),
                               'status': git('status', '--porcelain', '-uno', cwd=sdk).decode()}
        require(report['sdk_before'] == report['sdk_after'], 'SDK stable clean before/after')
        report['source_status_after'] = git('status', '--porcelain', '-uno').decode()
        require(report['source_status_before'] == report['source_status_after'], 'Source status stable')
        require(git('rev-parse', 'HEAD').decode().strip() == args.expected_head, 'Repository HEAD stable')
        report['status'] = 'PASS'
    except Exception as exc:
        report['status'] = 'FAIL'
        report['failure'] = repr(exc)
        raise
    finally:
        report['ended_unix'] = time.time()
        report['logs'] = [identity(run / x) for x in ['stdout.log', 'stderr.log', 'ninja-deps.txt'] if (run / x).is_file()]
        save()

if __name__ == '__main__': main()
