"""Read-only stdlib verifier. No subprocess, SDK, emulator or reference-codec calls."""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import ntpath
from pathlib import Path, PureWindowsPath
import re
import struct
import sys
import wave

sys.dont_write_bytecode = True
PREFIX = 'CYD_VORBIS_CHECKED_CORPUS_'
COMMANDS = ['sdk-head', 'sdk-clean', 'build', 'setup-macros', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after']
PANIC = r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|canary watchpoint|stack overflow'
FIXED = '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
OLD = 'd23fd5cb2ad7d8c3a87ebcda2197421245f571dea5724de3d328058264e491c2'
PROTOCOL = '547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e'
FORBIDDEN_PROFILE = r'^#define (LIMIT_TO_64kHz|CONFIG_FREERTOS_UNICORE)\b'
CONTROLS = {'packed': (6, 'sparse_explicit_d4_seq0', 'dd216d11f54d8cbe8419b04b74b1bcf8ae5be223834285624fa824a2defd5feb'),
            'wide': (8, 'sparse_explicit_d16_seq0', '5444e4f7c1dd6bfcf85e8ae53b8af4bb2e5b6a3fe165013a528db6b668fa2160'),
            'single': (12, 'single_explicit_d2_seq0', 'c81c799d00616a5aa5cc80b7d2f9854b42bd1fcb9b9902598fdf044eca2506cc')}


def need(ok, message):
    if not ok: raise RuntimeError(message)


def sha(data): return hashlib.sha256(data).hexdigest()
def norm(value): return str(value).replace('\\', '/')
def obj(data): return json.loads(data.decode('utf-8-sig'))


def verify(bundle):
    bundle = bundle.resolve()
    manifest = obj((bundle / 'manifest.json').read_bytes())
    need(manifest['schema'] == 'cyd-map2-checkpoint-v1', 'Unknown archive schema')
    files, raw, stored = manifest['files'], {}, {'manifest.json'}
    for original, row in files.items():
        need(not original.startswith('/') and '..' not in original.split('/'), 'Unsafe original key')
        need(type(row['raw_bytes']) is int and row['raw_bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', row['raw_sha256']), 'Invalid raw identity')
        if row['stored'] is None:
            need(row.get('omitted'), 'Undeclared omission')
            if 'actual_elf_header64_hex' in row:
                header = bytes.fromhex(row['actual_elf_header64_hex'])
                need(len(header) == 64 and header[:4] == b'\x7fELF' and struct.unpack_from('<H', header, 18)[0] == 94, 'Actual Xtensa ELF header')
            continue
        path = (bundle / row['stored']).resolve()
        need(path.is_relative_to(bundle) and row['stored'] not in stored, 'Unsafe/duplicate stored path')
        stored.add(row['stored'])
        blob = path.read_bytes()
        need(len(blob) == row['stored_bytes'] and sha(blob) == row['stored_sha256'], 'Stored bytes differ: ' + original)
        need(row['encoding'] in ('raw', 'gzip'), 'Unknown encoding')
        data = gzip.decompress(blob) if row['encoding'] == 'gzip' else blob
        need(len(data) == row['raw_bytes'] and sha(data) == row['raw_sha256'], 'Decoded bytes differ: ' + original)
        raw[original] = data
        if original.endswith(('.py', '.h')): need(row['encoding'] == 'raw', 'Source must remain uncompressed')
    for name, row in manifest['generated'].items():
        path = (bundle / name).resolve()
        need(path.is_relative_to(bundle) and name not in stored, 'Unsafe generated path')
        stored.add(name)
        need(len(path.read_bytes()) == row['bytes'] and sha(path.read_bytes()) == row['sha256'], 'Generated file changed')
    need((bundle / '.gitattributes').read_bytes() ==
         b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n', 'Raw Git byte policy missing')
    need({p.relative_to(bundle).as_posix() for p in bundle.rglob('*') if p.is_file()} == stored, 'Stored inventory differs')
    base = manifest['repository'].rstrip('/')

    def original(role, path):
        name = norm(path)
        aliases = manifest['aliases'].get(role, {})
        if name in aliases: return aliases[name]
        need(name.startswith(base + '/'), 'Original path outside archived repository: ' + name)
        return name[len(base) + 1:]

    def key(role, relative): return manifest['roles'][role]['root'] + '/' + norm(relative)
    def data(role, relative): return raw[key(role, relative)]
    def record(role, relative='report.json'): return obj(data(role, relative))
    def identity(role, relative): return files[key(role, relative)]['raw_sha256']
    reports = {role: record(role) for role in manifest['roles']}
    for name, item in manifest.get('unbuilt_history_artifacts', {}).items():
        role = item['role']
        report = reports[role]
        need(manifest['roles'][role]['kind'] == 'history' and name.startswith(key(role, 'build/')) and
             name.endswith(('.bin', '.elf')) and name not in files and report.get('completed') is False and
             any(c['name'] == 'build' and c['exit_status'] != 0 for c in report['commands']) and
             not any(c['name'] == 'qemu' for c in report['commands']), 'Invalid absent failed-build artifact')

    def receipt_check(value, code, role, report_hash=None):
        if isinstance(value, dict):
            need(role == 'baseline01' and value == dict(kind='direct_tool_observation', session_id=24179,
                 terminal_chunk_id='3b5497', exit_code=1), 'Unrecognized tool observation')
            return
        receipt = obj(raw[value])
        actual = receipt.get('exit_code', receipt.get('returncode'))
        need(type(actual) is int and actual == code, 'Wrong actual outer return code: ' + role)
        need(receipt.get('schema') == 'direct-exec-tool-terminal-v1' or receipt.get('status') == 'TERMINAL', 'Outer receipt not terminal')
        if report_hash is not None and 'report_sha256' in receipt:
            need(receipt['report_sha256'] == report_hash, 'Outer report hash mismatch')
        for path, row in receipt.get('logs', {}).items():
            need(files[original(role, path)]['raw_sha256'] == row['sha256'], 'Outer receipt log binding')
        if 'executable_sha256' in receipt:
            need(manifest['external_omitted'][norm(receipt['argv'][0])]['raw_sha256'] == receipt['executable_sha256'], 'Receipt tool omission binding')
        for field in ('runner_sha256', 'entrypoint_sha256'):
            if field in receipt: need(any(row['raw_sha256'] == receipt[field] for name, row in files.items() if name.endswith('.py')), 'Receipt source identity absent')

    for role, report in reports.items():
        kind = manifest['roles'][role]['kind']
        need(report.get('passed') is not True and report.get('full_G6_qualified') is not True and
             report.get('physical_device') is not True and report.get('production_radio_integration') is not True, 'Scope/acceptance inflated')
        need(report.get('numeric_reference_qualified') is not True and report.get('format_corpus_qualified') is not True,
             'Numerical/format NONPASS must remain explicit')
        code = 0 if role in ('capture17', 'capture25') else 1
        receipt_check(manifest['roles'][role]['terminal'], code, role, identity(role, 'report.json'))
        for name, row in report.get('inputs', {}).items():
            path = name if 'snapshot' in row else row['path']
            archived = original(role, path)
            need(files[archived]['raw_sha256'] == row['sha256'], 'Frozen input identity: ' + role)
            if 'bytes' in row: need(files[archived]['raw_bytes'] == row['bytes'], 'Frozen input size')
            if 'snapshot' in row: need(archived == key(role, row['snapshot']), 'Snapshot relocation mismatch')
        for field in ('variant_sources', 'build_outputs'):
            for path, digest in report.get(field, {}).items():
                need(identity(role, path) == digest, 'Report output/variant identity: ' + role + '/' + path)
        for path, digest in report.get('tools', {}).items():
            omitted = manifest['external_omitted'][norm(path)]
            need(omitted['raw_sha256'] == digest and omitted['raw_bytes'] > 0, 'Tool omission identity')
        for name, row in report.get('sdk_build_logs', {}).items():
            need(row.get('missing') is not True and identity(role, name) == row['sha256'] and
                 files[key(role, name)]['raw_bytes'] == row['bytes'], 'Actual SDK child log binding')
        commands = report.get('commands', [])
        if kind == 'target':
            expected = COMMANDS if role in ('capture17', 'capture25') else COMMANDS[:5 if role == 'baseline01' else 7]
            need([row['name'] for row in commands] == expected, 'Owned command inventory: ' + role)
        if kind in ('target', 'history'):
            if kind == 'history': need(report['result'] == 'NONPASS' and report['completed'] is False, 'Failed history mislabeled')
            for command in commands:
                need(command['state'] in ('complete', 'failed') and type(command['exit_status']) is int and
                     command['timed_out'] is False and command['interrupted'] is False, 'Incomplete owned command')
                if kind == 'target': need(command['state'] == 'complete' and command['exit_status'] == 0, 'Owned command not zero')
                for stream in ('stdout', 'stderr'):
                    need(identity(role, command['name'] + '.' + stream + '.log') == command[stream + '_sha256'], 'Owned log hash')
        if kind == 'target':
            for filename in ('build/compile_commands.json', 'build/build.ninja', 'build/CMakeCache.txt', 'sdkconfig'):
                need(key(role, filename) in raw, 'Actual build context missing')
            need(any(k.startswith(key(role, 'build/')) and k.endswith('.map') for k in raw), 'Actual link map missing')
            need(any(k.startswith(key(role, 'build/')) and 'actual_elf_header64_hex' in row for k, row in files.items()), 'Actual ELF64 evidence missing')
            context = report['setup_macro_context']
            need(context['row'] in record(role, 'build/compile_commands.json'), 'Actual setup macro compile row missing')
            generated = context['generated_inputs']
            need(len(generated) == 2, 'Expected exact cflags/specs bindings')
            for path, item in generated.items():
                need(item['sha256_before'] == item['sha256_after'] == files[original(role, path)]['raw_sha256'], 'Macro input changed')
            flags = next(path for path in generated if norm(path).endswith('/toolchain/cflags'))
            specs = next(path for path in generated if norm(path).endswith('/specs/picolibc.specs'))
            need(raw[original(role, flags)].decode().splitlines() == ['-Wno-frame-address', '-mlongcalls',
                 '-fno-builtin-memcpy', '-fno-builtin-memset', '-fno-builtin-bzero', '"-specs=' + norm(specs) + '"'], 'Wrong exact response content')
            argv = context['original_argv']
            need(argv.count('-c') == argv.count('-o') == 1 and [norm(a[1:]) for a in argv if a.startswith('@')] == [norm(flags)], 'Wrong preserved response/outer argv')
            stripped, skip = [], False
            for arg in argv:
                if skip: skip = False; continue
                if arg == '-o': skip = True; continue
                if arg != '-c': stripped.append(arg)
            need(context['probe_argv'] == stripped + ['-E', '-dM'], 'Macro probe changed original context')
            macros = data(role, 'setup-macros.stdout.log').decode(errors='replace').replace('\r\n', '\n')
            for macro in ('CONFIG_IDF_TARGET_ESP32', 'CONFIG_YORADIO_VORBIS_REPAIR'):
                need(re.search('^#define ' + macro + ' 1$', macros, re.M), 'Wrong actual setup target/repair context')
            need(re.search('^#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 240$', macros, re.M) and
                 not re.search(FORBIDDEN_PROFILE, macros, re.M), 'Wrong actual setup profile')
            need(data(role, 'sdk-head.stdout.log').strip() == b'7101770dc6db2667b3c477cc31365dd1acd6db4e' and
                 not data(role, 'sdk-clean.stdout.log').strip(), 'Actual SDK identity/cleanliness')

    def events(role):
        log = (data(role, 'qemu.stdout.log') + b'\n' + data(role, 'qemu.stderr.log')).decode(errors='replace')
        return log, [line for line in log.splitlines() if line.startswith(PREFIX)]

    def protocol(role):
        need(identity(role, 'sources/helpers/protocol.py') == PROTOCOL, 'Unreviewed frozen strict protocol')
        module_path = bundle / files[key(role, 'sources/helpers/protocol.py')]['stored']
        spec = importlib.util.spec_from_file_location('archived_protocol_' + role, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # Frozen stdlib-only protocol; never imports the SDK controller.
        class ArchivedOriginalPath(PureWindowsPath):
            def resolve(self): return type(self)(ntpath.normpath(str(self)))
            def read_bytes(self): return raw[original(role, self.resolve())]
        module.Path = ArchivedOriginalPath  # Relocate data reads only; preserve original path strings/contract identities.
        contract = record(role, 'sources/corpus/contract.json')
        log, _ = events(role)
        qemu = next(row for row in reports[role]['commands'] if row['name'] == 'qemu')
        observed = module.validate_log(log, contract, returncode=qemu['exit_status'], timed_out=qemu['timed_out'],
            interrupted=qemu['interrupted'], manifest_hashes=contract['model']['manifest_sha256'])
        captured = observed.pop('case_pcm')
        need(observed == reports[role]['observed'], 'Strict observed protocol/report mismatch')
        rows = reports[role]['observed_pcm']
        need(len(rows) == len(captured) == len(contract['model']['cases']), 'Missing actual PCM cases')
        for item, row in zip(captured, rows):
            need(item['case'] == row['case'] and item['id'] == row['id'] and item['sha256'] == row['sha256'] and
                 item['packet_offsets'] == row['packet_offsets'] and item['pcm'] == data(role, row['path']), 'Actual PCM persistence binding')
        need({key(role, row['path']) for row in rows} == {k for k in raw if k.startswith(key(role, 'observed-pcm/'))}, 'Actual PCM file set')
        return contract, captured

    captures = {}
    for role, shape in (('capture17', (17, 238, 398080)), ('capture25', (25, 350, 623360))):
        report = reports[role]
        need(report['completed'] is True and report['target_capture_completed'] is True and
             report['checked_decode_completed'] is True and report['numeric_reference_qualified'] is False and
             report['vendor_comparison_available'] is False and report['vendor_checked_pcm_equal'] is False, 'Capture scope mislabeled')
        contract, pcm = protocol(role)
        model = contract['model']
        need((len(model['cases']), model['total_packets'], model['total_pcm']) == shape, 'Full capture shape')
        need((identity(role, 'sources/corpus/contract.json'), contract['contract_sha256']) ==
             (('6c95b8d52a7bd5a3ca8e2d1b519f5d0ec3172e7e76e83ade8c1e78d364fdd391', '847022a7835de03c0f820b3f8e418e7e8b89b6125d2dba8bdf09712d33d3a65a')
              if role == 'capture17' else ('717ec7f703295f9851fd9241877cf249ff6f203c436786300a36247f2805218d', '660ac01523d3336ccb103f1443e51b870edf1a3d3f50321c5666969b1da634cc')), 'Reviewed exact contract identity')
        need(identity(role, 'variant/vorbis_repair/setup.c') == FIXED, 'Wrong fixed setup')
        if role == 'capture25':
            need(re.search(rb'^#define CORPUS_CASE_COUNT 25U\s*$', data(role, 'sources/project/main/data.h'), re.M),
                 'Actual25 materialized header must declare25')
            need(sha(data(role, 'sources/project/main/data.h')) ==
                 '97b1a62287dc048603eaaed239cf294a19a4c887ecc97d2fe2d887e7d8b8b6dc', 'Unreviewed corrected25 data bytes')
        captures[role] = contract, pcm
    need(identity('baseline02', 'variant/vorbis_repair/setup.c') == OLD, 'Historical baseline source changed')
    for role in ('vendor', 'baseline01', 'baseline02', 'packed', 'wide', 'single'):
        need(reports[role]['result'] == 'NONPASS' and reports[role]['completed'] is False and
             reports[role]['target_capture_completed'] is False, 'Historical/control NONPASS lost')
    need('Missing symbol esp_vorbis_dec_open' in reports['baseline01']['error'] and
         key('baseline01', 'qemu.stdout.log') not in raw, 'Obsolete symbol-gate history lost')
    vendor_log = data('vendor', 'qemu.stdout.log').decode(errors='replace')
    vendor_cases = [line for line in vendor_log.splitlines() if line.startswith('CYD_VORBIS_CORPUS_CASE ')]
    need(re.search(PANIC, vendor_log, re.I) and len(vendor_cases) == 6 and
         all(f'case={index} id={captures["capture17"][0]["model"]["cases"][index]["id"]} ' in line
             for index, line in enumerate(vendor_cases)) and
         len([line for line in vendor_log.splitlines() if line.startswith('CYD_VORBIS_CORPUS_PAIR ')]) == 84,
         'Original vendor six-case prefix and panic evidence lost')
    need(any('capture-01-backtrace' in name and name.endswith('stdout.log') and b'esp_vorbis_dec_open' in blob
             for name, blob in raw.items()), 'Actual public-open address-resolution evidence missing')

    def negative(role, fixed_role, index, case_id):
        log, got = events(role)
        _, accepted = events(fixed_role)
        begin = next(i for i, line in enumerate(accepted) if line.startswith(PREFIX + 'OPEN case=' + str(index) + ' '))
        need(not re.search(PANIC, log, re.I) and got[:begin] == accepted[:begin], 'Wrong/early/panicking negative prefix: ' + role)
        need(got[begin:] == [f'{PREFIX}OPEN case={index} id={case_id} checked_rc=-1 checked_handle=0 core=1',
             f'{PREFIX}FAILURE case={index} packet=0 reason=checked_public_open core=1'], 'Exact named open failure required: ' + role)
        need(data(role, 'sources/corpus/contract.json') == data(fixed_role, 'sources/corpus/contract.json'), 'Control contract differs')
    negative('baseline02', 'capture17', 6, 'sparse_explicit_d4_seq0')
    for role, (index, name, digest) in CONTROLS.items():
        need(identity(role, 'variant/vorbis_repair/setup.c') == digest, 'Wrong one-change control source')
        fixed_role = 'capture17' if role == 'packed' else 'capture25'
        negative(role, fixed_role, index, name)
        variants = [{name[len(key(r, 'variant/')):]: row['raw_sha256'] for name, row in files.items()
                     if name.startswith(key(r, 'variant/'))} for r in (role, fixed_role)]
        need(set(variants[0]) == set(variants[1]) and all(variants[0][name] == variants[1][name]
             for name in variants[0] if name != 'vorbis_repair/setup.c'), 'Unrelated control variant source changed')

    hosts = {}
    for role, count in (('host-old17', 17), ('host-new8', 8)):
        host = reports[role]
        need(host['completed'] is True and host['xiph_reference_qualified'] is True and
             host['dual_reference_qualified'] is False and len(host['cases']) == count and
             len(host['failures']) == (10 if count == 17 else 8), 'Original scoped Xiph proof')
        item = manifest['plan']['hosts']['old17' if count == 17 else 'new8']
        qualified = obj(raw[norm(item['qualification'])])
        need(qualified['completed'] is True and qualified['reference_corpus_qualified'] is True and
             qualified['original_dual_reference_passed'] is False and
             qualified['original_report_sha256'] == identity(role, 'report.json') and len(qualified['cases']) == count,
             'Original qualification/report linkage')
        need((qualified['xiph_cases'], qualified['native_compared'], qualified['native_lookup2_refusals']) ==
             ((17, 7, 10) if count == 17 else (8, 0, 8)), 'Historical reference scope altered')
        need(qualified['original_outer_receipt_sha256'] == files[manifest['roles'][role]['terminal']]['raw_sha256'],
             'Original host receipt/qualification linkage')
        for command in host['commands']:
            need(identity(role, command['receipt']) == command['sha256'], 'Reference command receipt hash')
            receipt_check(key(role, command['receipt']), obj(data(role, command['receipt']))['returncode'], role)
        for case in host['cases']:
            receipt = obj(data(role, f"cases/{case['id']}/decode-libvorbis.json"))
            need(receipt['returncode'] == 0, 'Xiph reference command not zero')
            native = obj(data(role, f"cases/{case['id']}/decode-vorbis.json"))
            need((native['returncode'] == 0) == ('vorbis' in case['decoded']), 'Native reference outcome/refusal changed')
            declared = next(row for row in qualified['cases'] if row['id'] == case['id'])
            need(declared['xiph_qualified'] is True and declared['pcm_sha256'] == case['decoded']['libvorbis']['pcm_sha256'],
                 'Qualified reference PCM differs')
        hosts[role] = {row['id']: row for row in host['cases']}

    def numeric(role, target):
        measured = reports[role]
        need(measured['measurement_completed'] is True and measured['actual_reference_compared'] is True and
             measured['passed'] is False and measured['bounded_corpus_pcm_qualified'] is False and
             measured['result'] == 'BOUNDED_CORPUS_PCM_REJECTED', 'Measured numerical NONPASS lost')
        policy = measured['policy']
        need(policy['max_abs_error'] == 2 and policy['selected_before_target_measurement'] is True and
             policy['threshold_fitted_to_output'] is False, 'Predeclared fixed comparison policy')
        contract, captured = captures[target]
        bindings = record(target, 'sources/reference/reference-binding02.json')['cases'] if target == 'capture25' else None
        need(len(measured['cases']) == len(captured), 'Numerical case count')
        maxima, target_by_id, reference_by_id = [], {}, {}
        for index, (case, pcm, result) in enumerate(zip(contract['model']['cases'], captured, measured['cases'])):
            bound = bindings[index] if bindings else None
            host_role = 'host-new8' if bound and bound['original_group'] == 'newbooks8' else 'host-old17'
            reference_id = bound['original_reference_id'] if bound else f"{case['source_index']}-{case['id']}"
            hostcase = hosts[host_role][reference_id]
            wav_bytes = data(host_role, f'cases/{reference_id}/libvorbis.wav')
            declared = hostcase['decoded']['libvorbis']
            need(sha(wav_bytes) == declared['wav_sha256'], 'Reference WAV hash')
            with wave.open(io.BytesIO(wav_bytes), 'rb') as wav:
                need((wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes()) ==
                     (2, 2, case['rate'], sum(case['frames'])), 'Actual WAV format/count')
                reference = wav.readframes(wav.getnframes())
            need(sha(reference) == declared['pcm_sha256'] and len(reference) == len(pcm['pcm']) == case['total_pcm'], 'Reference/actual PCM sizes')
            need(declared['frames'] == case['frames'][1:], 'Independent per-packet frame counts')
            for kind in ('identification', 'setup', 'audio'):
                path = PureWindowsPath(hostcase['source_matrix']).parent / hostcase['input'][kind]
                need(sha(raw[original(host_role, path)]) == case['raw_sha256'][kind], 'Reference raw payload binding')
            if bound:
                need(bound['id'] == case['id'] and bound['raw_sha256'] == case['raw_sha256'] and
                     bound['reference_pcm_sha256'] == sha(reference) and bound['reference_wav_sha256'] == sha(wav_bytes), 'Expanded original/reference binding')
            pairs = list(zip(struct.iter_unpack('<h', pcm['pcm']), struct.iter_unpack('<h', reference)))
            errors = [a[0] - b[0] for a, b in pairs]
            maximum = max(map(abs, errors), default=0)
            stats = result['comparison']['zero_lag_direct_LR']
            need(result['case'] == index and result['id'] == case['id'] and stats['max_abs_error'] == maximum and
                 stats['different_samples'] == sum(e != 0 for e in errors) and
                 stats['sum_squared_error'] == sum(e * e for e in errors), 'Independent signed-S16 comparison differs')
            need(result['packet_offsets'] == pcm['packet_offsets'] and result['rate'] == case['rate'] and
                 result['channels'] == 2 and result['bits'] == 16, 'Numerical packet/metadata binding')
            maxima.append((case['id'], maximum))
            target_by_id[case['id']], reference_by_id[case['id']] = pcm['pcm'], reference
        for kind, values in (('target', target_by_id), ('xiph', reference_by_id)):
            need(len(measured['metamorphic_relations'][kind]) == (8 if target == 'capture25' else 4), 'Complete relation inventory')
            for relation in measured['metamorphic_relations'][kind]:
                blobs = [values[name] for name in relation['cases']]
                equal = all(blob == blobs[0] for blob in blobs[1:])
                need(relation['kind'] in ('equal', 'different') and relation['observed_byte_equal'] is equal and
                     relation['expected_relation_observed'] is (equal if relation['kind'] == 'equal' else not equal),
                     'Actual same-decoder relation result differs')
        if target == 'capture25':
            subgroup = measured['declared_subgroup_books16']
            need(subgroup['case_indices'] == list(range(16)) and subgroup['does_not_override_full25'] is True and
                 subgroup['policy']['max_abs_error'] == 2 and subgroup['policy']['threshold_fitted_to_output'] is False and
                 subgroup['policy']['max_abs_error_within_bound'] is all(value <= 2 for _, value in maxima[:16]),
                 'Actual declared books16 bound/result differs')
        failures = {name for name, maximum in maxima if maximum > 2}
        expected_floor0 = {case['id'] for case in contract['model']['cases'] if case['id'].startswith('floor0-')}
        need(len(expected_floor0) == 6 and expected_floor0 <= failures, 'Six floor0 numerical NONPASS cases lost')
        return maxima
    need(reports['numeric-attempt01']['measurement_completed'] is False and
         reports['numeric-attempt01']['error'] == 'Reference framemd5 metadata mismatch', 'Original numerical parser NONPASS lost')
    numeric('numeric-attempt02', 'capture17')
    maxima25 = numeric('numeric-expanded25', 'capture25')
    return dict(verified=True, capture25_cases=25, packets=350, pcm_bytes=623360,
                books16_within_predeclared_bound=all(value <= 2 for _, value in maxima25[:16]),
                numerical_nonpass_preserved=True, max_abs_errors=dict(maxima25),
                format_conformance_qualified=False, full_G6_qualified=False, physical_device=False, production_firmware=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    print(json.dumps(verify(parser.parse_args().bundle), indent=2))
