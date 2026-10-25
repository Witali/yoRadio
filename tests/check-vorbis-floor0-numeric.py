"""Bind completed host/native captures and compare every native floor0 value.

Only exact-hash, reviewed pure readers/oracle definitions are imported. No SDK,
QEMU, compiler, decoder, reference process or physical device is executed.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
HOST_HELPER = '0d3f49022a2c6c13cf8ab820b4b3aab97913fd46eb58bc70562230a14de5d088'
TARGET_HELPER = 'a34da82409f4c4ca60a6d33f1e8e2159c3adb0d3cddc2ce7f6b03c8cb0856b8f'
WRAPPER = '33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e'
HOST_PYTHON = '4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a'
MODULE = {'floor0.c':'f456176e00303460978c3f98d9349323e66722bb7eca8204fad14400760b27b1',
          'include/native_vorbis_floor0.h':'6dab3b6e60d1c1bd64d5fc19dbf65598cc648c07147521f81079174890e2e97a',
          'CMakeLists.txt':'450187b88c7faf362092c7b0a95137c85d8d2492e4426b8248cd61d103a8b0aa'}
DATA = {'cases.json':'8807f04492065bd7ce0d9377eb158a7300c32f2c53c700bfbcdeacb6038cc595',
        'cases.h':'10b631e6b8040ccfb518d9be8692081e88be4ca8aabd24a1f53a395773f5ab37',
        'expected.json':'fb5ba38e984d0d7f1b0c34ca56bb719645aeb662e52bc9486409d996c72af69c'}
NATIVE_COMMANDS = ('sdk-head','sdk-clean','build','dependencies','symbols','merge',
                   'qemu','sdk-head-after','sdk-clean-after')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def norm(value):
    return str(value).replace('\\','/').rstrip('/')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('host','host-terminal','esp32','esp32-terminal','esp32c3','esp32c3-terminal','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh .build checker output')
    directories=[getattr(args,name).resolve() for name in ('host','esp32','esp32c3')]
    need(all(path.is_relative_to(ROOT/'.build') and path.is_dir() for path in directories) and
         not any(out.is_relative_to(path) or path.is_relative_to(out) for path in directories),'independent existing captures')
    out.mkdir(parents=True);(out/'inputs').mkdir()
    report=dict(completed=False,passed=False,measurement_completed=False,
        finite_coefficient_numeric_qualified=False,full_floor0_qualified=False,full_G6_qualified=False,
        PCM_qualified=False,decoder_executed=False,new_reference_processes_executed=False,
        SDK_or_QEMU_executed=False,production_radio_integration=False,physical_device=False,
        inputs={},pure_helpers_reused={},targets={},host_numeric_recomputed=False,
        scope='Finite exact-binary64 coefficient/gain layer plus retained host approximation tests. '
              'Recorded host campaign is rebound, not re-executed. Selected consumed source/metadata/log/input bytes '
              'and build/tool identities; no complete SDK dependency closure or binary semantics.')
    fingerprints={}
    def save():
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def read(path, role, expected=None, body=True):
        path=Path(path).resolve();need(path.is_file(),'required consumed file '+str(path))
        if body:
            data=path.read_bytes();pin=dict(bytes=len(data),sha256=sha(data))
        else:
            digest=hashlib.sha256()
            with path.open('rb') as stream:
                for part in iter(lambda:stream.read(1024*1024),b''):digest.update(part)
            data=None;pin=dict(bytes=path.stat().st_size,sha256=digest.hexdigest())
        need(expected is None or pin['sha256']==expected,'recorded identity '+str(path))
        key=str(path)
        if key in fingerprints:
            need(fingerprints[key]==pin,'consumed input changed')
        else:
            fingerprints[key]=pin
            row=dict(pin,roles=[])
            if body:
                snapshot='inputs/'+str(len(fingerprints)).zfill(4)+'-'+path.name
                (out/snapshot).write_bytes(data);row['snapshot']=snapshot
            else:
                row['identity_only_omission']='Executable/build binary retained by size/hash only; no binary semantics.'
            report['inputs'][key]=row
        report['inputs'][key]['roles'].append(role)
        return data
    def obj(path,role,expected=None):
        return json.loads(read(path,role,expected))
    def argument(argv,flag):
        need(argv.count(flag)==1 and argv.index(flag)+1<len(argv),'one argument '+flag)
        return argv[argv.index(flag)+1]
    def resolved(value,cwd=ROOT):
        path=Path(value);return path.resolve() if path.is_absolute() else (cwd/path).resolve()
    def load(path,pin,name):
        read(path,name,pin)
        snapshot=out/report['inputs'][str(Path(path).resolve())]['snapshot']
        spec=importlib.util.spec_from_file_location(name,snapshot)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        need(sha(snapshot.read_bytes())==pin,'exact pure helper while importing')
        report['pure_helpers_reused'][name]=dict(path=str(path),sha256=pin,
            scope='Reviewed definitions only; main guarded/unexecuted. '+name)
        return module
    def outer(path,directory,script):
        r=obj(path,'actual outer terminal')
        need(r['status']=='TERMINAL' and type(r['returncode']) is int and r['returncode']==0 and
             type(r['owned_pid']) is int and r['owned_pid']>0 and r['runner_sha256']==WRAPPER and
             r['executable_sha256']==HOST_PYTHON and resolved(r['cwd'])==ROOT and
             not r.get('timed_out') and not r.get('interrupted') and not r.get('error_type') and
             'returncode_after_stop' not in r,'normal owned outer receipt')
        argv=r['argv'];positions=[i for i,value in enumerate(argv) if resolved(value)==ROOT/'tests'/script]
        need(len(positions)==1 and tuple(argv[1:positions[0]]) in (('-B','-X','utf8'),('-B','-Xutf8')) and
             resolved(argument(argv,'--output'))==directory,'actual selected script/output invocation')
        read(argv[0],'outer executable identity',HOST_PYTHON,False)
        need(len(r['logs'])==2,'both actual outer streams')
        for original,pin in r['logs'].items():
            data=read(original,'outer stream',pin['sha256']);need(len(data)==pin['bytes'],'outer stream bytes')
        return r
    def source_snapshots(directory,table):
        for original,pin in table.items():
            snapshot=(directory/pin['snapshot']).resolve()
            need(snapshot.is_relative_to(directory),'bounded source snapshot')
            data=read(snapshot,'actual frozen source',pin['sha256'])
            need('bytes' not in pin or len(data)==pin['bytes'],'snapshot bytes')
            need(read(original,'unchanged source origin',pin['sha256'])==data,'frozen/current source equality')

    save()
    try:
        read(Path(__file__),'checker source')
        read(ROOT/'.build/cyd-vorbis-format-command-01.py','reviewed outer wrapper',WRAPPER)
        host=directories[0];h=obj(host/'report.json','completed host report')
        outer(args.host_terminal.resolve(),host,'test-vorbis-floor0-numeric.py')
        source_snapshots(host,h['sources'])
        oracle=load(host/'sources/test-vorbis-floor0-numeric.py',HOST_HELPER,'pure_decimal_oracle')
        for filename,pin in (('floor0.c',MODULE['floor0.c']),
                             ('native_vorbis_floor0.h',MODULE['include/native_vorbis_floor0.h']),
                             ('driver.c','1c5ee723cdeb09b3c6db5b66e3aafac75f830353cf7b8b5d333357403141f4d5')):
            read(host/'sources'/filename,'audited whole host source/header/adapter',pin)
        supervisor_owner=read(host/'sources/owned-supervisor-source.py','audited supervisor owner',
                             'df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2')
        literals=[node for node in ast.parse(supervisor_owner).body if isinstance(node,ast.Assign) and
                  any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(literals)==1 and read(host/'supervisor.py','actual nonce supervisor')==
             ast.literal_eval(literals[0].value).encode('utf-8'),'actual reviewed supervisor literal bytes')
        need(h['completed'] is True and h['passed'] is True and h['prepared'] is True and
             h['component_executed'] is True and h['source_inputs_unchanged'] is True and
             h['result']=='FINITE_FLOOR0_NUMERIC_QUALIFIED' and h['policy']==oracle.POLICY and
             (h['cases'],h['target_cases'],h['historical_calls'],h['historical_scalar_bins'])==(60541,327,168,58368) and
             h['numerical']['measurement_completed'] is True and h['numerical']['passed'] is True and
             not h['numerical']['failures'] and not h['numerical']['nonmeasurement_errors'] and
             all(h[key] is False for key in ('decoder_executed','SDK_or_QEMU_executed','full_G6_qualified','physical_device')),
             'retained complete passing host scope')
        need(tuple(row['name'] for row in h['commands'])==('compiler-version','compiler-machine','compile','execute'),
             'four actual host owned commands')
        for command in h['commands']:
            name=command['name'];request=obj(host/(name+'.request.json'),'host owned request')
            receipt=obj(host/(name+'.receipt.json'),'host owned receipt')
            need(command['supervisor']==receipt and request['argv']==command['child_argv'] and request['timeout']==60 and
                 request['nonce']==command['nonce']==receipt['nonce'] and
                 receipt['request_sha256']==sha(read(host/(name+'.request.json'),'host request binding')) and
                 all(receipt[key] is True for key in ('final','new_session','child_reaped','group_gone')) and
                 receipt['state']=='terminal' and receipt['child_returncode']==0 and
                 command['transport_returncode']==0 and not command.get('forced_transport_stop') and
                 'cleanup_error' not in receipt and type(receipt['child_pid']) is int and receipt['child_pid']>0,
                 'actual host child terminal and owned cleanup')
            for stream in ('stdout','stderr'):
                data=read(host/(name+'.'+stream+'.log'),'host actual child stream',command[stream+'_sha256'])
                if name in ('compile','execute'):need(not data,'strict clean host compile/sanitizer run')
        flags=h['commands'][2]['child_argv']
        need(all(flag in flags for flag in ('-Wall','-Wextra','-Werror','-fno-fast-math',
             '-ffp-contract=off','-fsanitize=address,undefined','-fno-sanitize-recover=all')),
             'actual strict sanitized binary64 host compile')
        read(host/'inputs.bin','complete host binary inputs',h['input_sha256'])
        read(host/'outputs.bin','complete host binary outputs',h['output_sha256'])
        data={name:read(host/'target-cases'/name,'predeclared target data',pin) for name,pin in DATA.items()}
        need(h['target_input_sha256']==DATA,'same original three host target files')
        model,expected=json.loads(data['cases.json']),json.loads(data['expected.json'])
        need(expected==dict(schema='native-vorbis-floor0-expected-v1',policy=oracle.POLICY,
                            cases=[oracle.oracle_case(row) for row in model['cases']]),
             'every independent Decimal expected value regenerated before target comparison')
        report['host']=dict(report_sha256=sha(read(host/'report.json','host report pin')),
            accepted=True,numerical=h['numerical'],scope='Recorded audited host campaign, exact inputs/outputs/receipts rebound; no fresh C execution.')
        report['policy']=oracle.POLICY
        for target,directory,terminal in (('esp32',directories[1],args.esp32_terminal),
                                          ('esp32c3',directories[2],args.esp32c3_terminal)):
            r=obj(directory/'report.json','completed '+target+' capture')
            receipt=outer(terminal.resolve(),directory,'run-vorbis-floor0-numeric-qemu.py')
            need(r['completed'] is True and r['math_capture_completed'] is True and
                 r['whole_module_compiled'] is True and r['source_inputs_unchanged'] is True and
                 r['result']=='CHECKED_MATH_CAPTURED' and r['target']==target and
                 all(r[key] is False for key in ('passed','numerical_reference_compared','numerical_qualified',
                     'full_floor0_qualified','decoder_executed','production_firmware','physical_device')),
                 'complete finite native capture, no preclaimed numerical/PCM acceptance')
            source_snapshots(directory,r['inputs'])
            reader=load(directory/'sources/controller.py',TARGET_HELPER,'pure_'+target+'_protocol')
            for name,pin in MODULE.items():
                read(directory/'sources/components/native_vorbis_numeric'/name,'exact native module source',pin)
                read(ROOT/'idf/components/native_vorbis_numeric'/name,'same canonical module source',pin)
            need(r['source_sha256']['source']==MODULE['floor0.c'] and
                 r['source_sha256']['header']==MODULE['include/native_vorbis_floor0.h'] and
                 r['source_sha256']['component']==MODULE['CMakeLists.txt'] and
                 r['source_sha256']['cases']==DATA['cases.json'] and r['source_sha256']['cases-header']==DATA['cases.h'],
                 'current canonical module/header/component and unchanged data pins')
            for name in ('cases.json','cases.h'):
                need(read(directory/'sources/cases'/name,'actual native data',DATA[name])==data[name],'native/host data equality')
            cases=reader.validate_cases(model,data['cases.h'].decode('ascii'))
            need(len(cases)==327 and tuple(row['name'] for row in r['commands'])==NATIVE_COMMANDS,
                 'whole original native327/nine-command scope')
            logs={}
            for command in r['commands']:
                need(command['state']=='complete' and type(command['exit_status']) is int and command['exit_status']==0 and
                     type(command['pid']) is int and command['pid']>0 and not command['timed_out'] and
                     not command['interrupted'] and resolved(command['cwd'])==directory,'all native owned normal command terminals')
                for stream in ('stdout','stderr'):
                    logs[(command['name'],stream)]=read(directory/(command['name']+'.'+stream+'.log'),
                        'actual native command stream',command[stream+'_sha256'])
            for name in ('sdk-head','sdk-head-after'):
                need(logs[(name,'stdout')].decode().strip()==reader.SDK_HEAD[target]==r['sdk_revision'],'actual SDK identity')
            for name in ('sdk-clean','sdk-clean-after'):need(not logs[(name,'stdout')].strip(),'SDK tracked tree clean')
            qemu=next(row for row in r['commands'] if row['name']=='qemu');argv=qemu['argv']
            for flag,value in (('-smp','2' if target=='esp32' else '1'),('-display','none'),('-monitor','none'),
                               ('-serial','stdio'),('-nic','none')):
                need(argument(argv,flag)==value,'isolated QEMU argument '+flag)
            need('-snapshot' in argv and '-no-reboot' in argv and Path(argument(argv,'-L')).is_dir(),'explicit ROM/snapshot/no-reboot')
            need(r['tools'][str(Path(argv[0]).resolve())]==r['source_sha256']['qemu'],'actual selected QEMU identity')
            replayed=reader.validate_log((logs[('qemu','stdout')]+b'\n'+logs[('qemu','stderr')]).decode(
                'utf-8',errors='replace'),cases,target,DATA['cases.json'])
            need(replayed.pop('rows')==r['rows'] and replayed==r['observed'],'every actual protocol value/guard/task replay')
            need(r['elf_machine']==(94 if target=='esp32' else 243) and
                 struct.unpack_from('<H',read(directory/'elf-header.bin','actual native ELF header'),18)[0]==r['elf_machine'],
                 'native ILP32 ELF architecture')
            for relative,pin in r['build_outputs'].items():
                body=not (Path(relative).suffix in ('.elf','.bin') and Path(relative).name!='elf-header.bin')
                read(directory/relative,'retained native build evidence',pin,body)
            for original,pin in r['tools'].items():read(original,'historical native tool identity',pin,False)
            argv=receipt['argv']
            need(resolved(argument(argv,'--cases'))==host/'target-cases' and
                 argument(argv,'--source-sha256')==MODULE['floor0.c'] and
                 argument(argv,'--header-sha256')==MODULE['include/native_vorbis_floor0.h'] and
                 argument(argv,'--component-sha256')==MODULE['CMakeLists.txt'] and
                 argument(argv,'--cases-sha256')==DATA['cases.json'] and
                 argument(argv,'--cases-header-sha256')==DATA['cases.h'],'actual reviewed native invocation data/source pins')
            measured=oracle.compare_target_rows(model,expected,r['rows'])
            report['targets'][target]=dict(measured,cases=len(cases),report_sha256=sha(read(directory/'report.json','native report pin')),
                outer_receipt_sha256=sha(read(terminal,'native outer receipt pin')),observed=replayed,
                stack_usage=r['stack_usage'],scope='Finite exact coefficient/gain core; no full angle path, synthesis, PCM or radio qualification.')
        for original,pin in list(report['inputs'].items()):
            read(original,'final consumed input identity',pin['sha256'],body='snapshot' in pin)
            if 'snapshot' in pin:
                need(sha((out/pin['snapshot']).read_bytes())==pin['sha256'],'saved consumed body unchanged')
        completed=all(row['measurement_completed'] for row in report['targets'].values())
        passed=completed and all(row['passed'] for row in report['targets'].values())
        report.update(completed=True,measurement_completed=completed,passed=passed,
            finite_coefficient_numeric_qualified=passed,source_inputs_unchanged=True,
            native_cases_compared=sum(len(row['metrics']) for row in report['targets'].values()),
            native_cases_required=sum(row['cases'] for row in report['targets'].values()),
            result='FINITE_COEFFICIENT_NUMERIC_QUALIFIED' if passed else 'FINITE_COEFFICIENT_NUMERIC_REJECTED')
        save();print(json.dumps({key:report[key] for key in ('completed','measurement_completed','passed',
            'native_cases_compared','finite_coefficient_numeric_qualified','result')}));return 0 if passed else 1
    except BaseException as error:
        report.update(completed=False,passed=False,finite_coefficient_numeric_qualified=False,error=repr(error));save();raise


if __name__=='__main__':
    sys.exit(main())
