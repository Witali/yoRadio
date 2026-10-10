"""Check FIR image, exact decoder objects, RAM/Flash placement and retained controls."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from elftools.elf.elffile import ELFFile

ROOT=Path('.build/c3-fir-20261009')
BUILD=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-fir32')
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-fir32')
OLD=Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-integer4')
BASE=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-flac-integer4')
OBJDUMP='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
sources=json.loads((ROOT/'source-hashes.json').read_text())
for name,digest in sources.items(): assert sha(Path(name))==digest,name
before,after=config(OLD/'sdkconfig'),config(ART/'sdkconfig')
changes={k:[before.get(k),after.get(k)] for k in before.keys()|after.keys() if before.get(k)!=after.get(k)}
assert changes=={k:[None,'y'] for k in ('CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION','CONFIG_YORADIO_PDM_INTEGER_FIR')},changes
commands=json.loads((BUILD/'compile_commands.json').read_text())
assert not any('flac_clz' in c['file'] for c in commands)

def objects(folder):
    paths=[]
    for pattern in ('flac_decoder.cpp.obj','custom_flac_adapter.cpp.obj','native_aac_decoder.c.obj','aac_*.c.obj'):
        paths+=list(folder.rglob(pattern))
    paths+=list((folder/'esp-idf/main/compact5').glob('*.obj'))
    result={}
    for path in paths:
        assert path.name not in result
        with path.open('rb') as stream:
            result[path.name]={s.name:dict(bytes=s['sh_size'],sha256=hashlib.sha256(s.data()).hexdigest())
                for s in ELFFile(stream).iter_sections() if s.name.startswith(('.text','.rodata')) and s['sh_size']}
    return result

codec=objects(BUILD)
assert len(codec)>=18 and codec==objects(BASE),'Codec arithmetic changed'
(ROOT/'codec-objects.json').write_text(json.dumps(codec,indent=2)+'\n')
elf_path=BUILD/'yoradio_esp32c3_oled_native.elf'
with elf_path.open('rb') as stream:
    elf=ELFFile(stream)
    sizes={s.name:s['sh_size'] for s in elf.iter_sections()
           if s.name.startswith(('.iram0.','.dram0.','.rtc.')) or s.name in ('.flash.text','.flash.rodata')}
    symbols={}
    for name,size,section in [('s_pcm_fir',136,'.dram0.bss'),('pcm_fir_coefficients',257*32*4,'.flash.rodata'),
                              ('pcm_fir_48k_coefficients',625*32*4,'.flash.rodata')]:
        found=elf.get_section_by_name('.symtab').get_symbol_by_name(name)
        assert len(found)==1 and found[0]['st_size']==size,name
        assert elf.get_section(found[0]['st_shndx']).name==section,name
        symbols[name]=dict(size=size,section=section,address=found[0]['st_value'])
rx=list(BUILD.rglob('esp_mbedtls_dynamic_impl.c.obj'));assert len(rx)==1
for tool,args,name in (
    ('tools/codec_benchmark/verify_aac_network_build.py',['--build',str(BUILD)],'aac'),
    ('tools/esp32c3_tests/verify_http_link.py',['--sdkconfig',str(BUILD/'sdkconfig'),'--elf',str(elf_path)],'http'),
    ('tools/esp32c3_tests/verify_adaptive_input_link.py',['--sdkconfig',str(BUILD/'sdkconfig'),'--elf',str(elf_path),'--tls-rx-object',str(rx[0])],'allocator')):
    with (ROOT/(name+'-audit.log')).open('xb') as log:
        subprocess.run([sys.executable,'-X','utf8',tool,*args,'--objdump',OBJDUMP,'--output',str(ROOT/(name+'-audit.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
output_object=list(BUILD.rglob('native_audio_output.c.obj'));assert len(output_object)==1
(ROOT/'output-disassembly.txt').write_bytes(subprocess.check_output([OBJDUMP,'-dr',str(output_object[0])]))
manifest=json.loads((ART/'manifest.json').read_text())
previous=json.loads((OLD/'manifest.json').read_text())
assert manifest['image']['sha256']==sha(ART/'app.bin') and manifest['image']['app_elf_sha256']==sha(elf_path)
assert manifest['image']['bytes']<=1900544
for key in ('extra_trust_ca_sha256','restoration_app_sha256','input_prefill_ms','input_prefill_min_ms'):
    manifest[key]=previous[key]
manifest.update(laboratory_only=True,production_qualified=False,hardware_tested=False,
    clock_mode='integer',integer_rate_compensation=True,fir_taps=32,fir_state_bytes=136,
    source_overlay_sha256=sources,bootloader_sha256=sha(ART/'bootloader.bin'),
    flac_input_extra_slots=4,source_note='FIR experiment; unchanged compact AAC/FLAC objects; inactive CLZ excluded.')
(ART/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result=dict(result='PASS',image=manifest['image'],sections=sizes,symbols=symbols,config_changes=changes,
    codec_objects=len(codec),codec_sections=sum(len(v) for v in codec.values()))
(ROOT/'build-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
