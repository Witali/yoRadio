"""Replay saved host/ESP32/C3 original-angle numbers; launch no compiler or SDK."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('host', 'esp32', 'esp32c3', 'receipts', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(), 'fresh task-local comparison output')
    out.mkdir(parents=True)
    (out/'inputs').mkdir()
    report = dict(completed=False, passed=False, measurement_completed=False,
                  host_numeric_recomputed=False, targets={}, inputs={},
                  SDK_or_QEMU_executed=False, component_executed=False,
                  full_floor0_qualified=False, full_G6_qualified=False,
                  PCM_qualified=False, physical_device=False)

    def save():
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')

    def read(path):
        path = path.resolve()
        body = path.read_bytes()
        digest = sha(body)
        previous = report['inputs'].get(str(path))
        need(previous is None or previous['sha256'] == digest, 'input changed between reads')
        destination = out/'inputs'/digest
        if not destination.exists():
            destination.write_bytes(body)
        else:
            need(destination.read_bytes() == body, 'content-addressed input collision')
        report['inputs'][str(path)] = dict(sha256=digest, bytes=len(body), snapshot='inputs/'+digest)
        return body

    def document(path):
        return json.loads(read(path))

    def terminal(name, directory, script, pins=None):
        receipt = document(args.receipts/(name+'.json'))
        need(receipt['status'] == 'TERMINAL' and type(receipt['returncode']) is int and
             receipt['returncode'] == 0 and type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0 and
             not any(key in receipt for key in ('error_type', 'returncode_after_stop')),
             'actual successful outer receipt '+name)
        cwd = Path(receipt['cwd']).resolve()
        argv = receipt['argv']
        need(cwd == ROOT and argv[1:4] == ['-B', '-X', 'utf8'] and
             Path(argv[0]).resolve() == Path(sys.executable).resolve() and
             (cwd/argv[4]).resolve() == ROOT/'tests'/script, 'actual command executable/script/cwd')
        runner = ROOT/'.build/cyd-vorbis-format-command-01.py'
        need(sha(read(runner)) == receipt['runner_sha256'] ==
             '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e' and
             receipt['executable_sha256'] == sha(Path(sys.executable).read_bytes()) ==
             '4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a',
             'recorded owned runner/executable identities')
        def option(key):
            need(argv.count('--'+key) == 1, 'one actual command option '+key)
            return argv[argv.index('--'+key)+1]
        need((cwd/option('output')).resolve() == directory, 'receipt belongs to supplied campaign')
        if name == 'host':
            need(len(argv) == 7 and argv[5] == '--output', 'exact host argv')
        else:
            need(option('target') == name and (cwd/option('cases')).resolve() == args.host.resolve()/'target-cases',
                 'actual native target and cases directory')
            for key, value in pins.items():
                need(option(key+'-sha256') == value, 'actual native source/data/tool pin '+key)
        need({Path(path).resolve() for path in receipt['logs']} ==
             {args.receipts.resolve()/(name+'.'+stream+'.log') for stream in ('stdout', 'stderr')},
             'exact owned outer stream inventory')
        for path, pin in receipt['logs'].items():
            body = read(Path(path))
            need(len(body) == pin['bytes'] and sha(body) == pin['sha256'], 'outer terminal stream '+name)

    def sources(directory, pins, snapshot_field):
        for origin, pin in pins.items():
            snapshot = (directory/pin[snapshot_field]).resolve()
            need(snapshot.is_relative_to(directory), 'contained frozen source')
            body = read(snapshot)
            need(sha(body) == pin['sha256'] == sha(read(Path(origin))), 'original/frozen source identity')

    save()
    try:
        read(Path(__file__))
        host = args.host.resolve()
        captured = {'esp32': args.esp32.resolve(), 'esp32c3': args.esp32c3.resolve()}
        terminal('host', host, 'test-vorbis-floor0-angles.py')
        hr = document(host/'report.json')
        need(hr['completed'] and hr['passed'] and hr['component_executed'], 'actual sanitized host run')
        sources(host, hr['sources'], 'snapshot')
        oracle_path = ROOT/'tests/test-vorbis-floor0-angles.py'
        need(sha(read(oracle_path)) == hr['sources'][str(oracle_path.resolve())]['sha256'],
             'same source oracle as actual host campaign')
        oracle = module(oracle_path, 'angle_oracle')
        control_path = ROOT/'tests/run-vorbis-floor0-angles-qemu.py'
        read(control_path)
        control = module(control_path, 'angle_capture')
        for command in hr['commands']:
            need(command['transport_returncode'] == 0 and command['supervisor']['child_returncode'] == 0 and
                 all(command['supervisor'][key] for key in ('final', 'new_session', 'child_reaped', 'group_gone')),
                 'owned host command completion')
            for stream in ('stdout', 'stderr'):
                need(sha(read(host/(command['name']+'.'+stream+'.log'))) == command[stream+'_sha256'],
                     'host command log')
        need([row['name'] for row in hr['commands']] == ['compiler-version', 'compiler-machine', 'compile', 'execute'],
             'complete actual host command inventory')
        inputs = read(host/'inputs.bin')
        model = document(host/'cases.json')
        need(sha(inputs) == hr['input_sha256'] and oracle.decode_input(inputs) == model, 'exact host inputs/model')
        output = read(host/'outputs.bin')
        need(sha(output) == hr['output_sha256'], 'actual output bytes')
        decoded = oracle.decode_output(output, model)
        repeated = oracle.compare_all(model, decoded['rows'])
        need(repeated == hr['numerical'] and decoded['metadata_controls'] == hr['metadata_controls'],
             'complete independent host numerical replay')
        report.update(host_numeric_recomputed=True, host_cases=repeated['cases'],
                      host_passed=repeated['passed'], host_metadata_controls=decoded['metadata_controls'])
        target = document(host/'target-cases/cases.json')
        header = read(host/'target-cases/cases.h')
        expected = document(host/'target-cases/expected.json')
        for name in ('cases.json', 'cases.h', 'expected.json'):
            need(sha(read(host/'target-cases'/name)) == hr['target_input_sha256'][name], 'target input pin')
        rows = control.validate_cases(target, header.decode('ascii'))
        for architecture, directory in captured.items():
            native = document(directory/'report.json')
            terminal(architecture, directory, 'run-vorbis-floor0-angles-qemu.py', native['source_sha256'])
            need(native['target'] == architecture and native['completed'] and native['math_capture_completed'] and
                 native['whole_module_compiled'] and not native['numerical_qualified'], 'actual structural native capture')
            sources(directory, native['inputs'], 'snapshot')
            need(native['source_sha256']['cases'] == sha(read(host/'target-cases/cases.json')) and
                 native['source_sha256']['cases-header'] == sha(header), 'same original native inputs')
            need(native['sdk_child']['exit_status'] == 0, 'normal SDK child completion')
            need(native['elf_machine'] == (94 if architecture == 'esp32' else 243), 'reported native architecture')
            elf = read(directory/'elf-header.bin')
            need(sha(elf) == native['build_outputs']['elf-header.bin'] and
                 elf[:4] == b'\x7fELF' and struct.unpack_from('<H', elf, 18)[0] == native['elf_machine'], 'saved ELF header')
            names = ['sdk-head', 'sdk-clean', 'build', 'dependencies', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after']
            need([row['name'] for row in native['commands']] == names, 'complete native command inventory')
            for command in native['commands']:
                need(command['state'] == 'complete' and command['exit_status'] == 0 and
                     not command['timed_out'] and not command['interrupted'], 'normal native terminal commands')
                for stream in ('stdout', 'stderr'):
                    need(sha(read(directory/(command['name']+'.'+stream+'.log'))) == command[stream+'_sha256'],
                         'native command log')
            log = read(directory/'qemu.stdout.log').decode('utf-8').replace('\r\n', '\n')
            log += '\n'+read(directory/'qemu.stderr.log').decode('utf-8').replace('\r\n', '\n')
            observed = control.validate_log(log, rows, architecture, native['source_sha256']['cases'])
            need(observed.pop('rows') == native['rows'] and observed == native['observed'], 'whole native event replay')
            result = oracle.compare_target_rows(target, expected, native['rows'])
            report['targets'][architecture] = result
            save()
        need(all(sha(Path(origin).read_bytes()) == pin['sha256'] == sha((out/pin['snapshot']).read_bytes())
                 for origin, pin in report['inputs'].items()), 'all consumed inputs unchanged')
        complete = repeated['measurement_completed'] and all(row['measurement_completed'] for row in report['targets'].values())
        passed = complete and repeated['passed'] and all(row['passed'] for row in report['targets'].values())
        report.update(completed=True, measurement_completed=complete, passed=passed,
                      native_cases_required=sum(row['cases'] for row in report['targets'].values()),
                      native_values_compared=sum(len(row['metrics']) for row in report['targets'].values()),
                      finite_original_angle_numeric_qualified=passed,
                      result='FINITE_ANGLES_NUMERIC_QUALIFIED' if passed else 'FINITE_ANGLES_NUMERIC_REJECTED')
        save()
        print(json.dumps({key: report[key] for key in ('completed', 'passed', 'host_cases', 'host_numeric_recomputed',
                                                      'native_values_compared', 'result')}))
        return 0 if passed else 1
    except BaseException as error:
        report.update(completed=False, passed=False, error=repr(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
