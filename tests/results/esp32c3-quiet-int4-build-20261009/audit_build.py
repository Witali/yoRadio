"""Check the quiet candidate's configuration, allocator routes and full codecs."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from elftools.elf.elffile import ELFFile

ROOT=Path('.build/c3-quiet-int4-20261009')
BUILD=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-int4')
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-int4')
OLD=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-qio80')
LAB=Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-integer4')
BASE=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-min250')
OBJDUMP=Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
old,new,lab=map(lambda p:config(p/'sdkconfig'),(BASE,ART,LAB))
intended={'CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK':None, 'CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS':'4'}
changes={k:dict(before=old.get(k),after=new.get(k)) for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
assert set(changes)==set(intended),changes
assert all(new.get(k)==value for k,value in intended.items())
for key in ('CONFIG_YORADIO_CPU_PROFILE','CONFIG_YORADIO_CPU_PROFILE_HTTP',
    'CONFIG_YORADIO_NETWORK_HEAP_PROFILE','CONFIG_YORADIO_PIPELINE_PROFILE',
    'CONFIG_YORADIO_STAGED_DMA_PROFILE','CONFIG_YORADIO_PDM_CLOCK_DIAGNOSTICS',
    'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE','CONFIG_YORADIO_DEEP_SLEEP_CLOCK'):
    assert new.get(key)!='y',key
for key,value in dict(CONFIG_ESP_CONSOLE_NONE='y',CONFIG_LOG_MAXIMUM_LEVEL='0',
    CONFIG_ESPTOOLPY_FLASHMODE_QIO='y',CONFIG_ESPTOOLPY_FLASHFREQ_80M='y',
    CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL='y').items():assert new[key]==value
for key,value in new.items():
    if re.search(r'WIFI.*(?:SSID|PASSWORD)|PASSWORD|SECRET',key):
        assert value in ('""','n','0'),key
elf=BUILD/'yoradio_esp32c3_oled_native.elf'
manifest=json.loads((ART/'manifest.json').read_text())
assert manifest['image']['app_elf_sha256']==sha(elf)
assert manifest['image']['sha256']==sha(ART/'app.bin')
commands=json.loads((BUILD/'compile_commands.json').read_text())
assert not any('flac_clz' in c['file'] or 'flash_mode_probe' in c['file'] or 'native_audio_output_dma.c' in c['file'] for c in commands)
sections={}
with elf.open('rb') as stream:
    data=ELFFile(stream)
    symbols={s.name:s for s in data.get_section_by_name('.symtab').iter_symbols()}
    sections={s.name:dict(size=s['sh_size'],address=s['sh_addr']) for s in data.iter_sections()
              if s.name in ('.iram0.text','.dram0.data','.dram0.bss','.flash.text','.flash.rodata')}
    assert symbols['s_tls_large_storage']['st_size']==17058
    assert 'native_audio_output_flush_pcm' in symbols and 'native_audio_output_discard_pcm' in symbols
    for name in ('s_dma_write_profile','s_dma_queue_overruns','network_heap_profile_poll','cpu_profiler_task'):
        assert name not in symbols,name
bundle=BUILD/'esp-idf/mbedtls/x509_crt_bundle'
old_bundle=Path(json.loads((OLD/'manifest.json').read_text())['build_directory'])/'esp-idf/mbedtls/x509_crt_bundle'
assert bundle.read_bytes()==old_bundle.read_bytes(),'Trust bundle differs from normal roots'
app=(ART/'app.bin').read_bytes()
assert all(marker not in app for marker in (b'PERF FLOW_STAGED_OUT:',b'PERF STAGED_DMA:',b'PERF PDM_CLOCK:',b'FLASH_PROBE_ENV'))
disassembly=subprocess.check_output([str(OBJDUMP),'-d','--disassemble=output_task',str(elf)])
assert b'native_audio_output_flush_pcm' in disassembly and b'native_audio_output_discard_pcm' in disassembly
(ROOT/'output-task-disassembly.txt').write_bytes(disassembly)
objects=list(BUILD.rglob('esp_mbedtls_dynamic_impl.c.obj'));assert len(objects)==1
audits=[
 ('tools/codec_benchmark/verify_aac_network_build.py',['--build',str(BUILD)],'verify-aac'),
 ('tools/esp32c3_tests/verify_http_link.py',['--sdkconfig',str(ART/'sdkconfig'),'--elf',str(elf)],'verify-http'),
 ('tools/esp32c3_tests/verify_adaptive_input_link.py',['--sdkconfig',str(ART/'sdkconfig'),'--elf',str(elf),'--tls-rx-object',str(objects[0])],'verify-allocator')]
for script,extra,name in audits:
    with (ROOT/(name+'.log')).open('xb') as log:
        subprocess.run([sys.executable,'-X','utf8',script,*extra,'--objdump',str(OBJDUMP),
                        '--output',str(ROOT/(name+'.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
names=[n for n in json.loads((LAB/'manifest.json').read_text())['source_overlay_sha256'] if n.startswith('idf/')]
sources={n:sha(Path(n)) for n in names}
manifest.update(production_profile=True,production_qualified=False,hardware_tested=False,
    expected_flash_mode='qio',flash_mhz=80,deep_sleep=False,console_and_logs=False,
    lab_ca=False,normal_trust_bundle_sha256=sha(bundle),clock_mode='integer',flac_input_extra_slots=4,
    fractional_clock_analog_qualified=False,input_prefill_min_ms=250,input_prefill_ms=500,
    bootloader_sha256=sha(ART/'bootloader.bin'),source_overlay_sha256=sources,
    source_note='Inactive unrelated CLZ block; CLZ and Flash probe explicitly OFF.',
    qualification='Build and linked-code checks only; quiet public-station/OTA qualification pending.')
(ART/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result=dict(result='PASS',scope='Build/link provenance only, no physical or acoustic acceptance',
    image=manifest['image'],configuration_changes=changes,sections=sections,
    source_overlay_sha256=sources,normal_trust_bundle_sha256=sha(bundle))
(ROOT/'build-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(result=result['result'],image=result['image'],sections=sections),indent=2))
