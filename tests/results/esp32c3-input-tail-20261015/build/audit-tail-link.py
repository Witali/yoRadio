import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
base=Path('.build/c3-input-tail-20261015')
elf=Path('idf/esp32c3-oled-native/build-input-tail-lab-20261015/yoradio_esp32c3_oled_native.elf')
objdump='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
dis=subprocess.check_output([objdump,'-d','--disassemble=stream_route_emit',str(elf)])
assert b'<adaptive_input_reopen_tail>' in dis
(base/'tail-link.disassembly.txt').write_bytes(dis)
with elf.open('rb') as f:
    e=ELFFile(f);sym=next(s for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='adaptive_input_reopen_tail')
    section=e.get_section(sym['st_shndx']).name
    assert section=='.flash.text'
    result=dict(result='PASS',elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),
                function_bytes=sym['st_size'],section=section,caller='stream_route_emit')
(base/'tail-link.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
