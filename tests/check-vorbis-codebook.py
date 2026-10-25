"""Replay saved owned-codebook values; execute no component, compiler or SDK."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
ORACLE_SHA = 'e6b56ef59fd387da6f8e288e035470535f6bebcad9aef3c2e1150e7e587246a1'
CONTROL_SHA = '55ccf491adf33f98023f779d31e7cb955f46dbaf9f5b7b6e20d62a14d991b33b'
DRIVER_SHA = '5cb7b8def265b62045721f21895508c6867b51c8d007050d95fb5625c321d44e'
MODULE = {'floor0.c': '297e055a68ff2ee4ea71e0879aef12456139945015d346b2a12a18db7b0a4335',
    'quant.c': '14e6b7eb910ee4c7a67ff0b1eccf8f4038315d1bf5821ad51fba32824e5ffb40',
    'include/native_vorbis_floor0.h': '122ee70ab248c5aa3a46354288be3d78418e6d5e67f15c4d44d43f5ff704c63b',
    'include/native_vorbis_quant.h': '55948c2a9af4d92e2ebe614398fd09708c454b4a6f179b602d964f06aac9a499',
    'codebook.c': '51122d5d9dce8513d371764c1208641bb7b3a64a170095510705a88d900522ec',
    'include/native_vorbis_codebook.h': '4373f63fa1f3bd352b7c30720e0c9c261d5b34df799b1d0b9c8787e700fbda20',
    'CMakeLists.txt': '2b2395e6b3aa254dd4c34657291cae0be05b395a343729b66e844a6013d77638'}

def need(ok, reason):
    if not ok: raise ValueError(reason)
def sha(body): return hashlib.sha256(body).hexdigest()
def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('host', 'esp32', 'esp32c3', 'receipts', 'output'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    need(all(re.fullmatch('[0-9a-f]{64}', pin) for pin in (ORACLE_SHA, CONTROL_SHA, DRIVER_SHA)), 'reviewed frozen source pins before measurement')
    out = args.output.resolve(); need(out.is_relative_to(ROOT/'.build') and out != ROOT/'.build' and not out.exists(), 'fresh comparison output')
    out.mkdir(parents=True); (out/'inputs').mkdir()
    report = dict(completed=False, passed=False, measurement_completed=False, host_exact_recomputed=False,
        finite_codebook_qualified=False, targets={}, inputs={}, identity_only={}, SDK_or_QEMU_executed=False,
        component_executed=False, decoder_executed=False, stream_decoder_executed=False, production_radio_integration=False,
        full_floor0_qualified=False, full_G6_qualified=False, PCM_qualified=False, physical_device=False)
    def save(): (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    def read(path):
        path = path.resolve(); body = path.read_bytes(); digest = sha(body); previous = report['inputs'].get(str(path))
        need(previous is None or previous['sha256'] == digest, 'consumed original input changed')
        destination = out/'inputs'/digest
        if not destination.exists(): destination.write_bytes(body)
        else: need(destination.read_bytes() == body, 'content-addressed input collision')
        report['inputs'][str(path)] = dict(sha256=digest, bytes=len(body), snapshot='inputs/'+digest); return body
    def document(path): return json.loads(read(path))
    def identity(path):
        path = path.resolve(); body = path.read_bytes(); pin = dict(sha256=sha(body), bytes=len(body), reason='Executable identity only; body omitted.')
        previous = report['identity_only'].get(str(path)); need(previous is None or previous == pin, 'executable identity changed')
        report['identity_only'][str(path)] = pin; return pin['sha256']
    def terminal(name, directory, script, pins=None):
        receipt = document(args.receipts/(name+'.json')); argv = receipt['argv']; cwd = Path(receipt['cwd']).resolve()
        need(receipt['status'] == 'TERMINAL' and type(receipt['returncode']) is int and receipt['returncode'] == 0 and
             type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0 and not receipt.get('timed_out') and not receipt.get('interrupted') and
             not any(key in receipt for key in ('error_type', 'returncode_after_stop')), 'actual successful outer terminal '+name)
        need(cwd == ROOT and argv[1:4] == ['-B', '-X', 'utf8'] and Path(argv[0]).resolve() == Path(sys.executable).resolve() and
             (cwd/argv[4]).resolve() == ROOT/'tests'/script, 'actual executable/script/cwd')
        need(sha(read(ROOT/'.build/cyd-vorbis-format-command-01.py')) == receipt['runner_sha256'] ==
             '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e' and
             receipt['executable_sha256'] == identity(Path(sys.executable)) ==
             '4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a', 'owned runner/executable identities')
        def option(key):
            flag = '--'+key; need(argv.count(flag) == 1 and argv.index(flag)+1 < len(argv), 'one complete actual option '+key)
            return argv[argv.index(flag)+1]
        need((cwd/option('output')).resolve() == directory, 'receipt belongs to supplied campaign')
        if name == 'host': need(len(argv) == 7 and argv[5] == '--output', 'exact host invocation')
        else:
            need(option('target') == name and (cwd/option('cases')).resolve() == args.host.resolve()/'target-cases', 'actual native target/cases')
            for key, value in pins.items(): need(option(key+'-sha256') == value, 'actual source/data/tool pin '+key)
        need({Path(path).resolve() for path in receipt['logs']} == {args.receipts.resolve()/(name+'.'+stream+'.log') for stream in ('stdout', 'stderr')}, 'exact actual outer log inventory')
        for path, pin in receipt['logs'].items():
            body = read(Path(path)); need(len(body) == pin['bytes'] and sha(body) == pin['sha256'], 'actual terminal stream')
    def sources(directory, pins):
        for origin, pin in pins.items():
            snapshot = (directory/pin['snapshot']).resolve(); need(snapshot.is_relative_to(directory), 'contained frozen source')
            body = read(snapshot); need(sha(body) == pin['sha256'] == sha(read(Path(origin))) and ('bytes' not in pin or len(body) == pin['bytes']), 'original/frozen source identity')
    save()
    try:
        read(Path(__file__)); host = args.host.resolve(); captured = {'esp32': args.esp32.resolve(), 'esp32c3': args.esp32c3.resolve()}
        terminal('host', host, 'test-vorbis-codebook.py'); hr = document(host/'report.json')
        need(all(hr[k] is True for k in ('completed', 'passed', 'prepared', 'component_executed', 'source_inputs_unchanged')), 'actual complete sanitized host campaign')
        sources(host, hr['sources'])
        oracle_path = ROOT/'tests/test-vorbis-codebook.py'; control_path = ROOT/'tests/run-vorbis-codebook-qemu.py'
        need(sha(read(oracle_path)) == ORACLE_SHA == hr['sources'][str(oracle_path.resolve())]['sha256'] and
             sha(read(control_path)) == CONTROL_SHA and sha(read(ROOT/'tests/native/vorbis_codebook_test.c')) == DRIVER_SHA, 'exact independently reviewed oracle/controller/adapter')
        oracle, control = load_module(oracle_path, 'codebook_oracle'), load_module(control_path, 'codebook_capture')
        for name, digest in MODULE.items(): need(sha(read(ROOT/'idf/components/native_vorbis_numeric'/name)) == digest, 'exact complete owned component '+name)
        need(hr['policy'] == oracle.POLICY and oracle.self_checks() == hr['oracle_self_checks'] and all(hr[k] is False for k in
             ('full_floor0_qualified', 'full_G6_qualified', 'PCM_qualified', 'decoder_executed', 'SDK_or_QEMU_executed', 'physical_device')), 'fixed host policy/scope')
        owner = ast.parse(read(host/'sources/supervisor-owner.py'))
        literals = [node.value for node in owner.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SUPERVISOR' for t in node.targets)]
        need(len(literals) == 1 and ast.literal_eval(literals[0]).encode() == read(host/'supervisor.py'), 'actual owned supervisor body')
        need([row['name'] for row in hr['commands']] == ['compiler-version', 'compiler-machine', 'compile', 'execute'], 'four actual host commands')
        for command in hr['commands']:
            name = command['name']; request, receipt = document(host/(name+'.request.json')), document(host/(name+'.receipt.json'))
            need(receipt == command['supervisor'] and request['argv'] == command['child_argv'] and request['timeout'] == 60 and
                 receipt['request_sha256'] == sha(read(host/(name+'.request.json'))) and receipt['nonce'] == request['nonce'] == command['nonce'] and
                 receipt['state'] == 'terminal' and type(receipt['child_returncode']) is int and receipt['child_returncode'] == 0 and
                 all(receipt[k] is True for k in ('final', 'new_session', 'child_reaped', 'group_gone')) and type(receipt['child_pid']) is int and
                 receipt['child_pid'] > 0 and receipt['owned_pgid'] == receipt['child_pid'] and command['transport_returncode'] == 0 and
                 command['transport_pid'] > 0 and not command.get('forced_transport_stop') and 'cleanup_error' not in receipt, 'actual host nonce/terminal/cleanup')
            for stream in ('stdout', 'stderr'):
                body = read(host/(name+'.'+stream+'.log')); need(sha(body) == command[stream+'_sha256'], 'actual host command stream')
                if name in ('compile', 'execute'): need(not body, 'clean strict compilation and sanitized execution')
        need(all(flag in hr['commands'][2]['child_argv'] for flag in ('-Werror', '-fno-fast-math', '-ffp-contract=off', '-fsanitize=address,undefined', '-fno-sanitize-recover=all')), 'actual sanitizer/floating compiler options')
        model = document(host/'cases.json'); inputs, output = read(host/'inputs.bin'), read(host/'outputs.bin')
        need(sha(read(host/'cases.json')) == hr['model_sha256'] and sha(inputs) == hr['input_sha256'] and sha(output) == hr['output_sha256'] and
             oracle.decode_input(inputs) == model and oracle.encode_input(model) == inputs, 'every original input/model/output byte')
        decoded = oracle.decode_output(output, model); repeated = oracle.compare_all(model, decoded['rows'])
        need(repeated == hr['numerical'] and repeated['measurement_completed'] is True and repeated['passed'] is hr['passed'] and
             repeated['cases'] == hr['cases'] == len(model['cases']) == 382 and
             decoded['metadata_controls'] == hr['metadata_controls'] == control.CONTROL_COUNT == 719,
             'all actual host exact values and setup/payload truncations replayed')
        report.update(host_exact_recomputed=True, host_cases=repeated['cases'], host_passed=repeated['passed'], host_metadata_controls=decoded['metadata_controls'],
            host_measurement={key: value for key, value in repeated.items() if key not in ('metrics', 'failures')})
        target = document(host/'target-cases/cases.json'); header = read(host/'target-cases/cases.h'); expected = document(host/'target-cases/expected.json')
        for name in ('cases.json', 'cases.h', 'expected.json'): need(sha(read(host/'target-cases'/name)) == hr['target_input_sha256'][name], 'predeclared target identity')
        need(len(target['cases']) == hr['target_cases'] == 200 and header.decode('ascii') == oracle.target_header(target) and
             expected == dict(schema='native-vorbis-codebook-expected-v1', policy=oracle.POLICY, cases=[oracle.expected_case(row) for row in target['cases']]), 'all original200 target inputs/header/expected outputs')
        by_id = {row['id']: row for row in model['cases']}; need(all(by_id[row['id']] == row for row in target['cases']), 'target subset of executed host inputs')
        rows = control.validate_cases(target, header.decode('ascii'))
        for architecture, directory in captured.items():
            native = document(directory/'report.json'); terminal(architecture, directory, 'run-vorbis-codebook-qemu.py', native['source_sha256'])
            need(native['target'] == architecture and native['result'] == 'CHECKED_CODEBOOK_CAPTURED' and
                 all(native[k] is True for k in ('completed', 'math_capture_completed', 'whole_module_compiled', 'source_inputs_unchanged')) and
                 all(native[k] is False for k in ('passed', 'numerical_reference_compared', 'numerical_qualified', 'full_floor0_qualified',
                     'decoder_executed', 'stream_decoder_executed', 'production_firmware', 'physical_device')), 'complete native exact capture with bounded scope')
            sources(directory, native['inputs'])
            for relative, digest in MODULE.items(): need(sha(read(directory/'sources/components/native_vorbis_numeric'/relative)) == digest, 'same frozen whole component')
            need(read(directory/'sources/controller.py') == read(control_path), 'same executed native capture controller')
            for name in ('cases.json', 'cases.h'): need(read(directory/'sources/cases'/name) == read(host/'target-cases'/name), 'same original native input data')
            need(set(native['source_sha256']) == set(control.PARTS)|{'cases', 'cases-header', 'qemu'} and
                 native['source_sha256']['cases'] == hr['target_input_sha256']['cases.json'] and native['source_sha256']['cases-header'] == sha(header), 'complete native source/data/tool pin inventory')
            for key, relative in control.PARTS.items(): need(native['source_sha256'][key] == MODULE[relative], 'native source argument identity')
            child = document(directory/'sdk-child.json')
            need(child == native['sdk_child'] and type(child['pid']) is int and child['pid'] > 0 and child['exit_status'] == 0, 'actual SDK child normal terminal')
            elf = read(directory/'elf-header.bin')
            need(len(elf) == 52 and sha(elf) == native['build_outputs']['elf-header.bin'] and elf[:6] == b'\x7fELF\x01\x01' and
                 struct.unpack_from('<H', elf, 18)[0] == native['elf_machine'] == (94 if architecture == 'esp32' else 243), 'actual ELF32 architecture header only')
            need([row['name'] for row in native['commands']] == ['sdk-head', 'sdk-clean', 'build', 'dependencies', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after'], 'all nine actual native commands')
            for command in native['commands']:
                need(command['state'] == 'complete' and type(command['exit_status']) is int and command['exit_status'] == 0 and
                     type(command['pid']) is int and command['pid'] > 0 and not command['timed_out'] and not command['interrupted'] and
                     Path(command['cwd']).resolve() == directory, 'owned native normal terminal')
                for stream in ('stdout', 'stderr'): need(sha(read(directory/(command['name']+'.'+stream+'.log'))) == command[stream+'_sha256'], 'actual native command stream')
            for name in ('sdk-head', 'sdk-head-after'): need(read(directory/(name+'.stdout.log')).decode().strip() == native['sdk_revision'] == control.SDK_HEAD[architecture], 'SDK before/after revision')
            for name in ('sdk-clean', 'sdk-clean-after'): need(not read(directory/(name+'.stdout.log')).strip(), 'SDK before/after clean')
            need(not native['build_warning_lines'], 'actual warning-free native compilation')
            log = read(directory/'qemu.stdout.log').decode('utf-8').replace('\r\n', '\n')+'\n'+read(directory/'qemu.stderr.log').decode('utf-8').replace('\r\n', '\n')
            observed = control.validate_log(log, rows, architecture, native['source_sha256']['cases'])
            need(observed.pop('rows') == native['rows'] and observed == native['observed'] and observed['cases'] == 200 and
                 observed['metadata_controls'] == hr['metadata_controls'], 'all actual ordered native events,values,cores and guards')
            result = oracle.compare_target_rows(target, expected, native['rows'])
            need(result['truncation_checks'] == result['payload_truncation_checks'] == 0, 'native did not repeat host per-cut campaigns')
            report['targets'][architecture] = result; save()
        need(all(sha(Path(origin).read_bytes()) == pin['sha256'] == sha((out/pin['snapshot']).read_bytes()) for origin, pin in report['inputs'].items()), 'all consumed original/frozen inputs unchanged')
        need(all(identity(Path(origin)) == pin['sha256'] for origin, pin in tuple(report['identity_only'].items())), 'identity-only executables unchanged')
        complete = repeated['measurement_completed'] and all(row['measurement_completed'] for row in report['targets'].values())
        passed = complete and repeated['passed'] and all(row['passed'] for row in report['targets'].values())
        report.update(completed=True, measurement_completed=complete, passed=passed, finite_codebook_qualified=passed,
            native_cases_required=sum(row['cases'] for row in report['targets'].values()), native_cases_compared=sum(len(row['metrics']) for row in report['targets'].values()),
            native_words_compared=sum(row['words'] for row in report['targets'].values()), native_decoded_entries_compared=sum(row['decoded'] for row in report['targets'].values()),
            native_affine_values_compared=sum(row['affine_values'] for row in report['targets'].values()),
            result='FINITE_CODEBOOK_QUALIFIED' if passed else 'FINITE_CODEBOOK_REJECTED')
        save(); print(json.dumps({key: report[key] for key in ('completed', 'passed', 'host_cases', 'host_exact_recomputed', 'native_cases_compared', 'result')}))
        return 0 if passed else 1
    except BaseException as error:
        report.update(completed=False, passed=False, error=repr(error)); save(); raise

if __name__ == '__main__': raise SystemExit(main())
