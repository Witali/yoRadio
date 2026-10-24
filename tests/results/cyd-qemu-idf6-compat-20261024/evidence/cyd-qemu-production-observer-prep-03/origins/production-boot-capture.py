"""Proposed exact-image local smoke runner. Not executed during preparation.

This creates only a fresh sibling .build output and starts one pinned emulator.
It never invokes SDK/build/esptool/serial tools, opens a NIC, or patches inputs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


HERE = Path(__file__).resolve().parent
PINS = HERE / 'inputs.json'
LIMIT_SECONDS = 120
SETTLE_SECONDS = 5
PANIC = re.compile(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|'
                   r'watchdog.*triggered|LoadProhibited|StoreProhibited', re.I)
STARTUP_ERROR = re.compile(r'NVS init failed|SPIFFS mount failed|Audio service failed|'
                           r'Radio control failed|Web server failed|Health sampler initialization failed|'
                           r'Time service unavailable|Network settings unavailable|'
                           r'TLS input reclamation not attached', re.I)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def save(path, value):
    temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('pdm', 'continuous', 'legacy', 'custom-flac-pdm',
                        'custom-flac-continuous', 'custom-flac-legacy', 'disabled-pdm'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    pins = json.loads(PINS.read_text(encoding='utf-8-sig'))
    root, output = Path(pins['root']).resolve(), args.output.resolve()
    require(output.parent == root / '.build' and not output.exists() and output != HERE,
            'Choose a fresh direct child of this worktree .build directory')
    output.mkdir()
    report_path = output / 'report.json'
    report = dict(scope='Exact production image boot smoke only', result='RUNNING',
                  profile=args.profile, inputs_manifest_sha256=sha(PINS),
                  runner_sha256=sha(__file__), qemu_started=False, startup_subset_passed=False,
                  full_radio_startup_qualified=False, static_rx_loan_exercised=False,
                  network_association_qualified=False, audio_output_qualified=False,
                  physical_qualification=False, controlled_host_stop=False)
    save(report_path, report)
    process = None
    started = None
    before = {}
    try:
        selected = pins['profiles'][args.profile]
        checked = [*pins['tools'].values(), *selected['files'].values(), *pins['source_evidence']]
        for item in checked:
            path = Path(item['path'])
            require(path.is_file() and sha(path) == item['sha256'], 'Pinned input changed: ' + str(path))
            before[str(path)] = item['sha256']
        require(selected['source_commit'] == pins['source_commit'], 'Wrong selected production source')
        require(selected['files']['app']['sha256'] == selected['app_sha256'], 'Wrong saved app digest')
        require(selected['files']['build_app']['sha256'] == selected['app_sha256'], 'Build and saved app differ')
        require(selected['files']['elf']['sha256'] == selected['elf_sha256'], 'Selected ELF differs from export')

        flash = bytearray(b'\xff') * 0x400000
        occupied = []
        for part in selected['flash_parts']:
            item = selected['files'][part['file_key']]
            raw, offset = Path(item['path']).read_bytes(), part['offset']
            require(offset >= 0 and offset + len(raw) <= len(flash), 'Flash component exceeds image')
            require(all(offset + len(raw) <= a or offset >= b for a, b in occupied), 'Flash inputs overlap')
            occupied.append((offset, offset + len(raw)))
            flash[offset:offset + len(raw)] = raw
        # Fresh emulated NVS only, with Smart Start disabled by normal defaults.
        require(flash[0x9000:0xe000] == b'\xff' * 0x5000, 'Unexpected initial NVS data')
        flash_path = output / 'qemu-flash.bin'
        flash_path.write_bytes(flash)
        require(sha(flash_path) == hashlib.sha256(flash).hexdigest(), 'Scratch image write mismatch')
        for part in selected['flash_parts']:
            raw = Path(selected['files'][part['file_key']]['path']).read_bytes()
            require(flash_path.read_bytes()[part['offset']:part['offset'] + len(raw)] == raw,
                    'Scratch image modified a production component')
        flash_hash = sha(flash_path)
        qemu, rom = pins['tools']['qemu']['path'], str(Path(pins['tools']['rom']['path']).parent)
        command = [qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,st7789=on,audiodev=quiet',
                   '-smp', '2', '-L', rom, '-display', 'none', '-monitor', 'none', '-serial', 'stdio',
                   '-no-reboot', '-snapshot', '-nic', 'none',
                   '-drive', 'file=' + str(flash_path).replace(',', ',,') + ',if=mtd,format=raw']
        report.update(command=command, flash_sha256=flash_hash,
                      flash_components_byte_exact=True, checked_inputs=before)
        save(report_path, report)
        log_path = output / 'qemu.log'
        expected_output = {'pdm': 'I2S PDM', 'continuous': 'internal DAC', 'legacy': 'legacy I2S/DAC x16'}[selected['backend']]
        ready_at = None
        with log_path.open('wb') as log:
            started = time.monotonic()
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            report.update(qemu_started=True, owned_process_id=process.pid)
            save(report_path, report)
            while True:
                text = log_path.read_text(encoding='utf-8', errors='replace')
                text = re.sub(r'\x1b\[[0-9;]*m', '', text)
                markers = dict(
                    after_early_mpi=text.count('Starting pure ESP-IDF yoRadio (Arduino-free)') == 1,
                    display_driver_entered='ST7789: SPI2 DMA' in text,
                    pipeline_owners_ready=('Pipeline ready: ' + expected_output + ',') in text,
                    radio_control_entered='Smart Start state: 2' in text,
                    web_service_ready=bool(re.search(r'Native HTTPS? server started', text)))
                report.update(markers=markers, network_failure_observed='Network failed:' in text,
                              early_mpi_prepare_returned=markers['after_early_mpi'],
                              display_init_and_clear_returned=markers['pipeline_owners_ready'] or markers['web_service_ready'],
                              audio_owners_created=markers['pipeline_owners_ready'],
                              radio_control_initialized=markers['radio_control_entered'] and markers['web_service_ready'],
                              panic_observed=bool(PANIC.search(text)), startup_error_observed=bool(STARTUP_ERROR.search(text)))
                save(report_path, report)
                require(not PANIC.search(text), 'Guest panic/reset diagnostic observed')
                require(not STARTUP_ERROR.search(text), 'Required startup service failed')
                require(process.poll() is None, 'Emulator exited before controlled capture stop')
                if all(markers.values()):
                    ready_at = time.monotonic() if ready_at is None else ready_at
                    if time.monotonic() - ready_at >= SETTLE_SECONDS:
                        report.update(startup_subset_passed=True, result='STARTUP_SMOKE_OBSERVED',
                                      display_init_and_clear_returned=True,
                                      early_mpi_prepare_returned=True, controlled_host_stop=True)
                        break
                require(time.monotonic() - started < LIMIT_SECONDS, 'Missing markers before bounded deadline')
                time.sleep(.25)
    except BaseException as error:
        report.update(result='FAIL_OR_EMULATOR_LIMIT', startup_subset_passed=False,
                      interrupted=not isinstance(error, Exception), error_type=type(error).__name__)
        # Reasons are controller constants/paths; no guest log/user data are copied.
        report['reason'] = str(error) if isinstance(error, RuntimeError) else type(error).__name__
    finally:
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
            report['qemu_exit_code'] = process.returncode
            report['elapsed_seconds'] = time.monotonic() - started
        changed = [path for path, value in before.items() if not Path(path).is_file() or sha(path) != value]
        report['changed_input_paths'] = changed
        if changed:
            report.update(result='FAIL_OR_EMULATOR_LIMIT', startup_subset_passed=False)
        flash_path = output / 'qemu-flash.bin'
        if flash_path.exists() and 'flash_sha256' in report:
            report['flash_unchanged_after_snapshot'] = sha(flash_path) == report['flash_sha256']
            if not report['flash_unchanged_after_snapshot']:
                report.update(result='FAIL_OR_EMULATOR_LIMIT', startup_subset_passed=False)
        log_path = output / 'qemu.log'
        if log_path.exists():
            report['qemu_log_sha256'] = sha(log_path)
            # Include any late diagnostics flushed during owned process shutdown.
            final_text = log_path.read_text(encoding='utf-8', errors='replace')
            if PANIC.search(final_text) or STARTUP_ERROR.search(final_text):
                report.update(result='FAIL_OR_EMULATOR_LIMIT', startup_subset_passed=False)
        save(report_path, report)
    print(json.dumps({key: report[key] for key in ('result', 'startup_subset_passed',
                     'full_radio_startup_qualified', 'static_rx_loan_exercised')}))
    return 0 if report['startup_subset_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
