"""Audit retained queue build against the original expanded owner-probe image."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from elftools.elf.elffile import ELFFile
from references import verify_references

verify_references()
ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
sys.path.insert(0, str(REPO/'tools/esp32c3_tests'))
from ota import image_info

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
config = lambda p: dict(re.findall(r'^(CONFIG_\w+)=(.+)$', p.read_text(), re.M))
prefix = 'idf/esp32c3-oled-native/main/'
changed = {prefix+n for n in ('adaptive_input.c','adaptive_input.h','tls_input_reserve.c')}
prior_sources = json.loads((ROOT/'sources.json').read_text())
current_sources = {p: sha(REPO/p) for p in prior_sources}
actual_changes = {p for p in prior_sources if prior_sources[p] != current_sources[p]}
assert actual_changes == changed, actual_changes
(ROOT/'fixed-sources.json').write_text(json.dumps(current_sources, indent=2)+'\n')
for name in changed:
    dest = ROOT/'fixed-sources'/name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes((REPO/name).read_bytes())

build = REPO/'idf/esp32c3-oled-native/build-idf-6.1-r9a97-flac-retained-owner'
original_build = REPO/'idf/esp32c3-oled-native/build-idf-6.1-r9a97-flac-input4-owner'
artifact = REPO/'firmware/development/esp32c3-idf-6.1-r9a97-flac-retained-owner'
original_artifact = REPO/'firmware/development/esp32c3-idf-6.1-r9a97-flac-input4-owner'
assert config(artifact/'sdkconfig') == config(original_artifact/'sdkconfig')
elf = build/'yoradio_esp32c3_oled_native.elf'
original_elf = original_build/elf.name
image = image_info((artifact/'app.bin').read_bytes())
assert image['app_elf_sha256'] == sha(elf)
commands = json.loads((build/'compile_commands.json').read_text())
assert not any('flac_clz' in c['file'] for c in commands)
assert sum(c['file'].endswith('heap_fragment_probe.c') for c in commands) == 1
output = ROOT/'audit-fixed-r2'
output.mkdir(exist_ok=False)
objdump = 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
disassembly = subprocess.check_output([objdump,'-d',str(elf)],text=True)
functions = dict(re.findall(r'^[0-9a-f]+ <([^>]+)>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',disassembly,re.M|re.S))
targets = {
    'heap_caps_aligned_alloc_base':'esp_heap_trace_alloc_hook',
    'heap_caps_realloc_base':'esp_heap_trace_alloc_hook',
    'heap_caps_free':'esp_heap_trace_free_hook',
    'heap_caps_realloc':'__wrap_heap_caps_realloc_base',
    '__wrap_heap_caps_free':'heap_caps_free',
    '__wrap_heap_caps_realloc_base':'heap_caps_realloc_base',
    'decoder_task':'heap_fragment_probe_poll',
    'tls_input_reserve_prepare_connection':'adaptive_input_set_limit',
}
for function, called in targets.items():
    assert function in functions and '<'+called+'>' in functions[function], (function,called)
    (output/(function+'.txt')).write_text(functions[function])
assert 'adaptive_input_release_one' not in functions['tls_input_reserve_prepare_connection']
for symbol in ('adaptive_input_return','adaptive_input_set_limit','esp_heap_trace_alloc_hook','esp_heap_trace_free_hook','heap_fragment_probe_poll',
               'tls_input_reserve_expand_flac','tls_input_reserve_finish_connection'):
    assert symbol in functions, symbol
    (output/(symbol+'.txt')).write_text(functions[symbol])
original_disassembly = subprocess.check_output([objdump,'-d',str(original_elf)],text=True)
original_functions = dict(re.findall(r'^[0-9a-f]+ <([^>]+)>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',original_disassembly,re.M|re.S))
inline_review = {}
for name in ('adaptive_input_return','adaptive_input_set_limit'):
    # GCC inlines/unrolls the pointer-rank helper. Retain both disassemblies;
    # source and host regressions validate semantics, not symbol presence.
    before_rank = len(re.findall(r'\bsnez\b',original_functions[name]))
    after_rank = len(re.findall(r'\bsnez\b',functions[name]))
    assert after_rank > before_rank and 'vPortEnterCritical' in functions[name]
    (output/(name+'-before.txt')).write_text(original_functions[name])
    inline_review[name] = dict(before_nonnull_counts=before_rank,after_nonnull_counts=after_rank)
rx = list(build.rglob('esp_mbedtls_dynamic_impl.c.obj')); assert len(rx) == 1
for tool,args,name in (
    ('tools/codec_benchmark/verify_aac_network_build.py',['--build',str(build)],'aac'),
    ('tools/esp32c3_tests/verify_http_link.py',['--sdkconfig',str(build/'sdkconfig'),'--elf',str(elf)],'http'),
    ('tools/esp32c3_tests/verify_adaptive_input_link.py',['--sdkconfig',str(build/'sdkconfig'),'--elf',str(elf),'--tls-rx-object',str(rx[0])],'allocator')):
    with (output/(name+'.log')).open('xb') as log:
        subprocess.run([sys.executable,'-X','utf8',tool,*args,'--objdump',objdump,'--output',str(output/(name+'.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)

def memory_sections(path):
    with path.open('rb') as stream:
        return {s.name:dict(size=s['sh_size'],address=s['sh_addr']) for s in ELFFile(stream).iter_sections()
                if s.name.startswith(('.iram0.','.dram0.','.rtc.')) or s.name in ('.flash.text','.flash.rodata')}

def codec_objects(directory):
    paths = []
    for pattern in ('flac_decoder.cpp.obj','custom_flac_adapter.cpp.obj','native_aac_decoder.c.obj','aac_*.c.obj'):
        paths += list(directory.rglob(pattern))
    paths += list((directory/'esp-idf/main/compact5').glob('*.obj'))
    result = {}
    for path in paths:
        assert path.name not in result, path
        with path.open('rb') as stream:
            result[path.name] = {s.name:dict(bytes=s['sh_size'],sha256=hashlib.sha256(s.data()).hexdigest())
                                for s in ELFFile(stream).iter_sections()
                                if s.name.startswith(('.text','.rodata')) and s['sh_size']}
    return result

before, after = memory_sections(original_elf), memory_sections(elf)
delta = {k:after.get(k,{}).get('size',0)-before.get(k,{}).get('size',0) for k in before.keys()|after.keys()}
assert all(v == 0 for k,v in delta.items() if k.startswith(('.iram0.','.dram0.','.rtc.'))), delta
objects = codec_objects(build)
assert objects and objects == codec_objects(original_build), 'Codec arithmetic changed'
(output/'codec-objects.json').write_text(json.dumps(dict(result='PASS',objects=objects),indent=2)+'\n')
manifest = json.loads((artifact/'manifest.json').read_text())
old_manifest = json.loads((original_artifact/'manifest.json').read_text())
for k in ('laboratory_only','production_qualified','flac_input_extra_slots','heap_owner_probe','clock_mode',
          'input_prefill_ms','input_prefill_min_ms','extra_trust_ca_sha256','restoration_app_sha256'):
    manifest[k] = old_manifest[k]
assert manifest['extra_trust_ca_sha256'] == sha(ROOT/'trust/ca.pem')
manifest.update(source_overlay_sha256={p:v for p,v in current_sources.items() if p.startswith(('idf/','yoRadio/'))},
                bootloader_sha256=sha(artifact/'bootloader.bin'),
                source_note='Retain earliest resident input buffers on ordinary shrink; actual TLS pressure can still reclaim idle buffers. Owner diagnostics enabled; inactive CLZ not compiled.')
(artifact/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result = dict(result='PASS',image=image,config_changes={},source_changes=sorted(changed),sections=after,
              baseline_sections=before,section_size_delta=delta,codec_objects=len(objects),
              codec_sections=sum(len(s) for s in objects.values()),targets=targets,inlined_rank_review=inline_review)
reports = json.loads((ROOT/'build-audit.json').read_text())
reports['fixed'] = result
(ROOT/'build-audit.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(result,indent=2))
