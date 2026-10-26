"""Read-only VQ range evidence verification; no extraction, compiler or child process."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / 'tests/results/vorbis-xiph-vq-range-20261026'
ARCHIVE_SHA = '29a4fec2ed51dc87c78db94868847cb6c3a262ffb38c6487710c74cbe29c590b'
RUNNER_SHA = 'bdf65c89293e159a5b96cc01880d1e7d3fd57c174ac3772973c105ff3043ae5c'
FIXTURE_SHA = '5bebe07378688c15e670890a0c8271b6a2f1159999167d4460dd011e16380d61'
PORT_SHA = 'b9cc3c829a816ef8f1a283e23a5b9cc1a45214e9eee541e85560858ed70b0104'
BASE_SHA = '897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def verify():
    archive = CHECKPOINT / 'captures.zip'
    need(sha(archive.read_bytes()) == ARCHIVE_SHA, 'unchanged archive identity')
    manifest = json.loads((CHECKPOINT / 'manifest.json').read_bytes())
    need(manifest['schema'] == 'xiph-vq-range-evidence-v1' and manifest['archive_sha256'] == ARCHIVE_SHA,
         'matching evidence manifest')
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        need(len(names) == len(set(names)) and set(names) == set(manifest['files']), 'complete unique member inventory')
        for name in names:
            path = PurePosixPath(name)
            need(name == path.as_posix() and not path.is_absolute() and '..' not in path.parts and
                 ':' not in name and '\\' not in name, 'canonical contained member name')
        bodies = {name: zipped.read(name) for name in names}
    for name, body in bodies.items():
        need(manifest['files'][name] == dict(bytes=len(body), sha256=sha(body)), 'member hash and extent: ' + name)
    read_json = lambda name: json.loads(bodies[name])
    runner = ROOT / 'tests/test-vorbis-xiph-vq-range.py'
    need(sha(runner.read_bytes()) == RUNNER_SHA, 'reviewed local pure reader')
    need(sha((ROOT / 'tests/native/vorbis_xiph_vq_range_host.c').read_bytes()) == FIXTURE_SHA, 'reviewed local fixture')
    need(sha(bodies['host03/sources/runner.py']) == RUNNER_SHA and
         sha(bodies['host03/sources/native/vorbis_xiph_vq_range_host.c']) == FIXTURE_SHA,
         'executed final sources match reviewed local files')
    spec = importlib.util.spec_from_file_location('trusted_local_vq_range_reader', runner)
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    # The only executable reader is the pinned local source; archived code never imports.
    report = read_json('host03/report.json')
    need(report['completed'] is True and report['measurement_valid'] is True and
         report['xiph_full_vq_range_conformant'] is False and report['owned_quantization_exact'] is True,
         'measurement success preserves the decoder range gap')
    for key in ('physical_device', 'DSP_executed', 'audio_decoder_executed', 'target_executed',
                'deferred_scopes_resumed', 'production_radio_integration'):
        need(report[key] is False, 'finite execution scope: ' + key)
    for pin in report['inputs'].values():
        need(sha(bodies['host03/' + pin['snapshot']]) == pin['sha256'], 'all executed source snapshots')
    for folder, filename, digest in (('native_vorbis_xiph', 'component-manifest.json', BASE_SHA),
                                     ('native_vorbis_xiph_port', 'port-manifest.json', PORT_SHA)):
        prefix = 'host03/sources/components/' + folder + '/'
        need(sha(bodies[prefix + filename]) == digest, 'pinned component manifest')
        source = read_json(prefix + filename)
        inventory = {name[len(prefix):] for name in bodies if name.startswith(prefix)}
        need(inventory == set(source['files']) | {filename}, 'complete frozen component inventory')
        need(all(sha(bodies[prefix + name]) == pin for name, pin in source['files'].items()), 'component source hashes')
    for name, digest in report['porting']['files'].items():
        need(sha(bodies['host03/generated/' + name]) == digest, 'all generated source hashes')
    need(report['porting']['port_manifest_sha256'] == PORT_SHA and
         report['porting']['base_manifest_sha256'] == BASE_SHA, 'same qualified port and base')
    need(report['compiler_machine'].strip() == 'x86_64-linux-gnu', 'host target, not ESP32 execution')
    commands = report['commands']
    need([row['name'] for row in commands] == ['compiler-version', 'compiler-machine',
         'compile-library-00', 'compile-alloc', 'compile-quant', 'compile-capture', 'link', 'execute'],
         'all eight actual commands')
    for row in commands:
        prefix = 'host03/' + row['name']
        request = read_json(prefix + '.request.json')
        receipt = read_json(prefix + '.receipt.json')
        need(receipt == row['supervisor'] and sha(bodies[prefix + '.request.json']) == row['request_sha256'],
             'actual supervisor receipt and request binding')
        need(request['argv'] == row['child_argv'] and request['nonce'] == row['nonce'] == receipt['nonce'] and
             receipt['request_sha256'] == row['request_sha256'], 'owned child identity')
        need(row['transport_exit'] == 0 and not row.get('forced_transport_stop') and receipt['state'] == 'terminal' and
             receipt['final'] is True and receipt['child_returncode'] == 0 and receipt['child_reaped'] is True and
             receipt['group_gone'] is True and receipt['new_session'] is True and
             receipt['child_pid'] == receipt['owned_pgid'], 'successful terminal and reaped process')
        for stream in ('stdout', 'stderr'):
            need(sha(bodies[prefix + '.' + stream + '.log']) == row[stream + '_sha256'], 'raw command diagnostic hash')
        if row['name'].startswith('compile-'):
            need(all(flag in row['child_argv'] for flag in ('-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                 '-UNDEBUG', '-fno-fast-math', '-ffp-contract=off')), 'active sanitizers and numeric flags')
    need(not bodies['host03/execute.stderr.log'], 'no sanitizer diagnostics')
    model = read_json('host03/cases.json')
    need(model == subject.cases() and sha(bodies['host03/cases.json']) == report['cases_sha256'], 'original declared finite cases')
    need(bodies['host03/input.bin'] == subject.input_bytes(model) and
         sha(bodies['host03/input.bin']) == report['input_sha256'], 'exact actual input bytes')
    capture = bodies['host03/capture.bin']
    need(sha(capture) == report['capture_sha256'], 'actual whole capture identity')
    measured = subject.measure(model, capture)
    need(measured == read_json('host03/measurement.json') and
         sha(bodies['host03/measurement.json']) == report['measurement_sha256'], 'complete independent exact remeasurement')
    for key in ('scalars', 'books', 'values', 'scalar_mismatches', 'table_component_mismatches',
                'exactly_binary32_representable_scalar_mismatches', 'field_clamp_altered_components',
                'current_float_differs_from_exact_clamped_recurrence'):
        need(measured[key] == report[key], 'measured report field: ' + key)
    need((measured['scalars'], measured['books'], measured['values']) == (14336, 8225, 271626) and
         measured['exactly_binary32_representable_scalar_mismatches'] == 1682, 'retained corpus and visible representable gap')
    need(bodies['host02/capture.bin'] == capture and
         read_json('host02/report.json')['measurement_valid'] is True, 'earlier successful capture retained unchanged')
    failed = read_json('host01/report.json')
    need(failed['completed'] is False and failed['commands'][-1]['name'] == 'compile-capture' and
         failed['commands'][-1]['supervisor']['child_returncode'] == 1 and
         b'comparison is always true' in bodies['host01/compile-capture.stderr.log'] and
         'host01/execute.receipt.json' not in bodies, 'initial compile refusal remains a failure')
    need(read_json('validation/host.json')['returncode'] == 1 and
         read_json('validation/host-classified.json')['returncode'] == 0, 'outer command results retained')
    need(bodies['validation/oracle.stdout.log'].strip() == b'VQ_RANGE_ORACLE_PASS controls=14' and
         read_json('validation/oracle.json')['returncode'] == 0, 'rational rounding and cancellation controls')
    lint = read_json('lint/report.json')
    need(lint['completed'] and len(lint['commands']) == 3 and lint['warnings'] == 25 and lint['errors'] == 0,
         'three-unit Clang result, without suppression')
    for index, row in enumerate(lint['commands']):
        stem = f"lint/{index:02d}-" + Path(row['source']).stem
        diagnostics = '\n'.join(bodies[stem + '.' + stream + '.log'].decode('utf-8', errors='replace') for stream in ('stdout', 'stderr'))
        need(len(re.findall(r': warning:', diagnostics)) == row['warnings'] and
             len(re.findall(r': (?:error|fatal error):', diagnostics)) == row['errors'] and
             row['returncode'] == 0 and not row.get('forced_stop'), 'raw unfiltered lint outcome')
    # Negative reader controls preserve evidence rather than accepting a shorter capture.
    changed_scalar = bytearray(capture)
    changed_scalar[16] ^= 1
    changed_affine = bytearray(capture)
    changed_affine[24 + 8 * len(model['words']) + 4] ^= 1
    rejected = 0
    for mutation in (b'', b'WRONGMAG' + capture[8:], capture[:-1], capture + b'\0',
                     bytes(changed_scalar), bytes(changed_affine)):
        try:
            subject.measure(model, mutation)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('corrupted or partial capture accepted')
    return dict(verified=True, scalars=measured['scalars'], books=measured['books'],
                exact_affine_components=measured['exact_affine_components'],
                exactly_binary32_representable_scalar_mismatches=1682,
                xiph_full_vq_range_conformant=False, target_executed=False,
                decoder_implementation_changed=False, corruption_controls=rejected)


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(verify()))
