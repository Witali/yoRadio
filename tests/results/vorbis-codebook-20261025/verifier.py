"""Offline codebook evidence: explicitly pinned pure readers, no saved mains."""
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
import ast
import gzip
import hashlib
import json
import posixpath
import re
import struct

def need(ok, reason):
    if not ok: raise ValueError(reason)
def sha(body): return hashlib.sha256(body).hexdigest()
def norm(value): return str(value).replace('\\', '/').rstrip('/')
def safe(value):
    need(isinstance(value, str) and value and norm(value) == value and ':' not in value and not PurePosixPath(value).is_absolute() and
         all(p not in ('', '.', '..') for p in value.split('/')), 'safe saved alias'); return value
ROOT = Path(__file__).resolve().parent
M = json.loads((ROOT/'manifest.json').read_bytes()); FILES, OBJECTS = M['files'], {}
need(M['schema'] == 'vorbis-codebook-evidence-v1' and M['complete'] is True and M['selected_sources_unchanged'] is True and
     all(M[k] is False for k in ('whole_dependency_closure', 'full_floor0_qualified', 'full_G6_qualified', 'PCM_qualified', 'physical_device', 'production_radio_integration')), 'finite archive scope')
for alias, pin in FILES.items():
    safe(alias)
    need(type(pin['bytes']) is int and pin['bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', pin['sha256']) and pin['object'] == 'objects/'+pin['sha256']+'.gz', 'content-address declaration')
    if pin['object'] not in OBJECTS: OBJECTS[pin['object']] = gzip.decompress((ROOT/pin['object']).read_bytes())
    body = OBJECTS[pin['object']]; need(len(body) == pin['bytes'] and sha(body) == pin['sha256'], 'every saved body '+alias)
