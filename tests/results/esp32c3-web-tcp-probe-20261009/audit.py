"""Check the actual linked diagnostic routes and unchanged AAC/FLAC objects."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,'tools/esp32c3_tests')
from ota import image_info
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
config = lambda p: dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
build = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-web-tcp-probe')
baseline = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-flac-retained-owner')
artifact = Path('firmware/development/esp32c3-idf-6.1-r9a97-web-tcp-probe')
old = Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-retained-owner')
before, after = config(old/'sdkconfig'), config(artifact/'sdkconfig')
changes = {k:[before.get(k),after.get(k)] for k in before.keys()|after.keys() if before.get(k)!=after.get(k)}
assert changes == {'CONFIG_YORADIO_WEB_TCP_PROBE':[None,'y']},changes
elf = build/'yoradio_esp32c3_oled_native.elf'
image = image_info((artifact/'app.bin').read_bytes())
assert image['app_elf_sha256'] == sha(elf)
commands = json.loads((build/'compile_commands.json').read_text())
assert sum(c['file'].endswith('web_tcp_probe.c') for c in commands) == 1
assert not any('flac_clz' in c['file'] for c in commands)
objdump='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
disassembly=subprocess.check_output([objdump,'-d',str(elf)],text=True)
functions=dict(re.findall(r'^[0-9a-f]+ <([^>]+)>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',disassembly,re.M|re.S))
out=ROOT/'audit'
out.mkdir(exist_ok=False)
routes={}
for target in ('__wrap_tcp_input','tcp_input','__wrap_ip4_output_if','ip4_output_if','web_tcp_probe_poll','network_heap_profile_poll'):
    callers=[name for name,body in functions.items() if '<'+target+'>' in body]
    assert callers,target
    routes[target]=callers
    for name in callers:
        (out/(name+'.txt')).write_text(functions[name])
assert 'ip4_input' in routes['__wrap_tcp_input'],routes
assert routes['tcp_input']==['__wrap_tcp_input'],routes
assert '__wrap_ip4_output_if' in routes['ip4_output_if'],routes
assert any(n.startswith('tcp_') for n in routes['__wrap_ip4_output_if']),routes
assert routes['web_tcp_probe_poll']==['status_task'],routes
assert routes['network_heap_profile_poll']==['web_tcp_probe_poll'],routes

def sections(path):
    with path.open('rb') as stream:
        return {s.name:s['sh_size'] for s in ELFFile(stream).iter_sections()
                if s.name.startswith(('.iram0.','.dram0.','.rtc.')) or s.name in ('.flash.text','.flash.rodata')}

def codec_objects(directory):
    paths=[]
    for pattern in ('flac_decoder.cpp.obj','custom_flac_adapter.cpp.obj','native_aac_decoder.c.obj','aac_*.c.obj'):
        paths+=list(directory.rglob(pattern))
    paths+=list((directory/'esp-idf/main/compact5').glob('*.obj'))
    result={}
    for path in paths:
        assert path.name not in result
        with path.open('rb') as stream:
            result[path.name]={s.name:dict(bytes=s['sh_size'],sha256=hashlib.sha256(s.data()).hexdigest())
                               for s in ELFFile(stream).iter_sections()
                               if s.name.startswith(('.text','.rodata')) and s['sh_size']}
    return result

objects=codec_objects(build)
assert len(objects)>=18 and objects==codec_objects(baseline),'Codec arithmetic changed'
(out/'codec-objects.json').write_text(json.dumps(objects,indent=2)+'\n')
prev, current=sections(baseline/elf.name),sections(elf)
delta={k:current.get(k,0)-prev.get(k,0) for k in prev.keys()|current.keys()}
assert delta['.rtc.data']==1024,delta
rx=list(build.rglob('esp_mbedtls_dynamic_impl.c.obj'));assert len(rx)==1
for tool,args,name in (
    ('tools/codec_benchmark/verify_aac_network_build.py',['--build',str(build)],'aac'),
    ('tools/esp32c3_tests/verify_http_link.py',['--sdkconfig',str(build/'sdkconfig'),'--elf',str(elf)],'http'),
    ('tools/esp32c3_tests/verify_adaptive_input_link.py',['--sdkconfig',str(build/'sdkconfig'),'--elf',str(elf),'--tls-rx-object',str(rx[0])],'allocator')):
    with (out/(name+'.log')).open('xb') as log:
        subprocess.run([sys.executable,'-X','utf8',tool,*args,'--objdump',objdump,'--output',str(out/(name+'.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
manifest=json.loads((artifact/'manifest.json').read_text())
previous=json.loads((old/'manifest.json').read_text())
for k in ('laboratory_only','production_qualified','flac_input_extra_slots','heap_owner_probe','clock_mode',
          'input_prefill_ms','input_prefill_min_ms','extra_trust_ca_sha256','restoration_app_sha256'):
    manifest[k]=previous[k]
manifest.update(web_tcp_probe=True,source_overlay_sha256=json.loads((ROOT/'sources.json').read_text()),
                bootloader_sha256=sha(artifact/'bootloader.bin'),
                source_note='Default-off TCP metadata diagnostic, existing WS task sampler. No codec arithmetic changes; inactive CLZ not compiled.')
(artifact/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result=dict(result='PASS',image=image,config_changes=changes,sections=current,section_size_delta=delta,
            routes=routes,codec_objects=len(objects),codec_sections=sum(len(v) for v in objects.values()))
(ROOT/'build-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
