import json
from pathlib import Path
import time
from types import SimpleNamespace
from unittest.mock import patch
from failure_monitor import FailureMonitor

root = Path(__file__).resolve().parent/'monitor-test'
root.mkdir(exist_ok=False)
trace = root/'phase-request-phases.jsonl'
one = json.dumps(dict(request=1,phase='connect',winerror=10048,at=time.monotonic()))+'\n'
two = json.dumps(dict(request=1,phase='request_including_connect',winerror=10048,at=time.monotonic()))+'\n'
trace.write_text(one+two[:20])
calls = []
def capture(command,**kwargs):
    calls.append(command)
    Path(command[-1]).write_text('{}\n')
    return SimpleNamespace(returncode=0)
with patch('failure_monitor.subprocess.run',side_effect=capture):
    monitor = FailureMonitor(root)
    try:
        deadline = time.monotonic()+3
        while not calls and time.monotonic()<deadline: time.sleep(.02)
        assert len(calls)==1
        with trace.open('a') as output: output.write(two[20:])
        time.sleep(.5)
    finally: monitor.close()
assert len(calls)==1 and len(monitor.rows)==1
assert monitor.rows[0]['exists'] and monitor.rows[0]['code']==0
print('PASS: one snapshot per failed request, including partial JSONL writes')
