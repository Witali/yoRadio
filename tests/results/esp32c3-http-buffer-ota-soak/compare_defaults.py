import hashlib,json,re,sys
from pathlib import Path
root=Path(__file__).resolve().parent
standard=Path(sys.argv[1]) if len(sys.argv)>1 else Path('idf/esp32c3-oled-native/build-idf61-default-audit/sdkconfig')
tested=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-http-txrelease/sdkconfig')
def config(path):
    return dict(re.findall(r'^(CONFIG_\w+)=(.*)$',path.read_text(),re.M))
a,b=config(standard),config(tested)
changes={k:dict(standard=a.get(k,'n'),tested=b.get(k,'n')) for k in sorted(a.keys()|b.keys()) if a.get(k,'n')!=b.get(k,'n')}
result=dict(scope='Fresh build-production.ps1 reconfigure versus physically tested candidate; no new application build',
    standard_sha256=hashlib.sha256(standard.read_bytes()).hexdigest(),tested_sha256=hashlib.sha256(tested.read_bytes()).hexdigest(),changes=changes)
(root/(sys.argv[2] if len(sys.argv)>2 else 'default-config-diff.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
