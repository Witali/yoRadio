"""RFC6716 section3 / AppendixB packet framing only; no codec arithmetic.

Self-delimited views remain byte-identical to the original multistream packet.
The common-framing control removes only AppendixB's extra size field. Creator
public single-stream and multistream synthesis must independently agree before
these controls are supplied to the public ESP32 decoder experiment.
"""
import hashlib
import struct


def need(value,why):
    if not value:raise ValueError(why)


def sha(body):return hashlib.sha256(body).hexdigest()


def frame_samples(toc):
    config=toc>>3
    return (480,960,1920,2880)[config&3] if config<12 else (480,960)[config&1] if config<16 else (120,240,480,960)[config&3]


def split_element(data,self_delimited):
    need(data and isinstance(self_delimited,bool),'nonempty complete packet view and explicit framing')
    code=data[0]&3;at=1;count=1 if code==0 else 2;vbr=code==2;padding=0;known=[]
    def size():
        nonlocal at
        need(at<len(data),'complete frame-size field');value=data[at];at+=1
        if value>=252:
            need(at<len(data),'complete two-byte frame-size field');value+=4*data[at];at+=1
        need(value<=1275,'bounded coded frame');return value
    if code==3:
        need(at<len(data),'complete frame-count byte');control=data[at];at+=1;count=control&63;vbr=bool(control&128)
        need(count and count<=48 and count*frame_samples(data[0])<=5760,'valid frame count and at most120ms')
        if control&64:
            while True:
                need(at<len(data),'complete padding length');value=data[at];at+=1;padding+=254 if value==255 else value
                need(padding<=len(data),'bounded original padding')
                if value<255:break
    if vbr:
        known=[size() for _ in range(count-1)]
    extra_begin=at
    if self_delimited:
        final_size=size();extra_end=at;sizes=known+[final_size] if vbr else [final_size]*count
        end=at+sum(sizes)+padding;need(end<=len(data),'all self-delimited payload and padding present')
        original=data[:end];common=data[:extra_begin]+data[extra_end:end]
    else:
        remaining=len(data)-at-padding;need(remaining>=0,'padding fits complete common packet')
        if vbr:
            last=remaining-sum(known);need(0<=last<=1275,'valid implicit final VBR frame');sizes=known+[last]
        else:
            need(remaining%count==0 and remaining//count<=1275,'equal complete CBR frames');sizes=[remaining//count]*count
        end=len(data);original=common=data;extra_end=extra_begin
    need(count*frame_samples(data[0])<=5760 and all(0<=n<=1275 for n in sizes),'valid complete coded geometry')
    return dict(original=original,common=common,consumed=end,extra_offset=extra_begin,extra_bytes=extra_end-extra_begin,
        code=code,frames=count,samples=count*frame_samples(data[0]),frame_bytes=sizes,padding=padding,self_delimited=self_delimited)


def split_multistream(packet,streams):
    need(isinstance(streams,int) and 1<=streams<=255,'explicit valid stream count');at=0;result=[]
    for stream in range(streams):
        row=split_element(packet[at:],stream+1<streams);row['offset']=at;at+=row['consumed'];result.append(row)
    need(at==len(packet) and len({r['samples'] for r in result})==1,'exact original packet coverage and equal stream durations')
    need(b''.join(r['original'] for r in result)==packet,'every original encoded byte retained')
    return result


def prepare(original_transport,packet_reader):
    info,packets=packet_reader(original_transport);body=b'MSPUB01\0'+original_transport[8:40];rows=[]
    for packet_id,packet in enumerate(packets):
        parts=split_multistream(packet,info['streams']);need(all(p['samples']==960 for p in parts),'selected complete20ms fixture')
        body+=struct.pack('<I',len(packet))+packet;entry=[]
        for stream,p in enumerate(parts):
            body+=struct.pack('<4I',p['offset'],len(p['original']),len(p['common']),int(p['self_delimited']))+p['original']+p['common']
            entry.append({k:v for k,v in p.items() if k not in ('original','common')}|dict(stream=stream,
                original_bytes=len(p['original']),common_bytes=len(p['common']),original_sha256=sha(p['original']),common_sha256=sha(p['common'])))
        rows.append(dict(packet=packet_id,bytes=len(packet),sha256=sha(packet),streams=entry))
    return body,dict(info,original_transport_sha256=sha(original_transport),bytes=len(body),sha256=sha(body),packets=rows)
