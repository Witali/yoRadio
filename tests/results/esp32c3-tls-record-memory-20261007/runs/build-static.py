import subprocess
from pathlib import Path
with Path('.build/c3-tls-records-20261007/build-static.log').open('xb') as log:
    result=subprocess.run(['pwsh.exe','-NoProfile','-File','.build/c3-tls-records-20261007/build-static.ps1'],stdout=log,stderr=subprocess.STDOUT)
print('STATIC_BUILD_EXIT',result.returncode)
raise SystemExit(result.returncode)
