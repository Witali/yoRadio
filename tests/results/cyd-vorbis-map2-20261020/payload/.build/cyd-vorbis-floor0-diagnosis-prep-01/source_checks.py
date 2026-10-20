"""AST and exact raw source hashes only; no fixture inspector/codec invocation."""
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
        raise RuntimeError('Preserve existing source checks')
    python_files = sorted(HERE.glob('*.py'))
    for path in python_files:
        ast.parse(path.read_bytes())
    pins = json.loads((HERE / 'source-pins.json').read_bytes())
    for row in pins['local_inputs']:
        raw = (ROOT / row['path']).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    files = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in HERE.iterdir() if p.is_file()}
    result = dict(result='SOURCE_ONLY_AUDIT_READY', python_AST_files=len(python_files),
        raw_local_source_pins_checked=len(pins['local_inputs']), files=files,
        fixture_inspection_proposal_executed=False, actual_PCM_read_or_remeasured=False,
        SDK_compiler_codec_QEMU_reference_Git_device_invoked=False, canonical_or_campaign_modified=False,
        decoder_arithmetic_diagnosed=False, full_G6_qualified=False)
    with output.open('xb') as stream:
        stream.write((json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(dict(result=result['result'], source_checks_sha256=sha(output.read_bytes()),
        fixture_inspection_executed=False)))


if __name__ == '__main__':
    main()
