"""Prepare full paired Ogg Opus gain inputs without running a decoder.

Only OpusHead's signed Q7.8 output-gain field and its containing page CRC may
change. Every audio/comment byte, lacing entry, granule and stream ID stays
identical to the pinned complete original fixture. Output is fresh and local.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'tests/fixtures/esp32c3_calibration/opus-510.ogg'
SOURCE_SHA='53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11'
VARIANTS=(('zero',0),('plus6',1536),('minus6',-1536))


def need(value,why):
    if not value: raise ValueError(why)


def sha(body): return hashlib.sha256(body).hexdigest()


def crc_table():
    table=[]
    for value in range(256):
        value <<= 24
        for _ in range(8):value=((value<<1)^(0x04c11db7 if value&0x80000000 else 0))&0xffffffff
        table.append(value)
    return tuple(table)


CRC_TABLE=crc_table()


def crc(body):
    value=0
    for byte in body:value=((value<<8)&0xffffffff)^CRC_TABLE[(value>>24)^byte]
    return value


def parse(body):
    """Complete original-stream page/CRC/continuation accounting, not synthesis."""
    pages=[];packets=[];pending=bytearray();at=0;serial=None
    while at<len(body):
        need(at+27<=len(body) and body[at:at+5]==b'OggS\0','complete Ogg v0 page header')
        n=body[at+26]; payload=at+27+n
        need(payload<=len(body),'complete lacing table')
        lace=body[at+27:payload];end=payload+sum(lace)
        need(end<=len(body),'complete page body')
        page=bytearray(body[at:end]);stored=int.from_bytes(page[22:26],'little');page[22:26]=bytes(4)
        need(crc(page)==stored,'every page CRC valid')
        flags=page[5];current=int.from_bytes(page[14:18],'little');sequence=int.from_bytes(page[18:22],'little')
        if serial is None:serial=current
        need(current==serial and sequence==len(pages),'one consecutive original logical stream')
        need(not flags&~7 and bool(flags&1)==bool(pending),'matching packet continuation flags')
        need(bool(flags&2)==(not pages) and bool(flags&4)==(end==len(body)),'complete BOS/EOS stream')
        pos=payload;first_packet=len(packets)
        for size in lace:
            pending.extend(body[pos:pos+size]);pos+=size
            if size<255:packets.append(bytes(pending));pending.clear()
        pages.append(dict(offset=at,end=end,payload=payload,sequence=sequence,
                          packets=len(packets)-first_packet,sha256=sha(body[at:end])))
        at=end
    need(pages and not pending and len(packets)>=3,'complete packet/stream ending')
    need(packets[0][:8]==b'OpusHead' and len(packets[0])==19 and packets[0][18]==0 and
         pages[0]['packets']==1 and pages[0]['end']-pages[0]['payload']==19,'original family0 ID header alone on first page')
    need(packets[1][:8]==b'OpusTags','original comment header')
    return pages,packets


def comments(packet):
    need(len(packet)>=16 and packet[:8]==b'OpusTags','complete comment prefix')
    at=8
    def span():
        nonlocal at
        need(at+4<=len(packet),'complete comment length')
        n=int.from_bytes(packet[at:at+4],'little');at+=4
        need(n<=len(packet)-at,'comment extent in packet')
        value=packet[at:at+n];at+=n
        return value
    span()
    need(at+4<=len(packet),'complete comment count')
    count=int.from_bytes(packet[at:at+4],'little');at+=4
    need(count<=(len(packet)-at)//4,'bounded complete comment count')
    return [span() for _ in range(count)]


def audio_identity(packets):
    digest=hashlib.sha256()
    for packet in packets[2:]:digest.update(len(packet).to_bytes(4,'little'));digest.update(packet)
    return dict(packets=len(packets)-2,packet_bytes=sum(map(len,packets[2:])),sha256=digest.hexdigest())


def mutate(source,gain_q8):
    need(isinstance(gain_q8,int) and -32768<=gain_q8<=32767,'signed16 Q7.8 output gain')
    pages,packets=parse(source)
    need(not any(value.upper().startswith((b'R128_TRACK_GAIN=',b'R128_ALBUM_GAIN=')) for value in comments(packets[1])),
         'gain-tag metadata must not become inconsistent when changing header gain')
    changed=bytearray(source);start=pages[0]['payload']+16
    changed[start:start+2]=gain_q8.to_bytes(2,'little',signed=True)
    changed[22:26]=bytes(4)
    changed[22:26]=crc(changed[:pages[0]['end']]).to_bytes(4,'little')
    return bytes(changed)


def verify_pair(source,changed,gain_q8):
    old_pages,old_packets=parse(source);pages,packets=parse(changed)
    need(len(changed)==len(source) and len(pages)==len(old_pages),'complete original encoded extent retained')
    start=old_pages[0]['payload']+16
    allowed=set(range(22,26))|{start,start+1}
    differences=[i for i,(old,new) in enumerate(zip(source,changed)) if old!=new]
    need(set(differences)<=allowed,'only gain and corresponding first-page CRC bytes change')
    need(int.from_bytes(packets[0][16:18],'little',signed=True)==gain_q8,'actual signed header gain matches request')
    need(packets[0][:16]+packets[0][18:]==old_packets[0][:16]+old_packets[0][18:] and
         packets[1:]==old_packets[1:],'all other header, comment and audio packet bytes identical')
    need(changed[old_pages[0]['end']:]==source[old_pages[0]['end']:],'all subsequent page bytes identical')
    return dict(gain_q8=gain_q8,gain_db=gain_q8/256,bytes=len(changed),sha256=sha(changed),
                changed_offsets=differences,first_page_end=pages[0]['end'],audio=audio_identity(packets))


def generate(out):
    out=Path(out).resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh capture inside ignored .build')
    source=SOURCE.read_bytes();need(len(source)==706319 and sha(source)==SOURCE_SHA,'complete pinned original fixture')
    pages,packets=parse(source)
    need(int.from_bytes(packets[0][16:18],'little',signed=True)==0,'original zero-gain baseline')
    out.mkdir(parents=True)
    report=dict(schema=1,passed=False,decoder_executed=False,native_target_executed=False,source_sha256=SOURCE_SHA,
                source_bytes=len(source),source_gain_q8=0,pages=len(pages),audio=audio_identity(packets),variants={})
    report_path=out/'manifest.json'
    try:
        for name,value in VARIANTS:
            changed=mutate(source,value);row=verify_pair(source,changed,value)
            (out/(name+'.ogg')).write_bytes(changed);report['variants'][name]=row
        need((out/'zero.ogg').read_bytes()==source,'zero baseline is the exact complete original')
        need(sha(SOURCE.read_bytes())==SOURCE_SHA,'source unchanged by generation')
        report['passed']=True
    finally:report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();report=generate(args.output)
    print(json.dumps(dict(passed=report['passed'],variants=list(report['variants']),audio_packets=report['audio']['packets'],
                          decoder_executed=False,native_target_executed=False)))


if __name__=='__main__':main()
