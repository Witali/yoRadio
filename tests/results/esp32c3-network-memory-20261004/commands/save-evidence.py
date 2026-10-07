import hashlib, json, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, 'tools/esp32c3_tests')
from network_memory import inspect as network_inspect
from summarize_public_windows import inspect as cpu_inspect
root = Path.cwd()
base = root/'.build/aac-network-memory'
out = root/'tests/results/esp32c3-network-memory-20261004'
out.mkdir(parents=True, exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
for name in ('baseline-http32', 'ota-transition', 'candidate-http32', 'candidate-https64'):
    target = out/name
    target.mkdir(exist_ok=True)
    for p in (base/name).glob('*.json'):
        copy(p, target/p.name)
    if name != 'ota-transition':
        for filename, data in [('network-summary.json', network_inspect(target)), ('summary.json', cpu_inspect(target))]:
            (target/filename).write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8', newline='\n')
for name in ('build-verification.json', 'build-first-failure.log', 'build-aac-network-memory.log', 'public-exits.json', 'final-board.json'):
    copy(base/name, out/name)
for p in (base/'host').glob('*.log'):
    copy(p, out/'host'/p.name)
copy(root/'.build/wifi-signal-check-20261004-103855.json', out/'wifi-signal-check.json')
copy(root/'idf/esp32c3-oled-native/build-aac-network-memory/esp-idf/main/compact5/audit.json', out/'physical-patch-audit.json')
copy(root/'.build/aac-asymmetric-production/network-allocation-audit.json', out/'network-allocation-audit.json')
paths = [root/p for p in (
    'idf/esp32c3-oled-native/main/CMakeLists.txt', 'idf/esp32c3-oled-native/main/Kconfig.projbuild',
    'idf/esp32c3-oled-native/main/cpu_profiler.c', 'idf/esp32c3-oled-native/main/network_heap_profile.c',
    'idf/esp32c3-oled-native/main/network_heap_profile.h', 'tests/native/network_heap_profile_test.c',
    'tests/test-esp32c3-network-memory.py', 'tests/test-network-heap-native.py',
    'tests/test-network-memory-evidence.py')]
paths += sorted((root/'tests/native/network_heap_profile_stubs').rglob('*.h'))
paths += sorted((root/'tools/esp32c3_tests').glob('*.py'))
paths += sorted((root/'tools/audio_test_server').glob('*.py'))
for p in paths:
    copy(p, out/'sources'/p.relative_to(root))
for name in ('build.py', 'save-firmware.py', 'run-public.py', 'save-evidence.py'):
    copy(base/name, out/'commands'/name)
sdk = Path('C:/Work/yoRadio/.idf/v6.0.2')
sdk_files = ['components/lwip/lwip/src/api/tcpip.c', 'components/lwip/lwip/src/include/lwip/priv/tcp_priv.h',
             'components/lwip/lwip/src/include/lwip/tcpip.h']
manifest = dict(base_commit='cb651dad2030214776bba22526ac67530ee320c0',
    diagnostic_commit='925ecf56',
    source_note='Exact modified firmware sources and runner snapshots retained; unchanged files are from base_commit.',
    sdk_files_sha256={n:sha(sdk/n) for n in sdk_files},
    firmware='firmware/development/esp32c3-aac-network-memory/manifest.json',
    note='Original acceptance gates and failures retained; snapshots do not cover all network allocation owners.')
(out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
checksums = {str(p.relative_to(out)).replace('\\','/'):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'checksums.json'}
(out/'checksums.json').write_text(json.dumps(checksums, indent=2)+'\n', encoding='utf-8', newline='\n')
print('Saved', len(checksums), 'evidence files')
