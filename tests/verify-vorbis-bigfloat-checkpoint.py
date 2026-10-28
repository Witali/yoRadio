"""Replay sealed host arithmetic data; never execute archived code or children."""
import argparse,ast,hashlib,importlib.util,json,re
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
FOLDER='tests/results/vorbis-bigfloat-20261028'
ARCHIVE_SHA='f15f8ccdac3fed71bb5a51b037698c8e2bf083e7adaf64a54c6c02cf849d8f90'
MANIFEST_SHA='f9c9969b58f54e6c617b092f2bedd52c78d34ee307eeac5e47560071ea0ed1a7'
PINS={
    'test-vorbis-bigfloat.py':'ea384976d4556ae95604b27a0072a732ae53e9558558f868730b3826bf12d7d7',
    'vorbis_synthesis_checkpoint.py':'dfff6c46c56bf0cbf95a2385ca3584314b720088bd11124247e20605d8712ed5',
    'test-vorbis-floor1-render.py':'df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2'}
FIXTURE_SHA='a07ae74869e64a4a008a5dd420bec305479fde6b8e420b721b6f973320809c79'
LIVE_COMPONENT={
    'bigfloat.c':'dc848de646f25ff5a8a4997cd422718e23ace867502b19e6062ca22887a4d93a',
    'CMakeLists.txt':'bf8ae76a80cd883e2b7c879d158c71c1bc130d704da320342e0118849dfc1bc3',
    'include/native_vorbis_bigfloat.h':'379726cc07f1fcbb2ecc1512c08ea077085fea12828cd96afd9fa0cca61013c1',
    'portability.patch':'cd15a88f0718bb2f18e2b8b269a57983315ef28617b2e836b3bba07391389a42',
    'portable/libbf.c':'158da48780e54571ae2ce56ef7049f9829f62817c005009c9018bdf74d92a378',
    'upstream/cutils.c':'a1ec96510f657c9f585d42083c527b25cbccd480a28d31c6fa2d25f705ccaeeb',
    'upstream/cutils.h':'92084de8f384cdd746f9fc86d8378acd178dc726cb79fbed3dbd3c642aa475a2',
    'upstream/libbf.c':'8abc36c9feaeaeb04729e3494c6b693611a518442d11c6546c86bc08b30a1228',
    'upstream/libbf.h':'6376f2965cef49ad9e1351ff99e3dce4c6e9961d9e59e75de45aad63a1724c8a',
    'upstream/list.h':'484a604d8996a9c23c23d453ec5017af05b2c74de4bb34da8abcd5f5b5880f3e',
    'upstream/readme.txt':'e5e5919ae21c0878c2b58508005a9c4c9acf182e00f14eadb99e55ac1d7f2019',
    'upstream-manifest.json':'edc6d65b51c205bfcc3c2fe1e58f0b012d265cb00337667417688baf0f097a77'}
HOSTS={'host01':(False,1),'host02':(False,2),'host03':(False,7),'host04':(True,13),'host05':(True,13)}
OMITTED={
    'host03/limb64':(1348488,'9b5c5050912fa7819d5dbef6d34adb2b7efc2360c8f98b26a51fdc3f8c3b3cbd'),
    'host04/limb32':(1366920,'d3273fb5c258f42e56faf88894cfd61cb0eb69b1156d40130e1ff6df84b2e69d'),
    'host04/limb64':(1348840,'83d254c63a50d8e0796a3182d8d62de700a859cb13397d7b0d97d31343d98fad'),
    'host05/limb32':(1366920,'86a1cfe0bd68610ea206165cd46fa1fe9a6356f2de7a5311cb81f10cb8a63b15'),
    'host05/limb64':(1348840,'685165eef06d8cb0a818b7096238d0e4cbb8240906ae375f0a96d99b64681b2b')}

def need(test,message):
    if not test:raise ValueError(message)
def sha(body):return hashlib.sha256(body).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def aliases(physical,manifest):
    need(manifest['storage']=='sha256-member-aliases-v1','explicit content-addressed storage');out={};used=set()
    for row in manifest['logical_files']:
        name=row['path'];path=PurePosixPath(name);digest=row['sha256'];blob=row['blob']
        need(path.parts and not path.is_absolute() and path.as_posix()==name and '..' not in path.parts and ':' not in name and '\\' not in name and name not in out and
            re.fullmatch('[0-9a-f]{64}',digest) and blob=='blobs/'+digest and blob in physical,'canonical unique logical byte alias')
        body=physical[blob];need(len(body)==row['bytes'] and sha(body)==digest,'exact logical alias size/hash');out[name]=body;used.add(blob)
    need(set(physical)==used,'no unreferenced physical blobs');return out

