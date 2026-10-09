"""Verify matched diagnostic changes, linked probe hooks and full codec paths."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from elftools.elf.elffile import ELFFile

sys.path.insert(0,'tools/esp32c3_tests')
from ota import image_info
ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
PRIOR=REPO/'tests/results/esp32c3-flac-input-growth-20261009'
OBJDUMP=Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
sources=json.loads((PRIOR/'sources.json').read_text())
for name,digest in sources.items():
    assert sha(REPO/name)==digest,name
    assert sha(PRIOR/'sources'/name)==digest,name
(ROOT/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'references.json').write_text(json.dumps({PRIOR.relative_to(REPO).as_posix():dict(index_sha256=sha(PRIOR/'index.json'))},indent=2)+'\n')

def sections(path):
    with path.open('rb') as f:
        elf=ELFFile(f)
        return {s.name:dict(size=s['sh_size'],address=s['sh_addr']) for s in elf.iter_sections()
            if s.name.startswith(('.iram0.','.dram0.','.rtc.')) or s.name in ('.flash.text','.flash.rodata')}

reports={}
for extra in (4,0):
    build=Path(f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-flac-input{extra}-owner')
    artifact=Path(f'firmware/development/esp32c3-idf-6.1-r9a97-flac-input{extra}-owner')
    baseline=Path(f'firmware/development/esp32c3-idf-6.1-r9a97-flac-input{extra}')
    output=ROOT/f'audit{extra}-r2';output.mkdir(exist_ok=False)
    base,actual=config(baseline/'sdkconfig'),config(artifact/'sdkconfig')
    changes={k:dict(before=base.get(k),after=actual.get(k)) for k in base.keys()|actual.keys() if base.get(k)!=actual.get(k)}
    ca_key='CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH'
    assert changes=={
        'CONFIG_YORADIO_HEAP_FRAGMENT_PROBE':dict(before=None,after='y'),
        'CONFIG_HEAP_USE_HOOKS':dict(before=None,after='y'),
        ca_key:dict(before=base[ca_key],after='"'+(ROOT/'trust/ca.pem').as_posix()+'"')},changes
    elf=build/'yoradio_esp32c3_oled_native.elf'
    image=image_info((artifact/'app.bin').read_bytes())
    assert image['app_elf_sha256']==sha(elf)
    commands=json.loads((build/'compile_commands.json').read_text())
    assert not any('flac_clz' in c['file'] for c in commands)
    assert sum(c['file'].endswith('heap_fragment_probe.c') for c in commands)==1
    disassembly=subprocess.check_output([str(OBJDUMP),'-d',str(elf)],text=True)
    functions=dict(re.findall(r'^[0-9a-f]+ <([^>]+)>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',disassembly,re.M|re.S))
    targets={
        'heap_caps_aligned_alloc_base':'esp_heap_trace_alloc_hook',
        'heap_caps_realloc_base':'esp_heap_trace_alloc_hook',
        'heap_caps_free':'esp_heap_trace_free_hook',
        'heap_caps_realloc':'__wrap_heap_caps_realloc_base',
        '__wrap_heap_caps_free':'heap_caps_free',
        '__wrap_heap_caps_realloc_base':'heap_caps_realloc_base',
        'decoder_task':'heap_fragment_probe_poll',
    }
    for function,called in targets.items():
        assert function in functions and '<'+called+'>' in functions[function],(function,called)
        (output/(function+'.txt')).write_text(functions[function])
    for name in ('esp_heap_trace_alloc_hook','esp_heap_trace_free_hook','heap_fragment_probe_poll'):
        assert name in functions,name
        (output/(name+'.txt')).write_text(functions[name])
    for symbol in ('tls_input_reserve_expand_flac','tls_input_reserve_finish_connection'):
        assert (symbol in functions)==bool(extra),symbol
    rx=list(build.rglob('esp_mbedtls_dynamic_impl.c.obj'));assert len(rx)==1
    for tool,args,name in (
        ('tools/codec_benchmark/verify_aac_network_build.py',['--build',str(build)],'aac'),
        ('tools/esp32c3_tests/verify_http_link.py',['--sdkconfig',str(build/'sdkconfig'),'--elf',str(elf)],'http'),
        ('tools/esp32c3_tests/verify_adaptive_input_link.py',['--sdkconfig',str(build/'sdkconfig'),'--elf',str(elf),'--tls-rx-object',str(rx[0])],'allocator')):
        with (output/(name+'.log')).open('xb') as log:
            subprocess.run([sys.executable,'-X','utf8',tool,*args,'--objdump',str(OBJDUMP),'--output',str(output/(name+'.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
    before_sections=sections(Path(f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-flac-input{extra}/yoradio_esp32c3_oled_native.elf'))
    after_sections=sections(elf)
    manifest=json.loads((artifact/'manifest.json').read_text())
    manifest.update(laboratory_only=True,production_qualified=False,flac_input_extra_slots=extra,
        heap_owner_probe=True,clock_mode='fractional',input_prefill_ms=500,input_prefill_min_ms=250,
        source_overlay_sha256={p:v for p,v in sources.items() if p.startswith(('idf/','yoRadio/'))},
        bootloader_sha256=sha(artifact/'bootloader.bin'),extra_trust_ca_sha256=sha(ROOT/'trust/ca.pem'),
        restoration_app_sha256='21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a',
        source_note='Unchanged firmware sources; owner diagnostic and fresh laboratory trust enabled. Inactive CLZ block not compiled.')
    (artifact/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    reports[str(extra)]=dict(result='PASS',image=image,changes=changes,sections=after_sections,
        baseline_sections=before_sections,section_size_delta={k:after_sections.get(k,{}).get('size',0)-before_sections.get(k,{}).get('size',0) for k in before_sections.keys()|after_sections.keys()})
(ROOT/'build-audit.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
