"""Read-only offline C3 raw8192 evidence verification. Never launches a process.

Only the exact reviewed native protocol module is evaluated, after its hardcoded
hash is checked. No original repository, SDK, tools, binaries or ROM is accessed.
Omitted binary identities and captured ELF header metadata are not replay proof.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import struct
import sys
sys.dont_write_bytecode = True

SCHEMA = 'c3-public-raw8192-archive-v1'
SDK = '9a97f6c54ec638111ce55cd36581b3c192f15207'
NATIVE = '4ed1674fe7f09dc1c92bc829eb42122d788883c1effb1c4fa728008a686e707e'
FIXTURE = '839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378'
HOST_TEST = '51b61040b255bbf00bb3b434a4f2bd50c2bbcdc60d65027153fbaf0fc3923d62'
CAPTURE = '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e'
OLD = 'd9393371872a3ffb292a9693ba254a7e3c5ac8646701166f0ae7260024e5c53b'
NEW = '83ce582554970e1a4bb70587e036c45af7bfb84519d3d7d87580eb4b9b1d38de'
COMMANDS = ('setup-macros', 'symbols', 'qemu-machine-help', 'merge', 'qemu')
BINARY = {'.elf', '.bin', '.a', '.o', '.obj', '.exe', '.dll', '.zip', '.rom', '.lib'}


def sha(data): return hashlib.sha256(data).hexdigest()
def norm(value): return str(value).replace('\\', '/')
def need(ok, message):
    if not ok: raise RuntimeError(message)
def samepath(a, b): return norm(a).casefold() == norm(b).casefold()
def relative(value):
    return value == norm(value) and bool(value) and not PureWindowsPath(value).is_absolute() and ':' not in value and all(x not in ('', '.', '..') for x in value.split('/'))
def terminal(row):
    need(row.get('status') == 'TERMINAL' and type(row.get('returncode')) is int and
         row['returncode'] == 0 and row.get('timed_out', False) is False, 'Actual terminal0/no-timeout required')


def windows_argv(command):
    """Portable Windows quote/backslash decoding, without launching Windows APIs.

    These captured GCC executable names have no quote/space in argv[0]; the
    remainder follows CommandLineToArgvW backslash-before-quote rules.
    """
    need(command and command[0] not in ' \t"', 'Unsupported executable token')
    args, i = [], 0
    while i < len(command):
        while i < len(command) and command[i] in ' \t': i += 1
        if i == len(command): break
        value, quoted = [], False
        while i < len(command) and (quoted or command[i] not in ' \t'):
            count = 0
            while i < len(command) and command[i] == '\\': count += 1; i += 1
            if i < len(command) and command[i] == '"':
                value.extend('\\' * (count//2))
                if count % 2: value.append('"'); i += 1
                elif quoted and i+1 < len(command) and command[i+1] == '"': value.append('"'); i += 2
                else: quoted = not quoted; i += 1
            else:
                value.extend('\\' * count)
                if i < len(command) and (quoted or command[i] not in ' \t'): value.append(command[i]); i += 1
        need(not quoted, 'Unclosed command quote')
        args.append(''.join(value))
    return args


class Archive:
    def __init__(self, bundle):
        self.bundle = Path(bundle).resolve()
        self.m = json.loads((self.bundle/'manifest.json').read_bytes())
        need(self.m['schema'] == SCHEMA, 'Unknown manifest schema')
        self.rows, self.raw, stored = {}, {}, {'manifest.json'}
        for table in ('files', 'external'):
            for key, row in self.m[table].items():
                need((relative(key) if table == 'files' else PureWindowsPath(key).is_absolute()), 'Unsafe original key')
                lookup = norm(key).casefold()
                need(lookup not in self.rows, 'Duplicate original key')
                self.rows[lookup] = (key, row)
                need(type(row['raw_bytes']) is int and row['raw_bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', row['raw_sha256']), 'Invalid raw identity')
                binary = PureWindowsPath(key).suffix.lower() in BINARY
                if row['stored'] is None:
                    need(binary and row.get('omitted'), 'Only binary identity omissions are allowed')
                    continue
                need(not binary and relative(row['stored']) and row['stored'] not in stored, 'Unsafe/duplicate/unexpected binary storage')
                path = self.bundle/row['stored']
                need(not path.is_symlink() and path.resolve().is_relative_to(self.bundle), 'Stored path escapes archive')
                blob = path.read_bytes(); stored.add(row['stored'])
                need(len(blob) == row['stored_bytes'] and sha(blob) == row['stored_sha256'], 'Stored identity mismatch: '+key)
                need(row['encoding'] in ('raw', 'gzip'), 'Unknown encoding')
                raw = gzip.decompress(blob) if row['encoding'] == 'gzip' else blob
                need(len(raw) == row['raw_bytes'] and sha(raw) == row['raw_sha256'], 'Raw identity mismatch: '+key)
                need(not (key.endswith('.py') or PureWindowsPath(key).name == 'fixture.h') or row['encoding'] == 'raw', 'Python/fixture must remain uncompressed')
                self.raw[lookup] = raw
        need(set(self.m['generated']) == {'.gitattributes'}, 'Unexpected generated files')
        attrs = (self.bundle/'.gitattributes').read_bytes(); row = self.m['generated']['.gitattributes']
        need(attrs == b'* -text\n** -text\n' and len(attrs) == row['raw_bytes'] and sha(attrs) == row['raw_sha256'], 'Archive byte-preservation rule changed')
        stored.add('.gitattributes')
        need(not any(p.is_symlink() for p in self.bundle.rglob('*')), 'Archive contains symlink')
        need({p.relative_to(self.bundle).as_posix() for p in self.bundle.rglob('*') if p.is_file()} == stored, 'Exact stored file set mismatch')
        for key, row in self.m['elf_metadata'].items():
            self.bind(key, row['sha256'], row['bytes'])
            header = bytes.fromhex(row['header_hex'])
            need(len(header) == 52 and header[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', header, 18)[0] == 243 and
                 row['elf_class'] == row['byte_order'] == 1 and row['machine'] == 243, 'Captured ELF header is not RV32/243')
        expected_elf = {key for key, row in self.m['files'].items() if key.endswith('.elf')}
        need(set(self.m['elf_metadata']) == expected_elf, 'Missing/extra ELF metadata')

    def reference(self, path, cwd=None):
        path, repository = norm(path), norm(self.m['repository_original']).rstrip('/')
        if not PureWindowsPath(path).is_absolute() and cwd:
            path = norm(cwd).rstrip('/')+'/'+path
        if path.casefold().startswith(repository.casefold()+'/'): path = path[len(repository)+1:]
        lookup = path.casefold()
        need(lookup in self.rows, 'Missing referenced evidence: '+path)
        return lookup

    def row(self, path, cwd=None): return self.rows[self.reference(path, cwd)][1]
    def data(self, path, cwd=None):
        key = self.reference(path, cwd)
        need(key in self.raw, 'Requested omitted bytes: '+str(path))
        return self.raw[key]
    def obj(self, path, cwd=None): return json.loads(self.data(path, cwd))
    def identity(self, path, cwd=None): return self.row(path, cwd)['raw_sha256']
    def bind(self, path, digest, size=None, cwd=None):
        row = self.row(path, cwd)
        need(row['raw_sha256'] == digest and (size is None or row['raw_bytes'] == size), 'Referenced identity mismatch: '+str(path))
    def key(self, role, name): return self.m['roots'][role]+'/'+norm(name)
    def get(self, role, name): return self.data(self.key(role, name))
    def json(self, role, name): return self.obj(self.key(role, name))
    def pin(self, role, name): return self.identity(self.key(role, name))
    def script(self, digest):
        need(any(key.startswith('.build/c3-vorbis-format-') and key.endswith('.py') and row['raw_sha256'] == digest
                 for key, row in self.m['files'].items()), 'Referenced qualification/preparation script missing')
    def receipt(self, path):
        row = self.obj(path); terminal(row)
        need(row['runner_sha256'] == CAPTURE and type(row['owned_pid']) is int and row['owned_pid'] > 0 and
             row['timeout_seconds'] > 0 and row['elapsed_seconds'] >= 0, 'Capture provenance incomplete')
        self.bind('.build/cyd-vorbis-format-command-01.py', row['runner_sha256'])
        self.bind(row['argv'][0], row['executable_sha256'])
        need(len(row['logs']) == 2, 'Require both captured streams')
        for name, log in row['logs'].items(): self.bind(name, log['sha256'], log['bytes'])
        return row


def check_prep(a):
    for role in ('project_prep', 'candidate_prep', 'protocol'):
        pins = a.json(role, 'pins.json'); rows = pins['files']
        if isinstance(rows, list):
            for row in rows: a.bind(a.key(role, row['relative']), row['sha256'], row['bytes'])
        else:
            for name, row in rows.items(): a.bind(a.key(role, name), row['sha256'], row['bytes'])
        for row in pins.get('external_inputs', []): a.bind(row['path'], row['sha256'], row['bytes'])
        for name, row in pins.get('origins', {}).items():
            a.bind(name, row['sha256'])
            if 'snapshot' in row: a.bind(a.key(role, row['snapshot']), row['sha256'])
        if role != 'protocol':
            need(pins['target'] == 'esp32c3' and pins['sdk_revision'] == SDK and pins['protocol'] == 'C3_VORBIS_FORMAT', 'Wrong C3/SDK pins')
            for tool in pins['tools'].values(): need(a.row(tool)['stored'] is None, 'Tools/ROM must be identities only')
    for row in a.json('tests_prep', 'input-pins.json')['inputs']: a.bind(row['path'], row['sha256'], row['bytes'])
    a.bind(a.key('protocol', 'c3_vorbis_format_protocol.py'), NATIVE)
    a.bind(a.key('protocol', 'fixture.h'), FIXTURE)
    host = a.json('protocol', 'host-tests.command.json')
    need(type(host['exit_status']) is int and host['exit_status'] == 0 and host['sdk_compiler_qemu_reference_or_git_executed'] is False, 'Preparatory host tests not successful/scoped')
    a.bind(host['argv'][0], host['python_sha256'])
    a.bind(a.key('protocol', 'test_c3_vorbis_format_protocol.py'), host['test_sha256'])
    a.bind(a.key('protocol', 'c3_vorbis_format_protocol.py'), host['module_sha256'])
    for stream in ('stdout', 'stderr'): a.bind(a.key('protocol', 'host-tests.'+stream+'.log'), host[stream+'_sha256'])
    need(re.search(rb'Ran 8 tests in [0-9.]+s\s+OK\s*$', a.get('protocol', 'host-tests.stderr.log')), 'Preparatory host8 summary missing')


def check_sources(a):
    path = 'variant/vorbis_repair/setup.c'
    old, new = a.get('baseline', path), a.get('acceptance', path)
    a.bind(a.key('baseline', path), OLD); a.bind(a.key('acceptance', path), NEW)
    removed = b'#else\r\n  if(vi->rate<64000 && ci->blocksizes[1]>4096)goto err_out;\r\n'
    need(old.count(removed) == 1 and new == old.replace(removed, b'', 1) and a.get('control', path) == old, 'Two-line source relation/control restoration changed')
    need(b'#ifdef LIMIT_TO_64kHz' in new, 'Optional limited profile removed')
    relation = a.json('candidate_prep', 'candidate-relation.json')
    need(relation['removed_bytes'].encode() == removed and relation['exact_removal_count'] == 1 and
         relation['other_decoder_source_changes'] is False and relation['canonical_changed'] is False, 'Historical candidate relation changed')
    a.bind(a.key('project_prep', 'pins.json'), relation['baseline_pins_sha256'])
    a.bind(a.key('baseline', 'baseline-qualification.json'), relation['baseline_qualification_sha256'])
    need(relation['original_setup_sha256'] == OLD and relation['candidate_setup_sha256'] == NEW, 'Candidate setup identities changed')
    a.script(relation['preparation_script_sha256'])
    variants = [{key[len(a.m['roots'][role]+'/variant/'):]:row['raw_sha256'] for key, row in a.m['files'].items()
                 if key.startswith(a.m['roots'][role]+'/variant/')} for role in ('baseline', 'acceptance', 'control')]
    need(set(variants[0]) == set(variants[1]) == set(variants[2]), 'Variant file sets differ')
    for name in variants[0]:
        if name != 'vorbis_repair/setup.c': need(variants[0][name] == variants[1][name] == variants[2][name], 'Unrelated variant source changed')
    # Qualified target caller/defaults/partitions stay byte-identical; its sole
    # CMake difference is the pinned setup SHA. Canonical adapted CMake is scoped separately.
    for role in ('acceptance', 'control'):
        for name in ('CMakeLists.txt', 'main/main.c', 'main/fixture.h', 'sdkconfig.defaults', 'partitions.csv'):
            need(a.get(role, 'sources/project/'+name) == a.get('baseline', 'sources/project/'+name), 'Caller/project input changed: '+name)
    bmake = a.get('baseline', 'sources/project/main/CMakeLists.txt')
    need(bmake.count(OLD.encode()) == 1 and a.get('acceptance', 'sources/project/main/CMakeLists.txt') == bmake.replace(OLD.encode(), NEW.encode(), 1) and
         a.get('control', 'sources/project/main/CMakeLists.txt') == bmake, 'Actual CMake change exceeds one setup pin')
    caller = a.json('project_prep', 'caller-relation.json')
    a.bind(caller['canonical_source'], caller['canonical_sha256'])
    text = a.data(caller['canonical_source']).decode()
    expected_changes = [('CYD_VORBIS_FORMAT', 'C3_VORBIS_FORMAT', 14), ('core=1', 'core=0', 4),
        ('xPortGetCoreID() == 1, "public_decode_core1"', 'xPortGetCoreID() == 0, "public_decode_core0"', 1),
        ('xTaskCreatePinnedToCore(task, "public_format", 16384, NULL, 3, NULL, 1)', 'xTaskCreatePinnedToCore(task, "public_format", 16384, NULL, 3, NULL, 0)', 1),
        ('create_core1_format_task', 'create_core0_format_task', 1)]
    need([(x['before'], x['after'], x['occurrences']) for x in caller['changes']] == expected_changes and caller['other_caller_edits'] is False, 'Unexpected caller adaptation')
    for before, after, count in expected_changes:
        need(text.count(before) == count, 'Caller replacement count changed'); text = text.replace(before, after)
    need(text.encode() == a.get('project_prep', caller['adapted_source']), 'Adapted caller differs beyond reviewed changes')
    a.bind(a.key('project_prep', caller['adapted_source']), caller['adapted_sha256'])
    historical = a.m['historical_inputs']
    need(len(historical) == 1, 'Exactly one historical original setup pin required')
    for row in caller['byte_equal_copies']:
        snapshot = a.key('project_prep', row['copy']); a.bind(snapshot, row['sha256'], row['bytes'])
        if row['copy'] == path:
            h = historical[0]
            need(samepath(h['original'], row['original']) and h['snapshot'] == snapshot and h['raw_sha256'] == row['sha256'] and
                 h['raw_bytes'] == row['bytes'] and h['reason'], 'Historical setup provenance lost')
        else: a.bind(row['original'], row['sha256'], row['bytes'])
    for role in ('baseline', 'acceptance', 'control'): a.bind(a.key(role, 'sources/project/main/fixture.h'), FIXTURE)


def check_campaign(a, role, validator):
    expected = 1 if role == 'baseline' else 0
    q = a.json(role, 'baseline-qualification.json' if expected else 'qualification.json')
    need(q['completed'] is True and q['target_live'] is False, 'Incomplete/live campaign')
    if role == 'baseline':
        need(q['result'] == 'REGRESSION_REPRODUCED' and q['passed'] is False and q['regression_reproduced'] is True and q['format_acceptance_qualified'] is False, 'Baseline mislabeled')
    else:
        control = role == 'control'
        need(q['result'] == ('CONTROL_EFFECTIVE' if control else 'FORMAT_ACCEPTED') and q['passed'] is (not control) and
             q['format_acceptance_qualified'] is (not control) and q['control_effective'] is control and
             q['regression_reproduced'] is False and q['scope'] == 'acceptance' and q['control'] == ('old-guard' if control else None), 'Acceptance/control mislabeled')
    prep = 'candidate_prep' if role == 'acceptance' else 'project_prep'
    a.bind(a.key(prep, 'pins.json'), q['source_pins_sha256'])
    a.bind(a.key(role, 'pins.json'), q['source_pins_sha256'])
    a.bind(a.key('protocol', 'pins.json'), q['protocol_pins_sha256'])
    a.bind(a.key(role, 'variant/vorbis_repair/setup.c'), q['setup_sha256'])
    a.bind(a.key(role, 'qemu-flash.bin'), q['flash_sha256'], 4194304)
    a.script(q['qualification_script_sha256'])
    for name, digest in q.get('source_copies', {}).items(): a.bind(a.key(role, name), digest)
    if role != 'baseline': need(len(q['source_copies']) == 9 and q['elf_machine'] == 243, 'Final source/ELF bindings incomplete')
    need(set(q['commands']) == set(COMMANDS), 'Five command receipts required')
    commands = {}
    for name in COMMANDS:
        row = q['commands'][name]
        need(row['record'] == name+'.json' and type(row['returncode']) is int and row['returncode'] == 0, 'Wrong command reference')
        a.bind(a.key(role, row['record']), row['sha256'])
        commands[name] = a.receipt(a.key(role, row['record']))
    sdk = a.json(role, 'sdk-build-result.json'); pins = a.json(prep, 'pins.json')
    need(sdk['status'] == 'TERMINAL_SUCCESS' and type(sdk['returncode']) is int and sdk['returncode'] == 0 and
         sdk['sdk_revision'] == SDK and sdk['sdk_tracked_clean'] is True and sdk['pins_sha256'] == q['source_pins_sha256'] and
         sdk['expected_rejection'] == expected, 'SDK result/pin/configuration mismatch')
    for name, tool in sdk['selected_tools'].items(): need(samepath(tool, pins['tools'][name]), 'Selected SDK tool differs from pin')
    need(samepath(sdk['compiler'], pins['tools']['compiler']) and samepath(sdk['executable'], pins['tools']['python']), 'SDK compiler/Python mismatch')
    a.reference(sdk['argv'][0]); need(samepath(sdk['argv'][0], pins['sdk_directory']+'/tools/idf.py'), 'SDK launcher mismatch')
    sdkargv = [norm(x) for x in sdk['argv']]
    need('IDF_TARGET=esp32c3' in sdkargv and 'IDF_TOOLCHAIN=gcc' in sdkargv and '--no-ccache' in sdkargv and
         'FORMAT_EXPECT_LOW_RATE_REJECTION='+str(expected) in sdkargv and sdkargv[-1] == 'build', 'Wrong actual SDK command')
    need(a.reference(sdk['argv'][sdk['argv'].index('-C')+1]+'/main/main.c') == a.reference(a.key(role, 'sources/project/main/main.c')) and
         samepath(sdk['argv'][sdk['argv'].index('-B')+1], norm(sdk['cwd'])+'/build'), 'SDK source/build root mismatch')
    for stream in ('stdout', 'stderr'): a.bind(a.key(role, 'sdk-build.'+stream+'.log'), sdk[stream+'_sha256'])
    outerpath = a.m['outer_sdk_records'][role]; outer = a.receipt(outerpath)
    need(outer['argv'][outer['argv'].index('-ExpectedRejection')+1] == str(expected) and
         outer['argv'][outer['argv'].index('-PinsSha256')+1] == q['source_pins_sha256'] and
         samepath(outer['argv'][outer['argv'].index('-Campaign')+1], sdk['cwd']), 'Outer SDK launch differs')
    launch = outer['argv'][outer['argv'].index('-File')+1]
    need(a.reference(launch, outer['cwd']) == a.reference(a.key(prep, 'sdk-build.ps1')), 'Outer SDK launcher not pinned prep script')
    if role != 'baseline':
        a.bind(a.key(role, 'sdk-build-result.json'), q['sdk_build_receipt_sha256']); a.bind(outerpath, q['sdk_outer_receipt_sha256'])
    context, post = a.json(role, 'macro-context.json'), a.json(role, 'postbuild-observations.json')
    for mapping in ('build_outputs', 'reviewed_sources', 'sdk_generated_sources'):
        for name, digest in context[mapping].items(): a.bind(a.key(role, name), digest)
    need({norm(x) for x in context['reviewed_sources']} == {'sources/project/main/main.c', 'variant/vorbis_repair/output.c', 'variant/vorbis_repair/setup.c'} and
         {norm(x) for x in context['sdk_generated_sources']} == {'build/project_elf_src_esp32c3.c', 'build/x509_crt_bundle.S'}, 'Unexpected owned source closure')
    a.bind(a.key(role, 'build/compile_commands.json'), context['compile_database_sha256'])
    a.bind(a.key(role, 'compiler-environment.json'), context['compiler_environment_sha256'])
    a.script(context['preparation_script_sha256']); a.script(post['preparation_script_sha256'])
    row, original = context['row'], context['original_argv']
    need(row in a.json(role, 'build/compile_commands.json') and windows_argv(row['command']) == original, 'Macro argv differs from actual compile row')
    need(samepath(row['directory'], context['directory']) and samepath(row['file'], original[-1]) and original.count('-c') == original.count('-o') == 1 and
         a.reference(row['file']) == a.reference(a.key(role, 'variant/vorbis_repair/setup.c')), 'Wrong setup translation unit')
    need(samepath(original[0], pins['tools']['compiler']), 'Macro compiler not pinned SDK compiler'); a.bind(original[0], context['compiler_sha256'])
    trimmed, skip = [], False
    for value in original:
        if skip: skip = False; continue
        if value == '-o': skip = True; continue
        if value != '-c': trimmed.append(value)
    need(context['argv'] == trimmed+['-E', '-dM'] and commands['setup-macros']['argv'] == context['argv'] and
         samepath(commands['setup-macros']['cwd'], context['directory']), 'Macro probe changed actual compiler context')
    frozen = context['frozen_inputs']
    need(len(frozen) == 4, 'Exactly four frozen macro inputs required')
    for path, entry in frozen.items(): a.bind(path, entry['sha256']); a.bind(a.key(role, entry['snapshot']), entry['sha256'])
    flags = next(x for x in frozen if norm(x).endswith('/build/toolchain/cflags'))
    specs = next(x for x in frozen if norm(x).endswith('/build/specs/picolibc.specs'))
    need({norm(x['snapshot']) for x in frozen.values()} == {'macro-inputs/toolchain/cflags', 'macro-inputs/specs/picolibc.specs', 'macro-inputs/project_elf_src_esp32c3.c', 'macro-inputs/x509_crt_bundle.S'}, 'Unexpected macro snapshot set')
    need([x for x in original if x.startswith('@')] == ['@'+norm(flags)], 'Response argument not retained exactly')
    need(a.data(flags).decode().splitlines() == ['-march=rv32imc_zicsr_zifencei', '-mtune=esp-base', '"-specs='+norm(specs)+'"', '-D__PICOLIBC_ERRNO_FUNCTION=__errno'] and a.data(specs), 'RV32 four flags/specs changed')
    env = a.json(role, 'compiler-environment.json')
    need(samepath(env['IDF_PATH'], pins['sdk_directory']) and samepath(env['IDF_TOOLS_PATH'], pins['tools_directory']), 'Compiler SDK environment changed')
    macros = a.get(role, 'setup-macros.stdout.log').decode().replace('\r\n', '\n')
    expected_macros = {'__riscv_xlen':32, 'CONFIG_IDF_TARGET_ESP32C3':1, 'CONFIG_FREERTOS_UNICORE':1,
                       'CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ':160, 'FORMAT_EXPECT_LOW_RATE_REJECTION':expected}
    need(post['macros'] == expected_macros and post['limit_to_64khz'] is False and not re.search(r'^#define LIMIT_TO_64kHz\b', macros, re.M), 'Wrong setup macros/optional cap')
    for name, value in expected_macros.items(): need(re.search(r'^#define '+name+' '+str(value)+r'$', macros, re.M), 'Required actual setup macro missing: '+name)
    for name, entry in post['commands'].items(): need(name in COMMANDS[:3] and entry == q['commands'][name], 'Postbuild command binding differs')
    need(set(post['commands']) == set(COMMANDS[:3]), 'Three postbuild command bindings required')
    symbols = {'__wrap_esp_vorbis_dec_open', '__wrap_esp_vorbis_dec_decode', 'esp_vorbis_dec_open', 'esp_vorbis_dec_decode'}
    need(set(post['symbols']) == symbols, 'Expected public raw wrappers missing')
    symboltext = a.get(role, 'symbols.stdout.log').decode()
    for name in symbols: need(re.search(r'\b'+name+r'\s*$', symboltext, re.M), 'Missing actual ELF symbol: '+name)
    need(a.reference(commands['symbols']['argv'][-1], commands['symbols']['cwd']) == a.reference(a.key(role, 'build/c3_vorbis_public_format.elf')), 'Symbols refer to different ELF')
    need(commands['qemu-machine-help']['argv'][1:] == ['-machine', 'help'] and re.search(rb'^esp32c3\s', a.get(role, 'qemu-machine-help.stdout.log'), re.M), 'C3 machine unavailable')
    config = a.json(role, 'build/config/sdkconfig.json')
    need(config['IDF_TARGET'] == 'esp32c3' and config['FREERTOS_UNICORE'] is True and config['ESP_DEFAULT_CPU_FREQ_MHZ'] == 160, 'Wrong generated target config')
    desc = a.json(role, 'build/project_description.json')
    need(desc['target'] == 'esp32c3' and desc['git_revision'] == SDK[:8] and samepath(desc['idf_path'], pins['sdk_directory']) and
         samepath(desc['c_compiler'], pins['tools']['compiler']), 'Generated project SDK/target/compiler differs')
    elf = a.key(role, 'build/c3_vorbis_public_format.elf')
    need(a.m['elf_metadata'][elf]['machine'] == 243, 'Actual selected ELF metadata missing')
    recipe = a.json(role, 'build/flasher_args.json'); a.bind(a.key(role, 'build/flasher_args.json'), post['recipe_sha256'])
    files = {'0x0':'bootloader/bootloader.bin', '0x8000':'partition_table/partition-table.bin', '0x10000':'c3_vorbis_public_format.bin'}
    need(recipe['flash_files'] == files and recipe['extra_esptool_args']['chip'] == 'esp32c3' and
         recipe['flash_settings'] == {'flash_mode':'dio', 'flash_size':'4MB', 'flash_freq':'40m'}, 'Wrong C3 merge recipe')
    need({norm(name) for name in post['flash_inputs']} == {'build/'+name for name in files.values()}, 'Wrong flash input set')
    for name, digest in post['flash_inputs'].items(): a.bind(a.key(role, name), digest)
    merge = a.json(role, 'merge-plan.json'); argv = merge['argv']
    need(commands['merge']['argv'] == argv and samepath(commands['merge']['cwd'], merge['directory']), 'Executed merge differs from saved plan')
    expected_merge = [pins['tools']['python'], '-m', 'esptool', '--chip', 'esp32c3', 'merge-bin', '--output', norm(sdk['cwd'])+'/qemu-flash.bin',
                      '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
    for offset, name in files.items(): expected_merge += [offset, norm(sdk['cwd'])+'/build/'+name]
    expected_merge += ['--pad-to-size', '4MB']
    need([norm(x) for x in argv] == [norm(x) for x in expected_merge], 'Actual merge offsets/inputs changed')
    qargv = commands['qemu']['argv']
    expected_qemu = [pins['tools']['qemu'], '-audiodev', 'none,id=quiet', '-M', 'esp32c3,audiodev=quiet', '-smp', '1',
        '-L', norm(PureWindowsPath(pins['tools']['rom']).parent), '-display', 'none', '-monitor', 'none', '-serial', 'stdio',
        '-no-reboot', '-snapshot', '-nic', 'none', '-drive', 'file='+norm(sdk['cwd'])+'/qemu-flash.bin,if=mtd,format=raw']
    need([norm(x) for x in qargv] == [norm(x) for x in expected_qemu], 'Actual QEMU machine/image/isolation changed')
    log = a.get(role, 'qemu.stdout.log').decode(errors='replace')+'\n'+a.get(role, 'qemu.stderr.log').decode(errors='replace')
    process = commands['qemu']
    observed = validator['validate_log'](log, 'baseline' if expected else 'acceptance', 'old-guard' if role == 'control' else None,
        a.get(role, 'sources/project/main/fixture.h').decode(), returncode=process['returncode'],
        timed_out=(process['status'] != 'TERMINAL' or process.get('timed_out', False)))
    count, pairs, pcm = (421, 5, 4631808) if role == 'acceptance' else ((279, 3, 2452224) if role == 'control' else (285, 3, 2452224))
    need(observed == q['observed'] and observed['protocol_lines'] == count and observed['vendor_packets'] == 68 and
         observed['exact_pairs'] == pairs and observed['exact_pair_packets'] == 68*pairs and q['exact_pair_pcm_bytes'] == pcm, 'Protocol report/count/accounting mismatch')
    pcm_observed = sum(int(x) for x in re.findall(r'^C3_VORBIS_FORMAT_EXACT .*? pcm=(\d+) ', log, re.M))
    need(pcm_observed == pcm, 'Exact pair PCM sum differs from native raw log')
    return observed


def check_root(a):
    def record(name): return a.obj('.build/c3-vorbis-format-'+name+'-01.json')
    combined = record('root-combined-qualification')
    need(combined['state'] == 'NARROW_C3_RAW8192_FIX_QUALIFIED' and combined['completed'] is True and combined['target_live'] is False and
         combined['elf_machine'] == 243 and combined['sdk_revision'] == SDK and combined['protocol'] == 'C3_VORBIS_FORMAT_' and combined['decode_core'] == 0, 'Combined identity/scope changed')
    for key in ('radio_integration_qualified', 'production_firmware_built', 'full_G6_qualified', 'Ogg_reset_EOF_OOM_qualified', 'physical_qualified', 'adapted_canonical_cmake_sdk_qualified'):
        need(combined[key] is False, 'Unsupported combined qualification: '+key)
    for role in ('baseline', 'acceptance', 'control'):
        a.bind(a.key(role, 'baseline-qualification.json' if role == 'baseline' else 'qualification.json'), combined[role+'_report_sha256'])
    extras = {'canonical_host_receipt':'host-canonical', 'test_promotion':'test-promotion', 'test_index_check':'index-check',
              'source_promotion':'source-promotion', 'independent_source_review':'candidate-review', 'source_index_relation':'source-index-relation'}
    for key, name in extras.items(): a.bind('.build/c3-vorbis-format-'+name+'-01.json', combined[key+'_sha256'])
    need(combined['canonical_setup_sha256'] == NEW and combined['canonical_host_tests'] == 8, 'Combined source/host count differs')
    promotion, staged = record('test-promotion'), record('index-check')
    need(len(promotion['files']) == 9 and staged['files'] == promotion['files'] and staged['raw_index_bytes_match_promoted_and_tested'] is True and
         promotion['adapted_cmake_sdk_qualified'] is False and promotion['caller_fixture_and_compile_link_directives_match_qualified_basis'] is True, 'Canonical promotion/index/source scope changed')
    a.bind(a.key('tests_prep', 'pins.json'), promotion['proposal_pins_sha256'])
    for name, digest in promotion['files'].items():
        a.bind(name, digest); a.bind(a.key('tests_prep', 'proposed/'+name), digest)
    a.bind('tests/c3_vorbis_format_protocol.py', NATIVE); a.bind('tests/test-c3-vorbis-format-protocol.py', HOST_TEST)
    host = a.receipt('.build/c3-vorbis-format-host-canonical-01.json')
    need(host['argv'][1:] == ['-B', '-X', 'utf8', 'tests/test-c3-vorbis-format-protocol.py', '-v'], 'Canonical host invocation differs')
    stderr = next(name for name in host['logs'] if name.endswith('.stderr.log'))
    need(re.search(rb'Ran 8 tests in [0-9.]+s\s+OK\s*$', a.data(stderr)), 'Canonical host8 summary missing')
    promotion = record('source-promotion')
    need(promotion['original_sha256'] == OLD and promotion['candidate_sha256'] == promotion['canonical_sha256'] == NEW and
         promotion['exact_two_line_removal'] is True and promotion['other_source_changes'] is False, 'Canonical source promotion differs')
    a.bind(promotion['canonical_source'], NEW)
    need(a.data(promotion['canonical_source']) == a.get('acceptance', 'variant/vorbis_repair/setup.c'), 'Promoted setup differs from actual accepted source')
    index = record('source-index-relation')
    need(index['canonical_source'] == promotion['canonical_source'] and index['candidate_sha256'] == index['working_source_sha256'] == NEW and
         index['canonical_index_sha256'] == combined['canonical_index_sha256'] and index['exact_two_line_index_removal'] is True and
         index['reversible_newline_conversion_only'] is True and index['source_tokens_unchanged'] is True, 'Source index relation changed')
    a.bind(index['index_snapshot'], index['canonical_index_sha256'])
    blob = a.data(index['index_snapshot'])
    need(b'\r' not in blob and blob.replace(b'\n', b'\r\n') == a.get('acceptance', 'variant/vorbis_repair/setup.c') and
         sha(a.get('baseline', 'variant/vorbis_repair/setup.c').replace(b'\r\n', b'\n')) == index['original_index_sha256'], 'Published LF bytes do not reversibly match executed CRLF candidate')
    for role in ('acceptance', 'control'): a.bind(a.key(role, 'qualification.json'), promotion[role+'_report_sha256'])
    review = record('candidate-review'); need(review['result'] == 'SOURCE_RELATION_CONFIRMED' and review['findings'] == [] and
        review['candidate_runtime_reviewed'] is False and review['production_promotion_qualified'] is False, 'Historical source audit scope changed')
    identities = review['identities']
    bindings = {'baseline_pins':('project_prep','pins.json'), 'candidate_pins':('candidate_prep','pins.json'),
        'baseline_qualification':('baseline','baseline-qualification.json'), 'candidate_relation':('candidate_prep','candidate-relation.json'),
        'candidate_diff':('candidate_prep','candidate.diff'), 'baseline_setup':('baseline','variant/vorbis_repair/setup.c'),
        'candidate_setup':('acceptance','variant/vorbis_repair/setup.c'), 'baseline_main_cmake':('project_prep','project/main/CMakeLists.txt'),
        'candidate_main_cmake':('candidate_prep','project/main/CMakeLists.txt')}
    for name, (role, path) in bindings.items(): a.bind(a.key(role, path), identities[name+'_sha256'])


def verify(bundle):
    a = Archive(bundle)
    check_prep(a); check_sources(a); check_root(a)
    # Evaluate only this reviewed, hash-pinned 59-line pure protocol module.
    code = a.get('protocol', 'c3_vorbis_format_protocol.py'); need(sha(code) == NATIVE, 'Unreviewed protocol code')
    validator = {}; exec(compile(code, 'frozen_c3_vorbis_format_protocol.py', 'exec'), validator)
    observed = {role:check_campaign(a, role, validator) for role in ('baseline', 'acceptance', 'control')}
    need(a.get('baseline', 'sdkconfig') == a.get('acceptance', 'sdkconfig') == a.get('control', 'sdkconfig'), 'Actual SDK config changed between campaigns')
    return dict(verified=True, observed=observed, public_raw_format_only=True, sdk_revision=SDK, elf_machine=243,
        omitted_binaries_replayed=False, production_firmware_qualified=False, radio_integration_qualified=False,
        Ogg_EOF_reset_OOM_qualified=False, physical_qualified=False, adapted_canonical_cmake_sdk_qualified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('bundle', type=Path)
    print(json.dumps(verify(parser.parse_args().bundle), indent=2))
