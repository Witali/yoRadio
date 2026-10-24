"""Offline current31 evidence replay. No SDK, decoder or external program runs.

Target events and signed16 metrics/relations are independently recomputed.
Only exact-hash owned pure C-array/link-recipe reader definitions are reused.
"""
from pathlib import Path, PurePosixPath
from collections import Counter
import ast
import gzip
import hashlib
import io
import json
import math
import posixpath
import re
import struct
import types
import wave


def need(ok,reason):
    if not ok: raise ValueError(reason)


def sha(data): return hashlib.sha256(data).hexdigest()


def norm(value): return str(value).replace('\\','/').rstrip('/')


def safe(value):
    need(isinstance(value,str) and value and norm(value)==value and ':' not in value and
         not PurePosixPath(value).is_absolute() and all(p not in ('','.','..') for p in value.split('/')),'safe archive alias')
    return value


ROOT=Path(__file__).resolve().parent
M=json.loads((ROOT/'manifest.json').read_bytes())
GROUPS={'prep':'.build/vorbis-format31-current-prep-01','host':'.build/vorbis-format31-current-host-01',
    'commands':'.build/vorbis-format31-current-validation-20261024-01','history01':'.build/vorbis-format31-current-cyd-01',
    'capture':'.build/vorbis-format31-current-cyd-02','numeric-prep':'.build/vorbis-format31-current-numeric-prep-01',
    'numeric':'.build/vorbis-format31-current-numeric-01'}
need(M['schema']=='vorbis-current-format31-evidence-v1' and M['complete'] is True and M['collection_sources_unchanged'] is True and
     M['groups']==GROUPS and M['predeclared_max_abs_error']==2 and M['corpus']==dict(cases=31,packets=434,pcm_bytes=738560,relations=14) and
     all(M[k] is False for k in ('full_G1_qualified','full_G4_qualified','full_G5_qualified','full_G6_qualified',
         'format_conformance_qualified','ogg_qualified','production_radio_integration','physical_device')),'finite complete archive scope')
FILES,CACHE=M['files'],{}
for alias,pin in FILES.items():
    safe(alias)
    need(type(pin['bytes']) is int and pin['bytes']>=0 and re.fullmatch('[0-9a-f]{64}',pin['sha256']) and
         pin['object']=='objects/'+pin['sha256']+'.gz','content address declaration')
    if pin['object'] not in CACHE: CACHE[pin['object']]=gzip.decompress((ROOT/pin['object']).read_bytes())
    data=CACHE[pin['object']]
    need(len(data)==pin['bytes'] and sha(data)==pin['sha256'],'archived body identity '+alias)
need(M['logical_files']==len(FILES) and M['unique_objects']==len(CACHE) and
     M['selected_uncompressed_bytes']==sum(x['bytes'] for x in FILES.values()),'archive accounting')
need({p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}==
     set(CACHE)|{'manifest.json','verifier.py','README.md','.gitattributes','CHECKPOINT.md'},'exact physical archive inventory')


def raw(alias):
    safe(alias);need(alias in FILES,'required saved body '+alias)
    return CACHE[FILES[alias]['object']]


def obj(alias): return json.loads(raw(alias))


for name in ('verifier.py','README.md','.gitattributes','CHECKPOINT.md'):
    need((ROOT/name).read_bytes()==raw(name),'physical root body binding')
