"""Preserve N4 frozen evidence with short, content-addressed dependency paths."""
from pathlib import Path
import hashlib
import json
import shutil

root = Path(__file__).resolve().parents[1]
dest = root / 'tests/results/network-power-transfer-20261019'
groups = {
    'historical': 'network-power-baseline-probe-02',
    'policy-c3-owner': 'network-power-qualified-01',
    'cyd-owner': 'cyd-network-power-owner-qualified-02',
    'http': 'cyd-network-power-http-qualified-01',
    'websocket': 'cyd-network-power-ws-qualified-01',
    'audio-controls-receive': 'audio-power-controls-receive-qualified-01',
    'maintenance-c3': 'audio-power-c3-maintenance-qualified-01',
    'maintenance-cyd': 'audio-power-cyd-maintenance-qualified-final',
    'commands-c3': 'audio-power-c3-commands-probe-01',
    'receive-c3': 'audio-power-c3-receive-probe-03',
    'receive-growth-c3': 'audio-power-c3-receive-growth-qualified',
    'supplements': 'audio-power-supplements-qualified',
    'settings-precursor': 'cyd-network-settings-qualified-02',
    'lint-cyd': 'lint-cyd-network-power-final',
    'lint-c3': 'lint-c3-network-power-final',
    'review': 'network-power-code-review-01',
}
allowed = {'.c', '.cpp', '.h', '.hpp', '.inc', '.py', '.ps1', '.js', '.json', '.log',
           '.md', '.yaml', '.d', '.txt', '.cmake', '.defaults', '.projbuild'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest.mkdir(parents=True, exist_ok=True)
reports = {}; checked = {}; relocated = {}
def copy(file, target):
    if target.exists():
        assert target.read_bytes() == file.read_bytes(), ('existing archive differs', target)
    else:
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(file, target)

for group, name in groups.items():
    source = root / '.build' / name
    primary = source / ('review.json' if group == 'review' else 'report.json')
    report = json.loads(primary.read_text(encoding='utf-8'))
    if group.startswith('lint-'):
        assert report['complete'] and report['errors'] == 0 and report['all_inputs_unchanged_after_analysis'], group
    elif group != 'review':
        assert report['passed'], group
    for file in source.rglob('*'):
        if not file.is_file() or '__pycache__' in file.parts:
            continue
        if file.suffix not in allowed and file.name not in {'sdkconfig', '.clang-tidy'}:
            continue
        relative = file.relative_to(source)
        target = dest / group / relative
        if 'dependency-sources' in relative.parts or len(str(target)) > 230:
            target = dest / 'dependencies' / (sha(file) + (file.suffix or '.txt'))
            relocated[group + '/' + relative.as_posix()] = target.relative_to(dest).as_posix()
        copy(file, target)
    reports[group] = sha(primary)
    verified = 0
    for relative, expected in report.get('source_sha256', {}).items():
        # Historical race controls deliberately compile exact earlier Git bytes.
        if group == 'historical':
            continue
        assert sha(root / relative) == expected, (group, relative)
        verified += 1
    checked[group] = verified

for name in ['network-power-lint-triage.json']:
    copy(root / '.build' / name, dest / name)
sdk = dest / 'sdk'
for board, project, log in [('cyd', 'esp32-cyd2usb-native', 'network-power-sdk-cyd-qualified'),
                             ('c3', 'esp32c3-oled-native', 'network-power-sdk-c3-final')]:
    for suffix in ['out.log', 'err.log']:
        copy(root / '.build' / (log + '.' + suffix), sdk / board / ('component.' + suffix))
    build = root / 'idf' / project / 'build-c3-transfer'
    for name in ['sdkconfig', 'config/sdkconfig.json', 'config/sdkconfig.h']:
        copy(build / name, sdk / board / name)

(dest / 'archive-paths.json').write_text(json.dumps(relocated, indent=2) + '\n', encoding='utf-8')
(dest / 'qualification.json').write_text(json.dumps({
    'passed': True, 'reports': reports, 'current_source_hashes_verified': checked,
    'source_commit': 'bde1e645',
    'dependency_paths': 'archive-paths.json maps original lint snapshot paths to short content-addressed raw files; reports and source manifests remain unchanged.',
    'sdk_scope': 'Pinned GCC component compilation. Source and dependency bytes are frozen independently by host/AST campaigns; SDK configurations/logs collected after component builds. Application exports recorded separately.',
    'physical_hardware': False, 'thread_sanitizer_qualified': False,
    'settings_status': 'N5 persistence precursor only, runtime/WebUI integration pending.',
}, indent=2) + '\n', encoding='utf-8')
print('Archived', sum(p.is_file() for p in dest.rglob('*')), 'raw files; dependency paths shortened')
