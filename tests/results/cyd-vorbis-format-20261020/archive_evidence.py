"""One-off CYD format evidence copy; run only after root selects terminal campaigns."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

def digest(data): return hashlib.sha256(data).hexdigest()
def need(ok, message):
    if not ok: raise RuntimeError(message)
def load(path): return json.loads(path.read_text(encoding='utf-8-sig'))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--acceptance', type=Path, required=True)
    p.add_argument('--control', type=Path, required=True)
    args = p.parse_args()
    repo, out = args.repository.resolve(), args.output.resolve()
    roots = {name:repo/'.build'/('cyd-vorbis-format-'+suffix) for name,suffix in
             (('baseline01','baseline-01'),('diagnostic01','diagnostic-01'),('baseline02','baseline-02'),('reference','prep-01'))}
    roots.update(acceptance=args.acceptance.resolve(),control=args.control.resolve())
    need(out.is_relative_to(repo/'tests/results') and not out.exists(), 'Use a fresh tests/results bundle')
    need(all(path.is_relative_to(repo) and path.is_dir() and not out.is_relative_to(path) for path in roots.values()), 'Input roots must be separate existing repository directories')
    a,c = load(roots['acceptance']/'report.json'),load(roots['control']/'report.json')
    need(a.get('passed') is True and a.get('completed') is True and a.get('format_acceptance_qualified') is True, 'Acceptance is not terminal/qualified')
    need(c.get('completed') is True and c.get('control_effective') is True and c.get('control') == 'old-guard' and c.get('format_acceptance_qualified') is False, 'Control is incomplete or mislabeled')
    for name in ('baseline01','diagnostic01'):
        need(load(roots[name]/'qualification.json').get('state') == 'NONPASS', name+' must retain NONPASS')
    b = load(roots['baseline02']/'manual-qualification.json')
    need(b.get('regression_reproduced') is True and b.get('format_acceptance_qualified') is False, 'Manual baseline is not diagnostic-only')
    manifest = dict(schema=1, roots={k:v.relative_to(repo).as_posix() for k,v in roots.items()}, files={}, external_omitted={},
        note='Source/log/reference evidence only. Object/CMake intermediates unselected; generated target/library/tool/ROM binaries are metadata-only omissions. Run verify_archive.py before treating the bundle as verified.')
    out.mkdir(parents=True,exist_ok=False)
    binary = {'.elf','.bin','.a','.exe','.dll','.zip','.rom'}
    def add(path, stored, omitted=False):
        key = path.relative_to(repo).as_posix()
        if key in manifest['files']: return
        data = path.read_bytes()
        row = dict(raw_sha256=digest(data),raw_bytes=len(data),stored=None)
        if omitted or path.suffix.lower() in binary:
            row['omitted'] = 'Generated target/library binary; identity retained, bytes deliberately not copied'
        else:
            compressed = path.suffix == '.s16le' or (len(data)>65536 and path.suffix != '.ogg')
            if path.suffix == '.py' or path.name == 'fixture.h': compressed = False
            blob = gzip.compress(data,compresslevel=9,mtime=0) if compressed else data
            dest = out/(stored+('.gz' if compressed else ''))
            need(dest.resolve().is_relative_to(out) and not dest.exists(), 'Duplicate/unsafe stored path')
            dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(blob)
            row.update(stored=dest.relative_to(out).as_posix(),encoding='gzip' if compressed else 'raw',
                       stored_sha256=digest(blob),stored_bytes=len(blob))
        manifest['files'][key] = row
    def external(path, expected):
        original = str(path); path = Path(path); data = path.read_bytes()
        need(digest(data) == expected, 'External tool/archive identity changed: '+str(path))
        previous = manifest['external_omitted'].get(original)
        row = dict(raw_sha256=expected,raw_bytes=len(data),omitted='Tool/vendor archive/ROM binary; never copied')
        need(previous is None or previous == row, 'Conflicting historical external identity')
        manifest['external_omitted'][original] = row
    context = ('compile_commands.json','project_description.json','flasher_args.json','build.ninja',
               'config/sdkconfig.h','toolchain/cflags','specs/picolibc.specs')
    for name,root in roots.items():
        report = load(root/('reference/report.json' if name == 'reference' else 'report.json'))
        if name == 'reference':
            selected = [path for path in root.rglob('*') if path.is_file()]
        else:
            selected = [path for path in root.iterdir() if path.is_file()]
            for folder in ('sources','variant','macro-inputs'):
                selected += [path for path in (root/folder).rglob('*') if path.is_file()]
            selected += [root/'build'/rel for rel in context if (root/'build'/rel).is_file()]
            declarations = [report]+[load(root/f) for f in ('qualification.json','manual-qualification.json') if (root/f).is_file()]
            for record in declarations:
                for field in ('build_outputs','outputs_sha256'):
                    selected += [root/str(rel).replace('\\','/') for rel in record.get(field,{})
                                 if (root/str(rel).replace('\\','/')).is_file()]
            if (root/'build/project_description.json').is_file():
                desc = load(root/'build/project_description.json')
                selected += [root/'build'/desc[field] for field in ('app_elf','app_bin')]
            if (root/'build/flasher_args.json').is_file():
                selected += [root/'build'/rel for rel in load(root/'build/flasher_args.json')['flash_files'].values()]
        for path in sorted(set(selected)): add(path,name+'/'+path.relative_to(root).as_posix())
        for path,expected in report.get('tools',{}).items(): external(path,expected)
    extras = ['.build/cyd-vorbis-format-command-01.py',
              '.build/cyd-vorbis-format-source-promotion-02.json',
              '.build/cyd-vorbis-format-index-check-02.json',
              '.build/cyd-vorbis-format-host-canonical-02.json',
              '.build/cyd-vorbis-format-host-canonical-02.stdout.log','.build/cyd-vorbis-format-host-canonical-02.stderr.log',
              '.build/cyd-vorbis-format-root-reference-check-01.json',
              '.build/cyd-vorbis-format-root-combined-qualification-01.json',
              'tests/test-cyd-vorbis-format-runner.py','tests/run-cyd-vorbis-format-qemu.py','tests/windows_compile_command.py']
    for name in extras: add(repo/name,'receipts/'+Path(name).name)
    host = load(repo/'.build/cyd-vorbis-format-host-canonical-02.json'); external(host['argv'][0],host['executable_sha256'])
    for filename in ('archive_evidence.py','verify_archive.py','README.template.md'):
        source = Path(__file__).resolve().with_name(filename)
        add(source,'README.md' if filename == 'README.template.md' else filename)
    # Detect inputs changing while copied; no historical source/current repo rewrite.
    for name,row in manifest['files'].items(): need(digest((repo/name).read_bytes()) == row['raw_sha256'], 'Input changed during archive: '+name)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(archived=True,verified=False,files=len(manifest['files']),output=str(out))))

if __name__ == '__main__': main()
