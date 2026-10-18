"""Compile actual CYD time HTTP handlers and settings/NVS transaction code.

HTTPD response/query/session cleanup and service snapshots are explicit seams.
No request-body receive seam is provided: these query-only routes must never
read or let HTTPD purge a supplied body. Host seams do not qualify SDK timing.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host

def stripped(path): return re.sub(r'^\s*#\s*include[^\n]*\n','',path.read_text(),flags=re.M)
def run(command):
    result=subprocess.run((['wsl.exe','--exec'] if sys.platform=='win32' else [])+command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
    return result.returncode,result.stdout
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    main=ROOT/'idf/esp32-cyd2usb-native/main';test=ROOT/'tests/native';shared=ROOT/'idf/components/native_time/include/native_time_sntp.h'
    files=[Path(__file__).resolve(),test/'cyd_web_time_test.c',test/'cyd_time_platform.h',test/'native_time_platform.h',shared,
           *[main/name for name in ('time_settings.c','time_settings.h','time_service.h','web_time.c','web_time.h')],ROOT/'idf/components/native_stream/include/json_buffer.h']
    hashes={f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    for f in files:
        target=out/'sources'/f.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes())
    (out/'headers.inc').write_text(stripped(shared)+stripped(main/'time_settings.h')+stripped(main/'time_service.h'))
    (out/'settings.inc').write_text(stripped(main/'time_settings.c'))
    source=stripped(main/'web_time.c');(out/'web_time.inc').write_text(source)
    command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+host(out),'-I'+host(test),'-I'+host(ROOT/'idf/components/native_stream/include'),host(test/'cyd_web_time_test.c')]
    report={'passed':False,'scope':__doc__,'physical_hardware':False,'command':command,
            'source_sha256':hashes,'cases':{},'positive_checks':0,'json_responses':0,'negative_controls':{}}
    def build(name):
        binary=out/name;code,log=run(command+['-o',host(binary)]);(out/(name+'-build.log')).write_bytes(log)
        if code:raise RuntimeError(log.decode(errors='replace'))
        return binary
    binary=build('http')
    for case in ('get','valid','invalid','body','boundaries','save_errors','response_errors'):
        code,log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case]);(out/(case+'.log')).write_bytes(log)
        if code:raise RuntimeError(case+': '+log.decode(errors='replace'))
        for line in log.decode().splitlines():
            if line.startswith('JSON '):json.loads(line[5:]);report['json_responses']+=1
        report['positive_checks']+=int(re.search(rb'PASS [a-z_]+: (\d+) checks',log).group(1))
        report['cases'][case]=log.decode().strip()
    mutations={
        'accept_duplicate':(' || (seen & (1U << index))','', 'invalid','!strcmp(status,"400 Bad Request")'),
        'accept_nul':('if (!value || value < 0x20U || value == 0x7fU ||','if ((value && value < 0x20U) || value == 0x7fU ||','invalid','!strcmp(status,"400 Bad Request")'),
        'skip_persist_error':('if (result != ESP_OK)\n        return reply(request, "500','if (false)\n        return reply(request, "500','save_errors','strcmp(status,"200 OK")'),
        'false_clock':('} else json_buffer_raw(&output, "null,\\\"local_time\\\":null");','} else json_buffer_raw(&output, "0,\\\"local_time\\\":null");','get','strstr(response, "\\\"utc_epoch\\\":null")'),
        'sdk_body_purge':('    return ESP_FAIL;\n}\n\nstatic int hex_value','    return ESP_OK;\n}\n\nstatic int hex_value','body','result == ESP_FAIL && close_calls == 1 && close_header && graceful'),
    }
    for name,(old,new,case,assertion) in mutations.items():
        assert source.count(old)==1,name;(out/'web_time.inc').write_text(source.replace(old,new));bad=build(name)
        code,log=run(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(bad),case]);(out/(name+'.log')).write_bytes(log)
        assert code and b'Assertion' in log and assertion.encode() in log,(name,log)
        assert b'ERROR: AddressSanitizer' not in log and b'runtime error:' not in log,(name,log)
        report['negative_controls'][name]={'rejected':True,'case':case,'status':code,'expected_assertion':assertion}
    (out/'web_time.inc').write_text(source)
    report['source_files_still_match_snapshot']=all(hashlib.sha256(f.read_bytes()).hexdigest()==hashes[f.relative_to(ROOT).as_posix()] for f in files)
    assert report['source_files_still_match_snapshot'];report['passed']=True
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(report['cases']),'groups +',len(mutations),'exact semantic mutants')
if __name__=='__main__':main()
