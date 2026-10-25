"""Replay archived TCP median attribution on fully qualified saved workloads."""
import argparse
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from runtime_evidence import decode, journal_evidence, require
from analyze_tcp_runtime import analysis_sources
from runtime_tcp_trend import attribute_trend
from runtime_tcp_snapshot import canonical
from verify_photo_format_matrix_evidence import source_hashes
from verify_tcp_inventory_evidence import verify as verify_inventory


def sha(raw):
    """Identify exact archive and decoded series bytes."""
    return hashlib.sha256(raw).hexdigest()


def archive_files(path, proof):
    """Read content-addressed blobs without following references outside parity storage."""
    blobs = {}
    for row in proof['blobs']:
        file = (path.parent / row['file']).resolve()
        require(file.is_relative_to(path.parent.resolve()), 'Evidence reference outside archive')
        packed = file.read_bytes()
        raw = gzip.decompress(packed)
        require(sha(packed) == row['gzip_sha256'] and sha(raw) == row['sha256'] and len(raw) == row['bytes']
                and row['sha256'] not in blobs, 'Changed or duplicate evidence payload')
        blobs[row['sha256']] = raw
    files = {row['source']: blobs[row['sha256']] for row in proof['raw']}
    require(len(files) == len(proof['raw']), 'Duplicate evidence label')
    return files


def validate_analysis(analysis, attribution, evidence, run, runtime, pins, producer_root):
    """Compare the real CLI result to independently reconstructed paired observations."""
    require(analysis['status'] == 'diagnostic_complete' and analysis['evidence_verified'] is True and
            analysis['h10_checks_evaluated'] is False and analysis['h10_checks_passed'] is False and
            analysis['all_functionality_verified'] is False and analysis['journal_prefix_only'] is False and
            analysis['analysis_inputs_unchanged'] is True, 'Wrong diagnostic scope')
    require(analysis['attribution'] == attribution, 'Original trend or additive components differ')
    require(analysis['complete_cycles_audited'] == run['cycles'] == evidence['cycles'] and
            analysis['journal_observed_sha256'] == evidence['sha256'] and analysis['pending_events'] == 0 and
            analysis['trailing_partial_bytes'] == 0, 'CLI journal coverage differs')
    require(analysis['terminal_workload_verified'] is True and analysis['terminal_guard_verified'] is True and
            analysis['start_record_verified'] is True and analysis['tcp_coverage'] == run['result']['tcp_coverage'] and
            analysis['elapsed_guest_seconds_observed'] == run['result']['elapsed_guest_seconds'], 'Incomplete workload coverage')
    for key in ('app_sha256', 'native_elf_sha256', 'qemu_sha256'):
        require(analysis[key] == runtime[key], 'CLI image identity differs')
    require(analysis['uart']['passed'] is True and analysis['uart']['rom_boots'] == 1, 'CLI boot capture differs')
    require(analysis['inputs_verified'] == len(runtime['inputs_sha256']), 'Runtime input coverage differs')
    source_root = Path(__file__).resolve().parents[3]
    expected_names = {Path(name).relative_to(source_root).as_posix() for name in analysis_sources()}
    prefix = producer_root.replace('\\', '/').rstrip('/') + '/'
    actual_names = set()
    for name, digest in analysis['analysis_inputs_sha256'].items():
        name = name.replace('\\', '/')
        require(name.startswith(prefix) and pins.get(name[len(prefix):]) == digest, 'Unbound analysis source')
        actual_names.add(name[len(prefix):])
    require(actual_names == expected_names, 'Missing or additional analysis identity')


def rejected_controls(analysis, *parameters):
    """Reject altered conclusions without repeatedly executing the same ROM replay."""
    rejected = []
    for case in ('h10-claim', 'false-verification', 'changed-original-trend', 'missing-cycle',
                 'changed-journal', 'changed-source', 'missing-source', 'fake-coverage'):
        row = copy.deepcopy(analysis)
        if case == 'h10-claim': row['h10_checks_passed'] = True
        elif case == 'false-verification': row['evidence_verified'] = False
        elif case == 'changed-original-trend': row['attribution']['original_trend']['status'] = 'no_decline_flagged_at_observed_resolution'
        elif case == 'missing-cycle': row['complete_cycles_audited'] -= 1
        elif case == 'changed-journal': row['journal_observed_sha256'] = '0' * 64
        elif case == 'changed-source': row['analysis_inputs_sha256'][next(iter(row['analysis_inputs_sha256']))] = '0' * 64
        elif case == 'missing-source': row['analysis_inputs_sha256'].pop(next(iter(row['analysis_inputs_sha256'])))
        else: row['tcp_coverage']['observed'] -= 1
        try:
            validate_analysis(row, *parameters)
        except (ValueError, KeyError, TypeError):
            rejected.append(case)
        else:
            raise AssertionError('Altered analysis accepted: ' + case)
    return rejected


