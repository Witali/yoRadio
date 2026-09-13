// Best tell-inline parent + reuse cache[lo] after selecting the lower PVQ index.
// No new table, allocation, spill or arithmetic approximation. C is a host model.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const tell=require('./tell_inline.cjs'),{once}=require('./bands.cjs'),{canonical}=require('./disassembly.cjs');
const kind='cache-reuse',source='upstream/celt/bands.c';
const edits=[
 ['\tmov.n\ta10, a4\t# lo$230_710, q\n',''],
 ['\tbge\ta9, a8, .L60\t# _982, tmp892,',[
  '# Both cache[lo] in a11 and its address in a10 are already live.',
  '# hi choice retains the original load; lo skips one redundant flash L8UI.',
  '# At .Lcache_cost_ready all registers/memory/SAR match the parent exactly.',
  '\tblt\ta9, a8, .L80',
  '\tmov.n\ta8, a11',
  '\tj\t.Lcache_cost_ready'].join('\n')],
 ['\tl8ui\ta8, a10, 0\t# *_210, *_210\n','\tl8ui\ta8, a10, 0\t# *_210, *_210\n.Lcache_cost_ready:\n']
];
function transform(text){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/Lcache_cost_ready/);
 const body=text.match(/^quant_partition:[\s\S]*?(?=^\s*\.size\s+quant_partition,)/m)?.[0];assert.ok(body);
 let changed=body;for(const [a,b]of edits)changed=once(changed,a,b);
 assert.equal((body.match(/\.L60\b/g)||[]).length,2,'unexpected incoming edge');
 return text.replace(body,changed);
}
function cModels(){
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 return tell.cModels().map(model=>{
  let text=fs.readFileSync(model.file,'utf8');
  text=once(text,'#include "rate.h"\n','#include "rate.h"\n'+[
   'static int y_pulses_cost(const CELTMode *m,int band,int LM,int bits,int *cost) {',
   ' const unsigned char *cache=m->cache.bits+m->cache.index[(LM+1)*m->nbEBands+band];',
   ' int lo=0,hi=cache[0],i,low;',
   ' bits--;',
   ' for(i=0;i<LOG_MAX_PSEUDO;i++) {',
   '  int mid=(lo+hi+1)>>1;',
   '  if((int)cache[mid]>=bits) hi=mid; else lo=mid;',
   ' }',
   ' low=lo==0?-1:(int)cache[lo];',
   ' if(bits-low <= (int)cache[hi]-bits) { *cost=lo==0?0:low+1; return lo; }',
   ' *cost=pulses2bits(m,band,LM,hi); return hi;',
   '}',''].join('\n'));
  text=once(text,'      q = bits2pulses(m, i, LM, b);\n      curr_bits = pulses2bits(m, i, LM, q);','      q = y_pulses_cost(m, i, LM, b, &curr_bits);');
  const file=path.join(dir,'bands.model.c');fs.writeFileSync(file,text);return {source:model.source,file};
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
  const overlay='bands-'+kind+'/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,after);
  const a=path.join(dir,'control.o'),b=path.join(dir,'candidate.o');
  for(const [s,o]of [[original,a],[dest,b]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
  const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
  const sa=sizes(a),sb=sizes(b);assert.deepEqual(Object.keys(sa),Object.keys(sb));
  for(const s of Object.keys(sa).filter(s=>sa[s]&&!s.startsWith('.xt.')&&s!=='.text.quant_partition')){
   if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,b])),canonical(run(dump,['-dr','-j',s,a])),s);
   else {assert.equal(sb[s],sa[s],s);assert.equal(run(dump,['-s','-j',s,b]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,a]).split('\n').slice(3).join('\n'),s);}
  }
  fs.writeFileSync(path.join(dir,'disassembly.txt'),run(dump,['-dr',b]));
  return {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:sa,sections_after:sb};
 });
 const report={schema:1,candidate:'bands-cache-reuse-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),recipe_sha256_lf:sourceHash(__filename),parent_sha256_lf:sourceHash(parentFile),files,
  additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-cache-reuse.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,source,edits,transform,cModels,generate};if(require.main===module)generate(process.argv[2]);
