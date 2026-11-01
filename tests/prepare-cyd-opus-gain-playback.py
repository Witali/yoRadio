"""Prepare independent gain/volume vectors and complete CRC-valid Opus views.

Only new ignored data captures are written. This neither executes a decoder nor
qualifies a production gain implementation. Decimal references operate on the
captured stock integer PCM, with combined gain before rounding/saturation.
Mono mixing/normalizer policy is deliberately outside these stereo vectors.
"""
import argparse
from array import array
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP, localcontext
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
STOCK=ROOT/'.build/cyd-opus-position-oracle-20261101-01'
GAINS=[('ZERO',0),('PLUS6',1536),('MINUS6',-1536),('PLUS20',5120),
       ('PLUS48',12288),('MAX',32767),('MIN',-32768)]
VOLUMES=[0,1,127,254]
FIXTURES={
    'OPUS20':dict(path='tests/fixtures/esp32c3_calibration/opus-510.ogg',bytes=706319,
        sha256='53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11',
        raw_bytes=2115840,raw_sha='a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b',
        logical_sha='b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f',stock_file='F20-vendor-raw.pcm'),
    'OPUS120':dict(path='tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg',bytes=707097,
        sha256='b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679',
        raw_bytes=2119680,raw_sha='670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684',
        logical_sha='4110db997c16a05c329284bb6105468752c25d67818e3a99b8c9d47c5f481fd0',stock_file='F120-vendor-raw.pcm'),
}


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(body):return hashlib.sha256(body).hexdigest()


def crc(body):
    value=0
    for byte in body:
        value^=byte<<24
        for _ in range(8):value=((value<<1)^(0x04c11db7 if value&0x80000000 else 0))&0xffffffff
    return value


def parse(body):
    at=0;pages=[];packets=[];pending=bytearray();serial=None
    while at<len(body):
        need(at+27<=len(body) and body[at:at+5]==b'OggS\0','complete Ogg v0 header')
        n=body[at+26];need(at+27+n<=len(body),'complete lacing table')
        lace=body[at+27:at+27+n];end=at+27+n+sum(lace)
        need(end<=len(body),'complete encoded page')
        page=body[at:end];stored=int.from_bytes(page[22:26],'little')
        need(crc(page[:22]+bytes(4)+page[26:])==stored,'actual Ogg CRC')
        current=int.from_bytes(page[14:18],'little')
        if serial is None:serial=current
        need(serial==current and int.from_bytes(page[18:22],'little')==len(pages),'one consecutive logical stream')
        flags=page[5]
        need(not flags&~7 and bool(flags&1)==bool(pending) and bool(flags&2)==(at==0) and bool(flags&4)==(end==len(body)),
             'actual complete BOS/continuation/EOS')
        payload=at+27+n;pos=payload
        for size in lace:
            pending.extend(body[pos:pos+size]);pos+=size
            if size<255:packets.append(bytes(pending));pending.clear()
        pages.append(dict(offset=at,end=end,payload=payload,serial=current,
            sequence=len(pages),granule=int.from_bytes(page[6:14],'little')))
        at=end
    need(not pending and len(packets)>2 and packets[0][:9]==b'OpusHead\1' and len(packets[0])==19 and
         packets[0][9]==2 and packets[0][18]==0 and packets[1].startswith(b'OpusTags'),'complete stereo family-zero Opus stream')
    tags=packets[1];pos=8
    need(pos+4<=len(tags),'vendor tag length');vendor=int.from_bytes(tags[pos:pos+4],'little');pos+=4+vendor
    need(pos+4<=len(tags),'comment count');count=int.from_bytes(tags[pos:pos+4],'little');pos+=4
    comments=[]
    for _ in range(count):
        need(pos+4<=len(tags),'comment length');n=int.from_bytes(tags[pos:pos+4],'little');pos+=4
        need(pos+n<=len(tags),'complete comment');comments.append(tags[pos:pos+n]);pos+=n
    need(not any(tag.upper().startswith((b'R128_TRACK_GAIN=',b'R128_ALBUM_GAIN=')) for tag in comments),'no inconsistent existing R128 gain tag')
    return pages,packets


def mutate(body,pages,gain,serial):
    need(isinstance(gain,int) and -32768<=gain<=32767 and 0<=serial<=0xffffffff,'signed gain and complete serial domain')
    changed=bytearray(body);gain_at=pages[0]['payload']+16
    changed[gain_at:gain_at+2]=gain.to_bytes(2,'little',signed=True)
    for page in pages:
        at,end=page['offset'],page['end']
        changed[at+14:at+18]=serial.to_bytes(4,'little');changed[at+22:at+26]=bytes(4)
        changed[at+22:at+26]=crc(changed[at:end]).to_bytes(4,'little')
    return bytes(changed)


