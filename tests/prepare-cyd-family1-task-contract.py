"""Prepare complete CYD family1 task contracts without production/source freeze.

Original packet bodies and independently prepared Appendix B offsets come from
the completed public fixture preparer. No decoder, SDK, QEMU or private ABI runs.
Large local fixture files are emitted only with the explicit --write-assets flag.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
PREP=ROOT/'tests/fixtures/opus_family1_playback_native/prepare.py'
REFERENCE=ROOT/'.build/opus-family1-reference-20261101-03'
EXPECTED_BLOB='a08da6bb2f5f5454ca7cbb61adc130a8faa0c00ba6d61ea9f2f93bdac67debce'
STRESS=ROOT/'.build/opus-family1-120ms-probe-20261101-01/results'
STRESS_SHA='c6a06d1bf954c9119f844167d43b3f080bdbe4e7c2a305318109e524cf3b6757'
LEGACY={
    13:dict(name='OPUS20',path='tests/fixtures/esp32c3_calibration/opus-510.ogg',bytes=706319,
            sha256='53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11'),
    14:dict(name='VORBIS',path='tests/fixtures/esp32c3_calibration/vorbis-q10.ogg',bytes=703584,
            sha256='09d6cfa599f2c4a25f5745e5c8a605b5a1583a42d7990b9e5242b8990adff12f'),
}


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(body):return hashlib.sha256(body).hexdigest()


def referenced_stream_order(mapping,streams,coupled):
    """Expected public-open order from the original decoded-channel map."""
    need(0<=coupled<=streams and streams>0 and 1<=len(mapping)<=8,'valid original public map geometry')
    result=[]
    for decoded in mapping:
        if decoded==255:continue
        need(0<=decoded<streams+coupled,'original decoded index is in the declared streams')
        stream=decoded//2 if decoded<2*coupled else decoded-coupled
        if stream not in result:result.append(stream)
    return result


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def compact_assets(contract,original,source):
    """Deduplicate immutable bodies; authenticate every original transport view.

    Only the direct-reference packet table and packet bodies remain contiguous.
    HTTP views are finite spans; no full encoded-stream RAM assembly is needed.
    """
    fixture_count=len(source['fixtures']);compact=bytearray(16+80*fixture_count);dedup={};views={};packet_tables=[]
    def append(body):
        digest=sha(body)
        if digest not in dedup:dedup[digest]=len(compact);compact.extend(body)
        at=dedup[digest];need(compact[at:at+len(body)]==body,'exact immutable deduplicated content')
        return at
    def add_span(spans,offset,size):
        if not size:return
        if spans and spans[-1]['offset']+spans[-1]['bytes']==offset:spans[-1]['bytes']+=size
        else:spans.append(dict(offset=offset,bytes=size))
    for row in source['fixtures']:
        fixture=row['id'];words=list(row['_words']) if '_words' in row else list(struct.unpack_from('<18I8s',original,16+80*fixture))
        if isinstance(words[-1],list):words[-1]=bytes(words[-1])
        cursor=words[8];packets=[];table=bytearray()
        for pin in row['packets']:
            frames,size,offset=struct.unpack_from('<3I',original,cursor);parts=original[cursor+12:cursor+12+8*row['streams']]
            cursor+=12+8*row['streams'];body=original[offset:offset+size]
            need(size==pin['bytes'] and frames==pin['frames'] and sha(body)==pin['sha256'],'every original complete direct-reference packet')
            new=append(body);packets.append((body,new));table.extend(struct.pack('<3I',frames,size,new)+parts)
        words[8]=append(table);packet_tables.append(dict(fixture=fixture,offset=words[8],bytes=len(table),sha256=sha(table)))
        for style in ('whole','split'):
            old_offset=words[9 if style=='whole' else 12];size=words[10 if style=='whole' else 13]
            encoded=original[old_offset:old_offset+size];at=packet_index=packet_position=0;spans=[];head_span_count=0;headers=[]
            # Both identification/comment packets precede the original audio.
            initial=[];p=0
            for _ in range(2):
                segments=encoded[p+26];header=27+segments;end=p+header+sum(encoded[p+27:p+header]);initial.append(encoded[p+header:end]);p=end
            all_packets=[(body,append(body)) for body in initial]+packets
            while at<len(encoded):
                need(encoded[at:at+5]==b'OggS\0','original complete physical page')
                count=encoded[at+26];header_size=27+count;header=encoded[at:at+header_size]
                add_span(spans,append(header),len(header));headers.append(dict(offset=at,bytes=len(header),sha256=sha(header)))
                payload=at+header_size
                for lace in header[27:]:
                    body,stored=all_packets[packet_index]
                    need(encoded[payload:payload+lace]==body[packet_position:packet_position+lace],'exact original laced packet-body span')
                    add_span(spans,stored+packet_position,lace);payload+=lace;packet_position+=lace
                    if lace<255:
                        need(packet_position==len(body),'complete original packet extent');packet_index+=1;packet_position=0
                at=payload
                if packet_index==1:head_span_count=len(spans)
            reconstructed=b''.join(compact[span['offset']:span['offset']+span['bytes']] for span in spans)
            need(at==len(encoded) and packet_index==len(all_packets) and not packet_position and reconstructed==encoded and
                 len(encoded)==row[style]['bytes'] and sha(encoded)==row[style]['sha256'],'complete independently reconstructed original transport SHA/extent')
            views[(fixture,style,1536)]=dict(reference=fixture,style=style,gain_q8=1536,spans=spans,
                bytes=len(encoded),sha256=sha(encoded),head_span_count=head_span_count,head_bytes=sum(x['bytes'] for x in spans[:head_span_count]))
        # HTTP spans live in the generated descriptor table, never in fields the
        # independent raw decoder does not consume. Preserve original counts.
        words[9]=words[12]=0
        compact[16+80*fixture:16+80*(fixture+1)]=struct.pack('<18I8s',*words)
    legacy_bodies={}
    for index,pin in LEGACY.items():
        body=(ROOT/pin['path']).read_bytes();need(len(body)==pin['bytes'] and sha(body)==pin['sha256'],'complete unchanged legacy successor')
        offset=append(body);head_size=27+body[26]+sum(body[27:27+body[26]])
        views[(index,'whole',0)]=dict(reference=index,style='whole',gain_q8=0,
            spans=[dict(offset=offset,bytes=head_size),dict(offset=offset+head_size,bytes=len(body)-head_size)],
            bytes=len(body),sha256=sha(body),head_span_count=1,head_bytes=head_size)
        legacy_bodies[index]=body
    prepare=load('independent_family1_gain_crc',PREP)
    reader=load('independent_family1_crc_reader',prepare.READER)
    for case in contract['cases']:
        for link in case['links']:
            reference,gain=link['reference'],link['gain_q8'];style='split' if case['page_style'] and reference<fixture_count else 'whole'
            key=(reference,style,gain)
            if key in views:continue
            source_key=(reference,style,1536 if reference<fixture_count else 0);view=views[source_key]
            need(reference!=14 and -32768<=gain<=32767,'only public signed OpusHead gain is changed')
            head=bytearray(b''.join(compact[s['offset']:s['offset']+s['bytes']] for s in view['spans'][:view['head_span_count']]))
            payload=27+head[26];need(head[payload:payload+8]==b'OpusHead','sole original identification packet')
            head[payload+16:payload+18]=gain.to_bytes(2,'little',signed=True);head[22:26]=bytes(4);head[22:26]=reader.crc(head).to_bytes(4,'little')
            spans=[dict(offset=append(head),bytes=len(head))]+view['spans'][view['head_span_count']:]
            body=b''.join(compact[s['offset']:s['offset']+s['bytes']] for s in spans)
            need(len(body)==view['bytes'] and body[len(head):]==b''.join(compact[s['offset']:s['offset']+s['bytes']] for s in view['spans'][view['head_span_count']:]),
                 'gain derivative retains every original following encoded byte')
            views[key]=dict(view,gain_q8=gain,spans=spans,sha256=sha(body),head_span_count=1)
    compact[:16]=struct.pack('<4I',0x46504131,2,fixture_count,80)
    descriptors=sum(len(view['spans']) for view in views.values())
    report=dict(passed=True,original_blob_bytes=len(original),original_blob_sha256=sha(original),
        unique_blob_bytes=len(compact),unique_blob_sha256=sha(compact),view_count=len(views),span_descriptors=descriptors,
        descriptor_bytes=descriptors*8,packet_tables=packet_tables,
        views=[view for _,view in sorted(views.items())],full_stream_RAM_reconstruction_required=False,
        complete_original_bodies_preserved=True,diagnostic_flash_bytes=4194304,actual_image_fit_measured=False)
    return bytes(compact),report


def add_stress(original,source):
    """Bind the completed real creator API probe; do not rerun/re-encode it."""
    driver=json.loads((STRESS.parent/'driver.json').read_bytes())
    need(driver['passed'] and driver['completed'] and driver['state']=='complete' and driver['pid']>0 and driver['exit_status']==0,
         'actual owned public creator process is terminal zero')
    for pin in driver['sources']:
        snapshot=STRESS.parent/pin['snapshot'];current=Path(pin['path'])
        need(len(snapshot.read_bytes())==pin['bytes'] and sha(snapshot.read_bytes())==pin['sha256'] and
             len(current.read_bytes())==pin['bytes'] and sha(current.read_bytes())==pin['sha256'],
             'every actual public creator driver input is unchanged')
    report=json.loads((STRESS/'report.json').read_bytes());body=(STRESS/'channels8-120ms.packets').read_bytes()
    need(report['passed'] and report['every_coded_frame_preserved'] and report['creator_full_float_exact'] and
         report['durations']==[5760,4800] and report['raw_frames']==10560 and report['pre_skip']==312 and
         report['logical_frames']==9600 and not report['native_executed'] and not report['new_tolerance_applied'] and
         len(body)==15447 and sha(body)==STRESS_SHA==report['transport']['sha256'],
         'genuine public creator active C8 120/100ms repacketization with complete original frames')
    need(report['libopus_version']=='libopus 1.4' and len(report['cat_events'])==55 and
         all(row['result']==0 for row in report['cat_events']) and len(report['outputs'])==10 and
         {(row['stream'],row['group'],row['frames'],row['samples']) for row in report['outputs']}==
         {(stream,group,frames,frames*960) for stream in range(5) for group,frames in [(0,6),(1,5)]},
         'all real creator repacketizer calls and output geometry accounted')
    prepare=load('complete_family1_stress_sources',PREP)
    framing=load('independent_stress_framing',prepare.FRAMING);reader=load('independent_stress_crc',prepare.READER)
    magic,c,n,m,pre,logical,count,mapping=struct.unpack('<8s6I8s',body[:40])
    need(magic==b'OFAM101\0' and (c,n,m,pre,logical,count)==(8,5,3,312,9600,2),'complete stress transport metadata')
    blob=bytearray(original);at=40;packets=[];records=[];table=bytearray()
    for packet_index in range(count):
        size=struct.unpack_from('<I',body,at)[0];at+=4;packet=body[at:at+size];at+=size
        parts=framing.split_multistream(packet,n);frames=parts[0]['samples']
        need(frames==[5760,4800][packet_index] and all(part['samples']==frames for part in parts),'every original grouped stream duration')
        offset=len(blob);blob.extend(packet);table.extend(struct.pack('<3I',frames,len(packet),offset))
        for part in parts:table.extend(struct.pack('<2I',part['offset'],len(part['original'])))
        packets.append(packet);records.append(dict(bytes=len(packet),sha256=sha(packet),frames=frames,
            parts=[dict(offset=p['offset'],bytes=len(p['original']),sha256=sha(p['original'])) for p in parts]))
    need(at==len(body),'all stress input bytes preserved');table_offset=len(blob);blob.extend(table)
    def physical(split):
        encoded=bytearray();pages=[];sequence=0
        def page(flags,gp,lace,payload):
            nonlocal sequence
            head=b'OggS\0'+bytes((flags,))+struct.pack('<QII',gp,0x6800000c,sequence)+bytes(4)+bytes((len(lace),))+bytes(lace)
            data=bytearray(head+payload);data[22:26]=reader.crc(data).to_bytes(4,'little')
            pages.append(dict(sequence=sequence,flags=flags,bytes=len(data),sha256=sha(data)));encoded.extend(data);sequence+=1
        def lace(size):return [255]*(size//255)+[size%255]
        head=b'OpusHead'+bytes((1,8))+struct.pack('<HIh',312,48000,1536)+bytes((1,5,3))+mapping
        vendor=b'public creator repacketized active C8';tags=b'OpusTags'+struct.pack('<I',len(vendor))+vendor+bytes(4)
        page(2,0,lace(len(head)),head);page(0,0,lace(len(tags)),tags);raw=0
        for index,packet in enumerate(packets):
            raw+=records[index]['frames'];last=index+1==len(packets);gp=312+9600 if last else raw
            if split:
                page(0,2**64-1,[255],packet[:255]);page(0,2**64-1,[],b'');page(1|(4 if last else 0),gp,lace(len(packet)-255),packet[255:])
            else:page(4 if last else 0,gp,lace(len(packet)),packet)
        need(raw==10560,'full stress raw clock');return bytes(encoded),pages
    whole,whole_pages=physical(False);split,split_pages=physical(True)
    whole_offset=len(blob);blob.extend(whole);split_offset=len(blob);blob.extend(split)
    words=[12,8,5,3,312,9600,10560,2,table_offset,whole_offset,len(whole),len(whole_pages),split_offset,len(split),len(split_pages),5,1536,0,list(mapping)]
    row=dict(id=12,name='active8_120',channels=8,streams=5,coupled=3,pre_skip=312,logical=9600,raw=10560,
        mapping=list(mapping),needed_streams=referenced_stream_order(mapping,5,3),original_source_sha256=STRESS_SHA,packets=records,
        whole=dict(bytes=len(whole),sha256=sha(whole),pages=whole_pages),split=dict(bytes=len(split),sha256=sha(split),pages=split_pages),_words=words)
    source=dict(source,fixtures=[*source['fixtures'],row],baseline_blob_sha256=EXPECTED_BLOB,
        stress_creator_report_sha256=sha((STRESS/'report.json').read_bytes()),stress_transport_sha256=STRESS_SHA,
        stress_creator_float=report['creator_float'])
    return bytes(blob),source


def contracts(reference=REFERENCE):
    prepare=load('reviewed_complete_family1_preparer',PREP)
    blob,source=prepare.build(reference)
    need(len(blob)==2494328 and sha(blob)==EXPECTED_BLOB and len(source['fixtures'])==12,
         'exact completed original-body reference corpus')
    blob,source=add_stress(blob,source)
    entries=[]
    for row in source['fixtures']:
        need(row['needed_streams']==referenced_stream_order(row['mapping'],row['streams'],row['coupled']),
             'every expected public-open sequence follows original first-reference stream order')
        offset=16+80*row['id'];words=tuple(row['_words']) if '_words' in row else struct.unpack_from('<18I8s',blob,offset)
        need(words[0]==row['id'] and list(words[-1][:row['channels']])==row['mapping'],
             'independent fixed-size data-only fixture table joins metadata')
        whole,split=words[9:11],words[12:14]
        pages=row['whole']['pages']
        hold=sum(page['bytes'] for page in pages[:3])
        need(len(pages)>=4 and 0<hold<whole[1] and row['pre_skip']<row['packets'][0]['frames'],
             'complete first audio packet precedes genuine partial transport hold')
        entries.append(dict(id=row['id'],name=row['name'],channels=row['channels'],
            streams=row['streams'],coupled=row['coupled'],needed_streams=row['needed_streams'],
            mapping=row['mapping'],pre_skip=row['pre_skip'],logical_frames=row['logical'],
            raw_frames=row['raw'],pcm_bytes=row['logical']*row['channels']*2,
            rate=48000,bits=16,layout='VORBIS',gain_q8=1536,
            whole_offset=whole[0],whole_bytes=whole[1],whole_sha256=row['whole']['sha256'],
            split_offset=split[0],split_bytes=split[1],split_sha256=row['split']['sha256'],
            hold_offset=hold,hold_after_complete_audio_packets=1,
            packet_table=words[8],packet_count=words[7],original_source_sha256=row['original_source_sha256']))
    cases=[]
    for fixture in (0,1,2,11,12):
        for case,schedule,style in (('T0',0,0),('T1',0,0),('T2',0,0),('FULL',1,0),('FULL',2,1),('FULL',3,1)):
            cases.append(dict(name=entries[fixture]['name'],id=case,reference=fixture,
                schedule=schedule,page_style=style,links=[dict(reference=fixture,gain_q8=1536)],volume=254))
    for fixture in range(3,11):
        for style in (0,1):
            cases.append(dict(name=entries[fixture]['name'],id='MAP',reference=fixture,
                schedule=0 if style==0 else 2,page_style=style,
                links=[dict(reference=fixture,gain_q8=1536)],volume=254))
    chains=[
        dict(name='LAYOUT_GAIN_CHAIN',links=[dict(reference=2,gain_q8=1536),
             dict(reference=0,gain_q8=-1536),dict(reference=13,gain_q8=0),
             dict(reference=14,gain_q8=0),dict(reference=1,gain_q8=1536)],volume=254),
        dict(name='REVERSE_120_CHAIN',links=[dict(reference=14,gain_q8=0),
             dict(reference=11,gain_q8=1536),dict(reference=2,gain_q8=-1536),
             dict(reference=13,gain_q8=1536),dict(reference=0,gain_q8=0)],volume=1),
    ]
    for chain in chains:cases.append(dict(chain,id='CHAIN',reference=-1,schedule=0,page_style=1))
    need(len(cases)==48 and sum(case['id']=='T1' for case in cases)==5 and
         sum(case['id']=='T2' for case in cases)==5,'declared complete bounded case matrix')
    handles=sum(sum(len(entries[link['reference']]['needed_streams']) if link['reference']<13 else 1 for link in case['links'])*
                (2 if case['id'] in ('T1','T2') else 1) for case in cases)
    need(handles==195,'every intended selected-stream public owner counted independently')
    contract=dict(passed=True,prepared_only=True,target_executed=False,production_sources_frozen=False,
        private_codec_abi=False,independent_codec_conformance=False,new_numeric_tolerance=False,
        same_vendor_integration_oracle=True,independent_public_reference_helpers_excluded=[
            'opus_family1_playback.h','opus_family1_decoder.h','opus_family1_mapping.h',
            'opus_multistream_framing.h','opus_pcm_trim.h','ogg_page_input.h','pcm_speaker_mix.h'],
        fixture_blob=dict(bytes=len(blob),sha256=sha(blob)),entries=entries,cases=cases,
        direct_public_reference_cases=13,legacy_reference_indices=dict(OPUS20=13,VORBIS=14),
        complete_output_cases=48,application_http_sessions=58,application_decoder_handles=handles,
        active_C8_120ms_stress=True,stress_creator_source_report_sha256=source['stress_creator_report_sha256'],
        ordinary_deadline_ms=30000,reference_capture_deadline_ms=90000,whole_qemu_deadline_ms=600000,
        deadlines_selected_once_at_entry=True,normalization_enabled=False,
        task_bindings=dict(stream=dict(core=0,priority=3,stack=6144),
            decode=dict(core=1,priority=5,stack=16384),output=dict(core=1,priority=6,stack=4096)),
        native_resource_refusal_is_format_allowance=False)
    return contract,blob,source


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',type=Path,default=REFERENCE)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--write-assets',action='store_true')
    args=parser.parse_args();contract,blob,source=contracts(args.reference.resolve())
    if args.output:
        out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local preparation')
        out.mkdir(parents=True)
        for name,value in [('contract.json',contract),('fixture-preparation.json',source)]:
            (out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
        if args.write_assets:(out/'fixtures.bin').write_bytes(blob)
    else:need(not args.write_assets,'explicit fresh output required for assets')
    print(json.dumps(dict(passed=True,prepared_only=True,fixtures=13,cases=48,http_sessions=58,
        fixture_bytes=len(blob),fixture_sha256=sha(blob),asset_copied=bool(args.output and args.write_assets),target_executed=False)))


if __name__=='__main__':main()
