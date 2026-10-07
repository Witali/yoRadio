import json, sys, time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board, Report, check_certificate_rejection, fixtures, require, sha
from diagnostic import DiagnosticCapture
from ota import image_info, snapshot, verify_snapshot
from ota_diagnostic import serial_health
from audio_test_server.tls_records import RecordServer

root=Path('.build/c3-tls-records-20261007')
image=Path('firmware/development/esp32c3-idf-6.1-compact-icy-debug/app.bin')
cfg=image.with_name('sdkconfig').read_text()
require('CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y' not in cfg,'Use normal trust roots')
board=Board('http://192.168.100.4')
identity=board.info()
require(identity['app_elf_sha256']==image_info(image.read_bytes())['app_elf_sha256'],'Wrong control image')
settings=snapshot(board)
report=Report(root/'negative-ca/report.json',identity)
report.data.update(test_ca_sha256=sha((root/'trust/ca.pem').read_bytes()),image_sha256=sha(image.read_bytes()))
capture=DiagnosticCapture('COM9')
specs=fixtures()
try:
    with RecordServer('192.168.100.253',8772,{'hev2-44100-stereo':specs['hev2-44100-stereo']},
            root/'trust/server.pem',root/'trust/server.key',seconds=20,grow_seconds=10) as server:
        def reject():
            board.stop()
            started=time.monotonic()
            board.play('https://192.168.100.253:8772/small/hev2-44100-stereo','aac')
            samples=[]
            while time.monotonic()-started<12:
                samples.append(dict(seconds=time.monotonic()-started,**board.status()))
                time.sleep(.2)
            report.data.update(status=samples,server_events=server.events)
            require(not any(s['audio'] for s in samples),'Untrusted audio played')
            alerts=[e['tls_reason'] for e in server.events if 'tls_reason' in e]
            verified=check_certificate_rejection(alerts,capture.since(started))
            require(all(e['audio_bytes']==0 for e in server.events),'Untrusted audio transmitted')
            return dict(certificate_bundle_rejected=verified,tls_alerts=alerts)
        report.case('normal-firmware-rejects-lab-ca',reject)
finally:
    def restore():
        board.stop()
        return verify_snapshot(board,settings)
    report.case('restore-settings',restore)
    capture.close()
    (root/'negative-ca/performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n')
    report.case('serial-health',lambda: require(serial_health(capture.rows)['result']=='PASS','Serial fault'))
    report.save()
raise SystemExit(report.exit_code())
