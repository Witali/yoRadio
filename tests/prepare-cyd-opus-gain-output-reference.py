"""Independent final-mono gain references for the ordered output-owner policy.

Header zero uses the exact legacy Q15/channel-round/truncating-average law.
Nonzero header mixes wide after combining channel Q15 and header gain, with one
nearest-away rounding and signed16 saturation. Normalization is disabled in this
reference; no production gain/render helper or decoder is imported/executed.
"""
from array import array
from collections import Counter
from decimal import Decimal,ROUND_HALF_UP,localcontext
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'tests/prepare-cyd-opus-gain-playback.py'
DATA_SHA='4462682381da8d78d687c7af6d04d8210ba92928c5e153059f7582860ba5ccb2'


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(body):return hashlib.sha256(body).hexdigest()


def coefficient(volume,balance):return (volume*balance*32768+2032)//4064


def round_q15(sample,gain):
    n=sample*gain
    return (n+16384)//32768 if n>=0 else -((-n+16384)//32768)


def average(left,right):
    n=left+right
    return n//2 if n>=0 else -((-n)//2)


def mono_sample(left,right,channels,gain,volume,balance,precision=120):
    l=coefficient(volume,16+balance if channels>1 and balance<0 else 16)
    r=coefficient(volume,16-balance if balance>0 else 16)
    if not gain:
        a=round_q15(left,l)
        return a if channels==1 else average(a,round_q15(right,r))
    with localcontext() as context:
        context.prec=precision
        factor=Decimal(10)**(Decimal(gain)/Decimal(5120))
        wide=Decimal(left*l+(right*r if channels>1 else 0))*factor/Decimal(32768*(2 if channels>1 else 1))
        n=int(wide.to_integral_value(rounding=ROUND_HALF_UP))
        return max(-32768,min(32767,n))


def sum_table(gain,volume,precision):
    with localcontext() as context:
        context.prec=precision
        factor=(Decimal(10)**(Decimal(gain)/Decimal(5120)))*Decimal(coefficient(volume,16))/Decimal(65536)
        rows=[]
        for n in range(-65536,65535):
            value=int((Decimal(n)*factor).to_integral_value(rounding=ROUND_HALF_UP))
            rows.append(max(-32768,min(32767,value)).to_bytes(2,'little',signed=True))
        return rows


def full_mono(pcm,gain,volume,table=None):
    samples=array('h');samples.frombytes(pcm)
    digest=hashlib.sha256();peak=nonzero=saturation=power=0
    player=coefficient(volume,16)
    for start in range(0,len(samples),8192):
        part=bytearray()
        for at in range(start,min(start+8192,len(samples)),2):
            a,b=samples[at],samples[at+1]
            if gain:
                body=table[a+b+65536];value=int.from_bytes(body,'little',signed=True)
            else:
                value=average(round_q15(a,player),round_q15(b,player));body=value.to_bytes(2,'little',signed=True)
            part.extend(body);peak=max(peak,abs(value));nonzero+=value!=0;saturation+=value in (-32768,32767);power+=value*value
        digest.update(part)
    return dict(bytes=len(pcm)//2,frames=len(pcm)//4,sha256=digest.hexdigest(),peak=peak,
        nonzero_samples=nonzero,saturation_samples=saturation,squared_sum=power)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve()
    need(sys.byteorder=='little' and out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh little-endian ignored reference capture')
    need(sha(DATA.read_bytes())==DATA_SHA,'pinned independent stereo fixture preparation')
    spec=importlib.util.spec_from_file_location('reviewed_complete_gain_data',DATA)
    data=importlib.util.module_from_spec(spec);spec.loader.exec_module(data)
    out.mkdir(parents=True)
    report=dict(passed=False,decoder_executed=False,native_target_executed=False,production_gain_qualified=False,
        normalization_enabled=False,header_zero_policy='legacy Q15 channel-round then truncating mono average',
        nonzero_header_policy='wide combined header/player mono, one nearest-away round and saturation',
        sources=[],references=[],vectors=[])
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,relative):
        body=path.read_bytes();copy=out/'sources'/relative;copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(body)
        report['sources'].append(dict(path=path.relative_to(ROOT).as_posix(),snapshot=copy.relative_to(out).as_posix(),bytes=len(body),sha256=sha(body)))
    save()
    try:
        freeze(Path(__file__).resolve(),Path('controller.py'));freeze(DATA,Path('independent-data.py'))
        stocks={}
        for name,pin in data.FIXTURES.items():
            path=data.STOCK/pin['stock_file'];raw=path.read_bytes()
            need(len(raw)==pin['raw_bytes'] and sha(raw)==pin['raw_sha'],'complete unchanged stock raw PCM')
            freeze(path,Path(name)/'stock-raw.pcm');pcm=raw[312*4:528312*4]
            need(len(pcm)==2112000 and sha(pcm)==pin['logical_sha'],'exact independently positioned retained stereo span')
            stocks[name]=pcm
        entries=0
        for label,gain in data.GAINS:
            for volume in data.VOLUMES:
                table=None
                if gain:
                    table=sum_table(gain,volume,100)
                    need(table==sum_table(gain,volume,160),'all possible stereo signed16 sums stable at100/160 Decimal digits')
                    entries+=len(table)
                for name,pcm in stocks.items():
                    row=full_mono(pcm,gain,volume,table)
                    need(row['bytes']==1056000 and row['frames']==528000,'every retained stereo frame contributes one mono sample')
                    if volume==0 or gain==-32768:need(row['nonzero_samples']==0,'exact complete mono mute/extreme silence')
                    if gain==12288 and volume==1:need(row['saturation_samples']==0 and row['peak']>1000,'anti-early-clipping final mono remains unsaturated and audible')
                    report['references'].append(dict(id=name+'_'+label,fixture=name,gain_q8=gain,volume=volume,balance=0,
                        player_q15=coefficient(volume,16),normalization=False,**row))
                save()
        pairs=[(-32768,-32768),(32767,32767),(-32768,32767),(32767,-32768),
            (30000,-30000),(-30000,30000),(30000,1000),(1000,30000),(-30000,-1000),(-1000,-30000),
            (20000,20000),(-20000,-20000),(1,0),(0,1),(-1,0),(0,-1),(3,-2),(-3,2),(0,0),(15293,-14000)]
        gains=sorted({gain for _,gain in data.GAINS}|{-1,1})
        for gain in gains:
            for volume in data.VOLUMES:
                for balance in (-16,-8,0,8,16):
                    for channels in (1,2):
                        for left,right in pairs:
                            value=mono_sample(left,right,channels,gain,volume,balance,100)
                            need(value==mono_sample(left,right,channels,gain,volume,balance,160),'selected layout/balance vectors stable at100/160 digits')
                            report['vectors'].append(dict(left=left,right=right,channels=channels,gain_q8=gain,
                                volume=volume,balance=balance,expected=value))
        for row in report['sources']:
            need(sha((ROOT/row['path']).read_bytes())==row['sha256']==sha((out/row['snapshot']).read_bytes()),'independent source/stock snapshot unchanged')
        report.update(passed=True,all_source_bindings_current=True,decimal_precision_digits=[100,160],
            checked_stereo_sum_entries=entries,full_references=len(report['references']),selected_vectors=len(report['vectors']))
        save();print(json.dumps(dict(passed=True,full_mono_references=len(report['references']),exact_mono_vectors=len(report['vectors']),
            checked_stereo_sum_entries=entries,decoder_executed=False,production_gain_qualified=False)))
        return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));save()
        print(json.dumps(dict(passed=False,failure=report['failure'])));return 1


if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
