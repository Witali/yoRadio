import subprocess,sys
from pathlib import Path
base=Path('.build/c3-raw-tail-quiet-20261015')
with (base/'build.log').open('wb') as log:
    p=subprocess.run(['pwsh.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(base/'build.ps1')],stdout=log,stderr=subprocess.STDOUT)
print('Build exit',p.returncode,flush=True)
if p.returncode:
    print((base/'build.log').read_text(errors='replace')[-1800:]);sys.exit(p.returncode)
for name in ('package.py','check-config.py'):
    subprocess.run([sys.executable,'-B','-X','utf8',str(base/name)],check=True)
