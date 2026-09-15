// Frequency and word bounds of the unconditional row-length byte probe; no target modification.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs'),{once}=require('./bands.cjs');
const rowAnchor='   cache = m->cache.bits + m->cache.index[(LM+1)*m->nbEBands+i];\n';
function instrument(text,observer) {
 text=once(text,'static int y_endpoint_cost(',observer+'\nstatic int y_endpoint_cost(');
 return once(text,rowAnchor,rowAnchor+'   (void)y_row_probe(m, cache, LM);\n');
}
function validateCounts(c) {
 assert.equal(c.phase.length,4);
 for(const v of[c.rows,c.minus_one,...c.phase])assert.ok(Number.isSafeInteger(v)&&v>=0);
 assert.ok(c.minus_one<=c.rows);assert.equal(c.phase.reduce((a,b)=>a+b,0),c.rows);
 return c.rows;
}
async function profile() {
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'pvq-a4-word'});
 const out=path.join(root,'.build/opus-pvq-row-word-profile');fs.mkdirSync(out,{recursive:true});
 const model=require('./pvq_a4_word.cjs').cModels().find(m=>m.source==='upstream/celt/bands.c');assert.ok(model);
 const observer=path.join(__dirname,'pvq_row_probe.inc.c');
 const text=instrument(fs.readFileSync(model.file,'utf8').replace(/\r\n/g,'\n'),fs.readFileSync(observer,'utf8'));
 const source=path.join(out,'bands.model.c'),object=path.join(out,'bands.model.o'),binary=path.join(out,'observer');fs.writeFileSync(source,text);
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(source),'-o',hostPath(object)]);
 const expected=path.join(base.out,'objects',path.basename(model.file)+'.o');assert.equal(base.objects.filter(p=>p===expected).length,1);
 execute('gcc',[...base.linkFlags,...base.objects.map(p=>hostPath(p===expected?object:p)),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const spec=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({name:f.name,file:path.join(fixtures,f.name+'.opuspkt')}));
 spec.push(...require('./high_fixtures.cjs').generate().map(f=>({name:f.name,file:f.file})));
 const result={schema:1,scope:'Host census of unconditional row-length reads. Returns original byte, verifies aligned-word bounds; no target timing or live qualification.',recipe_sha256_lf:sourceHash(__filename),observer_sha256_lf:sourceHash(observer),parent_recipe_sha256_lf:sourceHash(path.join(__dirname,'pvq_a4_word.cjs')),generated_model_sha256_lf:sourceHash(source),compiler:base.compiler,flags:base.flags,cases:[]};
 for(const f of spec){
  const original=path.join(out,f.name+'.base.pcm'),observed=path.join(out,f.name+'.observed.pcm'),stats=path.join(out,f.name+'.counts.json');
  const reference=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(base.binary),hostPath(f.file),hostPath(original)]));
  const probe=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0','YORADIO_ROW_COUNTS='+hostPath(stats),hostPath(binary),hostPath(f.file),hostPath(observed)]));
  const pcm=comparePcm(fs.readFileSync(original),fs.readFileSync(observed));assert.equal(pcm.exact,true);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(reference,k));assert.deepEqual(reference[k],probe[k]);}
  const counts=JSON.parse(fs.readFileSync(stats)),loads=validateCounts(counts),seconds=probe.samples/48000;
  result.cases.push({name:f.name,fixture_sha256:hash(fs.readFileSync(f.file)),reference,probe,pcm,counts,seconds,loads_per_audio_second:loads/seconds});
  console.log(f.name,JSON.stringify({counts,seconds,loads_per_audio_second:loads/seconds}));
 }
 result.passed=true;fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(result,null,2)+'\n');return result;
}
module.exports={rowAnchor,instrument,validateCounts,profile};if(require.main===module)profile().catch(e=>{console.error(e);process.exitCode=1;});
