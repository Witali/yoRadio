// Composition of independently exact parents; speed is NOT additive.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const intensity=require('./bands.cjs'),tell=require('./tell_inline.cjs');
function cModels(){
 const dir=path.join(root,'.build/opus-bands-tell-intensity');fs.mkdirSync(dir,{recursive:true});
 return tell.cModels().map(model=>{
  let text=fs.readFileSync(model.file,'utf8');
  text=intensity.once(text,'   qn = compute_qn(N, *b, offset, pulse_cap, stereo);',
   '   qn = (!encode && stereo && i>=intensity) ? 1 : compute_qn(N, *b, offset, pulse_cap, stereo);');
  const file=path.join(dir,path.basename(model.file));fs.writeFileSync(file,text);return {source:model.source,file};
 });
}
function generate(compiler){
 const {verify}=require('./verify.cjs');verify('bands-intensity-asm');verify('bands-tell-inline-asm');
 const base=path.join(component,'asm/lx106'),parent=JSON.parse(fs.readFileSync(path.join(base,'bands-tell-inline.json')));
 const dir=path.join(root,'.build/opus-bands-tell-intensity');fs.mkdirSync(dir,{recursive:true});
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const files=parent.files.map(entry=>{
  if(entry.source.endsWith('/entcode.c'))return {source:entry.source,overlay:entry.overlay,overlay_sha256_lf:entry.overlay_sha256_lf};
  const text=intensity.transform(fs.readFileSync(path.join(base,entry.overlay),'utf8'),'intensity');
  const pinned=fs.readFileSync(path.join(base,'gcc',entry.source+'.s'),'utf8');
  assert.equal(text,tell.transform(intensity.transform(pinned,'intensity'),entry.source),'Composition order must not change instructions');
  const overlay='bands-tell-intensity/'+entry.source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,text);
  const object=path.join(dir,'bands.o');run(compiler,['-mlongcalls','-x','assembler','-c',dest,'-o',object]);
  fs.writeFileSync(path.join(dir,'disassembly.txt'),run(dump,['-dr',object]));
  return {source:entry.source,overlay,overlay_sha256_lf:sourceHash(dest)};
 });
 const report={schema:1,candidate:'bands-tell-intensity-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),recipe_sha256_lf:sourceHash(__filename),
  parents:Object.fromEntries(['bands-intensity.json','bands-tell-inline.json'].map(f=>[f,sourceHash(path.join(base,f))])),files,
  additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-tell-intensity.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={cModels,generate};if(require.main===module)generate(process.argv[2]);
