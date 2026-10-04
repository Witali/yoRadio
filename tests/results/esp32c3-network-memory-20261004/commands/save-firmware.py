import hashlib, json, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, 'tools/esp32c3_tests')
from ota import image_info
root = Path.cwd()
build = root/'idf/esp32c3-oled-native/build-aac-network-memory'
old = root/'idf/esp32c3-oled-native/build-aac-asymmetric-production'
out = root/'firmware/development/esp32c3-aac-network-memory'
evidence = root/'.build/aac-network-memory'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def options(p): return dict(re.findall(r'^(CONFIG_\w+)=(.*)$', p.read_text(), re.M))
before, after = options(old/'sdkconfig'), options(build/'sdkconfig')
changes = {k: [before.get(k), after.get(k)] for k in sorted(before.keys() | after.keys()) if before.get(k) != after.get(k)}
assert changes == {'CONFIG_YORADIO_NETWORK_HEAP_PROFILE': [None, 'y']}, changes
audit = json.loads((build/'esp-idf/main/compact5/audit.json').read_text())
prior = json.loads((old/'esp-idf/main/compact5/audit.json').read_text())
for key in ('compiler_layout', 'functions'):
    assert audit[key] == prior[key], key
binutils = Path('C:/Work/yoRadio/.idf/tools-v6.0.2/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin')
elf = build/'yoradio_esp32c3_oled_native.elf'
symbols = subprocess.check_output([str(binutils/'riscv32-esp-elf-nm.exe'), '-S', '--defined-only', str(elf)], text=True)
assert 'network_heap_profile_poll' in symbols
assert '__wrap_compact5_sbr_open' in symbols
for name in ('aac_pointer_audit', 'low_workspace_report', 'qemu_aac'):
    assert name not in symbols
sections = {}
for name, folder in [('baseline', old), ('diagnostic', build)]:
    text = subprocess.check_output([str(binutils/'riscv32-esp-elf-size.exe'), '-A', str(folder/'yoradio_esp32c3_oled_native.elf')], text=True)
    sections[name] = {m[1]: int(m[2]) for m in re.finditer(r'^(\.[\w.]+)\s+(\d+)\s+\d+', text, re.M)}
delta = {k: sections['diagnostic'].get(k, 0)-sections['baseline'].get(k, 0) for k in sections['diagnostic'].keys() | sections['baseline'].keys()}
verification = dict(config_changes=changes, aac_patch_identical=True, sections=sections, section_deltas=delta, elf_sha256=sha(elf))
(evidence/'build-verification.json').write_text(json.dumps(verification, indent=2)+'\n', encoding='utf-8', newline='\n')
out.mkdir(parents=True, exist_ok=True)
for source, name in [('yoradio_esp32c3_oled_native.bin', 'app.bin'), ('sdkconfig', 'sdkconfig')]:
    shutil.copyfile(build/source, out/name)
manifest = dict(source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    source_note='Opt-in network heap diagnostic on top of this commit; exact source snapshots retained with evidence.',
    status='EXPERIMENTAL diagnostic image; not a production default.',
    evidence='tests/results/esp32c3-network-memory-20261004',
    image=image_info((out/'app.bin').read_bytes()),
    files={n: dict(bytes=(out/n).stat().st_size, sha256=sha(out/n)) for n in ('app.bin', 'sdkconfig')})
(out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps({'manifest': manifest, 'section_deltas': delta}, indent=2))
