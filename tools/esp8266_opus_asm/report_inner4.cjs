// Independent, matched A/B/A against best tell-inline. No discarded attempts.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash,run}=require('./export.cjs');
const {inspect}=require('./report_layout.cjs'),{archive}=require('./report_bands.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('./selection.cjs');
const control='esp8266-opus-bands-tell-inline-v1',candidate='esp8266-opus-bands-inner4-v1';
const dest=path.join(root,'firmware/development',candidate),experiment=path.join(root,'.build/opus-inner4-board');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function preflight(){
 require('./verify.cjs').verify('bands-inner4-asm');
 const manifests=[control,candidate].map(v=>{const d=path.join(root,'firmware/development',v),m=read(path.join(d,'manifest.json')),app=fs.readFileSync(path.join(d,'app.bin'));assert.equal(app.length,m.bytes);assert.equal(hash(app),m.app_sha256.toLowerCase());return m;});
 const [ma,mb]=manifests;
 assert.equal(ma.opus_backend,'bands-tell-inline-asm');assert.equal(mb.opus_backend,'bands-inner4-asm');
 for(const m of manifests){assert.equal(m.diagnostic,true);assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_bands_text_literals??false,false);}
 const identity=['opus_backend','opus_bands_tell_inline_manifest_sha256','opus_bands_inner4_manifest_sha256','built_utc','source_revision','app_sha256','bytes','opus_bands_text_literals'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!identity.includes(k))assert.deepEqual(mb[k]??null,ma[k]??null,'Build profile changed: '+k);
 const rm=read(path.join(component,'asm/lx106/bands-inner4.json'));
 assert.equal(mb.opus_bands_inner4_manifest_sha256.toLowerCase(),hash(fs.readFileSync(path.join(component,'asm/lx106/bands-inner4.json'))));
 assert.equal(rm.parent_sha256_lf,ma.opus_bands_tell_inline_manifest_sha256.toLowerCase());
 const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
 const obj=path.join(root,'.build',candidate,'esp-idf/opus_decoder/CMakeFiles/__idf_opus_decoder.dir/asm/lx106/bands-inner4/upstream/celt/vq.c.obj');
 const all=run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',path.join(root,'.build',control,'yoradio_esp8266_helix_native.elf')]);
 const names=[...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',obj]).matchAll(/^[0-9a-f]+\s+[0-9a-f]+\s+[Tt]\s+(\S+)$/gm)].map(m=>m[1]).filter(n=>new RegExp('\\s'+n.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'$','m').test(all));
 names.push('quant_partition','quant_band','quant_all_bands','ec_tell_frac','ec_dec_bits');assert.ok(names.includes('renormalise_vector'));
 const a=inspect(control,names),b=inspect(candidate,names);
 for(const [s,bytes]of Object.entries(a.sections).filter(([s])=>!s.startsWith('.flash.')))assert.equal(b.sections[s],bytes,'Static RAM changed: '+s);
 for(const name of names.filter(n=>n!=='renormalise_vector'))assert.deepEqual(b.functions[name].graph,a.functions[name].graph,'Unrelated linked graph changed: '+name);
 const graph=b.functions.renormalise_vector.graph,at=graph.findIndex(s=>s.startsWith('blti a14, 16, instruction:'));
 assert.ok(at>=0,'missing linked threshold');
 const expected=['srli a7, a14, 3','slli a7, a7, 3','add a7, a6, a7',
  'l16si a4, a6, 0','l16si a5, a6, 2','mull a4, a4, a4','add a2, a2, a4','mull a5, a5, a5','add a2, a2, a5',
  'l16si a4, a6, 4','l16si a5, a6, 6','mull a4, a4, a4','add a2, a2, a4','mull a5, a5, a5','add a2, a2, a5','addi a6, a6, 8'];
 assert.deepEqual(graph.slice(at+1,at+1+expected.length),expected);
 assert.equal(graph[at+17],'bne a7, a6, instruction:'+(at+4));
 assert.equal(graph[at+18],'beq a3, a6, instruction:'+(at+24));
 assert.equal(graph[at],'blti a14, 16, instruction:'+(at+19));
 assert.equal(graph[at+24],'addi a2, a2, 1','wrong scalar/bulk join');
 for(const image of [a,b])assert.match(image.functions.renormalise_vector.disassembly,/addi\s+a1,\s*a1,\s*-32/,'Missing 32-byte stack frame');
 const result={schema:1,manifests,recipe:rm,reference:a,candidate:b,linked_loop:graph.slice(at,at+25),unchanged_linked_graphs:names.filter(n=>n!=='renormalise_vector'),static_ram_delta:0};
 fs.writeFileSync(path.join(dest,'preflight.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({bytes:mb.bytes,static_ram_delta:0,sections:{A:a.sections,B:b.sections},linked_loop:result.linked_loop}));return result;
}
function report(){
 const build=preflight(),a=archive(path.join(experiment,'before'),path.join(dest,'controls/before')),b=archive(path.join(experiment,'candidate'),path.join(dest,'runs')),a2=archive(path.join(experiment,'after'),path.join(dest,'controls/after'));
 for(const [stage,rows]of [['before',a],['candidate',b],['after',a2]]){
  const ota=read(path.join(experiment,'ota-'+stage+'.json'));assert.equal(ota.pass,true);
  for(const r of rows){assert.equal(r.report.before.data.app_address,ota.after.app_address);assert.equal(r.report.after.data.app_address,ota.after.app_address);}
 }
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const r of [...a,...b,...a2]){assert.equal(r.report.interval_ms,15000);assert.equal(r.report.final.profile_stage??0,0);assert.ok(!r.report.final.functions);for(const [i,v]of r.report.final.results.entries()){assert.equal(v.pcm_hash,fixtures.fixtures[i].expected_hash);assert.equal(v.samples,fixtures.fixtures[i].samples*r.report.final.rounds);assert.equal(v.packets,fixtures.fixtures[i].packet_count*r.report.final.rounds);}}
 const initial=compare(a.map(x=>x.report),b.map(x=>x.report)),repeated=compare(a2.map(x=>x.report),b.map(x=>x.report));
 const host=read(path.join(root,'.build/opus-bands-inner4/correctness.json'));assert.equal(host.passed,true);assert.equal(host.recipe_sha256_lf,build.recipe.recipe_sha256_lf);assert.ok(host.cases.some(c=>c.name==='stereo-510'));assert.ok(host.cases.some(c=>c.name==='stereo-320-20ms'));
 const fixtureHash=sourceHash(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const m of build.manifests)assert.equal(m.opus_benchmark_manifest_sha256.toLowerCase(),fixtureHash);
 const compact=rows=>rows.map(({report,...r})=>r);
 const result={schema:1,build,initial,repeated,host,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},inputs:{before:compact(a),candidate:compact(b),after:compact(a2)},scope:'30 physical A/B/A attempts; raw RAM packets through192, no output/profiler. Host compatibility also320/510. No discarded runs; not live qualification.'};
 for(const f of ['initial-snapshot.json','ota-before.json','ota-candidate.json','ota-after.json'])fs.copyFileSync(path.join(experiment,f),path.join(dest,f));
 for(const f of ['host.log','correctness.json','regression.log'])fs.copyFileSync(path.join(root,'.build/opus-bands-inner4',f),path.join(dest,f));
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(result.selection));return result;
}
module.exports={preflight,report};if(require.main===module){if(process.argv.includes('--preflight'))preflight();else report();}
