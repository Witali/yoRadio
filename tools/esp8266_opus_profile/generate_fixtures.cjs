const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..');
const out=path.join(root,'tests/fixtures/opus_native');
fs.mkdirSync(out,{recursive:true});
// Own deterministic tone + white-noise signal; no recorded/copyright music.
const cases=[['stereo-128',128,2,20,'audio'],['stereo-510',510,2,20,'audio'],['mono-24',24,1,20,'voip'],['mono-12',12,1,20,'voip'],['stereo-64',64,2,20,'audio']];
for(const [name,kbps,channels,duration,application] of cases){
 const file=path.join(out,name+'.opus');
 const source='aevalsrc=0.24*sin(2*PI*997*t)+0.04*sin(2*PI*10007*t)|0.19*sin(2*PI*1703*t):s=48000:d=1.2';
 const args=['-hide_banner','-loglevel','error','-y','-f','lavfi','-i',source,'-f','lavfi','-i','anoisesrc=color=white:amplitude=0.025:seed=7349:r=48000:d=1.2','-filter_complex','[0:a][1:a]amix=inputs=2:normalize=0','-ac',String(channels),'-c:a','libopus','-application',application,'-b:a',kbps+'k','-vbr','off','-frame_duration',String(duration),file];
 const result=spawnSync('ffmpeg',args,{encoding:'utf8'});if(result.status!==0)throw Error(result.stderr);
 const data=fs.readFileSync(file);let pos=0,packet=[],all=[];
 while(pos<data.length){
   if(data.toString('ascii',pos,pos+4)!=='OggS')throw Error('Invalid Ogg fixture');
   const segs=data[pos+26],lace=data.subarray(pos+27,pos+27+segs);pos+=27+segs;
   for(const size of lace){packet.push(data.subarray(pos,pos+size));pos+=size;
     if(size<255){const joined=Buffer.concat(packet);packet=[];
       if(!['OpusHead','OpusTags'].includes(joined.toString('ascii',0,8))){const l=Buffer.alloc(2);l.writeUInt16LE(joined.length);all.push(l,joined);}
     }
   }
 }
 fs.writeFileSync(path.join(out,name+'.opuspkt'),Buffer.concat(all));
 console.log(name,data.length);
}
