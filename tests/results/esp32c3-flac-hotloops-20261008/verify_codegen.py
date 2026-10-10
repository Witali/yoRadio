import hashlib, json, struct, subprocess
from pathlib import Path

root=Path('.build/flac-hotloops-20261008')
audit=root/'lpc-codegen/final-source-audit'
out=root/'parent-review';out.mkdir(exist_ok=False)
command=json.loads((audit/'commands.json').read_text())[0]
old=out/'flac_decoder.cpp'
old.write_bytes(subprocess.check_output(['git','show','f284fa12:yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp']))
(out/'flac_decoder.h').write_bytes((audit/'inputs/flac_decoder.h').read_bytes())
args=command['args'][:]
for flag,name in [('-o','original.obj'),('-MF','original.d'),('-MT','original.obj')]:
    pos=args.index(flag);args[pos+1]=str((out/name).resolve())
pos=next(i for i,v in enumerate(args) if v.endswith('/inputs/flac_decoder.cpp') or v.endswith('\\inputs\\flac_decoder.cpp'))
args[pos]=str(old.resolve())
result=subprocess.run([command['compiler'],*args],cwd=command['directory'],capture_output=True)
(out/'build.log').write_bytes(result.stdout+result.stderr)
assert result.returncode==0
(out/'command.json').write_text(json.dumps(dict(command=command['compiler'],args=args,cwd=command['directory']),indent=2)+'\n')

def sections(path):
    data=path.read_bytes()
    assert data[:7]==b'\x7fELF\x01\x01\x01'
    offset=struct.unpack_from('<I',data,32)[0]
    entry,count,strings=struct.unpack_from('<HHH',data,46)
    assert entry==40
    rows=[struct.unpack_from('<10I',data,offset+i*entry) for i in range(count)]
    names=data[rows[strings][4]:rows[strings][4]+rows[strings][5]]
    output={}
    for row in rows:
        name=names[row[0]:].split(b'\0')[0].decode()
        if row[2]&2: # SHF_ALLOC: actual resident data/code, excluding debug info.
            content=data[row[4]:row[4]+row[5]] if row[1]!=8 else b''
            output[name]=dict(bytes=row[5],type=row[1],flags=row[2],sha256=hashlib.sha256(content).hexdigest())
    return output

objects={name:sections(audit/(name+'.obj')) for name in ['default','bytewise-rice','no-auto-unroll','combined']}
objects['original']=sections(out/'original.obj')
assert objects['original']==objects['default'], 'Default production object changed'
for name,rows in objects.items():
    assert {k:v for k,v in rows.items() if not k.startswith('.text')} == {
        k:v for k,v in objects['original'].items() if not k.startswith('.text')}, name
shift=root/'shift-codegen/frozen-audit'
assert sections(shift/'default.obj')==sections(shift/'bounded-shift.obj')
report=dict(passed=True,original_revision='f284fa12',default_alloc_sections_identical=True,
            bounded_shift_alloc_sections_identical=True,non_code_alloc_sections_unchanged=True,
            current_source_sha256=hashlib.sha256(Path('yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp').read_bytes()).hexdigest(),
            sections=objects)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in report.items() if k!='sections'})
