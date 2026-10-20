"""Read source/AST/record identities only; never call qualify/main or parse PCM."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    output = HERE / 'source-checks.json'
    if output.exists():
        raise RuntimeError('Preserve source checks')
    for name in ('prepare.py', 'carrier.py', 'qualify.py', 'check_source.py'):
        ast.parse((HERE / name).read_bytes())
    pins = json.loads((HERE / 'pins.json').read_bytes())
    helper = (HERE / 'carrier.py').read_bytes()
    assert sha(helper) == pins['carrier_source']['proposed_helper_sha256']
    source = (ROOT / pins['carrier_source']['path']).read_bytes()
    assert sha(source) == pins['carrier_source']['sha256']
    for raw in (source, helper):
        text = raw.decode()
        definitions = {node.name: ast.get_source_segment(text, node) for node in ast.parse(text).body if isinstance(node, ast.FunctionDef)}
        assert all(sha(definitions[name].encode()) == digest for name, digest in pins['carrier_source']['unchanged_definitions'].items())
    for row in pins['supporting_source_inputs']:
        data = (ROOT / row['path']).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
    checked = []
    for profile, expected in pins['profiles'].items():
        root = ROOT / '.build' / expected['campaign']
        report_bytes = (root / 'report.json').read_bytes()
        outer_bytes = root.with_name(root.name + '-command.json').read_bytes()
        assert sha(report_bytes) == expected['report_sha256'] and sha(outer_bytes) == expected['outer_sha256']
        report, outer = json.loads(report_bytes), json.loads(outer_bytes)
        assert report['driver_sha256'] == pins['driver_sha256'] and len(report['cases']) == expected['case_count']
        assert len(report['commands']) == expected['case_count'] * 2 and outer['returncode'] == expected['outer_returncode']
        checked.append(profile)
    files = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in sorted(HERE.iterdir()) if p.is_file()}
    result = dict(result='SOURCE_ONLY_READY', python_ast_files=4, pure_helper_definitions_byte_identical=3,
        pinned_completed_report_schemas=checked, files=files, qualifier_executed=False,
        actual_PCM_interpreted=False, actual_tools_rehashed=False, SDK_decoder_QEMU_Git_invoked=False,
        canonical_or_campaign_modified=False)
    data = (json.dumps(result, indent=2) + '\n').encode()
    with output.open('xb') as stream:
        stream.write(data)
    print(json.dumps(dict(result=result['result'], source_checks_sha256=sha(data), qualifier_executed=False)))


if __name__ == '__main__':
    main()
