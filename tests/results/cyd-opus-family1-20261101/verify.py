"""Verify published public family1 observations without native code or omitted payloads."""
import hashlib
import importlib.util
import json
from pathlib import Path,PurePosixPath
import re
import tempfile
import zipfile
FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]
def need(value,why):
    if not value:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def main():
    manifest=json.loads((FOLDER/'manifest.json').read_bytes());pin=manifest['archive'];archive=FOLDER/pin['path']
    need(archive.name=='captures.zip' and sha(archive.read_bytes())==pin['sha256'] and archive.stat().st_size==pin['bytes'],'exact archive bytes')
    files=manifest['files'];need(len({r['path'] for r in files})==len(files)==manifest['logical_files'],'unique logical file census')
    blobs={}
    with zipfile.ZipFile(archive) as z:
        need(len(z.infolist())==manifest['physical_blobs']==len({r['blob'] for r in files}),'exact physical blob census')
        for entry in z.infolist():
            body=z.read(entry);need(re.fullmatch('blobs/[a-f0-9]{64}',entry.filename) and entry.filename=='blobs/'+sha(body),'physical hash identity')
            need(not body.startswith((b'\x7fELF',b'MZ',b'!<arch>\n',b'OggS',b'OFAM101\0')),'no executable/library/audio payload')
            blobs[entry.filename]=body
    data={}
    for row in files:
        name=PurePosixPath(row['path']);body=blobs[row['blob']]
        need(not name.is_absolute() and '..' not in name.parts and name.as_posix()==row['path'],'contained logical paths')
        need(sha(body)==row['sha256'] and len(body)==row['bytes'],'all logical identities');data[row['path']]=body
    omitted=manifest['omitted_local_files']
    need(all(name not in data and row['original_retained_locally'] and row['byte_payload_published'] is False and
        re.fullmatch('[a-f0-9]{64}',row['sha256']) and row['bytes']>=0 for name,row in omitted.items()),'explicit local omission identities')
    def take(name):need(name in data,'required evidence '+name);return data[name]
    def identity(name,digest,size=None):
        if name in data:need(sha(data[name])==digest and (size is None or len(data[name])==size),'included original identity')
        else:need(name in omitted and omitted[name]['sha256']==digest and (size is None or omitted[name]['bytes']==size),'omitted identity, payload not read')
    for path,digest in manifest['canonical_source_sha256'].items():need(sha((ROOT/path).read_bytes())==digest,'current reviewed canonical diagnostic '+path)
    for label in ('reference01','reference02','reference03','native01','native02','native03'):
        report=json.loads(take(label+'/report.json'))
        for command in report['commands']:
            need(command['pid']>0 and command['state']=='complete' and isinstance(command['exit_status'],int),'original terminal process')
            for stream in ('stdout','stderr'):
                if label.startswith('reference'):
                    pin=command[stream];need(sha(take(label+'/'+pin['path']))==pin['sha256'],'unchanged host process stream')
                else:need(sha(take(label+'/'+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],'unchanged native process stream')
        if label.startswith('reference'):
            for row in report['sources']:identity(label+'/'+row['snapshot'],row['sha256'],row['bytes'])
        else:
            sources=json.loads(take(label+'/source-manifest.json'))
            for row in sources.values():identity(label+'/'+row['snapshot'],row['sha256'],row['bytes'])
    host_failure=json.loads(take('reference01/report.json'));activation=json.loads(take('native01/report.json'));compile_failure=json.loads(take('native02/report.json'))
    need(not host_failure['passed'] and host_failure['commands'][0]['exit_status']==4294967295 and host_failure['failure']['reason']=='actual terminal zero: compiler-version',
        'original WSL DWORD status preserved without shell normalization')
    need(not activation['passed'] and not activation['target_executed'] and activation['commands'][-1]['name']=='build' and
        activation['commands'][-1]['exit_status']==1 and b'Activation script failed' in take('native01/build.stderr.log'),'unchanged SDK activation failure')
    failed_child=json.loads(take('native02/sdk-child.json').decode('utf-8-sig'));need(not compile_failure['passed'] and not compile_failure['target_executed'] and
        failed_child['exit_status']==2 and b'-Werror=format=' in take('native02/sdk-build.stdout.log'),'unchanged genuine printf compile failure')
    old_host=json.loads(take('reference02/report.json'));need(old_host['passed'] and old_host['completed'] and 'libogg_identity' not in old_host,'original earlier host checkpoint preserved')
    reference=json.loads(take('reference03/report.json'));native=json.loads(take('native03/report.json'))
    need(sha(take('reference03/report.json'))==manifest['actual_reference_report_sha256'] and reference['passed'] and reference['completed'] and
        reference['all_source_bindings_current'] and reference['data_tests']=={'passed':True,'cases':18,'decoder_executed':False},'actual complete host reference')
    need(sha(take('native03/report.json'))==manifest['actual_native_report_sha256'] and native['passed'] and native['completed'] and native['target_executed'] and
        native['all_bound_inputs_current'] and not native['private_codec_abi'] and native['actual_translation_units']==5 and native['actual_compiler_dependencies']==206,'actual public native diagnostic')
    need(all(c['exit_status']==0 for c in reference['commands']+native['commands']),'all successful checkpoint commands genuinely terminal zero')
    child=json.loads(take('native03/sdk-child.json').decode('utf-8-sig'));need(child['pid']>0 and child['exit_status']==0,'actual SDK child terminal zero')
    bundle=json.loads(take('native03/execution-bundle.json'))
    for name,digest in bundle['artifacts'].items():identity('native03/'+name,digest)
    closure=json.loads(take('native03/actual-compiler-closure.json'));original=json.loads(take('native03/build/compile_commands.json'))
    need(len(closure['translation_units'])==5 and len(closure['dependencies'])==206,'actual compiler closure census')
    for row in closure['translation_units']:
        need(sum(all(row.get(k)==v for k,v in actual.items()) for actual in original)==1 and
            set(row['actual_dependency_paths'])<=set(closure['dependencies']),'selected TUs join exact original compile commands/dependencies')
    need('pcm_header_gain.h' not in {Path(path).name for path in closure['dependencies']},'wrapper forwards gain metadata without PCM math')
    for name,row in reference['fixtures'].items():
        channels=int(name.removeprefix('channels'));encoding=json.loads(take('reference03/'+name+'-encode.stdout.log'))
        decoded=json.loads(take('reference03/'+name+'-reference.stdout.log'))
        checks=[json.loads(line) for line in take('reference03/'+name+'-ogg-check.stdout.log').splitlines()]
        need(encoding==row['encoding'] and decoded==row['reference'] and checks==row['creator_libogg_checks'],'original independent creator result streams')
        need(encoding['libopus']=='libopus 1.4' and encoding['channels']==decoded['channels']==channels and decoded['packets']==11 and
            decoded['raw_frames']==10560 and decoded['trim_frames']==9600 and all(v>0 for v in encoding['input_channel_energy']) and
            all(v>0 for v in decoded['channel_energy']) and all(v>0 for v in decoded['channel_downmix_contribution_energy']),
            'complete full-channel creator reference with every speaker contributing')
        need(len(checks)==2 and [v['chunk'] for v in checks]==[row['accounting']['bytes'],257] and all(v['exact_original_packets'] and
            v['pages']==13 and v['audio_packets']==11 and v['eos'] and v['sync_errors']==v['packet_holes']==0 for v in checks),'creator libogg complete container qualification')
        for filename,pin in row['files'].items():identity('reference03/'+filename,pin['sha256'],pin['bytes'])
    controller=ROOT/'tests/run-cyd-opus-family1-qemu.py';spec=importlib.util.spec_from_file_location('reviewed_family1_data_reader',controller)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    log=(take('native03/qemu.stdout.log').decode()+'\n'+take('native03/qemu.stderr.log').decode()).replace('\r\n','\n')
    need('F1_PCM ' not in log,'this observed refusal emits no omitted PCM payload in published logs')
    def read(text,fixtures):
        (ROOT/'.build').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='family1-data-verify-',dir=ROOT/'.build') as directory:
            return reader.parse_log(text,fixtures,Path('omitted-reference-payloads-not-read'),Path(directory))
    measured=read(log,reference['fixtures']);need(measured==native['measurements']==manifest['native_measurements'],'all original public call/PCM/resource observations')
    def semantic(value):
        for case in value['cases']:
            r=case['measurements'];calls=case['public_calls'];need(r['cause']==r['process_status']==calls[-1]['result']==-7 and
                r['status']==(4 if r['mode'] else -7) and r['opens']==r['closes']==1 and r['raw_bytes']==r['output_bytes']==0 and not r['drained'],
                'observed unsupported result remains an error, without PCM or fake EOS')
        need(value['mandatory_family1_playback_qualified'] is False,'mandatory family1 gap remains open')
    semantic(measured)
    bad_logs=[log.replace('consumed=1061 status=-7','consumed=1060 status=-7',1),log.replace('cause=-7','cause=-2',1),
        log.replace('F1_CLOSE id=0\n','',1),log.replace('drained=0','drained=1',1),log.replace('fixture_bytes=6254','fixture_bytes=6253',1),
        log.replace('process_status=-7','process_status=0',1)]
    for bad in bad_logs:
        need(bad!=log,'contradictory control changes original evidence')
        try:semantic(read(bad,reference['fixtures']))
        except ValueError:pass
        else:raise ValueError('contradictory native evidence accepted')
    complete=measured['complete'];after=[v['measurements']['after'] for v in measured['cases']]
    need(complete['retained']==388 and complete['heap_free']==283228 and complete['heap_min']==266652 and complete['stack_free']==13628 and
        all(a-b==24 for a,b in zip(after,after[1:])),'honest retained-memory slope; cause is not attributed')
    need(manifest['mandatory_family1_playback_qualified'] is False and manifest['physical_output_qualified'] is False and
        manifest['production_code_changed'] is False and manifest['universal_codec_conformance_claim'] is False,'bounded diagnostic scope')
    print(json.dumps(dict(diagnostic_verified=True,native_cases=12,creator_reference_channels=[3,6,8],creator_container_walks=6,
        data_cases=18,rejected_controls=len(bad_logs),observed_public_result=-7,mandatory_family1_playback_qualified=False,
        omitted_binary_or_PCM_bytes_read=False,retained_bytes=388,memory_attribution_qualified=False)))
if __name__=='__main__':main()
