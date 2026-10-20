"""Fresh build-only runner. Qualification is a separate read-only operation."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import time
import check

ROOT, HERE, DEPS, PW = check.ROOT, check.HERE, check.DEPS, check.PW
identity, git, require = check.identity, check.git, check.require

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', choices=['esp32', 'esp32c3'], required=True)
    parser.add_argument('--stream', choices=['present', 'absent'], required=True)
    parser.add_argument('--expected-head', required=True)
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    run = HERE / args.attempt
    require(not run.exists(), 'Fresh attempt required')
    run.mkdir()
    report = {'schema': 'ota-component-check-v1', 'status': 'RUNNING', 'target': args.target, 'stream': args.stream,
              'scope': 'actual SDK native_ota static component build; qualification is separate',
              'full_application': False, 'hardware_tested': False, 'started_unix': time.time(), 'source_commit': args.expected_head}
    def save(): (run / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    save()
    try:
        cyd = args.target == 'esp32'
        source_project = ROOT / 'idf' / ('esp32-cyd2usb-native' if cyd else 'esp32c3-oled-native')
        sdk = DEPS / ('v6.0.2' if cyd else 'v6.1-9a97f6c54ec6')
        baseline = ROOT / 'firmware/development' / ('esp32-cyd2usb-native-early-mpi-pdm' if cyd else 'esp32c3-oled-native-ap-timeout')
        expected_sdk = '7101770dc6db2667b3c477cc31365dd1acd6db4e' if cyd else '9a97f6c54ec638111ce55cd36581b3c192f15207'
        require(git('rev-parse', 'HEAD').decode().strip() == args.expected_head, 'HEAD match')
        report['source_status_before'] = git('status', '--porcelain', '-uno').decode()
        report['sdk_before'] = {'path': str(sdk), 'commit': git('rev-parse', 'HEAD', cwd=sdk).decode().strip(), 'status': git('status', '--porcelain', '-uno', cwd=sdk).decode()}
        require(report['sdk_before']['commit'] == expected_sdk and not report['sdk_before']['status'], 'Clean pinned SDK')
        report['sources_before'] = check.snapshot(source_project) + [identity(HERE / p) for p in ['run.py', 'qualify.py']]
        report['sdk_cmake'] = [identity(sdk / p) for p in ['tools/cmake/component.cmake', 'tools/cmake/component_validation.cmake', 'tools/cmake/scripts/component_get_requirements.cmake']]
        report['baseline'] = [identity(baseline / p) for p in ['sdkconfig', 'sdkconfig.json', 'manifest.json', 'project_description.json']]
        tools_root = DEPS / ('tools-v6.0.2' if cyd else 'tools-v6.1')
        compiler = json.loads((baseline / 'manifest.json').read_bytes())['compiler']
        tool_paths = [Path(compiler), PW]
        tool_paths += list((tools_root / 'tools/cmake').glob('*/bin/cmake.exe'))
        tool_paths += list((tools_root / 'tools/ninja').glob('*/ninja.exe'))
        tool_paths += list((tools_root / 'python_env').glob('*/Scripts/python.exe'))
        report['tools_before'] = [identity(p) for p in tool_paths]
        project = source_project
        if not (cyd and args.stream == 'present'):
            project = run / 'project'
            (project / 'main').mkdir(parents=True)
            names = ['native_ota', 'native_storage', 'native_web_transport']
            if args.stream == 'present': names.append('native_stream')
            component_dirs = [ROOT / 'idf/components' / x for x in names]
            (project / 'CMakeLists.txt').write_text('cmake_minimum_required(VERSION 3.16)\nset(EXTRA_COMPONENT_DIRS\n' + ''.join('  "' + p.as_posix() + '"\n' for p in component_dirs) + ')\ninclude($ENV{IDF_PATH}/tools/cmake/project.cmake)\nproject(ota_dependency_component_check)\n', encoding='utf-8')
            (project / 'main/CMakeLists.txt').write_text('idf_component_register(REQUIRES native_ota)\n', encoding='utf-8')
            for name in ['main/Kconfig.projbuild', 'partitions.csv']:
                shutil.copyfile(source_project / name, project / name)
            report['isolated_project'] = {'reason': 'Scoped optional-dependency project; donor C3 configure and codec patchers are excluded.',
                'files': [identity(project / p) for p in ['CMakeLists.txt', 'main/CMakeLists.txt', 'main/Kconfig.projbuild', 'partitions.csv']]}
        build = HERE / ('ba' if cyd else 'bp')
        require(not build.exists(), 'Fresh short build directory required')
        build.mkdir()
        shutil.copyfile(baseline / 'sdkconfig', run / 'sdkconfig')
        report['sdkconfig_seed'] = identity(run / 'sdkconfig')
        invocation = {'schema': report['schema'], 'target': args.target, 'project': str(project), 'sdk': str(sdk),
                      'tools': str(tools_root), 'build': str(build), 'config': str(run / 'sdkconfig'),
                      'defaults': str(source_project / 'sdkconfig.defaults'), 'run': str(run), 'probe': str(HERE / 'probe.cmake')}
        (run / 'invocation.json').write_text(json.dumps(invocation, indent=2) + '\n', encoding='utf-8')
        report['command'] = [str(PW), '-NoProfile', '-NonInteractive', '-File', str(HERE / 'sdk.ps1'), '-Invocation', str(run / 'invocation.json')]
        save()
        with (run / 'stdout.log').open('wb') as out, (run / 'stderr.log').open('wb') as err:
            result = subprocess.run(report['command'], cwd=project, stdout=out, stderr=err)
        report['returncode'] = result.returncode
        require(result.returncode == 0, 'Actual SDK launcher terminal failure')
        report['sources_after'] = check.snapshot(source_project) + [identity(HERE / p) for p in ['run.py', 'qualify.py']]
        report['tools_after'] = [identity(x['path']) for x in report['tools_before']]
        require(report['sources_before'] == report['sources_after'] and report['tools_before'] == report['tools_after'], 'Sources/tools stable')
        report['sdk_after'] = {'path': str(sdk), 'commit': git('rev-parse', 'HEAD', cwd=sdk).decode().strip(), 'status': git('status', '--porcelain', '-uno', cwd=sdk).decode()}
        require(report['sdk_after'] == report['sdk_before'], 'SDK clean stable')
        report['source_status_after'] = git('status', '--porcelain', '-uno').decode()
        require(report['source_status_after'] == report['source_status_before'] and git('rev-parse', 'HEAD').decode().strip() == args.expected_head, 'HEAD/status stable')
        report['status'] = 'BUILD_PASS'
    except Exception as exc:
        report['status'], report['failure'] = 'FAIL', repr(exc)
        raise
    finally:
        report['ended_unix'] = time.time()
        report['logs'] = [identity(run / x) for x in ['stdout.log', 'stderr.log', 'ninja-deps.txt'] if (run / x).is_file()]
        save()

if __name__ == '__main__': main()
