"""Archive current N5 evidence; retain immutable reports and short raw dependencies."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
dest = root / 'tests/results/cyd-network-settings-20261020'
groups = {
    'owner': 'n5-runtime-final-03',
    'http': 'n5-http-02',
    'page': 'n5-page-02',
    'reboot': 'n5-reboot-leases-02',
    'persistence': 'n5-settings-persistence-01',
    'startup': 'n5-startup-02',
    'web-start': 'n5-web-start-final-03',
    'network-http': 'n5-network-http-regression-01',
    'websocket': 'n5-websocket-regression-01',
    'lint': 'lint-cyd-network-n5-01',
    'review': 'n5-independent-review-01',
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
        assert not report['final_open_findings']
        for relative, expected in report['final_source_sha256'].items():
            assert sha(root / relative) == expected, (group, relative)
        checked[group] = len(report['final_source_sha256'])
    if group not in {'review', 'lint'}:
        for relative, expected in report.get('source_sha256', {}).items():
            assert sha(root / relative) == expected, (group, relative)
        checked[group] = len(report.get('source_sha256', {}))
    # Review deliberately preserves the historical failing page and its final
    # repaired version. Its original input map is not relabeled as current.
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

copy(root / '.build/n5-lint-triage.json', dest / 'lint-triage.json')
for name in ['run-n5-lint.py', 'run-n5-lint-configure.ps1', 'triage-n5-lint.py', 'archive-n5.py']:
    copy(root / '.build' / name, dest / 'helpers' / name)
(dest / 'archive-paths.json').write_text(json.dumps(relocated, indent=2) + '\n', encoding='utf-8')
(dest / 'qualification.json').write_text(json.dumps(dict(
    passed=True, implementation_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
    reports=reports, current_source_hashes_verified=checked,
    dependency_paths='archive-paths.json maps every relocated original path to a short raw content-addressed file; all 652 lint manifest inputs are included and verified.',
    physical_hardware=False, thread_sanitizer_qualified=False,
    scope='N5 software integration host/sanitizer/full Clang AST qualification. Settings/NVS+HTTP execute together; owner uses coherent settings API and reboot seams, whose implementations are separately qualified. SDK application exports and physical RF/DHCP/AP/reboot/OTA-resource gates are separate.'
), indent=2) + '\n', encoding='utf-8')
print('Archived', len(reports), 'qualified groups and', sum(p.is_file() for p in dest.rglob('*')), 'raw evidence files')
