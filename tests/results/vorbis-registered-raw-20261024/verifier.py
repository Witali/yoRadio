"""Offline finite public Vorbis registry evidence; run no archived code or tools.

All protocol parsing and signed PCM arithmetic below are local finite readers.
Omitted executables/ELF have historical byte identity only. Collected Ninja/cache
recipes are collection-time facts, not independently pinned executed link bytes.
"""
from pathlib import Path, PurePosixPath
import gzip
import hashlib
import io
import json
import re
import struct
import wave


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def norm(value):
    return str(value).replace('\\', '/').rstrip('/')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(value):
    need(isinstance(value, str) and norm(value) == value and value and
         not PurePosixPath(value).is_absolute() and ':' not in value and
         all(part not in ('', '.', '..') for part in value.split('/')), 'relative archive name')
    return value


ROOT = Path(__file__).resolve().parent
M = json.loads((ROOT / 'manifest.json').read_bytes())
need(M['schema'] == 'vorbis-registered-evidence-v1' and M['complete'] is True and
     M['collection_sources_unchanged'] is True and M['predeclared_max_abs_error'] == 2,
     'complete finite registered evidence schema')
need(all(M[key] is False for key in ('full_G1_qualified', 'full_G6_qualified',
     'reset_behavior_qualified', 'production_radio_integration', 'physical_device')), 'finite scope')
FILES, GROUPS = M['files'], M['groups']
EXPECTED_GROUPS = {
    'cyd': '.build/vorbis-registered-cyd-02',
    'c3': '.build/vorbis-registered-c3-02',
    'historical-cyd01': '.build/vorbis-registered-cyd-01',
    'historical-c301': '.build/vorbis-registered-c3-01',
    'open-control': '.build/vorbis-registered-open-control-01',
    'decode-control': '.build/vorbis-registered-decode-control-01',
    'numeric': '.build/vorbis-registered-check-01',
    'commands': '.build/vorbis-registered-validation-20261024-01',
    'protocol-host': '.build/vorbis-registered-protocol-host-01',
    'cmake-host': '.build/vorbis-registered-cmake-host-01',
    'corpus': '.build/vorbis-floor1-positions-corpus-01',
}
need(GROUPS == EXPECTED_GROUPS, 'exact recorded group origins')
CACHE, IDENTITY_ONLY = {}, set()
for alias, row in FILES.items():
    safe_name(alias)
    need(type(row['bytes']) is int and row['bytes'] >= 0 and
         re.fullmatch('[0-9a-f]{64}', row['sha256']) and
         row['object'] == 'objects/' + row['sha256'] + '.gz', 'content-addressed file declaration')
    if row['object'] not in CACHE:
        CACHE[row['object']] = gzip.decompress((ROOT / row['object']).read_bytes())
    data = CACHE[row['object']]
    need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'saved byte identity: ' + alias)
need({p.relative_to(ROOT).as_posix() for p in (ROOT / 'objects').rglob('*') if p.is_file()} == set(CACHE),
     'exact compressed object inventory')
need(M['logical_files'] == len(FILES) and M['unique_objects'] == len(CACHE) and
     M['selected_uncompressed_bytes'] == sum(row['bytes'] for row in FILES.values()), 'archive accounting')


def raw(alias):
    safe_name(alias)
    need(alias in FILES, 'required archived bytes: ' + alias)
    return CACHE[FILES[alias]['object']]


def obj(alias):
    return json.loads(raw(alias))


for name in ('verifier.py', 'README.md', '.gitattributes'):
    need((ROOT / name).read_bytes() == raw(name), 'standalone root binding: ' + name)
need(raw('.gitattributes') == b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n',
     'literal preservation attributes')
