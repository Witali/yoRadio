import json,re
from pathlib import Path
base=Path('.build/c3-flac-input12-20261015')
def read(path):
    result={}
    for line in path.read_text().splitlines():
        match=re.fullmatch(r'(CONFIG_\w+)=(.*)',line)
        if match:result[match[1]]=match[2]
        match=re.fullmatch(r'# (CONFIG_\w+) is not set',line)
        if match:result[match[1]]='n'
    return result
old=read(Path('firmware/development/esp32c3-idf61-flac-output-diagnostic/sdkconfig'))
new=read(Path('firmware/development/esp32c3-idf61-flac-input12-diagnostic/sdkconfig'))
changes={k:[old.get(k),new.get(k)] for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)}
assert changes=={'CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS':['4','8']},changes
(base/'config-comparison.json').write_text(json.dumps(dict(result='PASS',changes=changes),indent=2)+'\n')
print(changes)
