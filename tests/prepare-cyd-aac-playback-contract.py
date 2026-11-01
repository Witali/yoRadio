"""Prepare complete public AAC task contracts without freezing production sources.

The PCM contract is the committed same-vendor native checkpoint, not an
independent codec-conformance oracle. No decoder, SDK or emulator runs here.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'tests/results/cyd-aac-public-config-20261101'
MANIFEST_SHA='f22687d4e404e0c45672f225322827ffb54061795b21acb96ff3045f4928a23d'
ARCHIVE_SHA='3a8b1eceb58eb5b2560d1bf763823b1378177780d151d60bc5d167225c17c1af'
READER_SHA='8172f773435878c5c6a6fadb3285d9db41f5727dab44e8593953480f171f58fd'
FIXTURE_MANIFEST_SHA='ac18a7e4a990682b3ce9f217408571c794556096571802bac966b5905635bc1c'
RATES=(96000,88200,64000,48000,44100,32000,24000,22050,16000,12000,11025,8000,7350)


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(body):return hashlib.sha256(body).hexdigest()


def adts(body):
    at=0;frames=[]
    while at<len(body):
        head=body[at:at+7]
        need(len(head)==7 and head[0]==255 and head[1]&246==240,'complete ADTS sync/header')
        index=(head[2]>>2)&15;size=((head[3]&3)<<11)|(head[4]<<3)|(head[5]>>5)
        need(index<len(RATES) and not head[6]&3 and size>=(7 if head[1]&1 else 9) and at+size<=len(body),
             'independently counted complete one-block ADTS frame')
        frames.append(dict(offset=at,bytes=size,end=at+size,core_rate=RATES[index],
            core_channels=((head[2]&1)<<2)|(head[3]>>6),profile=(head[2]>>6)&3))
        at+=size
    need(at==len(body) and len(frames)>=6,'entire original fixture and enough real frames for a bounded partial hold')
    return frames


def contracts():
    need(sha((PUBLIC/'manifest.json').read_bytes())==MANIFEST_SHA and
         sha((PUBLIC/'captures.zip').read_bytes())==ARCHIVE_SHA,'committed complete public checkpoint identities')
    manifest=json.loads((PUBLIC/'manifest.json').read_bytes());lookup={row['path']:row for row in manifest['files']}
    with zipfile.ZipFile(PUBLIC/'captures.zip') as archive:
        def take(name):
            pin=lookup[name];body=archive.read(pin['blob'])
            need(len(body)==pin['bytes'] and sha(body)==pin['sha256'],'exact original public checkpoint byte binding')
            return body
        report=json.loads(take('native02/report.json'))
        log=take('native02/qemu.stdout.log')+b'\n'+take('native02/qemu.stderr.log')
    need(report['passed'] and report['completed'] and report['all_bound_inputs_current'] and
         report['target']=='esp32' and not report['full_conformance_qualified'] and not report['private_abi_used'] and
         not report['compact_owner_ported'],'passing public same-vendor integration contract scope')
    need(all(row['state']=='complete' and row['exit_status']==0 for row in report['commands']),
         'every original native command terminal zero')
    reader_path=ROOT/'tests/run-cyd-aac-public-config-qemu.py'
    need(sha(reader_path.read_bytes())==READER_SHA,'pinned reviewed canonical public transcript reader')
    spec=importlib.util.spec_from_file_location('committed_public_aac_reader',reader_path)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    measured=reader.validate_log(log.decode('utf-8'))
    need(measured==report['measurements'],'all36 actual public configuration/input cases independently recounted')
    folder=ROOT/'tests/fixtures/aac_stream_format'
    need(sha((folder/'manifest.json').read_bytes())==FIXTURE_MANIFEST_SHA,'complete canonical FDK fixture manifest')
    source=json.loads((folder/'manifest.json').read_bytes());entries=[];blob=bytearray()
    for number,(name,pin) in enumerate(source['files'].items()):
        body=(folder/name).read_bytes()
        need(len(body)==pin['size_bytes'] and sha(body)==pin['sha256'],'complete unchanged original synthetic FDK fixture')
        frames=adts(body);geometry={(row['core_rate'],row['core_channels'],row['profile']) for row in frames}
        need(len(geometry)==1,'one original ADTS configuration per source fixture')
        core_rate,core_channels,profile=geometry.pop()
        rows=[row for row in measured['cases'] if row['id']==number and row['mode']==2]
        need(len(rows)==4 and {row['chunk'] for row in rows}=={len(body),4096,257,1},'complete public reference input schedules')
        actual=rows[0]
        need(all(tuple(row[key] for key in ('pcm','sha256','rate','channels','samples'))==
                 tuple(actual[key] for key in ('pcm','sha256','rate','channels','samples')) for row in rows),
             'whole same-vendor PCM contract is invariant across all original splits')
        hold=frames[2]['end']
        need(0<hold<len(body) and actual['pcm']==len(frames)*1024*(pin['sample_rate']//core_rate)*pin['channels']*2,
             'independent early encoded hold boundary and complete PCM geometry')
        entries.append(dict(id=number,name=name,path=(Path('tests/fixtures/aac_stream_format')/name).as_posix(),
            blob_offset=len(blob),bytes=len(body),sha256=sha(body),adts_frames=frames,hold_after_frame=3,hold_offset=hold,
            nominal_source_aot=pin['audio_object_type'],core_rate=core_rate,core_channels=core_channels,
            rate=actual['rate'],channels=actual['channels'],bits=actual['bits'],pcm_bytes=actual['pcm'],
            pcm_sha256=actual['sha256'],pcm_frames=actual['samples'],public_reference_stereo_differences=actual['stereo_differences']))
        blob+=body
    transitions=[
        dict(name='LC_RATE',parts=[0,2],kind='public ADTS sample-rate change'),
        dict(name='LC_LAYOUT',parts=[1,0],kind='public ADTS channel/rate change'),
        dict(name='LATE_HE',parts=[1,3],kind='public channel change plus late SBR'),
        dict(name='LATE_HEV2',parts=[1,5],kind='implicit late SBR/PS with unchanged ADTS core geometry'),
    ]
    for transition in transitions:
        encoded=b''.join(bytes(blob[entries[i]['blob_offset']:entries[i]['blob_offset']+entries[i]['bytes']]) for i in transition['parts'])
        transition.update(bytes=len(encoded),sha256=sha(encoded),requires_continuous_public_reference=True,
            independently_concatenated_pcm_is_valid=False,nominal_transition_required_for_observation_pass=False)
    return dict(passed=True,prepared_only=True,production_sources_frozen=False,decoder_executed=False,
        target_executed=False,independent_codec_conformance=False,private_abi_used=False,compact_owner_ported=False,
        reference_manifest_sha256=MANIFEST_SHA,reference_archive_sha256=ARCHIVE_SHA,reference_reader_sha256=READER_SHA,
        same_vendor_pcm_integration_oracle=True,fixtures=entries,continuous_observations=transitions,
        lifecycle_cases=['EOF_mixed','partial_Stop_reopen','partial_maintenance_resume','EOF_one_byte','EOF_257','EOF_4096'],
        task_bindings=dict(stream=dict(core=0,priority=3,stack=6144),decode=dict(core=1,priority=5,stack=16384),
                           output=dict(core=1,priority=6,stack=4096))),bytes(blob)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh task-local preparation directory')
    report,blob=contracts();out.mkdir(parents=True)
    (out/'contract.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    (out/'fixtures.bin').write_bytes(blob)
    (out/'controller.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(passed=True,prepared_only=True,production_sources_frozen=False,fixtures=6,
        frozen_public_cases_recounted=36,continuous_reference_observations=4,decoder_executed=False)))


if __name__=='__main__':
    sys.dont_write_bytecode=True
    main()
