"""Independently read saved format results, physical frames and target RAM."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from photo_flash_evidence import ready_frame,journal
import photo_runtime_metrics as metrics
from verify_jpeg_clock_evidence import protected


def sha(data):
    """Hash complete evidence bytes rather than a producer's success flag."""
    return hashlib.sha256(data).hexdigest()


def fields(ram,address,layout,base=metrics.BASE):
    """Reconstruct the full caller-owned diagnostic from saved RAM and DWARF."""
    size=layout['bytes'];assert base<=address<=base+len(ram)-size
    data=ram[address-base:address-base+size]
    def members(offset,kind):
        result={}
        for name,field in kind['fields'].items():
            at=offset+field['offset']
            if field.get('fields'):result[name]=members(at,field)
            elif field['bytes'] in (1,2,4,8):result[name]=int.from_bytes(data[at:at+field['bytes']],'little')
        return result
    return members(0,layout)


def validate(report,corpus,oracles,plan,resource_layout,diagnostic_layout,read):
    """Require corpus coverage, exact pixel references, resource reasons and reuse."""
    assert report['passed'] and report['owners_stopped']
    assert not any(report[k] for k in ('all_functionality_verified','lcd_acceptance','network_acceptance',
        'hardware_tested','rf_tested','physical_power_cut_tested'))
    assert report['program_limit_kib']==200 and report['elf_sha256']==resource_layout['elf_sha256']
    owned=[*plan['backing']['extents'],*plan['metadata']['extents'],*plan['caches'][4]['extents']]
    mutable=([(0x9000,0xf000),(0x3e7000,0x3e8000),(0x264000,0x27d000)]+
        [(r['offset'],r['offset']+r['bytes']) for r in owned])
    cases=report['cases'];primary=[r for r in cases if 'recovery_for' not in r]
    names=[r['name'] for r in primary];assert len(names)==len(set(names)) and set(names)<=corpus.keys()
    if report['complete_corpus']:assert len(names)==70 and set(names)==corpus.keys()
    accepted=refused=source_limits=recoveries=0;stacks=[];heap_lower_bounds=[]
    for index,row in enumerate(cases):
        assert row['passed'];assert row['source_sha256']==sha(corpus[row['name']])
        assert row['source_bytes']==len(corpus[row['name']])
        oracle=oracles[row['name']];assert row['expected']==oracle['expected']
        if row['expected']=='valid':assert row['rgb565_sha256']==oracle['rgb565_sha256']
        directory=row['directory'];before=read(directory+'/before.bin');after=read(directory+'/after.bin')
        assert len(before)==len(after)==0x400000 and sha(before)==row['before_sha256'] and sha(after)==row['after_sha256']
        if row['expected']=='source-slot':
            assert row['source_bytes']>102400 and row['start']['status']==400 and before==after and row['flash_unchanged']
            source_limits+=1;failed=True
        else:
            assert row['start']==dict(status=200,body='OK');result=row['finish'];d=result['diagnostic']
            assert 0<=d['program_bytes']<=204800
            protected(before,after,mutable)
            for phase in ('entry','exit'):
                observed=result[phase+'_resources'];ram=read(directory+'/'+observed['ram_file'])
                assert sha(ram)==observed['ram_sha256']
                derived=metrics.inspect(resource_layout,ram,observed['worker']['tcb_address'],
                    result['decode_diagnostic_address'] if phase=='exit' else None)
                for key in derived:assert observed[key]==derived[key],(index,phase,key)
                if phase=='exit':assert fields(ram,result['diagnostic_address'],diagnostic_layout)==d
                stacks.append(derived['worker']['untouched_prefix_bytes'])
                heap_lower_bounds.append(derived['sum_individual_heap_minima'])
            assert min(stacks)>=1024,'Insufficient observed photo worker stack margin'
            assert d['decode']['stores_opened']==d['decode']['stores_closed']
            failed=result['status']!=200
            if not failed:
                assert row['expected']=='valid' and result['body']=='OK' and result['return_status']==0
                assert d['decode']['status']==0 and d['decode']['rows']==240
                assert row['published']==dict(exists=True,size=row['source_bytes'])
                assert ready_frame(after,plan,4,row['source_sha256'],row['rgb565_sha256'])==row['cache']
                accepted+=1
            else:
                assert result['status']==400 and result['return_status']!=0
                assert row['published']==dict(exists=False,size=0) and not journal(after,plan)['entries'][4]['ready']
                kind=row['expected'];body=result['body']
                if kind=='valid':
                    assert body.startswith(('flash-write-limit;','heap-headroom;','service-heap-reserve;',
                        'library-pool-limit;','backing-capacity;'))
                elif kind=='unsupported-jpeg':assert d['decode']['status']==4
                elif kind=='truncated-jpeg':assert d['privacy']['status']==3 or d['decode']['status']==3
                elif kind=='invalid-jpeg':assert d['privacy']['status']==2 or d['decode']['status']==2
                elif kind=='backing-capacity':assert body.startswith(('backing-capacity;','heap-headroom;','service-heap-reserve;'))
                elif kind=='library-pool-limit':assert body.startswith(('library-pool-limit;','heap-headroom;','service-heap-reserve;'))
                else:raise AssertionError(kind)
                if kind in ('valid','backing-capacity','library-pool-limit'):
                    numbers=re.search(r'required=(\d+) available=(\d+)',body)
                    assert numbers and int(numbers[1])>int(numbers[2])
                refused+=1
        if failed:
            assert 'recovery_for' not in row and index+1<len(cases)
            next_row=cases[index+1]
            assert next_row.get('recovery_for')==index and next_row['finish']['status']==200
        if 'recovery_for' in row:
            assert not failed and row['recovery_for']==index-1 and row['name']=='flat-gray-progressive-8.jpg';recoveries+=1
    assert len(cases)==accepted+refused+source_limits and recoveries==refused+source_limits
    return dict(passed=True,complete_corpus=report['complete_corpus'],corpus_vectors=len(primary),workflows=len(cases),
        accepted=accepted,refused=refused,source_limits=source_limits,recoveries=recoveries,
        worker_untouched_minimum=min(stacks),sum_individual_heap_minima_lower_bound=min(heap_lower_bounds))


