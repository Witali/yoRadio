"""Execute the actual C3 connection/retry task with deterministic transport/RTOS stubs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--tls-retain-rx', action='store_true',
                        help='Verify the SDK retained-RX strategy on every connection attempt')
    parser.add_argument('--adaptive-input', action='store_true',
                        help='Verify input-memory preparation follows previous TLS cleanup')
    parser.add_argument('--flac-input-growth', action='store_true',
                        help='Verify FLAC-only growth after the current decoder is ready')
    parser.add_argument('--network-power',action='store_true',help='Link real shared policy and check receive/backoff/EOF intent')
    parser.add_argument('--read-timeout-ms', type=int, default=250,
                        help='HTTP body timeout to validate independently of connection deadlines (10..1000)')
    parser.add_argument('--read-size', type=int, default=2048,
                        help='HTTP body request size, independent of packet capacity (128..2048)')
    args = parser.parse_args()
    if not 10 <= args.read_timeout_ms <= 1000:
        parser.error('--read-timeout-ms must be within 10..1000')
    if not 128 <= args.read_size <= 2048:
        parser.error('--read-size must be within 128..2048')
    if args.flac_input_growth:
        args.adaptive_input = True
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'freertos').mkdir()
    (args.output/'freertos/FreeRTOS.h').write_text('#pragma once\n#include <pthread.h>\ntypedef pthread_mutex_t portMUX_TYPE;\n#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER\n#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))\n#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))\n')
    (args.output/'esp_err.h').write_text('#pragma once\n')
    source = ROOT/'idf/esp32c3-oled-native/main/audio_service.c'
    reader = source.with_name('stream_http_reader.c')
    reader_header = source.with_name('stream_http_reader.h')
    profile_header = source.with_name('tls_path_profile.h')
    probe_header = source.with_name('stream_probe.h')
    tags_header = source.with_name('stream_tags.h')
    icy = source.with_name('icy_title.c')
    icy_header = source.with_name('icy_title.h')
    harness = ROOT/'tests/native/stream_connection_retry_test.c'
    text = source.read_text()
    start = text.index('static void dispose_http_client(')
    dispose_code = text[start:text.index('\n}', start)+2]
    constants = '\n'.join(re.findall(r'^#define STREAM_(?:RETRY_.*|READ_TIMEOUT_MS.*|READ_SIZE.*)$', text, re.M))
    types = text[text.index('typedef struct {\n    uint32_t generation;'):
                 text.index('} stream_retry_t;')+len('} stream_retry_t;')]
    start = text.index('static bool http_status_is_redirect(')
    open_code = text[start:text.index('static bool send_encoded(', start)]
    start = text.index('static void begin_stream_deadline(')
    task_code = text[start:text.index('static void log_runtime_memory(const char *stage) {', start)]
    helpers = text[text.index('static inline void stream_transport_reset('):
                   text.index('static bool send_stream_audio(')]
    helpers += text[text.index('static inline uint8_t finish_stream_audio('):
                    text.index('static void stream_bitrate_add(')]
    reader_types=reader_header.read_text()
    reader_types=reader_types[reader_types.index('typedef struct {'):reader_types.index('} stream_http_reader_t;')+len('} stream_http_reader_t;')]
    unit = args.output/'test.c'
    unit.write_text(harness.read_text().replace('/* PRODUCTION_COMMAND_TYPES */', types)
        .replace('/* PRODUCTION_DISPOSE_CLIENT */', dispose_code)
        .replace('/* PRODUCTION_PROFILE_HEADER */', re.sub(
            r'^#(?:pragma once|include "sdkconfig.h")[^\n]*\n', '',
            profile_header.read_text(), flags=re.M))
        .replace('/* PRODUCTION_RETRY_CONSTANTS */', constants)
        .replace('/* PRODUCTION_HTTP_READER_TYPE */', reader_types)
        .replace('/* PRODUCTION_HTTP_READER */', reader.read_text()[reader.read_text().index('int stream_http_read('):])
        .replace('/* PRODUCTION_OPEN_STREAM */', open_code)
        .replace('/* PRODUCTION_STREAM_TASK */', task_code))
    unit.write_text(unit.read_text().replace('/* PRODUCTION_STREAM_HELPERS */', helpers))
    inputs = (source, reader, reader_header, profile_header, probe_header, tags_header, icy, icy_header, harness, ROOT/'tests/native/audio_power_seam.h', Path(__file__).resolve())
    power=ROOT/'idf/components/native_network_power'
    if args.network_power:inputs += (power/'native_network_power.c',power/'include/native_network_power.h')
    for path in inputs:
        saved = args.output/'sources'/path.relative_to(ROOT)
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(path.read_bytes())
    binary = args.output/'test'
    (args.output/'build.log').write_bytes(run(['gcc', '-std=c11', '-O2', '-g', '-Wall', '-Wextra',
        '-Werror', '-fsanitize=address,undefined', '-fno-pie', '-no-pie',
        f'-DCONFIG_YORADIO_STREAM_READ_TIMEOUT_MS={args.read_timeout_ms}',
        f'-DCONFIG_YORADIO_STREAM_READ_BYTES={args.read_size}',
        *(['-DCONFIG_YORADIO_TLS_RETAIN_RX_BUFFER=1'] if args.tls_retain_rx else []),
        *(['-DCONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=1'] if args.adaptive_input else []),
        *(['-DCONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=4'] if args.flac_input_growth else []),
        *(['-DAUDIO_POWER_INTEGRATION=1','-I'+host(args.output),'-I'+host(power),'-I'+host(power/'include'),'-pthread'] if args.network_power else []),
        '-I', host(source.parent), '-I',host(ROOT/'tests/native'), host(unit), host(icy), '-o', host(binary)]))
    result = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                  'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
    (args.output/'run.log').write_bytes(result)
    cases = 42 if args.flac_input_growth else 37
    assert f'PASS stream retry cases={cases};'.encode() in result
    (args.output/'report.json').write_text(json.dumps(dict(passed=True, cases=cases,
        flac_input_growth=args.flac_input_growth,
        tls_retain_rx=args.tls_retain_rx,
        adaptive_input=args.adaptive_input,
        read_timeout_ms=args.read_timeout_ms,
        read_size=args.read_size,
        source_sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in inputs},
        scope='Actual open_stream, retry scheduling and stream_task with deterministic platform stubs; '
              'HTTP lifetime/cancellation, not physical TLS/network or PCM quality'), indent=2)+'\n')
    print(result.decode())


if __name__ == '__main__':
    try:main()
    except subprocess.CalledProcessError as error:
        print(error.output.decode(errors='replace'),file=sys.stderr)
        raise
