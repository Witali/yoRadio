import hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tools/audio_test_server')
from generate_aac_growth import generate
root=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
cmd=json.loads((root/'build-command.json').read_text())
with (root/'build-unsandboxed.log').open('xb') as log:
    subprocess.run(['wsl.exe','--exec',*cmd],stdout=log,stderr=subprocess.STDOUT,check=True)
rows={}
for name in ('lc-48000-stereo','he-44100-stereo','hev2-44100-stereo'):
    source=Path('tests/fixtures/aac_stream_format')/(name+'.aac')
    data=source.read_bytes();base,growth,info=generate(data)
    folder=root/name;folder.mkdir();info['source_sha256']=sha(data);info['files']={}
    for label,payload in [('baseline',base),('growth',growth)]:
        path=folder/(label+'.aac');path.write_bytes(payload)
        info['files'][label]={'sha256':sha(payload),'bytes':len(payload)}
    (folder/'manifest.json').write_text(json.dumps(info,indent=2)+'\n');rows[name]=info
(root/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Built pristine FAAD float reference and 3 delayed-growth fixture pairs',flush=True)
references={}
for name,info in rows.items():
    folder=root/name;results={}
    for label in ('baseline','growth'):
        input_path=folder/(label+'.aac');stem=folder/label
        wsl=lambda p:'/mnt/'+p.resolve().drive[0].lower()+p.resolve().as_posix()[2:]
        command=['wsl.exe','--exec',wsl(root/'faad-float'),wsl(input_path),wsl(stem),'1']
        result=subprocess.run(command,capture_output=True,check=True)
        (folder/(label+'-faad.log')).write_bytes(result.stdout+result.stderr)
        faad=json.loads(result.stdout)
        assert faad['frames']==info['frames']
        if name.startswith(('he-','hev2-')): assert faad['sbr_frames']>0
        if name.startswith('hev2-'): assert faad['ps_frames']>0
        ffmpeg=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(input_path),'-map','0:a:0','-f','s16le','-acodec','pcm_s16le','pipe:1'],capture_output=True,check=True)
        (folder/(label+'-ffmpeg.log')).write_bytes(ffmpeg.stderr)
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,profile,sample_rate,channels','-of','json',str(input_path)]))
        assert ffmpeg.stdout
        results[label]=dict(faad=faad,faad_pcm_sha256=sha((folder/(label+'.pcm')).read_bytes()),
            ffmpeg_pcm_sha256=sha(ffmpeg.stdout),ffmpeg_pcm_bytes=len(ffmpeg.stdout),ffprobe=probe)
    for key in ('faad','faad_pcm_sha256','ffmpeg_pcm_sha256','ffmpeg_pcm_bytes','ffprobe'):
        assert results['baseline'][key]==results['growth'][key],(name,key)
    # Check per-frame PCM shape and SBR status as well as whole-stream PCM.
    for suffix in ('frames','state'):
        values=[]
        for label in ('baseline','growth'):
            lines=(folder/(label+'.'+suffix)).read_text().splitlines()
            values.append([line.split()[1:] if suffix=='frames' else line.split() for line in lines])
        assert values[0]==values[1],(name,suffix)
    references[name]=results
    (root/'references.json').write_text(json.dumps(references,indent=2)+'\n')
    print(name,'PASS: FFmpeg and FAAD each produce byte-identical PCM before/after DSE insertion',flush=True)
