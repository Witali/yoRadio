"""Replay full Storage init/read and preserve the still-failing higher-level I/O contract."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import Image, sha
from compile_factory_nvs_fixture import SDK_REVISION
from reverse.nvs_storage_linkage import qualify, archive_objects, PARTS
from reverse.nvs_storage_layout import layout
from reverse.nothrow_linkage import LinkedRuntime
from nvs_rom_crc import qualify as qualify_crc
from nvs_storage_controls import controls
from nvs_storage_target import run
from nvs_storage_geometry import run as geometry_run
from nvs_storage_oom import run as oom_run
from verify_rv32_disassembly_evidence import payload


def same(actual, expected):
    """Reject changed evidence even when its aggregate pass field is unchanged."""
    if actual != expected: raise ValueError('Storage before-evidence differs')


def verify(proof_path, root, factory, native, app, archive, rom):
    """Recompute all algorithms from immutable inputs without starting or resetting a VM."""
    proof = json.loads(proof_path.read_bytes())
    if proof['schema'] != 'nvs-storage-before-evidence-v1' or not proof['passed']:
        raise ValueError('Wrong Storage before proof')
    if proof['native_error_contract_passed'] is not False or proof['native_key_preservation_passed'] is not True:
        raise ValueError('Storage before failure hidden')
    if proof['native_temporary_cleanup_passed'] is not False: raise ValueError('Storage allocation leak hidden')
    for name in ('physical_hardware_tested', 'full_vm_power_fault_proved', 'whole_image_completeness_proved'):
        if proof[name] is not False: raise ValueError('Storage before scope overstated')
    for name, digest in proof['source_pins'].items():
        path = (root/name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path.read_bytes()) != digest:
            raise ValueError('Storage source pin differs: '+name)
    files = {name: payload(proof_path.parent, ref) for name, ref in proof['files'].items()}
    parts = {name: payload(proof_path.parent, ref) for name, ref in proof['factory_parts'].items()}
    provenance = json.loads(files['provenance'])
    if provenance['sdk_revision'] != SDK_REVISION or provenance['parent_object_sha256'] != PARTS['nvs_page.cpp'] or \
            provenance['factory_compiler_version_identified'] or provenance['production_firmware_built']:
        raise ValueError('Storage compilation provenance differs')
    for name in ('nvs_pagemanager.cpp', 'nvs_storage.cpp'):
        if provenance['sources'][name]['object_sha256'] != sha(parts[name]):
            raise ValueError('Storage source object provenance differs')
    if provenance['config_sha256'] != sha(payload(proof_path.parent, proof['config'])):
        raise ValueError('Storage analysis configuration differs')
    original, current, image, library, rom_raw = [p.read_bytes() for p in (factory, native, app, archive, rom)]
    if (sha(current), sha(image)) != (proof['native_elf_sha256'], proof['app_sha256']):
        raise ValueError('Preserve the exact Storage before pair')
    current_parts = archive_objects(library)
    qualified = qualify(original, parts, current, image, current_parts); same(qualified, json.loads(files['closure']))
    private = {'factory': layout(files['carrier']), 'native': layout(current)}
    same(private, json.loads(files['layout']))
    crc = qualify_crc(rom_raw); same(crc, json.loads(payload(proof_path.parent, proof['crc'])))
    readers = {'factory': Image(original).read, 'native': LinkedRuntime(current, image).read}
    target = run(qualified['variants'], readers, crc); same(target, json.loads(files['target']))
    geometry = geometry_run(qualified['variants'], readers, crc); same(geometry, json.loads(files['geometry']))
    oom = oom_run(qualified['variants'], readers, crc); same(oom, json.loads(files['oom']))
    if oom['native_temporary_cleanup_passed'] is not False: raise ValueError('Storage temporary leak changed')
    negative = controls(original, parts, current, image, current_parts, qualified, files['carrier'])
    same(negative, json.loads(files['controls']))
    if target['native_error_contract_passed'] is not False or not target['native_key_preservation_passed']:
        raise ValueError('Wrong Storage desired contract disposition')
    for variant, expected in (('factory', (224, 130)), ('native', (236, 134))):
        rows = target['faults'][variant]
        if (len(rows), sum(not r['error_surfaced'] for r in rows)) != expected:
            raise ValueError('Storage failure matrix changed')
        assert all(r['key_preservation_passed'] for r in rows)
    rejected = []
    for fault in ('missing-fault', 'masked-write-error', 'counterfeit-native-pass', 'factory-blob-loss-hidden', 'media-rollback', 'temporary-leak-hidden'):
        baseline = oom if fault == 'temporary-leak-hidden' else target
        changed = deepcopy(baseline)
        if fault == 'missing-fault': changed['faults']['native'].pop()
        elif fault == 'counterfeit-native-pass': changed['native_error_contract_passed'] = True
        elif fault == 'factory-blob-loss-hidden':
            row = next(r for r in changed['baselines']['factory'] if r['name'] == 'unpublished-blob-same-page')
            row['loaded']['lookups'][0]['status'] = 0
        elif fault == 'media-rollback':
            row = next(r for r in changed['faults']['native'] if r['partial'] and
                       any(op['failed'] and op['kind'] in ('write_raw', 'write', 'erase') for op in r['failed']['operations']))
            from nvs_storage_vectors import cases
            untouched = next(case for case in cases() if case['name'] == row['name'])
            before_sha = sha(b''.join(untouched['sectors']))
            assert row['failed']['media_sha256'] != before_sha
            row['failed']['media_sha256'] = before_sha
        elif fault == 'temporary-leak-hidden':
            changed['results']['native']['failures'][1]['leaked_temporary_bytes'] = 0
        else:
            row = next(r for r in changed['faults']['native'] if not r['error_surfaced'] and
                       any(op['failed'] and op['kind'] in ('write_raw', 'write') for op in r['failed']['operations']))
            row['failed']['status'] = 0x104; row['error_surfaced'] = True
        try: same(changed, baseline)
        except ValueError: rejected.append(fault)
        else: raise AssertionError('Altered Storage result accepted')
    if any(p.read_bytes() != data for p, data in zip((factory, native, app, archive, rom), (original, current, image, library, rom_raw))):
        raise ValueError('Storage input changed during replay')
    return dict(passed=True, functions={k: len(v['functions']) for k, v in qualified['variants'].items()},
                baseline_cases=18, stable_reopens=18, fault_cases=460, fault_recoveries=460,
                six_sector_geometry_cases=geometry['cases'],
                temporary_allocation_failure_cases=oom['cases'], native_temporary_cleanup_passed=False,
                factory_hidden_errors=130, native_hidden_errors=134, native_error_contract_passed=False,
                native_key_preservation_passed=True, input_mutations_rejected=len(negative['rejected']),
                report_mutations_rejected=rejected, whole_image_completeness_proved=False,
                physical_hardware_tested=False, full_vm_power_fault_proved=False)


def main():
    """Require exact production and factory/ROM inputs, not a previous JSON success claim."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    for name in ('proof', 'factory', 'native', 'app', 'nvs', 'rom'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.factory, args.native, args.app, args.nvs, args.rom)))


if __name__ == '__main__': main()
