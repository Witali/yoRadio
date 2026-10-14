import json,re
from pathlib import Path
def read(path):
    result={}
    for line in Path(path).read_text().splitlines():
        m=re.fullmatch(r'(CONFIG_\w+)=(.*)',line)
        n=re.fullmatch(r'# (CONFIG_\w+) is not set',line)
        if m:result[m[1]]=m[2]
        elif n:result[n[1]]='n'
    return result
old=read('firmware/development/esp32c3-idf61-continuous-confirm/sdkconfig')
new=read('firmware/development/esp32c3-idf61-confirm-probe/sdkconfig')
changes={k:[old.get(k),new.get(k)] for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
assert changes=={'CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC':['n','y']},changes
Path('.build/c3-confirm-probe-20261014/config-comparison.json').write_text(json.dumps(changes,indent=2)+'\n')
print('PASS: only PIPELINE_HEALTH_DIAGNOSTIC changed in sdkconfig')
