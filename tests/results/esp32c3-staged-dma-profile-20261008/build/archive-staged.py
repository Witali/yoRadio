import hashlib
import json
from pathlib import Path
import re
import subprocess
from elftools.elf.elffile import ELFFile

root = Path.cwd()
work = root / '.build/c3-staged-dma-profile-20261008'
archive = root / 'tests/results/esp32c3-staged-dma-profile-20261008'
variant = 'esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof'
firmware = root / 'firmware/development' / variant
manifest = json.loads((firmware / 'manifest.json').read_text())
build = root / manifest['build_directory']
elf = build / 'yoradio_esp32c3_oled_native.elf'
control = build.with_name(build.name.removesuffix('-dmaprof')) / elf.name
objdump = Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe')
sha = lambda value: hashlib.sha256(value).hexdigest()
assert sha(elf.read_bytes()) == manifest['elf_sha256']
assert sha((firmware/'app.bin').read_bytes()) == manifest['image']['sha256']
assert sha((firmware/'sdkconfig').read_bytes()) == manifest['sdkconfig_sha256']
for path, digest in manifest['source_overlay_sha256'].items():
    assert sha((root/path).read_bytes()) == digest, path

def sections(path):
    with path.open('rb') as stream:
        image = ELFFile(stream)
        return {section.name:section['sh_size'] for section in image.iter_sections()
                if section.name in ('.iram0.text', '.dram0.data', '.dram0.bss', '.flash.text')}

with elf.open('rb') as stream:
    image = ELFFile(stream)
    symbols = {}
    for name in ('dma_queue_overrun', 's_dma_overruns', 's_dma_write_profile'):
        found = image.get_section_by_name('.symtab').get_symbol_by_name(name)
        assert len(found) == 1
        symbol = found[0]
        symbols[name] = dict(address=symbol['st_value'], bytes=symbol['st_size'],
                             section=image.get_section(symbol['st_shndx']).name)
assert symbols['dma_queue_overrun']['section'] == '.iram0.text'
assert symbols['dma_queue_overrun']['bytes'] == 18
assert symbols['s_dma_overruns']['section'] == '.dram0.data'
assert symbols['s_dma_overruns']['bytes'] == 4
assert symbols['s_dma_overruns']['address'] % 4 == 0
assert symbols['s_dma_write_profile']['bytes'] == 32
disassembly = subprocess.check_output([str(objdump), '-d', '--disassemble=dma_queue_overrun', str(elf)])
instructions = re.findall(rb'^\s*[0-9a-f]+:\s+[0-9a-f]+\s+(\w+)', disassembly, re.M)
assert instructions == [b'lui', b'lw', b'li', b'addi', b'sw', b'ret'], instructions
audit = dict(elf_sha256=manifest['elf_sha256'], symbols=symbols,
             sections=dict(control=sections(control), candidate=sections(elf)),
             source_hash_guard_audited_idf='6.0.2', physical_test=False)
(work/'linked-audit.json').write_bytes((json.dumps(audit, indent=2)+'\n').encode())
(work/'staged-isr-disassembly.txt').write_bytes(disassembly)

files = {}
for path in work.iterdir():
    if path.is_file() and path.suffix in ('.json', '.log', '.txt', '.py', '.ps1'):
        files[Path('build')/path.name] = path
host = work/'host-faults'
for path in host.iterdir():
    if path.is_file() and path.suffix in ('.json', '.log', '.c'):
        files[Path('host')/path.name] = path
report = json.loads((host/'report.json').read_text())
for path, digest in report['sources'].items():
    assert sha((root/path).read_bytes()) == digest, path
sources = set(report['sources']) | set(manifest['source_overlay_sha256']) | {
    'tools/esp32c3_tests/staged_dma.py', 'tests/test-staged-dma.py'}
for path in sources:
    files[Path('sources')/path] = root/path
for path in firmware.iterdir():
    if path.is_file() and path.name != 'app.bin':
        files[Path('firmware')/path.name] = path
assert not archive.exists()
archive.mkdir(parents=True)
entries = {}
for destination, source in sorted(files.items()):
    data = source.read_bytes()
    path = archive/destination
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    entries[destination.as_posix()] = dict(bytes=len(data), sha256=sha(data))
index = dict(kind='Host and linked-image diagnostic qualification; no physical test',
             image=manifest['image'], source_head=manifest['source_head_at_capture'],
             file_count=len(entries), files=entries)
(archive/'index.json').write_bytes((json.dumps(index, indent=2)+'\n').encode())
print(json.dumps(dict(archive=str(archive), files=len(entries), audit=audit), indent=2))
