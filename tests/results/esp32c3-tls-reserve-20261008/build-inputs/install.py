import argparse
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board, require, exception_details
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image

p=argparse.ArgumentParser()
p.add_argument('--firmware',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
require(not a.output.exists(),'Preserve the existing report')
b=Board('http://192.168.100.4')
report={'result':'RUNNING','method':'native OTA application only'}
try:
    data=a.firmware.read_bytes();target=image_info(data)
    cfg=a.firmware.with_name('sdkconfig').read_text()
    require('CONFIG_YORADIO_QEMU=y' not in cfg and 'CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in cfg,'Use awake physical firmware')
    report['before']=b.info();report['target']=target
    require(len(data)<=report['before']['max_size'],'Image exceeds partition')
    report['phase']='stop-and-snapshot'
    b.stop()
    time.sleep(2)
    before=snapshot(b)
    slot='app0' if report['before']['partition']=='app1' else 'app1'
    started=time.monotonic()
    report['phase']='upload'
    status,body=upload(b.origin,multipart(data))
    report['http_status']=status
    require(status==200 and body==b'OK','OTA did not return OK')
    report['phase']='verify-boot'
    report['after']=wait_image(b,target['app_elf_sha256'],slot)
    report['elapsed_seconds']=time.monotonic()-started
    report['persistence']=verify_snapshot(b,before)
    report['status']=b.status();report['result']='PASS'
except Exception as error:
    report['result']='FAIL';report['exception']=exception_details(error)
    if isinstance(error,AssertionError):report['check']=str(error)
finally:
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps(report),flush=True)
sys.exit(0 if report['result']=='PASS' else 1)
