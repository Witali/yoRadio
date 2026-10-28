"""DEFERRED WIP: incomplete interval/gain test preparation, not qualification."""
import argparse,ast,hashlib,importlib.util,json,os,re,subprocess,sys,time,uuid
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORACLE_READER_SHA='f34cf3eacdaf02d0e1fcd5a8a08063e69aa302ad1f8b3f4f8704b40bed20fdbb'
BASIC_READER_SHA='ea384976d4556ae95604b27a0072a732ae53e9558558f868730b3826bf12d7d7'
ORACLE_C_SHA='a5b20411d709d8b255f23909d6f618ec56cd85219aa7b7e08b69dd0e4fa56408'
MPFR_HEADER_SHA='588c2bd606cba060afb49cd024f9119e996089a341a99d1dc7e0367622335a13'
MPFR_LIBRARY_SHA='7357c29f8de910cb83deaf3c62f845f4862695361a798555bc8d6994911f2eca'
SUPERVISOR_ORIGIN_SHA='df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2'
ORDINARY_LOG_WIDTH=Fraction(1,1<<64)
KINDS=('finite','absent','unity','pole','indeterminate','needs_precision','undefined_mapping')
COMPONENTS=('native_vorbis_bigfloat','native_vorbis_interval','native_vorbis_certified_gain','native_vorbis_numeric')

def need(test,message):
    if not test:raise ValueError(message)
def sha(body):return hashlib.sha256(body).hexdigest()
def linux(path):
    value=Path(path).resolve().as_posix();return '/mnt/'+value[0].lower()+value[2:] if os.name=='nt' else value
def trusted(path,digest,name):
    need(sha(path.read_bytes())==digest,'pinned independent live reader');spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def affine_integer(value):
    return sum((-1 if packed>>31 else 1)*(packed&0x1fffff)*multiplier*(1<<((packed>>21)&1023))
        for packed,multiplier in ((value['minimum_bits'],value['minimum_multiplier']),(value['delta_bits'],value['delta_multiplier'])))
def mathematical_key(row):
    amplitude=row['amplitude'];maximum=(1<<amplitude['amplitude_bits'])-1
    return (row['order'],Fraction(row['bark'],row['size']),Fraction(amplitude['raw_amplitude'],maximum) if maximum else Fraction(),
        amplitude['amplitude_offset'],tuple(affine_integer(value) for value in row['angles']))
def corpus(oracle):
    requests,identities,provenance=oracle.exact_inputs();requests+=oracle.special_inputs()
    need(len(requests)==8202 and len(identities)==447,'all8202 exact encodings and447 saved frame identities')
    classes=[];lookup={};mapping=[]
    for index,row in enumerate(requests):
        key=mathematical_key(row)
        if key not in lookup:lookup[key]=len(classes);classes.append(index)
        mapping.append(lookup[key])
    need(len(classes)==4360,'only exact mathematical reference deduplication')
    ordinary=sorted({request for frame in identities if frame['id'].startswith('original31-') for channel in frame['channels'] for request in channel['requests']})
    need(ordinary and len({frame['id'] for frame in identities})==447,'all original ordinary active floor0 provenance')
    return dict(requests=requests,identities=identities,provenance=provenance,reference_representatives=classes,reference_mapping=mapping,ordinary_requests=ordinary)
def encode_gain(rows,indices,precision,sweep=False,warm=False):
    lines=['VCGAIN1 '+str(len(indices))+' '+str(precision)+' '+str(int(sweep))+' '+str(int(warm))]
    for index in indices:
        row=rows[index];amplitude=row['amplitude'];values=[index,row['order'],row['bark'],row['size'],amplitude['amplitude_bits'],amplitude['raw_amplitude'],amplitude['amplitude_offset']]
        values.extend(angle[key] for angle in row['angles'] for key in ('minimum_bits','delta_bits','minimum_multiplier','delta_multiplier'))
        lines.append(' '.join(map(str,values)))
    return ('\n'.join(lines)+'\n').encode('ascii')
def fraction(sign,magnitude,exponent):
    n=-magnitude if sign else magnitude
    return Fraction(n<<exponent) if exponent>=0 else Fraction(n,1<<-exponent)
