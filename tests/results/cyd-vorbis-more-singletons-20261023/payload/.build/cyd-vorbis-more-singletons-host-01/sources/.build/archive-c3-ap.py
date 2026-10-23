"""Archive current C3 AP repair evidence; retain immutable reports and short raw dependencies."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
dest = root / 'tests/results/c3-ap-timeout-20261020'
groups = {
    'ap': 'c3-ap-timeout-final-02',
    'reboot': 'c3-ap-reboot-leases-01',
    'power': 'c3-ap-regression-power-01',
    'time-settings': 'c3-ap-regression-time-settings-01',
    'startup': 'c3-ap-regression-bootstrap-02',
    'wifi': 'c3-ap-regression-wifi-01',
    'time-service': 'c3-ap-regression-time-service-01',
    'websocket': 'c3-ap-regression-websocket-01',
    'lint': 'lint-c3-ap-timeout-01',
    'review': 'c3-ap-independent-review-01',
}
allowed = {'.c', '.cpp', '.h', '.hpp', '.inc', '.py', '.ps1', '.js', '.json',
           '.log', '.md', '.yaml', '.d', '.txt', '.cmake', '.defaults', '.projbuild'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
relocated, reports, checked = {}, {}, {}
dest.mkdir(parents=True, exist_ok=True)

def copy(source, target):
    if target.exists():
        assert target.read_bytes() == source.read_bytes(), target
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

for group, name in groups.items():
    source = root / '.build' / name
    primary = source / ('review.json' if group == 'review' else 'report.json')
    report = json.loads(primary.read_text(encoding='utf-8'))
    required = set()
    if group == 'lint':
        assert report['complete'] and report['errors'] == 0
        assert report['all_inputs_unchanged_after_analysis']
        manifest = json.loads((source / 'source-manifest.json').read_text(encoding='utf-8'))
        for path, entry in manifest['inputs'].items():
            assert sha(Path(path)) == entry['sha256'], path
            assert sha(source / entry['snapshot']) == entry['sha256'], entry['snapshot']
            required.add(entry['snapshot'])
        checked[group] = len(required)
    elif group == 'reboot':
        assert all(row['passed'] for row in report['variants'].values())
    elif group != 'review':
        assert report['passed'], group
    if group == 'review':
        assert not report['open_findings']
        for relative, expected in report['final_source_sha256'].items():
            assert sha(root / relative) == expected, (group, relative)
        checked[group] = len(report['final_source_sha256'])
    if group not in {'review', 'lint'}:
        for relative, expected in report.get('source_sha256', {}).items():
            assert sha(root / relative) == expected, (group, relative)
        checked[group] = len(report.get('source_sha256', {}))
    # Review retains its initial snapshot and the final expanded test inputs.
    # Its historical input map is not relabeled as current.
    for file in source.rglob('*'):
        if not file.is_file() or '__pycache__' in file.parts:
            continue
        relative = file.relative_to(source)
        if relative.as_posix() not in required and file.suffix not in allowed and file.name not in {'sdkconfig', '.clang-tidy'}:
            continue
        target = dest / group / relative
        if 'dependency-sources' in relative.parts or len(str(target)) > 230:
            target = dest / 'dependencies' / (sha(file) + (file.suffix or '.txt'))
            relocated[group + '/' + relative.as_posix()] = target.relative_to(dest).as_posix()
        copy(file, target)
    if group == 'lint':
        for relative in required:
            name = group + '/' + relative
            archived = dest / relocated.get(name, name)
            assert archived.is_file() and sha(archived) == sha(source / relative), name
    reports[group] = sha(primary)

copy(root / '.build/c3-ap-lint-triage.json', dest / 'lint-triage.json')
for name in ['run-c3-ap-lint.py', 'run-c3-ap-lint-configure.ps1', 'triage-c3-ap-lint.py', 'archive-c3-ap.py']:
    copy(root / '.build' / name, dest / 'helpers' / name)
(dest / 'archive-paths.json').write_text(json.dumps(relocated, indent=2) + '\n', encoding='utf-8')
(dest / 'qualification.json').write_text(json.dumps(dict(
    passed=True, implementation_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
    reports=reports, current_source_hashes_verified=checked,
    dependency_paths='archive-paths.json maps every relocated original path to a short raw content-addressed file; all 758 lint manifest inputs are included and verified.',
    physical_hardware=False, thread_sanitizer_qualified=False,
    scope='C3 AP timeout repair host/sanitizer/full Clang AST qualification. Exact selected network bodies and complete settings/NVS unit execute together. Activity/reboot/power internals are explicit seams in the AP suite; actual reboot and shared power have separate suites. SDK application export and physical RF/DHCP/AP/reboot/OTA-resource gates are separate.'
), indent=2) + '\n', encoding='utf-8')
print('Archived', len(reports), 'qualified groups and', sum(p.is_file() for p in dest.rglob('*')), 'raw evidence files')
