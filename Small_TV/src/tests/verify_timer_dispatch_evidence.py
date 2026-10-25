"""Replay timer-table, literal-instruction and transient graph evidence offline."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_factory_xrefs import audit as audit_graph, sha
from reverse.xref_delta import apply, digest
from match_factory_timers import classify as match_timers
from timer_dispatch_test import verify as instruction_verify
from timer_recovery_contract import validate, rejected_controls
from verify_factory_sdk_evidence import unpack, verify as verify_sdk
from verify_photo_format_matrix_evidence import source_hashes


def verify(path, root, dependency_root, libraries, assembly, revision=None):
    """Rebuild the ancestor graph, selected bodies and all explicit host observations."""
    proof = json.loads(path.read_bytes())
    assert proof['schema'] == 'wifi-timer-dispatch-evidence-v1' and proof['passed'] is True
    assert proof['whole_image_completeness_proved'] is False and proof['semantic_equivalence_proved'] is False
    assert proof['physical_hardware_tested'] is False and proof['h10_checks_passed'] is False
    assert proof['production_bug_fixed'] is False
    assert source_hashes(root, proof['source_pins'], revision) == proof['source_pins']
    base_path = (path.parent / proof['base']['file']).resolve()
    assert base_path.is_relative_to(path.parent.resolve()) and sha(base_path.read_bytes()) == proof['base']['sha256']
    original = verify_sdk(base_path, root, dependency_root, libraries, assembly, revision)
    base = json.loads(base_path.read_bytes())
    old_files = unpack(base, path.parent)
    ancestor = json.loads(old_files['base/manifest.json'])
    ancestor_files = unpack(ancestor, path.parent)
    before = apply(json.loads(ancestor_files['ghidra.json']), json.loads(old_files['graph-delta.json']))
    files = unpack(proof, path.parent)
    for name, expected in proof['source_pins'].items():
        assert sha(files['producer/' + name]) == expected
    after = apply(before, json.loads(files['graph-delta.json']))
    dispatch, timers = json.loads(files['dispatch-audit.json']), json.loads(files['timer-matches.json'])
    factory = (dependency_root / '.build/small-tv-reverse/factory-analysis.elf').read_bytes()
    native = (root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()
    timer_source_pins = timers.pop('inputs_sha256')
    assert timers == match_timers(factory, libraries), 'Prior timer-body matches differ'
    prefix = proof['producer_root'].replace('\\', '/').rstrip('/') + '/'
    for name, expected in timer_source_pins.items():
        name = name.replace('\\', '/')
        assert name.startswith(prefix) and proof['source_pins'][name[len(prefix):]] == expected
    units = json.loads(files['instruction-tests.json'])
    assert units.pop('inputs_unchanged') is True
    for name, expected in units.pop('inputs_sha256').items():
        name = name.replace('\\', '/')
        assert name.startswith(prefix) and proof['source_pins'][name[len(prefix):]] == expected
    measured = instruction_verify(factory, native, libraries, dispatch)
    assert units == measured, 'Literal dispatcher observations differ'
    arguments = (json.loads(files['recovery.json']), timers, dispatch, before, after,
                 json.loads(files['project-copy-inputs.json']), json.loads(files['project-integrity.json']))
    recovery = validate(*arguments)
    assert recovery == proof['recovery_result']
    rejected = rejected_controls(*arguments)
    assert rejected == proof['rejected_recovery_controls']
    selected = {row['address'] for row in json.loads(ancestor_files['producer/Small_TV/src/symbol-map.json'])['functions']}
    graph = audit_graph(after, assembly.read_text(), factory, selected, expected_gaps=())
    assert digest(graph) == proof['graph_audit_sha256']
    assert graph['gp_coverage_agrees'] and graph['gp_memory_instructions'] == 396 and not graph['database_gp_gaps']
    assert graph['ghidra_functions'] == len(after['functions']) == 5161
    return {'passed': True, 'table_callbacks_per_image': 14, 'matched_bodies_per_image': 17,
            'instruction_cases': measured['factory']['cases'] + measured['native']['cases'],
            'recovery': recovery, 'ancestor_controls_replayed': original['rejected_controls'],
            'new_controls_rejected': len(measured['table_rejected_controls']) + len(rejected),
            'vendor_prefetch_defect_present': {name: measured[name]['vendor_table_prefetch_defect_present'] for name in ('factory','native')},
            'production_bug_fixed': False, 'whole_image_completeness_proved': False, 'h10_checks_passed': False}


def main():
    """Read only saved artifacts and private host instruction fixtures; never contact a VM."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--dependency-root', type=Path, default=Path('C:/Work/yoRadio'))
    parser.add_argument('--sdk-libraries', type=Path, required=True)
    parser.add_argument('--assembly', type=Path, required=True)
    parser.add_argument('--source-revision')
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.dependency_root, args.sdk_libraries, args.assembly, args.source_revision)))


if __name__ == '__main__':
    main()
