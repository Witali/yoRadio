#!/usr/bin/env node
// Continuous encoding of our own seeded tone/noise signal, no packet looping.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const {pages}=require('./local_radio.cjs');
const root=path.resolve(__dirname,'../..');
const out=path.join(root,'tests/fixtures/opus_local_radio');
if(fs.existsSync(out))throw Error('Refusing to overwrite fixture directory');
fs.mkdirSync(out,{recursive:true});
const wav=path.join(root,'tests/fixtures/mp3_composite/tone-noise.wav');
const run=args=>{const r=spawnSync('ffmpeg',args,{encoding:'utf8',timeout:180000});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const manifest={source:'../mp3_composite/tone-noise.wav: own seeded tones, chirp and noise, repeated before encoding',
 source_sha256:hash(fs.readFileSync(wav)),encoder:run(['-version']).split(/\r?\n/)[0],duration_seconds:300,files:[]};
for(const [rate,frame] of [[24,60],[12,20]]) {
 const name=`mono-${rate}-${frame}ms.opus`;
 const args=['-hide_banner','-loglevel','error','-fflags','+bitexact','-stream_loop','-1','-i',wav,
  '-t','300','-map_metadata','-1','-ac','1','-ar','48000','-c:a','libopus','-application','voip',
  '-b:a',rate+'k','-vbr','off','-frame_duration',String(frame),'-flags:a','+bitexact',
  '-page_duration',String(frame*1000),path.join(out,name)];
 run(args);const data=fs.readFileSync(path.join(out,name)),p=pages(data);
 manifest.files.push({name,bitrate_kbps:rate,frame_ms:frame,bytes:data.length,sha256:hash(data),pages:p.length,duration_ms:p.at(-1).endMs,
  args:args.map(v=>v===wav?manifest.source.split(':')[0]:v===path.join(out,name)?name:v)});
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify(manifest,null,2));
