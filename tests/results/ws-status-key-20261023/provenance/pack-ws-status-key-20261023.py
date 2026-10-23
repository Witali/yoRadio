"""Preserve completed WS comparison regressions, focused target checks and history."""
import hashlib
import json
from pathlib import Path
import shutil
import struct

repo = Path(__file__).resolve().parents[1]
out = repo / 'tests/results/ws-status-key-20261023'
assert not out.exists()
out.mkdir()


def fact(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def copy(path, relative):
    destination = out / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    assert not destination.exists()
    shutil.copyfile(path, destination)
    assert path.read_bytes() == destination.read_bytes()


groups = {
    'cyd-before-initial': '.build/ws-status-key-cyd-before-01',
    'cyd-before-final': '.build/ws-status-key-cyd-before-02',
    'cyd-after': '.build/ws-status-key-cyd-after-01',
    'c3-before': '.build/c3-ws-status-padding-before-01',
    'c3-after': '.build/c3-ws-status-key-after-01',
    **{'target-' + str(i): '.build/ws-status-key-target-0' + str(i) for i in range(1, 5)},
}
extensions = {'.c', '.h', '.inc', '.py', '.json', '.log', '.yaml', '.d'}
for group, origin in groups.items():
    root = repo / origin
    assert root.is_dir()
    for path in sorted(root.rglob('*')):
        assert not path.is_symlink()
        if path.is_file() and (path.suffix in extensions or path.name in ('cflags', 'picolibc.specs')):
            copy(path, Path(group) / path.relative_to(root))
for i in range(1, 5):
    copy(repo / ('.build/run-ws-status-key-target-0' + str(i) + '.py'),
         'provenance/run-ws-status-key-target-0' + str(i) + '.py')
copy(Path(__file__), 'provenance/pack-ws-status-key-20261023.py')

target = json.loads((out / 'target-4/report.json').read_bytes())
assert target['passed'] and not target['full_app_configured_or_built']
commands = json.loads((out / 'target-4/commands.json').read_bytes())
assert len(commands) == 8 and all(r['returncode'] == 0 for r in commands.values())
objects = {}
warning_review = {}
for board, machine in [('cyd', 94), ('c3', 243)]:
    path = repo / groups['target-4'] / (board + '-websocket_service.o')
    raw = path.read_bytes()
    assert raw[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<HH', raw, 16) == (1, machine)
    assert fact(path) == target['profiles'][board]['analyses']['gcc']['object']
    objects[board] = {**fact(path), 'ELF_class': 32, 'relocatable': True, 'machine': machine,
                      'first_64_bytes_hex': raw[:64].hex(), 'body_omitted': True}
    oldpath = repo / ('.build/lint-cyd-input-reclaim-01/report.json' if board == 'cyd'
                     else '.build/lint-c3-ap-timeout-01/report.json')
    old = json.loads(oldpath.read_bytes())
    source_name = target['profiles'][board]['source']
    rows = [r for r in old['results'] if r['file'] == source_name]
    assert len(rows) == 1
    before = rows[0]
    after = target['profiles'][board]['analyses']['clang']['diagnostics']
    key = lambda d: (d['file'].replace('\\', '/'), d['check'], d['message'], d['severity'])
    before_set, after_set = {key(d) for d in before['diagnostics']}, {key(d) for d in after}
    assert after_set <= before_set
    assert [r[1] for r in before_set - after_set] == ['bugprone-suspicious-memory-comparison']
    warning_review[board] = {'earlier_report_path': str(oldpath), 'earlier_report_fact': fact(oldpath),
                            'earlier_selected_unit': before, 'current_diagnostics': after,
                            'new_warnings': 0, 'removed_check': 'bugprone-suspicious-memory-comparison'}
    assert fact(repo / source_name) == target['profiles'][board]['source_fact']
    for kind in ('gcc', 'clang'):
        analysis = target['profiles'][board]['analyses'][kind]
        assert analysis['all_inputs_unchanged']
        for name, expected in analysis['inputs'].items():
            assert fact(Path(name)) == expected
(out / 'object-identities.json').write_text(json.dumps(objects, indent=2) + '\n', encoding='utf-8')
(out / 'warning-review.json').write_text(json.dumps(warning_review, indent=2) + '\n', encoding='utf-8')

for group in ('cyd-after', 'c3-after'):
    report = json.loads((out / group / 'report.json').read_bytes())
    assert report['passed']
    for name, expected in report['source_sha256'].items():
        assert fact(repo / name)['sha256'] == expected
        assert fact(out / group / 'sources' / name)['sha256'] == expected
c3 = json.loads((out / 'c3-after/report.json').read_bytes())
assert c3['full_suite'] and len(c3['cases']) == 42 and len(c3['negative_controls']) == 7
assert all(r['passed'] for r in c3['cases'].values())
assert all(r['rejected'] for r in c3['negative_controls'].values())
for name in ('tests/native/cyd_websocket_test.c', 'tests/run-cyd-websocket.py'):
    assert (out / 'cyd-before-final/sources' / name).read_bytes() == (out / 'cyd-after/sources' / name).read_bytes()
for group, filename, assertion in [('cyd-before-final', 'failure.log', b'padding alone must not publish status'),
                                    ('c3-before', 'key_padding.log', b'padding-only changes must not publish status')]:
    raw = (out / group / filename).read_bytes()
    assert assertion in raw and b'runtime error:' not in raw and b'ERROR: AddressSanitizer' not in raw

terminals = {
    'cyd_before_initial': {'chunk': '9aaa3b', 'exit_code': 1, 'expected_logical_assertion': True},
    'cyd_before_final': {'chunk': '16a3f3', 'exit_code': 1, 'expected_logical_assertion': True},
    'cyd_after': {'chunk': 'bf173c', 'exit_code': 0, 'fixture_groups': 59},
    'c3_before': {'chunk': '7ee896', 'exit_code': 1, 'expected_logical_assertion': True},
    'c3_after': {'chunk': '0a775e', 'exit_code': 0, 'session_id': 82406, 'cases': 42, 'semantic_controls': 7},
    'target_1': {'chunk': 'a52b5d', 'exit_code': 1, 'stage': 'wrong compiler-basename preflight; compiler not launched'},
    'target_2': {'chunk': 'a63dcb', 'exit_code': 1, 'stage': 'after successful dependency walk; POSIX shlex removed literal Windows separators'},
    'target_3': {'chunk': '989937', 'exit_code': 0, 'session_id': 89282,
                 'final_input_closure': False, 'limit': 'response/specs not captured; tidy tool not pinned before execution'},
    'target_4': {'chunk': '30224c', 'exit_code': 0, 'session_id': 82221, 'final_input_closure': True},
}
(out / 'root-observations.json').write_text(json.dumps({'scope': 'Human-readable facts from actual root execution tool terminals; not fabricated process receipts.',
    'terminals': terminals, 'peer_review': {'target_4_script_sha256': 'dd49967496a4816f011545a2358cddf8969bd9f103eac90ae605afc7eb7e64c4', 'source_review_only': True},
    'physical_device': False, 'production_firmware_built': False, 'codec_deferrals_unchanged': True}, indent=2) + '\n', encoding='utf-8')
(out / '.gitattributes').write_bytes(b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n')
(out / 'README.md').write_text('''# Portable WebSocket status comparison, 2026-10-23

CYD and C3 now compare each status-key field and logical NUL-terminated string.
Structure padding and bytes after a string terminator no longer trigger redundant
status revisions/publications. Type layouts, capture, heartbeat, work admission,
queue ownership, task affinity and production hardware settings are unchanged.
This is a portability correction (P3), not a reproduced production crash.

| Check | Actual result |
| --- | --- |
| Old CYD/C3 with padding-only changes | Both fail the exact publication assertion |
| Current CYD host | 59 fixture groups, ASan/UBSan; all 18 scalar/4 string changes detected |
| Current C3 host | All 42 status-loop cases + 7 semantic controls, ASan/UBSan |
| Target GCC | Separate ESP32 Xtensa and ESP32-C3 RISC-V objects, zero diagnostics |
| Focused clang-tidy | CYD 1 / C3 2 existing warnings, zero errors or new warnings |

The new tests modify only padding selected by offsetof/member-size masks, then
check real status publication before heartbeat. Every scalar and visible string
is tested separately; logical string tails are tested too. CYD final before/after
use byte-identical harness/runner bytes. C3 full-suite mode retains all earlier
22 cases and seven controls; filtered before mode is explicitly not a full suite.

Both suspicious-memory-comparison warnings disappeared. The remaining diagnostics
are the existing bounded CYD RSSI conversion, C3 command aliases and a diagnostic
dead store. The HTTPD NULL-session trace requires a caller state excluded by the
SDK success/error flow; negative timezone promotion is intentionally signed.
Neither was changed just to reduce the warning count.

target-4 is the final focused target qualification. Its eight actual commands
use existing SDK compilation databases without configuring/building a full app.
It captures each dependency union and verifies captured source/header/config/
database/compiler inputs before/after analysis. Actual response/specs and analyzer
identities are frozen before the dependency walk, then rechecked. CYD remains
SDK6.0.2/240 MHz/SMP; C3 SDK6.1/160 MHz/unicore. The two genuine ELF32 relocatable
headers/machine identities and object hashes are retained; object bodies are omitted.
No linked firmware or physical timing/resource/acoustic result is claimed.

Target attempts 1 and 2 retain their actual preflight failures. Attempt 3 actually
compiled/analyzed both units but lacked complete captured compiler context; it
remains limited history. Attempt 4 includes that context after independent review.
The initial CYD before-run preceded the final added string-tail regression and is
also history; the final before-run matches the successful harness exactly.

Reports, logs, generated host text, frozen project source/header copies and exact
validation scripts are retained. External SDK/toolchain headers and executable
bodies remain recorded hashes, not replayable payloads. The archive verifies its
own bytes, not fresh compilation, full-app qualification or a new sanitizer run.
Reproduce host behavior with tests/run-cyd-websocket.py and
tests/run-c3-websocket-status.py --output FRESH_DIRECTORY from the repository.
The latter's default runs the complete suite.

No physical device, serial/reset/flashing or production firmware export occurred.
Production CYD stream core0 and decode/output core1 remain unchanged. Deferred
codec work is untouched; this correction is an independent WebSocket change.
''', encoding='utf-8', newline='\n')
verifier = '''"""Verify retained WS regression bytes; does not execute test/SDK code."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--manifest-sha256', required=True)
a = p.parse_args()
root = Path(__file__).resolve().parent
manifest = root / 'manifest.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == a.manifest_sha256
data = json.loads(manifest.read_bytes())
actual = {x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file() and x != manifest}
assert actual == set(data['files'])
for name, row in data['files'].items():
    path = (root / name).resolve()
    assert path.is_relative_to(root) and not (root / name).is_symlink()
    raw = path.read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
c3 = json.loads((root / 'c3-after/report.json').read_bytes())
cyd = json.loads((root / 'cyd-after/report.json').read_bytes())
target = json.loads((root / 'target-4/report.json').read_bytes())
assert c3['passed'] and c3['full_suite'] and len(c3['cases']) == 42 and len(c3['negative_controls']) == 7
assert cyd['passed'] and cyd['status_key_comparison']['padding_ignored'] and cyd['status_key_comparison']['string_tails_ignored']
assert target['passed'] and not target['full_app_configured_or_built']
print('PASS retained WS evidence integrity; CYD59/C342+7; focused targets only, no physical qualification')
'''
(out / 'verify.py').write_text(verifier, encoding='utf-8', newline='\n')
manifest = {'scope': 'Exact selected retained text/inventory; runtime facts remain separate actual campaign reports.',
            'files': {p.relative_to(out).as_posix(): fact(p) for p in sorted(out.rglob('*')) if p.is_file()}}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'files': len(manifest['files']) + 1, 'bytes': sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),
                  'manifest_sha256': fact(out / 'manifest.json')['sha256']}))
