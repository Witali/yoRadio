"""Independent host validation of complete 36-pair public Vorbis fixtures."""
import argparse,array,hashlib,importlib.util,json,math,struct,subprocess,sys,wave
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
PY=Path(sys.executable).resolve()
CAPTURE=ROOT/'.build/cyd-vorbis-format-command-01.py'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def need(ok,message):
    if not ok: raise RuntimeError(message)

def crc(data):
    result=0
    for value in data:
        result ^= value<<24
        for _ in range(8): result=((result<<1)^0x04c11db7 if result&0x80000000 else result<<1)&0xffffffff
    return result

def packets(data):
    result=[]; pending=bytearray(); pos=0; serial=None; sequence=0
    while pos<len(data):
        need(data[pos:pos+5]==b'OggS\0' and pos+27<=len(data),'Carrier header/version')
        count=data[pos+26]; laces=data[pos+27:pos+27+count]; end=pos+27+count+sum(laces)
        need(len(laces)==count and end<=len(data),'Carrier length')
        page=bytearray(data[pos:end]); expected=struct.unpack_from('<I',page,22)[0]; page[22:26]=bytes(4)
        need(crc(page)==expected,'Carrier CRC')
        stream,number=struct.unpack_from('<II',page,14)
        if serial is None: serial=stream
        need(stream==serial and number==sequence and bool(page[5]&1)==bool(pending),'Carrier sequence/continuation')
        need(bool(page[5]&2)==(sequence==0),'Carrier BOS')
        sequence+=1; offset=pos+27+count; finished=[]
        for size in laces:
            pending.extend(data[offset:offset+size]); offset+=size
            if size<255:
                finished.append(len(result)); result.append(dict(data=bytes(pending),granule=-1,eos=False)); pending.clear()
        if finished:
            result[finished[-1]]['granule']=struct.unpack_from('<q',page,6)[0]
            result[finished[-1]]['eos']=bool(page[5]&4)
        need(not page[5]&4 or end==len(data),'Carrier EOS')
        pos=end
    need(not pending and len(result)>3,'Complete packets required')
    for kind,row in zip((1,3,5),result): need(row['data'][:7]==bytes([kind])+b'vorbis','Vorbis header order')
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix',type=Path,action='append',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'Fresh host campaign required')
    prior=json.loads((ROOT/'.build/cyd-vorbis-format-prep-01/reference/report.json').read_text())
    tool=next(Path(path) for path in prior['tools'] if Path(path).name=='ffmpeg.exe')
    probe=tool.with_name('ffprobe.exe')
    need(sha(tool)==prior['tools'][str(tool)] and sha(probe)==prior['tools'][str(probe)],'Reference tool identity changed')
    need(sha(CAPTURE)=='33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e','Capture utility changed')
    out.mkdir(); (out/'sources').mkdir()
    inspector=ROOT/'.build/cyd-vorbis-block-matrix-design-01/inspect_fixture.py'
    frozen=out/'sources/inspect_fixture.py'; frozen.write_bytes(inspector.read_bytes())
    spec=importlib.util.spec_from_file_location('frozen_public_fixture_inspector',frozen)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    (out/'sources/driver.py').write_bytes(Path(__file__).read_bytes())
    report=dict(schema='public-vorbis-block-host-validation-v1',completed=False,passed=False,
                target_executed=False,production_changed=False,tools={str(x):sha(x) for x in (tool,probe,PY)},
                capture_sha256=sha(CAPTURE),driver_sha256=sha(__file__),inspector_sha256=sha(inspector),
                cross_reference_pcm16_max_error_allowed=2,cases=[],commands=[],failures=[])
    def save(): (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def run(name,argv):
        path=out/(name+'.json'); path.parent.mkdir(parents=True,exist_ok=True)
        command=[str(PY),'-B','-X','utf8',str(CAPTURE),'--record',str(path),'--cwd',str(ROOT),'--timeout','30','--',*map(str,argv)]
        wrapper=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45,
                               creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
        need(path.is_file(),'Missing owned command receipt: '+name)
        receipt=json.loads(path.read_text()); report['commands'].append(dict(name=name,receipt=path.relative_to(out).as_posix(),sha256=sha(path)))
        save(); need(wrapper.returncode==0 and receipt['status']=='TERMINAL' and receipt['returncode']==0,'Reference command failed: '+name)
        return path.with_suffix('.stdout.log').read_bytes()
    sizes=[1<<b for b in range(6,14)]; required={(s,l) for s in sizes for l in sizes if s<=l}
    try:
        for family_index,matrix_path in enumerate(args.matrix):
            matrix_path=matrix_path.resolve(); matrix=json.loads(matrix_path.read_text()); cases=matrix['cases']
            families={}
            for case in cases: families.setdefault(case.get('family','default'),[]).append(case)
            for family,items in families.items():
                need(len(items)==36 and {(x['short'],x['long']) for x in items}==required,'Complete 36-pair family required: '+family)
            destination=out/'sources'/('matrix-'+str(family_index)+'.json'); destination.write_bytes(matrix_path.read_bytes())
            for case in cases:
                family=str(case.get('family','default')); name=f'{family_index}-{family}-{case["id"]}'
                need(all(x.isalnum() or x in '-_' for x in name),'Simple case identifier required')
                record=dict(id=name,source_matrix=str(matrix_path),source_matrix_sha256=sha(matrix_path),input=case,passed=False)
                report['cases'].append(record)
                try:
                    source=(matrix_path.parent/case['ogg']).resolve()
                    need(source.is_relative_to(matrix_path.parent),'Input carrier path escape')
                    case_out=out/'cases'/name; case_out.mkdir(parents=True)
                    carrier=case_out/'input.ogg'; carrier.write_bytes(source.read_bytes()); record['ogg_sha256']=sha(carrier)
                    rows=packets(carrier.read_bytes()); info=rows[0]['data']; rate=struct.unpack_from('<I',info,12)[0]
                    s,l=1<<(info[28]&15),1<<(info[28]>>4); channels=info[11]
                    need((s,l,rate,channels)==(case['short'],case['long'],case['rate'],case['channels']),'Identification differs from matrix')
                    setup=module.inspect_setup(rows[2]['data'][7:],channels)
                    need([x['blockflag'] for x in setup['modes']]==[0,1],'Two explicit short/long modes required')
                    flags=[(row['data'][0]>>1)&1 for row in rows[3:]]
                    need(flags==case['mode_flags'] and flags[0]==0 and 1 in flags,'Packet modes differ')
                    natural=0
                    for i,(flag,row) in enumerate(zip(flags,rows[3:])):
                        need(not row['data'][0]&1,'Audio packet type')
                        if i: natural+=((l if flags[i-1] else s)+(l if flag else s))//4
                        need(row['granule']==natural and row['eos']==(i==len(flags)-1),'Per-packet granule/EOS differs')
                        if flag:
                            if i: need(((row['data'][0]>>2)&1)==flags[i-1],'Previous window flag')
                            if i+1<len(flags): need(((row['data'][0]>>3)&1)==flags[i+1],'Next window flag')
                    need(natural==case['expected_raw_samples'],'Natural overlap accounting differs')
                    record.update(raw_samples_per_channel=natural,packets=len(flags),setup=setup,decoded={})
                    raw=[]
                    for decoder in ('vorbis','libvorbis'):
                        wav_path=case_out/(decoder+'.wav')
                        run('cases/'+name+'/decode-'+decoder,[tool,'-nostdin','-n','-hide_banner','-loglevel','error','-xerror',
                            '-err_detect','explode','-c:a',decoder,'-i',carrier,'-map','0:a:0','-map_metadata','-1',
                            '-fflags','+bitexact','-flags:a','+bitexact','-c:a','pcm_s16le','-f','wav',wav_path])
                        with wave.open(str(wav_path),'rb') as wav:
                            observed=(wav.getframerate(),wav.getnchannels(),wav.getsampwidth(),wav.getnframes())
                            pcm=wav.readframes(wav.getnframes())
                        need(observed==(rate,channels,2,natural),'Reference WAV metadata/count differs: '+str(observed))
                        need(len(pcm)==natural*channels*2 and any(pcm),'Reference PCM missing/silent')
                        record['decoded'][decoder]=dict(wav_sha256=sha(wav_path),pcm_sha256=hashlib.sha256(pcm).hexdigest(),
                            pcm_bytes=len(pcm),nonzero_bytes=sum(x!=0 for x in pcm),rate=rate,channels=channels,bits=16,samples_per_channel=natural)
                        offset=0; transition_nonzero={}; output_packets=[]
                        for i in range(1,len(flags)):
                            size=((l if flags[i-1] else s)+(l if flags[i] else s))*channels//2
                            region=pcm[offset:offset+size]; offset+=size
                            transition=('L' if flags[i-1] else 'S')+('L' if flags[i] else 'S')
                            active=sum(x!=0 for x in region)
                            transition_nonzero[transition]=transition_nonzero.get(transition,0)+active
                            output_packets.append(dict(packet=i,transition=transition,pcm_bytes=size,nonzero_bytes=active))
                        need(offset==len(pcm),'Reference packet-region accounting differs')
                        record['decoded'][decoder].update(transition_nonzero_bytes=transition_nonzero,output_packets=output_packets)
                        need(all(transition_nonzero.values()),'Missing active PCM for a present transition: '+str(transition_nonzero))
                        values=array.array('h'); values.frombytes(pcm)
                        if sys.byteorder!='little': values.byteswap()
                        raw.append(values)
                    differences=[int(a)-int(b) for a,b in zip(*raw)]
                    record['cross_reference_max_abs_error']=max(map(abs,differences),default=0)
                    record['cross_reference_rms_error']=math.sqrt(sum(x*x for x in differences)/len(differences))
                    need(record['cross_reference_max_abs_error']<=2,'Independent reference PCM differs beyond two PCM16 LSB')
                    probe_output=run('cases/'+name+'/probe',[probe,'-v','error','-select_streams','a:0','-show_frames','-show_streams',
                        '-show_entries','stream=codec_name,sample_rate,channels:frame=nb_samples','-of','json',carrier])
                    metadata=json.loads(probe_output); stream=metadata['streams'][0]
                    need((stream['codec_name'],int(stream['sample_rate']),stream['channels'])==('vorbis',rate,channels),'Probe metadata differs')
                    need(sum(int(x['nb_samples']) for x in metadata['frames'])==natural,'Probe decoded sample count differs')
                    record['passed']=True
                except Exception as error:
                    record['error']=str(error); report['failures'].append(dict(id=name,error=str(error)))
                save(); print(json.dumps({'case':name,'passed':record['passed']}),flush=True)
        report.update(completed=True,passed=not report['failures'])
        need(sha(tool)==report['tools'][str(tool)] and sha(probe)==report['tools'][str(probe)],'Reference tools changed')
        save(); print(json.dumps({'host_validation_complete':True,'passed':report['passed'],'cases':len(report['cases']),'failures':len(report['failures'])}),flush=True)
        return 0 if report['passed'] else 1
    except BaseException as error:
        report['terminal_error']=str(error); save(); raise

if __name__=='__main__': raise SystemExit(main())
