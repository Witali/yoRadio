import hashlib,json,re,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
root=Path('.build/c3-web-wifi-probe-off').resolve();base=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-production-radio').resolve()
entry=next(v for v in json.loads((base/'compile_commands.json').read_text()) if Path(v['file']).name=='network_service.c')
output=root/'network_service.c.obj'
command,count=re.subn(r' -o (?:"[^"]+"|\S+)',lambda m:' -o "'+output.as_posix()+'"',entry['command']);assert count==1
assert '-MF ' not in command and ' -MD ' not in command
(root/'command.txt').write_text(command+'\n',encoding='utf-8')
r=subprocess.run(command,cwd=entry['directory'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(root/'compile.log').write_bytes(r.stdout);assert r.returncode==0,r.stdout.decode(errors='replace')
def sections(path):
    with path.open('rb') as f:return {s.name:hashlib.sha256(s.data()).hexdigest() for s in ELFFile(f).iter_sections() if s.name.startswith(('.text','.rodata','.bss','.data')) and s['sh_size']}
old=sections(base/'esp-idf/main/CMakeFiles/__idf_main.dir/network_service.c.obj');new=sections(output)
changes=[s for s in old.keys()|new.keys() if old.get(s)!=new.get(s)]
result=dict(result='PASS' if not changes else 'FAIL',sections=len(old),changes=changes,before=old,after=new,scope='Production-disabled diagnostic: network_service compiled with original production command/config; code/rodata/data/bss object sections compared')
(root/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert not changes
