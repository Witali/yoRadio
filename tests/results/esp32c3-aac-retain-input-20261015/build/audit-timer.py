import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
base=Path('.build/c3-aac-retain-input-20261015')
path=Path('idf/esp32c3-oled-native/build-aac-retain-lab-20261015/yoradio_esp32c3_oled_native.elf')
objdump='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
with path.open('rb') as f:
    elf=ELFFile(f);table=elf.get_section_by_name('.symtab');symbols={s.name:s for s in table.iter_symbols()}
    names=('dma_queue_overrun','esp_timer_get_time','esp_timer_impl_get_time','s_audio_pipeline_probe')
    info={}
    for name in names:
        symbol=symbols[name];section=elf.get_section(symbol['st_shndx']).name
        assert section==('.dram0.data' if name=='s_audio_pipeline_probe' else '.iram0.text'),(name,section)
        info[name]=dict(address=hex(symbol['st_value']),bytes=symbol['st_size'],section=section)
    assert info['s_audio_pipeline_probe']['bytes']==540
    assert info['esp_timer_get_time']['address']==info['esp_timer_impl_get_time']['address']
dis=subprocess.check_output([objdump,'-d','--disassemble=dma_queue_overrun',str(path)])
assert b'esp_timer_get_time' in dis or b'esp_timer_impl_get_time' in dis
(base/'timer-isr.disassembly.txt').write_bytes(dis)
(base/'timer-audit.json').write_text(json.dumps(dict(symbols=info,elf_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    scope='Linked ISR and system-timer alias reside in IRAM; diagnostic buffer is 540 DRAM bytes'),indent=2)+'\n')
print(json.dumps(info))
