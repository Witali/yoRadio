"""Phase B: root-owned full8 materialization after a reviewed actual qualifier terminal0."""
import argparse
import ast
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROJECT = 'target/cyd_vorbis_singleton_zero8_qemu'
QUALIFIER_SHA = '4eabc04a4ef877c61469b9c0b6a35560a2097f5fa395132bba60998bbd83e3c8'
QUALIFIER_PINS_SHA = '599cce53dee7e354e8b74773254ceb479e55e9d10c9308ffd918126edf198b72'
FIXED_SETUP = '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def sha(data): return hashlib.sha256(data).hexdigest()


def fact(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return dict(path=str(path), bytes=len(data), sha256=sha(data))


def put(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)


def document(path, value): put(path, (json.dumps(value, indent=2) + '\n').encode())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def seal_controller(template, replacements):
    """Source-only sealing; legitimate Python dunders remain untouched."""
    for marker, value in replacements.items():
        need(re.fullmatch(r'__[A-Z][A-Z0-9_]+__', marker), 'invalid_controller_marker')
        need(marker in template, 'controller_marker_missing:' + marker)
        template = template.replace(marker, value)
    need(re.search(r'__[A-Z][A-Z0-9_]+__', template) is None, 'unsealed_controller_placeholder')
    ast.parse(template)
    return template


def terminal_gate(args, qsha):
    path = args.qualification_terminal.resolve()
    need(path.is_relative_to(ROOT), 'qualifier_terminal_inside_checkout')
    value = json.loads(path.read_bytes())
    if value.get('schema') == 'direct-exec-tool-terminal-v1':
        need(type(value['exit_code']) is int and value['exit_code'] == 0 and value['report_sha256'] == qsha and
             value['entrypoint_sha256'] == QUALIFIER_SHA and type(value['session_id']) is int and value['session_id'] > 0 and
             value['terminal_chunk_id'], 'actual_qualifier_direct_tool_terminal0')
    else:
        need(value.get('status') == 'TERMINAL' and type(value.get('returncode')) is int and value['returncode'] == 0 and
             type(value.get('owned_pid')) is int and value['owned_pid'] > 0 and
             value.get('timed_out', False) is False and value.get('interrupted', False) is False and
             not value.get('error_type') and 'returncode_after_stop' not in value and
             value['runner_sha256'] == '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e', 'actual_qualifier_wrapper_terminal0')
        cwd, argv = Path(value['cwd']).resolve(), value['argv']
        need(cwd == ROOT and sum((cwd / part).resolve() == ROOT / '.build/cyd-vorbis-singleton-zero-bit-reference-prep-01/qualify.py' for part in argv) == 1,
             'qualifier_actual_entrypoint_and_cwd')
        def option(name):
            need(argv.count(name) == 1, 'qualifier_unique_actual_option:' + name)
            return argv[argv.index(name) + 1]
        need(option('--profile') == 'zero8' and (cwd / option('--output')).resolve() == args.qualification.resolve().parent and
             (cwd / option('--campaign')).resolve() == ROOT / '.build/cyd-vorbis-singleton-zero-bit-host-01' and
             (cwd / option('--outer')).resolve() == ROOT / '.build/cyd-vorbis-singleton-zero-bit-host-01-command.json', 'qualifier_actual_bound_operands')
    for origin, row in value.get('logs', {}).items():
        data = Path(origin).read_bytes()
        need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'actual_qualifier_terminal_log_identity')
    return fact(path)


