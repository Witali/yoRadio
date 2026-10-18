"""Verify portable RFC6455 message/control semantics under ASan and UBSan.

Tests the production header, all Unicode scalars and every byte split, numeric
UTF8 oracle, all uint16 Close codes, bounded assembly, controls and timeouts.
Wire-header/handshake conformance is a separate integration requirement.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'idf/components/native_stream/include/websocket_message.h'
TEST = ROOT / 'tests/native/ws_message_test.c'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources = [HEADER, TEST, Path(__file__)]
    for path in sources:
        target = out / 'sources' / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    variants = {'production': HEADER.read_text()}
    variants['mutant-unchecked-utf8'] = variants['production'].replace(
        '!websocket_message_utf8_check(message->buffer, message->used, final)', 'false')
    variants['mutant-orphan-continuation'] = variants['production'].replace(
        'if (!message->active) return websocket_message_error(message, 1002);',
        'if (false) return websocket_message_error(message, 1002);')
    variants['mutant-unchecked-close-code'] = re.sub(
        r'static inline bool websocket_message_close_code_valid\(uint16_t code\) \{.*?\n\}',
        'static inline bool websocket_message_close_code_valid(uint16_t code) { (void)code; return true; }',
        variants['production'], flags=re.S)
    variants['mutant-renewed-message-deadline'] = variants['production'].replace(
        'if (opcode == 0U) {', 'if (opcode == 0U) { message->started_us = now_us;')
    report = {'passed': True, 'sanitizers': ['ASan', 'UBSan'], 'negative_controls': {}}
    for name, text in variants.items():
        if name != 'production':
            assert text != variants['production'], name
        target = out / name
        target.mkdir()
        (target / HEADER.name).write_text(text)
        binary = target / 'test'
        command = ['gcc', '-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror',
                   '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                   '-I'+host(target), host(TEST), '-o', host(binary)]
        try:
            (target / 'build.log').write_bytes(run(command))
            code = 0
            try:
                log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                           'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '60', host(binary)])
            except subprocess.CalledProcessError as error:
                code, log = error.returncode, error.output
            (target / 'test.log').write_bytes(log)
            if name == 'production':
                assert code == 0, log.decode(errors='replace')
                report['counts'] = json.loads(log)
                print(log.decode().strip())
            else:
                assert code != 0 and b'Assertion' in log and b'Sanitizer' not in log, (name, code, log)
                report['negative_controls'][name] = {'expected_failure': True, 'exit_code': code}
                print(name + ': semantic assertion caught')
        except subprocess.CalledProcessError as error:
            (out / 'failure.log').write_bytes(error.output)
            print(error.output.decode(errors='replace'), file=sys.stderr)
            raise
    report['source_sha256'] = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
    report['references'] = ['https://www.rfc-editor.org/rfc/rfc6455.html#section-5.4',
                            'https://www.rfc-editor.org/rfc/rfc6455.html#section-5.5',
                            'https://www.rfc-editor.org/rfc/rfc6455.html#section-8.1',
                            'https://www.iana.org/assignments/websocket#close-code-number']
    report['scope'] = 'Production message/control helper only; no raw frame header/masking, HTTP upgrade, live TCP, SDK lifecycle or hardware timing proof.'
    (out / 'report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
