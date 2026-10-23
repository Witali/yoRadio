"""Focused C3 source/evidence packer; no SDK, compiler, codec, emulator, or Git calls."""
import argparse
import gzip
import json
from pathlib import Path
from dependency import Dependency, MANIFEST_SHA, need, norm, obj, rel, sha

ROLES = {'baseline', 'acceptance', 'numeric'}
CONTEXT = ('compile_commands.json', 'project_description.json', 'flasher_args.json',
           'build.ninja', 'CMakeCache.txt', 'config/sdkconfig.h', 'toolchain/cflags', 'specs/picolibc.specs')
SELF = ('pack.py', 'verify.py', 'dependency.py', 'README.md', 'plan.template.json',
        'source-relation.json', 'readiness.json', 'pack-adaptation.diff', 'verify-adaptation.diff',
        'check_source.py', 'source-closure.json')


def pack(repo, out, plan_path):
    repo, out, plan_path = repo.resolve(), out.resolve(), plan_path.resolve()
    plan = obj(plan_path.read_bytes())
    need(plan['schema'] == 'c3-map2-selection-v1' and set(plan['roles']) == ROLES and
         plan['dependency_manifest_sha256'] == MANIFEST_SHA, 'Exact C3/dependency role selection required')
    need(out.is_relative_to(repo / '.build') and out != repo / '.build' and not out.exists(),
         'Use a fresh independent .build stage')
    roots = [(repo / rel(item['path'])).resolve() for item in plan['roles'].values()]
    roots += [(repo / rel(path)).resolve() for path in plan['trees']]
    need(all(p.is_relative_to(repo) and p.is_dir() and not (p.is_relative_to(out) or out.is_relative_to(p))
             for p in roots), 'Missing or overlapping C3 input roots')
    dep = Dependency(repo)
    manifest = dict(schema='c3-map2-checkpoint-v1', repository=norm(repo), plan=plan, files={},
        aliases={}, roles={}, external_omitted={}, generated={}, verified=False,
        dependency_archive=dict(path='tests/results/cyd-vorbis-map2-20261020', manifest_sha256=MANIFEST_SHA,
            required=True, standalone=False), intended_destination='tests/results/c3-vorbis-map2-20261023',
        full_G6_qualified=False, physical_device=False, production_firmware=False)
    out.mkdir(parents=True, exist_ok=False)
    originals = {}

    def borrow(key):
        key = rel(key)
        source = dep.files[key]
        need(source['stored'] is not None, 'Only retained raw dependency entries may be borrowed')
        data = dep.read(key)
        row = dict(raw_bytes=len(data), raw_sha256=sha(data), stored=None, dependency_key=key)
        if key in manifest['files']:
            need(manifest['files'][key]['raw_sha256'] == row['raw_sha256'], 'Conflicting dependency identity')
        else:
            manifest['files'][key] = row
        return key

    def add(path, expected=None, stored=None, allow_borrow=True):
        path = path.resolve()
        need(path.is_relative_to(repo) and path.is_file(), 'Missing/outside source: ' + str(path))
        key = path.relative_to(repo).as_posix()
        data = path.read_bytes()
        need(expected is None or sha(data) == expected, 'Original source identity changed: ' + key)
        if key in manifest['files']:
            need(manifest['files'][key]['raw_sha256'] == sha(data), 'Conflicting local input identity')
            return key
        if allow_borrow and key in dep.files and dep.files[key]['stored'] is not None:
            need(dep.files[key]['raw_sha256'] == sha(data) and dep.read(key) == data,
                 'Exact original-path committed dependency identity required')
            return borrow(key)
        originals[key] = path
        row = dict(raw_bytes=len(data), raw_sha256=sha(data), stored=None)
        binary = path.suffix.lower() in {'.elf', '.a', '.exe', '.dll', '.rom', '.zip', '.o', '.obj'}
        binary |= path.suffix.lower() == '.bin' and ('build' in path.relative_to(repo).parts or path.name == 'qemu-flash.bin')
        if binary:
            row['omitted'] = 'Actual target/tool/package binary bytes hashed, not copied'
            if path.suffix.lower() == '.elf':
                need(len(data) >= 64 and data[:4] == b'\x7fELF', 'Actual ELF header required')
                row['actual_elf_header64_hex'] = data[:64].hex()
        else:
            compressed = len(data) > 65536 and path.suffix.lower() not in {'.py', '.h', '.ogg'}
            compressed |= path.suffix.lower() in {'.wav', '.s16le', '.pcm'}
            blob = gzip.compress(data, compresslevel=9, mtime=0) if compressed else data
            name = stored or 'payload/' + key
            if compressed:
                name += '.gz'
            dest = (out / rel(name)).resolve()
            need(dest.is_relative_to(out) and not dest.exists(), 'Unsafe/duplicate stored file')
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as stream:
                stream.write(blob)
            row.update(stored=dest.relative_to(out).as_posix(), encoding='gzip' if compressed else 'raw',
                       stored_bytes=len(blob), stored_sha256=sha(blob))
        manifest['files'][key] = row
        return key

    def tool(path, expected):
        path = Path(path).resolve()
        data = path.read_bytes()
        need(sha(data) == expected, 'Installed historical tool/archive identity changed')
        row = dict(raw_bytes=len(data), raw_sha256=expected, omitted='Actual tool/archive/ROM bytes hashed, not copied')
        key = norm(path)
        need(key not in manifest['external_omitted'] or manifest['external_omitted'][key] == row,
             'Conflicting tool/archive identity')
        manifest['external_omitted'][key] = row

    def receipt(path):
        path = (repo / rel(path)).resolve()
        key = add(path)
        record = obj(path.read_bytes())
        for name, row in record.get('logs', {}).items():
            add(Path(name), row['sha256'])
        if 'executable_sha256' in record:
            tool(record['argv'][0], record['executable_sha256'])
        return key

    for role, item in plan['roles'].items():
        root = (repo / rel(item['path'])).resolve()
        report = obj((root / 'report.json').read_bytes())
        need(sha((root / 'report.json').read_bytes()) == item['report_sha256'], 'Reviewed actual report identity differs')
        manifest['roles'][role] = dict(root=root.relative_to(repo).as_posix(), kind='numeric' if role == 'numeric' else 'target',
            terminal=receipt(item['terminal']), expected_outer_exit=item['expected_outer_exit'])
        selected = [p for p in root.iterdir() if p.is_file()]
        for folder in ('sources', 'variant', 'observed-pcm'):
            selected += [p for p in (root / folder).rglob('*') if p.is_file()]
        selected += [root / 'build' / path for path in CONTEXT if (root / 'build' / path).is_file()]
        selected += list((root / 'build').glob('*.map'))
        for field in ('build_outputs', 'variant_sources'):
            selected += [root / rel(path) for path in report.get(field, {})]
        for path in sorted(set(selected)):
            add(path, allow_borrow=False)  # Preserve actual C3 snapshots locally, even when bytes match CYD.
        aliases = manifest['aliases'][role] = {}
        for original, row in report.get('inputs', {}).items():
            path = root / rel(row['snapshot']) if 'snapshot' in row else Path(row['path'])
            key = add(path, row['sha256'], allow_borrow='snapshot' not in row)
            aliases[norm(original if 'snapshot' in row else row['path'])] = key
        for path, digest in report.get('tools', {}).items():
            tool(path, digest)

    # Retain the two exact independently qualified host scopes by explicit pinned
    # committed-archive keys. Their actual files are never recopied or synthesized.
    for role in ('host-old17', 'host-new8'):
        source_role = dep.manifest['roles'][role]
        manifest['roles'][role] = dict(source_role, dependency_role=True, expected_outer_exit=1)
        manifest['aliases'][role] = dict(dep.manifest['aliases'][role])
        keys = [key for key in dep.files if key.startswith(source_role['root'] + '/')]
        keys += list(manifest['aliases'][role].values()) + [source_role['terminal']]
        name = 'old17' if role == 'host-old17' else 'new8'
        keys.append(dep.manifest['plan']['hosts'][name]['qualification'])
        for key in sorted(set(keys)):
            borrow(key)

    for path in plan['trees']:
        for source in sorted((repo / rel(path)).rglob('*')):
            if source.is_file():
                add(source, allow_borrow=False)
    for path in plan['extras']:
        add(repo / rel(path))
    for name in SELF:
        add(Path(__file__).with_name(name), stored=name, allow_borrow=False)
    add(plan_path, stored='selection.json', allow_borrow=False)
    attributes = b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n'
    (out / '.gitattributes').write_bytes(attributes)
    manifest['generated']['.gitattributes'] = dict(bytes=len(attributes), sha256=sha(attributes))
    for key, path in originals.items():
        need(sha(path.read_bytes()) == manifest['files'][key]['raw_sha256'], 'Source changed during packing')
    for path, row in manifest['external_omitted'].items():
        need(sha(Path(path).read_bytes()) == row['raw_sha256'], 'Tool/archive changed during packing')
    dep.current()
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(packed=True, verified=False, files=len(manifest['files']),
        borrowed_files=sum('dependency_key' in row for row in manifest['files'].values()), output=str(out))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    args = parser.parse_args()
    pack(args.repository, args.output, args.plan)
