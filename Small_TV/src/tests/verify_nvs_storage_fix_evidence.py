"""Replay before/after Storage correction, overlay guards and independent network/LCD witnesses."""
import argparse
from copy import deepcopy
import json
from pathlib import Path

from check_nvs_storage_fix import check
from audit_factory_xrefs import sha
from nvs_storage_overlay_controls import run as overlay_controls
from verify_rv32_disassembly_evidence import payload
from verify_nothrow_fix_evidence import observed


def same(actual, expected):
    """Require actual recomputed results rather than trusting saved pass flags."""
    if actual != expected: raise ValueError('Storage fix evidence differs')


def verify(evidence, root, inputs, output):
    """Reexecute all CPU cases and private guard mutations without launching another VM."""
    proof = json.loads(evidence.read_bytes())
    if proof['schema'] != 'nvs-storage-fix-evidence-v1' or not proof['passed']:
        raise ValueError('Wrong Storage correction proof')
    for key in ('native_error_contract_passed', 'native_temporary_cleanup_passed', 'native_key_preservation_passed'):
        if proof[key] is not True: raise ValueError('Missing corrected Storage contract')
    for key in ('physical_hardware_tested', 'full_vm_power_fault_proved', 'whole_image_completeness_proved'):
        if proof[key] is not False: raise ValueError('Storage correction scope overstated')
    for name, digest in proof['source_pins'].items():
        path = (root/name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path.read_bytes()) != digest:
            raise ValueError('Storage correction source pin differs: '+name)
    files = {name: payload(evidence.parent, ref) for name, ref in proof['files'].items()}
    result = check(inputs, output)
    for name in proof['phases']:
        same(json.loads((output/(name+'.json')).read_bytes()), json.loads(files['phase:'+name]))
    assert (result['app_sha256'], result['native_elf_sha256']) == (proof['app_sha256'], proof['native_elf_sha256'])
    mutated = overlay_controls(inputs['native'].read_bytes(), inputs['app'].read_bytes(), inputs['nvs'].read_bytes(),
        inputs['old_app'].read_bytes(), inputs['old_nvs'].read_bytes(), inputs['component'], inputs['overlay'],
        json.loads(inputs['overlay_report'].read_bytes()), json.loads(inputs['commands'].read_bytes()), output/'overlay-controls')
    same(mutated, json.loads(files['overlay-controls']))
    network, display, owners = [json.loads(files[name]) for name in ('network', 'display', 'owners')]
    frames = {name: files['frame:'+name] for name in ('original', 'reconstructed')}
    observed(network, display, owners, frames)
    assert network['inputs_sha256'][str(inputs['native'].resolve())] == result['native_elf_sha256']
    assert display['app_sha256'] == result['app_sha256'] and display['native_elf_sha256'] == result['native_elf_sha256']
    for report in (network, display):
        assert all(sha(Path(path).read_bytes()) == digest for path, digest in report['inputs_sha256'].items())
    for name in ('native', 'privacy', 'nothrow', 'artifacts'): assert json.loads(files[name])['passed']
    assert json.loads(files['artifacts'])['app_sha256'] == result['app_sha256']
    # Check the complete production source manifest, including generated resources.
    project = root/'Small_TV/src'; resources = inputs['commands'].parent/'resources'
    manifest = json.loads((root/'firmware/development/small-tv-esp32c2-reconstructed/source-manifest.json').read_bytes())
    for row in manifest['files']:
        path = resources/row['file'][10:] if row['file'].startswith('generated/') else project/row['file']
        assert sha(path.read_bytes()) == row['sha256'], 'Production source/resource changed'
    rejected = []
    for fault in ('hidden-io-error', 'temporary-leak', 'missing-fault', 'stale-ntp', 'wrong-lcd'):
        if fault in ('stale-ntp', 'wrong-lcd'):
            net, screen = deepcopy(network), deepcopy(display)
            if fault == 'stale-ntp': net['phases'][2]['network']['ntp']['response_count'] = 0
            else: screen['cycles'][1]['display']['differing_rgb_bytes'] = 1
            try: observed(net, screen, owners, frames)
            except AssertionError: rejected.append(fault)
            else: raise AssertionError('Changed Storage runtime witness accepted')
        else:
            baseline = json.loads(files['phase:oom' if fault == 'temporary-leak' else 'phase:target'])
            changed = deepcopy(baseline)
            if fault == 'temporary-leak': changed['results']['native']['failures'][1]['leaked_temporary_bytes'] = 40
            elif fault == 'missing-fault': changed['faults']['native'].pop()
            else: changed['faults']['native'][0]['failed']['status'] = 0
            try: same(changed, baseline)
            except ValueError: rejected.append(fault)
            else: raise AssertionError('Changed Storage CPU result accepted')
    return dict(**result, native_checks=json.loads(files['native'])['checks'],
        privacy_checks=json.loads(files['privacy'])['assertions'], network_phases=3, exact_display_frames=2,
        overlay_mutations_rejected=len(mutated['rejected']), report_mutations_rejected=rejected)


def main():
    """Require a new diagnostic directory and explicit frozen before/current inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    for name in ('proof', 'old-root', 'factory', 'old-native', 'old-app', 'old-nvs', 'native', 'app', 'nvs', 'rom',
                 'component', 'overlay', 'overlay-report', 'commands', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    paths = vars(parser.parse_args()); evidence = paths.pop('evidence'); root = paths.pop('root'); output = paths.pop('output')
    print(json.dumps(verify(evidence, root, paths, output)))


if __name__ == '__main__': main()