need({p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == set(CACHE) |
     {'manifest.json', 'verifier.py', 'README.md', '.gitattributes'}, 'exact archive physical inventory')
OMISSIONS = {}
for row in M['omissions']:
    name = safe_name(row['path'])
    need(name not in OMISSIONS and type(row['bytes']) is int and row['bytes'] >= 0 and
         re.fullmatch('[0-9a-f]{64}', row['sha256']) and row['reason'], 'explicit unique identity-only omission')
    OMISSIONS[name] = row


def relative(original):
    value, checkout = norm(original), norm(M['checkout_root'])
    need(value.casefold().startswith(checkout.casefold() + '/'), 'original belongs to recorded checkout')
    return safe_name(value[len(checkout) + 1:])


def origin(group, path=''):
    return norm(M['checkout_root']) + '/' + GROUPS[group] + ('/' + norm(path) if path else '')


def sibling(original, path):
    safe_name(norm(path))
    return norm(original).rsplit('/', 1)[0] + '/' + norm(path)


def bound(group, path, digest=None, size=None, required=False):
    path = safe_name(norm(path)); alias = group + '/' + path
    if alias in FILES:
        data = raw(alias)
        need((digest is None or sha(data) == digest) and (size is None or len(data) == size),
             'recorded file binding: ' + alias)
        return data
    omitted = GROUPS[group] + '/' + path
    need(not required and digest is not None and omitted in OMISSIONS, 'missing saved body: ' + alias)
    row = OMISSIONS[omitted]
    need(row['sha256'] == digest and (size is None or row['bytes'] == size), 'omitted byte identity')
    IDENTITY_ONLY.add(omitted)
    return None


def recorded(group):
    report = obj(group + '/report.json')
    for row in report.get('inputs', {}).values():
        bound(group, row['snapshot'], row['sha256'], row.get('bytes'))
    for key in ('build_outputs', 'variant_sources', 'project_sources'):
        for path, digest in report.get(key, {}).items():
            bound(group, path, digest)
    for command in report.get('commands', []):
        for stream in ('stdout', 'stderr'):
            digest = command.get(stream + '_sha256')
            if digest is not None:
                bound(group, command.get(stream, command['name'] + '.' + stream + '.log'), digest, required=True)
    return report


REPORTS = {group: recorded(group) for group in ('cyd', 'c3', 'open-control', 'decode-control',
           'historical-cyd01', 'historical-c301', 'numeric')}
NUMERIC = REPORTS['numeric']
FROZEN = {}
for original, row in NUMERIC['inputs'].items():
    key = norm(original).casefold()
    need(key not in FROZEN, 'unique normalized numerical snapshot origin')
    FROZEN[key] = row


def frozen(original, digest=None, required=True):
    """External retained reference/baseline bodies come only from numeric inputs."""
    key = norm(original).casefold()
    need(key in FROZEN, 'retained original must have a numerical snapshot: ' + str(original))
    row = FROZEN[key]
    need(digest is None or row['sha256'] == digest, 'retained original report identity')
    return bound('numeric', row['snapshot'], row['sha256'], row.get('bytes'), required=required)


def numeric_closure(original, report):
    for row in report.get('inputs', {}).values():
        data = frozen(sibling(original, row['snapshot']), row['sha256'], required=False)
        need(data is None or 'bytes' not in row or len(data) == row['bytes'], 'nested input length')
    for key in ('build_outputs', 'variant_sources', 'project_sources'):
        for name, digest in report.get(key, {}).items():
            frozen(sibling(original, name), digest, required=False)
    for command in report.get('commands', []):
        for stream in ('stdout', 'stderr'):
            frozen(sibling(original, command.get(stream, command['name'] + '.' + stream + '.log')),
                   command[stream + '_sha256'])


def archived(original):
    rel = relative(original); found = []
    if 'canonical/' + rel in FILES:
        found.append(raw('canonical/' + rel))
    for group, source in GROUPS.items():
        if rel.startswith(source + '/'):
            alias = group + rel[len(source):]
            if alias in FILES:
                found.append(raw(alias))
    if norm(original).casefold() in FROZEN:
        found.append(frozen(original))
    need(found and len({sha(data) for data in found}) == 1, 'unambiguous saved path: ' + str(original))
    return found[0]


CORPUS_SHA = '82be88d2661d2457c4febfef4173b392adcbae1e014234f78fccc9babab4316a'
GENERATOR_SHA = '0248784f9baeb0c959bd1c63f56b958600d06c16f896c2c920b2cc88c442ca21'
HELPER_SHA = '8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1'
HEADER_SHA = '3b24c3980895de79c2b3cd6460e31182d7fbc5192d474bc7e88be1fe9f917b4b'
PROTOCOL_SHA = 'a64692cebcad800f0dc8236d852e9853def5c6e955f24dab2d6c90e21d96cf46'
REGISTERED_SHA = '153803c584620c0985626a334d54854a49080d4fb2b5b0a80d9f19485cc101d3'
HOST_TEST_SHA = '386326a7e8975e82d90675e7e88c43ae997fd938b84d11af21405bea6059fc16'
FFMPEG_SHA = '09948d4cdd0650da6ff5a87577469f2a218dc2615ae379f8f734d24c49de0f73'
REFERENCE_SHA = '183f3b8cfabe81021e0309a02de5674cfd264800a64d01ba2e75f0c7f0c26204'
BASELINE_SHA = {'esp32': '753c53375b29c4135f9c37844996c979c8d0f5bea8b509ec0d3a2d96840f764b',
               'esp32c3': '304e2b136ea69fa627b1eeab6792877cc3bd8a05e901a8e57d5a370c4182979f'}
SDK_HEAD = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e',
            'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
manifest, matrix = obj('corpus/manifest.json'), obj('corpus/matrix.json')
need(sha(raw('corpus/manifest.json')) == CORPUS_SHA and manifest['generator_sha256'] == GENERATOR_SHA and
     manifest['helper']['sha256'] == HELPER_SHA and manifest['construction_only'] is True, 'pinned corpus construction')
for path, digest in (('tests/vorbis_format_corpus/generate_floor1_positions.py', GENERATOR_SHA),
                     ('tests/vorbis_block_matrix/generate_minimal.py', HELPER_SHA),
                     ('tests/vorbis_registered_protocol.py', PROTOCOL_SHA),
                     ('tests/test-vorbis-registered-protocol.py', HOST_TEST_SHA),
                     ('tests/target/vorbis_floor1_positions_qemu/main/registered.c', REGISTERED_SHA)):
    need(sha(raw('canonical/' + path)) == digest, 'reviewed source identity: ' + path)
for row in manifest['files']:
    data = raw('corpus/' + row['path'])
    need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'complete corpus byte closure')
need({x.removeprefix('corpus/') for x in FILES if x.startswith('corpus/')} ==
     {row['path'] for row in manifest['files']} | {'manifest.json'}, 'exact corpus inventory')
for name in [row['path'] for row in manifest['files']] + ['manifest.json']:
    need(frozen(origin('corpus',name)) == raw('corpus/'+name), 'numerical checker captured the full exact corpus')
cases = matrix['cases']
need(matrix['schema'] == 'vorbis-floor1-positions-v1' and len(cases) == 14 and
     len({c['id'] for c in cases}) == 14 and [c['expected_valid'] for c in cases] == [True]*8+[False]*6 and
     matrix['valid_raw_packet_count'] == 112 and matrix['expected_valid_pcm_bytes'] == 225280,
     'complete fourteen-case matrix')
for c in cases:
    sizes, offsets = c['expected_packet_bytes'], c['offsets']
    need(re.fullmatch(r'\S+', c['id']) and len(sizes) == 14 and sizes[0] == 0 and
         all(type(n) is int and 1 < n <= 4096 for n in sizes[1:]) and sum(sizes) == 28160 and
         len(offsets) == 15 and offsets[0] == 0 and all(a < b for a,b in zip(offsets, offsets[1:])) and
         len(raw('corpus/' + c['audio'])) == offsets[-1], 'complete packet geometry')


def argument(argv, flag):
    need(argv.count(flag) == 1 and argv.index(flag)+1 < len(argv), 'single command argument: ' + flag)
    return argv[argv.index(flag)+1]


