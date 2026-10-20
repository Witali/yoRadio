"""Copy five completed uint32-rate checkpoints; no tool/verifier execution."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct

NAMES = ('baseline', 'acceptance', 'limited', 'validity-control', 'policy-control')
MODES = ('baseline', 'acceptance', 'limited', 'acceptance', 'limited')
CONTROLS = (None, None, None, 'signed-validity', 'signed-policy')
BINARY = {'.elf', '.bin', '.a', '.o', '.obj', '.exe', '.dll', '.rom', '.lib', '.zip', '.pyc'}
TEXT_BUILD = ('compile_commands.json', 'project_description.json', 'CMakeCache.txt',
              'build.ninja', 'flasher_args.json', 'flash_args', 'sdkconfig',
              'c3_vorbis_uint32_rate.map', 'CMakeFiles/rules.ninja',
              'esp-idf/main/cmake_install.cmake', 'ldgen_libraries', 'ldgen_libraries.in')


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def norm(path):
    return str(path).replace('\\', '/')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'output', *NAMES):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in NAMES:
        parser.add_argument('--' + name + '-terminal', type=Path, required=True)
    args = parser.parse_args()
    repo, out = args.repository.resolve(), args.output.resolve()
    roots = {name: getattr(args, name.replace('-', '_')).resolve() for name in NAMES}
    scratch = out.is_relative_to(repo / '.build') and out != repo / '.build'
    durable = out == repo / 'tests/results/c3-vorbis-uint32-rate-20261020'
    protected = (*roots.values(), Path(__file__).resolve().parent,
                 *(repo / '.build' / name for name in ('c3-vorbis-uint32-rate-source-01',
                    'c3-vorbis-uint32-rate-sdk-prep-01',
                    'cyd-vorbis-public-header-audit-01')))
    need(not out.exists() and (scratch or durable) and all(not out.is_relative_to(p) and not p.is_relative_to(out)
         for p in protected), 'Fresh independent .build staging or exact tests/results destination required')
    need(all(p.is_dir() and p.is_relative_to(repo / '.build') for p in roots.values()), 'Repository campaign directories required')
    reports = {}
    terminals = {}
    for name, mode, control in zip(NAMES, MODES, CONTROLS):
        path = roots[name] / 'report.json'
        report = json.loads(path.read_bytes())
        need(report.get('completed') is True and report.get('passed') is True and
             report.get('mode') == mode and report.get('control') == control, 'Live/nonpassing/wrong role: ' + name)
        terminal_path = getattr(args, name.replace('-', '_') + '_terminal').resolve()
        terminal = json.loads(terminal_path.read_bytes())
        need(terminal.get('schema') == 'direct-exec-tool-terminal-v1' and terminal.get('status') == 'TERMINAL' and
             type(terminal.get('exit_code')) is int and terminal['exit_code'] == 0 and
             terminal.get('report_sha256') == sha(path.read_bytes()), 'Unbound terminal receipt: ' + name)
        need(len(report.get('commands', [])) == 9 and all(c.get('state') == 'complete' and
             type(c.get('exit_status')) is int and c['exit_status'] == 0 and
             c.get('timed_out') is False and c.get('interrupted') is False for c in report['commands']),
             'Incomplete owned command: ' + name)
        reports[name] = report
        terminals[name] = terminal_path
    out.mkdir(parents=True, exist_ok=False)
    manifest = dict(schema='c3-public-uint32-rate-archive-v1', files={}, omitted={}, campaigns={},
        scope='Isolated C3 public raw uint32-rate checkpoint; baseline reproduction, acceptance, limited policy and two controls',
        full_G6_qualified=False, production_radio_integration=False, physical_device=False,
        omitted_bytes_replayable=False, object_cache_included=False)
    originals = {}

    def add(path, key, expected=None, binary=False):
        path = Path(path)
        need(path.is_file() and not path.is_symlink(), 'Missing/symlink evidence: ' + str(path))
        data = path.read_bytes()
        digest = sha(data)
        need(expected is None or expected == digest, 'Pinned evidence changed: ' + str(path))
        if key in originals:
            need(originals[key][1] == digest, 'Conflicting repeated role identity: ' + key)
            return
        need(key not in manifest['files'] and key not in manifest['omitted'], 'Duplicate archive key')
        originals[key] = (path, digest)
        row = dict(origin=norm(path.resolve()), sha256=digest, bytes=len(data))
        if binary or path.suffix.lower() in BINARY:
            need(path.suffix.lower() not in ('.o', '.obj', '.pyc'), 'Object/cache inputs are excluded entirely')
            row['reason'] = 'Identity only; binary bytes omitted; not replayable from this archive'
            if path.suffix.lower() == '.elf':
                need(len(data) >= 64 and data[:4] == b'\x7fELF' and data[4:6] == b'\x01\x01', 'Expected ELF32 little-endian')
                row['elf_header_hex'] = data[:64].hex()
                row['elf_machine'] = struct.unpack_from('<H', data, 18)[0]
            manifest['omitted'][key] = row
            return
        compressed = len(data) >= 16384 and path.suffix.lower() not in ('.py', '.h', '.c', '.ps1', '.cmake')
        stored = key + ('.gz' if compressed else '')
        encoded = gzip.compress(data, compresslevel=9, mtime=0) if compressed else data
        target = out / stored
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(encoded)
        row.update(stored=stored, encoding='gzip' if compressed else 'raw',
                   stored_bytes=len(encoded), stored_sha256=sha(encoded))
        manifest['files'][key] = row

    for name in NAMES:
        root, report = roots[name], reports[name]
        prefix = 'campaigns/' + name + '/'
        manifest['campaigns'][name] = dict(origin=norm(root), report=prefix + 'report.json',
            terminal=prefix + 'direct-tool-terminal.json', inputs=report['inputs'])
        for path in sorted(root.iterdir()):
            if path.is_file():
                add(path, prefix + path.name, report.get('build_outputs', {}).get(path.name))
        add(terminals[name], prefix + 'direct-tool-terminal.json')
        for folder in ('sources', 'variant'):
            for path in sorted((root / folder).rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts:
                    add(path, prefix + path.relative_to(root).as_posix())
        for original, row in report['inputs'].items():
            # Input snapshots are campaign-scoped. Never reopen an obsolete original canonical path.
            add(root / row['snapshot'], prefix + norm(row['snapshot']), row['sha256'])
        for rel, digest in report['variant_sources'].items():
            add(root / rel, prefix + norm(rel), digest)
        for rel, digest in report['build_outputs'].items():
            add(root / rel, prefix + norm(rel), digest)
        for rel in TEXT_BUILD:
            path = root / 'build' / rel
            if path.is_file():
                add(path, prefix + 'build/' + rel)
        for folder in ('config', 'toolchain', 'specs', 'log'):
            for path in sorted((root / 'build' / folder).rglob('*')):
                if path.is_file():
                    add(path, prefix + path.relative_to(root).as_posix())
        for path in sorted((root / 'build').rglob('*.a')):
            add(path, prefix + path.relative_to(root).as_posix(), binary=True)
        for i, (origin, digest) in enumerate(report['tools'].items()):
            add(Path(origin), prefix + 'omitted-tools/' + str(i) + '-' + Path(origin).name, digest, binary=True)

    extras = {
        'source-change': repo / '.build/c3-vorbis-uint32-rate-source-01',
        'header-audit': repo / '.build/cyd-vorbis-public-header-audit-01',
        'sdk-prep': repo / '.build/c3-vorbis-uint32-rate-sdk-prep-01'}
    for name, root in extras.items():
        need(root.is_dir(), 'Missing supporting evidence: ' + name)
        for path in sorted(root.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                add(path, 'extras/' + name + '/' + path.relative_to(root).as_posix())
    canonical = json.loads((extras['source-change'] / 'canonical-host-tests.command.json').read_bytes())
    add(repo / '.build/cyd-vorbis-format-command-01.py', 'extras/capture.py', canonical['runner_sha256'])
    for name in ('rate_protocol.py', 'test_rate_protocol.py'):
        add(repo / 'tests/c3_vorbis_rate' / name, 'extras/canonical-tests/' + name,
            sha((extras['sdk-prep'] / name).read_bytes()))
    host = json.loads((extras['sdk-prep'] / 'host-tests.command.json').read_bytes())
    manifest['supporting_host_inputs'] = {}
    canonical_fixture = repo / 'tests/target/c3_vorbis_format_qemu/main/fixture.h'
    for row in host['inputs_before']:
        path = Path(row['path']).resolve()
        if path.is_relative_to(extras['sdk-prep']):
            key = 'extras/sdk-prep/' + path.relative_to(extras['sdk-prep']).as_posix()
        else:
            need(path == canonical_fixture.resolve(), 'Unexpected external host-test source')
            key = 'extras/canonical-fixture.h'
        add(path, key, row['sha256'])
        manifest['supporting_host_inputs'][row['path']] = key
    for path in sorted(Path(__file__).resolve().parent.iterdir()):
        if path.is_file():
            add(path, path.name)
    attributes = out / '.gitattributes'
    attributes.write_bytes(b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n** -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n')
    manifest['files']['.gitattributes'] = dict(origin='archive generated attributes', sha256=sha(attributes.read_bytes()),
        bytes=attributes.stat().st_size, stored='.gitattributes', encoding='raw',
        stored_bytes=attributes.stat().st_size, stored_sha256=sha(attributes.read_bytes()))
    for path, digest in originals.values():
        need(sha(path.read_bytes()) == digest, 'Source changed during archive assembly: ' + str(path))
    with (out / 'manifest.json').open('xb') as stream:
        stream.write((json.dumps(manifest, indent=2) + '\n').encode())
    print(json.dumps(dict(result='COPIED_NOT_VERIFIED', output=str(out), files=len(manifest['files']),
                         omitted=len(manifest['omitted']), full_G6_qualified=False)))


if __name__ == '__main__':
    main()
