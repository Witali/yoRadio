import json,re,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parent
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-pipeline-probe')
path=build/'yoradio_esp32c3_oled_native.elf'
objdump='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
names=('dma_queue_overrun','esp_timer_impl_get_time','systimer_hal_get_counter_value','systimer_ticks_to_us')
result={}
with path.open('rb') as f:
    elf=ELFFile(f);symbols={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
    assert 'CONFIG_ESP_TIMER_IN_IRAM=y' in (build/'sdkconfig').read_text()
    assert symbols['esp_timer_get_time']['st_value']==symbols['esp_timer_impl_get_time']['st_value']
    for name in names:
        sym=symbols[name]
        address=sym['st_value'];section=sym['st_shndx']
        section_name=elf.get_section(section).name if type(section) is int else section
        assert section_name=='.iram0.text' or (section_name=='SHN_ABS' and 0x40000000<=address<0x40080000),(name,section_name,address)
        result[name]=dict(address=hex(address),bytes=sym['st_size'],section=section_name)
        raw=subprocess.check_output([objdump,'-d','--disassemble='+name,str(path)])
        (root/(name+'-walltime.txt')).write_bytes(raw)
        if name=='dma_queue_overrun':
            assert b'esp_timer_impl_get_time' in raw or b'esp_timer_get_time' in raw
            assert b'csrr' not in raw
sdk=Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6')
source=sdk/'components/esp_timer/src/esp_timer_impl_systimer.c'
assert '.ticks_to_us = systimer_ticks_to_us,' in source.read_text()
(root/'sdk-timer-source.c').write_bytes(source.read_bytes())
(root/'timer-audit.json').write_text(json.dumps(dict(result='PASS',symbols=result,
    scope='Linked overrun and hardware timer read in IRAM/ROM; conversion function assigned by SDK source'),indent=2)+'\n')
print(json.dumps(result))
