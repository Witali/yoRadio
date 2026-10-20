"""Read-only qualification of a terminal component build, without rebuilding."""
from pathlib import Path
import argparse
import copy
import json
import re
import struct
import time
import check

ROOT, HERE = check.ROOT, check.HERE
identity, git, require = check.identity, check.git, check.require

def warning_bodies(text):
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    blocks = re.findall(r'^CMake Warning[^\n]*\n[\s\S]*?(?=^Call Stack|\Z)', text, re.M)
    blocks += re.findall(r'^.*warning:.*$', text, re.M)
    return [' '.join(x.replace('\\', '/').split()) for x in blocks]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--output', default='qualification.json')
    args = parser.parse_args()
    run = HERE / args.attempt
    output = run / args.output
    require(not output.exists(), 'Never overwrite qualification')
    original = json.loads((run / 'report.json').read_bytes())
    require(original.get('returncode') == 0 and original['status'] in ['BUILD_PASS', 'FAIL'], 'Terminal successful actual build required')
    if original['status'] == 'FAIL':
        require(original.get('failure') == "KeyError('PYTHON')" and args.attempt in ['cyd-present-01', 'c3-absent-01'], 'Only preserved cache-parser failure can be qualified separately')
    report = copy.deepcopy(original)
    report['original_runner'] = {'report': identity(run / 'report.json'), 'status': original['status'], 'failure': original.get('failure')}
    report.pop('failure', None)
    report['status'] = 'QUALIFYING'
    report['qualification_started_unix'] = time.time()
    report['qualification_tool'] = identity(__file__)
    try:
        target, mode = report['target'], report['stream']
        cyd = target == 'esp32'
        baseline = ROOT / 'firmware/development' / ('esp32-cyd2usb-native-early-mpi-pdm' if cyd else 'esp32c3-oled-native-ap-timeout')
        sdk = Path(report['sdk_before']['path'])
        invocation = json.loads((run / 'invocation.json').read_bytes())
        build = Path(invocation['build'])
        for row in report['baseline'] + report['sources_before'] + report['sdk_cmake']:
            require(identity(row['path']) == row, 'Frozen source/baseline/SDK CMake input: ' + row['path'])
        report['sources_after'] = [identity(x['path']) for x in report['sources_before']]
        require(report['sources_after'] == report['sources_before'], 'Original pre-build source inputs unchanged')
        report['source_status_after'] = git('status', '--porcelain', '-uno').decode()
        require(report['source_status_after'] == report['source_status_before'], 'Original source status unchanged')
        require(git('rev-parse', 'HEAD').decode().strip() == report['source_commit'], 'Original HEAD unchanged')
        report['sdk_after'] = {'path': str(sdk), 'commit': git('rev-parse', 'HEAD', cwd=sdk).decode().strip(), 'status': git('status', '--porcelain', '-uno', cwd=sdk).decode()}
        require(report['sdk_after'] == report['sdk_before'] and report['sdk_after']['status'] == '', 'Pinned SDK remains clean')
        cache = (build / 'CMakeCache.txt').read_text(encoding='utf-8')
        cache_values = dict(re.findall(r'^([^#/:\r\n][^:=\r\n]*):[^=\r\n]*=(.*)$', cache, re.M))
        report['tools'] = [identity(cache_values[key]) for key in ['PYTHON', 'CMAKE_COMMAND', 'CMAKE_MAKE_PROGRAM', 'CMAKE_C_COMPILER_AR', 'CMAKE_C_COMPILER_RANLIB']]
        report['tools'].append(identity(check.PW))
        description = json.loads((build / 'project_description.json').read_bytes())
        ota, stream = description['build_component_info']['native_ota'], description['build_component_info'].get('native_stream')
        props = dict(x.split('=', 1) for x in (build / 'ota-target-properties.txt').read_text(encoding='utf-8').splitlines())
        require('lwip' in ota['priv_reqs'] and 'native_stream' not in ota['reqs'], 'Existing requirements / no public stream dependency')
        if mode == 'present':
            require(stream is not None and stream['include_dirs'] == ['include'], 'Actual existing stream component')
            require('__idf_native_stream' in props['LINK_LIBRARIES'].split(';'), 'Actual private target link')
            require('$<LINK_ONLY:__idf_native_stream>' in props['INTERFACE_LINK_LIBRARIES'].split(';'), 'Private link-only export')
            require('__idf_native_stream' not in props['INTERFACE_LINK_LIBRARIES'].split(';'), 'No public header re-export')
            require(props['NATIVE_STREAM_TYPE'] == 'STATIC_LIBRARY', 'Ordinary static library')
            require('/native_stream/include' not in props['INCLUDE_DIRECTORIES'].replace('\\', '/'), 'No direct sibling include when component present')
        else:
            require(stream is None and props['NATIVE_STREAM_TYPE'] == 'absent', 'No stream discovery')
            require('__idf_native_stream' not in props['LINK_LIBRARIES'] + props['INTERFACE_LINK_LIBRARIES'], 'No stream target introduced')
            require('/native_stream/include' in props['INCLUDE_DIRECTORIES'].replace('\\', '/'), 'Original private header fallback')
        report['component_graph'] = {'native_ota': ota, 'native_stream': stream}
        report['target_properties'] = props
        before = json.loads((baseline / 'sdkconfig.json').read_bytes())
        after = json.loads((build / 'config/sdkconfig.json').read_bytes())
        report['normalized_config_changes'] = {k: {'before': before.get(k), 'after': after.get(k)} for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
        report['common_config_changes'] = {k: v for k, v in report['normalized_config_changes'].items() if k in before and k in after}
        require(not report['common_config_changes'], 'All common configuration symbols preserved')
        full_cyd = cyd and mode == 'present'
        if full_cyd: require(not report['normalized_config_changes'], 'Full CYD normalized config preserved')
        report['normalized_config_scope'] = 'full CYD project' if full_cyd else 'shared symbols only; unavailable full-radio symbols recorded without qualification'
        require(after['IDF_TARGET'] == target, 'Correct actual target')
        rows = [x for x in json.loads((build / 'compile_commands.json').read_bytes()) if Path(x['file']).parent == ROOT / 'idf/components/native_ota']
        require(len(rows) == 3, 'Three actual OTA compile rows')
        stdout = (run / 'stdout.log').read_text(encoding='utf-8', errors='replace')
        stderr = (run / 'stderr.log').read_text(encoding='utf-8', errors='replace')
        require(not re.search(r'Private include directory[\s\S]{0,300}native_stream', stdout + stderr), 'Original OTA include-owner warning absent')
        manifest = json.loads((baseline / 'manifest.json').read_bytes())
        baseline_log = baseline / ('build-2.log' if cyd else 'build-stderr.log')
        baseline_sha = next(x['sha256'] for x in manifest['build_logs'] if x['file'] == 'build-2.log') if cyd else manifest['build_metadata_sha256']['build-stderr.log']
        require(identity(baseline_log)['sha256'] == baseline_sha, 'Immutable baseline warning log binding')
        report['baseline_warning_log'] = identity(baseline_log)
        report['baseline_warnings'] = [x for x in warning_bodies(baseline_log.read_text(encoding='utf-8')) if 'native_stream' not in x]
        report['warnings'] = warning_bodies(stdout + '\n' + stderr)
        report['new_warnings'] = [x for x in report['warnings'] if x not in report['baseline_warnings']]
        report['harness_advisories'] = []
        for warning in report['new_warnings']:
            if args.attempt == 'cyd-present-01' and 'CMAKE_OBJECT_PATH_MAX' in warning and '/mbedtls/mbedtls/tf-psa-crypto/core/CMakeLists.txt' in warning:
                report['harness_advisories'].append({'kind': 'long isolated build path', 'body': warning, 'scope': 'actual archive and three OTA objects compiled successfully; this advisory does not qualify full application portability'})
            elif args.attempt == 'c3-absent-01' and 'Partition table CSV file' in warning and 'not found' in warning and (str(run / 'project/partitions.csv').replace('\\', '/') in warning):
                report['harness_advisories'].append({'kind': 'isolated project omitted partition CSV', 'body': warning, 'scope': 'no partition/image/full application qualification; native_ota component compilation succeeded'})
        report['new_source_warnings'] = [x for x in report['new_warnings'] if x not in [a['body'] for a in report['harness_advisories']]]
        require(not report['new_source_warnings'] and len(report['harness_advisories']) <= 1, 'No new OTA/compiler warnings; exact historical harness advisories retained')
        report['missing_partition_tracebacks'] = stderr.count('FileNotFoundError:')
        require(not report['missing_partition_tracebacks'] or args.attempt == 'c3-absent-01', 'No unexpected configure tracebacks')
        report['notifications'] = [x for x in (stdout + stderr).splitlines() if x.startswith('NOTE:')]
        expected_compiler = 'xtensa-esp32-elf-gcc.exe' if cyd else 'riscv32-esp-elf-gcc.exe'
        dependencies = (run / 'ninja-deps.txt').read_text(encoding='utf-8')
        headers, results = {}, []
        for row in rows:
            command, source = row['command'], Path(row['file'])
            compiler = command.split(' -D', 1)[0].strip('"')
            compiler_identity = identity(compiler)
            if compiler_identity not in report['tools']: report['tools'].append(compiler_identity)
            require(Path(compiler).name == expected_compiler and compiler_identity['sha256'] == manifest['compiler_sha256'], 'Actual target compiler matches frozen baseline identity')
            require('/native_stream/include' in command.replace('\\', '/'), 'Actual propagated/fallback header path')
            require(str(sdk).replace('\\', '/') in command.replace('\\', '/'), 'Actual pinned SDK header path')
            actual_rows = [x for x in stdout.splitlines() if expected_compiler in x and source.name in x and ' -c ' in x]
            require(len(actual_rows) == 1, 'One actual compiler invocation per OTA source')
            match = re.search(r'(?:^|\n)([^\n]*native_ota[^\n]*' + re.escape(source.name) + r'\.obj):[^\n]*\n((?:    [^\n]*\n)+)', dependencies)
            require(match is not None, 'Actual consumed header closure')
            paths = [Path(x.strip()) for x in match.group(2).splitlines()]
            for p in paths:
                if not p.is_absolute(): p = build / p
                headers[str(p.resolve())] = identity(p)
            require(any(p.name == 'sdkconfig.h' for p in paths), 'Actual config header consumed')
            obj = build / match.group(1)
            raw = obj.read_bytes()
            machine = struct.unpack_from('<H', raw, 18)[0]
            require(raw[:4] == b'\x7fELF' and machine == (94 if cyd else 243), 'Actual object architecture')
            results.append({'source': identity(source), 'command': row, 'actual_stdout_row': actual_rows[0], 'object': identity(obj), 'elf_machine': machine, 'dependency_header_count': len(paths)})
        require(any('/native_stream/include/json_buffer.h' in p.replace('\\', '/') for p in headers), 'Actual json_buffer.h consumed')
        report['compile_results'], report['headers'] = results, list(headers.values())
        report['library'] = identity(build / 'esp-idf/native_ota/libnative_ota.a')
        report['generated'] = [identity(build / x) for x in ['CMakeCache.txt', 'build.ninja', 'compile_commands.json', 'project_description.json', 'config/sdkconfig.json', 'config/sdkconfig.h', 'ota-target-properties.txt']]
        report['response_files'] = [identity(p) for p in (build / 'toolchain').rglob('*') if p.is_file()]
        for row in report.get('tools_before', []): require(identity(row['path']) == row, 'Pre/post build tool identity')
        report['tool_identity_scope'] = 'before and after fresh build for resolved bootstrap tools; remaining linker helpers identified after build' if report.get('tools_before') else 'qualification after build; actual compiler matches immutable pre-existing baseline manifest; no claim of a new pre-build hash for other tools'
        require(identity(__file__) == report['qualification_tool'], 'Qualification tool stable')
        report['status'] = 'PASS'
    except Exception as exc:
        report['status'], report['failure'] = 'FAIL', repr(exc)
        raise
    finally:
        report['qualification_ended_unix'] = time.time()
        output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'attempt': args.attempt, 'report': identity(output)}))

if __name__ == '__main__': main()
