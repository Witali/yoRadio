import hashlib,json,re,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent
BUILD=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-output-health')
BASE=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-mpi-health')
OBJDUMP='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
name='yoradio_esp32c3_oled_native.elf'
def inspect(path):
    with path.open('rb') as f:
        elf=ELFFile(f)
        sections={s.name:s['sh_size'] for s in elf.iter_sections() if s.name.startswith(('.iram0.','.dram0.','.rtc.','.flash.'))}
        symbols={s.name:dict(bytes=s['st_size'],section=elf.get_section(s['st_shndx']).name if type(s['st_shndx']) is int else s['st_shndx']) for s in elf.get_section_by_name('.symtab').iter_symbols()}
        return sections,symbols
sections,symbols=inspect(BUILD/name)
before,_=inspect(BASE/name)
assert symbols['dma_queue_overrun']['section'].startswith('.iram0')
assert symbols['s_dma_overruns']['section'].startswith('.dram0')
assert symbols['s_dma_write_errors']['section'].startswith('.dram0')
assert symbols['s_dma_overruns']['bytes']==symbols['s_dma_write_errors']['bytes']==4
assert 's_dma_write_profile' not in symbols and 'cpu_profiler_task' not in symbols
code=subprocess.check_output([OBJDUMP,'-d','--disassemble=dma_queue_overrun',str(BUILD/name)],text=True)
(ROOT/'dma_queue_overrun.disassembly.txt').write_text(code)
instructions=[line.split('\t')[-1] for line in code.splitlines() if re.match(r'^\s*[0-9a-f]+:\s',line)]
# A leaf RV32 ISR: loads/stores/arithmetic/ret, no function calls or tail calls.
assert instructions
assert not re.search(r'\b(?:jal|jalr|call|tail|j)\s',code),code
getcode=subprocess.check_output([OBJDUMP,'-d','--disassemble=native_audio_output_health',str(BUILD/name)],text=True)
(ROOT/'native_audio_output_health.disassembly.txt').write_text(getcode)
result=dict(result='PASS',elf_sha256=hashlib.sha256((BUILD/name).read_bytes()).hexdigest(),
    output_symbols={key:symbols[key] for key in ('dma_queue_overrun','s_dma_overruns','s_dma_write_errors','native_audio_output_health')},
    section_deltas={key:value-before.get(key,0) for key,value in sections.items() if value!=before.get(key,0)},
    scope='Linked state, IRAM and leaf callback; hardware timing still requires physical test')
(ROOT/'output-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
