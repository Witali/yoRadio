// User-scoped quality experiment: only signal-path celt_cos_norm may differ
// by enough to cause <=2 PCM16 error. NEVER approximate bitexact_cos, which
// controls allocation/entropy. Original C and pinned GCC ASM stay unchanged.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {root,component,hash,sourceHash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
async function main(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'tell-inline'});
 const dir=path.join(root,'.build/opus-trig-tables');fs.mkdirSync(dir,{recursive:true});
 const original=path.join(component,'upstream/celt/mathops.c');
 const source=fs.readFileSync(original,'utf8').replace(/\r\n/g,'\n');
 const originalObject=base.objects.find(p=>p.replaceAll('\\','/').endsWith('/upstream/celt/mathops.c.o'));assert.ok(originalObject);
 const probe=path.join(dir,'values.c'),probeObject=path.join(dir,'values.o'),probeBin=path.join(dir,'values');
 fs.writeFileSync(probe,'#include <stdio.h>\n#include "config.h"\n#include "mathops.h"\nint main(void){for(int i=0;i<=32768;i++)printf("%d\\n",(int)celt_cos_norm(i));return 0;}\n');
 const compile=(s,o)=>execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(s),'-o',hostPath(o)]);
 compile(probe,probeObject);
 execute('gcc',[...base.linkFlags,hostPath(probeObject),hostPath(originalObject),'-Wl,--gc-sections','-lm','-o',hostPath(probeBin)]);
 const values=execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(probeBin)]).trim().split(/\r?\n/).map(Number);
 assert.equal(values.length,32769);assert.equal(values[0],32767);assert.equal(values[32768],0);
 const fixturesDir=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const fixtures=JSON.parse(fs.readFileSync(path.join(fixturesDir,'manifest.json'))).fixtures.map(f=>({name:f.name,file:path.join(fixturesDir,f.name+'.opuspkt')}));
 fixtures.push(...require('./high_fixtures.cjs').generate());
 const full=path.join(root,'tests/fixtures/opus_native');
 for(const f of JSON.parse(fs.readFileSync(path.join(full,'manifest.json'))).fixtures)
  fixtures.push({name:'full-'+f.name,file:path.join(full,f.name+'.opuspkt')});
 const run=(bin,input,out)=>{
  const args=['ASAN_OPTIONS=detect_leaks=0',hostPath(bin),hostPath(input),hostPath(out)];
  const r=process.platform==='win32'?spawnSync('wsl.exe',['--exec','env',...args],{encoding:'utf8'}):spawnSync('env',args,{encoding:'utf8'});
  assert.equal(r.status,0,r.stderr);const decoded=JSON.parse(r.stdout);
  const m=r.stderr.match(/^COS_CALLS (\d+)$/m);if(m)decoded.cos_calls=Number(m[1]);
  return decoded;
 };
 const references=new Map();
 for(const f of fixtures){const out=path.join(dir,f.name+'.reference.pcm');run(base.binary,f.file,out);references.set(f.name,fs.readFileSync(out));}
 const report={schema:1,scope:'Host signal-path table screening, not ASM speed or universal error proof',
  recipe_sha256_lf:sourceHash(__filename),source_sha256_lf:sourceHash(original),tolerance_pcm16:2,candidates:[]};
 for(const shift of [8,7,6,5]){
  const step=1<<shift,table=values.filter((v,i)=>i%step===0);let max=0;
  for(let i=0;i<32768;i++){
   const j=i>>shift,f=i&(step-1),v=(table[j]*(step-f)+table[j+1]*f+step/2)>>shift;
   max=Math.max(max,Math.abs(v-values[i]));
  }
  const file=path.join(dir,'mathops-table-'+step+'.c'),object=path.join(dir,'mathops-table-'+step+'.o'),binary=path.join(dir,'table-'+step);
  // Leave the exact function available but rename it. The wrapper counts ALL
  // calls, including calls GCC would otherwise inline within other C units.
  const helper=[
   '#include <stdio.h>','static unsigned y_cos_calls;',
   '__attribute__((destructor)) static void y_cos_report(void){fprintf(stderr,"COS_CALLS %u\\n",y_cos_calls);}',
   'static const opus_uint32 y_cos_table[]={' + table.map(v=>v+'U').join(',')+'};',
   'opus_val16 celt_cos_norm(opus_val32 input){',
   ' opus_uint32 x=(opus_uint32)input&131071U;int sign=1;y_cos_calls++;',
   ' if(x>65536U)x=131072U-x;',
   ' if(x>32768U){x=65536U-x;sign=-1;}',
   ' if(x==32768U)return 0;',
   ' unsigned i=x>>'+shift+',f=x&'+(step-1)+'U;',
   ' opus_uint32 value=(y_cos_table[i]*('+step+'U-f)+y_cos_table[i+1]*f+'+(step/2)+'U)>>'+shift+';',
   ' return sign*(int)value;','}',''
  ].join('\n');
  const signature='opus_val16 celt_cos_norm(opus_val32 x)';assert.equal(source.split(signature).length,2);
  fs.writeFileSync(file,source.replace(signature,'opus_val16 y_original_cos_norm(opus_val32 x)')+'\n'+helper);
  compile(file,object);
  execute('gcc',[...base.linkFlags,...base.objects.map(p=>hostPath(p===originalObject?object:p)),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
  const candidate={step,entries:table.length,flash_word_bytes:table.length*4,coefficient_max_error:max,cases:[]};
  for(const f of fixtures){
   const out=path.join(dir,f.name+'.table-'+step+'.pcm'),decoded=run(binary,f.file,out);
   const pcm=comparePcm(references.get(f.name),fs.readFileSync(out));
   assert.ok(Number.isInteger(decoded.cos_calls));
   const row={name:f.name,packet_sha256:hash(fs.readFileSync(f.file)),samples:decoded.samples,cos_calls:decoded.cos_calls,pcm};
   candidate.cases.push(row);console.log(JSON.stringify({step,name:f.name,max:pcm.max_absolute_error,snr_db:pcm.snr_db}));
  }
  candidate.corpus_within_tolerance=candidate.cases.every(r=>r.pcm.max_absolute_error<=2);report.candidates.push(candidate);
 }
 fs.writeFileSync(path.join(dir,'results.json'),JSON.stringify(report,null,2)+'\n');return report;
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
