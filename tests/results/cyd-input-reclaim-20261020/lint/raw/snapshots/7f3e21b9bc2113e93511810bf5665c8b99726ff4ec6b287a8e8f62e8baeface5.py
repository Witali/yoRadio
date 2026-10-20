"""Freeze all actual Clang unit/header/configuration inputs before full AST analysis."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

ROOT = Path.cwd()
sha = lambda data: hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board', choices=['cyd', 'c3'], required=True)
    args = parser.parse_args()
    project = Path('idf/esp32-cyd2usb-native' if args.board == 'cyd' else 'idf/esp32c3-oled-native')
    series, version = (('v6.0.2', '20.1.1_20250829') if args.board == 'cyd' else ('v6.1', '21.1.3_20260408'))
    tool = Path('C:/Work/yoRadio/.idf/tools-' + series + '/tools/esp-clang/esp-' + version + '/esp-clang/bin/clang-tidy.exe')
    build = ROOT / project / 'build-lint-input-reclaim-01'
    out = ROOT / ('.build/lint-' + args.board + '-input-reclaim-01')
    out.mkdir(exist_ok=False)
    (out / 'dependencies').mkdir()
    entries = json.loads((build / 'compile_commands.json').read_text(encoding='utf-8'))
    for entry in entries:
        assert 'esp-clang' in entry['command'].split()[0], entry['command'].split()[0]
    config = json.loads((build / 'config/sdkconfig.json').read_text(encoding='utf-8'))
    if args.board == 'cyd':
        assert config['YORADIO_NATIVE_AUDIO_OUTPUT_PDM'] and not config.get('YORADIO_NATIVE_DIAGNOSTICS')
        assert config['YORADIO_FLAC_DECODER_ESPRESSIF'] and not config.get('YORADIO_FLAC_DECODER_CUSTOM')
        assert config['ESP_DEFAULT_CPU_FREQ_MHZ'] == 240
        assert config['YORADIO_TLS_INPUT_RECLAIM']
    else:
        assert config['YORADIO_FLAC_DECODER_CUSTOM'] and not config.get('YORADIO_FLAC_DECODER_ESPRESSIF')
        assert config['ESP_DEFAULT_CPU_FREQ_MHZ'] == 160
    selected = []
    for entry in entries:
        path = Path(entry['file'])
        if not path.is_absolute(): path = Path(entry['directory']) / path
        path = path.resolve()
        if not path.is_relative_to(ROOT) or path.suffix.lower() not in ['.c', '.cc', '.cpp', '.cxx']:
            continue
        overlay = path.parent == build / 'native-httpd-rfc6455' and path.name in ['httpd_ws.c', 'httpd_parse.c']
        if not overlay and any(part.startswith(('build', '.')) for part in path.relative_to(ROOT).parts[:-1]):
            continue
        selected.append((path, entry))
    selected.sort(key=lambda item: str(item[0]))
    assert selected and len({p for p, _ in selected}) == len(selected)
    assert ROOT / 'idf/components/native_network_power/native_network_power.c' in {p for p, _ in selected}
    input_hashes = {str(path): sha(path.read_bytes()) for path, _ in selected}
    print('Clang preflight dependency inventory:', args.board, len(selected), 'units', flush=True)

    def dependencies(item):
        path, entry = item
        name = ('httpd_overlay__' + path.name if path.parent == build / 'native-httpd-rfc6455'
                else path.relative_to(ROOT).as_posix().replace('/', '__'))
        target = out / 'dependencies' / (name + '.d')
        command, count = re.subn(r' -o (?:"[^"]*"|\S+) -c ',
            ' -M -MT dependency -MF "' + target.as_posix() + '" ', entry['command'])
        assert count == 1, path
        result = subprocess.run(command, cwd=entry['directory'], capture_output=True, timeout=120)
        (out / 'dependencies' / (name + '.log')).write_bytes(result.stdout + result.stderr)
        assert result.returncode == 0, (path, result.returncode, result.stderr.decode(errors='replace'))
        body = target.read_text(encoding='utf-8').split(':', 1)[1].replace('\\\n', ' ')
        paths = sorted({Path(p).resolve() for p in shlex.split(body)})
        assert path in paths and paths
        assert sha(path.read_bytes()) == input_hashes[str(path)], path
        return path, paths, command

    with ThreadPoolExecutor(max_workers=4) as pool:
        inventory = list(pool.map(dependencies, selected))
    paths = {path for path, _ in selected}
    for _, dependencies_, _ in inventory: paths.update(dependencies_)
    names = subprocess.check_output(['git', '-c', 'core.longpaths=true', 'ls-files', '--cached', '--others', '--exclude-standard',
        'idf/components', (project / 'main').as_posix(), 'yoRadio/src/audioI2S', 'yoRadio/src/core'], cwd=ROOT, text=True).splitlines()
    paths.update((ROOT / name).resolve() for name in names if Path(name).suffix.lower() in ['.h', '.hpp', '.inc'] or Path(name).name in ['CMakeLists.txt', 'Kconfig.projbuild'])
    paths.update([ROOT / '.clang-tidy', ROOT / 'tools/run_native_lint.py', Path(__file__).resolve(),
        ROOT / '.build/run-input-reclaim-lint-configure.ps1', ROOT / project / 'build.ps1',
        ROOT / project / 'CMakeLists.txt', ROOT / project / 'sdkconfig.defaults'])
    paths.update(p for p in (ROOT / 'tools').glob('patch_*.py') if p.is_file())
    paths.update(p for p in (ROOT / project / 'main/compat').rglob('*.cmake') if p.is_file())
    paths.update(p for p in (ROOT / project).glob('idf-*') if p.is_file())
    for relative in ['compile_commands.json', 'CMakeCache.txt', 'sdkconfig', 'project_description.json',
                     'toolchain/cflags', 'toolchain/cxxflags']:
        path = build / relative
        if path.is_file(): paths.add(path)
    paths.update(p for p in (build / 'config').rglob('*') if p.is_file())
    external_root = Path('C:/Work/yoRadio/.idf')
    snapshots = {}
    for path in sorted(paths):
        if path.is_relative_to(ROOT): snapshot = Path('sources') / path.relative_to(ROOT)
        else:
            assert path.is_relative_to(external_root), path
            snapshot = Path('dependency-sources/.idf') / path.relative_to(external_root)
        raw = path.read_bytes()
        destination = out / snapshot
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        snapshots[str(path)] = {'snapshot': snapshot.as_posix(), 'sha256': sha(raw), 'bytes': len(raw)}
    manifest = dict(scope='All project translation units and generated project-patched HTTPD units in the actual SDK Clang database; complete Clang -M dependency union including SDK/vendor/toolchain headers, all project headers and relevant build/configuration inputs frozen before clang-tidy. Analysis uses that original SDK compiler database; every captured source/header/build input is checked afterward. No SDK/RTOS behavior is executed and no optimized Clang firmware code generation is claimed.',
        board=args.board, captured_before_analysis_utc=datetime.datetime.now(datetime.UTC).isoformat(),
        source_commit_before=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        actual_build_dir=build.relative_to(ROOT).as_posix(), analysis_database=build.relative_to(ROOT).as_posix(),
        tool={'path': str(tool), 'sha256': sha(tool.read_bytes()), 'version': subprocess.check_output([str(tool), '--version'], text=True).strip()},
        unit_dependencies={p.relative_to(ROOT).as_posix(): [str(d) for d in deps] for p, deps, _ in inventory},
        dependency_commands={p.relative_to(ROOT).as_posix(): cmd for p, _, cmd in inventory}, inputs=snapshots)
    (out / 'source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Frozen before analysis:', args.board, len(snapshots), 'source/header/build files', flush=True)
    command = [sys.executable, '-B', '-X', 'utf8', str(ROOT / 'tools/run_native_lint.py'),
        '--build-dir', str(build), '--clang-tidy', str(tool), '--output', str(out / 'analysis'),
        '--jobs', '2', '--include-httpd-overlay']
    with (out / 'analysis-console.log').open('w', encoding='utf-8') as log:
        process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding='utf-8', errors='replace')
        for line in process.stdout:
            print(line, end='', flush=True)
            log.write(line); log.flush()
        status = process.wait()
    after = {name: sha(Path(name).read_bytes()) == item['sha256'] for name, item in snapshots.items()}
    (out / 'post-analysis-verification.json').write_text(json.dumps(dict(passed=all(after.values()),
        completed_utc=datetime.datetime.now(datetime.UTC).isoformat(), inputs=after), indent=2) + '\n', encoding='utf-8')
    assert all(after.values()), [name for name, unchanged in after.items() if not unchanged]
    raw_report = out / 'analysis/report.json'
    report = json.loads(raw_report.read_text(encoding='utf-8'))
    assert {row['file'] for row in report['results']} == {p.relative_to(ROOT).as_posix() for p, _ in selected}
    for row in report['results']:
        assert row['source_sha256'] == snapshots[str((ROOT / row['file']).resolve())]['sha256']
    report.update(board=args.board, scope=manifest['scope'], source_manifest='source-manifest.json',
        source_manifest_sha256=sha((out / 'source-manifest.json').read_bytes()), captured_input_count=len(snapshots),
        pre_analysis_snapshot=True, all_inputs_unchanged_after_analysis=True, raw_report='analysis/report.json',
        raw_report_sha256=sha(raw_report.read_bytes()), analysis_command=command, analysis_exit=status)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    assert status == 0 and report['complete'] and report['errors'] == 0
    print('QUALIFIED', args.board, report['units'], 'units', report['warnings'], 'warnings', report['errors'], 'errors', flush=True)


if __name__ == '__main__': main()
