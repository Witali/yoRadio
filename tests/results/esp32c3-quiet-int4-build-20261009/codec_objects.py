"""Verify codec arithmetic remains byte-identical in the quiet candidate."""
import hashlib
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parent


def objects(directory):
    paths = []
    for pattern in ('flac_decoder.cpp.obj', 'custom_flac_adapter.cpp.obj',
                    'native_aac_decoder.c.obj', 'aac_*.c.obj'):
        paths += list(directory.rglob(pattern))
    paths += list((directory/'esp-idf/main/compact5').glob('*.obj'))
    result = {}
    for path in paths:
        assert path.name not in result
        with path.open('rb') as stream:
            result[path.name] = {s.name:dict(bytes=s['sh_size'], sha256=hashlib.sha256(s.data()).hexdigest())
                for s in ELFFile(stream).iter_sections()
                if s.name.startswith(('.text', '.rodata')) and s['sh_size']}
    assert len(result) >= 18
    return result


before = objects(Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-min250'))
after = objects(Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-int4'))
changes = {n:dict(before=before.get(n),after=after.get(n)) for n in before.keys()|after.keys() if before.get(n)!=after.get(n)}
result = dict(result='PASS' if not changes else 'FAIL', baseline='quiet-min250', candidate='quiet-int4',
              objects=len(after), sections=sum(len(s) for s in after.values()),
              before=before, after=after, changes=changes)
(root/'codec-objects.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('before','after','changes')},indent=2))
assert not changes, list(changes)
