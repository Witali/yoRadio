const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {component,sourceHash}=require('./export.cjs');
function verify(mode, directory=path.join(component,'asm/lx106'), componentRoot=component){
 assert.ok(['gcc-asm','optimized-asm','hoisted-asm','bands-intensity-asm','bands-blocks-asm','bands-combined-asm','bands-pulse-lookup-asm','bands-tell-inline-asm','bands-fused-asm','bands-tell-intensity-asm'].includes(mode),'Unknown ASM selection');
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
