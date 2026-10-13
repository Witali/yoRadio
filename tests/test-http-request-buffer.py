"""ASan/UBSan lifecycle tests using patched SDK sender and real header helpers."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from patch_http_request_buffer import patch,RELEASE
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--idf',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
sdk=a.idf/'components/esp_http_client'
raw=(sdk/'esp_http_client.c').read_bytes()
patched=patch(raw).decode()
try:patch(raw+b'\n/* unknown revision */')
except ValueError:pass
else:raise AssertionError('Unknown SDK accepted')
assert patch(raw.replace(b'\r\n',b'\n'))==patch(raw)
first=patched.index('static int http_client_prepare_first_line(')
end=patched.index('static esp_err_t esp_http_client_send_post_data(',first)
functions=patched[first:end]
harness=ROOT/'tests/native/http_request_buffer_test.c'
(a.output/'test.c').write_text(harness.read_text().replace('/* SDK_REQUEST_FUNCTIONS */',functions).replace('/* SDK_RELEASE_FUNCTION */',RELEASE))
(a.output/'esp_err.h').write_text('''#pragma once
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_NO_MEM 2
#define ESP_ERR_INVALID_ARG 3
#define ESP_ERR_INVALID_STATE 4
#define ESP_ERR_NOT_FOUND 5
''')
(a.output/'esp_log.h').write_text('''#pragma once
#include <stdio.h>
#include "esp_err.h"
#define unlikely(x) (x)
#define ESP_LOGD(tag,...) do { (void)(tag); if(0)printf(__VA_ARGS__); } while(0)
#define ESP_LOGE ESP_LOGD
#define ESP_LOGW ESP_LOGD
''')
(a.output/'esp_check.h').write_text('''#pragma once
#include "esp_log.h"
#define ESP_RETURN_ON_FALSE(x,code,tag,...) do { (void)(tag);if(!(x))return(code); } while(0)
''')
linux=lambda path:'/mnt/'+path.resolve().drive[0].lower()+path.resolve().as_posix()[2:]
binary=a.output/'test'
command=['wsl.exe','--exec','gcc','-std=gnu11','-Wall','-Wextra','-Werror','-g','-O1',
    '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
    '-I'+linux(a.output),'-I'+linux(sdk/'lib/include'),linux(a.output/'test.c'),
    linux(sdk/'lib/http_header.c'),linux(sdk/'lib/http_utils.c'),'-o',linux(binary)]
build=subprocess.run(command,capture_output=True,text=True,timeout=120)
(a.output/'build.log').write_text(build.stdout+build.stderr)
if build.returncode:print(build.stderr);raise SystemExit(build.returncode)
run=subprocess.run(['wsl.exe','--exec',linux(binary)],capture_output=True,text=True,timeout=30)
(a.output/'run.log').write_text(run.stdout+run.stderr)
report=dict(result='PASS' if run.returncode==0 and 'HTTP_REQUEST_BUFFER_PASS' in run.stdout else 'FAIL',
    output=run.stdout,returncode=run.returncode,sdk_sha256=hashlib.sha256(raw).hexdigest(),
    patched_sha256=hashlib.sha256(patched.encode()).hexdigest(),
    scope='Extracted SDK request sender and real SDK header/utilities; scripted transport and response-state transitions. No TLS or physical heap claim.')
(a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
raise SystemExit(0 if report['result']=='PASS' else 1)
