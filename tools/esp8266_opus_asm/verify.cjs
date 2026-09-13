const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {component,sourceHash}=require('./export.cjs');
function verify(mode, directory=path.join(component,'asm/lx106'), componentRoot=component){
 assert.ok(['gcc-asm','optimized-asm','hoisted-asm'].includes(mode),'Unknown ASM selection');
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
 if(mode==='optimized-asm'||mode==='hoisted-asm'){
  optimization=JSON.parse(fs.readFileSync(path.join(directory,mode==='hoisted-asm'?'hoisted.json':'optimized.json'),'utf8'));
  assert.equal(optimization.base_manifest_sha256,sourceHash(path.join(directory,'manifest.json')));
  assert.equal(sourceHash(path.join(directory,optimization.overlay)),optimization.overlay_sha256_lf);
  assert.equal(sourceHash(path.join(__dirname,mode==='hoisted-asm'?'hoist.cjs':'ec_dec_update.inc.s')),optimization.recipe_sha256_lf);
 }
 const files=manifest.files.map(f=>{
  assert.equal(f.section_contents_exact,true,'Unverified ASM tables/section contents');
  const file=path.join(directory,f.asm);assert.equal(sourceHash(file),f.asm_sha256_lf,'Modified GCC baseline: '+f.asm);
  return optimization&&f.source===(mode==='hoisted-asm'?'upstream/celt/vq.c':'upstream/celt/entdec.c')?path.join(directory,optimization.overlay):file;
 });
 return {manifest,files};
}
module.exports={verify};
if(require.main===module){
 const r=verify(process.argv[2]), i=process.argv.indexOf('--cmake-output');
 if(i>=0)fs.writeFileSync(process.argv[i+1],'set(OPUS_SOURCES\n'+r.files.map(f=>'  "'+f.replaceAll('\\','/')+'"').join('\n')+'\n)\n');
 console.log(`Verified ${r.files.length} ${process.argv[2]} sources and pinned C/header hashes`);
}
