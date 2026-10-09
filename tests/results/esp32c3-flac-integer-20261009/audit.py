"""Audit matched integer-clock builds before physical use."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, 'tools/esp32c3_tests')
from ota import image_info

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
config = lambda p: dict(re.findall(r'^(CONFIG_\w+)=(.+)$', p.read_text(), re.M))
objdump = 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
baseline = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-flac-retained-owner')
old = Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-retained-owner')

def objects(directory):
    paths = []
    for pattern in ('flac_decoder.cpp.obj', 'custom_flac_adapter.cpp.obj', 'native_aac_decoder.c.obj', 'aac_*.c.obj'):
        paths += list(directory.rglob(pattern))
    paths += list((directory/'esp-idf/main/compact5').glob('*.obj'))
    result = {}
    for path in paths:
        assert path.name not in result
        with path.open('rb') as stream:
            result[path.name] = {s.name: dict(bytes=s['sh_size'], sha256=hashlib.sha256(s.data()).hexdigest())
                for s in ELFFile(stream).iter_sections() if s.name.startswith(('.text', '.rodata')) and s['sh_size']}
    return result

sources = {}
for directory in ('idf/esp32c3-oled-native/main', 'tools/esp32c3_tests', 'tools/audio_test_server'):
    for src in sorted(Path(directory).glob('*')):
        if not src.is_file(): continue
        sources[src.as_posix()] = sha(src)
        dest = ROOT/'sources'/src
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read_bytes())
(ROOT/'sources.json').write_text(json.dumps(sources, indent=2)+'\n')
results, configs = {}, {}
previous = json.loads((old/'manifest.json').read_text())
for slots in (0, 4):
    variant = f'r9a97-flac-integer{slots}'
    build = Path(f'idf/esp32c3-oled-native/build-idf-6.1-{variant}')
    artifact = Path(f'firmware/development/esp32c3-idf-6.1-{variant}')
    out = ROOT/f'audit{slots}'; out.mkdir(exist_ok=False)
    before, after = config(old/'sdkconfig'), config(artifact/'sdkconfig')
    configs[slots] = after
    changes = {k: [before.get(k), after.get(k)] for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
    expected = {k: ['y', None] for k in ('CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK', 'CONFIG_YORADIO_HEAP_FRAGMENT_PROBE', 'CONFIG_HEAP_USE_HOOKS')}
    if slots == 0: expected['CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS'] = ['4', '0']
    assert changes == expected, changes
    elf = build/'yoradio_esp32c3_oled_native.elf'
    image = image_info((artifact/'app.bin').read_bytes())
    assert image['app_elf_sha256'] == sha(elf)
    commands = json.loads((build/'compile_commands.json').read_text())
    assert not any('flac_clz' in c['file'] for c in commands)
    current = objects(build)
    assert len(current) >= 18 and current == objects(baseline), 'Codec arithmetic changed'
    (out/'codec-objects.json').write_text(json.dumps(current, indent=2)+'\n')
    with elf.open('rb') as stream:
        sizes = {s.name: s['sh_size'] for s in ELFFile(stream).iter_sections()
                 if s.name.startswith(('.iram0.', '.dram0.', '.rtc.')) or s.name in ('.flash.text', '.flash.rodata')}
    rx = list(build.rglob('esp_mbedtls_dynamic_impl.c.obj')); assert len(rx) == 1
    for tool, args, name in (
        ('tools/codec_benchmark/verify_aac_network_build.py', ['--build', str(build)], 'aac'),
        ('tools/esp32c3_tests/verify_http_link.py', ['--sdkconfig', str(build/'sdkconfig'), '--elf', str(elf)], 'http'),
        ('tools/esp32c3_tests/verify_adaptive_input_link.py', ['--sdkconfig', str(build/'sdkconfig'), '--elf', str(elf), '--tls-rx-object', str(rx[0])], 'allocator')):
        with (out/(name+'.log')).open('xb') as log:
            subprocess.run([sys.executable, '-X', 'utf8', tool, *args, '--objdump', objdump, '--output', str(out/(name+'.json'))], stdout=log, stderr=subprocess.STDOUT, check=True)
    manifest = json.loads((artifact/'manifest.json').read_text())
    for key in ('extra_trust_ca_sha256', 'restoration_app_sha256', 'input_prefill_ms', 'input_prefill_min_ms'):
        manifest[key] = previous[key]
    manifest.update(laboratory_only=True, production_qualified=False, flac_input_extra_slots=slots,
        heap_owner_probe=False, web_tcp_probe=False, clock_mode='integer', source_overlay_sha256=sources,
        bootloader_sha256=sha(artifact/'bootloader.bin'),
        source_note='Current queue retention fix; normal integer clock; no heap hooks or TCP probe; profiling and lab CA only for testing. Inactive CLZ not compiled.')
    (artifact/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    results[str(slots)] = dict(result='PASS', image=image, config_changes=changes, sections=sizes,
        codec_objects=len(current), codec_sections=sum(len(v) for v in current.values()))
assert {k for k in configs[0] if configs[0].get(k) != configs[4].get(k)} == {'CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS'}
(ROOT/'build-audit.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results, indent=2))
