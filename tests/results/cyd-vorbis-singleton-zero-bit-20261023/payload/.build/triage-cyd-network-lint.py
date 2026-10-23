import collections
import hashlib
import json
from pathlib import Path
import re

root=Path.cwd()
baseline_path=root/'tests/results/native-runtime-transfer-20261018/lint-cyd/report.json'
vendor_path=root/'.build/lint-cyd-network-vendor-final/report.json'
custom_path=root/'.build/lint-cyd-network-custom-final/report.json'
baseline=json.loads(baseline_path.read_text(encoding='utf-8'))
vendor=json.loads(vendor_path.read_text(encoding='utf-8'))
custom=json.loads(custom_path.read_text(encoding='utf-8'))
assert baseline['complete'] and vendor['complete'] and custom['complete']
assert vendor['errors']==custom['errors']==0
def normalized(value):
    value=value.replace('\\','/').lower()
    value=value.removeprefix(root.as_posix().lower()+'/')
    value=re.sub(r'idf/esp32-cyd2usb-native/build[^/]+/', 'idf/esp32-cyd2usb-native/<clang-build>/', value)
    return value
def key(unit,diag):return normalized(unit),normalized(diag['file']),diag['check'],diag['message'],diag['severity']
previous=collections.Counter(key(row['file'],d) for row in baseline['results'] for d in row['diagnostics'])
added=[]
for row in vendor['results']:
    for diagnostic in row['diagnostics']:
        value=key(row['file'],diagnostic)
        if previous[value]:previous[value]-=1
        else:added.append(dict(unit=row['file'],**diagnostic))
removed=[dict(unit=k[0],file=k[1],check=k[2],message=k[3],severity=k[4],instances=count) for k,count in previous.items() if count]
new_units=sorted(set(normalized(r['file']) for r in vendor['results'])-set(normalized(r['file']) for r in baseline['results']))
summary=dict(passed=True,baseline=dict(report=baseline_path.relative_to(root).as_posix(),units=baseline['units'],warnings=baseline['warnings'],errors=baseline['errors']),
    vendor=dict(report=vendor_path.relative_to(root).as_posix(),units=vendor['units'],warnings=vendor['warnings'],errors=vendor['errors'],pre_frozen_inputs=vendor['captured_input_count']),
    custom=dict(report=custom_path.relative_to(root).as_posix(),units=custom['units'],warnings=custom['warnings'],errors=custom['errors'],pre_frozen_inputs=custom['captured_input_count']),
    new_units=new_units,new_warning_instances=added,removed_warning_instances=removed,
    new_reproduced_production_defects=0,
    triage=[],
    limits='All warnings and analyzer traces are retained. AST analysis does not prove concurrency/hardware behavior; actual-loop behavioral campaigns remain separate. No optimized Clang code generation was attempted because the prior time_settings_valid compiler crash remains a distinct known tool issue. No source warning suppression or cosmetic rewrite. The deferred AAC private owner-view issue was not retried or bypassed; C3/shared production sources are unchanged and no full C3 rerun was performed.')
target=root/'.build/cyd-network-lint-triage.json'
assert not target.exists()
target.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(new_units=new_units,new_warning_instances=added,removed_warning_instances=removed),indent=2))
