"""Reject real lookalike timer wrappers and altered relocated instruction bodies."""
import argparse
import copy
import gzip
import io
import json
from pathlib import Path
import sys

from elftools.elf.elffile import ELFFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_factory_xrefs import Image, sha, startup_gp
from match_factory_timers import CASES, classify, load_models, anchored_match
from reverse.rv32_link_match import match
from reverse.native_timer_match import describe as describe_native


def controls(factory, directory, report):
    """Exercise actual SDK/firmware bytes; masked call immediates must still bind correctly."""
    image, models = Image(factory), load_models(directory)
    gp = startup_gp(image)
    spec = models['pp_timer_coex_slice']['spec']
    start, end = 0x4207b11a, 0x4207b12c
    data = image.read(start, len(spec['code']) + 64, True)
    anchors = {'pm_coex_slice_timeout_process': 0x420756f0}
    anchored_match(spec, data, start, end, gp, anchors, {})
    rejected = []
    for case in ('real-neighbor-wrapper', 'changed-return', 'changed-relocated-callee',
                 'truncated-body', 'wrong-end', 'wrong-callee-anchor', 'missing-anchor', 'wrong-local-state-anchor'):
        code, first, last, selected, globals_, locals_ = bytearray(data), start, end, spec, dict(anchors), {}
        if case == 'real-neighbor-wrapper':
            first, last = 0x4207b108, 0x4207b11a
            code = bytearray(image.read(first, len(spec['code']) + 64, True))
            # The original byte matcher legitimately accepts the instruction
            # shape; only a bound callee can distinguish these real wrappers.
            lookalike = match(spec, code, first, gp)
            assert lookalike['symbol_bindings'][0]['address'] == 0x4207582e
        elif case == 'changed-return':
            assert code[12:14] == bytes.fromhex('0545')
            code[12:14] = bytes.fromhex('0145')
        elif case == 'changed-relocated-callee':
            code[7] ^= 0x10
            assert match(spec, code, start, gp)['symbol_bindings'][0]['address'] != anchors['pm_coex_slice_timeout_process']
        elif case == 'truncated-body': code = code[:end - start - 2]
        elif case == 'wrong-end': last += 2
        elif case == 'wrong-callee-anchor': globals_['pm_coex_slice_timeout_process'] += 2
        elif case == 'missing-anchor': globals_.clear()
        else:
            name, _, first, last = CASES[1]
            selected = models[name]['spec']
            code = image.read(first, len(selected['code']) + 64, True)
            row = next(item for item in report['functions'] if item['name'] == name)
            local = next(item for item in row['symbol_bindings'] if item['binding'] == 'STB_LOCAL')
            locals_[(local['name'], local['section'])] = local['address'] + 4
            globals_.clear()
        try:
            anchored_match(selected, bytes(code), first, last, gp, globals_, locals_)
        except (AssertionError, ValueError, IndexError):
            rejected.append(case)
        else:
            raise AssertionError('Unsafe timer identification accepted: ' + case)
    return rejected


def verify_report(factory, directory, saved):
    """Recreate every complete byte/edge/binding trace and the eight rejection controls."""
    expected = copy.deepcopy(saved)
    expected.pop('inputs_sha256')
    actual = classify(factory, directory)
    assert actual == expected, 'SDK timer match report differs'
    rejected = controls(factory, directory, actual)
    return {'passed': True, 'functions': len(actual['functions']),
            'sdk_bytes': sum(row['source_bytes'] for row in actual['functions']),
            'linked_bytes': sum(row['linked_bytes'] for row in actual['functions']),
            'local_branches_checked': sum(row['local_branches_checked'] for row in actual['functions']),
            'rejected_controls': rejected, 'whole_image_completeness_proved': False,
            'semantic_equivalence_proved': False, 'physical_hardware_tested': False,
            'no_vm_or_hardware_access': True}


def main():
    """Save new results and exact verifier identities after checking real saved evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--sdk-libraries', type=Path, required=True)
    parser.add_argument('--match-report', type=Path, required=True)
    parser.add_argument('--native-elf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.match_report.read_bytes()
    saved = json.loads(gzip.decompress(raw) if args.match_report.suffix == '.gz' else raw)
    files = [Path(__file__), Path(__file__).resolve().parents[1] / 'tools/reverse/native_timer_match.py',
             *map(Path, saved['inputs_sha256'])]
    pins = {str(file.resolve()): sha(file.read_bytes()) for file in files}
    assert all(pins[name] == digest for name, digest in saved['inputs_sha256'].items()), 'Changed matcher source'
    result = verify_report(args.elf.read_bytes(), args.sdk_libraries, saved)
    if args.native_elf:
        data = args.native_elf.read_bytes()
        native = describe_native(data, args.sdk_libraries)
        assert len(native['functions']) == len(CASES) == 9
        result['native'] = native
        # A real neighboring wrapper passes the instruction-shape matcher but
        # cannot use another timer's named native target. Return-value changes
        # must fail independently of address relocation.
        elf = ELFFile(io.BytesIO(data))
        table = list(elf.get_section_by_name('.symtab').iter_symbols())
        def code_for(name):
            """Read a selected symbol's actual executable bytes for negative controls."""
            symbol = next(row for row in table if row.name == name and row['st_info']['type'] == 'STT_FUNC')
            section = elf.get_section(symbol['st_shndx'])
            offset = symbol['st_value'] - section['sh_addr']
            return section.data()[offset:offset + symbol['st_size']]
        wrong_return = bytearray(code_for('pp_timer_coex_slice'))
        assert wrong_return[12:14] == bytes.fromhex('0545')
        wrong_return[12:14] = bytes.fromhex('0145')
        result['native_rejected_controls'] = []
        for name, code in (('real-neighbor-wrapper', code_for('pp_timer_sleep_delay')), ('changed-return', wrong_return)):
            try:
                describe_native(data, args.sdk_libraries, {'pp_timer_coex_slice': bytes(code)})
            except (AssertionError, ValueError):
                result['native_rejected_controls'].append(name)
            else:
                raise AssertionError('Altered native function accepted: ' + name)
    assert pins == {str(file.resolve()): sha(file.read_bytes()) for file in files}, 'Sources changed during test'
    result.update(inputs_sha256=pins, inputs_unchanged=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    summary = {key: value for key, value in result.items() if key not in ('inputs_sha256', 'native')}
    if 'native' in result:
        summary['native_functions_matched'] = len(result['native']['functions'])
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