def command_logs(report, read, campaign, reference=False):
    rows = {}
    tools = {norm(path).casefold() for path in report['tools']}
    for cmd in report['commands']:
        name = cmd['name']
        need(name not in rows and type(cmd.get('pid')) is int and cmd['pid'] > 0, 'unique owned command PID')
        need(norm(cmd['cwd']).casefold() == norm(campaign).casefold() and cmd['argv'] and
             norm(cmd['argv'][0]).casefold() in tools, 'owned command cwd/executable binding')
        if reference:
            need(cmd['state'] == 'terminal' and cmd['reaped'] is True and not cmd.get('forced_stop') and
                 type(cmd['returncode']) is int, 'actual normal reference terminal/reap')
        else:
            need(cmd['state'] == 'complete' and type(cmd['exit_status']) is int and cmd['exit_status'] == 0 and
                 'tree_stop_error' not in cmd and not cmd.get('forced_stop'), 'actual owned command terminal0')
        streams = []
        for stream in ('stdout', 'stderr'):
            data = read(cmd.get(stream, name + '.' + stream + '.log'))
            need(sha(data) == cmd[stream + '_sha256'], 'actual command stream hash')
            streams.append(data.decode('utf-8', errors='replace').replace('\r\n', '\n'))
        rows[name] = (cmd, *streams)
    return rows


PANIC = r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP'


def replay(log, core, control=None, registered=True):
    """Independent finite event reader; never import/execute the frozen parser."""
    need(not re.search(PANIC, log), 'panic cannot qualify')
    lines = [line for line in log.replace('\r\n', '\n').splitlines()
             if line.startswith(('FLOOR1_', 'VORBIS_REGISTRY_'))]
    at = 0
    def take(expected):
        nonlocal at
        need(at < len(lines) and lines[at] == expected, 'ordered event %d: %s' % (at, expected))
        at += 1
    def match(pattern):
        nonlocal at
        found = re.fullmatch(pattern, lines[at]) if at < len(lines) else None
        need(found is not None, 'exact event framing at %d' % at)
        at += 1
        return found.groups()
    take(f'FLOOR1_START coordinator=0 decoder={core}')
    if registered:
        take(f'VORBIS_REGISTRY_BEGIN cases=14 packets=112 retries=312 core={core}')
        take(f'VORBIS_REGISTRY_INITIAL empty=1 unsupported=1 core={core}')
    pcm, primers = {}, []
    packet_count = retries = metadata = 0
    for i, case in enumerate(cases):
        if registered:
            take(f'VORBIS_REGISTRY_REGISTER case={i} result=0 ops=1 supported=1 core={core}')
            if control == 'register-open':
                need(i == 0, 'open control only at case0'); break
            take(f'VORBIS_REGISTRY_BIND_OPEN case={i} match=1 core={core}')
            if control == 'register-decode':
                need(i == 0, 'decode control only at case0'); break
            take(f'VORBIS_REGISTRY_BIND_DECODE case={i} match=1 core={core}')
            take(f'VORBIS_REGISTRY_BIND_OTHER case={i} reset=1 close=1 core={core}')
        if not case['expected_valid']:
            take(f'FLOOR1_OPEN case={i} result=-1 handle=0')
            take(f'FLOOR1_REJECT case={i} name={case["id"]} result=-1 handle=0 core={core}')
            if registered:
                take(f'VORBIS_REGISTRY_UNREGISTER case={i} empty=1 unsupported=1 core={core}')
            continue
        take(f'FLOOR1_OPEN case={i} result=0 handle=1')
        pieces = []
        for p, size in enumerate(case['expected_packet_bytes']):
            if registered:
                if size:
                    for attempt in range(3):
                        take(f'VORBIS_REGISTRY_RETRY case={i} packet={p} attempt={attempt} result=-8 consumed=0 decoded=0 needed={size} untouched=1 canaries=1 core={core}')
                        retries += 1
                values = match(rf'VORBIS_REGISTRY_META case={i} packet={p} result=(-?\d+) sample_rate=(\d+) channel=(\d+) bits=(\d+) core={core}')
                status, rate, channel, bits = map(int, values)
                need((status,rate,channel,bits) == (0,48000,2,16) or
                     (size == 0 and status == -9 and 0 <= rate <= 0xffffffff and
                      0 <= channel <= 255 and 0 <= bits <= 255), 'actual public metadata')
                if not size:
                    primers.append(status)
                metadata += 1
            consumed, count, hexdata = match(rf'FLOOR1_PCM case={i} packet={p} consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)')
            data = bytes.fromhex(hexdata)
            need(int(consumed) == case['offsets'][p+1] - case['offsets'][p] and
                 int(count) == len(data) == size, 'exact complete raw packet consumption/PCM')
            pieces.append(data); packet_count += 1
        pcm[i] = b''.join(pieces)
        need(len(pcm[i]) == 28160 and any(pcm[i]), 'full nonzero case PCM')
        if registered:
            take(f'VORBIS_REGISTRY_CLOSE case={i} called=1 core={core}')
            take(f'VORBIS_REGISTRY_UNREGISTER case={i} empty=1 unsupported=1 core={core}')
        marker = 'renderer_repair=1' if registered else 'original_exact=1'
        take(f'FLOOR1_ACCEPT case={i} name={case["id"]} packets=14 pcm=28160 {marker} core={core}')
    failure = None
    if control:
        failure = 'registry_open_binding' if control == 'register-open' else 'registry_decode_binding'
        take(f'FLOOR1_FAILURE case=0 reason={failure}')
        take(f'VORBIS_REGISTRY_CLEANUP case=0 closed=0 empty=1 unsupported=1 core={core}')
    else:
        if registered:
            take(f'VORBIS_REGISTRY_COMPLETE registrations=14 bindings=14 closes=8 unregistrations=14 metadata=112 retries=312 core={core}')
            need((packet_count,retries,metadata) == (112,312,112), 'complete independently counted registry events')
        take(f'FLOOR1_COMPLETE accepted=8 rejected=6 packets=112 pcm=225280 core={core}')
    take('FLOOR1_CONTROLLED_STOP')
    need(at == len(lines), 'no missing/unknown/duplicated/reordered/extra protocol events')
    facts = dict(control_effective=bool(control), exact_failure=failure,
        registered_callbacks_qualified=not control, target_capture_completed=not control,
        registrations=1 if control else 14, bindings=0 if control else 14, closes=0 if control else 8,
        unregistrations=1 if control else 14, pcm_packets=packet_count, metadata_packets=metadata,
        retries=retries, pcm_bytes=0 if control else 225280,
        pcm_sha256={str(i):sha(data) for i,data in pcm.items()}, primer_info_results=primers,
        core=core, vendor_comparison_available=False, independent_reference_compared=False, full_G6_qualified=False)
    return facts, pcm


