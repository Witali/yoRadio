"""Parse AST and hash raw sources only; never import construction or witness code."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks, readiness = HERE / 'source-checks.json', HERE / 'readiness.json'
    if checks.exists() or readiness.exists():
        raise RuntimeError('Preserve source-only receipts; use a fresh successor')
    names = ['generate_singletons.py', 'independent_witness.py', 'test_construction.py', 'source_checks.py']
    trees = {n: ast.parse((HERE / n).read_bytes(), filename=n) for n in names}
    controls = [n.name for n in ast.walk(trees['test_construction.py']) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
    assert len(controls) == len(set(controls)) == 31
    pins = json.loads((HERE / 'source-pins.json').read_bytes())
    assert pins['schema'] == 'more-singletons-source-pins-v1' and len(pins['inputs']) == 5
    for item in pins['inputs']:
        old, new = Path(item['source']), HERE / item['snapshot']
        assert old.stat().st_size == new.stat().st_size == item['bytes']
        assert sha(old) == sha(new) == item['sha256']
    imports = []
    for node in ast.walk(trees['independent_witness.py']):
        if isinstance(node, ast.Import):
            imports.extend(x.name for x in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    assert not any('generate' in n or n in ('importlib', 'subprocess', 'ctypes') for n in imports)
    for node in ast.walk(trees['generate_singletons.py']):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            assert not any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id in ('base', 'books') for t in targets)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in ('setattr', 'exec', 'eval', 'compile')
    result = dict(schema='more-singletons-source-only-checks-v1', result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=4, raw_original_snapshots=5, proposed_control_methods=31, proposed_cases=8,
        proposed_raw_audio_packets=112, proposed_Ogg_pages=136, control_method_names=controls,
        independent_witness_imports=imports, original_sources_preserved=True,
        generator_witness_controls_reference_decoder_unit_compiler_SDK_QEMU_or_Git_executed=False,
        generated_raw_corpus_exists=False, PCM_or_target_qualified=False, full_G6_qualified=False,
        vendor_private_state_handles_binaries_or_disassembly_accessed=False)
    checks.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    files = {p.relative_to(HERE).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
             for p in sorted(HERE.rglob('*')) if p.is_file()}
    readiness.write_text(json.dumps(dict(schema='more-singletons-source-only-readiness-v1', runtime_executed=False,
        files=files), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(result=result['result'], files=len(files), readiness_sha256=sha(readiness), runtime_executed=False)))


if __name__ == '__main__':
    main()
