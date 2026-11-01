from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
names = ['pdm-01', 'disabled-pdm-01', 'gpio25-pdm-01', 'gpio25-disabled-pdm-01']
cache = {}
result = {'passed': True, 'captures': {}, 'full_boot_qualified': False,
          'physical_device': False, 'static_rx_loan_exercised': False}
for name in names:
    directory = ROOT / ('.build/cyd-production-boot-replay-20261030-' + name)
    report_path = directory / 'report.json'
    report = json.loads(report_path.read_text('utf-8'))
    mismatches = []
    for label, binding in report['bindings'].items():
        source = Path(binding['path'])
        key = str(source.resolve())
        if key not in cache:
            cache[key] = (sha(source), source.stat().st_size)
        if cache[key] != (binding['sha256'], binding['bytes']):
            mismatches.append(label)
    flash = directory / 'qemu-flash.bin'
    checks = {'all_current_bound_files_match': not mismatches,
        'flash_matches_original': sha(flash) == report['facts']['original_flash_sha256'],
        'console_matches_report': sha(directory / 'qemu.log') == report['qemu_log_sha256'],
        'terminal_nonpass_preserved': report['completed'] and not report['passed'],
        'old_flash_boundary_passed': report['old_flash_boundary_passed'],
        'early_mpi_return_log_observed': report['early_mpi_return_log_observed'],
        'no_static_rx_loan_claim': report['static_rx_loan_exercised'] is False}
    result['captures'][name] = {'report_sha256': sha(report_path),
        'bound_file_count': len(report['bindings']), 'checks': checks,
        'changed_labels': mismatches, 'qemu_status': report['qemu_exit_status'],
        'reason': report['reason'], 'emulated_input_delay_ns': report['facts'].get('emulated_input_delay_ns', 0)}
    result['passed'] &= all(checks.values())
result['unique_current_sources_checked'] = len(cache)
result['canonical_default_runner_sha256'] = sha(ROOT / 'tests/run-cyd-production-boot-replay.py')
assert result['canonical_default_runner_sha256'] == '0da3d484d7d7ed3becb5e2764a4d47780e779dccdae4f23984fff144a2068be0'
destination = ROOT / '.build/cyd-production-boot-replay-20261030-post-bindings-01.json'
assert not destination.exists()
destination.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result))
raise SystemExit(0 if result['passed'] else 1)
