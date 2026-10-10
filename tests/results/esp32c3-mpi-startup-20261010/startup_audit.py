"""Check linked startup order and static memory changes."""
from pathlib import Path
import json,subprocess,hashlib
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent
OBJDUMP='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
def sizes(path):
    with path.open('rb') as stream:return {s.name:s['sh_size'] for s in ELFFile(stream).iter_sections() if s.name.startswith(('.rtc.','.iram0.','.dram0.','.flash.'))}
for name,base in (('mpi-probe','web-tcp-v2'),('mpi-frac4','frac4')):
    folder=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-'+name)
    elf=folder/'yoradio_esp32c3_oled_native.elf'
    if not elf.exists():continue
    control=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-'+base+'/yoradio_esp32c3_oled_native.elf')
    text=subprocess.check_output([OBJDUMP,'-d','--disassemble=app_main',str(elf)],text=True)
    out=ROOT/name;out.mkdir(exist_ok=True);(out/'startup.disassembly.txt').write_text(text)
    ordered=['esp_crypto_mpi_lock_acquire','esp_crypto_mpi_lock_release','native_state_init','cpu_profiler_start']
    positions=[text.index('<'+n+'>') for n in ordered];assert positions==sorted(positions)
    assert text.count('<esp_crypto_mpi_lock_acquire>')==text.count('<esp_crypto_mpi_lock_release>')==1
    after,before=sizes(elf),sizes(control)
    changes={k:after.get(k,0)-before.get(k,0) for k in sorted(after.keys()|before.keys()) if after.get(k)!=before.get(k)}
    assert not any(v for k,v in changes.items() if k.startswith(('.rtc.','.dram0.','.iram0.'))),changes
    result=dict(result='PASS',elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),control_elf_sha256=hashlib.sha256(control.read_bytes()).hexdigest(),
        calls_in_order=ordered,section_changes=changes,disassembly_sha256=hashlib.sha256((out/'startup.disassembly.txt').read_bytes()).hexdigest())
    (out/'startup-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(name,json.dumps(result))
