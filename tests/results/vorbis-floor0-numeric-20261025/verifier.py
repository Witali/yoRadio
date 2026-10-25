"""Offline finite floor0 replay using pinned pure Decimal/corpus/event readers.

No saved main, compiler, SDK, QEMU, decoder or original filesystem path runs.
"""
from pathlib import Path, PurePosixPath
from collections import Counter
from decimal import Context, Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction
from functools import lru_cache
from types import SimpleNamespace
import ast
import gzip
import hashlib
import json
import math
import posixpath
import random
import re
import struct

def need(ok, reason):
    if not ok: raise ValueError(reason)

def sha(data): return hashlib.sha256(data).hexdigest()
def norm(value): return str(value).replace('\\', '/').rstrip('/')
def safe(value):
    need(isinstance(value, str) and value and norm(value) == value and ':' not in value and
         not PurePosixPath(value).is_absolute() and all(p not in ('', '.', '..') for p in value.split('/')), 'safe alias')
    return value

ROOT = Path(__file__).resolve().parent
M = json.loads((ROOT/'manifest.json').read_bytes()); FILES, OBJECTS = M['files'], {}
need(M['schema'] == 'vorbis-floor0-numeric-evidence-v1' and M['complete'] is True and M['selected_sources_unchanged'] is True and
     all(M[k] is False for k in ('whole_dependency_closure', 'full_floor0_qualified', 'full_G6_qualified',
         'PCM_qualified', 'production_radio_integration', 'physical_device')), 'finite numerical archive scope')
for alias, pin in FILES.items():
    safe(alias)
    need(type(pin['bytes']) is int and pin['bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', pin['sha256']) and
         pin['object'] == 'objects/'+pin['sha256']+'.gz', 'content address')
    if pin['object'] not in OBJECTS: OBJECTS[pin['object']] = gzip.decompress((ROOT/pin['object']).read_bytes())
    data = OBJECTS[pin['object']]
    need(len(data) == pin['bytes'] and sha(data) == pin['sha256'], 'saved body '+alias)
