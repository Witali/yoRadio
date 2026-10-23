import hashlib,json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
report={}
def diagnostic_key(d):
    path=d['file'].replace('\\','/')
    marker='/esp32-cyd-c3-review/'
    path=path.split(marker,1)[-1]
    return path,d['message'],d['check']
for board in ('cyd','c3'):
    current=root/f'.build/lint-{board}-ota-transfer-full/report.json'
    if not current.is_file():continue
    old=root/f'tests/results/native-web-transfer-20261018/lint-{board}/report.json'
    a=json.loads(current.read_text());b=json.loads(old.read_text())
    old_keys={diagnostic_key(d) for r in b['results'] for d in r['diagnostics']}
    groups={}
    new={}
    for r in a['results']:
        if 'native-httpd-rfc6455/' in r['file']:
            category='generated_sdk_overlay'
        else:
            category='project'
            path=root/r['file']
            assert hashlib.sha256(path.read_bytes()).hexdigest()==r['source_sha256'],r['file']
        group=groups.setdefault(category,{'units':0,'warnings':0,'errors':0})
        group['units']+=1
        for d in r['diagnostics']:
            group[d['severity']+'s']+=1
            key=diagnostic_key(d)
            if key not in old_keys:
                new.setdefault(key,[]).append({'unit':r['file'],'line':d['line'],'column':d['column']})
    assert a['complete'] and a['errors']==0
    report[board]={'passed':True,'counts':groups,'new_diagnostic_signatures':[{'file':k[0],'message':k[1],'check':k[2],'instances':v} for k,v in new.items()]}
(root/'.build/ota-lint-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