need(M['aliases'] == len(FILES) and M['objects'] == len(OBJECTS), 'archive accounting')
need({p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == set(OBJECTS)|{'manifest.json', 'verifier.py', 'README.md', 'CHECKPOINT.md', '.gitattributes'}, 'exact physical inventory')
def raw(alias): return OBJECTS[FILES[safe(alias)]['object']]
def obj(alias): return json.loads(raw(alias))
def text(alias): return raw(alias).decode('utf-8', errors='replace').replace('\r\n', '\n')
for name in ('verifier.py', 'README.md', 'CHECKPOINT.md', '.gitattributes'): need((ROOT/name).read_bytes() == raw(name), 'physical root body')
for key, row in M['origins'].items():
    need(key == norm(row['path']).casefold(), 'current origin path identity')
    if 'alias' in row: need(sha(raw(row['alias'])) == row['sha256'] and len(raw(row['alias'])) == row['bytes'], 'current original saved body')
    else: need(row in M['omissions'].values() and bool(row['reason']), 'explicit identity-only omission')
for alias, row in M['omissions'].items():
    safe(alias); need('alias' not in row and M['origins'][norm(row['path']).casefold()] == row, 'omission ledger')
for alias, row in M['historical_sources'].items():
    need(alias == row['alias'] and sha(raw(alias)) == row['sha256'] and len(raw(alias)) == row['bytes'] and bool(row['reason']), 'historical source stays separately identified')
CHECKOUT = norm(M['checkout'])
GROUPS = {name: '.build/vorbis-codebook-'+name+'-20261025-01' for name in ('host', 'validation', 'esp32', 'esp32c3', 'reference', 'boundaries')}
GROUPS.update({'lint-initial': '.build/vorbis-codebook-lint-20261025-01', 'lint-final': '.build/vorbis-codebook-lint-20261025-02'})
need(M['groups'] == GROUPS, 'exact selected campaign origins')
def original(path, digest, size=None, required=True):
    row = M['origins'].get(norm(path).casefold())
    need(row is not None and row['sha256'] == digest and (size is None or row['bytes'] == size), 'recorded original identity '+norm(path))
    need(not required or 'alias' in row, 'required retained original'); return raw(row['alias']) if 'alias' in row else None
def resolve(value):
    value = norm(value); return posixpath.normpath(value if re.match(r'^[A-Za-z]:/', value) else CHECKOUT+'/'+value)
def argument(argv, flag):
    need(argv.count(flag) == 1 and argv.index(flag)+1 < len(argv), 'unique actual option '+flag); return argv[argv.index(flag)+1]
WRAPPER = '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e'
PYTHON = '4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a'
ORACLE = 'e6b56ef59fd387da6f8e288e035470535f6bebcad9aef3c2e1150e7e587246a1'
CONTROL = '55ccf491adf33f98023f779d31e7cb955f46dbaf9f5b7b6e20d62a14d991b33b'
CHECKER = 'c7b002880495bbcfb117dce3a3303c4e24092ce8ab68b52ae68e73283556f1c9'
MODULE = {'floor0.c': '297e055a68ff2ee4ea71e0879aef12456139945015d346b2a12a18db7b0a4335',
    'quant.c': '14e6b7eb910ee4c7a67ff0b1eccf8f4038315d1bf5821ad51fba32824e5ffb40',
    'include/native_vorbis_floor0.h': '122ee70ab248c5aa3a46354288be3d78418e6d5e67f15c4d44d43f5ff704c63b',
    'include/native_vorbis_quant.h': '55948c2a9af4d92e2ebe614398fd09708c454b4a6f179b602d964f06aac9a499',
    'codebook.c': '51122d5d9dce8513d371764c1208641bb7b3a64a170095510705a88d900522ec',
    'include/native_vorbis_codebook.h': '4373f63fa1f3bd352b7c30720e0c9c261d5b34df799b1d0b9c8787e700fbda20',
    'CMakeLists.txt': '2b2395e6b3aa254dd4c34657291cae0be05b395a343729b66e844a6013d77638'}
need(sha(raw('canonical/.build/cyd-vorbis-format-command-01.py')) == WRAPPER and sha(raw('canonical/tests/check-vorbis-codebook.py')) == CHECKER, 'exact actual wrapper/checker')
def outer(name, code, script, output=None):
    r = obj('validation/'+name+'.json')
    need(r['status'] == 'TERMINAL' and type(r['returncode']) is int and r['returncode'] == code and type(r['owned_pid']) is int and r['owned_pid'] > 0 and
         r['runner_sha256'] == WRAPPER and r['executable_sha256'] == PYTHON and norm(r['cwd']).casefold() == CHECKOUT.casefold() and
         1 <= r['timeout_seconds'] <= 1200 and not r.get('timed_out') and not r.get('interrupted') and not r.get('error_type') and 'returncode_after_stop' not in r, 'actual outer normal terminal '+name)
    indexes = [i for i, value in enumerate(r['argv']) if resolve(value).casefold() == (CHECKOUT+'/'+script).casefold()]
    need(len(indexes) == 1 and tuple(r['argv'][1:indexes[0]]) in (('-B', '-X', 'utf8'), ('-B', '-Xutf8')), 'actual saved script invocation')
    if output is not None: need(resolve(argument(r['argv'], '--output')) == CHECKOUT+'/'+output, 'actual supplied campaign output')
    original(r['argv'][0], PYTHON, required=False); need(len(r['logs']) == 2, 'both owned outer streams')
    for path, pin in r['logs'].items(): original(path, pin['sha256'], pin['bytes'])
    return r
def snapshots(group, table):
    for path, pin in table.items():
        body = raw(group+'/'+safe(norm(pin['snapshot'])))
        need(sha(body) == pin['sha256'] and ('bytes' not in pin or len(body) == pin['bytes']) and original(path, pin['sha256'], len(body)) == body, 'all frozen/current inputs')
def pure(alias, digest, names, constants=()):
    body = raw(alias); need(sha(body) == digest, 'exact reviewed pure helper'); nodes, found, assigned = [], set(), set()
    for node in ast.parse(body).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names: nodes.append(node); found.add(node.name)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants:
            nodes.append(node); assigned.add(node.targets[0].id)
    need(found == set(names) and assigned == set(constants), 'exact pure closure; no saved imports/main/path/process functions')
    namespace = dict(hashlib=hashlib, json=json, re=re, struct=struct)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'reviewed-pure-codebook-definitions.py', 'exec'), namespace); return SimpleNamespace(**namespace)
