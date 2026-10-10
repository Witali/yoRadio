"""ASan/UBSan tests of real optional wrappers; cryptography/RTOS are scripted."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
args = p.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
stubs = {
    'sdkconfig.h': '#define CONFIG_YORADIO_TLS_PATH_PROFILE 1\n',
    'esp_timer.h': '#include <stdint.h>\nint64_t esp_timer_get_time(void);\n',
    'esp_log.h': 'void test_log(const char *, const char *, ...);\n#define ESP_LOGI test_log\n',
    'freertos/FreeRTOS.h': '''typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
void test_enter(void *); void test_exit(void *);
#define portENTER_CRITICAL test_enter
#define portEXIT_CRITICAL test_exit
''',
    'freertos/task.h': 'const char *pcTaskGetName(void *);\n',
    'esp_transport.h': 'typedef void *esp_transport_handle_t;\n',
    'aes/esp_aes.h': 'typedef int esp_aes_context;\n',
    'aes/esp_aes_gcm.h': 'typedef int esp_gcm_context;\n',
    'mbedtls/ssl.h': '''#include <stddef.h>
typedef int mbedtls_ssl_context;
#define MBEDTLS_ERR_SSL_WANT_READ (-0x6900)
#define MBEDTLS_ERR_SSL_WANT_WRITE (-0x6880)
#define MBEDTLS_ERR_SSL_TIMEOUT (-0x6800)
#define MBEDTLS_ERR_SSL_CONN_EOF (-0x7280)
int mbedtls_ssl_read(mbedtls_ssl_context *, unsigned char *, size_t);
int yoradio_mbedtls_ssl_read(mbedtls_ssl_context *, unsigned char *, size_t);
''',
    'esp_http_client.h': '''#include <stddef.h>
typedef int esp_err_t;
typedef void *esp_http_client_handle_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_HTTP_EAGAIN 0x7007
int esp_http_client_read(esp_http_client_handle_t, char *, int);
esp_err_t esp_http_client_close(esp_http_client_handle_t);
esp_err_t esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t, int *, int *);
''',
    'esp_tls_errors.h': '''#define ESP_ERR_MBEDTLS_SSL_READ_FAILED 0x801d
#define ESP_TLS_ERR_SSL_TIMEOUT (-0x6800)
#define ESP_TLS_ERR_SSL_WANT_READ (-0x6900)
#define ESP_TLS_ERR_SSL_WANT_WRITE (-0x6880)
''',
}
for name, source in stubs.items():
    path = args.output / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#pragma once\n' + source)

def linux(path):
    path = path.resolve()
    return '/mnt/' + path.drive[0].lower() + path.as_posix()[2:]

main = ROOT / 'idf/esp32c3-oled-native/main'
sources = [ROOT / 'tests/native/tls_path_profile_test.c'] + [main / name for name in
           ('tls_path_profile.c', 'tls_stream_eof.c', 'stream_http_reader.c')]
command = ['wsl.exe', '--exec', 'gcc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-O1', '-g',
           '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
           '-I' + linux(args.output), '-I' + linux(main), *map(linux, sources),
           '-o', linux(args.output / 'test')]
build = subprocess.run(command, capture_output=True, text=True, timeout=120)
(args.output / 'build.log').write_text(build.stdout + build.stderr)
if build.returncode:
    raise SystemExit(build.stderr)
run = subprocess.run(['wsl.exe', '--exec', linux(args.output / 'test')],
                     capture_output=True, text=True, timeout=30)
(args.output / 'run.log').write_text(run.stdout + run.stderr)
result = dict(result='PASS' if run.returncode == 0 and 'TLS_PATH_PROFILE_PASS' in run.stdout else 'FAIL',
              source_sha256={str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in sources + [main / 'tls_path_profile.h', Path(__file__)]},
              scope='Real wrappers and counters under ASan/UBSan, scripted API and task/time seams; no cryptography, scheduler or hardware qualification.',
              output=run.stdout, returncode=run.returncode)
(args.output / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
raise SystemExit(0 if result['result'] == 'PASS' else 1)
