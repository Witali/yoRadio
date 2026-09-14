// Matched raw A/B/A: best tell-inline vs shared bit_logp shrink-wrap.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash}=require('./export.cjs');
const {inspect}=require('./report_layout.cjs'),{archive}=require('./report_bands.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('./selection.cjs');
const control='esp8266-opus-bands-tell-inline-v1',candidate='esp8266-opus-bands-logp-v1';
const dest=path.join(root,'firmware/development',candidate),experiment=path.join(root,'.build/opus-logp-board');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function preflight(){
 require('./verify.cjs').verify('bands-logp-asm');
 const manifests=[control,candidate].map(v=>{const d=path.join(root,'firmware/development',v),m=read(path.join(d,'manifest.json')),app=fs.readFileSync(path.join(d,'app.bin'));assert.equal(app.length,m.bytes);assert.equal(hash(app),m.app_sha256.toLowerCase());return m;});
 const [ma,mb]=manifests;
 assert.equal(ma.opus_backend,'bands-tell-inline-asm');assert.equal(mb.opus_backend,'bands-logp-asm');
 for(const m of manifests){assert.equal(m.diagnostic,true);assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_bands_text_literals??false,false);}
 const identity=['opus_backend','opus_bands_tell_inline_manifest_sha256','opus_bands_logp_manifest_sha256','built_utc','source_revision','app_sha256','bytes','opus_bands_text_literals'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!identity.includes(k))assert.deepEqual(mb[k]??null,ma[k]??null,'Build profile changed: '+k);
 const rm=read(path.join(component,'asm/lx106/bands-logp.json'));
 assert.equal(mb.opus_bands_logp_manifest_sha256.toLowerCase(),hash(fs.readFileSync(path.join(component,'asm/lx106/bands-logp.json'))));
 assert.equal(rm.parent_sha256_lf,ma.opus_bands_tell_inline_manifest_sha256.toLowerCase());
 const names=['ec_dec_init','ec_decode','ec_decode_bin','ec_dec_update','ec_dec_bit_logp','ec_dec_icdf','ec_dec_uint','ec_dec_bits','quant_partition','quant_band','quant_all_bands','ec_tell_frac'];
 const a=inspect(control,names),b=inspect(candidate,names);
 for(const [s,bytes]of Object.entries(a.sections).filter(([s])=>!s.startsWith('.flash.')))assert.equal(b.sections[s],bytes,'Static RAM changed: '+s);
 for(const name of names.filter(n=>n!=='ec_dec_bit_logp'))assert.deepEqual(b.functions[name].graph,a.functions[name].graph,'Unrelated linked graph changed: '+name);
 const g=b.functions.ec_dec_bit_logp.graph;
 assert.deepEqual(g.slice(0,6),['l32i a5, a2, 28','l32i a4, a2, 32','ssr a3','srl a3, a5','movi a6, 1','bltu a4, a3, instruction:10']);
 assert.equal(g[12],'bgeu a9, a3, instruction:15');assert.equal(g[13],'mov a2, a6');assert.equal(g[14].trim(),'ret');
 assert.deepEqual(g.slice(15,21),['addi a1, a1, -16','s32i a13, a1, 8','s32i a12, a1, 12','s32i a14, a1, 4','s32i a15, a1, 0','mov a13, a6']);
 // The full unchanged cold CFG is also compared in the source-instruction test.
 assert.equal(g[21],'l32i a8, a2, 20');assert.match(b.functions.ec_dec_bit_logp.disassembly,/addi\s+a1,\s*a1,\s*16/);
 const sizeChanges=[...new Set([...Object.keys(a.function_sizes),...Object.keys(b.function_sizes)])].filter(k=>JSON.stringify(a.function_sizes[k])!==JSON.stringify(b.function_sizes[k])).map(name=>({name,A:a.function_sizes[name],B:b.function_sizes[name]}));
 const result={schema:1,manifests,recipe:rm,reference:a,candidate:b,linked_prefix:g.slice(0,22),unchanged_linked_graphs:names.filter(n=>n!=='ec_dec_bit_logp'),other_linked_size_changes:sizeChanges,static_ram_delta:0};
 fs.writeFileSync(path.join(dest,'preflight.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({bytes:mb.bytes,static_ram_delta:0,sections:{A:a.sections,B:b.sections},sizeChanges}));return result;
}
function report(){
 const build=preflight(),a=archive(path.join(experiment,'before'),path.join(dest,'controls/before')),b=archive(path.join(experiment,'candidate'),path.join(dest,'runs')),a2=archive(path.join(experiment,'after'),path.join(dest,'controls/after'));
 const fixturePath=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'),fixtures=read(fixturePath);
 for(const m of build.manifests)assert.equal(m.opus_benchmark_manifest_sha256.toLowerCase(),sourceHash(fixturePath));
 for(const [stage,rows]of [['before',a],['candidate',b],['after',a2]]){
  const ota=read(path.join(experiment,'ota-'+stage+'.json'));assert.equal(ota.pass,true);
  for(const r of rows){assert.equal(r.report.before.data.app_address,ota.after.app_address);assert.equal(r.report.after.data.app_address,ota.after.app_address);}
 }
 for(const r of [...a,...b,...a2]){assert.equal(r.report.interval_ms,15000);assert.equal(r.report.final.profile_stage??0,0);assert.ok(!r.report.final.functions);for(const [i,v]of r.report.final.results.entries()){assert.equal(v.pcm_hash,fixtures.fixtures[i].expected_hash);assert.equal(v.samples,fixtures.fixtures[i].samples*r.report.final.rounds);assert.equal(v.packets,fixtures.fixtures[i].packet_count*r.report.final.rounds);}}
 const initial=compare(a.map(x=>x.report),b.map(x=>x.report)),repeated=compare(a2.map(x=>x.report),b.map(x=>x.report));
 const host=read(path.join(root,'.build/opus-bands-logp/correctness.json'));assert.equal(host.passed,true);assert.equal(host.recipe_sha256_lf,build.recipe.recipe_sha256_lf);assert.ok(host.cases.some(c=>c.name==='stereo-510'));assert.equal(host.cases.length,11);
 const census=read(path.join(root,'.build/opus-bands-logp/census.json'));assert.equal(census.passed,true);assert.equal(census.recipe_sha256_lf,sourceHash(path.join(__dirname,'profile_logp.cjs')));
 for(const c of census.cases){assert.equal(c.pcm.exact,true);assert.equal(c.audio_duration_ms,c.samples/48);}
 const compact=rows=>rows.map(({report,...r})=>r);
 const result={schema:1,build,initial,repeated,host,census,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},inputs:{before:compact(a),candidate:compact(b),after:compact(a2)},scope:'30 physical A/B/A attempts; raw RAM packets through192, no output/profiler. Host compatibility320/510. No discarded attempts; not live qualification.'};
 for(const f of ['initial-snapshot.json','ota-before.json','ota-candidate.json','ota-after.json'])fs.copyFileSync(path.join(experiment,f),path.join(dest,f));
 for(const f of ['host.log','correctness.json','regression.log','census.json'])fs.copyFileSync(path.join(root,'.build/opus-bands-logp',f),path.join(dest,f));
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(result.selection));return result;
}
module.exports={preflight,report};if(require.main===module){if(process.argv.includes('--preflight'))preflight();else report();}
