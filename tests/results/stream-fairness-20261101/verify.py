"""Data-only fairness checkpoint verification; never compile or execute captures."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import zipfile

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(body):return hashlib.sha256(body).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--require-current',action='store_true');args=parser.parse_args()
    manifest=json.loads((FOLDER/'manifest.json').read_bytes());pin=manifest['archive'];archive=FOLDER/pin['path']
    need(archive.name=='captures.zip' and archive.stat().st_size==pin['bytes'] and sha(archive.read_bytes())==pin['sha256'],'exact archive bytes')
    need(manifest['HOST_qualified'] and manifest['CYD_syntax_qualified'] and not manifest['C3_SDK_qualified'] and
         not manifest['native_fairness_qualified'] and not manifest['physical_qualified'] and
         not manifest['watchdog_settings_changed'] and manifest['native05_historical_status']=='NONPASS','bounded frontend scope')
    rows=manifest['files'];need(len(rows)==manifest['logical_files']==len({row['path'] for row in rows}),'logical census')
    blobs={}
    with zipfile.ZipFile(archive) as container:
        need(len(container.infolist())==manifest['physical_blobs']==len({row['blob'] for row in rows}),'physical census')
        for entry in container.infolist():
            body=container.read(entry);need(entry.filename=='blobs/'+sha(body),'all physical identities')
            need(not body.startswith((b'MZ',b'\x7fELF',b'!<arch>\n')),'no executable/archive-library payload')
            blobs[entry.filename]=body
    data={}
    for row in rows:
        path=PurePosixPath(row['path']);body=blobs[row['blob']]
        need(not path.is_absolute() and '..' not in path.parts and path.as_posix()==row['path'] and
             path.suffix.lower() not in ('.bin','.exe','.elf','.o','.obj','.a','.pcm','.pyc','.zip') and
             len(body)==row['bytes'] and sha(body)==row['sha256'],'contained exact data-only records')
        data[row['path']]=body
    omitted=manifest['omitted_local_files']
    need(all(name not in data and row['original_retained_locally'] and row['byte_payload_published'] is False
             for name,row in omitted.items()),'whole originals retained outside publication')
    def take(name):need(name in data,'required unchanged record '+name);return data[name]
    def identity(name,digest,size=None):
        if name in data:need(sha(data[name])==digest and (size is None or len(data[name])==size),'included frozen identity')
        else:need(name in omitted and omitted[name]['sha256']==digest and
                  (size is None or omitted[name]['bytes']==size),'explicit omitted identity; bytes not read')
    for label,cases in (('c3-plain02',42),('c3-retain01',42),('c3-growth01',47)):
        report=json.loads(take(label+'/report.json'));need(report['passed'] and report['cases']==cases and report['fairness_cases']==5,'complete actual C3 HOST cases')
        need(('PASS stream retry cases='+str(cases)+';').encode() in take(label+'/run.log'),'original C3 terminal log')
        need(all(b'Sanitizer' not in take(label+'/'+name) and b'runtime error:' not in take(label+'/'+name) for name in ('build.log','run.log')),'clean original sanitizer logs')
        for name,digest in report['source_sha256'].items():
            identity(label+'/sources/'+name,digest)
            if args.require_current:need(sha((ROOT/name).read_bytes())==digest,'current final C3 HOST input '+name)
    failed=json.loads(take('c3-plain01/report.json'))
    need(not failed['passed'] and failed['stage']=='run' and failed['returncode']==134 and
         b'body_read_calls==4' in take('c3-plain01/run.log') and b'!eos_count' in take('c3-plain01/run.log'),'genuine first new Stop-observer failure')
    for name,digest in failed['source_sha256'].items():identity('c3-plain01/sources/'+name,digest)
    stream=json.loads(take('cyd-stream02/report.json'))
    need(stream['passed'] and stream['physical_hardware'] is False and stream['live_inputs_match_snapshot'],'current CYD HOST bindings')
    need(b'PASS CYD stream cases=55:' in take('cyd-stream02/test.log') and
         b'PASS CYD settings requests=80:' in take('cyd-stream02/test.log'),'all unchanged CYD stream/settings assertions')
    need(b'native_tls_rx_reserve_crt_bundle_attach' in take('cyd-stream01/failed-command.log') and
         b'undeclared' in take('cyd-stream01/failed-command.log'),'first missing-header harness failure retained')
    power=json.loads(take('power02/report.json'));need(power['passed'] and power['physical_hardware'] is False and power['sanitizers']==['ASan','UBSan'],'shared policy HOST scope')
    for field,log,count in (('c3','c3-controls-test.log',10),('cyd','cyd-controls-test.log',9),('cyd-receive','cyd-stream-test.log',9)):
        need(take('power02/'+log).decode()==power['controls'][field] and
             (' '+str(count)+' groups;') in power['controls'][field],'complete power frontend assertions')
    need(b'native_output_metrics.h: No such file' in take('power01/cyd-controls-build.log'),'first missing-metrics-header harness failure retained')
    for label,report in (('cyd-stream02',stream),('power02',power)):
        for name,digest in report['source_sha256'].items():
            identity(label+'/sources/'+name,digest)
            if args.require_current:need(sha((ROOT/name).read_bytes())==digest,'current final HOST input '+name)
    syntax=json.loads(take('syntax01/report.json'))
    need(syntax['passed'] and syntax['syntax_only'] and not syntax['target_executed'] and
         not syntax['old_outputs_mutated'] and len(syntax['sources'])==78 and len(syntax['commands'])==1,'actual bounded CYD Xtensa syntax proof')
    command=syntax['commands'][0]
    need(command['state']=='complete' and command['pid']>0 and command['exit_status']==0 and
         '-fsyntax-only' in command['argv'] and '-c' not in command['argv'],'one genuine terminal compiler child')
    for name in ('compiler.stdout.log','compiler.stderr.log'):
        need(syntax[name]['bytes']==0 and not take('syntax01/'+name),'zero syntax diagnostics')
    for row in syntax['sources']:
        identity('syntax01/'+row['snapshot'],row['sha256'],row['bytes'])
        if args.require_current:need(sha(Path(row['path']).read_bytes())==row['sha256'],'current actual syntax input')
    need(sha(take('syntax01/audio_service.d'))==syntax['dependency_file_sha256'],'actual compiler dependency output')
    audit=json.loads(take('native05-audit/report.json'));retention=json.loads(take('native05-retention/manifest.json'))
    need(audit['read_only_audit_passed'] and not audit['full_task_passed'] and audit['original_native05_status']=='NONPASS' and
         audit['observed_failure']=='task watchdog: IDLE0 starved; CPU0 radio_stream, CPU1 audio_output' and
         audit['watchdog_timeout_s']==20 and audit['both_idle_watchdogs_enabled'] and audit['watchdog_panic_enabled'] and
         len(audit['complete_references'])==13 and audit['successful_complete_case_count']==21 and audit['complete_write_return_records']==17579 and
         audit['all_complete_after_hash_records_successful_and_equal'] and audit['damaged_write_after_hash_not_claimed'] and
         not audit['active_C8_120_application_reached'] and not audit['OOM_proven'] and
         not audit['stack_failure_proven'] and not audit['codec_failure_proven'],'historical genuine idle starvation and honest limits')
    need(retention['preserved'] and retention['native05_status']=='NONPASS' and not retention['full_task_passed'] and
         not retention['original_capture_mutated'] and not retention['original_runtime_repeated'] and
         retention['historical_release_sha256']=='9e09f4dce079df11c1b5799cf76cdc750245b8d47d83b71613e6bb1e5b49654d','historical source closure, not live-source identity')
    need('native05-original/qemu.stdout.log' in omitted and 'native05-original/qemu.stdout.log' not in data,'whole PCM-bearing UART omitted')
    for name,digest in manifest['canonical_source_sha256'].items():
        identity('canonical/'+name,digest)
        if args.require_current:need(sha((ROOT/name).read_bytes())==digest,'current canonical raw input '+name)
    print(json.dumps(dict(checkpoint_verified=True,current_sources_required=args.require_current,
        c3_HOST_cases=[42,42,47],cyd_HOST_stream_cases=55,cyd_settings_requests=80,power_groups=[10,9,9],
        CYD_syntax_bindings=78,native_fairness_qualified=False,C3_SDK_qualified=False,physical_qualified=False,
        omitted_PCM_or_executable_bytes_read=False)))


if __name__=='__main__':main()
