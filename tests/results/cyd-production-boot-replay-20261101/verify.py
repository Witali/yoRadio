"""Read-only checks of the partial saved boot checkpoint; execute no archived code."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MANIFEST_SHA = '93713d82fce619ee50b8db9a478ba6334c283b8a81a5c2c9a3bc306d3aebd033'
VOLUME_SHA = 'e92e0bab990144ad683306fc59b60cb510656f96dff6f13952332cc7ca8ed027'
QEMU_SHA = '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def report(name):
    return json.loads((HERE / 'evidence' / name).read_bytes())


def main():
    body = (HERE / 'manifest.json').read_bytes()
    need(sha(body) == MANIFEST_SHA, 'pinned immutable capture manifest')
    manifest = json.loads(body)
    need(not manifest['production_startup_qualified'] and
         not manifest['physical_hardware_used'], 'partial checkpoint scope')
    paths = set()
    for row in manifest['files']:
        relative = Path(row['path'])
        path = (HERE / relative).resolve()
        need(path.is_relative_to(HERE) and row['path'] not in paths, 'unique contained paths')
        paths.add(row['path'])
        payload = path.read_bytes()
        need(len(payload) == row['bytes'] and sha(payload) == row['sha256'], 'exact original captured bytes')
        need(path.suffix in ('.py', '.json', '.log'), 'published text evidence only')
        need(not payload.startswith((b'\x7fELF', b'MZ')), 'no executable payload')
    actual = {path.relative_to(HERE).as_posix() for path in (HERE / 'evidence').rglob('*') if path.is_file()}
    need(actual == paths, 'no extra archived payload')
    need((HERE / 'evidence/default-runner.py').read_bytes() ==
         (ROOT / manifest['canonical_runner']).read_bytes(), 'canonical default runner matches capture')

    ordinary = {}
    gpio = {}
    for profile in ('pdm', 'disabled-pdm'):
        for prefix, selected in (('', ordinary), ('gpio25-', gpio)):
            capture = prefix + profile + '-01'
            r = report(capture + '/report.json')
            log = (HERE / 'evidence' / capture / 'qemu.log').read_bytes()
            need(r['completed'] and not r['passed'] and not r['startup_subset_passed'], 'preserved terminal nonpass')
            need(sha(log) == r['qemu_log_sha256'], 'original terminal log hash')
            need(r['all_bound_inputs_current'] and not r['changed_bound_input_labels'] and
                 r['flash_unchanged_after_snapshot'], 'unchanged bound inputs and original flash')
            need(r['old_flash_boundary_passed'] and r['early_mpi_return_log_observed'], 'genuine app main markers')
            need(r['facts']['replay_qemu_sha256'] == QEMU_SHA and
                 r['facts']['static_rx_config_enabled'] == (profile == 'pdm'), 'exact emulator and paired reserve config')
            need(not any(r[key] for key in ('firmware_or_config_patched', 'source_rebuilt',
                'physical_device', 'external_network', 'static_rx_loan_exercised',
                'full_radio_startup_qualified', 'audio_playback_qualified')), 'limited unmodified offline observation')
            for pin in r['bindings'].values():
                need(len(pin['sha256']) == 64 and pin['bytes'] > 0, 'complete exact input identities')
            if prefix:
                need(len(r['bindings']) == 51 and r['panic_observed'] and r['qemu_exit_status'] == 0,
                     'genuine panic can terminate QEMU with zero status')
                need(r['facts']['emulated_input_delay_ns'] == 25 and
                     not r['facts']['physical_delay_calibration_claimed'], 'explicit SDK-derived matrix receive profile')
                need(b'LoadStorePIFAddrError' in log and b'0x60033c00' in log and
                     b'ST7789: SPI2 DMA' in log and b'SPIFFS mount failed' not in log,
                     'display reached before actual PHY exception')
            else:
                need(len(r['bindings']) == 48 and r['startup_error_observed'] and
                     r['qemu_exit_status'] == 1 and b'SPIFFS: mount failed, -10025' in log,
                     'ordinary profile original SPIFFS failure retained')
            selected[profile] = r

    audit = report('cyd-production-boot-replay-20261030-filesystem-audit-01.json')
    for profile in ('pdm', 'disabled-pdm'):
        volume = audit['profiles'][profile]
        need(volume['spiffs_bytes'] == 589824 and volume['spiffs_sha256'] == VOLUME_SHA and
             volume['image_contains_exact_spiffs_bytes'], 'original volume present in each image')
        need(volume['block_count'] == volume['valid_magic_blocks'] == 144 and
             all(row['matches'] for row in volume['block_magic_checks']), 'all original block magic values match SDK')

    partial = report('spiffs-readback-01/report.json')
    need(not partial['passed'] and not partial['completed'] and
         partial['error'] == 'MMIO fixture deadline' and
         partial['full_read_chunks_completed'] == 2447 and len(partial['checks']) == 1154 and
         all(row['passed'] for row in partial['checks']), 'incomplete scalar campaign retained as nonpass')
    full = report('spiffs-readback-02/report.json')
    need(full['passed'] and full['completed'] and full['inputs_unchanged'] and
         full['inputs_before'] == full['inputs_after'], 'complete stopped-CPU readback and input identity')
    need(full['full_read_chunks_completed'] == 9216 and full['complete_readback_bytes'] == 589824 and
         full['complete_readback_sha256'] == full['source_volume_sha256'] == VOLUME_SHA and
         full['all_spiffs_bytes_equal'], 'complete readback hash observation')
    need(len(full['scalar_batch_checks']) == 16 and all(row['passed'] and
         row['scalar_sha256'] == row['batch_sha256'] == row['expected_sha256']
         for row in full['scalar_batch_checks']), 'scalar versus batched equivalence observations')
    need(not any(full[key] for key in ('guest_cpus_resumed', 'production_firmware_executed',
         'data_volume_substituted', 'application_or_config_modified', 'physical_device', 'external_network')),
         'readback is not a successful production boot')
    need(full['stdout_actual_eof'] and full['stdout_reader_joined'] and
         not full['controller_errors'] and full['qemu_exit_status'] == 1, 'owned readback process cleaned up')
    omitted = {(row['local_capture'], row['path']): row for row in manifest['omitted_local_payloads']}
    readback = omitted[('cyd-production-boot-replay-20261030-spiffs-readback-02', 'spiffs-readback.bin')]
    need(readback['bytes'] == 589824 and readback['sha256'] == VOLUME_SHA, 'omitted raw readback identity')

    symbols = report('symbolication-01/report.json')
    for profile in ('pdm', 'disabled-pdm'):
        result = symbols['profiles'][profile]
        need(result['capture_report_sha256'] == sha((HERE / 'evidence' / result['capture'].removeprefix(
             'cyd-production-boot-replay-20261030-') / 'report.json').read_bytes()), 'symbolication exact source capture')
        need(result['elf_sha256'] == gpio[profile]['facts']['elf_sha256'] and
             result['native_status'] == 0 and result['panic_type'] == 'LoadStorePIFAddrError' and
             result['fault_address'] == '0x60033c00' and
             result['function_names'][0] == 'register_chipv7_phy', 'symbolicated unchanged ELF and genuine PHY failure')

    print(json.dumps(dict(checkpoint_verified=True, original_captures=4,
        preserved_files=len(paths), omitted_local_files=len(omitted),
        full_production_boot_passed=False, executes_archived_code=False,
        omitted_payload_bytes_read=False)))


if __name__ == '__main__':
    main()