def verify():
    # Hash all executable local helpers and selected source before any import.
    folder=ROOT/FOLDER;need(sha((folder/'captures.zip').read_bytes())==ARCHIVE_SHA and sha((folder/'manifest.json').read_bytes())==MANIFEST_SHA,'pinned host archive/manifest before import')
    for name,pin in PINS.items():need(sha((ROOT/'tests'/name).read_bytes())==pin,'pinned live trusted reader: '+name)
    need(sha((ROOT/'tests/native/vorbis_bigfloat_host.c').read_bytes())==FIXTURE_SHA,'pinned live portable fixture')
    for name,pin in LIVE_COMPONENT.items():need(sha((ROOT/'idf/components/native_vorbis_bigfloat'/name).read_bytes())==pin,'pinned live selected source: '+name)
    helper=load(ROOT/'tests/vorbis_synthesis_checkpoint.py','bigfloat_checkpoint_helper');reader=load(ROOT/'tests/test-vorbis-bigfloat.py','bigfloat_checkpoint_reader')
    physical=helper.archive_members(FOLDER,ARCHIVE_SHA,MANIFEST_SHA);manifest=json.loads((folder/'manifest.json').read_bytes());members=aliases(physical,manifest)
    need(len(physical)==147 and sum(map(len,physical.values()))==26992059 and len(members)==274 and sum(map(len,members.values()))==30430683,'exact physical/logical inventory')
    need({name.split('/')[0] for name in members}==set(HOSTS)|{'context-stock-type','tools','receipts'},'complete attempt/context/tool/seal groups')
    omitted={row['path']:row for row in manifest['omitted']};need(len(omitted)==len(manifest['omitted']) and set(omitted)==set(OMITTED),'only five declared rebuildable executables omitted')
    for name,(count,digest) in OMITTED.items():need(name not in members and omitted[name]['bytes']==count and omitted[name]['sha256']==digest,'exact executable omission receipt')
    rows=reader.corpus(8192);need(len(rows)==701 and rows[-2]['id']==699 and rows[-1]['id']==700,'all699 original rows plus two appended carry regressions')
    need(reader.expected(rows[-2])['floor']==(1<<1572)-1 and reader.expected(rows[-1])['floor']==-(1<<1572),'specific all-ones positive floor versus negative carry')
    origin=(ROOT/'tests/test-vorbis-floor1-render.py').read_bytes();templates=[ast.literal_eval(n.value) for n in ast.parse(origin).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUPERVISOR' for t in n.targets)]
    need(len(templates)==1 and templates[0].count('assert 0<timeout<=60')==1,'pinned supervisor literal');supervisor=templates[0].replace('assert 0<timeout<=60','assert 0<timeout<=180').encode()
    measurements={};histories={};warning_counts={}
    for group,(passed,commands) in HOSTS.items():
        report=json.loads(members[group+'/report.json']);need(report['passed']==report['completed']==passed and len(report['commands'])==commands,'retained exact attempt state: '+group)
        for label,digest in report['sources'].items():need(sha(members[group+'/sources/'+label])==digest,'all frozen source/data bytes: '+group+'/'+label)
        if group=='host05':
            need(report['sources']['runner.py']==PINS['test-vorbis-bigfloat.py'] and report['sources']['native/vorbis_bigfloat_host.c']==FIXTURE_SHA,'final executed reader/fixture equals pinned live code')
            for name,digest in LIVE_COMPONENT.items():need(sha(members[group+'/sources/component/'+name])==digest,'final executed selected source equals pinned live code')
        need(members[group+'/supervisor.py']==supervisor and sha(supervisor)==report['supervisor_sha256'] and sha(members[group+'/sources/supervisor-origin.py'])==PINS['test-vorbis-floor1-render.py'],'exact timeout-only supervisor derivation')
        selected_rows=rows if group=='host05' else rows[:699]
        need(json.loads(members[group+'/cases.json'])==json.loads(json.dumps(selected_rows)) and members[group+'/input.txt']==reader.encode(selected_rows) and
            report['input_sha256']==sha(members[group+'/input.txt']) and report['cases_sha256']==sha(members[group+'/cases.json']) and report['case_count']==len(selected_rows),'complete unchanged original corpus and exact input recipe')
        prefix=group+'/sources/component/';upstream=members[prefix+'upstream/libbf.c'];portable=members[prefix+'portable/libbf.c'];inv=json.loads(members[prefix+'upstream-manifest.json'])
        need(sha(upstream)==LIVE_COMPONENT['upstream/libbf.c'] and inv['archive_sha256']==reader.UPSTREAM_ARCHIVE_SHA,'original creator bytes unchanged in every attempt')
        pointer_old=b'    return bf_get_int32(pres, a, flags);';pointer_new=b'    int value;\n    int status = bf_get_int32(&value, a, flags);\n    *pres = value;\n    return status;'
        copy_old=b'    memcpy(r->tab, a->tab, a->len * sizeof(limb_t));';copy_new=b'    if (a->len != 0)\n        memcpy(r->tab, a->tab, a->len * sizeof(limb_t));'
        need(upstream.count(pointer_old)==upstream.count(copy_old)==1,'unique declared portability sites')
        expected_portable=upstream.replace(pointer_old,pointer_new)
        if group in ('host04','host05'):expected_portable=expected_portable.replace(copy_old,copy_new)
        need(portable==expected_portable and len(inv['modifications'])==(2 if group in ('host04','host05') else 1),'exact historical portability-copy state without source omission')
        for entry in inv['files']:
            body=members[prefix+entry['path']];need(len(body)==entry['bytes'] and sha(body)==entry['sha256'],'every original upstream inventory entry')
        command_summary=[]
        for index,command in enumerate(report['commands']):
            name=command['name'];request_body=members[group+'/'+name+'.request.json'];request=json.loads(request_body);receipt=command['supervisor']
            need(command['request_sha256']==sha(request_body) and request['nonce']==command['nonce'] and re.fullmatch('[0-9a-f]{32}',command['nonce']) and
                request['argv']==command['child_argv'] and request['timeout']==(180 if name.startswith('execute') else 60) and not command.get('forced_transport_stop'),'nonce-bound exact child request')
            need(PurePosixPath(request['receipt']).name==name+'.receipt.json' and PurePosixPath(request['stop']).name==name+'.stop' and
                PurePosixPath(request['receipt']).parent==PurePosixPath(request['stop']).parent,'owned task-local receipt/stop paths')
            if group=='host01':
                need(index==0 and command['transport_exit']==4294967295 and not receipt and group+'/'+name+'.receipt.json' not in members and
                    'Wsl/E_ACCESSDENIED' in members[group+'/'+name+'.stdout.log'].decode('utf-16-le'),'actual pre-child WSL refusal, no invented child execution')
            else:
                expected_exit=1 if (group=='host02' and name=='compile-limb64') or (group=='host03' and name=='execute-limb64') else 0
                need(command['transport_exit']==0 and json.loads(members[group+'/'+name+'.receipt.json'])==receipt and receipt['nonce']==command['nonce'] and
                    receipt['request_sha256']==command['request_sha256'] and receipt['state']=='terminal' and receipt['final'] and receipt['new_session'] and
                    receipt['child_pid']==receipt['owned_pgid'] and receipt['child_pid']>0 and receipt['child_reaped'] and receipt['group_gone'] and receipt['child_returncode']==expected_exit,
                    'every observed child terminal/reaped/group-gone with exact actual result')
            if name.startswith('compile-'):
                argv=command['child_argv'];need('-fsanitize=address,undefined' in argv and '-fno-sanitize-recover=all' in argv and '-Wall' in argv and '-Wextra' in argv,'unchanged sanitizer and visible warning flags')
                need(any(arg.endswith('/portable/libbf.c') for arg in argv) if group=='host02' else any(arg.endswith('.c') for arg in argv),'compiled the actual selected source')
                if name.endswith('-libbf'):need(any(arg.endswith('/portable/libbf.c') for arg in argv) and not any(arg.endswith('/upstream/libbf.c') for arg in argv),'compiled portable adaptation rather than unchanged stock copy')
                if group!='host02':need(('-Werror' in argv)==(name.endswith('-bigfloat') or name.endswith('-vorbis_bigfloat_host')),'strict own code; unchanged third-party warnings retained')
                if 'limb32' in name:need('-U__SIZEOF_INT128__' in argv,'forced32 through compiler selection, no header patch')
            command_summary.append(dict(name=name,transport=command['transport_exit'],child=receipt.get('child_returncode')))
        if group=='host02':need(b'-Werror=sign-compare' in members[group+'/compile-limb64.stderr.log'],'retained third-party warning-policy failure')
        if group=='host03':need(b'runtime error: null pointer passed as argument 1' in members[group+'/execute-limb64.stderr.log'] and b'in bf_set' in members[group+'/execute-limb64.stderr.log'],'retained actual zero-copy sanitizer failure')
        histories[group]=dict(passed=passed,cases=len(selected_rows),commands=command_summary)
        if passed:
            measurements[group]={}
            for bits in (64,32):
                model='limb'+str(bits);body=members[group+'/execute-'+model+'.stdout.log'];need(not members[group+'/execute-'+model+'.stderr.log'],'clean final sanitizer execution')
                measured=reader.compare(body,selected_rows,bits);need(measured==report['measurements'][model],'all exact Fraction/isqrt outputs, floors, OOM recovery and actual NTT evidence')
                corrupt=reader.corruption_controls(body,selected_rows,bits);need(corrupt==report['corruption_controls'][model] and len(corrupt)==10 and all(row['rejected'] for row in corrupt),'all pure corruption controls')
                measurements[group][model]=measured
            warnings={}
            for command in report['commands']:
                name=command['name']
                if not name.startswith('compile-'):continue
                log=members[group+'/'+name+'.stderr.log'].decode('utf-8');warnings[name]=len(re.findall(r': warning:',log));need(not re.search(r': (?:fatal )?error:',log),'no compiler errors in successful attempts')
                if name.endswith('-bigfloat') or name.endswith('-vorbis_bigfloat_host'):need(not log,'zero own-source/fixture compiler diagnostics')
            need([warnings['compile-limb64-libbf'],warnings['compile-limb64-cutils'],warnings['compile-limb32-libbf'],warnings['compile-limb32-cutils']]==[27,2,25,2],'all third-party diagnostics remain visible')
            warning_counts[group]=warnings
    for model,refusals,checks in (('limb64',463,5682096),('limb32',825,12587858)):
        final=measurements['host05'][model];need(final['cases']==701 and final['allocation_refusals']==refusals and final['checks']==checks and final['guards']==18 and
            final['capacity_refusals']==1643 and final['alias_checks']==1253 and final['ntt_rows']==[681,684],'fixed final measured totals')
    context=json.loads(members['context-stock-type/report.json']);need(context['completed'] and not context['passed'] and context['source_only'] and not context['native_executed'] and not context['sdk_executed'] and not context['qemu_executed'],'separate source-only stock type failure context')
    for name in ('lx6','rv32'):need(b'incompatible pointer type' in members['context-stock-type/'+name+'-libbf.stderr.log'] and b'bf_get_int32' in members['context-stock-type/'+name+'-libbf.stderr.log'],'actual compiler type mismatch diagnostic')
    need(sha(members['context-stock-type/upstream-libbf.c'])==LIVE_COMPONENT['upstream/libbf.c'],'stock type diagnostic uses unchanged creator source')
    seal=json.loads(members['receipts/final701-seal.json']);need(seal['passed'] and seal['final_host']=='host05' and seal['all_owned_commands_terminal'] and seal['measurements']=={k:v for k,v in measurements['host05'].items()},'final seal binds replayed mathematical results')
    for model in ('limb64','limb32'):
        body=members['host05/execute-'+model+'.stdout.log'];need(seal['captures'][model]==dict(bytes=len(body),sha256=sha(body)),'complete exact capture identity')
    return dict(passed=True,archive_sha256=ARCHIVE_SHA,manifest_sha256=MANIFEST_SHA,logical_members=len(members),physical_members=len(physical),
        final_cases=701,limb64_refusals=463,limb32_refusals=825,corruption_controls_per_model=10,actual_NTT_rows=[681,684],histories=histories,
        warning_counts=warning_counts,selected_source_unchanged=True,original_creator_source_unchanged=True,all_owned_commands_terminal=True,
        numerical_values_replayed=True,archived_code_executed=False,children_started=False,archive_extracted=False,native_target_executed=False,transcendental_gain_certified=False,production_selected=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path);args=parser.parse_args();result=verify()
    if args.report:
        target=args.report.resolve();need(target.is_relative_to(ROOT/'.build') and not target.exists(),'fresh task-local pure replay report');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result));return 0
if __name__=='__main__':raise SystemExit(main())
