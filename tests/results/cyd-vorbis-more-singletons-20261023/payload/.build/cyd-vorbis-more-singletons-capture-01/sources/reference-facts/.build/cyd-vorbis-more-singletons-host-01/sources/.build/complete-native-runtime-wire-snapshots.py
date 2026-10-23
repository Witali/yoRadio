"""Add only hash-identified public source/report snapshots; never modify evidence."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'tests/results/native-runtime-transfer-20261018'
GROUPS={'time-wire-cyd':'cyd-time-wire-qualified-01',
        'wifi-wire-c3':'native-wifi-wire-qualified-c3',
        'wifi-wire-cyd-http':'native-wifi-wire-qualified-cyd-plain',
        'wifi-wire-cyd-tls':'native-wifi-wire-qualified-cyd-tls'}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text())
added=[]
def exact(source,relative,group,expected):
    assert source.is_file() and digest(source)==expected,(source,expected)
    assert source.suffix.lower() in {'.c','.h','.py','.json'},source
    assert b'-----BEGIN PRIVATE KEY-----\n' not in source.read_bytes()
    assert b'-----BEGIN RSA PRIVATE KEY-----\n' not in source.read_bytes()
    for base in [ROOT/'.build'/GROUPS[group],ARCHIVE/group]:
        target=base/relative
        if target.exists():assert target.read_bytes()==source.read_bytes(),target
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(source.read_bytes());added.append(str(target.relative_to(ROOT)))

ws=ROOT/'.build/ws-integration-qualified-final'
tls={target:ROOT/'.build'/('native-tls-ota-602' if target=='cyd' else 'native-tls-ota-611') for target in ['cyd','c3']}
wifi=ROOT/'.build/native-wifi-legacy-io-qualified'
for group in GROUPS:
    report=load(ARCHIVE/group/'report.json')
    if group=='time-wire-cyd':
        for relative,expected in report['tls_source_sha256'].items():
            exact(tls['cyd']/'sources'/relative,Path('tls-foundation-sources')/relative,group,expected)
        for name,expected in report['sdk_overlay']['generated_sha256'].items():
            exact(ws/'cyd/generated'/name,Path('composed/generated')/name,group,expected)
    else:
        for name,expected in report['input_report_sha256'].items():
            exact((wifi if name=='wifi' else ws)/'report.json',Path('foundation-reports')/(name+'.json'),group,expected)
        for variant,value in report['variants'].items():
            target=variant.split('-')[0]
            for name,expected in value['sdk_overlay']['generated_sha256'].items():
                exact(ws/target/'generated'/name,Path(variant)/'generated'/name,group,expected)
            if 'tls_report_sha256' in value:
                exact(tls[target]/'report.json',Path(variant)/'tls-foundation-report.json',group,value['tls_report_sha256'])
print('Added',len(added),'exact supplemental snapshots:',json.dumps(added,indent=2))
