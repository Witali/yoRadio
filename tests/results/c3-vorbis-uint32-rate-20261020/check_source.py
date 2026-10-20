"""AST and completed-baseline source/argv checks; no pack/verify/protocol run."""
import ast
import difflib
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
        raise RuntimeError('Preserve source checks')
    for name in ('pack.py', 'verify.py', 'adapt.py', 'check_source.py'):
        ast.parse((HERE / name).read_bytes())
    spec = importlib.util.spec_from_file_location('c3_rate_archive_source_review', HERE / 'verify.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    source = ROOT / '.build/c3-vorbis-uint32-rate-source-01'
    before, after = (source / 'before.c').read_bytes(), (source / 'after.c').read_bytes()
    assert sha(before) == verifier.BEFORE and sha(after) == verifier.AFTER
    assert verifier.fixed_source(before) == after and before.count(b'\n') == before.count(b'\r\n')
    baseline = ROOT / '.build/c3-vorbis-uint32-rate-baseline-01'
    report_bytes = (baseline / 'report.json').read_bytes()
    report = json.loads(report_bytes)
    context = report['setup_macro_context']
    assert verifier.windows_args(context['row']['command']) == context['original_argv']
    assert report['platform'] == 'esp32c3' and report['sdk_revision'] == verifier.SDK and report['elf_machine'] == 243
    assert report['coordinator_core'] == report['worker_core'] == 0
    cflags = (baseline / 'build/toolchain/cflags').read_bytes()
    assert len(cflags.decode().splitlines()) == 4 and b'-march=rv32imc_zicsr_zifencei' in cflags
    prep = ROOT / '.build/c3-vorbis-uint32-rate-sdk-prep-01'
    assert sha((prep / 'rate_protocol.py').read_bytes()) == verifier.PROTOCOL
    assert sha((prep / 'test_rate_protocol.py').read_bytes()) == verifier.TESTS
    assert sha((prep / 'target/c3_vorbis_uint32_rate_qemu/main/main.c').read_bytes()) == verifier.CALLER
    host = json.loads((prep / 'host-tests.command.json').read_bytes())
    assert host['schema'] == 'c3-rate-pure-host-tests-v1' and host['inputs_before'] == host['inputs_after']
    for row in host['inputs_before']:
        data = Path(row['path']).read_bytes()
        assert sha(data) == row['sha256'] and len(data) == row['bytes']
    base = ROOT / '.build/cyd-vorbis-uint32-rate-archive-prep-02'
    diff = ''.join(''.join(difflib.unified_diff((base / name).read_text().splitlines(True),
        (HERE / name).read_text().splitlines(True), fromfile='CYD02/' + name, tofile='C3-01/' + name))
        for name in ('pack.py', 'verify.py'))
    (HERE / 'adaptation.diff').write_bytes(diff.encode())
    files = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in sorted(HERE.iterdir()) if p.is_file()}
    result = dict(result='SOURCE_ONLY_READY', python_ast_files=4, exact_CRLF_source_projection=True,
        actual_completed_baseline_macro_argv_roundtrip=True, C3_pinned_protocol_caller_and_tests=True,
        baseline_report_sha256=sha(report_bytes), SDK_prep_readiness_sha256=sha((prep / 'readiness.json').read_bytes()),
        files=files, archive_packed=False, offline_archive_verifier_executed=False, target_protocol_revalidated=False,
        live_acceptance_limited_or_control_read=False, SDK_compiler_QEMU_codec_Git_invoked=False,
        canonical_or_campaign_modified=False)
    data = (json.dumps(result, indent=2) + '\n').encode()
    with output.open('xb') as stream:
        stream.write(data)
    print(json.dumps(dict(result=result['result'], source_checks_sha256=sha(data), archive_packed=False,
                         offline_archive_verifier_executed=False)))


if __name__ == '__main__':
    main()
