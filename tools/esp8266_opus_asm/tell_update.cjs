// Exact composition: four tell_frac inline sites plus two no-normalize
// update sites. The two macros retain their documented call0 ABI; no new
// stack slots, arena, table copies or C production changes. Speed is not additive.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const tell=require('./tell_inline.cjs'),update=require('./update_fast.cjs');
const {once}=require('./bands.cjs'),{canonical}=require('./disassembly.cjs');
const kind='tell-update',source='upstream/celt/bands.c';
function transform(text){return update.transform(tell.transform(text,source));}
function cModels(){
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 return tell.cModels().map(model=>{
  let text=fs.readFileSync(model.file,'utf8');
  assert.equal((text.match(/\bec_dec_update\(/g)||[]).length,2);
  text=text.replace(/\bec_dec_update\(/g,'y_update_fast(');
  text=once(text,'#include "rate.h"\n','#include "rate.h"\n'+update.helper());
  const file=path.join(dir,path.basename(model.file));fs.writeFileSync(file,text);
  return {source:model.source,file};
 });
}
function generate(compiler){
 const {verify}=require('./verify.cjs');verify('bands-tell-inline-asm');verify('bands-update-fast-asm');
 const base=path.join(component,'asm/lx106'),parent=JSON.parse(fs.readFileSync(path.join(base,'bands-tell-inline.json')));
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const files=parent.files.map(entry=>{
  if(entry.source!==source)return {source:entry.source,overlay:entry.overlay,overlay_sha256_lf:entry.overlay_sha256_lf};
  const pinned=fs.readFileSync(path.join(base,'gcc',source+'.s'),'utf8');
  const text=transform(pinned);assert.equal(text,update.transform(fs.readFileSync(path.join(base,entry.overlay),'utf8')));
  const overlay='bands-'+kind+'/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,text);
  const object=path.join(dir,'bands.o'),control=object+'.tell-inline';
  for(const [s,o] of [[path.join(base,entry.overlay),control],[dest,object]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
  const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
  const a=sizes(control),b=sizes(object);assert.deepEqual(Object.keys(a),Object.keys(b));
  for(const s of Object.keys(a).filter(s=>a[s]&&!s.startsWith('.xt.')&&!['.text.quant_partition','.text.quant_all_bands'].includes(s))){
   if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,control])),canonical(run(dump,['-dr','-j',s,object])),s);
   else {assert.equal(a[s],b[s],s);assert.equal(run(dump,['-s','-j',s,control]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,object]).split('\n').slice(3).join('\n'),s);}
  }
  fs.writeFileSync(path.join(dir,'disassembly.txt'),run(dump,['-dr',object]));
  return {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_tell:a,sections_combined:b};
 });
 const report={schema:1,candidate:'bands-tell-update-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),recipe_sha256_lf:sourceHash(__filename),
  parents:Object.fromEntries(['bands-tell-inline.json','bands-update-fast.json'].map(f=>[f,sourceHash(path.join(base,f))])),files,
  expanded_tell_sites:4,fast_update_sites:2,additional_table_bytes:0,additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-tell-update.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,source,transform,cModels,generate};if(require.main===module)generate(process.argv[2]);
