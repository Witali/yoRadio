"""Data-only replay of already-completed native runs; no Fraction/MPFR/child runs."""
import argparse,hashlib,io,json,re,stat,struct,sys,zipfile
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'tests/results/vorbis-bigfloat-native-20261028'
ARCHIVE_SHA='e607c44ccb08db5e5378b55a416f4adcf1ad41addde586040b0b5256cf2260e9'
MANIFEST_SHA='705d37bf3762b836f3521b7819f66e35343c82d1a39402e8e26c2a8ea998dea5'
CONTROLLER_SHA='2bf2dddc4997b0555d33c97fdaa41cb76a1bdd572357ae9e2fdfe804b240afb8'
FIXTURE_SHA='a07ae74869e64a4a008a5dd420bec305479fde6b8e420b721b6f973320809c79'
HOST32_SHA='b2fed430a10930dd928a440615ad2dc44018ae3de95a3a353d62d51fe65177c9'
LIVE_PREFIX='C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/'
GROUPS=['vorbis-bigfloat-protocol-esp32-20261028-01']+[f'vorbis-bigfloat-{t}-20261028-{i:02d}' for t in ('esp32','c3') for i in (1,2,3)]
REPORTS=['e7c52db69cb1cd5c940842b072896e04ae0f4923eb77c829ae393aa8d88da300',
 '5e23ec96efbaace88261654d954ff9ed2dab40a5d288d9577d59c7e64465b656',
 '747dc001ec41e86a2825b6d6f6b071e6ad0c7ce2da404989dddc78758aa80219',
 'a4873851e0ca0d1f9f82d67ab6604e1a45e0bf68aaabe1c844975354fbc00b60',
 'bc06d076cf343527fd41860792394623d97cf1baa2d41b73a141607e89184312',
 '8ca8f4d761afc9bf11f2829d18a0f123a5a67f597c690e7e968cbd229d3cf9f7',
 '3c9d9a19bfb0d68f4aeb0e291161dd2c38adfd81851ff2bacd12f0c5fdcfea0d']

