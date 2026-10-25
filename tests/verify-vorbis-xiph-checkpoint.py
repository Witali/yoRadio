"""Replay saved Xiph packet records and independently recompute all S16 errors.

Reads the checkpoint ZIP without extraction. Launches no SDK, compiler, codec,
QEMU or external process. Only the hash-pinned owned pure protocol is reused.
"""
import argparse,hashlib,io,json,struct,tarfile,types,zipfile
from pathlib import Path,PurePosixPath
CONTROLLER='837847878b19e352db8188b6927a3b3a91449bee74be9b59e93a9a110066c1d9'
MANIFEST='897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14'
MODEL='a12fcb6fea905027f9af4b1d1e5b5b561fa447f457d236cd5d004fd948b07883'
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def verify(path):
    with zipfile.ZipFile(path)as archive:
        names=archive.namelist();need(len(names)==len(set(names)),'unique archive members')
        need(all(not PurePosixPath(n).is_absolute()and '..'not in PurePosixPath(n).parts and ':'not in n and '\\'not in n for n in names),'relative archive members')
        manifest=json.loads(archive.read('manifest.json'));need(manifest['schema']=='vorbis-xiph-checkpoint-v1'and set(names)==set(manifest['files'])|{'manifest.json'},'exact complete archive inventory')
        for name,pin in manifest['files'].items():
            body=archive.read(name);need(len(body)==pin['bytes']and sha(body)==pin['sha256'],'archived bytes '+name)
        read=archive.read
        native=json.loads(read('native/report.json'));model=json.loads(read('prepared/cases.json'));comp=json.loads(read('comparison/report.json'))
        need(sha(json.dumps(model,sort_keys=True,separators=(',',':')).encode())==MODEL,'unchanged original31 model')
        need(native['completed']and native['capture_completed']and native['whole_module_compiled']and native['source_inputs_unchanged'],'complete native capture')
        for name in ('prepare','esp32-final','protocol','pcm-units-retry','comparison'):
            terminal=json.loads(read('receipts/'+name+'.json'));need(terminal['status']=='TERMINAL'and type(terminal['returncode'])is int and terminal['returncode']==0,'actual outer terminal '+name)
            for old,pin in terminal['logs'].items():need(sha(read('receipts/'+old.replace('\\','/').rsplit('/',1)[-1]))==pin['sha256'],'actual outer stream '+name)
        for command in native['commands']:
            need(command['state']=='complete'and command['exit_status']==0 and not command['timed_out']and not command['interrupted'],'actual owned native command')
            for stream in ('stdout','stderr'):need(sha(read('native/'+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],'actual native stream')
        for name,digest in native['build_outputs'].items():need(sha(read('native/'+name))==digest,'selected actual build output '+name)
        base='native/sources/components/native_vorbis_xiph/'
        raw=read(base+'component-manifest.json');need(sha(raw)==MANIFEST,'unchanged complete Xiph component')
        source_manifest=json.loads(raw)
        for name,digest in source_manifest['files'].items():need(sha(read(base+name))==digest,'complete component file '+name)
        provenance=json.loads(read(base+'SOURCE.json'))
        for source in provenance['sources']:
            name,version=source['name'],source['version'];filename=name+'-'+name+'-'+version+'.tar.xz';raw=read('download/'+filename)
            need(sha(raw)==source['archive']['sha256'],'official release archive')
            with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz')as tar:
                for relative,digest in source['files'].items():
                    member=tar.getmember(name+'-'+version+'/'+relative);need(member.isfile(),'regular imported upstream member');body=tar.extractfile(member).read()
                    need(sha(body)==digest and body==read(base+'upstream/'+name+'/'+relative),'unchanged upstream byte copy '+relative)
        raw=read('sources/tests/run-vorbis-xiph-qemu.py');need(sha(raw)==CONTROLLER,'reviewed pure protocol source')
        module=types.ModuleType('owned_saved_xiph_protocol');module.__file__=str(Path(__file__).resolve().parent/'run-vorbis-xiph-qemu.py');exec(compile(raw,module.__file__,'exec'),module.__dict__)
        cases=module.validate_cases(model,read('prepared/cases.h').decode('ascii'))
        log=read('native/qemu.stdout.log').decode('utf-8',errors='replace')+'\n'+read('native/qemu.stderr.log').decode('utf-8',errors='replace')
        replay=module.validate_log(log,cases,'esp32',native['source_sha256']['cases'],MANIFEST);rows=replay.pop('rows');need(rows==native['rows']and replay==native['observed'],'actual complete protocol replay')
        need(len(cases)==len(rows)==len(comp['comparison']['cases'])==31,'all31 saved numerical rows')
        measured=[];targets={};references={};total=packets=0
        for case,row,result in zip(cases,rows,comp['comparison']['cases']):
            reference=read('prepared/'+case['reference_path']);target=bytes.fromhex(row['pcm_hex']);need(sha(reference)==case['reference_pcm_sha256']and len(reference)==len(target)==case['pcm_bytes'],'whole original reference/target PCM')
            need(target==read('native/pcm/'+f"{case['case']:02d}-{case['id']}.s16le"),'saved actual PCM')
            values=lambda b:struct.unpack('<'+'h'*(len(b)//2),b)
            errors=[b-a for a,b in zip(values(reference),values(target))];metric={'samples':len(errors),'max_abs_error':max(map(abs,errors),default=0),'different_samples':sum(e!=0 for e in errors),'sum_signed_error':sum(errors),'sum_squared_error':sum(e*e for e in errors)}
            need(all(result['zero_lag_direct_LR'][k]==v for k,v in metric.items()),'independent direct S16 arithmetic')
            need(metric['max_abs_error']<=2 and result['passed']and row['api_ok'],'unchanged finite case acceptance')
            offset=0
            for packet,frames in zip(row['packets'],case['frames']):
                body=bytes.fromhex(packet['pcm_hex']);need(packet['frames']==frames and body==target[offset:offset+frames*4],'all original packet spans');offset+=frames*4;packets+=1
            need(offset==len(target),'whole packet coverage');total+=len(target);measured.append(metric);targets[case['id']]=target;references[case['id']]=reference
        for collection in (targets,references):
            for relation in model['relations']:
                ids=relation['cases'];equal=all(collection[k]==collection[ids[0]]for k in ids[1:]);need(equal==(relation['kind']=='equal'),'all original exact PCM relations')
        need(len(measured)==31 and packets==434 and total==738560 and len(model['relations'])==14,'whole original31 scope')
        need(comp['completed']and comp['passed']and comp['comparison']['passed']and not comp['physical_device']and not comp['production_radio_integration'],'qualified finite isolated result')
        return {'verified':True,'cases':31,'packets':packets,'pcm_bytes':total,'relations':14,'max_abs_error':max(m['max_abs_error']for m in measured),'physical_device':False,'full_standard_conformance':False}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive',type=Path);args=parser.parse_args();print(json.dumps(verify(args.archive)));return 0
if __name__=='__main__':raise SystemExit(main())
