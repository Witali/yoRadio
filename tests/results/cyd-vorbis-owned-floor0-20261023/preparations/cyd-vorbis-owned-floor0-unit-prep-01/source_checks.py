"""AST/raw/source assembly verification only; no independent reader/tests/C/SDK execution."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    output,readiness=HERE/'source-checks.json',HERE/'readiness.json'
    if output.exists() or readiness.exists():raise RuntimeError('Preserve source-only receipts')
    scripts=['assemble_fixture.py','fixture_bits.py','fixture_reader.py','protocol.py','test_semantics.py',
             'run-owned-floor0-unit.py','owned_qmp.py','windows_compile_command.py','source_checks.py']
    trees={}
    for name in scripts:trees[name]=ast.parse((HERE/name).read_bytes(),filename=name)
    controls=sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_')
                 for n in ast.walk(trees['test_semantics.py']))
    assert controls==25
    pins=json.loads((HERE/'source-pins.json').read_bytes())
    for item in pins['inputs']:
        old,new=Path(item['source']),HERE/item['snapshot']
        assert old.stat().st_size==new.stat().st_size==item['bytes'] and sha(old)==sha(new)==item['sha256']
    before=(HERE/'provenance/book_unit.c').read_bytes()
    raw=before[before.index(b'static unsigned current_case, current_probe;'):before.index(b'static uint8_t table_u8(')]
    support=(HERE/'project/main/unit_support.h').read_bytes()
    assert support==b'/* Exact controlled seams extracted from the reviewed owned-book unit. */\n#pragma once\n'+raw
    witness=(HERE/'provenance/equivalent-witness.py').read_bytes()
    raw_reader=witness[witness.index(b'class Reader:'):witness.index(b'def parse_setup(data):')]
    assert (HERE/'fixture_bits.py').read_bytes().endswith(raw_reader)
    contract=json.loads((HERE/'fixture-contract.json').read_bytes())
    model=contract['model']
    assert contract['contract_sha256']==hashlib.sha256(json.dumps(model,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert len(model['cases'])==12 and model['pairs']==[[i,i+6] for i in range(6)] and model['protocol_lines']==32
    header=(HERE/'project/main/unit_data.h').read_text()
    found=re.findall(r'static const uint8_t floor_setup_([0-9]{2})\[\] = \{([0-9,]+)\};',header)
    assert len(found)==12
    for index,((number,body),case) in enumerate(zip(found,model['cases'])):
        raw_setup=(HERE/case['setup_snapshot']).read_bytes()
        assert int(number)==index and bytes(map(int,body.split(',')))==raw_setup
        assert hashlib.sha256(raw_setup).hexdigest()==case['setup_sha256']
    parser=HERE/'project/main/pinned/production/vorbis_repair/setup.c'
    abi=HERE/'project/main/pinned/production/vorbis_repair_abi.h'
    assert sha(parser)=='6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
    assert sha(abi)=='e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60'
    controller_tree=trees['run-owned-floor0-unit.py']
    pins_node=next(n for n in controller_tree.body if isinstance(n,ast.Assign)
                   and any(isinstance(t,ast.Name) and t.id=='PINS' for t in n.targets))
    for key,value in zip(pins_node.value.keys,pins_node.value.values):
        name=ast.literal_eval(key)
        expected=sha(HERE/'fixture-contract.json') if isinstance(value,ast.Name) and value.id=='CONTRACT_SHA' else ast.literal_eval(value)
        assert sha(HERE/name)==expected
    for old,new,diff in [('provenance/book-runtime03-controller.py','run-owned-floor0-unit.py','controller.diff'),
                         ('provenance/book-owned_qmp.py','owned_qmp.py','qmp.diff'),
                         ('provenance/book-project-CMakeLists.txt','project/CMakeLists.txt','project.diff'),
                         ('provenance/book-main-CMakeLists.txt','project/main/CMakeLists.txt','component.diff')]:
        text=''.join(difflib.unified_diff((HERE/old).read_text().splitlines(True),(HERE/new).read_text().splitlines(True),fromfile=old,tofile=new))
        (HERE/diff).write_text(text,encoding='utf-8')
    ps=json.loads((HERE/'powershell-source-ast.json').read_text(encoding='utf-8-sig'))
    assert ps['parser_errors']==[] and ps['SDK_or_launcher_executed'] is False
    assert ps['script_sha256']==sha(HERE/'project/sdk-build.ps1')
    result=dict(schema='owned-floor0-unit-source-only-checks-v1',result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=len(scripts),raw_original_snapshots=len(pins['inputs']),raw_C_arrays_checked=12,
        prospective_cases=12,prospective_pairs=6,prospective_protocol_events=32,proposed_semantic_control_methods=controls,
        source_arrays_assembled=True,independent_raw_reader_or_controls_executed=False,
        production_parser_or_unit_or_compiler_or_SDK_or_QEMU_executed=False,
        vendor_handles_binaries_or_opaque_state_inspected=False,canonical_Git_archives_or_campaigns_modified=False,
        C_compile_link_or_unit_qualified=False,full_G6_qualified=False)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    files={p.relative_to(HERE).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(HERE.rglob('*')) if p.is_file()}
    readiness.write_text(json.dumps(dict(schema='owned-floor0-unit-runtime-source-only-readiness-v1',runtime_executed=False,files=files),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(result=result['result'],files=len(files),readiness_sha256=sha(readiness),C_compile_link_or_unit_qualified=False)))


if __name__=='__main__':main()
