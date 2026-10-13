import subprocess,difflib
from pathlib import Path
objdump='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
base=Path('idf/esp32c3-oled-native')
a=base/'build-idf-6.1-r9a97-quiet-http-txrelease';b=base/'build-idf-6.1-r9a97-production-radio'
rel='esp-idf/esp_http_client/CMakeFiles/__idf_esp_http_client.dir/__/__/yoradio_http/esp_http_client.c.obj'
outputs=[]
for root in (a,b):
    text=subprocess.check_output([objdump,'-dr','--section=.text.http_on_body',str(root/rel)],text=True)
    outputs.append(text.splitlines()[3:])
diff='\n'.join(difflib.unified_diff(*outputs,fromfile='tested',tofile='production'))
Path('.build/c3-production-radio/http-body-diff.txt').write_text(diff)
print(diff)
print('SDK overlay source equal:',(a/'yoradio_http/esp_http_client.c').read_bytes()==(b/'yoradio_http/esp_http_client.c').read_bytes())
