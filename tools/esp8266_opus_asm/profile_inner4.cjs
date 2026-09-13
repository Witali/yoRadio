// Host-only dynamic length census. No counters or extra memory in firmware.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root,component,sourceHash,hash}=require('./export.cjs'),{once}=require('./bands.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
async function main(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true});
 const dir=path.join(root,'.build/opus-bands-inner4'),source='upstream/celt/vq.c';fs.mkdirSync(dir,{recursive:true});
 let text=fs.readFileSync(path.join(component,source),'utf8').replace(/\r\n/g,'\n');
 const helpers=['#include <stdio.h>','static unsigned y_lengths[2049],y_invalid;',
  '__attribute__((destructor)) static void y_count_report(void) {',
  ' fprintf(stderr,"INNER4_INVALID %u\\n",y_invalid);',
  ' for(int n=0;n<=2048;n++) if(y_lengths[n]) fprintf(stderr,"INNER4_LENGTH %d %u\\n",n,y_lengths[n]);',
  '}',''].join('\n');
 text=once(text,'#ifndef OVERRIDE_renormalise_vector\n','#ifndef OVERRIDE_renormalise_vector\n'+helpers);
 text=once(text,'   E = EPSILON + celt_inner_prod(X, X, N, arch);',
  '   if(N>=0 && N<=2048) y_lengths[N]++; else y_invalid++;\n   E = EPSILON + celt_inner_prod(X, X, N, arch);');
 const file=path.join(dir,'vq.counted.c'),object=path.join(dir,'vq.counted.o'),binary=path.join(dir,'counted');fs.writeFileSync(file,text);
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(file),'-o',hostPath(object)]);
 let replaced=0;const objects=base.objects.map(p=>p.replaceAll('\\','/').endsWith('/upstream/celt/vq.c.o')?(replaced++,object):p);assert.equal(replaced,1);
 execute('gcc',[...base.linkFlags,...objects.map(hostPath),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const selected=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({...f,file:path.join(fixtures,f.name+'.opuspkt')}));
 selected.push(...require('./high_fixtures.cjs').generate());
 const report={scope:'Host fixed-point decode length counts only; not LX106 cycles or production CPU. No profiler in board builds.',recipe_sha256_lf:sourceHash(__filename),source_sha256_lf:sourceHash(path.join(component,source)),cases:[]};
 for(const f of selected){
  const a=path.join(dir,f.name+'.census-base.pcm'),b=path.join(dir,f.name+'.counted.pcm');
  const run=(bin,out)=>{const args=['ASAN_OPTIONS=detect_leaks=0',hostPath(bin),hostPath(f.file),hostPath(out)],r=process.platform==='win32'?spawnSync('wsl.exe',['--exec','env',...args],{encoding:'utf8'}):spawnSync('env',args,{encoding:'utf8'});assert.equal(r.status,0,r.stderr);return r;};
  run(base.binary,a);const r=run(binary,b);assert.match(r.stderr,/^INNER4_INVALID 0$/m);
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
  const lengths=[...r.stderr.matchAll(/^INNER4_LENGTH (\d+) (\d+)$/gm)].map(m=>({N:Number(m[1]),calls:Number(m[2])}));
  const total=lengths.reduce((s,x)=>s+x.calls,0),long=lengths.filter(x=>x.N>=8).reduce((s,x)=>s+x.calls,0);
  const scalarInstructions=lengths.reduce((s,x)=>s+5*x.N*x.calls,0);
  const candidateInstructions=lengths.reduce((s,x)=>s+x.calls*(x.N===0?0:x.N<8?5*x.N+1:5+14*Math.floor(x.N/4)+5*(x.N%4)),0);
  const decoded=JSON.parse(r.stdout);assert.equal(decoded.sample_rate,48000);assert.equal(decoded.output_channels,1);
  assert.equal(decoded.samples,pcm.compared_samples);
  const row={name:f.name,packet_sha256:hash(fs.readFileSync(f.file)),packets:decoded.packets,samples:decoded.samples,audio_duration_ms:decoded.samples/48,calls:total,bulk_calls:long,lengths,scalar_loop_instructions:scalarInstructions,candidate_loop_instructions:candidateInstructions,pcm};report.cases.push(row);
  console.log(JSON.stringify({name:f.name,calls:total,bulk_calls:long,instructions_saved:scalarInstructions-candidateInstructions}));
 }
 report.passed=true;fs.writeFileSync(path.join(dir,'census.json'),JSON.stringify(report,null,2)+'\n');
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
