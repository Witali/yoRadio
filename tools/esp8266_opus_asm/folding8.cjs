// Exact table for N0 divisible by eight, not a restriction on valid modes.
// The unchanged sqrt call handles every other size. C firmware stays intact.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs'),{once}=require('./bands.cjs');
const censusFile=path.join(__dirname,'folding-census-results.json');
function coefficients(){
 const r=JSON.parse(fs.readFileSync(censusFile));assert.equal(r.passed,true);
 assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'profile_folding.cjs')));
 for(const [key,file]of [['source_sha256_lf','bands.c'],['math_source_sha256_lf','mathops.c'],['mode_source_sha256_lf','modes.c']])assert.equal(r[key],sourceHash(path.join(component,'upstream/celt',file)));
 assert.equal(r.all_values.length,512);assert.equal(r.fixed_point,true);
 assert.equal(r.config_sha256_lf,sourceHash(path.join(component,'upstream/include/config.h')));
 assert.equal(r.all_values[256],32767);assert.equal(r.all_values[511],32767);
 return Array.from({length:23},(_,i)=>r.all_values[i*8]);
}
const macro=`# Folding scale: a14=N0, a2=N0<<22 already formed by the caller.
# a2=result; a3/a4 are call0-volatile. a0/a1/a12..a15 and all memory preserved
# on the fast path. Existing caller stack is unchanged; no stores/extra frame.
# Unsigned bound rejects negative/large N0 before the word-aligned table load.
# Other sizes call the original celt_sqrt with exactly the original argument.
\t.macro Y_FOLD8
\t.global y_fold8_begin
y_fold8_begin:
\tmovi a3,176
\tbltu a3,a14,.Lfold8_slow\\@
\textui a3,a14,0,3
\tbnez a3,.Lfold8_slow\\@
\tsrli a3,a14,3
\tl32r a4,.Lfold8_table
\taddx4 a3,a3,a4
\tl32i a2,a3,0
\tj .Lfold8_done\\@
.Lfold8_slow\\@:
\tcall0 celt_sqrt
.Lfold8_done\\@:
\t.global y_fold8_end
y_fold8_end:
\t.endm
`;
function transform(text){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/Y_FOLD8|y_fold8_/);
 const needle='\tslli\ta2, a14, 22\t#,,\n\tcall0\tcelt_sqrt\t\t#';
 text=once(text,needle,'\tslli\ta2, a14, 22\t#,,\n\tY_FOLD8\t# Exact multiples-of-eight folding scale; fallback unchanged.');
 const prefix='\t.section\t.text.quant_band,"ax",@progbits\n\t.literal_position\n';
 text=once(text,prefix,prefix+'\t.literal .Lfold8_table, yoradio_opus_folding8_table\n');
 const data=['\t.section .rodata.yoradio_opus_folding8_table,"a",@progbits','\t.balign 4','\t.type yoradio_opus_folding8_table,@object','yoradio_opus_folding8_table:',...coefficients().map(v=>'\t.word '+v),'\t.size yoradio_opus_folding8_table,.-yoradio_opus_folding8_table',''].join('\n');
 return macro+'\n'+text+'\n# Values computed by the pinned original fixed-point sqrt.\n'+data;
}
function cModels(){
 const source='upstream/celt/bands.c',parent=require('./tell_inline.cjs').cModels().find(m=>m.source===source);assert.ok(parent);
 let text=fs.readFileSync(parent.file,'utf8').replace(/\r\n/g,'\n');
 const decl='static const opus_int32 y_fold8_table[23]={'+coefficients().join(',')+'};\n';
 text=once(text,'/* This function is responsible for encoding and decoding a band for the mono case. */',decl+'/* This function is responsible for encoding and decoding a band for the mono case. */');
 text=once(text,'         n = celt_sqrt(SHL32(EXTEND32(N0),22));','         n = (opus_uint32)N0<=176U && !(N0&7) ? y_fold8_table[N0>>3] : celt_sqrt(SHL32(EXTEND32(N0),22));');
 const dir=path.join(root,'.build/opus-bands-folding8');fs.mkdirSync(dir,{recursive:true});const file=path.join(dir,'bands.model.c');fs.writeFileSync(file,text);return [{source,file}];
}
function generate(compiler){
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const base=path.join(component,'asm/lx106'),pf=path.join(base,'bands-tell-inline.json'),parent=JSON.parse(fs.readFileSync(pf));
 const source='upstream/celt/bands.c',entry=parent.files.find(f=>f.source===source),original=path.join(base,entry.overlay);
 assert.equal(sourceHash(original),entry.overlay_sha256_lf);
 const overlay='bands-folding8/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,transform(fs.readFileSync(original,'utf8')));
 const dir=path.join(root,'.build/opus-bands-folding8');fs.mkdirSync(dir,{recursive:true});const object=path.join(dir,'candidate.o');
 run(compiler,['-mlongcalls','-x','assembler','-c',dest,'-o',object]);
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');fs.writeFileSync(path.join(dir,'candidate.disassembly.txt'),run(dump,['-dr',object]));
 const files=parent.files.map(f=>f.source===source?{source,overlay,overlay_sha256_lf:sourceHash(dest)}:{source:f.source,overlay:f.overlay,overlay_sha256_lf:f.overlay_sha256_lf});
 const report={schema:1,candidate:'bands-folding8-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),parent_sha256_lf:sourceHash(pf),recipe_sha256_lf:sourceHash(__filename),census_sha256_lf:sourceHash(censusFile),files,table_bytes:92,additional_static_ram_bytes:0,stack_change_bytes:0,changed_calls:1,scope:'Exact fixed-point sqrt coefficients at one dynamic folding site; constant N2 site and all other sqrt calls unchanged; physical speed required'};
 fs.writeFileSync(path.join(base,'bands-folding8.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));return report;
}
module.exports={macro,coefficients,transform,cModels,generate};if(require.main===module)generate(process.argv[2]);
