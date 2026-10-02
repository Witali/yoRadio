"""Build the actual storage header with UBSan and an independent int64 oracle."""
from pathlib import Path
import os
import subprocess

ROOT=Path(__file__).resolve().parents[1]
if os.name=='nt':
    subprocess.run(['wsl.exe','--cd',str(ROOT),'--exec','python3','tests/run-aac-storage.py'],check=True)
else:
    out=ROOT/'.build/aac-storage-test';out.mkdir(parents=True,exist_ok=True)
    exe=out/'test'
    subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=undefined',
                    '-fno-sanitize-recover=all','-I'+str(ROOT/'idf/esp32c3-oled-native/main'),
                    str(ROOT/'tests/native/aac_storage_test.c'),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
