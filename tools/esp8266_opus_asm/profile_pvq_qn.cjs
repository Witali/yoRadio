// Host frequency/value census for a future exact qn table; no timing claims.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs'),{once}=require('./bands.cjs');
const anchor='   celt_assert(qn <= 256);\n   return qn;';
function instrument(text,observer){
 text=once(text,'static int compute_qn(',observer+'\nstatic int compute_qn(');
 return once(text,anchor,'   y_qn_observe(qb,qn,stereo);\n'+anchor);
}
function qnTable(){
 const exp2=[16384,17866,19483,21247,23170,25267,27554,30048];
 return Array.from({length:61},(_,i)=>{const qb=i+4,v=exp2[qb&7]>>>(14-(qb>>>3));return ((v+1)>>>1)*2;});
}
function validateCounts(c){
 for(const k of ['nonstereo','stereo']){
  const g=c[k];assert.equal(g.qb.length,61);
  for(const n of [g.total,g.low,...g.qb])assert.ok(Number.isSafeInteger(n)&&n>=0);
  assert.equal(g.total,g.low+g.qb.reduce((a,b)=>a+b,0));
 }
 return c.nonstereo.total-c.nonstereo.low;
}
async function profile(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'pvq-exp2-table32'});
 const out=path.join(root,'.build/opus-pvq-qn-profile');fs.mkdirSync(out,{recursive:true});
 const model=require('./pvq_exp2_table32.cjs').cModels().find(m=>m.source==='upstream/celt/bands.c');assert.ok(model);
 const observer=path.join(__dirname,'pvq_qn_probe.inc.c');
 const text=instrument(fs.readFileSync(model.file,'utf8').replace(/\r\n/g,'\n'),fs.readFileSync(observer,'utf8'));
 const source=path.join(out,'bands.model.c'),object=path.join(out,'bands.model.o'),binary=path.join(out,'observer');fs.writeFileSync(source,text);
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(source),'-o',hostPath(object)]);
 const expected=path.join(base.out,'objects',path.basename(model.file)+'.o');assert.equal(base.objects.filter(p=>p===expected).length,1);
 execute('gcc',[...base.linkFlags,...base.objects.map(p=>hostPath(p===expected?object:p)),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const spec=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({name:f.name,file:path.join(fixtures,f.name+'.opuspkt')}));
 spec.push(...require('./high_fixtures.cjs').generate().map(f=>({name:f.name,file:f.file})));
 const result={schema:1,scope:'Host census of original qn: non-stereo (target quant_partition clone) and stereo separately. No changed output, no target modification or measured LX106 speed.',recipe_sha256_lf:sourceHash(__filename),observer_sha256_lf:sourceHash(observer),parent_recipe_sha256_lf:sourceHash(path.join(__dirname,'pvq_exp2_table32.cjs')),generated_model_sha256_lf:sourceHash(source),compiler:base.compiler,flags:base.flags,table_qb4_to64:qnTable(),table_word_bytes:244,cases:[]};
 for(const f of spec){
  const original=path.join(out,f.name+'.base.pcm'),observed=path.join(out,f.name+'.observed.pcm'),stats=path.join(out,f.name+'.counts.json');
  const reference=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(base.binary),hostPath(f.file),hostPath(original)]));
  const probe=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0','YORADIO_QN_COUNTS='+hostPath(stats),hostPath(binary),hostPath(f.file),hostPath(observed)]));
  const pcm=comparePcm(fs.readFileSync(original),fs.readFileSync(observed));assert.equal(pcm.exact,true);
  for(const k of ['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(reference,k));assert.deepEqual(reference[k],probe[k]);}
  const counts=JSON.parse(fs.readFileSync(stats)),eligible=validateCounts(counts),seconds=probe.samples/48000;
  result.cases.push({name:f.name,fixture_sha256:hash(fs.readFileSync(f.file)),reference,probe,pcm,counts,seconds,eligible_per_audio_second:eligible/seconds});
  console.log(f.name,JSON.stringify({eligible,total:counts.nonstereo.total,stereo:counts.stereo.total,seconds,eligible_per_audio_second:eligible/seconds}));
 }
 result.passed=true;fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(result,null,2)+'\n');return result;
}
module.exports={anchor,instrument,validateCounts,qnTable,profile};if(require.main===module)profile().catch(e=>{console.error(e);process.exitCode=1;});
