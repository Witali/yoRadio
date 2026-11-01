"""Verify saved Tags/adapter HOST evidence; never execute archived code or omitted payload."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import zipfile
ROOT=Path(__file__).resolve().parents[1]
FOLDERS={'tags':'cyd-opus-tags-stream-20261101','playback':'cyd-opus-family1-playback-tags-20261101'}
def need(value,why):
    if not value:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--checkpoint',required=True,choices=FOLDERS);parser.add_argument('--require-current',action='store_true');args=parser.parse_args()
    folder=ROOT/'tests/results'/FOLDERS[args.checkpoint];manifest=json.loads((folder/'manifest.json').read_bytes());pin=manifest['archive'];archive=folder/pin['path']
    need(manifest['kind']==args.checkpoint and archive.name=='captures.zip' and sha(archive.read_bytes())==pin['sha256'] and archive.stat().st_size==pin['bytes'],'exact archive identity')
    rows=manifest['files'];need(len(rows)==manifest['logical_files']==len({r['path'] for r in rows}),'unique logical census');blobs={}
    with zipfile.ZipFile(archive) as z:
        need(len(z.infolist())==manifest['physical_blobs']==len({r['blob'] for r in rows}),'physical census')
        for entry in z.infolist():
            body=z.read(entry);need(re.fullmatch('blobs/[a-f0-9]{64}',entry.filename) and entry.filename=='blobs/'+sha(body),'physical identities')
            need(not body.startswith((b'\x7fELF',b'MZ',b'!<arch>\n',b'OggS',b'OFAM101\0',b'OTUF101\0')),'no executable/encoded/vector payload');blobs[entry.filename]=body
    data={}
    for row in rows:
        p=PurePosixPath(row['path']);need(not p.is_absolute() and '..' not in p.parts and p.as_posix()==row['path'],'contained logical path');body=blobs[row['blob']]
        need(sha(body)==row['sha256'] and len(body)==row['bytes'],'logical identities');data[row['path']]=body
    omitted=manifest['omitted_local_files'];need(all(name not in data and r['original_retained_locally'] and r['byte_payload_published'] is False for name,r in omitted.items()),'explicit local payload omissions')
    def take(name):need(name in data,'required original evidence '+name);return data[name]
    def identity(name,digest,size):
        if name in data:need(sha(data[name])==digest and len(data[name])==size,'included identity')
        else:need(name in omitted and omitted[name]['sha256']==digest and omitted[name]['bytes']==size,'omitted identity; payload not read')
    reports={}
    for label,digest in manifest['report_sha256'].items():
        body=take(label+'/report.json');need(sha(body)==digest,'original report identity');report=json.loads(body);reports[label]=report
        for row in report['sources']:identity(label+'/'+row['snapshot'],row['sha256'],row['bytes'])
        for command in report['commands']:
            need(command['state']=='complete' and command['pid']>0 and isinstance(command['exit_status'],int),'genuine terminal child')
            for stream in ('stdout','stderr'):
                row=command[stream];identity(label+'/'+row['path'],row['sha256'],row['bytes'])
        for key in ('executable','compiler_dependencies'):
            if key in report:
                row=report[key];identity(label+'/'+row['path'],row['sha256'],row['bytes'])
        for row in report.get('layout_executables',[]):identity(label+'/'+row['path'],row['sha256'],row['bytes'])
        if 'layout_reference' in report:
            row=report['layout_reference'];identity(label+'/'+row['snapshot'],row['sha256'],row['bytes'])
        for name,row in report.get('fixtures',{}).items():identity(label+'/fixtures/'+name,row['sha256'],row['bytes'])
        if 'reference' in report:
            row=report['reference']['file'];identity(label+'/utf8-vectors.bin',row['sha256'],row['bytes'])
    final=reports[manifest['final_capture']];need(final['passed'] and final['completed'] and final['all_source_bindings_current'] and all(c['exit_status']==0 for c in final['commands']),'qualified final HOST capture')
    actual=json.loads(take(manifest['final_capture']+'/test.stdout.log'));need(actual==final['measurements']==manifest['final_measurements'],'unchanged actual summary')
    if args.checkpoint=='tags':
        need(actual['passed'] and actual['python_utf8_vectors']==1308946 and actual['declared_text_packets']==2617892 and actual['parser_schedules']==2618236 and
            actual['field_controls']==32 and actual['size_policy_controls']==3 and actual['verified_page_schedules']==actual['creator_libogg_walks']==20 and
            actual['actual_page_acks']==3398 and actual['maximum_header_bytes']==125829120 and actual['parser_bytes']==32 and actual['stream_bytes']==56,'exact declared-text/verified-page and size-policy inventory')
        need(not actual['whole_comment_allocation'] and actual['binary_tail_permitted'] and not actual['decoder_executed'],'bounded validation-only scope')
        oracle=final['reference'];rows=oracle['rows'];need(oracle['cases']==1308946 and sum(r['cases'] for r in rows)==oracle['cases'] and
            rows[0]['category']=='all_unicode_scalars' and rows[0]['cases']==1112064 and rows[0]['invalid']==0 and
            [r['cases'] for r in rows[1:]]==[256,65536,65536,65536,18],'precise Python strict oracle coverage, not all longer byte sequences')
    else:
        failed=reports['host05'];need(not failed['passed'] and failed['commands'][-1]['name']=='layout-before-build' and failed['commands'][-1]['exit_status']==1 and
            b'Is a directory' in take('host05/layout-before-build.stderr.log'),'original genuine layout-path collision retained')
        need(actual['passed'] and actual['positive_schedules']==34 and actual['host_contract_controls']==27 and actual['creator_libogg_walks']==63 and actual['actual_page_acks']==1213 and
            actual['creator_pcm_samples_exact']==3975424 and actual['eos_close_retry']==1 and actual['maximum_unique_plane_bytes']==92160 and actual['maximum_output_chunk_bytes']==2048,'complete successor adapter inventory')
        need(actual['whole_original_120ms_packets']==92 and final['fixtures']['stereo120.packets']['complete_original_packets']==92 and final['fixtures']['stereo120.packets']['coded_bodies_unchanged'],'full original120ms input bodies')
        need(actual['gain_metadata_only'] and actual['scripted_host_statuses'] and not actual['native_esp_oom_qualified'] and not actual['production_selected'],'honest metadata/HOST refusal scope')
        before=final['host_layout']['before'];after=final['host_layout']['after'];need(before==dict(adapter_bytes=2768,raw_owner_bytes=304,packet_owner_bytes=128,static_zero_bytes=0) and
            after==dict(adapter_bytes=776,raw_owner_bytes=304,packet_owner_bytes=128,static_zero_bytes=2048),'actual HOST before/after layout')
        symbol=final['static_zero_symbol'];need(symbol.encode() in take('host06/static-zero-symbol.stdout.log') and int(symbol.split()[1],16)==2048 and symbol.split()[2]=='r','actual read-only static zero symbol')
        old=json.loads((ROOT/'tests/results/cyd-opus-family1-playback-20261101/manifest.json').read_bytes());reference=final['layout_reference']
        need(reference['checkpoint_archive_sha256']==old['archive']['sha256'] and reference['sha256']==old['canonical_source_sha256']['idf/esp32-cyd2usb-native/main/opus_family1_playback.h'],'layout-only historical source provenance')
    for path,digest in manifest['canonical_source_sha256'].items():
        if path==Path(__file__).relative_to(ROOT).as_posix():need(sha((ROOT/path).read_bytes())==digest,'current data verifier')
        else:
            source=[r for r in final['sources'] if r['path'].replace('\\','/').endswith('/'+path)];need(len(source)==1 and source[0]['sha256']==digest,'frozen canonical source closure')
        if args.require_current:need(sha((ROOT/path).read_bytes())==digest,'current checkpoint '+path)
    need(manifest['comment_length_utf8_validation_qualified'] and not manifest['native_executed'] and not manifest['production_selected'] and
        not manifest['native_esp_oom_qualified'] and not manifest['target_task_stack_measured'] and not manifest['all_standard_layouts_qualified'],'bounded HOST qualification scope')
    print(json.dumps(dict(checkpoint_verified=args.checkpoint,current_sources_required=args.require_current,preserved_captures=len(reports),logical_files=len(data),
        native_executed=False,production_selected=False,omitted_binary_or_PCM_payload_read=False)))
if __name__=='__main__':main()