need(raw('.gitattributes')==b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n','literal preservation rule')
ORIGINS=M['origins']
for key,row in ORIGINS.items():
    need(key==norm(row['path']).casefold() and type(row['bytes']) is int and row['bytes']>=0 and
         re.fullmatch('[0-9a-f]{64}',row['sha256']),'original identity declaration')
    if 'alias' in row:
        need(len(raw(row['alias']))==row['bytes'] and sha(raw(row['alias']))==row['sha256'],'original saved body binding')
    else: need(bool(row.get('omission_reason')),'explicit historical identity-only omission')
need(M['omissions']==[row for row in ORIGINS.values() if 'alias' not in row],'exact explicit omission accounting')
CHECKOUT=norm(M['checkout_root'])


def origin(group,relative=''):
    return CHECKOUT+'/'+GROUPS[group]+('/'+safe(norm(relative)) if relative else '')


def bound(group,relative,digest=None,size=None,required=True):
    alias=group+'/'+safe(norm(relative))
    if alias in FILES:
        data=raw(alias)
        need((digest is None or sha(data)==digest) and (size is None or len(data)==size),'recorded body '+alias)
        return data
    row=ORIGINS.get(origin(group,relative).casefold())
    need(not required and row is not None and 'alias' not in row and digest==row['sha256'] and
         (size is None or size==row['bytes']),'required body is missing '+alias)
    return None


T=obj('capture/report.json');N=obj('numeric/report.json');H=obj('history01/report.json')
FROZEN={norm(path).casefold():row for path,row in T['inputs'].items()}
need(len(FROZEN)==len(T['inputs']),'unique capture source origins')


def artifact(original,digest=None,size=None,required=True):
    key=norm(original).casefold();candidates=[]
    row=ORIGINS.get(key)
    if row is not None and (digest is None or row['sha256']==digest):
        if 'alias' in row: candidates.append(raw(row['alias']))
        elif not required:
            need((digest is None or digest==row['sha256']) and (size is None or size==row['bytes']),'identity-only original')
            return None
    if key in FROZEN and (digest is None or FROZEN[key]['sha256']==digest):
        pin=FROZEN[key];data=bound('capture',pin['snapshot'],pin['sha256'],pin.get('bytes'),required)
        if data is not None: candidates.append(data)
    need(candidates and len({sha(x) for x in candidates})==1,'unambiguous archived original '+norm(original))
    data=candidates[0]
    need((digest is None or sha(data)==digest) and (size is None or len(data)==size),'original body expected identity')
    return data


for role,pin in N['inputs'].items():
    row=M['numeric_inputs'][role]
    need(row['path'].casefold()==norm(pin['path']).casefold() and row['bytes']==pin['bytes'] and
         row['sha256']==pin['sha256'] and ORIGINS[row['path'].casefold()]==row,'every consumed numeric input retained or explicitly omitted')
    if 'alias' in row: need(sha(raw(row['alias']))==pin['sha256'],'numeric consumed body')
need(set(M['numeric_inputs'])==set(N['inputs']),'exact numerical input roles')

PINS={
    'run-cyd-vorbis-format-expanded31-qemu.py':'cf1de2f4af32b7d5868850732e57a6d28a90ae95134764fd05b11755cc7b7ace',
    'link_recipe.py':'1545657011cca3933f6ee36d8d0127a1c91b5ab908319df7004e8c8796e74316',
    'materialize.py':'fe216578f614f475e7eb96cee8b674f344d6b9d2afd42c46feb7cc8e1eef16bb',
    'protocol.py':'547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e',
    'contract.json':'ef8823f169d08b98fe5586221a7ab9a64904373e3be4f212631a58d1fcdc24ff',
    'data.h':'433ffdc59206485e0650c9fbbb0796bf053725c9dacf0cbdd6c3ebf826318cdf',
    'source-map.json':'f81cfc76044f7d4d1ad9949b8376945afd82815d001b9a4af1672acbb63f0c16',
    'reference-binding31.json':'a13275e2663a428895b326fbfbf9d38458f23b0eeee0811406f39e6dab3874b5',
    'source-pins.json':'564f4ae2568f07ba333180ba6afe47934342b5240e32f69c9df0f442c5ff06e0',
    'reference_binding.py':'fce060219d914542c570b7777b1cfc1f77303f8b5d4d914f23fc5153d20a751f',
    'target/cyd_vorbis_format_expanded31_qemu/main/main.c':'37eaeb25a272ceadaafe36d6309449d31895b7019523333ed0e4c48226d0d065',
    'target/cyd_vorbis_format_expanded31_qemu/sdk-build.ps1':'78663041c04c9c0824e4874f41c7404c8f43e037acc8cf099f79b087729a00e4',
    'target/cyd_vorbis_format_expanded31_qemu/raw-enable.cmake':'0ebdcb4d321368958c9640067775a09798dd27bc9df5aba650acc652fef7c135'}
for name,digest in PINS.items(): need(sha(raw('prep/'+name))==digest,'reviewed preparation source/data pin '+name)
for relative,pin in (('sources/helpers/run.py',PINS['run-cyd-vorbis-format-expanded31-qemu.py']),
        ('sources/helpers/protocol.py',PINS['protocol.py']),('sources/helpers/link_recipe.py',PINS['link_recipe.py']),
        ('sources/project/main/main.c',PINS['target/cyd_vorbis_format_expanded31_qemu/main/main.c']),
        ('sources/project/raw-enable.cmake',PINS['target/cyd_vorbis_format_expanded31_qemu/raw-enable.cmake']),
        ('sources/project/sdk-build.ps1',PINS['target/cyd_vorbis_format_expanded31_qemu/sdk-build.ps1'])):
    bound('capture',relative,pin)
CURRENT={'vorbis_repair/setup.c':'39d3d621e5e292258d6c0b6c48639a89d97aa7473ffb1273259af0af773fc225',
    'vorbis_repair/output.c':'0c2d2f7d6cb2aa294df6294f5c8ae089811220485917075d3a814a1275874e28',
    'vorbis_repair_abi.h':'e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60',
    'vorbis_repair/floor1_render.h':'3b24c3980895de79c2b3cd6460e31182d7fbc5192d474bc7e88be1fe9f917b4b',
    'vorbis_repair/COPYING':'d2ab5758336489da61c12cc5bb757da5339c4ae9001f9bb0562b4370249af814',
    'compat/vorbis_repair/enable.cmake':'1bfae06817e5b9bdb2ec1796c16ff3d664f7f8086fd51f3ca09823ad840a24b8'}
for name,digest in CURRENT.items():
    canonical=raw('canonical/idf/esp32-cyd2usb-native/main/'+name)
    need(sha(canonical)==digest and bound('capture','sources/candidate/'+name,digest)==canonical,'current executable source snapshots')
    variant=PINS['target/cyd_vorbis_format_expanded31_qemu/raw-enable.cmake'] if name.startswith('compat/') else digest
    bound('capture','variant/'+name,variant)


def recorded(group,r):
    for pin in r.get('inputs',{}).values(): bound(group,pin['snapshot'],pin['sha256'],pin.get('bytes'),False)
    for field in ('build_outputs','variant_sources'):
        for name,digest in r.get(field,{}).items(): bound(group,name,digest,required=False)
    for command in r.get('commands',[]):
        for stream in ('stdout','stderr'):
            if command.get(stream+'_sha256'):
                bound(group,command['name']+'.'+stream+'.log',command[stream+'_sha256'])


recorded('capture',T);recorded('history01',H)
COMMANDS=('sdk-head','sdk-clean','build','setup-macros','link-recipe','symbols','merge','qemu','sdk-head-after','sdk-clean-after')
need(T['completed'] is True and T['passed'] is False and T['target_capture_completed'] is True and T['checked_decode_completed'] is True and
     T['result']=='CHECKED_CORPUS_PCM_CAPTURED' and T['renderer']=='on' and T['platform']=='esp32' and T['elf_machine']==94 and
     T['coordinator_core']==0 and T['worker_core']==1 and T['current_source_sha256']==CURRENT and
     T['sdk_revision']=='7101770dc6db2667b3c477cc31365dd1acd6db4e' and
     tuple(x['name'] for x in T['commands'])==COMMANDS and
     all(T[k] is False for k in ('vendor_checked_pcm_equal','vendor_comparison_available','independent_reference_compared',
         'numeric_reference_qualified','format_corpus_qualified','full_G6_qualified','physical_device','production_radio_integration')),
     'exact current capture profile and finite scope')
TOOLS={norm(path).casefold():digest for path,digest in T['tools'].items()}
LOGS={}
for c in T['commands']:
    need(c['state']=='complete' and type(c['exit_status']) is int and c['exit_status']==0 and
         c['timed_out'] is False and c['interrupted'] is False and type(c['pid']) is int and c['pid']>0 and
         norm(c['argv'][0]).casefold() in TOOLS,'all ten owned normal target commands')
    need(norm(c['cwd']).casefold()==origin('capture').casefold() or c['name']=='setup-macros','command working directory')
    LOGS[c['name']]=bound('capture',c['name']+'.stdout.log',c['stdout_sha256']).decode('utf-8',errors='replace').replace('\r\n','\n')
for name in ('sdk-head','sdk-head-after'): need(LOGS[name].strip()==T['sdk_revision'],'actual SDK before/after identity')
for name in ('sdk-clean','sdk-clean-after'): need(not LOGS[name].strip(),'actual clean SDK before/after')
need(T['corpus_array_readback']==dict(cases=31,arrays=155,raw_payload_arrays=93,descriptor_capacity=31,all_raw_bytes_exact=True),
     'recorded complete raw array recovery')
for symbol in ('__wrap_esp_vorbis_dec_open','__wrap_esp_vorbis_dec_decode','esp_vorbis_dec_decode','__wrap_floor1_inverse2'):
    need(re.search(r'\b'+symbol+r'$',LOGS['symbols'],re.M),'actual linked wrapper symbol')
need(re.search(r'^#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 240$',LOGS['setup-macros'],re.M) and
     not re.search(r'^#define (?:LIMIT_TO_64kHz|CONFIG_FREERTOS_UNICORE)\b',LOGS['setup-macros'],re.M),'actual unrestricted240MHz/SMP macro context')
for key in ('CONFIG_IDF_TARGET_ESP32','CONFIG_YORADIO_VORBIS_REPAIR'):
    need(re.search(r'^#define '+key+r' 1$',LOGS['setup-macros'],re.M),'actual checked bridge macro')
qemu=next(x for x in T['commands'] if x['name']=='qemu')
qargs=list(map(norm,qemu['argv']))
for flag,value in (('-M','esp32,audiodev=quiet'),('-smp','2'),('-L','C:/Work/QEMU-ESP32/pc-bios'),('-nic','none'),
                   ('-display','none'),('-monitor','none'),('-serial','stdio')):
    need(qargs.count(flag)==1 and qargs[qargs.index(flag)+1]==value,'actual isolated QEMU argument '+flag)
need('-no-reboot' in qargs and '-snapshot' in qargs and TOOLS[norm(qargs[0]).casefold()]==
     '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d','pinned isolated QEMU and snapshot')

# Explicit reuse of this exact reviewed pure owned recipe reader only.
module=types.ModuleType('saved_owned_link_recipe')
exec(compile(raw('prep/link_recipe.py'),'saved-owned-link-recipe.py','exec'),module.__dict__)
link=T['link_recipe']
replayed=module.inspect(bound('capture','build/build.ninja',link['build_ninja_sha256']).decode('utf-8'),
    bound('capture','build/CMakeFiles/rules.ninja',link['rules_ninja_sha256']).decode('utf-8'),LOGS['link-recipe'],link['elf'],
    Path(norm(obj('capture/build/project_description.json')['c_compiler'])).name.replace('gcc','g++'))
need(all(link[key]==value for key,value in replayed.items()) and link['command_name']=='link-recipe' and
     link['stdout_sha256']==sha(bound('capture','link-recipe.stdout.log')) and link['recipe_observation_only'] is True and
     link['independently_observed_linker_execution'] is False,'actual printed ELF recipe replay, no invented linker receipt')

CONTRACT=obj('prep/contract.json');MODEL=CONTRACT['model'];CASES=MODEL['cases']
need(sha(json.dumps(MODEL,sort_keys=True,separators=(',',':')).encode())==CONTRACT['contract_sha256']==
     '419efac93fc69c65dc162f6b45017b0eb81a276f8de95d50d6f9d1bd06e5aa02' and
     len(CASES)==31 and MODEL['total_packets']==434 and MODEL['total_pcm']==738560 and MODEL['case_mask']==2147483647,
     'exact original complete31 model')
need(bound('capture','sources/corpus/contract.json',PINS['contract.json'])==raw('prep/contract.json') and
     bound('capture','sources/project/main/data.h',PINS['data.h'])==raw('prep/data.h'),'exact executed contract and full data')
mapping=obj('prep/source-map.json');binding=obj('prep/reference-binding31.json')
need(bound('capture','sources/corpus/source-map.json',PINS['source-map.json'])==raw('prep/source-map.json') and
     bound('capture','sources/reference/reference-binding31.json',PINS['reference-binding31.json'])==raw('prep/reference-binding31.json') and
     len(mapping['cases'])==len(binding['cases'])==31 and binding['new_reference_commands_executed'] is False and
     binding['aggregate_reference_campaign_exists'] is False and binding['dual_reference_passed'] is False,'unchanged source/reference bindings')
for pin in CONTRACT['source_facts']: artifact(pin['path'],pin['sha256'],pin['bytes'])
RAW_CASES=[]
for pin in CONTRACT['manifest_inputs']:
    matrix=json.loads(artifact(pin['path'],pin['sha256']))
    parent=norm(pin['path']).rsplit('/',1)[0]
    for case in matrix['cases']:
        RAW_CASES.append({kind:artifact(parent+'/'+case[kind]) for kind in ('identification','setup','audio')})
# Reuse just the approved pure recovery definitions, never its formatter/loader
# or materialize() function. They inspect supplied bytes and have no FS access.
tree=ast.parse(raw('prep/materialize.py'))
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('need','digest','recover')]
need(len(nodes)==3,'exact owned pure C recovery definition set')
namespace=dict(hashlib=hashlib,json=json,re=re)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'saved-owned-C-recovery.py','exec'),namespace)
recovered=namespace['recover'](raw('prep/data.h').decode('ascii'),CONTRACT,RAW_CASES,PINS['contract.json'])
need(len(recovered)==31,'independent complete restricted C readback via approved owned reader')


