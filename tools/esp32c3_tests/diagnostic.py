"""Run a C3 test with filtered panic PCs as well as performance evidence.

Retains MEPC/RA/MCAUSE and possible code addresses from stack/backtrace lines,
not raw stack contents, URLs, station names or network credentials. Stack code
addresses are candidates, not a verified unwind. Does not reset/flash on its own.
"""
import importlib
import re
import sys
import time

import run
from common import filter_tls_line
from serial_lines import serial_lines


WATCHDOG_TASKS = frozenset(('IDLE0', 'IDLE1', 'main', 'radio_stream',
                          'audio_decode', 'audio_output', 'wifi', 'tcpip',
                          'tiT', 'tcpip_task', 'httpd', 'websocket_statu',
                          'websocket_status', 'cpu_profile', 'esp_timer',
                          'sys_evt', 'Tmr Svc', 'ipc0', 'ipc1'))


def watchdog_line(line):
    """Keep SDK watchdog context even if its first line was lost on UART.

    User watchdog entries can contain arbitrary names. Only known firmware
    task names are retained; all others get a fixed redacted identifier.
    Context alone still fails runtime gates, just like the timeout caption.
    """
    clean = re.sub(r'\x1b\[[0-9;]*m', '', line)
    match = re.search(r'\btask_wdt: (.*)$', clean)
    if not match:
        return None
    body = match.group(1).strip()
    prefix = 'Runtime watchdog timeout: task_watchdog=true'
    if body.startswith('Task watchdog got triggered.'):
        return prefix
    if body == 'Tasks currently running:':
        return prefix + ' phase=current-tasks'
    entry = re.fullmatch(r'- (.+) \(CPU (0|1|0/1)\)', body)
    current = re.fullmatch(r'CPU (0|1): (.+)', body)
    if entry or current:
        name, cpu = entry.groups() if entry else current.groups()[::-1]
        task = name.replace(' ', '_') if name in WATCHDOG_TASKS else 'redacted'
        phase = 'starved' if entry else 'running'
        return f'{prefix} phase={phase} cpu={cpu} task={task}'
    backtrace = re.fullmatch(r'Print CPU (0|1)(?: \(current core\))? (backtrace|registers)', body)
    if backtrace:
        return f'{prefix} phase={backtrace.group(2)} cpu={backtrace.group(1)}'
    return None


def filter_line(line):
    # Task-context replay survives native-USB loss of early ISR log captions.
    counter = re.search(r'\bPERF watchdog: task_timeouts=([1-9][0-9]*)\b', line)
    if counter:
        return ('Runtime watchdog timeout: task_watchdog=true '
                'events=' + counter.group(1))
    watchdog = watchdog_line(line)
    if watchdog:
        return watchdog
    tls = filter_tls_line(line)
    if tls:
        return tls
    if re.search(r'PERF |Memory .*: free=|decode (?:error|failed)|allocation failed|'
                 r'assert failed|Guru Meditation|CORRUPT HEAP|serial capture interrupted', line):
        return line
    adaptive = re.search(r'\bTLS_INPUT released=\d+ retries=\d+ request=\d+ '
                         r'resident=\d+ minimum=\d+ target=\d+ occupied=\d+ capacity=\d+\b', line)
    if adaptive:
        return adaptive.group(0)
    reserved = re.search(r'\bTLS_RESERVE capacity=\d+ minimum=\d+ allocations=\d+ '
                         r'releases=\d+ busy_fallbacks=\d+ oversize=\d+ busy=\d+ used=\d+\b', line)
    if reserved:
        return reserved.group(0)
    registers = re.findall(r'\b(MEPC|RA|MCAUSE)\s*:\s*(0x[0-9a-fA-F]+)', line)
    if registers:
        return 'PANIC registers: '+' '.join(name+'='+value for name, value in registers)
    if line.startswith('Backtrace:') or re.match(r'^(?:0x)?3fc[0-9a-fA-F]+:', line):
        candidates = [int(value, 16) for value in re.findall(r'0x([0-9a-fA-F]{8})', line)]
        code = [value for value in candidates if 0x40000000 <= value < 0x40080000 or
                0x4037c000 <= value < 0x403e0000 or 0x42000000 <= value < 0x42800000]
        if code:
            return 'PANIC stack code candidates: '+' '.join(f'0x{value:08x}' for value in code)
    if re.match(r'^(ESP-ROM:|rst:|Saved PC:|ELF file SHA256:|waiting for download)', line):
        return line
    return None


class DiagnosticCapture(run.Capture):
    def read(self):
        for line in serial_lines(self.port, self.closed):
            safe = filter_line(line)
            if safe:
                self.rows.append(dict(at=time.perf_counter(), line=safe))


def main():
    choices = ('run', 'memory', 'ota_transition', 'pool_settle', 'terminal_memory')
    if len(sys.argv) < 2 or sys.argv[1] not in choices:
        raise SystemExit('Usage: diagnostic.py {'+'|'.join(choices)+'} [runner arguments]')
    name = sys.argv.pop(1)
    run.Capture = DiagnosticCapture
    module = importlib.import_module(name)
    module.Capture = DiagnosticCapture
    return module.main()


if __name__ == '__main__':
    raise SystemExit(main())
