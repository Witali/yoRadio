const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {root,hash,sourceHash}=require('./export.cjs'),frozen=require('./frozen_div.cjs');
const {archive}=require('./report_bands.cjs'),{compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const {validateRun}=require('./report_small_div_tail.cjs'),{selectHighBitrate}=require('./selection.cjs');
const dest=frozen.art('asm'),experiment=path.join(root,'.build/opus-frozen-div-board');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
function pairedManifests(rom,asm){
 assert.equal(rom.post_link_division_target,'rom');assert.equal(asm.post_link_division_target,'asm');
 for(const k of new Set([...Object.keys(rom),...Object.keys(asm)]))
  if(!['purpose','app_sha256','post_link_division_target'].includes(k))assert.deepEqual(rom[k],asm[k],k);
 for(const m of [rom,asm]){
  assert.equal(m.diagnostic,true);assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);
  assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_division_benchmark,false);
  assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');
 }
}
function verifyPair(){
 const proof=read(path.join(dest,'preflight.json'));
 assert.equal(proof.recipe_sha256_lf,sourceHash(path.join(__dirname,'frozen_div.cjs')));
 const manifests={},apps={};
 for(const t of ['rom','asm']){
  manifests[t]=read(path.join(frozen.art(t),'manifest.json'));apps[t]=fs.readFileSync(path.join(frozen.art(t),'app.bin'));
  assert.equal(manifests[t].app_sha256,hash(apps[t]));assert.equal(manifests[t].bytes,apps[t].length);
  assert.equal(manifests[t].post_link_recipe_sha256_lf,proof.recipe_sha256_lf);
 }
 pairedManifests(manifests.rom,manifests.asm);
 const elf=zlib.gunzipSync(fs.readFileSync(path.join(dest,'linked.elf.gz')));
 assert.equal(hash(elf),proof.parent_elf_sha256);
 const {output}=frozen.patchLiteral(elf,proof.literal,proof.helper,proof.rom);
 assert.equal(hash(output),proof.rom_elf_sha256);
 assert.deepEqual(frozen.compareImages(apps.asm,apps.rom,proof.literal,proof.helper,proof.rom),proof.imageProof);
 return {proof,manifests};
}
function report(){
 const pair=verifyPair(),groups={};
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const [name,dir]of [['before','controls/before'],['candidate','runs'],['after','controls/after']]){
  const rows=archive(path.join(experiment,name),path.join(dest,dir));
  const ota=read(path.join(experiment,'ota-'+name+'.json'));assert.equal(ota.pass,true);
  assert.equal(ota.sha256,pair.manifests[name==='candidate'?'asm':'rom'].app_sha256);
  for(const r of rows)validateRun(r.report,fixtures,ota.after.app_address);
  const to=path.join(dest,'ota-'+name+'.json'),bytes=fs.readFileSync(path.join(experiment,'ota-'+name+'.json'));
  if(fs.existsSync(to))assert.deepEqual(fs.readFileSync(to),bytes);else fs.writeFileSync(to,bytes);
  groups[name]=rows;
 }
 const initial=compare(groups.before.map(r=>r.report),groups.candidate.map(r=>r.report));
 const repeated=compare(groups.after.map(r=>r.report),groups.candidate.map(r=>r.report));
 const previousFile=path.join(root,'firmware/development/esp8266-opus-small-div-tail-v1/comparison.json'),previous=read(previousFile);
 const anchor={file:path.relative(root,previousFile).replaceAll('\\','/'),sha256:hash(fs.readFileSync(previousFile)),
  before_192:previous.initial.cases[4].reference.task_budget_percent.median,
  after_192:previous.repeated.cases[4].reference.task_budget_percent.median,
  scope:'Historical same-profile best tell-inline reference; not an extra physical run in this frozen pair'};
 const censusFile=path.join(root,'firmware/development/esp8266-opus-division-micro-v2/census/census.json');
 const census=read(censusFile);assert.equal(census.passed,true);
 assert.equal(census.manifest_sha256,hash(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'))));
 const attribution={source:path.relative(root,censusFile).replaceAll('\\','/'),sha256:hash(fs.readFileSync(censusFile)),
  scope:'Total raw-decoder time difference divided by host operand count, including downstream cache effects. NOT an exclusive helper timer or measured cache-miss count.',
  cases:initial.cases.map((c,i)=>{
   const h=census.cases[i];assert.equal(h.name,c.name);
   const rounds=groups.candidate[0].report.final.rounds,calls=h.calls*rounds;
   assert.equal(h.samples*rounds,c.candidate.samples_per_run);
   const extra=(c.candidate.task_budget_percent.median-c.reference.task_budget_percent.median)*c.candidate.samples_per_run/4.8;
   return {name:c.name,host_calls_per_round:h.calls,rounds,calls_per_run:calls,extra_total_us:extra,extra_us_per_host_call:calls?extra/calls:null,
    powers:h.powers,power_percent:h.calls?100*h.powers/h.calls:null,fallback:h.fallback};
  })};
 const result={schema:1,scope:'Thirty frozen-layout raw A/B/A attempts. Paired ROM vs ASM identifies callee effect at these addresses, not cache misses or production qualification.',
  pair,initial,repeated,relative_pair_selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},
  historical_best:anchor,attribution,
  candidate_beats_both_historical_192:initial.cases[4].candidate.task_budget_percent.median<Math.min(anchor.before_192,anchor.after_192),
  inputs:Object.fromEntries(Object.entries(groups).map(([k,rows])=>[k,rows.map(({report,...r})=>r)]))};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,ROM:c.reference.task_budget_percent.median,ASM:c.candidate.task_budget_percent.median,ROM2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify({relative:result.relative_pair_selection,beats_best:result.candidate_beats_both_historical_192}));return result;
}
module.exports={pairedManifests,verifyPair,report};if(require.main===module)report();