def replay(log):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|stack overflow|timed out',log,re.I),
         'target panic/timeout/corruption')
    prefix='CYD_VORBIS_CHECKED_CORPUS_';lines=log.splitlines()
    need(not any(('VORBIS_CORPUS_' in x or 'VORBIS_CHECKED_CORPUS_' in x) and not x.startswith(prefix) for x in lines),'foreign target event')
    events=[x[len(prefix):] for x in lines if x.startswith(prefix)];cursor=0
    def take(kind,expected,extra=()):
        nonlocal cursor
        need(cursor<len(events),'missing ordered target event')
        tokens=events[cursor].split(' ');cursor+=1
        need(tokens[0]==kind and all(token.count('=')==1 for token in tokens[1:]),'event kind/syntax/order')
        fields={}
        for token in tokens[1:]:
            key,value=token.split('=');need(key not in fields,'duplicate event field');fields[key]=value
        need(set(fields)==set(expected)|set(extra) and all(fields[k]==str(v) for k,v in expected.items()),'exact finite target event fields')
        return fields
    take('BEGIN',dict(contract=CONTRACT['contract_sha256'],cases=31,packets=434,coordinator=0))
    take('WORKER',dict(core=1,priority=3,configured_stack=16384))
    pcms={}
    for index,c in enumerate(CASES):
        need(c['channels']==2 and len(c['sizes'])==len(c['pcm'])==len(c['frames'])==len(c['transitions'])==14 and
             c['frames'][0]==c['pcm'][0]==0 and c['total_pcm']==sum(c['pcm']),'complete per-case overlap model')
        take('OPEN',dict(case=index,id=c['id'],checked_rc=0,checked_handle=1,core=1))
        data=bytearray();left=right=0
        for packet,(size,pcm,frames,transition) in enumerate(zip(c['sizes'],c['pcm'],c['frames'],c['transitions'])):
            fields=take('PACKET',dict(case=index,packet=packet,size=size,checked_rc=0,checked_consumed=size,
                expected_pcm=pcm,checked_pcm=pcm,checked_rate=c['rate'],checked_channels=2,checked_bits=16,
                checked_canary=1,transition=transition,core=1),('nz_l','nz_r'))
            need(all(re.fullmatch(r'0|[1-9][0-9]*',fields[k]) for k in ('nz_l','nz_r')),'canonical nonzero counts')
            emitted=take('PCM_HEX',dict(case=index,packet=packet,bytes=pcm,core=1),('hex',))['hex']
            need(re.fullmatch(r'(?:[0-9a-f]{2})*',emitted) is not None and len(emitted)==2*pcm,'full exact PCM hex')
            part=bytes.fromhex(emitted);nl=sum(part[i:i+2]!=b'\0\0' for i in range(0,len(part),4));nr=sum(part[i:i+2]!=b'\0\0' for i in range(2,len(part),4))
            need((nl,nr)==(int(fields['nz_l']),int(fields['nz_r'])) and
                 ((nl==nr==0) if not packet else (1<=nl<=frames and 1<=nr<=frames)),'actual nonzero channel counts')
            data.extend(part);left+=nl;right+=nr
        take('CLOSE',dict(case=index,checked_rc=0,core=1))
        take('CASE',dict(case=index,id=c['id'],packets=14,pcm=c['total_pcm'],nz_l=left,nz_r=right,transitions_mask=15,core=1))
        pcms[c['id']]=bytes(data)
    take('COMPLETE',dict(cases=31,packets=434,pcm=738560,cases_mask=2147483647,core=1))
    need(cursor==len(events)==964,'all964 target events exactly once')
    return pcms


