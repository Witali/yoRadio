// Placement-only derivative of exact small_div. Local literal words travel
// with the helper in the SDK's late .irom1.text flash segment. No arithmetic,
// caller ABI, RAM or protected GCC/C source changes.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const small=require('./small_div.cjs');
function transform(original){
 let text=small.transform(original);
 const prefix='\t.section .text.yoradio_opus_small_udiv,"ax",@progbits\n\t.literal_position\n\t.literal .Ly_small_table, yoradio_opus_small_div_table\n\t.literal .Ly_small_fallback, __udivsi3\n';
 assert.equal(text.split(prefix).length,2);
 text=text.replace(prefix,
  '\t.section .irom1.text,"ax",@progbits\n\t.balign 4\n.Ly_small_table:\n\t.word yoradio_opus_small_div_table\n.Ly_small_fallback:\n\t.word __udivsi3\n');
 const table='\t.section .rodata.yoradio_opus_small_div_table,"a",@progbits';
 assert.equal(text.split(table).length,2);
 text=text.replace(table,'\t.section .irom1.text,"ax",@progbits');
 return text;
}
function generate(compiler){
 require('./verify.cjs').verify('bands-small-div-asm');
 const base=path.join(component,'asm/lx106'),parentFile=path.join(base,'bands-small-div.json');
 const parent=JSON.parse(fs.readFileSync(parentFile)),source='upstream/celt/entdec.c';
 const original=fs.readFileSync(path.join(base,'gcc',source+'.s'),'utf8');
 const overlay='bands-small-div-tail/'+source+'.s',dest=path.join(base,overlay);
 fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,transform(original));
 const dir=path.join(root,'.build/opus-bands-small-div-tail');fs.mkdirSync(dir,{recursive:true});
 const object=path.join(dir,'candidate.o'),dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 run(compiler,['-mlongcalls','-x','assembler','-c',dest,'-o',object]);
 const sections=run(dump,['-h',object]);assert.match(sections,/\.irom1\.text/);
 assert.doesNotMatch(sections,/\.literal\.yoradio_opus_small_udiv|\.text\.yoradio_opus_small_udiv|\.rodata\.yoradio_opus_small_div_table/);
 fs.writeFileSync(path.join(dir,'candidate.disassembly.txt'),run(dump,['-dr',object]));
 const files=parent.files.slice(0,2).map(f=>({source:f.source,overlay:f.overlay,overlay_sha256_lf:f.overlay_sha256_lf}));
 files.push({source,overlay,overlay_sha256_lf:sourceHash(dest)});
 const manifest={schema:1,candidate:'bands-small-div-tail-v1',
  base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),parent_sha256_lf:sourceHash(parentFile),
  recipe_sha256_lf:sourceHash(__filename),small_recipe_sha256_lf:sourceHash(path.join(__dirname,'small_div.cjs')),
  files,changed_calls:3,additional_static_ram_bytes:0,scope:'same exact arithmetic; helper/literals/table in late flash; linked addresses must be audited'};
 fs.writeFileSync(path.join(base,'bands-small-div-tail.json'),JSON.stringify(manifest,null,2)+'\n');
 console.log(JSON.stringify(manifest));return manifest;
}
module.exports={transform,generate};if(require.main===module)generate(process.argv[2]);
