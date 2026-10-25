"""Replay static and literal-instruction event-11 evidence from original inputs."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path

from timer_event11_test import run
from audit_factory_xrefs import sha


def compare(observed, expected):
    """Check recomputed contents, never an archived passed flag by itself."""
    if observed != expected:
        raise ValueError('Event-11 evidence differs from original-instruction replay')


def verify(proof_path, root, factory, native, old_library, new_library):
    """Hash bounded archive/source data, rerun the CPU matrix, then fault results."""
    proof = json.loads(proof_path.read_bytes())
    assert proof['schema'] == 'wifi-timer-event11-evidence-v1'
    assert proof['passed'] and not proof['semantic_equivalence_proved']
    assert not proof['whole_image_completeness_proved'] and not proof['physical_hardware_tested']
    pins = proof['source_pins']
    for name, digest in pins.items():
        source = (root / name).resolve()
        assert source.is_relative_to(root.resolve()) and sha(source.read_bytes()) == digest
    reference = proof['report']
    path = (proof_path.parent / reference['file']).resolve()
    assert path.is_relative_to(proof_path.parent.resolve())
    compressed = path.read_bytes()
    assert len(compressed) <= 131072 and sha(compressed) == reference['gzip_sha256']
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        raw = stream.read(2097153)
    assert len(raw) == reference['bytes'] <= 2097152 and sha(raw) == reference['sha256']
    saved = json.loads(raw)
    assert saved.pop('inputs_unchanged') is True
    saved_inputs = saved.pop('inputs_sha256')
    sources = {name: sha((root / name).read_bytes()) for name in pins}
    assert sources == pins
    expected_inputs = {
        **{str((Path(proof['producer_root']) / name).resolve()): digest
           for name, digest in pins.items() if name != 'Small_TV/src/tests/verify_timer_event11_evidence.py'},
        **{str(path.resolve()): sha(path.read_bytes()) for path in (factory, native, old_library, new_library)},
    }
    assert saved_inputs == expected_inputs
    actual = run(factory, native, old_library, new_library)
    compare(saved, actual)
    rejected = []
    for field in ('event-count', 'coverage', 'abi-version', 'observed-call', 'unjustified-equivalence'):
        changed = deepcopy(saved)
        if field == 'event-count':
            changed['instructions']['total_executions'] += 1
        elif field == 'coverage':
            changed['instructions']['coverage']['factory'][0]['visited'] -= 1
        elif field == 'abi-version':
            changed['qualification']['layouts']['factory']['osi_table']['version'] = 9
        elif field == 'observed-call':
            changed['instructions']['representative_differences']['different-rearm-formula']['observed']['factory']['calls'][1][1] += 1
        else:
            changed['semantic_equivalence_proved'] = True
        try:
            compare(changed, actual)
        except ValueError:
            rejected.append(field)
        else:
            raise AssertionError('Altered evidence accepted: ' + field)
    assert {name: sha((root / name).read_bytes()) for name in pins} == pins
    return dict(passed=True, qualified_bodies=8, instruction_executions=actual['instructions']['total_executions'],
                static_controls=len(actual['rejected_controls']), evidence_controls=rejected,
                semantic_equivalence_proved=False, whole_image_completeness_proved=False,
                physical_hardware_tested=False)


def main():
    """Read local inputs and private fixtures only; never launch or attach a VM."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--factory', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--old-library', type=Path, required=True)
    parser.add_argument('--new-library', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.factory, args.native, args.old_library, args.new_library)))


if __name__ == '__main__':
    main()
