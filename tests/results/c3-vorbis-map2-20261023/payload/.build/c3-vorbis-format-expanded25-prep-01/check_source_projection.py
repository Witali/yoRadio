"""Pure file/AST/projection checks. Imports or executes no proposed runtime code."""
import ast
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
CYD = ROOT / '.build/cyd-vorbis-format-expanded25-prep-01'
RATE = ROOT / '.build/c3-vorbis-uint32-rate-sdk-prep-01'
PROJECT = P / 'target/c3_vorbis_format_expanded25_qemu'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def constants(text):
    return {node.targets[0].id: ast.literal_eval(node.value)
            for node in ast.parse(text).body
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}


def function(text, name):
    tree = ast.parse(text)
    return ast.dump(next(n for n in ast.walk(tree)
                         if isinstance(n, ast.FunctionDef) and n.name == name),
                    include_attributes=False)


def check():
    selected = json.loads((P / 'donor-selection.json').read_bytes())
    for rel, value in selected.items():
        assert digest(CYD / rel) == value, ('selected donor drift', rel)
    for rel in ('contract.json', 'source-map.json', 'reference_binding02.py', 'reference-binding02.json'):
        assert (P / rel).read_bytes() == (CYD / rel).read_bytes(), rel
    a = (CYD / 'target/cyd_vorbis_format_expanded25_qemu/main/main.c').read_text()
    b = (PROJECT / 'main/main.c').read_text()
    expected = a.replace('CYD_VORBIS_CHECKED_CORPUS_', 'C3_VORBIS_CHECKED_CORPUS_')
    expected = expected.replace('core == 1', 'core == 0').replace('NULL, 3, NULL, 1)', 'NULL, 3, NULL, 0)')
    expected = expected.replace('create_worker_core1', 'create_worker_core0')
    assert b == expected, 'caller changed beyond prefix/core'
    protocol = (P / 'protocol.py').read_text()
    assert protocol == (CYD / 'protocol.py').read_text().replace(
        'CYD_VORBIS_CHECKED_CORPUS_', 'C3_VORBIS_CHECKED_CORPUS_').replace('core=1', 'core=0')
    assert (PROJECT / 'main/corpus_case.h').read_bytes() == (
        CYD / 'target/cyd_vorbis_format_expanded25_qemu/main/corpus_case.h').read_bytes()
    assert (PROJECT / 'main/data.h').read_bytes() == (
        CYD / 'target/cyd_vorbis_format_expanded25_qemu/main/data.h').read_bytes()
    for rel in ('windows_compile_command.py', 'platform-facts.json'):
        assert (P / rel).read_bytes() == (RATE / rel).read_bytes(), rel
    for rel in ('sdkconfig.defaults', 'partitions.csv'):
        assert (PROJECT / rel).read_bytes() == (RATE / 'target/c3_vorbis_uint32_rate_qemu' / rel).read_bytes()
    controller = (P / 'run-c3-vorbis-format-expanded25-qemu.py').read_text()
    donor = (CYD / 'run-cyd-vorbis-format-expanded25-qemu02.py').read_text()
    rate = (RATE / 'run-c3-vorbis-uint32-rate-qemu.py').read_text()
    const, old = constants(controller), constants(rate)
    for key in ('ARCHIVES', 'SDK_HEAD', 'TOOL_SHA', 'MODULES'):
        assert const[key] == old[key], key
    for name in ('save', 'freeze', 'current', 'execute'):
        assert function(controller, name) == function(donor, name), name
    for name, path in (
        ('CALLER_SHA', PROJECT / 'main/main.c'), ('PROTOCOL_SHA', P / 'protocol.py'),
        ('RAW_HELPER_SHA', PROJECT / 'raw-enable.cmake'), ('CASE_HEADER_SHA', PROJECT / 'main/corpus_case.h'),
        ('CONTRACT_FILE_SHA', P / 'contract.json'), ('REFERENCE_HELPER_SHA', P / 'reference_binding02.py'),
        ('REFERENCE_BINDING_SHA', P / 'reference-binding02.json'), ('SOURCE_MAP_SHA', P / 'source-map.json'),
    ):
        assert const[name] == digest(path), name
    assert const['DATA_HEADER_SHA'] == digest(CYD / 'materialized01/data.h')
    contract = json.loads((P / 'contract.json').read_bytes())
    model = contract['model']
    assert (contract['contract_sha256'], len(model['cases']), model['total_packets'], model['total_pcm'],
            model['case_mask']) == (const['CONTRACT_ID'], 25, 350, 623360, 33554431)
    parsed = [str(path.relative_to(P)) for path in sorted(P.glob('*.py'))
              if ast.parse(path.read_text()) is not None]
    return dict(status='SOURCE_AST_PROJECTION_VERIFIED', python_parsed=parsed,
                cases=25, packets=350, expected_pcm_bytes=623360, protocol_events=778,
                caller_prefix_and_core_only=True, protocol_prefix_and_core_only=True,
                unchanged_owned_process_functions=True, unchanged_c3_macro_helper=True,
                unchanged_selected_reference_binding=True, sdk_compiled=False,
                target_executed=False, tests_executed=False, reference_executed=False)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
