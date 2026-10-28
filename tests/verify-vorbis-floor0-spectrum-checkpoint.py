"""Replay pinned floor0 spectrum evidence locally; no archived code or children."""
import argparse, ast, importlib.util, json, re
from pathlib import Path, PurePosixPath
import hashlib

ROOT = Path(__file__).resolve().parents[1]
FOLDER = 'tests/results/vorbis-floor0-spectrum-20261028'
ARCHIVE_SHA = 'c45e814f94f3462be4d4e5d054253d8d5fdbbec24e15d29b605da8eb4c2d9fb0'
MANIFEST_SHA = '1b04de449a6361bb33511ae826628aacf3e832ce02854675344e5433f77f613b'
PINS = {
    'vorbis_synthesis_checkpoint.py':'dfff6c46c56bf0cbf95a2385ca3584314b720088bd11124247e20605d8712ed5',
    'test-vorbis-floor0-product.py':'7ffd50ef1d747a17383e6ce631ff174b51c09d5749143b0b15cf4c8b0deb24f7',
    'test-vorbis-floor0-frame.py':'e92e1470f9806fe9fa2fe3c6903bd8f4015ab735ede11d54b6be5dc9c95c5357',
    'test-vorbis-setup.py':'ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff',
    'test-vorbis-floor-packet.py':'8ab01db0169af95e75f7aa6cc1e7c28df48371f94f445aaa03c08882c17776d7',
    'test-vorbis-residue.py':'1191a648a9070a995b1e256519ce71891f70779d924db651db16c490c856f31d',
    'vorbis_packet_frame_model.py':'5ed0ad7b589fc16de2d99f5aca77e179808aa0553fd22d9907b59369abcd77a9',
    'test-vorbis-packet-frame.py':'7c449b4b190500b0ab5931205f06e51e9f691112ebea80ac1affb7b200cb22d0',
    'test-vorbis-floor1-frame.py':'570f1cc80a4eea6611bb2ef8a051ce11d1a9e60d6aff96afbc764f247ffccdad',
    'test-vorbis-transform.py':'443000f55dc389a3a53a84af4a8bb118ada5367e4a3ccbf8525a9ceb630cf59c',
    'test-vorbis-floor0-angles.py':'1965f554980254900e5df6fb92ebfa2e1dd5ffa159ff9383561df33782e4a742',
    'test-vorbis-floor0-numeric.py':'0d3f49022a2c6c13cf8ab820b4b3aab97913fd46eb58bc70562230a14de5d088',
    'test-vorbis-floor1-render.py':'df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2'}


