// Placement-only exchange: pinned ASM entropy leaves for the task PDM packer.
// No arithmetic changes, no replacement of C fallback, no additional arena.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs');
const {inspect}=require('./report_layout.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const {archive}=require('./report_bands.cjs');
const {validateRun}=require('./report_small_div_tail.cjs');
const {selectHighBitrate}=require('./selection.cjs');
const control='esp8266-opus-entropy-control-v1',candidate='esp8266-opus-entropy-iram-v1';
const art=v=>path.join(root,'firmware/development',v),dir=art(candidate);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const moved=['ec_decode','ec_dec_update','ec_dec_bit_logp'];
const names=[...moved,'ec_decode_bin','ec_dec_uint','ec_dec_icdf','ec_dec_bits',
 'quant_partition','quant_all_bands','decode_pulses','clt_mdct_backward_c',
 'i2s_pdm_pack32','nodac_slc_isr','__moddi3'];
const iram=a=>a>=0x40100000&&a<0x4010c000;
function checkPlacement(a,b){
 for(const n of names)assert.deepEqual(b.functions[n].graph,a.functions[n].graph,n+' linked instruction semantics');
 for(const n of moved){assert.equal(iram(a.functions[n].address),false);assert.equal(iram(b.functions[n].address),true);}
 assert.equal(iram(a.functions.i2s_pdm_pack32.address),true);assert.equal(iram(b.functions.i2s_pdm_pack32.address),false);
 assert.equal(iram(a.functions.nodac_slc_isr.address),true);assert.equal(iram(b.functions.nodac_slc_isr.address),true);
 for(const p of [a,b])assert.ok(p.functions.__moddi3.address>=0x40200000);
 for(const n of ['.dram0.data','.dram0.bss','.iram0.bss','.iram0.vectors'])assert.equal(b.sections[n],a.sections[n],n);
 const delta=b.sections['.iram0.text']-a.sections['.iram0.text'];assert.ok(delta<=0,'IRAM must not grow');
 return delta;
}
function preflight(){
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const manifests=[control,candidate].map(v=>{
  const m=read(path.join(art(v),'manifest.json')),b=fs.readFileSync(path.join(art(v),'app.bin'));
  assert.equal(b.length,m.bytes);assert.equal(hash(b),m.app_sha256.toLowerCase());assert.ok(b.length<=0xf0000);
  assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.diagnostic,true);
  assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);
  assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_division_benchmark,false);
  assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');assert.equal(m.pdm32_iram,true);return m;
 });
 const [ma,mb]=manifests;assert.equal(ma.opus_entropy_iram_swap,false);assert.equal(mb.opus_entropy_iram_swap,true);
 const different=['opus_entropy_iram_swap','opus_entropy_iram_fragment_sha256','built_utc','source_revision','app_sha256','bytes'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!different.includes(k))assert.deepEqual(ma[k],mb[k],k);
 const a=inspect(control,names),b=inspect(candidate,names);
 const delta=checkPlacement(a,b);
 const previous=inspect('esp8266-opus-tail-control-v1',names);
 for(const n of names)assert.deepEqual(a.functions[n].graph,previous.functions[n].graph,n+' current vs previous best control');
 const result={schema:1,manifests,control:a,candidate:b,static_dram_delta:0,static_iram_delta:delta,
  moved,recipe_sha256_lf:sourceHash(__filename),
  scope:'Unchanged pinned ASM and PDM arithmetic; three entropy functions exchange IRAM with task-only PDM packer. Not cache-off safe or live-qualified.'};
 fs.writeFileSync(path.join(dir,'preflight.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({passed:true,iram_delta:delta,bytes:mb.bytes,placement:moved.map(n=>[n,b.functions[n].address,b.functions[n].bytes])}));
 return result;
}
function report(){
 const proof=preflight(),experiment=path.join(root,'.build/opus-entropy-iram-board');
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 const groups={};
 for(const [n,sub]of [['before','controls/before'],['candidate','runs'],['after','controls/after']]){
  const ota=read(path.join(experiment,'ota-'+n+'.json'));assert.equal(ota.pass,true);
  assert.equal(ota.sha256,proof.manifests[n==='candidate'?1:0].app_sha256.toLowerCase());
  const rows=archive(path.join(experiment,n),path.join(dir,sub));
  for(const r of rows)validateRun(r.report,fixtures,ota.after.app_address);
  fs.copyFileSync(path.join(experiment,'ota-'+n+'.json'),path.join(dir,'ota-'+n+'.json'));groups[n]=rows;
 }
 const initial=compare(groups.before.map(r=>r.report),groups.candidate.map(r=>r.report));
 const repeated=compare(groups.after.map(r=>r.report),groups.candidate.map(r=>r.report));
 const result={proof,initial,repeated,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},
  inputs:Object.fromEntries(Object.entries(groups).map(([n,rows])=>[n,rows.map(({report,...r})=>r)])),
  scope:'30 raw physical A/B/A attempts; preserve all maxima/errors. Output disabled, not a live qualification.'};
 fs.writeFileSync(path.join(dir,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(result.selection));return result;
}
module.exports={preflight,checkPlacement,report};
if(require.main===module){if(process.argv.includes('--preflight'))preflight();else report();}
