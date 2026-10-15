import hashlib,json,subprocess,sys
from pathlib import Path
root=Path('.build/c3-flac-tcp-20261015/host');root.mkdir(parents=True,exist_ok=True)
rows=[]
for name in ('test-audio-server-nodelay.py','test-audio-delivery-stats.py','test-audio-server-pauses.py','test-audio-server-pacing.py'):
    source=Path('tests')/name
    p=subprocess.run([sys.executable,'-B',str(source)],capture_output=True)
    (root/(name+'.log')).write_bytes(p.stdout+p.stderr)
    rows.append(dict(test=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),exit_code=p.returncode))
    print(name,p.returncode,flush=True)
(root/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
raise SystemExit(any(r['exit_code'] for r in rows))
