"""Exact pure helper definitions from the pinned public carrier parser."""
import struct

def need(ok,message):
    if not ok: raise RuntimeError(message)

def crc(data):
    result=0
    for value in data:
        result ^= value<<24
        for _ in range(8): result=((result<<1)^0x04c11db7 if result&0x80000000 else result<<1)&0xffffffff
    return result

def packets(data):
    result=[]; pending=bytearray(); pos=0; serial=None; sequence=0
    while pos<len(data):
        need(data[pos:pos+5]==b'OggS\0' and pos+27<=len(data),'Carrier header/version')
        count=data[pos+26]; laces=data[pos+27:pos+27+count]; end=pos+27+count+sum(laces)
        need(len(laces)==count and end<=len(data),'Carrier length')
        page=bytearray(data[pos:end]); expected=struct.unpack_from('<I',page,22)[0]; page[22:26]=bytes(4)
        need(crc(page)==expected,'Carrier CRC')
        stream,number=struct.unpack_from('<II',page,14)
        if serial is None: serial=stream
        need(stream==serial and number==sequence and bool(page[5]&1)==bool(pending),'Carrier sequence/continuation')
        need(bool(page[5]&2)==(sequence==0),'Carrier BOS')
        sequence+=1; offset=pos+27+count; finished=[]
        for size in laces:
            pending.extend(data[offset:offset+size]); offset+=size
            if size<255:
                finished.append(len(result)); result.append(dict(data=bytes(pending),granule=-1,eos=False)); pending.clear()
        if finished:
            result[finished[-1]]['granule']=struct.unpack_from('<q',page,6)[0]
            result[finished[-1]]['eos']=bool(page[5]&4)
        need(not page[5]&4 or end==len(data),'Carrier EOS')
        pos=end
    need(not pending and len(result)>3,'Complete packets required')
    for kind,row in zip((1,3,5),result): need(row['data'][:7]==bytes([kind])+b'vorbis','Vorbis header order')
    return result
