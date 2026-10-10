import hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
elf = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97f6c54ec6-rx6-reserve-floor/yoradio_esp32c3_oled_native.elf')
sdk = Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6')
tool = Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-addr2line.exe')
command = [str(tool), '-e', str(elf), '-a', '-f', '-i', '-C', '0x420823b2', '0x42082458']
resolved = subprocess.check_output(command, text=True)
inputs = ['components/riscv/include/esp_private/panic_reason.h',
          'components/lwip/lwip/src/core/ipv4/ip4.c']
result = dict(elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),
    command=command, resolved=resolved,
    sdk_inputs={name: hashlib.sha256((sdk/name).read_bytes()).hexdigest() for name in inputs},
    mcause='0xdeadc0de', interpretation='SDK software-written invalid cause, used for register dumps without a crash.',
    classification='Unresolved runtime diagnostic failure, consistent with nonfatal watchdog. No reason line captured; no allocation failure or reboot demonstrated.',
    evidence='extended/formats/performance.json')
(root/'flac-diagnostic.json').write_text(json.dumps(result, indent=2)+'\n')
print(resolved)