def decode_control(data):
    anchor = b'.decode = esp_vorbis_dec_decode,'
    declaration = b'esp_audio_err_t __wrap_esp_vorbis_dec_register(void) {'
    need(data.count(anchor) == data.count(declaration) == 1, 'exact decode control anchors')
    newline = b'\r\n' if b'\r\n' in data else b'\n'
    prototype = (b'extern esp_audio_err_t __real_esp_vorbis_dec_decode(void *, esp_audio_dec_in_raw_t *, '
                 b'esp_audio_dec_out_frame_t *, esp_audio_dec_info_t *);' + newline)
    return data.replace(anchor, b'.decode = __real_esp_vorbis_dec_decode,', 1).replace(declaration, prototype+declaration, 1)


PCM, CAPTURE_LOGS = {}, {}
for group, target, control in (('cyd','esp32',None), ('c3','esp32c3',None),
                             ('open-control','esp32','register-open'), ('decode-control','esp32','register-decode')):
    r = REPORTS[group]; core = 1 if target == 'esp32' else 0
    need(r['completed'] is True and r['passed'] is False and r['target'] == target and
         r['dispatch'] == 'registered' and r['renderer'] == 'on' and r['control'] == control and
         r['corpus_kind'] == 'positions' and r['corpus_manifest_sha256'] == CORPUS_SHA and
         r['numerical_reference_qualified'] is False and r['elf_machine'] == (94 if core else 243),
         'actual complete registered fixture and architecture')
    need(all(r[key] is False for key in ('full_G6_qualified','production_radio_integration','physical_device')),
         'finite capture scope')
    need(r['result'] == ('REGISTER_BINDING_CONTROL_EFFECTIVE' if control else 'RENDER_CAPTURED') and
         r['control_effective'] is bool(control) and r['target_capture_completed'] is (not control) and
         r['registered_callbacks_qualified'] is (not control), 'captured protocol/control status')
    logs = command_logs(r, lambda name: raw(group+'/'+norm(name)), origin(group)); CAPTURE_LOGS[group] = logs
    need(set(logs) == {'sdk-head','sdk-clean','build','symbols','merge','qemu','sdk-head-after','sdk-clean-after'},
         'complete actual child receipts')
    need(logs['sdk-head'][1].strip() == logs['sdk-head-after'][1].strip() == SDK_HEAD[target] and
         not logs['sdk-clean'][1].strip() and not logs['sdk-clean-after'][1].strip(), 'SDK before/after clean identity')
    build = logs['build'][0]['argv']
    need(argument(build,'-Target') == target and argument(build,'-Renderer') == 'on' and
         argument(build,'-Dispatch') == 'registered' and argument(build,'-BindingControl') == (control or 'none') and
         norm(argument(build,'-Campaign')).casefold() == origin(group).casefold() and
         norm(argument(build,'-File')).casefold() == origin(group,'sources/project/sdk-build.ps1').casefold(),
         'frozen owned SDK command route')
    qargs = logs['qemu'][0]['argv']
    need(argument(qargs,'-M') == target and argument(qargs,'-smp') == ('2' if core else '1') and
         argument(qargs,'-nic') == 'none' and argument(qargs,'-monitor') == 'none' and
         all(flag in qargs for flag in ('-no-reboot','-snapshot')) and
         origin(group,'qemu-flash.bin').casefold() in norm(argument(qargs,'-drive')).casefold(), 'isolated actual target/core/flash route')
    config = raw(group+'/sdkconfig')
    need((b'CONFIG_FREERTOS_UNICORE=y' in config) == (core == 0) and
         ('CONFIG_IDF_TARGET="'+target+'"').encode() in config, 'actual target/core configuration')
    # Source and executed compilation bindings are separate from late recipe copies.
    need(sha(raw(group+'/sources/registered_protocol.py')) == PROTOCOL_SHA and
         sha(raw(group+'/project/main/registered.c')) == REGISTERED_SHA and
         raw(group+'/sources/runner.py') == raw('canonical/tests/run-vorbis-floor1-positions-qemu.py'), 'frozen reviewed protocol/runner/harness')
    for name in [row['path'] for row in manifest['files']] + ['manifest.json']:
        need(raw(group+'/sources/corpus/'+name) == raw('corpus/'+name), 'full exact actual target corpus snapshot')
    for name, digest in r['variant_sources'].items():
        part = norm(name).removeprefix('variant/')
        before, after = raw(group+'/sources/main/'+part), raw(group+'/'+norm(name))
        platform = 'esp32-cyd2usb' if target == 'esp32' else 'esp32c3-oled'
        need(before == raw('canonical/idf/'+platform+'-native/main/'+part), 'frozen repair source matches reviewed platform source')
        expected = decode_control(before) if control == 'register-decode' and part == 'vorbis_repair/setup.c' else before
        need(after == expected and sha(after) == digest, 'exact narrow variant mutation or unchanged source')
    need(sha(raw(group+'/variant/vorbis_repair/floor1_render.h')) == HEADER_SHA, 'reviewed public renderer source')
    for name in r['project_sources']:
        part = norm(name).removeprefix('project/')
        before = raw('corpus/fixture.h') if part == 'main/fixture.h' else raw(group+'/sources/'+part) if part in ('sdkconfig.defaults','partitions.csv') else raw(group+'/sources/project/'+part)
        need(raw(group+'/'+norm(name)) == before, 'unchanged actual fixture build project')
    commands = obj(group+'/build/compile_commands.json')
    harness_rows = [row for row in commands if norm(row['file']).casefold() == origin(group,'project/main/registered.c').casefold()]
    need(len(harness_rows) == 1 and harness_rows == r['harness_compile_rows'], 'actual registered fixture compilation')
    variants = [row for row in commands if norm(row['file']).casefold().startswith(origin(group,'variant/').casefold()+'/')]
    need(variants == r['compile_rows'] and len(variants) == 2 and
         {norm(row['file']).rsplit('/',1)[-1] for row in variants} == {'setup.c','output.c'}, 'actual two repair compilation rows')
    symbols = logs['symbols'][1]
    required = ('__wrap_esp_vorbis_dec_open','__wrap_esp_vorbis_dec_decode','esp_vorbis_dec_decode',
                '__wrap_floor1_inverse2','esp_audio_dec_get_ops','esp_audio_dec_open','esp_audio_dec_process',
                'esp_audio_dec_get_info','esp_audio_dec_close','esp_audio_dec_unregister',
                'esp_vorbis_dec_register' if control == 'register-open' else '__wrap_esp_vorbis_dec_register')
    need(all(re.search(r'\b'+symbol+r'$', symbols, re.M) for symbol in required), 'actual linked public/wrapper symbols')
    elf_names = [norm(name) for name in r['build_outputs'] if name.endswith('.elf')]
    need(len(elf_names) == 1 and origin(group,elf_names[0]).casefold() in
         {norm(x).casefold() for x in logs['symbols'][0]['argv']}, 'symbols command binds recorded ELF identity')
    recipe = raw(group+'/build/build.ninja').decode(errors='replace').replace('\r\n','\n')
    link_flags = re.findall(r'^  LINK_FLAGS = (.*)$',recipe,re.M)
    need(len(link_flags) == 1 and all(('-Wl,--wrap='+s) in link_flags[0] for s in
         ('esp_vorbis_dec_open','esp_vorbis_dec_decode','floor1_inverse2')) and
         (('-Wl,--wrap=esp_vorbis_dec_register' in link_flags[0]) == (control != 'register-open')),
         'collection-time final executable link recipe')
    cache = raw(group+'/build/CMakeCache.txt').decode(errors='replace').replace('\r\n','\n')
    for key,value in (('FLOOR1_RENDER_MODE','on'),('FLOOR1_DISPATCH_MODE','registered'),('FLOOR1_BINDING_CONTROL',control or 'none')):
        need(re.findall(r'^'+key+r':[^=\r\n]+=(.*)$',cache,re.M) == [value], 'collection-time explicit CMake recipe')
    need(not re.search(PANIC, logs['qemu'][2]), 'no target stderr panic')
    facts, pcm = replay(logs['qemu'][1], core, control)
    need(facts == r['observed_registry'], 'independent complete registry protocol replay')
    if control:
        need(r['observed']['exact_failure'] == ['0',facts['exact_failure']] and not pcm and
             not any(alias.startswith(group+'/pcm/') for alias in FILES), 'case0 precise control/no PCM/cleanup')
    else:
        pins = {norm(name):digest for name,digest in r['observed']['pcm'].items()}
        need(set(pins) == {f'pcm/{i}.s16le' for i in range(8)}, 'all eight target raw PCM pins')
        for i,data in pcm.items():
            need(data == raw(group+f'/pcm/{i}.s16le') and sha(data) == pins[f'pcm/{i}.s16le'], 'transcript/raw/hash equality')
        need(r['observed']['summary'] == ['8','6','112','225280',str(core)], 'complete target summary binding')
        PCM[target] = pcm


