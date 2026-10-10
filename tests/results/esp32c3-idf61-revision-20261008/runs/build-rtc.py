import subprocess
from pathlib import Path
root = Path('.build/c3-idf-head-20261008')
with (root/'build-rtc32k.log').open('xb') as log:
    code = subprocess.run(['pwsh.exe', '-NoProfile', '-File', str(root/'build-rtc.ps1')], stdout=log, stderr=subprocess.STDOUT).returncode
raise SystemExit(code)
