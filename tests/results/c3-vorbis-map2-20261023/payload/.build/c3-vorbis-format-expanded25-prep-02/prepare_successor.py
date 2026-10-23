"""Create-only source successor: exact prior C3 runtime plus corrected data pin."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT/'.build/c3-vorbis-format-expanded25-prep-01'
CYD = ROOT/'.build/cyd-vorbis-format-expanded25-prep-02'
OLD_READINESS = '73cf6cc976a7300cd23ca1f47fcc778da9e67bfd277dd0b7cc842c2bee362003'
OLD_CONTROLLER = '7a7ba50fd01656c7e3a29e9d2e72a8d75f6d15a105e57f0f25bdfc638a4270f4'
OLD_DATA = '4cba27844a6a9018c103e06ac8e505590ae0549ef2dfe6238ebd933b4dfb9757'
NEW_DATA = '97b1a62287dc048603eaaed239cf294a19a4c887ecc97d2fe2d887e7d8b8b6dc'
RUNNER = 'run-c3-vorbis-format-expanded25-qemu.py'


def fact(path):
    data = path.read_bytes()
    return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream: stream.write(data)


def json_write(path,value):
    write(path,(json.dumps(value,indent=2)+'\n').encode())


def old_inputs():
    assert fact(OLD/'readiness.json')['sha256'] == OLD_READINESS
    manifest = json.loads((OLD/'readiness.json').read_bytes())
    assert fact(OLD/RUNNER)['sha256'] == OLD_CONTROLLER
    for name,row in manifest['files'].items(): assert fact(OLD/name) == row,name
    for name,row in manifest['external_inputs'].items(): assert fact(ROOT/name) == row,name
    return manifest


def main():
    original = old_inputs()
    data_source = CYD/'materialized01/data.h'
    assert fact(data_source)['sha256'] == NEW_DATA
    runtime = [name for name in original['files'] if name.startswith('target/')]
    runtime += [RUNNER,'protocol.py','windows_compile_command.py','platform-facts.json',
        'contract.json','source-map.json','reference_binding02.py','reference-binding02.json']
    copied = {}
    for name in runtime:
        data = (OLD/name).read_bytes()
        if name == RUNNER:
            assert data.count(OLD_DATA.encode()) == 1
            data = data.replace(OLD_DATA.encode(),NEW_DATA.encode())
            before,after = ast.parse((OLD/name).read_bytes()),ast.parse(data)
            def assignments(tree):
                return {n.targets[0].id:ast.literal_eval(n.value) for n in tree.body
                    if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
            a,b = assignments(before),assignments(after)
            assert a.pop('DATA_HEADER_SHA') == OLD_DATA and b.pop('DATA_HEADER_SHA') == NEW_DATA and a == b
            # Reverting exactly the selected data literal recovers the complete old source.
            assert data.replace(NEW_DATA.encode(),OLD_DATA.encode()) == (OLD/name).read_bytes()
        write(HERE/name,data)
        copied[name] = dict(original=original['files'][name],successor=fact(HERE/name),
            relation='DATA_HEADER_SHA_LITERAL_ONLY' if name == RUNNER else 'BYTE_IDENTICAL')
    write(HERE/'materialized01/data.h',data_source.read_bytes())
    text = (OLD/'README.md').read_bytes().decode()
    text = text.replace('# Standalone C3 public raw expanded25 capture proposal',
        '# Standalone C3 public raw expanded25 capture successor02')
    text = text.replace(OLD_DATA,NEW_DATA)
    text = text.replace('.build/c3-vorbis-format-expanded25-prep-01/contract.json',
        '.build/c3-vorbis-format-expanded25-prep-02/contract.json')
    text = text.replace('.build/cyd-vorbis-format-expanded25-prep-01/materialized01/data.h',
        '.build/c3-vorbis-format-expanded25-prep-02/materialized01/data.h')
    text += '''
## Corrected source-only successor relationship

Frozen C3prep01 is preserved. Its readiness identity is
`73cf6cc976a7300cd23ca1f47fcc778da9e67bfd277dd0b7cc842c2bee362003`;
its controller identity is
`7a7ba50fd01656c7e3a29e9d2e72a8d75f6d15a105e57f0f25bdfc638a4270f4`.
The only functional runtime-source change here is DATA_HEADER_SHA from the old
`4cba27844a6a9018c103e06ac8e505590ae0549ef2dfe6238ebd933b4dfb9757`
to the corrected full25 data identity above. The new materialized01/data.h is
copied byte-for-byte from CYDprep02/materialized01/data.h; it is not regenerated.
All other runtime files are byte-identical to C3prep01 (including the deliberately
unusable project data.h template); corrected input is supplied explicitly by CLI.
The unchanged contract still names its original frozen matrices/raw paths. They
are source provenance, not a request to rerun old generators or references.

The prior CYD capture01 failed compilation because the supplied materialized
header had capacity17 with25 descriptors and an obsolete expected PCM macro.
No prior source-only check is treated as compile/target proof. The independent
restricted C reader in check_successor.py parses numeric macros, all raw arrays
and actual descriptor entries separately; it compares them to the unchanged25
model and actual raw SHA values. It rejects original17 data and independent count,
PCM-total and descriptor-omission corruptions. These are source construction
checks, not protocol tests or decoding. No SDK/compiler/QEMU/reference/PCM/Git
operation is executed by this preparation.

Full root-owned entrypoint (all runtime options and candidate selection remain
unchanged):

```powershell
& 'C:/Users/rudol/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B .build/c3-vorbis-format-expanded25-prep-02/run-c3-vorbis-format-expanded25-qemu.py --contract .build/c3-vorbis-format-expanded25-prep-02/contract.json --contract-sha256 717ec7f703295f9851fd9241877cf249ff6f203c436786300a36247f2805218d --data-header .build/c3-vorbis-format-expanded25-prep-02/materialized01/data.h --data-sha256 97b1a62287dc048603eaaed239cf294a19a4c887ecc97d2fe2d887e7d8b8b6dc --candidate '<repository/idf/esp32c3-oled-native/main or separately reviewed ce2e candidate main>' --output '<fresh root-selected checkout .build C3 campaign>'
```

This command is documentation only; it has not been executed here. C3 baseline
f3d8 and acceptance candidate ce2e each require distinct actual target/numerical
evidence. The source-only successor does not inherit any CYD target result.
'''
    write(HERE/'README.md',text.encode())
    for name in (RUNNER,'README.md'):
        difference=''.join(difflib.unified_diff((OLD/name).read_bytes().decode().splitlines(True),
            (HERE/name).read_bytes().decode().splitlines(True),fromfile='frozen01/'+name,tofile='successor02/'+name))
        write(HERE/('controller-revision02.diff' if name == RUNNER else 'README-revision02.diff'),difference.encode())
    json_write(HERE/'source-relation.json',dict(schema='c3-expanded25-corrected-data-source-relation-v1',
        source_only=True,prior_readiness_sha256=OLD_READINESS,prior_controller_sha256=OLD_CONTROLLER,
        source_files=copied,corrected_data_source=dict(path=str(data_source.resolve()),**fact(data_source)),
        corrected_data_copy=fact(HERE/'materialized01/data.h'),contract_model_unchanged=True,
        sole_functional_change='DATA_HEADER_SHA literal selects corrected full25 header',
        SDK_compiler_QEMU_reference_protocol_tests_PCM_Git_executed=False))
    assert old_inputs() == original
    assert fact(data_source) == fact(HERE/'materialized01/data.h')
    print(json.dumps(dict(scope='SOURCE_COPY_AST_ONLY',controller=fact(HERE/RUNNER),
        data=fact(HERE/'materialized01/data.h'),old_inputs_unchanged=True,runtime_files=len(runtime))))


if __name__ == '__main__': main()
