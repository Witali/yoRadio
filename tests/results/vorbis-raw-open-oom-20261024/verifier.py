"""Offline checked raw-open evidence. Reuse only exact-hash owned pure parsers.

Signed16 metrics are independently recomputed for captured baseline PCM only.
Recovery equality is target memcmp/marker evidence; recovery PCM is not saved.
No archived decoder, SDK, compiler, runner, checker or test program executes.
"""
from pathlib import Path, PurePosixPath
import gzip
import hashlib
import io
import json
import re
import struct
import types
import wave


def need(ok,reason):
    if not ok: raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def norm(value):
    return str(value).replace('\\','/').rstrip('/')


def safe_name(value):
    need(isinstance(value,str) and value and norm(value) == value and ':' not in value and
         not PurePosixPath(value).is_absolute() and all(p not in ('','.','..') for p in value.split('/')),'relative archive name')
    return value


ROOT = Path(__file__).resolve().parent
M = json.loads((ROOT/'manifest.json').read_bytes())
GROUPS = {
    'baseline-cyd': '.build/vorbis-open-oom-baseline-cyd-01',
    'baseline-c3': '.build/vorbis-open-oom-baseline-c3-01',
    'cyd': '.build/vorbis-open-oom-cyd-01', 'c3': '.build/vorbis-open-oom-c3-01',
    'legacy-control': '.build/vorbis-open-oom-legacy-control-01',
    'global-control': '.build/vorbis-open-oom-global-control-01',
    'numeric': '.build/vorbis-open-oom-check-01',
    'receipts': '.build/vorbis-open-oom-host-validation-20261024-01',
    'cmake': '.build/vorbis-open-oom-cmake-host-01',
    'corpus': '.build/vorbis-floor1-slopes-corpus-01',
}
need(M['schema'] == 'vorbis-raw-open-oom-evidence-v1' and M['complete'] is True and
     M['collection_sources_unchanged'] is True and M['groups'] == GROUPS and M['predeclared_max_abs_error'] == 2 and
     all(M[k] is False for k in ('full_G1_qualified','full_G4_qualified','full_G5_qualified','full_G6_qualified',
         'ogg_qualified','production_radio_integration','physical_device')),'complete finite checked-open schema')
FILES,CACHE,IDENTITY_ONLY = M['files'],{},set()
for alias,pin in FILES.items():
    safe_name(alias)
    need(type(pin['bytes']) is int and pin['bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}',pin['sha256']) and
         pin['object'] == 'objects/'+pin['sha256']+'.gz','content-addressed body declaration')
    if pin['object'] not in CACHE: CACHE[pin['object']] = gzip.decompress((ROOT/pin['object']).read_bytes())
    data = CACHE[pin['object']]
    need(len(data) == pin['bytes'] and sha(data) == pin['sha256'],'saved byte identity: '+alias)
need({p.relative_to(ROOT).as_posix() for p in (ROOT/'objects').rglob('*') if p.is_file()} == set(CACHE),'exact object inventory')
need(M['logical_files'] == len(FILES) and M['unique_objects'] == len(CACHE) and
     M['selected_uncompressed_bytes'] == sum(x['bytes'] for x in FILES.values()),'archive accounting')


def raw(alias):
    safe_name(alias);need(alias in FILES,'required saved body: '+alias)
    return CACHE[FILES[alias]['object']]


def obj(alias):
    return json.loads(raw(alias))


for name in ('verifier.py','README.md','.gitattributes'):
    need((ROOT/name).read_bytes() == raw(name),'root body binding: '+name)
