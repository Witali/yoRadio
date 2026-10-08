import subprocess,sys
from pathlib import Path
root=Path('.build/c3-idf-head-20261008')
steps=[('build-qemu',['pwsh.exe','-NoProfile','-File',str(root/'build-qemu.ps1')]),('qemu-run',[sys.executable,'-X','utf8',str(root/'qemu-run.py'),'--version','6.1-9a97f6c54ec6']),('qemu-pcm',[sys.executable,'-X','utf8','.build/idf-upgrade/check-compact-pcm.py','--label','head9a97'])]
for name,command in steps:
 print('START',name,flush=True)
 with (root/(name+'.log')).open('xb') as log:
  code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1200).returncode
 print('END',name,code,flush=True)
 if code:raise SystemExit(code)
