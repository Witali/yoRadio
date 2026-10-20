"""SOURCE PROPOSAL: construct public candidates and command plans; never run codecs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=HERE/'encoder-192000.ogg'
EXPECTED_SOURCE='82ef0b5354ac3baea18d24479360a4b1d84956c789b969333f333efcb018e2f1'
EXPECTED_AUDIO='4e7aee5fa90add769e2dc95d8c2e0fab858b07d176932fdc581d12608799c8cc'

def digest(data): return hashlib.sha256(data).hexdigest()

def crc(data):
    value=0
    for byte in data:
        value ^= byte << 24
        for _ in range(8): value=((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value

def unpack(data):
    packets=[]; pending=bytearray(); pos=0; serial=None; sequence=0
    while pos<len(data):
        assert data[pos:pos+4]==b'OggS' and data[pos+4]==0
        n=data[pos+26]; laces=data[pos+27:pos+27+n]; end=pos+27+n+sum(laces)
        assert end<=len(data) and len(laces)==n
        page=bytearray(data[pos:end]); expected=struct.unpack_from('<I',page,22)[0]; page[22:26]=bytes(4)
        assert crc(page)==expected
        sid,seq=struct.unpack_from('<II',page,14)
        if serial is None: serial=sid
        assert sid==serial and seq==sequence and bool(page[5]&1)==bool(pending)
        sequence += 1; offset=27+n
        for size in laces:
            pending.extend(page[offset:offset+size]); offset += size
            if size<255: packets.append(bytes(pending)); pending.clear()
        pos=end
    assert not pending and pos==len(data)
    return serial,packets

def page(packets,serial,sequence,flags,granule):
    laces=[]
    for packet in packets: laces += [255]*(len(packet)//255)+[len(packet)%255]
    assert len(laces)<=255
    data=bytearray(b'OggS'+bytes([0,flags])+struct.pack('<qII',granule,serial,sequence)+bytes(4)+bytes([len(laces)])+bytes(laces)+b''.join(packets))
    struct.pack_into('<I',data,22,crc(data))
    return bytes(data)

def candidate_audio(audio,family):
    donors=list(range(68)) if family=='identity' else [0,0,1,2,0]+list(range(3,68))
    flags=[0 if donor==0 else 1 for donor in donors]; result=[]; edits=[]
    for i,donor in enumerate(donors):
        old=audio[donor]; new=bytearray(old)
        if flags[i]:
            prev=flags[i-1] if i else (old[0]>>2)&1
            nxt=flags[i+1] if i+1<len(flags) else (old[0]>>3)&1
            new[0]=(new[0]&~12) | prev<<2 | nxt<<3
        if bytes(new)!=old:
            assert len(new)==len(old) and bytes(new[1:])==old[1:] and (new[0]^old[0]) & ~12==0
            edits.append(dict(packet=i,donor=donor,old_first_byte=old[0],new_first_byte=new[0]))
        result.append(bytes(new))
    if family=='identity': assert not edits and result==audio
    else:
        assert len(result)==70 and len(edits)==2
        assert [(e['packet'],e['donor']) for e in edits]==[(3,2),(5,3)]
        assert [result[i] for i in (0,1,4)]==[audio[0]]*3
    return result,flags,donors,edits

def command_plan(path,pcm_dir,ffmpeg,ffprobe):
    commands=[dict(name='packet-frame-probe',argv=[str(ffprobe),'-v','error','-show_packets','-show_frames',
        '-show_entries','stream=codec_name,sample_rate,channels:packet=pts,dts,duration,flags,side_data_list:frame=pts,nb_samples','-of','json',str(path)])]
    for decoder in ('vorbis','libvorbis'):
        pcm=pcm_dir/(path.stem+'-'+decoder+'.wav')
        commands.append(dict(name='decode-'+decoder,wav=str(pcm),argv=[str(ffmpeg),'-nostdin','-hide_banner',
            '-loglevel','warning','-xerror','-err_detect','explode','-c:a',decoder,'-i',str(path),
            '-map','0:a:0','-c:a','pcm_s16le','-f','wav',str(pcm)]))
    return commands

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--ffmpeg',type=Path,required=True)
    parser.add_argument('--ffprobe',type=Path,required=True)
    args=parser.parse_args(); output=args.output.resolve()
    assert not output.exists(),'A fresh output directory is required'
    source=SOURCE.read_bytes(); assert digest(source)==EXPECTED_SOURCE
    serial,original=unpack(source); assert len(original)==71
    for packet,kind in zip(original[:3],(1,3,5)): assert packet[:7]==bytes([kind])+b'vorbis'
    audio=original[3:]; assert digest(b''.join(audio))==EXPECTED_AUDIO
    assert audio[0][0]&3==0 and audio[1][0]&15==10 and all(p[0]&15==14 for p in audio[2:])
    output.mkdir(); (output/'pcm').mkdir()
    report=dict(schema='public-vorbis-block-matrix-candidates-v1',source=str(SOURCE),source_sha256=digest(source),
        source_setup_sha256=digest(original[2]),source_audio_sha256=EXPECTED_AUDIO,source_packet_count=68,
        reference_executed=False,validity_qualified=False,
        tools={str(p.resolve()):digest(p.read_bytes()) for p in (args.ffmpeg,args.ffprobe)},cases=[])
    for family in ('identity','transitions'):
        current,flags,donors,edits=candidate_audio(audio,family)
        for s in range(6,14):
            for l in range(s,14):
                short,long=1<<s,1<<l
                ident=bytearray(original[0]); ident[28]=l<<4 | s
                blocks=[long if flag else short for flag in flags]
                pcm=[0]+[a+b for a,b in zip(blocks,blocks[1:])]
                transitions=Counter(('L' if a else 'S')+('L' if b else 'S') for a,b in zip(flags,flags[1:]))
                expected=dict(SL=1,LL=66) if family=='identity' else dict(SS=1,SL=2,LL=65,LS=1)
                assert transitions==expected
                assert sum(pcm)==((short if family=='identity' else 5*short)+133*long)
                granules=[]; granule=0
                for size in pcm: granule += size//4; granules.append(granule)
                container=page([ident],serial,0,2,0)+page(original[1:3],serial,1,0,0)
                for i,packet in enumerate(current):
                    container += page([packet],serial,i+2,4 if i+1==len(current) else 0,granules[i])
                _,again=unpack(container)
                assert again==[bytes(ident),*original[1:3],*current]
                assert bytes(ident[:28]+ident[29:])==original[0][:28]+original[0][29:]
                path=output/(f'{family}-short{short:04d}-long{long:04d}.ogg'); path.write_bytes(container)
                report['cases'].append(dict(id=path.stem,ogg=path.relative_to(output).as_posix(),
                    family=family,short=short,long=long,rate=192000,channels=2,bits=16,
                    mode_flags=flags,expected_raw_samples=sum(pcm)//4,path=str(path),sha256=digest(container),
                    packet_count=len(current),raw_pcm_bytes=pcm,raw_pcm_total_bytes=sum(pcm),
                    audio_packet_granules=granules,one_audio_packet_per_page=True,
                    natural_eos_granule=sum(pcm)//4,transitions=transitions,donors=donors,window_edits=edits,
                    preserved_setup=True,audio_byte_identical=family=='identity',
                    small_long_reinterpretation=long<512,host_validity='PENDING',
                    commands=command_plan(path,output/'pcm',args.ffmpeg.resolve(),args.ffprobe.resolve())))
    assert len(report['cases'])==72
    (output/'candidates.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Constructed72 UNQUALIFIED candidates; reference command plans are not executed.')

if __name__=='__main__': main()