TARGET_PCM=replay(LOGS['qemu']+'\n'+bound('capture','qemu.stderr.log').decode('utf-8',errors='replace'))
need(len(T['observed_pcm'])==31 and T['observed']['protocol_lines']==964 and T['observed']['pcm']==738560 and
     T['observed']['decoded_packets']==434 and T['observed']['cases']==31,'recorded complete target observations')
pcm_aliases=set()
for index,(c,row) in enumerate(zip(CASES,T['observed_pcm'])):
    expected='observed-pcm/'+str(index).zfill(2)+'-'+c['id']+'.s16le';offsets=[0]
    for size in c['pcm']: offsets.append(offsets[-1]+size)
    need(norm(row['path'])==expected and row['case']==index and row['id']==c['id'] and row['bytes']==c['total_pcm'] and
         row['packet_offsets']==offsets and row['source_index']==c['source_index'],'captured complete per-case PCM rows')
    need(bound('capture',expected,row['sha256'],row['bytes'])==TARGET_PCM[c['id']],'saved PCM equals every actual event byte')
    pcm_aliases.add('capture/'+expected)
need({name for name in FILES if name.startswith('capture/observed-pcm/')}==pcm_aliases,'exact31 persisted PCM inventory')


def wav(data,rate,frames):
    with wave.open(io.BytesIO(data),'rb') as reader:
        need(reader.getcomptype()=='NONE' and reader.getnchannels()==2 and reader.getsampwidth()==2 and
             reader.getframerate()==rate and reader.getnframes()==frames,'complete stereo S16 reference WAV metadata')
        pcm=reader.readframes(frames+1)
    need(len(pcm)==frames*4,'full untrimmed reference WAV bytes')
    return pcm


def frames_md5(data,pcm,rate,frames):
    text=data.decode('utf-8').replace('\r\n','\n')
    need(re.search(r'^#tb 0: 1/'+str(rate)+'$',text,re.M) and re.search(r'^#sample_rate 0: '+str(rate)+'$',text,re.M) and
         '#codec_id 0: pcm_s16le' in text and re.search(r'^#channel_layout_name 0: (?:2 channels|stereo)$',text,re.M),
         'actual reference framemd5 metadata')
    lines=[line for line in text.splitlines() if line and not line.startswith('#')]
    need(frames[0]==0 and len(lines)==13,'all thirteen nonprimer reference packets')
    cursor=timestamp=0
    for line,count in zip(lines,frames[1:]):
        fields=[x.strip() for x in line.split(',')]
        need(len(fields)==6 and [int(x) for x in fields[:5]]==[0,timestamp,timestamp,count,count*4],'reference PTS/duration/bytes')
        part=pcm[cursor:cursor+count*4]
        need(hashlib.md5(part).hexdigest()==fields[5],'reference every-packet checksum')
        cursor+=count*4;timestamp+=count
    need(cursor==len(pcm),'reference packet boundaries cover complete PCM')


def reference_argv(ffmpeg,folder,decoder):
    return [ffmpeg,'-nostdin','-n','-hide_banner','-loglevel','error','-xerror','-err_detect','explode',
        '-c:a',decoder,'-i',folder+'/input.ogg','-map','0:a:0','-map_metadata','-1','-fflags','+bitexact',
        '-flags:a','+bitexact','-c:a','pcm_s16le','-f','wav',folder+'/'+decoder+'.wav',
        '-map','0:a:0','-map_metadata','-1','-flags:a','+bitexact','-c:a','pcm_s16le','-f','framemd5','-']


