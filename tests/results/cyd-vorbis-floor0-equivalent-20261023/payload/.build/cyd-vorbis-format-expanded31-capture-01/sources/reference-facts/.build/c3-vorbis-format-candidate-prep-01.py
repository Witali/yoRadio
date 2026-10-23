"""Prepare the minimal candidate independently from the qualified C3 baseline."""
import difflib,hashlib,json
from pathlib import Path

root=Path(__file__).resolve().parent.parent
base=root/'.build/c3-vorbis-format-project-prep-01'
out=root/'.build/c3-vorbis-format-candidate-prep-01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
baseline_pins='a433b95841ae724549fb845058d61da3c12b01167efa7f9ca748ed46ecca970d'
assert sha(base/'pins.json')==baseline_pins
pins=json.loads((base/'pins.json').read_text())
for row in pins['files']:
    p=base/row['relative']
    assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for row in pins['external_inputs']:
    p=Path(row['path']); assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
qualification=json.loads((root/'.build/c3-vorbis-format-baseline-01/baseline-qualification.json').read_text())
assert qualification['result']=='REGRESSION_REPRODUCED' and qualification['completed']
assert qualification['observed']['exact_pair_packets']==204
assert not out.exists()
out.mkdir()
for row in pins['files']:
    destination=out/row['relative']; destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_bytes((base/row['relative']).read_bytes())
setup=out/'variant/vorbis_repair/setup.c'
before=setup.read_bytes()
assert before==(root/'idf/esp32c3-oled-native/main/vorbis_repair/setup.c').read_bytes()
newline=b'\r\n' if b'\r\n' in before else b'\n'
removed=b'#else'+newline+b'  if(vi->rate<64000 && ci->blocksizes[1]>4096)goto err_out;'+newline
assert before.count(removed)==1
after=before.replace(removed,b'')
setup.write_bytes(after)
cmake=out/'project/main/CMakeLists.txt'
cmake_before=cmake.read_bytes()
old_hash=hashlib.sha256(before).hexdigest(); new_hash=sha(setup)
assert cmake_before.count(old_hash.encode())==1
cmake.write_bytes(cmake_before.replace(old_hash.encode(),new_hash.encode()))
diff=''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='baseline/setup.c',tofile='candidate/setup.c'))
(out/'candidate.diff').write_text(diff,encoding='utf-8',newline='')
relation=dict(schema='c3-public-vorbis-format-two-line-candidate-v1',baseline_pins_sha256=baseline_pins,
    baseline_qualification_sha256=sha(root/'.build/c3-vorbis-format-baseline-01/baseline-qualification.json'),
    original_setup_sha256=old_hash,candidate_setup_sha256=new_hash,removed_bytes=removed.decode(),
    exact_removal_count=1,other_decoder_source_changes=False,canonical_changed=False,
    optional_limit_preserved=True,ordinary_header_checks_preserved=True,
    fixtures_and_caller_unchanged=True,preparation_script_sha256=sha(__file__))
(out/'candidate-relation.json').write_text(json.dumps(relation,indent=2)+'\n',encoding='utf-8',newline='\n')
(out/'REVIEW.md').write_text('''# Independent C3 candidate source preparation

This variant is derived from the qualified C3 baseline. Only the two-line
default rate/block coupling is removed from setup.c; the explicit
LIMIT_TO_64kHz option and ordinary header checks remain byte-identical.
The minimal CMake's setup SHA is updated to the reviewed candidate SHA.
Caller, fixture, SDK, output.c, C3 ABI and archive/tool identities are unchanged.
candidate-relation.json and candidate.diff give the complete change.

No canonical source is modified and no SDK/compiler/QEMU command is executed
by this preparation. The root will independently build this variant with
ExpectedRejection 0 and the untouched baseline variant with ExpectedRejection 0
as an exact old-guard control, preserving the full original/vendor prerequisites.
The source test scope remains public opaque raw open/decode/close only.
No radio/Ogg/EOF/reset/OOM/private owner work is included.
''',encoding='utf-8',newline='\n')
pins['current_source_expected_baseline_rejection']=0
pins['variant']='reviewed_two_line_candidate'
pins['baseline_pins_sha256']=baseline_pins
names=[row['relative'] for row in pins['files']]+['candidate.diff','candidate-relation.json']
pins['files']=[dict(relative=name,bytes=(out/name).stat().st_size,sha256=sha(out/name)) for name in names]
(out/'pins.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8',newline='\n')
print(diff)
print(json.dumps({'candidate_prep':str(out),'pins_sha256':sha(out/'pins.json'),'setup_sha256':new_hash,'canonical_changed':False}))
