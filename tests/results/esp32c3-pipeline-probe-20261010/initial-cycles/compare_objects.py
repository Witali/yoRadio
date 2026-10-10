"""Compare all application object code/constant sections against the prior quiet build."""
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
before,after=collect('quiet-growth-tls'),collect('quiet-pipeline-probe')
assert before.keys()==after.keys()
changed=[name for name in after if after[name]!=before[name]]
assert {Path(name).name for name in changed}=={'audio_service.c.obj','native_audio_output.c.obj','web_service.c.obj'},changed
result=dict(result='PASS',objects=len(after),unchanged=len(after)-len(changed),changed=changed,
            scope='All application object code and constants; debug and relocated final addresses excluded')
(ROOT/'application-object-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'application-object-sections.json').write_text(json.dumps(after,indent=2)+'\n')
print(json.dumps(result))
