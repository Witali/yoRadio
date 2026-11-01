"""Independent data-only Ogg framing of creator multistream encoder packets."""
import hashlib
import struct


def need(value,why):
    if not value:raise ValueError(why)


def sha(body):return hashlib.sha256(body).hexdigest()


def crc(body):
    value=0
    for byte in body:
        value^=byte<<24
        for _ in range(8):value=((value<<1)^(0x04c11db7 if value&0x80000000 else 0))&0xffffffff
    return value


def packets(body):
    need(len(body)>=40 and body[:8]==b'OFAM101\0','complete public packet transport')
    channels,streams,coupled,pre_skip,frames,count=struct.unpack_from('<6I',body,8);mapping=list(body[32:32+channels])
    need(channels in (3,6,8) and streams+coupled==channels and coupled<=streams and 0<pre_skip<960 and frames==9600 and count==11,
         'complete measured creator family1 geometry')
    need(len(set(mapping))==channels and sorted(mapping)==list(range(channels)),'creator default surround permutation includes every channel')
    at=40;result=[]
    for _ in range(count):
        need(at+4<=len(body),'complete packet length');n=struct.unpack_from('<I',body,at)[0];at+=4
        need(0<n<=61440 and at+n<=len(body),'complete bounded encoded packet');result.append(body[at:at+n]);at+=n
    need(at==len(body),'exact complete packet transport')
    return dict(channels=channels,streams=streams,coupled=coupled,pre_skip=pre_skip,frames=frames,count=count,mapping=mapping),result


def page(packet,serial,sequence,gp,flags):
    lace=bytes([255]*(len(packet)//255)+[len(packet)%255]);need(len(lace)<=255,'one complete packet per bounded page')
    value=bytearray(struct.pack('<4sBBQIIIB',b'OggS',0,flags,gp,serial,sequence,0,len(lace))+lace+packet)
    struct.pack_into('<I',value,22,crc(value));return bytes(value)


def make(body):
    info,audio=packets(body);c=info['channels'];serial=0x46310000+c
    head=struct.pack('<8sBBHIhB',b'OpusHead',1,c,info['pre_skip'],48000,0,1)+bytes([info['streams'],info['coupled'],*info['mapping']])
    vendor=b'public-libopus-family1-diagnostic';tags=b'OpusTags'+struct.pack('<I',len(vendor))+vendor+struct.pack('<I',0)
    result=page(head,serial,0,0,2)+page(tags,serial,1,0,0)
    for i,packet in enumerate(audio):
        final=i+1==len(audio);gp=info['pre_skip']+info['frames'] if final else (i+1)*960
        result+=page(packet,serial,i+2,gp,4 if final else 0)
    verified=parse(result);need(verified['packets'][2:]==audio,'all complete encoded bodies retained')
    return result,dict(info,serial=serial,bytes=len(result),sha256=sha(result),pages=len(audio)+2,
                       packet_sha256=sha(b''.join(struct.pack('<I',len(p))+p for p in audio)))


def parse(body):
    at=0;result=[];pages=[];serial=None
    while at<len(body):
        need(at+27<=len(body) and body[at:at+5]==b'OggS\0','complete Ogg v0 header')
        n=body[at+26];payload=at+27+n;need(payload<=len(body),'complete lacing');lace=body[at+27:payload];end=payload+sum(lace)
        need(end<=len(body) and n and lace[-1]<255 and all(v==255 for v in lace[:-1]),'one complete packet per page')
        p=bytearray(body[at:end]);stored=struct.unpack_from('<I',p,22)[0];p[22:26]=bytes(4);need(crc(p)==stored,'actual complete page CRC')
        current,seq=struct.unpack_from('<II',p,14);serial=current if serial is None else serial
        need(current==serial and seq==len(pages) and p[5]==(2 if not pages else 4 if end==len(body) else 0),'complete one-serial BOS/EOS sequence')
        pages.append(dict(bytes=end-at,granule=struct.unpack_from('<Q',p,6)[0]));result.append(body[payload:end]);at=end
    need(len(result)==13 and result[0][:8]==b'OpusHead' and result[1][:8]==b'OpusTags','complete headers and eleven audio packets')
    c=result[0][9];need(c in (3,6,8) and result[0][18]==1 and len(result[0])==21+c,'complete family1 header')
    need(pages[0]['granule']==pages[1]['granule']==0 and [p['granule'] for p in pages[2:-1]]==list(range(960,10560,960)),'exact packet granules')
    need(pages[-1]['granule']==int.from_bytes(result[0][10:12],'little')+9600,'exact complete logical EOS')
    return dict(packets=result,pages=pages,channels=c)
