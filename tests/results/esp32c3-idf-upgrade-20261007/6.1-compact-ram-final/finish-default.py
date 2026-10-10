"""Finish the chosen defaults after the separate RAM experiments release the board."""
import json, subprocess, sys, time
from pathlib import Path
root=Path('.build/idf-upgrade')
deadline=time.monotonic()+1200
while 'TLS_CHECK_COMPLETE' not in (root/'physical-6.1-compact-tls-check.log').read_text():
    if time.monotonic()>deadline:raise SystemExit('TLS test still owns board')
    time.sleep(5)
results=[]
def run(name,script,args,required=False,timeout=2400):
    print('START',name,flush=True)
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
    results.append(dict(name=name,code=code,command=command))
    (root/'physical-6.1-compact-finish.json').write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,code,flush=True)
    if required and code:raise SystemExit('Required phase failed: '+name)
image=Path('firmware/development/esp32c3-idf-6.1-compact-tls-production/app.bin')
run('install-6.1-compact-tls-production','.build/idf-upgrade/install.py',
    ['--firmware',image,'--output',root/'install-6.1-compact-tls-production.json'],True)
run('physical-6.1-compact-tls-quiet-check','.build/idf-upgrade/quiet-public.py',
    ['--firmware',image,'--case','groovesalad-64-aac','--case','groovesalad-16-aac',
     '--aac-reference-command',root/'faad-reference-command.json',
     '--output',root/'physical-6.1-compact-tls-quiet-check'])
image=Path('firmware/development/esp32c3-idf-6.1-compact-ram-profile/app.bin')
run('install-6.1-compact-ram-resume','.build/idf-upgrade/install.py',
    ['--firmware',image,'--output',root/'install-6.1-compact-ram-resume.json'],True)
(root/'hold-6.1-compact-ram').unlink()
run('physical-6.1-compact-ram-resumed-stage','.build/idf-upgrade/physical-stage.py',
    ['--version','6.1-compact-ram','--resume-public',
     '--matrix-recheck',root/'physical-6.1-compact-ram-eof-recheck/report.json',
     '--aac-reference-command',root/'faad-reference-command.json'],True,timeout=7200)
print('DEFAULT_QUALIFICATION_COMPLETE',flush=True)
