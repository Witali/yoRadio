"""Freeze actual Clang unit/header/build inputs before a fresh CYD AST campaign."""
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
TOOL = Path('C:/Work/yoRadio/.idf/tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829/esp-clang/bin/clang-tidy.exe')
sha = lambda data: hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['vendor', 'custom'], required=True)
    args = parser.parse_args()
    build = ROOT / ('idf/esp32-cyd2usb-native/build-lint-network-' + args.mode + '-final')
    out = ROOT / ('.build/lint-cyd-network-' + args.mode + '-final')
    out.mkdir(exist_ok=False)
    (out / 'dependencies').mkdir()
    entries = json.loads((build / 'compile_commands.json').read_text(encoding='utf-8'))
    for entry in entries:
        assert 'esp-clang' in entry['command'].split()[0], entry['command'].split()[0]
    config = json.loads((build / 'config/sdkconfig.json').read_text(encoding='utf-8'))
    assert bool(config.get('YORADIO_FLAC_DECODER_CUSTOM')) == (args.mode == 'custom')
    assert bool(config.get('YORADIO_FLAC_DECODER_ESPRESSIF')) == (args.mode == 'vendor')
    assert config['YORADIO_NATIVE_AUDIO_OUTPUT_PDM'] and not config.get('YORADIO_NATIVE_DIAGNOSTICS')
    assert config['ESP_DEFAULT_CPU_FREQ_MHZ'] == 240 if 'ESP_DEFAULT_CPU_FREQ_MHZ' in config else config['ESP32_DEFAULT_CPU_FREQ_MHZ'] == 240
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
        if args.mode == 'custom' and path not in [ROOT / 'idf/esp32-cyd2usb-native/main/audio_service.c', ROOT / 'idf/esp32-cyd2usb-native/main/decoder_registration.c']:
            continue
        selected.append((path, entry))
    selected.sort(key=lambda item: str(item[0]))
    assert selected and len({p for p, _ in selected}) == len(selected)
    if args.mode == 'custom': assert len(selected) == 2
    input_hashes = {str(path): sha(path.read_bytes()) for path, _ in selected}
    print('Clang preflight dependency inventory:', args.mode, len(selected), 'units', flush=True)

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
    # Include all project-owned headers, including inactive conditional paths,
    # not merely the headers entered by this preprocessing configuration.
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard',
        'idf/components', 'idf/esp32-cyd2usb-native/main', 'yoRadio/src/audioI2S', 'yoRadio/src/core'], cwd=ROOT, text=True).splitlines()
    paths.update((ROOT / name).resolve() for name in names if Path(name).suffix.lower() in ['.h', '.hpp', '.inc'] or Path(name).name in ['CMakeLists.txt', 'Kconfig.projbuild'])
    paths.update([ROOT / '.clang-tidy', ROOT / 'tools/run_native_lint.py', Path(__file__).resolve(),
        ROOT / '.build/run-network-lint-configure.ps1', ROOT / 'idf/esp32-cyd2usb-native/build.ps1',
        ROOT / 'idf/esp32-cyd2usb-native/CMakeLists.txt', ROOT / 'idf/esp32-cyd2usb-native/sdkconfig.defaults'])
    for relative in ['compile_commands.json', 'CMakeCache.txt', 'sdkconfig', 'project_description.json',
                     'toolchain/cflags', 'toolchain/cxxflags']:
        path = build / relative
        if path.is_file(): paths.add(path)
    paths.update(p for p in (build / 'config').rglob('*') if p.is_file())
    actual_analysis_db = build
    if args.mode == 'custom':
        actual_analysis_db = out / 'filtered-db'
        actual_analysis_db.mkdir()
        (actual_analysis_db / 'compile_commands.json').write_text(json.dumps([e for _, e in selected], indent=2) + '\n', encoding='utf-8')
        paths.add(actual_analysis_db / 'compile_commands.json')
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
    manifest = dict(scope='All selected translation units, complete actual Clang -M dependency union including SDK/vendor/toolchain headers, all project headers and relevant build/configuration inputs frozen before clang-tidy. Analysis uses the original SDK compiler database; every captured source/header/build input is checked after it. No SDK/RTOS behavior is executed and no optimized Clang firmware code generation is claimed.',
        mode=args.mode, captured_before_analysis_utc=datetime.datetime.now(datetime.UTC).isoformat(),
        source_commit_before=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        actual_build_dir=build.relative_to(ROOT).as_posix(), analysis_database=actual_analysis_db.relative_to(ROOT).as_posix(),
        tool={'path': str(TOOL), 'sha256': sha(TOOL.read_bytes()), 'version': subprocess.check_output([str(TOOL), '--version'], text=True).strip()},
        unit_dependencies={p.relative_to(ROOT).as_posix(): [str(d) for d in deps] for p, deps, _ in inventory},
        dependency_commands={p.relative_to(ROOT).as_posix(): cmd for p, _, cmd in inventory},
        inputs=snapshots)
    (out / 'source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Frozen before analysis:', len(snapshots), 'source/header/build files', flush=True)
    command = [sys.executable, '-B', '-X', 'utf8', str(ROOT / 'tools/run_native_lint.py'),
        '--build-dir', str(actual_analysis_db), '--clang-tidy', str(TOOL),
        '--output', str(out / 'analysis'), '--jobs', '2']
    if args.mode == 'vendor': command.append('--include-httpd-overlay')
    with (out / 'analysis-console.log').open('w', encoding='utf-8') as log:
        process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding='utf-8', errors='replace')
        for line in process.stdout:
            print(line, end='', flush=True)
            log.write(line); log.flush()
        status = process.wait()
    after = {}
    for name, item in snapshots.items():
        after[name] = sha(Path(name).read_bytes()) == item['sha256']
    (out / 'post-analysis-verification.json').write_text(json.dumps(dict(passed=all(after.values()),
        completed_utc=datetime.datetime.now(datetime.UTC).isoformat(), inputs=after), indent=2) + '\n', encoding='utf-8')
    assert all(after.values()), [name for name, unchanged in after.items() if not unchanged]
    raw_report = out / 'analysis/report.json'
    report = json.loads(raw_report.read_text(encoding='utf-8'))
    assert {row['file'] for row in report['results']} == {p.relative_to(ROOT).as_posix() for p, _ in selected}
    for row in report['results']:
        assert row['source_sha256'] == snapshots[str((ROOT / row['file']).resolve())]['sha256']
    report.update(mode=args.mode, scope=manifest['scope'],
        source_manifest='source-manifest.json', source_manifest_sha256=sha((out / 'source-manifest.json').read_bytes()),
        captured_input_count=len(snapshots), pre_analysis_snapshot=True, all_inputs_unchanged_after_analysis=True,
        raw_report='analysis/report.json', raw_report_sha256=sha(raw_report.read_bytes()),
        analysis_command=command, analysis_exit=status)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    assert status == 0 and report['complete'] and report['errors'] == 0
    print('QUALIFIED', args.mode, report['units'], 'units', report['warnings'], 'warnings', report['errors'], 'errors', flush=True)


if __name__ == '__main__': main()
