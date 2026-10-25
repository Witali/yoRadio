"""Offline arithmetic and receipt replay; execute no saved program or compiler."""
from pathlib import Path, PurePosixPath
import ast
import gzip
import hashlib
import json
import re
import struct


def need(ok, reason):
    if not ok: raise ValueError(reason)


def sha(data): return hashlib.sha256(data).hexdigest()
def norm(path): return str(path).replace('\\', '/').rstrip('/')


def safe(name):
    need(isinstance(name, str) and name and norm(name) == name and ':' not in name and
         not PurePosixPath(name).is_absolute() and all(x not in ('', '.', '..') for x in name.split('/')),
         'safe archive alias')
    return name


ROOT = Path(__file__).resolve().parent
M = json.loads((ROOT/'manifest.json').read_bytes())
need(M['schema'] == 'vorbis-quantvals-evidence-v1' and M['complete'] is True and
     M['selected_sources_unchanged'] is True and all(M[k] is False for k in
     ('whole_dependency_closure', 'raw_decoder_qualified', 'full_G6_qualified', 'production_firmware', 'physical_device')),
     'finite arithmetic archive scope')
FILES, OBJECTS = M['files'], {}
for alias, pin in FILES.items():
    safe(alias)
    need(type(pin['bytes']) is int and pin['bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}', pin['sha256']) and
         pin['object'] == 'objects/'+pin['sha256']+'.gz', 'content-address declaration')
    if pin['object'] not in OBJECTS: OBJECTS[pin['object']] = gzip.decompress((ROOT/pin['object']).read_bytes())
    data = OBJECTS[pin['object']]
    need(len(data) == pin['bytes'] and sha(data) == pin['sha256'], 'saved body identity '+alias)
need(M['aliases'] == len(FILES) and M['objects'] == len(OBJECTS), 'archive accounting')
need({p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} ==
     set(OBJECTS)|{'manifest.json', 'verifier.py', 'README.md', 'CHECKPOINT.md', '.gitattributes'}, 'exact physical inventory')


def raw(alias): return OBJECTS[FILES[safe(alias)]['object']]
def obj(alias): return json.loads(raw(alias))
def text(alias): return raw(alias).decode('utf-8', errors='replace').replace('\r\n', '\n')


for name in ('verifier.py', 'README.md', 'CHECKPOINT.md', '.gitattributes'):
    need((ROOT/name).read_bytes() == raw(name), 'physical root binding')
for key, row in M['origins'].items():
    need(key == norm(row['path']).casefold(), 'original path identity')
    if 'alias' in row: need(len(raw(row['alias'])) == row['bytes'] and sha(raw(row['alias'])) == row['sha256'], 'original body binding')
    else: need(row in M['omissions'].values() and bool(row['reason']), 'explicit identity-only omission')
for alias, row in M['omissions'].items():
    safe(alias); need('alias' not in row and M['origins'][norm(row['path']).casefold()] == row, 'omission ledger')
CHECKOUT = norm(M['checkout'])


def original(path, digest, size=None, required=True):
    row = M['origins'].get(norm(path).casefold())
    need(row is not None and row['sha256'] == digest and (size is None or row['bytes'] == size), 'recorded original identity')
    need(not required or 'alias' in row, 'required source body')
    return raw(row['alias']) if 'alias' in row else None


def outer(name, code, output=None):
    r = obj('validation/'+name+'.json')
    need(r['status'] == 'TERMINAL' and type(r['returncode']) is int and r['returncode'] == code and
         type(r['owned_pid']) is int and r['owned_pid'] > 0 and not r.get('error_type') and
         not r.get('timed_out') and not r.get('interrupted') and 'returncode_after_stop' not in r and
         r['runner_sha256'] == sha(raw('canonical/.build/cyd-vorbis-format-command-01.py')) and
         norm(r['cwd']).casefold() == CHECKOUT.casefold() and 1 <= r['timeout_seconds'] <= 1200,
         'actual normal outer receipt '+name)
    original(r['argv'][0], r['executable_sha256'], required=False)
    if output is not None:
        need(r['argv'].count('--output') == 1 and norm(r['argv'][r['argv'].index('--output')+1]).endswith(output), 'actual output argument')
    for path, pin in r['logs'].items(): original(path, pin['sha256'], pin['bytes'])
    need(len(r['logs']) == 2, 'both outer streams')
    return r


