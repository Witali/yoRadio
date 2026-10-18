"""Qualify frozen actual CYD upload and deferred reboot implementations.

Mapped filesystem/HTTP/RTOS seams exercise bounded production handlers with
ASan/UBSan. This does not establish physical flash durability or task timing.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32-cyd2usb-native/main'
SHARED = ROOT / 'idf/components/native_storage'
C3_MAIN = ROOT / 'idf/esp32c3-oled-native/main'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run
spec = importlib.util.spec_from_file_location('cyd_upload_functions', ROOT / 'tests/run-web-warning-regressions.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__), ROOT/'tests/native/cyd_upload_test.c', ROOT/'tests/native/cyd_upload_reboot_test.c',
             ROOT/'tests/native/cyd_upload_pair_test.c',
             ROOT/'tests/run-web-warning-regressions.py',
             C3_MAIN/'web_upload.c', C3_MAIN/'web_upload.h',
             *(MAIN/name for name in ['web_upload.c','web_upload.h','web_reboot.c','web_reboot.h',
                                      'network_service.c','network_service.h']),
             SHARED/'file_transaction.c', *(SHARED/'include'/name for name in
                 ['file_transaction.h','credential_line.h','web_file_form.h','web_multipart.h'])]
    hashes = {}
    for file in files:
        relative = file.relative_to(ROOT)
        data = file.read_bytes()
        hashes[relative.as_posix()] = hashlib.sha256(data).hexdigest()
        destination = out/'sources'/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    frozen = out/'sources'
    main = frozen/MAIN.relative_to(ROOT)
    shared = frozen/SHARED.relative_to(ROOT)
    strip_includes = lambda source: re.sub(r'^#include[^\n]*\n', '', source, flags=re.M)
    (out/'cyd-upload-production.inc').write_text(strip_includes((main/'web_upload.c').read_text()))
    (out/'c3-upload-production.inc').write_text(strip_includes((frozen/C3_MAIN.relative_to(ROOT)/'web_upload.c').read_text()))
    (out/'cyd-reboot-production.inc').write_text(strip_includes((main/'web_reboot.c').read_text()))
    network = (main/'network_service.c').read_text()
    (out/'cyd-wifi-production.inc').write_text(''.join(helpers.function(network,name) for name in
        ['network_service_storage_init','read_credentials','network_service_validate_credentials_file',
         'network_service_save_credentials_file','network_service_save_credentials']))
    report = {'passed':False, 'physical_hardware':False, 'sanitizers':['ASan','UBSan'],
              'source_sha256':hashes, 'variants':{}}
    for name in ['upload','upload-c3','reboot','pair']:
        binary = out/name
        test = frozen/'tests/native'/('cyd_upload_test.c' if name.startswith('upload') else 'cyd_upload_'+name+'_test.c')
        command = ['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
                   '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-pthread',
                   '-I'+host(out),'-I'+host(shared),'-I'+host(shared/'include'),host(test),'-o',host(binary)]
        if name=='upload-c3': command.insert(1,'-DTEST_C3_UPLOAD=1')
        for stage,args in [('build',command),('test',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
             'UBSAN_OPTIONS=halt_on_error=1','timeout','45',host(binary),host(out/'fs')])]:
            if stage=='test':(out/'fs').mkdir(exist_ok=True)
            try:
                log = run(args)
            except subprocess.CalledProcessError as error:
                (out/(name+'-'+stage+'.log')).write_bytes(error.output)
                print(error.output.decode(errors='replace'),file=sys.stderr)
                raise
            (out/(name+'-'+stage+'.log')).write_bytes(log)
        print(log.decode(),end='')
        report['variants'][name] = {'passed':True,'scenarios':int(re.search(rb': (\d+) scenarios',log)[1])}
    report['passed'] = True
    report['scope'] = ('Actual full CYD and C3 upload handlers and sink, shared multipart/form/transaction, actual CYD Wi-Fi persistence (also used as the explicit Wi-Fi API seam in the C3 upload leg); '
        'mapped host files with SPIFFS no-overwrite rename rule, HTTP fragmentation/errors/time budgets, bounded heap and IO faults. '
        'Radio candidate index preparation and reboot readiness/request are explicit seams in the upload leg. Actual pair publication/rollback and interruption states and actual reboot task qualified separately. '
        'No claim of multi-file publication atomicity, physical SPIFFS durability, Wi-Fi reconnection, or hardware timing.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
