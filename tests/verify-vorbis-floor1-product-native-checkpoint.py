"""Replay native floor1 evidence with pinned local pure readers only."""
import argparse, contextlib, hashlib, importlib.util, io, json, re, zipfile
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'tests/results/vorbis-floor1-product-native-20261026'
ARCHIVE_SHA='e2366f3078c20b9b2928e897c60eae5b5223403b9345ac621a0a41c6aff70ee7'
MANIFEST_SHA='419e6cf04799b672b31f82352aea411a731d7c5d11cf6120b0b0e9a11b2f388b'
PINS={'run-vorbis-floor1-product-qemu.py':'7201310d761815c1a672b9fa0272df608f349716a709f92e42881f4759b1f4f3',
      'test-vorbis-floor1-product.py':'d03e736c2e66504c5d2d22e9ae1b4af23ee8871d89c5fdb610caa9a3c118c9ff',
      'test-vorbis-floor1-product-protocol.py':'fff49545001295a755d868a6e19f49162ae56382de360af6ffca32d1b1f78248'}


def need(ok,reason):
    if not ok: raise ValueError(reason)


def sha(body): return hashlib.sha256(body).hexdigest()


def verify():
    need(sha((FOLDER/'captures.zip').read_bytes())==ARCHIVE_SHA,'pinned native archive')
    manifest_body=(FOLDER/'manifest.json').read_bytes()
    need(sha(manifest_body)==MANIFEST_SHA,'pinned manifest')
    manifest=json.loads(manifest_body)
    need(manifest['schema']=='vorbis-floor1-product-native-evidence-v1' and manifest['archive_sha256']==ARCHIVE_SHA,'manifest identity')
    with zipfile.ZipFile(FOLDER/'captures.zip') as archive:
        names=archive.namelist()
        need(len(names)==len(set(names))==263 and set(names)==set(manifest['files']),'exact native inventory')
        for name in names:
            path=PurePosixPath(name)
            need(path.as_posix()==name and not path.is_absolute() and '..' not in path.parts and ':' not in name and '\\' not in name,'contained member name')
        bodies={name:archive.read(name) for name in names}
    for name,body in bodies.items():
        need(manifest['files'][name]==dict(bytes=len(body),sha256=sha(body)),'member bytes/hash')
    read=lambda name:json.loads(bodies[name])
    modules={}
    for name,pin in PINS.items():
        path=ROOT/'tests'/name
        need(sha(path.read_bytes())==pin,'trusted local pure reader')
        spec=importlib.util.spec_from_file_location('trusted_native_floor1_'+str(len(modules)),path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);modules[name]=module
    subject=modules['run-vorbis-floor1-product-qemu.py']
    math=modules['test-vorbis-floor1-product.py']
    protocol=modules['test-vorbis-floor1-product-protocol.py']
    originals,cases=subject.native_cases(math)
    need(len(originals)==1663 and len(cases)==2957,'complete retained scalar campaign')
    current=(ROOT/'tests/run-vorbis-floor1-product-qemu.py').read_bytes()
    old_line=b"save(); print(json.dumps(dict(completed=True,passed=True,target=args.target,**report['measurements']))); return 0"
    new_line=b"save(); print(json.dumps(dict(completed=True,target=args.target,**report['measurements']))); return 0"
    need(current.count(new_line)==1,'one corrected summary expression')
    executed=current.replace(new_line,old_line)
    replay=read('replay02/report.json')
    need(replay['passed'] and not replay['original_outer_controllers_clean'] and replay['retained_original_outer_terminal_status']==1 and
         replay['retained_footer_error_type']=='TypeError' and replay['final_controller_sha256']==sha(current) and
         replay['executed_controller_sha256']==sha(executed),'retained outer failure and summary-only source change')
    need(json.loads((FOLDER/'replay.json').read_bytes())==replay,'public replay receipt')
    results={}
    for target,machine in (('esp32',94),('esp32c3',243)):
        report=read(target+'/report.json')
        need(report['completed'] and report['passed'] and report['target_executed'] and report['numerical_qualified'] and
             report['error_type']=='TypeError' and 'multiple values' in report['error'],'numeric completion followed by footer failure')
        for key in ('frame_decoder_executed','setup_owner_executed','Xiph_decoder_executed','deferred_scopes_resumed','production_firmware','physical_device'):
            need(report[key] is False,'finite runtime boundary')
        need(bodies[target+'/sources/controller.py']==executed,'exact operational controller; only footer later differs')
        need(read(target+'/cases.json')==dict(schema='native-floor1-product-cases-v1',cases=cases) and
             bodies[target+'/cases.h']==subject.header(cases)==bodies[target+'/project/main/cases.h'],'every descriptor/header byte')
        need(sha(bodies[target+'/cases.json'])==report['cases_sha256'] and sha(bodies[target+'/cases.h'])==report['cases_header_sha256'],'compiled case identities')
        for original,pin in report['inputs'].items():
            frozen=bodies[target+'/'+pin['snapshot']]
            need(sha(frozen)==pin['sha256'],'all frozen inputs')
            portable=original.replace('\\','/')
            if pin['snapshot']=='sources/controller.py':continue
            for marker in ('/idf/components/','/tests/'):
                if marker in portable:
                    local=ROOT/(marker.strip('/')+'/'+portable.split(marker,1)[1])
                    need(local.read_bytes()==frozen,'current operational sources equal executed snapshots')
        need([row['name'] for row in report['commands']]==['sdk-head','sdk-clean','build','symbols','merge','qemu'],'actual command inventory')
        for row in report['commands']:
            need(row['state']=='complete' and row['exit_status']==0,'actual child terminal0')
            for stream in ('stdout','stderr'):
                need(sha(bodies[target+'/'+row['name']+'.'+stream+'.log'])==row[stream+'_sha256'],'raw child diagnostics')
        need(report['sdk_child']==read(target+'/sdk-child.json') and report['sdk_child']['exit_status']==0 and report['sdk_child']['pid']>0,'real SDK child receipt')
        need(report['tools']['powershell']['personal_path_redacted'] and report['tools']['powershell']['path']=='runtime-path-redacted' and
             re.fullmatch('[0-9a-f]{64}',report['tools']['powershell']['sha256']),'explicit private-path alias with exact executable hash')
        for name,digest in report['build_outputs'].items():
            need(sha(bodies[target+'/'+name])==digest,'selected native build outputs')
        description=read(target+'/build/project_description.json')
        elf=bodies[target+'/build/'+description['app_elf']]
        need(elf[:6]==b'\x7fELF\x01\x01' and int.from_bytes(elf[16:18],'little')==2 and
             int.from_bytes(elf[18:20],'little')==machine and len(bodies[target+'/qemu-flash.bin'])==4194304,'actual ELF32/flash images')
        symbols=bodies[target+'/symbols.stdout.log'].decode('utf-8').replace('\r\n','\n')
        need(all(re.search(r'\bnative_vorbis_floor1_'+name+r'$',symbols,re.M) for name in ('scale','scale_measure')) and
             not re.search(r'\b(?:native_vorbis_(?:frame_decode|setup_owner_replace)|vorbis_synthesis|esp_vorbis_dec_open|floor1_host_fixture_main_not_executed)$',symbols,re.M),'generic-only linked execution')
        table=math.table_from_upstream(bodies[target+'/sources/upstream-floor1.c'])
        need(table==read(target+'/factors.json'),'independent rational coefficient table')
        measured=subject.validate_log(bodies[target+'/qemu.stdout.log'].decode('utf-8',errors='replace')+'\n'+
             bodies[target+'/qemu.stderr.log'].decode('utf-8',errors='replace'),cases,originals,math,table,target,report['cases_sha256'])
        need(measured==read(target+'/measurement.json') and {k:v for k,v in measured.items() if k!='rows'}==report['measurements'],'every native product limb')
        need(measured['exact_samples']==619564 and measured['exact_limb_words']==11817093 and measured['refused_rows']==23 and
             measured['refusal_controls']==713 and measured['runtime_assertions']==14627821 and measured['maximum_limbs']==36,'complete native counts')
        recorded=replay['profiles'][target]
        need(recorded['source_report_sha256']==sha(bodies[target+'/report.json']) and recorded['measurement_sha256']==sha(bodies[target+'/measurement.json']) and
             recorded['measurements']==report['measurements'] and recorded['original_controller_cli_exit']==1 and recorded['actual_native_children_exit']==0 and
             recorded['pure_replay_passed'] and recorded['summary_regression_passed'],'honest supplementary replay outcome')
        config=bodies[target+'/sdkconfig'].decode().replace('\r\n','\n')
        for key,values in recorded['watchdog'].items():need(re.findall('^'+key+r'=(.+)$',config,re.M)==values,'actual watchdog settings')
        need(recorded['watchdog']['CONFIG_ESP_TASK_WDT_EN']==['y'] and recorded['watchdog']['CONFIG_ESP_TASK_WDT_INIT']==['y'] and
             recorded['watchdog']['CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0']==['y'] and
             (target!='esp32' or recorded['watchdog']['CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1']==['y']),'unchanged watchdog/IDLE checking')
        for alias,tool in report['tools'].items():need(recorded['actual_tool_hashes_verified'][alias]['sha256']==tool['sha256'],'post-run binary identity')
        results[target]=report['measurements']
    need(results['esp32']['exact_limb_sha256']==results['esp32c3']['exact_limb_sha256'],'same exact native words across ISAs')
    need(len(replay['commands'])==10,'post-run SDK/compiler/dependency commands')
    for row in replay['commands']:
        need(row['exit_status']==0 and not row.get('forced_stop'),'post-run child terminal')
        for stream in ('stdout','stderr'):need(sha(bodies['replay02/'+row['name']+'.'+stream+'.log'])==row[stream+'_sha256'],'post-run raw diagnostics')
    failed=read('failed-build01/report.json')
    need(not failed['completed'] and not failed['passed'] and not failed['target_executed'] and
         failed['commands'][-1]['name']=='build' and failed['commands'][-1]['exit_status']==1,'retained first compile failure')
    need(not read('replay01/report.json')['passed'],'retained first alias-resolver replay failure')
    saved_protocol=read('protocol/report.json')
    need(saved_protocol['exit_status']==0 and saved_protocol['script_sha256']==PINS['test-vorbis-floor1-product-protocol.py'] and
         sha(bodies['protocol/stdout.log'])==saved_protocol['stdout_sha256'] and not bodies['protocol/stderr.log'],'actual pure protocol test receipt')
    output=io.StringIO()
    with contextlib.redirect_stdout(output):protocol.main()
    controls=json.loads(output.getvalue())
    need(controls==saved_protocol['result']==dict(passed=True,valid_targets=2,cases_per_target=9,rejected_controls=28),'independent malformed/partial/numeric controls')
    return dict(passed=True,members=len(bodies),native_profiles=results,protocol_controls=28,
                original_outer_controllers_clean=False,original_outer_exit_status=1,summary_only_corrected=True,
                replay_passed=True,production_firmware=False,deferred_scopes_resumed=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=verify()
    if args.output:
        need(not args.output.exists(),'fresh receipt');args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))
