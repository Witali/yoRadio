// Composition only: no third optimization and no change to either parent.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const intensity=require('./bands.cjs'),blocks=require('./blocks.cjs');
function cModels(){
 const dir=path.join(root,'.build/opus-bands-combined');fs.mkdirSync(dir,{recursive:true});
 return blocks.cModels().map(model=>{
  let text=fs.readFileSync(model.file,'utf8');
  if(model.source.endsWith('/bands.c'))text=intensity.once(text,
   '   qn = compute_qn(N, *b, offset, pulse_cap, stereo);',
   '   qn = (!encode && stereo && i>=intensity) ? 1 : compute_qn(N, *b, offset, pulse_cap, stereo);');
  const file=path.join(dir,path.basename(model.file));fs.writeFileSync(file,text);return {source:model.source,file};
 });
}
function generate(compiler){
 const {verify}=require('./verify.cjs');verify('bands-intensity-asm');verify('bands-blocks-asm');
 const base=path.join(component,'asm/lx106'),a=JSON.parse(fs.readFileSync(path.join(base,'bands-blocks.json')));
 const dir=path.join(root,'.build/opus-bands-combined');fs.mkdirSync(dir,{recursive:true});
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const files=a.files.map(entry=>{
  const original=path.join(base,entry.overlay);
  if(entry.source.endsWith('/vq.c'))return {source:entry.source,overlay:entry.overlay,overlay_sha256_lf:entry.overlay_sha256_lf};
  const text=intensity.transform(fs.readFileSync(original,'utf8'),'intensity');
  const overlay='bands-combined/'+entry.source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,text);
  const object=path.join(dir,'bands.o');run(compiler,['-mlongcalls','-x','assembler','-c',dest,'-o',object]);
  fs.writeFileSync(path.join(dir,'disassembly.txt'),run(dump,['-dr','-j','.text.quant_band','-j','.text.quant_all_bands',object]));
  return {source:entry.source,overlay,overlay_sha256_lf:sourceHash(dest)};
 });
 const report={schema:1,candidate:'bands-combined-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),recipe_sha256_lf:sourceHash(__filename),
  parents:Object.fromEntries(['bands-intensity.json','bands-blocks.json'].map(f=>[f,sourceHash(path.join(base,f))])),files,
  additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-combined.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={cModels,generate};if(require.main===module)generate(process.argv[2]);
