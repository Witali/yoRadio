"""Offline owned-VQ evidence replay through explicitly pinned pure definitions.

No saved main, SDK, compiler, QEMU, decoder or original-path filesystem runs.
"""
from pathlib import Path, PurePosixPath
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from functools import lru_cache
from fractions import Fraction
from types import SimpleNamespace
import ast
import gzip
import hashlib
import json
import math
import posixpath
import re
import struct

def need(ok, reason):
    if not ok: raise ValueError(reason)
def sha(data): return hashlib.sha256(data).hexdigest()
def norm(value): return str(value).replace('\\', '/').rstrip('/')
def safe(value):
    need(isinstance(value, str) and value and norm(value) == value and ':' not in value and
         not PurePosixPath(value).is_absolute() and all(p not in ('', '.', '..') for p in value.split('/')), 'safe archive alias')
    return value
ROOT = Path(__file__).resolve().parent
M = json.loads((ROOT/'manifest.json').read_bytes()); FILES, OBJECTS = M['files'], {}
need(M['schema'] == 'vorbis-quantization-evidence-v1' and M['complete'] is True and M['selected_sources_unchanged'] is True and
     all(M[k] is False for k in ('whole_dependency_closure', 'full_floor0_qualified', 'full_G6_qualified', 'PCM_qualified',
         'production_radio_integration', 'physical_device')), 'finite archive scope')
for alias, pin in FILES.items():
    safe(alias)
    need(type(pin['bytes']) is int and pin['bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', pin['sha256']) and
         pin['object'] == 'objects/'+pin['sha256']+'.gz', 'content-address declaration')
    if pin['object'] not in OBJECTS: OBJECTS[pin['object']] = gzip.decompress((ROOT/pin['object']).read_bytes())
    data = OBJECTS[pin['object']]; need(len(data) == pin['bytes'] and sha(data) == pin['sha256'], 'saved body '+alias)
