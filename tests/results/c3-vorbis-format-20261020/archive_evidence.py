"""Collect root-selected terminal C3 raw8192 evidence; never starts a tool.

Collection does not qualify the resulting archive. Run its separate read-only
verifier after root review. Preserve a failed/partial output; never overwrite it.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys

SCHEMA = 'c3-public-raw8192-archive-v1'
SDK = '9a97f6c54ec638111ce55cd36581b3c192f15207'
BINARY = {'.elf', '.bin', '.a', '.o', '.obj', '.exe', '.dll', '.zip', '.rom', '.lib'}
COMMANDS = ('setup-macros', 'symbols', 'qemu-machine-help', 'merge', 'qemu')
ROOT_RECORDS = ('root-combined-qualification', 'source-promotion', 'test-promotion',
                'index-check', 'candidate-review', 'host-canonical', 'source-index-relation')


def need(ok, message):
    if not ok: raise RuntimeError(message)
def sha(data): return hashlib.sha256(data).hexdigest()
def load(path): return json.loads(Path(path).read_bytes())
def norm(value): return str(value).replace('\\', '/')
def raw_identity(data): return dict(raw_sha256=sha(data), raw_bytes=len(data))


def terminal(record):
    need(record.get('status') == 'TERMINAL' and type(record.get('returncode')) is int and
         record['returncode'] == 0 and record.get('timed_out', False) is False,
         'Require actual terminal0, without timeout')


def qualification(role, root):
    report = load(root/('baseline-qualification.json' if role == 'baseline' else 'qualification.json'))
    need(report.get('completed') is True and report.get('target_live') is False, 'Campaign is live/incomplete')
    if role == 'baseline':
        need(report['result'] == 'REGRESSION_REPRODUCED' and report['regression_reproduced'] is True and
             report['passed'] is False and report['format_acceptance_qualified'] is False,
             'Historical baseline regression must remain unqualified')
    else:
        control = role == 'control'
        need(report['result'] == ('CONTROL_EFFECTIVE' if control else 'FORMAT_ACCEPTED') and
             report['passed'] is (not control) and report['format_acceptance_qualified'] is (not control) and
             report['control_effective'] is control and report['scope'] == 'acceptance' and
             report['control'] == ('old-guard' if control else None), 'Acceptance/control semantics incomplete')
    need(set(report['commands']) == set(COMMANDS), 'Five actual command records required')
    for name in COMMANDS:
        row = report['commands'][name]
        need(norm(row['record']) == name+'.json' and row['returncode'] == 0, 'Wrong command report reference')
        path = root/(name+'.json')
        need(sha(path.read_bytes()) == row['sha256'], 'Command receipt changed')
        terminal(load(path))
    sdk = load(root/'sdk-build-result.json')
    need(sdk['status'] == 'TERMINAL_SUCCESS' and type(sdk['returncode']) is int and sdk['returncode'] == 0 and
         sdk['sdk_revision'] == SDK and sdk['sdk_tracked_clean'] is True, 'SDK build incomplete/wrong pin')
    return report


class Collector:
    def __init__(self, repository, output, roots, outer):
        self.repo, self.out = repository, output
        self.inputs = {}
        self.manifest = dict(schema=SCHEMA, repository_original=str(repository),
            roots={k:v.relative_to(repository).as_posix() for k,v in roots.items()},
            outer_sdk_records={k:v.relative_to(repository).as_posix() for k,v in outer.items()},
            files={}, external={}, elf_metadata={}, generated={}, historical_inputs=[],
            scope='public raw format only; no radio/Ogg/EOF/reset/OOM/resource/physical qualification')

    def add(self, path, stored=None, *, expected=None, size=None):
        path = Path(path).resolve()
        need(path.is_file() and not path.is_symlink(), 'Missing/nonregular evidence input: '+str(path))
        data = path.read_bytes()
        need(expected is None or sha(data) == expected, 'Pinned input bytes changed: '+str(path))
        need(size is None or len(data) == size, 'Pinned input size changed: '+str(path))
        local = path.is_relative_to(self.repo)
        key = path.relative_to(self.repo).as_posix() if local else norm(path)
        table = self.manifest['files' if local else 'external']
        if key in table:
            need(table[key]['raw_sha256'] == sha(data) and table[key]['raw_bytes'] == len(data), 'Conflicting input identity')
            return
        row = dict(raw_identity(data), stored=None)
        if path.suffix.lower() in BINARY:
            row['omitted'] = 'Binary identity only; bytes are not archived'
            if path.suffix.lower() == '.elf':
                need(data[:6] == b'\x7fELF\x01\x01' and len(data) >= 52 and struct.unpack_from('<H', data, 18)[0] == 243,
                     'Selected target ELF must be little-endian ELF32/RISC-V243')
                self.manifest['elf_metadata'][key] = dict(sha256=sha(data), bytes=len(data),
                    elf_class=1, byte_order=1, machine=243, header_hex=data[:52].hex())
        else:
            if stored is None:
                stored = ('receipts/'+key) if local else ('external/'+sha(key.encode())[:16]+'/'+path.name)
            compressed = len(data) > 65536 and path.suffix.lower() != '.py' and path.name != 'fixture.h'
            blob = gzip.compress(data, compresslevel=9, mtime=0) if compressed else data
            destination = self.out/(stored+('.gz' if compressed else ''))
            need(destination.resolve().is_relative_to(self.out) and not destination.exists(), 'Unsafe/duplicate stored destination')
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(blob)
            row.update(stored=destination.relative_to(self.out).as_posix(), encoding='gzip' if compressed else 'raw',
                       stored_sha256=sha(blob), stored_bytes=len(blob))
        table[key] = row
        self.inputs[str(path)] = raw_identity(data)

    def tree(self, root, stored):
        for path in sorted(root.rglob('*')):
            if path.is_file(): self.add(path, stored+'/'+path.relative_to(root).as_posix())

    def receipt(self, path):
        record = load(path)
        terminal(record)
        self.add(path)
        for log, row in record['logs'].items():
            self.add(log, expected=row['sha256'], size=row['bytes'])
        self.add(record['argv'][0], expected=record['executable_sha256'])

    def prep_pins(self, root):
        pins = load(root/'pins.json')
        rows = pins['files']
        if isinstance(rows, list):
            for row in rows: self.add(root/row['relative'], expected=row['sha256'], size=row['bytes'])
        else:
            for name,row in rows.items(): self.add(root/name, expected=row['sha256'], size=row['bytes'])
        for row in pins.get('external_inputs', []): self.add(row['path'], expected=row['sha256'], size=row['bytes'])
        for name,row in pins.get('origins', {}).items():
            self.add(self.repo/name, expected=row['sha256'])

    def finish(self):
        for name,row in self.inputs.items():
            need(raw_identity(Path(name).read_bytes()) == row, 'Input changed during collection: '+name)
        (self.out/'manifest.json').write_text(json.dumps(self.manifest, indent=2, sort_keys=True)+'\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'baseline', 'acceptance', 'control', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    for name in ('project-prep', 'candidate-prep', 'protocol-prep', 'tests-prep'):
        p.add_argument('--'+name, type=Path)
    for role in ('baseline', 'acceptance', 'control'): p.add_argument('--'+role+'-sdk-record', type=Path)
    p.add_argument('--extra', action='append', default=[], type=Path,
                   help='Additional final root qualification/selection receipts; no executable is launched')
    args = p.parse_args()
    repo, out = args.repository.resolve(), args.output.resolve()
    need(out == repo/'tests/results/c3-vorbis-format-20261020' and not out.exists(), 'Require fresh exact C3 archive destination')
    roots = {role:getattr(args, role).resolve() for role in ('baseline', 'acceptance', 'control')}
    for role,suffix in (('project_prep','project-prep-01'),('candidate_prep','candidate-prep-01'),
                        ('protocol','protocol-prep-01'),('tests_prep','tests-prep-01')):
        option = 'protocol_prep' if role == 'protocol' else role
        roots[role] = (getattr(args, option) or repo/'.build'/('c3-vorbis-format-'+suffix)).resolve()
    need(len(set(roots.values())) == len(roots) and all(path.is_relative_to(repo) and path.is_dir() and
         not out.is_relative_to(path) for path in roots.values()), 'Input roots must be distinct existing repository paths')
    # Read terminal semantics before any output mutation; do not run against a live campaign.
    reports = {role:qualification(role, roots[role]) for role in ('baseline', 'acceptance', 'control')}
    outer = {}
    for role in reports:
        path = (getattr(args, role+'_sdk_record') or repo/'.build'/(roots[role].name+'-command.json')).resolve()
        need(path.is_relative_to(repo), 'Outer SDK receipt must belong to this repository')
        terminal(load(path)); outer[role] = path
    root_records = {name:repo/'.build'/('c3-vorbis-format-'+name+'-01.json') for name in ROOT_RECORDS}
    need(all(path.is_file() for path in root_records.values()), 'Final root/source/host receipts required')
    combined = load(root_records['root-combined-qualification'])
    need(combined.get('completed') is True and combined.get('target_live') is False and
         combined.get('state') == 'NARROW_C3_RAW8192_FIX_QUALIFIED', 'Root combined qualification incomplete')
    terminal(load(root_records['host-canonical']))
    out.mkdir(parents=True, exist_ok=False)
    c = Collector(repo, out, roots, outer)
    attributes = b'* -text\n** -text\n'
    (out/'.gitattributes').write_bytes(attributes)
    c.manifest['generated']['.gitattributes'] = raw_identity(attributes)
    context = ('CMakeCache.txt','compile_commands.json','project_description.json','flasher_args.json','build.ninja',
               'config/sdkconfig.h','config/sdkconfig.json','toolchain/cflags','specs/picolibc.specs')
    for role in reports:
        root = roots[role]
        for path in sorted(root.iterdir()):
            if path.is_file(): c.add(path, role+'/'+path.name)
        for folder in ('sources', 'variant', 'macro-inputs'): c.tree(root/folder, role+'/'+folder)
        for rel in context: c.add(root/'build'/rel, role+'/build/'+rel)
        macro,post = load(root/'macro-context.json'),load(root/'postbuild-observations.json')
        for mapping in ('build_outputs','reviewed_sources','sdk_generated_sources'):
            for rel,digest in macro[mapping].items(): c.add(root/norm(rel), role+'/'+norm(rel), expected=digest)
        for original,row in macro['frozen_inputs'].items():
            c.add(original, expected=row['sha256'])
            c.add(root/norm(row['snapshot']), role+'/'+norm(row['snapshot']), expected=row['sha256'])
        for rel,digest in post['flash_inputs'].items(): c.add(root/norm(rel), role+'/'+norm(rel), expected=digest)
        for name in COMMANDS: c.receipt(root/(name+'.json'))
        c.receipt(outer[role])
        sdk = load(root/'sdk-build-result.json')
        for stream in ('stdout','stderr'): c.add(root/('sdk-build.'+stream+'.log'), expected=sdk[stream+'_sha256'])
    for role in ('project_prep', 'candidate_prep', 'protocol', 'tests_prep'):
        c.tree(roots[role], 'prep/'+role)
    for role in ('project_prep','candidate_prep','protocol'): c.prep_pins(roots[role])
    for row in load(roots['tests_prep']/'input-pins.json')['inputs']:
        c.add(repo/norm(row['path']), expected=row['sha256'], size=row['bytes'])
    relation = load(roots['project_prep']/'caller-relation.json')
    c.add(relation['canonical_source'], expected=relation['canonical_sha256'])
    promotion = load(root_records['source-promotion'])
    for row in relation['byte_equal_copies']:
        original = Path(row['original']).resolve()
        if original == repo/promotion['canonical_source']:
            # This historical pin described the original source, before its accepted promotion.
            # Archive its exact frozen old bytes under the real snapshot path, not the current path.
            snapshot = roots['project_prep']/norm(row['copy'])
            c.add(snapshot, expected=row['sha256'], size=row['bytes'])
            c.manifest['historical_inputs'].append(dict(original=norm(original),
                raw_sha256=row['sha256'], raw_bytes=row['bytes'],
                snapshot=snapshot.relative_to(repo).as_posix(),
                reason='Original caller-relation pin before accepted canonical source promotion'))
            c.add(original, expected=promotion['canonical_sha256'])
        else:
            c.add(original, expected=row['sha256'], size=row['bytes'])
    host = load(roots['protocol']/'host-tests.command.json')
    c.add(host['argv'][0], expected=host['python_sha256'])
    capture = repo/'.build/cyd-vorbis-format-command-01.py'
    c.add(capture)
    for path in sorted((repo/'.build').glob('c3-vorbis-format-*.py')): c.add(path)
    c.add(repo/'.build/c3-vorbis-format-derived-scripts-01.json')
    c.add(repo/'tests/windows_compile_command.py')
    for path in root_records.values(): c.add(path)
    index = load(root_records['source-index-relation'])
    c.add(repo/index['index_snapshot'], expected=index['canonical_index_sha256'])
    c.receipt(root_records['host-canonical'])
    for name,digest in load(root_records['test-promotion'])['files'].items(): c.add(repo/name, expected=digest)
    c.add(repo/'.gitattributes')
    for path in args.extra: c.add(path if path.is_absolute() else repo/path)
    here = Path(__file__).resolve().parent
    for filename in ('archive_evidence.py','verify_archive.py','PREP.md','README.template.md'):
        c.add(here/filename, 'README.md' if filename == 'README.template.md' else filename)
    c.finish()
    print(json.dumps(dict(collected=True, verified=False, output=str(out),
                         files=len(c.manifest['files']), external=len(c.manifest['external']))))


if __name__ == '__main__': main()
