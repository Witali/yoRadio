"""Read-only stdlib verifier for the focused CYD uint32-rate evidence archive."""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import struct
import sys

sys.dont_write_bytecode = True
NAMES = ('baseline', 'acceptance', 'limited', 'validity-control', 'policy-control')
MODES = ('baseline', 'acceptance', 'limited', 'acceptance', 'limited')
CONTROLS = (None, None, None, 'signed-validity', 'signed-policy')
COUNTS = ((14, 2, 952, 3816960, 988), (16, 0, 1088, 4362240, 1124),
          (11, 5, 748, 2999040, 784), (14, 0, 952, 3816960, 985), (11, 3, 748, 2999040, 781))
BEFORE = 'b7e1999c349f9353a5690eaf5b05a0387db1bcad365d7f079c4a6c52ae493156'
AFTER = 'd23fd5cb2ad7d8c3a87ebcda2197421245f571dea5724de3d328058264e491c2'
PROTOCOL = '53a9c81ae3293e99c0ea0fe9ef48b62ee2b78fde184fd080151b83f34dc9da79'
CALLER = '3d97389d3e8befd2ebf6642172cbe9f285d12954aed0b0bd8168d832ba3d7483'
TESTS = 'bf9aee429042a512439f1fdf2ab5594e7e3812ff45bb52fdda8cc1c3c7f61ad8'
FIXTURE = '839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378'
SDK = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
ARCHIVES = {'libesp_audio_codec.a': '92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58',
            'libesp_audio_simple_dec.a': 'ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6'}
