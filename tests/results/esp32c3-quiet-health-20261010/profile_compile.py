"""Compile the changed profiler in its diagnostic configuration without altering that build."""
import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-mpi-frac4').resolve()
entries=json.loads((build/'compile_commands.json').read_text())
entry=next(e for e in entries if e['file'].endswith('cpu_profiler.c'))
output=root/'profiler-diagnostic.obj'
command,count=re.subn(r' -o \S+ ',lambda m:' -o "'+output.as_posix()+'" ',entry['command'])
assert count==1 and '-MF ' not in command and '-MD ' not in command
completed=subprocess.run(command,cwd=entry['directory'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
(root/'profiler-diagnostic-compile.log').write_bytes(completed.stdout)
assert completed.returncode==0,completed.returncode
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(result='PASS',scope='RV32 compile of changed source with diagnostic profiling enabled; no existing objects overwritten',
    command=command,source_sha256=sha(Path(entry['file'])),sdkconfig_sha256=sha(build/'sdkconfig'),object_sha256=sha(output))
(root/'profiler-diagnostic-compile.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: diagnostic profiler translation unit compiled with the pinned RV32 toolchain')
