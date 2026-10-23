"""Materialize the pinned finite owned-book evidence; never execute any verifier."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct

PLAN_SHA = '49540a8a0ce0667c88c68b044e36e5b43cb6f4dbf2caf4326416d5e5122acdd8'
BINARY = {'.elf', '.bin', '.a', '.o', '.obj', '.exe', '.dll', '.rom', '.lib', '.zip', '.pyc'}
TEXT_BUILD = ('compile_commands.json', 'project_description.json', 'CMakeCache.txt', 'build.ninja',
              'CMakeFiles/rules.ninja', 'flasher_args.json', 'flash_args', 'cyd_vorbis_owned_book_unit.map')


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe(value):
    value = str(value).replace('\\', '/')
    path = PurePosixPath(value)
    need(value and not path.is_absolute() and '..' not in path.parts and ':' not in value, 'Unsafe archive key')
    return path.as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    repo, out = args.repository.resolve(), args.output.resolve()
    plan_raw = (here / 'plan.json').read_bytes()
    need(sha(plan_raw) == PLAN_SHA, 'Exact reviewed parent terminal plan required')
    plan = json.loads(plan_raw)
    need(plan['state'] == 'ACTUAL_PARENT_TERMINALS_PINNED' and Path(plan['repository']).resolve() == repo,
         'Wrong repository or pending terminal plan')
    roots = [Path(x['path']).resolve() for x in plan['preparations'] + plan['roles']]
    durable = out == repo / plan['canonical_destination']
    scratch = out.is_relative_to(repo / '.build') and out != repo / '.build'
    need(not out.exists() and (durable or scratch) and all(not out.is_relative_to(p) and not p.is_relative_to(out)
        for p in (*roots, here)), 'Fresh separate .build stage or exact canonical destination required')
    need(all(p.is_dir() and p.is_relative_to(repo / '.build') for p in roots), 'Pinned worktree preparations/campaigns required')
    reports = {}
    for role in plan['roles']:
        report_raw = (Path(role['path']) / 'report.json').read_bytes()
        terminal_raw = Path(role['terminal_path']).read_bytes()
        need(sha(report_raw) == role['report_sha256'] and sha(terminal_raw) == role['terminal_sha256'], 'Pinned actual role bytes changed')
        report, terminal = json.loads(report_raw), json.loads(terminal_raw)
        need(terminal['schema'] == 'direct-exec-tool-terminal-v1' and type(terminal['session_id']) is int
             and terminal['exit_code'] == role['expected_exit_code'] and terminal['report_sha256'] == sha(report_raw)
             and report['result'] == role['expected_result'], 'Missing/wrong actual parent terminal')
        reports[role['role']] = report
    out.mkdir(parents=True, exist_ok=False)
    manifest = dict(schema='cyd-owned-book-evidence-archive-v1', files={}, omitted={}, preparations={}, campaigns={},
        plan_sha256=PLAN_SHA, source_only_packer=False, scope='Exact production owned parser plus bounded public vector consumer',
        vendor_backend_qualified=False, PCM_qualified=False, full_G6_qualified=False, physical_qualified=False,
        production_radio_integration=False, omitted_binary_bytes_replayable=False,
        QMP_EOF_direct_boolean_recorded=False, QMP_EOF_enforced_by_exact_captured_helper=True)
    originals = {}

    def put(data, key, origin, derived=None):
        key = safe(key)
        need(key not in manifest['files'] and key not in manifest['omitted'], 'Duplicate archive key: ' + key)
        compress = len(data) >= 16384 and Path(key).suffix.lower() not in ('.py', '.c', '.h', '.ps1', '.cmake', '.diff')
        stored = key + ('.gz' if compress else '')
        encoded = gzip.compress(data, compresslevel=9, mtime=0) if compress else data
        target = out / stored
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(encoded)
        row = dict(origin=str(origin).replace('\\', '/'), bytes=len(data), sha256=sha(data), stored=stored,
                   stored_bytes=len(encoded), stored_sha256=sha(encoded), compression='gzip' if compress else 'none')
        if derived is not None:
            row['derived_from_full_sha256'] = derived
        manifest['files'][key] = row

    def add(path, key, expected=None, fixture=False, tool=False):
        path = Path(path)
        key = safe(key)
        need(path.is_file() and not path.is_symlink(), 'Missing/symlink input: ' + str(path))
        data = path.read_bytes()
        digest = sha(data)
        need(expected is None or expected == digest, 'Changed pinned evidence: ' + str(path))
        if key in manifest['files'] or key in manifest['omitted']:
            row = manifest['files'].get(key, manifest['omitted'].get(key))
            need(row['sha256'] == digest and row['bytes'] == len(data), 'Conflicting repeated input key')
            return
        originals[str(path.resolve())] = digest
        if tool or (path.suffix.lower() in BINARY and not fixture):
            need(path.suffix.lower() not in ('.o', '.obj', '.pyc'), 'Object/cache bytes are outside this focused record')
            row = dict(origin=str(path.resolve()).replace('\\', '/'), bytes=len(data), sha256=digest,
                       reason='Identity only; runtime/tool binary bytes omitted; no replay claim')
            if path.suffix.lower() == '.elf':
                need(len(data) >= 64 and data[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', data, 18)[0] == 94,
                     'Actual little-endian ELF32/Xtensa header required')
                header_key = key + '.header64'
                put(data[:64], header_key, str(path.resolve()) + '[0:64]', derived=digest)
                row.update(elf_header_key=header_key, elf_machine=94, elf_header_bytes=64)
            manifest['omitted'][key] = row
        else:
            put(data, key, path.resolve())

    add(here / 'plan.json', 'plan.json', PLAN_SHA)
    for name in ('verify.py', 'protocol.py', 'pack.py', 'README.md', 'source-checks.json'):
        add(here / name, name)
    put(b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n', '.gitattributes', 'packer literal raw-byte policy')
    for prep in plan['preparations']:
        root = Path(prep['path'])
        index_raw = (root / prep['index']).read_bytes()
        need(sha(index_raw) == prep['index_sha256'], 'Reviewed preparation index changed')
        index = json.loads(index_raw)
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        need(actual == set(index['files']) | {prep['index']}, 'Preparation file set changed')
        prefix = 'preparations/' + prep['name']
        for name in sorted(actual):
            expected = prep['index_sha256'] if name == prep['index'] else index['files'][name]['sha256']
            add(root / name, prefix + '/' + name, expected, fixture='/fixtures/setup/' in '/' + name)
        manifest['preparations'][prep['name']] = dict(prefix=prefix, index=prep['index'], index_sha256=prep['index_sha256'])
    for role in plan['roles']:
        name, root, report = role['role'], Path(role['path']), reports[role['role']]
        prefix = 'campaigns/' + name
        add(Path(role['terminal_path']), prefix + '/parent-terminal.json', role['terminal_sha256'])
        for path in sorted(root.iterdir()):
            if path.is_file() and path.suffix.lower() not in BINARY and path.name != 'report.json.tmp':
                add(path, prefix + '/' + path.name,
                    role['report_sha256'] if path.name == 'report.json' else None)
        for path in sorted((root / 'sources').rglob('*')):
            if path.is_file():
                rel = path.relative_to(root).as_posix()
                add(path, prefix + '/' + rel, fixture='/fixtures/setup/' in '/' + rel)
        for origin, fact in report['inputs'].items():
            snapshot = root / fact['snapshot']
            need(snapshot.resolve().is_relative_to(root / 'sources') and sha(snapshot.read_bytes()) == fact['sha256']
                 and snapshot.stat().st_size == fact['bytes'], 'Declared actual input snapshot mismatch')
            add(snapshot, prefix + '/' + fact['snapshot'], fact['sha256'], fixture='/fixtures/setup/' in '/' + fact['snapshot'])
            original = Path(origin)
            need(original.is_file() and sha(original.read_bytes()) == fact['sha256'], 'Current declared original differs from frozen input')
            originals[str(original.resolve())] = fact['sha256']
        for rel, digest in report['build_outputs'].items():
            path = root / safe(rel)
            need(path.resolve().is_relative_to(root), 'Build output escaped campaign')
            add(path, prefix + '/' + safe(rel), digest)
        for rel in TEXT_BUILD:
            path = root / 'build' / rel
            if path.is_file():
                add(path, prefix + '/build/' + rel)
        tool_keys = {}
        for index, (path, digest) in enumerate(report['tools'].items()):
            key = prefix + '/tools/' + f'{index:02d}-' + Path(path).name
            add(Path(path), key, digest, tool=True)
            tool_keys[path] = key
        manifest['campaigns'][name] = dict(prefix=prefix, historical_root=role['path'], prep=role['prep'],
            report_sha256=role['report_sha256'], terminal_sha256=role['terminal_sha256'],
            expected_result=role['expected_result'], expected_exit_code=role['expected_exit_code'], tool_keys=tool_keys)
    for path, expected in originals.items():
        need(Path(path).is_file() and sha(Path(path).read_bytes()) == expected, 'Input changed during materialization: ' + path)
    with (out / 'manifest.json').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(result='OWNED_BOOK_EVIDENCE_MATERIALIZED_UNVERIFIED', files=len(manifest['files']),
        omitted=len(manifest['omitted']), manifest_sha256=sha((out / 'manifest.json').read_bytes()),
        verifier_executed=False, vendor_backend_qualified=False, PCM_qualified=False, full_G6_qualified=False)))


if __name__ == '__main__':
    main()
