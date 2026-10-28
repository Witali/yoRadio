"""Recompute the NVS correction evidence and independent network/LCD witnesses."""
import argparse
from copy import deepcopy
import json
from pathlib import Path

from check_nvs_recovery import check
from audit_factory_xrefs import sha
from verify_rv32_disassembly_evidence import payload
from verify_nothrow_fix_evidence import observed


def same(actual, expected):
    """Reject forged saved results using the same comparison as a normal replay."""
    if actual != expected:
        raise ValueError('Replayed NVS phase differs')


def verify(evidence, root, inputs, output):
    """Replay actual instructions, then compare every saved phase rather than success flags."""
    proof = json.loads(evidence.read_bytes())
    if proof['schema'] != 'nvs-recovery-evidence-v1' or not proof['passed']:
        raise ValueError('Wrong NVS correction evidence')
    for name in ('native_counter_contract_passed', 'native_key_contract_passed', 'native_io_error_contract_passed'):
        if proof[name] is not True:
            raise ValueError('Missing corrected NVS contract')
    for name in ('physical_hardware_tested', 'full_vm_power_fault_proved', 'whole_image_completeness_proved'):
        if proof[name] is not False:
            raise ValueError('NVS correction overstates its coverage')
    for name, digest in proof['source_pins'].items():
        path = (root/name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path.read_bytes()) != digest:
            raise ValueError('NVS correction source pin differs: '+name)
    files = {name: payload(evidence.parent, ref) for name, ref in proof['files'].items()}
    result = check(inputs, output)
    for name in proof['phases']:
        same(json.loads((output/(name+'.json')).read_bytes()), json.loads(files['phase:'+name]))
    if (result['app_sha256'], result['native_elf_sha256']) != (proof['app_sha256'], proof['native_elf_sha256']):
        raise ValueError('NVS firmware pair differs')
    network, display, owners = [json.loads(files[name]) for name in ('network', 'display', 'owners')]
    frames = {name: files['frame:'+name] for name in ('original', 'reconstructed')}
    observed(network, display, owners, frames)
    assert network['inputs_sha256'][str(inputs['native'].resolve())] == result['native_elf_sha256']
    assert display['app_sha256'] == result['app_sha256'] and display['native_elf_sha256'] == result['native_elf_sha256']
    for report in (network, display):
        assert all(sha(Path(path).read_bytes()) == digest for path, digest in report['inputs_sha256'].items())
    for name in ('native', 'privacy', 'nothrow', 'artifacts'):
        assert json.loads(files[name])['passed']
    assert json.loads(files['artifacts'])['app_sha256'] == result['app_sha256']
    rejected = []
    for fault in ('missing-fault-case', 'hidden-write-error', 'wrong-counter', 'lost-key', 'stale-ntp', 'wrong-lcd'):
        if fault in ('stale-ntp', 'wrong-lcd'):
            net, screen = deepcopy(network), deepcopy(display)
            if fault == 'stale-ntp':
                net['phases'][2]['network']['ntp']['response_count'] = 0
            else:
                screen['cycles'][1]['display']['differing_rgb_bytes'] = 1
            try:
                observed(net, screen, owners, frames)
            except AssertionError:
                rejected.append(fault)
            else:
                raise AssertionError('Altered NVS runtime witness accepted')
        else:
            original = json.loads(files['phase:faults' if 'fault' in fault or 'error' in fault else 'phase:target'])
            changed = deepcopy(original)
            if fault == 'missing-fault-case':
                changed['results'].pop()
            elif fault == 'hidden-write-error':
                row = next(r for r in changed['results'] if r['failed']['operations'][-1]['kind'] == 'write_raw')
                row['failed']['status'] = 0
            elif fault == 'wrong-counter':
                changed['results'][0]['loaded']['fields']['erased'] += 1
            else:
                row = next(r for r in changed['results'] if r['name'] == 'hash24-collision')
                row['loaded']['lookups'][0]['status'] = 0x1102
            try:
                same(changed, original)
            except ValueError:
                rejected.append(fault)
            else:
                raise AssertionError('Altered NVS phase accepted')
    return dict(passed=True, **{k: v for k, v in result.items() if k != 'passed'},
                native_checks=json.loads(files['native'])['checks'],
                privacy_checks=json.loads(files['privacy'])['assertions'], network_phases=3,
                exact_display_frames=2, report_mutations_rejected=rejected)


def main():
    """Write only fresh replay diagnostics; preserve production and historical input files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    for name in ('proof', 'factory', 'native', 'app', 'nvs', 'old-native', 'old-app', 'old-nvs',
                 'rom', 'source', 'generated', 'patch-report', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = vars(parser.parse_args()); evidence = args.pop('evidence'); root = args.pop('root'); output = args.pop('output')
    print(json.dumps(verify(evidence, root, args, output)))


if __name__ == '__main__':
    main()
