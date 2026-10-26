"""Replay actual partial-record repair, physical program prefixes and recovery counters."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha
from reverse.factory_nvs import native_object, qualify as nvs_qualify
from reverse.nvs_repair_linkage import qualify
from nvs_partial_repair import run
from nvs_partition_fixture import Partition
from nvs_repair_controls import controls
from verify_rv32_disassembly_evidence import payload


def same(actual, expected):
    """Reject any altered operation, physical digest, Page field or acceptance claim."""
    if actual != expected: raise ValueError('Partial NVS repair evidence differs')


def verify(proof_path, root, factory, native, app, archive):
    """Use only pinned source objects and private synthetic sectors; no live flash or VM."""
    proof = json.loads(proof_path.read_bytes())
    if proof['schema'] != 'nvs-partial-repair-evidence-v1' or not proof['passed']: raise ValueError('Wrong repair proof')
    for name, digest in proof['source_pins'].items():
        path = (root/name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path.read_bytes()) != digest: raise ValueError('Repair source differs: '+name)
    files = {name: payload(proof_path.parent, ref) for name, ref in proof['files'].items()}
    obj = payload(proof_path.parent, proof['factory_object'])
    original = factory.read_bytes(); current = native.read_bytes(); image = app.read_bytes()
    current_obj = native_object(archive.read_bytes())
    nvs = nvs_qualify(original, obj, current, image, current_obj)
    same(nvs, json.loads(payload(proof_path.parent, proof['base_qualification'])))
    linkage = qualify(original, obj, current, image, current_obj, nvs); same(linkage, json.loads(files['linkage']))
    target = run(original, current, image, linkage); same(target, json.loads(files['target']))
    negative = controls(original, obj, current, image, current_obj, nvs, linkage); same(negative, json.loads(files['controls']))
    rejected = []
    for fault in ('no-extra-program', 'missing-reopen', 'rollback-media', 'silent-purge-failure',
                  'guaranteed-retry-purge', 'whole-table-claim', 'full-vm-power-claim'):
        changed = deepcopy(target)
        if fault == 'no-extra-program': changed['native_extra_program_bytes_per_repaired_slot'] = 0
        elif fault == 'missing-reopen': changed['results']['native'][0].pop('reopened')
        elif fault == 'rollback-media':
            row = next(r for r in changed['faults']['native'] if r['partial'] and
                       r['failed']['operations'][-1]['kind'] == 'write_raw' and r['failed']['operations'][-1]['bytes'] == 4)
            initial = Partition([0]*row['slot']+[3]*(126-row['slot']), {row['slot']})
            row['failed']['physical_sha256'] = sha(initial.initial)
        elif fault == 'silent-purge-failure':
            row = next(r for r in changed['faults']['native'] if r['failed']['operations'][-1]['kind'] == 'write_raw' and
                       r['failed']['operations'][-1]['bytes'] == 32)
            row['failed']['result'] = 0
        elif fault == 'guaranteed-retry-purge':
            row = next(r for r in changed['faults']['native'] if r['retained_nonzero_payload_bytes_after_retry'])
            row['retained_nonzero_payload_bytes_after_retry'] = 0
        elif fault == 'whole-table-claim': changed['whole_entry_table_algorithm_proved'] = True
        else: changed['full_vm_power_fault_proved'] = True
        try: same(changed, target)
        except ValueError: rejected.append(fault)
        else: raise AssertionError('Forged repair claim accepted')
    if factory.read_bytes() != original or native.read_bytes() != current or app.read_bytes() != image:
        raise ValueError('Firmware changed during repair replay')
    for key in ('whole_entry_table_algorithm_proved', 'physical_hardware_tested', 'full_vm_power_fault_proved'):
        if proof[key] is not False: raise ValueError('Unproved repair claim')
    retained = [r['retained_nonzero_payload_bytes_after_retry'] for r in target['faults']['native']
                if r['retained_nonzero_payload_bytes_after_retry']]
    count = sum(target[k] for k in ('successful_cases', 'reopened_cases', 'baseline_cases', 'fault_cases', 'recovery_cases'))
    return dict(passed=True, cpu_cases=count, helpers={k: len(v['functions']) for k, v in linkage['variants'].items()},
                extra_program_bytes_per_repair=32, erase_operations=0, repeated_open_programs=0,
                fault_cases=target['fault_cases'], actual_recoveries=target['recovery_cases'],
                retry_payload_remnants=dict(cases=len(retained), minimum=min(retained), maximum=max(retained)),
                input_mutations_rejected=len(negative['rejected']), report_mutations_rejected=rejected,
                whole_entry_table_algorithm_proved=False, full_vm_power_fault_proved=False, physical_hardware_tested=False)


def main():
    """Require explicit original/current firmware paths and reuse archived source objects."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    for name in ('proof', 'factory', 'native', 'app', 'nvs'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.factory, args.native, args.app, args.nvs)))


if __name__ == '__main__': main()
