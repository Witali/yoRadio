import hashlib,json,subprocess
from pathlib import Path
root=Path('.build/c3-aac-pause-ab-20261014/fixtures');root.mkdir(parents=True,exist_ok=False)
path=root/'aac-lc-44100-128k.aac'
source='aevalsrc=0.25*sin(2*PI*997*t)+0.1*sin(2*PI*113*t)|0.25*sin(2*PI*1201*t)+0.1*sin(2*PI*179*t):s=44100:d=100'
command=['ffmpeg','-nostdin','-v','error','-f','lavfi','-i',source,'-c:a','aac','-b:a','128k','-f','adts',str(path)]
subprocess.run(command,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]))
stream=probe['streams'][0]
assert stream['codec_name']=='aac' and stream['profile']=='LC' and stream['sample_rate']=='44100' and stream['channels']==2
pcm=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(path),'-f','s16le','-c:a','pcm_s16le','-'])
data=path.read_bytes();pos=frames=0
while pos<len(data):
    assert data[pos]==255 and data[pos+1]&0xf6==0xf0
    size=((data[pos+3]&3)<<11)|(data[pos+4]<<3)|(data[pos+5]>>5)
    assert size>=7 and pos+size<=len(data) and data[pos+6]&3==0
    pos+=size;frames+=1
assert len(pcm)==frames*1024*4
seconds=frames*1024/44100
spec=dict(name='aac-lc-44100-128k',file=path.name,sha256=hashlib.sha256(data).hexdigest(),
          seconds=seconds,codec='aac',profile='AAC-LC',mime='audio/aac',label='AAC PCM',rate=44100,channels=2,bits=16)
manifest=dict(fixtures=[spec],generation_command=command,ffprobe=probe,pcm_sha256=hashlib.sha256(pcm).hexdigest(),
              decoded_frames=frames*1024,encoded_bytes=len(data))
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
schedule=[(int(len(data)/seconds*t),delay) for t,delay in ((25,.1),(45,.25),(65,.5))]
(root/'schedule.json').write_text(json.dumps(schedule,indent=2)+'\n')
print(json.dumps(dict(seconds=seconds,bytes=len(data),schedule=schedule)))
