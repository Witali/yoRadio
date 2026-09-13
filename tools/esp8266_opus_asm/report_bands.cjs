// Archive every numbered attempt and compare identical raw benchmark profiles.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,hash,sourceHash,run}=require('./export.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('./selection.cjs');
const compilerBin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
function read(file){return JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));}
function archive(source,dest){
 fs.mkdirSync(dest,{recursive:true});
 const names=fs.readdirSync(source).filter(n=>/^run[1-9]\d*\.(json|log)$/.test(n)).sort();
 assert.equal(names.filter(n=>n.endsWith('.json')).length,10,'Exactly ten recorded attempts, not a filtered subset');
 const reports=[];
 for(const name of names){const from=path.join(source,name),to=path.join(dest,name),bytes=fs.readFileSync(from);
  if(fs.existsSync(to))assert.equal(hash(fs.readFileSync(to)),hash(bytes),'Do not overwrite a different run');
  else fs.copyFileSync(from,to);
 }
 for(let i=1;i<=10;i++){const file=path.join(dest,'run'+i+'.json');reports.push({file:path.relative(root,file).replaceAll('\\','/'),sha256:hash(fs.readFileSync(file)),report:read(file)});}
 return reports;
}
function report(kind){
 assert.ok(['intensity','blocks','combined','pulse-lookup'].includes(kind));
 const av='esp8266-opus-functions-control-v2',bv='esp8266-opus-bands-'+kind+'-v1';
 const art=path.join(root,'firmware/development',bv),control=path.join(root,'firmware/development/esp8266-opus-bands-control-v1');
 const aa=path.join(root,'firmware/development',av),ma=read(path.join(aa,'manifest.json')),mb=read(path.join(art,'manifest.json'));
 for(const [dir,m] of [[aa,ma],[art,mb]]){
  const bytes=fs.readFileSync(path.join(dir,'app.bin'));assert.equal(bytes.length,m.bytes);assert.equal(hash(bytes),m.app_sha256.toLowerCase());
  assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);
 }
 assert.equal(ma.opus_backend,'gcc-asm');assert.equal(mb.opus_backend,'bands-'+kind+'-asm');
 const identity=['opus_backend','opus_asm_optimization_sha256','opus_bands_blocks_manifest_sha256','opus_bands_combined_manifest_sha256','opus_bands_pulse_lookup_manifest_sha256','built_utc','source_revision','app_sha256','bytes'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!identity.includes(k))assert.deepEqual(mb[k]??null,ma[k]??null,'Build profile differs: '+k);
 const recipe=path.join(component,'asm/lx106/bands-'+kind+'.json'),rm=read(recipe);
 const selected=kind==='intensity'?mb.opus_asm_optimization_sha256:mb['opus_bands_'+kind.replaceAll('-','_')+'_manifest_sha256'];
 assert.equal(selected.toLowerCase(),hash(fs.readFileSync(recipe)));
 fs.mkdirSync(control,{recursive:true});
 for(const file of ['app.bin','manifest.json']){
  const dest=path.join(control,file);if(fs.existsSync(dest))assert.equal(hash(fs.readFileSync(dest)),hash(fs.readFileSync(path.join(aa,file))));
  else fs.copyFileSync(path.join(aa,file),dest);
 }
 const a=kind==='pulse-lookup'
  ?archive(path.join(root,'.build/opus-pulse-lookup-control-20260913'),path.join(control,'pulse-lookup-20260913'))
  :archive(path.join(root,'.build/opus-bands-control-20260913'),path.join(control,'initial'));
 const b=archive(path.join(root,'.build/opus-bands-'+kind+'-20260913'),path.join(art,'runs'));
 const result=compare(a.map(v=>v.report),b.map(v=>v.report));
 const repeated=path.join(root,'.build/opus-bands-control-repeat-20260913');
 if(kind!=='pulse-lookup'&&fs.existsSync(path.join(repeated,'run10.json'))&&read(path.join(repeated,'run10.json')).final?.state===3){
  const a2=archive(repeated,path.join(control,'repeated'));result.repeated_control=compare(a2.map(v=>v.report),b.map(v=>v.report));
  result.repeated_control_inputs=a2.map(({report,...r})=>r);
 }
 const sections=variant=>{
  const elf=path.join(root,'.build',variant,'yoradio_esp8266_helix_native.elf');
  return Object.fromEntries([...run(path.join(compilerBin,'xtensa-lx106-elf-size.exe'),['-A',elf]).matchAll(/^(\.(?:iram0|dram0|flash)\.\S+)\s+(\d+)\s+/gm)].map(m=>[m[1],Number(m[2])]));
 };
 const sa=sections(av),sb=sections(bv);assert.ok(Object.keys(sa).length>=5);
 for(const s of Object.keys(sa).filter(s=>!s.startsWith('.flash.')))assert.equal(sb[s],sa[s],'Static RAM changed: '+s);
 result.build={reference:ma,candidate:mb,reference_sections:sa,candidate_sections:sb,recipe_manifest:rm,recipe_manifest_sha256:sourceHash(recipe),static_ram_delta:0};
 result.inputs={reference:a.map(({report,...r})=>r),candidate:b.map(({report,...r})=>r)};
 const host=path.join(root,'.build/opus-bands-'+kind+'/correctness.json');result.host=read(host);assert.equal(result.host.passed,true);assert.equal(result.host.recipe_sha256_lf,rm.recipe_sha256_lf);
 result.selection={initial:selectHighBitrate(result.cases),repeated_control:result.repeated_control?selectHighBitrate(result.repeated_control.cases):null};
 result.selection.accepted_for_experimental_asm=result.selection.initial.accepted_for_experimental_asm&&
  (kind==='pulse-lookup'||!!result.selection.repeated_control?.accepted_for_experimental_asm);
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const run of [...a,...b])for(const [i,v] of run.report.final.results.entries()){
  assert.equal(v.pcm_hash,fixtures.fixtures[i].expected_hash);assert.equal(v.samples,fixtures.fixtures[i].samples*run.report.final.rounds);
  assert.equal(v.packets,fixtures.fixtures[i].packet_count*run.report.final.rounds);
 }
 fs.writeFileSync(path.join(art,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result.cases.map(c=>({name:c.name,baseline:c.reference.task_budget_percent.median,candidate:c.candidate.task_budget_percent.median,reduction_percent:c.median_task_reduction_percent,min_heap:c.candidate.min_dram.min,stack_free:c.candidate.stack_free_lifetime.min})),null,2));
 return result;
}
module.exports={report,archive};
if(require.main===module)report(process.argv[2]);
