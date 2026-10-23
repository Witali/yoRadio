"""Read back final canonical host/config/service evidence without rerunning tests."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent.parent
out = root / '.build/cyd-static-rx-host-root-audit-01.json'
assert not out.exists()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
applied = json.loads((root / '.build/cyd-static-rx-tests-applied-01.json').read_bytes())
assert len(applied['source_files']) == 34
for name, digest in applied['source_files'].items():
    assert sha((root / name).read_bytes()) == digest, name
gates = {}
for name, folder, owner in [('unit', 'rxu01', 86428), ('config', 'rxc01', 21895), ('service', 'rxs01', 79183)]:
    base = root / '.build' / folder
    raw = (base / 'report.json').read_bytes()
    report = json.loads(raw)
    assert report['passed'] is True
    for path, row in report['inputs'].items():
        assert sha(Path(path).read_bytes()) == row['sha256'], path
        assert sha((base / row['snapshot']).read_bytes()) == row['sha256'], row['snapshot']
    for command in report.get('commands', []):
        assert type(command['exit_status']) is int, command['label']
        assert sha((base / (command['label'] + '.log')).read_bytes()) == command['log_sha256']
    contract = report['module_contract']
    assert contract['normalized_lf_sha256'] == '17e98a29cadd0387d9db725d50c12514847426cd9cfa607abf5224884fe17555'
    assert contract['userdata_api_used'] is False and contract['integer_identity_keys'] is True
    if name == 'unit':
        assert len(report['positive_cases']) == 8 and len(report['controls']) == 9 and len(report['compile_rejections']) == 14
        restored = [row for row in report['commands'] if row['label'].startswith('restored-')]
        assert len(restored) == 8 and all(row['exit_status'] == 0 for row in restored)
        assert report['tools_before'] == report['tools_after']
        assert all(row['exit_status'] == 2 for row in report['controls'].values())
        assert all(type(row['exit_status']) is int and row['exit_status'] != 0 for row in report['compile_rejections'].values())
        detail = {'positive_groups': 8, 'exact_named_controls': 9, 'compile_rejections': 14, 'restored_groups': 8}
    elif name == 'config':
        assert len(report['cases']) == report['configure_case_count'] == 45
        assert sum(name.startswith('guard-') for name in report['cases']) == 19
        assert all(row['passed'] is True for row in report['cases'].values())
        for case, row in report['cases'].items():
            assert sha((base / case / 'configure.log').read_bytes()) == row['log_sha256']
        for path, digest in report['tools'].items():
            assert sha(Path(path).read_bytes()) == digest
        detail = {'configure_cases': 45, 'supporting_guard_mutations': 19, 'compiler': False}
    else:
        assert len(report['variants']) == 12 and len(report['controls']) == 2 and not report['quick']
        assert sum(map(len, report['variants'].values())) == 536
        expected = {f'r{reserve}-q{reclaim}-{backend}' for reserve in (0, 1) for reclaim in (0, 1) for backend in ('pdm', 'dac', 'legacy_dac')}
        assert set(report['variants']) == expected
        assert all(row['exit_status'] == 0 for cases in report['variants'].values() for row in cases.values())
        assert all(row['exit_status'] == 2 for row in report['controls'].values())
        assert report['tools_before'] == report['tools_after']
        for relative, digest in report['generated'].items():
            assert sha((base / relative).read_bytes()) == digest, relative
        detail = {'option_backend_variants': 12, 'scenario_executions': 536, 'exact_binding_controls': 2}
    gates[name] = {'owner_session': owner, 'root_observed_terminal_exit': 0, 'report': str(base / 'report.json'), 'report_sha256': sha(raw), 'readback_passed': True, **detail}
out.write_text(json.dumps({'passed': True, 'canonical_files_unchanged': 34, 'gates': gates,
    'scope': 'Readback of completed host/config evidence; no new test run; no actual SDK/QEMU/physical claim'}, indent=2) + '\n', encoding='utf-8')
print(json.dumps(gates, indent=2))
