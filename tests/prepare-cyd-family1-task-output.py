"""Independent Decimal final-mono oracle over captured stock integer PCM.

No production gain/layout/mix/trim helper or decoder is imported. The reference
is same-vendor integration; creator numerical conformance is a separate gate.
"""
from array import array
from decimal import Decimal,ROUND_HALF_UP,localcontext
import hashlib
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
LEGACY_PCM={
    13:dict(path='.build/cyd-opus-position-oracle-20261101-01/F20-vendor-raw.pcm',
        bytes=2115840,sha256='a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b',
        offset=1248,logical_bytes=2112000,logical_sha256='b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f'),
    14:dict(path='.build/cyd-ogg-gain-task-20261101-04/stock-vorbis.pcm',
        bytes=2112000,sha256='e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910',
        offset=0,logical_bytes=2112000,logical_sha256='e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910'),
}


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(body):return hashlib.sha256(body).hexdigest()


def player(volume):return (volume*16*32768+2032)//4064


def channel_round(sample,gain):
    value=sample*gain
    return (value+16384)//32768 if value>=0 else -((-value+16384)//32768)


def truncate_half(value):return value//2 if value>=0 else -((-value)//2)


def speaker_coefficients(channels):
    # Exact formulas of RFC7845 section5.1.1.5 figures4–9, no helper import.
    a=Decimal(1)/Decimal(2).sqrt();b=Decimal(3).sqrt()/2
    zero,one,half=Decimal(0),Decimal(1),Decimal('0.5')
    if channels==1:return [one],[one]
    if channels==2:return [one,zero],[zero,one]
    if channels==3:left,right,scale=[one,a,zero],[zero,a,one],one/(one+a)
    elif channels==4:left,right,scale=[one,zero,b,half],[zero,one,half,b],one/(one+b+half)
    elif channels==5:left,right,scale=[one,a,zero,b,half],[zero,a,one,half,b],2/(one+a+b+half)
    elif channels==6:left,right,scale=[one,a,zero,b,half,a],[zero,a,one,half,b,a],2/(one+2*a+b+half)
    elif channels==7:left,right,scale=[one,a,zero,b,half,a*b,a],[zero,a,one,half,b,a*b,a],2/(one+2*a+b+half+a*b)
    else:
        need(channels==8,'declared public speaker range')
        left,right,scale=[one,a,zero,b,half,b,half,a],[zero,a,one,half,b,half,b,a],2/(2+2*a+2*b)
    return [value*scale for value in left],[value*scale for value in right]


def mono(pcm,channels,layout,gain,volume,precision):
    need(sys.byteorder=='little' and 1<=channels<=8 and len(pcm)%(channels*2)==0,'whole little-endian logical PCM frames')
    source=array('h');source.frombytes(pcm);output=bytearray();saturations=peak=nonzero=0
    q15=player(volume)
    with localcontext() as context:
        context.prec=precision
        factor=Decimal(10)**(Decimal(gain)/5120)*Decimal(q15)/32768
        if layout:
            left,right=speaker_coefficients(channels);weights=[factor*(a+b)/2 for a,b in zip(left,right)]
        else:
            need(channels in (1,2),'legacy corpus mono/stereo only');weights=[factor/channels]*channels
        # The mono/stereo identity matrix has finitely many integer sums.
        # Cache only values actually present; no production arithmetic is used.
        identity_cache={}
        for at in range(0,len(source),channels):
            if not layout and not gain:
                a=channel_round(source[at],q15)
                value=a if channels==1 else truncate_half(a+channel_round(source[at+1],q15))
            else:
                if channels<=2:
                    total=sum(source[at:at+channels])
                    if total not in identity_cache:
                        exact=Decimal(total)*weights[0]
                        identity_cache[total]=int(exact.to_integral_value(rounding=ROUND_HALF_UP))
                    rounded=identity_cache[total]
                else:
                    exact=sum((Decimal(source[at+i])*weights[i] for i in range(channels)),Decimal(0))
                    rounded=int(exact.to_integral_value(rounding=ROUND_HALF_UP))
                value=max(-32768,min(32767,rounded))
            output.extend(value.to_bytes(2,'little',signed=True));saturations+=value in (-32768,32767);nonzero+=value!=0;peak=max(peak,abs(value))
    return bytes(output),dict(bytes=len(output),frames=len(output)//2,sha256=sha(output),saturation_samples=saturations,nonzero_samples=nonzero,peak=peak)


def qualify(contract,measured,reference_pcm,out):
    """Called only after a genuine terminal native transcript is validated."""
    need(len(reference_pcm)==13 and out.is_dir() and out.resolve().is_relative_to(ROOT/'.build'),
         'all genuine public reference captures and existing contained native output')
    stocks={index:body for index,body in enumerate(reference_pcm)};bindings=[]
    for index,pin in LEGACY_PCM.items():
        path=ROOT/pin['path'];body=path.read_bytes()
        need(len(body)==pin['bytes'] and sha(body)==pin['sha256'],'complete earlier stock integer PCM identity')
        logical=body[pin['offset']:pin['offset']+pin['logical_bytes']]
        need(len(logical)==pin['logical_bytes'] and sha(logical)==pin['logical_sha256'],'all earlier independently positioned logical samples')
        stocks[index]=logical;bindings.append(dict(reference=index,**pin))
    for index,body in enumerate(reference_pcm):
        pin=measured['reference_pcm'][index]
        need(len(body)==pin['bytes'] and sha(body)==pin['sha256'],'whole direct public reference capture before Decimal')
        (out/('reference-'+str(index)+'.pcm')).write_bytes(body)
    entries={entry['id']:entry for entry in contract['entries']};cache={};records=[];cursor=0
    for case,render_case,plan in zip(measured['cases'],measured['render_cases'],contract['cases']):
        source_hash=hashlib.sha256();mono_hash=hashlib.sha256()
        for index,link in enumerate(plan['links']):
            reference,gain=link['reference'],link['gain_q8'];entry=entries.get(reference)
            channels=entry['channels'] if entry else 2;layout=1 if entry else 0;pcm=stocks[reference]
            key=(reference,gain,plan['volume'])
            if key not in cache:
                body,pin=mono(pcm,channels,layout,gain,plan['volume'],100)
                other,second=mono(pcm,channels,layout,gain,plan['volume'],160)
                need(body==other and pin==second,'entire final mono result stable at100/160 Decimal digits, no tolerance')
                cache[key]=(body,pin);records.append(dict(reference=reference,channels=channels,layout=layout,gain_q8=gain,volume=plan['volume'],**pin))
            body,pin=cache[key];actual=measured['render_links'][cursor];cursor+=1
            need(actual['bytes']==pin['bytes'] and actual['sha256']==pin['sha256'],'every full actual final-mono link equals independent Decimal')
            source_hash.update(pcm);mono_hash.update(body)
        need(case['sha256']==source_hash.hexdigest() and render_case['sha256']==mono_hash.hexdigest(),'all complete source and driver chain bytes, not concatenated hashes')
    return dict(passed=True,production_helpers_reused=False,decoder_executed=False,decimal_precision_digits=[100,160],
        normalization_enabled=False,full_reference_captures=[dict(reference=i,bytes=len(body),sha256=sha(body)) for i,body in enumerate(reference_pcm)],
        earlier_stock_bindings=bindings,full_mono_references=records,complete_cases=len(contract['cases']),
        independent_codec_conformance=False,new_tolerance_applied=False)