# Preserve the first actual preparation failures without promoting them.
for group in ('historical-cyd01','historical-c301'):
    r = REPORTS[group]
    need(r['result'] == 'NONPASS' and r['completed'] is False and r['passed'] is False and
         r['target_capture_completed'] is False and r['registered_callbacks_qualified'] is False and
         not any(cmd['name'] == 'qemu' for cmd in r['commands']) and
         any(cmd['name'] == 'build' and cmd.get('exit_status') == 1 for cmd in r['commands']), 'preserved precompiler historical NONPASS')


def metrics(a,b):
    need(len(a) == len(b) and len(a)%2 == 0, 'full signed16 vector lengths')
    errors = [abs(x[0]-y[0]) for x,y in zip(struct.iter_unpack('<h',a),struct.iter_unpack('<h',b))]
    return dict(samples=len(errors), max_abs_error=max(errors,default=0), over_bound=sum(x>2 for x in errors), allowed=2)


need(NUMERIC['schema'] == 'floor1-render-independent-check-v1' and NUMERIC['completed'] is True and
     NUMERIC['passed'] is True and NUMERIC['finite_renderer_qualified'] is True and
     NUMERIC['both_architectures_qualified'] is True and NUMERIC['result'] == 'FINITE_RENDERER_NUMERICALLY_QUALIFIED' and
     NUMERIC['corpus_kind'] == 'positions' and NUMERIC['corpus_manifest_sha256'] == CORPUS_SHA and
     NUMERIC['predeclared_max_abs_error'] == 2 and NUMERIC['failures'] == [] and NUMERIC['commands'] == [] and
     NUMERIC['ffmpeg_executed'] is False and NUMERIC['sdk_or_target_executed'] is False and
     all(NUMERIC[x] is False for x in ('full_G6_qualified','production_radio_integration','physical_device')),
     'complete finite retained-reference-only numerical report')
