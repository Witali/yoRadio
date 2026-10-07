"""Retain a completed RX-copy sizing run and its original acceptance results."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import sha
from ota_diagnostic import serial_health
from rx_copy_profile import analyze, window
from summarize_stream_memory import summarize


def profile_summary(folder):
    result = analyze(json.loads((folder/'performance.json').read_bytes()))
    batches = json.loads((folder/'status.json').read_bytes())
    if any(b.get('in_progress') or b.get('interrupted') for b in batches):
        raise ValueError('Incomplete measurement window')
    result['windows'] = [dict(case=b['case'], **window(result['snapshots'], b['started_at'], b['ended_at']))
                         for b in batches if 'started_at' in b and 'ended_at' in b]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    playback = summarize(args.work/'study', independent_network=True)
    profile = profile_summary(args.work/'study')
    build = json.loads((args.artifact/'manifest.json').read_bytes())
    if playback['image'] != build['elf_sha256']:
        raise ValueError('Measured firmware differs from artifact')
    if playback['requested_seconds'] != 600 or playback['observed_seconds'] < 600:
        raise ValueError('Missing ten-minute observation')
    for name, field in (('app.bin', 'app_sha256'), ('sdkconfig', 'sdkconfig_sha256')):
        if sha((args.artifact/name).read_bytes()) != build[field]:
            raise ValueError('Firmware hash mismatch: '+name)
    args.output.mkdir(parents=True, exist_ok=False)

    def save(name, data):
        dest = args.output/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.read_bytes() != data:
            raise ValueError('Conflicting retained bytes: '+str(name))
        dest.write_bytes(data)

    def dump(name, value):
        save(name, (json.dumps(value, indent=2)+'\n').encode())

    def source(name, digest=None):
        data = (ROOT/name).read_bytes()
        if digest and sha(data) != digest:
            raise ValueError('Measured source changed: '+name)
        save(Path('sources')/name, data)

    save('.gitattributes', b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
    for phase in ('ota', 'study', 'restore'):
        report = json.loads((args.work/phase/'report.json').read_bytes())
        for path in sorted((args.work/phase).glob('*.json')):
            save(Path(phase)/path.name, path.read_bytes())
        for name, digest in report['test_sources_sha256'].items():
            source(name, digest)
        if phase != 'study':
            if not report['cases'] or any(c['result'] != 'PASS' for c in report['cases']):
                raise ValueError('OTA transition failed: '+phase)
            health = serial_health(json.loads((args.work/phase/'performance.json').read_bytes()))
            # Retain failed/incomplete serial capture as evidence. HTTP OTA
            # success must never turn this independent gate into PASS.
            saved = args.work/phase/'serial-health.json'
            if saved.exists():
                if json.loads(saved.read_bytes()) != health:
                    raise ValueError('OTA serial health replay differs: '+phase)
            else:
                dump(Path(phase)/'serial-health.json', health)
    for path in sorted((args.work/'verify').rglob('*')):
        if path.is_file():
            save(path.relative_to(args.work), path.read_bytes())
    for name, digest in build['source_sha256'].items():
        source(name, digest)
    for name in ('manifest.json', 'sdkconfig'):
        save(Path('firmware')/name, (args.artifact/name).read_bytes())
    for path in sorted((args.work/'host-final').rglob('*')):
        if path.is_file() and path.name != 'test': # Native executable is replaceable.
            save(Path('host')/path.relative_to(args.work/'host-final'), path.read_bytes())
    for name in ('tools/codec_benchmark/save_rx_copy_profile_evidence.py',
                 'tools/codec_benchmark/verify_vorbis_repair_build.py',
                 'tests/test-rx-copy-profile.py', 'tests/test-rx-copy-profile-evidence.py'):
        source(name)
    save('board-final.json', (args.work/'board-final.json').read_bytes())
    dump('summary.json', dict(profile=profile, playback=playback))
    dump('provenance.json', dict(artifact=args.artifact.as_posix(), diagnostic_only=True,
        production_qualified=False, acoustic_continuity_qualified=False,
        note='Allocation capacity excludes allocator headers. Peaks since boot; class peaks '
             'need not coincide. Added tracking RAM/timing; not a production CPU benchmark. '
             'Original failed gates, including independent OTA serial health, retained. '
             'Fixed packet pool not implemented.'))
    dump('manifest.json', {p.relative_to(args.output).as_posix(): dict(bytes=p.stat().st_size,
        sha256=sha(p.read_bytes())) for p in sorted(args.output.rglob('*')) if p.is_file()})
    print('Saved RX-copy sizing evidence')


if __name__ == '__main__':
    main()
