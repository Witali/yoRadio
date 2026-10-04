import subprocess,sys
from pathlib import Path
root=Path.cwd()
name=sys.argv[1] if len(sys.argv)>1 else 'build-qemu-aac-asymmetric'
log=root/'.build/aac-network-memory'/f'{name}.log'
with log.open('wb') as out:
    result=subprocess.run(['pwsh.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',
        str(root/'idf/esp32c3-oled-native/build.ps1'),'-BuildDirectory',name,
        '-Sdkconfig',name+'/sdkconfig','-DependencyRoot','C:/Work/yoRadio/.idf','build'],
        stdout=out,stderr=subprocess.STDOUT)
print('\n'.join(log.read_text(encoding='utf-8',errors='replace').splitlines()[-17:]))
sys.exit(result.returncode)