COMMANDS = ('sdk-head', 'sdk-clean', 'build', 'setup-macros', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after')
SIGNED = (b'  if(vi->rate<1)goto err_out;', b'  if(vi->rate>=64000 || ci->blocksizes[1]>4096)goto err_out;')
UNSIGNED = (b'  if((uint32_t)vi->rate<1)goto err_out;', b'  if((uint32_t)vi->rate>=64000 || ci->blocksizes[1]>4096)goto err_out;')


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def norm(path):
    return str(path).replace('\\', '/')


def safe_relative(value):
    path = PurePosixPath(norm(value))
    need(value and not path.is_absolute() and '..' not in path.parts and ':' not in str(path), 'Unsafe archive path')
    return path.as_posix()


def historical_relative(value, root):
    path = PureWindowsPath(value).relative_to(PureWindowsPath(root))
    return safe_relative(path.as_posix())


def windows_args(command):
    """Pure Windows backslash/quote parsing for these direct recorded GCC rows."""
    out, i = [], 0
    while i < len(command):
        while i < len(command) and command[i] in ' \t':
            i += 1
        if i == len(command):
            break
        word, quoted = '', False
        while i < len(command) and (quoted or command[i] not in ' \t'):
            count = 0
            while i < len(command) and command[i] == '\\':
                count += 1
                i += 1
            if i < len(command) and command[i] == '"':
                word += '\\' * (count // 2)
                if count % 2:
                    word += '"'
                elif quoted and i + 1 < len(command) and command[i + 1] == '"':
                    word += '"'
                    i += 1
                else:
                    quoted = not quoted
                i += 1
            else:
                word += '\\' * count
                if i < len(command) and (quoted or command[i] not in ' \t'):
                    word += command[i]
                    i += 1
        need(not quoted, 'Unclosed compile command quote')
        out.append(word)
    return out


def fixed_source(before):
    need(before.count(b'#ifdef LIMIT_TO_64kHz\n') == 1, 'Exact source policy marker')
    after = before.replace(b'#ifdef LIMIT_TO_64kHz\n',
        b'/* Vorbis rate is unsigned; retain the fixed vendor ABI field layout. */\n#ifdef LIMIT_TO_64kHz\n', 1)
    for old, new in zip(SIGNED, UNSIGNED):
        need(after.count(old) == 1 and after.count(new) == 0, 'Exact original signed guards')
        after = after.replace(old, new, 1)
    return after


def command_facts(row):
    need(row.get('state') == 'complete' and type(row.get('exit_status')) is int and row['exit_status'] == 0 and
         row.get('timed_out') is False and row.get('interrupted') is False and
         type(row.get('pid')) is int and row['pid'] > 0 and row.get('argv') and row.get('cwd'), 'Invalid actual command facts')


def verify(root):
    root = Path(root).resolve()
    manifest = json.loads((root / 'manifest.json').read_bytes())
    need(manifest.get('schema') == 'cyd-public-uint32-rate-archive-v1', 'Archive schema')
    need(all(manifest.get(k) is False for k in ('full_G6_qualified', 'production_radio_integration',
         'physical_device', 'omitted_bytes_replayable', 'object_cache_included')), 'Archive scope overclaim')
    files, omitted = manifest['files'], manifest['omitted']
    stored = set()
    for key, row in files.items():
        safe_relative(key)
        rel = safe_relative(row['stored'])
        need(rel not in stored, 'Duplicate stored path')
        stored.add(rel)
        path = root / rel
        need(path.is_file() and not path.is_symlink(), 'Missing/symlink stored evidence')
        encoded = path.read_bytes()
        need(len(encoded) == row['stored_bytes'] and sha(encoded) == row['stored_sha256'], 'Stored bytes changed: ' + key)
        need(row['encoding'] in ('raw', 'gzip'), 'Unknown encoding')
        data = gzip.decompress(encoded) if row['encoding'] == 'gzip' else encoded
        need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'Raw bytes changed: ' + key)
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    need(not any(p.is_symlink() for p in root.rglob('*')) and actual == stored | {'manifest.json'}, 'Exact stored file set differs')
    need(not set(files) & set(omitted), 'Stored/omitted conflict')
    for key, row in omitted.items():
        safe_relative(key)
        need(type(row['bytes']) is int and row['bytes'] > 0 and re.fullmatch('[0-9a-f]{64}', row['sha256']) and
             row.get('reason') and PurePosixPath(key).suffix not in ('.o', '.obj', '.pyc'), 'Invalid binary omission')
        if key.endswith('.elf'):
            header = bytes.fromhex(row['elf_header_hex'])
            need(len(header) == 64 and header[:6] == b'\x7fELF\x01\x01' and
                 struct.unpack_from('<H', header, 18)[0] == row['elf_machine'] == 94, 'Captured actual ELF header machine')

    def read(key):
        row = files[key]
        data = (root / row['stored']).read_bytes()
        return gzip.decompress(data) if row['encoding'] == 'gzip' else data

    def load(key):
        return json.loads(read(key))

    def identity(key, digest):
        row = files.get(key, omitted.get(key))
        need(row is not None and row['sha256'] == digest, 'Missing/wrong role identity: ' + key)

    before, after = read('extras/source-change/before.c'), read('extras/source-change/after.c')
    need(sha(before) == BEFORE and sha(after) == AFTER and fixed_source(before) == after, 'Fix is not comment plus two exact casts')
    relation = load('extras/source-change/relation.json')
    need(relation['before_sha256'] == BEFORE and relation['after_sha256'] == AFTER and
         relation['ABI_type_layout_changed'] is False and relation['newline_preserved'] is True, 'Source relation metadata')
    need(set(manifest['campaigns']) == set(NAMES), 'All five exact campaign roles required')
    observations = {}
    common_candidate = None
    for name, mode, control, counts in zip(NAMES, MODES, CONTROLS, COUNTS):
        prefix = 'campaigns/' + name + '/'
        meta = manifest['campaigns'][name]
        need(meta['report'] == prefix + 'report.json' and meta['terminal'] == prefix + 'direct-tool-terminal.json', 'Cross-role report path')
        report = load(meta['report'])
        need(report.get('completed') is True and report.get('passed') is True and
             report['mode'] == mode and report['control'] == control, 'Campaign role/outcome')
        expected_flags = dict(rate_acceptance_qualified=name == 'acceptance', limited_policy_qualified=name == 'limited',
            regression_reproduced=name == 'baseline', control_effective=control is not None,
            full_G6_qualified=False, production_radio_integration=False, physical_device=False)
        need(all(report.get(k) is value for k, value in expected_flags.items()), 'Baseline/control qualification conflated')
        need(report['result'] == ('CONTROL_EFFECTIVE' if control else
             {'baseline': 'REGRESSION_REPRODUCED', 'acceptance': 'UINT32_RATE_ACCEPTED', 'limited': 'LIMITED_POLICY_VERIFIED'}[mode]), 'Result classification')
        need(meta['inputs'] == report['inputs'], 'Campaign input bindings changed')
        for original, row in report['inputs'].items():
            identity(prefix + safe_relative(row['snapshot']), row['sha256'])
        terminal = load(meta['terminal'])
        need(terminal.get('schema') == 'direct-exec-tool-terminal-v1' and terminal.get('status') == 'TERMINAL' and
             type(terminal.get('exit_code')) is int and terminal['exit_code'] == 0 and
             type(terminal.get('session_id')) is int and terminal['session_id'] > 0 and terminal.get('chunk_id') and
             terminal.get('cwd') and terminal.get('scope') and terminal['report_sha256'] == sha(read(meta['report'])) and
             terminal['original_entrypoint_sha256'] == sha(read(prefix + 'sources/helpers/run.py')), 'Actual outer tool terminal binding')
        commands = report['commands']
        need(tuple(c['name'] for c in commands) == COMMANDS, 'Exact nine actual command receipts')
        for row in commands:
            command_facts(row)
            for stream in ('stdout', 'stderr'):
                identity(prefix + row['name'] + '.' + stream + '.log', row[stream + '_sha256'])
        for role, expected in (('sdk-head', SDK), ('sdk-head-after', SDK), ('sdk-clean', ''), ('sdk-clean-after', '')):
            need(read(prefix + role + '.stdout.log').decode().strip() == expected, 'SDK revision/clean evidence')
        for rel, row in report['sdk_build_logs'].items():
            identity(prefix + rel, row['sha256'])
            need(len(read(prefix + rel)) == row['bytes'], 'SDK child log size')
        for rel, digest in report['build_outputs'].items():
            identity(prefix + safe_relative(rel), digest)
        need(prefix + 'build/cyd_vorbis_uint32_rate.elf' in omitted, 'Explicit omitted ELF identity required')
        for rel, digest in report['variant_sources'].items():
            identity(prefix + safe_relative(rel), digest)
        candidate = read(prefix + 'sources/candidate/vorbis_repair/setup.c')
        need(candidate == (before if name == 'baseline' else after), 'Wrong source version for campaign')
        selected = candidate
        if control:
            index = 0 if control == 'signed-validity' else 1
            selected = candidate.replace(UNSIGNED[index], SIGNED[index], 1)
            need(selected != candidate and selected.replace(SIGNED[index], UNSIGNED[index], 1) == candidate, 'Control changed more than named guard')
        need(read(prefix + 'variant/vorbis_repair/setup.c') == selected, 'Actual selected control source')
        guard = report['guard_variant']
        need(guard == dict(original_sha256=sha(candidate), selected_sha256=sha(selected),
             control=control, changed=control is not None), 'Guard variant metadata')
        candidate_rest = {key: read(prefix + 'sources/candidate/' + key) for key in
            ('vorbis_repair/output.c', 'vorbis_repair_abi.h', 'vorbis_repair/COPYING', 'compat/vorbis_repair/enable.cmake')}
        if common_candidate is None:
            common_candidate = candidate_rest
        need(candidate_rest == common_candidate, 'Unrelated source/ABI changes between campaigns')
        identity(prefix + 'sources/project/main/main.c', CALLER)
        identity(prefix + 'sources/project/main/fixture.h', FIXTURE)
        identity(prefix + 'sources/canonical-fixture.h', FIXTURE)
        identity(prefix + 'sources/helpers/rate_protocol.py', PROTOCOL)
        identity(prefix + 'sources/helpers/rate_protocol.py', sha(read('extras/caller-prep/rate_protocol.py')))
        rows = load(prefix + 'build/compile_commands.json')
        context = report['setup_macro_context']
        need(sum(row == context['row'] for row in rows) == 1, 'Actual setup compile row absent/ambiguous')
        setup_rel = historical_relative(context['row']['file'], meta['origin'])
        need(setup_rel == 'variant/vorbis_repair/setup.c', 'Actual compiled setup source')
        selected_rows = [historical_relative(row['file'], meta['origin']) for row in rows
                         if norm(row['file']).startswith(norm(meta['origin']) + '/')]
        need(selected_rows.count('sources/project/main/main.c') == 1 and
             sorted(x for x in selected_rows if x.startswith('variant/')) == ['variant/vorbis_repair/output.c', 'variant/vorbis_repair/setup.c'], 'Actual caller/bridge compile closure')
        original = context['row'].get('arguments', windows_args(context['row'].get('command', '')))
        need(original == context['original_argv'], 'Parsed Windows compile row differs from actual recorded argv')
        probe, i = [original[0]], 1
        while i < len(original):
            if original[i] == '-c':
                i += 1
            elif original[i] == '-o':
                i += 2
            else:
                probe.append(original[i]); i += 1
        need(original.count('-c') == original.count('-o') == 1 and probe + ['-E', '-dM'] == context['probe_argv'] == commands[3]['argv'] and
             norm(context['cwd']) == norm(context['row']['directory']) == norm(commands[3]['cwd']), 'Macro probe changed compile context')
        compiler = load(prefix + 'compiler-identity-before-build.json')
        need(norm(original[0]) == norm(compiler['compiler']), 'Actual macro compiler binding')
        for key, sha_key in (('compiler', 'compiler_sha256'), ('nm', 'nm_sha256')):
            need(report['tools'][compiler[key]] == compiler[sha_key], 'Compiler identity tool pin')
        generated = context['generated_inputs']
        need(len(generated) == 2 and sum(x.startswith('@') for x in original) == 1, 'Actual generated macro inputs')
        for origin, row in generated.items():
            rel = historical_relative(origin, meta['origin'])
            need(rel in ('build/toolchain/cflags', 'build/specs/picolibc.specs') and
                 row['sha256_before'] == row['sha256_after'], 'Generated input changed during probe')
            identity(prefix + rel, row['sha256_before'])
            identity(prefix + 'sources/generated/' + rel[len('build/'):], row['sha256_before'])
        cflags = read(prefix + 'build/toolchain/cflags').decode().splitlines()
        need(cflags == ['-Wno-frame-address', '-mlongcalls', '-fno-builtin-memcpy', '-fno-builtin-memset', '-fno-builtin-bzero',
             '"-specs=' + norm(meta['origin']) + '/build/specs/picolibc.specs"'], 'Preserved six-line Xtensa cflags/specs')
        macro_text = read(prefix + 'setup-macros.stdout.log').decode().replace('\r\n', '\n')
        macros = dict(re.findall(r'^#define (\w+)(?: (.*))?$', macro_text, re.M))
        for key, value in {'RATE_EXPECT_UNSIGNED_REJECTION': str(int(mode == 'baseline')),
            'RATE_LIMITED_POLICY': str(int(mode == 'limited')), 'CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ': '240',
            'CONFIG_IDF_TARGET_ESP32': '1', 'CONFIG_YORADIO_VORBIS_REPAIR': '1', '__SIZEOF_LONG__': '4',
            '__SIZEOF_POINTER__': '4', '__LONG_MAX__': '0x7fffffffL', '__XTENSA__': '1'}.items():
            need(macros.get(key) == value, 'Actual setup macro missing/wrong: ' + key)
        need('CONFIG_FREERTOS_UNICORE' not in macros and
             (macros.get('LIMIT_TO_64kHz') == '1' if mode == 'limited' else 'LIMIT_TO_64kHz' not in macros), 'SMP/optional policy compile context')
        desc = load(prefix + 'build/project_description.json')
        need(desc['target'] == 'esp32' and norm(desc['c_compiler']) == norm(compiler['compiler']) and
             desc['app_elf'] == 'cyd_vorbis_uint32_rate.elf', 'Actual SDK project identity')
        config = load(prefix + 'build/config/sdkconfig.json')
        need(config.get('IDF_TARGET') == 'esp32' and config.get('ESP_DEFAULT_CPU_FREQ_MHZ') == 240 and
             config.get('FREERTOS_UNICORE') is False and config.get('YORADIO_VORBIS_REPAIR') is True, 'Generated SDK config')
        symbols = read(prefix + 'symbols.stdout.log').decode().replace('\r\n', '\n')
        need(all(re.search(r'\b' + symbol + r'$', symbols, re.M) for symbol in
             ('__wrap_esp_vorbis_dec_open', '__wrap_esp_vorbis_dec_decode', 'esp_vorbis_dec_open', 'esp_vorbis_dec_decode')), 'Actual original/wrapped symbols')
        recipe = load(prefix + 'build/flasher_args.json')
        expected_flash = {'0x1000': 'bootloader/bootloader.bin', '0x8000': 'partition_table/partition-table.bin', '0x10000': 'cyd_vorbis_uint32_rate.bin'}
        need(recipe['flash_files'] == expected_flash and recipe['flash_settings'] ==
             dict(flash_mode='dio', flash_size='4MB', flash_freq='40m'), 'Actual CYD flash recipe')
        merge = commands[5]['argv']
        for offset, image in expected_flash.items():
            need(merge.count(offset) == 1 and historical_relative(merge[merge.index(offset) + 1], meta['origin']) == 'build/' + image,
                 'Actual merge offsets/images')
        for origin, digest in report['tools'].items():
            matches = [row for key, row in omitted.items() if key.startswith(prefix + 'omitted-tools/') and norm(row['origin']) == norm(origin)]
            need(len(matches) == 1 and matches[0]['sha256'] == digest, 'Actual omitted tool/ROM/archive identity')
        for archive, digest in ARCHIVES.items():
            need([value for path, value in report['tools'].items() if PureWindowsPath(path).name == archive] == [digest], 'Pinned public vendor archive')
        protocol_path = root / files[prefix + 'sources/helpers/rate_protocol.py']['stored']
        spec = importlib.util.spec_from_file_location('frozen_rate_protocol_' + name.replace('-', '_'), protocol_path)
        protocol = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(protocol)
        qemu = commands[6]
        log = read(prefix + 'qemu.stdout.log').decode(errors='replace').replace('\r\n', '\n') + '\n' + read(prefix + 'qemu.stderr.log').decode(errors='replace').replace('\r\n', '\n')
        observed = protocol.validate_log(log, mode, control, returncode=qemu['exit_status'], timed_out=qemu['timed_out'], interrupted=qemu['interrupted'])
        need(observed == report['observed'] and tuple(observed[k] for k in
             ('accepted', 'rejected', 'paired_packets', 'pcm_bytes', 'protocol_lines')) == counts, 'Strict observed rate protocol/counts')
        observations[name] = observed
    identity('extras/caller-prep/test_rate_protocol.py', TESTS)
    identity('extras/caller-prep/main.c', CALLER)
    identity('extras/caller-prep/rate_protocol.py', PROTOCOL)
    identity('extras/canonical-tests/test_rate_protocol.py', TESTS)
    identity('extras/canonical-tests/rate_protocol.py', PROTOCOL)
    for folder, receipt in (('caller-prep', 'host-tests-02.json'), ('source-change', 'canonical-host-tests.command.json')):
        host = load('extras/' + folder + '/' + receipt)
        need(host['status'] == 'TERMINAL' and type(host['returncode']) is int and host['returncode'] == 0 and
             type(host['owned_pid']) is int and host['owned_pid'] > 0 and not host.get('timed_out', False) and not host.get('interrupted', False), 'Actual pure host test receipt')
        identity('extras/capture.py', host['runner_sha256'])
        stderr_key = None
        for origin, row in host['logs'].items():
            key = 'extras/' + folder + '/' + PureWindowsPath(origin).name
            identity(key, row['sha256'])
            need(len(read(key)) == row['bytes'], 'Actual host test log size')
            if key.endswith('.stderr.log'):
                stderr_key = key
        need(stderr_key and re.search(r'Ran 19 tests in .*\n\nOK\s*$', read(stderr_key).decode().replace('\r\n', '\n')), 'Actual nineteen host methods')
    return dict(result='OFFLINE_VERIFIED', campaigns=5, owned_commands=45, observed=observations,
        binary_bytes_reverified=False, omitted_bytes_replayable=False, full_G6_qualified=False,
        production_radio_integration=False, physical_device=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    print(json.dumps(verify(parser.parse_args().archive)))
