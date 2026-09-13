// Exact ASM lookup, independently selectable from intensity/block experiments.
// Derived tables retain upstream Xiph licensing; no upstream C or baseline edits.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const {reference}=require('./pulse_inverse.cjs'),{once}=require('./bands.cjs');
const {canonical}=require('./disassembly.cjs');
const kind='pulse-lookup',sources=['upstream/celt/bands.c','upstream/celt/modes.c'];
function tables(){
 const src=fs.readFileSync(path.join(component,'upstream/celt/static_modes_fixed.h'),'utf8');
 const array=(name,n)=>{const m=src.match(new RegExp('\\b'+name+'\\['+n+'\\]\\s*=\\s*\\{([^}]+)\\}'));assert.ok(m);const a=m[1].split(',').map(s=>s.trim()).filter(Boolean).map(Number);assert.equal(a.length,n);assert.ok(a.every(Number.isInteger));return a;};
 const index=array('cache_index50',105),bits=array('cache_bits50',392),offsets=[...new Set(index.filter(x=>x>=0))].sort((a,b)=>a-b);
 assert.equal(offsets.length,23);const map=Array(392).fill(255),rows=offsets.map((o,r)=>{map[o]=r;return Array.from({length:260},(_,b)=>b<=256?reference(bits.slice(o),b):0);});
 const pack=a=>Array.from({length:a.length/4},(_,i)=>(a[4*i]|a[4*i+1]<<8|a[4*i+2]<<16|a[4*i+3]<<24)>>>0);
 return {bits,index,offsets,map,rows,mapWords:pack(map),inverseWords:pack(rows.flat())};
}
function transform(text,source){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/ASM pulse lookup/);
 if(source.endsWith('/modes.c'))return text+'\n# Address-only alias of the original immutable table; no copied data.\n\t.global y_opus_cache_bits50\n\t.set y_opus_cache_bits50, cache_bits50\n';
 assert.equal(source,sources[0]);
 text=once(text,'\t.literal .LC2, -16384\n','\t.literal .LC2, -16384\n'+
  '\t.literal .Lasm_pulse_base, y_opus_cache_bits50\n\t.literal .Lasm_pulse_map, .Lasm_pulse_map_data\n\t.literal .Lasm_pulse_inverse, .Lasm_pulse_inverse_data\n');
 text=once(text,'.L22:\n','.L22:\n'+fs.readFileSync(path.join(__dirname,'pulse_lookup.inc.s'),'utf8').replace(/\r\n/g,'\n'));
 const t=tables();
 for(const [name,data] of [['map',t.mapWords],['inverse',t.inverseWords]])text+='\n# Derived from cache_bits50; upstream/COPYING applies.\n\t.section .rodata.y_pulse_'+name+',"a",@progbits\n\t.balign 4\n.Lasm_pulse_'+name+'_data:\n'+data.map(v=>'\t.word 0x'+v.toString(16).padStart(8,'0')).join('\n')+'\n';
 return text;
}
function cModels(){
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const t=tables(),def=(name,data)=>'static const unsigned '+name+'[] = {'+data.map(v=>v+'u').join(',')+'};\n';
 const helper='/* Semantic mirror of the inline LX106 lookup; fallback returns -1. */\n#include <stdint.h>\n'+
  'extern const unsigned char y_opus_cache_bits50[392];\n'+def('y_pulse_map',t.mapWords)+def('y_pulse_inverse',t.inverseWords)+
  'static int y_pulse_lookup(const unsigned char *cache, int bits) {\n'+
  ' uintptr_t offset=(uintptr_t)cache-(uintptr_t)y_opus_cache_bits50;\n'+
  ' if(offset>=392 || (unsigned)bits>256) return -1;\n'+
  ' unsigned row=(y_pulse_map[offset>>2]>>((offset&3)*8))&255;\n'+
  ' if(row==255) return -1;\n'+
  ' return (y_pulse_inverse[row*65+((unsigned)bits>>2)]>>((bits&3)*8))&255;\n}\n';
 fs.writeFileSync(path.join(dir,'lookup.model.h'),helper);
 fs.writeFileSync(path.join(dir,'lookup.testdata.h'),'/* Xiph cache_bits50 test data; upstream/COPYING applies. */\n'+
  'const unsigned char y_opus_cache_bits50[392] = {'+t.bits.join(',')+'};\n'+def('y_row_offsets',t.offsets));
 return sources.map(source=>{
  let text=fs.readFileSync(path.join(component,source),'utf8').replace(/\r\n/g,'\n');
  if(source.endsWith('/modes.c'))text+='\nextern const unsigned char y_opus_cache_bits50[392] __attribute__((alias("cache_bits50")));\n';
  else {
   text=once(text,'#include "rate.h"\n','#include "rate.h"\n#include "lookup.model.h"\n');
   text=once(text,'      q = bits2pulses(m, i, LM, b);',
    '      q = y_pulse_lookup(cache, b);\n      if (q < 0) q = bits2pulses(m, i, LM, b);');
  }
  const file=path.join(dir,path.basename(source)+'.model.c');fs.writeFileSync(file,text);return {source,file};
 });
}
function generate(compiler){
 const base=path.join(component,'asm/lx106'),mf=path.join(base,'manifest.json'),m=JSON.parse(fs.readFileSync(mf));
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const files=sources.map(source=>{
  const e=m.files.find(f=>f.source===source),original=path.join(base,e.asm);assert.equal(sourceHash(original),e.asm_sha256_lf);
  const overlay='bands-'+kind+'/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,transform(fs.readFileSync(original,'utf8'),source));
  const object=path.join(dir,path.basename(source)+'.o'),control=object+'.control';
  for(const [s,o] of [[original,control],[dest,object]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
  const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
  const a=sizes(control),b=sizes(object);
  for(const s of Object.keys(a).filter(s=>a[s]&&!s.startsWith('.xt.')&&!(source===sources[0]&&['.text.quant_partition','.literal.quant_partition'].includes(s)))){
   if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,control])),canonical(run(dump,['-dr','-j',s,object])),s);
   else {assert.equal(a[s],b[s],s);assert.equal(run(dump,['-s','-j',s,control]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,object]).split('\n').slice(3).join('\n'),s);}
  }
  fs.writeFileSync(object+'.dump',run(dump,['-dr',object]));return {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:a,sections_after:b};
 });
 const report={schema:1,candidate:'bands-'+kind+'-v1',base_manifest_sha256:sourceHash(mf),recipe_sha256_lf:sourceHash(__filename),
  dependencies:Object.fromEntries(['pulse_lookup.inc.s','pulse_inverse.cjs'].map(f=>[f,sourceHash(path.join(__dirname,f))])),files,
  table_flash_bytes:6372,additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-'+kind+'.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,sources,tables,transform,cModels,generate};if(require.main===module)generate(process.argv[2]);