need(M['aliases'] == len(FILES) and M['objects'] == len(OBJECTS), 'archive accounting')
need({p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == set(OBJECTS)|
     {'manifest.json', 'verifier.py', 'README.md', 'CHECKPOINT.md', '.gitattributes'}, 'exact physical inventory')
def raw(alias): return OBJECTS[FILES[safe(alias)]['object']]
def obj(alias): return json.loads(raw(alias))
def text(alias): return raw(alias).decode('utf-8', errors='replace').replace('\r\n', '\n')
for name in ('verifier.py', 'README.md', 'CHECKPOINT.md', '.gitattributes'):
    need((ROOT/name).read_bytes() == raw(name), 'physical root body')
for key, row in M['origins'].items():
    need(key == norm(row['path']).casefold(), 'original path identity')
    if 'alias' in row: need(sha(raw(row['alias'])) == row['sha256'] and len(raw(row['alias'])) == row['bytes'], 'original saved body')
    else: need(row in M['omissions'].values() and bool(row['reason']), 'explicit identity-only omission')
for alias, row in M['omissions'].items():
    safe(alias); need('alias' not in row and M['origins'][norm(row['path']).casefold()] == row, 'omission ledger')
CHECKOUT = norm(M['checkout'])
expected_groups = {name: '.build/vorbis-quantization-'+name+'-20261025-01' for name in ('host', 'validation', 'esp32', 'esp32c3')}
expected_groups.update(math='.build/vorbis-quantization-reference-20261025-01',
    oldangle='.build/vorbis-quantization-angle-regression-20261025-01', oldcoeff='.build/vorbis-quantization-coefficient-regression-20261025-01',
    anglebaseline='.build/vorbis-floor0-angles-host-20261025-01', coeffbaseline='.build/vorbis-floor0-numeric-host-20261025-01')
need(M['groups'] == expected_groups, 'exact selected campaign origins')
def original(path, digest, size=None, required=True):
    row = M['origins'].get(norm(path).casefold())
    need(row is not None and row['sha256'] == digest and (size is None or row['bytes'] == size), 'recorded original identity '+norm(path))
    need(not required or 'alias' in row, 'required saved body')
    return raw(row['alias']) if 'alias' in row else None
def resolve(value):
    value = norm(value); return posixpath.normpath(value if re.match(r'^[A-Za-z]:/', value) else CHECKOUT+'/'+value)
def argument(argv, flag):
    need(argv.count(flag) == 1 and argv.index(flag)+1 < len(argv), 'unique argument '+flag)
    return argv[argv.index(flag)+1]
WRAPPER = '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e'
PYTHON = '4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a'
ORACLE = 'bf5d0c1097fd1ef2f167f078e7c7204f3ebe6dd6e062ae20cadc739cd6f91e74'
CONTROL = '34a6010c57bf37f3a484fc741364f054e6c7162b55920f144fe5fc0d00ce2754'
CERTIFICATE = '46730e6caa94c3dcb421a88fab4f60c1cae9bdf5cf9636cb34ecbf3ee4d30c7c'
CHECKER = 'd47755999c3a2aded4f1a8eabb11cb8ac2db2f09f05040b4cd55c3f4b09e3a4f'
MODULE = {'floor0.c': '297e055a68ff2ee4ea71e0879aef12456139945015d346b2a12a18db7b0a4335',
    'quant.c': '14e6b7eb910ee4c7a67ff0b1eccf8f4038315d1bf5821ad51fba32824e5ffb40',
    'include/native_vorbis_floor0.h': '122ee70ab248c5aa3a46354288be3d78418e6d5e67f15c4d44d43f5ff704c63b',
    'include/native_vorbis_quant.h': '55948c2a9af4d92e2ebe614398fd09708c454b4a6f179b602d964f06aac9a499',
    'CMakeLists.txt': 'a907f471c7712d6021606dcc6a61bae23cd43127b407e8ffca9a27ce0ae4cf8b'}
need(sha(raw('canonical/.build/cyd-vorbis-format-command-01.py')) == WRAPPER and
     sha(raw('canonical/tests/check-vorbis-quantization.py')) == CHECKER, 'reviewed actual wrapper/checker')
def outer(alias, code, script, output):
    r = obj(alias)
    need(r['status'] == 'TERMINAL' and type(r['returncode']) is int and r['returncode'] == code and
         type(r['owned_pid']) is int and r['owned_pid'] > 0 and r['runner_sha256'] == WRAPPER and r['executable_sha256'] == PYTHON and
         norm(r['cwd']).casefold() == CHECKOUT.casefold() and 1 <= r['timeout_seconds'] <= 1200 and
         not r.get('timed_out') and not r.get('interrupted') and not r.get('error_type') and 'returncode_after_stop' not in r, 'actual outer terminal '+alias)
    indices = [i for i, value in enumerate(r['argv']) if resolve(value).casefold() == (CHECKOUT+'/'+script).casefold()]
    need(len(indices) == 1 and tuple(r['argv'][1:indices[0]]) in (('-B', '-X', 'utf8'), ('-B', '-Xutf8')), 'actual script invocation')
    if output is not None: need(resolve(argument(r['argv'], '--output')) == CHECKOUT+'/'+output, 'selected output argument')
    original(r['argv'][0], PYTHON, required=False); need(len(r['logs']) == 2, 'both outer streams')
    for path, pin in r['logs'].items(): original(path, pin['sha256'], pin['bytes'])
    return r
def snapshots(group, table):
    for path, pin in table.items():
        data = raw(group+'/'+safe(norm(pin['snapshot'])))
        need(sha(data) == pin['sha256'] and ('bytes' not in pin or len(data) == pin['bytes']) and
             original(path, pin['sha256'], len(data)) == data, 'actual frozen/current source identity')
def pure(alias, digest, names, constants=()):
    body = raw(alias); need(sha(body) == digest, 'exact reviewed pure helper')
    nodes, found, assigned = [], set(), set()
    for node in ast.parse(body).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names: nodes.append(node); found.add(node.name)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants:
            nodes.append(node); assigned.add(node.targets[0].id)
    need(found == set(names) and assigned == set(constants), 'exact pure closure; no main/import/path/process code')
    namespace = dict(Context=Context, Decimal=Decimal, ROUND_CEILING=ROUND_CEILING, ROUND_FLOOR=ROUND_FLOOR,
        localcontext=localcontext, lru_cache=lru_cache, Fraction=Fraction, hashlib=hashlib, json=json, math=math, re=re, struct=struct)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'reviewed-pure-saved-definitions.py', 'exec'), namespace)
    return SimpleNamespace(**namespace)
