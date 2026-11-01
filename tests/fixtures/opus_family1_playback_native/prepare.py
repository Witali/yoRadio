"""Build complete public adapter inputs and independent direct-native framing tables; no synthesis."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
ROOT=Path(__file__).resolve().parents[3]
FRAMING=ROOT/'tests/fixtures/opus_multistream_public/framing.py'
READER=ROOT/'tests/fixtures/opus_header_gain/generate.py'
LONG=ROOT/'tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg'
LONG_SHA='b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679'
def need(value,why):
    if not value:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def build(reference):
    old=json.loads((ROOT/'tests/results/cyd-opus-multistream-public-20261101/manifest.json').read_bytes())
    gain=json.loads((ROOT/'tests/results/cyd-opus-header-gain-20261101/manifest.json').read_bytes())
    need(sha(FRAMING.read_bytes())==old['canonical_source_sha256'][FRAMING.relative_to(ROOT).as_posix()],'frozen independently creator-qualified framing code')
    need(sha(READER.read_bytes())==gain['canonical_source_sha256'][READER.relative_to(ROOT).as_posix()],'frozen complete original120ms reader')
    framing=load_module('adapter_independent_framing',FRAMING);reader=load_module('adapter_original_reader',READER)
    expected=json.loads((ROOT/'tests/results/cyd-opus-family1-20261101/manifest.json').read_bytes())['reference_fixtures'];sources=[]
    for channels in (3,6,8):
        name='channels'+str(channels)+'.packets';body=(reference/name).read_bytes();pin=expected['channels'+str(channels)]['files'][name];need(len(body)==pin['bytes'] and sha(body)==pin['sha256'],'complete original20ms transport')
        fields=struct.unpack('<8s6I8s',body[:40]);_,c,n,m,pre,logical,count,mapping=fields;at=40;packets=[]
        for _ in range(count):size=struct.unpack_from('<I',body,at)[0];at+=4;packets.append(body[at:at+size]);at+=size
        need(at==len(body) and count==11 and c==channels,'all original packets present');sources.append(dict(channels=c,streams=n,coupled=m,pre_skip=pre,logical=logical,mapping=list(mapping[:c]),packets=packets,source_sha256=sha(body)))
    long_body=LONG.read_bytes();need(sha(long_body)==LONG_SHA,'exact full original120ms source');pages,packets=reader.parse(long_body);pre=int.from_bytes(packets[0][10:12],'little');logical=int.from_bytes(long_body[pages[-1]['offset']+6:pages[-1]['offset']+14],'little')-pre
    variants=[dict(s,name='default'+str(s['channels'])) for s in sources]
    maps=((7,),(6,0),(5,5,255),(7,0,6,1),(255,255,255,255,255),(0,1,2,3,4,5),(7,7,6,5,0,255,1),(0,7,0,7,255,5,6,255))
    variants += [dict(sources[2],channels=len(mapping),mapping=list(mapping),name='map'+str(len(mapping))) for mapping in maps]
    variants.append(dict(channels=2,streams=1,coupled=1,pre_skip=pre,logical=logical,mapping=[0,1],packets=packets[2:],source_sha256=LONG_SHA,name='full120'))
    need(len(variants)==12 and len(variants[-1]['packets'])==92,'finite full fixture inventory');blob=bytearray(16+80*len(variants));dedup={};entries=[];records=[]
    def append(body):
        digest=sha(body)
        if digest not in dedup:dedup[digest]=len(blob);blob.extend(body)
        offset=dedup[digest];need(blob[offset:offset+len(body)]==body,'exact deduplicated bytes');return offset
    def physical(source,style):
        result=bytearray();sequence=0;identity=[];serial=0x67000000+source['id']
        def page(flags,gp,table,payload):
            nonlocal sequence
            need(len(table)<=255 and sum(table)==len(payload),'complete independent lacing');body=bytearray(b'OggS\0'+bytes((flags,))+struct.pack('<QII',gp,serial,sequence)+bytes(4)+bytes((len(table),))+bytes(table)+payload)
            body[22:26]=struct.pack('<I',reader.crc(body));identity.append(dict(sequence=sequence,flags=flags,bytes=len(body),sha256=sha(body)));result.extend(body);sequence+=1
        def lace(size):return [255]*(size//255)+[size%255]
        head=b'OpusHead'+bytes((1,source['channels']))+struct.pack('<HIh',source['pre_skip'],44100,1536)+bytes((1,source['streams'],source['coupled'],*source['mapping']))
        page(2,0,lace(len(head)),head);vendor=b'public native adapter\x00'+bytes.fromhex('f0908080');tags=b'OpusTags'+struct.pack('<I',len(vendor))+vendor+struct.pack('<II',1,8)+b'TITLE=ok'+bytes.fromhex('ff00c080')
        page(0,0,lace(len(tags)),tags);raw=0
        for packet_id,(packet,parts) in enumerate(zip(source['packets'],source['parts'])):
            raw+=parts[0]['samples'];last=packet_id+1==len(source['packets']);gp=source['pre_skip']+source['logical'] if last else raw
            if style and len(packet)>255:
                page(0,0xffffffffffffffff,[255],packet[:255]);page(packet_id%2,0xffffffffffffffff,[],b'');page(1|(4 if last else 0),gp,lace(len(packet)-255),packet[255:])
            else:page(4 if last else 0,gp,lace(len(packet)),packet)
        need(raw==source['raw'],'complete raw time');return bytes(result),identity
    for fixture_id,source in enumerate(variants):
        source['id']=fixture_id;source['parts']=[framing.split_multistream(p,source['streams']) for p in source['packets']];source['raw']=sum(v[0]['samples'] for v in source['parts']);needed=[]
        for index in source['mapping']:
            if index!=255:
                stream=index//2 if index<2*source['coupled'] else index-source['coupled']
                if stream not in needed:needed.append(stream)
        table=bytearray();packet_records=[]
        for packet,parts in zip(source['packets'],source['parts']):
            offset=append(packet);table.extend(struct.pack('<3I',parts[0]['samples'],len(packet),offset))
            for part in parts:table.extend(struct.pack('<2I',part['offset'],len(part['original'])))
            packet_records.append(dict(bytes=len(packet),sha256=sha(packet),frames=parts[0]['samples'],parts=[dict(offset=p['offset'],bytes=len(p['original']),sha256=sha(p['original'])) for p in parts]))
        table_offset=append(table);whole,whole_pages=physical(source,0);split,split_pages=physical(source,1);whole_offset=append(whole);split_offset=append(split)
        fields=(fixture_id,source['channels'],source['streams'],source['coupled'],source['pre_skip'],source['logical'],source['raw'],len(source['packets']),table_offset,whole_offset,len(whole),len(whole_pages),split_offset,len(split),len(split_pages),len(needed),1536,0)
        entries.append(struct.pack('<18I8s',*fields,bytes(source['mapping']).ljust(8,b'\0')))
        records.append(dict(id=fixture_id,name=source['name'],channels=source['channels'],streams=source['streams'],coupled=source['coupled'],pre_skip=source['pre_skip'],logical=source['logical'],raw=source['raw'],mapping=source['mapping'],needed_streams=needed,
            original_source_sha256=source['source_sha256'],packets=packet_records,whole=dict(bytes=len(whole),sha256=sha(whole),pages=whole_pages),split=dict(bytes=len(split),sha256=sha(split),pages=split_pages)))
    blob[:16]=struct.pack('<4I',0x46504131,1,len(variants),80);blob[16:16+80*len(entries)]=b''.join(entries)
    return bytes(blob),dict(passed=True,decoder_executed=False,fixtures=records,bytes=len(blob),sha256=sha(blob),original_packet_bodies_preserved=True,
        independent_direct_native_reference='precomputed original AppendixB elementary offsets and raw-time bounds; no production framing/mapping/trim helper in reference TU',numeric_conformance_claim=False)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reference',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh local data preparation');out.mkdir(parents=True);body,report=build(args.reference.resolve());(out/'fixtures.bin').write_bytes(body);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,fixtures=12,bytes=len(body),sha256=sha(body))))
if __name__=='__main__':main()