SCOPES={};REFS={};reference_children=reference_wavs=native_refusals=0
need(len(binding['source_scopes'])==3,'original17/new8/full12 separate scopes')
for scope in binding['source_scopes']:
    host_path=CHECKOUT+'/'+scope['host_path'];host_root=host_path.rsplit('/',1)[0]
    host=json.loads(artifact(host_path,scope['host_sha256']))
    qualified=json.loads(artifact(CHECKOUT+'/'+scope['qualification_path'],scope['qualification_sha256']))
    terminal=json.loads(artifact(CHECKOUT+'/'+scope['receipt_path'],scope['receipt_sha256']))
    count=12 if scope.get('name')=='new12' else scope['totals'][0]
    need(count in (17,8,12) and host['completed'] is True and host['xiph_reference_qualified'] is True and
         host['dual_reference_qualified'] is False and terminal['status']=='TERMINAL' and terminal['returncode']==1 and
         type(terminal['owned_pid']) is int and terminal['owned_pid']>0 and
         terminal['runner_sha256']==host['capture_sha256'] and len(host['cases'])==len(qualified['cases'])==count and
         len(host['commands'])==2*count,'actual historical separate reference NONPASS scopes')
    if scope.get('name')=='new12':
        need(qualified['completed'] is True and qualified['result']=='XIPH_EQUIVALENCE_QUALIFIED_DUAL_NONPASS' and
             qualified['xiph_reference_qualified'] is True and qualified['dual_reference_qualified'] is False and
             qualified['original_report_sha256']==scope['host_sha256'] and qualified['original_outer_returncode']==1 and
             (qualified['xiph_cases'],qualified['native_lookup2_refusals'],qualified['actual_child_commands_checked'],qualified['xiph_PCM_equal_pairs'])==(12,12,24,6),
             'retained complete full12 Xiph qualification')
    else:
        need(qualified['completed'] is True and qualified['reference_corpus_qualified'] is True and qualified['original_dual_reference_passed'] is False and
             qualified['original_report_sha256']==scope['host_sha256'] and qualified['original_outer_receipt_sha256']==scope['receipt_sha256'] and
             [qualified[k] for k in ('xiph_cases','native_compared','native_lookup2_refusals','paired_raw_packets','expected_pcm_bytes')]==scope['totals'],
             'retained complete old17/new8 Xiph qualification')
    for original,pin in host['inputs'].items():
        artifact(host_root+'/'+norm(pin['snapshot']),pin['sha256'],pin.get('bytes'))
    for original,pin in terminal['logs'].items(): artifact(original,pin['sha256'],pin['bytes'])
    commands={row['name']:row for row in host['commands']}
    need(len(commands)==2*count,'unique historical child names')
    ffmpeg=[name for name in host['tools'] if norm(name).rsplit('/',1)[-1]=='ffmpeg.exe']
    need(len(ffmpeg)==1,'one recorded reference executable');ffmpeg=ffmpeg[0]
    pcms={};native={};by_id={}
    for case in host['cases']:
        rid=case['id'];fields=case['input'];folder=host_root+'/cases/'+rid
        accepted=[x for x in qualified['cases'] if x['id']==rid]
        need(len(accepted)==1,'unique actual qualified reference case');accepted=accepted[0]
        need((accepted['xiph_reference_revalidated'] if scope.get('name')=='new12' else accepted['xiph_qualified']) is True,
             'actual accepted Xiph case')
        frames=fields.get('expected_packet_samples',fields.get('expected_packet_frames'))
        need(len(frames)==14 and frames[0]==0 and sum(frames)*4==fields['expected_s16le_bytes'],'reference frame model')
        matrix_parent=norm(case['source_matrix']).rsplit('/',1)[0]
        for kind in ('identification','setup','audio','ogg'):
            source=matrix_parent+'/'+fields[kind];pin=host['inputs'][next(x for x in host['inputs'] if norm(x).casefold()==source.casefold())]
            source_bytes=artifact(source,pin['sha256'],pin.get('bytes'))
            if kind=='ogg': need(source_bytes==artifact(folder+'/input.ogg',case['ogg_sha256']),'actual decoded carrier equals original raw-source carrier')
        for decoder in ('libvorbis','vorbis'):
            entry=commands['cases/'+rid+'/decode-'+decoder]
            receipt=json.loads(artifact(host_root+'/'+norm(entry['receipt']),entry['sha256']))
            code=0 if decoder in case['decoded'] else 3199971767
            need(receipt['status']=='TERMINAL' and type(receipt['returncode']) is int and receipt['returncode']==code and
                 type(receipt['owned_pid']) is int and receipt['owned_pid']>0 and not receipt.get('timed_out') and
                 not receipt.get('interrupted') and not receipt.get('error_type') and 'returncode_after_stop' not in receipt and
                 receipt['runner_sha256']==host['capture_sha256'] and receipt['executable_sha256']==host['tools'][ffmpeg] and
                 list(map(norm,receipt['argv']))==list(map(norm,reference_argv(ffmpeg,folder,decoder))) and receipt['timeout_seconds']==30,
                 'exact actual reference child terminal/argv/tool identity; no transforms')
            streams={}
            for stream in ('stdout','stderr'):
                name='decode-'+decoder+'.'+stream+'.log'
                pins=[pin for path,pin in receipt['logs'].items() if norm(path).rsplit('/',1)[-1]==name]
                need(len(pins)==1,'unique actual reference stream');pin=pins[0]
                streams[stream]=artifact(folder+'/'+name,pin['sha256'],pin['bytes'])
            need(len(receipt['logs'])==2,'both actual reference streams')
            reference_children+=1
            if code:
                need(decoder=='vorbis' and not streams['stdout'] and b'Codebook lookup type not supported.' in streams['stderr'],
                     'actual native lookup2 refusal, never replacement Xiph PCM')
                native_refusals+=1;continue
            need(not streams['stderr'],'strict accepted reference has no error')
            info=case['decoded'][decoder]
            pcm=wav(artifact(folder+'/'+decoder+'.wav',info['wav_sha256']),fields['rate'],sum(frames))
            frames_md5(streams['stdout'],pcm,fields['rate'],frames)
            need(sha(pcm)==info['pcm_sha256'] and len(pcm)==info['pcm_bytes']==fields['expected_s16le_bytes'] and
                 (info['rate'],info['channels'],info['bits'])==(fields['rate'],2,16) and info['frames']==frames[1:],
                 'actual WAV/PCM/frame metadata and byte binding')
            if decoder=='libvorbis':
                need(sha(pcm)==accepted['pcm_sha256'] and len(pcm)==accepted['pcm_bytes'],'qualified Xiph PCM binding')
                pcms[fields['id']]=pcm;by_id[rid]=(case,accepted,pcm);reference_wavs+=1
            else: native[fields['id']]=pcm
        REFS[(scope['qualification_sha256'],rid)]=by_id[rid]
    if scope.get('name')=='new12':
        for relation in scope['exact_equivalence_relations']:
            need(pcms[relation['original_id']]==pcms[relation['equivalent_id']] and
                 sha(pcms[relation['original_id']])==relation['historical_pcm_sha256'],'all six original full12 Xiph equality pairs')
    SCOPES[scope['qualification_sha256']]=dict(scope=scope,qualified=qualified,host=host,pcms=pcms,native=native)
need((reference_children,reference_wavs,native_refusals)==(74,37,30),'all actual old17/new8/full12 reference children and native refusals')


