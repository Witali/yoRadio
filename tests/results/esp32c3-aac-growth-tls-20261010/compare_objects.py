"""Only the test trust bundle should change; all application object arithmetic stays identical."""
import hashlib,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parent
BASE=Path('idf/esp32c3-oled-native')
def collect(name):
    folder=BASE/('build-idf-6.1-r9a97-'+name)/'esp-idf/main'
    result={}
    for path in folder.rglob('*.obj'):
        with path.open('rb') as stream:
            sections={s.name:dict(size=s['sh_size'],sha256=hashlib.sha256(s.data()).hexdigest())
                      for s in ELFFile(stream).iter_sections()
                      if s['sh_size'] and s.name.startswith(('.text','.rodata','.srodata'))}
        result[path.relative_to(folder).as_posix()]=sections
    return result
before,after=collect('quiet-output-health'),collect('quiet-growth-tls')
assert len(before)==50 and before==after,'Application code/constants changed'
result=dict(result='PASS',objects=len(after),unchanged=len(after),changed=[],
            scope='All application object code and constants; debug and relocated final addresses excluded')
(ROOT/'application-object-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'application-object-sections.json').write_text(json.dumps(after,indent=2)+'\n')
print(json.dumps(result))
