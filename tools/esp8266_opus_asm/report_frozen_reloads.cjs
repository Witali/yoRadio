const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs'),f=require('./frozen_reloads.cjs');
const {archive}=require('./report_bands.cjs'),{validateRun}=require('./report_small_div_tail.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('./selection.cjs');
const dest=f.art('candidate'),experiment=path.join(root,'.build/opus-frozen-reloads-board');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function verifyPair(){
 const proof=read(path.join(dest,'preflight.json'));assert.equal(proof.recipe_sha256_lf,sourceHash(path.join(__dirname,'frozen_reloads.cjs')));
 const a=zlib.gunzipSync(fs.readFileSync(path.join(dest,'parent.elf.gz')));assert.equal(hash(a),proof.parent_elf_sha256);
 assert.equal(proof.patches.length,8);assert.equal(f.specs.length,8);
 const patches=f.specs.map(s=>f.findPatch(proof.functions[s.fn],s));
 patches.forEach((p,i)=>{const {before_hex,after_hex,...saved}=proof.patches[i];assert.deepEqual(saved,p);});
 const b=f.patchElf(a,proof.patches);assert.equal(hash(b),proof.candidate_elf_sha256);
 const {sections}=require('./frozen_div.cjs');const object=fs.readFileSync(path.join(dest,'patches.o')),ss=sections(object);
 proof.patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.ok(s);assert.equal(s.bytes,p.bytes);assert.equal(object.subarray(s.offset,s.offset+s.bytes).toString('hex'),p.after_hex);});
 for(const n of f.names){const ar=f.rows(proof.functions[n].disassembly),br=f.rows(proof.actual_functions[n].disassembly);assert.equal(ar.length,br.length);ar.forEach((r,i)=>{const p=proof.patches.find(p=>p.address===r.address);assert.equal(br[i].address,r.address);assert.equal(br[i].bytes,r.bytes);assert.equal(br[i].text,p?f.normalized(p.instruction):r.text);});}
 const manifests={},apps={};for(const t of ['control','candidate']){manifests[t]=read(path.join(f.art(t),'manifest.json'));apps[t]=fs.readFileSync(path.join(f.art(t),'app.bin'));assert.equal(hash(apps[t]),manifests[t].app_sha256);assert.equal(apps[t].length,manifests[t].bytes);assert.equal(manifests[t].post_link_recipe_sha256_lf,proof.recipe_sha256_lf);}
 f.manifestPair(manifests.control,manifests.candidate);assert.deepEqual(f.compareApps(apps.control,apps.candidate,proof.patches),proof.imageProof);
 return {proof,manifests};
}
function report(){
 const pair=verifyPair(),groups={},fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const [name,dir]of [['before','controls/before'],['candidate','runs'],['after','controls/after']]){
  const ota=read(path.join(experiment,'ota-'+name+'.json'));assert.equal(ota.pass,true);assert.equal(ota.sha256,pair.manifests[name==='candidate'?'candidate':'control'].app_sha256);
  const rows=archive(path.join(experiment,name),path.join(dest,dir));assert.equal(rows.length,10);for(const r of rows)validateRun(r.report,fixtures,ota.after.app_address);groups[name]=rows;
  fs.copyFileSync(path.join(experiment,'ota-'+name+'.json'),path.join(dest,'ota-'+name+'.json'));
 }
 const initial=compare(groups.before.map(r=>r.report),groups.candidate.map(r=>r.report)),repeated=compare(groups.after.map(r=>r.report),groups.candidate.map(r=>r.report));
 const result={pair,initial,repeated,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},inputs:Object.fromEntries(Object.entries(groups).map(([k,rs])=>[k,rs.map(({report,...r})=>r)])),scope:'All30 frozen-layout A/B/A raw attempts retained. No function/stage profiling or physical output; not live qualification.'};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));console.log(JSON.stringify(result.selection));return result;
}
module.exports={verifyPair,report,experiment};if(require.main===module)report();
