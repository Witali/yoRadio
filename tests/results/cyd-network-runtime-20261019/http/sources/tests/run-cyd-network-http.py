"""Actual CYD network status/retry handlers with explicit HTTPD/snapshot seams.

This is handler semantics, not a TCP/parser/TLS or physical networking gate.
The permanent owner, SDK wrapper and wire foundations are qualified separately.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def host(path):
    text = Path(path).resolve().as_posix()
    return '/mnt/' + text[0].lower() + text[2:] if sys.platform == 'win32' else text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if sys.platform == 'win32':
        raise SystemExit(subprocess.call(['wsl.exe', '--exec', 'python3', host(__file__),
                                         '--output', host(args.output)]))
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    import resource
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    files = [Path(__file__), ROOT/'tests/native/cyd_network_http_test.c',
             ROOT/'tests/run-web-warning-regressions.py',
             ROOT/'tools/codec_benchmark/run_output_dma_host.py',
             ROOT/'idf/esp32-cyd2usb-native/main/web_service.c',
             ROOT/'idf/esp32-cyd2usb-native/main/network_status.h']
    hashes = {}
    for path in files:
        data=path.read_bytes(); relative=path.relative_to(ROOT)
        target=out/'sources'/relative; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
        hashes[relative.as_posix()]=hashlib.sha256(data).hexdigest()
    frozen=out/'sources'
    sys.path.insert(0,str(frozen/'tools/codec_benchmark'))
    spec=importlib.util.spec_from_file_location('extract',frozen/'tests/run-web-warning-regressions.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    web=(frozen/'idf/esp32-cyd2usb-native/main/web_service.c').read_text()
    unit=''.join(helper.function(web,name) for name in ['reconnect_handler','network_handler'])
    (out/'esp_err.h').write_text('#pragma once\ntypedef int esp_err_t;\n#define ESP_OK 0\n#define ESP_FAIL (-1)\n#define ESP_ERR_NOT_FOUND 0x105\n#define ESP_ERR_TIMEOUT 0x107\n#define ESP_ERR_INVALID_STATE 0x103\n')
    command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
        '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
        '-I'+str(out),'-I'+str(frozen/'idf/esp32-cyd2usb-native/main'),
        str(frozen/'tests/native/cyd_network_http_test.c'),'-o',str(out/'network-http')]

    def execute(name, source, assertion=None):
        (out/'production.inc').write_text(source)
        built=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/(name+'-build.log')).write_bytes(built.stdout);assert built.returncode==0,built.stdout.decode(errors='replace')
        result=subprocess.run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
            'UBSAN_OPTIONS=halt_on_error=1',str(out/'network-http')],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/(name+'.log')).write_bytes(result.stdout)
        assert b'ERROR: AddressSanitizer' not in result.stdout and b'runtime error:' not in result.stdout
        if assertion is None:
            assert result.returncode==0,result.stdout.decode(errors='replace')
            return result.stdout.decode()
        assert result.returncode!=0 and b'Assertion' in result.stdout and assertion.encode() in result.stdout,(name,result.stdout)
        return {'detected':True,'expected_assertion':assertion,'exit_code':result.returncode}

    positive=execute('positive',unit)
    parsed=[json.loads(line.split('=',1)[1]) for line in positive.splitlines() if line.startswith(('JSON=','JSON_MAX='))]
    assert len(parsed)==7 and parsed[-1]['rssi_age_ms']==2**64-1 and parsed[-1]['last_error']==-2**31
    controls={}
    mutations=[
        ('network_body_purge','return ESP_FAIL;','return ESP_OK;', 'network_handler(&request)==ESP_FAIL'),
        ('retry_body_purge','return ESP_FAIL;','return ESP_OK;', 'reconnect_handler(&request)==ESP_FAIL'),
        ('missing_no_store','httpd_resp_set_hdr(request, "Cache-Control", "no-store");','/* omitted cache policy */','status == 200 && no_store && json_type'),
        ('false_connected_claim','\\"accepted\\":true','\\"connected\\":true','strstr(response,"\\"accepted\\":true")'),
    ]
    for name,old,new,assertion in mutations:
        if name=='network_body_purge':
            first=helper.function(web,'reconnect_handler'); second=helper.function(web,'network_handler')
            assert old in second; changed=first+second.replace(old,new,1)
        elif name=='missing_no_store':
            changed=helper.function(web,'reconnect_handler')+helper.function(web,'network_handler').replace(old,new)
        else:
            assert old in unit; changed=unit.replace(old,new,1)
        controls[name]=execute(name,changed,assertion)
    (out/'production.inc').write_text(unit)
    (out/'report.json').write_text(json.dumps({'passed':True,'scope':__doc__,
        'source_sha256':hashes,'actual_handler_cases':16,'parsed_actual_json_responses':len(parsed),
        'sanitizers':['ASan','UBSan'],'physical_hardware':False,'negative_controls':controls},indent=2)+'\n')
    print(positive.splitlines()[-1]);print('PASS',len(controls),'exact semantic controls')


if __name__=='__main__': main()
