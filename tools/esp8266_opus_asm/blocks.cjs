// Exact division strength reduction at three decoder block-count sites.
// Do not touch qn/entropy divisions or exp_rotation's arbitrary stride2.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const {canonical}=require('./disassembly.cjs');
const specs=[{source:'upstream/celt/bands.c',fn:'quant_band',calls:1},
 {source:'upstream/celt/vq.c',fn:'alg_unquant',calls:2}];
function transform(text,spec){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/# ASM block division:/);
 const re=new RegExp('^'+spec.fn+':[\\s\\S]*?(?=^\\s*\\.size\\s+'+spec.fn+',)','m');
 const body=text.match(re)?.[0];assert.ok(body);let count=0;
 const updated=body.replace(/^\tcall0\t__udivsi3\t\t#$/gm,()=>{
  const label='.Lasm_block_'+spec.fn+'_'+count++;
  return '# ASM block division: a2=unsigned N, a3=unsigned B; result a2.\n'+
   '# a4/a5 are call-clobbered; no extra stack, loads or interrupt masking.\n'+
   '# Normal B=1,2,4,8 (TF may change it). Non-powers/zero retain libgcc.\n'+
   '\tbeqz\ta3, '+label+'_fallback\n\taddi\ta4, a3, -1\n\tand\ta4, a4, a3\n'+
   '\tbnez\ta4, '+label+'_fallback\n\tnsau\ta4, a3\n\tmovi\ta5, 31\n'+
   '\tsub\ta4, a5, a4\n\tssr\ta4\n\tsrl\ta2, a2\n\tj\t'+label+'_done\n'+
   label+'_fallback:\n\tcall0\t__udivsi3\t\t#\n'+label+'_done:';
 });assert.equal(count,spec.calls);return text.replace(body,updated);
}
function cModels(){
 const dir=path.join(root,'.build/opus-bands-blocks');fs.mkdirSync(dir,{recursive:true});
 const helper='\n/* Semantic mirror of the LX106 block division shortcut. */\n'+
  'static unsigned y_block_div(unsigned n, unsigned d) {\n'+
  ' if (d && !(d & (d-1))) return n >> (31-__builtin_clz(d));\n return n/d;\n}\n';
 return specs.map(spec=>{
  let text=fs.readFileSync(path.join(component,spec.source),'utf8').replace(/\r\n/g,'\n');
  // Helper has only built-in types; put it before includes without changing flags.
  text=helper+text;
  const replacements=spec.fn==='quant_band'?['N_B = celt_udiv(N_B, B);']:
    ['len = celt_udiv(len, stride);','N0 = celt_udiv(N, B);'];
  for(const before of replacements){assert.equal(text.split(before).length,2);text=text.replace(before,before.replace('celt_udiv','y_block_div'));}
  const file=path.join(dir,path.basename(spec.source)+'.model.c');fs.writeFileSync(file,text);
  return {source:spec.source,file};
 });
}
function generate(compiler){
 const base=path.join(component,'asm/lx106'),mf=path.join(base,'manifest.json'),m=JSON.parse(fs.readFileSync(mf));
 const dir=path.join(root,'.build/opus-bands-blocks');fs.mkdirSync(dir,{recursive:true});
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const files=specs.map(spec=>{
  const entry=m.files.find(f=>f.source===spec.source),original=path.join(base,entry.asm);assert.equal(sourceHash(original),entry.asm_sha256_lf);
  const overlay='bands-blocks/'+spec.source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});
  fs.writeFileSync(dest,transform(fs.readFileSync(original,'utf8'),spec));
  const obj=path.join(dir,spec.fn+'.o'),control=path.join(dir,spec.fn+'.control.o');
  for(const [src,out] of [[dest,obj],[original,control]])run(compiler,['-mlongcalls','-x','assembler','-c',src,'-o',out]);
  const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
  const a=sizes(control),b=sizes(obj);assert.deepEqual(Object.keys(a),Object.keys(b));
  for(const s of Object.keys(a).filter(s=>a[s]&&!s.startsWith('.xt.')&&s!=='.text.'+spec.fn)){
   if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,control])),canonical(run(dump,['-dr','-j',s,obj])),s);
   else {assert.equal(a[s],b[s],s);for(const arg of ['-dr','-s'])assert.equal(run(dump,[arg,'-j',s,control]).split('\n').slice(3).join('\n'),run(dump,[arg,'-j',s,obj]).split('\n').slice(3).join('\n'),s);}
  }
  fs.writeFileSync(path.join(dir,spec.fn+'.disassembly.txt'),run(dump,['-dr','-j','.text.'+spec.fn,obj]));
  return {...spec,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:a,sections_after:b};
 });
 const report={schema:1,candidate:'bands-blocks-v1',base_manifest_sha256:sourceHash(mf),recipe_sha256_lf:sourceHash(__filename),files,additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-blocks.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={specs,transform,cModels,generate};
if(require.main===module)generate(process.argv[2]);
