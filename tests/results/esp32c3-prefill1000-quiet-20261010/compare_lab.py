"""Require identical application objects to the measured laboratory candidate."""
import hashlib
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
BASE = Path('idf/esp32c3-oled-native')
OLD = BASE / 'build-idf-6.1-r9a97-quiet-prefill1000-reneg'
NEW = BASE / 'build-idf-6.1-r9a97-quiet-prefill1000'

def collect(folder):
    main = folder / 'esp-idf/main'
    result = {}
    for path in main.rglob('*.obj'):
        with path.open('rb') as stream:
            result[path.relative_to(main).as_posix()] = {
                s.name: dict(bytes=s['sh_size'], sha256=hashlib.sha256(s.data()).hexdigest())
                for s in ELFFile(stream).iter_sections() if s['sh_size'] and
                s.name.startswith(('.text', '.rodata', '.srodata', '.data', '.bss'))}
    return result

def memory(folder):
    with (folder / 'yoradio_esp32c3_oled_native.elf').open('rb') as stream:
        return {s.name: s['sh_size'] for s in ELFFile(stream).iter_sections()
                if s.name.startswith(('.dram', '.iram', '.rtc'))}

before, after = collect(OLD), collect(NEW)
assert before and before == after, [n for n in before.keys() | after.keys() if before.get(n) != after.get(n)]
assert memory(OLD) == memory(NEW)
result = dict(result='PASS', objects=len(after), identical_objects=len(after),
              sections=after, static_memory_sections=memory(NEW),
              scope='Application object code/data and static RAM/IRAM identical to measured lab image; normal trust audited separately')
(ROOT / 'laboratory-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print('PASS:', len(after), 'identical application objects and unchanged static RAM/IRAM')