need(M['aliases'] == len(FILES) and M['objects'] == len(OBJECTS), 'accounting')
need({p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == set(OBJECTS)|
     {'manifest.json', 'verifier.py', 'README.md', 'CHECKPOINT.md', '.gitattributes'}, 'exact physical inventory')
def raw(alias): return OBJECTS[FILES[safe(alias)]['object']]
def obj(alias): return json.loads(raw(alias))
def text(alias): return raw(alias).decode('utf-8', errors='replace').replace('\r\n', '\n')
for name in ('verifier.py', 'README.md', 'CHECKPOINT.md', '.gitattributes'):
    need((ROOT/name).read_bytes() == raw(name), 'root body binding')
for key, row in M['origins'].items():
    need(key == norm(row['path']).casefold(), 'original path declaration')
    if 'alias' in row: need(sha(raw(row['alias'])) == row['sha256'] and len(raw(row['alias'])) == row['bytes'], 'original body')
    else: need(row in M['omissions'].values() and bool(row['reason']), 'explicit identity-only omission')
for alias, row in M['omissions'].items():
    safe(alias); need('alias' not in row and M['origins'][norm(row['path']).casefold()] == row, 'omission ledger')
CHECKOUT = norm(M['checkout'])
need(M['groups'] == {'host': '.build/vorbis-floor0-numeric-host-20261025-01',
     'validation': '.build/vorbis-floor0-numeric-validation-20261025-01',
     'esp32': '.build/vorbis-floor0-numeric-esp32-20261025-01',
     'esp32c3': '.build/vorbis-floor0-numeric-esp32c3-20261025-01',
     'math': '.build/vorbis-floor0-numeric-reference-20261025-01'}, 'exact selected campaign origins')
def original(path, digest, size=None, required=True):
    row = M['origins'].get(norm(path).casefold())
    need(row is not None and row['sha256'] == digest and (size is None or row['bytes'] == size), 'original identity '+norm(path))
    need(not required or 'alias' in row, 'required source body')
    return raw(row['alias']) if 'alias' in row else None
def resolve(value):
    value = norm(value)
    return posixpath.normpath(value if re.match(r'^[A-Za-z]:/', value) else CHECKOUT+'/'+value)
def argument(argv, flag):
    need(argv.count(flag) == 1 and argv.index(flag)+1 < len(argv), 'unique argument '+flag)
    return argv[argv.index(flag)+1]

WRAPPER = '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e'
PYTHON = '4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a'
ORACLE = '0d3f49022a2c6c13cf8ab820b4b3aab97913fd46eb58bc70562230a14de5d088'
READER = 'a34da82409f4c4ca60a6d33f1e8e2159c3adb0d3cddc2ce7f6b03c8cb0856b8f'
CHECKER = 'b4a7c5bb1d63f5b1135a7637885e49379243afaf46a7527acb8311e9daa4e30e'
MODULE = {'floor0.c': 'f456176e00303460978c3f98d9349323e66722bb7eca8204fad14400760b27b1',
          'include/native_vorbis_floor0.h': '6dab3b6e60d1c1bd64d5fc19dbf65598cc648c07147521f81079174890e2e97a',
          'CMakeLists.txt': '450187b88c7faf362092c7b0a95137c85d8d2492e4426b8248cd61d103a8b0aa'}
need(sha(raw('canonical/.build/cyd-vorbis-format-command-01.py')) == WRAPPER and
     sha(raw('canonical/tests/check-vorbis-floor0-numeric.py')) == CHECKER, 'reviewed wrapper/checker')
def outer(name, code, script):
    r = obj('validation/'+name+'.json')
    need(r['status'] == 'TERMINAL' and type(r['returncode']) is int and r['returncode'] == code and
         type(r['owned_pid']) is int and r['owned_pid'] > 0 and r['runner_sha256'] == WRAPPER and r['executable_sha256'] == PYTHON and
         norm(r['cwd']).casefold() == CHECKOUT.casefold() and 1 <= r['timeout_seconds'] <= 1200 and
         not r.get('timed_out') and not r.get('interrupted') and not r.get('error_type') and 'returncode_after_stop' not in r,
         'actual owned outer '+name)
    indices = [i for i, value in enumerate(r['argv']) if resolve(value).casefold() == (CHECKOUT+'/'+script).casefold()]
    need(len(indices) == 1 and tuple(r['argv'][1:indices[0]]) in (('-B', '-X', 'utf8'), ('-B', '-Xutf8')), 'actual script argv')
    if name != 'protocol':
        group = 'math' if name == 'numeric' else name
        need(resolve(argument(r['argv'], '--output')) == CHECKOUT+'/'+M['groups'][group], 'actual selected output')
    original(r['argv'][0], PYTHON, required=False)
    need(len(r['logs']) == 2, 'both outer streams')
    for path, pin in r['logs'].items(): original(path, pin['sha256'], pin['bytes'])
    return r
def snapshots(group, table):
    for path, pin in table.items():
        data = raw(group+'/'+safe(norm(pin['snapshot'])))
        need(sha(data) == pin['sha256'] and ('bytes' not in pin or len(data) == pin['bytes']) and
             original(path, pin['sha256'], len(data)) == data, 'frozen source/current origin binding')

# Explicit pinned PURE definitions only. No imports, ROOT assignments, main or
# process/file helpers from either saved program execute.
def pure(alias, digest, names, constants):
    body = raw(alias); need(sha(body) == digest, 'reviewed pure source pin')
    tree = ast.parse(body); nodes = []; found = set(); assigned = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            nodes.append(node); found.add(node.name)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants:
            nodes.append(node); assigned.add(node.targets[0].id)
    need(found == set(names) and assigned == set(constants), 'exact selected pure definitions/constants')
    namespace = dict(Counter=Counter, Context=Context, Decimal=Decimal, ROUND_FLOOR=ROUND_FLOOR, localcontext=localcontext,
                     Fraction=Fraction, lru_cache=lru_cache, hashlib=hashlib, json=json, math=math, random=random, re=re, struct=struct)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'reviewed-saved-pure-definitions.py', 'exec'), namespace)
    return SimpleNamespace(**namespace)
