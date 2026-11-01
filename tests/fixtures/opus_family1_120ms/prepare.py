"""Creator public repacketizer: retain every original active C8 coded frame in 120/100ms groups."""
import argparse
import ctypes
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
def need(value,why):
    if not value:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True,type=Path);parser.add_argument('--framing',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();out=args.output.resolve();need(not out.exists(),'fresh public creator output');out.mkdir(parents=True)
    spec=importlib.util.spec_from_file_location('qualified_public_framing',args.framing);framing=importlib.util.module_from_spec(spec);spec.loader.exec_module(framing)
    body=args.input.read_bytes();need(body[:8]==b'OFAM101\0','original complete input');c,n,m,pre,logical,count=struct.unpack_from('<6I',body,8);mapping=body[32:40];need((c,n,m,count)==(8,5,3,11),'exact original default C8 source')
    packets=[];at=40
    for _ in range(count):size=struct.unpack_from('<I',body,at)[0];at+=4;packets.append(body[at:at+size]);at+=size
    need(at==len(body),'complete original input');parts=[framing.split_multistream(p,n) for p in packets]
    library=Path('/lib/x86_64-linux-gnu/libopus.so.0').resolve();need(sha(library.read_bytes())=='63ddaf057d71c53090607e0467eb308640c3b39b0f189e5b937e9c397be2f676','unchanged measured installed creator library')
    lib=ctypes.CDLL(str(library));pointer=ctypes.c_void_p;integer=ctypes.c_int;length=ctypes.c_int32;byte=ctypes.c_ubyte;byte_pointer=ctypes.POINTER(byte)
    signatures={'opus_repacketizer_create':([],pointer),'opus_repacketizer_init':([pointer],pointer),'opus_repacketizer_cat':([pointer,byte_pointer,length],integer),
        'opus_repacketizer_get_nb_frames':([pointer],integer),'opus_repacketizer_out':([pointer,byte_pointer,length],length),'opus_repacketizer_destroy':([pointer],None),
        'opus_multistream_decoder_create':([length,integer,integer,integer,byte_pointer,ctypes.POINTER(integer)],pointer),
        'opus_multistream_decode_float':([pointer,byte_pointer,length,ctypes.POINTER(ctypes.c_float),integer,integer],integer),'opus_multistream_decoder_destroy':([pointer],None),'opus_get_version_string':([],ctypes.c_char_p)}
    for name,(arguments,result) in signatures.items():function=getattr(lib,name);function.argtypes=arguments;function.restype=result
    def data(value):return (byte*len(value)).from_buffer_copy(value)
    def frames(common):
        view=framing.split_element(common,False);position=view['extra_offset'];result=[]
        for size in view['frame_bytes']:result.append(common[position:position+size]);position+=size
        need(position+view['padding']==len(common),'complete coded-frame bodies');return result
    def size_field(value):
        need(0<=value<=1275,'coded frame size');first=value if value<252 else 252+(value-252)%4
        return bytes((first,)) if value<252 else bytes((first,(value-first)//4))
    toc=[];cat_events=[];outputs=[];grouped=[]
    for stream in range(n):
        values=[v[stream] for v in parts];configs=[v['common'][0]&0xfc for v in values];need(len(set(configs))==1 and all(v['samples']==960 and v['frames']==1 for v in values),'actual compatible public repacketizer TOC configuration')
        toc.append(dict(stream=stream,top6_values=configs,frame_counts=[v['frames'] for v in values],samples=[v['samples'] for v in values]));stream_groups=[]
        for group,(begin,end) in enumerate(((0,6),(6,11))):
            rp=lib.opus_repacketizer_create();need(bool(rp),'actual creator repacketizer allocation');held=[]
            try:
                for index in range(begin,end):
                    encoded=data(values[index]['common']);held.append(encoded);status=lib.opus_repacketizer_cat(rp,encoded,len(encoded));cat_events.append(dict(stream=stream,group=group,packet=index,result=status));need(status==0,'actual creator public cat success')
                number=lib.opus_repacketizer_get_nb_frames(rp);buffer=(byte*61440)();actual=lib.opus_repacketizer_out(rp,buffer,len(buffer));need(number==end-begin and 0<actual<=len(buffer),'actual complete creator output')
                common=bytes(buffer[:actual]);view=framing.split_element(common,False);need(view['samples']==(end-begin)*960,'actual grouped duration')
                original_frames=[frame for v in values[begin:end] for frame in frames(v['common'])];need(frames(common)==original_frames,'every original coded frame byte preserved in order')
                self_delimited=stream+1<n;encoded=common[:view['extra_offset']]+size_field(view['frame_bytes'][-1])+common[view['extra_offset']:] if self_delimited else common
                check=framing.split_element(encoded,self_delimited);need(check['common']==common and check['samples']==(end-begin)*960,'independent AppendixB framing round trip');stream_groups.append(encoded)
                outputs.append(dict(stream=stream,group=group,frames=number,samples=view['samples'],bytes=actual,coded_sha256=[sha(v) for v in original_frames],common_sha256=sha(common),original_framing_sha256=sha(encoded)))
            finally:lib.opus_repacketizer_destroy(rp)
        grouped.append(stream_groups)
    new_packets=[b''.join(grouped[stream][group] for stream in range(n)) for group in range(2)]
    for group,packet in enumerate(new_packets):need(all(p['samples']==(5760 if group==0 else 4800) for p in framing.split_multistream(packet,n)),'complete independently framed multistream packet')
    def decode(inputs):
        error=integer();decoder=lib.opus_multistream_decoder_create(48000,c,n,m,data(mapping),ctypes.byref(error));need(bool(decoder) and error.value==0,'actual public creator multistream open');result=bytearray()
        try:
            for packet in inputs:
                output=(ctypes.c_float*(5760*c))();actual=lib.opus_multistream_decode_float(decoder,data(packet),len(packet),output,5760,0);need(actual>0,'actual complete creator synthesis');result.extend(ctypes.string_at(output,actual*c*4))
        finally:lib.opus_multistream_decoder_destroy(decoder)
        return bytes(result)
    original_pcm=decode(packets);grouped_pcm=decode(new_packets);need(original_pcm==grouped_pcm and len(original_pcm)==10560*c*4,'exact complete creator float invariance; no tolerance')
    header=bytearray(body[:40]);struct.pack_into('<I',header,28,2);transport=bytes(header)+b''.join(struct.pack('<I',len(p))+p for p in new_packets);(out/'channels8-120ms.packets').write_bytes(transport)
    report=dict(passed=True,libopus_version=lib.opus_get_version_string().decode(),library=dict(path=str(library),sha256=sha(library.read_bytes())),source=dict(bytes=len(body),sha256=sha(body)),framing_source_sha256=sha(args.framing.read_bytes()),
        public_symbols=list(signatures),actual_toc=toc,cat_events=cat_events,outputs=outputs,original_packets=11,grouped_packets=2,durations=[5760,4800],raw_frames=10560,pre_skip=pre,logical_frames=logical,
        every_coded_frame_preserved=True,creator_full_float_exact=True,creator_float=dict(bytes=len(original_pcm),sha256=sha(original_pcm)),transport=dict(bytes=len(transport),sha256=sha(transport)),native_executed=False,new_tolerance_applied=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,public_repacketizer=True,groups=[6,5],durations=[5760,4800],coded_frames=55,creator_float_exact=True,transport_sha256=sha(transport))))
if __name__=='__main__':main()
