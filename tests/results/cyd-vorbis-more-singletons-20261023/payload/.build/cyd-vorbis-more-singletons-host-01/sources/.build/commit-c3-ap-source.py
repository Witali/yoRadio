from pathlib import Path
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[1]
def git(*args):
    return subprocess.check_output(['git','-c','core.longpaths=true',*args],cwd=root,text=True).strip()
assert not git('diff','--cached','--name-only'), 'Preserve pre-existing staging'
groups = ['c3-ap-timeout-final-02','c3-ap-regression-power-01',
          'c3-ap-regression-time-settings-01','c3-ap-regression-bootstrap-02',
          'c3-ap-regression-wifi-01','c3-ap-regression-time-service-01',
          'c3-ap-regression-websocket-01','c3-ap-reboot-leases-01']
for group in groups:
    report = json.loads((root/'.build'/group/'report.json').read_text())
    assert report['passed'], group
    for path, expected in report['source_sha256'].items():
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==expected,(group,path)
review=json.loads((root/'.build/c3-ap-independent-review-01/review.json').read_text())
assert review['result'].startswith('No actionable correctness regression')
assert not review.get('final_test_report_pending',True)
lint=json.loads((root/'.build/lint-c3-ap-timeout-01/report.json').read_text())
assert lint['complete'] and lint['errors']==0 and lint['all_inputs_unchanged_after_analysis']
paths = ['idf/esp32c3-oled-native/main/network_service.c',
         'idf/esp32c3-oled-native/main/runtime_settings.c',
         'idf/esp32c3-oled-native/main/runtime_settings.h',
         'tests/run-c3-ap-timeout.py',
         *['tests/native/c3_ap_timeout/'+name for name in ('platform.h','platform.c','test.c','README.md')],
         'tests/native/network_power/test.c','tests/native/network_power/README.md',
         'tests/native/cyd_time_events_test.c','tests/run-network-power.py','tests/run-cyd-time-events.py']
git('add','--',*paths)
assert set(git('diff','--cached','--name-only').splitlines())==set(paths)
git('diff','--cached','--check')
print(git('commit','-m','Guard C3 AP timeout with current settings and restart ownership'))
print('Committed',git('rev-parse','HEAD'))
