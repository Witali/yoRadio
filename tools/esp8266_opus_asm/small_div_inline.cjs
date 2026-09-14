// Inline the already proved exact arithmetic; remove only the helper call.
// The original GCC snapshot, normal ROM divisions and C fallback stay intact.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const small=require('./small_div.cjs');
const begin='yoradio_opus_small_udiv:\n',end='.Ly_small_ret:\n';
const arithmetic=small.helper.slice(small.helper.indexOf(begin)+begin.length,small.helper.indexOf(end));
assert.ok(arithmetic.startsWith('\tmovi a4,256\n'));
const macro=`# Exact inline n/d, a2=n,a3=d -> a2. Same call0 volatile registers/SAR.
# No stores or new stack. a1/a12..a15 preserved. Fast path leaves a0 alone;
# both enclosing GCC functions already save/restore a0 for remaining calls.
# d=0/>256 calls original ROM with original arguments; no bitrate restriction.
# The one shared table is flash-only, 129 aligned words, never copied to RAM.
\t.macro Y_OPUS_SMALL_DIV id
\t.global y_div_inline_\\id\\()_begin
y_div_inline_\\id\\()_begin:
${arithmetic.replaceAll('.Ly_small_slow','.Ly_inline_slow\\@').replaceAll('.Ly_small_ret','.Ly_inline_done\\@').replaceAll('.Ly_small_table','.Ly_inline_table')}\tj .Ly_inline_done\\@
.Ly_inline_slow\\@:
\tcall0 __udivsi3
.Ly_inline_done\\@:
\t.global y_div_inline_\\id\\()_end
y_div_inline_\\id\\()_end:
\t.endm
`;
const tableText=small.helper.slice(small.helper.indexOf('\t.section .rodata.yoradio_opus_small_div_table'));
function transform(original){
 let text=original.replace(/\r\n/g,'\n'),changes=0;
 assert.doesNotMatch(text,/Y_OPUS_SMALL_DIV|y_div_inline_/);
 const prefix='\t.section\t.text.ec_decode,"ax",@progbits\n\t.literal_position\n';
 assert.equal(text.split(prefix).length,2);
 text=text.replace(prefix,prefix+'\t.literal .Ly_inline_table, yoradio_opus_small_div_table\n');
 text=text.replace(/^(ec_decode|ec_dec_uint):[\s\S]*?(?=^\s*\.size\s+\1,)/gm,body=>{
  const name=body.startsWith('ec_decode:')?'ec_decode':'ec_dec_uint';let calls=0;
  assert.match(body,/s32i\.n\s+a0, sp,/);assert.match(body,/l32i\.n\s+a0, sp,/);
  const result=body.replace(/\bcall0\s+__udivsi3\b/g,call=>calls++%2?call:'Y_OPUS_SMALL_DIV '+changes++);
  assert.equal(calls,name==='ec_decode'?2:4);return result;
 });assert.equal(changes,3);
 return macro+'\n'+text+'\n# One shared exact reciprocal table.\n'+tableText;
}
function generate(compiler){
 require('./verify.cjs').verify('bands-small-div-asm');
 const base=path.join(component,'asm/lx106'),parentFile=path.join(base,'bands-tell-inline.json'),parent=JSON.parse(fs.readFileSync(parentFile));
 const source='upstream/celt/entdec.c',original=fs.readFileSync(path.join(base,'gcc',source+'.s'),'utf8');
 const overlay='bands-small-div-inline/'+source+'.s',dest=path.join(base,overlay);
 fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,transform(original));
 const dir=path.join(root,'.build/opus-bands-small-div-inline');fs.mkdirSync(dir,{recursive:true});
 const object=path.join(dir,'candidate.o'),dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 run(compiler,['-mlongcalls','-x','assembler','-c',dest,'-o',object]);
 const sections=run(dump,['-h',object]),disassembly=run(dump,['-dr',object]);
 assert.doesNotMatch(sections,/\.text\.yoradio_opus_small_udiv/);
 assert.equal((disassembly.match(/\bmul16u\b/g)||[]).length,12);
 fs.writeFileSync(path.join(dir,'candidate.disassembly.txt'),disassembly);
 const files=parent.files.map(f=>({source:f.source,overlay:f.overlay,overlay_sha256_lf:f.overlay_sha256_lf}));
 files.push({source,overlay,overlay_sha256_lf:sourceHash(dest)});
 const report={schema:1,candidate:'bands-small-div-inline-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),
  parent_sha256_lf:sourceHash(parentFile),recipe_sha256_lf:sourceHash(__filename),small_recipe_sha256_lf:sourceHash(path.join(__dirname,'small_div.cjs')),
  files,expanded_calls:3,table_bytes:516,additional_static_ram_bytes:0,stack_change_bytes:0,
  scope:'Exact small-div arithmetic in three existing call0 sites; no helper CALL/RET on fast path; linked proof and board speed required'};
 fs.writeFileSync(path.join(base,'bands-small-div-inline.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({generated:overlay,expanded_calls:3,table_bytes:516}));return report;
}
module.exports={macro,arithmetic,tableText,transform,generate};if(require.main===module)generate(process.argv[2]);
