// Compatibility fixtures beyond the 192-kbit/s speed target, not a rate cap.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process'),{root}=require('./export.cjs');
const {framed,oggPackets}=require('../esp8266_opus_profile/generate_phase_fixtures.cjs');
function generate(){
 const dir=path.join(root,'.build/opus-high-compatibility');fs.mkdirSync(dir,{recursive:true});
 const fixtures=[];
 for(const duration of [2.5,5,10,20]){
  const name='stereo-320-'+duration+'ms',file=path.join(dir,name+'.opuspkt');
  const args=['-hide_banner','-loglevel','error','-f','lavfi','-i','aevalsrc=0.24*sin(2*PI*997*t)|0.19*sin(2*PI*1703*t):s=48000:d=0.24',
   '-f','lavfi','-i','anoisesrc=color=white:amplitude=0.025:seed=7349:r=48000:d=0.24','-filter_complex','[0:a][1:a]amix=inputs=2:normalize=0',
   '-ac','2','-c:a','libopus','-application','lowdelay','-b:a','320k','-vbr','off','-frame_duration',String(duration),'-f','ogg','pipe:1'];
  const r=spawnSync('ffmpeg',args,{maxBuffer:4*1024*1024});assert.equal(r.status,0,r.stderr?.toString());
  fs.writeFileSync(file,framed(oggPackets(r.stdout)));fixtures.push({name,file,command:args});
 }
 fixtures.push({name:'stereo-510',file:path.join(root,'tests/fixtures/opus_native/stereo-510.opuspkt')});
 return fixtures;
}
module.exports={generate};
