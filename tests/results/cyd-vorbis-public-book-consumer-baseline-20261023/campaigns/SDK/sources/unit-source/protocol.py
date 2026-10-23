"""Pure complete owned-vector observation checks; never launches a target."""
import json
import re

from oracle import need

PREFIX='PUBLIC_BOOK_CONSUMER_'
VECTOR=re.compile(r'^PUBLIC_BOOK_CONSUMER_VECTOR case=(\d+) probe=(\d+) point=(-?\d+) bits=(\d+) consumed=(\d+) equal=([01]) core=(-?\d+) values=(-?\d+(?:,-?\d+)*)$')


def vector(line,model,core):
    match=VECTOR.fullmatch(line);need(match is not None,'exact complete vector record')
    ci,pi,point,bits,consumed,equal,observed_core=map(int,match.groups()[:7]);values=list(map(int,match[8].split(',')))
    need(ci<len(model['cases']),'case index');case=model['cases'][ci];b=case['book']
    need(pi<len(b['probes']) and point in b['points'],'full named codeword/point')
    probe=b['probes'][pi];need(bits==consumed==probe['bits'] and observed_core==core and len(values)==b['dim'],'exact consumed valid vector dimensions/core')
    expected=probe['expected_by_point'][str(point)]
    need(bool(equal)==(values==expected),'reported equality must reflect every exact Fraction component')
    return dict(case=ci,probe=pi,point=point,values=values,expected=expected,equal=bool(equal),wire_scope=probe['wire_scope'])


def validate_sdk(log,contract):
    model=contract['model'];lines=[line for line in log.splitlines() if line.startswith(PREFIX)]
    need(not re.search(r'Guru Meditation|panic|abort\(\)|Stack smashing|Brownout',log,re.I),'no actual target panic/reset')
    count=model['case_count'];calls=model['vector_calls']
    need(lines[0]==f'{PREFIX}BEGIN contract={contract["contract_sha256"]} cases={count} calls={calls} core=0','exact SDK beginning')
    cursor=1;records=[];fields=[]
    for ci,c in enumerate(model['cases']):
        b=c['book'];line=lines[cursor];cursor+=1
        match=re.fullmatch(PREFIX+r'FIELDS case=(\d+) type=(\d+) node=(\d+) leaf=(\d+) qbits=(\d+) qpack=(\d+) qmin=(-?\d+) minp=(-?\d+) qdel=(-?\d+) delp=(-?\d+) table=([0-9a-f]+) qval=([0-9a-f]+|-) core=0',line)
        need(match is not None,'full actual SDK publication record')
        observed=list(map(int,match.groups()[:10]));need(observed==[ci,b['dec_type'],b['dec_nodeb'],b['dec_leafw'],b['q_bits'],b['q_pack'],b['q_min'],b['q_minp'],b['q_del'],b['q_delp']],'every canonical published scalar field')
        table=bytes.fromhex(match[11]);qval=b'' if match[12]=='-' else bytes.fromhex(match[12]);need(len(table)==b['table_bytes'] and qval.hex()==b['qval_hex'],'full actual owned arrays/quantized rows')
        fields.append(dict(case=ci,scalars=observed,table_hex=table.hex(),qval_hex=qval.hex()))
        for pi,p in enumerate(b['probes']):
            for point in b['points']:
                row=vector(lines[cursor],model,0);cursor+=1;need((row['case'],row['probe'],row['point'])==(ci,pi,point),'full ordered SDK calls');records.append(row)
        need(lines[cursor]==f'{PREFIX}CASE case={ci} probes={len(b["probes"])} live=0 core=0','normal owned clear and free');cursor+=1
    unequal=sum(not row['equal'] for row in records)
    need(len(records)==calls and lines[cursor]==f'{PREFIX}COMPLETE cases={count} calls={calls} unequal={unequal} live=0 core=0' and cursor+1==len(lines),'exact complete SDK observation inventory')
    return dict(observation_completed=True,actual_canonical_SDK_publication_completed=True,
        complete_Fraction_comparison=True,all_Fraction_vectors_equal=unequal==0,unequal_calls=unequal,
        fields=fields,vectors=records,protocol_events=len(lines),host_sanitizers_qualified=False,
        public_arithmetic_portability_qualified=False,full_standard_qualified=False,vendor_cause_diagnosed=False)
