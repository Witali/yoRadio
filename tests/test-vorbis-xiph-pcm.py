"""Compare every original31 Xiph PCM sample at the fixed2-S16 bound.

Pure numerical functions are reusable offline. The CLI replays the captured
protocol with a pinned reader and launches no codec, compiler, SDK or process.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import struct
import sys
ROOT=Path(__file__).resolve().parents[1]
EXPORTER=ROOT/'tests/prepare-vorbis-xiph.py'
EXPORTER_SHA='04507fa0ab9425e6f77b3c268b4ddfd5b3ac4af35c1d27dd438157f246d8acb6'
CONTROLLER=ROOT/'tests/run-vorbis-xiph-qemu.py'
CONTROLLER_SHA='837847878b19e352db8188b6927a3b3a91449bee74be9b59e93a9a110066c1d9'
MODEL_SHA='a12fcb6fea905027f9af4b1d1e5b5b561fa447f457d236cd5d004fd948b07883'
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(body):return hashlib.sha256(body).hexdigest()
def receipt_basename(value):
    need(type(value)is str and re.fullmatch(r'[A-Za-z0-9_-]{1,63}',value)is not None,'safe native receipt basename without extension');return value
def module(path,name,pin):
    need(sha(path.read_bytes())==pin,'reviewed pure source identity: '+name);spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

def samples(body):
    need(type(body)is bytes and len(body)%4==0,'whole stereo signed16 bytes');return struct.unpack('<'+'h'*(len(body)//2),body)
def errors(reference,target,channel=None):
    need(len(reference)==len(target),'full equal-length numerical comparison');delta=[b-a for a,b in zip(reference,target)];n=len(delta);first=next((i for i,d in enumerate(delta)if d),None)
    return dict(samples=n,different_samples=sum(d!=0 for d in delta),max_abs_error=max(map(abs,delta),default=0),min_signed_error=min(delta,default=0),max_signed_error=max(delta,default=0),sum_signed_error=sum(delta),sum_squared_error=sum(d*d for d in delta),rms_error=math.sqrt(sum(d*d for d in delta)/n)if n else 0,reference_nonzero_samples=sum(a!=0 for a in reference),target_nonzero_samples=sum(b!=0 for b in target),reference_clipped_samples=sum(a in(-32768,32767)for a in reference),target_clipped_samples=sum(b in(-32768,32767)for b in target),first_mismatch=None if first is None else dict(sample=first,frame=first//2 if channel is None else first,channel=first%2 if channel is None else channel,reference=reference[first],target=target[first],signed_error=delta[first]),signed_error_histogram={str(k):v for k,v in sorted(Counter(delta).items())})
def transitions(case,pcm):
    values=samples(pcm);result={name:[0,0]for name in('SS','SL','LS','LL')};offset=0
    for i,frames in enumerate(case['frames']):
        if i:
            name='SL'[case['modes'][i-1]]+'SL'[case['modes'][i]]
            for ch in(0,1):result[name][ch]+=sum(values[2*(offset+j)+ch]!=0 for j in range(frames))
        offset+=frames
    need(offset*4==len(pcm),'complete original transition coverage');return result

def compare_rows(model,rows,references):
    cases=model['cases'];need(len(cases)==len(rows)==31 and set(references)=={c['id']for c in cases},'every original31 case required');results=[];failures=[];target_pcm={};reference_pcm={};compared=0;packets_compared=0;sample_count=0
    for i,(case,row)in enumerate(zip(cases,rows)):
        try:
            need(row['case']==i and row['id']==case['id']and row['guards']==row['unchanged']==1,'actual ordered guarded case identity');need(type(row['pcm_hex'])is str,'complete PCM byte capture');actual=bytes.fromhex(row['pcm_hex']);reference=references[case['id']];need(sha(reference)==case['reference_pcm_sha256']and len(reference)==case['pcm_bytes'],'unchanged qualified reference PCM');target_pcm[case['id']]=actual;reference_pcm[case['id']]=reference;reasons=[]
            if row['header_statuses']!=[0,0,0]or row['synthesis_init_status']!=0 or row['block_init_status']!=0 or row['api_ok']is not True:reasons.append('public header/synthesis API status')
            if row['info']!=dict(rate=case['rate'],channels=case['channels'],short_block=case['short_block'],long_block=case['long_block']):reasons.append('persistent original stream metadata')
            need(len(row['packets'])==14,'all original packet slots retained');joined=bytearray();packet_results=[];offset=0
            for index,(packet,frames)in enumerate(zip(row['packets'],case['frames'])):
                need(packet['packet']==index and packet['granule']==case['granules'][index]and packet['eos']==int(index==13),'original packet index/granule/EOS identity');body=bytes.fromhex(packet['pcm_hex']);joined+=body;part_ref=reference[offset:offset+frames*4];offset+=frames*4
                packet_reasons=[]
                if packet['synthesis_status']!=0 or packet['blockin_status']!=0 or packet['read_status']!=(0 if packet['frames'] else -99):packet_reasons.append('public packet API status')
                if packet['frames']!=frames or len(body)!=frames*4:packet_reasons.append('original untrimmed packet frame count')
                metric=errors(samples(part_ref),samples(body))if len(body)==len(part_ref)else None
                if metric is not None:packets_compared+=1
                packet_results.append(dict(packet=index,expected_frames=frames,actual_frames=packet['frames'],bytes=len(body),comparison=metric,failure_reasons=packet_reasons));reasons+=['packet '+str(index)+': '+why for why in packet_reasons]
            need(bytes(joined)==actual,'stream PCM equals every ordered packet byte');complete=len(actual)==len(reference)and row['pcm_bytes']==case['pcm_bytes']and row['frames']==sum(case['frames']);whole=None;channels=[];reference_transitions=transitions(case,reference);actual_transitions=None
            if not complete:reasons.append('whole original PCM frame/byte count')
            else:
                aa,bb=samples(reference),samples(actual);whole=errors(aa,bb);channels=[errors(aa[ch::2],bb[ch::2],ch)for ch in(0,1)];actual_transitions=transitions(case,actual);compared+=1;sample_count+=len(aa)
                if whole['max_abs_error']>2:reasons.append('fixed2-S16 error bound')
                if any(ch['reference_nonzero_samples']==0 or ch['target_nonzero_samples']==0 for ch in channels):reasons.append('both original channels must be nonzero')
                if any(not count for table in(reference_transitions,actual_transitions)for pair in table.values()for count in pair):reasons.append('both original channels must be nonzero in every transition')
            measured=dict(case=i,id=case['id'],measurement_completed=complete,passed=not reasons,failure_reasons=reasons,reference_sha256=sha(reference),target_sha256=sha(actual),reference_pcm_bytes=len(reference),target_pcm_bytes=len(actual),zero_lag_direct_LR=whole,channels=channels,packets=packet_results,reference_transition_channel_nonzero=reference_transitions,target_transition_channel_nonzero=actual_transitions)
            results.append(measured)
            if reasons:failures.append(dict(case=i,id=case['id'],reasons=reasons))
        except(ValueError,KeyError,TypeError,struct.error)as error:results.append(dict(case=i,id=case['id'],measurement_completed=False,passed=False,nonmeasurement_error=str(error),actual=row));failures.append(dict(case=i,id=case['id'],nonmeasurement_error=str(error)))
    relation_results={}
    for name,values in(('reference',reference_pcm),('target',target_pcm)):
        relations=[]
        for relation in model['relations']:
            ids=relation['cases'];available=all(key in values and len(values[key])==next(c['pcm_bytes']for c in cases if c['id']==key)for key in ids);equal=available and all(values[key]==values[ids[0]]for key in ids[1:]);passed=available and(equal if relation['kind']=='equal'else not equal);relations.append(dict(kind=relation['kind'],cases=ids,measurement_completed=available,observed_byte_equal=equal,passed=passed))
        relation_results[name]=relations
        if not all(row['passed']for row in relations):failures.append(dict(scope=name,reasons=['original14 exact relations']))
    complete=compared==31 and packets_compared==434 and sample_count==738560//2
    return dict(measurement_completed=complete,passed=complete and not failures,policy=model['policy'],cases=results,failures=failures,relations=relation_results,cases_compared=compared,packets_compared=packets_compared,samples_compared=sample_count,required_cases=31,required_packets=434,required_samples=738560//2,max_abs_error_allowed=2,alignment_adjusted=False,gain_fitted=False,subset_used=False,full_standard_conformance=False,production_radio_integration=False,physical_device=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('prepared','capture','receipts','output'):parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--native-receipt',type=receipt_basename,default='esp32')
    args=parser.parse_args();out=args.output.resolve();need(out.is_relative_to(ROOT/'.build')and out!=ROOT/'.build'and not out.exists(),'fresh task-local comparison output');out.mkdir(parents=True);(out/'inputs').mkdir();ledger={}
    def read(path,pin=None):
        path=path.resolve();need(path.is_relative_to(ROOT),'task input boundary');body=path.read_bytes();digest=sha(body);need(pin is None or digest==pin,'consumed input hash: '+str(path));name='inputs/'+digest
        if not(out/name).exists():(out/name).write_bytes(body)
        entry=dict(sha256=digest,bytes=len(body),snapshot=name);need(str(path)not in ledger or ledger[str(path)]==entry,'one consumed source identity');ledger[str(path)]=entry;return body
    report=dict(completed=False,passed=False,native_receipt=args.native_receipt,codec_or_compiler_or_SDK_executed=False,inputs=ledger,identity_only={},full_standard_conformance=False,full_G6_qualified=False,production_radio_integration=False,physical_device=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def identity(path):
        path=Path(path).resolve();body=path.read_bytes();pin=dict(sha256=sha(body),bytes=len(body),reason='Executable identity only; external binary body omitted.');previous=report['identity_only'].get(str(path));need(previous is None or previous==pin,'executable identity remains unchanged');report['identity_only'][str(path)]=pin;return pin['sha256']
    def terminal(name,directory,script,pins=None):
        receipt=json.loads(read(args.receipts/(name+'.json')));argv=receipt['argv'];cwd=Path(receipt['cwd']).resolve()
        need(receipt['status']=='TERMINAL'and type(receipt['returncode'])is int and receipt['returncode']==0 and type(receipt['owned_pid'])is int and receipt['owned_pid']>0 and not receipt.get('timed_out')and not receipt.get('interrupted')and not any(key in receipt for key in('error_type','returncode_after_stop')),'actual successful owned outer terminal '+name)
        need(cwd==ROOT and argv[1:4]==['-B','-X','utf8']and Path(argv[0]).resolve()==Path(sys.executable).resolve()and(cwd/argv[4]).resolve()==ROOT/'tests'/script,'actual executable/script/cwd')
        need(receipt['runner_sha256']==sha(read(ROOT/'.build/cyd-vorbis-format-command-01.py'))=='33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e'and receipt['executable_sha256']==identity(sys.executable)=='4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a','owned runner/Python identities')
        def option(key):
            flag='--'+key;need(argv.count(flag)==1 and argv.index(flag)+1<len(argv),'unique complete actual option '+key);return argv[argv.index(flag)+1]
        need((cwd/option('output')).resolve()==directory,'terminal belongs to supplied campaign')
        if name=='prepare':need(len(argv)==7 and argv[5]=='--output','exact source-only export invocation')
        else:
            need(option('target')=='esp32'and(cwd/option('cases')).resolve()==args.prepared.resolve(),'actual full31 native target/cases')
            for key,value in pins.items():need(option(key+'-sha256')==value,'actual explicit data/source/tool pin '+key)
        need({Path(path).resolve()for path in receipt['logs']}=={args.receipts.resolve()/(name+'.'+stem+'.log')for stem in('stdout','stderr')},'exact outer stream inventory')
        for path,pin in receipt['logs'].items():need(len(read(Path(path),pin['sha256']))==pin['bytes'],'actual outer terminal bytes')
    save()
    try:
        read(Path(__file__));read(EXPORTER,EXPORTER_SHA);read(CONTROLLER,CONTROLLER_SHA);exporter=module(EXPORTER,'owned_xiph_exporter',EXPORTER_SHA);controller=module(CONTROLLER,'owned_xiph_protocol',CONTROLLER_SHA);prepared=args.prepared.resolve();capture=args.capture.resolve();terminal('prepare',prepared,'prepare-vorbis-xiph.py');pre=json.loads(read(prepared/'report.json'));need(pre['completed']is True and pre['prepared']is True and pre['codec_or_compiler_or_SDK_executed']is False,'actual preparation-only result');model=json.loads(read(prepared/'cases.json',pre['files']['cases.json']));exporter.validate_model(model);need(sha(exporter.canonical(model))==pre['model_sha256'],'fixed original model identity');header=read(prepared/'cases.h',pre['files']['cases.h']);need(header==exporter.target_header(model).encode('ascii'),'complete exact C header readback')
        need(sha(exporter.canonical(model))==MODEL_SHA and json.loads(read(args.receipts/'prepare.stdout.log'))==pre,'exact prepared original model and actual exporter output')
        for path,pin in pre['inputs'].items():need(read(Path(path),pin['sha256'])==read(prepared/pin['snapshot'],pin['sha256']),'all historical source bodies and snapshots remain unchanged')
        references={case['id']:read(prepared/case['reference_path'],case['reference_pcm_sha256'])for case in model['cases']}
        captured=json.loads(read(capture/'report.json'));pins=captured['source_sha256'];terminal(args.native_receipt,capture,'run-vorbis-xiph-qemu.py',pins)
        need(captured['target']=='esp32'and captured['result']=='CHECKED_XIPH_CAPTURED'and all(captured[key]is True for key in('completed','capture_completed','math_capture_completed','whole_module_compiled','source_inputs_unchanged'))and all(captured[key]is False for key in('passed','numerical_reference_compared','numerical_qualified','full_decoder_qualified','production_firmware','production_radio_integration','physical_device')),'actual full31 upstream capture and limited scope')
        need(set(pins)=={'component-manifest','cases','cases-header','qemu'}and pins['cases']==pre['files']['cases.json']and pins['cases-header']==pre['files']['cases.h'],'same original complete31 input pins')
        for path,pin in captured['inputs'].items():
            snapshot=(capture/pin['snapshot']).resolve();need(snapshot.is_relative_to(capture),'contained native source snapshot');body=read(snapshot,pin['sha256']);need(body==read(Path(path),pin['sha256'])and len(body)==pin['bytes'],'same original/frozen native source')
        need(read(capture/'sources/controller.py')==read(CONTROLLER,CONTROLLER_SHA)and read(capture/'sources/cases/cases.json')==read(prepared/'cases.json')and read(capture/'sources/cases/cases.h')==header,'executed controller and original raw data bodies')
        component=capture/'sources/components/native_vorbis_xiph';manifest=controller.validate_manifest(json.loads(read(component/'component-manifest.json',pins['component-manifest'])))
        for name,digest in manifest['files'].items():need(read(component/name,digest)==read(ROOT/'idf/components/native_vorbis_xiph'/name,digest),'unchanged complete upstream source/config '+name)
        need(captured['component_compile_sources']==manifest['compile_sources']and set(captured['compile_rows'])=={'fixture',*manifest['compile_sources']},'all twenty-two upstream translation units plus fixture')
        commands=captured['commands'];need([row['name']for row in commands]==['sdk-head','sdk-clean','build','dependencies','symbols','merge','qemu','sdk-head-after','sdk-clean-after'],'nine actual owned native commands')
        for command in commands:
            need(command['state']=='complete'and type(command['exit_status'])is int and command['exit_status']==0 and type(command['pid'])is int and command['pid']>0 and not command['timed_out']and not command['interrupted']and not any(key in command for key in('tree_stop_returncode','tree_stop_error')),'actual normal SDK/QEMU command terminal')
            for stem in('stdout','stderr'):read(capture/(command['name']+'.'+stem+'.log'),command[stem+'_sha256'])
        need(captured['sdk_revision']==controller.SDK_HEAD['esp32']and (read(capture/'sdk-head.stdout.log').decode().strip()==read(capture/'sdk-head-after.stdout.log').decode().strip()==captured['sdk_revision'])and not read(capture/'sdk-clean.stdout.log').strip()and not read(capture/'sdk-clean-after.stdout.log').strip(),'actual clean pinned SDK before/after')
        child=json.loads(read(capture/'sdk-child.json'));need(child==captured['sdk_child']and type(child['pid'])is int and child['pid']>0 and child['exit_status']==0,'actual SDK child terminal')
        for path,digest in captured['build_outputs'].items():
            file=(capture/path).resolve();need(file.is_relative_to(capture),'contained actual build output');read(file,digest)
        elf=read(capture/'elf-header.bin');need(len(elf)==52 and elf[:7]==b'\x7fELF\x01\x01\x01'and struct.unpack_from('<H',elf,18)[0]==captured['elf_machine']==94,'actual ELF32 little-endian Xtensa header')
        database=json.loads(read(capture/'build/compile_commands.json'))
        for key,row in captured['compile_rows'].items():need(row in database and all(flag in row['command']for flag in('-fno-fast-math','-ffp-contract=off','-fstack-usage')),'actual complete source compile recipe '+key)
        for path,digest in captured['tools'].items():need(identity(path)==digest,'recorded actual tool identity')
        qemu=next(row for row in commands if row['name']=='qemu');need(captured['tools'][qemu['argv'][0]]==pins['qemu'],'actual selected QEMU identity');qargs=qemu['argv']
        for flag,value in(('-M','esp32,audiodev=quiet'),('-smp','2'),('-nic','none'),('-display','none'),('-monitor','none'),('-serial','stdio')):need(qargs.count(flag)==1 and qargs[qargs.index(flag)+1]==value,'actual isolated QEMU profile '+flag)
        need(qargs.count('-L')==1 and '-no-reboot'in qargs and '-snapshot'in qargs,'explicit ROM and finite isolated QEMU execution')
        source_rows=controller.validate_cases(model,header.decode('ascii'));rawlog=read(capture/'qemu.stdout.log').decode('utf-8',errors='replace')+'\n'+read(capture/'qemu.stderr.log').decode('utf-8',errors='replace');replayed=controller.validate_log(rawlog,source_rows,'esp32',pins['cases'],pins['component-manifest']);rows=replayed.pop('rows');need(rows==captured['rows']and replayed==captured['observed'],'all actual ordered public API/PCM/guard/resource events replayed')
        for row in rows:need(read(capture/'pcm'/('%02d-'%row['case']+row['id']+'.s16le'))==bytes.fromhex(row['pcm_hex']),'saved PCM equals every actual capture byte')
        measured=compare_rows(model,rows,references)
        need(all(sha(Path(path).read_bytes())==pin['sha256']and sha((out/pin['snapshot']).read_bytes())==pin['sha256']for path,pin in ledger.items()),'every consumed source/input unchanged');report.update(completed=measured['measurement_completed'],passed=measured['passed'],comparison=measured,source_inputs_unchanged=True,result='BOUNDED_ORIGINAL31_PCM_QUALIFIED'if measured['passed']else'BOUNDED_ORIGINAL31_PCM_REJECTED');save();print(json.dumps(dict(completed=report['completed'],passed=report['passed'],result=report['result'],cases_compared=measured['cases_compared'],packets_compared=measured['packets_compared'],samples_compared=measured['samples_compared'])));return 0 if report['passed']else 1
    except BaseException as error:report.update(completed=False,passed=False,error=repr(error));save();raise
if __name__=='__main__':sys.exit(main())
