"""Test real IDF HTTP body parsing/read control and the radio fatal-error guard."""
import argparse, hashlib, json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--idf',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
args=p.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
sdk=args.idf/'components/esp_http_client/esp_http_client.c'
source=sdk.read_text()
start=source.index('int esp_http_client_read(')
end=source.index('\nesp_err_t esp_http_client_perform(',start)
function=source[start:end]
assert function.rstrip().endswith('}')
harness=ROOT/'tests/native/stream_http_reader_test.c'
complete_start=source.index('bool esp_http_client_is_complete_data_received(')
complete=source[complete_start:start]
body_start=source.index('static int http_on_body(')
body=source[body_start:source.index('static int http_on_chunk_complete(',body_start)]
parser=args.idf/'components/http_parser'
tls_source=(args.idf/'components/esp-tls/esp_tls_mbedtls.c').read_text()
tls_start=tls_source.index('ssize_t esp_mbedtls_read(')
tls_read=tls_source[tls_start:tls_source.index('ssize_t esp_mbedtls_write(',tls_start)]
generated=(harness.read_text().replace('/* SDK_HTTP_CLIENT_READ */',function)
    .replace('/* SDK_HTTP_COMPLETE */',complete).replace('/* SDK_HTTP_BODY */',body)
    .replace('/* SDK_TLS_READ */',tls_read))
(args.output/'test.c').write_text(generated)
(args.output/'esp_http_client.h').write_text('''#pragma once
#include <stddef.h>
typedef int esp_err_t;
typedef struct fake_client *esp_http_client_handle_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_HTTP_EAGAIN 0x7007
int esp_http_client_read(esp_http_client_handle_t,char *,int);
esp_err_t esp_http_client_close(esp_http_client_handle_t);
esp_err_t esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t,int *,int *);
''')
(args.output/'esp_tls_errors.h').write_text('''#pragma once
#define ESP_ERR_MBEDTLS_SSL_READ_FAILED 0x801d
#define ESP_TLS_ERR_SSL_TIMEOUT (-0x6800)
#define ESP_TLS_ERR_SSL_WANT_READ (-0x6900)
#define ESP_TLS_ERR_SSL_WANT_WRITE (-0x6880)
''')
# Keep injected TLS codes synchronized with each tested SDK, not guessed values.
import re
ssl=(args.idf/'components/mbedtls/mbedtls/include/mbedtls/ssl.h').read_text()
with (args.output/'esp_tls_errors.h').open('a') as codes:
    for name in ('MBEDTLS_ERR_SSL_ALLOC_FAILED','MBEDTLS_ERR_SSL_INVALID_MAC','MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY','MBEDTLS_ERR_SSL_CONN_EOF'):
        value=re.search(r'^#define\s+'+name+r'\s+(\S+)',ssl,re.M)
        assert value, name
        literal=value[1]
        if literal == 'PSA_ERROR_INSUFFICIENT_MEMORY':
            psa=(args.idf/'components/mbedtls/mbedtls/tf-psa-crypto/include/psa/crypto_values.h').read_text()
            literal=re.search(r'^#define\s+PSA_ERROR_INSUFFICIENT_MEMORY\s+\(\(psa_status_t\)(-\d+)\)',psa,re.M)[1]
        assert re.fullmatch(r'-(?:0x[0-9a-fA-F]+|\d+)',literal), literal
        codes.write(f'#define {name} ({literal})\n')

(args.output/'mbedtls').mkdir(exist_ok=True)
(args.output/'mbedtls/ssl.h').write_text('''#pragma once
#include <stddef.h>
#include "esp_tls_errors.h"
typedef int mbedtls_ssl_context;
int __wrap_mbedtls_ssl_read(mbedtls_ssl_context *, unsigned char *, size_t);
''')

def linux(path):
    path=path.resolve()
    return '/mnt/'+path.drive[0].lower()+path.as_posix()[2:]
main=ROOT/'idf/esp32c3-oled-native/main'
binary=args.output/'test'
command=['wsl.exe','--exec','gcc','-std=c11','-Wall','-Wextra','-Werror','-g','-O1',
    '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
    '-I'+linux(args.output),'-I'+linux(main),'-I'+linux(parser),linux(args.output/'test.c'),
    linux(main/'stream_http_reader.c'),linux(main/'tls_stream_eof.c'),linux(parser/'http_parser.c'),
    '-o',linux(binary)]
build=subprocess.run(command,capture_output=True,text=True,timeout=120)
(args.output/'build.log').write_text(build.stdout+build.stderr)
if build.returncode:raise SystemExit(build.returncode)
run=subprocess.run(['wsl.exe','--exec',linux(binary)],capture_output=True,text=True,timeout=30)
(args.output/'run.log').write_text(run.stdout+run.stderr)
report=dict(result='PASS' if run.returncode==0 and 'STREAM_HTTP_READER_PASS' in run.stdout else 'FAIL',
    idf=str(args.idf), sdk_source_sha256=hashlib.sha256(sdk.read_bytes()).hexdigest(),
    extracted_function_sha256=hashlib.sha256(function.encode()).hexdigest(),
    sources_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (harness,main/'stream_http_reader.c',main/'stream_http_reader.h',main/'tls_stream_eof.c',Path(__file__))},
    tls_adapter_sha256=hashlib.sha256(tls_read.encode()).hexdigest(),
    parser_sha256=hashlib.sha256((parser/'http_parser.c').read_bytes()).hexdigest(),
    body_callbacks_sha256=hashlib.sha256(body.encode()).hexdigest(),
    completion_function_sha256=hashlib.sha256(complete.encode()).hexdigest(),
    scope='Real SDK HTTP read/completion functions, body callbacks and HTTP parser; scripted transport and header bookkeeping; actual radio guard under ASan/UBSan. TLS cryptography, TLS close alerts and hardware are not emulated.',
    output=run.stdout,returncode=run.returncode)
(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['result']=='PASS' else 1)