need(len(NUMERIC['references']) == 1 and len(NUMERIC['baselines']) == 2 and
     len(NUMERIC['targets']) == 2 and not NUMERIC['controls'], 'exact registry numerical scope')
reference = NUMERIC['references'][0]
need(reference['kind'] == 'retained_positions' and reference['report_sha256'] == REFERENCE_SHA and
     reference['original_result'] == 'NONPASS' and len(reference['cases']) == 14, 'unchanged retained original reference')
original = reference['report']; original_raw = frozen(original,REFERENCE_SHA); reference_report = json.loads(original_raw)
need(reference_report['result'] == 'NONPASS' and reference_report['passed'] is False, 'original overall NONPASS preserved')
numeric_closure(original, reference_report)
reference_logs = command_logs(reference_report, lambda name:frozen(sibling(original,name)), norm(original).rsplit('/',1)[0], reference=True)
need(set(reference_logs) == {f'case-{i:02d}-{d}' for i in range(14) for d in ('vorbis','libvorbis')}, 'all twenty-eight original actual children')
ffmpegs = [path for path,digest in reference_report['tools'].items() if norm(path).rsplit('/',1)[-1].lower() == 'ffmpeg.exe' and digest == FFMPEG_SHA]
need(len(ffmpegs) == 1, 'retained pinned FFmpeg executable identity only')
refs = {}
for i,fact in enumerate(reference['cases']):
    need((fact['index'],fact['id']) == (i,cases[i]['id']), 'reference case order')
    cmd,stdout,stderr = reference_logs[f'case-{i:02d}-libvorbis']
    wavpath = sibling(original,f'case-{i:02d}-libvorbis.wav')
    inputpath = argument(cmd['argv'],'-i')
    need(frozen(inputpath) == raw('corpus/'+cases[i]['ogg']), 'retained carrier bytes equal actual target corpus')
    expected = [ffmpegs[0],'-nostdin','-n','-hide_banner','-loglevel','error','-xerror','-c:a','libvorbis',
                '-i',inputpath,'-map','0:a:0','-map_metadata','-1','-fflags','+bitexact','-flags:a','+bitexact',
                '-c:a','pcm_s16le','-f','wav',cmd['argv'][-1]]
    need(cmd['argv'] == expected and norm(cmd['argv'][-1]).casefold() == norm(wavpath).casefold() and
         norm(fact['wav_path']).casefold() == norm(wavpath).casefold() and cmd['returncode'] == fact['returncode'],
         'exact retained reference command without signal transforms')
    if i < 8:
        data = frozen(fact['pcm_path']); wavbytes = frozen(fact['wav_path'])
        need(cmd['returncode'] == 0 and fact['decoded'] is True and fact['codec_rejection'] is False and
             len(data) == fact['pcm_bytes'] == 28160 and any(data) and sha(data) == fact['pcm_sha256'] and
             sha(wavbytes) == fact['wav_sha256'], 'complete successful retained PCM/WAV')
        with wave.open(io.BytesIO(wavbytes),'rb') as stream:
            meta = dict(channels=stream.getnchannels(),sample_rate=stream.getframerate(),sample_bytes=stream.getsampwidth(),
                        frames=stream.getnframes(),compression=stream.getcomptype())
            need(meta == dict(channels=2,sample_rate=48000,sample_bytes=2,frames=7040,compression='NONE') == fact['metadata'] and
                 stream.readframes(7040) == data and not stream.readframes(1), 'WAV exactly binds full signed16 stereo reference')
        refs[i] = data
    else:
        need(fact['codec_rejection'] is True and fact['decoded'] is False and fact['pcm_bytes'] == 0 and
             cmd['returncode'] in (1,-1094995529,3199971767), 'actual normal malformed codec rejection')
        codec = re.search(r'\[libvorbis @ [^]]+\].*(?:header.*(?:damaged|corrupt|invalid)|floor.*(?:invalid|error))|'
                          r'\[dec:libvorbis @ [^]]+\] Error while opening decoder: Invalid data found',stderr,re.I)
        need(codec is not None and not re.search(r'Unknown decoder|Decoder .*not found|Unrecognized option|Option .*not found|'
             r'No such file or directory|Permission denied|Error writing|Unable to find.*output format',stderr,re.I), 'codec refusal is not infrastructure failure')
        errors = [line for line in stderr.splitlines() if line.startswith('Error opening output')]
        need(not errors or (errors == ['Error opening output file '+cmd['argv'][-1]+'.',
             'Error opening output files: Invalid data found when processing input'] and stderr.find(errors[0]) > codec.end()), 'exact bound output path refusal only')
        for suffix in ('.wav','.s16le'):
            path = sibling(original,f'case-{i:02d}-libvorbis'+suffix)
            need(norm(path).casefold() not in FROZEN or not frozen(path), 'no invalid reference PCM output')


# Native output is retained historical evidence, including its numerical NONPASS.
for item in reference_report['cases']:
    for fact in item['decoded'].values():
        if fact.get('wav_sha256') is not None:
            cmd = reference_logs[fact['command']][0]
            wavbytes = frozen(cmd['argv'][-1],fact['wav_sha256'])
            if wavbytes:
                with wave.open(io.BytesIO(wavbytes),'rb') as stream:
                    data = stream.readframes(stream.getnframes())
                    need(len(data) == fact['pcm_bytes'] and sha(data) == fact['pcm_sha256'], 'advertised historical native/reference PCM')
                if fact.get('pcm_path'):
                    need(frozen(sibling(original,fact['pcm_path'])) == data, 'advertised historical raw PCM')


BASELINE_PCM = {}
need({fact['target'] for fact in NUMERIC['baselines']} == {'esp32','esp32c3'} and
     {fact['target'] for fact in NUMERIC['targets']} == {'esp32','esp32c3'}, 'distinct complete architecture pairs')
