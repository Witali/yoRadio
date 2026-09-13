// Isolate call/return removal: exact GCC arithmetic, four decoder sites only.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const {once}=require('./bands.cjs');
const {canonical}=require('./disassembly.cjs');
const kind='tell-inline',sources=['upstream/celt/bands.c','upstream/celt/entcode.c'];
function transform(text,source){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/y_opus_tell_correction|Y_OPUS_TELL_FRAC/);
 if(source===sources[1])return text+'\n# Address-only alias; the original 32-byte table is not duplicated.\n\t.global y_opus_tell_correction\n\t.set y_opus_tell_correction, correction$2307\n';
 assert.equal(source,sources[0]);
 text=once(text,'\t.literal .LC2, -16384\n','\t.literal .LC2, -16384\n\t.literal .Lasm_tell_table, y_opus_tell_correction\n');
 const re=/^quant_partition:[\s\S]*?(?=^\s*\.size\s+quant_partition,)/m;
 const body=text.match(re)?.[0];assert.ok(body);let calls=0;
 const changed=body.replace(/^\tcall0\tec_tell_frac\t\t#$/gm,match=>++calls<=4?
  '\tY_OPUS_TELL_FRAC\t# Exact inlining; original call0 ABI and state.':match);
 assert.equal(calls,6,'Pinned quant_partition has four decoder and two encoder sites');
 text=text.replace(body,changed);
 return fs.readFileSync(path.join(__dirname,'tell_inline.inc.s'),'utf8').replace(/\r\n/g,'\n')+'\n'+text;
}
function cModels(){
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const ent=fs.readFileSync(path.join(component,sources[1]),'utf8').replace(/\r\n/g,'\n');
 const body=ent.match(/opus_uint32 ec_tell_frac\(ec_ctx \*_this\)\{[\s\S]*?^\}/m)?.[0];assert.ok(body);
 let bands=fs.readFileSync(path.join(component,sources[0]),'utf8').replace(/\r\n/g,'\n');
 // Host semantic check expands the same PURE body at all bands sites. Physical
 // ASM is intentionally narrower; its four-site scope is checked independently.
 bands=bands.replace(/\bec_tell_frac\(/g,'y_inline_tell_frac(');
 bands=once(bands,'#include "rate.h"\n','#include "rate.h"\n'+
  body.replace('opus_uint32 ec_tell_frac','static inline opus_uint32 y_inline_tell_frac')+'\n');
 const file=path.join(dir,'bands.model.c');fs.writeFileSync(file,bands);
 return [{source:sources[0],file}];
}
function generate(compiler){
 const base=path.join(component,'asm/lx106'),mf=path.join(base,'manifest.json'),m=JSON.parse(fs.readFileSync(mf));
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const files=sources.map(source=>{
  const e=m.files.find(f=>f.source===source),original=path.join(base,e.asm);assert.equal(sourceHash(original),e.asm_sha256_lf);
  const overlay='bands-'+kind+'/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});
  fs.writeFileSync(dest,transform(fs.readFileSync(original,'utf8'),source));
  const object=path.join(dir,path.basename(source)+'.o'),control=object+'.control';
  for(const [s,o] of [[original,control],[dest,object]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
  const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
  const a=sizes(control),b=sizes(object);assert.deepEqual(Object.keys(a),Object.keys(b));
  for(const s of Object.keys(a).filter(s=>a[s]&&!s.startsWith('.xt.')&&!(source===sources[0]&&['.text.quant_partition','.literal.quant_partition'].includes(s)))){
   if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,control])),canonical(run(dump,['-dr','-j',s,object])),s);
   else {assert.equal(a[s],b[s],s);assert.equal(run(dump,['-s','-j',s,control]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,object]).split('\n').slice(3).join('\n'),s);}
  }
  fs.writeFileSync(object+'.dump',run(dump,['-dr',object]));
  return {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:a,sections_after:b};
 });
 const report={schema:1,candidate:'bands-'+kind+'-v1',base_manifest_sha256:sourceHash(mf),recipe_sha256_lf:sourceHash(__filename),
  dependencies:{'tell_inline.inc.s':sourceHash(path.join(__dirname,'tell_inline.inc.s'))},files,
  expanded_call_sites:4,additional_table_bytes:0,additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-'+kind+'.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,sources,transform,cModels,generate};if(require.main===module)generate(process.argv[2]);