def primitive_corpus():
    rows=[]
    def point(sign,m,e):return (sign,m,e)
    def add(operation,a=((0,0,0),(0,0,0)),b=((0,0,0),(0,0,0)),precision=64,sweep=False,label=''):
        rows.append(dict(id=len(rows),operation=operation,a=a,b=b,precision=precision,sweep=sweep,label=label))
    for p in (16,64,128,512):
        add('pi',precision=p,sweep=p==16,label='MPFR-constant');add('ln2',precision=p,sweep=p==16,label='MPFR-constant')
    for value in ((0,0,0),(0,1,-1),(1,1,-1),(0,1,0),(1,1,0),(0,1,-788),(1,1,-788),(0,1,-1023),
                  (0,(1<<300)+1,-1),(1,(1<<300)+1,-1)):
        for p in (32,128,512):
            for operation in ('sin','cos'):add(operation,(value,value),precision=p,sweep=p==32 and value==(0,1,-1),label='MPFR-direct-point')
    pairs=[(((1,3,-1),(0,5,-1)),((0,1,-1),(0,3,-1))),
           (((1,3,-1),(1,1,-1)),((1,5,-1),(1,1,-2))),
           (((0,1,-788),(0,3,-788)),((0,1,-1023),(0,3,-1023))),
           (((0,(1<<65)+1,-64),(0,(1<<65)+3,-64)),((1,(1<<65)+3,-64),(1,(1<<65)+1,-64)))]
    for a,b in pairs:
        for operation in ('add','sub','mul','div','square','sqrt','negate','scale2'):
            add(operation,a,b,precision=64,sweep=a==pairs[0][0],label='exact-Fraction-interval')
    add('div',((0,1,0),(0,2,0)),((1,1,0),(0,1,0)),label='uncertain-divisor')
    add('div',((0,1,0),(0,2,0)),label='exact-zero-divisor')
    add('sqrt',((1,1,0),(0,1,0)),label='uncertain-root')
    add('sqrt',((1,2,0),(1,1,0)),label='negative-root')
    return rows
def encode_primitives(rows):
    lines=['VCINT1 '+str(len(rows))]
    for row in rows:
        values=[row['id'],row['operation'],row['precision'],int(row['sweep'])]
        for endpoint in (*row['a'],*row['b']):values.extend((endpoint[0],endpoint[2],format(endpoint[1],'x')))
        lines.append(' '.join(map(str,values)))
    return ('\n'.join(lines)+'\n').encode('ascii')
def primitive_exact(row,basic):
    endpoints=lambda pair:tuple(fraction(*value) for value in pair)
    a,b=endpoints(row['a']),endpoints(row['b']);operation=row['operation'];p=row['precision']
    if operation in ('pi','ln2','sin','cos'):return None
    if operation=='add':bounds=(a[0]+b[0],a[1]+b[1])
    elif operation=='sub':bounds=(a[0]-b[1],a[1]-b[0])
    elif operation=='mul':values=[x*y for x in a for y in b];bounds=(min(values),max(values))
    elif operation=='div':
        if b==(0,0):return dict(status=-4)
        if b[0]<=0<=b[1]:return dict(status=-6)
        values=[x/y for x in a for y in b];bounds=(min(values),max(values))
    elif operation=='square':bounds=(Fraction() if a[0]<=0<=a[1] else min(x*x for x in a),max(x*x for x in a))
    elif operation=='sqrt':
        if a[1]<0:return dict(status=-4)
        if a[0]<0:return dict(status=-6)
        lo=basic.rounded_sqrt(a[0],p,-1);hi=basic.rounded_sqrt(a[1],p,1)
        return dict(status=0,lower=fraction(*lo),upper=fraction(*hi),square_crosses_zero=False)
    elif operation=='negate':bounds=(-a[1],-a[0])
    elif operation=='scale2':bounds=(a[0]*8,a[1]*8)
    else:raise ValueError('known interval operation')
    return dict(status=0,lower=bounds[0],upper=bounds[1],square_crosses_zero=operation=='square' and a[0]<=0<=a[1])


if __name__ == '__main__':
    raise SystemExit('Deferred WIP: qualification runner is incomplete; no tests were executed.')
