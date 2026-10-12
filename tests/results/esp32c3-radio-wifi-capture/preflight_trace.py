import json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from web_tcp import parse
from common import fixtures
root=Path('.build/c3-radio-wifi-capture');p=root/'physical/performance.json'
if p.exists():
    rows=json.loads(p.read_text());frames=[];errors=[]
    for row in rows:
        try:
            value=parse(row)
            if value:frames.append(value)
        except ValueError as error:errors.append(str(error))
    print(json.dumps(dict(rows=len(rows),frames=len(frames),wifi=[f for f in frames if f['kind']=='wifi'],invalid=errors[:5]),indent=2))
specs=fixtures(Path('.build/c3-production-radio-opus/fixtures/manifest.json'))
wanted=('stress-opus-48000-2ch-16bit-90s','hev2-44100-stereo')
(root/'fixture-specs.json').write_text(json.dumps({k:{f:v for f,v in specs[k].items() if f!='data'} for k in wanted},indent=2)+'\n')
