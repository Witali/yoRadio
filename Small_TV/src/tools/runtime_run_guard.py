"""Watch a running native soak for silent resets without modifying its inputs."""
import argparse
import json
from pathlib import Path
import re
import sys
import time

PANICS = (b'Guru Meditation', b'assert failed', b'abort() was called', b'watchdog got triggered')


def inspect_uart(data, previous_length=0):
    """Audit the complete capture, retaining counts and categories, never log payloads."""
    # A reset can interrupt the application's last UART line. Match the ROM's
    # banner plus Build line without requiring a preceding newline.
    boots = len(re.findall(rb'ESP-ROM:esp32c2[^\r\n]*\r?\nBuild:', data))
    errors = []
    if len(data) < previous_length:
        errors.append('uart_history_truncated')
    if boots != 1:
        errors.append('unexpected_rom_boot_count')
    if any(token in data for token in PANICS):
        errors.append('panic_or_watchdog')
    return {'passed': not errors, 'bytes': len(data), 'rom_boots': boots, 'errors': errors}


def read_report(path):
    """Tolerate a report currently being rewritten; absence is not a final result."""
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, json.JSONDecodeError):
        return None


def main():
    """Audit an existing soak's UART and preserve a separate guard result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--qemu-tools', type=Path, required=True)
    parser.add_argument('--interval', type=float, default=5)
    args = parser.parse_args()
    if not .1 <= args.interval <= 30:
        raise ValueError('Guard interval must be 0.1..30 host seconds')
    folder = args.run.resolve()
    state = folder / 'vm'
    sys.path.insert(0, str(args.qemu_tools.resolve()))
    import small_tv_vm as vm
    session = vm.get_session(state)
    expected_name = session['name']
    target = folder / 'uptime-guard.json'
    if target.exists():
        raise ValueError('A guard already owns this run')
    result = {'scope': 'Independent UART boot/panic guard; not a memory trend or 24-hour pass.',
              'status': 'running', 'passed': False, 'polls': 0,
              'vm_name': expected_name, 'source_file': 'vm/uart.log'}
    previous_length = 0
    while True:
        sample = inspect_uart((state / 'uart.log').read_bytes(), previous_length)
        previous_length = sample['bytes']
        result.update({'polls': result['polls'] + 1, 'last_observation': sample})
        workload = read_report(folder / 'report.json')
        if not sample['passed']:
            result['status'] = 'failed'
            vm.save_json(target, result)
            # The workload owns the sole QMP connection. The guard is read-only;
            # its failure must be inspected before accepting the workload.
            return 1
        if workload is not None and 'journal' in workload and 'inputs_unchanged' in workload:
            result.update({'status': 'complete', 'passed': True,
                           'workload_passed': workload['passed']})
            vm.save_json(target, result)
            return 0
        vm.save_json(target, result)
        time.sleep(args.interval)


if __name__ == '__main__':
    raise SystemExit(main())