oracle = pure('canonical/tests/test-vorbis-codebook.py', ORACLE,
    ('need', 'sha', 'Bits', 'greedy_words', 'integer_root', 'parse_setup', 'decode_one', 'vector', 'exact_case', 'validate_model',
     'Reader', 'encode_input', 'decode_input', 'decode_output', 'expected_case', 'compare_all', 'compare_target_rows', 'target_header', 'self_checks'),
    ('OPS', 'QFIELDS', 'AFFINE', 'POLICY'))
control = pure('canonical/tests/run-vorbis-codebook-qemu.py', CONTROL,
    ('need', 'sequence', 'validate_cases', 'validate_log'), ('PARTS', 'SDK_HEAD', 'OPS', 'AFFINE', 'QUANT', 'PUBLIC', 'CONTROL_COUNT'))
for relative, digest in MODULE.items(): need(sha(raw('canonical/idf/components/native_vorbis_numeric/'+relative)) == digest, 'current module pin')
h = obj('host/report.json'); snapshots('host', h['sources']); outer('host', 0, 'tests/test-vorbis-codebook.py', GROUPS['host'])
need(all(h[k] is True for k in ('completed', 'passed', 'prepared', 'component_executed', 'source_inputs_unchanged')) and
     (h['cases'], h['target_cases'], h['metadata_controls']) == (382, 200, 719) and h['policy'] == oracle.POLICY and
     oracle.self_checks() == h['oracle_self_checks'] and all(h[k] is False for k in
     ('full_floor0_qualified', 'full_G6_qualified', 'PCM_qualified', 'decoder_executed', 'SDK_or_QEMU_executed', 'physical_device')), 'actual scoped complete sanitized host campaign')
need(raw('host/sources/test-vorbis-codebook.py') == raw('canonical/tests/test-vorbis-codebook.py') and
     raw('host/sources/driver.c') == raw('canonical/tests/native/vorbis_codebook_test.c') and
     sha(raw('host/sources/driver.c')) == '5cb7b8def265b62045721f21895508c6867b51c8d007050d95fb5625c321d44e', 'actual frozen oracle/adapter')