need(raw('.gitattributes') == b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n','literal preservation attributes')
need({p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == set(CACHE) |
     {'manifest.json','verifier.py','README.md','.gitattributes'},'exact physical archive inventory')
OMISSIONS = {}
for pin in M['omissions']:
    name = safe_name(pin['path'])
    need(name not in OMISSIONS and type(pin['bytes']) is int and pin['bytes'] >= 0 and
         re.fullmatch('[0-9a-f]{64}',pin['sha256']) and pin['reason'],'unique explicit omission')
    OMISSIONS[name] = pin


def relative(original):
    value,checkout = norm(original),norm(M['checkout_root'])
    need(value.casefold().startswith(checkout.casefold()+'/'),'recorded checkout path')
    return safe_name(value[len(checkout)+1:])


def origin(group,path=''):
    return norm(M['checkout_root'])+'/'+GROUPS[group]+('/'+norm(path) if path else '')


def bound(group,path,digest=None,size=None,required=True):
    path = safe_name(norm(path));alias = group+'/'+path
    if alias in FILES:
        data = raw(alias)
        need((digest is None or sha(data) == digest) and (size is None or len(data) == size),'recorded body: '+alias)
        return data
    name = GROUPS[group]+'/'+path
    need(not required and digest is not None and name in OMISSIONS,'missing required bytes: '+alias)
    pin = OMISSIONS[name]
    need(pin['sha256'] == digest and (size is None or pin['bytes'] == size),'identity-only omission binding')
    IDENTITY_ONLY.add(name)
    return None


def recorded(group):
    r = obj(group+'/report.json')
    for pin in r.get('inputs',{}).values():
        bound(group,pin['snapshot'],pin['sha256'],pin.get('bytes'),required=False)
    for key in ('build_outputs','variant_sources','project_sources'):
        for name,digest in r.get(key,{}).items(): bound(group,name,digest,required=False)
    for c in r.get('commands',[]):
        for stream in ('stdout','stderr'):
            digest = c.get(stream+'_sha256')
            if digest is not None: bound(group,c.get(stream,c['name']+'.'+stream+'.log'),digest)
    return r


R = {g:recorded(g) for g in ('baseline-cyd','baseline-c3','cyd','c3','legacy-control','global-control','numeric')}
N = R['numeric'];FROZEN = {}
for original,pin in N['inputs'].items():
    key = norm(original).casefold();need(key not in FROZEN,'unique numerical source origin');FROZEN[key] = pin


def frozen(original):
    key = norm(original).casefold();need(key in FROZEN,'required numerical snapshot origin')
    pin = FROZEN[key]
    return bound('numeric',pin['snapshot'],pin['sha256'],pin.get('bytes'))


def archived(original):
    rel = relative(original);found = []
    if 'canonical/'+rel in FILES: found.append(raw('canonical/'+rel))
    for group,source in GROUPS.items():
        if rel.startswith(source+'/') and group+rel[len(source):] in FILES: found.append(raw(group+rel[len(source):]))
    if norm(original).casefold() in FROZEN: found.append(frozen(original))
    need(found and len({sha(x) for x in found}) == 1,'unambiguous saved path')
    return found[0]


OWN_PINS = {
    'tests/vorbis_open_oom_protocol.py':'a877d98798d867392eddf5c20a77677fec80870f8ccd79a371f544aaeabfa9f8',
    'tests/vorbis_registered_protocol.py':'a64692cebcad800f0dc8236d852e9853def5c6e955f24dab2d6c90e21d96cf46',
    'tests/test-vorbis-open-oom-protocol.py':'cd9e976f06e5e6ff2007bef30e883f99b2cfcb763db21060b73828c0f08ecbc8',
    'tests/test-vorbis-registered-protocol.py':'386326a7e8975e82d90675e7e88c43ae997fd938b84d11af21405bea6059fc16',
    'tests/test-vorbis-floor1-reference-outcomes.py':'25f4b37576bdbaaf957b63c1ddf79553e437ad21f7b95097056e17996660ffab',
    'tests/test-vorbis-registered-cmake.py':'4dcc0d2ff22e44f313d80df9523460b17cff0e8f9262e6edcefacf99bf79bf99',
    'tests/target/vorbis_floor1_positions_qemu/main/open_oom.h':'15b54ec99ddb41e531550e205ef60d3a2ef5c7ec86b02f9e9564862e7071c2b6',
    '.build/cyd-vorbis-format-command-01.py':'33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e',
    'tests/vorbis_format_corpus/generate_floor1_slopes.py':'835158eac4bb5a6eebaa43a2ec45b331b93943f045d82e41abe31bf389dab37b',
    'tests/vorbis_block_matrix/generate_minimal.py':'8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1',
}
for name,digest in OWN_PINS.items(): need(sha(raw('canonical/'+name)) == digest,'reviewed owned source: '+name)
for name in ('docs/CYD_VORBIS_TRANSFER_DESIGN.md','docs/ESP32_CYD_C3_TRANSFER_PLAN.md'):
    need(bool(raw('canonical/'+name)),'nonempty publication-time design/plan documentation')


def parser(name):
    need(name in ('tests/vorbis_open_oom_protocol.py','tests/vorbis_registered_protocol.py'),'approved pure parser name')
    data = raw('canonical/'+name);need(sha(data) == OWN_PINS[name],'approved pure parser hash')
    module = types.ModuleType('saved_'+name.rsplit('/',1)[-1].replace('.py',''))
    exec(compile(data,'canonical/'+name,'exec'),module.__dict__)
    return module.validate_log


oom_parser = parser('tests/vorbis_open_oom_protocol.py')
registry_parser = parser('tests/vorbis_registered_protocol.py')
CORPUS_SHA = '3893c81d5af0f7ed7110633e210a211a633404710cafc0570208df47d56a3182'
manifest,matrix = obj('corpus/manifest.json'),obj('corpus/matrix.json')
need(sha(raw('corpus/manifest.json')) == CORPUS_SHA and manifest['construction_only'] is True and
     manifest['generator_sha256'] == OWN_PINS['tests/vorbis_format_corpus/generate_floor1_slopes.py'] and
     manifest['helper']['sha256'] == OWN_PINS['tests/vorbis_block_matrix/generate_minimal.py'],'pinned slopes corpus')
CORPUS_NAMES = [x['path'] for x in manifest['files']]+['manifest.json']
need(len(set(CORPUS_NAMES)) == len(CORPUS_NAMES) and {a.removeprefix('corpus/') for a in FILES if a.startswith('corpus/')} ==
     set(CORPUS_NAMES),'exact corpus inventory')
for pin in manifest['files']:
    need(len(raw('corpus/'+pin['path'])) == pin['bytes'] and sha(raw('corpus/'+pin['path'])) == pin['sha256'],'corpus body hash')
for name in CORPUS_NAMES: need(frozen(origin('corpus',name)) == raw('corpus/'+name),'full numerical corpus snapshot')
cases = matrix['cases']
need(matrix['schema'] == 'vorbis-floor1-slopes-v1' and len(cases) == 14 and
     [c['expected_valid'] for c in cases] == [True]*8+[False]*6 and
     matrix['expected_valid_pcm_bytes'] == 225280 and matrix['valid_raw_packet_count'] == 112,'complete finite matrix')


def arg(argv,flag):
    need(argv.count(flag) == 1 and argv.index(flag)+1 < len(argv),'unique argument: '+flag)
    return argv[argv.index(flag)+1]


def logs(group,reference=False):
    r = R[group];result = {};tools = {norm(x).casefold() for x in r['tools']}
    for c in r['commands']:
        name = c['name'];need(name not in result and type(c.get('pid')) is int and c['pid'] > 0,'unique owned child PID')
        need(norm(c['cwd']).casefold() == origin(group).casefold() and norm(c['argv'][0]).casefold() in tools,'child cwd/tool binding')
        if reference:
            need(c['state'] == 'terminal' and c['reaped'] is True and not c.get('forced_stop') and
                 type(c.get('returncode')) is int,'actual normal reference terminal/reap')
        else:
            need(c['state'] == 'complete' and type(c.get('exit_status')) is int and c['exit_status'] == 0 and
                 'tree_stop_error' not in c,'actual target child terminal0')
        streams = []
        for stream in ('stdout','stderr'):
            data = raw(group+'/'+norm(c.get(stream,name+'.'+stream+'.log')))
            need(sha(data) == c[stream+'_sha256'],'actual command stream hash')
            streams.append(data.decode('utf-8',errors='replace').replace('\r\n','\n'))
        result[name] = (c,*streams)
    return result


PANIC = r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP'
SDK_HEAD = {'esp32':'7101770dc6db2667b3c477cc31365dd1acd6db4e','esp32c3':'9a97f6c54ec638111ce55cd36581b3c192f15207'}
LEGACY_SETUP = {'esp32':'0693018ea053991be4fb9df48318a6306e2dfd78769b22fa4b9cb70531e04334',
                'esp32c3':'caa4cad946fea9ed8f0d6c84c8c73343be30cd465b800d61ae11a9c8582a63fc'}
FIXED_SETUP = {'esp32':'39d3d621e5e292258d6c0b6c48639a89d97aa7473ffb1273259af0af773fc225',
               'esp32c3':'46b5684843a106af21f885db600efc54b1f04116216230ac26aa88d4b9464728'}
PCM,FACTS = {},{}
for group,target,control in (
        ('baseline-cyd','esp32','oom-legacy'),('baseline-c3','esp32c3','oom-legacy'),
        ('cyd','esp32',None),('c3','esp32c3',None),
        ('legacy-control','esp32','oom-legacy'),('global-control','esp32','oom-global')):
    r = R[group];initial = group.startswith('baseline-');core = 1 if target == 'esp32' else 0
    need(r['completed'] is True and r['passed'] is False and r['target'] == target and r['control'] == control and
         r['renderer'] == 'on' and r['dispatch'] == 'registered' and r['open_oom'] is True and r['reset_cycles'] is False and
         r['corpus_kind'] == 'slopes' and r['corpus_manifest_sha256'] == CORPUS_SHA and r['elf_machine'] == (94 if core else 243) and
         r['control_effective'] is bool(control) and r['target_capture_completed'] is (control is None) and
         r['raw_open_oom_qualified'] is (control is None) and r['registered_callbacks_qualified'] is (control is None) and
         r['raw_reset_behavior_qualified'] is False and r['numerical_reference_qualified'] is False and
         r['result'] == ('OPEN_OOM_CONTROL_EFFECTIVE' if control else 'RENDER_CAPTURED'),'actual finite capture/control status')
    need(all(r[k] is False for k in ('full_G6_qualified','production_radio_integration','physical_device')),'finite actual scope')
    commands = logs(group)
    need(set(commands) == {'sdk-head','sdk-clean','build','symbols','merge','qemu','sdk-head-after','sdk-clean-after'},'all actual child receipts')
    need(commands['sdk-head'][1].strip() == commands['sdk-head-after'][1].strip() == SDK_HEAD[target] and
         not commands['sdk-clean'][1].strip() and not commands['sdk-clean-after'][1].strip(),'SDK clean before/after identity')
    build,qargs = commands['build'][0]['argv'],commands['qemu'][0]['argv']
    need(arg(build,'-Target') == target and arg(build,'-Renderer') == 'on' and arg(build,'-Dispatch') == 'registered' and
         arg(build,'-BindingControl') == 'none' and arg(build,'-ResetCycles') == 'off' and arg(build,'-OpenOom') == 'on' and
         norm(arg(build,'-Campaign')).casefold() == origin(group).casefold() and
         norm(arg(build,'-File')).casefold() == origin(group,'sources/project/sdk-build.ps1').casefold(),'actual frozen build/observer route')
    need(arg(qargs,'-M') == target and arg(qargs,'-smp') == ('2' if core else '1') and arg(qargs,'-nic') == 'none' and
         arg(qargs,'-monitor') == 'none' and all(x in qargs for x in ('-snapshot','-no-reboot')) and
         origin(group,'qemu-flash.bin').casefold() in norm(arg(qargs,'-drive')).casefold(),'actual machine/core/flash isolation')
    config = raw(group+'/sdkconfig')
    need((b'CONFIG_FREERTOS_UNICORE=y' in config) == (core == 0) and
         ('CONFIG_IDF_TARGET="'+target+'"').encode() in config,'actual architecture/core configuration')
    for filename,canonical in (('runner.py','tests/run-vorbis-floor1-positions-qemu.py'),
            ('registered_protocol.py','tests/vorbis_registered_protocol.py'),('open_oom_protocol.py','tests/vorbis_open_oom_protocol.py')):
        need(raw(group+'/sources/'+filename) == raw('canonical/'+canonical),'actual frozen owned source identity')
    platform = 'esp32-cyd2usb' if target == 'esp32' else 'esp32c3-oled'
    for name in r['variant_sources']:
        part = norm(name).removeprefix('variant/');before = raw(group+'/sources/main/'+part);after = raw(group+'/'+norm(name))
        if initial and part == 'vorbis_repair/setup.c':
            need(sha(before) == LEGACY_SETUP[target] and after == before and
                 r['oom_control_source'] == 'unchanged legacy source baseline','actual unchanged pre-fix source')
            continue
        need(before == raw('canonical/idf/'+platform+'-native/main/'+part),'reviewed current platform source')
        if part == 'vorbis_repair/setup.c': need(sha(before) == FIXED_SETUP[target],'frozen reviewed production classification fix')
        expected = before
        if group == 'legacy-control' and part == 'vorbis_repair/setup.c':
            anchor = b'result = open_scope.failed ? ESP_AUDIO_ERR_MEM_LACK : ESP_AUDIO_ERR_FAIL;'
            need(before.count(anchor) == 1 and r['oom_control_source'] == 'restored header-error classification only','single classification control anchor')
            expected = before.replace(anchor,b'result = ESP_AUDIO_ERR_FAIL;',1)
        if group == 'global-control' and part == 'vorbis_repair/setup.c':
            anchor = b'static _Thread_local repair_open_scope *repair_active_open_scope;'
            need(before.count(anchor) == 1 and r['oom_control_source'] == 'removed open error-scope TLS only','single TLS control anchor')
            expected = before.replace(anchor,b'static repair_open_scope *repair_active_open_scope;',1)
        need(after == expected,'unchanged source or exact single declared control mutation')
    for name in r['project_sources']:
        part = norm(name).removeprefix('project/')
        before = raw('corpus/fixture.h') if part == 'main/fixture.h' else raw(group+'/sources/'+part) if part in ('sdkconfig.defaults','partitions.csv') else raw(group+'/sources/project/'+part)
        need(raw(group+'/'+norm(name)) == before,'unchanged actual fixture project')
        if part not in ('main/fixture.h','sdkconfig.defaults','partitions.csv','README.md'):
            need(before == raw('canonical/tests/target/vorbis_floor1_positions_qemu/'+part),'reviewed executable project source')
    for name in CORPUS_NAMES: need(raw(group+'/sources/corpus/'+name) == raw('corpus/'+name),'full actual corpus snapshot')
    compile_commands = obj(group+'/build/compile_commands.json')
    harness = [c for c in compile_commands if norm(c['file']).casefold() == origin(group,'project/main/registered.c').casefold()]
    need(len(harness) == 1 and harness == r['harness_compile_rows'] and
         re.search(r'(?:^|\s)-DVORBIS_OPEN_OOM=1(?:\s|$)',harness[0]['command']) and
         not re.search(r'(?:^|\s)-DVORBIS_RESET_CYCLES=',harness[0]['command']),'actual exclusive OOM fixture compilation')
    variants = [c for c in compile_commands if norm(c['file']).casefold().startswith(origin(group,'variant').casefold()+'/')]
    need(variants == r['compile_rows'] and len(variants) == 2 and
         {norm(c['file']).rsplit('/',1)[-1] for c in variants} == {'setup.c','output.c'},'actual two repair compilation rows')
    symbols = commands['symbols'][1]
    for symbol in ('__wrap_media_lib_module_calloc','__wrap_media_lib_free','media_lib_module_calloc','media_lib_free',
            '__wrap_esp_vorbis_dec_register','__wrap_esp_vorbis_dec_open','__wrap_esp_vorbis_dec_decode',
            '__wrap_floor1_inverse2','esp_vorbis_dec_close','esp_audio_dec_get_ops','esp_audio_dec_open',
            'esp_audio_dec_process','esp_audio_dec_get_info','esp_audio_dec_close','esp_audio_dec_unregister'):
        need(re.search(r'\b'+symbol+r'$',symbols,re.M),'actual linked public/observer symbol: '+symbol)
    elfs = [norm(name) for name in r['build_outputs'] if name.endswith('.elf')]
    need(len(elfs) == 1 and origin(group,elfs[0]).casefold() in {norm(x).casefold() for x in commands['symbols'][0]['argv']},'symbols/ELF identity binding')
    need(not re.search(PANIC,commands['qemu'][2]),'no target stderr panic')
    facts = oom_parser(commands['qemu'][1],matrix,target,control,returncode=commands['qemu'][0]['exit_status'],timed_out=False,interrupted=False)
    need(facts == r['observed_oom'] and facts['recovery_pcm_is_separately_captured'] is False,'explicit reused parser and recovery evidence scope')
    FACTS[group] = facts
    if control:
        failure,case = ('oom_memory_error','0') if control == 'oom-legacy' else ('oom_task_error_isolation','14')
        need(r['observed']['exact_failure'] == [case,failure] and facts['exact_failure'] == failure and
             facts['raw_open_oom_qualified'] is False and not any(a.startswith(group+'/pcm/') for a in FILES),
             'specific unqualified allocation control; no saved candidate PCM')
        continue
    positions = sum(map(len,facts['allocation_request_bytes'].values()))
    need(set(facts['allocation_request_bytes']) == {str(i) for i in range(8)} and
         facts['faults'] == facts['recoveries'] == 2*positions and facts['observed_allocation_positions'] == positions and
         facts['recovery_packets'] == 28*positions and facts['recovery_pcm_bytes'] == 56320*positions and
         facts['recovery_target_byte_exact'] is True and len(facts['nested_pairs']) == 4 and len(facts['task_scenarios']) == 2,
         'actual dynamic Ni and complete fault/recovery/nested/task matrix')
    need(registry_parser(commands['qemu'][1],matrix,target,returncode=0,timed_out=False,interrupted=False) == r['observed_registry'],
         'explicit reused registry parser')
    pins = {norm(name):digest for name,digest in r['observed']['pcm'].items()}
    need(set(pins) == {f'pcm/{i}.s16le' for i in range(8)} and
         {a.removeprefix(group+'/') for a in FILES if a.startswith(group+'/pcm/')} == set(pins),'baseline-only saved PCM inventory')
    events = re.findall(r'^FLOOR1_PCM case=(\d+) packet=(\d+) consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)$',commands['qemu'][1],re.M)
    need([(int(c),int(p)) for c,p,*_ in events] == [(c,p) for c in range(8) for p in range(14)],'complete ordered baseline PCM records')
    PCM[target] = {}
    for i in range(8):
        data = b''.join(bytes.fromhex(e[4]) for e in events[i*14:(i+1)*14])
        need(data == raw(group+f'/pcm/{i}.s16le') and len(data) == 28160 and any(data) and
             sha(data) == pins[f'pcm/{i}.s16le'] == facts['baseline_pcm_sha256'][str(i)],'captured baseline/transcript/hash binding')
        PCM[target][i] = data


for group,baseline in (('cyd','baseline-cyd'),('c3','baseline-c3')):
    need(FACTS[group]['allocation_request_bytes']['0'] == FACTS[baseline]['allocation_request_bytes']['0'],
         'same observed case0 allocation route before/after classification fix')


def metrics(a,b):
    need(len(a) == len(b) and len(a)%2 == 0,'full signed16 vector length')
    errors = [abs(x[0]-y[0]) for x,y in zip(struct.iter_unpack('<h',a),struct.iter_unpack('<h',b))]
    return dict(samples=len(errors),max_abs_error=max(errors,default=0),over_bound=sum(e>2 for e in errors),allowed=2)


need(N['schema'] == 'floor1-render-independent-check-v1' and N['completed'] is True and N['passed'] is True and
     N['finite_renderer_qualified'] is True and N['both_architectures_qualified'] is True and
     N['result'] == 'FINITE_RENDERER_NUMERICALLY_QUALIFIED' and N['corpus_kind'] == 'slopes' and
     N['corpus_manifest_sha256'] == CORPUS_SHA and N['predeclared_max_abs_error'] == 2 and not N['failures'] and
     N['ffmpeg_executed'] is True and N['sdk_or_target_executed'] is False and not N['baselines'] and not N['controls'] and
     all(N[k] is False for k in ('full_G6_qualified','production_radio_integration','physical_device')),'complete independent baseline-only numerical report')
need(frozen(norm(M['checkout_root'])+'/tests/check-vorbis-floor1-render.py') == raw('canonical/tests/check-vorbis-floor1-render.py'),
     'executed numerical checker source identity')
need(len(N['references']) == 1 and N['references'][0]['kind'] == 'fresh_libvorbis' and len(N['references'][0]['cases']) == 14 and
     len(N['commands']) == 14 and len(N['targets']) == 2 and {t['target'] for t in N['targets']} == {'esp32','esp32c3'},
     'all fresh fourteen references and two candidates')
reference = N['references'][0];FFMPEG_SHA = '09948d4cdd0650da6ff5a87577469f2a218dc2615ae379f8f734d24c49de0f73'
need(reference['ffmpeg_sha256'] == FFMPEG_SHA,'pinned FFmpeg executable identity only')
commands = logs('numeric',reference=True)
need(set(commands) == {f'case-{i:02d}-libvorbis' for i in range(14)},'all actual named reference children')
refs = {}
for i,fact in enumerate(reference['cases']):
    name = f'case-{i:02d}-libvorbis';c,stdout,stderr = commands[name];argv = c['argv']
    need((fact['index'],fact['id']) == (i,cases[i]['id']) and fact['qualified'] is True and
         fact['expected_valid'] is cases[i]['expected_valid'],'reference case order/actual completion')
    tools = [p for path,p in N['tools'].items() if norm(path).casefold() == norm(argv[0]).casefold()]
    need(len(tools) == 1 and (tools[0]['sha256'] if isinstance(tools[0],dict) else tools[0]) == FFMPEG_SHA and
         norm(argv[0]).casefold() == norm(reference['ffmpeg']).casefold(),'actual pinned reference executable')
    expected = [argv[0],'-nostdin','-n','-hide_banner','-loglevel','error','-xerror','-c:a','libvorbis',
        '-i',arg(argv,'-i'),'-map','0:a:0','-map_metadata','-1','-fflags','+bitexact','-flags:a','+bitexact',
        '-c:a','pcm_s16le','-f','wav',argv[-1]]
    need(argv == expected and norm(argv[-1]).casefold() == origin('numeric',name+'.wav').casefold() and
         norm(fact['wav_path']).casefold() == origin('numeric',name+'.wav').casefold() and
         frozen(arg(argv,'-i')) == raw('corpus/'+cases[i]['ogg']) and c['returncode'] == fact['returncode'],
         'exact command/carrier with no transforms')
    if i < 8:
        data,wavbytes = raw('numeric/'+name+'.s16le'),raw('numeric/'+name+'.wav')
        need(norm(fact['pcm_path']).casefold() == origin('numeric',name+'.s16le').casefold() and frozen(fact['pcm_path']) == data and
             frozen(fact['wav_path']) == wavbytes and c['returncode'] == 0 and fact['decoded'] is True and
             fact['codec_rejection'] is False and len(data) == fact['pcm_bytes'] == 28160 and any(data) and
             sha(data) == fact['pcm_sha256'] and sha(wavbytes) == fact['wav_sha256'],'complete successful reference PCM/WAV')
        with wave.open(io.BytesIO(wavbytes),'rb') as stream:
            metadata = dict(channels=stream.getnchannels(),sample_rate=stream.getframerate(),sample_bytes=stream.getsampwidth(),
                            frames=stream.getnframes(),compression=stream.getcomptype())
            need(metadata == dict(channels=2,sample_rate=48000,sample_bytes=2,frames=7040,compression='NONE') == fact['metadata'] and
                 stream.readframes(7040) == data and not stream.readframes(1),'complete signed16 stereo48k WAV binding')
        refs[i] = data
    else:
        need(c['returncode'] in (1,-1094995529,3199971767) and fact['decoded'] is False and fact['codec_rejection'] is True and
             fact['pcm_bytes'] == 0 and fact['pcm_sha256'] == sha(b'') and fact['metadata'] is None,'normal INVALIDDATA codec refusal without PCM')
        codec = re.search(r'\[libvorbis @ [^]]+\].*(?:header.*(?:damaged|corrupt|invalid)|floor.*(?:invalid|error))|'
                          r'\[dec:libvorbis @ [^]]+\] Error while opening decoder: Invalid data found',stderr,re.I)
        need(codec is not None and not re.search(r'Unknown decoder|Decoder .*not found|Unrecognized option|Option .*not found|'
             r'No such file or directory|Permission denied|Error writing|Unable to find.*output format',stderr,re.I),'codec refusal versus infrastructure error')
        lines = stderr.splitlines();indices = [j for j,line in enumerate(lines) if line.startswith('Error opening output')]
        need(not indices or (len(indices) == 2 and indices[1] == indices[0]+1 and
             lines[indices[0]] == 'Error opening output file '+argv[-1]+'.' and
             lines[indices[1]] == 'Error opening output files: Invalid data found when processing input' and
             stderr.find(lines[indices[0]]) > codec.end()),'only exact codec-consequent bound output error')
        for suffix in ('.wav','.s16le'):
            alias = 'numeric/'+name+suffix;need(alias not in FILES or not raw(alias),'no invalid reference output')
        need(fact['wav_sha256'] is None or fact['wav_sha256'] == sha(b''),'invalid WAV identity')
for target in N['targets']:
    platform = target['target'];group = 'cyd' if platform == 'esp32' else 'c3';core = 1 if group == 'cyd' else 0
    need(target['role'] == 'candidate' and target['core'] == core and target['dispatch'] == 'registered' and
         target['registered_callbacks_qualified'] is True and target['raw_open_oom_qualified'] is True and
         target['raw_reset_behavior_qualified'] is False and target['numerically_qualified'] is True and
         target['pcm_bytes'] == 225280 and len(target['cases']) == 8 and target['report_sha256'] == sha(raw(group+'/report.json')) and
         norm(target['report']).casefold() == origin(group,'report.json').casefold() and frozen(target['report']) == raw(group+'/report.json'),
         'numeric exact captured candidate baseline binding')
    for i,fact in enumerate(target['cases']):
        data = PCM[platform][i];actual = metrics(data,refs[i])
        need((fact['index'],fact['id']) == (i,cases[i]['id']) and fact['raw_sha256'] == sha(data) == target['pcm_sha256'][str(i)] and
             all(fact[k] == v for k,v in actual.items()) and actual['over_bound'] == 0 and len(fact['packets']) == 14,
             'independent full signed16 baseline metrics within fixed two-LSB bound')
        offset = 0
        for packet,size in enumerate(cases[i]['expected_packet_bytes']):
            need(fact['packets'][packet] == dict(packet=packet,**metrics(data[offset:offset+size],refs[i][offset:offset+size])),
                 'independent every-packet baseline metric')
            offset += size
        need(offset == 28160,'no omitted baseline PCM suffix')


WRAPPER_SHA = OWN_PINS['.build/cyd-vorbis-format-command-01.py']


def wrapper(alias):
    r = obj(alias)
    need(r['status'] == 'TERMINAL' and type(r.get('owned_pid')) is int and r['owned_pid'] > 0 and
         type(r.get('returncode')) is int and r['runner_sha256'] == WRAPPER_SHA and
         re.fullmatch('[0-9a-f]{64}',r['executable_sha256']) and norm(r['cwd']).casefold() == norm(M['checkout_root']).casefold(),
         'actual owned outer terminal/reap receipt')
    for path,pin in r['logs'].items():
        data = archived(path);need(len(data) == pin['bytes'] and sha(data) == pin['sha256'],'actual outer log binding')
    return r


for name,count,script in (('protocol',18,'tests/test-vorbis-open-oom-protocol.py'),
        ('registered',12,'tests/test-vorbis-registered-protocol.py'),
        ('reference-outcomes',8,'tests/test-vorbis-floor1-reference-outcomes.py'),
        ('cmake',37,'tests/test-vorbis-registered-cmake.py')):
    r = wrapper('receipts/'+name+'.json')
    need(r['returncode'] == 0 and script in [norm(x) for x in r['argv']],'actual complete focused host suite')
    text = raw('receipts/'+name+'.stderr.log').decode('utf-8').replace('\r\n','\n')
    need(re.findall(r'^Ran (\d+) tests in [0-9.]+s$',text,re.M) == [str(count)] and text.endswith('\nOK\n') and
         len(re.findall(r'^test_\w+ .* \.\.\. ok$',text,re.M)) == count,'complete actual host count/outcome')
invocation_error = wrapper('receipts/render-checker.json')
error_text = raw('receipts/render-checker.stderr.log').decode('utf-8').replace('\r\n','\n')
need(invocation_error['returncode'] == 2 and 'tests/test-vorbis-floor1-render.py' in
     [norm(x) for x in invocation_error['argv']] and '--output' not in invocation_error['argv'] and
     'the following arguments are required: --output' in error_text and not re.search(r'^Ran \d+ tests|^OK$',error_text,re.M) and
     not raw('receipts/render-checker.stdout.log'),'retained argument-parsing error ran no renderer tests')


before,after = obj('receipts/cmake-before.json'),obj('receipts/cmake-after.json')
need(before == after and len(before) == 6 and len({p['path'] for p in before}) == 6,'actual CMake selected before/after identities')
for pin in before:
    need(type(pin['bytes']) is int and pin['bytes'] > 0 and re.fullmatch('[0-9a-f]{64}',pin['sha256']),'source/tool identity')
    if norm(pin['path']).casefold().startswith(norm(M['checkout_root']).casefold()+'/'):
        data = raw('canonical/'+relative(pin['path']))
        need(len(data) == pin['bytes'] and sha(data) == pin['sha256'],'historical CMake source bytes')
    if pin.get('snapshot'):
        data = raw('receipts/'+pin['snapshot'])
        need(len(data) == pin['bytes'] and sha(data) == pin['sha256'],'actual retained selected source snapshot')
phase = obj('cmake/report.json')
need(sha(raw('cmake/report.json')) == 'ca018953c088cfffc771d460e4cc2a9f5d7a19a08976cdce18c3bd0543a9ae98' and
     phase['passed'] is True and phase['tests_run'] == 37 and len(phase['commands']) == 37 and
     phase['configure_only'] is True and phase['inputs_unchanged'] is True and phase['frozen_copies_unchanged'] is True and
     all(phase[k] is False for k in ('compiler_invoked','sdk_export_invoked','runtime_invoked')),'actual pinned CMake37')
need(raw('cmake/component.cmake') == raw('canonical/tests/target/vorbis_floor1_positions_qemu/main/CMakeLists.txt') and
     sha(raw('cmake/component.cmake')) == phase['frozen_source']['sha256'] and
     sha(raw('cmake/binding-before-early.cmake')) == phase['negative_control']['sha256'],'CMake subject/control source identities')
need(len(set(phase['expected_cases'])) == 37 and {c['name'] for c in phase['commands']} == set(phase['expected_cases']),'all phase/recipe cases')
for c in phase['commands']:
    name = c['name'];data = raw('cmake/'+name+'/case.cmake')
    need(len(data) == c['script']['bytes'] and sha(data) == c['script']['sha256'] and c['passed'] is True and
         c['timed_out'] is False and c['interrupted'] is False and c['returncode'] == (1 if c['expected_error'] else 0),'actual CMake script/result')
    for stream in ('stdout','stderr'):
        data = raw('cmake/'+name+'/'+stream+'.log')
        need(len(data) == c[stream]['bytes'] and sha(data) == c[stream]['sha256'],'CMake stream hash')


campaigns = {}
for alias in FILES:
    if not(alias.startswith('receipts/') and alias.endswith('.json')): continue
    value = obj(alias)
    if not isinstance(value,dict) or 'owned_pid' not in value: continue
    r = wrapper(alias);argv = r['argv']
    if '--output' not in argv: continue
    output = norm(arg(argv,'--output'))
    if not output.casefold().startswith(norm(M['checkout_root']).casefold()+'/'): output = norm(M['checkout_root'])+'/'+output
    matches = [g for g in ('baseline-cyd','baseline-c3','cyd','c3','legacy-control','global-control','numeric')
               if output.casefold() == origin(g).casefold()]
    if matches:
        group = matches[0];need(group not in campaigns and r['returncode'] == 0,'one actual successful campaign wrapper')
        script = 'tests/check-vorbis-floor1-render.py' if group == 'numeric' else 'tests/run-vorbis-floor1-positions-qemu.py'
        need(script in [norm(x) for x in argv] and (group == 'numeric' or '--open-oom' in argv),'actual campaign script/mode route')
        campaigns[group] = r
need(set(campaigns) == {'baseline-cyd','baseline-c3','cyd','c3','legacy-control','global-control','numeric'},'all seven actual campaign receipts')

print(json.dumps(dict(archive_verified=True,aliases=len(FILES),unique_objects=len(CACHE),
    protocol_method='explicit reviewed hash-bound owned pure parser reuse',independent_second_protocol_parser=False,
    finite_checked_raw_open_qualified=True,both_architectures=True,
    allocation_positions={t:{k:len(v) for k,v in FACTS[g]['allocation_request_bytes'].items()} for t,g in (('esp32','cyd'),('esp32c3','c3'))},
    fault_recovery_counts={t:{k:FACTS[g][k] for k in ('faults','recoveries','recovery_packets','recovery_pcm_bytes')}
        for t,g in (('esp32','cyd'),('esp32c3','c3'))},
    independent_reference_scope='captured baseline PCM only',finite_signed16_bound=2,
    actual_baseline_max_abs_error=max(metrics(PCM[t][i],refs[i])['max_abs_error'] for t in PCM for i in range(8)),
    recovery_pcm_separately_captured=False,recovery_evidence='target guarded memcmp assertions and complete markers',
    initial_unchanged_source_baselines_preserved=True,narrow_legacy_global_controls_effective=True,
    host_tests=dict(protocol=18,registered=12,reference_outcomes=8,cmake=37),
    render_checker_invocation=dict(returncode=2,invocation_error=True,tests_run=0,passed=False),
    host_protocol_registered_reference_historical_before_after_pins_available=False,
    omitted_identity_records_checked=len(IDENTITY_ONLY),omitted_binary_semantics_verified=False,
    full_dependency_closure=False,late_recipe_execution_pin=False,new_decoder_or_target_execution=False,
    full_G1_qualified=False,full_G4_qualified=False,full_G5_qualified=False,full_G6_qualified=False,
    ogg_qualified=False,production_radio_integration=False,physical_device=False)))
