"""Replay completed candidate-QEMU workloads without promoting them to H10."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from runtime_evidence import journal_evidence,require
from verify_photo_format_matrix_evidence import source_hashes


def sha(data):
    """Bind every archived typed observation and source snapshot to its bytes."""
    return hashlib.sha256(data).hexdigest()


def validate(report,evidence,guard,supervisor,uart,cycles):
    """Require complete workload, real reconnects, memory headroom and UART guard."""
    require(report['schema_version']==5,'Expected explicit executable identity')
    require(report['passed'] and report['inputs_unchanged'] and report['no_panic'] and
        not report.get('error') and not report.get('cleanup_error'),'Failed workload')
    require(report['all_functionality_verified'] is False,'Overstated scope')
    require(report['inputs_sha256'].get(report['qemu_executable'])==report['qemu_sha256'],
        'Unpinned executable identity')
    require(report['cycles_requested']==report['completed_cycles']==evidence['cycles']==cycles,
        'Incomplete cycle count')
    require(report['duration_requested_guest_seconds'] is None,'Not a duration workload')
    require(report['summary']==evidence['summary'] and report['journal']['sha256']==evidence['sha256'],
        'Journal aggregates differ')
    summary=evidence['summary'];require(summary['outages']==cycles//2,'Missing reconnects')
    require(report['outage_every_cycles']==2 and report['outage_guest_seconds']==1,'Changed workload')
    require(report['rom_counter_crosscheck']['checks']==evidence['rom_calls'],'Incomplete ROM crosscheck')
    require(report['weather_coverage_passed'] and report['weather_observation']==evidence['weather'] and
        evidence['weather']['valid_samples']>0,'Missing parsed weather')
    require(report['weather_fixture']['responses_ok']>0 and
        report['weather_fixture']['all_synthetic_locations'] and report['weather_fixture']['all_synthetic_keys'],
        'Invalid weather fixture')
    start=report['workload_start_guest_seconds'];end=report['workload_end_guest_seconds']
    require(end>start and abs(end-start-report['elapsed_guest_seconds'])<1e-6,'Wrong duration arithmetic')
    series=evidence['series'];require(start<=series[0]['guest_seconds']<=start+1 and
        end-1<=series[-1]['guest_seconds']<=end,'Missing duration coverage')
    require(report['radio_clock_wraps']==int(end*1e6)//2**32-int(series[0]['guest_seconds']*1e6)//2**32,
        'Wrong clock wrap count')
    require(uart['passed'] and uart['rom_boots']==1 and not uart['errors'],'UART reset or panic')
    require(guard['status']=='complete' and guard['passed'] and guard['workload_passed'] and
        guard['last_observation']==uart,'Independent guard differs')
    require(supervisor['status']=='complete' and supervisor['passed'] and supervisor['sources_unchanged'] and
        supervisor['guard_exit_code']==supervisor['workload_exit_code']==0 and not supervisor['cleanup_errors'],
        'Supervisor did not finish successfully')
    return dict(passed=True,cycles=cycles,outages=summary['outages'],http_requests=summary['http_requests'],
        elapsed_guest_seconds=report['elapsed_guest_seconds'],
        minimum_sampled_free_heap_bytes=summary['minimum_sampled_free_heap_bytes'],
        minimum_sdk_sum_of_per_heap_minima_bytes=summary['minimum_sdk_sum_of_per_heap_minima_bytes'],
        minimum_task_stack_fill_bytes=min(summary['minimum_task_stack_fill_bytes_by_name'].values()),
        maximum_http_or_batch_guest_seconds=summary['maximum_http_or_batch_guest_seconds'],h10_checks_passed=False)


def rejections(report,evidence,guard,supervisor,uart,cycles):
    """Reject altered identities, missing work and false guard conclusions."""
    rejected=[]
    for case in ('emulator-identity','cycles','rom-counters','weather','duration','guard','uart-reset','supervisor'):
        r,e,g,s,u=copy.deepcopy((report,evidence,guard,supervisor,uart))
        if case=='emulator-identity':r['qemu_sha256']='00'*32
        elif case=='cycles':r['completed_cycles']-=1
        elif case=='rom-counters':r['rom_counter_crosscheck']['checks']-=2
        elif case=='weather':r['weather_coverage_passed']=False
        elif case=='duration':r['elapsed_guest_seconds']+=1
        elif case=='guard':g['passed']=False
        elif case=='uart-reset':u['rom_boots']=2;g['last_observation']=u
        else:s['sources_unchanged']=False
        try:validate(r,e,g,s,u,cycles)
        except ValueError:rejected.append(case)
        else:raise AssertionError('Invalid runtime evidence accepted: '+case)
    return rejected


def verify(path,root,revision=None):
    """Recompute journals and check archived sources; no VM or firmware writes."""
    proof=json.loads(path.read_text());assert proof['schema_version']==1 and proof['passed'] and not proof['h10_checks_passed']
    assert not proof['all_functionality_verified'] and not proof['physical_hardware_tested']
    model=proof['network_model_evidence'];model_path=(path.parent/model['file']).resolve()
    assert model_path.is_relative_to(path.parent.resolve())
    app=(root/'firmware/development/small-tv-esp32c2-reconstructed/app.bin').read_bytes()
    elf=(root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()
    assert sha(app)==proof['app_sha256'] and sha(elf)==proof['elf_sha256']
    assert app[176:208]==bytes.fromhex(proof['elf_sha256'])
    blobs={}
    for row in proof['blobs']:
        file=(path.parent/row['file']).resolve();assert file.is_relative_to(path.parent.resolve())
        packed=file.read_bytes();assert sha(packed)==row['gzip_sha256'];data=gzip.decompress(packed)
        assert sha(data)==row['sha256'] and len(data)==row['bytes'];assert row['sha256'] not in blobs
        blobs[row['sha256']]=data
    files={row['source']:blobs[row['sha256']] for row in proof['raw']};assert len(files)==len(proof['raw'])
    # The archived bytes preserve the exact SHA; a checkout may change JSON line endings.
    model_bytes=files['model/evidence.json'];assert sha(model_bytes)==model['sha256']
    model_data=json.loads(model_bytes);assert json.loads(model_path.read_text())==model_data
    assert model_data['builds']['after']['sha256']==proof['qemu_sha256']
    assert source_hashes(root,proof['source_pins'],revision)==proof['source_pins']
    for name,digest in proof['source_pins'].items():assert sha(files['producer/'+name])==digest
    assert proof['photo_chunks']==(len(files['producer/Small_TV/src/tests/fixtures/jpeg/rgb-420.jpg'])+4095)//4096
    assert b'Ran 25 tests' in files['unit/analysis-tests.log'] and b'OK' in files['unit/analysis-tests.log']
    stopped=json.loads(files['unit/qualification-processes.json'])
    assert stopped['passed'] and stopped['all_absent'] and len(set(stopped['checked_process_ids']))==8
    results=[];controls=0
    for run in proof['runs']:
        prefix=run['name']+'/';read=lambda name:json.loads(files[prefix+name])
        report=read('report.json');guard=read('uptime-guard.json');supervisor=read('supervisor.json');uart=read('uart-summary.json')
        if run['cycles']==40:
            start=read('start.json');assert start['completed_cycles_at_capture']==0
            for key in ('app_sha256','native_elf_sha256','qemu_sha256','inputs_sha256','duration_requested_guest_seconds'):
                assert start[key]==report[key]
            assert start['guard']['source_sha256']==proof['source_pins']['Small_TV/src/tools/runtime_run_guard.py']
        assert report['app_sha256']==proof['app_sha256'] and report['native_elf_sha256']==proof['elf_sha256']
        assert report['qemu_sha256']==proof['qemu_sha256']
        for name,digest in report['inputs_sha256'].items():
            relative=name.replace('\\','/').split('/small-tv-improvement-plan/',1)[-1]
            if relative.startswith('Small_TV/') and relative.endswith(('.py','.json')):
                assert proof['source_pins'][relative]==digest
        data=files[prefix+'events.jsonl'];assert sha(data)==report['journal']['sha256']
        # Keep replay output in a bounded content-addressed workspace, never a VM directory.
        folder=(root/'.build/runtime-candidate-replay'/sha(data)).resolve()
        assert folder.is_relative_to((root/'.build').resolve());folder.mkdir(parents=True,exist_ok=True)
        journal=folder/'events.jsonl';journal.write_bytes(data)
        evidence=journal_evidence(journal,proof['photo_chunks'],2,require_weather=True)
        result=validate(report,evidence,guard,supervisor,uart,run['cycles'])
        rejected=rejections(report,evidence,guard,supervisor,uart,run['cycles'])
        assert result==run['result'] and rejected==run['rejected_controls'];controls+=len(rejected);results.append(result)
    assert {r['cycles'] for r in results}=={4,40}
    return dict(passed=True,runs=results,unsafe_controls_rejected=controls,h10_checks_passed=False)


def main():
    """Validate the selected archived workloads without claiming 24-hour acceptance."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--source-revision')
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.source_revision)))


if __name__=='__main__':main()
