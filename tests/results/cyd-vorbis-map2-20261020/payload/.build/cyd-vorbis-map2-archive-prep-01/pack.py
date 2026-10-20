"""One-off source/evidence packer. No SDK, compiler, codec, emulator or Git calls."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

CAMPAIGNS = {'vendor', 'baseline01', 'baseline02', 'capture17', 'capture25', 'packed', 'wide', 'single'}
NUMERIC = {'attempt01', 'attempt02', 'expanded25'}
CONTEXT = ('compile_commands.json', 'project_description.json', 'flasher_args.json',
           'build.ninja', 'CMakeCache.txt', 'config/sdkconfig.h', 'toolchain/cflags', 'specs/picolibc.specs')


def need(ok, message):
    if not ok: raise RuntimeError(message)


def sha(data): return hashlib.sha256(data).hexdigest()
def norm(value): return str(value).replace('\\', '/')
def load(path): return json.loads(path.read_bytes().decode('utf-8-sig'))


def pack(repo, out, plan_path):
    repo, out, plan_path = repo.resolve(), out.resolve(), plan_path.resolve()
    plan = load(plan_path)
    need(plan['schema'] == 1 and set(plan['campaigns']) == CAMPAIGNS and
         set(plan['numeric']) == NUMERIC and set(plan['hosts']) == {'old17', 'new8'}, 'Incomplete explicit role selection')
    need(out.is_relative_to(repo / '.build') and out != repo / '.build' and not out.exists(),
         'Stage only in a fresh .build directory; root promotes after verification')
    selections = list(plan['campaigns'].values()) + list(plan['numeric'].values()) + list(plan['hosts'].values()) + plan['history']
    roots = [(repo / item['path']).resolve() for item in selections] + [(repo / rel).resolve() for rel in plan['trees']]
    need(all(p.is_relative_to(repo) and p.is_dir() and not (out.is_relative_to(p) or p.is_relative_to(out))
             for p in roots), 'Missing, unsafe or overlapping input/output root')
    manifest = dict(schema='cyd-map2-checkpoint-v1', repository=norm(repo), plan=plan, files={},
                    aliases={}, roles={}, external_omitted={}, generated={},
                    intended_destination='tests/results/cyd-vorbis-map2-20261020',
                    verified=False, full_G6_qualified=False, physical_device=False, production_firmware=False)
    out.mkdir(parents=True, exist_ok=False)
    originals = {}

    def add(path, stored=None, expected=None, binary=False):
        path = path.resolve()
        need(path.is_relative_to(repo) and path.is_file(), 'Missing/outside repository input: ' + str(path))
        key = path.relative_to(repo).as_posix()
        data = path.read_bytes()
        need(expected is None or sha(data) == expected, 'Historical input differs: ' + key)
        if key in manifest['files']:
            need(manifest['files'][key]['raw_sha256'] == sha(data), 'Conflicting source identity')
            return key
        originals[key] = path
        row = dict(raw_bytes=len(data), raw_sha256=sha(data), stored=None)
        # Raw identification/setup/audio .bin fixtures are retained. Only target binaries are omitted.
        omitted = binary or path.suffix.lower() in {'.elf', '.a', '.exe', '.dll', '.rom', '.zip', '.o', '.obj'}
        omitted |= path.suffix.lower() == '.bin' and ('build' in path.relative_to(repo).parts or path.name == 'qemu-flash.bin')
        if omitted:
            row['omitted'] = 'Target/tool/package binary; actual bytes hashed, not copied'
            if path.suffix.lower() == '.elf':
                need(len(data) >= 64 and data[:4] == b'\x7fELF', 'Actual ELF header required')
                row['actual_elf_header64_hex'] = data[:64].hex()
        else:
            compressed = len(data) > 65536 and path.suffix.lower() not in {'.py', '.h', '.ogg'}
            compressed |= path.suffix.lower() in {'.wav', '.s16le', '.pcm'}
            blob = gzip.compress(data, compresslevel=9, mtime=0) if compressed else data
            dest = out / (stored or ('payload/' + key))
            if compressed: dest = dest.with_name(dest.name + '.gz')
            need(dest.resolve().is_relative_to(out) and not dest.exists(), 'Unsafe/duplicate stored file')
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as stream: stream.write(blob)
            row.update(stored=dest.relative_to(out).as_posix(), encoding='gzip' if compressed else 'raw',
                       stored_bytes=len(blob), stored_sha256=sha(blob))
        manifest['files'][key] = row
        return key

    def tool(path, expected):
        path = Path(path).resolve()
        data = path.read_bytes()
        need(sha(data) == expected, 'Installed historical tool/archive changed: ' + str(path))
        row = dict(raw_bytes=len(data), raw_sha256=expected, omitted='Tool/archive/ROM bytes not copied')
        key = norm(path)
        need(key not in manifest['external_omitted'] or manifest['external_omitted'][key] == row,
             'Conflicting historical tool identity')
        manifest['external_omitted'][key] = row

    def receipt(item):
        if isinstance(item, dict):
            need(item == dict(kind='direct_tool_observation', session_id=24179,
                             terminal_chunk_id='3b5497', exit_code=1), 'Only the authoritative baseline01 tool fact is supported')
            return item
        path = (repo / item).resolve()
        key = add(path)
        record = load(path)
        for name, row in record.get('logs', {}).items(): add(Path(name), expected=row['sha256'])
        if 'executable_sha256' in record: tool(record['argv'][0], record['executable_sha256'])
        return key

    def collect(role, item, kind):
        root = (repo / item['path']).resolve()
        manifest['roles'][role] = dict(root=root.relative_to(repo).as_posix(), kind=kind,
                                      terminal=receipt(item['terminal']))
        selected = [p for p in root.iterdir() if p.is_file()]
        for folder in ('sources', 'variant', 'observed-pcm') + (('cases',) if kind == 'host' else ()):
            selected += [p for p in (root / folder).rglob('*') if p.is_file()]
        selected += [root / 'build' / rel for rel in CONTEXT if (root / 'build' / rel).is_file()]
        selected += list((root / 'build').glob('*.map'))
        report = load(root / 'report.json')
        for field in ('build_outputs', 'variant_sources'):
            selected += [root / norm(rel) for rel in report.get(field, {})]
        desc = root / 'build/project_description.json'
        if desc.is_file():
            selected += [root / 'build' / load(desc)[key] for key in ('app_elf', 'app_bin')]
        recipe = root / 'build/flasher_args.json'
        if recipe.is_file(): selected += [root / 'build' / rel for rel in load(recipe)['flash_files'].values()]
        for path in sorted(set(selected)): add(path)
        aliases = manifest['aliases'][role] = {}
        for original, row in report.get('inputs', {}).items():
            if 'snapshot' in row:
                target = root / norm(row['snapshot'])
                key = add(target, expected=row['sha256'])
                aliases[norm(original)] = key
            else:
                path = Path(row['path']).resolve()
                key = add(path, expected=row['sha256'])
                aliases[norm(path)] = key
        for path, expected in report.get('tools', {}).items(): tool(path, expected)
        if item.get('qualification'): add(repo / item['qualification'])
        if item.get('witness'): add(repo / item['witness'])

    for name, item in plan['campaigns'].items(): collect(name, item, 'target')
    for name, item in plan['numeric'].items(): collect('numeric-' + name, item, 'numeric')
    for name, item in plan['hosts'].items(): collect('host-' + name, item, 'host')
    for index, item in enumerate(plan['history']): collect('history-' + str(index), item, 'history')
    for rel in plan['trees']:
        for path in sorted((repo / rel).rglob('*')):
            if path.is_file(): add(path)
    for rel in plan['extras']:
        add(repo / rel)
        if rel.endswith('.json') and 'argv' in load(repo / rel): receipt(rel)
    for name in ('pack.py', 'verify.py', 'README.md', 'plan.template.json', 'source_ast_check.py',
                 'source-ast.stdout.log', 'source-ast.stderr.log', 'source-ast-command.json', 'readiness.json'):
        add(Path(__file__).with_name(name), stored=name)
    add(plan_path, stored='selection.json')
    attributes = b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n'
    (out / '.gitattributes').write_bytes(attributes)
    manifest['generated']['.gitattributes'] = dict(bytes=len(attributes), sha256=sha(attributes))
    # Original paths/reports stay unchanged; historical canonical inputs are checked through snapshots.
    for key, path in originals.items():
        need(sha(path.read_bytes()) == manifest['files'][key]['raw_sha256'], 'Input changed while copying: ' + key)
    for path, row in manifest['external_omitted'].items():
        need(sha(Path(path).read_bytes()) == row['raw_sha256'], 'Tool/archive changed while copying')
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(packed=True, verified=False, files=len(manifest['files']), output=str(out))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    args = parser.parse_args()
    pack(args.repository, args.output, args.plan)
