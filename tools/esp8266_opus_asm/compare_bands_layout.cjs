// Reassemble reviewed sources before comparing: do not trust stale object files.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash,run}=require('./export.cjs');
const {verify}=require('./verify.cjs'),{canonical}=require('./disassembly.cjs');
function compare(compiler){
 verify('bands-intensity-asm');verify('bands-combined-asm');
 const dir=path.join(root,'.build/opus-bands-layout-audit');fs.mkdirSync(dir,{recursive:true});
 const bin=path.dirname(compiler),dump=path.join(bin,'xtensa-lx106-elf-objdump.exe');
 const values=['intensity','combined'].map(kind=>{
  const src=path.join(component,'asm/lx106/bands-'+kind+'/upstream/celt/bands.c.s');
  const obj=path.join(dir,kind+'.o');run(compiler,['-mlongcalls','-x','assembler','-c',src,'-o',obj]);
  const instructions=canonical(run(dump,['-dr','-j','.text.quant_all_bands',obj]));
  return {kind,source_sha256_lf:sourceHash(src),object_sha256:hash(fs.readFileSync(obj)),instructions};
 });assert.deepEqual(values[0].instructions,values[1].instructions);
 const variants=['esp8266-opus-functions-control-v2','esp8266-opus-bands-intensity-v1','esp8266-opus-bands-blocks-v1','esp8266-opus-bands-combined-v1'];
 const symbols=variants.map(variant=>{
  const data=run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',path.join(root,'.build',variant,'yoradio_esp8266_helix_native.elf')]);
  return {variant,functions:Object.fromEntries([...data.matchAll(/^([0-9a-f]+) ([0-9a-f]+) [Tt] (quant_all_bands|quant_band|alg_unquant|decode_pulses)$/gm)].map(m=>[m[3],{address:m[1],bytes:parseInt(m[2],16)}]))};
 });
 const report={scope:'Equivalent quant_all_bands instruction semantics/branch graph; layout/cache explanation is a hypothesis, not measured causation',equivalent:true,instructions:values[0].instructions.length,sources:values.map(({instructions,...v})=>v),symbols};
 fs.writeFileSync(path.join(root,'firmware/development/esp8266-opus-bands-combined-v1/layout.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
if(require.main===module)compare(process.argv[2]);
