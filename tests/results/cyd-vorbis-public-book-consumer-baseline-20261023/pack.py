"""Pack standalone owned/public book baseline evidence, without executing its verifier."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct

BINARY = {'.elf', '.bin', '.a', '.exe', '.dll', '.rom', '.lib', '.zip'}
TEXT_BUILD = ('compile_commands.json', 'project_description.json', 'CMakeCache.txt', 'build.ninja',
              'CMakeFiles/rules.ninja', 'flasher_args.json', 'flash_args', 'config/sdkconfig.h',
              'toolchain/cflags', 'specs/picolibc.specs', 'cyd_vorbis_owned_book_unit.map')


def need(ok, reason):
    if not ok: raise RuntimeError(reason)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def safe(value):
    value = str(value).replace('\\', '/'); path = PurePosixPath(value)
    need(value and not path.is_absolute() and '..' not in path.parts and ':' not in value, 'Safe relative archive key')
    return path.as_posix()


def indexed(index):
    return index['files'] if isinstance(index['files'], dict) else {row['path']: row for row in index['files']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'output', 'plan'): parser.add_argument('--' + name, type=Path, required=True)
    for name in ('plan-sha256', 'readiness-sha256'): parser.add_argument('--' + name, required=True)
    args = parser.parse_args(); here = Path(__file__).resolve().parent; repo = args.repository.resolve(); out = args.output.resolve()
    planraw = args.plan.resolve().read_bytes(); need(sha(planraw) == args.plan_sha256, 'Exact root-reviewed selection plan')
    plan = json.loads(planraw)
    need(plan['schema'] == 'public-book-baseline-archive-plan-v1' and plan['state'] == 'ACTUAL_PARENT_TERMINALS_PINNED' and
         Path(plan['repository']).resolve() == repo and plan['archive_data_dependencies'] == [] and
         plan['canonical_destination'] == 'tests/results/cyd-vorbis-public-book-consumer-baseline-20261023', 'Standalone finite actual baseline plan')
    readyraw = (here / 'readiness.json').read_bytes(); need(sha(readyraw) == args.readiness_sha256, 'Reviewed archive source readiness')
    ready = json.loads(readyraw)
    need(ready['schema'] == 'public-book-baseline-archive-source-readiness-v1' and ready['source_only'] is True and
         {p.relative_to(here).as_posix() for p in here.rglob('*') if p.is_file()} == set(ready['files']) | {'readiness.json'}, 'Complete immutable archive source set')
    for name, row in ready['files'].items():
        raw = (here / safe(name)).read_bytes(); need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Archive source identity')
    roots = [Path(row['path']).resolve() for row in plan['preparations'] + plan['roles']]
    need(out.is_relative_to(repo / '.build') and out != repo / '.build' and not out.exists() and
         not out.is_relative_to(here) and not here.is_relative_to(out) and
         all(p.is_dir() and p.is_relative_to(repo / '.build') and not out.is_relative_to(p) and not p.is_relative_to(out) for p in roots), 'Fresh nonoverlapping stage')
    need([row['role'] for row in plan['roles']] == ['SDK', 'host'], 'Both actual separate baseline campaigns')
    out.mkdir(parents=True, exist_ok=False)
    m = dict(schema='public-book-consumer-baseline-archive-v1', plan_sha256=args.plan_sha256, files={}, omitted={},
        preparations={}, campaigns={}, extra_receipts=[], extra_files=[], record_only=[], recorded_external_tools={}, archive_data_dependencies=[],
        standalone=True, verified=False, host_sanitizers_qualified=False, public_arithmetic_portability_qualified=False,
        full_standard_qualified=False, vendor_cause_diagnosed=False, full_G6_qualified=False, physical_device=False,
        production_radio_integration=False, omitted_binary_bytes_replayable=False)
    originals = {}

    def put(raw, key, origin, derived=None):
        key = safe(key); need(key not in m['files'] and key not in m['omitted'], 'Unique archive key')
        compressed = len(raw) >= 16384 and Path(key).suffix.lower() not in ('.py', '.c', '.h', '.inc', '.ps1', '.cmake', '.diff')
        encoded = gzip.compress(raw, compresslevel=9, mtime=0) if compressed else raw; stored = key + ('.gz' if compressed else '')
        dest = out / safe(stored); dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as stream: stream.write(encoded)
        row = dict(origin=str(origin).replace('\\', '/'), bytes=len(raw), sha256=sha(raw), stored=stored,
                   stored_bytes=len(encoded), stored_sha256=sha(encoded), compression='gzip' if compressed else 'none')
        if derived is not None: row['derived_from_full_sha256'] = derived
        m['files'][key] = row

    def add(path, key, expected=None, tool=False, binary=False):
        need(not Path(path).is_symlink(), 'No symlink source'); path = Path(path).resolve(); key = safe(key)
        need(path.is_file() and (tool or path.is_relative_to(repo)), 'Regular scoped source or explicit hash-only tool')
        raw = path.read_bytes(); digest = sha(raw); need(expected is None or digest == expected, 'Pinned original changed: ' + str(path))
        if key in m['files'] or key in m['omitted']:
            row = m['files'].get(key, m['omitted'].get(key)); need(row['sha256'] == digest and row['bytes'] == len(raw), 'Repeated identity differs'); return key
        originals[str(path)] = digest
        fixture = path.suffix.lower() == '.bin' and ('fixtures' in path.parts or 'sources' in path.parts)
        if tool or binary or (path.suffix.lower() in BINARY and not fixture):
            row = dict(origin=str(path).replace('\\', '/'), bytes=len(raw), sha256=digest, reason='Actual tool/app/library binary body omitted; hash identity only')
            if path.suffix.lower() == '.elf':
                need(len(raw) >= 64 and raw[:7] == b'\x7fELF\x01\x01\x01' and struct.unpack_from('<H', raw, 18)[0] == 94, 'Actual own ELF32/Xtensa94 header')
                header = key + '.header64'; put(raw[:64], header, str(path) + '[0:64]', derived=digest)
                row.update(elf_header_key=header, elf_machine=94, elf_header_bytes=64)
            elif binary and path.name == 'consumer-baseline':
                need(len(raw) >= 64 and raw[:7] == b'\x7fELF\x02\x01\x01' and struct.unpack_from('<H', raw, 18)[0] == 62, 'Actual own host ELF64/x86_64 header')
                header = key + '.header64'; put(raw[:64], header, str(path) + '[0:64]', derived=digest)
                row.update(elf_header_key=header, elf_machine=62, elf_header_bytes=64)
            m['omitted'][key] = row
        else: put(raw, key, path)
        return key

    def receipt(path, key, expected, code):
        raw = Path(path).read_bytes(); need(sha(raw) == expected, 'Exact actual outer receipt')
        value = json.loads(raw); actual = value.get('exit_code', value.get('returncode'))
        need(type(actual) is int and actual == code and (value.get('status') == 'TERMINAL' or value.get('schema') == 'direct-exec-tool-terminal-v1'), 'Actual parent terminal')
        entry = dict(key=add(path, key, expected), log_keys={}, tool_key=None)
        for index, (origin, row) in enumerate(value.get('logs', {}).items()):
            entry['log_keys'][origin] = add(origin, key + '.streams/' + f'{index:02d}-' + Path(origin).name, row['sha256'])
        if 'executable_sha256' in value:
            entry['tool_key'] = add(value['argv'][0], key + '.tool/' + Path(value['argv'][0]).name, value['executable_sha256'], tool=True)
        return entry

    put(planraw, 'plan.json', args.plan.resolve())
    for name in sorted(ready['files']): add(here / name, name, ready['files'][name]['sha256'])
    add(here / 'readiness.json', 'readiness.json', args.readiness_sha256)
    add(plan['checkpoint']['path'], 'CHECKPOINT.md', plan['checkpoint']['sha256'])
    put(b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n', '.gitattributes', 'literal raw-byte policy')
    for row in plan['preparations']:
        root = Path(row['path']); prefix = 'preparations/' + safe(row['name']); indexraw = (root / row['index']).read_bytes()
        need(sha(indexraw) == row['index_sha256'], 'Reviewed complete preparation index')
        index = json.loads(indexraw); entries = indexed(index); names = {q.relative_to(root).as_posix() for q in root.rglob('*') if q.is_file()}
        need(names == set(entries) | {row['index']}, 'Every preparation/runtime/proposal file')
        for name in sorted(names): add(root / name, prefix + '/' + safe(name), row['index_sha256'] if name == row['index'] else entries[name]['sha256'])
        m['preparations'][row['name']] = dict(prefix=prefix, index=row['index'], index_sha256=row['index_sha256'])
    for role in plan['roles']:
        name = role['role']; root = Path(role['path']); prefix = 'campaigns/' + name; report = json.loads((root / 'report.json').read_bytes())
        need(sha((root / 'report.json').read_bytes()) == role['report_sha256'], 'Actual reviewed report')
        outer = receipt(role['terminal_path'], prefix + '/parent-terminal.json', role['terminal_sha256'], role['expected_exit_code'])
        for path in sorted(root.iterdir()):
            if path.is_file() and path.name != 'report.json.tmp': add(path, prefix + '/' + path.name, binary=path.name == 'consumer-baseline')
        inputs, tools = {}, {}
        if name == 'SDK':
            for path in sorted((root / 'sources').rglob('*')):
                if path.is_file(): add(path, prefix + '/' + path.relative_to(root).as_posix())
            for origin, fact in report['inputs'].items():
                snapshot = safe(fact['snapshot']); path = (root / snapshot).resolve()
                need(path.is_relative_to(root / 'sources') and path.stat().st_size == fact['bytes'], 'Bounded exact input snapshot')
                inputs[origin] = add(path, prefix + '/' + snapshot, fact['sha256'])
                need(sha(Path(origin).read_bytes()) == fact['sha256'], 'Original input changed from actual snapshot'); originals[origin] = fact['sha256']
            for rel, digest in report['build_outputs'].items(): add(root / safe(rel), prefix + '/' + safe(rel), digest)
            for rel in TEXT_BUILD:
                if (root / 'build' / rel).is_file(): add(root / 'build' / rel, prefix + '/build/' + rel)
            for index, (origin, digest) in enumerate(report['tools'].items()): tools[origin] = add(origin, prefix + '/tools/' + f'{index:02d}-' + Path(origin).name, digest, tool=True)
        else:
            add(root / 'consumer-baseline', prefix + '/consumer-baseline', report['host_binary_sha256'], binary=True)
            m['recorded_external_tools'] = {
                report['commands'][0]['argv'][0]: dict(sha256=report['compiler_sha256'], evidence_source=prefix + '/report.json', new_Windows_rehash=False, body_omitted=True),
                report['host_python_path']: dict(sha256=report['host_python_sha256'], evidence_source=prefix + '/report.json', new_Windows_rehash=False, body_omitted=True)}
        m['campaigns'][name] = dict(prefix=prefix, historical_root=str(root), report_sha256=role['report_sha256'], outer=outer,
                                   input_keys=inputs, tool_keys=tools)
    for index, row in enumerate(plan['extra_receipts']):
        m['extra_receipts'].append(receipt(row['path'], 'root-receipts/' + f'{index:02d}-' + Path(row['path']).name, row['sha256'], row['expected_exit_code']))
    for row in plan['extra_files']: m['extra_files'].append(add(row['path'], 'root-sources/' + Path(row['path']).name, row['sha256']))
    for index, row in enumerate(plan['record_only']):
        need(row['record_only'] is row['inputs_not_traversed'] is True, 'Prior results are record-only')
        m['record_only'].append(add(row['path'], 'record-only/' + f'{index:02d}-' + Path(row['path']).name, row['sha256']))
    for origin, digest in originals.items(): need(sha(Path(origin).read_bytes()) == digest, 'Declared original changed during packing')
    with (out / 'manifest.json').open('x', encoding='utf-8', newline='\n') as stream: stream.write(json.dumps(m, indent=2) + '\n')
    print(json.dumps(dict(result='BASELINE_EVIDENCE_PACKED_UNVERIFIED', files=len(m['files']), omitted=len(m['omitted']), manifest_sha256=sha((out / 'manifest.json').read_bytes()), verifier_executed=False)))


if __name__ == '__main__': main()
