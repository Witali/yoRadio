"""Verify saved header-gain observations; execute no archived or native code."""
import hashlib
import importlib.util
import json
from pathlib import Path,PurePosixPath
import re
import struct
import zipfile
FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]
def need(value,why):
    if not value:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def main():
    manifest=json.loads((FOLDER/'manifest.json').read_bytes());pin=manifest['archive'];archive=FOLDER/pin['path']
    need(archive.name=='captures.zip' and sha(archive.read_bytes())==pin['sha256'] and archive.stat().st_size==pin['bytes'],'exact public archive bytes')
    rows=manifest['files'];need(len({r['path'] for r in rows})==len(rows)==manifest['logical_files'],'unique logical census')
    blobs={}
    with zipfile.ZipFile(archive) as z:
        need(len(z.infolist())==manifest['physical_blobs']==len({r['blob'] for r in rows}),'exact physical census')
        for row in z.infolist():
            body=z.read(row);need(re.fullmatch(r'blobs/[a-f0-9]{64}',row.filename) and row.filename=='blobs/'+sha(body),'all physical bytes')
            need(not body.startswith((b'\x7fELF',b'MZ',b'!<arch>\n')),'no executable or static-library payload')
            blobs[row.filename]=body
    data={}
    for row in rows:
        name=PurePosixPath(row['path']);body=blobs[row['blob']]
        need(not name.is_absolute() and '..' not in name.parts and name.as_posix()==row['path'],'contained logical paths')
        need(sha(body)==row['sha256'] and len(body)==row['bytes'],'all logical byte identities');data[row['path']]=body
    omitted=manifest['omitted_local_files']
    need(all(name not in data and row['original_retained_locally'] and row['byte_payload_published'] is False and
             re.fullmatch(r'[a-f0-9]{64}',row['sha256']) and row['bytes']>0 for name,row in omitted.items()),'explicit local omission identities')
    def take(name):
        need(name in data,'required original evidence '+name);return data[name]
    def identity(name,digest,size=None):
        if name in data:need(sha(data[name])==digest and (size is None or len(data[name])==size),'published source/artifact identity')
        else:need(name in omitted and omitted[name]['sha256']==digest and (size is None or omitted[name]['bytes']==size),'omitted identity; bytes not read')
    for name,digest in manifest['canonical_source_sha256'].items():need(sha((ROOT/name).read_bytes())==digest,'reviewed canonical source '+name)
    controller=ROOT/'tests/run-cyd-opus-header-gain-qemu.py'
    spec=importlib.util.spec_from_file_location('reviewed_public_gain_reader',controller)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    # Reviewed current data readers only. No archived Python/C is imported.
    native=json.loads(take('native01/report.json'))
    need(sha(take('native01/report.json'))==manifest['native_original_report_sha256'] and native['passed'] and native['completed'] and
         native['target_executed'] and native['all_bound_inputs_current'] and not native['private_abi_used'],'original completed public native observation')
    for original,pin in native['inputs'].items():identity('native01/'+pin['snapshot'],pin['sha256'],pin['bytes'])
    need(take('native01/sources/controller.py')==controller.read_bytes(),'actual executed controller matches reviewed reader')
    for name,digest in native['build_outputs'].items():identity('native01/'+name,digest)
    entries=reader.fixture_accounting();need(entries==native['fixtures'],'exact complete paired encoded fixtures')
    generated=reader.make_fixture_blob(entries)
    need(sha(generated)==native['fixture_blob']['sha256'] and len(generated)==native['fixture_blob']['bytes'],'reconstructed complete encoded test transport')
    identity('native01/project/main/gains.bin',sha(generated),len(generated))
    commands=native['commands']
    need([row['name'] for row in commands]==['vendor-head','vendor-clean','sdk-head','sdk-clean','build','compiler-version',
         *['compiler-deps-'+str(i) for i in range(5)],'symbols','merge','qemu'],'complete original native command inventory')
    for row in commands:
        need(row['state']=='complete' and row['pid']>0 and row['exit_status']==0,'actual native process terminal zero')
        for stream in ('stdout','stderr'):need(sha(take('native01/'+row['name']+'.'+stream+'.log'))==row[stream+'_sha256'],'unchanged native stdout/stderr')
    child=json.loads(take('native01/sdk-child.json'));need(child['pid']>0 and child['exit_status']==0,'actual SDK driver child')
    argv=commands[-1]['argv'];need('-snapshot' in argv and argv[argv.index('-smp')+1]=='2' and argv[argv.index('-nic')+1]=='none','actual dual-core network-free diagnostic')
    need(native['tools']['qemu']['sha256']=='4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d','selected LX6 emulator identity')
    closure=json.loads(take('native01/actual-compiler-closure.json'))
    need(len(closure['translation_units'])==native['actual_translation_units']==5 and
         len(closure['dependencies'])==native['actual_compiler_dependencies']==202,'actual selected GCC closure')
    original=json.loads(take('native01/build/compile_commands.json'))
    for row in closure['translation_units']:
        need(sum(all(row.get(key)==value for key,value in actual.items()) for actual in original)==1,'selected TU joins original compiler command')
        need(set(row['actual_dependency_paths'])<=set(closure['dependencies']),'every actual TU dependency accounted')
    log=take('native01/qemu.stdout.log').decode('utf-8')+'\n'+take('native01/qemu.stderr.log').decode('utf-8')
    measured=reader.validate_log(log,entries)
    need(measured==native['measurements']==manifest['native_measurements'],'all six actual PCM/signal/lifetime observations')
    need(measured['gain_behavior']=='ignored_for_this_complete_fixture' and measured['header_gain_applied'] is False and
         manifest['header_gain_support'] is False and not manifest['production_gain_added'],'missing header-gain support remains open')
    first=measured['cases'][0];signal=(first['sha256'],first['energy'],first['absolute'],first['peak'],first['nonzero'],first['clips'])
    need(all((r['sha256'],r['energy'],r['absolute'],r['peak'],r['nonzero'],r['clips'])==signal for r in measured['cases']) and first['nonzero']>0,
         'independently identical nonzero whole outputs for all gain variants')
    mutations=[log.replace('gain_q8=1536','gain_q8=0',1),log.replace('energy=12668839949307','energy=0',1),
               log.replace('input=706319','input=706318',1),log.replace('data_eos=551','data_eos=0',1),
               log.replace('cases=6 core=1','cases=5 core=1',1),
               '\n'.join(line for line in log.splitlines() if not line.startswith('OPUS_GAIN_CASE id=2 gain_q8=-1536 chunk=257 '))]
    for bad in mutations:
        need(bad!=log,'contradictory transcript control changes evidence')
        try:reader.validate_log(bad,entries)
        except ValueError:pass
        else:raise ValueError('contradictory transcript accepted')
    reference=json.loads(take('reference01/report.json'))
    need(sha(take('reference01/report.json'))==manifest['reference_original_report_sha256'] and reference['passed'] and reference['completed'] and
         reference['all_source_bindings_current'] and reference['vendor_executed'] is False,'actual independent public reference execution')
    for row in reference['sources']:identity('reference01/'+row['snapshot'],row['sha256'],row['bytes'])
    for command in reference['commands']:
        need(command['state']=='complete' and command['pid']>0 and command['exit_status']==0,'reference tool/decoder terminal zero')
        for stream in ('stdout','stderr'):
            pin=command[stream];need(sha(take('reference01/'+pin['path']))==pin['sha256'],'original reference command logs')
    identity('reference01/'+reference['executable']['path'],reference['executable']['sha256'],reference['executable']['bytes'])
    generator=reader.generator_module();source=generator.SOURCE.read_bytes();_,packets=generator.parse(source)
    pcm_hashes=[];raw_floats=[]
    for name,gain in generator.VARIANTS:
        row=reference['fixtures'][name];actual=json.loads(take('reference01/'+name+'-reference.stdout.log'))
        need(actual==row['measurements']==manifest['reference_measurements'][name] and actual['reference']=='libopus 1.4' and
             actual['gain_q8']==gain and actual['raw_frames']==528960 and actual['pcm_bytes']==2115840 and
             actual['packets']==551 and actual['clips']==0 and actual['nonzero']>0 and actual['peak']>0 and
             not actual['library_header_gain_used'] and not actual['numeric_conformance_claim'],'complete raw float decode plus explicit normative gain')
        transport=struct.pack('<8sIIQIi',b'OGAIN01\0',48000,2,528960,551,gain)+b''.join(len(p).to_bytes(4,'little')+p for p in packets[2:])
        need(sha(transport)==row['packet_transport']['sha256'],'independent original packet transport with actual signed gain')
        for key in ('packet_transport','pcm'):
            pin=row[key];identity('reference01/'+pin['path'],pin['sha256'],pin['bytes'])
        pcm_hashes.append(row['pcm']['sha256']);raw_floats.append((actual['raw_float_peak'],actual['raw_float_energy']))
    need(len(set(pcm_hashes))==3 and len(set(raw_floats))==1,'reference has three distinct gained signals from the same raw float signal')
    for label,case_count in (('data01',19),('data02',20)):
        saved=json.loads(take(label+'/report.json'));need(saved['passed'] and len(saved['cases'])==case_count and
            saved['all_source_bindings_current'] and not saved['decoder_executed'] and not saved['native_target_executed'],'separate data-only fixture qualification')
        for pin in saved['sources'].values():identity(label+'/'+pin['snapshot'],pin['sha256'],pin['bytes'])
    print(json.dumps(dict(observation_verified=True,native_handles=6,full_audio_packets=551,data_cases=20,reference_decodes=3,
        header_gain_applied=False,production_gain_added=False,rejected_controls=len(mutations),logical_files=len(data),
        omitted_local_files=len(omitted),omitted_binary_or_PCM_bytes_read=False)))
if __name__=='__main__':main()
