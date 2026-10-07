"""Retain the C3 output-priority experiment and its exact control identity."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from compare_output_priority import compare
from compare_output_priority_matrix import compare as compare_matrix


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--control', type=Path, required=True)
    p.add_argument('--artifact', type=Path, required=True)
    p.add_argument('--artifact-off', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    def write(name, data):
        path = args.output/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def freeze(name, digest=None):
        data = (ROOT/name).read_bytes()
        if digest and sha(data) != digest:
            raise ValueError('Changed measured source: '+name)
        write('sources/'+name, data)

    def dump(name, value):
        write(name, (json.dumps(value, indent=2)+'\n').encode())

    # Raw Windows logs/configs and upstream snapshots must retain their bytes.
    write('.gitattributes', b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
    for name in ('report.json', 'performance.json', 'status.json'):
        write('control/'+name, (args.control/name).read_bytes())
    for folder in ('board', 'ota', 'restore', 'matrix-control', 'matrix-candidate', 'ota-candidate'):
        report = json.loads((args.work/folder/'report.json').read_text())
        if not report['cases'] or folder in ('board', 'matrix-control', 'matrix-candidate') and not any(
                c['name'] == 'restore-board' for c in report['cases']):
            raise ValueError('Incomplete run: '+folder)
        for name, digest in report['test_sources_sha256'].items():
            freeze(name, digest)
        for path in sorted((args.work/folder).glob('*.json')):
            write(folder+'/'+path.name, path.read_bytes())
    interrupted = args.work/'matrix-control-interrupted'
    for path in sorted(interrupted.glob('*.json')):
        write('matrix-control-interrupted/'+path.name, path.read_bytes())
    old_report = json.loads((interrupted/'report.json').read_text())
    old_runner = interrupted/'output_priority_matrix.py'
    name = 'tools/esp32c3_tests/output_priority_matrix.py'
    if sha(old_runner.read_bytes()) != old_report['test_sources_sha256'][name]:
        raise ValueError('Changed interrupted runner')
    write('matrix-control-interrupted/sources/'+name, old_runner.read_bytes())
    dump('matrix-control-interrupted/termination.json', dict(completed=False,
        observed='2026-10-07', process_handle_missing=True, python_process_absent=True,
        note='Host test process disappeared before the last two load cases. Cause unknown. '
             'Seven completed load cases and their recovery checks retained; full matrix rerun.'))
    for folder in ('verify', 'verify-off'):
        for path in sorted((args.work/folder).rglob('*')):
            if path.is_file():
                write(folder+'/'+path.relative_to(args.work/folder).as_posix(), path.read_bytes())
    for artifact, folder in ((args.artifact, 'firmware'), (args.artifact_off, 'firmware-off')):
        build = json.loads((artifact/'manifest.json').read_text())
        for name, field in (('app.bin', 'app_sha256'), ('sdkconfig', 'sdkconfig_sha256')):
            if sha((artifact/name).read_bytes()) != build[field]:
                raise ValueError('Changed firmware artifact: '+str(artifact/name))
        for name in ('manifest.json', 'sdkconfig'):
            write(folder+'/'+name, (artifact/name).read_bytes())
        for name, digest in build['source_sha256'].items():
            freeze(name, digest)
    control_off = ROOT/'firmware/development/esp32c3-pipeline-profile-off'
    control_report = json.loads((args.work/'matrix-control/report.json').read_text())
    for name, field in (('app.bin', 'firmware_sha256'), ('sdkconfig', 'sdkconfig_sha256')):
        if sha((control_off/name).read_bytes()) != control_report[field]:
            raise ValueError('Changed profile-off control: '+name)
    for name in ('manifest.json', 'sdkconfig'):
        write('firmware-control-off/'+name, (control_off/name).read_bytes())
    for name in ('tools/esp32c3_tests/compare_output_priority.py',
                 'tools/esp32c3_tests/compare_output_priority_matrix.py',
                 'tools/esp32c3_tests/output_priority_matrix.py',
                 'tools/codec_benchmark/save_output_priority_evidence.py',
                 'tests/test-output-priority-matrix.py',
                 'tests/test-output-priority-evidence.py'):
        freeze(name)
    dump('comparison.json', compare(args.control, args.work/'board'))
    dump('matrix-comparison.json', compare_matrix(args.work/'matrix-control', args.work/'matrix-candidate'))
    write('fixtures/manifest.json', (args.work/'fixtures/manifest.json').read_bytes())
    dump('provenance.json', dict(control=str(args.control), artifact=str(args.artifact),
        artifact_off=str(args.artifact_off), production_qualified=False,
        note='A matched scheduling experiment with a seven-codec regression matrix. '
        'Original failures retained. Original firmware restored between phases; '
        'profile-off priority-8 candidate left installed after the second matrix. '
        'Short tests do not establish acoustic continuity or long-term qualification.'))
    files = {p.relative_to(args.output).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
             for p in sorted(args.output.rglob('*')) if p.is_file()}
    dump('manifest.json', files)
    print('Saved', len(files), 'evidence files')


if __name__ == '__main__':
    main()