functions = ('need', 'sha', 'double_hex', 'from_hex', 'dec', 'decimal_pi', 'decimal_cos', 'decimal_atan', 'bark', 'bark_map',
             'bin_cosine', 'denominator_oracle', 'scaled_value', 'decimal_scaled', 'expected_value', 'gain_oracle', 'oracle_case',
             'curve_case', 'gain_case', 'cases', 'target_header', 'pack', 'Reader', 'unpack', 'actual_value', 'compare_numeric',
             'compare_target_rows', 'oracle_self_checks')
oracle = pure('host/sources/test-vorbis-floor0-numeric.py', ORACLE, functions, ('DECIMAL_CONTEXT', 'POLICY', 'TARGET_KEYS'))
reader = pure('esp32/sources/controller.py', READER, ('need', 'number', 'sequence', 'validate_cases', 'validate_log'), ('API',))
need(raw('host/sources/test-vorbis-floor0-numeric.py') == raw('canonical/tests/test-vorbis-floor0-numeric.py') and
     raw('esp32/sources/controller.py') == raw('esp32c3/sources/controller.py') == raw('canonical/tests/run-vorbis-floor0-numeric-qemu.py'),
     'current/executed pure helpers exactly equal')
h = obj('host/report.json'); outer('host', 0, 'tests/test-vorbis-floor0-numeric.py'); snapshots('host', h['sources'])
need(h['completed'] is True and h['prepared'] is True and h['source_inputs_unchanged'] is True and h['component_executed'] is True and
     h['policy'] == oracle.POLICY and (h['cases'], h['target_cases'], h['historical_calls'], h['historical_scalar_bins']) == (60541, 327, 168, 58368) and
     all(h[k] is False for k in ('decoder_executed', 'SDK_or_QEMU_executed', 'full_G6_qualified', 'physical_device')), 'full finite host scope')
