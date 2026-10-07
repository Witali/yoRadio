"""Freeze queue-wait measurements, configurations and exact tested sources."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from pipeline_flow import summarize


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--idf', type=Path, required=True, help='Pinned ESP-IDF 6.0.2 checkout')
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    def write(name, data):
        path = args.output/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def dump(name, value):
        write(name, (json.dumps(value, indent=2)+'\n').encode())

    def freeze(name, expected):
        data = (ROOT/name).read_bytes()
        if sha(data) != expected:
            raise ValueError('Tested source changed: '+name)
        write('sources/'+name, data)

    write('.gitattributes', b'* -text\n')
    for folder in ('board', 'board-off', 'ota', 'ota-off'):
        report = json.loads((args.work/folder/'report.json').read_text())
        if not report['cases'] or (folder.startswith('board') and
                not any(c['name'] == 'restore-board' for c in report['cases'])):
            raise ValueError('Incomplete run: '+folder)
        for name, digest in report['test_sources_sha256'].items():
            freeze(name, digest)
        for path in sorted((args.work/folder).glob('*.json')):
            write(folder+'/'+path.name, path.read_bytes())
        if folder.startswith('board'):
            dump(folder+'/summary.json', summarize(args.work/folder))

    for folder in ('host-profile', 'host-dma-profile', 'verify', 'verify-off'):
        for path in sorted((args.work/folder).rglob('*')):
            if path.is_file() and (path.suffix in ('.json', '.log', '.asm') or
                                   'sources' in path.relative_to(args.work/folder).parts):
                write(folder+'/'+path.relative_to(args.work/folder).as_posix(), path.read_bytes())

    for suffix in ('', '-off'):
        artifact = ROOT/'firmware/development'/('esp32c3-pipeline-profile'+suffix)
        build = json.loads((artifact/'manifest.json').read_text())
        for file, field in (('app.bin', 'app_sha256'), ('sdkconfig', 'sdkconfig_sha256')):
            if sha((artifact/file).read_bytes()) != build[field]:
                raise ValueError('Changed firmware artifact: '+str(artifact/file))
        for name, digest in build['source_sha256'].items():
            freeze(name, digest)
        for name in ('manifest.json', 'sdkconfig'):
            write('firmware'+suffix+'/'+name, (artifact/name).read_bytes())

    for name in ('tests/test-pipeline-flow.py', 'tests/test-pipeline-flow-evidence.py',
                 'tools/codec_benchmark/save_pipeline_flow_evidence.py'):
        freeze(name, sha((ROOT/name).read_bytes()))
    # Preserve the primary driver source used to interpret completion overruns.
    driver = args.idf/'components/esp_driver_i2s'
    for name in ('i2s_common.c', 'i2s_private.h'):
        write('esp-idf-6.0.2/'+name, (driver/name).read_bytes())
    dump('provenance.json', dict(production_qualified=False,
        source_commit='a738b43a',
        note='On/off images compiled before commit with identical runtime configuration except PIPELINE_PROFILE. '
             'No broadcast audio or credentials are retained here. Original failures are preserved.'))
    files = {p.relative_to(args.output).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
             for p in sorted(args.output.rglob('*')) if p.is_file()}
    dump('manifest.json', files)
    print('Saved', len(files), 'evidence files')


if __name__ == '__main__':
    main()