def need(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def norm(s):return s.replace('\\','/')
def canonical(s):
    return isinstance(s,str) and bool(s) and s.isascii() and ':' not in s and '\\' not in s and not any(ord(c)<32 or ord(c)==127 for c in s) and not PurePosixPath(s).is_absolute() and '..' not in PurePosixPath(s).parts and PurePosixPath(s).as_posix()==s

def inventory():
    ab=(FOLDER/'captures.zip').read_bytes();mb=(FOLDER/'manifest.json').read_bytes()
    need(len(ab)==7978161 and sha(ab)==ARCHIVE_SHA and sha(mb)==MANIFEST_SHA,'sealed archive/manifest identity')
    m=json.loads(mb);need(m['schema']=='vorbis-bigfloat-native-evidence-v1','native manifest schema')
    need((m['physical_members'],m['physical_bytes'],m['logical_members'],m['logical_bytes'],m['omitted_members'],m['omitted_bytes'])==(206,84711921,532,113484670,3424,294056278),'explicit physical/logical/omitted totals')
    pins={x['path']:x for x in m['files']};need(len(pins)==len(m['files'])==206,'unique physical inventory');physical={}
    with zipfile.ZipFile(io.BytesIO(ab)) as z:
        need(len(z.infolist())==206 and len(set(z.namelist()))==206 and set(z.namelist())==set(pins),'exact ZIP member set')
        for info in z.infolist():
            need(canonical(info.filename) and not info.is_dir() and not info.flag_bits&1 and stat.S_IFMT(info.external_attr>>16) in (0,stat.S_IFREG),'canonical regular ZIP member')
            b=z.read(info);p=pins[info.filename];need(len(b)==p['bytes'] and sha(b)==p['sha256'] and info.filename=='blobs/'+p['sha256'],'every physical byte and content-addressed name');physical[info.filename]=b
    logical={}
    for row in m['logical_files']:
        need(canonical(row['path']) and row['path'] not in logical and row['blob']=='blobs/'+row['sha256'] and row['blob'] in physical,'canonical unique alias')
        b=physical[row['blob']];need((len(b),sha(b))==(row['bytes'],row['sha256']),'complete alias byte identity');logical[row['path']]=b
    omitted={}
    for row in m['omitted']:
        need(canonical(row['path']) and '/build/' in row['path'] and row['path'] not in logical and row['path'] not in omitted and re.fullmatch('[0-9a-f]{64}',row['sha256']) and type(row['bytes']) is int and row['bytes']>=0,'explicit derived omission')
        omitted[row['path']]=row
    need(len(logical)==532 and sum(map(len,logical.values()))==113484670 and len(omitted)==3424 and sum(x['bytes'] for x in omitted.values())==294056278,'all logical and omitted byte extents')
    need([x['name'] for x in m['groups']]==GROUPS,'all seven attempt/protocol groups')
    for index,g in enumerate(GROUPS):need(sha(logical[g+'/report.json'])==REPORTS[index]==m['groups'][index]['report_sha256'],'exact historical/final report')
    return logical,omitted

def projection(body):
    """Compare actual exact words, not just their hashes; drop allocator ABI fields."""
    output=[];primary=refused=0
    for line in body.decode('ascii').splitlines():
        p=line.split(' ')
        if p[0]=='BFBEGIN':need(p==['BFBEGIN','1','32','701'],'complete32-bit corpus');q=p
        elif p[0]=='BFROW':need(len(p)==12 and int(p[1])==primary,'ordered complete primary');primary+=1;q=p[:8]
        elif p[0]=='BFOOM':need(len(p)==17,'complete refusal record');refused+=1;q=p[:3]+p[4:14]
        elif p[0]=='BFGUARD':need(p==['BFGUARD','18'],'all guard controls');q=p
        elif p[0]=='BFEND':need(len(p)==10 and p[1:7]==['701','825','3606','1643','1253','12587858'] and p[8:]==['0','0'],'full cleanup/counters');q=p[:7]+p[8:]
        else:raise ValueError('foreign mathematical record')
        output.append(' '.join(q))
    need(primary==701 and refused==825 and output[-1].startswith('BFEND '),'complete actual primary/recovery set')
    return ('\n'.join(output)+'\n').encode()

def metadata(line,tag,fixed):
    p=line.split(' ');need(p[0]==tag and all(x.count('=')==1 for x in p[1:]),'metadata syntax');r=dict(x.split('=') for x in p[1:]);need(len(r)==len(p)-1 and all(r.get(k)==str(v) for k,v in fixed.items()),'native metadata identity');return r

def final(members,omitted,group,target):
    r=json.loads(members[group+'/report.json']);machine=94 if target=='esp32' else 243;core=1 if target=='esp32' else 0
    need(r['completed'] and r['passed'] and r['numerical_qualified'] and r['target_executed'] and r['target']==target and not r['physical_device'] and not r['production_firmware'] and not r['production_selected'] and not r['transcendental_gain_certified'],'actual unselected native scope')
    need([x['name'] for x in r['commands']]==['sdk-head','sdk-clean','build','symbols','size','merge','qemu'],'seven native commands')
    for command in r['commands']:
        need(command['state']=='complete' and command['exit_status']==0 and command['pid']>0,'actual process terminal0')
        for stream in ('stdout','stderr'):need(sha(members[group+'/'+command['name']+'.'+stream+'.log'])==command[stream+'_sha256'],'every exact process log')
    child=json.loads(members[group+'/sdk-child.json'].decode('utf-8-sig'));need(child==r['sdk_child'] and child['exit_status']==0 and child['pid']>0,'actual SDK child receipt')
    need(r['fixture_sha256']==FIXTURE_SHA and r['host32_capture_sha256']==HOST32_SHA,'frozen original fixture/reference')
    need(sha(members[group+'/project/main/vorbis_bigfloat_host.c'])==FIXTURE_SHA and
         members[group+'/project/main/vorbis_bigfloat_host.c']==members[group+'/sources/native/vorbis_bigfloat_host.c'],
         'actual included fixture is the unchanged original')
    need(sha(members[group+'/input.txt'])==r['input_sha256'] and sha(members[group+'/cases.json'])==r['cases_sha256'] and
         len(json.loads(members[group+'/cases.json']))==701 and sha(members[group+'/corpus.h'])==r['corpus_header_sha256'] and
         members[group+'/corpus.h']==members[group+'/project/main/corpus.h'],'complete actual frozen corpus and flash-resident input header')
    for source,pin in r['inputs'].items():
        body=members[group+'/'+pin['snapshot']];need((len(body),sha(body))==(pin['bytes'],pin['sha256']),'every executed source snapshot')
        relative=norm(source);need(relative.startswith(LIVE_PREFIX),'known source path mapper');relative=relative[len(LIVE_PREFIX):];need(canonical(relative),'contained source mapping')
        if not relative.endswith('.md'):need((ROOT/relative).read_bytes()==body,'exact final live executable/build/header/patch/manifest: '+relative)
    need(sha(members[group+'/sources/controller.py'])==CONTROLLER_SHA,'executed final controller identity')
    for name,pin in r['build_outputs'].items():
        full=group+'/'+name
        if full in members:need(sha(members[full])==pin,'retained SDK/image/config/object identity')
        else:need(full in omitted and omitted[full]['sha256']==pin,'explicit SDK-derived omission identity')
    need(len(r['compile_rows'])==4 and len(r['stack_records'])==4,'all foundation/fixture native objects')
    for row in r['compile_rows']:
        c=row['command'];name=norm(row['file']).rsplit('/',1)[-1]
        need(all(x in c for x in ('-UNDEBUG','-fstack-usage','-fno-fast-math','-ffp-contract=off')),'actual arithmetic flags')
        if name in ('libbf.c','cutils.c'):need(all(x in c for x in ('-Wsign-compare','-Wunused-parameter','-Wno-error=sign-compare','-Wno-error=unused-parameter')) and ('-Wno-error=format' in c)==(name=='libbf.c'),'narrow creator warning policy')
        else:need('-Werror' in c and '-Wno-error=format' not in c and '-Wno-error=sign-compare' not in c,'strict owned warning policy')
        output=norm(row['output']);prefix=LIVE_PREFIX+'.build/'+group+'/build/'
        if output.startswith(prefix):output=output[len(prefix):]
        need(canonical(output),'contained object path');body=members[group+'/build/'+output]
        need(body[:9]==b'\x7fELF\x01\x01\x01\0\0' and struct.unpack_from('<HH',body,16)==(1,machine) and struct.unpack_from('<I',body,36)[0]==(768 if core else 1),'actual ELF32 object machine/ABI')
    for name,lines in r['stack_records'].items():need(members[group+'/'+name].decode().splitlines()==lines,'all selected compiler stack reports')
    elf=members[group+'/build/vorbis_bigfloat_qemu.elf'];need(elf[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<HH',elf,16)==(2,machine),'actual executable ELF32 machine')
    need(len(members[group+'/qemu-flash.bin'])==4194304,'complete actual merged flash image')
    config=members[group+'/sdkconfig'].decode().replace('\r\n','\n')
    for setting in ['CONFIG_ESP_TASK_WDT_EN=y','CONFIG_ESP_TASK_WDT_INIT=y','CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0=y']+(['CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=y'] if core else []):need(re.search('^'+re.escape(setting)+'$',config,re.M),'watchdog and IDLE enabled')
    need(bool(re.search('^CONFIG_FREERTOS_UNICORE=y$',config,re.M))==(not core),'actual target core configuration')
    symbols=members[group+'/symbols.stdout.log'].decode().replace('\r\n','\n')
    for symbol in r['required_symbols']:need(re.search(r'\b'+symbol+r'(?:\.[A-Za-z0-9_.]+)?$',symbols,re.M),'linked exercised symbol')
    need(not re.search(r['excluded_symbol_pattern'],symbols,re.M) and r['section_gc_verified'],'excluded formatter/transcendental symbols absent')
    linkmap=members[group+'/build/vorbis_bigfloat_qemu.map'].decode(errors='replace').split('Memory Configuration',1)[0]
    need('Discarded input sections' in linkmap and all('.text.'+n in linkmap for n in ('bf_print_str','bfdec_print_str','bf_cos','bf_get_float64')) and b'--gc-sections' in members[group+'/build/build.ninja'],'actual discarded helper sections')
    log=members[group+'/qemu.stdout.log'].decode().replace('\r\n','\n');need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|stack overflow',log,re.I),'no native panic')
    events=[x for x in log.splitlines() if x.startswith('BF')]
    metadata(events[0],'BFQ_BEGIN',dict(target=target,cases=701,data=r['input_sha256'],fixture=FIXTURE_SHA,coordinator=0,worker=core))
    for line,tag,flushes in [(events[1],'BFQ_WORKER',0),(events[-2],'BFQ_COMPLETE',1527)]:
        record=metadata(line,tag,dict(status=0,core=core,priority=3,stack=16384,flushes=flushes,idle0=0,idle1=0 if core else -1,heap_integrity=1))
        need(0<int(record['stack_free'])<=16384 and 0<int(record['heap_min'])<=int(record['heap_free']),'observed stack/heap fields')
    metadata(events[-1],'BFQ_STOP',dict(status='CAPTURED'))
    capture=members[group+'/capture.txt'];need(capture==('\n'.join(events[2:-2])+'\n').encode(),'every actual BF record retained')
    host=members[group+'/host32-reference.txt'];need(sha(host)==HOST32_SHA,'actual qualified host32 reference bytes')
    actual,reference=projection(capture),projection(host);need(actual==reference,'every exact primary/refusal/recovery dyadic/floor equals actual host32, not a digest-only substitution')
    measured=json.loads(members[group+'/measurement.json']);need(sha(members[group+'/measurement.json'])==r['measurement_sha256'] and measured['primary_host32_equal']==701 and measured['recovery_host32_equal']==825 and measured['passed'],'recorded independent Fraction/full host32 qualification')
    need(r['arithmetic']['cases']==701 and r['arithmetic']['allocation_refusals']==825 and r['arithmetic']['ntt_rows']==[681,684] and r['protocol_controls']['malformed_refused']==10 and len(r['corruption_controls'])==10 and all(x['rejected'] for x in r['corruption_controls']),'complete retained controls and actual NTT paths')
    return dict(target=target,cases=701,allocation_refusals=825,exact_records_equal=True,mathematical_projection_sha256=sha(actual),capture_sha256=sha(capture),own_objects=4,reported_build_outputs=len(r['build_outputs']),all_commands_terminal=True,initial=measured['initial'],terminal=measured['terminal'],peak_allocator_bytes=r['arithmetic']['peak_allocator_bytes'])

def verify():
    members,omitted=inventory();need(sha((ROOT/'tests/test-vorbis-bigfloat-qemu.py').read_bytes())==CONTROLLER_SHA,'live controller frozen')
    protocol=json.loads(members[GROUPS[0]+'/report.json']);need(protocol['protocol_only'] and protocol['completed'] and
        protocol['passed'] and not protocol['target_executed'] and not protocol['commands'] and
        protocol['protocol_controls']['synthetic_protocol_only'] and protocol['protocol_controls']['malformed_refused']==10,
        'synthetic protocol group remains distinct from actual native runs')
    histories=[]
    for target in ('esp32','c3'):
        for attempt in (1,2):
            g=f'vorbis-bigfloat-{target}-20261028-{attempt:02d}';r=json.loads(members[g+'/report.json']);need(not r['passed'] and not r['target_executed'] and [x['name'] for x in r['commands']]==['sdk-head','sdk-clean','build'],'all failed attempts preserved without native execution')
            need(all(x['state']=='complete' and x['exit_status']==(1 if x['name']=='build' else 0) and x['pid']>0 for x in r['commands']),'terminal failed-build process facts')
            for command in r['commands']:
                for stream in ('stdout','stderr'):need(sha(members[g+'/'+command['name']+'.'+stream+'.log'])==command[stream+'_sha256'],'historical process log identity')
            if attempt==1:need(b'WinError 623' in members[g+'/build.stderr.log'] and g+'/sdk-child.json' not in members,'SDK activation infrastructure failure before compiler child')
            else:
                child=json.loads(members[g+'/sdk-child.json'].decode('utf-8-sig'));text=members[g+'/sdk-build.stdout.log'].decode(errors='replace');need(child['exit_status']==2 and child['pid']>0 and len([l for l in text.splitlines() if 'error:' in l])==13 and '[-Werror=format=]' in text,'actual13format diagnostics retained before QEMU')
            histories.append(dict(target=target,attempt=attempt,reason='SDK activation WinError623' if attempt==1 else '13 creator format errors under SDK-Werror'))
    a=final(members,omitted,'vorbis-bigfloat-esp32-20261028-03','esp32');b=final(members,omitted,'vorbis-bigfloat-c3-20261028-03','esp32c3')
    need(a['mathematical_projection_sha256']==b['mathematical_projection_sha256'],'cross-ISA exact result identity after direct per-record comparisons')
    return dict(passed=True,archive_sha256=ARCHIVE_SHA,manifest_sha256=MANIFEST_SHA,physical_members=206,logical_members=532,derived_omissions=3424,histories=histories,native=[a,b],controller_sha256=CONTROLLER_SHA,verifier_sha256=sha(Path(__file__).read_bytes()),commands_reexecuted=0,Fraction_or_MPFR_reexecuted=False,archived_code_executed=False,archives_extracted=False,custom_gain_work_deferred=True,production_selected=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=FOLDER/'replay.json');a=p.parse_args();out=a.output.resolve();need(out.is_relative_to(ROOT) and not out.exists(),'fresh replay output')
    try:r=verify()
    except BaseException as e:r=dict(passed=False,error_type=type(e).__name__,error=str(e),commands_reexecuted=0,verifier_sha256=sha(Path(__file__).read_bytes()))
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(r),flush=True);return 0 if r['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
