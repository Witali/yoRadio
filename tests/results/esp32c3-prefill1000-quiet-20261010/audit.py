"""Audit configuration isolation, full codecs and allocation routes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from elftools.elf.elffile import ELFFile

p=argparse.ArgumentParser();p.add_argument('--target',choices=['quiet-prefill1000'],required=True);a=p.parse_args()
ROOT=Path('.build/c3-prefill1000-quiet-20261010')
lab=False
baseline='quiet-mpi-health'
BUILD=Path(f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-{a.target}')
BASE=Path(f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-{baseline}')
ART=Path(f'firmware/development/esp32c3-idf-6.1-r9a97-{a.target}')
OLD=Path(f'firmware/development/esp32c3-idf-6.1-r9a97-{baseline}')
OUT=ROOT/a.target;OUT.mkdir(exist_ok=True)
OBJDUMP='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
sources=json.loads((ROOT/'source-hashes.json').read_text())
for name,digest in sources.items():assert sha(Path(name))==digest,name
before,after=config(OLD/'sdkconfig'),config(ART/'sdkconfig')
changes={k:[before.get(k),after.get(k)] for k in before.keys()|after.keys() if before.get(k)!=after.get(k)}
assert changes=={'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS':['250','1000'],'CONFIG_YORADIO_INPUT_PREFILL_MS':['500','1000']},changes
for key in ('CONFIG_YORADIO_PDM_INTEGER_FIR','CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION','CONFIG_YORADIO_DEEP_SLEEP_CLOCK'):
    assert after.get(key)!='y',key
commands=json.loads((BUILD/'compile_commands.json').read_text())
assert not any('flac_clz' in c['file'] or 'native_audio_output_dma.c' in c['file'] for c in commands)

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
assert len(codec)>=18 and codec==objects(BASE),'Decoder arithmetic changed'
(OUT/'codec-objects.json').write_text(json.dumps(codec,indent=2)+'\n')
elf_path=BUILD/'yoradio_esp32c3_oled_native.elf'
with elf_path.open('rb') as stream:
    elf=ELFFile(stream)
    sizes={s.name:s['sh_size'] for s in elf.iter_sections()
           if s.name.startswith(('.iram0.','.dram0.','.rtc.')) or s.name in ('.flash.text','.flash.rodata')}
    symbols={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
    assert symbols['s_tls_large_storage']['st_size']==17058
    for name in ('s_audio_pipeline_probe','s_pcm_fir','pcm_fir_coefficients','pcm_fir_48k_coefficients'):assert name not in symbols
rx=list(BUILD.rglob('esp_mbedtls_dynamic_impl.c.obj'));assert len(rx)==1
for tool,args,name in (
    ('tools/codec_benchmark/verify_aac_network_build.py',['--build',str(BUILD)],'aac'),
    ('tools/esp32c3_tests/verify_http_link.py',['--sdkconfig',str(BUILD/'sdkconfig'),'--elf',str(elf_path)],'http'),
    ('tools/esp32c3_tests/verify_adaptive_input_link.py',['--sdkconfig',str(BUILD/'sdkconfig'),'--elf',str(elf_path),'--tls-rx-object',str(rx[0])],'allocator')):
    with (OUT/(name+'-audit.log')).open('xb') as log:
        subprocess.run([sys.executable,'-X','utf8',tool,*args,'--objdump',OBJDUMP,'--output',str(OUT/(name+'-audit.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
bundle=BUILD/'esp-idf/mbedtls/x509_crt_bundle'
assert bundle.read_bytes()==(BASE/'esp-idf/mbedtls/x509_crt_bundle').read_bytes()
manifest=json.loads((ART/'manifest.json').read_text())
previous=json.loads((OLD/'manifest.json').read_text())
assert manifest['image']['sha256']==sha(ART/'app.bin') and manifest['image']['app_elf_sha256']==sha(elf_path)
assert manifest['image']['bytes']<=1900544
for key,value in after.items():
    if re.search(r'WIFI.*(?:SSID|PASSWORD)|PASSWORD|SECRET',key):assert value in ('""','n','0'),key
if not lab:
    assert after['CONFIG_ESP_CONSOLE_NONE']=='y' and after['CONFIG_LOG_MAXIMUM_LEVEL']=='0'
    assert after.get('CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE')!='y'
    for name in ('s_dma_write_profile','s_dma_queue_overruns','network_heap_profile_poll','cpu_profiler_task'):assert name not in symbols
    assert not any('boot_probe.c' in c['file'] for c in commands)
    app=(ART/'app.bin').read_bytes()
    assert all(marker not in app for marker in (b'PERF FLOW_STAGED_OUT:',b'PERF STAGED_DMA:',b'PERF PDM_CLOCK:',b'FLASH_PROBE_ENV'))
manifest.update(laboratory_only=lab,production_profile=not lab,production_qualified=False,hardware_tested=False,
    clock_mode='fractional',integer_rate_compensation=False,fir=False,nominal_pcm_output_hz=48000,
    source_overlay_sha256=sources,bootloader_sha256=sha(ART/'bootloader.bin'),
    restoration_app_sha256='798f8c312bfcea37206908ee7ae13f88d8d821f9642fd3fb0846186f3411ccde',
    flac_input_extra_slots=4,input_prefill_min_ms=1000,input_prefill_ms=1000,
    tls_rx_reserve_bytes=17058,deep_sleep=False,expected_flash_mode='qio',flash_mhz=80,
    console_and_logs=lab,lab_ca=lab,trust_bundle_sha256=sha(bundle),
    early_mpi_lock=True,heap_owner_probe=a.target=='mpi-probe',web_tcp_probe=a.target=='mpi-probe',production_health=True,output_health=True,pipeline_diagnostic=False,source_note='Quiet candidate with early MPI initialization and on-demand health; lifetime OOM/WDT counters; inactive CLZ excluded.')
if lab:manifest['extra_trust_ca_sha256']=previous['extra_trust_ca_sha256']
(ART/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result=dict(result='PASS',scope='Build/link checks only',image=manifest['image'],sections=sizes,config_changes=changes,
    codec_objects=len(codec),codec_sections=sum(len(v) for v in codec.values()),trust_bundle_sha256=sha(bundle))
(OUT/'build-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
