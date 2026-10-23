"""Finish normative Xiph reference checks; preserve native FFmpeg NONPASS."""
import array,hashlib,json,re,subprocess,sys,wave
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
PY=Path(sys.executable).resolve(); CAPTURE=ROOT/'.build/cyd-vorbis-format-command-01.py'
OLD=ROOT/'.build/cyd-vorbis-block-host-01'; OUT=ROOT/'.build/cyd-vorbis-block-xiph-01'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def need(ok,message):
    if not ok: raise RuntimeError(message)

def main():
    need(not OUT.exists(),'Fresh Xiph completion output required')
    old=json.loads((OLD/'report.json').read_text()); outer=json.loads((ROOT/'.build/cyd-vorbis-block-host-01-command.json').read_text())
    need(old['completed'] is True and old['passed'] is False and len(old['cases'])==108 and len(old['failures'])==30,'Unexpected original matrix scope')
    need(outer['status']=='TERMINAL' and outer['returncode']==1,'Original dual-reference NONPASS must remain')
    audit=ROOT/'.build/cyd-vorbis-floor-range-audit-01/AUDIT.md'
    need(sha(audit)=='e155ee25ce646dbf770fd9c41f4ee0d2551674718a622dda0da50a7edfe95994','Unreviewed normative audit')
    tool=next(Path(path) for path in old['tools'] if Path(path).name=='ffmpeg.exe')
    need(sha(tool)==old['tools'][str(tool)],'Reference tool changed')
    OUT.mkdir(); (OUT/'sources').mkdir(); (OUT/'sources/complete.py').write_bytes(Path(__file__).read_bytes())
    (OUT/'sources/AUDIT.md').write_bytes(audit.read_bytes())
    report=dict(schema='public-vorbis-block-xiph-reference-v1',completed=False,reference_corpus_qualified=False,
        original_dual_reference_passed=False,original_report_sha256=sha(OLD/'report.json'),
        original_outer_receipt_sha256=sha(ROOT/'.build/cyd-vorbis-block-host-01-command.json'),
        normative_audit_sha256=sha(audit),ffmpeg_sha256=sha(tool),driver_sha256=sha(__file__),
        target_executed=False,production_changed=False,full_G6_qualified=False,
        coverage='all108 cases retained; Xiph reference all108, native cross-check78, native unsupported30',cases=[],failures=[])
    def save(): (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    for original in old['cases']:
        case=original['input']; name=original['id']; row=dict(id=name,input=case,reference_qualified=False,native_comparison_qualified=original['passed'])
        report['cases'].append(row)
        try:
            if original['passed']:
                need(original['cross_reference_max_abs_error']<=2 and len(original['decoded'])==2,'Original positive comparison incomplete')
                for decoder,details in original['decoded'].items():
                    need(sha(OLD/'cases'/name/(decoder+'.wav'))==details['wav_sha256'],'Original reference changed')
                    need(details['nonzero_bytes']>0 and all(details['transition_nonzero_bytes'].values()),'Original active transitions missing')
                row.update(reference_qualified=True,source='prior dual-reference pass',decoded=original['decoded'])
            else:
                need(original['error']=='Reference command failed: cases/'+name+'/decode-vorbis','Unexpected original failure')
                native_path=OLD/'cases'/name/'decode-vorbis.json'; native=json.loads(native_path.read_text())
                need(native['status']=='TERMINAL' and native['returncode']!=0,'Native refusal not terminal')
                stderr=(native_path.with_suffix('.stderr.log')).read_text()
                need('Floor value is too large for blocksize:' in stderr and case['long']<2048,'Not the audited floor restriction')
                case_out=OUT/'cases'/name; case_out.mkdir(parents=True)
                carrier=case_out/'input.ogg'; carrier.write_bytes((OLD/'cases'/name/'input.ogg').read_bytes())
                need(sha(carrier)==original['ogg_sha256'],'Carrier changed')
                output=case_out/'libvorbis.wav'; record=case_out/'decode-libvorbis.json'
                argv=[str(tool),'-nostdin','-n','-hide_banner','-loglevel','error','-xerror','-err_detect','explode',
                    '-c:a','libvorbis','-i',str(carrier),'-map','0:a:0','-map_metadata','-1','-fflags','+bitexact',
                    '-flags:a','+bitexact','-c:a','pcm_s16le','-f','wav',str(output),
                    '-map','0:a:0','-map_metadata','-1','-flags:a','+bitexact','-c:a','pcm_s16le','-f','framemd5','-']
                wrapper=subprocess.run([str(PY),'-B','-X','utf8',str(CAPTURE),'--record',str(record),'--cwd',str(ROOT),'--timeout','30','--',*argv],
                    cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
                receipt=json.loads(record.read_text()); need(wrapper.returncode==0 and receipt['status']=='TERMINAL' and receipt['returncode']==0,'Xiph reference failed')
                diagnostics=record.with_suffix('.stderr.log').read_text().splitlines()
                allowed=r'\[vorbis @ [0-9a-fA-F]+\]\s+(?:Floor value is too large for blocksize: \d+ \(\d+\)|Vorbis setup header packet corrupt \(floors\)\.|Setup header corrupt\.)\s*'
                need(all(not line or re.fullmatch(allowed,line) for line in diagnostics),'Unexplained Xiph/frontend diagnostic')
                with wave.open(str(output),'rb') as wav:
                    observed=(wav.getframerate(),wav.getnchannels(),wav.getsampwidth(),wav.getnframes()); pcm=wav.readframes(wav.getnframes())
                need(observed==(case['rate'],case['channels'],2,case['expected_raw_samples']),'Xiph WAV dimensions/count differ')
                need(any(pcm),'Xiph PCM silent')
                flags=case['mode_flags']; sizes=[case['long'] if flag else case['short'] for flag in flags]
                samples=[(a+b)//4 for a,b in zip(sizes,sizes[1:])]; offset=0; transitions={}
                for i,frames in enumerate(samples,1):
                    size=frames*case['channels']*2; region=pcm[offset:offset+size]; offset+=size
                    transition=('L' if flags[i-1] else 'S')+('L' if flags[i] else 'S')
                    transitions[transition]=transitions.get(transition,0)+sum(x!=0 for x in region)
                need(offset==len(pcm) and all(transitions.values()),'Xiph active transition/count missing')
                frame_log=record.with_suffix('.stdout.log').read_text(); frame_rows=[line for line in frame_log.splitlines() if line and not line.startswith('#')]
                durations=[int(line.split(',')[3]) for line in frame_rows]; byte_sizes=[int(line.split(',')[4]) for line in frame_rows]
                need(durations==samples and byte_sizes==[n*case['channels']*2 for n in samples],'Xiph per-frame count/drop mismatch')
                need(re.search(r'^#sample_rate 0: '+str(case['rate'])+r'$',frame_log,re.M),'Xiph frame sample rate absent')
                row.update(reference_qualified=True,source='completed Xiph reference; native floor restriction retained',
                    native_refusal_receipt_sha256=sha(native_path),receipt_sha256=sha(record),wav_sha256=sha(output),
                    pcm_sha256=hashlib.sha256(pcm).hexdigest(),pcm_bytes=len(pcm),nonzero_bytes=sum(x!=0 for x in pcm),
                    frames=durations,transition_nonzero_bytes=transitions)
        except Exception as error:
            row['error']=str(error); report['failures'].append(dict(id=name,error=str(error)))
        save(); print(json.dumps({'case':name,'reference_qualified':row['reference_qualified']}),flush=True)
    report.update(completed=True,reference_corpus_qualified=not report['failures'])
    need(sha(tool)==report['ffmpeg_sha256'],'Reference executable changed'); save()
    print(json.dumps({'completed':True,'reference_corpus_qualified':report['reference_corpus_qualified'],'failures':len(report['failures'])}),flush=True)
    return 0 if report['reference_corpus_qualified'] else 1

if __name__=='__main__': raise SystemExit(main())
