import hashlib,json,re,subprocess
from pathlib import Path
root=Path.cwd()
build=root/'idf/esp32c3-oled-native/build-aac-low-production'
old=root/'firmware/development/esp32c3-aac-smoothing-history/sdkconfig'
new=root/'firmware/development/esp32c3-aac-low-workspace/sdkconfig'
def options(p):
    return dict(re.findall(r'^(CONFIG_\w+)=(.*)$',p.read_text(),re.M))
before,after=options(old),options(new)
changed={k:[before.get(k),after.get(k)] for k in sorted(before.keys()|after.keys()) if before.get(k)!=after.get(k)}
assert changed=={'CONFIG_YORADIO_AAC_LOW_WORKSPACE':[None,'y']},changed
binutils=root.parent.parent/'.idf/tools-v6.0.2/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin'
binutils=Path('C:/Work/yoRadio/.idf/tools-v6.0.2/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin')
elf=build/'yoradio_esp32c3_oled_native.elf'
symbols=subprocess.check_output([str(binutils/'riscv32-esp-elf-nm.exe'),'--defined-only',str(elf)],text=True)
excluded=('aac_pointer_audit','low_workspace_report','aac_high_history_test_interleave','qemu_aac')
assert all(name not in symbols for name in excluded)
assert '__wrap_compact5_sbr_dec' in symbols
disassembly=subprocess.check_output([str(binutils/'riscv32-esp-elf-objdump.exe'),'-d',
    '--disassemble=__wrap_compact5_sbr_dec',str(elf)],text=True)
out=root/'.build/aac-low-production'
(out/'physical-low-wrapper.asm').write_text(disassembly,encoding='utf-8',newline='\n')
report=dict(config_changes=changed,absent_test_symbols=list(excluded),
            elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),
            wrapper_disassembly_sha256=hashlib.sha256((out/'physical-low-wrapper.asm').read_bytes()).hexdigest(),
            sdkconfig_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),
            source_commit='327d32c21607a7ff3e9d590ed6891a4021189036')
(out/'build-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(report,indent=2))
