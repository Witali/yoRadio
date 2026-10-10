"""Check the linked quiet callbacks, their IRAM placement and exact build identity."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent
BUILD=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-mpi-health')
BASE=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-frac4')
ELF=BUILD/'yoradio_esp32c3_oled_native.elf'
OBJDUMP='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
with ELF.open('rb') as f:
    elf=ELFFile(f);symbols={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
    callbacks={}
    for name in ('record_allocation_failure','esp_task_wdt_isr_user_handler'):
        symbol=symbols[name];section=elf.get_section(symbol['st_shndx']).name
        assert section.startswith('.iram0'),(name,section)
        callbacks[name]=dict(section=section,bytes=symbol['st_size'])
    state={n:symbols[n]['st_size'] for n in ('s_health_boot_id','s_allocation_failures','s_task_watchdog_events')}
    assert state==dict(s_health_boot_id=8,s_allocation_failures=4,s_task_watchdog_events=4)
    for name in ('s_previous','s_previous_count','s_previous_total','cpu_profiler_task','s_dma_write_profile'):
        assert name not in symbols,name
    assert 'health_handler' in symbols
    sections={s.name:s['sh_size'] for s in elf.iter_sections() if s.name.startswith(('.iram0.','.dram0.','.rtc.','.flash.'))}
with (BASE/ELF.name).open('rb') as f:
    before={s.name:s['sh_size'] for s in ELFFile(f).iter_sections() if s.name in sections}
delta={k:v-before.get(k,0) for k,v in sections.items() if v!=before.get(k,0)}
disassembly={}
for name in ('app_main','record_allocation_failure','esp_task_wdt_isr_user_handler','cpu_profiler_start'):
    text=subprocess.check_output([OBJDUMP,'-d','--disassemble='+name,str(ELF)],text=True)
    disassembly[name]=text
    (ROOT/(name+'.disassembly.txt')).write_text(text)
startup=disassembly['app_main'];names=('esp_crypto_mpi_lock_acquire','esp_crypto_mpi_lock_release','native_state_init','cpu_profiler_start')
positions=[startup.index('<'+name+'>') for name in names];assert positions==sorted(positions)
assert '<heap_caps_register_failed_alloc_callback>' in disassembly['cpu_profiler_start']
for name in ('record_allocation_failure','esp_task_wdt_isr_user_handler'):
    assert not any(marker in disassembly[name] for marker in ('<malloc>','<esp_log','<heap_caps_get','<printf>'))
result=dict(result='PASS',elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),
    callbacks=callbacks,counter_and_identity_bytes=state,section_changes=delta,calls_in_order=names,
    scope='IRAM callbacks and quiet linked build; target behavior still requires board tests')
(ROOT/'health-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
