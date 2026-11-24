#!/usr/bin/env python3
"""Real-QEMU regression for ESP32 I2S OUTLINK_START command semantics."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from threading import Timer

BASE = 0x3ff4f000
CONF, RAW, CLEAR, LINK, EOF_ADDR, LC = [BASE + x for x in (8, 12, 24, 48, 56, 96)]
START, TX_START, OWNER = 1 << 29, 1 << 4, 1 << 31
EOF, TEOF, ERROR = 1 << 12, 1 << 16, 1 << 14
A, B, BUFFER = 0x3ffb1000, 0x3ffb1020, 0x3ffb2000
ADDR = 0xfffff


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class VM:
    def __init__(self, qemu, bios, folder):
        self.transactions = []
        self.stderr = (folder / 'qemu-stderr.log').open('wb')
        self.command = [str(qemu), '-M', 'esp32,audiodev=quiet,dac-rate=48000',
                        '-smp', '2', '-accel', 'qtest', '-L', str(bios), '-nic', 'none',
                        '-audiodev', 'none,id=quiet', '-display', 'none', '-serial', 'none',
                        '-monitor', 'none', '-qtest', 'stdio', '-qtest-log', 'none']
        self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=self.stderr,
                                       text=True, bufsize=1,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        self.watchdog = Timer(15, self.process.kill)
        self.watchdog.start()

    def issue(self, command):
        self.process.stdin.write(command + '\n')
        self.process.stdin.flush()
        while True:
            line = self.process.stdout.readline()
            if line.startswith('IRQ '):
                continue
            if not line.startswith('OK'):
                raise RuntimeError(f'{command}: {line!r}; returncode={self.process.poll()}')
            reply = line[2:].strip()
            self.transactions.append({'command': command, 'reply': reply})
            return reply

    def write(self, address, value):
        self.issue(f'writel {address:#x} {value:#x}')

    def read(self, address):
        return int(self.issue(f'readl {address:#x}'), 0)

    def advance(self):
        self.issue('clock_step 100000')

    def descriptor(self, address):
        self.write(address, OWNER | (1 << 30) | (16 << 12) | 16)
        self.write(address + 4, BUFFER)
        self.write(address + 8, 0)
        self.write(BUFFER, 0x81238123)

    def close(self):
        self.watchdog.cancel()
        if self.process.poll() is None:
            self.process.terminate()
        self.process.wait(timeout=5)
        self.process.stdin.close()
        self.process.stdout.close()
        self.stderr.close()


def run_case(name, qemu, bios, root):
    folder = root / name
    folder.mkdir()
    vm = VM(qemu, bios, folder)
    checks = []

    def expect(label, actual, expected):
        checks.append({'label': label, 'actual': actual, 'expected': expected,
                       'passed': actual == expected})

    try:
        vm.write(CONF, 1)
        vm.write(CONF, 0)
        vm.write(CLEAR, 0xffffffff)
        vm.write(LC, (1 << 6) | (1 << 8) | ((1 << 12) if name.endswith('owner-check') else 0))
        vm.descriptor(A)
        vm.descriptor(B)
        if name.startswith('self-clear'):
            tx_first = name.endswith('tx-on')
            if tx_first:
                vm.write(CONF, TX_START)
            vm.write(LINK, START | (A & ADDR))
            expect('START self-clears after command', bool(vm.read(LINK) & START), False)
            vm.advance()
            if not tx_first:
                expect('armed link waits for TX', vm.read(RAW) & (EOF | TEOF | ERROR), 0)
                vm.write(CONF, TX_START)
                vm.advance()
            expect('valid transfer completes', vm.read(RAW) & (EOF | TEOF | ERROR), EOF | TEOF)
            expect('EOF address is A', vm.read(EOF_ADDR), A)
        else:
            vm.write(CONF, TX_START)
            vm.write(LINK, START | (A & ADDR))
            vm.advance()
            expect('first SDK transfer completes', vm.read(RAW) & (EOF | TEOF | ERROR), EOF | TEOF)
            expect('first transfer writes owner back', bool(vm.read(A) & OWNER), False)
            vm.write(CLEAR, 0xffffffff)

            # Exactly model LL bitfield RMW: set address, then separately set START.
            address_word = (vm.read(LINK) & ~ADDR) | (B & ADDR)
            vm.write(LINK, address_word)
            vm.advance()
            expect('address-only RMW does not complete B', vm.read(RAW) & (EOF | TEOF | ERROR), 0)
            expect('address-only RMW preserves B ownership', bool(vm.read(B) & OWNER), True)
            expect('address-only RMW preserves last EOF A', vm.read(EOF_ADDR), A)
            vm.write(CLEAR, 0xffffffff)

            start_word = vm.read(LINK) | START
            vm.write(LINK, start_word)
            expect('second START self-clears', bool(vm.read(LINK) & START), False)
            vm.advance()
            expect('explicit START completes B exactly once', vm.read(RAW) & (EOF | TEOF | ERROR), EOF | TEOF)
            expect('explicit START returns B', vm.read(EOF_ADDR), B)
            expect('second transfer writes owner back', bool(vm.read(B) & OWNER), False)
        result = {'case': name, 'passed': all(x['passed'] for x in checks),
                  'checks': checks, 'qemu_command': vm.command,
                  'transactions': vm.transactions}
    finally:
        vm.close()
    (folder / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu', type=Path, required=True)
    parser.add_argument('--bios', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy', type=Path, required=True)
    args = parser.parse_args()
    qemu, bios = args.qemu.resolve(strict=True), args.bios.resolve(strict=True)
    args.output.mkdir()
    results = [run_case(name, qemu, bios, args.output) for name in
               ('self-clear-tx-on', 'self-clear-tx-off', 'repeat-sdk-owner-off', 'repeat-sdk-owner-check')]
    legacy = subprocess.run([os.sys.executable, str(args.legacy.resolve(strict=True)),
                             '--qemu', str(qemu), '--bios', str(bios)],
                            capture_output=True, text=True, timeout=30)
    (args.output / 'legacy-stdout.log').write_text(legacy.stdout)
    (args.output / 'legacy-stderr.log').write_text(legacy.stderr)
    report = {'qemu': str(qemu), 'qemu_sha256': sha(qemu),
              'test_sha256': sha(Path(__file__)), 'legacy_test_sha256': sha(args.legacy),
              'new_cases': [{'case': x['case'], 'passed': x['passed'],
                             'failed_checks': [c for c in x['checks'] if not c['passed']]} for x in results],
              'new_passed': sum(x['passed'] for x in results), 'new_total': len(results),
              'legacy_six_passed': legacy.returncode == 0,
              'legacy_returncode': legacy.returncode,
              'scope': 'Real QEMU qtest MMIO, no guest instructions, firmware, TLS, or timing qualification.'}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return 0 if report['new_passed'] == report['new_total'] and report['legacy_six_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
