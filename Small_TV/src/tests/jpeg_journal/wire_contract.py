"""Independently parse actual C-written journal banks with Python struct/zlib/SHA."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib


def decode(bank,page_bytes):
    """V1 wire interpretation, independent of the C encoder and CRC algorithm."""
    body=bank[:512]
    assert body[:8]==b'STVJC01\0'
    version,length,generation=struct.unpack_from('<IIQ',body,8)
    assert version==1 and length==512 and generation>0
    frame_bytes,source_limit,slots=struct.unpack_from('<III',body,88)
    assert (frame_bytes,source_limit,slots)==(115200,0x19000,5)
    assert body[100:112]==b'\0'*12 and body[472:508]==b'\0'*36
    crc=struct.unpack_from('<I',body,508)[0]
    assert zlib.crc32(body[:508])==crc
    expected_footer=b'STVCMT1\0'+struct.pack('<QII',generation,crc,crc^0xffffffff)+b'\xff'*(page_bytes-24)
    assert bank[4096-page_bytes:]==expected_footer
    entries=[]
    for slot in range(5):
        raw=body[112+72*slot:112+72*(slot+1)]
        ready,source_bytes=struct.unpack_from('<II',raw)
        assert ready in (0,1)
        if not ready:assert raw==b'\0'*72
        else:assert 0<source_bytes<=source_limit
        entries.append(dict(ready=bool(ready),source_bytes=source_bytes,
                            source_sha256=raw[8:40].hex(),frame_sha256=raw[40:72].hex()))
    return dict(generation=generation,layout_id=body[24:56].hex(),codec_id=body[56:88].hex(),entries=entries)


def frame_sha(slot,newer):
    """Literal full pixel oracle; no production/storage/color code imported."""
    return hashlib.sha256(bytes(((i*37+(i>>7)*19+slot*41)^(0x6d if newer else 0xb2))&255
                               for i in range(115200))).hexdigest()


def main():
    """Bind persisted identities and every slot to actual physical-frame fixtures."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args()
    plan=json.loads((args.run/'plan.json').read_text())
    records=[]
    for page_bytes in (128,256):
        path=args.run/f'complete-{page_bytes}.bin'
        raw=path.read_bytes();assert len(raw)==8192
        states=[decode(raw[i:i+4096],page_bytes) for i in (0,4096)]
        states.sort(key=lambda row:row['generation'])
        assert [row['generation'] for row in states]==[7,8]
        for state in states:
            assert state['layout_id']==plan['layout_id'] and state['codec_id']==plan['journal_test_codec_id']
            for slot,entry in enumerate(state['entries']):
                ready=state['generation']==8 or slot!=0
                assert entry['ready']==ready
                if not ready:continue
                newer=slot==0
                source=b'\xc7'*293 if newer else bytes((slot+i*3)&255 for i in range(293))
                assert entry['source_bytes']==293 and entry['source_sha256']==hashlib.sha256(source).hexdigest()
                assert entry['frame_sha256']==frame_sha(slot,newer)
        records.append(dict(page_bytes=page_bytes,file=path.name,sha256=hashlib.sha256(raw).hexdigest(),states=states))
    report=dict(passed=True,scope=__doc__,page_geometries=2,snapshots=4,records=records,
                parser_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    with (args.run/'wire-report.json').open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(report,indent=2)+'\n')
    print('PASS independent wire: 4snapshots, CRC/footer/order/identities/all5slots')


if __name__=='__main__':
    main()
