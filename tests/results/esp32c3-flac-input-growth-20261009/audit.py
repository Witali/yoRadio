"""Pin the two FLAC queue variants and audit their linked allocator routes."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from elftools.elf.elffile import ELFFile

sys.path.insert(0, 'tools/esp32c3_tests')
from ota import image_info
ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
OBJDUMP = Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
config = lambda p: dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
base = config(Path('firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250/sdkconfig'))
sources = {}
for folder, pattern in [('idf/esp32c3-oled-native/main','*'),
                        ('idf/esp32c3-oled-native/components/custom_flac','*'),
                        ('tools/esp32c3_tests','*.py'),('tools/audio_test_server','*.py')]:
    for path in sorted(Path(folder).glob(pattern)):
        if not path.is_file(): continue
        name = path.as_posix()
        target = ROOT/'sources'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(path.read_bytes())
        sources[name] = sha(path)
for name in ('yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp',
             'yoRadio/src/audioI2S/flac_decoder/flac_decoder.h',
             'tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py'):
    path = Path(name); target = ROOT/'sources'/name
    target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(path.read_bytes())
    sources[name] = sha(path)
(ROOT/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
reports = {}
for extra in (0,4):
    build = Path(f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-flac-input{extra}')
    artifact = Path(f'firmware/development/esp32c3-idf-6.1-r9a97-flac-input{extra}')
    output = ROOT/f'audit{extra}'; output.mkdir(exist_ok=False)
    actual = config(artifact/'sdkconfig')
    changes = {k:dict(before=base.get(k),after=actual.get(k)) for k in base.keys()|actual.keys() if base.get(k)!=actual.get(k)}
    assert changes == {'CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS':dict(before=None,after=str(extra))},changes
    elf = build/'yoradio_esp32c3_oled_native.elf'
    image = image_info((artifact/'app.bin').read_bytes())
    assert image['app_elf_sha256'] == sha(elf)
    commands = json.loads((build/'compile_commands.json').read_text())
    assert not any('flac_clz' in c['file'] for c in commands)
    with elf.open('rb') as f:
        data = ELFFile(f)
        sections = {s.name:dict(size=s['sh_size'],address=s['sh_addr']) for s in data.iter_sections()
                    if s.name in ('.iram0.text','.dram0.data','.dram0.bss','.flash.text','.flash.rodata')}
        symbols = {s.name for s in data.get_section_by_name('.symtab').iter_symbols()}
    for symbol in ('tls_input_reserve_expand_flac','tls_input_reserve_finish_connection','s_flac_input_ready_generation'):
        assert (symbol in symbols) == bool(extra),symbol
    disassembly = subprocess.check_output([str(OBJDUMP),'-d',str(elf)],text=True)
    functions = dict(re.findall(r'^[0-9a-f]+ <([^>]+)>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',disassembly,re.M|re.S))
    for symbol in ('stream_task','decoder_task','tls_input_reserve_expand_flac','tls_input_reserve_finish_connection'):
        if symbol in functions: (output/(symbol+'.txt')).write_text(functions[symbol])
    if extra:
        assert '<tls_input_reserve_expand_flac>' in functions['stream_task']
        assert '<adaptive_input_restore_one>' in functions['tls_input_reserve_expand_flac']
        assert '<heap_caps_get_free_size>' in functions['tls_input_reserve_expand_flac']
    rx = list(build.rglob('esp_mbedtls_dynamic_impl.c.obj'))
    assert len(rx) == 1,rx
    for tool,args,name in [
        ('tools/codec_benchmark/verify_aac_network_build.py',['--build',str(build)],'aac'),
        ('tools/esp32c3_tests/verify_http_link.py',['--sdkconfig',str(build/'sdkconfig'),'--elf',str(elf)],'http'),
        ('tools/esp32c3_tests/verify_adaptive_input_link.py',['--sdkconfig',str(build/'sdkconfig'),'--elf',str(elf),'--tls-rx-object',str(rx[0])],'allocator')]:
        with (output/(name+'.log')).open('xb') as log:
            subprocess.run([sys.executable,'-X','utf8',tool,*args,'--objdump',str(OBJDUMP),'--output',str(output/(name+'.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
    manifest = json.loads((artifact/'manifest.json').read_text())
    manifest.update(laboratory_only=True,production_qualified=False,flac_input_extra_slots=extra,
        input_prefill_ms=500,input_prefill_min_ms=250,clock_mode='fractional',
        source_overlay_sha256={p:v for p,v in sources.items() if p.startswith(('idf/','yoRadio/'))},
        bootloader_sha256=sha(artifact/'bootloader.bin'),
        extra_trust_ca_sha256='5d07cd4783170ceeb5933e41a9618d7c0775567f7e9307d8478390cf3f526de8',
        restoration_app_sha256='21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a',
        source_note='Unrelated CLZ CMake changes are inactive; no CLZ benchmark sources compiled.')
    (artifact/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    reports[str(extra)] = dict(result='PASS',image=image,changes=changes,sections=sections)
(ROOT/'build-audit.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
