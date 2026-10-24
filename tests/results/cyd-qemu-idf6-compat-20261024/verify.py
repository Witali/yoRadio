"""Verify saved evidence bytes and report consistency; does not execute QEMU."""
import hashlib
import json
from pathlib import Path
import sys


def need(value, message):
    if not value:
        raise RuntimeError(message)


root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
manifest = json.loads((root / 'manifest.json').read_bytes())
names = set()
for row in manifest['files']:
    relative = Path(row['path'])
    need(not relative.is_absolute() and '..' not in relative.parts, 'Relative artifact path')
    need(row['path'] not in names, 'Unique artifact path')
    names.add(row['path'])
    raw = (root / relative).read_bytes()
    need(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'],
         'Artifact identity: ' + row['path'])
actual = {x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file()}
need(actual == names | {'manifest.json'}, 'Exact artifact membership')


def read(group, name):
    return json.loads((root / 'evidence' / group / name).read_bytes())


for group, count, failures in [
        ('cyd-qemu-idf6-baseline-mmio-02', 187, 49),
        ('cyd-qemu-idf6-patched-mmio-01', 187, 0),
        ('cyd-qemu-idf6-sr2-control-mmio-01', 200, 7),
        ('cyd-qemu-idf6-patched-mmio-02', 200, 0),
        ('cyd-qemu-idf6-subbyte-control-mmio-01', 274, 73),
        ('cyd-qemu-idf6-patched-mmio-03', 274, 0),
        ('cyd-qemu-input-delay-control-01', 386, 24),
        ('cyd-qemu-input-delay-control-02', 391, 24),
        ('cyd-qemu-idf6-final-mmio-01', 274, 0),
        ('cyd-qemu-input-delay-0-01', 391, 0),
        ('cyd-qemu-input-delay-25-01', 391, 0)]:
    report = read(group, 'report.json')
    checks = report['checks']
    need(len(checks) == count, 'Complete MMIO matrix')
    need(all(x['passed'] == (x['actual'] == x['expected']) for x in checks),
         'MMIO comparison consistency')
    need(sum(not x['passed'] for x in checks) == failures, 'Control/fixed MMIO result')
    need(report['result'] == ('MMIO_REGRESSIONS_FAILED' if failures else
                              'MMIO_REGRESSIONS_COMPLETED'), 'MMIO result classification')
    need(report['case_execution_completed'] and report['inputs_unchanged']
         and report['stdout_actual_eof'] and report['stdout_reader_joined']
         and not report['controller_errors'] and report['error'] is None
         and report['cleanup_method'] == 'terminate-owned-paused-qtest-process',
         'MMIO lifecycle and preservation')

for group in ('cyd-qemu-idf6-baseline-peripherals-01', 'cyd-qemu-idf6-patched-peripherals-01',
              'cyd-qemu-idf6-final-peripherals-0-01', 'cyd-qemu-idf6-final-peripherals-25-01'):
    report = read(group, 'owned-report.json')
    need(report['result'] == 'CLASSIC_PERIPHERAL_REGRESSIONS_COMPLETED'
         and not report['errors'] and report['inputs_unchanged'], 'Peripheral result')
    need(len(report['owned_children']) == 2 and all(
         x['returncode'] == 0 and not x['forced'] for x in report['owned_children']),
         'Two completed owned peripheral children')
    saved = read(group, 'modular-report.json')
    need(saved == report['peripheral_report'] and saved['passed'] and saved['soc'] == 'esp32',
         'Saved peripheral report consistency')
    need(set(saved['checks']) == {'esp32_dual_spi', 'legacy_cyd_mmio'}, 'Classic ESP32 groups')
    need(all(value is True or (name == 'topology' and value == 'two_hosts')
             for checks in saved['checks'].values() for name, value in checks.items()),
         'Peripheral assertions retained')

boot = read('cyd-qemu-production-observation-20261024-06', 'report.json')
need(boot['result'] == 'OBSERVATION_COMPLETED' and boot['actual_qemu_exit_code'] == 0
     and boot['all_selected_inputs_unchanged'] and boot['scratch_flash_unchanged']
     and not boot['cleanup_errors'] and boot['qmp_reader']['actual_eof']
     and boot['qmp_reader']['joined'] and boot['qmp_reader']['error'] is None
     and not boot['qmp_reader']['controller_closed_stdout'], 'Completed boot observation')
need(boot['firmware_patched'] is False and boot['emulator_model_patched'] is True
     and boot['full_radio_startup_qualified'] is False
     and boot['physical_qualification'] is False, 'Honest observation scope')
need(boot['emulated_spi_input_delay_ns'] == 25 and boot['fixed_flash_source_clock_hz'] == 80000000,
     'Explicit functional input path assumption')
uart = (root / 'evidence/cyd-qemu-production-observation-20261024-06/uart.log').read_text(encoding='utf-8')
need('SPIFFS mount failed' not in uart and 'EXCVADDR: 0x60033c00' in uart
     and 'LoadStorePIFAddrError' in uart and boot['panic_observed'],
     'Saved observation remains a partial RF failure')
print(json.dumps(dict(artifact_integrity_verified=True, artifact_files=len(names),
                     baseline_mmio_failures=49, fixed_mmio_passed=274,
                     input_delay_checks_each=391, tested_input_delays_ns=[0, 25],
                     classic_peripheral_groups_each=2, boot_observation=boot['result'],
                     boot_markers=boot['markers'], panic_observed=boot['panic_observed'],
                     startup_error_observed=boot['startup_error_observed'],
                     full_radio_or_physical_qualified=False), indent=2))