def prepare(args):
    output, qpath = args.output.resolve(), args.qualification.resolve()
    need(output.parent == ROOT / '.build' and not output.exists() and qpath.is_relative_to(ROOT) and
         not qpath.is_relative_to(output), 'fresh_direct_child_build_runtime_and_bound_qualification')
    need(re.fullmatch('[0-9a-f]{64}', args.qualification_sha256), 'explicit_reviewed_actual_qualification_SHA')
    qraw = qpath.read_bytes()
    need(sha(qraw) == args.qualification_sha256, 'reviewed_qualification_identity')
    q = json.loads(qraw)
    need(q['completed'] is True and q['reference_corpus_qualified'] is True and q['result'] == 'XIPH_QUALIFIED_DUAL_NONPASS' and
         q['profile'] == 'zero8' and q['original_dual_reference_passed'] is False and
         (q['xiph_cases'], q['native_compared'], q['native_lookup2_refusals'], q['native_packet_decode_failures'], q['paired_raw_packets'], q['expected_pcm_bytes']) ==
         (8, 4, 0, 4, 112, 225280) and q['validated_inputs']['qualifier/script']['sha256'] == QUALIFIER_SHA and
         q['validated_inputs']['qualifier/pins']['sha256'] == QUALIFIER_PINS_SHA, 'actual_full8_reviewed_qualification_before_materialization')
    qterminal = terminal_gate(args, sha(qraw))  # No output directory/controller exists before this gate.
    readiness = json.loads((HERE / 'readiness.json').read_bytes())
    before = []
    for row in readiness['files']:
        observed = fact(HERE / row['path'])
        need((observed['bytes'], observed['sha256']) == (row['bytes'], row['sha256']), 'prepared_source_pin')
        before.append(observed)
    inputs = json.loads((HERE / 'source-inputs.json').read_bytes())
    for row in inputs['files']:
        observed = fact(ROOT / row['path'])
        need((observed['bytes'], observed['sha256']) == (row['bytes'], row['sha256']), 'frozen_materialization_input')
        before.append(observed)
    need(sha((HERE / 'recorded_qualification.py').read_bytes()) == QUALIFIER_SHA and sha((HERE / 'pins.json').read_bytes()) == QUALIFIER_PINS_SHA and
         sha((ROOT / 'idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c').read_bytes()) == FIXED_SETUP, 'reviewed_qualifier_and_CYD_setup_pins')
    comparison = ROOT / '.build/cyd-vorbis-singleton-zero-bit-generated-01/matrix.json'
    source = json.loads(comparison.read_bytes())
    ids = inputs['expected_case_ids']
    need([row['id'] for row in source['cases']] == ids and len(ids) == 8 and
         q['xiph_metamorphic_checks'] == [dict(decoder='libvorbis', kind=kind, cases=group, passed=True)
             for kind, field in (('equal','expected_same_decoder_pcm_equal_groups'),('different','expected_same_decoder_pcm_different_pairs'))
             for group in source[field]], 'actual_four_original_zero_equal_pairs')
    references = dict(inputs['reference'])
    need(qpath == ROOT / references['qualification']['path'] and sha(qraw) == references['qualification']['sha256'] and
         fact(qterminal['path']) == dict(path=str((ROOT / references['qualification_terminal']['path']).resolve()),
             bytes=references['qualification_terminal']['bytes'], sha256=references['qualification_terminal']['sha256']), 'exact_actual_qualifier_paths_and_identities')
    references['qualification'] = dict(path=qpath.relative_to(ROOT).as_posix(), bytes=len(qraw), sha256=sha(qraw))
    references['qualification_terminal'] = dict(path=Path(qterminal['path']).relative_to(ROOT).as_posix(),
                                              bytes=qterminal['bytes'], sha256=qterminal['sha256'])
    pins = dict(schema='singleton-zero8-sealed-runtime-inputs-v1', reference=references,
        qualifier_sha256=QUALIFIER_SHA, qualifier_pins_sha256=QUALIFIER_PINS_SHA,
        carrier_sha256=sha((HERE / 'carrier.py').read_bytes()),
        expected_case_ids=ids, expected_equal_groups=source['expected_same_decoder_pcm_equal_groups'],
        expected_different_pairs=source['expected_same_decoder_pcm_different_pairs'],
        qualified_reviewed_report_sha256=args.qualification_sha256, actual_qualifier_terminal0_required=True)
    output.mkdir()
    for name in ('protocol.py', 'windows_compile_command.py', 'materialize.py', 'reference_binding.py',
                 'recorded_qualification.py', 'carrier.py', 'pins.json'):
        put(output / name, (HERE / name).read_bytes())
    document(output / 'source-pins.json', pins)
    for path in sorted((HERE / PROJECT).rglob('*')):
        if path.is_file(): put(output / PROJECT / path.relative_to(HERE / PROJECT), path.read_bytes())
    mapping, manifests, raw_cases = [], [], []
    for group, selected in (('original4', source['cases'][:4]), ('zero4', source['cases'][4:])):
        for case in selected:
            pairs = {}
            for kind in ('identification', 'comment', 'setup', 'audio', 'ogg'):
                original = (comparison.parent / case[kind]).resolve()
                destination = (output / 'inputs' / group / case[kind]).resolve()
                need(original.is_relative_to(comparison.parent) and destination.is_relative_to(output / 'inputs' / group), 'raw_selection_boundary')
                data = original.read_bytes()
                put(destination, data)
                need(destination.read_bytes() == data, 'raw_selection_exact_copy')
                pairs[kind] = dict(original=fact(original), selected=fact(destination))
            index = len(mapping)
            mapping.append(dict(case=index, id=case['id'], original_group='original4' if index < 4 else 'zero4',
                original_matrix=fact(comparison), original_case_fields=case, selected_case_fields=copy.deepcopy(case), fields_changed=[], files=pairs))
            raw_cases.append({kind: (comparison.parent / case[kind]).read_bytes() for kind in ('identification', 'setup', 'audio')})
        matrix = output / 'inputs' / group / 'matrix.json'
        document(matrix, dict(schema='explicit-singleton-zero8-selection-v1', cases=selected, source_matrix=fact(comparison), case_fields_changed=False))
        manifests.append(dict(path=str(matrix.resolve()), sha256=sha(matrix.read_bytes())))
    mapping = dict(schema='singleton-zero8-original-source-map-v1', cases=mapping, original_cases_rewritten=False,
                   order='original4,zero4', new_reference_commands_executed=False)
    document(output / 'source-map.json', mapping)
    protocol = module('pinned_singleton_zero8_protocol', output / 'protocol.py')
    contract = protocol.load_contract(manifests)
    model = contract['model']
    counts = dict(cases=len(model['cases']), packets=model['total_packets'], expected_pcm_bytes=model['total_pcm'],
        protocol_events=3 + len(model['cases']) * (2 * protocol.PACKETS + 3), case_mask=model['case_mask'],
        arrays=len(model['cases']) * 5, full_raw_arrays=len(model['cases']) * 3)
    need(list(counts.values()) == [8, 112, 225280, 251, 255, 40, 24] and
         [case['id'] for case in model['cases']] == ids, 'complete_full8_derived_model_counts_and_order')
    document(output / 'contract.json', contract)
    formatter = module('singleton_zero8_source_formatter', output / 'materialize.py')
    materialized = formatter.materialize(output / 'contract.json', raw_cases, output / 'materialized01')
    sys.path.insert(0, str(output))  # Ordinary imports select the exact copied helpers.
    binder = module('singleton_zero8_recorded_reference_binding', output / 'reference_binding.py')
    binding = binder.derive(contract, mapping)
    document(output / 'reference-binding8.json', binding)
    replacements = {'__FIRST_MATRIX_PATH__': Path(manifests[0]['path']).relative_to(ROOT).as_posix(), '__FIRST_MATRIX_SHA__': manifests[0]['sha256'],
        '__SECOND_MATRIX_PATH__': Path(manifests[1]['path']).relative_to(ROOT).as_posix(), '__SECOND_MATRIX_SHA__': manifests[1]['sha256'],
        '__REFERENCE_PROOFS__': repr({row['path']: row['sha256'] for row in references.values()}),
        '__CONTRACT_ID__': contract['contract_sha256'], '__CONTRACT_FILE_SHA__': sha((output / 'contract.json').read_bytes()),
        '__DATA_HEADER_SHA__': materialized['header']['sha256'], '__SOURCE_MAP_SHA__': sha((output / 'source-map.json').read_bytes()),
        '__REFERENCE_BINDING_SHA__': sha((output / 'reference-binding8.json').read_bytes()),
        '__REFERENCE_HELPER_SHA__': sha((output / 'reference_binding.py').read_bytes()),
        '__RECORDED_HELPER_SHA__': sha((output / 'recorded_qualification.py').read_bytes()),
        '__CARRIER_HELPER_SHA__': sha((output / 'carrier.py').read_bytes()),
        '__QUALIFIER_PINS_SHA__': sha((output / 'pins.json').read_bytes()), '__SOURCE_PINS_SHA__': sha((output / 'source-pins.json').read_bytes()),
        '__QUALIFICATION_ROOT__': qpath.parent.relative_to(ROOT).as_posix(),
        '__CASE_COUNT__': str(counts['cases']), '__TOTAL_PACKETS__': str(counts['packets']), '__TOTAL_PCM__': str(counts['expected_pcm_bytes']),
        '__CASE_MASK__': str(counts['case_mask']), '__PROTOCOL_EVENTS__': str(counts['protocol_events'])}
    template = (HERE / 'controller.template.py').read_text(encoding='utf-8')
    template = seal_controller(template, replacements)
    controller = output / 'run-cyd-vorbis-singleton-zero8-qemu.py'
    # This is the first runnable controller publication, after qualification,
    # complete source/reference binding, and independent C header recovery.
    put(controller, template.encode())
    for row in before:
        need(fact(row['path']) == row, 'input_changed_during_materialization')
    document(output / 'preparation.json', dict(schema='singleton-zero8-root-materialization-v1', completed=True,
        counts=counts, actual_qualification_terminal0_verified=True, qualification=fact(qpath),
        contract=fact(output / 'contract.json'), header=materialized['header'], controller=fact(controller),
        all_eight_original_bytes_unchanged=True, target_executed=False, numeric_qualified=False, full_G6_qualified=False))
    print(json.dumps(dict(output=str(output), counts=counts, controller=fact(controller), target_executed=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--qualification', type=Path, required=True)
    parser.add_argument('--qualification-sha256', required=True)
    parser.add_argument('--qualification-terminal', type=Path, required=True)
    prepare(parser.parse_args())