def samples(data):
    need(isinstance(data,bytes) and len(data)%4==0,'complete stereo signed16 bytes')
    return struct.unpack('<'+'h'*(len(data)//2),data)


def errors(a,b,histogram=False):
    need(len(a)==len(b),'full equal-length sample vectors')
    delta=[y-x for x,y in zip(a,b)];count=len(delta);square=sum(x*x for x in delta)
    first=next((i for i,value in enumerate(delta) if value),None)
    result=dict(samples=count,different_samples=sum(x!=0 for x in delta),
        min_signed_error=min(delta) if count else None,max_signed_error=max(delta) if count else None,
        max_abs_error=max(map(abs,delta)) if count else None,sum_signed_error=sum(delta),sum_squared_error=square,
        mean_signed_error=sum(delta)/count if count else None,rms_error=math.sqrt(square/count) if count else None,
        reference_sum_squares=sum(x*x for x in a),target_sum_squares=sum(x*x for x in b),
        reference_nonzero_samples=sum(x!=0 for x in a),target_nonzero_samples=sum(x!=0 for x in b),
        reference_clipped_samples=sum(x in (-32768,32767) for x in a),target_clipped_samples=sum(x in (-32768,32767) for x in b),
        first_mismatch=None if first is None else dict(sample=first,reference=a[first],target=b[first],signed_error=delta[first]))
    if histogram: result['signed_error_histogram']={str(k):value for k,value in sorted(Counter(delta).items())}
    return result


def comparison(reference,target,packet_bytes):
    need(len(reference)==len(target)==sum(packet_bytes) and len(packet_bytes)==14,'full exact14 packet PCM comparison')
    a,b=samples(reference),samples(target);whole=errors(a,b,True)
    if whole['first_mismatch']:
        item=whole['first_mismatch'];item.update(frame=item['sample']//2,channel=item['sample']%2)
    packets=[];cursor=0
    for index,size in enumerate(packet_bytes):
        first,stop=cursor//2,(cursor+size)//2;aa,bb=a[first:stop],b[first:stop]
        packets.append(dict(packet=index,byte_offset=cursor,bytes=size,frames=size//4,all_samples=errors(aa,bb),
            channels=[errors(aa[ch::2],bb[ch::2]) for ch in (0,1)]));cursor+=size
    return dict(byte_equal=reference==target,frames=len(reference)//4,unit='signed S16 integer LSB; error=target-reference',
        zero_lag_direct_LR=whole,channels=[errors(a[ch::2],b[ch::2]) for ch in (0,1)],packets=packets)


def transitions(c,pcm):
    result={key:[0,0] for key in ('SS','SL','LS','LL')};offsets=[0]
    for size in c['pcm']: offsets.append(offsets[-1]+size)
    for packet in range(1,14):
        key='SL'[c['modes'][packet-1]]+'SL'[c['modes'][packet]]
        for channel in (0,1):
            result[key][channel]+=sum(pcm[i:i+2]!=b'\0\0' for i in range(offsets[packet]+channel*2,offsets[packet+1],4))
    return result


XIPH_PCM={};CASE_RESULTS=[]
need(N['measurement_completed'] is True and N['actual_reference_compared'] is True and N['passed'] is False and
     N['retained_reference_outputs_reused'] is True and N['new_reference_processes_executed'] is False and len(N['cases'])==31 and
     all(N[key] is False for key in ('vendor_comparison_available','vendor_checked_pcm_equal','numeric_reference_qualified',
         'format_conformance_qualified','format_corpus_qualified','full_G6_qualified','physical_device','production_radio_integration')),
     'complete finite numerical measurement without full conformance')
for index,(c,source,original,numeric) in enumerate(zip(CASES,binding['cases'],mapping['cases'],N['cases'])):
    need(source['case']==original['case']==numeric['case']==index and source['id']==original['id']==numeric['id']==c['id'] and
         source['raw_sha256']==c['raw_sha256'] and original['fields_changed']==[],'all31 exact source order/raw identity')
    case,qualified,reference=REFS[(source['qualification_sha256'],source['original_reference_id'])]
    need(case['input']==original['original_case_fields']==original['selected_case_fields'] and
         sha(reference)==source['reference_pcm_sha256'] and sha(reference)==qualified['pcm_sha256'] and
         qualified['frames']==c['frames'][1:] and len(reference)==source['pcm_bytes']==c['total_pcm'],'selected Xiph raw/model/PCM binding')
    XIPH_PCM[c['id']]=reference;target=TARGET_PCM[c['id']]
    result=comparison(reference,target,c['pcm'])
    need(numeric['comparison']==result and numeric['target_transition_channel_nonzero']==transitions(c,target) and
         numeric['reference_transition_channel_nonzero']==transitions(c,reference),'independently recomputed every signed16 metric,channel,packet and transition')
    need(numeric['alignment']['diagnostic_only'] is True and numeric['alignment']['applied_shift_frames']==0 and
         numeric['alignment']['applied_channel_swap'] is False,'diagnostic alignment never changes acceptance')
    CASE_RESULTS.append(result)

DECLARED=[]
for group in ('books8','newbooks8'):
    originals=[row for row in mapping['cases'] if row['original_group']==group]
    need(len(originals)==8,'all original book group entries')
    pin=originals[0]['original_matrix'];matrix=json.loads(artifact(pin['path'],pin['sha256'],pin['bytes']))
    rows=[]
    for kind,field in (('equal','expected_same_decoder_pcm_equal_groups'),('different','expected_same_decoder_pcm_different_pairs')):
        rows += [dict(decoder='libvorbis',kind=kind,cases=ids,passed=True) for ids in matrix.get(field,[])]
    scope=SCOPES[binding['cases'][originals[0]['case']]['qualification_sha256']]
    need(len(rows)==4 and rows==scope['qualified']['xiph_metamorphic_checks'],'original four declared book relations')
    DECLARED+=rows
DECLARED += [dict(kind='equal',cases=[CASES[19+i]['id'],CASES[25+i]['id']]) for i in range(6)]


def relations(pcms):
    result=[]
    for row in DECLARED:
        ids=row['cases'];first=pcms[ids[0]];equal=all(pcms[name]==first for name in ids[1:])
        result.append(dict(kind=row['kind'],cases=ids,observed_byte_equal=equal,
            expected_relation_observed=equal if row['kind']=='equal' else not equal,
            comparisons=[dict(first=ids[0],second=name,**errors(samples(first),samples(pcms[name]))) for name in ids[1:]]))
    return result


META=dict(xiph=relations(XIPH_PCM),target=relations(TARGET_PCM))
need(all(len(rows)==14 for rows in META.values()) and META==N['metamorphic_relations'] and
     all(row['expected_relation_observed'] for row in META['xiph']),'independently recomputed14 relations per decoder')
numeric=all(row['zero_lag_direct_LR']['max_abs_error']<=2 for row in CASE_RESULTS)
nonzero=all(all(row[key]>0 for key in ('reference_nonzero_samples','target_nonzero_samples'))
            for result in CASE_RESULTS for row in result['channels'])
transition_ok=all(all(n>0 for pair in transitions(c,pcms[c['id']]).values() for n in pair)
                  for c in CASES for pcms in (XIPH_PCM,TARGET_PCM))
relation_ok=all(row['expected_relation_observed'] for rows in META.values() for row in rows)
qualified=numeric and nonzero and transition_ok and relation_ok
policy=N['policy']
need(policy==dict(purpose='bounded-corpus-regression-not-standard-conformance',scope='full_expanded31',max_abs_error=2,
    selected_before_target_measurement=True,threshold_fitted_to_output=False,
    alignment='Every original zero-lag L/R sample and packet; no trim, gain fit, shift, swap or resampling',
    max_abs_error_within_bound=numeric,both_channels_nonzero=nonzero,both_channels_nonzero_each_transition=transition_ok,
    all_fourteen_relations_per_decoder=relation_ok,required_cases=31) and N['bounded_corpus_pcm_qualified'] is qualified and
    N['result']==('BOUNDED_CORPUS_PCM_QUALIFIED' if qualified else 'BOUNDED_CORPUS_PCM_REJECTED'),
    'independent fixed2 policy result; measured NONPASS stays NONPASS')

NUMERIC_PINS={'compare_capture31.py':'b12acb4df3ee51bbf398044c5060387af9740d7e4c2df7296be56c425a9d0825',
    'test_current_bindings.py':'38d1d0b937a1996ab521263fb3e7e544ccefc9eaecc3e7ed59a8348034a94ead',
    'pcm_metrics.py':'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f',
    'policy25.py':'32ef721fa8a812684e83be296d7b74f90a12414644639f74ea353eef862d3dd6',
    'policy31.py':'da5553823f588e7a7d9adb82d53044a30c2de6eda696d9e8af1c6848a912e9c7',
    'reference31.py':'d136aa4d3fd0d7505195efa8de6f1fe0f6501ea4a874c6616e181311256e75d3'}
for name,digest in NUMERIC_PINS.items(): need(sha(raw('numeric-prep/'+name))==digest,'actual current numerical adapter/helper pin')
WRAPPER='33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e'
HOST_PYTHON='4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a'
need(sha(raw('canonical/.build/cyd-vorbis-format-command-01.py'))==WRAPPER,'actual owned outer wrapper source')


def resolve(value):
    value=norm(value)
    return posixpath.normpath(value if re.match(r'^[A-Za-z]:/',value) else CHECKOUT+'/'+value)


def argument(argv,flag):
    need(argv.count(flag)==1 and argv.index(flag)+1<len(argv),'unique argument '+flag)
    return argv[argv.index(flag)+1]


def receipt(alias,code,script):
    r=obj(alias)
    need(r['status']=='TERMINAL' and type(r['returncode']) is int and r['returncode']==code and
         type(r['owned_pid']) is int and r['owned_pid']>0 and r['runner_sha256']==WRAPPER and
         r['executable_sha256']==HOST_PYTHON and norm(r['cwd']).casefold()==CHECKOUT.casefold() and
         not r.get('timed_out') and not r.get('interrupted') and not r.get('error_type') and 'returncode_after_stop' not in r,
         'actual bounded owned outer terminal '+alias)
    entries=[i for i,value in enumerate(r['argv']) if resolve(value).casefold()==resolve(script).casefold()]
    need(len(entries)==1 and entries[0] in (3,4) and tuple(r['argv'][1:entries[0]]) in (('-B','-Xutf8'),('-B','-X','utf8')),
         'actual Python script/argv binding')
    need(type(r['timeout_seconds']) is int and 1<=r['timeout_seconds']<=1200 and len(r['logs'])==2,'bounded outer invocation')
    logs={}
    for original,pin in r['logs'].items():
        logs[norm(original).rsplit('/',1)[-1]]=artifact(original,pin['sha256'],pin['bytes'])
    return r,logs


capture_outer,_=receipt('commands/cyd02.json',0,GROUPS['prep']+'/run-cyd-vorbis-format-expanded31-qemu.py')
need(resolve(argument(capture_outer['argv'],'--output')).casefold()==origin('capture').casefold() and
     argument(capture_outer['argv'],'--contract-sha256')==PINS['contract.json'] and
     argument(capture_outer['argv'],'--data-sha256')==PINS['data.h'] and
     norm(argument(capture_outer['argv'],'--sdk-python')).endswith('/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe') and
     norm(argument(capture_outer['argv'],'--rom'))=='C:/Work/QEMU-ESP32/pc-bios','correct actual SDK Python and explicit ROM path')
need(N['target_process_evidence']==dict(report_sha256=sha(raw('capture/report.json')),outer_returncode=0,
    owned_pid=capture_outer['owned_pid'],outer_receipt_sha256=sha(raw('commands/cyd02.json')),new_reference_processes_executed=False) and
    norm(N['inputs']['target/report']['path']).casefold()==origin('capture','report.json').casefold() and
    N['inputs']['target/report']['sha256']==sha(raw('capture/report.json')) and
    N['current_capture_evidence']==dict(source_sha256=CURRENT,renderer='on',link_recipe=link,
        recipe_observation_only=True,independently_observed_linker_execution=False),
    'numerical report binds this exact current capture/source/recipe/outer receipt')
numerical_outer,numeric_logs=receipt('commands/numeric.json',0 if qualified else 1,GROUPS['numeric-prep']+'/compare_capture31.py')
need(resolve(argument(numerical_outer['argv'],'--target')).casefold()==origin('capture').casefold() and
     resolve(argument(numerical_outer['argv'],'--target-terminal')).casefold()==(origin('commands','cyd02.json')).casefold() and
     resolve(argument(numerical_outer['argv'],'--output')).casefold()==origin('numeric').casefold() and
     argument(numerical_outer['argv'],'--target-report-sha256')==sha(raw('capture/report.json')) and
     argument(numerical_outer['argv'],'--max-abs-error')=='2' and not numeric_logs['numeric.stderr.log'],
     'actual complete numerical invocation and expected pass/nonpass terminal')
history_outer,_=receipt('commands/cyd.json',1,GROUPS['prep']+'/run-cyd-vorbis-format-expanded31-qemu.py')
need(resolve(argument(history_outer['argv'],'--output')).casefold()==origin('history01').casefold() and
     norm(argument(history_outer['argv'],'--sdk-python'))=='C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' and
     H['completed'] is False and H['passed'] is False and H['target_capture_completed'] is False and H['result']=='NONPASS' and
     tuple(c['name'] for c in H['commands'])==('sdk-head','sdk-clean','build') and H['commands'][-1]['exit_status']==1 and
     all(row.get('missing') for row in H['sdk_build_logs'].values()) and
     b'ESP-IDF Python virtual environment' in raw('history01/build.stderr.log') and b'not found' in raw('history01/build.stderr.log'),
     'initial wrong-SDK-Python export failure, no compiler/QEMU capture')
for name in ('sdk-head','sdk-clean'):
    c=next(x for x in H['commands'] if x['name']==name)
    need(c['state']=='complete' and c['exit_status']==0,'initial SDK identity observations completed')

host=obj('host/report.json')
receipt('commands/preparation-host.json',0,GROUPS['prep']+'/check-preparation.py')
need(host['passed'] is True and host['tests_run']==8 and len(host['commands'])==8 and host['inputs_unchanged'] is True and
     host['inputs']==host['inputs_after'] and host['configure_only'] is True and
     all(host[key] is False for key in ('compiler_invoked','SDK_invoked','QEMU_invoked','reference_invoked','prepared_Python_imported')),
     'actual eight bounded CMake-P/AST checks')
expected_host={'early-undefined','component-current','wrong-sdk','repair-disabled','wrong-setup','wrong-output','wrong-abi','wrong-floor'}
need({c['name'] for c in host['commands']}==expected_host,'all eight intended phase/pin cases')
for c in host['commands']:
    need(c['passed'] is True and c['child_reaped'] is True and c['timed_out'] is False and
         c['exit_status']==(1 if c['expected_error'] else 0) and type(c['pid']) is int and c['pid']>0,'actual CMake child result/reap')
    directory='host/'+c['name']
    need(sha(raw(directory+'/case.cmake'))==c['script']['sha256'],'exact actual CMake script')
    for stream in ('stdout','stderr'):
        need(sha(raw(directory+'/'+stream+'.log'))==c[stream]['sha256'],'actual CMake child stream')
    if c['expected_error']:
        need(c['expected_error'] in (raw(directory+'/stdout.log')+raw(directory+'/stderr.log')).decode('utf-8'),'exact intended phase/pin refusal')
    need(sha(raw(directory+'/variant/compat/vorbis_repair/enable.cmake'))==PINS['target/cyd_vorbis_format_expanded31_qemu/raw-enable.cmake'],
         'every actual host case used exact frozen helper')
for original,pin in host['inputs'].items():
    if norm(original).casefold() in ORIGINS: artifact(original,pin['sha256'],pin['bytes'])
    else: need(norm(original).endswith('/python.exe') or norm(original).endswith('/cmake.exe'),'only historical host tool identities lack body')
link_host,link_logs=receipt('commands/link-host.json',0,'.build/test-vorbis-format31-current-link-01.py')
need(b'Ran 8 tests in ' in link_logs['link-host.stderr.log'] and
     link_logs['link-host.stderr.log'].replace(b'\r\n',b'\n').endswith(b'\nOK\n') and
     PINS['link_recipe.py'].encode() in raw('canonical/.build/test-vorbis-format31-current-link-01.py'),
     'actual eight synthetic recipe tests with exact reviewed subject')
_,binding_logs=receipt('numeric-prep/host-bindings.json',0,GROUPS['numeric-prep']+'/test_current_bindings.py')
need(b'Ran 9 tests in ' in binding_logs['host-bindings.stderr.log'] and
     binding_logs['host-bindings.stderr.log'].replace(b'\r\n',b'\n').endswith(b'\nOK\n'),'actual nine numerical binding checks')
before=obj('numeric-prep/host-bindings.sources-before.json');after=obj('numeric-prep/host-bindings.sources-after.json')
binding_result=obj('numeric-prep/host-binding-result.json')
need(before==after==binding_result['sources'] and binding_result['tests_run']==9 and binding_result['returncode']==0 and
     binding_result['sources_unchanged'] is True and binding_result['complete31_measurement_executed'] is False and
     binding_result['reference_or_target_process_executed'] is False,'honest focused host result/source stability')
for row in before: need(sha(raw('numeric-prep/'+row['path']))==row['sha256'],'actual numerical host source pins')

PARITY=obj('commands/old-pcm-parity.json')
receipt('commands/parity.json',0,'.build/compare-vorbis-format31-current-old-01.py')
need(PARITY['comparison_completed'] is True and PARITY['inputs_unchanged'] is True and
     (PARITY['total_cases'],PARITY['total_packets'],PARITY['total_pcm_bytes'])==(31,434,738560) and
     PARITY['new_decoder_or_reference_execution'] is False and PARITY['numerical_qualification'] is False and
     set(M['parity_inputs'])==set(PARITY['selected_inputs']),'complete historical/current selected PCM parity scope')
for original,pin in PARITY['selected_inputs'].items():
    row=M['parity_inputs'][original]
    need(row['sha256']==pin['sha256'] and row['bytes']==pin['bytes'] and row['alias'] in FILES,'every selected parity body saved')
    artifact(original,pin['sha256'],pin['bytes'])
old_root=CHECKOUT+'/.build/cyd-vorbis-format-expanded31-capture-01'
old=json.loads(artifact(old_root+'/report.json','6f7f346df8c2185776fa8727977e363c284f8bdc459ef90c5ed28affc3b6d81d'))
need(old['completed'] is True and old['target_capture_completed'] is True and len(old['observed_pcm'])==31,'retained old complete capture report')
parity_rows=[]
for index,(c,pin,current_pin) in enumerate(zip(CASES,old['observed_pcm'],T['observed_pcm'])):
    need(pin['case']==index and pin['id']==c['id'] and pin['bytes']==current_pin['bytes'] and
         pin['packet_offsets']==current_pin['packet_offsets'],'old/current exact case and packet boundaries')
    old_pcm=artifact(old_root+'/'+norm(pin['path']),pin['sha256'],pin['bytes']);current=TARGET_PCM[c['id']]
    offsets=pin['packet_offsets']
    parity_rows.append(dict(case=index,id=c['id'],bytes=len(old_pcm),old_sha256=sha(old_pcm),current_sha256=sha(current),
        byte_equal=old_pcm==current,packet_equal=[old_pcm[a:b]==current[a:b] for a,b in zip(offsets,offsets[1:])]))
need(parity_rows==PARITY['cases'] and PARITY['byte_equal_cases']==sum(row['byte_equal'] for row in parity_rows) and
     PARITY['all_31_byte_equal'] is all(row['byte_equal'] for row in parity_rows),'independent every old/current byte and434 packet vectors')
for name in ('docs/CYD_VORBIS_TRANSFER_DESIGN.md','docs/ESP32_CYD_C3_TRANSFER_PLAN.md','docs/CYD_VORBIS_FLOOR0_REMAINING.md',
             'idf/esp32-cyd2usb-native/main/vorbis_repair/README.md'):
    need(bool(raw('canonical/'+name)),'nonempty publication-time documentation')

print(json.dumps(dict(evidence_integrity_verified=True,cases=31,raw_packets=434,pcm_bytes=738560,
    independent_signed16_and_packet_metrics_verified=True,relations_per_decoder=14,
    actual_reference_children_checked=reference_children,qualified_Xiph_WAVs_checked=reference_wavs,
    historical_native_lookup2_refusals=native_refusals,bounded_corpus_pcm_qualified=qualified,
    numerical_result=N['result'],predeclared_max_abs_error=2,
    case_max_abs_error={c['id']:result['zero_lag_direct_LR']['max_abs_error'] for c,result in zip(CASES,CASE_RESULTS)},
    old_current_byte_equal_cases=PARITY['byte_equal_cases'],full_G6_qualified=False,format_conformance_qualified=False,
    production_radio_integration=False,physical_device=False)))
