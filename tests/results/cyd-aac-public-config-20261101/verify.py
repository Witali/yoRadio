"""Verify saved public AAC evidence without running archived code or native tools."""
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]


def need(value,why):
    if not value: raise ValueError(why)


def sha(body): return hashlib.sha256(body).hexdigest()


def main():
    manifest=json.loads((FOLDER/'manifest.json').read_bytes())
    pin=manifest['archive'];archive=FOLDER/pin['path']
    need(archive.name=='captures.zip' and sha(archive.read_bytes())==pin['sha256'] and archive.stat().st_size==pin['bytes'], 'exact evidence archive')
    rows=manifest['files']
    need(len({r['path'] for r in rows})==len(rows)==manifest['logical_files'],'unique logical inventory')
    blobs={}
    with zipfile.ZipFile(archive) as z:
        need(len(z.infolist())==manifest['physical_blobs']==len({r['blob'] for r in rows}),'exact physical blob census')
        for entry in z.infolist():
            need(re.fullmatch(r'blobs/[a-f0-9]{64}',entry.filename),'canonical blob name')
            body=z.read(entry)
            need(entry.filename=='blobs/'+sha(body),'all published physical bytes')
            need(not body.startswith((b'\x7fELF',b'MZ',b'!<arch>\n')),'no executable/archive image payload')
            blobs[entry.filename]=body
    data={}
    for row in rows:
        name=PurePosixPath(row['path']);body=blobs[row['blob']]
        need(not name.is_absolute() and '..' not in name.parts and name.as_posix()==row['path'],'contained logical path')
        need(len(body)==row['bytes'] and sha(body)==row['sha256'],'all logical byte bindings')
        data[row['path']]=body
    omitted=manifest['omitted_local_files']
    need(all(name not in data and row['byte_payload_published'] is False and row['original_retained_locally'] and
             re.fullmatch(r'[a-f0-9]{64}',row['sha256']) and row['bytes']>0 for name,row in omitted.items()),'explicit omitted local payload identities')

    def take(name):
        need(name in data,'required unchanged published file: '+name)
        return data[name]

    def identity(name,digest,size=None):
        if name in data:
            need(sha(data[name])==digest and (size is None or len(data[name])==size),'published source/artifact identity')
        else:
            need(name in omitted and omitted[name]['sha256']==digest and (size is None or omitted[name]['bytes']==size), 'omitted identity; bytes not re-read')

    for name,digest in manifest['canonical_source_sha256'].items():
        need(sha((ROOT/name).read_bytes())==digest,'unchanged reviewed canonical source: '+name)
    controller=ROOT/'tests/run-cyd-aac-public-config-qemu.py'
    spec=importlib.util.spec_from_file_location('reviewed_public_aac_reader',controller)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    # Only reviewed current data readers run. No archived source is imported.
    report=json.loads(take('native02/report.json'))
    need(report['passed'] and report['completed'] and report['target_executed'] and report['all_bound_inputs_current'] and
         report['private_abi_used'] is False and report['compact_owner_ported'] is False,'actual native successful scope')
    need(sha(take('native02/report.json'))==manifest['native_report_sha256'],'original native report bytes')
    for name in ('native01','native02'):
        native=json.loads(take(name+'/report.json'))
        for original,pin in native['inputs'].items(): identity(name+'/'+pin['snapshot'],pin['sha256'],pin['bytes'])
        for item,digest in native.get('build_outputs',{}).items(): identity(name+'/'+item,digest)
        for command in native['commands']:
            for stream in ('stdout','stderr'):
                need(sha(take(name+'/'+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],'original native process log identity')
        child=json.loads(take(name+'/sdk-child.json'))
        need(child['pid']>0 and child['exit_status']==(0 if name=='native02' else 2),'actual SDK child terminal status')
    need(all(c['state']=='complete' and c['pid']>0 and c['exit_status']==0 for c in report['commands']),'all authoritative native commands terminal zero')
    need(report['commands'][-1]['name']=='qemu' and '-snapshot' in report['commands'][-1]['argv'] and
         report['commands'][-1]['argv'][report['commands'][-1]['argv'].index('-nic')+1]=='none','actual network-free nonpersistent QEMU invocation')
    need(report['tools']['qemu']['sha256']=='4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d','pinned LX6 emulator')
    need(any(c['name']=='build' and c['exit_status']!=0 for c in json.loads(take('native01/report.json'))['commands']) and
         not json.loads(take('native01/report.json'))['target_executed'],'original compiler-format failure remains nonpassing before QEMU')
    closure=json.loads(take('native02/actual-compiler-closure.json'))
    need(len(closure['translation_units'])==report['actual_translation_units']==5 and
         len(closure['dependencies'])==report['actual_compiler_dependencies']==203,'actual selected GCC source/dependency census')
    original_commands=json.loads(take('native02/build/compile_commands.json'))
    for tu in closure['translation_units']:
        need(sum(all(row.get(k)==v for k,v in original.items()) for row in [tu] for original in original_commands)==1,'selected TU joins actual compiler command')
        need(set(tu['actual_dependency_paths'])<=set(closure['dependencies']),'TU actual dependency paths exist')
        need('/project/' in tu['file'].replace('\\','/') or '/sources/vendor/' in tu['file'].replace('\\','/'),'actual frozen source selected')
    main=next(tu for tu in closure['translation_units'] if Path(tu['file']).name=='main.c')
    need(any(Path(path).name=='aac_public_config.h' for path in main['actual_dependency_paths']),'actual GCC consumes production public configuration header')
    entries=reader.fixture_accounting()
    need(entries==report['fixtures']==manifest['fixtures'],'full original ADTS byte/frame accounting')
    measured=reader.validate_log(take('native02/qemu.stdout.log').decode('utf-8')+'\n'+take('native02/qemu.stderr.log').decode('utf-8'),entries)
    need(measured==report['measurements']==manifest['measurements'],'all36 actual complete PCM/rate/layout and scoped config observations')
    log=take('native02/qemu.stdout.log').decode('utf-8')
    mutations=[log.replace('scope_returned=1','scope_returned=0',1),
               log.replace('overwritten_plus=1','overwritten_plus=0',1),
               log.replace('rate=44100 channels=2 bits=16 samples=28672','rate=22050 channels=2 bits=16 samples=28672',1),
               log.replace('cases=36 core=1 registry_before','cases=35 core=1 registry_before',1),
               '\n'.join(line for line in log.splitlines() if not line.startswith('AAC_PUBLIC_OPEN instance=36 ')),
               log+'\nGuru Meditation\n']
    for bad in mutations:
        need(bad!=log,'contradictory control modifies original transcript')
        try: reader.validate_log(bad,entries)
        except ValueError: pass
        else: raise ValueError('contradictory observed transcript accepted')
    for name in ('kconfig01','kconfig02','integration01','integration02'):
        saved=json.loads(take(name+'/report.json'))
        for original,pin in saved['sources'].items(): identity(name+'/'+pin['snapshot'],pin['sha256'],pin['bytes'])
        need(saved['passed']==name.endswith('02'),'original host/compile nonpasses remain distinct')
    host=json.loads(take('kconfig02/report.json'))
    need(len(host['cases'])==8 and host['all_source_bindings_current'] and all(r['passed'] for r in host['cases']),'eight actual Kconfig rules')
    integration=json.loads(take('integration02/report.json'))
    need(sha(take('integration02/report.json'))==manifest['integration_report_sha256'] and integration['all_source_bindings_current'],'original successful production-TU report')
    need({(r['backend'],r['aac_plus']) for r in integration['profiles']}=={(b,on) for b in ('pdm','continuous','legacy') for on in (False,True)},'six actual production-TU variants')
    need(len(integration['commands'])==12 and all(c['state']=='complete' and c['pid']>0 and c['exit_status']==0 for c in integration['commands']),'all actual preprocess/compile commands terminal zero')
    for command in integration['commands']:
        for stream in ('stdout','stderr'):
            pin=command[stream];need(sha(take('integration02/'+pin['path']))==pin['sha256'],'actual production compile log identity')
    for row in integration['profiles']:
        identity('integration02/'+row['object']['path'],row['object']['sha256'],row['object']['bytes'])
        need(sha(take('integration02/'+row['stack_usage']['path']))==row['stack_usage']['sha256'],'actual stack-usage records')
        need(row['source_sha256']==manifest['compiled_current_audio_service_sha256'],'all six compile the same current integration source')
    print(json.dumps(dict(passed=True,native_cases=36,kconfig_cases=8,production_TU_profiles=6,
        rejected_transcript_controls=len(mutations),logical_files=len(data),omitted_local_files=len(omitted),
        compact_owner_ported=False,native_production_pipeline_executed=False,omitted_binary_bytes_read=False)))


if __name__=='__main__':main()
