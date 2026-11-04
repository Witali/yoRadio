"""Host-only complete immutable-transport and independent oracle regressions."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(body):return hashlib.sha256(body).hexdigest()


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def ogg_packets(body):
    at=0;packets=[];partial=bytearray();serial=None;sequence=0
    while at<len(body):
        need(body[at:at+5]==b'OggS\0' and at+27<=len(body),'complete public physical header')
        count=body[at+26];payload=at+27+count;end=payload+sum(body[at+27:payload])
        need(end<=len(body),'complete public physical extent');page=bytearray(body[at:end]);stored=struct.unpack_from('<I',page,22)[0];page[22:26]=bytes(4)
        crc=0
        for byte in page:
            crc^=byte<<24
            for _ in range(8):crc=((crc<<1)^(0x04c11db7 if crc>>31 else 0))&0xffffffff
        current=struct.unpack_from('<I',page,14)[0]
        if serial is None:serial=current
        need(crc==stored and current==serial and struct.unpack_from('<I',page,18)[0]==sequence,'original page CRC/serial/sequence')
        position=payload
        for size in body[at+27:payload]:
            partial.extend(body[position:position+size]);position+=size
            if size<255:packets.append(bytes(partial));partial.clear()
        need(position==end,'whole exact lacing payload');at=end;sequence+=1
    need(at==len(body) and not partial and sequence>2,'whole public logical transport')
    return packets


def check_header_stream_order(entry,head):
    """Independent metadata check from an authenticated public OpusHead."""
    streams,coupled=head[19:21];mapping=head[21:21+head[9]]
    decoded_streams=[]
    for index in mapping:
        if index==255:continue
        need(index<streams+coupled,'authenticated decoded-channel index is in range')
        decoded_streams.append(index//2 if index<2*coupled else index-coupled)
    expected=list(dict.fromkeys(decoded_streams))
    need(entry['needed_streams']==expected,'all-entry first-reference public-open order from authenticated map')
    return expected


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    out=parser.parse_args().output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh local host-only result')
    out.mkdir(parents=True);report=dict(passed=False,SDK_build_started=False,decoder_executed=False,QEMU_started=False,production_sources_frozen=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    try:
        assets=module('new_family1_immutable_assets',ROOT/'tests/prepare-cyd-family1-task-assets.py')
        contract,blob,header,size_header,source=assets.prepare();entries={entry['id']:entry for entry in contract['entries']}
        views=contract['immutable_storage']['views'];original_packets={};controls=0;stream_orders={}
        for row in source['fixtures']:
            words=struct.unpack_from('<18I8s',blob,16+80*row['id']);table=words[8];packets=[]
            for pin in row['packets']:
                frames,size,offset=struct.unpack_from('<3I',blob,table);table+=12+8*row['streams'];body=blob[offset:offset+size]
                need(sha(body)==pin['sha256'] and frames==pin['frames'] and size==pin['bytes'],'every complete independent raw-reference packet rebound')
                packets.append(body)
            original_packets[row['id']]=packets
        partition_reads=0
        for view in views:
            spans=view['spans'];need(all(span['bytes']>0 and span['offset']+span['bytes']<=len(blob) for span in spans),'bounded immutable span descriptors')
            body=b''.join(blob[span['offset']:span['offset']+span['bytes']] for span in spans)
            need(len(body)==view['bytes'] and sha(body)==view['sha256'],'whole authenticated original/gain view')
            packets=ogg_packets(body);reference=view['reference']
            if reference<13:
                entry=entries[reference]
                need(packets[0].startswith(b'OpusHead') and packets[0][9]==entry['channels'] and packets[0][18]==1 and
                     int.from_bytes(packets[0][10:12],'little')==entry['pre_skip'] and int.from_bytes(packets[0][16:18],'little',signed=True)==view['gain_q8'] and
                     packets[0][21:21+entry['channels']]==bytes(entry['mapping']) and packets[2:]==original_packets[reference],
                     'all exact original audio packets, public mapping, trim and gain after independent page walk')
                expected_order=check_header_stream_order(entry,packets[0]);stream_orders[reference]=expected_order
                if reference==12 and view['style']=='whole':
                    wrong=dict(entry,needed_streams=sorted(expected_order))
                    need(wrong['needed_streams']!=expected_order,'active C8 sorted order differs from first reference')
                    try:check_header_stream_order(wrong,packets[0])
                    except ValueError:controls+=1
                    else:raise ValueError('sorted-but-wrong public-open order accepted')
            # Partition the immutable view independently by prefix positions;
            # request boundaries deliberately cross headers/lacing/body spans.
            starts=[];position=0
            for span in spans:starts.append((position,position+span['bytes'],span));position+=span['bytes']
            for chunk in (1,257,4096):
                digest=hashlib.sha256()
                for start in range(0,len(body),chunk):
                    stop=min(start+chunk,len(body));part=bytearray()
                    for left,right,span in starts:
                        if right<=start:continue
                        if left>=stop:break
                        a,b=max(start,left)-left,min(stop,right)-left
                        part.extend(blob[span['offset']+a:span['offset']+b])
                    need(bytes(part)==body[start:stop],'every bounded partial request matches immutable full source');digest.update(part);partition_reads+=1
                need(digest.hexdigest()==view['sha256'],'all one-byte/split request schedules preserve complete input')
            damaged=bytearray(body);damaged[-1]^=1
            try:ogg_packets(damaged)
            except ValueError:controls+=1
            else:raise ValueError('one-bit physical payload corruption accepted')
        output=module('independent_family1_final_output',ROOT/'tests/prepare-cyd-family1-task-output.py')
        golden_path=ROOT/'.build/cyd-opus-gain-output-reference-20261101-01/report.json';golden=json.loads(golden_path.read_bytes())
        need(golden['passed'] and golden['all_source_bindings_current'] and not golden['decoder_executed'],'previous full independent Decimal reference scope')
        stock_pin=output.LEGACY_PCM[13];raw=(ROOT/stock_pin['path']).read_bytes();need(sha(raw)==stock_pin['sha256'],'complete prior stock PCM')
        pcm=raw[stock_pin['offset']:stock_pin['offset']+stock_pin['logical_bytes']];regressions=[]
        for gain,volume in [(0,254),(1536,1),(-1536,254)]:
            first,pin=output.mono(pcm,2,0,gain,volume,100);second,other=output.mono(pcm,2,0,gain,volume,160)
            expected=[row for row in golden['references'] if row['fixture']=='OPUS20' and row['gain_q8']==gain and row['volume']==volume]
            need(len(expected)==1 and first==second and pin==other and all(pin[key]==expected[0][key] for key in ('bytes','frames','sha256','peak','nonzero_samples','saturation_samples')),
                 'new independent final-mono implementation preserves whole committed legacy regression')
            regressions.append(dict(gain_q8=gain,volume=volume,**pin))
        reader=module('new_family1_actual_log_reader',ROOT/'tests/read-cyd-family1-task-log.py')
        for text in ('','CYD_F1_TASK_BOOT sdk=v6.0.2 actual_tasks=1 actual_output=1 public_raw=1 hardware=0\n'):
            try:reader.validate(text,contract)
            except ValueError:controls+=1
            else:raise ValueError('incomplete nonexistent native evidence accepted')
        need(set(stream_orders)==set(entries),'all13 complete entry maps independently checked')
        report.update(passed=True,immutable_views=len(views),source_fixtures=len(entries),complete_packet_sets=13,
            all_entry_first_reference_orders=stream_orders,sorted_but_wrong_order_rejected=True,
            partition_reads=partition_reads,corruption_or_incomplete_controls=controls,prior_full_Decimal_regressions=regressions,
            asset_bytes=len(blob),asset_sha256=sha(blob),descriptor_bytes=contract['immutable_storage']['descriptor_bytes'],
            full_original_encoded_inputs_preserved=True,new_numeric_tolerance=False,actual_image_fit_measured=False,
            original_goldens=dict(path=golden_path.relative_to(ROOT).as_posix(),bytes=golden_path.stat().st_size,sha256=sha(golden_path.read_bytes())))
        save();print(json.dumps({key:report[key] for key in ('passed','immutable_views','partition_reads','corruption_or_incomplete_controls','asset_bytes','decoder_executed','QEMU_started')}));return 0
    except Exception as error:
        report.update(failure_type=type(error).__name__,failure=str(error));save();print(json.dumps(dict(passed=False,failure=str(error))));return 1


if __name__=='__main__':raise SystemExit(main())
