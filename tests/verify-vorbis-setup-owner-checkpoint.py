"""Read-only source, receipt and independent-oracle verification of owner evidence."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/vorbis-setup-owner-20261026'
ARCHIVE_SHA = '5b90e1a242036f1c86fbbec6f76dea52b4c6e4837a39941b779f051a9d7d28c6'
RUNNER_SHA = 'c4dd5c80cd61b6807a59908baf5dcee025814a7125cacf60b2b3a6e69521740d'
ORACLE_SHA = 'ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def module(path, name, digest):
    need(sha(path.read_bytes()) == digest, 'reviewed trusted local reader: ' + name)
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def verify():
    archive = FOLDER / 'captures.zip'
    need(sha(archive.read_bytes()) == ARCHIVE_SHA, 'unchanged complete archive')
    manifest = json.loads((FOLDER / 'manifest.json').read_bytes())
    need(manifest['schema'] == 'vorbis-setup-owner-evidence-v1' and
         manifest['archive_sha256'] == ARCHIVE_SHA, 'evidence schema and identity')
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        need(len(names) == len(set(names)) and set(names) == set(manifest['files']), 'complete unique member inventory')
        for name in names:
            path = PurePosixPath(name)
            need(name == path.as_posix() and not path.is_absolute() and '..' not in path.parts and
                 ':' not in name and '\\' not in name, 'canonical member path')
        bodies = {name: zipped.read(name) for name in names}
    for name, body in bodies.items():
        need(manifest['files'][name] == dict(bytes=len(body), sha256=sha(body)), 'exact member bytes: ' + name)
    read_json = lambda name: json.loads(bodies[name])
    subject = module(ROOT / 'tests/test-vorbis-setup-owner.py', 'trusted_local_owner_reader', RUNNER_SHA)
    oracle = module(ROOT / 'tests/test-vorbis-setup.py', 'trusted_local_setup_oracle', ORACLE_SHA)
    report = read_json('host02/report.json')
    need(report['completed'] and report['passed'] and report['host_all_prefixes'], 'complete host gate')
    need(sha(bodies['host02/sources/runner.py']) == RUNNER_SHA and
         sha(bodies['host02/sources/setup-oracle.py']) == ORACLE_SHA, 'executed reviewed readers')
    for key in ('native_target_executed', 'Xiph_executed', 'DSP_executed', 'audio_decoder_executed',
                'deferred_scopes_resumed', 'production_radio_integration'):
        need(report[key] is False, 'finite execution scope: ' + key)
    for pin in report['inputs'].values():
        need(sha(bodies['host02/' + pin['snapshot']]) == pin['sha256'], 'all executed source/input hashes')
    for name, body in bodies.items():
        prefix = 'host02/sources/components/'
        if name.startswith(prefix):
            current = ROOT / 'idf/components' / name.removeprefix(prefix)
            need(current.read_bytes() == body, 'current component equals executed component')
        prefix = 'host02/sources/native/'
        if name.startswith(prefix):
            need((ROOT / 'tests/native' / name.removeprefix(prefix)).read_bytes() == body, 'current fixture equals executed fixture')
    need(report['compiler_machine'].strip() == 'x86_64-linux-gnu', 'actual host architecture')
    commands = report['commands']
    need([row['name'] for row in commands] == ['compiler-version', 'compiler-machine'] +
         [f'compile-{index:02d}' for index in range(6)] + ['link', 'execute'], 'all ten owned commands')
    for row in commands:
        prefix = 'host02/' + row['name']
        request = read_json(prefix + '.request.json')
        receipt = read_json(prefix + '.receipt.json')
        need(receipt == row['supervisor'] and sha(bodies[prefix + '.request.json']) == row['request_sha256'], 'actual receipt/request binding')
        need(request['argv'] == row['child_argv'] and request['nonce'] == row['nonce'] == receipt['nonce'] and
             receipt['request_sha256'] == row['request_sha256'], 'owned process identity')
        need(row['transport_exit'] == 0 and not row.get('forced_transport_stop') and receipt['state'] == 'terminal' and
             receipt['final'] and receipt['child_returncode'] == 0 and receipt['child_reaped'] and receipt['group_gone'] and
             receipt['new_session'] and receipt['child_pid'] == receipt['owned_pgid'], 'terminal/reaped successful process')
        for stream in ('stdout', 'stderr'):
            need(sha(bodies[prefix + '.' + stream + '.log']) == row[stream + '_sha256'], 'raw diagnostic hash')
        if row['name'].startswith('compile-'):
            need(all(flag in row['child_argv'] for flag in ('-UNDEBUG', '-Wall', '-Wextra', '-Werror',
                 '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-fast-math', '-ffp-contract=off')),
                 'assertions, warnings and sanitizers active')
    need(not bodies['host02/execute.stderr.log'], 'no sanitizer diagnostics')
    # Only pinned repository modules execute; no archived code is imported.
    model = subject.cases(oracle, bodies['host02/sources/public-fixture.h'], bodies['host02/sources/original31.json'])
    need(model == read_json('host02/cases.json') and
         sha(bodies['host02/cases.json']) == report['model_sha256'], 'independent full corpus reconstruction')
    need(subject.target_header(model) == bodies['host02/owner_cases.h'] and
         sha(bodies['host02/owner_cases.h']) == report['generated_header_sha256'], 'every predeclared C oracle word and input byte')
    valid = [case for case in model['cases'] if case['status'] == 0]
    allocations = []
    for case in valid:
        fields = case['expected']
        word_count = fields[9] | (fields[10] << 32)
        quant_count = fields[11] | (fields[12] << 32)
        allocations.append(3 + bool(word_count) + bool(quant_count))
    expected = dict(cases=len(model['cases']), checks=19038727,
        successes=2 * len(model['cases']) + sum(1 + 3 * count for count in allocations),
        parse_failures=len(model['cases']) - len(valid) + sum(233 + case['setup_end_bit'] for case in valid),
        allocation_refusals=len(model['cases']) - len(valid) + 2 * sum(allocations))
    need(expected == report['totals'] == dict(cases=335, checks=19038727, successes=5378,
         parse_failures=399810, allocation_refusals=2982), 'complete original scope and derived operation counts')
    need(sum(case['original31'] for case in model['cases']) == 31 and len(valid) == 295,
         'all original31 pairs and all valid cases')
    need(bodies['host01/cases.json'] == bodies['host02/cases.json'] and
         read_json('host01/report.json')['totals'] == expected, 'earlier full host pass retained')
    need(read_json('validation/host.json')['returncode'] == 0 and
         read_json('validation/host-final.json')['returncode'] == 0, 'actual outer terminal results')
    for prefix, warning_count in (('lint01', 1), ('lint02', 0)):
        lint = read_json(prefix + '/report.json')
        need(lint['completed'] and len(lint['commands']) == 6 and lint['warnings'] == warning_count and lint['errors'] == 0,
             'both full Clang outcomes retained')
        for index, row in enumerate(lint['commands']):
            stem = prefix + '/' + f'{index:02d}-' + Path(row['source']).stem
            text = '\n'.join(bodies[stem + '.' + stream + '.log'].decode('utf-8', errors='replace') for stream in ('stdout', 'stderr'))
            need(len(re.findall(r': warning:', text)) == row['warnings'] and
                 len(re.findall(r': (?:error|fatal error):', text)) == row['errors'] and
                 row['returncode'] == 0 and not row.get('forced_stop'), 'unfiltered Clang diagnostics')
    stopped = read_json('observations/target-preparation.json')
    need(not stopped['controller_present'] and not stopped['protocol_tests_present'] and
         not stopped['target_campaign_present'] and not stopped['SDK_or_QEMU_started'] and
         not stopped['explicit_safety_rejection_reported'] and stopped['cause'] is None and
         stopped['controller_write_attempts'] == 2 and stopped['tool_response'] == 'aborted before dispatch' and
         stopped['full_native_gate_requires_all_prefix_sweeps'], 'target failure remains unqualified with unknown cause')
    need(len(stopped['prototype_files']) == 7 and all(sha(bodies['target-prototype/' + name]) == digest
         for name, digest in stopped['prototype_files'].items()), 'seven exact unrun prototype files')
    return dict(verified=True, cases=335, valid_cases=295, original31=31,
        successful_opens=expected['successes'], parse_failures=expected['parse_failures'],
        allocation_refusals=expected['allocation_refusals'], host_all_prefixes=True,
        native_target_executed=False, RANGE_dynamically_qualified=False,
        production_radio_integration=False)


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(verify()))
