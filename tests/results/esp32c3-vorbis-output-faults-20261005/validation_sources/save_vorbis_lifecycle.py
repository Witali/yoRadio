"""Validate and retain an original or repaired Vorbis QEMU failure sweep."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil

import run_vorbis_lifecycle as runner


def read_log(folder, name):
    path=folder/(name+'.log')
    data=path.read_bytes() if path.exists() else gzip.decompress((folder/(name+'.log.gz')).read_bytes())
    return data, data.decode(errors='replace')


def peak_ledger(log, symbols):
    live = {}
    peak_requested = peak_actual = 0
    at_peak = []
    for event in runner.allocation_ledger(log,symbols):
        if event['run'] != 1:
            continue
        if event['event']=='ALLOC' and int(event['ptr'],16):
            if event['kind']=='realloc' and int(event['old'],16):
                if event['old'] not in live:raise ValueError('Unknown realloc owner')
                del live[event['old']]
            if event['ptr'] in live:raise ValueError('Overlapping allocation owners')
            live[event['ptr']]=event
        elif event['event']=='FREE':
            if event['ptr'] not in live:raise ValueError('Unknown/double free in baseline')
            if event['id']!=live[event['ptr']]['id']:raise ValueError('Mismatched free lifetime')
            del live[event['ptr']]
        requested=sum(e['requested'] for e in live.values())
        actual=sum(e['actual'] for e in live.values())
        peak_requested=max(peak_requested,requested)
        if actual>peak_actual:
            peak_actual=actual;at_peak=list(live.values())
    if live:raise ValueError('Baseline has unreleased stream owners')
    groups=defaultdict(lambda:dict(count=0,requested=0,actual=0))
    for event in at_peak:
        function=(event['caller_function'] or event['caller']).split('+')[0]
        group=groups[function]
        group['count']+=1;group['requested']+=event['requested'];group['actual']+=event['actual']
    return dict(peak_requested=peak_requested,peak_actual=peak_actual,
                owners_at_peak=at_peak,by_allocator_caller=dict(groups))


def summarize(folder):
    report=json.loads((folder/'report.json').read_text())
    if not report.get('coverage_complete'):raise ValueError('Full fault sweep was not completed')
    cases=report['cases']
    baseline=cases[0]
    if baseline['name']!='baseline' or baseline['cycles']<100:raise ValueError('Missing 100-cycle baseline')
    count=report['expected_allocation_failures']
    expected={'baseline',*(f'oom-{i:04d}' for i in range(1,count+1)),
              'invalid-info-version','truncated-info','truncated-setup','invalid-codebook-sync'}
    boundary_tests = report.get('boundary_failure_tests', False)
    if boundary_tests:
        expected.update(f'registration-{i:04d}' for i in range(1,baseline['registration']['attempts']+1))
        expected.update(('service-open-0001','service-open-0002'))
    if {c['name'] for c in cases}!=expected or len(cases)!=len(expected):
        raise ValueError('Missing/duplicate fault case')
    symbols=runner.symbol_table((folder/'symbols.txt').read_text())
    _,base_log=read_log(folder,'baseline')
    baseline_check=runner.assess(base_log,cycles=baseline['cycles'])
    if not baseline_check['decoder_gate_pass']:raise ValueError('Baseline failed revalidation')
    reference=baseline_check['reference']
    if reference['attempts']!=count:raise ValueError('Incomplete allocation sweep')
    ledger=peak_ledger(base_log,symbols)
    if (ledger['peak_requested'],ledger['peak_actual'])!=(reference['peak_requested'],reference['peak_actual']):
        raise ValueError('Replayed owner ledger disagrees with target peak counters')
    baseline_allocations={e['attempt']:e for e in runner.records(base_log,'ALLOC') if e['run']==1}
    registration_allocations={e['attempt']:e for e in runner.records(base_log,'ALLOC') if e['run']==0}
    outcomes=[]
    for case in cases:
        raw,log=read_log(folder,case['name'])
        if hashlib.sha256(raw).hexdigest()!=case['log_sha256']:raise ValueError('Log changed: '+case['name'])
        checked=runner.assess(log,cycles=case['cycles'],fail_at=case['fail_at'],
                              direct=case['direct'],reference=reference)
        if checked['status']!=case['status']:raise ValueError('Changed classification: '+case['name'])
        events=runner.allocation_ledger(log,symbols)
        injected=next((e for e in events if e['event']=='INJECT'),None)
        if case['fail_at']:
            original=(registration_allocations if case['direct']==2 else baseline_allocations)[case['fail_at']]
            for target,source in [('kind','kind'),('bytes','requested'),('phase','phase'),('caller','caller')]:
                if injected[target]!=original[source]:raise ValueError('Injection reached another allocation site')
        fault_pc=re.search(r'MEPC\s*:\s*0x([0-9a-f]+)',log)
        panic_function=None
        if fault_pc:
            pc=int(fault_pc[1],16)
            panic_function=next((name+f'+0x{pc-address:x}' for address,size,name in symbols if address<=pc<address+size),None)
        outcomes.append(dict(name=case['name'],status=checked['status'],
            injected_allocation=injected,panic_pc=fault_pc[1] if fault_pc else None,
            panic_function=panic_function,recovery_ok=checked.get('recovery_ok'),
            result=checked['rows'][0] if checked['rows'] else None))
    summary = dict(step_one_complete=True,decoder_fixed=False,hardware_tested=False,
        coverage='Every allocation request in the successful single-fixture path; one injected failure per fresh VM',
        cycles=baseline['cycles'],allocation_failure_cases=count,malformed_cases=4,
        counts=dict(Counter(c['status'] for c in outcomes)),
        oom_counts=dict(Counter(c['status'] for c in outcomes if c['name'].startswith('oom-'))),
        baseline_reference=reference,registration=baseline_check['registration'],
        peak_ledger=ledger,outcomes=outcomes)
    if report.get('decoder_repair'):
        original = json.loads((runner.ROOT/'tests/results/esp32c3-vorbis-lifecycle-20261004/report.json').read_text())['cases'][0]['reference']
        pcm_match = all(reference[key] == original[key] for key in ('pcm','samples','sha256'))
        independent = report.get('pcm_reference')
        reference_match = independent and independent.get('raw_packet_reference') and all(
            reference[k] == independent['reference'][k] for k in ('pcm','samples','sha256'))
        if (not pcm_match and not reference_match) or report.get('original_pcm_match') != pcm_match:
            raise ValueError('Repaired PCM does not match the original decoder')
        summary.update(original_pcm_match=pcm_match, boundary_failure_tests=boundary_tests,
                       initialization_gate_pass=boundary_tests and all(
                           c['status'] in ('PASS','HANDLED','TOLERATED') for c in outcomes),
                       production_qualified=False)
        if independent: summary['pcm_reference'] = independent
    return summary


def verify_artifacts(folder, build):
    """Refuse a later rebuild or changed source snapshot as original evidence."""
    report = json.loads((folder / 'report.json').read_text())
    for name, expected in report['source_sha256'].items():
        if runner.sha(folder / 'sources' / name) != expected:
            raise ValueError('Source snapshot changed: ' + name)
    for name, key in [('sdkconfig', 'config_sha256'),
                      ('yoradio_esp32c3_oled_native.bin', 'app_sha256'),
                      ('yoradio_esp32c3_oled_native.elf', 'elf_sha256')]:
        if runner.sha(build / name) != report[key]:
            raise ValueError('Build changed after the run: ' + name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--build',type=Path,required=True)
    args=parser.parse_args()
    summary=summarize(args.run)
    verify_artifacts(args.run, args.build)
    if args.output.exists():raise ValueError('Use a new retained evidence directory')
    args.output.mkdir(parents=True)
    for name in ['report.json','symbols.txt','merge.log']:
        shutil.copyfile(args.run/name,args.output/name)
    shutil.copytree(args.run/'sources',args.output/'sources')
    for path in sorted(args.run.glob('*.log')):
        if path.name=='merge.log':continue
        (args.output/(path.name+'.gz')).write_bytes(gzip.compress(path.read_bytes(),mtime=0))
    # Ordered ledgers are derived again from the unchanged raw logs. The
    # original runner's ledger hashes remain in report.json for provenance.
    symbols=runner.symbol_table((args.run/'symbols.txt').read_text())
    for case in summary['outcomes']:
        _,log=read_log(args.run,case['name'])
        payload=(json.dumps(runner.allocation_ledger(log,symbols),indent=2)+'\n').encode()
        (args.output/(case['name']+'-allocations.json.gz')).write_bytes(gzip.compress(payload,mtime=0))
    shutil.copyfile(args.build/'sdkconfig',args.output/'sdkconfig')
    build_dir=args.output/'build';build_dir.mkdir()
    for name in ['yoradio_esp32c3_oled_native.bin','bootloader/bootloader.bin','partition_table/partition-table.bin','ota_data_initial.bin']:
        dest=build_dir/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(args.build/name,dest)
    summary['classifier_sha256']=runner.sha(Path(runner.__file__))
    summary['saver_sha256']=runner.sha(Path(__file__))
    validation=args.output/'validation_sources';validation.mkdir()
    shutil.copyfile(runner.__file__,validation/'run_vorbis_lifecycle.py')
    shutil.copyfile(__file__,validation/'save_vorbis_lifecycle.py')
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (args.output/'.gitattributes').write_text('* -text\n')
    manifest={}
    for path in sorted(args.output.rglob('*')):
        if path.is_file():manifest[path.relative_to(args.output).as_posix()]={'bytes':path.stat().st_size,'sha256':runner.sha(path)}
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary['counts']))
    print('Retained files:',len(manifest))


if __name__=='__main__':main()
