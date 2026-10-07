"""Generate bounded AAC error cases from the retained FAAD FIL trace."""
import argparse
import hashlib
import json
from pathlib import Path

from generate_aac_sbr_gaps import adts_frames,remove_sbr

ROOT=Path(__file__).resolve().parents[2]


def generate(output=ROOT/'tests/fixtures/aac_faults'):
    source=ROOT/'tests/fixtures/aac_sbr_gap'
    output.mkdir(parents=True,exist_ok=True)
    name='hev2-44100-stereo'
    manifest=json.loads((source/'manifest.json').read_text())['cases'][name]
    data=(source/('source-'+name+'.aac')).read_bytes()
    trace=(source/(name+'.trace')).read_bytes()
    assert hashlib.sha256(data).hexdigest()==manifest['source_sha256']
    assert hashlib.sha256(trace).hexdigest()==manifest['trace_sha256']
    frame=adts_frames(data)[0]
    spans=[list(map(int,line.split()[2:])) for line in trace.decode().splitlines() if line.startswith('FIL 0 ')]
    remove_sbr(frame,spans[0],spans[1:]) # Validate all traced boundaries and the untouched core.
    bits=''.join(f'{b:08b}' for b in frame)
    def pack(bits):
        bits+='0'*(-len(bits)%8)
        result=bytearray(int(bits[i:i+8],2) for i in range(0,len(bits),8))
        size=len(result);result[3]=(result[3]&0xfc)|(size>>11)
        result[4]=(size>>3)&255;result[5]=(result[5]&0x1f)|((size&7)<<5)
        return bytes(result)
    cases={'header-only':pack(bits[:56]),
           'sbr-truncated':pack(bits[:spans[0][1]+4])}
    for label,span in zip(('sbr-count-overrun','fill-count-overrun'),spans):
        begin,payload,*_=span
        cases[label]=pack(bits[:begin+3]+'1111'+'11111111'+bits[payload:])
    rows={}
    for name,data in cases.items():
        (output/(name+'.aac')).write_bytes(data)
        rows[name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),expected='no PCM; error or safe frame skip')
    (output/'manifest.json').write_text(json.dumps(dict(source_sha256=manifest['source_sha256'],
        trace_sha256=manifest['trace_sha256'],cases=rows),indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Generated',len(rows),'malformed frames from verified FIL spans')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'tests/fixtures/aac_faults')
    generate(parser.parse_args().output)
