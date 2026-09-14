const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,hash,run}=require('./export.cjs');
const {inspect,linkedGraph}=require('./report_layout.cjs'),{wordAt}=require('./audit_update_link.cjs');
const {helperDisassembly}=require('./small_div_link.cjs'),{archive}=require('./report_bands.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('./selection.cjs');
const control='esp8266-opus-tail-control-v1',candidate='esp8266-opus-small-div-tail-v1';
const dest=path.join(root,'firmware/development',candidate),experiment=path.join(root,'.build/opus-small-div-tail-board');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function preflight(){
 require('./verify.cjs').verify('bands-small-div-tail-asm');
 const manifests=[control,candidate].map(v=>{const d=path.join(root,'firmware/development',v),m=read(path.join(d,'manifest.json')),b=fs.readFileSync(path.join(d,'app.bin'));assert.equal(b.length,m.bytes);assert.equal(hash(b),m.app_sha256.toLowerCase());assert.ok(b.length<=0xf0000);return m;});
 const [ma,mb]=manifests;
 assert.equal(ma.opus_backend,'bands-tell-inline-asm');assert.equal(mb.opus_backend,'bands-small-div-tail-asm');
 const identity=['opus_backend','opus_bands_tell_inline_manifest_sha256','opus_bands_small_div_tail_manifest_sha256','built_utc','source_revision','app_sha256','bytes'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!identity.includes(k))assert.deepEqual(mb[k]??null,ma[k]??null,k);
 for(const m of manifests){assert.equal(m.diagnostic,true);assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_division_benchmark,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);}
 const recipe=read(path.join(component,'asm/lx106/bands-small-div-tail.json'));
 assert.equal(mb.opus_bands_small_div_tail_manifest_sha256.toLowerCase(),hash(fs.readFileSync(path.join(component,'asm/lx106/bands-small-div-tail.json'))));
 const names=['ec_decode','ec_dec_uint','ec_decode_bin','ec_dec_update','ec_dec_bit_logp','quant_partition','quant_all_bands','decode_pulses','celt_cos_norm','clt_mdct_backward_c'];
 const a=inspect(control,names),b=inspect(candidate,names),old=inspect('esp8266-opus-bands-tell-inline-v1',names);
 for(const [s,n]of Object.entries(a.sections).filter(([s])=>!s.startsWith('.flash.')))assert.equal(b.sections[s],n,s);
 let calls=0;
 for(const n of names){
  // New current-source raw control must still have the old best decoder.
  assert.deepEqual(a.functions[n].graph,old.functions[n].graph,n+' control');
  const restored=b.functions[n].graph.map(x=>{if(x==='call0 yoradio_opus_small_udiv'){calls++;return 'call0 0x4000e21c';}return x;});
  assert.deepEqual(restored,a.functions[n].graph,n+' candidate');
  assert.equal(b.functions[n].bytes,a.functions[n].bytes,n+' instruction bytes');
 }assert.equal(calls,3);
 const elf=path.join(root,'.build',candidate,'yoradio_esp8266_helix_native.elf');
 const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
 const symbols=Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-n',elf]).matchAll(/^([0-9a-f]+)\s+\S\s+(\S+)$/gm)].map(m=>[m[2],parseInt(m[1],16)]));
 const start=symbols.yoradio_opus_small_udiv;
 const dump=(begin,end)=>run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d','--start-address=0x'+begin.toString(16),'--stop-address=0x'+end.toString(16),elf]);
 const dis=helperDisassembly(start,start+114,dump);
 const graph=linkedGraph(dis,n=>wordAt(elf,n),n=>n===symbols.yoradio_opus_small_div_table?'yoradio_opus_small_div_table':n===symbols.__udivsi3?'__udivsi3':'0x'+n.toString(16)).graph;
 const previous=read(path.join(root,'firmware/development/esp8266-opus-bands-small-div-v1/preflight.json'));
 assert.deepEqual(graph,previous.helper.graph,'Actual late helper instructions');
 for(const [i,v]of require('./small_div.cjs').table.entries())assert.equal(wordAt(elf,symbols.yoradio_opus_small_div_table+4*i),v);
 assert.ok(start>=b.functions.quant_all_bands.address+b.functions.quant_all_bands.bytes);
 const host=read(path.join(root,'.build/opus-bands-small-div/correctness.json'));assert.equal(host.passed,true);
 assert.equal(host.recipe_sha256_lf,recipe.small_recipe_sha256_lf);
 assert.ok(host.cases.some(c=>c.name==='stereo-510'));assert.ok(host.cases.some(c=>c.name==='stereo-320-20ms'));
 const result={manifests,recipe,static_ram_delta:0,changed_calls:calls,control:a,candidate:b,old_control:old,
  addresses:names.map(n=>({name:n,A:a.functions[n].address,B:b.functions[n].address,delta:b.functions[n].address-a.functions[n].address})),
  helper:{address:start,table_address:symbols.yoradio_opus_small_div_table,graph,disassembly:dis},
  host,scope:'Identical arithmetic, changed flash placement; address preservation is measured, not assumed'};
 fs.writeFileSync(path.join(dest,'preflight.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({passed:true,bytes:mb.bytes,static_ram_delta:0,addresses:result.addresses,helper:start}));return result;
}
function validateRun(r,fixtures,appAddress){
 assert.ok(!r.error,r.error);assert.equal(r.interval_ms,15000);
 assert.equal(r.before.data.app_address,appAddress);assert.equal(r.after.data.app_address,appAddress);
 const s=r.final;assert.equal(s.state,3);assert.equal(s.error,0);assert.equal(s.rounds,10);
 assert.equal(s.physical_output,false);assert.ok(!s.division_microbenchmark);
 assert.equal(s.profile_stage??0,0);assert.ok(!s.functions);
 assert.deepEqual(r.fixtures,fixtures);assert.equal(s.results.length,fixtures.fixtures.length);
 for(const [i,v]of s.results.entries()){
  const f=fixtures.fixtures[i];assert.equal(v.id,i);assert.equal(v.error,0);
  assert.equal(v.pcm_hash,f.expected_hash,f.name+' PCM');
  assert.equal(v.samples,f.samples*s.rounds,f.name+' samples');
  assert.equal(v.packets,f.packet_count*s.rounds,f.name+' packets');
 }
}
function report(){
 const proof=preflight();
 const a=archive(path.join(experiment,'before'),path.join(dest,'controls/before'));
 const b=archive(path.join(experiment,'candidate'),path.join(dest,'runs'));
 const a2=archive(path.join(experiment,'after'),path.join(dest,'controls/after'));
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const [name,rows]of [['before',a],['candidate',b],['after',a2]]){
  const ota=read(path.join(experiment,'ota-'+name+'.json'));assert.equal(ota.pass,true);
  assert.equal(ota.sha256,proof.manifests[name==='candidate'?1:0].app_sha256.toLowerCase());
  for(const r of rows)validateRun(r.report,fixtures,ota.after.app_address);
  fs.copyFileSync(path.join(experiment,'ota-'+name+'.json'),path.join(dest,'ota-'+name+'.json'));
 }
 const initial=compare(a.map(r=>r.report),b.map(r=>r.report)),repeated=compare(a2.map(r=>r.report),b.map(r=>r.report));
 const result={proof,initial,repeated,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},
  inputs:{before:a.map(({report,...r})=>r),candidate:b.map(({report,...r})=>r),after:a2.map(({report,...r})=>r)},
  scope:'30 physical raw A/B/A attempts, all retained; not live qualification'};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(result.selection));return result;
}
module.exports={preflight,validateRun,report};if(require.main===module){if(process.argv.includes('--preflight'))preflight();else report();}
