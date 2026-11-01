"""Replay unchanged saved CYD PDM production components with the qualified IDF6 QEMU.

No source rebuild, component/header patch, board, COM port, host sound or NIC
is used. This records genuine boot milestones and the next actual failure.
Static TLS loans, radio traffic, audio playback and physical acceptance remain
outside a network-free startup observation, even when all idle markers appear.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / 'tests/results/cyd-production-radio-boot-20261020'
HISTORICAL_INPUTS_SHA = 'f9cf237bbbefe7967abbb558b06beb1ed4617035769669bb770223ad01bf5b12'
SOURCE_COMMIT = '3a563324abdca56144a40d5759def0ccfe708b3c'
QEMU = ROOT / '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
QEMU_SHA = '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d'
QEMU_IDENTITY = QEMU.parent / 'build-identity.json'
LOG_LIMIT = 8 * 1024 * 1024
PANIC = re.compile(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|'
                   r'watchdog.*triggered|LoadProhibited|StoreProhibited', re.I)
STARTUP_ERROR = re.compile(r'NVS init failed|SPIFFS mount failed|Audio service failed|'
    r'Radio control failed|Web server failed|Health sampler initialization failed|'
    r'Time service unavailable|Network settings unavailable|TLS input reclamation not attached', re.I)


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def observations(text, version, expected_elf):
    text = re.sub(r'\x1b\[[0-9;]*m', '', text.replace('\r\n', '\n'))
    elf_match = re.search(r'ELF file SHA256:\s*([a-fA-F0-9]{8,64})', text)
    assert_match = re.search(r'assert failed:\s*([A-Za-z_0-9]+)\s+([A-Za-z_0-9.]+):(\d+)', text)
    markers = dict(
        project_identity=bool(re.search(r'Project name:\s*yoradio_cyd2usb_native(?:\s|$)', text)),
        version_identity=bool(re.search(r'App version:\s*' + re.escape(version) + r'(?:\s|$)', text)),
        elf_identity=bool(elf_match and expected_elf.startswith(elf_match.group(1).lower())),
        sdk_calling_app_main='main_task: Calling app_main()' in text,
        after_early_mpi_log=text.count('Starting pure ESP-IDF yoRadio (Arduino-free)') == 1,
        display_driver_entered='ST7789: SPI2 DMA' in text,
        pipeline_owners_ready='Pipeline ready: I2S PDM,' in text,
        radio_control_entered='Smart Start state: 2' in text,
        web_service_ready=bool(re.search(r'Native HTTPS? server started', text)))
    assertion = None if not assert_match else dict(function=assert_match.group(1), file=assert_match.group(2),
                                                   line=int(assert_match.group(3)))
    return dict(markers=markers, panic_observed=bool(PANIC.search(text)), startup_error_observed=bool(STARTUP_ERROR.search(text)),
                qie_failure_observed='Failed to set QIE bit' in text,
                sdk_flash_assert_observed='__esp_system_init_fn_init_flash' in text,
                network_failure_observed='Network failed:' in text,
                assertion=assertion, old_flash_boundary_passed=markers['sdk_calling_app_main'] or markers['after_early_mpi_log'],
                early_mpi_return_log_observed=markers['after_early_mpi_log'])


def prepare(profile):
    bindings = {}

    def bind(label, path, expected=None):
        path = Path(path).resolve()
        need(path.is_file(), 'required local input exists: ' + label)
        value = file_sha(path)
        need(expected is None or value == expected, 'exact input hash: ' + label)
        bindings[label] = dict(path=str(path), sha256=value, bytes=path.stat().st_size)
        return path

    pins_path = bind('historical_inputs', HISTORY / 'preparation/inputs.json', HISTORICAL_INPUTS_SHA)
    pins = json.loads(pins_path.read_bytes())
    need(pins['source_commit'] == SOURCE_COMMIT, 'original saved production source commit')
    historical_manifest = json.loads((HISTORY / 'manifest.json').read_bytes())
    bind('historical_manifest', HISTORY / 'manifest.json')
    for row in historical_manifest['files']:
        bind('historical:' + row['path'], HISTORY / row['path'], row['sha256'])
    selected = pins['profiles'][profile]
    need(selected['backend'] == 'pdm' and selected['source_commit'] == SOURCE_COMMIT, 'original PDM profile and source')
    for name, pin in selected['files'].items():
        bind('production:' + name, pin['path'], pin['sha256'])
    bind('qemu', QEMU, QEMU_SHA)
    bind('qemu_build_identity', QEMU_IDENTITY)
    identity = json.loads(QEMU_IDENTITY.read_bytes())
    need(identity['result'] == 'ACTUAL_OFFLINE_BUILD_COMPLETED' and identity['qemu']['sha256'] == QEMU_SHA and
         not identity['firmware_modified'] and not identity['source_dependency_closure_claimed'],
         'selected-source emulator build provenance without full dependency closure claim')
    for name, pin in identity['selected_sources'].items():
        bind('model:' + name, Path(identity['source_worktree']) / name, pin['sha256'])
    roms = []
    for name in ('rom', 'rom_app'):
        pin = pins['tools'][name]
        roms.append(bind(name, pin['path'], pin['sha256']))
    need(roms[0].parent == roms[1].parent, 'same original ROM directory')
    bind('runner', Path(__file__))
    bind('python', Path(sys.executable))
    app_main_pin = next(row for row in pins['source_evidence'] if row['path'].replace('\\', '/').endswith('/main/app_main.c'))
    app_main = bind('historical_app_main', app_main_pin['path'], app_main_pin['sha256'])
    source = app_main.read_text('utf-8')
    entry = source.index('void app_main(void)')
    need(source.index('native_tls_early_mpi_prepare();', entry) < source.index('Starting pure ESP-IDF yoRadio (Arduino-free)', entry),
         'original application marker follows the early-MPI call')
    config = Path(selected['files']['sdkconfig']['path']).read_text('utf-8')
    reserve_enabled = bool(re.search(r'^CONFIG_YORADIO_TLS_STATIC_RX_RESERVE=y$', config, re.M))
    need(reserve_enabled == (profile == 'pdm') and
         re.search(r'^CONFIG_YORADIO_TLS_EARLY_MPI_LOCK=y$', config, re.M) and
         re.search(r'^CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM=y$', config, re.M) and
         re.search(r'^CONFIG_ESPTOOLPY_FLASHMODE_QIO=y$', config, re.M) and
         re.search(r'^CONFIG_ESPTOOLPY_FLASHMODE="dio"$', config, re.M) and
         re.search(r'^CONFIG_ESPTOOLPY_FLASHFREQ_80M=y$', config, re.M),
         'original full configs preserve reserve control, early MPI, PDM and QIO/DIO-header distinction')
    need(selected['files']['app']['sha256'] == selected['files']['build_app']['sha256'] == selected['app_sha256'] and
         selected['files']['elf']['sha256'] == selected['elf_sha256'], 'saved production app/ELF/export agreement')
    flash = bytearray(b'\xff') * 0x400000
    occupied = []
    for part in selected['flash_parts']:
        pin = selected['files'][part['file_key']]
        raw, offset = Path(pin['path']).read_bytes(), part['offset']
        need(offset >= 0 and offset + len(raw) <= len(flash) and
             all(offset + len(raw) <= begin or offset >= end for begin, end in occupied), 'original nonoverlapping four-MiB recipe')
        occupied.append((offset, offset + len(raw)))
        flash[offset:offset + len(raw)] = raw
    need(flash[0x9000:0xe000] == b'\xff' * 0x5000, 'fresh emulated NVS, no board state copied')
    for part in selected['flash_parts']:
        raw = Path(selected['files'][part['file_key']]['path']).read_bytes()
        need(flash[part['offset']:part['offset'] + len(raw)] == raw, 'every production component byte preserved')
    historical_profile = 'pdm' if profile == 'pdm' else 'disabled-pdm'
    old_report = json.loads((HISTORY / historical_profile / 'report.json').read_bytes())
    need(sha(flash) == old_report['flash_sha256'], 'fresh merged bytes exactly reproduce the original failed snapshot')
    facts = dict(production_source_commit=SOURCE_COMMIT, app_version=selected['app_version'],
                 app_sha256=selected['app_sha256'], elf_sha256=selected['elf_sha256'],
                 original_flash_sha256=old_report['flash_sha256'], static_rx_config_enabled=reserve_enabled,
                 early_mpi_config_enabled=True, full_dependency_closure_claimed=False,
                 original_qemu_sha256=pins['tools']['qemu']['sha256'], replay_qemu_sha256=QEMU_SHA,
                 original_component_count=len(selected['files']), new_selected_model_source_count=len(identity['selected_sources']))
    return facts, bindings, flash, roms[0].parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('pdm', 'disabled-pdm'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=120)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    need(out.parent == ROOT / '.build' and not out.exists() and out.name.startswith('cyd-production-boot-replay-20261030-'),
         'fresh direct-child replay campaign')
    need(1 <= args.timeout <= 120, 'bounded ordinary guest observation')
    facts, bindings, flash, rom = prepare(args.profile)
    if args.preflight_only:
        print(json.dumps(dict(preflight=True, output_created=False, native_process_started=False,
                             profile=args.profile, flash_sha256=sha(flash), bound_files=len(bindings))))
        return 0
    out.mkdir()
    source_dir = out / 'sources'
    source_dir.mkdir()
    for name in ('runner', 'historical_inputs', 'historical_app_main', 'qemu_build_identity'):
        shutil.copyfile(bindings[name]['path'], source_dir / (name + Path(bindings[name]['path']).suffix))
    flash_path = out / 'qemu-flash.bin'
    flash_path.write_bytes(flash)
    need(file_sha(flash_path) == facts['original_flash_sha256'], 'actual merged image is unchanged')
    command = [str(QEMU), '-audiodev', 'none,id=quiet', '-M', 'esp32,st7789=on,audiodev=quiet',
               '-smp', '2', '-L', str(rom), '-display', 'none', '-monitor', 'none', '-serial', 'stdio',
               '-no-reboot', '-snapshot', '-nic', 'none',
               '-drive', 'file=' + str(flash_path).replace(',', ',,') + ',if=mtd,format=raw']
    report = dict(passed=False, completed=False, startup_subset_passed=False, result='starting', profile=args.profile,
                  facts=facts, bindings=bindings, command=command, physical_device=False,
                  firmware_or_config_patched=False, source_rebuilt=False, external_network=False,
                  static_rx_loan_exercised=False, full_radio_startup_qualified=False, audio_playback_qualified=False,
                  performance_or_radio_resource_claim=False, qemu_started=False, controlled_host_stop=False,
                  log_limit_bytes=LOG_LIMIT, log_limit_is_monitored_not_os_quota=True)
    process, started, ready_at = None, time.monotonic(), None
    log_path = out / 'qemu.log'

    def save():
        write_json(out / 'report.json', report)

    def read_observations():
        need(log_path.stat().st_size <= LOG_LIMIT, 'guest_log_limit_exceeded')
        current = observations(log_path.read_text('utf-8', errors='replace'), facts['app_version'], facts['elf_sha256'])
        report.update(current)
        return current

    save()
    try:
        with log_path.open('xb') as log:
            process = subprocess.Popen(command, cwd=out, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            report.update(qemu_started=True, qemu_pid=process.pid)
            save()
            while True:
                current = read_observations()
                save()
                need(not current['panic_observed'], 'guest_panic_observed')
                need(not current['startup_error_observed'], 'startup_service_error_observed')
                need(process.poll() is None, 'guest_exited_before_controlled_observation_end')
                if all(current['markers'].values()):
                    ready_at = time.monotonic() if ready_at is None else ready_at
                    if time.monotonic() - ready_at >= 5:
                        report.update(passed=True, completed=True, startup_subset_passed=True,
                                      result='bounded_idle_startup_observed', controlled_host_stop=True)
                        break
                need(time.monotonic() - started < args.timeout, 'required_startup_markers_missing_before_deadline')
                time.sleep(0.1)
    except BaseException as error:
        report.update(passed=False, completed=True, startup_subset_passed=False, result='nonpass_or_emulator_limit',
                      error_type=type(error).__name__, reason=str(error) if isinstance(error, ValueError) else type(error).__name__)
    finally:
        if process is not None:
            if process.poll() is None:
                report['owned_child_termination_requested'] = True
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
                    report['owned_child_kill_required'] = True
            report['qemu_exit_status'] = process.returncode
        report['elapsed_seconds'] = time.monotonic() - started
        changed = [name for name, pin in bindings.items() if not Path(pin['path']).is_file() or file_sha(pin['path']) != pin['sha256']]
        report['changed_bound_input_labels'] = changed
        report['all_bound_inputs_current'] = not changed
        report['flash_unchanged_after_snapshot'] = file_sha(flash_path) == facts['original_flash_sha256']
        if log_path.exists():
            try:
                read_observations()
            except ValueError:
                report.update(passed=False, startup_subset_passed=False, result='nonpass_or_emulator_limit',
                              reason='guest_log_limit_exceeded_after_owned_child_cleanup')
            report['qemu_log_sha256'] = file_sha(log_path)
        if changed or not report['flash_unchanged_after_snapshot'] or report.get('panic_observed') or report.get('startup_error_observed'):
            report.update(passed=False, startup_subset_passed=False, result='nonpass_or_emulator_limit')
        save()
    print(json.dumps({key: report.get(key) for key in ('passed', 'profile', 'result', 'old_flash_boundary_passed',
        'early_mpi_return_log_observed', 'markers', 'qie_failure_observed', 'assertion', 'reason', 'qemu_exit_status',
        'all_bound_inputs_current', 'flash_unchanged_after_snapshot', 'static_rx_loan_exercised')}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
