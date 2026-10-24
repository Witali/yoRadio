"""Offline RAW reset replay and independent signed16 metrics; no external tools.

The reviewed, exact-hash owned pure transcript parsers are explicitly reused.
This is not an independent second protocol implementation. No archived decoder,
SDK, compiler, runner, checker or test program is imported or executed.
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


def need(ok, reason):
    if not ok: raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def norm(value):
    return str(value).replace('\\','/').rstrip('/')


def safe_name(value):
    need(isinstance(value,str) and value and norm(value) == value and ':' not in value and
         not PurePosixPath(value).is_absolute() and all(p not in ('','.','..') for p in value.split('/')), 'relative archive name')
    return value


ROOT = Path(__file__).resolve().parent
M = json.loads((ROOT/'manifest.json').read_bytes())
GROUPS = {
    'cyd': '.build/vorbis-reset-cyd-02', 'c3': '.build/vorbis-reset-c3-02',
    'control': '.build/vorbis-reset-skip-control-02',
    'history-cyd01': '.build/vorbis-reset-cyd-01', 'history-c301': '.build/vorbis-reset-c3-01',
    'history-control01': '.build/vorbis-reset-skip-control-01',
    'numeric': '.build/vorbis-reset-check-01', 'commands': '.build/vorbis-reset-validation-20261024-01',
    'host': '.build/vorbis-reset-host-validation-20261024-01', 'cmake': '.build/vorbis-reset-cmake-host-01',
    'corpus': '.build/vorbis-floor1-slopes-corpus-01',
}
LIMITS = ('full_G1_qualified','full_G3_qualified','full_G6_qualified','ogg_qualified',
          'production_radio_integration','physical_device')
need(M['schema'] == 'vorbis-raw-reset-evidence-v1' and M['complete'] is True and
     M['collection_sources_unchanged'] is True and M['groups'] == GROUPS and
     M['predeclared_max_abs_error'] == 2 and all(M[k] is False for k in LIMITS), 'complete finite RAW evidence schema')
FILES, CACHE, IDENTITY_ONLY = M['files'], {}, set()
for alias,row in FILES.items():
    safe_name(alias)
    need(type(row['bytes']) is int and row['bytes'] >= 0 and re.fullmatch('[0-9a-f]{64}',row['sha256']) and
         row['object'] == 'objects/'+row['sha256']+'.gz', 'content-addressed body declaration')
    if row['object'] not in CACHE:
        CACHE[row['object']] = gzip.decompress((ROOT/row['object']).read_bytes())
    data = CACHE[row['object']]
    need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'saved bytes: '+alias)
need({p.relative_to(ROOT).as_posix() for p in (ROOT/'objects').rglob('*') if p.is_file()} == set(CACHE), 'exact object inventory')
need(M['logical_files'] == len(FILES) and M['unique_objects'] == len(CACHE) and
     M['selected_uncompressed_bytes'] == sum(x['bytes'] for x in FILES.values()), 'archive accounting')


def raw(alias):
    safe_name(alias);need(alias in FILES,'required body: '+alias)
    return CACHE[FILES[alias]['object']]


def obj(alias):
    return json.loads(raw(alias))


for name in ('verifier.py','README.md','.gitattributes'):
    need((ROOT/name).read_bytes() == raw(name),'standalone root body: '+name)
need(raw('.gitattributes') == b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n', 'literal-byte attributes')
need({p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == set(CACHE) |
     {'manifest.json','verifier.py','README.md','.gitattributes'}, 'exact physical archive inventory')
OMISSIONS = {}
for row in M['omissions']:
    name = safe_name(row['path'])
    need(name not in OMISSIONS and type(row['bytes']) is int and row['bytes'] >= 0 and
         re.fullmatch('[0-9a-f]{64}',row['sha256']) and row['reason'], 'explicit unique identity-only omission')
    OMISSIONS[name] = row


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
        need((digest is None or sha(data) == digest) and (size is None or len(data) == size),'declared body identity: '+alias)
        return data
    name = GROUPS[group]+'/'+path
    need(not required and digest is not None and name in OMISSIONS,'missing required bytes: '+alias)
    pin = OMISSIONS[name]
    need(pin['sha256'] == digest and (size is None or pin['bytes'] == size),'omitted identity')
    IDENTITY_ONLY.add(name)
    return None


def recorded(group):
    r = obj(group+'/report.json')
    for pin in r.get('inputs',{}).values():
        bound(group,pin['snapshot'],pin['sha256'],pin.get('bytes'),required=False)
    for key in ('build_outputs','variant_sources','project_sources'):
        for name,digest in r.get(key,{}).items():
            bound(group,name,digest,required=False)
    for cmd in r.get('commands',[]):
        for stream in ('stdout','stderr'):
            digest = cmd.get(stream+'_sha256')
            if digest is not None: bound(group,cmd.get(stream,cmd['name']+'.'+stream+'.log'),digest)
    return r


REPORTS = {g:recorded(g) for g in ('cyd','c3','control','numeric','history-cyd01','history-c301','history-control01')}
N = REPORTS['numeric']
FROZEN = {}
for original,pin in N['inputs'].items():
    key = norm(original).casefold();need(key not in FROZEN,'unique numerical input origin');FROZEN[key] = pin


def frozen(original):
    key = norm(original).casefold();need(key in FROZEN,'numerical snapshot origin')
    pin = FROZEN[key]
    return bound('numeric',pin['snapshot'],pin['sha256'],pin.get('bytes'))


def archived(original):
    rel = relative(original);found = []
    if 'canonical/'+rel in FILES: found.append(raw('canonical/'+rel))
    for group,source in GROUPS.items():
        if rel.startswith(source+'/') and group+rel[len(source):] in FILES:
            found.append(raw(group+rel[len(source):]))
    if norm(original).casefold() in FROZEN: found.append(frozen(original))
    need(found and len({sha(x) for x in found}) == 1,'unambiguous saved origin')
    return found[0]


PINS = {
    'tests/vorbis_reset_protocol.py': '6c9c1dd1383224e895edcc1d608586d83b22619a904604002f734c205a82d16b',
    'tests/vorbis_registered_protocol.py': 'a64692cebcad800f0dc8236d852e9853def5c6e955f24dab2d6c90e21d96cf46',
    'tests/test-vorbis-reset-protocol.py': '3c45ea9ee289863da397699007e7ad2ac3b9980fab4337c3efbe8bd6aa805fc2',
    'tests/test-vorbis-registered-protocol.py': '386326a7e8975e82d90675e7e88c43ae997fd938b84d11af21405bea6059fc16',
    'tests/test-vorbis-floor1-reference-outcomes.py': '25f4b37576bdbaaf957b63c1ddf79553e437ad21f7b95097056e17996660ffab',
    'tests/test-vorbis-registered-cmake.py': '7a10eb07c60576ce51d5930255e52089b90a25992fbd86d7f2d8d1a20d7bedad',
    'tests/run-vorbis-floor1-positions-qemu.py': '68c8ca0f12ba49b69d7825d03a7880af4bd347eb69def54f406f78fd1cf7bb30',
    'tests/check-vorbis-floor1-render.py': '95f92986f4e2a52971eaf69072d202f95ec40fb14352a9ffc412efbdc0e2013d',
    'tests/target/vorbis_floor1_positions_qemu/main/registered.c': '47bb09ce2badccba02684ba81f5c9f15b77bb518bb1530415d10a64d1d6a1cbf',
    'tests/target/vorbis_floor1_positions_qemu/main/reset_cycles.h': '9478d30639d75bd85a7f330cf6370af74ecc1d8573df02c7f5b289740bef9892',
    'tests/target/vorbis_floor1_positions_qemu/main/CMakeLists.txt': '6dc46475a7e64ae95304e65c57e93eafc4adf3855621ade536bd0c8743588006',
    'tests/target/vorbis_floor1_positions_qemu/sdk-build.ps1': '959d60806db62c46ed9d00bb35efab5b8b14c18b40e8b82a309c38a6980a1ae7',
    '.build/cyd-vorbis-format-command-01.py': '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e',
    'tests/vorbis_format_corpus/generate_floor1_slopes.py': '835158eac4bb5a6eebaa43a2ec45b331b93943f045d82e41abe31bf389dab37b',
    'tests/vorbis_block_matrix/generate_minimal.py': '8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1',
}
for name,digest in PINS.items(): need(sha(raw('canonical/'+name)) == digest,'reviewed owned source: '+name)


def approved_parser(name):
    """Only these two exact-hash, reviewed stdlib-only owned parsers may execute."""
    need(name in ('tests/vorbis_reset_protocol.py','tests/vorbis_registered_protocol.py'),'approved pure parser name')
    source = raw('canonical/'+name);need(sha(source) == PINS[name],'approved pure parser hash')
    module = types.ModuleType('saved_'+name.rsplit('/',1)[-1].replace('.py',''))
    exec(compile(source,'canonical/'+name,'exec'),module.__dict__)
    return module.validate_log


reset_parser = approved_parser('tests/vorbis_reset_protocol.py')
registry_parser = approved_parser('tests/vorbis_registered_protocol.py')
CORPUS_SHA = '3893c81d5af0f7ed7110633e210a211a633404710cafc0570208df47d56a3182'
manifest,matrix = obj('corpus/manifest.json'),obj('corpus/matrix.json')
need(sha(raw('corpus/manifest.json')) == CORPUS_SHA and manifest['construction_only'] is True and
     manifest['generator_sha256'] == PINS['tests/vorbis_format_corpus/generate_floor1_slopes.py'] and
     manifest['helper']['sha256'] == PINS['tests/vorbis_block_matrix/generate_minimal.py'],'pinned construction corpus')
CORPUS_NAMES = [x['path'] for x in manifest['files']]+['manifest.json']
need(len(CORPUS_NAMES) == len(set(CORPUS_NAMES)) and
     {x.removeprefix('corpus/') for x in FILES if x.startswith('corpus/')} == set(CORPUS_NAMES),'exact corpus inventory')
for row in manifest['files']:
    need(len(raw('corpus/'+row['path'])) == row['bytes'] and sha(raw('corpus/'+row['path'])) == row['sha256'],'corpus body hash')
for name in CORPUS_NAMES: need(frozen(origin('corpus',name)) == raw('corpus/'+name),'numerical full exact corpus snapshot')
cases = matrix['cases']
need(matrix['schema'] == 'vorbis-floor1-slopes-v1' and len(cases) == 14 and
     [c['expected_valid'] for c in cases] == [True]*8+[False]*6 and
     matrix['expected_valid_pcm_bytes'] == 225280 and matrix['valid_raw_packet_count'] == 112,'complete slopes matrix')


def arg(argv,flag):
    need(argv.count(flag) == 1 and argv.index(flag)+1 < len(argv),'unique argument: '+flag)
    return argv[argv.index(flag)+1]


def command_logs(group,reference=False):
    report = REPORTS[group];logs = {};tools = {norm(x).casefold() for x in report['tools']}
    for c in report['commands']:
        name = c['name'];need(name not in logs and type(c.get('pid')) is int and c['pid'] > 0,'unique owned command PID')
        need(norm(c['cwd']).casefold() == origin(group).casefold() and norm(c['argv'][0]).casefold() in tools,'command cwd/tool binding')
        if reference:
            need(c['state'] == 'terminal' and c['reaped'] is True and not c.get('forced_stop') and type(c.get('returncode')) is int,'normal reaped reference child')
        else:
            need(c['state'] == 'complete' and type(c.get('exit_status')) is int and c['exit_status'] == 0 and
                 'tree_stop_error' not in c,'actual target terminal0')
        streams = []
        for stream in ('stdout','stderr'):
            data = raw(group+'/'+norm(c.get(stream,name+'.'+stream+'.log')))
            need(sha(data) == c[stream+'_sha256'],'owned command log binding')
            streams.append(data.decode('utf-8',errors='replace').replace('\r\n','\n'))
        logs[name] = (c,*streams)
    return logs


PANIC = r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP'
SDK_HEAD = {'esp32':'7101770dc6db2667b3c477cc31365dd1acd6db4e','esp32c3':'9a97f6c54ec638111ce55cd36581b3c192f15207'}
PCM = {}
for group,target in (('cyd','esp32'),('c3','esp32c3'),('control','esp32')):
    r = REPORTS[group];control = 'reset-skip' if group == 'control' else None;core = 1 if target == 'esp32' else 0
    need(r['completed'] is True and r['passed'] is False and r['target'] == target and r['renderer'] == 'on' and
         r['dispatch'] == 'registered' and r['reset_cycles'] is True and r['control'] == control and
         r['corpus_kind'] == 'slopes' and r['corpus_manifest_sha256'] == CORPUS_SHA and
         r['control_effective'] is bool(control) and r['target_capture_completed'] is (not control) and
         r['raw_reset_behavior_qualified'] is (not control) and r['registered_callbacks_qualified'] is (not control) and
         r['numerical_reference_qualified'] is False and r['elf_machine'] == (94 if core else 243) and
         r['result'] == ('RESET_SKIP_CONTROL_EFFECTIVE' if control else 'RENDER_CAPTURED'),'actual finite reset result/architecture')
    need(all(r[x] is False for x in ('full_G6_qualified','production_radio_integration','physical_device')),'finite target scope')
    logs = command_logs(group)
    need(set(logs) == {'sdk-head','sdk-clean','build','symbols','merge','qemu','sdk-head-after','sdk-clean-after'},'all owned commands')
    need(logs['sdk-head'][1].strip() == logs['sdk-head-after'][1].strip() == SDK_HEAD[target] and
         not logs['sdk-clean'][1].strip() and not logs['sdk-clean-after'][1].strip(),'SDK clean before/after identity')
    build,qargs = logs['build'][0]['argv'],logs['qemu'][0]['argv']
    need(arg(build,'-Target') == target and arg(build,'-Renderer') == 'on' and arg(build,'-Dispatch') == 'registered' and
         arg(build,'-BindingControl') == 'none' and arg(build,'-ResetCycles') == 'on' and
         norm(arg(build,'-Campaign')).casefold() == origin(group).casefold() and
         norm(arg(build,'-File')).casefold() == origin(group,'sources/project/sdk-build.ps1').casefold(),'actual frozen build/reset route')
    need(arg(qargs,'-M') == target and arg(qargs,'-smp') == ('2' if core else '1') and arg(qargs,'-nic') == 'none' and
         arg(qargs,'-monitor') == 'none' and all(x in qargs for x in ('-snapshot','-no-reboot')) and
         origin(group,'qemu-flash.bin').casefold() in norm(arg(qargs,'-drive')).casefold(),'actual machine/core/flash isolation')
    config = raw(group+'/sdkconfig')
    need((b'CONFIG_FREERTOS_UNICORE=y' in config) == (core == 0) and
         ('CONFIG_IDF_TARGET="'+target+'"').encode() in config,'target/core SDK configuration')
    for filename,source in (('runner.py','tests/run-vorbis-floor1-positions-qemu.py'),
            ('registered_protocol.py','tests/vorbis_registered_protocol.py'),('reset_protocol.py','tests/vorbis_reset_protocol.py')):
        need(raw(group+'/sources/'+filename) == raw('canonical/'+source),'executed frozen owned source')
    platform = 'esp32-cyd2usb' if target == 'esp32' else 'esp32c3-oled'
    for name in r['variant_sources']:
        part = norm(name).removeprefix('variant/')
        need(raw(group+'/'+norm(name)) == raw(group+'/sources/main/'+part) ==
             raw('canonical/idf/'+platform+'-native/main/'+part),'unchanged executed repair sources')
    for name in r['project_sources']:
        part = norm(name).removeprefix('project/')
        before = raw('corpus/fixture.h') if part == 'main/fixture.h' else raw(group+'/sources/'+part) if part in ('sdkconfig.defaults','partitions.csv') else raw(group+'/sources/project/'+part)
        expected = before
        # Publication README text may be updated after the campaign. Its actual
        # frozen/build copies still must match each other and their report pins.
        if part not in ('main/fixture.h','sdkconfig.defaults','partitions.csv','README.md'):
            need(before == raw('canonical/tests/target/vorbis_floor1_positions_qemu/'+part),'frozen project is reviewed owned source')
        if control and part == 'main/reset_cycles.h':
            anchor = b'#define VORBIS_RESET_SKIP_CONTROL 0'
            need(before.count(anchor) == 1,'single skipped-reset control anchor')
            expected = before.replace(anchor,b'#define VORBIS_RESET_SKIP_CONTROL 1',1)
        need(raw(group+'/'+norm(name)) == expected,'unchanged project or exact single reset-skip mutation')
    for name in CORPUS_NAMES: need(raw(group+'/sources/corpus/'+name) == raw('corpus/'+name),'full actual corpus bytes')
    commands = obj(group+'/build/compile_commands.json')
    rows = [row for row in commands if norm(row['file']).casefold() == origin(group,'project/main/registered.c').casefold()]
    need(len(rows) == 1 and rows == r['harness_compile_rows'] and
         re.search(r'(?:^|\s)-DVORBIS_RESET_CYCLES=1(?:\s|$)',rows[0]['command']),'actual reset-enabled registered compilation')
    variants = [row for row in commands if norm(row['file']).casefold().startswith(origin(group,'variant').casefold()+'/')]
    need(variants == r['compile_rows'] and len(variants) == 2 and
         {norm(row['file']).rsplit('/',1)[-1] for row in variants} == {'setup.c','output.c'},'actual repair compilation rows')
    symbols = logs['symbols'][1]
    for symbol in ('esp_audio_dec_reset','__wrap_esp_vorbis_dec_register','__wrap_esp_vorbis_dec_open',
            '__wrap_esp_vorbis_dec_decode','__wrap_floor1_inverse2','esp_audio_dec_get_ops','esp_audio_dec_open',
            'esp_audio_dec_process','esp_audio_dec_get_info','esp_audio_dec_close','esp_audio_dec_unregister'):
        need(re.search(r'\b'+symbol+r'$',symbols,re.M),'actual public/wrapper symbol: '+symbol)
    elf_names = [norm(name) for name in r['build_outputs'] if name.endswith('.elf')]
    need(len(elf_names) == 1 and origin(group,elf_names[0]).casefold() in
         {norm(x).casefold() for x in logs['symbols'][0]['argv']},'symbols command binds recorded ELF identity')
    need(not re.search(PANIC,logs['qemu'][2]),'target stderr panic exclusion')
    facts = reset_parser(logs['qemu'][1],matrix,target,control,returncode=logs['qemu'][0]['exit_status'],timed_out=False,interrupted=False)
    need(facts == r['observed_reset'],'reused exact-hash reset parser replay binding')
    if control:
        need(facts['exact_failure'] == 'reset_primer_empty' and facts['control_primer']['bytes'] > 0 and
             facts['reset_cycles_qualified'] is False and facts['registered_callbacks_qualified'] is False and
             r['observed']['exact_failure'] == ['0','reset_primer_empty'] and
             not any(alias.startswith('control/pcm/') for alias in FILES),'specific nonempty-primer control remains unqualified')
        continue
    need(registry_parser(logs['qemu'][1],matrix,target,returncode=0,timed_out=False,interrupted=False) == r['observed_registry'],
         'reused reviewed registry parser binding')
    pins = {norm(name):digest for name,digest in r['observed']['pcm'].items()}
    need(set(pins) == {f'pcm/{i}.s16le' for i in range(8)},'all target baseline PCM files')
    events = re.findall(r'^FLOOR1_PCM case=(\d+) packet=(\d+) consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)$',logs['qemu'][1],re.M)
    need([(int(c),int(p)) for c,p,*_ in events] == [(c,p) for c in range(8) for p in range(14)],'all baseline packet records')
    PCM[target] = {}
    for i in range(8):
        data = b''.join(bytes.fromhex(event[4]) for event in events[i*14:(i+1)*14])
        need(data == raw(group+f'/pcm/{i}.s16le') and len(data) == 28160 and any(data) and
             sha(data) == pins[f'pcm/{i}.s16le'] == facts['baseline_pcm_sha256'][str(i)],'raw baseline/transcript/hash binds every reset replay and prefix')
        PCM[target][i] = data


for group in ('history-cyd01','history-c301','history-control01'):
    r = REPORTS[group]
    need(r['completed'] is False and r['passed'] is False and r['result'] == 'NONPASS' and
         r['raw_reset_behavior_qualified'] is False and r['registered_callbacks_qualified'] is False and
         r['target_capture_completed'] is False and not any(c['name'] == 'qemu' for c in r['commands']) and
         any(c['name'] == 'build' and c.get('exit_status') == 1 for c in r['commands']),'preserved pre-QEMU failed01 history')


def metrics(a,b):
    need(len(a) == len(b) and len(a)%2 == 0,'complete signed16 vector length')
    errors = [abs(x[0]-y[0]) for x,y in zip(struct.iter_unpack('<h',a),struct.iter_unpack('<h',b))]
    return dict(samples=len(errors),max_abs_error=max(errors,default=0),over_bound=sum(e>2 for e in errors),allowed=2)


need(N['schema'] == 'floor1-render-independent-check-v1' and N['completed'] is True and N['passed'] is True and
     N['finite_renderer_qualified'] is True and N['both_architectures_qualified'] is True and
     N['result'] == 'FINITE_RENDERER_NUMERICALLY_QUALIFIED' and N['corpus_kind'] == 'slopes' and
     N['corpus_manifest_sha256'] == CORPUS_SHA and N['predeclared_max_abs_error'] == 2 and N['failures'] == [] and
     N['ffmpeg_executed'] is True and N['sdk_or_target_executed'] is False and not N['baselines'] and not N['controls'] and
     all(N[k] is False for k in ('full_G6_qualified','production_radio_integration','physical_device')),'complete independent fresh numerical report')
need(frozen(norm(M['checkout_root'])+'/tests/check-vorbis-floor1-render.py') ==
     raw('canonical/tests/check-vorbis-floor1-render.py'),'numerical checker frozen source binding')
need(len(N['references']) == 1 and N['references'][0]['kind'] == 'fresh_libvorbis' and
     len(N['references'][0]['cases']) == 14 and len(N['commands']) == 14 and len(N['targets']) == 2 and
     {t['target'] for t in N['targets']} == {'esp32','esp32c3'},'fourteen fresh references and both distinct targets')
reference = N['references'][0]
FFMPEG_SHA = '09948d4cdd0650da6ff5a87577469f2a218dc2615ae379f8f734d24c49de0f73'
need(reference['ffmpeg_sha256'] == FFMPEG_SHA,'approved FFmpeg executable historical identity')
logs = command_logs('numeric',reference=True)
need(set(logs) == {f'case-{i:02d}-libvorbis' for i in range(14)},'all actual named fresh children')
refs = {}
for i,fact in enumerate(reference['cases']):
    name = f'case-{i:02d}-libvorbis';cmd,stdout,stderr = logs[name];argv = cmd['argv']
    need((fact['index'],fact['id']) == (i,cases[i]['id']) and fact['qualified'] is True and
         fact['expected_valid'] is cases[i]['expected_valid'],'reference case order/actual qualification')
    tool = [pin for path,pin in N['tools'].items() if norm(path).casefold() == norm(argv[0]).casefold()]
    need(len(tool) == 1 and (tool[0]['sha256'] if isinstance(tool[0],dict) else tool[0]) == FFMPEG_SHA and
         norm(argv[0]).casefold() == norm(reference['ffmpeg']).casefold(),'actual reference executable pin')
    expected = [argv[0],'-nostdin','-n','-hide_banner','-loglevel','error','-xerror','-c:a','libvorbis',
        '-i',arg(argv,'-i'),'-map','0:a:0','-map_metadata','-1','-fflags','+bitexact','-flags:a','+bitexact',
        '-c:a','pcm_s16le','-f','wav',argv[-1]]
    need(argv == expected and norm(argv[-1]).casefold() == origin('numeric',name+'.wav').casefold() and
         norm(fact['wav_path']).casefold() == origin('numeric',name+'.wav').casefold() and
         frozen(arg(argv,'-i')) == raw('corpus/'+cases[i]['ogg']) and cmd['returncode'] == fact['returncode'],
         'exact reference command and carrier, with no signal transforms')
    if i < 8:
        data,wavbytes = raw('numeric/'+name+'.s16le'),raw('numeric/'+name+'.wav')
        need(norm(fact['pcm_path']).casefold() == origin('numeric',name+'.s16le').casefold() and
             frozen(fact['pcm_path']) == data and frozen(fact['wav_path']) == wavbytes and cmd['returncode'] == 0 and
             fact['decoded'] is True and fact['codec_rejection'] is False and len(data) == fact['pcm_bytes'] == 28160 and
             any(data) and sha(data) == fact['pcm_sha256'] and sha(wavbytes) == fact['wav_sha256'],'full nonzero successful reference PCM/WAV')
        with wave.open(io.BytesIO(wavbytes),'rb') as stream:
            metadata = dict(channels=stream.getnchannels(),sample_rate=stream.getframerate(),sample_bytes=stream.getsampwidth(),
                            frames=stream.getnframes(),compression=stream.getcomptype())
            need(metadata == dict(channels=2,sample_rate=48000,sample_bytes=2,frames=7040,compression='NONE') == fact['metadata'] and
                 stream.readframes(7040) == data and not stream.readframes(1),'complete exact stereo48k/S16 WAV binding')
        refs[i] = data
    else:
        need(cmd['returncode'] in (1,-1094995529,3199971767) and fact['decoded'] is False and fact['codec_rejection'] is True and
             fact['pcm_bytes'] == 0 and fact['pcm_sha256'] == sha(b'') and fact['metadata'] is None,'normal INVALIDDATA refusal without PCM')
        codec = re.search(r'\[libvorbis @ [^]]+\].*(?:header.*(?:damaged|corrupt|invalid)|floor.*(?:invalid|error))|'
                          r'\[dec:libvorbis @ [^]]+\] Error while opening decoder: Invalid data found',stderr,re.I)
        need(codec is not None and not re.search(r'Unknown decoder|Decoder .*not found|Unrecognized option|Option .*not found|'
             r'No such file or directory|Permission denied|Error writing|Unable to find.*output format',stderr,re.I),'codec refusal is not infrastructure failure')
        lines = stderr.splitlines();indices = [j for j,line in enumerate(lines) if line.startswith('Error opening output')]
        need(not indices or (len(indices) == 2 and indices[1] == indices[0]+1 and
             lines[indices[0]] == 'Error opening output file '+argv[-1]+'.' and
             lines[indices[1]] == 'Error opening output files: Invalid data found when processing input' and
             stderr.find(lines[indices[0]]) > codec.end()),'only exact codec-consequent output path refusal')
        for suffix in ('.wav','.s16le'):
            alias = 'numeric/'+name+suffix
            need(alias not in FILES or not raw(alias),'no invalid reference output')
        need(fact['wav_sha256'] is None or fact['wav_sha256'] == sha(b''),'invalid reference WAV identity')
for target in N['targets']:
    platform = target['target'];group = 'cyd' if platform == 'esp32' else 'c3';core = 1 if group == 'cyd' else 0
    need(target['role'] == 'candidate' and target['core'] == core and target['dispatch'] == 'registered' and
         target['registered_callbacks_qualified'] is True and target['raw_reset_behavior_qualified'] is True and
         target['numerically_qualified'] is True and target['pcm_bytes'] == 225280 and len(target['cases']) == 8 and
         target['report_sha256'] == sha(raw(group+'/report.json')) and
         norm(target['report']).casefold() == origin(group,'report.json').casefold() and
         frozen(target['report']) == raw(group+'/report.json'),'numeric exact target report/raw reset binding')
    for i,fact in enumerate(target['cases']):
        data = PCM[platform][i];actual = metrics(data,refs[i])
        need((fact['index'],fact['id']) == (i,cases[i]['id']) and fact['raw_sha256'] == sha(data) == target['pcm_sha256'][str(i)] and
             all(fact[k] == v for k,v in actual.items()) and actual['over_bound'] == 0 and len(fact['packets']) == 14,
             'independent complete signed16 metrics within fixed2 bound')
        offset = 0
        for packet,size in enumerate(cases[i]['expected_packet_bytes']):
            need(fact['packets'][packet] == dict(packet=packet,**metrics(data[offset:offset+size],refs[i][offset:offset+size])),
                 'independent every-packet signed16 metric')
            offset += size
        need(offset == 28160,'no omitted PCM suffix')


WRAPPER_SHA = PINS['.build/cyd-vorbis-format-command-01.py']


def wrapper(alias):
    receipt = obj(alias)
    need(receipt['status'] == 'TERMINAL' and type(receipt.get('owned_pid')) is int and receipt['owned_pid'] > 0 and
         type(receipt.get('returncode')) is int and receipt['runner_sha256'] == WRAPPER_SHA and
         re.fullmatch('[0-9a-f]{64}',receipt['executable_sha256']) and
         norm(receipt['cwd']).casefold() == norm(M['checkout_root']).casefold(),'actual owned outer terminal/reap receipt')
    for path,pin in receipt['logs'].items():
        data = archived(path);need(len(data) == pin['bytes'] and sha(data) == pin['sha256'],'outer log binding')
    return receipt


for name,count,script in (('reset-protocol',14,'tests/test-vorbis-reset-protocol.py'),
        ('registry',12,'tests/test-vorbis-registered-protocol.py'),
        ('numeric-classifier',8,'tests/test-vorbis-floor1-reference-outcomes.py'),
        ('cmake',22,'tests/test-vorbis-registered-cmake.py')):
    receipt = wrapper('host/'+name+'.json')
    need(receipt['returncode'] == 0 and script in [norm(x) for x in receipt['argv']],'actual complete owned host suite')
    text = raw('host/'+name+'.stderr.log').decode('utf-8').replace('\r\n','\n')
    need(re.findall(r'^Ran (\d+) tests in [0-9.]+s$',text,re.M) == [str(count)] and text.endswith('\nOK\n') and
         len(re.findall(r'^test_\w+ .* \.\.\. ok$',text,re.M)) == count,'actual full host suite count/outcome')


def before_after(before,after):
    rows = obj('host/'+before);need(rows == obj('host/'+after),'retained before/after input identity')
    need(rows and len({row['path'] for row in rows}) == len(rows),'unique before/after inputs')
    for pin in rows:
        need(type(pin['bytes']) is int and pin['bytes'] > 0 and re.fullmatch('[0-9a-f]{64}',pin['sha256']),'selected source/tool identity')
        path = norm(pin['path'])
        if ':' not in path:
            need(len(raw('canonical/'+path)) == pin['bytes'] and sha(raw('canonical/'+path)) == pin['sha256'],'historical recorded source bytes')
        elif path.casefold().startswith(norm(M['checkout_root']).casefold()+'/'):
            data = raw('canonical/'+relative(path))
            need(len(data) == pin['bytes'] and sha(data) == pin['sha256'],'historical selected checkout source')
        if pin.get('snapshot'):
            data = raw('host/'+pin['snapshot'])
            need(len(data) == pin['bytes'] and sha(data) == pin['sha256'],'retained selected source snapshot')
    return rows


need(len(before_after('reset-protocol.sources-before.json','reset-protocol.sources-after.json')) == 3,'reset protocol three-source identity')
need(len(before_after('cmake-before.json','cmake-after.json')) == 6,'CMake selected six-source/tool identity')
phase = obj('cmake/report.json')
need(sha(raw('cmake/report.json')) == '4fab1612f9b187a5e16b5d22fd4af6da7c21ab897e1516e3ed6f62ecaa10bd02' and
     phase['passed'] is True and phase['tests_run'] == 22 and len(phase['commands']) == 22 and
     phase['inputs_unchanged'] is True and phase['frozen_copies_unchanged'] is True and phase['configure_only'] is True and
     all(phase[k] is False for k in ('compiler_invoked','sdk_export_invoked','runtime_invoked')),'actual pinned CMake22 configuration-only evidence')
need(raw('cmake/component.cmake') == raw('canonical/tests/target/vorbis_floor1_positions_qemu/main/CMakeLists.txt') and
     sha(raw('cmake/component.cmake')) == phase['frozen_source']['sha256'] and
     sha(raw('cmake/binding-before-early.cmake')) == phase['negative_control']['sha256'],'frozen CMake subject/control bytes')
need(len(set(phase['expected_cases'])) == 22 and {c['name'] for c in phase['commands']} == set(phase['expected_cases']),'all exact phase/recipe cases')
for c in phase['commands']:
    name = c['name'];script = raw('cmake/'+name+'/case.cmake')
    need(len(script) == c['script']['bytes'] and sha(script) == c['script']['sha256'] and c['passed'] is True and
         c['timed_out'] is False and c['interrupted'] is False and c['returncode'] == (1 if c['expected_error'] else 0), 'actual CMake script/result binding')
    for stream in ('stdout','stderr'):
        data = raw('cmake/'+name+'/'+stream+'.log')
        need(len(data) == c[stream]['bytes'] and sha(data) == c[stream]['sha256'],'actual CMake log hash')


current = {}
for alias in FILES:
    if not(alias.startswith('commands/') and alias.endswith('.json')): continue
    candidate = obj(alias)
    if 'owned_pid' not in candidate: continue
    receipt = wrapper(alias);argv = receipt['argv']
    if '--output' not in argv: continue
    output = norm(arg(argv,'--output'))
    if not output.casefold().startswith(norm(M['checkout_root']).casefold()+'/'):
        output = norm(M['checkout_root'])+'/'+output
    matches = [g for g in ('cyd','c3','control','numeric') if output.casefold() == origin(g).casefold()]
    if matches:
        group = matches[0];need(group not in current and receipt['returncode'] == 0,'one actual successful current campaign wrapper')
        script = 'tests/check-vorbis-floor1-render.py' if group == 'numeric' else 'tests/run-vorbis-floor1-positions-qemu.py'
        need(script in [norm(x) for x in argv],'actual campaign script argv')
        need(group == 'numeric' or '--reset-cycles' in argv,'actual reset mode outer selection')
        current[group] = receipt
need(set(current) == {'cyd','c3','control','numeric'},'all actual campaign wrapper receipts')

print(json.dumps(dict(archive_verified=True,aliases=len(FILES),unique_objects=len(CACHE),
    protocol_method='explicit reviewed hash-bound own pure parser reuse',independent_second_protocol_parser=False,
    finite_raw_reset_qualified=True,both_architectures=True,reset_calls_each=72,reset_rounds_each=32,
    baseline_packets_each=112,replay_packets_each=448,prefix_packets_each=96,accepted_packets_each=656,
    baseline_tiny_retries_each=312,reset_tiny_retries_each=24,total_tiny_retries_each=336,
    actual_pcm_bytes_each=1339392,finite_signed16_bound=2,
    actual_max_abs_error=max(metrics(PCM[t][i],refs[i])['max_abs_error'] for t in PCM for i in range(8)),
    skipped_reset_control_effective=True,host_tests=dict(reset=14,registry=12,classifier=8,cmake=22),
    registry_classifier_historical_before_after_source_pins_available=False,
    historical_failed01_preserved=True,omitted_identity_records_checked=len(IDENTITY_ONLY),
    omitted_binary_semantics_verified=False,full_dependency_closure=False,late_recipe_execution_pin=False,
    canonical_documentation_role='collection-time text; executed source snapshots remain separately bound',
    new_decoder_or_target_execution=False,full_G1_qualified=False,full_G3_qualified=False,full_G6_qualified=False,
    ogg_qualified=False,production_radio_integration=False,physical_device=False)))
