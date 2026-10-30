"""Verify published Opus evidence without building, decoding or running QEMU."""
import hashlib
import importlib.util
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'tests/results/cyd-opus-20261030'
READER_SHA='5e49b9bbf143917ee370fa1c6984ac8e96eb73b3110a89a91178176f0d7d3acc'
FIXTURE_SHA='53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11'
PCM_SHA='a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b'


def need(value,reason):
    if not value: raise ValueError(reason)


def sha(body): return hashlib.sha256(body).hexdigest()


def fixture_accounting(encoded):
    """Independently reconstruct this Ogg fixture and its RFC 7845 timeline."""
    pages=[]; packets=[]; pending=bytearray(); position=0; serial=None
    while position<len(encoded):
        need(encoded[position:position+4]==b'OggS' and position+27<=len(encoded),'complete Ogg page capture/header')
        header=encoded[position:position+27]
        need(header[4]==0 and not header[5]&~7,'Ogg version and page flags')
        count=header[26]; lacing=encoded[position+27:position+27+count]
        need(len(lacing)==count,'complete Ogg segment table')
        end=position+27+count+sum(lacing)
        need(end<=len(encoded),'complete Ogg page body')
        page=bytearray(encoded[position:end]); expected=int.from_bytes(page[22:26],'little'); page[22:26]=b'\0'*4
        crc=0
        for byte in page:
            crc^=byte<<24
            for _ in range(8): crc=((crc<<1)^(0x04c11db7 if crc&0x80000000 else 0))&0xffffffff
        need(crc==expected,'independent Ogg page CRC')
        actual_serial=int.from_bytes(header[14:18],'little')
        if serial is None: serial=actual_serial
        need(actual_serial==serial and int.from_bytes(header[18:22],'little')==len(pages),
             'single logical stream with consecutive Ogg page sequence')
        need(bool(header[5]&1)==bool(pending) and bool(header[5]&2)==(not pages),'continuation reconstruction and single BOS')
        granule=int.from_bytes(header[6:14],'little')
        cursor=position+27+count; completed=[]
        for size in lacing:
            pending.extend(encoded[cursor:cursor+size]); cursor+=size
            if size<255:
                completed.append(len(packets)); packets.append(bytes(pending)); pending.clear()
        pages.append(dict(index=len(pages),granule=granule,eos=bool(header[5]&4),completed_packets=completed))
        position=end
    need(not pending and len(pages)==15 and pages[-1]['eos'] and not any(page['eos'] for page in pages[:-1]),
         'all fixture bytes, continued packets and one terminal EOS page')
    head=packets[0]
    need(head[:8]==b'OpusHead' and len(head)==19 and head[8]==1 and head[9]==2 and head[18]==0 and
         packets[1].startswith(b'OpusTags'),'stereo mapping-family-zero Opus headers')
    preskip=int.from_bytes(head[10:12],'little')
    durations=[]
    for packet in packets[2:]:
        need(packet,'nonempty Opus audio packet')
        config=packet[0]>>3; code=packet[0]&3
        need(config>=16,'CELT mode packet TOC')
        if code==0: frames=1
        elif code in (1,2): frames=2
        else:
            need(len(packet)>=2,'complete Opus frame-count header')
            frames=packet[1]&63
        duration=(120<<(config&3))*frames
        need(frames>0 and duration==960,'each fixture CELT packet totals 20 ms at 48 kHz')
        durations.append(duration)
    raw=sum(durations); cumulative=0; initial_offset=None
    for page in pages:
        audio=[index-2 for index in page['completed_packets'] if index>=2]
        cumulative+=sum(durations[index] for index in audio)
        if audio:
            need(page['granule']!=0xffffffffffffffff,'completed audio page has a granule')
            if initial_offset is None: initial_offset=page['granule']-cumulative
            if not page['eos']: need(page['granule']==cumulative+initial_offset,'nonterminal granule/sample accounting')
    terminal=pages[-1]['granule']; tail=raw+initial_offset-terminal
    playback=terminal-initial_offset-preskip
    result=dict(pages=len(pages),valid_crc_pages=len(pages),consecutive_pages=True,
                reconstructed_packets=len(packets),audio_packets=len(durations),all_audio_celt_20ms=True,
                raw_frames=raw,pre_skip_frames=preskip,eos_granule=terminal,initial_granule_offset=initial_offset,
                end_trim_frames=tail,logical_playback_frames=playback,logical_pcm16_stereo_bytes=playback*4)
    need(len(durations)==551 and raw==528960 and preskip==312 and terminal==528312 and
         initial_offset==0 and tail==648 and playback==528000,'independent fixture timeline and required trims')
    return result


