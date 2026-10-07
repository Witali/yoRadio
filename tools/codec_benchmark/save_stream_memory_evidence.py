"""Retain a completed C3 stream-memory run, its interruption and OTA restore."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import sha
from summarize_stream_memory import summarize


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--artifact', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = summarize(args.work/'board-10min')
    args.output.mkdir(parents=True, exist_ok=False)

    def write(name, data):
        path = args.output/name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != data:
            raise ValueError('Conflicting source snapshots: '+name)
        path.write_bytes(data)

    def dump(name, data):
        write(name, (json.dumps(data, indent=2)+'\n').encode())

    def freeze(name, digest=None):
        data = (ROOT/name).read_bytes()
        if digest and sha(data) != digest:
            raise ValueError('Changed measured source: '+name)
        write('sources/'+name, data)

    write('.gitattributes', b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
    for folder in ('ota', 'board', 'board-10min', 'restore'):
        report = json.loads((args.work/folder/'report.json').read_text())
        if folder in ('ota', 'restore') and (not report['cases'] or any(
                c['result'] != 'PASS' for c in report['cases'])):
            raise ValueError('OTA installation/restore did not pass: '+folder)
        for path in sorted((args.work/folder).glob('*.json')):
            write(folder+'/'+path.name, path.read_bytes())
        # Source inventory is broad; freeze every recorded entry, including
        # helper parsers, at its recorded hash rather than guessing imports.
        for name, digest in report['test_sources_sha256'].items():
            freeze(name, digest)
    initial = json.loads((args.work/'board/checkpoint.json').read_text())
    if initial.get('complete'):
        raise ValueError('Expected the retained user-shortened preliminary run')
    dump('board/termination.json', dict(complete=False,
        reason='User requested ten minutes instead of thirty. Host session interrupted; '
               'a fresh 600-second run performs full Stop recovery and settings checks.',
        last_checkpoint_elapsed_seconds=initial.get('elapsed_seconds')))
    for path in sorted((args.work/'verify').rglob('*')):
        if path.is_file():
            write('verify/'+path.relative_to(args.work/'verify').as_posix(), path.read_bytes())
    build = json.loads((args.artifact/'manifest.json').read_text())
    for name, field in (('app.bin', 'app_sha256'), ('sdkconfig', 'sdkconfig_sha256')):
        if sha((args.artifact/name).read_bytes()) != build[field]:
            raise ValueError('Changed diagnostic firmware: '+name)
    if build['elf_sha256'] != result['image']:
        raise ValueError('Wrong measured ELF image')
    for name in ('manifest.json', 'sdkconfig'):
        write('firmware/'+name, (args.artifact/name).read_bytes())
    for name, digest in build['source_sha256'].items():
        freeze(name, digest)
    for name in ('tools/esp32c3_tests/summarize_stream_memory.py',
                 'tools/codec_benchmark/save_stream_memory_evidence.py',
                 'tests/test-stream-memory-summary.py', 'tests/test-stream-memory-study.py',
                 'tests/test-stream-memory-evidence.py'):
        freeze(name)
    write('board-final.json', (args.work/'board-final.json').read_bytes())
    dump('summary.json', result)
    dump('provenance.json', dict(diagnostic_artifact=args.artifact.as_posix(),
        restore_artifact='firmware/development/esp32c3-output-first',
        production_qualified=False, requested_seconds=600,
        note='Physical RX-owner diagnostic; CPU is informational. Original failures and '
             'incomplete preliminary capture retained. No physical audio capture.'))
    manifest = {p.relative_to(args.output).as_posix(): dict(bytes=p.stat().st_size,
                 sha256=sha(p.read_bytes())) for p in sorted(args.output.rglob('*')) if p.is_file()}
    dump('manifest.json', manifest)
    print('Saved', len(manifest), 'evidence files')


if __name__ == '__main__':
    main()
