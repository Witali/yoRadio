"""AST/raw preparation only: never import or run packer/verifier/protocol."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    output = HERE / 'source-checks.json'
    readiness = HERE / 'readiness.json'
    if output.exists() or readiness.exists():
        raise RuntimeError('Preserve source-only preparation receipts')
    scripts = [HERE / n for n in ('pack.py', 'verify.py', 'protocol.py', 'source_checks.py')]
    for path in scripts:
        ast.parse(path.read_bytes(), filename=path.name)
    assert sha(HERE / 'plan.json') == '49540a8a0ce0667c88c68b044e36e5b43cb6f4dbf2caf4326416d5e5122acdd8'
    assert sha(HERE / 'protocol.py') == 'c87b344b9ad84af3434e8e13f82560e988490c85edcdc53cbc8888553f5ce21c'
    plan = json.loads((HERE / 'plan.json').read_bytes())
    facts = []
    for role in plan['roles']:
        for name,path,digest in (('report',Path(role['path']) / 'report.json',role['report_sha256']),
                                 ('parent-terminal',Path(role['terminal_path']),role['terminal_sha256'])):
            assert sha(path) == digest
            facts.append(dict(role=role['role'], kind=name, bytes=path.stat().st_size, sha256=digest))
    for prep in plan['preparations']:
        path = Path(prep['path']) / prep['index']
        assert sha(path) == prep['index_sha256']
        facts.append(dict(preparation=prep['name'], index=prep['index'], sha256=prep['index_sha256']))
    result = dict(schema='owned-book-archive-source-only-checks-v1', result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=len(scripts), raw_terminal_report_and_prep_index_facts=facts,
        packer_or_verifier_executed=False, archive_materialized=False, archive_qualified=False,
        SDK_compiler_QEMU_unit_tests_decoder_or_reference_executed=False,
        canonical_Git_archives_or_campaigns_modified=False, full_G6_qualified=False)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    files = {p.relative_to(HERE).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))
             for p in sorted(HERE.rglob('*')) if p.is_file()}
    readiness.write_text(json.dumps(dict(schema='owned-book-archive-source-only-readiness-v1',
        archive_materialized=False, packer_or_verifier_executed=False, files=files),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(result=result['result'],files=len(files),readiness_sha256=sha(readiness),
                         packer_or_verifier_executed=False)))


if __name__ == '__main__':
    main()
