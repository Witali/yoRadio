"""Offline standalone baseline replay; no process, compiler, SDK, codec or Git calls."""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
import ntpath
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import struct
import sys

sys.dont_write_bytecode = True
SDK = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
SOURCE = '6d009ae122974c4993ab88e8befc350f40077d9095d14e85f784c8a9ef40e6bc'
RUNTIME = 'c5b554bc0df7c566742c0d9ceeb157fdf81116d93426c22e73adf04af9d8cc77'
CONTROLLER = '1d500f7ae44334cc62110da70a0243ec39faf5fa43bc4c585c23b1b94bb68f1f'
CONTRACT = 'a50a9350ac681f58d18774455127714b8d2ce195430b873c746d7b2b79374c48'
MODEL = '92a9c6ba03892f6e6637b5e6cf5889e5cf0defe92e6d5357e40120acad66d8ff'
ENTRYPOINT = 'b656752ca5f0d00a7fe3b96b8fc2ebf94da9956331d746e45f64e671f75518f6'
QMP = 'e9e6d00bf5cf05aad9262429d149f93f067e1bf3b8691a58cb0a56a0bf7269fa'
ORACLE = '38ed33532e8cf0e4f7a76aad6650ab144b72e7df4d54168c807e39f2f9ea97d5'
PROTOCOL = 'a28abe38bf7f8f757073dd9d56d6c1f41679d23dca0125a1f61dc090ac1d9f72'
SETUP = '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
ABI = 'e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60'
PORT = '2660e256f14857b0aaa0f7104071796bc8095fa01c8eb1f87da82bdd116b696f'
HEADER = '0e7fe555d413f82419a7688e549cb6d153cf5867fc67a0e2ec5c394a5735ce67'
REPORTS = {'SDK': '8988baa98cc0c72a494dd70eec229860fb953cba63ce58a38b4f0caa155bab74', 'host': '8289faff1ab23e749035ba912feefc58263c39b06f26f87689dd04fcb528c999'}
COMMANDS = ['sdk-head', 'sdk-clean', 'sdk-configure-launcher', 'unit-macros-before', 'unit-dependencies-before', 'sdk-build-launcher',
            'unit-macros-after', 'unit-dependencies-after', 'symbols', 'ninja-commands', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after']
MACROS = dict(__SIZEOF_INT__='4', __SIZEOF_LONG__='4', __SIZEOF_POINTER__='4', __XTENSA__='1', __BYTE_ORDER__='__ORDER_LITTLE_ENDIAN__',
              CONFIG_IDF_TARGET_ESP32='1', CONFIG_IDF_TARGET_ARCH_XTENSA='1', CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ='240', CONFIG_FREERTOS_NUMBER_OF_CORES='2',
              CONFIG_ESP_MAIN_TASK_AFFINITY_CPU0='1', CONFIG_ESP_MAIN_TASK_AFFINITY='0x0', CONFIG_ESP_MAIN_TASK_STACK_SIZE='16384')
BAD_LINK = re.compile(r'libesp_audio_(?:codec|simple_dec)\.a|esp-adf-libs|--wrap[=, ]+esp_vorbis|lib(?:i?vorbis(?:file)?|ogg)\.a', re.I)
BAD_SYMBOL = re.compile(r'(?:__wrap_|__real_)?(?:esp_vorbis_dec_\w+|esp_audio_(?:simple_)?dec_\w+)|repair_(?:vorbis_open|vorbis_register)|vorbis_synthesis_\w+|ov_\w+')
FALSE = ('host_sanitizers_qualified', 'public_arithmetic_portability_qualified', 'full_standard_qualified', 'vendor_cause_diagnosed', 'full_G6_qualified', 'physical_device', 'production_radio_integration')


def need(ok, reason):
    if not ok: raise RuntimeError(reason)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def safe(value):
    value = str(value).replace('\\', '/'); path = PurePosixPath(value)
    need(value and not path.is_absolute() and '..' not in path.parts and ':' not in value, 'Safe archived relative key')
    return path.as_posix()


def win(value): return PureWindowsPath(ntpath.normpath(str(value)))


def indexed(value):
    return value['files'] if isinstance(value['files'], dict) else {row['path']: row for row in value['files']}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--manifest-sha256', required=True); args = parser.parse_args(); root = args.root.resolve()
    manifestraw = (root / 'manifest.json').read_bytes(); need(sha(manifestraw) == args.manifest_sha256, 'Independently reviewed archive manifest')
    m = json.loads(manifestraw)
    need(m['schema'] == 'public-book-consumer-baseline-archive-v1' and m['archive_data_dependencies'] == [] and m['standalone'] is True and
         all(m[k] is False for k in FALSE) and m['omitted_binary_bytes_replayable'] is False, 'Separate finite baseline scope, standalone sources')
    expected = {safe(row['stored']) for row in m['files'].values()} | {'manifest.json'}
    need(expected == {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} and len(expected) == len(m['files']) + 1, 'Exact stored file inventory')
    cache = {}
    def raw(key):
        key = safe(key)
        if key not in cache:
            row = m['files'][key]; path = root / safe(row['stored']); need(path.is_file() and not path.is_symlink(), 'Regular scoped retained file')
            blob = path.read_bytes(); need(len(blob) == row['stored_bytes'] and sha(blob) == row['stored_sha256'] and row['compression'] in ('none', 'gzip'), 'Exact lossless stored bytes')
            value = gzip.decompress(blob) if row['compression'] == 'gzip' else blob
            need(len(value) == row['bytes'] and sha(value) == row['sha256'], 'Exact raw original bytes'); cache[key] = value
        return cache[key]
    def obj(key): return json.loads(raw(key).decode('utf-8-sig'))
    def text(key): return raw(key).decode('utf-8', errors='replace').replace('\r\n', '\n')
    def identity(key, digest, size=None):
        row = m['files'].get(key, m['omitted'].get(key)); need(row is not None and row['sha256'] == digest and (size is None or row['bytes'] == size), 'Retained/omitted original identity')
        if key in m['files']: need(sha(raw(key)) == digest, 'Actual retained byte identity')
        else: need(row['bytes'] > 0 and row.get('reason'), 'Explicit nonempty binary omission')
    def module(name, key, expected_sha):
        need(sha(raw(key)) == expected_sha and m['files'][key]['compression'] == 'none', 'Exact unchanged pure module source')
        spec = importlib.util.spec_from_file_location(name, root / m['files'][key]['stored']); value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
    for key in m['files']: raw(key)
    need(sha(raw('plan.json')) == m['plan_sha256'], 'Exact reviewed root plan')
    plan = obj('plan.json')
    need(plan['schema'] == 'public-book-baseline-archive-plan-v1' and plan['state'] == 'ACTUAL_PARENT_TERMINALS_PINNED' and plan['archive_data_dependencies'] == [] and
         plan['canonical_destination'] == 'tests/results/cyd-vorbis-public-book-consumer-baseline-20261023', 'Standalone baseline selection')
    need(sha(raw('CHECKPOINT.md')) == plan['checkpoint']['sha256'], 'Root checkpoint exact bytes')
    need(raw('.gitattributes') == b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n', 'Captured raw-byte Git policy')
    counts = {'source': 159, 'runtime': 19, 'controller': 199, 'proposal-only': 5}
    need(set(m['preparations']) == set(counts) == {r['name'] for r in plan['preparations']}, 'Every separate fixed preparation inventory')
    for row in plan['preparations']:
        prefix = 'preparations/' + safe(row['name']); entry = m['preparations'][row['name']]
        need(entry == dict(prefix=prefix, index=row['index'], index_sha256=row['index_sha256']), 'Preparation association')
        identity(prefix + '/' + row['index'], row['index_sha256']); index = obj(prefix + '/' + row['index']); entries = indexed(index)
        names = {key[len(prefix)+1:] for key in (*m['files'], *m['omitted']) if key.startswith(prefix + '/')}
        need(names == set(entries) | {row['index']} and len(names) == counts[row['name']], 'Complete preparation including readiness')
        for name, fact in entries.items(): identity(prefix + '/' + safe(name), fact['sha256'], fact['bytes'])
    source, runtime, controller = 'preparations/source/', 'preparations/runtime/', 'preparations/controller/'
    need(sha(raw(source + 'readiness.json')) == SOURCE and sha(raw(runtime + 'readiness.json')) == RUNTIME and sha(raw(controller + 'readiness.json')) == CONTROLLER, 'Fixed independent source/runtime/controller pins')
    for row in obj(source + 'readiness.json')['files']:
        identity(controller + 'unit-source/' + safe(row['path']), row['sha256'], row['bytes'])
    for row in obj(runtime + 'readiness.json')['files']:
        identity(controller + safe(row['path']), row['sha256'], row['bytes'])
    for origin in obj(controller + 'source-origins.json')['inputs']:
        identity(controller + safe(origin['snapshot']), origin['sha256'], origin['bytes'])
    need(sha(raw(runtime + 'contract.json')) == CONTRACT and sha(raw(runtime + 'project/main/consumer_data.h')) == HEADER and
         sha(raw(runtime + 'project/main/consumer_port.inc')) == PORT and raw(runtime + 'project/main/consumer_port.inc') == raw(source + 'consumer_port.inc'), 'Unmodified baseline runtime bytes')
    need(sha(raw(runtime + 'project/main/pinned/production/vorbis_repair/setup.c')) == SETUP and sha(raw(runtime + 'project/main/pinned/production/vorbis_repair_abi.h')) == ABI, 'Exact canonical parser/ILP32 ABI')
    need(sha(raw(source + 'public-original/codebook.c')) == '0cfcbdadd7a491bc6bb7c24a2e7d3ed6ce9fb9360122b93631d205fcdf5ac749' and
         sha(raw(source + 'public-original/codebook.h')) == '88c0cffdfaf4ad0e9143f6c9e99ee9e6d69703ac544655c91e01ae12afcb4172' and
         sha(raw(source + 'public-original/COPYING')) == 'd2ab5758336489da61c12cc5bb757da5339c4ae9001f9bb0562b4370249af814', 'Original public source and license')
    original = raw(source + 'public-original/consumer-fragment.inc')
    ported = original.replace(b'int decode_map(', b'static int public_decode_map(').replace(b'void *ptr=s->q_val+', b'void *ptr=(unsigned char *)s->q_val+')
    need(ported == raw(source + 'consumer_port.inc'), 'Only two pre-existing declared public port changes')
    contract = obj(runtime + 'contract.json'); model = contract['model']
    need(contract['contract_sha256'] == sha(json.dumps(model, sort_keys=True, separators=(',', ':')).encode()) == MODEL and
         (model['case_count'], model['codeword_probes'], model['vector_calls']) == (36, 123, 365), 'Raw contract versus canonical model identity')
    saved = {name: sys.modules.get(name) for name in ('oracle', 'protocol')}
    try:
        oracle = module('oracle', source + 'oracle.py', ORACLE); sys.modules['oracle'] = oracle
        protocol = module('protocol', source + 'protocol.py', PROTOCOL); sys.modules['protocol'] = protocol
        materialize = module('baseline_pure_materialize', source + 'materialize.py', sha(raw('provenance/materialize.py')))
        host_functions = module('baseline_pure_host_functions', source + 'run_host.py', sha(raw('provenance/run_host.py')))
        inputs = obj(source + 'fixture-inputs.json'); cases, setups = [], []
        for ci, row in enumerate(inputs['cases']):
            original_setup = raw(source + safe(row['setup'])); need(sha(original_setup) == row['setup_sha256'], 'Each original raw setup source')
            setup, edits = oracle.patch_zero_fields(original_setup, row['book_index'], row['overrides'])
            points = (-8, -24) if 'floor0-even6-' in row['id'] else (0, -8, -24)
            description = oracle.describe(setup, row['book_index'], points); host_table = materialize.host_table(description)
            cases.append(dict(index=ci, id=row['id'], input=row, materialized_setup_sha256=sha(setup), zero_field_edits=edits,
                book=description, host_table_hex=host_table.hex(), host_table_is_independent_owned_format=True, host_table_claimed_target_publication=False))
            setups.append(setup)
        need(cases == model['cases'] and len(cases) == 36 and sum(len(c['book']['probes']) for c in cases) == 123 and
             sum(len(c['book']['probes']) * len(c['book']['points']) for c in cases) == 365, 'Full raw-book/Fraction/scaled quantization oracle reconstruction')
        need([c['index'] for c in cases if c['input']['unit_only_new_book']] == [34, 35] and sum(len(c['zero_field_edits']) for c in cases) == 3, 'Two unit-only zero-field variants, three declared field replacements')
        header = raw(runtime + 'project/main/consumer_data.h'); need(materialize.render(model, setups) == header, 'All123 C probe rows,365 point vectors and every C descriptor/array byte')
        for ci, setup in enumerate(setups):
            match = re.search(rb'static const uint8_t raw_' + str(ci).encode() + rb'\[\] = \{([0-9,]+)\};', header)
            need(match is not None and bytes(map(int, match[1].split(b','))) == setup, 'Independent complete raw36 C-array recovery')
        verify_campaigns(m, plan, raw, obj, text, identity, module, protocol, host_functions, contract, model, source, runtime, controller)
    finally:
        for name, old in saved.items():
            if old is None: sys.modules.pop(name, None)
            else: sys.modules[name] = old
    print(json.dumps(dict(result='BASELINE_ARCHIVE_VERIFIED', SDK_publications=36, SDK_Fraction_exact=365, SDK_protocol_events=439,
        host_Fraction_exact=331, host_UBSan_NONPASS=34, host_sanitizers_qualified=False, standalone=True,
        guard_proposal_only=True, prior_target_PCM_replayed=False, full_standard_qualified=False, vendor_cause_diagnosed=False,
        full_G6_qualified=False, physical_device=False, production_radio_integration=False)))


def verify_campaigns(m, plan, raw, obj, text, identity, module, protocol, host_functions, contract, model, source, runtime, controller):
    def receipt(entry, code):
        value = obj(entry['key']); actual = value.get('exit_code', value.get('returncode'))
        need(type(actual) is int and actual == code and (value.get('status') == 'TERMINAL' or value.get('schema') == 'direct-exec-tool-terminal-v1'), 'Actual owned parent terminal')
        if value.get('status') == 'TERMINAL': need(type(value['owned_pid']) is int and value['owned_pid'] > 0 and not value.get('timed_out', False) and not value.get('interrupted', False), 'Owned normal parent status')
        need(set(entry['log_keys']) == set(value.get('logs', {})), 'Every parent stream retained')
        for origin, fact in value.get('logs', {}).items(): identity(entry['log_keys'][origin], fact['sha256'], fact['bytes'])
        if 'executable_sha256' in value: identity(entry['tool_key'], value['executable_sha256'])
        return value
    need(set(m['campaigns']) == {'SDK', 'host'} and [r['role'] for r in plan['roles']] == ['SDK', 'host'], 'Both separate baseline roles')
    for role in plan['roles']:
        info = m['campaigns'][role['role']]; need(info['prefix'] == 'campaigns/' + role['role'] and win(info['historical_root']) == win(role['path']), 'Exact role association')
        identity(info['prefix'] + '/report.json', role['report_sha256']); need(role['report_sha256'] == REPORTS[role['role']], 'Pinned actual baseline report')
        identity(info['outer']['key'], role['terminal_sha256']); receipt(info['outer'], role['expected_exit_code'])
    sdk, hostprefix = 'campaigns/SDK/', 'campaigns/host/'
    r, host = obj(sdk + 'report.json'), obj(hostprefix + 'report.json'); role = m['campaigns']['SDK']; hrole = m['campaigns']['host']
    terminal = obj(role['outer']['key'])
    need((terminal['session_id'], terminal['terminal_chunk_id'], terminal['exit_code']) == (90202, 'ba4727', 0) and
         terminal['report_sha256'] == REPORTS['SDK'] and terminal['entrypoint_sha256'] == ENTRYPOINT, 'Actual direct SDK terminal0')
    need(r['schema'] == 'public-book-consumer-SDK-runtime-v1' and r['result'] == 'PUBLIC_BOOK_CONSUMER_SDK_DIAGNOSTICS_RECORDED' and
         r['numerical_result'] == 'EXACT_FRACTION_EQUAL' and r['unequal_calls'] == 0 and
         all(r[k] is True for k in ('completed', 'source_compile_link_qualified', 'actual_canonical_SDK_publication_completed', 'complete_Fraction_comparison', 'all_Fraction_vectors_equal', 'declared_inputs_tools_configs_unchanged')) and
         all(r[k] is False for k in ('host_sanitizers_qualified', 'public_arithmetic_portability_qualified', 'full_standard_qualified', 'vendor_cause_diagnosed', 'vendor_backend_qualified', 'PCM_qualified', 'full_G6_qualified', 'physical_qualified', 'production_radio_integration')) and
         r['host_sanitizer_facts'] == 'NOT_EVALUATED_BY_THIS_SDK_CONTROLLER', 'Separate exact SDK publication/Fraction facts, no host or broader pass')
    need((r['source_readiness_sha256'], r['generated_runtime_readiness_sha256'], r['readiness_sha256'], r['contract_file_sha256'], r['canonical_model_sha256']) == (SOURCE, RUNTIME, CONTROLLER, CONTRACT, MODEL), 'Exact separate source/runtime/model/file identities')
    need(set(role['input_keys']) == set(r['inputs']) and set(role['tool_keys']) == set(r['tools']), 'Every declared SDK input/tool')
    aliases = {win(origin): key for origin, key in role['input_keys'].items()}; need(len(aliases) == len(role['input_keys']), 'Unambiguous normalized input paths')
    for origin, fact in r['inputs'].items():
        need(role['input_keys'][origin] == sdk + safe(fact['snapshot']), 'Original path to exact frozen snapshot association')
        identity(role['input_keys'][origin], fact['sha256'], fact['bytes'])
    def frozen(path, digest=None, size=None):
        key = aliases[win(path)]
        if digest is not None: identity(key, digest, size)
        return raw(key)
    for origin, digest in r['tools'].items(): identity(role['tool_keys'][origin], digest)
    for name, digest in r['build_outputs'].items(): identity(sdk + safe(name), digest)
    need(sha(raw(sdk + 'sources/run-public-book-consumer.py')) == ENTRYPOINT and sha(raw(sdk + 'sources/owned_qmp.py')) == QMP and
         raw(sdk + 'sources/project/main/consumer_unit.c') == raw(runtime + 'project/main/consumer_unit.c') and
         raw(sdk + 'sources/project/main/consumer_data.h') == raw(runtime + 'project/main/consumer_data.h') and
         raw(sdk + 'sources/project/main/consumer_port.inc') == raw(runtime + 'project/main/consumer_port.inc'), 'Exact executed controller/C baseline')
    need([row['name'] for row in r['commands']] == COMMANDS, 'Every actual14 SDK commands')
    commands = {row['name']: row for row in r['commands']}
    for row in r['commands']:
        need(row['state'] == 'complete' and type(row['pid']) is int and row['pid'] > 0 and row['exit_status'] == 0 and
             all(row[k] is False for k in ('timed_out', 'interrupted', 'force_stopped')), 'Actual14 owned normal command terminals')
        if row['name'] != 'qemu':
            for stream in ('stdout', 'stderr'): identity(sdk + row['name'] + '.' + stream + '.log', row[stream + '_sha256'])
    for action in ('configure', 'build'):
        child = obj(sdk + 'sdk-' + action + '-process.json'); env = obj(sdk + action + '-compiler-environment.json')
        need(child['action'] == action and child['terminal'] is True and child['exit_status'] == 0 and type(child['pid']) is int and child['pid'] > 0 and
             child['pid'] != commands['sdk-' + action + '-launcher']['pid'] and win(child['cwd']) == win(role['historical_root']), 'Separate actual SDK child terminal0')
        need(r['tools'][str(PureWindowsPath(child['argv'][0]))] == '0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14', 'Actual SDK Python tool identity')
        need(set(env) == {'PATH', 'IDF_PATH', 'IDF_TOOLS_PATH', 'IDF_PYTHON_ENV_PATH'} and 'v6.0.2' in env['IDF_PATH'], 'Actual activated SDK environment')
    need(obj(sdk + 'configure-compiler-identity.json') == obj(sdk + 'build-compiler-identity.json'), 'Compiler/nm/ninja identity stable')
    for suffix in ('', '-after'):
        need(text(sdk + 'sdk-head' + suffix + '.stdout.log').strip() == SDK and not text(sdk + 'sdk-clean' + suffix + '.stdout.log').strip(), 'Actual SDK clean/head before and after')
    need(r['compiler_diagnostics'] == {'stdout': [], 'stderr': []} and not re.search(r'\b(?:warning:|error:)', text(sdk + 'sdk-build.stdout.log') + text(sdk + 'sdk-build.stderr.log')), 'Actual retained compiler diagnostics zero')
    context = r['compile_context']; rows = obj(sdk + 'build/compile_commands.json'); desc = obj(sdk + 'build/project_description.json')
    support = module('pure_archived_compile_context', 'compile_context.py', sha(raw('compile_context.py')))
    need(context['actual_row'] in rows and desc['project_name'] == 'cyd_vorbis_owned_book_unit' and not any('esp_audio' in n for n in desc['build_components']), 'Actual single-own-TU compile/component context')
    project = win(role['historical_root']) / 'sources/project'; unit = project / 'main/consumer_unit.c'; build = win(role['historical_root']) / 'build'
    own = [row for row in rows if (win(row['directory']) / row['file']).is_relative_to(project)]
    need(len(own) == 1 and win(own[0]['directory']) / own[0]['file'] == unit and own[0] == context['actual_row'], 'Exactly one own compiled C unit')
    original = context['actual_row'].get('arguments') or support.windows_args(context['actual_row']['command'])
    need(original == context['original_argv'] and win(context['actual_row']['directory']) == win(context['cwd']) and
         '-fno-inline' in original and '-ffunction-sections' in original and '-fdata-sections' in original, 'Exact real compiler argv and baseline flags')
    reduced, i = [original[0]], 1
    while i < len(original):
        if original[i] == '-c': i += 1
        elif original[i] == '-o': i += 2
        else: reduced.append(original[i]); i += 1
    need(context['macro_argv'] == reduced + ['-E', '-dM'] and context['dependency_argv'] == reduced + ['-M'], 'Real same-source macro/dependency probes')
    generated = [win(context['cwd']) / arg[1:] for arg in original if arg.startswith('@')]
    need(generated == [build / 'toolchain/cflags'], 'Exact one generated response path')
    cflags = frozen(generated[0]).decode().splitlines(); specs = build / 'specs/picolibc.specs'
    need(cflags == ['-Wno-frame-address', '-mlongcalls', '-fno-builtin-memcpy', '-fno-builtin-memset', '-fno-builtin-bzero', '"-specs=' + specs.as_posix() + '"'] and frozen(specs), 'Frozen six-line cflags/specs context')
    before = text(sdk + 'unit-macros-before.stdout.log'); need(before == text(sdk + 'unit-macros-after.stdout.log'), 'Exact macros before/after')
    macros = dict(re.findall(r'^#define ([A-Za-z_0-9]+)(?: (.*))?$', before, re.M))
    need(context['expected_macros'] == MACROS and all(macros.get(k) == v for k, v in MACROS.items()) and 'CONFIG_FREERTOS_UNICORE' not in macros, 'Actual ILP32/Xtensa/SMP/core0 stack16384')
    identity(sdk + 'unit-macros-before.stdout.log', context['macros_before_sha256'])
    deptext = text(sdk + 'unit-dependencies-before.stdout.log'); need(deptext == text(sdk + 'unit-dependencies-after.stdout.log'), 'Full raw GCC dependency walk unchanged')
    deps = support.dependency_rows(deptext, context['cwd']); actual = context['actual_dependencies']
    need([win(p) for p in deps] == [win(row['path']) for row in actual] and actual, 'Every actual GCC row in original order, including repetitions')
    needed = {unit, project / 'main/consumer_data.h', project / 'main/consumer_port.inc', project / 'main/pinned/production/vorbis_repair/setup.c', project / 'main/pinned/production/vorbis_repair_abi.h', build / 'config/sdkconfig.h'}
    needed.update(project / 'main/pinned/codec/include' / name for name in ('esp_audio_types.h', 'decoder/esp_audio_dec.h', 'decoder/esp_audio_dec_reg.h', 'decoder/impl/esp_vorbis_dec.h'))
    need(needed <= set(map(win, deps)), 'All actual unit/public consumer/parser/ABI/declaration include dependencies')
    for row in actual: frozen(row['path'], row['sha256'], row['bytes'])
    symbols = text(sdk + 'symbols.stdout.log')
    for symbol in ('repair_vorbis_book_unpack', 'repair_vorbis_book_clear', 'decode_packed_entry_number', 'public_decode_map', 'app_main'):
        need(re.search(r'^[0-9a-f]+\s+[0-9a-f]+\s+[tT]\s+' + symbol + r'$', symbols, re.M), 'Actual retained own parser/public consumer symbol')
    need(not any(BAD_SYMBOL.fullmatch(line.split()[-1]) for line in symbols.splitlines() if line.split()), 'No linked vendor/full-stream decoder/open/register/wrapper symbols')
    maptext = text(sdk + 'build/cyd_vorbis_owned_book_unit.map'); link = text(sdk + 'ninja-commands.stdout.log')
    need('consumer_unit.c.obj' in maptext and 'public_decode_map' in maptext and 'repair_vorbis_book_unpack' in maptext and
         not BAD_LINK.search(maptext + link + json.dumps(rows)) and '--gc-sections' in link and 'consumer_unit.c' in link, 'Actual own link/map and no decoder archives')
    elfkey = sdk + 'build/cyd_vorbis_owned_book_unit.elf'; elf = m['omitted'][elfkey]; header = raw(elf['elf_header_key'])
    need(len(header) == 64 and header[:7] == b'\x7fELF\x01\x01\x01' and struct.unpack_from('<H', header, 18)[0] == 94 and
         m['files'][elf['elf_header_key']]['derived_from_full_sha256'] == elf['sha256'], 'Actual own ELF32/Xtensa94 header with omitted body hash')
    recipe = obj(sdk + 'build/flasher_args.json')
    need({k:recipe['flash_settings'][k] for k in ('flash_mode', 'flash_size', 'flash_freq')} == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m') and
         {int(k, 0): safe(v) for k, v in recipe['flash_files'].items()} == {0x1000:'bootloader/bootloader.bin', 0x8000:'partition_table/partition-table.bin', 0x10000:'cyd_vorbis_owned_book_unit.bin'}, 'Actual DIO40/4MB 1000/8000/10000 flash recipe')
    need(m['omitted'][sdk + 'qemu-flash.bin']['bytes'] == 4 * 1024 * 1024, 'Actual isolated padded snapshot image')
    q = commands['qemu']; need(all(q[k] is True for k in ('complete_observed', 'qmp_capabilities_acknowledged', 'qmp_quit_acknowledged', 'owned_shutdown_observed', 'stdout_eof_observed', 'reader_joined', 'lifecycle_qualified')), 'Actual complete QMP/EOF/join lifecycle')
    need(q['actual_started_time_ns'] < q['actual_terminal_time_ns'] and q['exit_status'] == 0, 'Actual owned child exit0 after start')
    for key in ('qemu.serial.log', 'qemu.stderr.log', 'qemu.qmp.stdout.log', 'qemu.qmp.requests.jsonl'): identity(sdk + key, q[key]['sha256'], q[key]['bytes'])
    messages = [json.loads(line) for line in text(sdk + 'qemu.qmp.stdout.log').splitlines() if line.strip()]
    requests = [json.loads(line) for line in text(sdk + 'qemu.qmp.requests.jsonl').splitlines() if line.strip()]
    need(messages == [row['message'] for row in q['qmp_messages']] and len(messages) == 4 and isinstance(messages[0]['QMP']['version'], dict) and isinstance(messages[0]['QMP']['capabilities'], list), 'Actual raw QMP greeting/messages')
    need(requests == q['qmp_requests'] and [row['message'] for row in requests] == [{'execute':'qmp_capabilities','id':'owned-capabilities'}, {'execute':'quit','id':'owned-quit'}], 'Only own actual capabilities/quit requests')
    need({msg['id'] for msg in messages if 'return' in msg and msg['return'] == {}} == {'owned-capabilities', 'owned-quit'} and
         [msg['data'] for msg in messages if msg.get('event') == 'SHUTDOWN'] == [{'guest':False,'reason':'host-qmp-quit'}], 'Actual both acknowledgements and non-guest host shutdown')
    argv = q['argv']; need(argv[argv.index('-serial')+1] == 'file:' + str(win(role['historical_root']) / 'qemu.serial.log') and
         argv[argv.index('-qmp')+1] == 'stdio' and argv[argv.index('-nic')+1] == 'none' and argv[argv.index('-audiodev')+1] == 'none,id=quiet' and
         argv[argv.index('-display')+1] == argv[argv.index('-monitor')+1] == 'none' and '-snapshot' in argv and '-no-reboot' in argv, 'Owned scoped serial/QMP without network/audio/display')
    serial = raw(sdk + 'qemu.serial.log'); need(sha(serial[:q['serial_bytes_at_complete']]) == q['serial_sha256_at_complete'], 'Actual serial prefix observed at COMPLETE')
    observed = protocol.validate_sdk(text(sdk + 'qemu.serial.log') + '\n' + text(sdk + 'qemu.stderr.log'), contract)
    need(observed == r['observed'] and observed['protocol_events'] == 439 and len(observed['fields']) == 36 and len(observed['vectors']) == 365 and
         observed['complete_Fraction_comparison'] is observed['all_Fraction_vectors_equal'] is observed['actual_canonical_SDK_publication_completed'] is True and observed['host_sanitizers_qualified'] is False, 'Complete439/36/365 actual publication/Fraction replay after real terminal0')
    verify_host(m, plan, raw, obj, text, identity, receipt, host, hostprefix, host_functions, protocol, model)


def verify_host(m, plan, raw, obj, text, identity, receipt, host, prefix, host_functions, protocol, model):
    need(host['schema'] == 'public-book-consumer-host-diagnostic-v1' and host['result'] == 'BASELINE_DIAGNOSTICS_RECORDED' and
         host['completed'] is host['host_consumer_diagnostics_completed'] is True and
         all(host[k] is False for k in ('host_sanitizers_clean', 'complete_Fraction_comparison', 'all_Fraction_vectors_equal',
             'actual_canonical_SDK_publication_completed', 'public_arithmetic_portability_qualified', 'full_standard_qualified', 'vendor_cause_diagnosed')),
         'Host331 exact plus34 sanitizer NONPASS remain separate from SDK')
    need(host['runtime_readiness_sha256'] == RUNTIME and host['compiler_sha256'] == '1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26' and
         re.fullmatch('[0-9a-f]{64}', host['host_python_sha256']) and host['host_python_path'].startswith('/usr/'), 'Recorded independent WSL compiler/Python identities; no live tool fallback')
    identity(prefix + 'consumer-baseline', host['host_binary_sha256']); need(prefix + 'consumer-baseline' in m['omitted'], 'Own host binary body hash-only')
    host_binary = m['omitted'][prefix + 'consumer-baseline']; host_header = raw(host_binary['elf_header_key'])
    need(len(host_header) == 64 and host_header[:7] == b'\x7fELF\x02\x01\x01' and struct.unpack_from('<H', host_header, 18)[0] == 62 and
         m['files'][host_binary['elf_header_key']]['derived_from_full_sha256'] == host_binary['sha256'], 'Actual own ELF64/x86_64 header separate from target ELF32/Xtensa')
    need(m['recorded_external_tools'] == {
        host['commands'][0]['argv'][0]: dict(sha256=host['compiler_sha256'], evidence_source=prefix + 'report.json', new_Windows_rehash=False, body_omitted=True),
        host['host_python_path']: dict(sha256=host['host_python_sha256'], evidence_source=prefix + 'report.json', new_Windows_rehash=False, body_omitted=True)},
        'Linux compiler/Python are recorded external tool hashes; no Windows path fallback or invented rehash')
    flags = ['-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-fno-pie','-no-pie']
    need(host['compile_flags'] == flags and len(host['commands']) == 366 and len(host['records']) == 365, 'Complete original sanitizer flags and366/365 inventory')
    def wsl(path):
        value = win(path); return '/mnt/' + value.drive[0].lower() + value.as_posix()[2:]
    runtime_path = wsl(next(row['path'] for row in plan['preparations'] if row['name'] == 'runtime'))
    host_path = wsl(m['campaigns']['host']['historical_root']); main = runtime_path + '/project/main'
    compile_row = host['commands'][0]
    need(compile_row['name'] == 'compile' and compile_row['argv'] == ['/usr/bin/x86_64-linux-gnu-gcc-13', *flags, '-I', main, main + '/consumer_unit.c', '-o', host_path + '/consumer-baseline'] and
         compile_row['returncode'] == 0, 'Actual exact sanitizer compile source/output/profile')
    logkeys = set()
    for row in host['commands']:
        need(row['terminal'] is True and row['timed_out'] is row['interrupted'] is False and row['cwd'] == runtime_path and
             isinstance(row['elapsed_seconds'], (int,float)) and row['elapsed_seconds'] >= 0 and type(row['returncode']) is int, 'Every actual host child terminal without timeout/interruption')
        for stream in ('stdout', 'stderr'):
            fact = row[stream]; need(fact['path'] == row['name'] + '.' + stream + '.log', 'Actual child stream path')
            identity(prefix + safe(fact['path']), fact['sha256'], fact['bytes']); logkeys.add(prefix + safe(fact['path']))
    need(len(logkeys) == 732 and logkeys == {key for key in m['files'] if key.startswith(prefix) and '/' not in key[len(prefix):] and key.endswith(('.stdout.log','.stderr.log'))}, 'Every732 host child stream, no subset')
    need(not raw(prefix + compile_row['stdout']['path']) and not raw(prefix + compile_row['stderr']['path']), 'Actual clean sanitizer compile diagnostics')
    cursor = 0; clean = 0; failures = []; failure_cases = Counter()
    for ci, case in enumerate(model['cases']):
        b = case['book']
        for pi, probe in enumerate(b['probes']):
            for qi, point in enumerate(b['points']):
                record = host['records'][cursor]; row = host['commands'][cursor+1]; cursor += 1
                name = f'case{ci:02d}-probe{pi:02d}-point{qi}'
                need(row['name'] == record['command'] == name and row['argv'] == [host_path + '/consumer-baseline', str(ci), str(pi), str(qi)] and
                     (record['case'],record['probe'],record['point'],record['wire_scope']) == (ci,pi,point,probe['wire_scope']), 'Every complete ordered original child operand/point/tolerance scope')
                stdout, stderr = raw(prefix + row['stdout']['path']), raw(prefix + row['stderr']['path'])
                if record['comparison'] is not None:
                    comparison = protocol.vector(stdout.decode().strip(), model, -1)
                    need(comparison == record['comparison'] and (comparison['case'],comparison['probe'],comparison['point']) == (ci,pi,point) and comparison['equal'] is True and row['returncode'] == 0 and not stderr and
                         record['sanitizer_clean'] is host_functions.sanitizer_clean_scope(row, stderr, comparison) is True, 'Every331 available host vector fully exact and sanitizer-clean')
                    clean += 1
                else:
                    line, exponent = (139, point-b['q_minp']) if b['q_min'] == 0 else (145, point-b['q_delp'])
                    need(ci in (32,34,35) and (b['q_min'] == 0 or b['q_del'] == 0) and exponent >= 32 and row['returncode'] == 1 and not stdout and
                         record['sanitizer_clean'] is False and host_functions.sanitizer_clean_scope(row, stderr, None) is False,
                         'Missing vector is actual public zero-field sanitizer NONPASS, never expected pass')
                    expected = main + f"/consumer_port.inc:{line}:" + ('21' if line == 139 else '33') + f": runtime error: shift exponent {exponent} is too large for 32-bit type 'int'"
                    need(stderr.decode().splitlines()[0] == expected and 'public_decode_map' in stderr.decode() and 'consumer_unit.c:103' in stderr.decode(), 'Exact owned public-C zero-shift diagnostic and original source locations139/145')
                    failures.append(dict(case=ci,probe=pi,point=point,line=line,exponent=exponent)); failure_cases[ci] += 1
    need(cursor == 365 and clean == 331 and len(failures) == 34 and dict(failure_cases) == {32:4,34:15,35:15}, 'Full331+34 classification, not334 or subset success')
    need(len(m['extra_receipts']) == len(plan['extra_receipts']) == 2, 'Actual26 controls and materialization')
    for selected, entry in zip(plan['extra_receipts'],m['extra_receipts']):
        identity(entry['key'],selected['sha256']); actual = receipt(entry,selected['expected_exit_code'])
        if 'controls' in PureWindowsPath(selected['path']).name:
            stderr_key = next(key for origin,key in entry['log_keys'].items() if origin.endswith('stderr.log'))
            need(re.search(rb'Ran 26 tests\b.*\bOK\b',raw(stderr_key),re.S), 'Actual full26 passing controls, not rerun')
    need(len(m['extra_files']) == len(plan['extra_files']), 'All separately pinned factual notes/runner sources')
    for selected, key in zip(plan['extra_files'], m['extra_files']): identity(key, selected['sha256'])
    summary_key = next(key for key in m['extra_files'] if key.endswith('root-baseline-summary-01.json')); summary = obj(summary_key)
    need(sha(raw(summary_key)) == '23739ac9796722e3fdeff1c6f9f1a2467f9c3b4aced934eec7bc3e6d6f646732' and summary['report_sha256'] == REPORTS['host'] and
         (summary['actual_host_commands'],summary['actual_host_probe_calls'],summary['available_exact_Fraction_vectors'],summary['sanitizer_aborted_without_vector']) == (366,365,331,34) and
         summary['full_host_comparison_qualified'] is summary['actual_SDK_executed'] is summary['opaque_vendor_cause_diagnosed'] is False and summary['baseline_never_relabelled_expected_PASS'] is True,
         'Historical pre-SDK root summary remains unchanged, separate from later actual SDK fact')
    proposal = obj('preparations/proposal-only/readiness.json'); analysis = obj('preparations/proposal-only/source-analysis.json')
    need(proposal['source_only'] is proposal['proposal_only'] is True and proposal['source_agent_new_consumer_or_target_execution'] is False and
         analysis['proposed_diff_only'] is True and all(analysis[k] is False for k in ('guarded_C_source_or_runtime_written','production_or_ABI_changed','baseline_results_rewritten','missing_vectors_treated_as_expected_PASS','opaque_vendor_effect_or_cause_known')),
         'Earlier completed analysis/diff remains proposal-only, no guarded successor execution claim')
    need(len(m['record_only']) == len(plan['record_only']) and len(m['record_only']) >= 3, 'Finite prior result metadata only')
    for selected, key in zip(plan['record_only'], m['record_only']):
        need(selected['record_only'] is selected['inputs_not_traversed'] is True and key.startswith('record-only/'), 'No prior result input or target PCM replay')
        identity(key,selected['sha256'])


if __name__ == '__main__': main()
