"""Verify the quiet build's sole output-code difference and unchanged static RAM."""
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parent
BASE = Path('idf/esp32c3-oled-native')
OLD = BASE / 'build-idf-6.1-r9a97-quiet-growth-tls'
NEW = BASE / 'build-idf-6.1-r9a97-quiet-prefill1000-reneg'

def sections(path):
    with path.open('rb') as stream:
        return {s.name: s.data() for s in ELFFile(stream).iter_sections()
                if s['sh_size'] and s.name.startswith(('.text', '.rodata', '.srodata', '.data', '.bss'))}

def one(folder, pattern):
    matches = list(folder.rglob(pattern))
    assert len(matches) == 1, matches
    return matches[0]

before = sections(one(OLD, 'native_audio_output.c.obj'))
after = sections(one(NEW, 'native_audio_output.c.obj'))
changed = [key for key in before.keys() | after.keys() if before.get(key) != after.get(key)]
section = '.text.native_audio_output_suspend'
assert changed == [section], changed
def line_instruction(line):
    return ((line << 20) | (12 << 7) | 0x13).to_bytes(4, 'little')
assert after[section].count(line_instruction(606)) == 1
assert after[section].replace(line_instruction(606), line_instruction(599)) == before[section]

def memory(folder):
    with (folder / 'yoradio_esp32c3_oled_native.elf').open('rb') as stream:
        return {s.name: s['sh_size'] for s in ELFFile(stream).iter_sections()
                if s.name.startswith(('.dram', '.iram', '.rtc'))}

old_memory, new_memory = memory(OLD), memory(NEW)
assert old_memory == new_memory, (old_memory, new_memory)
result = dict(result='PASS', static_memory_sections=new_memory,
              output_difference='ESP_ERROR_CHECK source line 599 -> 606 only',
              scope='Object bytes and linked static RAM/IRAM sizes; no runtime guarantee')
(ROOT / 'output-and-ram-audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