def verify(path, root, rom, revision=None):
    """Verify prior full ROM/TCP replay, host tests and exact new CLI calculations."""
    proof = decode(path.read_bytes())
    require(proof['schema'] == 'tcp-trend-attribution-v1' and proof['passed'] is True and
            proof['h10_checks_passed'] is False and proof['all_functionality_verified'] is False and
            proof['physical_hardware_tested'] is False, 'Wrong trend proof scope')
    require(source_hashes(root, proof['source_pins'], revision) == proof['source_pins'], 'Attribution sources differ')
    base_path = (path.parent / proof['inventory_proof']['file']).resolve()
    require(base_path.is_relative_to(path.parent.resolve()) and
            sha(base_path.read_bytes()) == proof['inventory_proof']['sha256'], 'Inventory proof differs')
    # This performs full instruction replay and all 76 original controls before
    # a previously bound lean TCP series can be used in the mathematical layer.
    base_result = verify_inventory(base_path, root, rom, revision)
    base = decode(base_path.read_bytes())
    files, base_files = archive_files(path, proof), archive_files(base_path, base)
    for name, raw in files.items():
        if name.startswith('source/'):
            require(sha(raw) == proof['source_pins'].get(name[len('source/'):]), 'Archived analysis source differs')
    prefix = proof['producer_root'].replace('\\', '/').rstrip('/') + '/'
    for name, count in (('math', 22), ('cli', 8)):
        unit = decode(files['unit/' + name + '.json'])
        require(unit['passed'] is True and unit['tests'] == count and unit['inputs_unchanged'] is True and
                unit['no_vm_or_hardware_access'] is True and unit['h10_checks_passed'] is False and
                unit['all_functionality_verified'] is False and not unit['failures'] and not unit['errors'], 'Host tests failed')
        require(('Ran ' + str(count) + ' tests').encode() in files['unit/' + name + '.log'] and
                b'OK' in files['unit/' + name + '.log'], 'Host test transcript missing')
        for source, digest in unit['inputs_sha256'].items():
            source = source.replace('\\', '/')
            require(source.startswith(prefix) and proof['source_pins'].get(source[len(prefix):]) == digest, 'Unbound test source')
    results = []
    require({row['name'] for row in proof['runs']} == {'preflight', 'churn-40'} and len(proof['runs']) == 2, 'Missing or repeated run')
    for row in proof['runs']:
        name = row['name']
        run = next(item for item in base['runs'] if item['name'] == name)
        runtime = decode(base_files[name + '/report.json'])
        raw = base_files[name + '/events.jsonl']
        folder = root / '.build/tcp-trend-replay' / sha(raw)
        folder.mkdir(parents=True, exist_ok=True)
        journal = folder / 'events.jsonl'
        journal.write_bytes(raw)
        # Instruction validation already ran above; recover the exact free-heap
        # series through the original journal reader without a second ROM walk.
        evidence = journal_evidence(journal, base['photo_chunks'], runtime['outage_every_cycles'], require_weather=True)
        tcp = decode(files[name + '/tcp-series.json'])
        require(sha(canonical(tcp)) == run['tcp_series_sha256'], 'TCP series differs from qualified inventory')
        attribution = attribute_trend(evidence['series'], tcp, runtime['workload_start_guest_seconds'],
            runtime['workload_end_guest_seconds'], phase_period=math.lcm(20, runtime['outage_every_cycles'] or 1))
        analysis = decode(files[name + '/analysis.json'])
        parameters = (attribution, evidence, run, runtime, proof['source_pins'], proof['producer_root'])
        validate_analysis(analysis, *parameters)
        rejected = rejected_controls(analysis, *parameters)
        require(rejected == row['rejected_controls'], 'Rejection controls differ')
        results.append({'name': name, 'cycles': evidence['cycles'], 'snapshots': attribution['paired_snapshots'],
                        'trend_status': attribution['original_trend']['status'], 'rejected_controls': len(rejected)})
    return {'passed': True, 'runs': results, 'inventory_controls_replayed': base_result['unsafe_controls_rejected'],
            'host_tests': 30, 'h10_checks_passed': False, 'all_functionality_verified': False}


def main():
    """Read an immutable archive without contacting QMP, RSP or physical hardware."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--source-revision')
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.rom, args.source_revision)))


if __name__ == '__main__':
    main()
