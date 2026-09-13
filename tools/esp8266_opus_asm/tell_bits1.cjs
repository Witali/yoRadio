// Compose the best tell-inline with exact, constant-one entropy specialization.
// Protected GCC source and shared ec_dec_bits remain unchanged; no RAM growth.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const tell=require('./tell_inline.cjs'),{once}=require('./bands.cjs'),{canonical}=require('./disassembly.cjs');
const kind='tell-bits1',source='upstream/celt/bands.c',macroPath=path.join(__dirname,'bits1_fast.inc.s');
function addBits(text){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/Y_OPUS_BITS1_FAST/);
 let total=0;
 for(const [name,expected] of [['quant_band',1],['quant_all_bands',2]]){
  const body=text.match(new RegExp('^'+name+':[\\s\\S]*?(?=^\\s*\\.size\\s+'+name+',)','m'))?.[0];assert.ok(body);
  let n=0;const changed=body.replace(/^\tcall0\tec_dec_bits\t\t#$/gm,()=>{n++;return '\tY_OPUS_BITS1_FAST\t# Exact constant-one sign decode; original cold call.';});
  assert.equal(n,expected);total+=n;text=text.replace(body,changed);
 }
 assert.equal(total,3);assert.doesNotMatch(text,/^\tcall0\tec_dec_bits\t/gm);
 return fs.readFileSync(macroPath,'utf8').replace(/\r\n/g,'\n')+'\n'+text;
}
function transform(text){return addBits(tell.transform(text,source));}
function cModels(){
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 return tell.cModels().map(model=>{
  let text=fs.readFileSync(model.file,'utf8');assert.equal((text.match(/ec_dec_bits\(ec, 1\)/g)||[]).length,2);
  text=text.replace(/ec_dec_bits\(ec, 1\)/g,'y_bits1_fast(ec)');
  text=once(text,'#include "rate.h"\n','#include "rate.h"\n'+[
   'static opus_uint32 y_bits1_fast(ec_dec *ctx) {',
   ' if ((unsigned)ctx->nend_bits != 0) {',
   '  opus_uint32 result=ctx->end_window & 1u;',
   '  ctx->end_window >>= 1; ctx->nend_bits -= 1; ctx->nbits_total += 1;',
   '  return result;',
   ' } return ec_dec_bits(ctx, 1);',
   '}',''].join('\n'));
  const file=path.join(dir,path.basename(model.file));fs.writeFileSync(file,text);return {source:model.source,file};
 });
}
function generate(compiler){
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const base=path.join(component,'asm/lx106'),parentFile=path.join(base,'bands-tell-inline.json'),parent=JSON.parse(fs.readFileSync(parentFile));
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const files=parent.files.map(e=>{
  if(e.source!==source)return {source:e.source,overlay:e.overlay,overlay_sha256_lf:e.overlay_sha256_lf};
  const controlSource=path.join(base,e.overlay),text=transform(fs.readFileSync(path.join(base,'gcc',source+'.s'),'utf8'));
  assert.equal(text,addBits(fs.readFileSync(controlSource,'utf8')));
  const overlay='bands-'+kind+'/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,text);
  const object=path.join(dir,'bands.o'),control=object+'.tell-inline';
  for(const [s,o] of [[controlSource,control],[dest,object]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
  const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
  const a=sizes(control),b=sizes(object);assert.deepEqual(Object.keys(a),Object.keys(b));
  for(const s of Object.keys(a).filter(s=>a[s]&&!s.startsWith('.xt.')&&!['.text.quant_band','.text.quant_all_bands'].includes(s))){
   if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,control])),canonical(run(dump,['-dr','-j',s,object])),s);
   else {assert.equal(a[s],b[s],s);assert.equal(run(dump,['-s','-j',s,control]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,object]).split('\n').slice(3).join('\n'),s);}
  }
  fs.writeFileSync(path.join(dir,'disassembly.txt'),run(dump,['-dr',object]));
  return {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_tell:a,sections_candidate:b};
 });
 const report={schema:1,candidate:'bands-tell-bits1-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),recipe_sha256_lf:sourceHash(__filename),
  parent_sha256_lf:sourceHash(parentFile),dependencies:{'bits1_fast.inc.s':sourceHash(macroPath)},files,
  expanded_tell_sites:4,fast_bits1_sites:3,additional_table_bytes:0,additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-'+kind+'.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,source,transform,addBits,cModels,generate};if(require.main===module)generate(process.argv[2]);
