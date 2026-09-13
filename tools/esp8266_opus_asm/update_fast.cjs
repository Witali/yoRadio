// Selective no-normalize inline path, not the previously rejected whole
// ec_dec_update rewrite. All cold calls retain the pinned GCC implementation.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const {once}=require('./bands.cjs'),{canonical}=require('./disassembly.cjs');
const kind='update-fast',source='upstream/celt/bands.c';
const macroPath=path.join(__dirname,'update_fast.inc.s');
function transform(text){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/Y_OPUS_UPDATE_FAST/);
 let calls=0;
 for(const name of ['quant_partition','quant_all_bands']){
  const body=text.match(new RegExp('^'+name+':[\\s\\S]*?(?=^\\s*\\.size\\s+'+name+',)','m'))?.[0];assert.ok(body);
  const changed=once(body,'\tcall0\tec_dec_update\t\t#',
   '\tY_OPUS_UPDATE_FAST\t# No-normalize path; original cold call and ABI.');
  text=text.replace(body,changed);calls++;
 }
 assert.equal(calls,2);assert.doesNotMatch(text,/^\tcall0\tec_dec_update\t/gm);
 return fs.readFileSync(macroPath,'utf8').replace(/\r\n/g,'\n')+'\n'+text;
}
function helper(){
 return [
 '/* Host mirror; actual ASM is also interpreted independently in tests. */',
 'static void y_update_fast(ec_dec *ctx,unsigned fl,unsigned fh,unsigned ft) {',
 ' opus_uint32 s=ctx->ext*(ft-fh);',
 ' opus_uint32 rng=fl?ctx->ext*(fh-fl):ctx->rng-s;',
 ' if(rng>8388608u) {',
 '  ctx->val-=s; ctx->rng=rng;',
 ' } else ec_dec_update(ctx,fl,fh,ft);',
 '}',''].join('\n');
}
function cModels(){
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 let text=fs.readFileSync(path.join(component,source),'utf8').replace(/\r\n/g,'\n');
 assert.equal((text.match(/\bec_dec_update\(/g)||[]).length,2);
 text=text.replace(/\bec_dec_update\(/g,'y_update_fast(');
 text=once(text,'#include "rate.h"\n','#include "rate.h"\n'+helper());
 const file=path.join(dir,'bands.model.c');fs.writeFileSync(file,text);
 return [{source,file}];
}
function generate(compiler){
 const base=path.join(component,'asm/lx106'),mf=path.join(base,'manifest.json'),m=JSON.parse(fs.readFileSync(mf));
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const e=m.files.find(f=>f.source===source),original=path.join(base,e.asm);assert.equal(sourceHash(original),e.asm_sha256_lf);
 const overlay='bands-'+kind+'/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.writeFileSync(dest,transform(fs.readFileSync(original,'utf8')));
 const object=path.join(dir,'bands.o'),control=object+'.control',dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 for(const [s,o] of [[original,control],[dest,object]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
 const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const a=sizes(control),b=sizes(object);assert.deepEqual(Object.keys(a),Object.keys(b));
 for(const s of Object.keys(a).filter(s=>a[s]&&!s.startsWith('.xt.')&&!['.text.quant_partition','.text.quant_all_bands'].includes(s))){
  if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,control])),canonical(run(dump,['-dr','-j',s,object])),s);
  else {assert.equal(a[s],b[s],s);assert.equal(run(dump,['-s','-j',s,control]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,object]).split('\n').slice(3).join('\n'),s);}
 }
 fs.writeFileSync(path.join(dir,'disassembly.txt'),run(dump,['-dr',object]));
 const report={schema:1,candidate:'bands-'+kind+'-v1',base_manifest_sha256:sourceHash(mf),recipe_sha256_lf:sourceHash(__filename),
  dependencies:{'update_fast.inc.s':sourceHash(macroPath)},
  files:[{source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:a,sections_after:b}],
  fast_call_sites:2,additional_table_bytes:0,additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-'+kind+'.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,source,transform,helper,cModels,generate};if(require.main===module)generate(process.argv[2]);
