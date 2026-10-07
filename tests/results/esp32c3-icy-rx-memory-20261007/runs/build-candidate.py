import subprocess
from pathlib import Path
with Path('.build/c3-memory-20261007/build-candidate.log').open('xb') as log:
    result=subprocess.run(['pwsh.exe','-NoProfile','-File','.build/c3-memory-20261007/build-candidate.ps1'],stdout=log,stderr=subprocess.STDOUT)
print('CANDIDATE_BUILD_EXIT',result.returncode)
raise SystemExit(result.returncode)
