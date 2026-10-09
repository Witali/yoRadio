"""Audit the PCM-tail candidate against the completed prefill control."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from elftools.elf.elffile import ELFFile

sys.path.insert(0,'tools/esp32c3_tests')
from ota import image_info

ROOT=Path('.build/c3-pcm-tail-board-20261009')
BUILD=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-pcm-tail')
ARTIFACT=Path('firmware/development/esp32c3-idf-6.1-r9a97-pcm-tail')
CONTROL=Path('firmware/development/esp32c3-idf-6.1-r9a97-input-prefill500')
OBJDUMP=Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
old,new=config(CONTROL/'sdkconfig'),config(ARTIFACT/'sdkconfig')
changes={k:dict(before=old.get(k),after=new.get(k)) for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
assert not changes,changes
image=image_info((ARTIFACT/'app.bin').read_bytes())
elf=BUILD/'yoradio_esp32c3_oled_native.elf'
assert image['app_elf_sha256']==sha(elf)
commands=json.loads((BUILD/'compile_commands.json').read_text())
assert not any('flac_clz' in c['file'] for c in commands)
with elf.open('rb') as f:
    sections={s.name:dict(size=s['sh_size'],address=s['sh_addr']) for s in ELFFile(f).iter_sections()
              if s.name in ('.iram0.text','.dram0.data','.dram0.bss','.flash.text','.flash.rodata')}
inputs=('idf/esp32c3-oled-native/main/audio_service.c',
        'idf/esp32c3-oled-native/main/native_audio_output.c',
        'idf/esp32c3-oled-native/main/native_audio_output.h',
        'idf/esp32c3-oled-native/main/native_audio_output_qemu.c',
        'idf/esp32c3-oled-native/main/Kconfig.projbuild',
        'idf/esp32c3-oled-native/main/CMakeLists.txt',
        'idf/esp32c3-oled-native/sdkconfig.input-prefill.defaults',
        'tools/audio_test_server/generate_pcm_tails.py','tools/esp32c3_tests/pcm_tail.py',
        'tests/test-pcm-tail.py')
source_hashes={p:sha(Path(p)) for p in inputs}
host=json.loads((ROOT/'host-profile/report.json').read_text())
assert all(sha(Path(p))==v for p,v in host['sources'].items())
assert host['pcm_identical'] and host['staged_profile_pcm_identical'] and host['profile_pcm_identical']
for name in ('output_task','native_audio_output_flush_pcm','native_audio_output_discard_pcm'):
    code=subprocess.check_output([str(OBJDUMP),'-d','-S','--disassemble='+name,str(elf)])
    (ROOT/(name+'-disassembly.txt')).write_bytes(code)
    assert ('<'+name+'>:').encode() in code,name
    if name=='output_task':
        assert b'native_audio_output_flush_pcm' in code and b'native_audio_output_discard_pcm' in code
    elif name=='native_audio_output_flush_pcm':
        assert b'pdm_write_block' in code or b'i2s_channel_write' in code
assert b'PERF PCM_END: generation=' in (ARTIFACT/'app.bin').read_bytes()
assert b'PERF PCM_FLUSH: frames=' in (ARTIFACT/'app.bin').read_bytes()
for tool,extra,name in [
    ('tools/codec_benchmark/verify_aac_network_build.py',['--build',str(BUILD)],'verify-aac.json'),
    ('tools/esp32c3_tests/verify_http_link.py',['--sdkconfig',str(BUILD/'sdkconfig'),'--elf',str(elf)],'verify-http.json')]:
    with (ROOT/(name+'.log')).open('xb') as log:
        subprocess.run([sys.executable,'-X','utf8',tool,*extra,'--objdump',str(OBJDUMP),
                        '--output',str(ROOT/name)],stdout=log,stderr=subprocess.STDOUT,check=True)
manifest=json.loads((ARTIFACT/'manifest.json').read_text())
manifest.update(laboratory_only=True,production_qualified=False,input_prefill_ms=500,
    clock_mode='fractional',control_app_sha256=sha(CONTROL/'app.bin'),
    source_overlay_sha256=source_hashes,bootloader_sha256=sha(ARTIFACT/'bootloader.bin'),
    source_note='Unrelated main CMake CLZ changes are inactive; no CLZ source compiled.',
    extra_trust_ca_sha256='5d07cd4783170ceeb5933e41a9618d7c0775567f7e9307d8478390cf3f526de8',
    restoration_app_sha256='21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a',
    qualification='Full build, PCM parity/profile host tests and linked output/AAC/HTTP audits; physical tests pending')
(ARTIFACT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result=dict(result='PASS',image=image,configuration_changes=changes,
            sections=sections,source_overlay_sha256=source_hashes)
(ROOT/'build-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
