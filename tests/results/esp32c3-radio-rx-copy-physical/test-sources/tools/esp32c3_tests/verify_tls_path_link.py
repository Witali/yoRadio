"""Prove optional profiler wrappers are called in the final RISC-V image."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--sdkconfig', type=Path, required=True)
    p.add_argument('--objdump', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if 'CONFIG_YORADIO_TLS_PATH_PROFILE=y' not in args.sdkconfig.read_text():
        raise ValueError('TLS path profiler is disabled')
    pairs = [
        ('stream_http_read', 'esp_http_client_read'),
        ('stream_http_read', 'tls_path_profile_end'),
        ('yoradio_mbedtls_ssl_read', 'tls_path_profile_end'),
        ('ssl_read', '__wrap_esp_transport_poll_read'),
        ('esp_crypto_aes_gcm_decrypt', '__wrap_esp_aes_gcm_auth_decrypt'),
        ('esp_aes_gcm_update', '__wrap_esp_aes_crypt_ctr'),
        ('esp_aes_gcm_finish', '__wrap_esp_aes_crypt_ctr'),
    ]
    for symbol in ('esp_transport_poll_read', 'esp_aes_gcm_auth_decrypt', 'esp_aes_crypt_ctr'):
        pairs.append(('__wrap_' + symbol, symbol))
    evidence = []
    for caller, target in pairs:
        disassembly = subprocess.check_output(
            [args.objdump, '-d', '--disassemble=' + caller, str(args.elf)], text=True)
        calls = [line.strip() for line in disassembly.splitlines()
                 if re.search(r'\b(?:jal|j|call|tail)\b', line) and '<' + target + '>' in line]
        evidence.append(dict(caller=caller, target=target, calls=calls,
                             disassembly_sha256=hashlib.sha256(disassembly.encode()).hexdigest()))
    bodies = []
    for symbol in ('esp_transport_poll_read', 'esp_aes_gcm_auth_decrypt', 'esp_aes_crypt_ctr'):
        disassembly = subprocess.check_output(
            [args.objdump, '-d', '--disassemble=__wrap_' + symbol, str(args.elf)], text=True)
        # -O3 can split end() into a .part.N body or inline it for a constant
        # stage. Preserve the actual body for review instead of requiring a
        # call the compiler legitimately removed. Physical counters still
        # need to demonstrate execution; this is a linked-code audit only.
        call = re.search(r'\b(?:jal|j|call|tail)\b[^\n]*<tls_path_profile_end(?:\.part\.\d+)?>', disassembly)
        inline = all('<' + name + '>' in disassembly for name in
                     ('s_samples', 'esp_timer_get_time', 'vPortEnterCritical', 'vPortExitCritical'))
        bodies.append(dict(wrapper='__wrap_' + symbol, end_call=bool(call),
                           inlined_counter_references=inline, disassembly=disassembly))
    result = dict(result='PASS' if all(e['calls'] for e in evidence) and
                  all(b['end_call'] or b['inlined_counter_references'] for b in bodies) else 'FAIL',
                  elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),
                  sdkconfig_sha256=hashlib.sha256(args.sdkconfig.read_bytes()).hexdigest(), calls=evidence,
                  counter_bodies=bodies,
                  scope='Linked call routes and counter-body references only; run verify_http_link.py separately for the SDK dynamic RX chain. Physical counter growth is separate evidence.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if result['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
