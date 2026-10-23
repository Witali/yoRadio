"""AST/raw source preparation checks only; never import/run protocol or C unit."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    output = HERE / 'source-checks02.json'
    if output.exists():
        raise RuntimeError('Preserve source-only checks')
    scripts = sorted(HERE.glob('*.py'))
    for path in scripts:
        ast.parse(path.read_bytes())
    pins = json.loads((HERE / 'source-pins.json').read_bytes())
    for row in pins['inputs']:
        raw = (HERE / row['snapshot']).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    raw = (HERE / 'fixture-contract.json').read_bytes()
    contract = json.loads(raw)
    model = contract['model']
    assert contract['contract_sha256'] == sha(json.dumps(model, sort_keys=True, separators=(',', ':')).encode())
    assert len(model['cases']) == model['case_count'] == 16
    assert sum(len(c['probes']) for c in model['cases']) == model['probe_count'] == 61
    files = {p.relative_to(HERE).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
             for p in sorted(HERE.rglob('*')) if p.is_file()}
    result = dict(result='OWNED_BOOK_UNIT_SOURCE_ONLY_READY', AST_files=len(scripts),
        raw_source_snapshots_checked=len(pins['inputs']), files=files,
        contract_file_sha256=sha(raw), contract_model_sha256=contract['contract_sha256'],
        cases=16, active_words=59, vector_probes=61, prospective_protocol_events=97,
        compiler_or_SDK_or_QEMU_or_tests_or_decoder_or_reference_executed=False,
        C_compile_link_or_unit_execution_qualified=False, protocol_synthetic_tests_executed=False,
        vendor_binary_or_handle_inspected=False, canonical_Git_archives_or_campaigns_modified=False,
        terminal_shutdown_and_link_closure_still_pending=True, full_G6_qualified=False)
    with output.open('xb') as stream:
        stream.write((json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(dict(result=result['result'], source_checks_sha256=sha(output.read_bytes()),
        C_compile_link_or_unit_execution_qualified=False)))


if __name__ == '__main__':
    main()
