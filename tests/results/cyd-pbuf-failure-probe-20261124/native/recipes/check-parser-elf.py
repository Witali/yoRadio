from pathlib import Path
import hashlib,json,re,runpy,subprocess
root=Path.cwd();base=root/'.build/cpbuf24';elf=base/'sdk/legacy/compiled/yoradio_cyd2usb_native.elf'
assert hashlib.sha256(elf.read_bytes()).hexdigest()=='695ec4e4cd1e7647e3524fea480999ec582c28b81cf70ff5c04b3a4593b7c191'
bin=Path('C:/Work/yoRadio/.idf/tools-v6.0.2/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin')
objdump=bin/'xtensa-esp32-elf-objdump.exe';addr2line=bin/'xtensa-esp32-elf-addr2line.exe'
assert objdump.is_file()and addr2line.is_file()
r=subprocess.run([str(objdump),'-d','--disassemble=tcp_write',str(elf)],capture_output=True);assert r.returncode==0
m=re.search(rb'^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+(call8|callx8)\s+',r.stdout,re.M);assert m
pc=int(m[1],16);api=runpy.run_path(str(base/'analyse-pbuf-native.py'),run_name='actual_elf_test')
proof=api['inspect_pc'](pc,elf,addr2line,objdump,api['executable_sections'](elf.read_bytes()))
assert any(frame['function']=='tcp_write'for frame in proof['frames'])
out=base/'native-parser-elf-witness.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,scope='Parser/tool format witness at an actual tcp_write call, not an observed native pbuf failure.',elf=api['pin'](elf),source=api['pin'](base/'analyse-pbuf-native.py'),proof=proof),indent=2)+'\n')
print(json.dumps(dict(parser_real_elf_witness=True,instruction=proof['instruction']['mnemonic'],function='tcp_write')))
