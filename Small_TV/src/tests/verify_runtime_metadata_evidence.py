"""Replay qualified factory runtime metadata and every compact-call graph edge without Ghidra."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_factory_xrefs import Image, sha
from reverse.runtime_call_gaps import OBJECTS, qualify
from reverse.runtime_metadata import verify as check
from reverse.xref_delta import apply
from runtime_metadata_controls import controls
from verify_rv32_disassembly_evidence import payload


def verify(proof_path, root, factory, native):
    """Recompute object matches and graph changes; never trust an archived passed flag alone."""
    proof = json.loads(proof_path.read_bytes())
    if proof['schema'] != 'runtime-metadata-evidence-v1' or not proof['passed']:
        raise ValueError('Wrong runtime metadata proof')
    for name, digest in proof['source_pins'].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path.read_bytes()) != digest:
            raise ValueError('Runtime metadata source pin differs: ' + name)
    files = {name: payload(proof_path.parent, ref) for name, ref in proof['files'].items()}
    original = factory.read_bytes(); current = native.read_bytes()
    parts = {name: payload(proof_path.parent, ref) for name, ref in proof['objects'].items()}
    if set(parts) != set(OBJECTS): raise ValueError('Incomplete runtime objects')
    qualification = qualify(original, current, parts)
    recorded = json.loads(payload(proof_path.parent, proof['qualification']))
    if recorded.pop('inputs_unchanged') is not True or recorded != qualification:
        raise ValueError('Object qualification changed')
    before = json.loads(payload(proof_path.parent, proof['graph_before']))
    after = apply(before, json.loads(files['graph_delta']))
    manifest = json.loads(files['manifest']); recovery = json.loads(files['recovery'])
    image = Image(original)
    measured = check(image, qualification, manifest, recovery, before, after)
    if measured != json.loads(files['validation']): raise ValueError('Recomputed metadata validation differs')
    mutated = controls(image, qualification, manifest, recovery, before, after)
    if mutated != json.loads(files['controls']): raise ValueError('Runtime metadata controls differ')
    integrity = json.loads(files['project_integrity'])
    if not (integrity['original_before'] == integrity['original_after'] ==
            integrity['copy_before'] == integrity['copy_after']) or len(integrity['original_before']) != 10:
        raise ValueError('Original/copied Ghidra project changed')
    if proof['headless_exit_code'] != 0 or proof['headless_read_only'] is not True:
        raise ValueError('Missing terminal read-only Ghidra completion')
    for key in ('whole_image_completeness_proved', 'semantic_equivalence_proved',
                'persistent_project_modified', 'physical_hardware_tested'):
        if proof[key] is not False: raise ValueError('Unproved metadata claim: ' + key)
    if factory.read_bytes() != original or native.read_bytes() != current:
        raise ValueError('Firmware input changed during verification')
    return dict(**measured, altered_inputs_rejected=len(mutated['rejected']),
                project_files_unchanged=10)


def main():
    """Require explicit unchanged factory/frozen-native images; no SDK, VM or board is modified."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    for name in ('proof', 'factory', 'native'): parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.factory, args.native)))


if __name__ == '__main__': main()
