// Host-only path counts, NOT LX106 timing. Reuse baseline objects, replacing
// only a private instrumented vq object; never mutate the real codec or cache.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root,component,sourceHash}=require('./export.cjs'),{once}=require('./bands.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
async function main(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true});
 const dir=path.join(root,'.build/opus-shapes'),source=path.join(component,'upstream/celt/vq.c');fs.mkdirSync(dir,{recursive:true});
 let text=fs.readFileSync(source,'utf8').replace(/\r\n/g,'\n');
 const helper=`
#include <stdio.h>
static unsigned long long y_calls, y_values, y_fused_calls, y_fused_values,
 y_rotation_calls, y_rotation_fused_calls, y_block_calls[65], y_block_values[65];
static void y_shape(int N,int K,int spread,int B) {
 y_calls++; y_values+=N;
 int eligible=B>1 && B<=8 && !(B&(B-1)) && N>=B && N%B==0;
 if(eligible) { y_fused_calls++; y_fused_values+=N; }
 if(B>=0 && B<=64) { y_block_calls[B]++; y_block_values[B]+=N; }
 if(2*K<N && spread!=SPREAD_NONE) { y_rotation_calls++; if(eligible)y_rotation_fused_calls++; }
}
__attribute__((destructor)) static void y_report(void) {
 fprintf(stderr,"Y_SHAPES {\\"calls\\":%llu,\\"values\\":%llu,\\"fused_calls\\":%llu,\\"fused_values\\":%llu,\\"rotation_calls\\":%llu,\\"rotation_fused_calls\\":%llu,\\"blocks\\":[",
 y_calls,y_values,y_fused_calls,y_fused_values,y_rotation_calls,y_rotation_fused_calls);
 for(int b=0;b<=64;b++) fprintf(stderr,"%s{\\"B\\":%d,\\"calls\\":%llu,\\"values\\":%llu}",b?",":"",b,y_block_calls[b],y_block_values[b]);
 fprintf(stderr,"]}\\n");
}
`;
 text=once(text,'unsigned alg_unquant(',helper+'\nunsigned alg_unquant(');
 const body=text.match(/^unsigned alg_unquant\([\s\S]*?^}/m)[0];
 text=text.replace(body,once(body,'   SAVE_STACK;','   y_shape(N, K, spread, B);\n   SAVE_STACK;'));
 const model=path.join(dir,'vq.counted.c'),object=path.join(dir,'vq.o'),binary=path.join(dir,'probe');fs.writeFileSync(model,text);
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(model),'-o',hostPath(object)]);
 let replaced=0;const objects=base.objects.map(p=>p.replaceAll('\\','/').endsWith('/upstream/celt/vq.c.o')?(replaced++,object):p);assert.equal(replaced,1);
 execute('gcc',[...base.linkFlags,...objects.map(hostPath),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const report={scope:'Host C fixed-point path distribution; one fixture decode, not self-tests or CPU timing. Same exact PCM as baseline. No firmware changes.',source_sha256_lf:sourceHash(source),recipe_sha256_lf:sourceHash(__filename),cases:[]};
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 for(const f of JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures){
  const a=path.join(dir,f.name+'.base.pcm'),b=path.join(dir,f.name+'.counted.pcm'),input=path.join(fixtures,f.name+'.opuspkt');
  const run=(bin,out)=>{
   const args=['ASAN_OPTIONS=detect_leaks=0',hostPath(bin),hostPath(input),hostPath(out)];
   const r=process.platform==='win32'?spawnSync('wsl.exe',['--exec','env',...args],{encoding:'utf8'}):spawnSync('env',args,{encoding:'utf8'});
   assert.equal(r.status,0,r.stderr);return r;
  };
  const reference=run(base.binary,a),candidate=run(binary,b),counts=JSON.parse(candidate.stderr.match(/^Y_SHAPES (.+)$/m)[1]);
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
  assert.equal(counts.blocks.reduce((s,b)=>s+b.calls,0),counts.calls,'Unexpected block count outside profiled range');
  assert.equal(counts.blocks.reduce((s,b)=>s+b.values,0),counts.values);
  counts.blocks=counts.blocks.filter(b=>b.calls);
  const decoded=JSON.parse(reference.stdout);report.cases.push({name:f.name,fixture_packets:f.packet_count,decoded_samples:decoded.samples,pcm,counts});
  console.log(f.name,JSON.stringify(counts));
 }
 report.passed=true;fs.writeFileSync(path.join(dir,'result.json'),JSON.stringify(report,null,2)+'\n');
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