def main():
    """Inspect files only; no running guest or physical device is required."""
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,nargs='+',required=True)
    args=parser.parse_args()
    from photo_format_matrix_qemu import fixtures,factory_pixels
    corpus,rows,_=fixtures();oracles={r['name']:r for r in rows}
    reports=[json.loads((run/'report.json').read_text()) for run in args.run]
    archive=Path(__file__).resolve().parents[3]/'firmware/development/small-tv-esp32c2-reconstructed'
    if any(r['name']=='rich-baseline-8.jpg' for report in reports for r in report['cases']):
        oracles['rich-baseline-8.jpg'].update(factory_pixels(corpus['rich-baseline-8.jpg'],Path('C:/Work/yoRadio')))
    plan=json.loads((archive/'jpeg-cache-plan.json').read_text())
    results=[];covered=[]
    for run,report in zip(args.run,reports):
        for name in ('app_sha256','elf_sha256','source_sha256'):assert report[name]==reports[0][name]
        for name,digest in report['inputs_sha256'].items():assert sha(Path(name).read_bytes())==digest,name
        read=lambda name:(run/name).read_bytes()
        results.append(validate(report,corpus,oracles,plan,json.loads(read('resource-layout.json')),
            json.loads(read('diagnostic-layout.json')),read))
        covered += [r['name'] for r in report['cases'] if 'recovery_for' not in r]
    assert len(covered)==len(set(covered)),'Corpus vector duplicated across parts'
    print(json.dumps(dict(passed=True,complete_corpus=set(covered)==corpus.keys(),
        corpus_vectors=len(covered),runs=results)))


if __name__=='__main__':main()
