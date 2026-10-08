import hashlib,json,re,subprocess
from pathlib import Path
root=Path('.build/c3-flac-watchdog-20261008')
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97f6c54ec6-rx6-reserve-profile')
elf=build/'yoradio_esp32c3_oled_native.elf'
obj='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
symbols=subprocess.check_output([obj,'-t',str(elf)],text=True)
handler=subprocess.check_output([obj,'-d','--disassemble=esp_task_wdt_isr_user_handler',str(elf)],text=True)
caller=subprocess.check_output([obj,'-d','--disassemble=task_wdt_isr',str(elf)],text=True)
assert re.search(r'\.iram0.text\s+00000010 esp_task_wdt_isr_user_handler',symbols)
assert re.search(r'\.dram0.data\s+00000004 s_task_watchdog_events',symbols)
assert not re.search(r'\b(?:call|jal|jalr)\b',handler)
assert '<esp_task_wdt_isr_user_handler>' in caller
(root/'watchdog-linked.txt').write_text(handler+'\n'+caller)
(root/'watchdog-link.json').write_text(json.dumps(dict(result='PASS',elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),handler_iram_bytes=16,counter_dram_bytes=4,handler_calls=[],sdk_isr_calls_handler=True),indent=2)+'\n')
print('PASS watchdog IRAM, DRAM and SDK ISR call audit')