def q15(volume):
    need(isinstance(volume,int) and 0<=volume<=254,'existing player volume domain')
    # Independent integer evaluation of the current zero-balance channel gain.
    denominator=254*16
    return (volume*16*32768+denominator//2)//denominator


def decimal_table(gain,player,precision):
    with localcontext() as context:
        context.prec=precision
        header=Decimal(10)**(Decimal(gain)/Decimal(5120))
        factor=header*Decimal(player)/Decimal(32768)
        encoded=[];values=[];early=[]
        for unsigned in range(65536):
            sample=unsigned if unsigned<32768 else unsigned-65536
            rounded=int((Decimal(sample)*factor).to_integral_value(rounding=ROUND_HALF_UP))
            value=max(-32768,min(32767,rounded));values.append(value);encoded.append(value.to_bytes(2,'little',signed=True))
            header_only=int((Decimal(sample)*header).to_integral_value(rounding=ROUND_HALF_UP))
            clipped=max(-32768,min(32767,header_only))
            after=int((Decimal(clipped)*Decimal(player)/Decimal(32768)).to_integral_value(rounding=ROUND_HALF_UP))
            early.append(max(-32768,min(32767,after)))
        return encoded,values,early,str(header),str(factor)


def full_reference(samples,histogram,encoded,values,early):
    digest=hashlib.sha256()
    for at in range(0,len(samples),4096):digest.update(b''.join(encoded[n] for n in samples[at:at+4096]))
    peak=nonzero=saturated=power=changed_by_early_clip=0
    for unsigned,count in histogram.items():
        sample=values[unsigned];peak=max(peak,abs(sample));nonzero+=count*(sample!=0)
        saturated+=count*(sample in (-32768,32767));power+=count*sample*sample
        changed_by_early_clip+=count*(sample!=early[unsigned])
    return dict(bytes=len(samples)*2,sha256=digest.hexdigest(),samples=len(samples),peak=peak,
                nonzero_samples=nonzero,saturation_samples=saturated,squared_sum=power,
                differs_from_header_clip_then_player_samples=changed_by_early_clip)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve()
    need(sys.byteorder=='little' and out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh little-endian host capture')
    out.mkdir(parents=True)
    report=dict(passed=False,decoder_executed=False,native_target_executed=False,production_gain_qualified=False,
                reference_policy='combined stereo integer-PCM gain before one nearest-away rounding/saturation',
                mono_mixing_policy_qualified=False,normalizer_policy_qualified=False,numeric_codec_conformance_claim=False,
                sources=[],variants=[],references=[],vectors=[],guards=[])
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,relative):
        target=out/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);body=path.read_bytes();target.write_bytes(body)
        report['sources'].append(dict(path=path.relative_to(ROOT).as_posix(),snapshot=target.relative_to(out).as_posix(),bytes=len(body),sha256=sha(body)))
    save()
    try:
        freeze(Path(__file__).resolve(),Path('controller.py'))
        stocks={};all_views={}
        for number,(name,pin) in enumerate(FIXTURES.items()):
            path=ROOT/pin['path'];encoded=path.read_bytes();need(len(encoded)==pin['bytes'] and sha(encoded)==pin['sha256'],'complete unchanged original fixture')
            freeze(path,Path(name)/'original.ogg');pages,packets=parse(encoded)
            need(int.from_bytes(packets[0][16:18],'little',signed=True)==0,'original gain is zero')
            preskip=int.from_bytes(packets[0][10:12],'little');end=pages[-1]['granule']
            need(preskip==312 and end==528312,'actual header/end timeline')
            raw_path=STOCK/pin['stock_file'];raw=raw_path.read_bytes()
            need(len(raw)==pin['raw_bytes'] and sha(raw)==pin['raw_sha'],'complete actual stock PCM identity')
            freeze(raw_path,Path(name)/'stock-raw.pcm');logical=raw[preskip*4:end*4]
            need(len(logical)==2112000 and sha(logical)==pin['logical_sha'],'independently positioned exact stock logical PCM')
            samples=array('H');samples.frombytes(logical);stocks[name]=(samples,Counter(samples))
            for index,(label,gain) in enumerate(GAINS):
                serial=pages[0]['serial'] if gain==0 else 0x47500000+number*256+index
                body=mutate(encoded,pages,gain,serial);modified,new_packets=parse(body)
                need(new_packets[1:]==packets[1:] and modified[-1]['granule']==end and
                     int.from_bytes(new_packets[0][16:18],'little',signed=True)==gain,'all comments/audio and timeline preserved')
                if gain==0:need(body==encoded,'zero-gain bytes are exactly original')
                allowed=set(range(pages[0]['payload']+16,pages[0]['payload']+18))
                for page in pages:allowed.update(range(page['offset']+14,page['offset']+18));allowed.update(range(page['offset']+22,page['offset']+26))
                need(all(i in allowed for i,(a,b) in enumerate(zip(encoded,body)) if a!=b),'only gain/serial/CRC metadata changes')
                file=out/(name+'_'+label+'.ogg');file.write_bytes(body);all_views[name+'_'+label]=body
                patches=[]
                for i,page in enumerate(pages):
                    # First ID page includes the complete19-byte head; later patches are only27-byte page headers.
                    stop=page['end'] if i==0 else page['offset']+27
                    patches.append(dict(offset=page['offset'],bytes=stop-page['offset'],header_hex=body[page['offset']:stop].hex()))
                report['variants'].append(dict(id=name+'_'+label,fixture=name,gain_q8=gain,serial=serial,bytes=len(body),sha256=sha(body),
                    pages=len(pages),audio_packets=len(packets)-2,preskip=preskip,eos_granule=end,patches=patches,local_file=file.name))
            save()
        selected=[-32768,-32767,-20000,-10000,-513,-2,-1,0,1,2,513,10000,20000,32766,32767]
        for label,gain in GAINS:
            for volume in VOLUMES:
                player=q15(volume)
                table,values,early,header,factor=decimal_table(gain,player,100)
                second,second_values,second_early,_,_=decimal_table(gain,player,160)
                need(table==second and values==second_values and early==second_early,'all65536 signed16 sample references stable at100/160 Decimal digits')
                for sample in selected:
                    unsigned=sample if sample>=0 else sample+65536
                    report['vectors'].append(dict(gain_q8=gain,volume=volume,player_q15=player,input=sample,expected=values[unsigned]))
                for name,(samples,histogram) in stocks.items():
                    result=full_reference(samples,histogram,table,values,early)
                    need(result['bytes']==2112000 and result['samples']==1056000,'complete full-stream stereo reference span')
                    if gain==0 and volume==254:need(result['sha256']==FIXTURES[name]['logical_sha'],'zero header/unity player byte identity')
                    if volume==0 or gain==-32768:need(result['nonzero_samples']==0,'combined mute/negative-extreme silence')
                    if gain==32767 and volume==254:need(result['saturation_samples']==result['nonzero_samples'],'positive extreme saturates every nonzero stock sample')
                    if gain==12288 and volume==1:need(result['differs_from_header_clip_then_player_samples']>900000 and result['saturation_samples']==0,
                        'full-fixture anti-early-saturation control remains below final clipping')
                    report['references'].append(dict(id=name+'_'+label,fixture=name,gain_q8=gain,volume=volume,player_q15=player,
                        header_factor_decimal=header,combined_factor_decimal=factor,**result))
                save()
        chain=['OPUS20_PLUS6','OPUS120_MINUS6','OPUS20_ZERO','OPUS20_MAX','OPUS120_MIN','OPUS120_ZERO','OPUS20_MINUS6','OPUS120_PLUS6']
        need(len({next(row['serial'] for row in report['variants'] if row['id']==name) for name in chain})==len(chain),
             'all concatenated Opus logical-stream serials distinct')
        report['opus_chain_views']=dict(ids=chain,encoded_bytes=sum(len(all_views[name]) for name in chain),
            sha256=sha(b''.join(all_views[name] for name in chain)),vorbis_bypass_to_be_added_by_native_gate=True)
        for name,pin in FIXTURES.items():
            body=(ROOT/pin['path']).read_bytes();pages,_=parse(body)
            try:parse(body[:pages[0]['end']-1])
            except ValueError:report['guards'].append(name+' truncated-head rejected')
            else:need(False,'truncated head accepted')
            bad=bytearray(body);bad[pages[0]['payload']+16]^=1
            try:parse(bad)
            except ValueError:report['guards'].append(name+' gain-without-new-crc rejected')
            else:need(False,'unverified gain mutation accepted')
        for row in report['sources']:
            need(sha((ROOT/row['path']).read_bytes())==row['sha256']==sha((out/row['snapshot']).read_bytes()),'frozen original inputs unchanged')
        report.update(passed=True,all_source_bindings_current=True,decimal_precision_digits=[100,160],
            distinct_signed16_tables=len(GAINS)*len(VOLUMES),signed16_table_entries=65536*len(GAINS)*len(VOLUMES))
        save();print(json.dumps(dict(passed=True,variants=len(report['variants']),full_stereo_references=len(report['references']),
            exact_small_vectors=len(report['vectors']),signed16_table_entries=report['signed16_table_entries'],
            decoder_executed=False,native_target_executed=False,production_gain_qualified=False)))
        return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));save()
        print(json.dumps(dict(passed=False,failure=report['failure'])));return 1


if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
