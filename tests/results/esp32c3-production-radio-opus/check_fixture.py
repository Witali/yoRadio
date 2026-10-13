import hashlib,json,subprocess
from pathlib import Path
root=Path('.build/c3-production-radio-opus');fixture=root/'fixtures/stress-opus-48000-2ch-16bit-90s.ogg';progress=root/'fixture-decode-progress.log'
r=subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(fixture),'-progress',str(progress),'-f','null','NUL'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=30)
values=dict(line.split('=',1) for line in progress.read_text().splitlines() if '=' in line)
seconds=float(values.get('out_time_us','0'))/1e6
result=dict(result='PASS' if r.returncode==0 and seconds>=90 and not r.stderr else 'FAIL',returncode=r.returncode,decoded_seconds=seconds,error_bytes=len(r.stderr),fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),scope='Complete encoded-fixture validation; no hardware PCM comparison')
(root/'fixture-reference.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
