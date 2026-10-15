import json,re
from pathlib import Path
base=Path('.build/c3-input-usage-20261015')
def cfg(path):
    s=Path(path).read_text();d=dict(re.findall(r'^(CONFIG_\w+)=(.+)$',s,re.M))
    d.update({k:'n' for k in re.findall(r'^# (CONFIG_\w+) is not set$',s,re.M)})
    d.setdefault('CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS','0');return d
old=cfg('firmware/development/esp32c3-idf61-confirm-tls-lab/sdkconfig')
new=cfg('firmware/development/esp32c3-idf61-input-usage-lab/sdkconfig')
diff={k:[old.get(k),new.get(k)] for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)}
assert diff=={},diff
(base/'config-comparison.json').write_text(json.dumps({'result':'PASS','differences':diff},indent=2)+'\n')
print(json.dumps(diff))
