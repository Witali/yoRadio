"""AST/raw identities only; never import or evaluate the diagnostic or its math."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    output, readiness = HERE/'source-checks.json', HERE/'readiness.json'
    if output.exists() or readiness.exists():
        raise RuntimeError('Preserve source-only receipts')
    for name in ('curve_diagnostic.py','source_checks.py','provenance/reviewed-fixture-witness.py'):
        ast.parse((HERE/name).read_bytes(),filename=name)
    pins = json.loads((HERE/'source-pins.json').read_bytes())
    for item in pins['inputs']:
        original, copy = Path(item['source']), HERE/item['snapshot']
        assert original.stat().st_size == copy.stat().st_size == item['bytes']
        assert sha(original) == sha(copy) == item['sha256']
    source_tree = ast.parse((HERE/'curve_diagnostic.py').read_bytes())
    assignment = next(n for n in source_tree.body if isinstance(n,ast.Assign)
                      and any(isinstance(t,ast.Name) and t.id=='EXPECTED_IDS' for t in n.targets))
    assert list(ast.literal_eval(assignment.value)) == pins['case_ids']
    assert len(pins['inputs'])==30 and len(pins['case_ids'])==6
    refs = json.loads((HERE/'source-references.json').read_bytes())
    assert refs['web_raw_bytes_downloaded'] is False and refs['web_SHA256_assigned'] is False
    result = dict(schema='floor0-own-curve-source-only-checks-v1',result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=3,raw_original_snapshots_checked=30,original_cases=6,
        prospective_packets=84,prospective_channel_packets=168,prospective_bin_observations=2688,
        proposed_own_formula_control_groups=5,diagnostic_or_math_or_controls_executed=False,
        decoder_or_reference_or_SDK_or_QEMU_or_tests_executed=False,
        canonical_Git_archives_or_campaigns_modified=False,web_raw_SHA256_invented=False,
        numeric_qualified=False,full_G6_qualified=False)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    files = {p.relative_to(HERE).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))
             for p in sorted(HERE.rglob('*')) if p.is_file()}
    readiness.write_text(json.dumps(dict(schema='floor0-own-curve-source-only-readiness-v1',
        diagnostic_or_math_executed=False,files=files),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(result=result['result'],files=len(files),readiness_sha256=sha(readiness),
                         diagnostic_or_math_executed=False)))


if __name__=='__main__':
    main()
