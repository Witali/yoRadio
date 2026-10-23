"""Bind completed format references without changing the original dual NONPASS."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'.build/cyd-vorbis-format-corpus-qualified-01'
SOURCE=ROOT/'.build/cyd-vorbis-format-corpus-host-01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,message):
    if not ok:raise RuntimeError(message)

def main():
    need(not OUT.exists(),'Fresh qualification output required')
    OUT.mkdir()
    original=SOURCE/'report.json';r=json.loads(original.read_text())
    outer=ROOT/'.build/cyd-vorbis-format-corpus-host-01-command.json';receipt=json.loads(outer.read_text())
    need(receipt['status']=='TERMINAL' and type(receipt['returncode']) is int and receipt['returncode']==1,'Actual completed dual-reference NONPASS required')
    need(r['completed'] is True and r['xiph_reference_qualified'] is True and r['dual_reference_qualified'] is False and
         len(r['cases'])==17 and len(r['commands'])==34 and len(r['failures'])==10,'Original corpus scope/result differs')
    need(all(sha(path)==value['sha256']==sha(SOURCE/value['snapshot']) for path,value in r['inputs'].items()),'Frozen inputs changed')
    need(all(sha(path)==value for path,value in r['tools'].items()),'Reference tools changed')
    for path,row in receipt['logs'].items():need(sha(path)==row['sha256'] and Path(path).stat().st_size==row['bytes'],'Outer command stream changed')
    commands={c['name']:c for c in r['commands']};cases=[];native_compared=0;refused=0
    for case in r['cases']:
        encoded=case['input'];need('libvorbis' in case['decoded'],'Missing Xiph result')
        xiph=case['decoded']['libvorbis'];frames=encoded.get('expected_packet_samples',encoded.get('expected_packet_frames'))
        need((xiph['rate'],xiph['channels'],xiph['bits'])==(encoded['rate'],encoded['channels'],16) and
             xiph['frames']==frames[1:] and xiph['pcm_bytes']==encoded['expected_s16le_bytes'] and
             xiph['transition_nonzero_bytes'] and all(n>0 for n in xiph['transition_nonzero_bytes'].values()),'Actual reference metadata/count/nonzero evidence differs')
        for decoder in ('vorbis','libvorbis'):
            command=commands['cases/'+case['id']+'/decode-'+decoder];path=SOURCE/command['receipt']
            need(sha(path)==command['sha256'],'Reference receipt changed')
            c=json.loads(path.read_text());need(c['status']=='TERMINAL' and type(c['returncode']) is int,'Reference command not terminal')
            for log,row in c['logs'].items():need(sha(log)==row['sha256'] and Path(log).stat().st_size==row['bytes'],'Reference stream changed')
            need(sha(c['argv'][0])==c['executable_sha256'],'Reference executable identity differs')
            if decoder=='libvorbis' or 'vorbis' in case['decoded']:
                need(c['returncode']==0,'Qualified reference command must exit0')
            else:
                need(c['returncode']==3199971767,'Unexpected native refusal status')
                stderr=next(Path(log) for log in c['logs'] if log.endswith('.stderr.log'))
                need('Codebook lookup type not supported.' in stderr.read_text(errors='replace'),'Native refusal is not the documented lookup2 restriction')
        compared='vorbis' in case['decoded']
        if compared:
            need(not case['failures'] and case['cross_reference_max_abs_error']<=2,'Native PCM cross-reference mismatch')
            native_compared+=1
        else:
            need(len(case['failures'])==1 and case['failures'][0]['stage']=='vorbis','Unexpected case failure')
            refused+=1
        cases.append(dict(id=case['id'],xiph_qualified=True,native_compared=compared,
            native_lookup2_refusal=not compared,pcm_sha256=xiph['pcm_sha256'],pcm_bytes=xiph['pcm_bytes'],
            frames=xiph['frames'],transition_nonzero_bytes=xiph['transition_nonzero_bytes']))
    need((native_compared,refused)==(7,10),'Native support coverage differs')
    xiph_checks=[c for c in r['metamorphic_checks'] if c['decoder']=='libvorbis']
    need(len(xiph_checks)==4 and all(c['passed'] is True for c in xiph_checks),'Xiph book-representation/sequence PCM checks failed')
    result=dict(schema='public-vorbis-format-corpus-reference-qualification-v1',completed=True,
        reference_corpus_qualified=True,original_dual_reference_passed=False,
        original_report_sha256=sha(original),original_outer_receipt_sha256=sha(outer),
        cases=cases,xiph_cases=17,native_compared=7,native_lookup2_refusals=10,
        xiph_metamorphic_checks=xiph_checks,paired_raw_packets=sum(c['input']['packet_count'] for c in r['cases']),
        expected_pcm_bytes=sum(c['pcm_bytes'] for c in cases),
        primary_basis=dict(vorbis='https://xiph.org/vorbis/doc/Vorbis_I_spec.html',
          ffmpeg_native_guard='https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.1.1/libavcodec/vorbisdec.c',
          note='n8.1.1 lines400-403 reject lookup_type>=2; Vorbis I3.2.1 defines legal lookup2. Actual Xiph decode, not the spec alone, qualifies these complete carriers.'),
        target_executed=False,production_changed=False,full_G6_qualified=False)
    (OUT/'qualification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('reference_corpus_qualified','xiph_cases','native_compared','native_lookup2_refusals','paired_raw_packets','expected_pcm_bytes')}))

if __name__=='__main__':main()