def verify():
    # Validate every dependency before importing even the shared inspection helper.
    for name, digest in PINS.items():
        if hashlib.sha256((ROOT/'tests'/name).read_bytes()).hexdigest() != digest:
            raise ValueError('pinned local reader: '+name)
    path = ROOT/'tests/vorbis_synthesis_checkpoint.py'
    spec = importlib.util.spec_from_file_location('floor0_checkpoint_helper', path)
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    need, sha = helper.need, helper.sha
    members = helper.archive_members(FOLDER, ARCHIVE_SHA, MANIFEST_SHA)
    read = lambda name: json.loads(members[name])
    need(len(members)==731 and sum(map(len,members.values()))==128907598, 'complete evidence inventory')
    for name in members:
        need(PurePosixPath(name).as_posix()==name and ':' not in name and '\\' not in name,
             'canonical data-only archive member')
    modules = {name:helper.load_local('tests/'+name, digest, 'floor0_checkpoint_'+str(index))
        for index,(name,digest) in enumerate(PINS.items()) if name not in
        ('vorbis_synthesis_checkpoint.py','test-vorbis-floor1-render.py')}
    math = modules.pop('test-vorbis-floor0-product.py')
    frame = modules.pop('test-vorbis-floor0-frame.py')
    need(frame.SPECTRUM_BOUND==2e-12 and frame.TRANSFORM_BOUND==5e-12, 'unchanged predeclared numerical bounds')
    manifest = json.loads((ROOT/FOLDER/'manifest.json').read_bytes())
    omitted = {row['path']:row for row in manifest['omitted']}
    need(set(omitted)=={'math02/product','math03/product','frame03/handoff','frame04/handoff',
        'frame06/handoff','frame07/handoff','frame08/handoff'} and all(
        row['bytes']>0 and re.fullmatch('[0-9a-f]{64}',row['sha256']) and name not in members
        for name,row in omitted.items()), 'only seven rebuildable host executables omitted')

    def sources(group, report, live=False, profile=False):
        for label,digest in report['sources'].items():
            body = members[group+'/sources/'+label]
            need(sha(body)==digest, 'every frozen source byte')
            if not live: continue
            if profile: relative = 'idf/components/'+label
            elif label.startswith('components/'): relative = 'idf/'+label
            elif label.startswith('native/'): relative = 'tests/'+label
            elif label=='runner.py': relative = 'tests/test-vorbis-floor0-'+('product.py' if group.startswith('math') else 'frame.py')
            elif label=='supervisor-origin.py': relative = 'tests/test-vorbis-floor1-render.py'
            elif label in PINS: relative = 'tests/'+label
            else: continue
            # Documentation may be updated after the executed code was frozen.
            if Path(relative).suffix in ('.c','.h','.inc','.py') or Path(relative).name=='CMakeLists.txt':
                need((ROOT/relative).read_bytes()==body, 'current executed source equals final snapshot')

    def commands(group, report, successful=True):
        for row in report['commands']:
            stem=group+'/'+row['name'];request=read(stem+'.request.json')
            need(request['argv']==row['child_argv'] and request['nonce']==row['nonce'] and
                sha(members[stem+'.request.json'])==row['request_sha256'], 'owned request binding')
            receipt=row['supervisor']
            if not receipt:
                need(not successful and row['transport_exit']!=0 and stem+'.receipt.json' not in members,
                     'preserved refusal before child dispatch')
                continue
            need(receipt==read(stem+'.receipt.json') and receipt['nonce']==row['nonce'] and
                receipt['request_sha256']==row['request_sha256'] and row['transport_exit']==0 and
                not row.get('forced_transport_stop') and receipt['state']=='terminal' and receipt['final'] and
                receipt['new_session'] and receipt['child_pid']==receipt['owned_pgid'] and receipt['child_reaped'] and
                receipt['group_gone'] and (not successful or receipt['child_returncode']==0), 'all children terminal and reaped')
        if 'supervisor_sha256' in report:
            need(sha(members[group+'/supervisor.py'])==report['supervisor_sha256'], 'frozen supervisor identity')
            tree=ast.parse(members[group+'/sources/supervisor-origin.py'])
            definitions=[ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and
                any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
            need(len(definitions)==1 and members[group+'/supervisor.py']==definitions[0].encode(),
                 'supervisor is literal data from frozen local controller')

    def host(group):
        report,capture=helper.clean_host(members,group)
        sources(group,report,live=True);commands(group,report)
        need([row['name'] for row in report['commands']]==['compiler-version','compile','execute'] and
            report['sanitizers']==['address','undefined'] and not report['native_executed'] and
            not report['PCM_executed'], 'complete host-only command scope')
        argv=report['commands'][1]['child_argv']
        need(all(flag in argv for flag in ('-UNDEBUG','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra',
            '-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all')) and
            sum(arg.endswith('.c') for arg in argv)==(2 if group.startswith('math') else 14), 'all compilation units instrumented')
        need(sha(members[group+'/input.bin'])==report['input_sha256'], 'raw input identity')
        executable='product' if group.startswith('math') else 'handoff'
        need(omitted[group+'/'+executable]['sha256']==report['binary_sha256'], 'omitted derived binary identity')
        return report,capture

    math_report,math_capture=host('math03');rows=math.cases()
    need(len(rows)==81384 and math.encode(rows)==members['math03/input.bin'], 'complete independently rebuilt arithmetic input')
    math_measured=math.inspect_capture(math_capture,rows)
    math_controls=math.corruption_controls(math_capture,rows)
    need(math_measured==math_report['measurements'] and len(math_controls)==9 and
        math_controls==math_report['corruption_controls'] and math_report['controls']==
        dict(rows=81384,invalid=2174,controls=444,checks=7100180), 'all products, once-rounded bits and nine corruption controls')
    need(members['math03/execute.stdout.log'].decode().strip()==
        'FLOOR0_PRODUCT_CAPTURE rows=81384 invalid=2174 controls=444 checks=7100180', 'actual arithmetic guard totals')

    report,capture=host('frame08');model=read('frame08/model.json')
    original,original_model,table=frame.original_inputs()
    need(members['frame08/sources/original31.json']==original and
        members['frame08/sources/xiph-floor1.c']==table and model['cases'][:434]==original_model['cases'],
        'all original434 raw packets and pinned independent table retained')
    original_model['cases'].extend(frame.supplement(modules))
    need(model==original_model and len(model['cases'])==447 and len(frame.EXTRA_ROUTES)==13 and
        modules['test-vorbis-packet-frame.py'].encode_input(model)==members['frame08/input.bin'],
        'all original packets plus thirteen genuine raw-packet supplements')
    need(sha(members['frame08/model.json'])==report['model_sha256'] and
        sha(members['frame08/front.bin'])==report['front_sha256'] and report['units']==14 and
        not report['overlap_executed'] and not report['production_selected'] and not report['deferred_scopes_resumed'] and
        report['floor0_gain_executed'] and report['transform_executed'], 'qualified frame/transform scope and capture provenance')
    relations=json.loads(original)['relations']
    need(len(relations)==report['original_relations']==14 and report['relations_sha256']==
        sha(json.dumps(relations,sort_keys=True).encode())=='049c77280080e459e3ff6ce9315f3156074b54a79e9607b4c7c8ba3633e83589',
        'fourteen unchanged relation identities, without claiming PCM execution')
    need(modules['test-vorbis-transform.py'].oracle_anchors()==report['transform_anchors'], 'independent FFT anchors')
    measured=frame.compare(capture,members['frame08/front.bin'],model,table,modules)
    controls=frame.corruption_controls(capture,members['frame08/front.bin'],model,table,modules)
    need(measured==report['measurements'] and len(controls)==10 and controls==report['corruption_controls'] and
        report['controls']==dict(cases=447,channels=894,floor0=362,floor1=532,refusals=4522,checks=5155393),
        'complete raw front end, spectrum, IMDCT and ten rejection controls')
    need(measured['original_floor0_channels']==336 and measured['floor1_channels']==532 and
        measured['exact_floor0_joint_values']==116960 and measured['near_unity_normalization_channels']==2 and
        measured['routed_channels']==14 and measured['zero_channels']==5 and
        measured['nonzero_floor0_reference_values']==5376 and measured['time_values']==751360 and
        not measured['full_codec_qualified'], 'all final numerical and explicit route cohorts')
    need(members['frame08/execute.stdout.log'].decode().strip()==
        'FLOOR0_HANDOFF cases=447 channels=894 floor0=362 floor1=532 refusals=4522 checks=5155393 live=0 bytes=0',
        'actual raw-packet guard and allocation totals')

    seal=read('receipts/vorbis-floor0-frame-final-seal-20261028-01.json')
    need(all(seal[key] for key in ('passed','live_sources_identical_to_frozen','all_commands_terminal',
        'all_original434_rows_identical','privacy_passed')) and seal['original_relations']==14 and
        seal['runner_sha256']==PINS['test-vorbis-floor0-frame.py'] and
        seal['fixture_sha256']==sha(members['frame08/sources/native/vorbis_floor0_frame_host.c']), 'sealed source and corpus provenance')
    for key in ('capture_sha256','front_sha256','binary_sha256','model_sha256','input_sha256'):
        need(seal[key]==report[key], 'seal binds final executed evidence')

    profiles=read('profiles01/report.json');sources('profiles01',profiles,live=True,profile=True)
    names=['lx6-version','lx6-product','lx6-floor0_spectrum','lx6-header','rv32-version','rv32-product',
        'rv32-floor0_spectrum','rv32-header','lint-product','lint-floor0_spectrum']
    need(profiles['completed'] and profiles['passed'] and profiles['source_only'] and not profiles['native_executed'] and
        [row['name'] for row in profiles['commands']]==names, 'ten source-only profile commands')
    for row in profiles['commands']:
        need(row['returncode']==0 and not row.get('forced_stop'), 'profile process terminal')
        for stream in ('stdout','stderr'):
            need(sha(members['profiles01/'+row['name']+'.'+stream+'.log'])==row[stream+'_sha256'], 'unaltered profile diagnostics')
    need(profiles['lint']==[dict(unit='product',warnings=0,errors=0),dict(unit='floor0_spectrum',warnings=0,errors=0)] and
        all(not members['profiles01/'+name+'.'+stream+'.log'] for name in names[-2:] for stream in ('stdout','stderr')),
        'both production units have zero lint diagnostics')
    need(len(profiles['objects'])==6 and {row['name'] for row in profiles['objects']}==
        {target+'-'+unit+'.o' for target in ('lx6','rv32') for unit in ('product','floor0_spectrum','header')}, 'six actual source objects')
    for row in profiles['objects']:
        body=members['profiles01/'+row['name']]
        machine=94 if row['name'].startswith('lx6-') else 243
        need(sha(body)==row['sha256'] and body[:6]==b'\x7fELF\x01\x01' and
            int.from_bytes(body[16:18],'little')==1 and int.from_bytes(body[18:20],'little')==row['machine']==machine,
            'hash-bound little-endian ELF32 relocatable for LX6/RV32')
    own_frames={}
    for name,text in profiles['stack_records'].items():
        # The profile controller used read_text(), which normalizes CRLF.
        # archive_members already checks the original unnormalized byte hash.
        need(members['profiles01/'+name].decode().replace('\r\n','\n')==text, 'unaltered compiler stack report')
        parsed={}
        for line in text.splitlines():
            site,count,kind=line.split('\t');need(kind=='static','only static own-function frames')
            parsed[site.rsplit(':',1)[-1]]=int(count)
        own_frames[name]=parsed
    for target,prepare,product in (('lx6',400,176),('rv32',384,192)):
        need(own_frames[target+'-floor0_spectrum.su']['native_vorbis_frame_floor0_prepare']==prepare and
            own_frames[target+'-floor0_spectrum.su']['native_vorbis_frame_floor0_materialize']==272 and
            own_frames[target+'-product.su']['native_floor0_product']==product, 'bounded own frames, without whole-call-chain claim')

    for group,source_group,fixture,warnings in (
        ('math-fixture-lint01','math03','vorbis_floor0_product_host.c',0),
        ('frame-fixture-lint01','frame08','vorbis_floor0_frame_host.c',12)):
        lint=read(group+'/report.json');diagnostics=members[group+'/stdout.log']+members[group+'/stderr.log']
        need(lint['completed'] and lint['returncode']==0 and lint['source_only'] and not lint['native_executed'] and
            not lint['SDK_executed'] and lint['warnings']==warnings and lint['errors']==0 and
            len(re.findall(rb': warning:',diagnostics))==warnings and not re.search(rb': error:',diagnostics) and
            lint['source_sha256']==sha(members[source_group+'/sources/native/'+fixture]), 'honest fixture lint totals and actual source binding')
        need(members[group+'/clang-tidy.yaml']==members['profiles01/clang-tidy.yaml']==(ROOT/'.clang-tidy').read_bytes(),
             'unchanged lint configuration, no added suppressions')

    # Preserve failed preparation, dispatch, compiler and pure-reader attempts.
    history={}
    for group in ['math01','math02']+['frame'+str(i).zfill(2) for i in range(1,8)]:
        old=read(group+'/report.json');sources(group,old);commands(group,old,successful=False)
        history[group]=dict(completed=old['completed'],passed=old['passed'],commands=len(old['commands']))
    need(not history['math01']['passed'] and not history['math02']['passed'] and
        all(not history[group]['passed'] for group in ('frame01','frame02','frame03','frame05')) and
        all(history[group]['passed'] for group in ('frame04','frame06','frame07')), 'historical attempts retained honestly')
    need(members['frame03/capture.bin']==members['frame04/capture.bin'] and
        members['frame06/capture.bin']==members['frame07/capture.bin'], 'pure fixes and stronger guards preserve their numerical captures')
    return dict(passed=True,members=len(members),decoded_bytes=sum(map(len,members.values())),math=math_measured,
        math_corruption_controls=math_controls,frame=measured,frame_corruption_controls=controls,
        historical_attempts=history,profile_commands=10,ELF32_objects=6,production_lint_warnings=0,
        fixture_lint_warnings=dict(math=0,frame=12),own_function_frames=own_frames,
        original_relations=14,archived_code_executed=False,commands_reexecuted=0,files_extracted=False,
        native_executed=False,overlap_executed=False,PCM_executed=False,full_codec_qualified=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path);args=parser.parse_args()
    if args.report and (not args.report.resolve().is_relative_to(ROOT/'.build') or args.report.exists()):
        raise ValueError('fresh report within task-local .build required')
    result=verify()
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))
