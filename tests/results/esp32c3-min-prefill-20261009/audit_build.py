"""Audit the exact minimum-prefill experimental image before physical installation."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from elftools.elf.elffile import ELFFile

sys.path.insert(0,'tools/esp32c3_tests')
from ota import image_info
ROOT=Path('.build/c3-min-prefill-20261009')
BUILD=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-prefill-min250')
ARTIFACT=Path('firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250')
CONTROL=Path('firmware/development/esp32c3-idf-6.1-r9a97-staged-flow')
OBJDUMP=Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
old,new=config(CONTROL/'sdkconfig'),config(ARTIFACT/'sdkconfig')
changes={k:dict(before=old.get(k),after=new.get(k)) for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
assert changes=={'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS':{'before':None,'after':'250'}},changes
image=image_info((ARTIFACT/'app.bin').read_bytes())
elf=BUILD/'yoradio_esp32c3_oled_native.elf'
assert image['app_elf_sha256']==sha(elf)
commands=json.loads((BUILD/'compile_commands.json').read_text())
assert not any('flac_clz' in c['file'] for c in commands)
assert not any('native_audio_output_dma.c' in c['file'] for c in commands)
with elf.open('rb') as f:
    data=ELFFile(f)
    sections={s.name:dict(size=s['sh_size'],address=s['sh_addr']) for s in data.iter_sections()
              if s.name in ('.iram0.text','.dram0.data','.dram0.bss','.flash.text','.flash.rodata')}
    symbols={s.name for s in data.get_section_by_name('.symtab').iter_symbols()}
assert 'native_i2s_take_wait_profile' not in symbols
app=(ARTIFACT/'app.bin').read_bytes()
assert b'PERF FLOW_STAGED_OUT:' in app and b'PERF FLOW_DEC:' in app
assert b'PERF FLOW_OUT:' not in app
code=subprocess.check_output([str(OBJDUMP),'-d','-S','--disassemble=output_task',str(elf)])
(ROOT/'output-task-disassembly.txt').write_bytes(code)
assert b'native_audio_output_flush_pcm' in code and b'native_audio_output_discard_pcm' in code
host=json.loads((ROOT/'host-min-prefill/report.json').read_text())
assert all(v['result']=='PASS' for v in host['variants'].values())
assert all(sha(Path(p))==v for p,v in host['source_sha256'].items())
inputs=('idf/esp32c3-oled-native/main/audio_service.c',
        'idf/esp32c3-oled-native/main/native_audio_output.c',
        'idf/esp32c3-oled-native/main/native_audio_output.h',
        'idf/esp32c3-oled-native/main/pipeline_profile.h',
        'idf/esp32c3-oled-native/main/pipeline_wait.h',
        'idf/esp32c3-oled-native/main/Kconfig.projbuild',
        'idf/esp32c3-oled-native/main/CMakeLists.txt')
source_hashes={p:sha(Path(p)) for p in inputs}
for tool,extra,name in [
    ('tools/codec_benchmark/verify_aac_network_build.py',['--build',str(BUILD)],'verify-aac.json'),
    ('tools/esp32c3_tests/verify_http_link.py',['--sdkconfig',str(BUILD/'sdkconfig'),'--elf',str(elf)],'verify-http.json')]:
    with (ROOT/(name+'.log')).open('xb') as log:
        subprocess.run([sys.executable,'-X','utf8',tool,*extra,'--objdump',str(OBJDUMP),
                        '--output',str(ROOT/name)],stdout=log,stderr=subprocess.STDOUT,check=True)
manifest=json.loads((ARTIFACT/'manifest.json').read_text())
manifest.update(laboratory_only=True,production_qualified=False,input_prefill_ms=500,input_prefill_min_ms=250,
    clock_mode='fractional',control_app_sha256=sha(CONTROL/'app.bin'),
    source_overlay_sha256=source_hashes,bootloader_sha256=sha(ARTIFACT/'bootloader.bin'),
    source_note='Unrelated CLZ CMake block is inactive; no CLZ source compiled.',
    extra_trust_ca_sha256='5d07cd4783170ceeb5933e41a9618d7c0775567f7e9307d8478390cf3f526de8',
    restoration_app_sha256='21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a',
    qualification='Build and 88 host minimum-prefill checks; full AAC and HTTP link audit; physical measurements pending')
(ARTIFACT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result=dict(result='PASS',image=image,configuration_changes=changes,
            sections=sections,source_overlay_sha256=source_hashes)
(ROOT/'build-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
