#!/usr/bin/env python3
"""Remove parser-identified SBR FIL elements, retaining every AAC core bit.

This is a deliberately narrow fixture generator, not a general AAC editor.
Only one raw data block per CRC-free ADTS frame is supported. A removed SBR
element may be followed only by traced fill-data/empty FIL elements, ID_END
and zero byte-alignment bits. Trailing fill elements are preserved verbatim.
FAAD source is verified against its pinned archive before adding passive
tracing to a disposable syntax.c copy. The reference extraction is untouched.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import tarfile
import wave
from run_faad_history_comparison import REVISION, ARCHIVE_SHA256, host_path, host_command

ROOT=Path(__file__).resolve().parents[2]
SBR_TYPES=(13,14)
ID_FIL='110'
ID_END='111'


def sha(data):return hashlib.sha256(data).hexdigest()


def adts_frames(data):
    frames=[];pos=0
    while pos<len(data):
        h=data[pos:pos+7]
        if len(h)!=7 or h[0]!=255 or h[1]&0xf6!=0xf0 or not h[1]&1 or h[6]&3:
            raise ValueError('Expected one CRC-free ADTS raw data block')
        size=((h[3]&3)<<11)|(h[4]<<3)|(h[5]>>5)
        if size<7 or pos+size>len(data):raise ValueError('Truncated ADTS frame')
        frames.append(data[pos:pos+size]);pos+=size
    if not frames:raise ValueError('Empty ADTS stream')
    return frames


def remove_sbr(frame,span,trailing=()):
    begin,payload,end,extension,count=span
    bits=''.join(f'{b:08b}' for b in frame)
    if not (56<=begin<payload<end<=len(bits)) or extension not in SBR_TYPES:
        raise ValueError('Invalid SBR syntax span')
    if bits[begin:begin+3]!=ID_FIL or int(bits[payload:payload+4],2)!=extension:
        raise ValueError('Parser trace does not match source bits')
    declared=int(bits[begin+3:begin+7],2)
    expected_payload=begin+7
    if declared==15:
        declared+=int(bits[begin+7:begin+15],2)-1;expected_payload+=8
    if payload!=expected_payload or count!=declared or end!=payload+8*count:
        raise ValueError('Parser/count disagreement')
    cursor=end
    for next_begin,next_payload,next_end,next_type,next_count in trailing:
        if next_begin!=cursor or next_type not in (1,255) or bits[cursor:cursor+3]!=ID_FIL:
            raise ValueError('Unverified element after SBR')
        declared=int(bits[cursor+3:cursor+7],2);offset=cursor+7
        if declared==15:declared+=int(bits[offset:offset+8],2)-1;offset+=8
        if (next_payload!=offset or declared!=next_count or next_end!=offset+declared*8 or
            (next_count and int(bits[offset:offset+4],2)!=next_type) or
            (not next_count and next_type!=255)):
            raise ValueError('Trailing fill parser/count disagreement')
        cursor=next_end
    suffix=bits[cursor:]
    if not suffix.startswith(ID_END) or len(suffix)>10 or '1' in suffix[3:]:
        raise ValueError('SBR is not the last element before zero-padded ID_END')
    kept=bits[:begin]+bits[end:cursor]+ID_END
    kept+='0'*(-len(kept)%8)
    result=bytearray(int(kept[i:i+8],2) for i in range(0,len(kept),8))
    size=len(result)
    result[3]=(result[3]&0xfc)|(size>>11)
    result[4]=(size>>3)&255
    result[5]=(result[5]&0x1f)|((size&7)<<5)
    # No audio core bit or ADTS field other than frame length may change.
    restored=bytearray(result);restored[3:6]=frame[3:6]
    check=''.join(f'{b:08b}' for b in restored)
    if check[:begin]!=bits[:begin]:raise ValueError('AAC core/header changed')
    if len(adts_frames(bytes(result)))!=1:raise ValueError('Invalid rewritten ADTS')
    return bytes(result)


def instrument(source):
    marker='/* Table 4.4.11 */'
    if source.count(marker)!=1:raise ValueError('Unexpected FAAD fill parser')
    start=source.index(marker);end=source.index('\n/*',start+len(marker))
    function=source[start:end]
    function=function.replace('    uint16_t count;',
        '    extern void yoradio_trace_fil(unsigned,unsigned,unsigned,unsigned,unsigned);\n'
        '    unsigned trace_begin=faad_get_processed_bits(ld)-3, trace_payload, trace_count;\n'
        '    unsigned trace_type=255;\n    uint16_t count;',1)
    anchor='    if (count > 0)\n'
    if function.count(anchor)!=1:raise ValueError('Ambiguous FAAD count block')
    function=function.replace(anchor,'    trace_payload=faad_get_processed_bits(ld);\n'
        '    trace_count=count;\n    if (count) trace_type=faad_showbits(ld,4);\n'+anchor,1)
    if function.count('    return 0;')!=1:raise ValueError('Ambiguous FAAD return')
    function=function.replace('    return 0;',
        '    yoradio_trace_fil(trace_begin,trace_payload,faad_get_processed_bits(ld),trace_type,trace_count);\n'
        '    return 0;',1)
    return source[:start]+function+source[end:]


def mono_source(encoder,work):
    rate=32000;pcm=bytearray()
    for i in range(rate//2):
        sample=7000*math.sin(2*math.pi*997*i/rate)+3000*math.sin(2*math.pi*12000*i/rate)
        pcm+=struct.pack('<h',round(sample))
    wav=work/'mono.wav';aac=work/'mono.aac'
    with wave.open(str(wav),'wb') as f:
        f.setparams((1,2,rate,0,'NONE','not compressed'));f.writeframes(pcm)
    result=subprocess.run(host_command([host_path(encoder),'-t','5','-r','24000',host_path(wav),host_path(aac)]),
                          capture_output=True,check=True)
    (work/'encoder.log').write_bytes(result.stdout+result.stderr)
    return aac.read_bytes(),dict(rate=rate,channels=1,aot=5,bitrate=24000,pcm_sha256=sha(pcm),
        encoder_sha256=sha(encoder.read_bytes()),encoder_revision='716f4394641d53f0d79c9ddac3fa93b03a49f278')


def run(args):
    source=args.source.resolve();work=args.work.resolve();out=args.output.resolve()
    work.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
    archive=source.parent/f'faad2-{REVISION}.tar.gz'
    if sha(archive.read_bytes())!=ARCHIVE_SHA256:raise ValueError('Unpinned FAAD archive')
    verified=0
    with tarfile.open(archive) as tar:
        for entry in tar.getmembers():
            if entry.isfile():
                if (source.parent/entry.name).read_bytes()!=tar.extractfile(entry).read():
                    raise ValueError('Modified reference: '+entry.name)
                verified+=1
    traced=work/'syntax-trace.c'
    traced.write_text(instrument((source/'libfaad/syntax.c').read_text()),encoding='utf-8',newline='\n')
    command=['gcc','-O2','-fno-strict-aliasing','-ffloat-store','-DAPPLY_DRC',
        '-DHAVE_INTTYPES_H=1','-DHAVE_MEMCPY=1','-DHAVE_STRING_H=1','-DHAVE_STRINGS_H=1',
        '-DHAVE_SYS_STAT_H=1','-DHAVE_SYS_TYPES_H=1','-DHAVE_LRINTF=1','-DPACKAGE_VERSION="trace"',
        '-I'+host_path(source/'include'),'-I'+host_path(source/'libfaad')]
    command += [host_path(traced if p.name=='syntax.c' else p) for p in sorted((source/'libfaad').glob('*.c'))]
    probe=ROOT/'tools/codec_benchmark/faad_fil_probe.c'
    exe=work/'fil-probe';command += [host_path(probe),'-lm','-o',host_path(exe)]
    result=subprocess.run(host_command(command),capture_output=True)
    (work/'build.log').write_bytes(result.stdout+result.stderr);result.check_returncode()
    inputs={}
    existing=ROOT/'tests/fixtures/aac_stream_format'
    pinned=json.loads((existing/'manifest.json').read_text())['files']
    for name in ('he-44100-stereo','he-48000-stereo','hev2-44100-stereo'):
        data=(existing/(name+'.aac')).read_bytes();meta=pinned[name+'.aac']
        if sha(data)!=meta['sha256']:raise ValueError('Changed input '+name)
        inputs[name]=(data,dict(rate=meta['sample_rate'],channels=meta['channels'],aot=meta['audio_object_type']))
    inputs['he-32000-mono']=mono_source(args.encoder.resolve(),work)
    manifest=dict(faad_revision=REVISION,archive_sha256=ARCHIVE_SHA256,verified_source_files=verified,
        trace_source_sha256=sha(traced.read_bytes()),probe_sha256=sha(probe.read_bytes()),
        executable_sha256=sha(exe.read_bytes()),cases={})
    for name,(data,metadata) in inputs.items():
        original=out/('source-'+name+'.aac');original.write_bytes(data)
        result=subprocess.run(host_command([host_path(exe),host_path(original)]),capture_output=True)
        (out/(name+'.trace')).write_bytes(result.stdout)
        (work/(name+'.stderr')).write_bytes(result.stderr);result.check_returncode()
        spans={};all_spans={};trace=result.stdout.decode()
        for line in trace.splitlines():
            if line.startswith('FIL '):
                index,*span=map(int,line.split()[1:])
                all_spans.setdefault(index,[]).append(span)
                if span[-2] in SBR_TYPES:spans.setdefault(index,[]).append(span)
        frames=adts_frames(data)
        if set(spans)!=set(range(len(frames))) or any(len(s)!=1 for s in spans.values()):
            raise ValueError('Expected exactly one SBR FIL in every source frame: '+name)
        missing=b''.join(remove_sbr(f,spans[i][0],[s for s in all_spans[i] if s[0]>=spans[i][0][2]])
                         for i,f in enumerate(frames))
        missing_path=out/('missing-'+name+'.aac');missing_path.write_bytes(missing)
        entry=dict(**metadata,frames=len(frames),source_sha256=sha(data),missing_sha256=sha(missing),
                   source_bytes=len(data),missing_bytes=len(missing),trace_sha256=sha(result.stdout))
        # Independently parse the complete modified stream; it must have no SBR FIL.
        result=subprocess.run(host_command([host_path(exe),host_path(missing_path)]),capture_output=True)
        (out/(name+'-missing.trace')).write_bytes(result.stdout)
        (work/(name+'-missing.stderr')).write_bytes(result.stderr);result.check_returncode()
        if any(line.startswith('FIL ') and int(line.split()[-2]) in SBR_TYPES for line in result.stdout.decode().splitlines()):
            raise ValueError('SBR element remains')
        entry['missing_trace_sha256']=sha(result.stdout)
        manifest['cases'][name]=entry
        print(name,len(frames),'frames; SBR removed, AAC core bits unchanged',flush=True)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    (work/'build-command.json').write_text(json.dumps(command,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--encoder',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args())
