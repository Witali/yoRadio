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


def filter_line(line):
    if re.search(r'\btask_wdt: Task watchdog got triggered\.', line):
        # A nonfatal watchdog dump uses a synthetic MCAUSE. Retain the actual
        # timeout reason even when the subsequent register lines are lost.
        return 'Runtime watchdog timeout: task_watchdog=true'
    tls = filter_tls_line(line)
    if tls:
        return tls
    if re.search(r'PERF |Memory .*: free=|decode (?:error|failed)|allocation failed|'
                 r'assert failed|Guru Meditation|CORRUPT HEAP|serial capture interrupted', line):
        return line
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
                self.rows.append(dict(at=time.monotonic(), line=safe))


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
