const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash}=require('./export.cjs');
const {generateModel}=require('./model.cjs');
const {verify}=require('./verify.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
async function check(fixtures){
 verify('gcc-asm');verify('optimized-asm');
 const out=path.join(root,'.build/opus-asm-check');fs.mkdirSync(out,{recursive:true});
 const generated=generateModel(),binary=path.join(out,'unit');
 const includes=['','upstream/include','upstream/celt','upstream/silk'].map(p=>'-I'+hostPath(path.join(component,p)));
 execute('gcc',['-O2','-fwrapv','-ffunction-sections','-fdata-sections','-fno-pie','-no-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all','-DYORADIO_OPUS_BOUNDED=1','-DOPUS_FAST_INT64=0',...includes,
  hostPath(generated.model),hostPath(generated.reference),hostPath(path.join(root,'tests/native/esp8266_opus_asm_entropy_test.c')),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const unit=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(binary)]));console.log('Instruction-model unit checks',unit);
 const baseline=await buildHost({bounded:true,fastInt64:0,sanitize:true});
 const candidate=await buildHost({bounded:true,fastInt64:0,sanitize:true,asmEntropyModel:true});
 const files=fs.readdirSync(fixtures).filter(f=>f.endsWith('.opuspkt')).sort(),results=[];
 assert.ok(files.length>=5);
 for(const file of files){
  const a=path.join(out,file+'.c.pcm'),b=path.join(out,file+'.asm-model.pcm');
  const args=[hostPath(path.join(fixtures,file))];
  const control=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(baseline.binary),...args,hostPath(a),'--self-test']));
  const model=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(candidate.binary),...args,hostPath(b),'--self-test']));
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true,file);
  for(const key of ['samples','modes','scratch_byte_peak_bytes','scratch_word_peak_bytes','persistent_bytes','reset_exact','oom_reinitialized_exact','arena_guards_ok'])assert.deepEqual(model[key],control[key],file+' '+key);
  for(const key of ['reset_exact','oom_reinitialized_exact','arena_guards_ok'])assert.equal(model[key],true,file+' '+key);
  results.push({file,input_sha256:sourceHashBinary(path.join(fixtures,file)),pcm,decoder:model});console.log(file+': exact PCM');
 }
 const route=['mono-12.opuspkt','stereo-64.opuspkt','mono-24.opuspkt','stereo-192.opuspkt','mono-12.opuspkt'];
 const sequence=(build,name)=>{const pcm=path.join(out,name+'.sequence.pcm');return {state:JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(build.binary),'--sequence',hostPath(pcm),...route.map(f=>hostPath(path.join(fixtures,f)))])),pcm:fs.readFileSync(pcm)};};
 const seqA=sequence(baseline,'c'),seqB=sequence(candidate,'asm');
 const mixed={route,pcm:comparePcm(seqA.pcm,seqB.pcm),decoder:seqB.state};assert.equal(mixed.pcm.exact,true);assert.equal(seqB.state.reset_exact,true);assert.ok(seqB.state.plc_frames>0);
 for(const key of ['samples','sequence_packets','plc_frames','scratch_byte_peak_bytes','scratch_word_peak_bytes','persistent_bytes'])assert.deepEqual(seqB.state[key],seqA.state[key],key);
 const report={passed:true,scope:'ASM instruction semantics model, not target execution or CPU timing',unit,recipe_sha256_lf:sourceHash(path.join(__dirname,'ec_dec_update.inc.s')),results,mixed};
 fs.writeFileSync(path.join(root,'firmware/development/esp8266-opus-asm-library/correctness.json'),JSON.stringify(report,null,2)+'\n');return report;
}
function sourceHashBinary(p){return require('./export.cjs').hash(fs.readFileSync(p));}
module.exports={check};if(require.main===module)check(path.resolve(process.argv[2])).catch(e=>{console.error(e);process.exitCode=1;});
