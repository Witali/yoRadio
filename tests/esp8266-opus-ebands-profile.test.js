const test=require('node:test'),assert=require('node:assert/strict');
const f=require('../tools/esp8266_opus_asm/profile_ebands.cjs');
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {root,sourceHash,hash}=require('../tools/esp8266_opus_asm/export.cjs');
test('eBands observer instruments only real read expressions and preserves index side effects once',()=>{
 const input='/* eBands[3] */\nconst char *s="eBands[4]";\nint x=eBands[--i]+m->eBands[i+1]+eBands[m->nbEBands-1];';
 const {output,sites}=f.instrument(input,'bands','OBSERVER');assert.equal(sites.length,3);
 assert.ok(output.includes('/* eBands[3] */'));assert.ok(output.includes('"eBands[4]"'));
 assert.equal(output.match(/--i/g).length,1);assert.ok(output.includes('y_eband_read(eBands,(--i),0,__func__)'));
 assert.equal(sites[0].line,3);assert.throws(()=>f.instrument(output,'bands',''));
 assert.throws(()=>f.instrument('x->eBands[0]','rate',''));assert.throws(()=>f.instrument('eBands[f()]','rate',''));
 assert.throws(()=>f.instrument('eBands[0','rate',''));assert.throws(()=>f.instrument('','rate',''));
});
test('saved eBands census preserves ten exact PCM and arena results through510kbps',()=>{
 const dir=path.join(root,'docs/benchmarks/esp8266-opus-ebands-profile-2026-09-17'),r=JSON.parse(fs.readFileSync(path.join(dir,'summary.json')));
 assert.equal(r.passed,true);assert.equal(r.cases.length,10);assert.ok(r.flags.includes('-fsanitize=address,undefined'));
 for(const [field,file]of[['recipe_sha256_lf','profile_ebands.cjs'],['observer_sha256_lf','ebands_probe.inc.c'],['parent_recipe_sha256_lf','pvq_exp2_table32.cjs']])assert.equal(r[field],sourceHash(path.join(root,'tools/esp8266_opus_asm',file)));
 for(const unit of f.units){const model=zlib.gunzipSync(fs.readFileSync(path.join(dir,unit+'.counted.c.gz'))).toString('utf8');assert.equal(hash(model.replace(/\r\n/g,'\n')),r.units[unit].generated_sha256_lf);}
 for(const c of r.cases){
  assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);const functions={};
  for(const unit of f.units){assert.deepEqual(c.counts[unit],JSON.parse(fs.readFileSync(path.join(dir,c.name+'.'+unit+'.json'))));assert.equal(f.validateCounts(c.counts[unit],r.units[unit].sites),c.totals[unit]);
   for(const x of c.counts[unit])if(x.total)functions[unit+':'+x.function]=(functions[unit+':'+x.function]||0)+x.total;}
  assert.deepEqual(functions,c.functions);
  for(const key of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok'])assert.deepEqual(c.reference[key],c.probe[key]);
 }
 assert.ok(r.cases.some(x=>x.name==='stereo-510'));assert.deepEqual(r.cases.find(x=>x.name==='mono-12').totals,{bands:0,celt_decoder:0,rate:0});
 const c=r.cases.find(x=>x.name==='stereo-192');assert.equal(c.seconds,0.24);assert.equal(c.functions['rate:clt_compute_allocation'],4344);
 const pair=r.units.rate.sites.filter(s=>s.line===596);assert.equal(pair.length,2);for(const s of pair)assert.equal(c.counts.rate[s.id].total,1008);
});
test('eBands histogram rejects lost reads, invalid dimensions and unknown executed functions',()=>{
 const c=[{id:0,function:'f',total:2,indices:Array(22).fill(0)}];c[0].indices[0]=c[0].indices[21]=1;
 assert.equal(f.validateCounts(c,[{}]),2);
 for(const mutate of[x=>x[0].total++,x=>x[0].indices.pop(),x=>x[0].indices[0]=-1,x=>x[0].function='',x=>x[0].id=1]){
  const bad=structuredClone(c);mutate(bad);assert.throws(()=>f.validateCounts(bad,[{}]));
 }
});
