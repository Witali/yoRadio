"""Execute the actual C3 connection/retry task with deterministic transport/RTOS stubs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = ROOT/'idf/esp32c3-oled-native/main/audio_service.c'
    harness = ROOT/'tests/native/stream_connection_retry_test.c'
    text = source.read_text()
    constants = '\n'.join(re.findall(r'^#define STREAM_RETRY_.*$', text, re.M))
    types = text[text.index('typedef struct {\n    uint32_t generation;'):
                 text.index('} stream_retry_t;')+len('} stream_retry_t;')]
    start = text.index('static bool http_status_is_redirect(')
    open_code = text[start:text.index('static bool send_encoded(', start)]
    start = text.index('static void schedule_stream_retry(')
    task_code = text[start:text.index('static void log_runtime_memory(const char *stage) {', start)]
    unit = args.output/'test.c'
    unit.write_text(harness.read_text().replace('/* PRODUCTION_COMMAND_TYPES */', types)
        .replace('/* PRODUCTION_RETRY_CONSTANTS */', constants)
        .replace('/* PRODUCTION_OPEN_STREAM */', open_code)
        .replace('/* PRODUCTION_STREAM_TASK */', task_code))
    for path in (source, harness, Path(__file__).resolve()):
        saved = args.output/'sources'/path.relative_to(ROOT)
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(path.read_bytes())
    binary = args.output/'test'
    (args.output/'build.log').write_bytes(run(['gcc', '-std=c11', '-O2', '-g', '-Wall', '-Wextra',
        '-Werror', '-fsanitize=address,undefined', '-fno-pie', '-no-pie', host(unit), '-o', host(binary)]))
    result = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                  'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
    (args.output/'run.log').write_bytes(result)
    assert b'PASS stream retry cases=29;' in result
    (args.output/'report.json').write_text(json.dumps(dict(passed=True, cases=29,
        source_sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (source, harness, Path(__file__).resolve())},
        scope='Actual open_stream, retry scheduling and stream_task with deterministic platform stubs; '
              'HTTP lifetime/cancellation, not physical TLS/network or PCM quality'), indent=2)+'\n')
    print(result.decode())


if __name__ == '__main__':
    main()
