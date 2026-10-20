"""Inspect public fixture syntax/accounting only; no codec or process execution."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'.build/cyd-vorbis-format-prep-01/project/main/fixture.h'

class Bits:
    def __init__(self,data): self.data,self.pos = data,0
    def get(self,n):
        if n < 0 or self.pos+n > len(self.data)*8: raise ValueError('Truncated public setup')
        out = sum(((self.data[(self.pos+i)//8] >> ((self.pos+i)%8)) & 1) << i for i in range(n))
        self.pos += n
        return out
    def skip(self,n):
        if n < 0 or self.pos+n > len(self.data)*8: raise ValueError('Truncated public setup lookup')
        self.pos += n

def inspect_setup(data,channels):
    b=Bits(data); books=b.get(8)+1
    for _ in range(books):
        assert b.get(24)==0x564342
        dim,entries=b.get(16),b.get(24)
        assert dim and entries
        if b.get(1):
            length,current=b.get(5)+1,0
            while current < entries:
                assert length <= 32
                count=b.get((entries-current).bit_length()); assert current+count <= entries
                current += count; length += 1
        else:
            sparse=b.get(1)
            for _ in range(entries):
                if not sparse or b.get(1): b.get(5)
        lookup=b.get(4); assert lookup <= 2
        if lookup:
            b.get(32); b.get(32); width=b.get(4)+1; b.get(1)
            if lookup==1:
                lo,hi=1,entries+1
                while hi-lo > 1:
                    mid=(hi+lo)//2
                    if mid**dim <= entries: lo=mid
                    else: hi=mid
                count=lo
            else: count=entries*dim
            b.skip(count*width)
    for _ in range(b.get(6)+1): assert b.get(16)==0
    floors=[]
    for _ in range(b.get(6)+1):
        kind=b.get(16); assert kind==1
        classes=[b.get(4) for _ in range(b.get(5))]; dimensions=[]
        for _ in range(max(classes,default=-1)+1):
            dimensions.append(b.get(3)+1); subclasses=b.get(2)
            if subclasses: assert b.get(8) < books
            for _ in range(1 << subclasses): assert b.get(8)-1 < books
        multiplier,width=b.get(2)+1,b.get(4)
        xs=[0,1 << width]
        for cls in classes:
            xs += [b.get(width) for _ in range(dimensions[cls])]
        assert len(xs)==len(set(xs))
        floors.append(dict(type=kind,multiplier=multiplier,rangebits=width,x_list=xs))
    residues=[]
    for _ in range(b.get(6)+1):
        kind,begin,end=b.get(16),b.get(24),b.get(24); assert kind<=2 and begin<=end
        partition,classes,book=b.get(24)+1,b.get(6)+1,b.get(8); assert book < books
        cascades=[]
        for _ in range(classes):
            low=b.get(3); high=b.get(5) if b.get(1) else 0; cascades.append(low | high << 3)
        for cascade in cascades:
            for bit in range(8):
                if cascade & (1 << bit): assert b.get(8) < books
        residues.append(dict(type=kind,begin=begin,end=end,partition=partition))
    mappings=[]
    for _ in range(b.get(6)+1):
        assert b.get(16)==0
        submaps=b.get(4)+1 if b.get(1) else 1; coupling=[]
        if b.get(1):
            for _ in range(b.get(8)+1):
                magnitude,angle=b.get((channels-1).bit_length()),b.get((channels-1).bit_length())
                assert magnitude != angle and magnitude < channels and angle < channels
                coupling.append([magnitude,angle])
        assert b.get(2)==0
        mux=[b.get(4) for _ in range(channels)] if submaps > 1 else [0]*channels
        assert all(x < submaps for x in mux)
        submap=[]
        for _ in range(submaps):
            assert b.get(8)==0
            floor,residue=b.get(8),b.get(8); assert floor<len(floors) and residue<len(residues)
            submap.append(dict(floor=floor,residue=residue))
        mappings.append(dict(mux=mux,coupling=coupling,submaps=submap))
    modes=[]
    for _ in range(b.get(6)+1):
        flag=b.get(1); assert b.get(16)==b.get(16)==0
        mapping=b.get(8); assert mapping < len(mappings)
        modes.append(dict(blockflag=flag,mapping=mapping))
    assert b.get(1)==1 and b.get(len(data)*8-b.pos)==0
    return dict(codebooks=books,floors=floors,residues=residues,mappings=mappings,modes=modes)

def main():
    raw=SOURCE.read_bytes(); header=raw.decode()
    def array(name):
        body=re.search(r'\b'+name+r'\[\]\s*=\s*\{([^}]+)\}',header).group(1)
        return [int(x) for x in body.split(',') if x.strip()]
    info,setup,audio=map(lambda n:bytes(array(n)),('fixture_info','fixture_setup','fixture_packets'))
    offsets,flags=array('fixture_offsets'),array('fixture_long_mode')
    assert len(info)==23 and info[4]==2 and len(offsets)==69 and flags==[0]+[1]*67
    summary=inspect_setup(setup,info[4]); packets=[]
    for i,(a,z) in enumerate(zip(offsets,offsets[1:])):
        bits=Bits(audio[a:z]); assert bits.get(1)==0
        mode=bits.get((len(summary['modes'])-1).bit_length()); flag=summary['modes'][mode]['blockflag']
        assert flag==flags[i]
        packets.append(dict(packet=i,mode=mode,blockflag=flag,previous=bits.get(1) if flag else None,next=bits.get(1) if flag else None))
    result=dict(schema='public-vorbis-block-matrix-source-inspection-v1',source=SOURCE.relative_to(ROOT).as_posix(),
        source_sha256=hashlib.sha256(raw).hexdigest(),setup_sha256=hashlib.sha256(setup).hexdigest(),
        audio_sha256=hashlib.sha256(audio).hexdigest(),setup=summary,packet_headers=packets,
        codec_or_reference_execution=False,validity_qualified=False)
    (HERE/'fixture-inspection.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(source=result['source'],floors=summary['floors'],mappings=summary['mappings'],modes=summary['modes'],packet_headers=[packets[0],packets[1],packets[-1]])))

if __name__=='__main__': main()
