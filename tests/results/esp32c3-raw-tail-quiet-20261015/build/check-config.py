import json,re
from pathlib import Path
base=Path('.build/c3-raw-tail-quiet-20261015')
def read(path):
    result={}
    for line in path.read_text().splitlines():
        match=re.fullmatch(r'(CONFIG_\w+)=(.*)',line)
        if match:result[match[1]]=match[2]
        match=re.fullmatch(r'# (CONFIG_\w+) is not set',line)
        if match:result[match[1]]='n'
    return result
old=read(Path('firmware/development/esp32c3-idf61-input-tail-quiet/sdkconfig'))
new=read(Path('firmware/development/esp32c3-idf61-raw-tail-quiet/sdkconfig'))
changes={k:[old.get(k),new.get(k)] for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)}
assert changes=={'CONFIG_YORADIO_STREAM_READ_BYTES':[None,'2048'], 'CONFIG_YORADIO_STREAM_READ_TIMEOUT_MS':[None,'250']},changes
(base/'config-comparison.json').write_text(json.dumps(dict(result='PASS',changes=changes),indent=2)+'\n')
print(changes)
