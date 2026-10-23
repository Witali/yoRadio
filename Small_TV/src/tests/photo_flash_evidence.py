"""Independent readback of canonical JPEG journal/source/physical RGB565 bytes."""
import hashlib
import struct
import zlib


def digest(data):
    """Hash the actual physical image slice, not a copied readiness flag."""
    return hashlib.sha256(data).hexdigest()


def materialize(flash,extents,length):
    """Read exactly the logical prefix of a generated scattered allocation."""
    result=bytearray()
    for extent in extents:
        offset,size=extent['offset'],extent['bytes']
        assert 0<=offset<=len(flash)-size
        result.extend(flash[offset:offset+min(size,length-len(result))])
        if len(result)==length:break
    assert len(result)==length
    return bytes(result)


def journal(flash,plan):
    """Choose the newest valid committed bank before checking its build identity."""
    metadata=materialize(flash,plan['metadata']['extents'],8192);valid=[]
    for bank in range(2):
        sector=metadata[bank*4096:(bank+1)*4096];body,footer=sector[:512],sector[-256:]
        if body[:8]!=b'STVJC01\0' or struct.unpack_from('<II',body,8)!=(1,512):continue
        generation=struct.unpack_from('<Q',body,16)[0];crc=struct.unpack_from('<I',body,508)[0]
        if not generation or zlib.crc32(body[:508])!=crc:continue
        if footer[:8]!=b'STVCMT1\0' or struct.unpack_from('<QII',footer,8)!=(generation,crc,crc^0xffffffff):continue
        if footer[24:]!=b'\xff'*232:continue
        if struct.unpack_from('<III',body,88)!=(115200,102400,5) or any(body[100:112]) or any(body[472:508]):continue
        entries=[];canonical=True
        for slot in range(5):
            entry=body[112+slot*72:184+slot*72];ready,length=struct.unpack_from('<II',entry)
            if ready not in (0,1) or ready and not 0<length<=102400 or not ready and any(entry):canonical=False;break
            entries.append(dict(ready=bool(ready),source_bytes=length,source_sha256=entry[8:40].hex(),frame_sha256=entry[40:72].hex()))
        if canonical:valid.append(dict(bank=bank,generation=generation,body=body,entries=entries))
    assert valid,'No complete canonical JPEG journal bank'
    valid.sort(key=lambda row:row['generation'],reverse=True);head=valid[0]
    if len(valid)==2 and valid[0]['generation']==valid[1]['generation']:assert valid[0]['body']==valid[1]['body'],'Ambiguous generation'
    assert head['body'][24:56].hex()==plan['layout_id'] and head['body'][56:88].hex()==plan['cache_codec_id'],'Newest journal belongs to another layout/codec'
    return {name:value for name,value in head.items() if name!='body'}


def ready_frame(flash,plan,slot,source_sha256,frame_sha256):
    """Check ready metadata AND full source/frame bytes against independent hashes."""
    head=journal(flash,plan);entry=head['entries'][slot];assert entry['ready']
    source=flash[0x200000+slot*102400:0x200000+slot*102400+entry['source_bytes']]
    pixels=materialize(flash,plan['caches'][slot]['extents'],115200)
    assert digest(source)==entry['source_sha256']==source_sha256
    assert digest(pixels)==entry['frame_sha256']==frame_sha256
    return dict(bank=head['bank'],generation=head['generation'],source_bytes=entry['source_bytes'],
                source_sha256=source_sha256,frame_sha256=frame_sha256,physical_frame_bytes=len(pixels))


def rejection_checks(flash,plan,slot,source_sha256,frame_sha256):
    """Reject source/frame damage and a newer foreign record with valid CRC/commit."""
    ready_frame(flash,plan,slot,source_sha256,frame_sha256);head=journal(flash,plan)
    bank_offset=plan['metadata']['extents'][0]['offset']+head['bank']*4096
    rejected=[]
    for name in ('source-byte','frame-byte','newest-foreign-codec'):
        changed=bytearray(flash)
        if name=='source-byte':changed[0x200000+slot*102400+2]^=1
        elif name=='frame-byte':changed[plan['caches'][slot]['extents'][0]['offset']]^=1
        else:
            changed[bank_offset+56]^=1
            crc=zlib.crc32(changed[bank_offset:bank_offset+508])
            struct.pack_into('<I',changed,bank_offset+508,crc)
            struct.pack_into('<II',changed,bank_offset+4096-256+16,crc,crc^0xffffffff)
        try:ready_frame(changed,plan,slot,source_sha256,frame_sha256)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('Unsafe flash evidence accepted: '+name)
    return rejected
