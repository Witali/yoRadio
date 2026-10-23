"""Archive the qualified network slice without test binaries or live credentials."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'tests/results/cyd-network-runtime-20261019'
GROUPS = {
    'historical-baseline': 'network-runtime-baseline-qualified-03',
    'profiles': 'cyd-network-profiles-qualified-02',
    'netif': 'cyd-network-netif-qualified-02',
    'owner': 'cyd-network-runtime-qualified-02',
    'http': 'cyd-network-http-probe-02',
    'websocket': 'cyd-network-ws-probe-02',
    'static-page': 'cyd-network-static-final-01',
    'persistence': 'cyd-network-storage-current-final',
    'physical-row-reader': 'cyd-network-reader-current-final',
    'startup-time-affinity': 'cyd-network-facade-current-final',
}
EXTENSIONS = {'.c', '.cpp', '.h', '.inc', '.py', '.ps1', '.js', '.json', '.log', '.md'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
DEST.mkdir(parents=True, exist_ok=True)
reports = {}
verified = {}
generated_config_changes = {}
for group, name in GROUPS.items():
    source = ROOT / '.build' / name
    report = json.loads((source / 'report.json').read_text(encoding='utf-8'))
    assert report['passed'], name
    for file in source.rglob('*'):
        if not file.is_file() or file.suffix not in EXTENSIONS or '__pycache__' in file.parts:
            continue
        target = DEST / group / file.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
    reports[group] = sha(source / 'report.json')
    checked = 0
    for relative, expected in report.get('source_sha256', {}).items():
        frozen = DEST / group / 'sources' / relative
        if group == 'historical-baseline' and relative.startswith('idf/'):
            # Exact historical Git bytes are already frozen by that runner.
            assert sha(frozen) == expected, (group, 'historical', relative)
            continue
        live = ROOT / relative
        if '/build-c3-transfer/config/' in relative:
            assert sha(frozen) == expected, (group, 'original generated config', relative)
            if sha(live) != expected:
                generated_config_changes[group] = {'original_sha256': expected, 'current_sha256': sha(live), 'path': relative}
            continue
        assert sha(live) == expected, (group, relative)
        if frozen.exists():
            assert sha(frozen) == expected, (group, 'frozen', relative)
        else:
            frozen.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(live, frozen)
        checked += 1
    verified[group] = checked

sdk = DEST / 'sdk'; sdk.mkdir(exist_ok=True)
for name in ['cyd-network-sdk.out.log', 'cyd-network-sdk.err.log', 'run-cyd-network-sdk.ps1']:
    shutil.copyfile(ROOT / '.build' / name, sdk / name)
build = ROOT / 'idf/esp32-cyd2usb-native/build-c3-transfer'
for name in ['sdkconfig', 'config/sdkconfig.h', 'config/sdkconfig.json']:
    target = sdk / name; target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(build / name, target)
production = [p for p in (ROOT / 'idf/esp32-cyd2usb-native/main').iterdir()
              if p.suffix in {'.c', '.cpp', '.h'} or p.name in {'CMakeLists.txt', 'Kconfig.projbuild'}]
for file in production:
    target = sdk / 'sources' / file.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(file, target)
commands = json.loads((build / 'compile_commands.json').read_text(encoding='utf-8'))
selected = [row for row in commands if '/main/' in row['file'].replace('\\', '/')
            and 'esp32-cyd2usb-native' in row['file'].replace('\\', '/')]
(sdk / 'compile_commands.json').write_text(json.dumps(selected, indent=2) + '\n', encoding='utf-8')
(DEST / 'qualification.json').write_text(json.dumps({
    'passed': True,
    'source_commit': 'b736d38f',
    'reports': reports,
    'current_input_hashes_verified': verified,
    'generated_config_changes_since_host_campaign': generated_config_changes,
    'sdk_scope': 'Pinned Xtensa GCC main component compilation. Incremental log records final web_service rebuild; other units were compiled earlier in this campaign. SDK snapshots collected after compilation, not a frozen pre-build reconstruction. No application export, QEMU, RF or hardware claim.',
    'physical_hardware': False,
    'thread_sanitizer': 'Unavailable: independent race-free control failed at runtime startup; see owner report/logs.',
}, indent=2) + '\n', encoding='utf-8')
print('Archived', sum(p.is_file() for p in DEST.rglob('*')), 'files; current frozen inputs verified')
