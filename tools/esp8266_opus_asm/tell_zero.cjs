// Decoder-only mono theta with qn=1 consumes no entropy. Remove T(ec)-T(ec),
// not any entropy operation. Preserve all other branches, tables and stack.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const tell=require('./tell_inline.cjs'),{once}=require('./bands.cjs'),{canonical}=require('./disassembly.cjs');
const kind='tell-zero',source='upstream/celt/bands.c';
const start='# @OPUS@\\upstream\\celt\\bands.c:760:    tell = ec_tell_frac(ec);\n';
function oldBlock(text){
 const body=text.match(/^quant_partition:[\s\S]*?(?=^\s*\.size\s+quant_partition,)/m)?.[0];assert.ok(body);
 const at=body.indexOf(start),end=body.indexOf('.L27:\n',at);assert.ok(at>=0&&end>at);
 const block=body.slice(at,end);
 const lines=block.split('\n').map(l=>l.split('#')[0].trim()).filter(Boolean);
 assert.deepEqual(lines,[
  'l32i.n\ta2, sp, 20','Y_OPUS_TELL_FRAC','mov.n\ta11, a2',
  'l32i.n\ta2, sp, 20','s32i\ta11, sp, 72','Y_OPUS_TELL_FRAC',
  'l32i\ta11, sp, 72','sub\ta11, a2, a11','sub\ta10, a14, a11','j\t.L29']);
 assert.match(body.slice(at-190,at),/bnez\.n\ta7, \.L28/);
 return block;
}
function replacement(){return [
 '# Exact decoder-only mono theta qn=1: entropy state is unchanged.',
 '# ec_tell_frac is read-only, so qalloc=T(ec)-T(ec)=0; b remains a14.',
 '# Output a11=0, a10=b. Preserve a0/a1/a7..a9/a12..a15 and all memory.',
 '# a2..a6/SAR are dead at .L29; its loads/SSL redefine them before use.',
 '# Stack slot sp+72 was only a temporary tell spill in this removed block.',
 '# Stereo inverse-bit entropy, qn>1, encoder paths and recursion are untouched.',
 '\tmovi.n\ta11, 0','\tmov.n\ta10, a14','\tj\t.L29',''].join('\n');}
function transform(text){text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/qalloc=T\(ec\)-T\(ec\)=0/);return once(text,oldBlock(text),replacement());}
function cModels(counted=false){
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 return tell.cModels().map(model=>{
  let text=fs.readFileSync(model.file,'utf8');
  const body=text.match(/^static void compute_theta\([\s\S]*?^}/m)?.[0];assert.ok(body);
  let changed=once(body,'   tell = y_inline_tell_frac(ec);','   const int y_skip_tell = !encode && !stereo && qn == 1;\n'+(counted?'   y_total++; if (y_skip_tell) y_skipped++;\n':'')+'   tell = y_skip_tell ? 0 : y_inline_tell_frac(ec);');
  changed=once(changed,'   qalloc = y_inline_tell_frac(ec) - tell;','   qalloc = y_skip_tell ? 0 : y_inline_tell_frac(ec) - tell;');
  text=text.replace(body,changed);
  if(counted)text=once(text,'#include "rate.h"\n','#include "rate.h"\n#include <stdio.h>\nstatic unsigned long y_total,y_skipped;\n__attribute__((destructor)) static void y_count_report(void){fprintf(stderr,"TELL_ZERO %lu %lu\\n",y_total,y_skipped);}\n');
  const file=path.join(dir,counted?'bands.counted.c':'bands.model.c');fs.writeFileSync(file,text);return {source:model.source,file};
 });
}
function generate(compiler){
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const base=path.join(component,'asm/lx106'),parentFile=path.join(base,'bands-tell-inline.json'),parent=JSON.parse(fs.readFileSync(parentFile));
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const files=parent.files.map(e=>{
  if(e.source!==source)return {source:e.source,overlay:e.overlay,overlay_sha256_lf:e.overlay_sha256_lf};
  const original=path.join(base,e.overlay),before=fs.readFileSync(original,'utf8').replace(/\r\n/g,'\n'),after=transform(before);
  assert.equal(after.replace(replacement(),oldBlock(before)),before);
  // Screened-out experiment: never create a selectable firmware overlay.
  const overlay='bands-'+kind+'/'+source+'.s',dest=path.join(dir,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,after);
  const a=path.join(dir,'control.o'),b=path.join(dir,'candidate.o');
  for(const [s,o]of [[original,a],[dest,b]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
  const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
  const sa=sizes(a),sb=sizes(b);assert.deepEqual(Object.keys(sa),Object.keys(sb));
  for(const s of Object.keys(sa).filter(s=>sa[s]&&!s.startsWith('.xt.')&&s!=='.text.quant_partition')){
   assert.equal(sb[s],sa[s],s);
   if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,b])),canonical(run(dump,['-dr','-j',s,a])),s);
   else assert.equal(run(dump,['-s','-j',s,b]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,a]).split('\n').slice(3).join('\n'),s);
  }
  assert.ok(sb['.text.quant_partition']<sa['.text.quant_partition']);
  fs.writeFileSync(path.join(dir,'disassembly.txt'),run(dump,['-dr',b]));
  return {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:sa,sections_after:sb};
 });
 const report={schema:1,candidate:'bands-tell-zero-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),recipe_sha256_lf:sourceHash(__filename),parent_sha256_lf:sourceHash(parentFile),files,removed_inline_tell_sites:2,additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(dir,'bands-tell-zero.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,source,oldBlock,replacement,transform,cModels,generate};if(require.main===module)generate(process.argv[2]);
