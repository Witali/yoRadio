"""Retain a matched ordinary/copy RX experiment, including failed load gates."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import sha
from summarize_stream_memory import summarize
from ota_diagnostic import serial_health

COPY_KEYS = ('CONFIG_LWIP_L2_TO_L3_COPY', 'CONFIG_L2_TO_L3_COPY')


def validate_pair(configs, builds, summaries):
    base, copy = (set(configs[k].splitlines()) for k in ('baseline', 'candidate'))
    if copy-base != {k+'=y' for k in COPY_KEYS} or base-copy != {'# '+k+' is not set' for k in COPY_KEYS}:
        raise ValueError('Expected only native RX-copy configuration differences')
    if builds['baseline']['source_sha256'] != builds['candidate']['source_sha256']:
        raise ValueError('Firmware source inventories differ')
    before, after = (summaries[k] for k in ('baseline', 'candidate'))
    if before['fixture_hashes'] != after['fixture_hashes']:
        raise ValueError('Different stream bytes')
    if any(s['requested_seconds'] != 600 or s['observed_seconds'] < 600 for s in summaries.values()):
        raise ValueError('Both observations must cover ten minutes')
    if any(s['cpu_budget_percent'] is not None for s in summaries.values()):
        raise ValueError('CPU is informational for this experiment')
    for name, build in builds.items():
        if build['elf_sha256'] != summaries[name]['image']:
            raise ValueError('Measured image does not match artifact')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--baseline-artifact', type=Path, required=True)
    p.add_argument('--candidate-artifact', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    artifacts = dict(baseline=args.baseline_artifact, candidate=args.candidate_artifact)
    builds = {k: json.loads((v/'manifest.json').read_text()) for k,v in artifacts.items()}
    configs = {k: (v/'sdkconfig').read_text() for k,v in artifacts.items()}
    summaries = {k: summarize(args.work/k, independent_network=True) for k in artifacts}
    validate_pair(configs, builds, summaries)
    for name, folder in artifacts.items():
        for filename, field in (('app.bin','app_sha256'), ('sdkconfig','sdkconfig_sha256')):
            if sha((folder/filename).read_bytes()) != builds[name][field]:
                raise ValueError('Changed firmware artifact: '+name+'/'+filename)
    args.output.mkdir(parents=True, exist_ok=False)

    def save(name, data):
        path = args.output/name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != data:
            raise ValueError('Conflicting retained file: '+str(name))
        path.write_bytes(data)

    def dump(name, value):
        save(name, (json.dumps(value, indent=2)+'\n').encode())

    def source(name, digest=None):
        data = (ROOT/name).read_bytes()
        if digest and sha(data) != digest:
            data = (args.work/'runner-sources'/digest/Path(name).name).read_bytes()
        if digest and sha(data) != digest:
            raise ValueError('Measured source missing: '+name)
        save(Path('sources')/sha(data)/name, data)

    save('.gitattributes', b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
    for name in ('baseline','ota','candidate','restore'):
        report = json.loads((args.work/name/'report.json').read_text())
        if name in ('ota','restore') and (not report['cases'] or any(c['result'] != 'PASS' for c in report['cases'])):
            raise ValueError('OTA transition not successful: '+name)
        if name in ('ota','restore'):
            health = serial_health(json.loads((args.work/name/'performance.json').read_text()))
            if health['result'] != 'PASS':
                raise ValueError('OTA serial fault or missing capture: '+name)
            saved_health = args.work/name/'serial-health.json'
            if saved_health.exists():
                if json.loads(saved_health.read_text()) != health:
                    raise ValueError('Saved OTA health differs from replay: '+name)
            else:
                dump(Path(name)/'serial-health.json', health)
        for path in sorted((args.work/name).glob('*.json')):
            save(Path(name)/path.name, path.read_bytes())
        for path, digest in report['test_sources_sha256'].items():
            source(path, digest)
    for name, folder in artifacts.items():
        for filename in ('manifest.json','sdkconfig'):
            save(Path('firmware')/name/filename, (folder/filename).read_bytes())
        for path, digest in builds[name]['source_sha256'].items():
            source(path, digest)
    for folder in ('verify','sdk'):
        for path in sorted((args.work/folder).rglob('*')):
            if path.is_file(): save(path.relative_to(args.work), path.read_bytes())
    for path in ('tools/codec_benchmark/save_rx_comparison_evidence.py',
                 'tools/esp32c3_tests/summarize_stream_memory.py',
                 'tests/test-stream-memory-summary.py', 'tests/test-rx-comparison-evidence.py'):
        source(path)
    save('board-final.json', (args.work/'board-final.json').read_bytes())
    dump('summary.json', summaries)
    dump('provenance.json', dict(artifacts={k: v.as_posix() for k,v in artifacts.items()},
        production_qualified=False, acoustic_continuity_qualified=False,
        note='Same firmware sources, one native RX-copy flag and its alias. '
             'Sequential single-board trials; RF and host scheduling are not controlled. '
             'Original failed gates remain unchanged; CPU is informational.'))
    dump('manifest.json', {p.relative_to(args.output).as_posix(): dict(bytes=p.stat().st_size,
        sha256=sha(p.read_bytes())) for p in sorted(args.output.rglob('*')) if p.is_file()})
    print('Saved matched RX comparison')


if __name__ == '__main__':
    main()
