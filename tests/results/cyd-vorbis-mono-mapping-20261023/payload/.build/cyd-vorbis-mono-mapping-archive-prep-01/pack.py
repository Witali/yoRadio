"""Focused CYD mono/mapping21 source/evidence packer; no SDK, compiler, codec, emulator, or Git calls."""
import argparse
import gzip
import json
from pathlib import Path
from dependency import Dependency, MANIFEST_SHA, need, norm, obj, rel, sha

ROLES = {'capture21', 'numeric21', 'numeric-input-failure01', 'host21'}
CONTEXT = ('compile_commands.json', 'project_description.json', 'flasher_args.json',
           'build.ninja', 'CMakeCache.txt', 'config/sdkconfig.h', 'toolchain/cflags', 'specs/picolibc.specs')

def pack(repo, out, plan_path, readiness_sha256):
    repo, out, plan_path = repo.resolve(), out.resolve(), plan_path.resolve()
    plan = obj(plan_path.read_bytes())
    here = Path(__file__).resolve().parent
    need(sha((here / 'readiness.json').read_bytes()) == readiness_sha256, 'Root-reviewed archive source readiness')
    readiness = obj((here / 'readiness.json').read_bytes())
    need(readiness['schema'] == 'mono-mapping-archive-source-only-readiness-v1' and readiness['runtime_executed'] is False, 'Source-only archive readiness')
    need({p.relative_to(here).as_posix() for p in here.rglob('*') if p.is_file()} == set(readiness['files']) | {'readiness.json'}, 'Exact archive-preparation inventory')
    for name, row in readiness['files'].items():
        raw = (here / rel(name)).read_bytes()
        need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Archive-preparation source identity')
    need(plan['schema'] == 'cyd-mono-mapping-selection-v1' and set(plan['roles']) == ROLES and
         plan['dependency_manifest_sha256'] == MANIFEST_SHA, 'Exact CYD mono/mapping dependency role selection required')
    need(out.is_relative_to(repo / '.build') and out != repo / '.build' and not out.exists(),
         'Use a fresh independent .build stage')
    need(not (out == here or out.is_relative_to(here) or here.is_relative_to(out)), 'Archive stage must not overlap immutable preparation')
    roots = [(repo / rel(item['path'])).resolve() for item in plan['roles'].values()]
    roots += [(repo / rel(path)).resolve() for path in plan['trees']]
    need(all(p.is_relative_to(repo) and p.is_dir() and not (p.is_relative_to(out) or out.is_relative_to(p))
             for p in roots), 'Missing or overlapping CYD mono/mapping input roots')
    dep = Dependency(repo)
    manifest = dict(schema='cyd-mono-mapping-checkpoint-v1', repository=norm(repo), plan=plan, files={},
        aliases={}, roles={}, external_omitted={}, generated={}, verified=False,
        dependency_archive=dict(path='tests/results/cyd-vorbis-map2-20261020', manifest_sha256=MANIFEST_SHA,
            required=True, standalone=False, scope='exact-shared-entries-only-no-prior-campaign-replay'), intended_destination='tests/results/cyd-vorbis-mono-mapping-20261023',
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
        need(key not in manifest['external_omitted'] or all(manifest['external_omitted'][key][field] == value for field, value in row.items()),
             'Conflicting tool/archive identity')
        manifest['external_omitted'].setdefault(key, {}).update(row)

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
        need(sha((repo / rel(item['terminal'])).read_bytes()) == item['terminal_sha256'], 'Reviewed actual outer receipt identity differs')
        manifest['roles'][role] = dict(root=root.relative_to(repo).as_posix(), kind='numeric' if role.startswith('numeric') else 'host' if role == 'host21' else 'target',
            terminal=receipt(item['terminal']), expected_outer_exit=item['expected_outer_exit'])
        selected = [p for p in root.iterdir() if p.is_file()]
        for folder in ('sources', 'variant', 'observed-pcm', 'cases'):
            selected += [p for p in (root / folder).rglob('*') if p.is_file()]
        selected += [root / 'build' / path for path in CONTEXT if (root / 'build' / path).is_file()]
        selected += list((root / 'build').glob('*.map'))
        for field in ('build_outputs', 'variant_sources'):
            selected += [root / rel(path) for path in report.get(field, {})]
        for path in sorted(set(selected)):
            add(path, allow_borrow=False)  # Preserve actual target21/host21 snapshot copies locally, including matching dependency bytes.
        aliases = manifest['aliases'][role] = {}
        for original, row in report.get('inputs', {}).items():
            path = root / rel(row['snapshot']) if 'snapshot' in row else Path(row['path'])
            original_path = norm(original if 'snapshot' in row else row['path'])
            if path.resolve().is_relative_to(repo):
                key = add(path, row['sha256'], allow_borrow='snapshot' not in row)
                aliases[original_path] = key
            else:
                need(role.startswith('numeric') and 'snapshot' not in row and path.name in {'ffmpeg.exe', 'python.exe'},
                     'Only explicitly identified external numeric reference tools may be hash-only inputs')
                tool(path, row['sha256'])
                external = manifest['external_omitted'][norm(path.resolve())]
                need('bytes' not in row or external['raw_bytes'] == row['bytes'], 'External numeric input size differs')
                external['external_numeric_input'] = True
                manifest.setdefault('external_numeric_aliases', {}).setdefault(role, {})[original_path] = norm(path.resolve())
        for path, digest in report.get('tools', {}).items():
            tool(path, digest)

    for path in plan['extra_receipts']:
        need(sha((repo / rel(path)).read_bytes()) == plan['extra_receipt_pins'][path], 'Exact actual extra receipt identity')
        receipt(path)

    for path in plan['trees']:
        for source in sorted((repo / rel(path)).rglob('*')):
            if source.is_file():
                add(source, allow_borrow=False)
    for path in plan['extras']:
        add(repo / rel(path))
    checkpoint = repo / rel(plan['checkpoint']['path'])
    add(checkpoint, plan['checkpoint']['sha256'], stored='CHECKPOINT.md', allow_borrow=False)
    for name in sorted(readiness['files']):
        add(here / rel(name), stored=name, allow_borrow=False)
    add(here / 'readiness.json', expected=readiness_sha256, stored='readiness.json', allow_borrow=False)
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
    parser.add_argument('--readiness-sha256', required=True)
    args = parser.parse_args()
    pack(args.repository, args.output, args.plan, args.readiness_sha256)
