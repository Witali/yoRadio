"""Verify HTTP/TLS wrappers in a linked C3 image, independently of host tests."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--objdump', required=True)
    p.add_argument('--sdkconfig', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    dynamic = 'CONFIG_MBEDTLS_DYNAMIC_BUFFER=y' in args.sdkconfig.read_text()
    pairs = [
        ('stream_task', 'stream_http_read'),
        ('esp_mbedtls_read', 'yoradio_mbedtls_ssl_read'),
        ('yoradio_mbedtls_ssl_read', '__wrap_mbedtls_ssl_read' if dynamic else 'mbedtls_ssl_read'),
    ]
    if dynamic:
        pairs.extend([
            ('__wrap_mbedtls_ssl_read', 'esp_mbedtls_add_rx_buffer'),
            ('__wrap_mbedtls_ssl_read', 'mbedtls_ssl_read'),
            ('__wrap_mbedtls_ssl_read', 'esp_mbedtls_free_rx_buffer'),
        ])
    evidence = []
    for caller, target in pairs:
        disassembly = subprocess.check_output(
            [args.objdump, '-d', '--disassemble='+caller, str(args.elf)], text=True)
        calls = [line.strip() for line in disassembly.splitlines()
                 if re.search(r'\b(?:jal|j|call|tail)\b', line)
                 and '<'+target+'>' in line]
        evidence.append(dict(caller=caller, target=target, calls=calls,
                             disassembly_sha256=hashlib.sha256(disassembly.encode()).hexdigest()))
    passed = all(e['calls'] for e in evidence)
    result = dict(result='PASS' if passed else 'FAIL',
                  dynamic_buffers=dynamic,
                  sdkconfig_sha256=hashlib.sha256(args.sdkconfig.read_bytes()).hexdigest(),
                  elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),
                  calls=evidence, scope='Linked RISC-V call paths only; no hardware or TLS cryptography qualification')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