for fact in NUMERIC['baselines']:
    target = fact['target']; core = 1 if target == 'esp32' else 0
    reportbytes = frozen(fact['report'],BASELINE_SHA[target]); baseline = json.loads(reportbytes)
    need(fact['report_sha256'] == BASELINE_SHA[target] and baseline['completed'] is True and baseline['passed'] is True and
         baseline['result'] == 'FINITE_MATRIX_PASSED' and baseline['control'] is None and baseline['target'] == target and
         baseline['elf_machine'] == (94 if core else 243), 'unchanged original architecture baseline report')
    numeric_closure(fact['report'],baseline)
    logs = command_logs(baseline,lambda name:frozen(sibling(fact['report'],name)),norm(fact['report']).rsplit('/',1)[0])
    need(not re.search(PANIC,logs['qemu'][2]), 'baseline stderr panic exclusion')
    ignored, pcm = replay(logs['qemu'][1],core,registered=False)
    for i,data in pcm.items():
        need(data == frozen(sibling(fact['report'],f'pcm/{i}.s16le')) and
             sha(data) == fact['pcm_sha256'][str(i)], 'full baseline transcript/raw/hash binding')
    BASELINE_PCM[target] = pcm
for target in NUMERIC['targets']:
    platform = target['target']; group = 'cyd' if platform == 'esp32' else 'c3'; core = 1 if group == 'cyd' else 0
    need(target['role'] == 'candidate' and target['core'] == core and target['dispatch'] == 'registered' and
         target['registered_callbacks_qualified'] is True and target['numerically_qualified'] is True and
         target['report_sha256'] == sha(raw(group+'/report.json')) and
         norm(target['report']).casefold() == origin(group,'report.json').casefold() and
         target['pcm_bytes'] == 225280 and len(target['cases']) == 8 and target['ordinary_baseline_byte_exact'] is True,
         'numerical candidate binds exact registered target report')
    need(all(PCM[platform][i] == BASELINE_PCM[platform][i] for i in range(3,8)), 'ordinary five cases remain byte-exact to frozen baseline')
    for i,fact in enumerate(target['cases']):
        data = PCM[platform][i]; actual = metrics(data,refs[i])
        need((fact['index'],fact['id']) == (i,cases[i]['id']) and fact['raw_sha256'] == sha(data) ==
             target['pcm_sha256'][str(i)] and actual['over_bound'] == 0 and
             all(fact[key] == value for key,value in actual.items()) and len(fact['packets']) == 14,
             'all 14080 signed16 samples compared within predeclared two LSB')
        offset = 0
        for p,size in enumerate(cases[i]['expected_packet_bytes']):
            expected = metrics(data[offset:offset+size],refs[i][offset:offset+size]); offset += size
            need(fact['packets'][p] == dict(packet=p,**expected), 'full per-packet signed16 metrics')
        need(offset == len(data), 'no omitted PCM suffix')


host = obj('protocol-host/receipt.json')
need(host['exit_code'] == 0 and host['source_before'] == host['source_after'] and
     norm(host['cwd']).casefold() == norm(M['checkout_root']).casefold() and
     len(host['source_before']) == 3 and len({row['path'] for row in host['source_before']}) == 3 and
     host['command'][1:] == ['-B','tests/test-vorbis-registered-protocol.py','-v'] and
     host['started_utc'] < host['finished_utc'], 'actual focused protocol host terminal receipt')
for row in host['source_before']:
    data = raw('canonical/'+row['path'])
    need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'host before/after source binding')
for stream in ('stdout','stderr'):
    need(sha(raw('protocol-host/'+stream+'.log')) == host[stream+'_sha256'], 'host output hash')
hostlog = raw('protocol-host/stderr.log').decode(errors='replace').replace('\r\n','\n')
need(re.search(r'^Ran 12 tests in [0-9.]+s$',hostlog,re.M) and hostlog.endswith('\nOK\n') and
     len(re.findall(r'^test_\w+ .* \.\.\. ok$',hostlog,re.M)) == 12, 'actual twelve focused mutation tests')


# Recheck the real script-mode CMake phase regression without invoking CMake.
phase = obj('cmake-host/report.json')
need(phase['passed'] is True and phase['configure_only'] is True and phase['tests_run'] == 8 and
     phase['inputs_unchanged'] is True and phase['frozen_copies_unchanged'] is True and
     all(phase[key] is False for key in ('compiler_invoked','sdk_export_invoked','runtime_invoked')) and
     len(phase['commands']) == 8, 'complete actual eight-case phase-guard regression')
component = raw('cmake-host/component.cmake')
need(component == raw('canonical/tests/target/vorbis_floor1_positions_qemu/main/CMakeLists.txt') and
     len(component) == phase['frozen_source']['bytes'] and sha(component) == phase['frozen_source']['sha256'],
     'CMake frozen subject binding')
newline = b'\r\n' if b'\r\n' in component else b'\n'
block = newline.join(line.encode() for line in (
    'set(binding_controls "none" "register-open" "register-decode")',
    'if(NOT FLOOR1_BINDING_CONTROL IN_LIST binding_controls)',
    '    message(FATAL_ERROR "Explicit known FLOOR1_BINDING_CONTROL is required")','endif()',''))
early = b'if(CMAKE_BUILD_EARLY_EXPANSION)' + newline
need(component.count(block) == component.count(early) == 1, 'single exact CMake phase-control anchors')
old_placement = raw('cmake-host/binding-before-early.cmake')
need(old_placement == component.replace(block,b'',1).replace(early,block+early,1) and
     len(old_placement) == phase['negative_control']['bytes'] and
     sha(old_placement) == phase['negative_control']['sha256'], 'only the binding guard moves in the old-placement control')
for original,pin in phase['inputs'].items():
    need(type(pin['bytes']) is int and pin['bytes'] > 0 and re.fullmatch('[0-9a-f]{64}',pin['sha256']), 'CMake input/tool identity')
    if norm(original).casefold().startswith(norm(M['checkout_root']).casefold()+'/'):
        alias = 'canonical/'+relative(original)
        if alias in FILES:
            need(len(raw(alias)) == pin['bytes'] and sha(raw(alias)) == pin['sha256'], 'CMake source before/after binding')
