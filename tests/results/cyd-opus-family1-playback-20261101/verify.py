"""Validate saved adapter HOST evidence without executing archived/native code or payload."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import zipfile
FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]
def need(value,why):
    if not value:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--require-current',action='store_true');args=parser.parse_args()
    manifest=json.loads((FOLDER/'manifest.json').read_bytes());pin=manifest['archive'];archive=FOLDER/pin['path']
    need(archive.name=='captures.zip' and sha(archive.read_bytes())==pin['sha256'] and archive.stat().st_size==pin['bytes'],'archive byte identity')
    rows=manifest['files'];need(len(rows)==manifest['logical_files']==len({r['path'] for r in rows}),'logical census');blobs={}
    with zipfile.ZipFile(archive) as z:
        need(len(z.infolist())==manifest['physical_blobs']==len({r['blob'] for r in rows}),'physical census')
        for entry in z.infolist():
            body=z.read(entry);need(re.fullmatch('blobs/[a-f0-9]{64}',entry.filename) and entry.filename=='blobs/'+sha(body),'physical identities')
            need(not body.startswith((b'\x7fELF',b'MZ',b'!<arch>\n',b'OggS',b'OFAM101\0')),'no executable/encoded payload');blobs[entry.filename]=body
    data={}
    for row in rows:
        p=PurePosixPath(row['path']);need(not p.is_absolute() and '..' not in p.parts and p.as_posix()==row['path'],'contained logical path')
        body=blobs[row['blob']];need(len(body)==row['bytes'] and sha(body)==row['sha256'],'logical identities');data[row['path']]=body
    omitted=manifest['omitted_local_files'];need(all(name not in data and r['original_retained_locally'] and r['byte_payload_published'] is False for name,r in omitted.items()),'explicit local payload omissions')
    def take(name):need(name in data,'required original evidence '+name);return data[name]
    def identity(name,digest,size):
        if name in data:need(sha(data[name])==digest and len(data[name])==size,'included evidence identity')
        else:need(name in omitted and omitted[name]['sha256']==digest and omitted[name]['bytes']==size,'omitted identity, payload not read')
    reports={}
    for label,digest in manifest['report_sha256'].items():
        body=take(label+'/report.json');need(sha(body)==digest,'original report identity');report=json.loads(body);reports[label]=report
        for source in report['sources']:identity(label+'/'+source['snapshot'],source['sha256'],source['bytes'])
        for command in report['commands']:
            need(command['state']=='complete' and command['pid']>0 and isinstance(command['exit_status'],int),'actual terminal child record')
            for stream in ('stdout','stderr'):
                r=command[stream];identity(label+'/'+r['path'],r['sha256'],r['bytes'])
        for key in ('executable','compiler_dependencies'):
            if key in report:
                r=report[key];identity(label+'/'+r['path'],r['sha256'],r['bytes'])
        for name,r in report['fixtures'].items():identity(label+'/fixtures/'+name,r['sha256'],r['bytes'])
    failed=reports['host01'];need(not failed['passed'] and failed['commands'][-1]['name']=='compiler-version' and failed['commands'][-1]['exit_status']==4294967295,'original WSL sandbox DWORD preserved')
    failed=reports['host02'];need(not failed['passed'] and failed['commands'][-1]['name']=='build' and failed['commands'][-1]['exit_status']==1 and b'misleading-indentation' in take('host02/build.stderr.log'),'genuine initial test-source -Werror failure preserved')
    original=reports['host03'];need(original['passed'] and original['completed'] and all(c['exit_status']==0 for c in original['commands']),'original33/25 PASS before stronger pending-owner witness')
    final=reports['host04'];need(final['passed'] and final['completed'] and final['all_source_bindings_current'] and all(c['exit_status']==0 for c in final['commands']),'qualified final capture')
    actual=json.loads(take('host04/test.stdout.log'));need(actual==final['measurements']==manifest['final_measurements']==original['measurements'],'exact original summary/census')
    need(actual['positive_schedules']==33 and actual['host_contract_controls']==25 and actual['creator_libogg_walks']==60 and actual['actual_page_acks']==1170 and
        actual['creator_pcm_samples_exact']==3898624 and actual['eos_close_retry']==1 and actual['maximum_unique_plane_bytes']==92160 and actual['maximum_output_chunk_bytes']==2048,'bounded actual HOST measurements')
    need(actual['whole_original_120ms_packets']==92 and final['fixtures']['stereo120.packets']['complete_original_packets']==92 and final['fixtures']['stereo120.packets']['coded_bodies_unchanged'],'complete original120ms bodies')
    need(actual['gain_metadata_only'] and actual['scripted_host_statuses'] and not actual['native_esp_oom_qualified'] and not actual['production_selected'] and
        final['host_public_api_test_double'] and final['creator_synthesis_real'] and final['creator_libogg_crc_and_packet_walk'],'honest creator-backed HOST/status scope')
    need(not manifest['native_executed'] and not manifest['production_selected'] and not manifest['all_standard_layouts_qualified'] and
        not manifest['comment_length_utf8_validation_qualified'] and not manifest['formal_codec_conformance_qualified'],'remaining format/native gates explicit')
    for path,digest in manifest['canonical_source_sha256'].items():
        matching=[r for r in final['sources'] if r['path'].replace('\\','/').endswith('/'+path)]
        if path.endswith('/verify.py'):need(sha((ROOT/path).read_bytes())==digest,'current data verifier')
        else:need(len(matching)==1 and matching[0]['sha256']==digest,'checkpoint frozen canonical source')
        if args.require_current:need(sha((ROOT/path).read_bytes())==digest,'current reviewed checkpoint '+path)
    print(json.dumps(dict(checkpoint_verified=True,current_sources_required=args.require_current,preserved_captures=4,logical_files=len(data),native_executed=False,
        production_selected=False,comment_validation_qualified=False,omitted_executable_encoded_or_PCM_payload_read=False)))
if __name__=='__main__':main()
