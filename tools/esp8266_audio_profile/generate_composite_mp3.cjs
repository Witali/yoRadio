#!/usr/bin/env node
// Deterministic, self-authored benchmark audio. Never uses a downloaded song.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
function makeWave(seed=0x594f5241) {
  const rate=44100, frames=rate, values=new Float64Array(frames*2);
  let state=seed>>>0, lowL=0, lowR=0, maximum=0;
  function noise() {
    state^=state<<13; state^=state>>>17; state^=state<<5;
    return (state>>>0)/2147483648-1;
  }
  for(let i=0;i<frames;i++) {
    const t=i/rate, a=noise(), b=noise();
    lowL+=0.12*(a-lowL); lowR+=0.12*(b-lowR);
    const tone=0.18*Math.sin(2*Math.PI*440*t)+0.13*Math.sin(2*Math.PI*997*t);
    const sweep=0.07*Math.sin(2*Math.PI*(200*t+2900*t*t));
    const envelope=0.7+0.3*Math.sin(2*Math.PI*2*t)**2;
    const edge=Math.min(1,i/132,(frames-1-i)/132);
    const burst=(i%11025)<1800?0.08:0;
    values[2*i]=edge*(envelope*(tone+sweep)+0.08*a+0.1*lowL+burst*b);
    values[2*i+1]=edge*(envelope*(0.9*tone-sweep)+0.05*a+0.07*b+0.1*lowR+burst*a);
    maximum=Math.max(maximum,Math.abs(values[2*i]),Math.abs(values[2*i+1]));
  }
  const wave=Buffer.alloc(44+frames*4), gain=23170/maximum;
  wave.write('RIFF',0); wave.writeUInt32LE(wave.length-8,4); wave.write('WAVEfmt ',8);
  wave.writeUInt32LE(16,16); wave.writeUInt16LE(1,20); wave.writeUInt16LE(2,22);
  wave.writeUInt32LE(rate,24); wave.writeUInt32LE(rate*4,28);
  wave.writeUInt16LE(4,32); wave.writeUInt16LE(16,34);
  wave.write('data',36); wave.writeUInt32LE(frames*4,40);
  for(let i=0;i<values.length;i++) wave.writeInt16LE(Math.round(values[i]*gain),44+i*2);
  return wave;
}
function main() {
  const args=process.argv.slice(2);
  function option(key,fallback){const i=args.indexOf(key);return i<0?fallback:args[i+1];}
  const out=path.resolve(option('--output','tests/fixtures/mp3_composite'));
  const ffmpeg=option('--ffmpeg','ffmpeg');
  fs.mkdirSync(out,{recursive:true});
  const wav=path.join(out,'tone-noise.wav');
  fs.writeFileSync(wav,makeWave());
  const version=spawnSync(ffmpeg,['-version'],{encoding:'utf8'});
  if(version.status!==0) throw new Error('FFmpeg unavailable: '+version.stderr);
  const manifest={generator:'generate_composite_mp3.cjs',seed:'0x594f5241',
    source_rate:44100,source_channels:2,source_bits:16,source_seconds:1,
    peak_dbfs:-3.01,components:['440 Hz','997 Hz','200..6000 Hz chirp',
      'seeded white noise','low-pass noise','short noise bursts'],
    encoder:version.stdout.split(/\r?\n/)[0],files:{}};
  const names=['tone-noise.wav'];
  for(const bitrate of [64,128,320]) {
    const name='mix-'+String(bitrate).padStart(3,'0')+'.mp3';
    const encoded=spawnSync(ffmpeg,['-hide_banner','-loglevel','error','-y',
      '-i',wav,'-map_metadata','-1','-c:a','libmp3lame','-b:a',bitrate+'k',
      '-ar','44100','-ac','2','-joint_stereo','1','-reservoir','1',
      '-write_xing','0','-id3v2_version','0',path.join(out,name)],{encoding:'utf8'});
    if(encoded.status!==0) throw new Error(encoded.stderr);
    names.push(name);
  }
  for(const name of names) {
    const bytes=fs.readFileSync(path.join(out,name));
    manifest.files[name]={bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')};
  }
  fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
  console.log(JSON.stringify(manifest,null,2));
}
module.exports={makeWave};
if(require.main===module) main();