owner = ast.parse(raw('host/sources/owned-supervisor-source.py'))
supervisors = [n.value for n in owner.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SUPERVISOR' for t in n.targets)]
need(len(supervisors) == 1 and ast.literal_eval(supervisors[0]).encode() == raw('host/supervisor.py') and
     raw('host/sources/driver.c') == raw('canonical/tests/native/vorbis_floor0_numeric_test.c'), 'actual reviewed host driver/supervisor')
need(tuple(c['name'] for c in h['commands']) == ('compiler-version', 'compiler-machine', 'compile', 'execute'), 'all four host commands')
for c in h['commands']:
    prefix = 'host/'+c['name']; request, receipt = obj(prefix+'.request.json'), obj(prefix+'.receipt.json')
    need(receipt == c['supervisor'] and request['argv'] == c['child_argv'] and request['timeout'] == 60 and
         receipt['request_sha256'] == sha(raw(prefix+'.request.json')) and receipt['nonce'] == request['nonce'] == c['nonce'] and
         receipt['state'] == 'terminal' and receipt['child_returncode'] == 0 and all(receipt[k] is True for k in
         ('final', 'new_session', 'child_reaped', 'group_gone')) and type(receipt['child_pid']) is int and receipt['child_pid'] > 0 and
         receipt['owned_pgid'] == receipt['child_pid'] and c['transport_returncode'] == 0 and c['transport_pid'] > 0 and
         not c.get('forced_transport_stop') and 'cleanup_error' not in receipt, 'actual host owned terminal/cleanup')
    for stream in ('stdout', 'stderr'):
        need(sha(raw(prefix+'.'+stream+'.log')) == c[stream+'_sha256'], 'host stream')
        if c['name'] in ('compile', 'execute'): need(not raw(prefix+'.'+stream+'.log'), 'clean strict compile/sanitizer run')
need(all(flag in h['commands'][2]['child_argv'] for flag in ('-Werror', '-fno-fast-math', '-ffp-contract=off',
     '-fsanitize=address,undefined', '-fno-sanitize-recover=all')), 'actual strict sanitized compiler flags')
historical = raw('host/sources/historical-contract.json')
need(sha(historical) == '1f8817117df942c4d6564614e71a90147a9faa6e782ff945830dc11d5b9f6e3d', 'recorded168-input contract only')
rows, target = oracle.cases(json.loads(historical)); data = raw('host/inputs.bin')
need(len(rows) == 60541 and len(target) == 327 and oracle.pack(rows) == data and sha(data) == h['input_sha256'] and
     dict(Counter(row['operation'] for row in rows)) == h['case_groups'], 'regenerated complete host operations/binary inputs')
model = obj('host/target-cases/cases.json'); expected = obj('host/target-cases/expected.json')
need(model == dict(schema='native-vorbis-floor0-numeric-cases-v1', cases=target) and
     raw('host/target-cases/cases.h').decode('ascii') == oracle.target_header(target) and expected ==
     dict(schema='native-vorbis-floor0-expected-v1', policy=oracle.POLICY, cases=[oracle.oracle_case(row) for row in target]),
     'all327 independent expected values and exact materialized C arrays')
for name, digest in h['target_input_sha256'].items(): need(sha(raw('host/target-cases/'+name)) == digest, 'predeclared target file identity')
output = raw('host/outputs.bin'); need(sha(output) == h['output_sha256'], 'complete actual host outputs')
observed, metadata = oracle.unpack(output, rows)
numeric = passing = bark_bins = 0; maxima = [Decimal(0)]*3; cosine_errors = []; failures = []
for index, (case, actual) in enumerate(zip(rows, observed)):
    if case['operation'] in ('curve', 'gain', 'at_bin'):
        selected = dict(case)
        if selected['operation'] == 'at_bin':
            selected.update(operation='curve', w_hex=actual['w_hex'])
            error = abs(oracle.dec(oracle.from_hex(actual['w_hex']))-oracle.bin_cosine(case['bin'], case['bark_size']))
            cosine_errors.append(error)
            if error > Decimal('4e-15'): failures.append(dict(index=index, id=case['id'], reason='composed bin cosine approximation', cosine_absolute_error=str(error)))
        metric = oracle.compare_numeric(selected, actual); numeric += 1; passing += metric['qualified']
        for i, key in enumerate(('denominator_relative_error', 'gain_absolute_error', 'gain_relative_error')):
            if metric[key] is not None: maxima[i] = max(maxima[i], Decimal(metric[key]))
        if not metric['qualified']: failures.append(dict(index=index, **metric))
    elif case['operation'] == 'prepare':
        for element, (angle, bits) in enumerate(zip(case['angles'], actual['values'])):
            error = abs(oracle.dec(oracle.from_hex(bits))-2*oracle.decimal_cos(oracle.dec(angle))); cosine_errors.append(error)
            if error > Decimal('4e-15'): failures.append(dict(index=index, id=case['id'], element=element, reason='separate angle cosine approximation', cosine_absolute_error=str(error)))
    elif case['operation'] == 'bin':
        error = abs(oracle.dec(oracle.from_hex(actual['w_hex']))-oracle.bin_cosine(case['bin'], case['bark_size'])); cosine_errors.append(error)
        if error > Decimal('4e-15'): failures.append(dict(index=index, id=case['id'], reason='separate bin cosine approximation', cosine_absolute_error=str(error)))
    else:
        wanted = oracle.bark_map(case['rate'], case['bins'], case['bark_size']); bark_bins += len(wanted)
        differences = [dict(bin=i, expected=value, actual=actual['values'][i]) for i, value in enumerate(wanted) if actual['values'][i] != value]
        if differences: failures.append(dict(index=index, id=case['id'], reason='independent exact Bark integer map', different_bins=differences))
host_numeric = dict(cases_compared=len(rows), numeric_scalar_comparisons=numeric, measurement_completed=True, metadata_controls=metadata,
    cosine_values_compared=len(cosine_errors), bark_bins_compared=bark_bins, max_denominator_relative_error=str(maxima[0]),
    max_gain_absolute_error=str(maxima[1]), max_gain_relative_error_including_near_zero=str(maxima[2]),
    max_cosine_absolute_error=str(max(cosine_errors, default=Decimal(0))), failures=failures, nonmeasurement_errors=[],
    passing_numeric_cases=passing, rejected_numeric_cases=numeric-passing, passed=not failures)
need(host_numeric == h['numerical'] and (numeric, metadata, len(cosine_errors), bark_bins) == (60471, 49, 1145, 25542) and
     h['passed'] is host_numeric['passed'] and h['result'] == ('FINITE_FLOOR0_NUMERIC_QUALIFIED' if h['passed'] else 'FINITE_FLOOR0_NUMERIC_REJECTED'),
     'every host result and complete numerical summary independently replayed')
outer('protocol', 0, '.build/test-vorbis-floor0-numeric-protocol-01.py')
need(raw('canonical/.build/test-vorbis-floor0-numeric-protocol-01.py') == raw('canonical/tests/test-vorbis-floor0-numeric-protocol.py') and
     'Ran 13 tests in ' in text('validation/protocol.stderr.log') and text('validation/protocol.stderr.log').endswith('\nOK\n'), 'actual13 pure protocol tests')
commands = ('sdk-head', 'sdk-clean', 'build', 'dependencies', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after')
sdk = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e', 'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
public = ('prepare_cosines', 'denominator', 'gain_from_denominator', 'gain_at_cosine', 'bark_map', 'bin_cosine', 'gain_at_bin')
n = obj('math/report.json'); measured = {}
need(n['host']['report_sha256'] == sha(raw('host/report.json')) and n['host']['accepted'] is True and
     n['host']['numerical'] == h['numerical'], 'math checker binds this actual audited host result')
for architecture in ('esp32', 'esp32c3'):
    r = obj(architecture+'/report.json'); base = CHECKOUT+'/'+M['groups'][architecture]
    receipt = outer(architecture, 0, 'tests/run-vorbis-floor0-numeric-qemu.py'); snapshots(architecture, r['inputs'])
    need(all(r[k] is True for k in ('completed', 'math_capture_completed', 'whole_module_compiled', 'source_inputs_unchanged')) and
         all(r[k] is False for k in ('passed', 'numerical_reference_compared', 'numerical_qualified', 'full_floor0_qualified',
             'decoder_executed', 'production_firmware', 'physical_device')) and r['result'] == 'CHECKED_MATH_CAPTURED', 'native guarded capture scope')
    for relative, digest in MODULE.items():
        need(sha(raw('canonical/idf/components/native_vorbis_numeric/'+relative)) == digest and
             raw(architecture+'/sources/components/native_vorbis_numeric/'+relative) == raw('canonical/idf/components/native_vorbis_numeric/'+relative), 'actual canonical module source')
    for name in ('cases.json', 'cases.h'):
        need(raw(architecture+'/sources/cases/'+name) == raw('host/target-cases/'+name), 'native complete original data')
    pins = dict(source=MODULE['floor0.c'], header=MODULE['include/native_vorbis_floor0.h'], component=MODULE['CMakeLists.txt'],
                cases=sha(raw('host/target-cases/cases.json')), **{'cases-header': sha(raw('host/target-cases/cases.h'))})
    need(all(r['source_sha256'][key] == value and argument(receipt['argv'], '--'+key+'-sha256') == value for key, value in pins.items()) and
         argument(receipt['argv'], '--target') == architecture and resolve(argument(receipt['argv'], '--cases')) ==
         CHECKOUT+'/'+M['groups']['host']+'/target-cases', 'actual explicit native source/header/component/data invocation pins')
    cases = reader.validate_cases(model, text('host/target-cases/cases.h'))
    need(len(cases) == 327 and tuple(c['name'] for c in r['commands']) == commands and r['sdk_revision'] == sdk[architecture], 'original327/nine-command target scope')
    for c in r['commands']:
        need(c['state'] == 'complete' and c['exit_status'] == 0 and type(c['pid']) is int and c['pid'] > 0 and
             not c['timed_out'] and not c['interrupted'] and norm(c['cwd']) == base, 'actual owned target terminal')
        for stream in ('stdout', 'stderr'): need(sha(raw(architecture+'/'+c['name']+'.'+stream+'.log')) == c[stream+'_sha256'], 'native command stream')
    for name in ('sdk-head', 'sdk-head-after'): need(text(architecture+'/'+name+'.stdout.log').strip() == sdk[architecture], 'SDK before/after revision')
    for name in ('sdk-clean', 'sdk-clean-after'): need(not text(architecture+'/'+name+'.stdout.log').strip(), 'SDK before/after tracked clean')
    for path, digest in r['tools'].items(): original(path, digest, required=False)
    for path, digest in r['project_sources'].items(): need(sha(raw(architecture+'/'+path)) == digest, 'configured project')
    for path, digest in r['build_outputs'].items(): original(base+'/'+path, digest, required=False)
    rows_db = obj(architecture+'/build/compile_commands.json')
    for role, file in (('fixture', base+'/project/main/main.c'), ('module', base+'/sources/components/native_vorbis_numeric/floor0.c')):
        selected = [row for row in rows_db if norm(row['file']) == file]
        need(selected == [r['compile_rows'][role]], 'actual selected compiler row')
    need(all(flag in r['compile_rows']['module']['command'] for flag in ('-fno-fast-math', '-fstack-usage')), 'actual floating/stack compiler flags')
    deps = norm(text(architecture+'/dependencies.stdout.log')).casefold()
    need(all((base+'/'+name).casefold() in deps for name in ('sources/components/native_vorbis_numeric/floor0.c',
         'sources/components/native_vorbis_numeric/include/native_vorbis_floor0.h', 'project/main/cases.h')), 'actual native dependencies')
    symbols = text(architecture+'/symbols.stdout.log')
    need(all(re.search(r'\bnative_vorbis_floor0_'+name+r'$', symbols, re.M) for name in public) and
         not re.search(r'\b(?:__wrap_)?esp_vorbis_dec_(?:open|decode)$', symbols, re.M), 'all public math symbols, no decoder')
    frames = []
    for line in text(architecture+'/'+r['stack_usage']['path']).splitlines():
        fields = line.rsplit('\t', 2); need(len(fields) == 3 and fields[1].isdigit(), 'actual compiler .su row')
        frames.append(dict(function=fields[0].rsplit(':', 1)[-1], bytes=int(fields[1]), qualifier=fields[2]))
    need(frames == r['stack_usage']['rows'] and all(any(row['function'] == 'native_vorbis_floor0_'+name for row in frames) for name in public), 'compiler frame estimates only')
    elf_names = [path for path in r['build_outputs'] if path.endswith('.elf')]; need(len(elf_names) == 1, 'one native ELF')
    elf = raw(M['elf_headers'][architecture+'/'+elf_names[0]])
    need(elf == raw(architecture+'/elf-header.bin') and len(elf) == 52 and elf[:6] == b'\x7fELF\x01\x01' and
         struct.unpack_from('<H', elf, 18)[0] == r['elf_machine'] == (94 if architecture == 'esp32' else 243), 'actual ELF32 architecture header only')
    need(b'libesp_audio_codec.a' not in raw(architecture+'/'+elf_names[0][:-4]+'.map') and not r['build_warning_lines'], 'no vendor archive or compiler warnings')
    child = obj(architecture+'/sdk-child.json'); need(child == r['sdk_child'] and child['pid'] > 0 and child['exit_status'] == 0 and 'build' in child['argv'], 'actual SDK child')
    config = text(architecture+'/sdkconfig')
    need(re.search(r'^CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ='+str(240 if architecture == 'esp32' else 160)+'$', config, re.M) and
         bool(re.search(r'^CONFIG_FREERTOS_UNICORE=y$', config, re.M)) == (architecture == 'esp32c3'), 'native CPU/core configuration')
    qemu = next(c for c in r['commands'] if c['name'] == 'qemu')
    for flag, value in (('-smp', '2' if architecture == 'esp32' else '1'), ('-display', 'none'), ('-monitor', 'none'), ('-serial', 'stdio'), ('-nic', 'none')):
        need(argument(qemu['argv'], flag) == value, 'isolated QEMU '+flag)
    need('-no-reboot' in qemu['argv'] and '-snapshot' in qemu['argv'], 'controlled native snapshot')
    parsed = reader.validate_log(text(architecture+'/qemu.stdout.log')+'\n'+text(architecture+'/qemu.stderr.log'), cases, architecture, sha(raw('host/target-cases/cases.json')))
    need(parsed.pop('rows') == r['rows'] and parsed == r['observed'] and (parsed['cases'], parsed['protocol_lines'], parsed['api_groups']) == (327, 347, 16), 'every actual native event/value/guard/task')
    measured[architecture] = oracle.compare_target_rows(model, expected, r['rows'])
    recorded = n['targets'][architecture]
    need(all(recorded[key] == value for key, value in measured[architecture].items()) and recorded['cases'] == 327 and
         recorded['report_sha256'] == sha(raw(architecture+'/report.json')) and recorded['outer_receipt_sha256'] == sha(raw('validation/'+architecture+'.json')) and
         recorded['observed'] == parsed and recorded['stack_usage'] == r['stack_usage'], 'all327 metrics/failed results independently recomputed')
need(n['completed'] is True and n['measurement_completed'] is True and n['source_inputs_unchanged'] is True and
     all(row['measurement_completed'] and len(row['metrics']) == 327 for row in measured.values()) and
     all(n[k] is False for k in ('full_floor0_qualified', 'full_G6_qualified', 'PCM_qualified', 'decoder_executed', 'new_reference_processes_executed',
         'SDK_or_QEMU_executed', 'production_radio_integration', 'physical_device')), 'complete math measurement without full decoder qualification')
passed = all(row['passed'] for row in measured.values()); numerical_outer = outer('numeric', 0 if passed else 1, 'tests/check-vorbis-floor0-numeric.py')
for name in ('host', 'esp32', 'esp32c3'):
    need(resolve(argument(numerical_outer['argv'], '--'+name)) == CHECKOUT+'/'+M['groups'][name] and
         resolve(argument(numerical_outer['argv'], '--'+name+'-terminal')) == CHECKOUT+'/'+M['groups']['validation']+'/'+name+'.json',
         'actual numerical invocation binds all three captures/terminals')
need(n['passed'] is passed and n['finite_coefficient_numeric_qualified'] is passed and n['policy'] == oracle.POLICY and
     n['native_cases_compared'] == n['native_cases_required'] == 654 and n['host_numeric_recomputed'] is False and n['result'] == M['numerical_result'] ==
     ('FINITE_COEFFICIENT_NUMERIC_QUALIFIED' if passed else 'FINITE_COEFFICIENT_NUMERIC_REJECTED') and
     M['finite_coefficient_numeric_qualified'] is passed, 'actual fixed policy PASS or NONPASS retained')
for path, pin in n['inputs'].items():
    data = original(path, pin['sha256'], pin['bytes'], required='snapshot' in pin)
    if 'snapshot' in pin: need(data == raw('math/'+safe(norm(pin['snapshot']))), 'every consumed math body')
print(json.dumps(dict(evidence_integrity_verified=True, host_operations_recomputed=60541, host_numeric_recomputed=60471,
    historical_owned_input_calls=168, historical_scalar_bins=58368, host_metadata_controls=metadata, host_cosine_values=1145,
    host_Bark_bins=25542, native_cases_per_architecture=327, native_cases_compared=654, native_commands_per_target=9,
    finite_coefficient_numeric_qualified=passed, numerical_result=n['result'], explicit_pinned_pure_definitions_reused=True,
    full_floor0_qualified=False, full_G6_qualified=False, PCM_qualified=False, physical_device=False)))
