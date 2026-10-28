"""Replay factory/before defects and corrected C2 recovery without modifying a VM or flash image."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import Image, sha
from reverse.nothrow_linkage import LinkedRuntime
from reverse.nvs_record_linkage import qualify, archive_objects
from verify_nvs_recovery import verify as verify_linkage
from nvs_rom_crc import qualify as qualify_crc, vectors as crc_vectors
from nvs_header_vectors import run as header_run
from nvs_records_cpu import run as records_run
from nvs_records_controls import controls
from nvs_recovery_target import run as target_run
from nvs_recovery_faults import run as faults_run
from nvs_partial_repair import run as partial_run
from verify_rv32_disassembly_evidence import payload


def check(inputs, output):
    """Save each completed phase and require explicit failure of the old desired contracts."""
    output.mkdir(parents=True, exist_ok=False)
    def save(name, result):
        """Keep diagnostic witnesses even when a later strict phase fails."""
        (output/(name+'.json')).write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n')
        print(json.dumps(dict(phase=name, passed=result['passed'])), flush=True)
        return result
    before_proof = json.loads(inputs['proof'].read_bytes()); base = inputs['proof'].parent
    parts = {'nvs_page.cpp': payload(base, before_proof['page_object']),
             'nvs_types.cpp': payload(base, before_proof['files']['object:types']),
             'nvs_item_hash_list.cpp': payload(base, before_proof['files']['object:hash'])}
    raw = {name: path.read_bytes() for name, path in inputs.items() if name != 'proof'}
    if sha(raw['old_native']) != before_proof['native_elf_sha256'] or sha(raw['old_app']) != before_proof['app_sha256']:
        raise ValueError('Preserve the exact historical NVS before pair')
    native_parts = archive_objects(raw['nvs']); old_parts = archive_objects(raw['old_nvs'])
    linked = save('linked', verify_linkage(raw['native'], raw['app'], raw['nvs'], raw['source'],
                      raw['generated'], json.loads(raw['patch_report'])))
    current = save('closure', qualify(raw['factory'], parts, raw['native'], raw['app'], native_parts))
    old = save('before-closure', qualify(raw['factory'], parts, raw['old_native'], raw['old_app'], old_parts))
    crc = save('crc', qualify_crc(raw['rom'])); save('crc-vectors', crc_vectors(crc))
    save('headers', header_run(raw['factory'], raw['native'], raw['app'], current, crc))
    saved_records = save('records', records_run(raw['factory'], raw['native'], raw['app'], current, crc,
                                              native_fixes=('counts', 'key_identity')))
    assert saved_records['native_counter_contract_passed'] and saved_records['native_key_contract_passed']
    reader = LinkedRuntime(raw['native'], raw['app']).read
    target = save('target', target_run(current['variants']['native'], reader, crc))
    old_reader = LinkedRuntime(raw['old_native'], raw['old_app']).read
    before = save('faults-before', faults_run('native', old['variants']['native'], old_reader, crc))
    assert not before['error_contract_passed'] and before['hidden_errors']
    factory_faults = save('faults-factory', faults_run('factory', old['variants']['factory'], Image(raw['factory']).read, crc))
    assert not factory_faults['error_contract_passed']
    faults = save('faults', faults_run('native', current['variants']['native'], reader, crc,
                                      require_errors=True, require_retention=True))
    partial = save('partial', partial_run(raw['factory'], raw['native'], raw['app'], current))
    negative = save('controls', controls(raw['factory'], parts, raw['native'], raw['app'], native_parts, current, crc))
    rejected = []
    def reject(name, operation):
        """Exercise the real production source/linkage guard with mismatched inputs."""
        try:
            operation()
        except (ValueError, AssertionError):
            rejected.append(name)
        else:
            raise AssertionError('Altered NVS build input accepted: '+name)
    patch_report = json.loads(raw['patch_report'])
    reject('wrong-sdk-source', lambda: verify_linkage(raw['native'], raw['app'], raw['nvs'],
            raw['source']+b'\n', raw['generated'], patch_report))
    reject('wrong-generated-copy', lambda: verify_linkage(raw['native'], raw['app'], raw['nvs'],
            raw['source'], raw['generated']+b'\n', patch_report))
    changed = deepcopy(patch_report); changed['fixes'] = []
    reject('missing-fix-identity', lambda: verify_linkage(raw['native'], raw['app'], raw['nvs'],
            raw['source'], raw['generated'], changed))
    reject('old-source-archive', lambda: verify_linkage(raw['native'], raw['app'], raw['old_nvs'],
            raw['source'], raw['generated'], patch_report))
    reject('wrong-elf-app-pair', lambda: verify_linkage(raw['native'], raw['old_app'], raw['nvs'],
            raw['source'], raw['generated'], patch_report))
    result = dict(passed=True, app_sha256=linked['app_sha256'], native_elf_sha256=linked['elf_sha256'],
                  record_cases=target['record_cases'], stable_reopens=target['reopen_cases'],
                  full_freeing_cases=target['full_freeing_cases'], fault_cases=faults['cases'],
                  before_hidden_errors=len(before['hidden_errors']), factory_hidden_errors=len(factory_faults['hidden_errors']),
                  partial_cases=partial['successful_cases']+partial['reopened_cases']+partial['baseline_cases']+
                                partial['fault_cases']+partial['recovery_cases'],
                  source_link_rejections=rejected, input_mutations_rejected=len(negative['rejected']),
                  physical_hardware_tested=False, full_vm_power_fault_proved=False)
    if any(path.read_bytes() != raw[name] for name, path in inputs.items() if name != 'proof'):
        raise ValueError('NVS recovery input changed during replay')
    save('result', result)
    return result


def main():
    """Require matching production artifacts and preserved historical inputs explicitly."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('proof', 'factory', 'native', 'app', 'nvs', 'old-native', 'old-app', 'old-nvs',
                 'rom', 'source', 'generated', 'patch-report', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = vars(parser.parse_args()); output = args.pop('output')
    print(json.dumps(check(args, output)))


if __name__ == '__main__':
    main()
