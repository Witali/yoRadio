const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,sourceHash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
async function check(kind){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true});
 const candidate=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:kind});
 const out=path.join(root,'.build/opus-bands-'+kind),fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const report={scope:'Host semantic mirror, exact PCM/guards; not LX106 execution or timing',kind,recipe_sha256_lf:sourceHash(path.join(__dirname,kind==='intensity'?'bands.cjs':kind.replaceAll('-','_')+'.cjs')),cases:[]};
 const probe=(bin,args)=>JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(bin),...args]));
 const compare=(name,args)=>{
  const a=path.join(out,name+'.base.pcm'),b=path.join(out,name+'.candidate.pcm');
  const reference=probe(base.binary,args(a)),result=probe(candidate.binary,args(b));
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true,name);
  for(const k of ['samples','scratch_byte_peak_bytes','scratch_word_peak_bytes','persistent_bytes','reset_exact','oom_reinitialized_exact','arena_guards_ok','plc_frames'])
   assert.deepEqual(result[k],reference[k],name+' '+k);
  assert.equal(result.reset_exact,true);
  if(name==='mixed') assert.ok(result.plc_frames>0);
  else {assert.equal(result.arena_guards_ok,true);assert.equal(result.oom_reinitialized_exact,true);}
  report.cases.push({name,pcm,reference,candidate:result});console.log(name,'exact PCM');
 };
 for(const f of JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures)
  compare(f.name,pcm=>[hostPath(path.join(fixtures,f.name+'.opuspkt')),hostPath(pcm),'--self-test']);
 compare('mixed',pcm=>['--sequence',hostPath(pcm),...['mono-12','mono-24','stereo-64','stereo-192','mono-12'].map(n=>hostPath(path.join(fixtures,n+'.opuspkt')))]);
 report.passed=true;fs.writeFileSync(path.join(out,'correctness.json'),JSON.stringify(report,null,2)+'\n');
}
if(require.main===module)check(process.argv[2]).catch(e=>{console.error(e);process.exitCode=1;});
