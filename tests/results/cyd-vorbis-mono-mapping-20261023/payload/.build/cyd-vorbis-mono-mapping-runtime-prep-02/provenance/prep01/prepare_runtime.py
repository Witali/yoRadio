"""Root-only materialization of complete mono21 after frozen actual reference qualification."""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROJECT = 'target/cyd_vorbis_mono21_qemu'
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


def prepare(args):
    output = args.output.resolve()
    need(output.parent == ROOT / '.build' and not output.exists(), 'fresh_direct_child_build_runtime')
    readiness = json.loads((HERE / 'readiness.json').read_bytes())
    before = []
    for row in readiness['files']:
        observed = fact(HERE / row['path'])
        need((observed['bytes'], observed['sha256']) == (row['bytes'], row['sha256']), 'prepared_source_pin')
        before.append(observed)
    inputs = json.loads((HERE / 'source-inputs.json').read_bytes())
    for row in inputs['files']:
        observed = fact(ROOT / row['path'])
        need((observed['bytes'], observed['sha256']) == (row['bytes'], row['sha256']), 'frozen_source_input')
        before.append(observed)
    refs = inputs['reference']
    qpath = ROOT / refs['qualification']['path']
    q = json.loads(qpath.read_bytes())
    need(args.qualification_sha256 == refs['qualification']['sha256'] and
         q['profile'] == 'mono21' and q['result'] == 'DUAL_REFERENCE_QUALIFIED' and
         all(q[key] is True for key in ('completed', 'reference_corpus_qualified', 'dual_reference_qualified')) and
         (q['xiph_cases'], q['native_compared'], q['paired_raw_packets'], q['expected_pcm_bytes']) == (21, 21, 294, 464640),
         'reviewed_actual_complete21_reference_qualification_required')
    terminal = json.loads((ROOT / refs['qualification_terminal']['path']).read_bytes())
    need(terminal['status'] == 'TERMINAL' and type(terminal['returncode']) is int and terminal['returncode'] == 0 and
         type(terminal['owned_pid']) is int and terminal['owned_pid'] > 0 and
         terminal.get('timed_out', False) is False and terminal.get('interrupted', False) is False and
         not terminal.get('error_type') and 'returncode_after_stop' not in terminal and
         terminal['runner_sha256'] == inputs['command_wrapper_sha256'], 'actual_pinned_qualifier_terminal0')
    argv, cwd = terminal['argv'], Path(terminal['cwd']).resolve()
    need(cwd == ROOT and argv.count('--profile') == 1 and argv[argv.index('--profile') + 1] == 'mono21' and
         sum((cwd / part).resolve() == ROOT / inputs['qualifier_path'] for part in argv) == 1,
         'qualifier_actual_profile_entrypoint')
    for option, expected in (('--repository', ROOT), ('--campaign', (ROOT / refs['host']['path']).parent),
                             ('--outer', ROOT / refs['host_outer']['path']), ('--output', qpath.parent)):
        need(argv.count(option) == 1 and (cwd / argv[argv.index(option) + 1]).resolve() == expected.resolve(),
             'qualifier_actual_operand:' + option)
    for name, row in terminal['logs'].items():
        observed = fact(name)
        need((observed['bytes'], observed['sha256']) == (row['bytes'], row['sha256']), 'qualifier_actual_log_identity')
        before.append(observed)
    need(sha((ROOT / 'idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c').read_bytes()) == FIXED_SETUP,
         'reviewed_CYD_source_required')
    comparison = ROOT / refs['comparison']['path']
    source = json.loads(comparison.read_bytes())
    ids = inputs['expected_case_ids']
    need([row['id'] for row in source['cases']] == ids and len(ids) == 21 and
         comparison.read_bytes() == (ROOT / refs['host_matrix']['path']).read_bytes(), 'exact_original21_matrix')
    # This gate and all source pins precede any output creation or controller.
    output.mkdir()
    for name in ('protocol.py', 'windows_compile_command.py', 'materialize.py', 'reference_binding.py',
                 'recorded_qualification.py', 'carrier.py'):
        put(output / name, (HERE / name).read_bytes())
    document(output / 'source-pins.json', dict(schema='mono21-sealed-runtime-inputs-v1', reference=refs,
        qualifier_sha256=inputs['qualifier_sha256'], qualifier_pins_sha256=inputs['qualifier_pins_sha256'],
        carrier_sha256=inputs['carrier_sha256'], command_wrapper_sha256=inputs['command_wrapper_sha256'],
        expected_case_ids=ids, qualified_reviewed_report_sha256=args.qualification_sha256,
        actual_qualifier_terminal0_required=True, prior_unrelated_NONPASS_unchanged=True))
    for path in sorted((HERE / PROJECT).rglob('*')):
        if path.is_file(): put(output / PROJECT / path.relative_to(HERE / PROJECT), path.read_bytes())
    corpus = output / 'inputs/all21'
    manifest = json.loads((ROOT / refs['manifest']['path']).read_bytes())
    for row in manifest['files']:
        original = (comparison.parent / row['path']).resolve()
        destination = (corpus / row['path']).resolve()
        need(original.is_relative_to(comparison.parent) and destination.is_relative_to(corpus), 'corpus_copy_boundaries')
        data = original.read_bytes()
        need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'canonical_complete_corpus_pin')
        put(destination, data)
    put(corpus / 'manifest.json', (ROOT / refs['manifest']['path']).read_bytes())
    mapping, raw_cases = [], []
    for index, case in enumerate(source['cases']):
        pairs = {}
        for kind in ('identification', 'comment', 'setup', 'audio', 'ogg'):
            original, destination = comparison.parent / case[kind], corpus / case[kind]
            need(original.read_bytes() == destination.read_bytes(), 'original_raw_exact_copy')
            pairs[kind] = dict(original=fact(original), selected=fact(destination))
        mapping.append(dict(case=index, id=case['id'], original_group='mono21',
            original_matrix=fact(comparison), original_reference_matrix=refs['host_matrix'],
            original_case_fields=case, selected_case_fields=copy.deepcopy(case), fields_changed=[], files=pairs))
        raw_cases.append({kind: (corpus / case[kind]).read_bytes() for kind in ('identification', 'setup', 'audio')})
    mapping = dict(schema='mono21-original-source-map-v1', cases=mapping, original_cases_rewritten=False,
                   order='exact-original-matrix-order', new_reference_commands_executed=False)
    document(output / 'source-map.json', mapping)
    matrix = corpus / 'matrix.json'
    manifests = [dict(path=str(matrix.resolve()), sha256=sha(matrix.read_bytes()))]
    protocol = module('mono21_protocol', output / 'protocol.py')
    contract = protocol.load_contract(manifests)
    model = contract['model']
    counts = dict(cases=len(model['cases']), packets=model['total_packets'], expected_pcm_bytes=model['total_pcm'],
        protocol_events=3 + len(model['cases']) * (2 * protocol.PACKETS + 3), case_mask=model['case_mask'],
        arrays=len(model['cases']) * 5, full_raw_arrays=len(model['cases']) * 3)
    need(list(counts.values()) == [21, 294, 464640, 654, 2097151, 105, 63] and
         [case['id'] for case in model['cases']] == ids and
         [case['channels'] for case in model['cases']].count(1) == 9 and
         [case['channels'] for case in model['cases']].count(2) == 12, 'complete21_derived_counts_order_channels')
    document(output / 'contract.json', contract)
    formatter = module('mono21_formatter', output / 'materialize.py')
    materialized = formatter.materialize(output / 'contract.json', raw_cases, output / 'materialized01')
    sys.path.insert(0, str(output))  # Ordinary imports resolve the exact copied helper bytes.
    binder = module('mono21_recorded_reference_binding', output / 'reference_binding.py')
    binding = binder.derive(contract, mapping)
    document(output / 'reference-binding21.json', binding)
    replacements = {'__FIRST_MATRIX_PATH__': matrix.relative_to(ROOT).as_posix(), '__FIRST_MATRIX_SHA__': manifests[0]['sha256'],
        '__REFERENCE_PROOFS__': repr({row['path']: row['sha256'] for row in refs.values()}),
        '__CONTRACT_ID__': contract['contract_sha256'], '__CONTRACT_FILE_SHA__': sha((output / 'contract.json').read_bytes()),
        '__DATA_HEADER_SHA__': materialized['header']['sha256'], '__SOURCE_MAP_SHA__': sha((output / 'source-map.json').read_bytes()),
        '__REFERENCE_BINDING_SHA__': sha((output / 'reference-binding21.json').read_bytes()),
        '__REFERENCE_HELPER_SHA__': sha((output / 'reference_binding.py').read_bytes()),
        '__RECORDED_HELPER_SHA__': sha((output / 'recorded_qualification.py').read_bytes()),
        '__CARRIER_HELPER_SHA__': sha((output / 'carrier.py').read_bytes()),
        '__SOURCE_PINS_SHA__': sha((output / 'source-pins.json').read_bytes()),
        '__QUALIFICATION_ROOT__': qpath.parent.relative_to(ROOT).as_posix(),
        '__CASE_COUNT__': str(counts['cases']), '__TOTAL_PACKETS__': str(counts['packets']), '__TOTAL_PCM__': str(counts['expected_pcm_bytes']),
        '__CASE_MASK__': str(counts['case_mask']), '__PROTOCOL_EVENTS__': str(counts['protocol_events'])}
    template = (HERE / 'controller.template.py').read_text(encoding='utf-8')
    for marker, value in replacements.items():
        need(marker in template, 'controller_marker_missing:' + marker)
        template = template.replace(marker, value)
    need('__' not in template.replace('__file__', '').replace('__name__', '').replace('__main__', '')
         .replace('__wrap_esp_vorbis_dec_open', '').replace('__wrap_esp_vorbis_dec_decode', ''), 'unsealed_controller_marker')
    ast.parse(template)
    controller = output / 'run-cyd-vorbis-mono21-qemu.py'
    # First runnable controller: actual qualifier, full42 recorded-reference replay,
    # full21 source binding and independent C readback have already succeeded.
    put(controller, template.encode())
    for row in before:
        need(fact(row['path']) == row, 'input_changed_during_materialization')
    document(output / 'preparation.json', dict(schema='mono21-root-materialization-v1', completed=True,
        counts=counts, actual_qualification_terminal0_verified=True, qualification=fact(qpath),
        contract=fact(output / 'contract.json'), header=materialized['header'], controller=fact(controller),
        all_twenty_one_original_bytes_unchanged=True, target_executed=False, numeric_qualified=False, full_G6_qualified=False))
    print(json.dumps(dict(output=str(output), counts=counts, controller=fact(controller), target_executed=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--qualification-sha256', required=True)
    prepare(parser.parse_args())
