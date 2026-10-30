"""Verify saved native vendor evidence without building, decoding or using QEMU."""
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/cyd-espressif-reuse-20261030'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def main():
    manifest = json.loads((FOLDER / 'native-manifest.json').read_bytes())
    archive_bytes = (FOLDER / manifest['archive']['path']).read_bytes()
    need(len(archive_bytes) == manifest['archive']['bytes'] and
         sha(archive_bytes) == manifest['archive']['sha256'], 'complete native archive identity')
    rows = manifest['files']
    need(len({r['path'] for r in rows}) == len(rows) == manifest['logical_files'], 'unique logical paths')
    blobs = {r['blob'] for r in rows}
    with zipfile.ZipFile(FOLDER / manifest['archive']['path']) as archive:
        need(len(archive.infolist()) == len(blobs) == manifest['physical_files'] and
             set(archive.namelist()) == blobs, 'exact physical archive members')
        physical = {name: archive.read(name) for name in blobs}
    files = {}
    for row in rows:
        body = physical[row['blob']]
        need(row['blob'] == 'blobs/' + sha(body) and sha(body) == row['sha256'] and
             len(body) == row['bytes'], 'every saved logical byte')
        files[row['path']] = body
    replay = json.loads(files['replay/verification.json'])
    need(replay['passed'] and replay['original_reports_preserved'], 'separate passing replay')
    reader_path = ROOT / 'tests/run-espressif-vorbis-qemu.py'
    reader_body = reader_path.read_bytes()
    need(reader_body == files['replay/reader.py'] and sha(reader_body) == replay['current_reader_sha256'],
         'reviewed current transcript reader; no artifact code execution')
    spec = importlib.util.spec_from_file_location('vendor_checkpoint_reader', reader_path)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    results = {}
    for target in ('esp32', 'esp32c3'):
        prefix = 'captures/espressif-vorbis-' + target + '-20261030-04/'
        report_bytes = files[prefix + 'report.json']
        report = json.loads(report_bytes)
        pinned = replay['targets'][target]
        need(not report['passed'] and not report['completed'] and
             report['failure'] == 'one-byte schedule really coalesced retained prefixes' and
             sha(report_bytes) == pinned['report_sha256'], 'unchanged original checker failure')
        need(report['target_executed'] and all(c['state'] == 'complete' and c['exit_status'] == 0
             for c in report['commands']), 'all actual SDK/QEMU commands terminal zero')
        original = files[prefix + 'sources/controller.py']
        need(original.count(b"row['pending_max'] > 1") == 1 and
             original.replace(b"row['pending_max'] > 1", b"row['pending_max'] > 0") == reader_body,
             'only the documented one-byte reader correction')
        for pin in report['inputs'].values():
            need(sha(files[prefix + pin['snapshot']]) == pin['sha256'], 'all frozen native inputs')
        for name, expected in report['build_outputs'].items():
            need(sha(files[prefix + name]) == expected, 'all saved native build outputs')
        for stream in ('stdout', 'stderr'):
            need(sha(files[prefix + 'qemu.' + stream + '.log']) == pinned['qemu_' + stream + '_sha256'],
                 'actual saved QEMU stream')
        log = (files[prefix + 'qemu.stdout.log'] + b'\n' + files[prefix + 'qemu.stderr.log']).decode('utf-8')
        measured = reader.validate_log(log, target)
        need(measured == pinned['measurements'] == manifest['measurements'][target],
             'every native result and resource record')
        results[target] = measured
    need(len({r['warmup']['sha256'] for r in results.values()}) == 1,
         'cross-architecture full PCM identity')
    print(json.dumps(dict(passed=True, targets=list(results), physical_files=len(blobs),
        logical_files=len(rows), pcm_bytes_per_stream=2112000, actual_native_runs_repeated=False,
        original_outer_reports_preserved_nonpass=True, full_pcm_independent_oracle=False)))


if __name__ == '__main__':
    main()
