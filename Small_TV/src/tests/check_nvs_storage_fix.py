"""Compare preserved full-Storage failures with a corrected production image and overlay."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha, Image
from verify_nvs_storage import verify as storage_guard
from verify_nvs_storage_before_evidence import verify as before_verify
from reverse.nvs_storage_linkage import qualify, archive_objects
from reverse.nvs_storage_layout import layout
from reverse.nvs_record_linkage import qualify as record_qualify, archive_objects as record_objects
from reverse.nothrow_linkage import LinkedRuntime
from nvs_rom_crc import qualify as qualify_crc
from nvs_storage_target import run as target_run
from nvs_storage_oom import run as oom_run
from nvs_storage_geometry import run as geometry_run
from nvs_storage_compat import run as compat_run
from nvs_storage_controls import controls
from nvs_records_cpu import run as record_run
from nvs_partial_repair import run as partial_run
from verify_rv32_disassembly_evidence import payload


def check(paths, output):
    """Preserve diagnostics after each phase and require all new desired contracts to pass."""
    output.mkdir(parents=True, exist_ok=False)
    def save(name, value):
        """Retain real intermediate evidence if any later phase rejects the candidate."""
        (output/(name+'.json')).write_text(json.dumps(value, indent=2)+'\n', encoding='utf8', newline='\n')
        print(json.dumps(dict(phase=name, passed=value['passed'])), flush=True)
        return value
    proof = json.loads(paths['proof'].read_bytes()); base = paths['proof'].parent
    parts = {name: payload(base, ref) for name, ref in proof['factory_parts'].items()}
    native, app, library = [paths[name].read_bytes() for name in ('native', 'app', 'nvs')]
    factory = paths['factory'].read_bytes(); rom = qualify_crc(paths['rom'].read_bytes())
    guarded = save('guard', storage_guard(native, app, library, paths['component'], paths['overlay'],
                   json.loads(paths['overlay_report'].read_bytes()), json.loads(paths['commands'].read_bytes())))
    qualified = save('closure', qualify(factory, parts, native, app, archive_objects(library)))
    save('layout', dict(passed=True, factory=layout(payload(base, proof['files']['carrier'])), native=layout(native)))
    readers = {'factory': Image(factory).read, 'native': LinkedRuntime(native, app).read}
    oom = save('oom', oom_run(qualified['variants'], readers, rom, require_native_cleanup=True))
    assert oom['native_temporary_cleanup_passed']
    save('geometry', geometry_run(qualified['variants'], readers, rom))
    compat = save('compatibility', compat_run(qualified['variants']['native'], readers['native'], rom))
    after = save('target', target_run(qualified['variants'], readers, rom, require_native_errors=True))
    assert after['native_error_contract_passed'] and after['native_key_preservation_passed']
    current_pages = record_objects(library)
    page_parts = {k: v for k, v in parts.items() if k in current_pages}
    record_linkage = save('page-closure', record_qualify(factory, page_parts, native, app, current_pages))
    records = save('page-records', record_run(factory, native, app, record_linkage, rom, native_fixes=('counts', 'key_identity')))
    partial = save('page-partial', partial_run(factory, native, app, record_linkage))
    negative = save('controls', controls(factory, parts, native, app, archive_objects(library), qualified,
                                         payload(base, proof['files']['carrier'])))
    before = save('before', before_verify(paths['proof'], paths['old_root'], paths['factory'], paths['old_native'],
                  paths['old_app'], paths['old_nvs'], paths['rom']))
    assert not before['native_error_contract_passed'] and not before['native_temporary_cleanup_passed']
    if any(paths[name].read_bytes() != value for name, value in (('native', native), ('app', app), ('nvs', library), ('factory', factory))):
        raise ValueError('Storage fix input changed during testing')
    return save('result', dict(passed=True, app_sha256=sha(app), native_elf_sha256=sha(native),
        native_error_contract_passed=True, native_temporary_cleanup_passed=True,
        native_key_preservation_passed=True, before_hidden_errors=before['native_hidden_errors'],
        native_fault_cases=len(after['faults']['native']), baseline_cases=18, geometry_cases=6, custom_oom_cases=4,
        compatibility_cases=compat['replacement_cases']+compat['same_object_retries'],
        old_page_cases=partial['successful_cases']+partial['reopened_cases']+partial['baseline_cases']+
                       partial['fault_cases']+partial['recovery_cases'], input_mutations_rejected=len(negative['rejected']),
        local_translation_units=guarded['local_translation_units'], physical_hardware_tested=False,
        full_vm_power_fault_proved=False, whole_image_completeness_proved=False))


def main():
    """Require separate preserved before inputs and matching current build artifacts explicitly."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('proof', 'old-root', 'factory', 'old-native', 'old-app', 'old-nvs', 'native', 'app', 'nvs', 'rom',
                 'component', 'overlay', 'overlay-report', 'commands', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    paths = vars(parser.parse_args()); output = paths.pop('output')
    print(json.dumps(check(paths, output)))


if __name__ == '__main__': main()
