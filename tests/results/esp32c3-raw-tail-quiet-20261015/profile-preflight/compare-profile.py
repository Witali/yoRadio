import hashlib,json,re,sys
from pathlib import Path
def config(path):
    result={}
    for line in path.read_text().splitlines():
        if match:=re.fullmatch(r'(CONFIG_\w+)=(.*)',line):result[match[1]]=match[2]
        elif match:=re.fullmatch(r'# (CONFIG_\w+) is not set',line):result[match[1]]='n'
    return result
reference=Path('firmware/development/esp32c3-idf61-raw-tail-quiet/sdkconfig')
actual=Path(sys.argv[1]);out=Path(sys.argv[2])
a,b=config(reference),config(actual)
diff={key:dict(reference=a.get(key),actual=b.get(key)) for key in sorted(a.keys()|b.keys()) if a.get(key)!=b.get(key)}
record=dict(reference=str(reference),actual=str(actual),reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
    actual_sha256=hashlib.sha256(actual.read_bytes()).hexdigest(),reference_keys=len(a),actual_keys=len(b),differences=diff)
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
raise SystemExit(bool(diff))
