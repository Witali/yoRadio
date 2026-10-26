"""Recompute factory NVS identity, full caller coverage and the real OOM correction."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha
from reverse.factory_nvs import FACTORY_OBJECT, native_object, qualify, source_correspondence
from factory_nvs_controls import controls
from factory_nvs_find import run as find_run
from factory_nvs_oom import run as oom_run
from factory_nvs_target import run as target_run
from verify_rv32_disassembly_evidence import payload


def same(actual, expected):
    """Require a complete recomputed result, including every boundary and negative claim."""
    if actual != expected: raise ValueError('Factory NVS evidence differs from replay')


def verify(proof_path, root, factory, native, app, archive, sdk, native_sdk):
    """Use current pinned bytes and explicit SDK sources, without a VM, board or network."""
    proof = json.loads(proof_path.read_bytes())
    if proof['schema'] != 'factory-nvs-evidence-v1' or not proof['passed']: raise ValueError('Wrong NVS proof')
    for name, digest in proof['source_pins'].items():
        path = (root/name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path.read_bytes()) != digest: raise ValueError('NVS source pin differs: '+name)
    files = {name: payload(proof_path.parent, ref) for name, ref in proof['files'].items()}
    original = factory.read_bytes(); current = native.read_bytes(); image = app.read_bytes()
    current_object = native_object(archive.read_bytes()); obj = files['object']
    qualification = qualify(original, obj, current, image, current_object)
    same(qualification, json.loads(files['qualification']))
    provenance = json.loads(files['provenance'])
    if not provenance['passed'] or provenance['sdk_revision'] != '735507283d5b2f9fb363a1901172dbd9e847945d' or \
            provenance['object_sha256'] != sha(obj) or sha(obj) != FACTORY_OBJECT or \
            provenance['layout_elf_sha256'] != sha(files['layout']) or provenance['config_sha256'] != sha(files['config']):
        raise ValueError('NVS fixture provenance differs')
    if any(provenance[key] is not False for key in ('factory_compiler_version_identified', 'factory_config_identified', 'production_firmware_built')):
        raise ValueError('Unproved factory build identity')
    if len(provenance['dependencies']) != 258 or sum(k.startswith('sdk/') for k in provenance['dependencies']) != 34:
        raise ValueError('Incomplete compiler/SDK dependency closure')
    package = json.loads(files['compiler_package'])
    tools_raw = (sdk/'tools/tools.json').read_bytes(); tools = json.loads(tools_raw)
    tool = next(t for t in tools['tools'] if t['name'] == 'riscv32-esp-elf')
    version = next(v for v in tool['versions'] if v['name'] == 'esp-14.2.0_20260121')
    if package['package'] != version['win64'] or package['tools_json_sha256'] != sha(tools_raw) or \
            package['package']['sha256'] != 'c2734714e59f684b74d1cb278f75b4ae9ec546aa1e55d73786ef039410e4a8f7' or \
            package['download_checked'] is not True or package['independent_builds'] != 2 or \
            package['identical_object_layout_and_provenance'] is not True:
        raise ValueError('Compiler package/reproduction provenance changed')
    old_cpp = (sdk/'components/nvs_flash/src/nvs_page.cpp').read_bytes()
    if sha(old_cpp) != provenance['dependencies']['sdk/components/nvs_flash/src/nvs_page.cpp']:
        raise ValueError('Factory SDK source changed')
    sources = source_correspondence(old_cpp, (native_sdk/'components/nvs_flash/src/nvs_page.cpp').read_bytes(),
                                    (native_sdk/'components/nvs_flash/src/nvs_page.hpp').read_bytes())
    same(sources, json.loads(files['sources']))
    target = target_run(original, current, image, qualification, files['layout']); same(target, json.loads(files['target']))
    find = find_run(original, qualification); same(find, json.loads(files['find']))
    legacy = json.loads(payload(proof_path.parent, proof['legacy_runtime']))
    wrappers = json.loads(payload(proof_path.parent, proof['current_wrappers']))
    oom = oom_run(original, current, image, qualification, legacy, wrappers); same(oom, json.loads(files['oom']))
    negative = controls(original, obj, current, image, current_object, qualification); same(negative, json.loads(files['controls']))
    rejected = []
    for fault in ('missed-caller-case', 'false-source-parity', 'false-allocator-execution', 'false-entry-table-execution', 'false-factory-oom-fix'):
        baseline = sources if fault == 'false-source-parity' else oom if fault == 'false-factory-oom-fix' else target
        changed = deepcopy(baseline)
        if fault == 'missed-caller-case': changed['results']['factory'].pop()
        elif fault == 'false-source-parity': changed['inherited_repair_policy_equivalence_proved'] = True
        elif fault == 'false-allocator-execution': changed['allocator_runtime_executed'] = True
        elif fault == 'false-entry-table-execution': changed['entry_table_algorithm_executed'] = True
        else: changed['factory_nothrow_contract_passed'] = True
        try: same(changed, baseline)
        except ValueError: rejected.append(fault)
        else: raise AssertionError('Forged NVS result accepted')
    if any(proof[key] is not False for key in ('whole_image_completeness_proved', 'physical_hardware_tested', 'full_vm_fault_injection_proved')):
        raise ValueError('Unproved NVS acceptance claim')
    if factory.read_bytes() != original or native.read_bytes() != current or app.read_bytes() != image:
        raise ValueError('NVS image changed during replay')
    return dict(passed=True, qualified_functions={k: len(v['functions']) for k, v in qualification['variants'].items()},
                caller_cases=target['total_cases'], caller_instructions={k: v['caller_instruction_starts'] for k, v in target['coverage'].items()},
                find_cases=find['cases'], find_instruction_starts=find['helper_instruction_starts'],
                actual_oom={k: v['outcome'] for k, v in oom['results'].items()},
                input_mutations_rejected=len(negative['rejected']), report_mutations_rejected=rejected,
                entry_table_algorithm_executed=False, inherited_repair_policy_equivalence_proved=False,
                recompilation_executed=False,
                whole_image_completeness_proved=False, physical_hardware_tested=False)


def main():
    """Require the current ELF/app/archive and explicit factory/current SDK directories."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    for name in ('proof', 'factory', 'native', 'app', 'nvs', 'sdk', 'native-sdk'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.factory, args.native, args.app, args.nvs, args.sdk, args.native_sdk)))


if __name__ == '__main__': main()
