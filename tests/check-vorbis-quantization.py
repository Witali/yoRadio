"""Replay saved owned-VQ/affine results; execute no component, compiler or SDK."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
ORACLE_SHA='bf5d0c1097fd1ef2f167f078e7c7204f3ebe6dd6e062ae20cadc739cd6f91e74'
CONTROL_SHA='34a6010c57bf37f3a484fc741364f054e6c7162b55920f144fe5fc0d00ce2754'
MODULE={'floor0.c':'297e055a68ff2ee4ea71e0879aef12456139945015d346b2a12a18db7b0a4335',
    'quant.c':'14e6b7eb910ee4c7a67ff0b1eccf8f4038315d1bf5821ad51fba32824e5ffb40',
    'include/native_vorbis_floor0.h':'122ee70ab248c5aa3a46354288be3d78418e6d5e67f15c4d44d43f5ff704c63b',
    'include/native_vorbis_quant.h':'55948c2a9af4d92e2ebe614398fd09708c454b4a6f179b602d964f06aac9a499',
    'CMakeLists.txt':'a907f471c7712d6021606dcc6a61bae23cd43127b407e8ffca9a27ce0ae4cf8b'}

def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(data):return hashlib.sha256(data).hexdigest()
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result);return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('host','esp32','esp32c3','receipts','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh task-local comparison output')
    out.mkdir(parents=True);(out/'inputs').mkdir()
    report=dict(completed=False,passed=False,measurement_completed=False,host_numeric_recomputed=False,finite_quantization_affine_qualified=False,targets={},inputs={},identity_only={},
        SDK_or_QEMU_executed=False,component_executed=False,decoder_executed=False,production_radio_integration=False,
        full_floor0_qualified=False,full_G6_qualified=False,PCM_qualified=False,physical_device=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def read(path):
        path=path.resolve();body=path.read_bytes();digest=sha(body);previous=report['inputs'].get(str(path))
        need(previous is None or previous['sha256']==digest,'consumed input changed')
        destination=out/'inputs'/digest
        if not destination.exists():destination.write_bytes(body)
        else:need(destination.read_bytes()==body,'content-addressed input collision')
        report['inputs'][str(path)]=dict(sha256=digest,bytes=len(body),snapshot='inputs/'+digest);return body
    def document(path):return json.loads(read(path))
    def identity(path):
        path=path.resolve();body=path.read_bytes();pin=dict(sha256=sha(body),bytes=len(body),reason='External executable identity only; body is not retained.')
        previous=report['identity_only'].get(str(path));need(previous is None or previous==pin,'external executable identity changed')
        report['identity_only'][str(path)]=pin;return pin['sha256']
    def terminal(name,directory,script,pins=None):
        receipt=document(args.receipts/(name+'.json'))
        need(receipt['status']=='TERMINAL' and type(receipt['returncode'])is int and receipt['returncode']==0 and
             type(receipt['owned_pid'])is int and receipt['owned_pid']>0 and not receipt.get('timed_out') and
             not receipt.get('interrupted') and not any(key in receipt for key in ('error_type','returncode_after_stop')),'actual successful outer terminal '+name)
        cwd=Path(receipt['cwd']).resolve();argv=receipt['argv']
        need(cwd==ROOT and argv[1:4]==['-B','-X','utf8'] and Path(argv[0]).resolve()==Path(sys.executable).resolve() and
             (cwd/argv[4]).resolve()==ROOT/'tests'/script,'actual executable/script/cwd')
        need(sha(read(ROOT/'.build/cyd-vorbis-format-command-01.py'))==receipt['runner_sha256']=='33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e' and
             receipt['executable_sha256']==identity(Path(sys.executable))=='4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a','owned runner/Python identity')
        def option(key):
            flag='--'+key;need(argv.count(flag)==1 and argv.index(flag)+1<len(argv),'one complete command option '+key)
            return argv[argv.index(flag)+1]
        need((cwd/option('output')).resolve()==directory,'outer receipt belongs to supplied campaign')
        if name=='host':need(len(argv)==7 and argv[5]=='--output','exact actual host argv')
        else:
            need(option('target')==name and (cwd/option('cases')).resolve()==args.host.resolve()/'target-cases','actual target and original cases directory')
            for key,value in pins.items():need(option(key+'-sha256')==value,'actual native source/data/tool pin '+key)
        need({Path(path).resolve() for path in receipt['logs']}=={args.receipts.resolve()/(name+'.'+stream+'.log') for stream in ('stdout','stderr')},'exact owned outer log inventory')
        for path,pin in receipt['logs'].items():
            body=read(Path(path));need(len(body)==pin['bytes'] and sha(body)==pin['sha256'],'actual outer log identity')
    def sources(directory,pins):
        for origin,pin in pins.items():
            snapshot=(directory/pin['snapshot']).resolve();need(snapshot.is_relative_to(directory),'contained frozen input')
            body=read(snapshot);need(sha(body)==pin['sha256']==sha(read(Path(origin))) and ('bytes'not in pin or len(body)==pin['bytes']),'original/frozen input identity')
    save()
    try:
        read(Path(__file__));host=args.host.resolve();captured={'esp32':args.esp32.resolve(),'esp32c3':args.esp32c3.resolve()}
        terminal('host',host,'test-vorbis-quantization.py');hr=document(host/'report.json')
        need(all(hr[k]is True for k in ('completed','passed','prepared','component_executed','source_inputs_unchanged')) and
             (hr['cases'],hr['target_cases'],hr['metadata_controls'])==(6572,200,152),'actual complete sanitized host campaign')
        sources(host,hr['sources'])
        oracle_path=ROOT/'tests/test-vorbis-quantization.py';control_path=ROOT/'tests/run-vorbis-quantization-qemu.py'
        need(sha(read(oracle_path))==ORACLE_SHA==hr['sources'][str(oracle_path.resolve())]['sha256'],'exact executed independent oracle source')
        need(sha(read(control_path))==CONTROL_SHA,'exact reviewed native capture reader')
        oracle=module(oracle_path,'quantization_oracle');control=module(control_path,'quantization_capture')
        for name,digest in MODULE.items():need(sha(read(ROOT/'idf/components/native_vorbis_numeric'/name))==digest,'reviewed whole component source '+name)
        need(sha(read(ROOT/'tests/native/vorbis_quantization_test.c'))=='4e34f90c8a9cd6c212d8ae9b3e123bb80749f7ee80f44a85ef45845247ad3a42','actual guarded host adapter source')
        need(hr['policy']==oracle.POLICY and all(hr[k]is False for k in ('full_floor0_qualified','full_G6_qualified','PCM_qualified','decoder_executed','SDK_or_QEMU_executed','physical_device')),'fixed host policy and qualification scope')
        need(oracle.check_phase_table(read(host/'sources/floor0.c').decode())==hr['phase_table'],'same complete independently checked phase table')
        owner=ast.parse(read(host/'sources/supervisor-owner.py'))
        literals=[node.value for node in owner.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUPERVISOR' for t in node.targets)]
        need(len(literals)==1 and ast.literal_eval(literals[0]).encode()==read(host/'supervisor.py'),'actual nonce-owned supervisor body')
        need([row['name'] for row in hr['commands']]==['compiler-version','compiler-machine','compile','execute'],'all four actual host commands')
        for command in hr['commands']:
            name=command['name'];request=document(host/(name+'.request.json'));receipt=document(host/(name+'.receipt.json'))
            need(receipt==command['supervisor'] and request['argv']==command['child_argv'] and request['timeout']==60 and
                 receipt['request_sha256']==sha(read(host/(name+'.request.json'))) and receipt['nonce']==request['nonce']==command['nonce'] and
                 receipt['state']=='terminal' and type(receipt['child_returncode'])is int and receipt['child_returncode']==0 and
                 all(receipt[k]is True for k in ('final','new_session','child_reaped','group_gone')) and
                 type(receipt['child_pid'])is int and receipt['child_pid']>0 and receipt['owned_pgid']==receipt['child_pid'] and
                 command['transport_returncode']==0 and command['transport_pid']>0 and not command.get('forced_transport_stop') and 'cleanup_error'not in receipt,'owned host command request/terminal/cleanup')
            for stream in ('stdout','stderr'):
                body=read(host/(name+'.'+stream+'.log'));need(sha(body)==command[stream+'_sha256'],'actual host command stream')
                if name in ('compile','execute'):need(not body,'clean strict compile and sanitized run')
        need(all(flag in hr['commands'][2]['child_argv'] for flag in ('-Werror','-fno-fast-math','-ffp-contract=off','-fsanitize=address,undefined','-fno-sanitize-recover=all')),'actual floating and sanitizer flags')
        model=document(host/'cases.json');inputs=read(host/'inputs.bin');output=read(host/'outputs.bin')
        need(sha(read(host/'cases.json'))==hr['model_sha256'] and sha(inputs)==hr['input_sha256'] and sha(output)==hr['output_sha256'] and
             oracle.decode_input(inputs)==model and oracle.encode_input(model)==inputs,'every original host input/model/output byte')
        decoded=oracle.decode_output(output,model);repeated=oracle.compare_all(model,decoded['rows'])
        need(repeated==hr['numerical'] and repeated['measurement_completed']is True and repeated['cases']==6572 and
             repeated['passed']is hr['passed'] and decoded['metadata_controls']==hr['metadata_controls']==152,'complete exact/Decimal host replay')
        report.update(host_numeric_recomputed=True,host_cases=repeated['cases'],host_passed=repeated['passed'],host_metadata_controls=152,
            host_exact_values=repeated['exact_values'],host_numerical_cases=repeated['numerical_cases'])
        target=document(host/'target-cases/cases.json');header=read(host/'target-cases/cases.h');expected=document(host/'target-cases/expected.json')
        for name in ('cases.json','cases.h','expected.json'):need(sha(read(host/'target-cases'/name))==hr['target_input_sha256'][name],'unchanged predeclared target input')
        need(len(target['cases'])==200 and header.decode('ascii')==oracle.target_header(target) and
             expected==dict(schema='native-vorbis-quantization-expected-v1',policy=oracle.POLICY,cases=[oracle.expected_case(row) for row in target['cases']]),'all200 exact original target header/expected values')
        by_id={row['id']:row for row in model['cases']};need(all(by_id[row['id']]==row for row in target['cases']),'target subset of executed host model')
        rows=control.validate_cases(target,header.decode('ascii'))
        for architecture,directory in captured.items():
            native=document(directory/'report.json');terminal(architecture,directory,'run-vorbis-quantization-qemu.py',native['source_sha256'])
            need(native['target']==architecture and native['result']=='CHECKED_QUANTIZATION_CAPTURED' and all(native[k]is True for k in ('completed','math_capture_completed','whole_module_compiled','source_inputs_unchanged')) and
                 all(native[k]is False for k in ('passed','numerical_reference_compared','numerical_qualified','full_floor0_qualified','decoder_executed','production_firmware','physical_device')),'actual structural native capture and finite scope')
            sources(directory,native['inputs'])
            for relative,digest in MODULE.items():need(sha(read(directory/'sources/components/native_vorbis_numeric'/relative))==digest,'same complete frozen native component')
            need(read(directory/'sources/controller.py')==read(control_path),'same executed frozen capture controller')
            for name in ('cases.json','cases.h'):need(read(directory/'sources/cases'/name)==read(host/'target-cases'/name),'same original native model/header')
            need(native['source_sha256']['cases']==hr['target_input_sha256']['cases.json'] and native['source_sha256']['cases-header']==sha(header),'same native data pins')
            need(set(native['source_sha256'])==set(control.PARTS)|{'cases','cases-header','qemu'},'complete native source/data/QEMU pin inventory')
            for key,relative in control.PARTS.items():need(native['source_sha256'][key]==MODULE[relative],'same native source argument pin')
            need(native['sdk_child']['exit_status']==0 and type(native['sdk_child']['pid'])is int and native['sdk_child']['pid']>0,'normal SDK child completion')
            need(native['elf_machine']==(94 if architecture=='esp32' else 243),'reported native architecture')
            elf=read(directory/'elf-header.bin');need(len(elf)==52 and sha(elf)==native['build_outputs']['elf-header.bin'] and elf[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<H',elf,18)[0]==native['elf_machine'],'saved actual ELF32 architecture header only')
            need([row['name'] for row in native['commands']]==['sdk-head','sdk-clean','build','dependencies','symbols','merge','qemu','sdk-head-after','sdk-clean-after'],'all nine actual native commands')
            for command in native['commands']:
                need(command['state']=='complete' and type(command['exit_status'])is int and command['exit_status']==0 and type(command['pid'])is int and command['pid']>0 and not command['timed_out'] and not command['interrupted'] and Path(command['cwd']).resolve()==directory,'normal owned native command')
                for stream in ('stdout','stderr'):need(sha(read(directory/(command['name']+'.'+stream+'.log')))==command[stream+'_sha256'],'actual native command stream')
            for name in ('sdk-head','sdk-head-after'):need(read(directory/(name+'.stdout.log')).decode().strip()==native['sdk_revision']==control.SDK_HEAD[architecture],'same before/after SDK revision')
            for name in ('sdk-clean','sdk-clean-after'):need(not read(directory/(name+'.stdout.log')).strip(),'SDK clean before/after')
            need(not native['build_warning_lines'],'no actual build warnings')
            log=read(directory/'qemu.stdout.log').decode('utf-8').replace('\r\n','\n')+'\n'+read(directory/'qemu.stderr.log').decode('utf-8').replace('\r\n','\n')
            parsed=control.validate_log(log,rows,architecture,native['source_sha256']['cases'])
            need(parsed.pop('rows')==native['rows'] and parsed==native['observed'] and parsed['cases']==200 and parsed['metadata_controls']==152,'every actual ordered native event/value/core/guard')
            report['targets'][architecture]=oracle.compare_target_rows(target,expected,native['rows']);save()
        need(all(sha(Path(origin).read_bytes())==pin['sha256']==sha((out/pin['snapshot']).read_bytes()) for origin,pin in report['inputs'].items()),'all consumed original/frozen input bytes unchanged')
        need(all(identity(Path(origin))==pin['sha256'] for origin,pin in tuple(report['identity_only'].items())),'external executable identities unchanged')
        complete=repeated['measurement_completed'] and all(row['measurement_completed'] for row in report['targets'].values())
        passed=complete and repeated['passed'] and all(row['passed'] for row in report['targets'].values())
        report.update(completed=True,measurement_completed=complete,passed=passed,native_cases_required=sum(row['cases'] for row in report['targets'].values()),
            native_values_compared=sum(len(row['metrics']) for row in report['targets'].values()),native_affine_values_compared=sum(row['exact_values'] for row in report['targets'].values()),
            native_numerical_cases_compared=sum(row['numerical_cases'] for row in report['targets'].values()),finite_quantization_affine_qualified=passed,
            result='FINITE_QUANTIZATION_AFFINE_QUALIFIED' if passed else 'FINITE_QUANTIZATION_AFFINE_REJECTED')
        save();print(json.dumps({key:report[key] for key in ('completed','passed','host_cases','host_numeric_recomputed','native_values_compared','result')}));return 0 if passed else 1
    except BaseException as error:report.update(completed=False,passed=False,error=repr(error));save();raise

if __name__=='__main__':raise SystemExit(main())
