import json,re
from pathlib import Path
base=Path('.build/c3-raw-tail-20261015')
def read(path):
    result={}
    for line in path.read_text().splitlines():
        match=re.fullmatch(r'(CONFIG_\w+)=(.*)',line)
        if match:result[match[1]]=match[2]
        match=re.fullmatch(r'# (CONFIG_\w+) is not set',line)
        if match:result[match[1]]='n'
    return result
old=read(Path('firmware/development/esp32c3-idf61-read512-diagnostic/sdkconfig'))
new=read(Path('firmware/development/esp32c3-idf61-raw-tail-diagnostic/sdkconfig'))
changes={k:[old.get(k),new.get(k)] for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)}
assert changes=={},changes
(base/'config-comparison.json').write_text(json.dumps(dict(result='PASS',changes=changes),indent=2)+'\n')
print(changes)
