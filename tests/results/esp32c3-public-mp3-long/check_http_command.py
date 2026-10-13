import hashlib,json,subprocess
from pathlib import Path
root=Path('.build/c3-mp3-long')
progress=root/'http-command-check-progress.log'
command=['ffmpeg','-nostdin','-v','error','-rw_timeout','15000000','-i','http://ice5.somafm.com/groovesalad-256-mp3','-t','3','-vn','-progress',str(progress),'-f','null','NUL']
r=subprocess.run(command,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=30)
values=dict(line.split('=',1) for line in progress.read_text().splitlines() if '=' in line)
seconds=float(values.get('out_time_us','0'))/1e6
result=dict(result='PASS' if r.returncode==0 and seconds>=3 and not r.stderr else 'FAIL',returncode=r.returncode,decoded_seconds=seconds,error_bytes=len(r.stderr),error_sha256=hashlib.sha256(r.stderr).hexdigest(),scope='HTTP FFmpeg command check only; no concurrent board HTTP comparison',correction='Only add tls_verify for HTTPS input')
(root/'http-command-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
