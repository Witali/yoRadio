import hashlib, json, re, subprocess
from pathlib import Path
root=Path('.build/c3-memory-20261007')
project=Path('idf/esp32c3-oled-native')
tool=Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin')
def settings(path):
    return {line.split('=',1)[0]:line for line in path.read_text().splitlines()
            if line.startswith('CONFIG_') or line.startswith('# CONFIG_')}
def build(name):
    directory=project/name
    elf=directory/'yoradio_esp32c3_oled_native.elf'
    symbols=subprocess.check_output([tool/'riscv32-esp-elf-nm.exe','-S',elf],text=True)
    size=subprocess.check_output([tool/'riscv32-esp-elf-size.exe','-A',elf],text=True)
    rows={}
    for line in size.splitlines():
        fields=line.split()
        if len(fields)==3 and fields[0].startswith('.'):rows[fields[0]]=int(fields[1])
    return dict(elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),sections=rows,
        icy_symbols=[l for l in symbols.splitlines() if re.search(r'\bs_icy_',l)])
old=build('build-idf-6.1-compact-ram-production')
new=build('build-idf-6.1-compact-icy-quiet')
old_config=settings(Path('firmware/development/esp32c3-idf-6.1-compact-ram-http-production/sdkconfig'))
new_config=settings(Path('firmware/development/esp32c3-idf-6.1-compact-icy-quiet/sdkconfig'))
differences={k:[old_config.get(k),new_config.get(k)] for k in old_config.keys()|new_config.keys() if old_config.get(k)!=new_config.get(k)}
result=dict(old=old,new=new,config_differences=differences,
    bss_saved=old['sections']['.dram0.bss']-new['sections']['.dram0.bss'],
    note='Symbol-size difference is distinct from aligned BSS/linker capacity. Builds use identical flags.' if not differences else 'Configuration differs; no isolated memory claim.')
(root/'icy-size.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('old','new')}))
print(old['icy_symbols'],new['icy_symbols'])
control=settings(Path('firmware/development/esp32c3-idf-6.1-memory-control-profile/sdkconfig'))
copy=settings(Path('firmware/development/esp32c3-idf-6.1-memory-rxcopy-profile/sdkconfig'))
differences={k:[control.get(k),copy.get(k)] for k in control.keys()|copy.keys() if control.get(k)!=copy.get(k)}
(root/'rx-config-diff.json').write_text(json.dumps(differences,indent=2)+'\n')
print('RX config differences',json.dumps(differences))
