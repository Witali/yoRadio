"""Reject incorrect SDK event-11 bodies before interpreting their differences."""
import argparse
from importlib.metadata import version
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_factory_xrefs import Image, sha
from reverse.timer_event11_match import qualify, NAMES, adapter_table
from timer_event11_semantics import run as semantics


def run(factory_path, native_path, old_library, new_library):
    """Qualify real bodies, then fault exact code in private host copies."""
    factory, native = factory_path.read_bytes(), native_path.read_bytes()
    accepted = qualify(factory, native, old_library, new_library)
    image = Image(factory)
    functions = {row['name']: row for row in accepted['layouts']['factory']['functions']}
    callback = functions[NAMES['factory'][0]]
    raw = image.read(int(callback['start'], 0), callback['linked_bytes'], True)
    assert raw.count(bytes.fromhex('0545')) == 1
    changed_return = raw.replace(bytes.fromhex('0545'), bytes.fromhex('0945'))
    rearm = functions[NAMES['factory'][2]]
    rearm_code = image.read(int(rearm['start'], 0), rearm['linked_bytes'], True)
    handler = functions[NAMES['factory'][1]]
    handler_code = image.read(int(handler['start'], 0), handler['linked_bytes'], True)
    wrong_state = bytearray(handler_code)
    assert bytes(wrong_state[8:12]) == bytes.fromhex('b737cc3f')
    wrong_state[8:12] = bytes.fromhex('b747cc3f')
    setter = accepted['layouts']['factory']['configuration_function']
    setter_code = image.read(int(setter['start'], 0), setter['linked_bytes'], True)
    table = accepted['layouts']['factory']['osi_table']['address']
    def damaged_table(offset, value):
        """Fault only a private initialized table read, never the firmware image."""
        def read(address, size, execute=False):
            raw = bytearray(image.read(address, size, execute))
            if address == table and size == 480:
                raw[offset:offset + 4] = value.to_bytes(4, 'little')
            return bytes(raw)
        return adapter_table(read, 'factory')
    cases = {
        'wrong-factory-image': lambda: qualify(factory[:-1], native, old_library, new_library),
        'wrong-native-image': lambda: qualify(factory, native[:-1], old_library, new_library),
        'swapped-sdk-version': lambda: qualify(factory, native, new_library, old_library),
        'wrapper-return-value': lambda: qualify(factory, native, old_library, new_library,
                                                {('factory', NAMES['factory'][0]): changed_return}),
        'truncated-rearm': lambda: qualify(factory, native, old_library, new_library,
                                            {('factory', NAMES['factory'][2]): rearm_code[:-2]}),
        'neighboring-body': lambda: qualify(factory, native, old_library, new_library,
                                             {('factory', NAMES['factory'][2]): image.read(0x42074c08, len(rearm_code), True)}),
        'changed-pm-state-anchor': lambda: qualify(factory, native, old_library, new_library,
                                                   {('factory', NAMES['factory'][1]): bytes(wrong_state)}),
        'truncated-config-setter': lambda: qualify(factory, native, old_library, new_library,
                                                     {('factory', 'pm_set_bss_max_idle'): setter_code[:-2]}),
        'wrong-osi-version': lambda: damaged_table(0, 9),
        'wrong-osi-magic': lambda: damaged_table(476, 0),
        'swapped-timer-units-slot': lambda: damaged_table(224, 0x40384800),
    }
    rejected = []
    for name, action in cases.items():
        try:
            action()
        except (AssertionError, ValueError):
            rejected.append(name)
        else:
            raise AssertionError('Invalid event-11 qualification accepted: ' + name)
    return dict(passed=True, qualification=accepted, rejected_controls=rejected,
                instructions=semantics(accepted, factory, native),
                engines={'unicorn': version('unicorn'), 'pyelftools': version('pyelftools')},
                semantic_equivalence_proved=False, whole_image_completeness_proved=False,
                physical_hardware_tested=False)


def main():
    """Read immutable binaries and save a new static/instruction checkpoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--factory', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--old-library', type=Path, required=True)
    parser.add_argument('--new-library', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Preserve existing event-11 results; use a new output')
    root = Path(__file__).resolve().parents[1]
    inputs = [args.factory, args.native, args.old_library, args.new_library, Path(__file__),
              *(root / path for path in (
                  'tools/reverse/timer_event11_match.py', 'tools/reverse/rv32_link_match.py',
                  'tools/reverse/elf_archive.py', 'tools/audit_factory_xrefs.py',
                  'tests/timer_event11_semantics.py', 'tests/timer_event11_model.py',
                  'tests/timer_event11_instructions.py'))]
    pins = {str(path.resolve()): sha(path.read_bytes()) for path in inputs}
    result = run(args.factory, args.native, args.old_library, args.new_library)
    assert all(sha(Path(path).read_bytes()) == digest for path, digest in pins.items())
    result.update(inputs_sha256=pins, inputs_unchanged=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=True, qualified_bodies=8, rejected_controls=len(result['rejected_controls']),
                          instruction_executions=result['instructions']['total_executions'],
                          coverage=result['instructions']['coverage'])))


if __name__ == '__main__':
    main()
