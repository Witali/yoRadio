"""Replay completed candidate-QEMU workloads without promoting them to H10."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from runtime_evidence import journal_evidence,require
from verify_photo_format_matrix_evidence import source_hashes


def sha(data):
    """Bind every archived typed observation and source snapshot to its bytes."""
    return hashlib.sha256(data).hexdigest()


def validate_model(data, proof, model_path=None):
    """Bind the executable to either its AP fix or the merged QEMU checkpoint."""
    identity = proof['network_model_evidence']
    assert sha(data) == identity['sha256']
    model = json.loads(data)
    kind = identity.get('kind', 'network-stalled-peer-v1')
    if kind == 'qemu-main-merge-v1':
        assert proof['schema_version'] in (2, 3)
        assert model['schema'] == 'qemu-main-merge-validation-v1'
        assert model['passed'] and not model['all_functionality_verified']
        assert re.fullmatch('[0-9a-f]{40}', model['compiled_source_commit'])
        assert model['executables']['riscv32']['sha256'] == proof['qemu_sha256']
        pins = model['model_source_sha256']
        assert pins and all(re.fullmatch('[0-9a-f]{64}', value) for value in pins.values())
    else:
        assert kind == 'network-stalled-peer-v1' and proof['schema_version'] == 1
        assert model_path is not None and json.loads(model_path.read_text()) == model
        assert model['builds']['after']['sha256'] == proof['qemu_sha256']


def model_rejections(data, proof):
    """Reject internally rehashed but unqualified or mismatched main manifests."""
    if proof['schema_version'] == 1:
        return []
    rejected = []
    for case in ('model-failed', 'model-emulator', 'model-commit', 'model-scope'):
        changed, candidate = copy.deepcopy(json.loads(data)), copy.deepcopy(proof)
        if case == 'model-failed': changed['passed'] = False
        elif case == 'model-emulator': changed['executables']['riscv32']['sha256'] = '00' * 32
        elif case == 'model-commit': changed['compiled_source_commit'] = 'unknown'
        else: changed['all_functionality_verified'] = True
        raw = json.dumps(changed).encode()
        candidate['network_model_evidence']['sha256'] = sha(raw)
        try: validate_model(raw, candidate)
        except AssertionError: rejected.append(case)
        else: raise AssertionError('Invalid merged QEMU identity accepted: ' + case)
    return rejected


def validate(report,evidence,guard,supervisor,uart,cycles,expected_schema=5):
    """Require complete workload, real reconnects, memory headroom and UART guard."""
    require(expected_schema in (5,6) and report['schema_version']==expected_schema,
        'Expected matching runtime observation schema')
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
    result=dict(passed=True,cycles=cycles,outages=summary['outages'],http_requests=summary['http_requests'],
        elapsed_guest_seconds=report['elapsed_guest_seconds'],
        minimum_sampled_free_heap_bytes=summary['minimum_sampled_free_heap_bytes'],
        minimum_sdk_sum_of_per_heap_minima_bytes=summary['minimum_sdk_sum_of_per_heap_minima_bytes'],
        minimum_task_stack_fill_bytes=min(summary['minimum_task_stack_fill_bytes_by_name'].values()),
        maximum_http_or_batch_guest_seconds=summary['maximum_http_or_batch_guest_seconds'],h10_checks_passed=False)
    if expected_schema==6:
        require(evidence.get('verified_snapshots')==summary['snapshots'],'Missing topology instruction replay')
        result.update(heap_topology_snapshots=summary['snapshots'],
            heap_header_inventories=summary['snapshots']*len(summary['first_snapshot']['heap']['heaps']))
    return result


def rejections(report,evidence,guard,supervisor,uart,cycles,expected_schema=5):
    """Reject altered identities, missing work and false guard conclusions."""
    rejected=[]
    cases=['emulator-identity','cycles','rom-counters','weather','duration','guard','uart-reset','supervisor']
    if expected_schema==6:cases.append('skipped-topology-replay')
    for case in cases:
        r,e,g,s,u=copy.deepcopy((report,evidence,guard,supervisor,uart))
        if case=='emulator-identity':r['qemu_sha256']='00'*32
        elif case=='cycles':r['completed_cycles']-=1
        elif case=='rom-counters':r['rom_counter_crosscheck']['checks']-=2
        elif case=='weather':r['weather_coverage_passed']=False
        elif case=='duration':r['elapsed_guest_seconds']+=1
        elif case=='guard':g['passed']=False
        elif case=='uart-reset':u['rom_boots']=2;g['last_observation']=u
        elif case=='supervisor':s['sources_unchanged']=False
        else:e.pop('verified_snapshots',None)
        try:validate(r,e,g,s,u,cycles,expected_schema)
        except ValueError:rejected.append(case)
        else:raise AssertionError('Invalid runtime evidence accepted: '+case)
    return rejected


def topology_rejections(snapshot,topology):
    """Reject modified real-VM metadata even when ordinary heap totals still agree."""
    rejected=[]
    for case in ('missing-heap','fake-free-counter','wrong-dispatch','original-rom-walker',
                 'missing-header','hidden-overhead','wrong-elf','unused-metadata'):
        row=copy.deepcopy(snapshot);data=row['heap_topology'];part=data['heaps'][0]
        if case=='missing-heap':data['heaps'].pop()
        elif case=='fake-free-counter':
            row['heap']['free_bytes']+=4;row['heap']['heaps'][0]['free_bytes']+=4
            part['summary']['free_bytes']+=4
            header=bytearray.fromhex(part['header_hex'])
            offset=topology.layout['structures']['multi_heap_info']['fields']['free_bytes']['offset']
            header[offset:offset+4]=part['summary']['free_bytes'].to_bytes(4,'little')
            part['header_hex']=header.hex();part['inventory']['record']['free_counter']+=4
        elif case=='wrong-dispatch':
            table=bytearray.fromhex(data['dispatch_hex'])
            offset=topology.dispatch_layout['fields']['tlsf_walk_pool']
            table[offset:offset+4]=topology.walker.image.functions['tlsf_walk_pool']['address'].to_bytes(4,'little')
            data['dispatch_hex']=table.hex()
        elif case=='original-rom-walker':part['inventory']['record']['linked']=False
        elif case=='missing-header':part['inventory']['record']['metadata_words'].pop()
        elif case=='hidden-overhead':part['inventory']['allocated_header_bytes']=0
        elif case=='wrong-elf':data['elf_sha256']='00'*32
        else:part['inventory']['record']['metadata_words'].append([4,0])
        try:topology.validate(row)
        except (ValueError,KeyError,TypeError):rejected.append(case)
        else:raise AssertionError('Invalid heap topology accepted: '+case)
    return rejected


def verify(path,root,revision=None,rom=None):
    """Recompute journals and check archived sources; no VM or firmware writes."""
    proof=json.loads(path.read_text());assert proof['schema_version'] in (1,2,3) and proof['passed'] and not proof['h10_checks_passed']
    assert not proof['all_functionality_verified'] and not proof['physical_hardware_tested']
    model=proof['network_model_evidence'];model_path=None
    if proof['schema_version']==1:
        model_path=(path.parent/model['file']).resolve()
        assert model_path.is_relative_to(path.parent.resolve())
    app=(root/'firmware/development/small-tv-esp32c2-reconstructed/app.bin').read_bytes()
    elf=(root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()
    assert sha(app)==proof['app_sha256'] and sha(elf)==proof['elf_sha256']
    assert app[176:208]==bytes.fromhex(proof['elf_sha256'])
    topology=None
    if proof['schema_version']==3:
        from runtime_heap_topology import HeapTopology
        assert rom is not None and sha(rom.read_bytes())==proof['rom_sha256']
        topology=HeapTopology(rom,root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf')
    blobs={}
    for row in proof['blobs']:
        file=(path.parent/row['file']).resolve();assert file.is_relative_to(path.parent.resolve())
        packed=file.read_bytes();assert sha(packed)==row['gzip_sha256'];data=gzip.decompress(packed)
        assert sha(data)==row['sha256'] and len(data)==row['bytes'];assert row['sha256'] not in blobs
        blobs[row['sha256']]=data
    files={row['source']:blobs[row['sha256']] for row in proof['raw']};assert len(files)==len(proof['raw'])
    # The archived bytes preserve the exact SHA; a checkout may change JSON line endings.
    model_bytes=files['model/evidence.json'];validate_model(model_bytes,proof,model_path)
    model_controls=model_rejections(model_bytes,proof)
    assert model_controls==proof.get('model_rejected_controls',[])
    assert source_hashes(root,proof['source_pins'],revision)==proof['source_pins']
    for name,digest in proof['source_pins'].items():assert sha(files['producer/'+name])==digest
    assert proof['photo_chunks']==(len(files['producer/Small_TV/src/tests/fixtures/jpeg/rgb-420.jpg'])+4095)//4096
    assert b'Ran 25 tests' in files['unit/analysis-tests.log'] and b'OK' in files['unit/analysis-tests.log']
    stopped=json.loads(files['unit/qualification-processes.json'])
    assert stopped['passed'] and stopped['all_absent'] and len(set(stopped['checked_process_ids']))==8
    if topology:
        assert b'Ran 16 tests' in files['unit/memory-tests.log'] and b'OK' in files['unit/memory-tests.log']
        for name,count in (('unit/instructions.json',11),('unit/topology.json',8)):
            unit=json.loads(files[name]);assert unit['passed'] and unit['inputs_unchanged']
            assert unit['tests']==count and unit['no_vm_or_hardware_access']
            assert not unit['all_functionality_verified'] and not unit['failures'] and not unit['errors']
            producer_prefix=proof['producer_root'].replace('\\','/').rstrip('/')+'/'
            for filename,digest in unit['inputs_sha256'].items():
                normalized=filename.replace('\\','/')
                if normalized.endswith('/esp32c2_rev200_rom.elf'):
                    assert digest==proof['rom_sha256']
                elif normalized==producer_prefix+'.build/small-tv-esp32c2/small_tv_reconstructed.elf':
                    assert digest==proof['elf_sha256']
                else:
                    assert normalized.startswith(producer_prefix)
                    assert proof['source_pins'][normalized[len(producer_prefix):]]==digest
    results=[];controls=0
    for run in proof['runs']:
        prefix=run['name']+'/';read=lambda name:json.loads(files[prefix+name])
        report=read('report.json');guard=read('uptime-guard.json');supervisor=read('supervisor.json');uart=read('uart-summary.json')
        if run['cycles']==40:
            start=read('start.json');assert start['completed_cycles_at_capture']==0
            for key in ('app_sha256','native_elf_sha256','qemu_sha256','inputs_sha256','duration_requested_guest_seconds'):
                assert start[key]==report[key]
            assert start['guard']['source_sha256']==proof['source_pins']['Small_TV/src/tools/runtime_run_guard.py']
            if topology:
                assert start['capture_script_sha256']==sha(files['unit/capture-start.ps1'])
        assert report['app_sha256']==proof['app_sha256'] and report['native_elf_sha256']==proof['elf_sha256']
        assert report['qemu_sha256']==proof['qemu_sha256']
        for name,digest in report['inputs_sha256'].items():
            normalized=name.replace('\\','/')
            if proof['schema_version']==3:
                # FIXED_TEST: keep the run prefix intact when resolving producer inputs.
                producer_prefix=proof['producer_root'].replace('\\','/').rstrip('/')+'/'
                relative=normalized[len(producer_prefix):] if normalized.startswith(producer_prefix) else ''
            else:
                relative=normalized.split('/small-tv-improvement-plan/',1)[-1]
            if relative.startswith('Small_TV/') and relative.endswith(('.py','.json')):
                assert proof['source_pins'][relative]==digest
        data=files[prefix+'events.jsonl'];assert sha(data)==report['journal']['sha256']
        # Keep replay output in a bounded content-addressed workspace, never a VM directory.
        folder=(root/'.build/runtime-candidate-replay'/sha(data)).resolve()
        assert folder.is_relative_to((root/'.build').resolve());folder.mkdir(parents=True,exist_ok=True)
        journal=folder/'events.jsonl';journal.write_bytes(data)
        evidence=journal_evidence(journal,proof['photo_chunks'],2,require_weather=True,
            snapshot_check=topology.validate if topology else None)
        schema=6 if topology else 5
        result=validate(report,evidence,guard,supervisor,uart,run['cycles'],schema)
        rejected=rejections(report,evidence,guard,supervisor,uart,run['cycles'],schema)
        if topology:
            rejected_topology=topology_rejections(evidence['summary']['first_snapshot'],topology)
            assert rejected_topology==run['topology_rejected_controls']
            controls+=len(rejected_topology)
        assert result==run['result'] and rejected==run['rejected_controls'];controls+=len(rejected);results.append(result)
    assert {r['cycles'] for r in results}=={4,40}
    return dict(passed=True,runs=results,unsafe_controls_rejected=controls+len(model_controls),h10_checks_passed=False)


def main():
    """Validate the selected archived workloads without claiming 24-hour acceptance."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--source-revision')
    parser.add_argument('--rom',type=Path,help='Exact C2 ROM ELF, required for topology evidence')
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.source_revision,args.rom)))


if __name__=='__main__':main()
