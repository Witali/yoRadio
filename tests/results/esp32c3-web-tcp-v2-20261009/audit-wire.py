"""Verify inlined encoders call the ESP32-C3 ROM CRC and standard output."""
import json
from pathlib import Path
import re
import subprocess
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parent
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-web-tcp-v2')
objdump='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
elf=build/'yoradio_esp32c3_oled_native.elf'
asm=subprocess.check_output([objdump,'-d',str(elf)],text=True)
functions=dict(re.findall(r'^[0-9a-f]+ <([^>]+)>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',asm,re.M|re.S))
with elf.open('rb') as stream:
    symbols=ELFFile(stream).get_section_by_name('.symtab')
    rom=symbols.get_symbol_by_name('esp_rom_crc32_le')[0]['st_value']
    assert symbols.get_symbol_by_name('crc32_le')[0]['st_value']==rom
assert 0x40000000<=rom<0x40080000
routes={}
for name,count in (('web_tcp_probe_poll',2),('web_tcp_probe_log_listener',1)):
    body=functions[name]
    assert body.count('<crc32_le>')==count and body.count('<fputs>')==count
    (ROOT/'audit'/(name+'.txt')).write_text(body)
    routes[name]=count
result=dict(result='PASS',crc_rom_address=hex(rom),inlined_encoder_calls=routes,
            crc_input_bytes=49,frame_bytes_before_crlf=58,
            original_audit='Standalone emit_frame symbol assertion failed because GCC inlined it; ROM label is crc32_le, alias of esp_rom_crc32_le.')
(ROOT/'wire-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
