"""Read a single logical Ogg/Vorbis stream for independent test accounting."""
import struct
from run_vorbis_lifecycle import ogg_crc


def packets(data):
    result=[]; pending=bytearray(); pos=0; serial=None; sequence=0
    while pos<len(data):
        if data[pos:pos+4]!=b'OggS' or pos+27>len(data): raise ValueError('Truncated Ogg header')
        count=data[pos+26]; laces=data[pos+27:pos+27+count]
        end=pos+27+count+sum(laces)
        if len(laces)!=count or end>len(data): raise ValueError('Truncated Ogg body')
        page=bytearray(data[pos:end]); checksum=struct.unpack_from('<I',page,22)[0]; page[22:26]=bytes(4)
        if ogg_crc(page)!=checksum: raise ValueError('Ogg CRC')
        page_serial,page_sequence=struct.unpack_from('<II',page,14)
        if serial is None: serial=page_serial
        if page_serial!=serial or page_sequence!=sequence: raise ValueError('Not a consecutive single stream')
        if bool(page[5]&1)!=bool(pending): raise ValueError('Invalid continuation')
        sequence+=1; offset=pos+27+count; completed=[]
        for size in laces:
            pending.extend(data[offset:offset+size]); offset+=size
            if size<255:
                completed.append(len(result)); result.append(dict(data=bytes(pending),granule=-1,eos=False))
                pending.clear()
        if completed:
            result[completed[-1]]['granule']=struct.unpack_from('<q',page,6)[0]
            result[completed[-1]]['eos']=bool(page[5]&4)
        pos=end
    if pending: raise ValueError('Unterminated Ogg packet')
    if len(result)<3: raise ValueError('Missing Vorbis headers')
    for kind,packet in zip((1,3,5),result):
        if packet['data'][:7]!=bytes([kind])+b'vorbis': raise ValueError('Invalid Vorbis headers')
    return result
