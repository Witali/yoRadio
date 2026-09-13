// Host-only census of the exact no-entropy theta branch, never a speed estimate.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root,component,sourceHash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
async function main(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true});
 const model=require('./tell_zero.cjs').cModels(true)[0],dir=path.dirname(model.file),object=path.join(dir,'counted.o'),binary=path.join(dir,'counted');
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(model.file),'-o',hostPath(object)]);
 let replaced=0;const objects=base.objects.map(p=>p.replaceAll('\\','/').endsWith('/upstream/celt/bands.c.o')?(replaced++,object):p);assert.equal(replaced,1);
 execute('gcc',[...base.linkFlags,...objects.map(hostPath),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const selected=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({...f,file:path.join(fixtures,f.name+'.opuspkt')}));
 const {inspectPackets}=require('../esp8266_opus_profile/fixtures.cjs');
 const {oggPackets,framed}=require('../esp8266_opus_profile/generate_phase_fixtures.cjs');
 // Compatibility is not limited by the 192-kbit/s physical speed target.
 const commands=[];
 for(const duration of [2.5,5,10,20]){
  const name='stereo-320-'+duration+'ms',file=path.join(dir,name+'.opuspkt');
  const args=['-hide_banner','-loglevel','error','-f','lavfi','-i','aevalsrc=0.24*sin(2*PI*997*t)|0.19*sin(2*PI*1703*t):s=48000:d=0.24',
   '-f','lavfi','-i','anoisesrc=color=white:amplitude=0.025:seed=7349:r=48000:d=0.24','-filter_complex','[0:a][1:a]amix=inputs=2:normalize=0',
   '-ac','2','-c:a','libopus','-application','lowdelay','-b:a','320k','-vbr','off','-frame_duration',String(duration),'-f','ogg','pipe:1'];
  const encoded=spawnSync('ffmpeg',args,{maxBuffer:4*1024*1024});assert.equal(encoded.status,0,encoded.stderr?.toString());
  const raw=framed(oggPackets(encoded.stdout));fs.writeFileSync(file,raw);commands.push(args);
  selected.push({name,file,packet_count:inspectPackets(raw).packets});
 }
 const highFile=path.join(root,'tests/fixtures/opus_native/stereo-510.opuspkt');
 selected.push({name:'stereo-510',file:highFile,packet_count:inspectPackets(fs.readFileSync(highFile)).packets});
 const report={scope:'One host fixed-point decode per fixture; counts only, not LX106 timing. Includes 320/510 kbit/s; no decoder bitrate limit.',
  recipe_sha256_lf:sourceHash(path.join(__dirname,'tell_zero.cjs')),commands_320:commands,cases:[]};
 for(const f of selected){
  const a=path.join(dir,f.name+'.base.pcm'),b=path.join(dir,f.name+'.counted.pcm');
  const run=(bin,out)=>{const args=['ASAN_OPTIONS=detect_leaks=0',hostPath(bin),hostPath(f.file),hostPath(out)],r=process.platform==='win32'?spawnSync('wsl.exe',['--exec','env',...args],{encoding:'utf8'}):spawnSync('env',args,{encoding:'utf8'});assert.equal(r.status,0,r.stderr);return r;};
  run(base.binary,a);const r=run(binary,b),m=r.stderr.match(/^TELL_ZERO (\d+) (\d+)$/m);assert.ok(m,r.stderr);
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
  const row={name:f.name,packets:f.packet_count,packet_sha256:require('node:crypto').createHash('sha256').update(fs.readFileSync(f.file)).digest('hex'),theta_calls:Number(m[1]),eligible_calls:Number(m[2]),pcm};assert.ok(row.eligible_calls<=row.theta_calls);report.cases.push(row);console.log(JSON.stringify(row));
 }
 report.passed=true;fs.writeFileSync(path.join(dir,'census.json'),JSON.stringify(report,null,2)+'\n');
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
