const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {component,sourceHash}=require('./export.cjs');
function verify(mode, directory=path.join(component,'asm/lx106'), componentRoot=component){
 assert.ok(['gcc-asm','optimized-asm','hoisted-asm','bands-intensity-asm','bands-blocks-asm','bands-combined-asm','bands-pulse-lookup-asm','bands-tell-inline-asm','bands-fused-asm','bands-tell-intensity-asm','bands-update-fast-asm','bands-tell-update-asm','bands-tell-bits1-asm','bands-layout32-asm','bands-layout128-asm','bands-cache-reuse-asm','bands-inner4-asm','bands-logp-asm','bands-pvq-addx-asm','bands-small-div-asm','bands-small-div-tail-asm','bands-small-div-inline-asm','bands-folding8-asm','bands-partition-decode-asm'].includes(mode),'Unknown ASM selection');
 const manifest=JSON.parse(fs.readFileSync(path.join(directory,'manifest.json'),'utf8'));
 assert.equal(manifest.roundtrip_exact,true);
 assert.equal(manifest.cpu,'LX106');assert.equal(manifest.abi,'call0');
 assert.deepEqual(manifest.feature_defines,[
  'YORADIO_OPUS_BOUNDED=1','YORADIO_OPUS_FIR_FLASH_WORD=1','YORADIO_OPUS_ICDF_FLASH_WORD=1',
  'YORADIO_OPUS_PROFILE_STAGE=0','YORADIO_OPUS_WORD_ASM=1'
 ],'ASM snapshot feature set is incompatible with the build guard');
 for(const [relative,expected] of Object.entries(manifest.protected_sources))
  assert.equal(sourceHash(path.join(componentRoot,relative)),expected,'Stale ASM source/header: '+relative+'; regenerate the snapshot');
 const actual=['src','celt','silk','silk/fixed'].flatMap(d=>fs.readdirSync(path.join(componentRoot,'upstream',d)).filter(f=>f.endsWith('.c')).map(f=>'upstream/'+d+'/'+f)).sort();
 assert.deepEqual(manifest.files.map(f=>f.source).sort(),actual,'ASM corpus does not cover current C units');
 let optimization;
 let overlays=[];
 if(mode==='bands-partition-decode-asm'){
  verify('bands-tell-inline-asm',directory,componentRoot);
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-partition-decode.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-tell-inline.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'partition_decode.cjs')));
  assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.stack_change_bytes,0);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  const parent=JSON.parse(fs.readFileSync(path.join(directory,'bands-tell-inline.json')));
  const original=fs.readFileSync(path.join(directory,parent.files[0].overlay),'utf8');
  const candidate=require('./partition_decode.cjs').specialize(original);
  assert.equal(fs.readFileSync(path.join(directory,r.files[0].overlay),'utf8').replace(/\r\n/g,'\n'),candidate.text);
  assert.deepEqual(r.proof,candidate.proof);assert.deepEqual(r.files[1],parent.files[1]);
  overlays=r.files;
 }
 if(mode==='bands-folding8-asm'){
  verify('bands-tell-inline-asm',directory,componentRoot);
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-folding8.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-tell-inline.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'folding8.cjs')));
  assert.equal(r.census_sha256_lf,sourceHash(path.join(__dirname,'folding-census-results.json')));
  assert.equal(r.table_bytes,92);assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.stack_change_bytes,0);assert.equal(r.changed_calls,1);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  const parent=JSON.parse(fs.readFileSync(path.join(directory,'bands-tell-inline.json')));
  const original=fs.readFileSync(path.join(directory,parent.files[0].overlay),'utf8');
  assert.equal(fs.readFileSync(path.join(directory,r.files[0].overlay),'utf8').replace(/\r\n/g,'\n'),require('./folding8.cjs').transform(original));
  overlays=r.files;
 }
 if(mode==='bands-small-div-inline-asm'){
  verify('bands-small-div-asm',directory,componentRoot);
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-small-div-inline.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-tell-inline.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'small_div_inline.cjs')));
  assert.equal(r.small_recipe_sha256_lf,sourceHash(path.join(__dirname,'small_div.cjs')));
  assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.stack_change_bytes,0);
  assert.equal(r.expanded_calls,3);assert.equal(r.table_bytes,516);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c','upstream/celt/entdec.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  const original=fs.readFileSync(path.join(directory,'gcc/upstream/celt/entdec.c.s'),'utf8');
  assert.equal(fs.readFileSync(path.join(directory,r.files[2].overlay),'utf8').replace(/\r\n/g,'\n'),require('./small_div_inline.cjs').transform(original));
  overlays=r.files;
 }
 if(mode==='bands-small-div-tail-asm'){
  verify('bands-small-div-asm',directory,componentRoot);
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-small-div-tail.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-small-div.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'small_div_tail.cjs')));
  assert.equal(r.small_recipe_sha256_lf,sourceHash(path.join(__dirname,'small_div.cjs')));
  assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.changed_calls,3);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c','upstream/celt/entdec.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  const original=fs.readFileSync(path.join(directory,'gcc/upstream/celt/entdec.c.s'),'utf8');
  assert.equal(fs.readFileSync(path.join(directory,r.files[2].overlay),'utf8').replace(/\r\n/g,'\n'),require('./small_div_tail.cjs').transform(original));
  overlays=r.files;
 }
 if(mode==='bands-small-div-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-small-div.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'small_div.cjs')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-tell-inline.json')));
  assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.stack_change_bytes,0);
  assert.equal(r.changed_calls,3);assert.equal(r.table_bytes,516);
  verify('bands-tell-inline-asm',directory,componentRoot);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c','upstream/celt/entdec.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  const original=fs.readFileSync(path.join(directory,'gcc/upstream/celt/entdec.c.s'),'utf8');
  assert.equal(fs.readFileSync(path.join(directory,r.files[2].overlay),'utf8').replace(/\r\n/g,'\n'),require('./small_div.cjs').transform(original));
  overlays=r.files;
 }
 if(mode==='bands-pvq-addx-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-pvq-addx.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'pvq_addx.cjs')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-tell-inline.json')));
  assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.stack_change_bytes,0);
  assert.equal(r.fused_pairs,20);assert.equal(r.object_instruction_graph_exact,true);
  verify('bands-tell-inline-asm',directory,componentRoot);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c','upstream/celt/cwrs.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-logp-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-logp.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'logp.cjs')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-tell-inline.json')));
  assert.deepEqual(Object.keys(r.dependencies),['logp_prefix.inc.s']);
  assert.equal(r.dependencies['logp_prefix.inc.s'],sourceHash(path.join(__dirname,'logp_prefix.inc.s')));
  assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.stack_fast_bytes,0);assert.equal(r.stack_cold_bytes,16);
  verify('bands-tell-inline-asm',directory,componentRoot);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c','upstream/celt/entdec.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-inner4-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-inner4.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'inner4.cjs')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-tell-inline.json')));
  assert.deepEqual(Object.keys(r.dependencies),['inner4_loop.inc.s']);
  assert.equal(r.dependencies['inner4_loop.inc.s'],sourceHash(path.join(__dirname,'inner4_loop.inc.s')));
  assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.stack_change_bytes,0);
  assert.equal(r.unroll_elements,4);assert.equal(r.threshold_elements,8);
  verify('bands-tell-inline-asm',directory,componentRoot);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c','upstream/celt/vq.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-cache-reuse-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-cache-reuse.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'cache_reuse.cjs')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-tell-inline.json')));
  assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.stack_change_bytes,0);
  verify('bands-tell-inline-asm',directory,componentRoot);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-layout32-asm'||mode==='bands-layout128-asm'){
  const bytes=mode==='bands-layout32-asm'?32:128;
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-layout'+bytes+'.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'layout.cjs')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-tell-inline.json')));
  assert.equal(r.pad_bytes,bytes);assert.equal(r.pad_before,'quant_partition');
  assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.stack_change_bytes,0);
  verify('bands-tell-inline-asm',directory,componentRoot);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  assert.equal(r.files[0].object_instruction_graph_exact,true);
  overlays=r.files;
 }
 if(mode==='bands-tell-bits1-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-tell-bits1.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'tell_bits1.cjs')));
  assert.equal(r.parent_sha256_lf,sourceHash(path.join(directory,'bands-tell-inline.json')));
  assert.deepEqual(Object.keys(r.dependencies),['bits1_fast.inc.s']);
  assert.equal(r.dependencies['bits1_fast.inc.s'],sourceHash(path.join(__dirname,'bits1_fast.inc.s')));
  verify('bands-tell-inline-asm',directory,componentRoot);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-tell-update-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-tell-update.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'tell_update.cjs')));
  assert.deepEqual(Object.keys(r.parents),['bands-tell-inline.json','bands-update-fast.json']);
  for(const [f,h] of Object.entries(r.parents))assert.equal(sourceHash(path.join(directory,f)),h);
  verify('bands-tell-inline-asm',directory,componentRoot);verify('bands-update-fast-asm',directory,componentRoot);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-update-fast-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-update-fast.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'update_fast.cjs')));
  assert.deepEqual(Object.keys(r.dependencies),['update_fast.inc.s']);
  assert.equal(r.dependencies['update_fast.inc.s'],sourceHash(path.join(__dirname,'update_fast.inc.s')));
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-tell-intensity-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-tell-intensity.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'tell_intensity.cjs')));
  assert.deepEqual(Object.keys(r.parents),['bands-intensity.json','bands-tell-inline.json']);
  for(const [f,h] of Object.entries(r.parents))assert.equal(sourceHash(path.join(directory,f)),h);
  verify('bands-intensity-asm',directory,componentRoot);verify('bands-tell-inline-asm',directory,componentRoot);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-fused-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-fused.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'fused.cjs')));
  assert.deepEqual(Object.keys(r.dependencies),['fused_normalize.inc.s','../../tests/native/esp8266_opus_fused_normalize_test.c']);
  for(const [f,h] of Object.entries(r.dependencies))assert.equal(sourceHash(path.join(__dirname,f)),h);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/vq.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-tell-inline-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-tell-inline.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'tell_inline.cjs')));
  assert.deepEqual(Object.keys(r.dependencies),['tell_inline.inc.s']);
  assert.equal(r.dependencies['tell_inline.inc.s'],sourceHash(path.join(__dirname,'tell_inline.inc.s')));
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/entcode.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-pulse-lookup-asm'){
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-pulse-lookup.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'pulse_lookup.cjs')));
  assert.deepEqual(Object.keys(r.dependencies),['pulse_lookup.inc.s','pulse_inverse.cjs']);
  for(const [f,h] of Object.entries(r.dependencies))assert.equal(sourceHash(path.join(__dirname,f)),h);
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/modes.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-blocks-asm'||mode==='bands-combined-asm'){
  const kind=mode==='bands-blocks-asm'?'blocks':'combined';
  const r=JSON.parse(fs.readFileSync(path.join(directory,'bands-'+kind+'.json'),'utf8'));
  assert.equal(r.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,kind+'.cjs')));
  if(kind==='combined'){
   assert.deepEqual(Object.keys(r.parents),['bands-intensity.json','bands-blocks.json']);
   for(const [f,h] of Object.entries(r.parents))assert.equal(sourceHash(path.join(directory,f)),h);
   verify('bands-intensity-asm',directory,componentRoot);verify('bands-blocks-asm',directory,componentRoot);
  }
  assert.deepEqual(r.files.map(f=>f.source),['upstream/celt/bands.c','upstream/celt/vq.c']);
  for(const f of r.files)assert.equal(sourceHash(path.join(directory,f.overlay)),f.overlay_sha256_lf);
  overlays=r.files;
 }
 if(mode==='bands-intensity-asm'){
  optimization=JSON.parse(fs.readFileSync(path.join(directory,'bands-intensity.json'),'utf8'));
  assert.equal(optimization.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(sourceHash(path.join(directory,optimization.overlay)),optimization.overlay_sha256_lf);
  assert.equal(sourceHash(path.join(__dirname,'bands.cjs')),optimization.recipe_sha256_lf);
  assert.equal(optimization.source,'upstream/celt/bands.c');
 }
 if(mode==='optimized-asm'||mode==='hoisted-asm'){
  optimization=JSON.parse(fs.readFileSync(path.join(directory,mode==='hoisted-asm'?'hoisted.json':'optimized.json'),'utf8'));
  assert.equal(optimization.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(sourceHash(path.join(directory,optimization.overlay)),optimization.overlay_sha256_lf);
  assert.equal(sourceHash(path.join(__dirname,mode==='hoisted-asm'?'hoist.cjs':'ec_dec_update.inc.s')),optimization.recipe_sha256_lf);
 }
 const files=manifest.files.map(f=>{
  assert.equal(f.section_contents_exact,true,'Unverified ASM tables/section contents');
  const file=path.join(directory,f.asm);assert.equal(sourceHash(file),f.asm_sha256_lf,'Modified GCC baseline: '+f.asm);
  const overlay=overlays.find(o=>o.source===f.source);if(overlay)return path.join(directory,overlay.overlay);
  return optimization&&f.source===(mode==='bands-intensity-asm'?optimization.source:mode==='hoisted-asm'?'upstream/celt/vq.c':'upstream/celt/entdec.c')?path.join(directory,optimization.overlay):file;
 });
 return {manifest,files};
}
module.exports={verify};
if(require.main===module){
 const r=verify(process.argv[2]), i=process.argv.indexOf('--cmake-output');
 if(i>=0)fs.writeFileSync(process.argv[i+1],'set(OPUS_SOURCES\n'+r.files.map(f=>'  "'+f.replaceAll('\\','/')+'"').join('\n')+'\n)\n');
 console.log(`Verified ${r.files.length} ${process.argv[2]} sources and pinned C/header hashes`);
}
