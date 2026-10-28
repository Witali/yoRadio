"""Reproduce inherited NVS defects with real Item/HashList code and real ROM CRC."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha
from reverse.nvs_record_linkage import archive_objects, qualify
from nvs_rom_crc import qualify as rom_qualify, vectors as crc_vectors
from nvs_records_cpu import run
from nvs_header_vectors import run as headers_run
from nvs_records_controls import controls
from verify_rv32_disassembly_evidence import payload


def same(actual, expected):
    """A successful reproduction does not turn a failing preservation contract into a pass."""
    if actual != expected: raise ValueError('NVS record before-evidence differs')


def verify(proof_path, root, factory, native, app, archive, rom):
    """Replay bounded synthetic records without rewriting firmware, source SDKs or a VM."""
    proof = json.loads(proof_path.read_bytes())
    if proof['schema'] != 'nvs-records-before-evidence-v1' or not proof['passed']: raise ValueError('Wrong before proof')
    for name, digest in proof['source_pins'].items():
        path = (root/name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path.read_bytes()) != digest: raise ValueError('Record source pin differs: '+name)
    files = {name: payload(proof_path.parent, ref) for name, ref in proof['files'].items()}
    parts = {'nvs_page.cpp': payload(proof_path.parent, proof['page_object']),
             'nvs_types.cpp': files['object:types'], 'nvs_item_hash_list.cpp': files['object:hash']}
    original = factory.read_bytes(); current = native.read_bytes(); image = app.read_bytes()
    if sha(current) != proof['native_elf_sha256'] or sha(image) != proof['app_sha256']: raise ValueError('Wrong before image')
    current_parts = archive_objects(archive.read_bytes()); linkage = qualify(original, parts, current, image, current_parts)
    same(linkage, json.loads(files['linkage']))
    crc = rom_qualify(rom.read_bytes()); same(crc, json.loads(files['crc']))
    arithmetic = crc_vectors(crc); same(arithmetic, json.loads(files['crc_vectors']))
    headers = headers_run(original, current, image, linkage, crc); same(headers, json.loads(files['headers']))
    before = run(original, current, image, linkage, crc); same(before, json.loads(files['before']))
    negative = controls(original, parts, current, image, current_parts, linkage, crc); same(negative, json.loads(files['controls']))
    for key in ('native_counter_contract_passed', 'native_key_contract_passed'):
        if before[key] is not False or proof[key] is not False: raise ValueError('Unfixed NVS defect hidden')
    expected_counts = ['illegal-slot', 'variable-erased-child', 'variable-partial-empty-child']
    expected_keys = ['blob-chunks', 'blob-generations', 'published-index-before-new-generation', 'hash24-collision']
    for rows in before['results'].values():
        if [r['name'] for r in rows if not r['counters_correct']] != expected_counts or \
                [r['name'] for r in rows if not r['keys_correct']] != expected_keys: raise ValueError('Known before defect set differs')
    rejected = []
    for fault in ('counter-pass', 'key-pass', 'hash-collision-lookup', 'chunk-retention-lookup', 'rom-computation', 'missing-header-case'):
        baseline = headers if fault == 'missing-header-case' else crc if fault == 'rom-computation' else before
        changed = deepcopy(baseline)
        if fault == 'counter-pass': changed['native_counter_contract_passed'] = True
        elif fault == 'key-pass': changed['native_key_contract_passed'] = True
        elif fault.endswith('-lookup'):
            name = 'hash24-collision' if fault.startswith('hash') else 'published-index-before-new-generation'
            row = next(r for r in changed['results']['native'] if r['name'] == name)
            row['lookups'][0]['status'] = 0
        elif fault == 'rom-computation': changed['table']['sha256'] = '0'*64
        else: changed['results']['native'].pop()
        try: same(changed, baseline)
        except ValueError: rejected.append(fault)
        else: raise AssertionError('Forged before result accepted')
    if factory.read_bytes() != original or native.read_bytes() != current or app.read_bytes() != image:
        raise ValueError('Before firmware input changed')
    return dict(passed=True, functions={k: len(v['functions']) for k, v in linkage['variants'].items()},
                rom_cases=arithmetic['cases'], header_cases=headers['total_cases'],
                record_cases=sum(len(v) for v in before['results'].values()), oom_cases=sum(len(v) for v in before['oom'].values()),
                counter_failures=expected_counts, key_failures=expected_keys, native_counter_contract_passed=False,
                native_key_contract_passed=False, input_mutations_rejected=len(negative['rejected']),
                report_mutations_rejected=rejected, physical_hardware_tested=False)


def main():
    """Require the exact unchanged before pair and official ROM ELF."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    for name in ('proof', 'factory', 'native', 'app', 'nvs', 'rom'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args(); print(json.dumps(verify(args.proof, args.root, args.factory, args.native, args.app, args.nvs, args.rom)))


if __name__ == '__main__': main()
