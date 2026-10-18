"""Exercise actual CYD credential loading and the shared physical-row reader.

Uses mapped real stdio and cookie read fragmentation/errors with synthetic
fixtures. A pinned historical source proves the oversized-row regression.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'idf/esp32-cyd2usb-native/main'
SHARED=ROOT/'idf/components/native_storage/include/credential_line.h'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
spec=importlib.util.spec_from_file_location('web_warning_helpers',ROOT/'tests/run-web-warning-regressions.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--baseline',default='4d5d8e1812a2e7f04a04144e27aeb472b2446ebf')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    source=MAIN/'network_service.c'
    baseline=subprocess.check_output(['git','rev-parse',args.baseline],cwd=ROOT,text=True).strip()
    old=subprocess.check_output(['git','show',baseline+':'+source.relative_to(ROOT).as_posix()],cwd=ROOT).decode()
    (out/'baseline-network_service.c').write_text(old)
    current=source.read_text()
    test=ROOT/'tests/native/cyd_wifi_warning_test.c'
    report={'baseline_commit':baseline,'sanitizers':['ASan','UBSan'],'physical_tested':False,'variants':{}}
    for name,contents,negative in [('negative-old-source',old,True),('shared-reader',current,False)]:
        (out/'cyd-wifi-production.inc').write_text(helpers.function(contents,'read_credentials'))
        binary=out/name
        (out/(name+'-build.log')).write_bytes(run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(out),'-I'+host(SHARED.parent),host(test),'-o',host(binary)]))
        try:
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',
                     'timeout','30',host(binary),host(out/(name+'.csv'))]);passed=True
        except subprocess.CalledProcessError as error:log=error.output;passed=False
        (out/(name+'.log')).write_bytes(log)
        if negative:assert not passed,'Historical CYD reader unexpectedly accepted the rejection regression'
        else:assert passed,log.decode(errors='replace');print(log.decode(),end='')
        report['variants'][name]='DETECTED' if negative else 'PASS'
    files=[Path(__file__),test,source,SHARED,ROOT/'tests/run-web-warning-regressions.py']
    report['source_sha256']={path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    for path in files:
        snapshot=out/'sources'/path.relative_to(ROOT);snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(path.read_bytes())
    report['passed']=True
    report['scope']='Actual CYD first-valid credential reader and exact shared bounded row helper; mapped stdio/cookie IO seams, no Wi-Fi hardware or profile/reconnect/timing/power changes.'
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
