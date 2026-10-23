from pathlib import Path
import hashlib,json,subprocess,sys
root=Path.cwd();out=root/'.build/cyd-flac-runtime-qualified-final'; binary=out/'task'
meta=(out/'metadata.flac').read_bytes()[:1077]; (out/'metadata-only.flac').write_bytes(meta); (out/'empty.pcm').write_bytes(b'')
rows=[]
for schedule in [0,1,127,2048]:
 h=lambda p:'/mnt/c/'+p.resolve().as_posix()[3:]
 command=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','90',h(binary),h(out/'metadata-only.flac'),h(out/'empty.pcm'),'24','2','pcm',str(schedule)]
 result=subprocess.run(['wsl.exe','--exec']+command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
 (out/('metadata-only-'+str(schedule)+'.log')).write_bytes(result.stdout)
 assert result.returncode==0,result.stdout.decode(errors='replace')
 rows.append(dict(schedule=schedule,command=command,exit_code=result.returncode))
(out/'metadata-only-boundaries.json').write_text(json.dumps(dict(passed=True,scope='Complete metadata-only EOF lifecycle controls for the same frozen task/adapter/core binary, in addition to 4304 truncated metadata schedules.',primary_report_sha256=hashlib.sha256((out/'report.json').read_bytes()).hexdigest(),metadata_bytes=len(meta),metadata_sha256=hashlib.sha256(meta).hexdigest(),checks=rows),indent=2)+'\n')
print('PASS four complete metadata-only EOF controls')