oracle = pure('canonical/tests/test-vorbis-quantization.py', ORACLE,
    ('need', 'sha', 'context', 'number', 'unpack', 'affine_value', 'integer_root', 'packet', 'read_packet', 'vector', 'exact_case',
     'pi_interval', 'pi', 'cosine', 'theta_cosine', 'scaled', 'expected_value', 'actual_value', 'floor_expected', 'check_phase_table',
     'a', 'validate_model', 'Reader', 'encode_input', 'decode_input', 'decode_output', 'expected_case', 'compare_case', 'compare_all',
     'compare_target_rows', 'target_header', 'self_checks'), ('AFFINE', 'LAYOUT', 'OPS', 'POLICY'))
control = pure('canonical/tests/run-vorbis-quantization-qemu.py', CONTROL,
    ('need', 'number', 'sequence', 'packet_model', 'validate_cases', 'validate_log'), ('PARTS', 'SDK_HEAD', 'OPS', 'AFFINE', 'LAYOUT', 'PUBLIC'))
certificate = pure('canonical/tests/vorbis_floor0_phase_certificate.py', CERTIFICATE,
    ('need', 'atan_interval', 'pi_interval', 'fraction_record', 'cf_linear_form_certificate', 'certify_source'))
for relative, digest in MODULE.items(): need(sha(raw('canonical/idf/components/native_vorbis_numeric/'+relative)) == digest, 'current module pin')
proof = certificate.certify_source(raw('canonical/idf/components/native_vorbis_numeric/floor0.c').decode('utf-8'))
need(proof == obj('validation/phase-result.json') and proof['source_sha256'] == MODULE['floor0.c'] and
     proof['full_exact_affine_nonzero_gap_exponent'] == 1904 and proof['retained_nonzero_affine_phase_significant_bits_at_least'] == 400 and
     proof['table_bits'] == 4096 and proof['phase_fraction_bits'] == 2304 and all(proof[k] is False for k in
         ('compiled_reduction_qualified', 'compiled_affine_reduction_qualified', 'libm_or_total_floating_error_qualified', 'decoder_or_PCM_qualified')),
     'full exact-rational phase proof, separate from numerical/libm qualification')
