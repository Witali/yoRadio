// Keep every physical attempt; verify firmware identity before comparing CPU.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs'),f=require('./fft_load3.cjs'),base=require('./frozen_reloads.cjs');
const {sections}=require('./frozen_div.cjs'),{archive}=require('./report_bands.cjs'),{validateRun}=require('./report_small_div_tail.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('./selection.cjs');
const dest=f.art('candidate'),experiment=path.join(root,'.build/opus-fft-load3-board'),read=f.read;
function verifyPair(){
 const proof=read(path.join(dest,'preflight.json'));
 assert.equal(proof.recipe_sha256_lf,sourceHash(path.join(__dirname,'fft_load3.cjs')));assert.equal(proof.asm_sha256_lf,sourceHash(f.sourceFile));assert.equal(proof.asm_sha256_lf,sourceHash(path.join(dest,'patches.s')));
 const a=zlib.gunzipSync(fs.readFileSync(path.join(dest,'parent.elf.gz')));assert.equal(hash(a),proof.parent_elf_sha256);assert.equal(proof.patches.length,1);
 const p=f.findPatch(proof.functions.opus_fft_impl),{before_hex,after_hex,...saved}=proof.patches[0];assert.deepEqual(p,saved);
 const b=base.patchElf(a,proof.patches);assert.equal(hash(b),proof.candidate_elf_sha256);
 const object=fs.readFileSync(path.join(dest,'patches.o')),s=sections(object).find(s=>s.name==='.text.patch0');assert.equal(s.bytes,8);assert.equal(object.subarray(s.offset,s.offset+s.bytes).toString('hex'),after_hex);
 const old=base.rows(proof.functions.opus_fft_impl.disassembly),now=base.rows(proof.actual_functions.opus_fft_impl.disassembly),inside=rs=>rs.filter(r=>r.address>=p.address&&r.address<p.address+p.bytes),outside=rs=>rs.filter(r=>r.address<p.address||r.address>=p.address+p.bytes);
 assert.deepEqual(outside(old),outside(now));assert.deepEqual(inside(now).map(r=>r.bytes),[3,2,3]);assert.deepEqual(inside(now).map(r=>r.text),f.replacement);assert.deepEqual(f.prove(inside(old).map(r=>r.text),inside(now).map(r=>r.text)),proof.symbolic);
 for(const n of f.names.filter(n=>n!=='opus_fft_impl'))assert.deepEqual(proof.actual_functions[n],proof.functions[n]);
 const manifests={},apps={};for(const t of['control','candidate']){manifests[t]=read(path.join(f.art(t),'manifest.json'));apps[t]=fs.readFileSync(path.join(f.art(t),'app.bin'));assert.equal(hash(apps[t]),manifests[t].app_sha256);assert.equal(apps[t].length,manifests[t].bytes);assert.equal(manifests[t].post_link_recipe_sha256_lf,proof.recipe_sha256_lf);assert.equal(manifests[t].post_link_asm_sha256_lf,proof.asm_sha256_lf);}
 f.manifestPair(manifests.control,manifests.candidate);assert.deepEqual(base.compareApps(apps.control,apps.candidate,proof.patches),proof.imageProof);assert.equal(hash(apps.control),require('./report_mdct_post_pair.cjs').verifyPair().manifests.candidate.app_sha256);return{proof,manifests};
}
function report(){const pair=verifyPair(),groups={},fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const[name,sub]of[['before','controls/before'],['candidate','runs'],['after','controls/after']]){const ota=read(path.join(experiment,'ota-'+name+'.json'));assert.equal(ota.pass,true);assert.equal(ota.sha256,pair.manifests[name==='candidate'?'candidate':'control'].app_sha256);const rows=archive(path.join(experiment,name),path.join(dest,sub));assert.equal(rows.length,10);for(const r of rows)validateRun(r.report,fixtures,ota.after.app_address);groups[name]=rows;fs.copyFileSync(path.join(experiment,'ota-'+name+'.json'),path.join(dest,'ota-'+name+'.json'));}
 const initial=compare(groups.before.map(r=>r.report),groups.candidate.map(r=>r.report)),repeated=compare(groups.after.map(r=>r.report),groups.candidate.map(r=>r.report)),result={pair,initial,repeated,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},inputs:Object.fromEntries(Object.entries(groups).map(([k,rs])=>[k,rs.map(({report,...r})=>r)])),scope:'All30 FFT three-load frozen-layout A/B/A attempts retained. RAM packets, no network audio/output/function/stage profiler. Not live qualification.'};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));console.log(JSON.stringify(result.selection));return result;
}
module.exports={verifyPair,report,experiment};if(require.main===module)report();