phase_cases = {
    'early-undefined': ('main.c',None,False,True),
    'early-registered': ('registered.c',None,False,False),
    'early-unknown': ('main.c',None,False,False),
    'unknown-dispatch': ('main.c','Explicit FLOOR1_DISPATCH_MODE direct/registered is required',False,False),
    'unknown-binding': ('main.c','Explicit known FLOOR1_BINDING_CONTROL is required',False,False),
    'renderer-off': ('registered.c','Registered dispatch requires the renderer',False,False),
    'direct-control': ('main.c','Binding controls require registered dispatch',False,False),
    'old-placement-control': ('main.c','Explicit known FLOOR1_BINDING_CONTROL is required',True,True),
}
need({cmd['name'] for cmd in phase['commands']} == set(phase_cases), 'all distinct required CMake phase cases')
for cmd in phase['commands']:
    name = cmd['name']; source,error,control,undefined = phase_cases[name]
    script = raw('cmake-host/'+name+'/case.cmake')
    need(len(script) == cmd['script']['bytes'] and sha(script) == cmd['script']['sha256'] and
         cmd['helper'] == ('binding-before-early.cmake' if control else 'component.cmake') and
         cmd['expected_error'] == error and cmd['returncode'] == (1 if error else 0) and
         cmd['timed_out'] is False and cmd['interrupted'] is False and cmd['passed'] is True and
         norm(cmd['cwd']).casefold() == origin('cmake-host',name).casefold() and
         len(cmd['argv']) == 3 and cmd['argv'][1] == '-P' and
         norm(cmd['argv'][2]).casefold() == origin('cmake-host',name+'/case.cmake').casefold(), 'actual CMake script/child/result binding')
    tool_pins = [pin for path,pin in phase['inputs'].items() if norm(path).casefold() == norm(cmd['argv'][0]).casefold()]
    need(len(tool_pins) == 1, 'actual pinned CMake executable identity only')
    text = ''
    for stream in ('stdout','stderr'):
        data = raw('cmake-host/'+name+'/'+stream+'.log')
        need(len(data) == cmd[stream]['bytes'] and sha(data) == cmd[stream]['sha256'], 'actual CMake log hash')
        text += data.decode('utf-8')
    need(text.count('REGISTRY_CMAKE_IDF_REGISTER source='+source) == 1 and 'UNEXPECTED_' not in text and
         'Select the ESP32 or ESP32-C3 standalone raw test' not in text and 'Wrong pinned SDK' not in text,
         'CMake discovery precedes every expected phase outcome')
    if error:
        need(' '.join(text.split()).count(error) == 1 and 'REGISTRY_CMAKE_EARLY_COMPLETE' not in text,
             'exact CMake predicate failure')
    else:
        need(text.count('REGISTRY_CMAKE_EARLY_COMPLETE') == 1, 'normal CMake discovery completion')
    need(not undefined or 'REGISTRY_CMAKE_OPTIONS_UNDEFINED' in text, 'actual undefined-cache witness')


# Outer command wrappers retain their own historical exit states. Require one
# successful, correctly bound wrapper per current group; failed 01 stays failed.
WRAPPERS = {}
for alias in FILES:
    if not (alias.startswith('commands/') and alias.endswith('.json')):
        continue
    receipt = obj(alias)
    if 'owned_pid' not in receipt:
        continue
    need(receipt['status'] == 'TERMINAL' and type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0 and
         type(receipt['returncode']) is int and norm(receipt['cwd']).casefold() == norm(M['checkout_root']).casefold(),
         'actual owned outer wrapper terminal receipt')
    need(re.fullmatch('[0-9a-f]{64}',receipt['runner_sha256']) and
         re.fullmatch('[0-9a-f]{64}',receipt['executable_sha256']), 'outer wrapper/executable historical identities')
    for path,row in receipt['logs'].items():
        data = archived(path)
        need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'outer wrapper log binding')
    argv = receipt['argv']
    if '--output' not in argv:
        continue
    output = norm(argument(argv,'--output'))
    if not output.casefold().startswith(norm(M['checkout_root']).casefold()+'/'):
        output = norm(M['checkout_root'])+'/'+output
    groups = [group for group in ('cyd','c3','open-control','decode-control','numeric') if output.casefold() == origin(group).casefold()]
    if groups:
        group = groups[0]
        need(group not in WRAPPERS and receipt['returncode'] == 0, 'one successful current outer command')
        script = 'tests/check-vorbis-floor1-render.py' if group == 'numeric' else 'tests/run-vorbis-floor1-positions-qemu.py'
        need(script in [norm(value) for value in argv], 'actual current outer argv script binding')
        WRAPPERS[group] = receipt
need(set(WRAPPERS) == {'cyd','c3','open-control','decode-control','numeric'}, 'all current campaigns have actual outer terminal0 receipts')

print(json.dumps(dict(archive_verified=True, aliases=len(FILES), unique_objects=len(CACHE),
    independent_protocol_replayed=True, architectures=['esp32','esp32c3'], registry_cycles_each=14,
    metadata_packets_each=112, repeated_tiny_retries_each=312, complete_pcm_bytes_each=225280,
    finite_signed16_bound=2, actual_max_abs_error=max(metrics(PCM[t][i],refs[i])['max_abs_error']
        for t in PCM for i in range(8)), actual_named_binding_controls=True,
    historical_nonpass_preserved=True, protocol_host_tests_retained=12,
    cmake_phase_guard_cases_retained=8,
    omitted_identity_records_checked=len(IDENTITY_ONLY), omitted_binary_semantics_verified=False,
    late_link_recipe_independently_execution_pinned=False, new_decoder_or_target_execution=False,
    full_G1_qualified=False, full_G6_qualified=False, reset_behavior_qualified=False,
    production_radio_integration=False, physical_device=False)))