phase_outer = outer('validation/phase.json', 0, 'tests/vorbis_floor0_phase_certificate.py', M['groups']['validation']+'/phase-result.json')
need(resolve(argument(phase_outer['argv'], '--source')) == CHECKOUT+'/idf/components/native_vorbis_numeric/floor0.c', 'actual certificate source argument')
def host_receipts(group):
    r = obj(group+'/report.json'); snapshots(group, r['sources'])
    owner = ast.parse(raw(group+'/sources/'+('owned-supervisor-source.py' if group == 'oldcoeff' else 'supervisor-owner.py')))
    values = [n.value for n in owner.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SUPERVISOR' for t in n.targets)]
    need(len(values) == 1 and ast.literal_eval(values[0]).encode() == raw(group+'/supervisor.py'), 'actual owned supervisor body')
    need(tuple(c['name'] for c in r['commands']) == ('compiler-version', 'compiler-machine', 'compile', 'execute'), 'four actual host commands')
    for c in r['commands']:
        prefix = group+'/'+c['name']; request, receipt = obj(prefix+'.request.json'), obj(prefix+'.receipt.json')
        need(receipt == c['supervisor'] and request['argv'] == c['child_argv'] and request['timeout'] == 60 and
             receipt['request_sha256'] == sha(raw(prefix+'.request.json')) and receipt['nonce'] == request['nonce'] == c['nonce'] and
             receipt['state'] == 'terminal' and receipt['child_returncode'] == 0 and all(receipt[k] is True for k in
             ('final', 'new_session', 'child_reaped', 'group_gone')) and type(receipt['child_pid']) is int and receipt['child_pid'] > 0 and
             receipt['owned_pgid'] == receipt['child_pid'] and c['transport_returncode'] == 0 and c['transport_pid'] > 0 and
             not c.get('forced_transport_stop') and 'cleanup_error' not in receipt, 'owned host terminal/session/cleanup')
        for stream in ('stdout', 'stderr'):
            need(sha(raw(prefix+'.'+stream+'.log')) == c[stream+'_sha256'], 'actual host stream')
            if c['name'] in ('compile', 'execute'): need(not raw(prefix+'.'+stream+'.log'), 'clean strict compile/sanitizer execution')
    need(all(flag in r['commands'][2]['child_argv'] for flag in ('-Werror', '-fno-fast-math', '-ffp-contract=off',
         '-fsanitize=address,undefined', '-fno-sanitize-recover=all')), 'actual sanitized compilation flags')
    return r
h = host_receipts('host'); outer('validation/host.json', 0, 'tests/test-vorbis-quantization.py', M['groups']['host'])
need(all(h[k] is True for k in ('completed', 'passed', 'prepared', 'component_executed', 'source_inputs_unchanged')) and
     (h['cases'], h['target_cases'], h['metadata_controls']) == (6572, 200, 152) and h['policy'] == oracle.POLICY and
     all(h[k] is False for k in ('full_floor0_qualified', 'full_G6_qualified', 'PCM_qualified', 'decoder_executed', 'SDK_or_QEMU_executed', 'physical_device')),
     'actual finite owned-VQ host scope')
need(raw('host/sources/test-vorbis-quantization.py') == raw('canonical/tests/test-vorbis-quantization.py') and
     raw('host/sources/driver.c') == raw('canonical/tests/native/vorbis_quantization_test.c') and
     sha(raw('host/sources/driver.c')) == '4e34f90c8a9cd6c212d8ae9b3e123bb80749f7ee80f44a85ef45845247ad3a42' and
     oracle.check_phase_table(text('host/sources/floor0.c')) == h['phase_table'] and oracle.self_checks() == h['oracle_self_checks'], 'actual independent oracle/table/adapter')
model = obj('host/cases.json'); inputs, outputs = raw('host/inputs.bin'), raw('host/outputs.bin')
need(sha(raw('host/cases.json')) == h['model_sha256'] and sha(inputs) == h['input_sha256'] and sha(outputs) == h['output_sha256'] and
     oracle.decode_input(inputs) == model and oracle.encode_input(model) == inputs, 'every original host input/model/output byte')
decoded = oracle.decode_output(outputs, model); host_measured = oracle.compare_all(model, decoded['rows'])
need(host_measured == h['numerical'] and host_measured['measurement_completed'] is True and host_measured['passed'] is h['passed'] and
     (host_measured['cases'], host_measured['exact_values'], host_measured['numerical_cases'], decoded['metadata_controls']) ==
     (6572, 79834, 92, 152), 'all6572 exact host results and92 floor results independently replayed')
target, expected = obj('host/target-cases/cases.json'), obj('host/target-cases/expected.json')
by_id = {row['id']: row for row in model['cases']}
need(len(target['cases']) == 200 and all(by_id[row['id']] == row for row in target['cases']) and
     raw('host/target-cases/cases.h').decode('ascii') == oracle.target_header(target) and expected ==
     dict(schema='native-vorbis-quantization-expected-v1', policy=oracle.POLICY, cases=[oracle.expected_case(row) for row in target['cases']]),
     'all200 predeclared mixed target cases/header/expected values')
for name, digest in h['target_input_sha256'].items(): need(sha(raw('host/target-cases/'+name)) == digest, 'predeclared target data hash')
outer('validation/protocol.json', 0, 'tests/test-vorbis-quantization-protocol.py', None)
need(sha(raw('canonical/tests/test-vorbis-quantization-protocol.py')) == 'd9cc84073271dad3588348e0a62f8c29239c88ef6454b25ef240d515130c7c05' and
     'Ran 12 tests in ' in text('validation/protocol.stderr.log') and text('validation/protocol.stderr.log').endswith('\nOK\n'), 'actual12 pure protocol methods')
# Legacy fixtures only gained frozen dependencies; these are pure protocol tests.
for label, script, methods, script_digest, controller_path, controller_digest in (('legacy-angle-protocol', 'tests/test-vorbis-floor0-angles-protocol.py', 12, '6f79caf55af7f04da92262f2b9eea6d3706507eab03a2c2c2980651d0d7daa7e', 'tests/run-vorbis-floor0-angles-qemu.py', 'd4552d2ff062a5a8f62daacb314837f73c39a1c6d91b301c55c420ac373e48e7'), ('legacy-numeric-protocol', 'tests/test-vorbis-floor0-numeric-protocol.py', 13, '0ff7adc7620a01e28f639970886f67fe0c47b5277b5d52ade3362d0f78cc9853', 'tests/run-vorbis-floor0-numeric-qemu.py', '86a4fdb9b02afb00a148b3694c3173a17af9fbbefba6d60671bc1f55cdc7082f')):
    outer('validation/'+label+'.json', 0, script, None)
    need(sha(raw('canonical/'+script)) == script_digest and sha(raw('canonical/'+controller_path)) == controller_digest and
         ('Ran '+str(methods)+' tests in ') in text('validation/'+label+'.stderr.log') and
         text('validation/'+label+'.stderr.log').endswith('\nOK\n'), 'actual legacy pure protocol suite; no new SDK qualification')
for group, receipt, helper, driver, cases, baseline, baseline_sha, input_sha, output_sha, helper_sha in (
    ('oldangle', 'angle-regression', 'test-vorbis-floor0-angles.py', 'vorbis_floor0_angles_test.c', 2376, 'anglebaseline',
     '5dfd8d4977fd70fcaac2861a2056def2926dfbbeab21da429545c1750e15c5ee',
     'a7a4ff07160dbf7ab9dea99744d4de598a71418642294c258a9241085cae56b0',
     '3e669d330efc3b02aefc727e95ff11cc2483c7872306499046c68f9a0513fb42',
     '1965f554980254900e5df6fb92ebfa2e1dd5ffa159ff9383561df33782e4a742'),
    ('oldcoeff', 'coefficient-regression', 'test-vorbis-floor0-numeric.py', 'vorbis_floor0_numeric_test.c', 60541, 'coeffbaseline',
     '8fa58dd5520887ce1bedb63ebd01e175e0a7b182908bf64fd729a86b9903539a',
     '87e8be2debd4dd9983ab9f6d8ffd5639912ce89dbe61ae42bb32f9ce263d0150',
     '475d0558e6cfbbb083bdf9a0f76b0da1dfdb0a985103c4a482dda87b2ec9e960',
     '0d3f49022a2c6c13cf8ab820b4b3aab97913fd46eb58bc70562230a14de5d088')):
    r = host_receipts(group); outer('validation/'+receipt+'.json', 0, 'tests/'+helper, M['groups'][group])
    need(all(r[k] is True for k in ('completed', 'passed', 'source_inputs_unchanged')) and r['cases'] == cases and
         sha(raw(group+'/sources/'+helper)) == helper_sha and raw(group+'/sources/driver.c') == raw('canonical/tests/native/'+driver) and
         sha(raw(baseline+'/report.json')) == baseline_sha and raw(group+'/outputs.bin') == raw(baseline+'/outputs.bin') and
         sha(raw(group+'/outputs.bin')) == r['output_sha256'] == output_sha and sha(raw(group+'/inputs.bin')) == r['input_sha256'] == input_sha,
         'prior actual receipt/source/input/output integrity and baseline byte parity only')
commands = ('sdk-head', 'sdk-clean', 'build', 'dependencies', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after')
n = obj('math/report.json'); measured = {}; rows = control.validate_cases(target, text('host/target-cases/cases.h'))
for architecture in ('esp32', 'esp32c3'):
    r = obj(architecture+'/report.json'); base = CHECKOUT+'/'+M['groups'][architecture]
    receipt = outer('validation/'+architecture+'.json', 0, 'tests/run-vorbis-quantization-qemu.py', M['groups'][architecture]); snapshots(architecture, r['inputs'])
    need(all(r[k] is True for k in ('completed', 'math_capture_completed', 'whole_module_compiled', 'source_inputs_unchanged')) and
         all(r[k] is False for k in ('passed', 'numerical_reference_compared', 'numerical_qualified', 'full_floor0_qualified', 'decoder_executed',
             'production_firmware', 'physical_device')) and r['result'] == 'CHECKED_QUANTIZATION_CAPTURED' and r['target'] == architecture,
         'complete guarded native quantization capture')
    need(raw(architecture+'/sources/controller.py') == raw('canonical/tests/run-vorbis-quantization-qemu.py'), 'actual executed frozen controller')
    for relative in MODULE: need(raw(architecture+'/sources/components/native_vorbis_numeric/'+relative) == raw('canonical/idf/components/native_vorbis_numeric/'+relative), 'actual canonical whole module')
    for name in ('cases.json', 'cases.h'): need(raw(architecture+'/sources/cases/'+name) == raw('host/target-cases/'+name), 'original native data')
    pins = {key: MODULE[relative] for key, relative in control.PARTS.items()}
    pins.update(cases=h['target_input_sha256']['cases.json'], **{'cases-header': h['target_input_sha256']['cases.h'], 'qemu': r['source_sha256']['qemu']})
    need(r['source_sha256'] == pins and all(argument(receipt['argv'], '--'+key+'-sha256') == value for key, value in pins.items()) and
         argument(receipt['argv'], '--target') == architecture and resolve(argument(receipt['argv'], '--cases')) == CHECKOUT+'/'+M['groups']['host']+'/target-cases', 'actual complete native source/data/tool invocation')
    original(argument(receipt['argv'], '--qemu'), pins['qemu'], required=False)
    need(tuple(c['name'] for c in r['commands']) == commands and r['sdk_revision'] == control.SDK_HEAD[architecture], 'all nine native commands')
    for c in r['commands']:
        need(c['state'] == 'complete' and c['exit_status'] == 0 and type(c['pid']) is int and c['pid'] > 0 and
             not c['timed_out'] and not c['interrupted'] and norm(c['cwd']) == base, 'actual native terminal')
        for stream in ('stdout', 'stderr'): need(sha(raw(architecture+'/'+c['name']+'.'+stream+'.log')) == c[stream+'_sha256'], 'actual native stream')
    for name in ('sdk-head', 'sdk-head-after'): need(text(architecture+'/'+name+'.stdout.log').strip() == control.SDK_HEAD[architecture], 'SDK before/after revision')
    for name in ('sdk-clean', 'sdk-clean-after'): need(not text(architecture+'/'+name+'.stdout.log').strip(), 'SDK before/after clean')
    for path, digest in r['tools'].items(): original(path, digest, required=False)
    for path, digest in r['project_sources'].items(): need(sha(raw(architecture+'/'+path)) == digest, 'configured project source')
    for path, digest in r['build_outputs'].items(): original(base+'/'+path, digest, required=False)
    database = obj(architecture+'/build/compile_commands.json')
    for role, path in (('fixture', base+'/project/main/main.c'), ('floor', base+'/sources/components/native_vorbis_numeric/floor0.c'),
                       ('quant', base+'/sources/components/native_vorbis_numeric/quant.c')):
        need([row for row in database if norm(row['file']) == path] == [r['compile_rows'][role]], 'actual selected compile row')
    need(all(flag in r['compile_rows'][role]['command'] for role in ('floor', 'quant') for flag in ('-fno-fast-math', '-fstack-usage')), 'actual whole-module float/frame flags')
    deps = norm(text(architecture+'/dependencies.stdout.log')).casefold()
    need(all((base+'/'+path).casefold() in deps for path in [*['sources/components/native_vorbis_numeric/'+relative for relative in MODULE if relative != 'CMakeLists.txt'],
         'project/main/cases.h']), 'actual both source/header/data dependencies')
    symbols = text(architecture+'/symbols.stdout.log')
    need(all(re.search(r'\bnative_vorbis_'+name+r'$', symbols, re.M) for name in control.PUBLIC) and
         not re.search(r'\b(?:__wrap_)?esp_vorbis_dec_(?:open|decode)$', symbols, re.M), 'actual public VQ/affine symbols; no decoder')
    frames = []; need(len(r['stack_usage']['paths']) == len(set(r['stack_usage']['paths'])) == 2, 'two module frame files')
    for path in r['stack_usage']['paths']:
        for line in text(architecture+'/'+path).splitlines():
            fields = line.rsplit('\t', 2); need(len(fields) == 3 and fields[1].isdigit(), 'actual compiler frame row')
            frames.append(dict(function=fields[0].rsplit(':', 1)[-1], bytes=int(fields[1]), qualifier=fields[2], path=path))
    need(frames == r['stack_usage']['rows'], 'both actual .su frame estimates only')
    elf_names = [path for path in r['build_outputs'] if path.endswith('.elf')]; need(len(elf_names) == 1, 'one native ELF')
    elf = raw(M['elf_headers'][architecture+'/'+elf_names[0]])
    need(elf == raw(architecture+'/elf-header.bin') and len(elf) == 52 and elf[:6] == b'\x7fELF\x01\x01' and
         struct.unpack_from('<H', elf, 18)[0] == r['elf_machine'] == (94 if architecture == 'esp32' else 243), 'actual ELF32 architecture header only')
    need(b'libesp_audio_codec.a' not in raw(architecture+'/'+elf_names[0][:-4]+'.map') and not r['build_warning_lines'], 'no vendor decoder archive or compiler warnings')
    child = obj(architecture+'/sdk-child.json'); need(child == r['sdk_child'] and child['pid'] > 0 and child['exit_status'] == 0 and 'build' in child['argv'], 'actual SDK child terminal')
    config = text(architecture+'/sdkconfig')
    need(re.search(r'^CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ='+str(240 if architecture == 'esp32' else 160)+'$', config, re.M) and
         bool(re.search(r'^CONFIG_FREERTOS_UNICORE=y$', config, re.M)) == (architecture == 'esp32c3'), 'native CPU/core configuration')
    qemu = next(c for c in r['commands'] if c['name'] == 'qemu')
    for flag, value in (('-smp', '2' if architecture == 'esp32' else '1'), ('-display', 'none'), ('-monitor', 'none'), ('-serial', 'stdio'), ('-nic', 'none')):
        need(argument(qemu['argv'], flag) == value, 'isolated QEMU '+flag)
    need('-snapshot' in qemu['argv'] and '-no-reboot' in qemu['argv'], 'controlled no-reboot snapshot')
    observed = control.validate_log(text(architecture+'/qemu.stdout.log')+'\n'+text(architecture+'/qemu.stderr.log'), rows, architecture, h['target_input_sha256']['cases.json'])
    need(observed.pop('rows') == r['rows'] and observed == r['observed'] and
         (observed['cases'], observed['protocol_lines'], observed['metadata_controls']) == (200, 1061, 152), 'every actual native event/value/guard/core')
    measured[architecture] = oracle.compare_target_rows(target, expected, r['rows'])
    need(measured[architecture] == n['targets'][architecture] and measured[architecture]['measurement_completed'] is True and
         measured[architecture]['cases'] == len(measured[architecture]['metrics']) == 200, 'all200 native exact/numerical results retained')
passed = host_measured['passed'] and all(row['passed'] for row in measured.values())
need(all(n[k] is True for k in ('completed', 'measurement_completed', 'host_numeric_recomputed')) and
     n['host_cases'] == 6572 and n['host_metadata_controls'] == 152 and n['host_passed'] is host_measured['passed'] and
     n['host_exact_values'] == 79834 and n['host_numerical_cases'] == 92 and
     n['native_cases_required'] == n['native_values_compared'] == 400 and n['passed'] is passed and
     n['native_affine_values_compared'] == sum(row['exact_values'] for row in measured.values()) and
     n['native_numerical_cases_compared'] == sum(row['numerical_cases'] for row in measured.values()) == 184 and
     n['finite_quantization_affine_qualified'] is passed and M['finite_quantization_affine_qualified'] is passed and
     n['result'] == M['numerical_result'] == ('FINITE_QUANTIZATION_AFFINE_QUALIFIED' if passed else 'FINITE_QUANTIZATION_AFFINE_REJECTED') and
     all(n[k] is False for k in ('SDK_or_QEMU_executed', 'component_executed', 'decoder_executed', 'production_radio_integration',
         'full_floor0_qualified', 'full_G6_qualified', 'PCM_qualified', 'physical_device')), 'actual complete fixed-policy measurement, without full codec qualification')
numeric_outer = outer('validation/numeric.json', 0 if passed else 1, 'tests/check-vorbis-quantization.py', M['groups']['math'])
for name in ('host', 'esp32', 'esp32c3'):
    need(resolve(argument(numeric_outer['argv'], '--'+name)) == CHECKOUT+'/'+M['groups'][name], 'actual comparison capture argument')
need(resolve(argument(numeric_outer['argv'], '--receipts')) == CHECKOUT+'/'+M['groups']['validation'], 'actual comparison receipts')
for path, pin in n['inputs'].items():
    need(original(path, pin['sha256'], pin['bytes']) == raw('math/'+safe(norm(pin['snapshot']))), 'every consumed actual comparison body')
for path, pin in n['identity_only'].items():
    need(original(path, pin['sha256'], pin['bytes'], required=False) is None and bool(pin['reason']), 'actual comparator identity-only executable')
print(json.dumps(dict(evidence_integrity_verified=True, host_cases=6572, host_exact_values=79834, host_numerical_cases=92,
    native_cases_per_architecture=200, native_cases_compared=400, native_numerical_cases=184, native_commands_per_architecture=9,
    host_metadata_controls=152, affine_phase_certificate_recomputed=True, affine_phase_gap_exponent=1904,
    prior_angle_and_coefficient_output_byte_equal=True, prior_regression_numeric_oracles_recomputed=False,
    numerical_result=n['result'], finite_quantization_affine_qualified=passed, explicit_pinned_pure_definitions_reused=True,
    full_floor0_qualified=False, full_G6_qualified=False, PCM_qualified=False, physical_device=False)))