def host_commands(group, report):
    owner = ast.parse(raw(group+'/sources/supervisor-owner.py'))
    literals = [node.value for node in owner.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SUPERVISOR' for t in node.targets)]
    need(len(literals) == 1 and ast.literal_eval(literals[0]).encode() == raw(group+'/supervisor.py'), 'actual owned supervisor body')
    need(tuple(c['name'] for c in report['commands']) == ('compiler-version', 'compiler-machine', 'compile', 'execute'), 'four owned host commands')
    for c in report['commands']:
        prefix = group+'/'+c['name']; request, receipt = obj(prefix+'.request.json'), obj(prefix+'.receipt.json')
        need(receipt == c['supervisor'] and request['argv'] == c['child_argv'] and request['timeout'] == 60 and
             receipt['request_sha256'] == sha(raw(prefix+'.request.json')) and receipt['nonce'] == request['nonce'] == c['nonce'] and
             receipt['state'] == 'terminal' and receipt['child_returncode'] == 0 and all(receipt[k] is True for k in ('final', 'new_session', 'child_reaped', 'group_gone')) and
             type(receipt['child_pid']) is int and receipt['child_pid'] > 0 and receipt['owned_pgid'] == receipt['child_pid'] and c['transport_returncode'] == 0 and
             c['transport_pid'] > 0 and not c.get('forced_transport_stop') and 'cleanup_error' not in receipt, 'actual host request/terminal/cleanup')
        for stream in ('stdout', 'stderr'):
            need(sha(raw(prefix+'.'+stream+'.log')) == c[stream+'_sha256'], 'actual host stream')
            if c['name'] in ('compile', 'execute'): need(not raw(prefix+'.'+stream+'.log'), 'clean strict compilation and sanitizer execution')
    need(all(flag in report['commands'][2]['child_argv'] for flag in ('-Werror', '-fno-fast-math', '-ffp-contract=off', '-fsanitize=address,undefined', '-fno-sanitize-recover=all')), 'actual sanitizer/floating compilation flags')
host_commands('host', h)
boundary = pure('canonical/tests/test-vorbis-codebook-boundaries.py', '2b005725ddc2994a711bfc2dff2f0131459594ec0c126f7495cdfacb7a780872', ('need', 'validate_capture'), ('POLICY', 'EXPECTED'))
b = obj('boundaries/report.json'); snapshots('boundaries', b['sources']); host_commands('boundaries', b)
outer('boundaries', 0, 'tests/test-vorbis-codebook-boundaries.py', GROUPS['boundaries'])
need(all(b[k] is True for k in ('completed', 'passed', 'prepared', 'component_executed', 'source_inputs_unchanged')) and b['policy'] == boundary.POLICY and
     b['result'] == 'HOST_CODEBOOK_BOUNDARIES_QUALIFIED' and (b['status_checks'], b['negative_cases']) == (290, 140) and
     all(b[k] is False for k in ('SDK_or_QEMU_executed', 'decoder_executed', 'full_floor0_qualified', 'full_G6_qualified', 'PCM_qualified', 'physical_device')) and
     raw('boundaries/sources/test-vorbis-codebook-boundaries.py') == raw('canonical/tests/test-vorbis-codebook-boundaries.py') and
     raw('boundaries/sources/driver.c') == raw('canonical/tests/native/vorbis_codebook_boundaries_test.c') and
     sha(raw('boundaries/sources/driver.c')) == '53171ad4b78798f52dc31dcff1e8c0d537d16ee2de4d2f5681cda67f1fb983ae' and
     sha(raw('boundaries/capture.json')) == b['capture_sha256'] and obj('boundaries/capture.json') == b['assertion_capture'] and
     boundary.validate_capture(b['assertion_capture']) == dict(passed=True, status_checks=290, negative_cases=140),
     'actual boundary C assertion/terminal/JSON integrity only; no offline C or mathematical rerun')
model = obj('host/cases.json'); inputs, outputs = raw('host/inputs.bin'), raw('host/outputs.bin')
need(sha(raw('host/cases.json')) == h['model_sha256'] and sha(inputs) == h['input_sha256'] and sha(outputs) == h['output_sha256'] and
     oracle.decode_input(inputs) == model and oracle.encode_input(model) == inputs, 'every original binary input/model/output byte')
decoded = oracle.decode_output(outputs, model); host_result = oracle.compare_all(model, decoded['rows'])
need(host_result == h['numerical'] and host_result['measurement_completed'] is True and host_result['passed'] is h['passed'] and
     tuple(host_result[k] for k in ('cases', 'words', 'decoded', 'affine_values', 'truncation_checks', 'payload_truncation_checks')) ==
     (382, 11653, 5963, 24603, 318030, 31580) and decoded['metadata_controls'] == 719, 'all host exact results and actual per-cut counts independently replayed')
target, expected = obj('host/target-cases/cases.json'), obj('host/target-cases/expected.json'); by_id = {row['id']: row for row in model['cases']}
need(len(target['cases']) == 200 and all(by_id[row['id']] == row for row in target['cases']) and
     raw('host/target-cases/cases.h').decode('ascii') == oracle.target_header(target) and expected ==
     dict(schema='native-vorbis-codebook-expected-v1', policy=oracle.POLICY, cases=[oracle.expected_case(row) for row in target['cases']]), 'all200 exact target inputs/header/expected values')
for name, digest in h['target_input_sha256'].items(): need(sha(raw('host/target-cases/'+name)) == digest, 'predeclared target identity')
for receipt, script, count, digest in (
    ('protocol', 'test-vorbis-codebook-protocol.py', 12, '6f4f7ea9689d4db7a30066e4e821813357a41ae668c1ef49c7e8f141e886ed2b'),
    ('old-quant-protocol', 'test-vorbis-quantization-protocol.py', 12, 'd9cc84073271dad3588348e0a62f8c29239c88ef6454b25ef240d515130c7c05'),
    ('old-angle-protocol', 'test-vorbis-floor0-angles-protocol.py', 12, '6f79caf55af7f04da92262f2b9eea6d3706507eab03a2c2c2980651d0d7daa7e'),
    ('old-numeric-protocol', 'test-vorbis-floor0-numeric-protocol.py', 13, '0ff7adc7620a01e28f639970886f67fe0c47b5277b5d52ade3362d0f78cc9853')):
    outer(receipt, 0, 'tests/'+script)
    need(sha(raw('canonical/tests/'+script)) == digest and 'Ran '+str(count)+' tests in ' in text('validation/'+receipt+'.stderr.log') and
         text('validation/'+receipt+'.stderr.log').endswith('\nOK\n'), 'actual pure protocol receipt/log method counts only')
for group, receipt, script, digest, old_code, total in (
    ('lint-initial', 'lint', '.build/run-vorbis-codebook-lint-01.py', 'e76b6624dd5b879aa88bc42210df5fff0ee3331ffe58951683780647267c1b13', '4e6e9e35f7d2355c78c98a89e8cb6e15a41fca9efb7fd49cd42002b9b4b1a3df', 16),
    ('lint-final', 'lint-final', '.build/run-vorbis-codebook-lint-02.py', 'e5b4dffa75a280f982dd055456c75d62e5013f229bf7a50ee393f875b47335ef', MODULE['codebook.c'], 2)):
    lint = obj(group+'/report.json'); outer(receipt, 0, script)
    need(lint['completed'] is True and lint['warnings'] == total and lint['errors'] == 0 and 'Standalone owned component only' in lint['scope'] and
         sha(raw('canonical/'+script)) == digest and raw('canonical/'+script) == raw(group+'/runner.py'), 'actual standalone lint source/scope')
    for origin, pin in lint['inputs'].items():
        alias = group+'/'+norm(pin['snapshot']); row = M['historical_sources'][alias]
        need(row['path'].casefold() == norm(origin).casefold() and row['sha256'] == pin['sha256'] == sha(raw(alias)), 'historical lint snapshot identity')
        relative = norm(pin['snapshot']).removeprefix('sources/')
        wanted = old_code if relative == 'codebook.c' else MODULE.get(relative, '27b1de038a07a9476ab195865192e9eebc8b58d036b0f359a6689caf2b7aed64')
        need(pin['sha256'] == wanted, 'reviewed historical lint source/config')
    need([c['name'] for c in lint['commands']] == [arch+'-'+unit for arch in ('esp32', 'esp32c3') for unit in ('floor0', 'quant', 'codebook')], 'six actual standalone target/unit analyses')
    warning_sum = 0
    for c in lint['commands']:
        arch, unit = c['name'].split('-'); argv = c['argv']; base = CHECKOUT+'/'+GROUPS[group]
        need(c['returncode'] == 0 and c['pid'] > 0 and not c.get('forced_stop') and norm(c['cwd']) == base and
             norm(argv[1]) == base+'/sources/'+unit+'.c' and '-fno-fast-math' in argv and '-std=c11' in argv and
             ('--target=xtensa-esp-elf' if arch == 'esp32' else '--target=riscv32-esp-elf') in argv, 'actual bounded cross-target lint command')
        original(argv[0], lint['tools'][argv[0]], required=False); logs = []
        for stream in ('stdout', 'stderr'):
            body = raw(group+'/'+c['name']+'.'+stream+'.log'); need(sha(body) == c[stream+'_sha256'], 'actual lint diagnostic stream'); logs.append(body.decode('utf-8', errors='replace'))
        body = '\n'.join(logs); warnings = len(re.findall(r': warning:', body)); errors = len(re.findall(r': (?:error|fatal error):', body))
        need(warnings == c['warnings'] == (1 if unit == 'floor0' else 7 if unit == 'codebook' and group == 'lint-initial' else 0) and errors == c['errors'] == 0,
             'all retained standalone warnings/errors counted honestly'); warning_sum += warnings
    need(warning_sum == lint['warnings'], 'complete initial/final lint totals')
n = obj('reference/report.json'); measured = {}; rows = control.validate_cases(target, text('host/target-cases/cases.h'))
commands = ('sdk-head', 'sdk-clean', 'build', 'dependencies', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after')
for architecture in ('esp32', 'esp32c3'):
    r = obj(architecture+'/report.json'); base = CHECKOUT+'/'+GROUPS[architecture]
    receipt = outer(architecture, 0, 'tests/run-vorbis-codebook-qemu.py', GROUPS[architecture]); snapshots(architecture, r['inputs'])
    need(all(r[k] is True for k in ('completed', 'math_capture_completed', 'whole_module_compiled', 'source_inputs_unchanged')) and
         all(r[k] is False for k in ('passed', 'numerical_reference_compared', 'numerical_qualified', 'full_floor0_qualified', 'decoder_executed', 'stream_decoder_executed', 'production_firmware', 'physical_device')) and
         r['target'] == architecture and r['result'] == 'CHECKED_CODEBOOK_CAPTURED', 'actual scoped native capture')
    need(raw(architecture+'/sources/controller.py') == raw('canonical/tests/run-vorbis-codebook-qemu.py'), 'actual frozen controller')
    for relative in MODULE: need(raw(architecture+'/sources/components/native_vorbis_numeric/'+relative) == raw('canonical/idf/components/native_vorbis_numeric/'+relative), 'actual whole module source')
    for name in ('cases.json', 'cases.h'): need(raw(architecture+'/sources/cases/'+name) == raw('host/target-cases/'+name), 'actual original native inputs')
    pins = {key: MODULE[relative] for key, relative in control.PARTS.items()}
    pins.update(cases=h['target_input_sha256']['cases.json'], **{'cases-header': h['target_input_sha256']['cases.h'], 'qemu': r['source_sha256']['qemu']})
    need(r['source_sha256'] == pins and all(argument(receipt['argv'], '--'+key+'-sha256') == value for key, value in pins.items()) and
         argument(receipt['argv'], '--target') == architecture and resolve(argument(receipt['argv'], '--cases')) == CHECKOUT+'/'+GROUPS['host']+'/target-cases', 'actual complete native source/data/tool invocation')
    original(argument(receipt['argv'], '--qemu'), pins['qemu'], required=False)
    need(tuple(c['name'] for c in r['commands']) == commands and r['sdk_revision'] == control.SDK_HEAD[architecture], 'all nine actual native commands')
    for c in r['commands']:
        need(c['state'] == 'complete' and c['exit_status'] == 0 and c['pid'] > 0 and not c['timed_out'] and not c['interrupted'] and norm(c['cwd']) == base, 'native actual normal terminal')
        for stream in ('stdout', 'stderr'): need(sha(raw(architecture+'/'+c['name']+'.'+stream+'.log')) == c[stream+'_sha256'], 'every actual native command stream')
    for name in ('sdk-head', 'sdk-head-after'): need(text(architecture+'/'+name+'.stdout.log').strip() == control.SDK_HEAD[architecture], 'SDK revision before/after')
    for name in ('sdk-clean', 'sdk-clean-after'): need(not text(architecture+'/'+name+'.stdout.log').strip(), 'SDK clean before/after')
    for path, digest in r['tools'].items(): original(path, digest, required=False)
    for path, digest in r['project_sources'].items(): need(sha(raw(architecture+'/'+path)) == digest, 'actual configured project source')
    for path, digest in r['build_outputs'].items(): original(base+'/'+path, digest, required=False)
    database = obj(architecture+'/build/compile_commands.json')
    for role, path in [('fixture', base+'/project/main/main.c')]+[(role, base+'/sources/components/native_vorbis_numeric/'+unit+'.c') for role, unit in (('floor', 'floor0'), ('quant', 'quant'), ('codebook', 'codebook'))]:
        need([row for row in database if norm(row['file']) == path] == [r['compile_rows'][role]], 'actual selected compile row')
    need(all(flag in r['compile_rows'][role]['command'] for role in ('floor', 'quant', 'codebook') for flag in ('-fno-fast-math', '-fstack-usage')), 'actual three-unit compilation flags')
    deps = norm(text(architecture+'/dependencies.stdout.log')).casefold()
    need(all((base+'/'+path).casefold() in deps for path in [*['sources/components/native_vorbis_numeric/'+relative for relative in MODULE if relative != 'CMakeLists.txt'], 'project/main/cases.h']), 'actual source/header/data dependencies')
    symbols = text(architecture+'/symbols.stdout.log')
    need(all(re.search(r'\bnative_vorbis_'+name+r'$', symbols, re.M) for name in control.PUBLIC) and not re.search(r'\b(?:__wrap_)?esp_vorbis_dec_(?:open|decode)$', symbols, re.M), 'actual codebook APIs; no stream decoder')
    frames = []; need(len(r['stack_usage']['paths']) == len(set(r['stack_usage']['paths'])) == 3, 'three actual compiler-frame files')
    for path in r['stack_usage']['paths']:
        for line in text(architecture+'/'+path).splitlines():
            fields = line.rsplit('\t', 2); need(len(fields) == 3 and fields[1].isdigit(), 'compiler frame row')
            frames.append(dict(function=fields[0].rsplit(':', 1)[-1], bytes=int(fields[1]), qualifier=fields[2], path=path))
    need(frames == r['stack_usage']['rows'], 'all actual .su rows, frames only')
    elf_names = [path for path in r['build_outputs'] if path.endswith('.elf')]; need(len(elf_names) == 1, 'one actual native ELF')
    elf = raw(M['elf_headers'][architecture+'/'+elf_names[0]])
    need(elf == raw(architecture+'/elf-header.bin') and len(elf) == 52 and elf[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', elf, 18)[0] == r['elf_machine'] == (94 if architecture == 'esp32' else 243), 'actual ELF architecture header only')
    need(b'libesp_audio_codec.a' not in raw(architecture+'/'+elf_names[0][:-4]+'.map') and not r['build_warning_lines'], 'no vendor decoder archive or build warnings')
    child = obj(architecture+'/sdk-child.json'); need(child == r['sdk_child'] and child['pid'] > 0 and child['exit_status'] == 0 and 'build' in child['argv'], 'actual SDK child terminal')
    config = text(architecture+'/sdkconfig')
    need(re.search(r'^CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ='+str(240 if architecture == 'esp32' else 160)+'$', config, re.M) and bool(re.search(r'^CONFIG_FREERTOS_UNICORE=y$', config, re.M)) == (architecture == 'esp32c3'), 'actual CPU/core profile')
    qemu = next(c for c in r['commands'] if c['name'] == 'qemu')
    for flag, value in (('-smp', '2' if architecture == 'esp32' else '1'), ('-display', 'none'), ('-monitor', 'none'), ('-serial', 'stdio'), ('-nic', 'none')): need(argument(qemu['argv'], flag) == value, 'isolated QEMU '+flag)
    need(argument(qemu['argv'], '-M') == ('esp32,audiodev=quiet' if architecture == 'esp32' else 'esp32c3') and
         resolve(argument(qemu['argv'], '-L')) == resolve(argument(receipt['argv'], '--rom')), 'actual native machine and supplied ROM directory')
    need('-snapshot' in qemu['argv'] and '-no-reboot' in qemu['argv'], 'isolated controlled snapshot')
    parsed = control.validate_log(text(architecture+'/qemu.stdout.log')+'\n'+text(architecture+'/qemu.stderr.log'), rows, architecture, h['target_input_sha256']['cases.json'])
    need(parsed.pop('rows') == r['rows'] and parsed == r['observed'] and (parsed['cases'], parsed['metadata_controls'], parsed['protocol_lines']) == (200, 719, 1405), 'all actual native ordered events/guards/cores')
    measured[architecture] = oracle.compare_target_rows(target, expected, r['rows'])
    need(measured[architecture] == n['targets'][architecture] and measured[architecture]['measurement_completed'] is True and measured[architecture]['cases'] == len(measured[architecture]['metrics']) == 200 and
         measured[architecture]['truncation_checks'] == measured[architecture]['payload_truncation_checks'] == 0, 'all200 native exact results; host cut campaigns not repeated')
passed = host_result['passed'] and all(row['passed'] for row in measured.values())
need(all(n[k] is True for k in ('completed', 'measurement_completed', 'host_exact_recomputed')) and n['host_cases'] == 382 and n['host_metadata_controls'] == 719 and n['host_passed'] is host_result['passed'] and
     n['host_measurement'] == {key: value for key, value in host_result.items() if key not in ('metrics', 'failures')} and n['native_cases_required'] == n['native_cases_compared'] == 400 and
     n['native_words_compared'] == sum(row['words'] for row in measured.values()) and n['native_decoded_entries_compared'] == sum(row['decoded'] for row in measured.values()) and
     n['native_affine_values_compared'] == sum(row['affine_values'] for row in measured.values()) and n['passed'] is passed and n['finite_codebook_qualified'] is M['finite_codebook_qualified'] is passed and
     n['result'] == M['numerical_result'] == ('FINITE_CODEBOOK_QUALIFIED' if passed else 'FINITE_CODEBOOK_REJECTED') and all(n[k] is False for k in
     ('SDK_or_QEMU_executed', 'component_executed', 'decoder_executed', 'stream_decoder_executed', 'production_radio_integration', 'full_floor0_qualified', 'full_G6_qualified', 'PCM_qualified', 'physical_device')), 'complete finite exact result, including measured NONPASS')
receipt = outer('numeric', 0 if passed else 1, 'tests/check-vorbis-codebook.py', GROUPS['reference'])
for name in ('host', 'esp32', 'esp32c3'): need(resolve(argument(receipt['argv'], '--'+name)) == CHECKOUT+'/'+GROUPS[name], 'actual comparison input directory')
need(resolve(argument(receipt['argv'], '--receipts')) == CHECKOUT+'/'+GROUPS['validation'], 'actual comparison receipts directory')
for path, pin in n['inputs'].items(): need(original(path, pin['sha256'], pin['bytes']) == raw('reference/'+safe(norm(pin['snapshot']))), 'every actually consumed comparison body')
for path, pin in n['identity_only'].items(): need(original(path, pin['sha256'], pin['bytes'], required=False) is None and bool(pin['reason']), 'explicit actual comparison executable identity')
print(json.dumps(dict(evidence_integrity_verified=True, host_cases=382, host_controls=719, host_words=11653, host_decoded=5963,
    host_affine_values=24603, host_setup_cuts=318030, host_payload_cuts=31580, native_cases_compared=400, native_cuts_repeated=False,
    boundary_assertion_status_checks=290, boundary_negative_cases=140, boundary_scope='actual C receipt and JSON integrity only',
    initial_standalone_lint_warnings=16, final_standalone_lint_warnings=2, legacy_protocols_integrity_only=True,
    numerical_result=n['result'], finite_codebook_qualified=passed, explicit_pinned_pure_definitions_reused=True,
    full_floor0_qualified=False, full_G6_qualified=False, PCM_qualified=False, physical_device=False)))