def function(body):
    source = body.decode().replace('\r\n', '\n')
    start = re.search(r'^static long _book_maptype1_quantvals\([^\n]*\)\s*\{', source, re.M)
    need(start is not None, 'canonical integer-root function')
    cursor, depth = source.index('{', start.start())+1, 1
    while depth:
        depth += (source[cursor] == '{')-(source[cursor] == '}'); cursor += 1
    return source[start.start():cursor]+'\n'


def literal(alias, name):
    values = [n.value for n in ast.parse(raw(alias)).body if isinstance(n, ast.Assign) and
              any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    need(len(values) == 1, 'one saved driver/supervisor literal')
    value = ast.literal_eval(values[0]); need(isinstance(value, str), 'literal text only')
    return value.encode('utf-8')


PROFILES = {'esp32': 'esp32-cyd2usb-native', 'esp32c3': 'esp32c3-oled-native'}
SETUP = {'esp32': '06e2e4436cb41662fa28bbe545dba6b360919f3dde59212b8e4ce085e00fba99',
         'esp32c3': '7e82af42b44ecc872d58ef3c4f9296c4b61632183846f2550514c664f7fe2805'}
ABI = {'esp32': 'e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60',
       'esp32c3': 'dd26a294cf3887853e12174f3958ea9cccdaa9425ff6a7b21d46faa350bde61c'}
SDK = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e', 'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
for target, profile in PROFILES.items():
    need(sha(raw('canonical/idf/'+profile+'/main/vorbis_repair/setup.c')) == SETUP[target] and
         sha(raw('canonical/idf/'+profile+'/main/vorbis_repair_abi.h')) == ABI[target], 'reviewed current canonical source pins')
need(function(raw('canonical/idf/'+PROFILES['esp32']+'/main/vorbis_repair/setup.c')) ==
     function(raw('canonical/idf/'+PROFILES['esp32c3']+'/main/vorbis_repair/setup.c')), 'same portable root implementation')


def rows(data):
    count = struct.unpack_from('<I', data)[0]
    need(len(data) == 4+12*count, 'complete host binary inputs')
    result = list(struct.iter_unpack('<III', data[4:]))
    for entries, dimensions, value in result:
        need(1 <= entries <= 16777215 and 1 <= dimensions <= 65535 and 1 <= value <= entries and
             pow(value, dimensions) <= entries < pow(value+1, dimensions), 'independent bignum integer root')
    return result


HOST_ROWS = {}
for number, name, code in ((1, 'host', 1), (2, 'host02', 1), (3, 'host03', 0), (4, 'host04', 0)):
    group = 'host'+str(number); r = obj(group+'/report.json')
    outer(name, code, M['groups'][group])
    for path, pin in r['sources'].items(): need(sha(raw(group+'/'+pin['snapshot'])) == pin['sha256'], 'every historical host snapshot')
    need(all(r[k] is False for k in ('raw_decoder_executed', 'target_executed', 'physical_device', 'full_G6_qualified')), 'host-only scope')
    if number == 1:
        need(r['completed'] is False and r['passed'] is False and not r['commands'] and
             'both canonical arithmetic implementations equal' in r['error'], 'initial LF comparison failure retained'); continue
    if number == 2:
        need(r['completed'] is False and r['passed'] is False and len(r['commands']) == 1 and
             r['commands'][0]['supervisor'] == {} and r['commands'][0]['transport_returncode'] == 4294967295 and
             'Wsl/E_ACCESSDENIED' in raw(group+'/compiler-version.stdout.log').decode('utf-16le'), 'actual WSL access failure retained'); continue
    need(r['completed'] is True and r['passed'] is True and r['function_source_line_endings_normalized'] is True, 'actual complete host measurement')
    for target in PROFILES: need(sha(raw(group+'/sources/'+target+'-setup.c')) == SETUP[target], 'host measured current canonical arithmetic source')
    need(raw(group+'/supervisor.py') == literal(group+'/sources/owned-supervisor-source.py', 'SUPERVISOR') and
         all(raw(group+'/'+variant+'/driver.c') == literal(group+'/sources/test-vorbis-quantvals.py', 'DRIVER')
             for variant in ('native-long', 'int32-model', 'baseline')), 'actual generated supervisor and all three driver bodies')
    data = raw(group+'/inputs.bin'); inputs = rows(data); HOST_ROWS[number] = inputs
    need(len(inputs) == r['cases'] == (35975 if number == 4 else 35969) and sha(data) == r['input_sha256'], 'full original host corpus')
    expected_names = ('compiler-version', 'compiler-machine', 'native-long-compile', 'native-long-execute',
                      'int32-model-compile', 'int32-model-execute', 'baseline-compile', 'baseline-execute')
    need(tuple(c['name'] for c in r['commands']) == expected_names, 'all eight owned host commands')
    for c in r['commands']:
        prefix = group+'/'+c['name']; request = obj(prefix+'.request.json'); receipt = obj(prefix+'.receipt.json')
        expected_code = 1 if c['name'] == 'baseline-execute' else 0
        need(receipt == c['supervisor'] and request['argv'] == c['child_argv'] and request['timeout'] == 60 and
             receipt['request_sha256'] == sha(raw(prefix+'.request.json')) and receipt['nonce'] == request['nonce'] == c['nonce'] and
             receipt['state'] == 'terminal' and receipt['child_returncode'] == expected_code and
             all(receipt[k] is True for k in ('final', 'new_session', 'child_reaped', 'group_gone')) and
             type(receipt['child_pid']) is int and receipt['child_pid'] > 0 and receipt['owned_pgid'] == receipt['child_pid'] and
             c['transport_returncode'] == 0 and c['transport_pid'] > 0 and not c.get('forced_transport_stop') and 'cleanup_error' not in receipt,
             'actual owned supervisor nonce/terminal/reap/group cleanup')
        location = CHECKOUT[0].lower()+CHECKOUT[2:]+'/'+M['groups'][group]
        need(c['argv'] == ['wsl.exe', '--exec', 'python3', '/mnt/'+location+'/supervisor.py', '/mnt/'+location+'/'+c['name']+'.request.json'], 'actual supervisor transport argv')
        for stream in ('stdout', 'stderr'): need(sha(raw(prefix+'.'+stream+'.log')) == c[stream+'_sha256'], 'host child stream binding')
        if c['name'].endswith('-compile'):
            need(all(flag in c['child_argv'] for flag in ('-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-Werror', '-fno-pie', '-no-pie')) and
                 not raw(prefix+'.stdout.log') and not raw(prefix+'.stderr.log'), 'actual sanitized warning-clean compilation')
    for variant, bits in (('native-long', 64), ('int32-model', 32)):
        output = raw(group+'/'+variant+'/outputs.bin'); values = struct.unpack('<'+'I'*(len(output)//4), output)
        need(values[:2] == (len(inputs), bits) and tuple(values[2:]) == tuple(row[2] for row in inputs) and
             sha(output) == r['variants'][variant]['output_sha256'] and r['variants'][variant]['exact'] is True and
             not raw(group+'/'+variant+'-execute.stdout.log') and not raw(group+'/'+variant+'-execute.stderr.log'), 'every sanitized output root independently exact')
        helper = function(raw(group+'/sources/esp32-setup.c'))
        if variant == 'int32-model': helper = re.sub(r'\blong\b', 'int32_t', helper)
        need(raw(group+'/'+variant+'/helper.inc').decode() == helper, 'exact extracted helper/model transformation')
    need(rows(raw(group+'/baseline/inputs.bin')) == [(2, 64, 1)] and r['baseline']['signed_power_overflow_detected'] is True and
         sha(raw(group+'/baseline/setup.c')) == r['baseline']['source_sha256'] == '39d3d621e5e292258d6c0b6c48639a89d97aa7473ffb1273259af0af773fc225' and
         b'runtime error: signed integer overflow:' in raw(group+'/baseline-execute.stderr.log'), 'named original source UBSan witness')


document = obj('host4/target-cases/cases.json'); target_rows = [tuple(row[k] for k in ('entries', 'dimensions', 'expected')) for row in document['cases']]
host_set = set(HOST_ROWS[4])
need(document['schema'] == 'vorbis-quantvals-cases-v1' and len(target_rows) == 2179 and
     all(row in host_set for row in target_rows), 'complete target subset of independent host inputs')
header = text('host4/target-cases/cases.h')
need(re.findall(r'^#define QUANTVALS_CASE_COUNT (\d+)$', header, re.M) == ['2179'], 'exact target array capacity')
body = re.findall(r'quantvals_cases\[[^]]*\]\s*=\s*\{(.*?)\};', header, re.S)
need(len(body) == 1, 'one target C array')
pattern = re.compile(r'\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\}')
matches = list(pattern.finditer(body[0])); cursor = 0
for i, match in enumerate(matches):
    need(re.fullmatch(r'\s*' if i == 0 else r'\s*,\s*', body[0][cursor:match.start()]), 'literal C rows require commas')
    cursor = match.end()
need([tuple(map(int, match.groups())) for match in matches] == target_rows and
     re.fullmatch(r'\s*,?\s*', body[0][cursor:]), 'all2179 literal C rows independently recovered')
COMMANDS = ('sdk-head', 'sdk-clean', 'build', 'dependencies', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after')
executed_controller = raw('esp32/sources/controller.py')
need(sha(executed_controller) == '53b1d4ea705378ec3ad2d82b5ca5b371a6b0452beac0b087fb8a5455aa720849' and
     executed_controller == raw('esp32c3/sources/controller.py'), 'exact original controller executed by both SDK campaigns')
old_tree, new_tree = ast.parse(executed_controller), ast.parse(raw('canonical/tests/run-vorbis-quantvals-qemu.py'))
for tree in (old_tree, new_tree):
    need(sum(isinstance(n, ast.FunctionDef) and n.name == 'validate_cases' for n in tree.body) == 1, 'one pure case reader')
    tree.body = [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name == 'validate_cases')]
need(ast.dump(old_tree) == ast.dump(new_tree), 'publication controller changes only pure case reader; SDK did not execute amendment')
need(sha(raw('canonical/tests/run-vorbis-quantvals-qemu.py')) == '5301cc5e0196ee8439bc1dd5683fc989b69c3dc223346aff900333dffe1f0470' and
     sha(raw('canonical/tests/test-vorbis-quantvals-protocol.py')) == 'ce02a1dab10cdf6362731b986ebb1792c0facd626a04b73f26f6631e6bb872fe', 'final pure reader and same before/after unit source pins')
for name, code in (('protocol-before', 1), ('protocol-after', 0), ('reader-replay', 0)): outer(name, code)
before, after = text('validation/protocol-before.stderr.log'), text('validation/protocol-after.stderr.log')
need('Ran 12 tests in ' in before and 'FAIL: test_missing_row_comma_is_rejected' in before and
     before.endswith('FAILED (failures=1)\n') and 'Ran 12 tests in ' in after and after.endswith('\nOK\n'), 'actual named reader failure and twelve passing unit methods')
replay = obj('validation/reader-replay-result.json')
need(all(replay[k] is True for k in ('completed', 'passed', 'final_reader_replayed_on_actual_saved_data', 'ast_changes_only_in_validate_cases', 'inputs_unchanged')) and
     replay['sdk_or_qemu_or_decoder_executed'] is False and replay['executed_controller_sha256'] == sha(executed_controller) and
     replay['final_controller_sha256'] == sha(raw('canonical/tests/run-vorbis-quantvals-qemu.py')), 'actual final pure-reader saved-data replay scope')
for path, pin in replay['inputs'].items(): original(path, pin['sha256'], pin['bytes'])
for target, profile in PROFILES.items():
    r = obj(target+'/report.json'); base = CHECKOUT+'/'+M['groups'][target]; core = 1 if target == 'esp32' else 0
    receipt = outer(target, 0, M['groups'][target])
    for flag, value in (('--setup-sha256', SETUP[target]), ('--abi-sha256', ABI[target]),
                        ('--cases-sha256', sha(raw('host4/target-cases/cases.json'))), ('--header-sha256', sha(raw('host4/target-cases/cases.h')))):
        need(receipt['argv'].count(flag) == 1 and receipt['argv'][receipt['argv'].index(flag)+1] == value, 'actual explicit source/data pin argument')
    need(all(r[k] is True for k in ('completed', 'passed', 'finite_integer_root_qualified', 'whole_setup_compiled', 'source_inputs_unchanged')) and
         all(r[k] is False for k in ('codec_archive_linked', 'decoder_executed', 'full_G6_qualified', 'production_firmware', 'physical_device')) and
         r['result'] == 'FINITE_QUANTVALS_EXACT' and r['target'] == target and r['sdk_revision'] == SDK[target], 'actual finite native target result')
    need(tuple(c['name'] for c in r['commands']) == COMMANDS, 'all nine target commands')
    for c in r['commands']:
        need(c['state'] == 'complete' and c['exit_status'] == 0 and type(c['pid']) is int and c['pid'] > 0 and
             not c['timed_out'] and not c['interrupted'] and 'error' not in c and norm(c['cwd']) == base, 'actual normal owned target child')
        for stream in ('stdout', 'stderr'): need(sha(raw(target+'/'+c['name']+'.'+stream+'.log')) == c[stream+'_sha256'], 'target child streams')
    for name in ('sdk-head', 'sdk-head-after'): need(text(target+'/'+name+'.stdout.log').strip() == SDK[target], 'SDK before/after revision')
    for name in ('sdk-clean', 'sdk-clean-after'): need(not text(target+'/'+name+'.stdout.log').strip(), 'SDK before/after clean')
    for path, pin in r['inputs'].items(): need(sha(raw(target+'/'+pin['snapshot'])) == pin['sha256'] and len(raw(target+'/'+pin['snapshot'])) == pin['bytes'], 'frozen executed target source')
    for name, digest in r['project_sources'].items(): need(sha(raw(target+'/'+name)) == digest, 'configured project identity')
    for name, digest in r['build_outputs'].items():
        if target+'/'+name in FILES: need(sha(raw(target+'/'+name)) == digest, 'selected actual build output')
        else: need(M['omissions'][target+'/'+name]['sha256'] == digest, 'omitted binary historical identity')
    for path, digest in r['tools'].items(): original(path, digest, required=False)
    for name in ('setup.c',): need(raw(target+'/sources/candidate/vorbis_repair/'+name) == raw('canonical/idf/'+profile+'/main/vorbis_repair/'+name), 'actual current canonical setup')
    need(sha(raw(target+'/sources/candidate/vorbis_repair_abi.h')) == ABI[target] and
         raw(target+'/sources/cases/cases.json') == raw('host4/target-cases/cases.json') and
         raw(target+'/project/main/cases.h') == raw('host4/target-cases/cases.h') and
         r['cases_sha256'] == sha(raw('host4/target-cases/cases.json')) and r['header_sha256'] == sha(raw('host4/target-cases/cases.h')), 'actual ABI/full independent cases')
    deps = text(target+'/dependencies.stdout.log').replace('\\', '/').casefold()
    required_deps = ('sources/candidate/vorbis_repair/setup.c', 'sources/candidate/vorbis_repair_abi.h', 'project/main/cases.h')
    required_deps += tuple('sources/codec/'+name for name in ('include/esp_audio_types.h', 'include/decoder/esp_audio_dec.h', 'include/decoder/esp_audio_dec_reg.h', 'include/decoder/impl/esp_vorbis_dec.h'))
    need(all((base+'/'+name).casefold() in deps for name in required_deps), 'actual canonical whole-source native dependency observation')
    compile_rows = obj(target+'/build/compile_commands.json'); main = [row for row in compile_rows if norm(row['file']) == base+'/project/main/main.c']
    need(main == [r['main_compile_row']] and 'QUANTVALS_SETUP_FILE' in main[0]['command'] and
         r['cases_sha256'] in main[0]['command'], 'actual selected native compile row')
    symbols = text(target+'/symbols.stdout.log')
    need(re.search(r'\b_book_maptype1_quantvals$', symbols, re.M) and not re.search(r'\b(?:__wrap_)?esp_vorbis_dec_(?:open|decode)$', symbols, re.M), 'actual arithmetic symbol, no retained decoder')
    elf_names = [name for name in r['build_outputs'] if name.endswith('.elf')]; need(len(elf_names) == 1, 'one selected native ELF')
    elf = raw(M['elf_headers'][target+'/'+elf_names[0]])
    need(len(elf) == 52 and elf[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', elf, 18)[0] == r['elf_machine'] == (94 if target == 'esp32' else 243), 'saved actual ELF32 architecture header only')
    need(b'libesp_audio_codec.a' not in raw(target+'/'+elf_names[0][:-4]+'.map'), 'actual no-vendor-archive map')
    config = text(target+'/sdkconfig')
    need(re.search(r'^CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ='+str(240 if target == 'esp32' else 160)+'$', config, re.M) and
         bool(re.search(r'^CONFIG_FREERTOS_UNICORE=y$', config, re.M)) == (target == 'esp32c3'), 'native CPU/SMP configuration')
    child = obj(target+'/sdk-child.json'); need(child == r['sdk_child'] and child['pid'] > 0 and child['exit_status'] == 0 and
         'build' in child['argv'] and '-D' in child['argv'], 'actual SDK child terminal and argv')
    flasher = obj(target+'/build/flasher_args.json')
    need(flasher['flash_settings'] == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m') and
         {int(x, 0) for x in flasher['flash_files']} == ({4096, 32768, 65536} if target == 'esp32' else {0, 32768, 65536}), 'native boot-image recipe identities')
    qemu = next(c for c in r['commands'] if c['name'] == 'qemu')
    for flag, value in (('-smp', '2' if target == 'esp32' else '1'), ('-nic', 'none'), ('-monitor', 'none'), ('-display', 'none')):
        need(qemu['argv'].count(flag) == 1 and qemu['argv'][qemu['argv'].index(flag)+1] == value, 'isolated actual QEMU argument')
    need('-no-reboot' in qemu['argv'] and '-snapshot' in qemu['argv'], 'controlled no-reboot snapshot QEMU')
    log = text(target+'/qemu.stdout.log')+'\n'+text(target+'/qemu.stderr.log')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|stack overflow|timed out', log, re.I), 'no target panic/timeout')
    expected = [f'QUANTVALS_BEGIN cases=2179 coordinator=0 worker={core} data={r["cases_sha256"]}', f'QUANTVALS_WORKER core={core} priority=3 stack=16384']
    expected += [f'QUANTVALS_CASE index={i} entries={e} dimensions={d} expected={v} actual={v} core={core}' for i, (e, d, v) in enumerate(target_rows)]
    expected += [f'QUANTVALS_COMPLETE cases=2179 core={core}', 'QUANTVALS_STOP status=PASS']
    need([line for line in log.splitlines() if line.startswith('QUANTVALS_')] == expected and
         r['observed'] == dict(cases=2179, protocol_lines=2183, coordinator_core=0, worker_core=core,
                               priority=3, configured_stack=16384, every_root_exact=True), 'every ordered actual target event')
need(replay['targets'] == [dict(target=t, cases=2179, observed=obj(t+'/report.json')['observed']) for t in PROFILES], 'final reader replay covers both complete actual target observations')

print(json.dumps(dict(evidence_integrity_verified=True, host_cases_per_model=35975, models=2,
                     target_cases_per_architecture=2179, target_architectures=2, native_commands_per_target=9,
                     independent_bignum_roots=True, original_UBSan_witness_retained=True,
                     raw_decoder_qualified=False, full_G6_qualified=False, physical_device=False)))
