import json,subprocess,sys,time
from pathlib import Path
control=Path('.build/c3-retained-tls-20261008/physical/final-board.json')
deadline=time.monotonic()+1800
print('Waiting for control firmware restoration',flush=True)
while not control.exists():
    if time.monotonic()>deadline:raise SystemExit('Control restoration did not finish; no board actions taken')
    time.sleep(10)
assert json.loads(control.read_text())['result']=='PASS'
raise SystemExit(subprocess.run([sys.executable,'-X','utf8','.build/c3-idf-head-20261008/physical.py']).returncode)
