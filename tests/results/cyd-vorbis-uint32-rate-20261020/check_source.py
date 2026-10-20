"""AST/source/recorded-argv checks only; never call pack.main or verify.verify."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    output = HERE / 'source-checks.json'
    if output.exists():
        raise RuntimeError('Preserve previous source checks')
    for name in ('pack.py', 'verify.py', 'check_source.py'):
        ast.parse((HERE / name).read_bytes())
    spec = importlib.util.spec_from_file_location('rate_archive_source_review', HERE / 'verify.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)  # Pure definitions/constants; main is guarded.
    source = ROOT / '.build/cyd-vorbis-uint32-rate-source-01'
    if verifier.fixed_source((source / 'before.c').read_bytes()) != (source / 'after.c').read_bytes():
        raise RuntimeError('Source projection mismatch')
    reports = {}
    for name in verifier.NAMES:
        path = ROOT / '.build' / ('cyd-vorbis-uint32-rate-' + name + '-01') / 'report.json'
        data = path.read_bytes()
        report = json.loads(data)
        context = report['setup_macro_context']
        row = context['row']
        argv = row['arguments'] if 'arguments' in row else verifier.windows_args(row['command'])
        if argv != context['original_argv']:
            raise RuntimeError('Recorded Windows argv parser mismatch: ' + name)
        reports[name] = dict(path=str(path), sha256=sha(data), recorded_macro_argv_roundtrip=True)
    files = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
             for p in sorted(HERE.iterdir()) if p.is_file()}
    result = dict(result='SOURCE_ONLY_READY', python_ast_files=3, fixed_source_projection=True,
        actual_recorded_macro_argv_roundtrips=5, report_identities=reports, files=files,
        archive_packed=False, offline_archive_verifier_executed=False, target_protocol_revalidated=False,
        SDK_compiler_QEMU_codec_Git_invoked=False, canonical_or_campaign_modified=False)
    data = (json.dumps(result, indent=2) + '\n').encode()
    with output.open('xb') as stream:
        stream.write(data)
    print(json.dumps(dict(result=result['result'], source_checks_sha256=sha(data),
                         archive_packed=False, offline_archive_verifier_executed=False)))


if __name__ == '__main__':
    main()
