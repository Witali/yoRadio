"""Pure strict-reader controls; this starts no SDK, emulator or child process."""
import importlib.util, json, struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('floor1_native_protocol',ROOT/'tests/run-vorbis-floor1-product-qemu.py')
subject=importlib.util.module_from_spec(spec); spec.loader.exec_module(subject)
math=subject.load_math()
originals,all_cases=subject.native_cases(math)
ids={'width-0001-batch0','width-1087-batch1','limb-patterns-34-batch6','constant-000',
     'unit-255','exponent-underflow','invalid-domain-1087--1','zero-4096-255','selected-channel-2-width-1087'}
cases=[row for row in all_cases if row['id'] in ids]
subject.need(len(cases)==len(ids),'all representative protocol domains')
table=math.table_from_upstream((ROOT/'idf/components/native_vorbis_xiph/upstream/libvorbis/lib/floor1.c').read_bytes())
DATA='1'*64


def valid(target):
    core=1 if target=='esp32' else 0
    lines=[f'F1_BEGIN cases={len(cases)} coordinator=0 worker={core} data={DATA}',
           f'F1_WORKER core={core} priority=3 stack=16384']
    refusals=0; checks=0
    for i,case in enumerate(cases):
        status,layout=math.expected_layout(subject.expected_row(case),table)
        product=-1 if case['pattern']==3 else status
        lines.append(f'F1_CASE row={i} id={case["id"]} measure={status} product={product} core={core}')
        words=[]
        if product==0:
            lines.append('F1_LAYOUT row='+str(i)+' '+' '.join(f'{k}={v}' for k,v in layout.items())+f' core={core}')
            if layout['limbs']:
                mask=(1<<(32*layout['limbs']))-1
                for bin_index,index in enumerate(case['indices']):
                    c=table[index]
                    value=subject.expected_scalar(math,originals,case,bin_index)*c['mantissa'] << (case['exponent']+c['exponent']-layout['exponent'])
                    words.extend(struct.unpack('<'+'I'*layout['limbs'],(value&mask).to_bytes(layout['limbs']*4,'little')))
        for start in range(0,len(words),128) if words else (0,):
            piece=words[start:start+128]; runs=[]; at=0
            while at<len(piece):
                end=at+1
                while end<len(piece) and piece[end]==piece[at]: end+=1
                runs.append(f'{piece[at]:08x}:{end-at}'); at=end
            lines.append(f'F1_WORDS row={i} start={start} total={len(words)} count={len(piece)} runs='+(','.join(runs) if runs else '-')+f' core={core}')
        count=(25 if case['width'] else 19) if case['controls'] else 0
        refusals+=count; checks+=100
        lines.append(f'F1_END row={i} guards=1 unchanged=1 refusals={count} checks=100 core={core}')
    lines += [f'F1_COMPLETE cases={len(cases)} refusals={refusals} checks={checks+len(cases)} core={core}','F1_STOP status=CAPTURED']
    return '\n'.join(lines)+'\n'


def main():
    header=subject.header(all_cases)
    subject.need(header.endswith(b'};\n') and header.count(b' {"')==len(all_cases),'complete generated C descriptor array')
    measured={'passed':True,'cases':len(cases)}
    summary=dict(completed=True,target='esp32',**measured)
    subject.need(summary==dict(completed=True,target='esp32',passed=True,cases=len(cases)),
                 'footer preserves measured PASS without duplicate keyword')
    rejected=0
    for target in ('esp32','esp32c3'):
        log=valid(target)
        observed=subject.validate_log(log,cases,originals,math,table,target,DATA)
        subject.need(observed['passed'] and observed['cases']==len(cases),'valid lossless protocol')
        lines=log.splitlines(); word=next(i for i,x in enumerate(lines) if x.startswith('F1_WORDS') and 'runs=-' not in x)
        mutations=[log[:log.rfind('F1_STOP')],log+'F1_STOP status=CAPTURED\n',
            log.replace('priority=3','priority=4',1),log.replace('guards=1','guards=0',1),
            log.replace('unchanged=1','unchanged=0',1),log.replace('data='+DATA,'data='+'2'*64,1),
            log.replace('F1_CASE row=0','F1_CASE row=1',1),log+'task watchdog\n',
            log.replace('F1_STOP status=CAPTURED','F1_STOP status=FAILED',1),
            log.replace('F1_WORKER core=','torn F1_WORKER core=',1)]
        changed=list(lines); changed[word]=changed[word].replace(' start=0 ',' start=1 ',1); mutations.append('\n'.join(changed))
        changed=list(lines); value=changed[word].split('runs=')[1][:8]; different='00000001' if value=='00000000' else '00000000'
        changed[word]=changed[word].replace('runs='+value,'runs='+different,1); mutations.append('\n'.join(changed))
        changed=list(lines); changed.insert(word,changed[word]); mutations.append('\n'.join(changed))
        changed=list(lines); changed[word]=changed[word].replace(' count=128 ',' count=127 ',1); mutations.append('\n'.join(changed))
        for body in mutations:
            try: subject.validate_log(body,cases,originals,math,table,target,DATA)
            except ValueError: rejected+=1
            else: raise AssertionError('corrupt/partial native transcript accepted')
    subject.need(rejected==28,'all explicit corrupt controls rejected')
    print(json.dumps(dict(passed=True,valid_targets=2,cases_per_target=len(cases),rejected_controls=rejected)))


if __name__=='__main__': main()
