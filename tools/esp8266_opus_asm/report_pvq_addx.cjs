// Matched best-parent A/B/A; all runs remain part of the report.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash}=require('./export.cjs');
const {inspect}=require('./report_layout.cjs'),{archive}=require('./report_bands.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('./selection.cjs');
const recipe=require('./pvq_addx.cjs');
const control='esp8266-opus-bands-tell-inline-v1',candidate='esp8266-opus-bands-pvq-addx-v1';
const dest=path.join(root,'firmware/development',candidate),experiment=path.join(root,'.build/opus-pvq-addx-board');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function preflight(){
 require('./verify.cjs').verify('bands-pvq-addx-asm');
 const manifests=[control,candidate].map(v=>{const d=path.join(root,'firmware/development',v),m=read(path.join(d,'manifest.json')),app=fs.readFileSync(path.join(d,'app.bin'));assert.equal(app.length,m.bytes);assert.equal(hash(app),m.app_sha256.toLowerCase());return m;});
 const [ma,mb]=manifests;assert.equal(ma.opus_backend,'bands-tell-inline-asm');assert.equal(mb.opus_backend,'bands-pvq-addx-asm');
 for(const m of manifests){assert.equal(m.diagnostic,true);assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_bands_text_literals??false,false);}
 const identity=['opus_backend','opus_bands_tell_inline_manifest_sha256','opus_bands_pvq_addx_manifest_sha256','built_utc','source_revision','app_sha256','bytes','opus_bands_text_literals'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!identity.includes(k))assert.deepEqual(mb[k]??null,ma[k]??null,'Build profile changed: '+k);
 const rm=read(path.join(component,'asm/lx106/bands-pvq-addx.json'));
 assert.equal(mb.opus_bands_pvq_addx_manifest_sha256.toLowerCase(),hash(fs.readFileSync(path.join(component,'asm/lx106/bands-pvq-addx.json'))));
 assert.equal(rm.parent_sha256_lf,ma.opus_bands_tell_inline_manifest_sha256.toLowerCase());
 const names=['decode_pulses','quant_partition','quant_band','quant_all_bands','ec_tell_frac','ec_dec_bits','alg_unquant','clt_mdct_backward_c'];
 const a=inspect(control,names),b=inspect(candidate,names);
 for(const [s,bytes]of Object.entries(a.sections).filter(([s])=>!s.startsWith('.flash.')))assert.equal(b.sections[s],bytes,'Static RAM changed: '+s);
 for(const n of names.filter(n=>n!=='decode_pulses'))assert.deepEqual(b.functions[n].graph,a.functions[n].graph,'Unrelated linked graph changed: '+n);
 const f=recipe.fuseGraph(a.functions.decode_pulses.graph);assert.equal(f.count,20);
 assert.deepEqual(recipe.normalizeBranches(b.functions.decode_pulses.graph).graph,recipe.normalizeBranches(f.graph).graph);
 assert.equal(b.functions.decode_pulses.graph.filter(s=>s.startsWith('addx4 ')).length,20);
 for(const image of [a,b])assert.match(image.functions.decode_pulses.disassembly,/addi\s+a1,\s*a1,\s*-48/);
 const result={schema:1,manifests,recipe:rm,reference:a,candidate:b,fused_pairs:20,unchanged_linked_graphs:names.filter(n=>n!=='decode_pulses'),static_ram_delta:0};
 fs.writeFileSync(path.join(dest,'preflight.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({bytes:mb.bytes,static_ram_delta:0,sections:{A:a.sections,B:b.sections},decode_pulses_bytes:[a.functions.decode_pulses.bytes,b.functions.decode_pulses.bytes],physical_instructions:[a.functions.decode_pulses.physical_instruction_count,b.functions.decode_pulses.physical_instruction_count]}));return result;
}
function report(){
 const build=preflight(),a=archive(path.join(experiment,'before'),path.join(dest,'controls/before')),b=archive(path.join(experiment,'candidate'),path.join(dest,'runs')),a2=archive(path.join(experiment,'after'),path.join(dest,'controls/after'));
 for(const [stage,rows]of [['before',a],['candidate',b],['after',a2]]){
  const ota=read(path.join(experiment,'ota-'+stage+'.json'));assert.equal(ota.pass,true);
  assert.equal(ota.sha256,build.manifests[stage==='candidate'?1:0].app_sha256.toLowerCase());
  for(const r of rows){assert.equal(r.report.before.data.app_address,ota.after.app_address);assert.equal(r.report.after.data.app_address,ota.after.app_address);}
 }
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const r of [...a,...b,...a2]){assert.equal(r.report.interval_ms,15000);assert.equal(r.report.final.profile_stage??0,0);assert.ok(!r.report.final.functions);for(const [i,v]of r.report.final.results.entries()){assert.equal(v.pcm_hash,fixtures.fixtures[i].expected_hash);assert.equal(v.samples,fixtures.fixtures[i].samples*r.report.final.rounds);assert.equal(v.packets,fixtures.fixtures[i].packet_count*r.report.final.rounds);}}
 const initial=compare(a.map(x=>x.report),b.map(x=>x.report)),repeated=compare(a2.map(x=>x.report),b.map(x=>x.report));
 const host=read(path.join(root,'.build/opus-bands-tell-inline/correctness.json'));assert.equal(host.passed,true);assert.ok(host.cases.some(c=>c.name==='stereo-510'));assert.ok(host.cases.some(c=>c.name==='stereo-320-20ms'));
 const fixtureHash=sourceHash(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));for(const m of build.manifests)assert.equal(m.opus_benchmark_manifest_sha256.toLowerCase(),fixtureHash);
 const compact=rows=>rows.map(({report,...r})=>r);
 const result={schema:1,build,initial,repeated,parent_host_pcm:host,host_scope:'Unchanged parent algorithm; new ADDX4 covered by local register equivalence and object/linked graph proofs, not host execution of LX106.',selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},inputs:{before:compact(a),candidate:compact(b),after:compact(a2)},scope:'30 physical A/B/A attempts; raw RAM packets through192, no output/profiler. No discarded runs; not live qualification.'};
 for(const f of ['initial-snapshot.json','ota-before.json','ota-candidate.json','ota-after.json'])fs.copyFileSync(path.join(experiment,f),path.join(dest,f));
 for(const f of ['build.log','host.log','regression.log'])fs.copyFileSync(path.join(root,'.build/opus-bands-pvq-addx',f),path.join(dest,f));
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(result.selection));return result;
}
module.exports={preflight,report};if(require.main===module){if(process.argv.includes('--preflight'))preflight();else report();}