def verify():
    manifest=json.loads((FOLDER/'direct-manifest.json').read_bytes())
    archive_path=FOLDER/manifest['archive']['path']
    need(archive_path.name=='direct-captures.zip' and archive_path.parent==FOLDER and
         archive_path.stat().st_size==manifest['archive']['bytes'] and
         sha(archive_path.read_bytes())==manifest['archive']['sha256'],'complete published archive identity')
    rows=manifest['files']
    need(len({row['path'] for row in rows})==len(rows)==manifest['logical_files'],'complete unique logical inventory')
    blobs={row['blob'] for row in rows}
    with zipfile.ZipFile(archive_path) as archive:
        need(len(archive.infolist())==len(blobs)==manifest['physical_files'] and set(archive.namelist())==blobs,
             'exact deduplicated physical archive inventory')
        physical={name:archive.read(name) for name in blobs}
    files={}
    for row in rows:
        path=PurePosixPath(row['path'])
        need(path.as_posix()==row['path'] and not path.is_absolute() and '..' not in path.parts and
             '\\' not in row['path'] and ':' not in row['path'],'canonical logical path')
        body=physical[row['blob']]
        need(re.fullmatch(r'blobs/[0-9a-f]{64}',row['blob']) and row['blob']=='blobs/'+sha(body) and
             sha(body)==row['sha256'] and len(body)==row['bytes'],'every published byte')
        need(path.suffix.lower() not in ('.elf','.bin'),'compiled image bytes are never published')
        files[row['path']]=body
    def take(name):
        need(name in files,'required saved evidence: '+name)
        return files[name]
    def data(name): return json.loads(take(name))
    omitted={row['path']:row for row in manifest['compiled_images_omitted']}
    need(len(omitted)>=10 and all(name not in files and row['original_retained_locally'] and
         row['byte_payload_published'] is False and row['bytes']>0 and
         re.fullmatch(r'[0-9a-f]{64}',row['sha256']) for name,row in omitted.items()),
         'explicit local-only image hash provenance; no omitted binary bytes checked')
    excluded={row['path']:row for row in manifest['other_bytes_omitted']}
    need(all(name not in files and row['original_retained_locally'] and row['byte_payload_published'] is False
             for name,row in excluded.items()),'explicit other publication omissions')
    reader_path=ROOT/'tests/run-cyd-espressif-opus-qemu.py'
    reader_bytes=reader_path.read_bytes()
    need(sha(reader_bytes)==READER_SHA==manifest['reader_sha256'] and
         take('verification/reader.py')==reader_bytes,'reviewed canonical data-only reader identity')
    need(take('verification/verifier.py')==Path(__file__).read_bytes(),'standalone verifier identity')
    spec=importlib.util.spec_from_file_location('reviewed_opus_direct_reader',reader_path)
    reader=importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)
    measurements={}
    for number in ('01','02'):
        prefix='captures/direct'+number+'/'
        report=data(prefix+'report.json')
        need(report['target']=='esp32' and report['target_executed'] and report['fixture_sha256']==FIXTURE_SHA and
             report['fixture_bytes']==706319 and report['output_capacity']==12288 and
             report['vendor_revision']==reader.REVISION and report['sdk_revision']==reader.SDK_HEAD['esp32'],
             'unchanged public vendor, fixture and original output capacity')
        need(not report['production_firmware'] and not report['physical_device'] and not report['private_abi_used'] and
             not report['custom_decoder'] and not report['full_conformance_qualified'],'bounded diagnostic scope')
        if number=='01':
            need(not report['passed'] and not report['completed'] and
                 report['failure']=='one-byte feed really exercises pending input','original reader failure stays nonpassing')
        else: need(report['passed'] and report['completed'],'fresh authoritative successful native campaign')
        for command in report['commands']:
            need(command['state']=='complete' and command['pid']>0 and command['exit_status']==0,
                 'actual native command terminal zero')
            for stream in ('stdout','stderr'):
                need(sha(take(prefix+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],
                     'exact original native child output')
        child=json.loads(take(prefix+'sdk-child.json').decode('utf-8-sig'))
        need(child['pid']>0 and child['exit_status']==0,'actual SDK compiler-driver child terminal zero')
        for pin in report['inputs'].values():
            name=prefix+pin['snapshot']
            if name in excluded:
                need(excluded[name]['sha256']==pin['sha256'] and excluded[name]['bytes']==pin['bytes'],
                     'omitted source hash provenance')
            else:
                body=take(name)
                need(sha(body)==pin['sha256'] and len(body)==pin['bytes'],'all frozen published input bytes')
        for name,digest in report['build_outputs'].items():
            logical=prefix+name
            if logical in omitted: need(omitted[logical]['sha256']==digest,'omitted image hash binding')
            elif logical in excluded: need(excluded[logical]['sha256']==digest,'omitted output hash binding')
            else: need(sha(take(logical))==digest,'every published build output byte binding')
        log=(take(prefix+'qemu.stdout.log')+b'\n'+take(prefix+'qemu.stderr.log')).decode('utf-8')
        measured=reader.validate_log(log)
        need(measured==manifest['measurements'][number] and measured['reference']==data(prefix+'baseline.json')==report['baseline'],
             'independently recounted baseline and all exact split-feed results')
        if number=='02': need(measured==report['measurements'],'original passing reader result retained')
        need(measured['baseline']['pcm']==2115840 and measured['baseline']['sha256']==PCM_SHA and
             measured['retained_after_unregister_bytes']==100 and not measured['total_ownership_zero_retention'] and
             not measured['full_pcm_independent_oracle'],'actual raw vendor identity and honest persistent retention')
        need(all(row['input']==706319 and row['pcm']==2115840 and row['sha256']==PCM_SHA and
                 row['before']==row['after']==270632 for row in measured['cases']),
             'all complete encoded bytes and exact stable stream ownership')
        measurements[number]=measured
    old=take('captures/direct01/sources/controller.py')
    removed=b"    need(rows[-1]['coalesces']>0,'one-byte feed really exercises pending input')\n"
    need(old.count(removed)==1 and old.replace(removed,b'')==reader_bytes==take('captures/direct02/sources/controller.py'),
         'exact single unsupported reader-assumption correction; native source is unchanged')
    first=data('captures/direct01/report.json')['inputs']; second=data('captures/direct02/report.json')['inputs']
    need(set(first)==set(second) and all(first[name]==second[name] for name in first if
         first[name]['snapshot']!='sources/controller.py'),'all other frozen native inputs unchanged between attempts')
    encoded=take('captures/direct02/project/main/fixture.ogg')
    need(sha(encoded)==FIXTURE_SHA and fixture_accounting(encoded)==manifest['fixture_accounting'],
         'independent CRC, packet reconstruction, TOC duration and granule/pre-skip arithmetic')
    lib=data('reference/libopus/report.json')
    need(lib['passed'] and lib['completed'] and lib['fixture_sha256']==FIXTURE_SHA and
         lib['decoder']=='FFmpeg libopus wrapper' and not lib['independent_pcm_conformance_claim'] and
         not lib['bundled_libopus_version_reported'] and lib['pcm_bytes']==2112000 and
         sha(take('reference/libopus/playback.pcm'))==lib['pcm_sha256'] and
         len(take('reference/libopus/playback.pcm'))==lib['pcm_bytes'],'separate libopus playback-length observation with explicit limits')
    for command in lib['commands']:
        need(command['state']=='complete' and command['pid']>0 and command['exit_status']==0,'libopus wrapper command status')
        for stream in ('stdout','stderr'):
            need(sha(take('reference/libopus/'+command['name']+'.'+stream+'.log'))==command[stream+'_sha256'],
                 'original libopus wrapper logs')
    need(manifest['required_pending_opus_trim'] and manifest['raw_vendor_frames']==528960 and
         manifest['logical_playback_frames']==528000 and manifest['pre_skip_frames']==312 and
         manifest['end_trim_frames']==648,'raw extra output remains a required correctness gate')
    return dict(passed=True,logical_files=len(rows),physical_files=len(blobs),cases=[4096,257,1],
                original_reader_failure_preserved=True,actual_native_runs_repeated=False,
                artifact_code_executed=False,raw_vendor_pcm_bytes=2115840,logical_playback_pcm_bytes=2112000,
                standard_complete=False,required_pending_opus_trim=True,terminal_registry_retained_bytes=100,
                omitted_compiled_image_files=len(omitted),omitted_binary_bytes_verified=False)


if __name__=='__main__': print(json.dumps(verify()))
