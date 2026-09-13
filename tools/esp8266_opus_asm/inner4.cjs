// Selective four-element expansion of the squared inner product in CELT
// renormalise_vector. Best tell-inline parent; no global compiler unrolling.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const tell=require('./tell_inline.cjs'),{once}=require('./bands.cjs'),{canonical}=require('./disassembly.cjs');
const kind='inner4',source='upstream/celt/vq.c';
const include=path.join(__dirname,'inner4_loop.inc.s');
const scalarStart='.L182:\n';
const scalarEnd='\tbne\ta3, a6, .L182\t# _102, ivtmp$303,\n';
function transform(text){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/Linner4_/);
 const body=text.match(/^renormalise_vector:[\s\S]*?(?=^\s*\.size\s+renormalise_vector,)/m)?.[0];assert.ok(body);
 let changed=once(body,scalarStart,fs.readFileSync(include,'utf8').replace(/\r\n/g,'\n')+'\n'+scalarStart);
 changed=once(changed,scalarEnd,scalarEnd+'.Linner4_done:\n');
 return text.replace(body,changed);
}
function cModels(){
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 let text=fs.readFileSync(path.join(component,source),'utf8').replace(/\r\n/g,'\n');
 const helper=[
  '/* Host mirror: exact operation order, unsigned accumulator matches ADD32. */',
  'static opus_val32 y_inner4_square(const opus_val16 *x, int N) {',
  ' opus_uint32 xy=0; int i=0;',
  ' if(N>=8) for(;i<=N-4;i+=4) {',
  '  xy+=(opus_uint32)MULT16_16(x[i],x[i]);',
  '  xy+=(opus_uint32)MULT16_16(x[i+1],x[i+1]);',
  '  xy+=(opus_uint32)MULT16_16(x[i+2],x[i+2]);',
  '  xy+=(opus_uint32)MULT16_16(x[i+3],x[i+3]);',
  ' }',
  ' for(;i<N;i++) xy+=(opus_uint32)MULT16_16(x[i],x[i]);',
  ' return (opus_val32)xy;',
  '}', ''
 ].join('\n');
 text=once(text,'#ifndef OVERRIDE_renormalise_vector\n','#ifndef OVERRIDE_renormalise_vector\n'+helper);
 text=once(text,'   E = EPSILON + celt_inner_prod(X, X, N, arch);','   E = ADD32(EPSILON, y_inner4_square(X, N));');
 const file=path.join(dir,'vq.model.c');fs.writeFileSync(file,text);
 return [...tell.cModels(),{source,file}];
}
function generate(compiler){
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const base=path.join(component,'asm/lx106'),parentFile=path.join(base,'bands-tell-inline.json'),parent=JSON.parse(fs.readFileSync(parentFile));
 const manifest=JSON.parse(fs.readFileSync(path.join(base,'manifest.json'))),entry=manifest.files.find(f=>f.source===source);
 const original=path.join(base,entry.asm);assert.equal(sourceHash(original),entry.asm_sha256_lf);
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const overlay='bands-'+kind+'/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.writeFileSync(dest,transform(fs.readFileSync(original,'utf8')));
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const a=path.join(dir,'control.o'),b=path.join(dir,'candidate.o');
 for(const [s,o]of [[original,a],[dest,b]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
 const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const sa=sizes(a),sb=sizes(b);assert.deepEqual(Object.keys(sa),Object.keys(sb));
 for(const s of Object.keys(sa).filter(s=>sa[s]&&!s.startsWith('.xt.')&&s!=='.text.renormalise_vector')){
  if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,b])),canonical(run(dump,['-dr','-j',s,a])),s);
  else {assert.equal(sb[s],sa[s],s);assert.equal(run(dump,['-s','-j',s,b]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,a]).split('\n').slice(3).join('\n'),s);}
 }
 for(const [name,o]of [['control',a],['candidate',b]])fs.writeFileSync(path.join(dir,name+'.disassembly.txt'),run(dump,['-dr',o]));
 const files=[...parent.files.map(e=>({source:e.source,overlay:e.overlay,overlay_sha256_lf:e.overlay_sha256_lf})),
  {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:sa,sections_after:sb}];
 const report={schema:1,candidate:'bands-inner4-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),
  recipe_sha256_lf:sourceHash(__filename),parent_sha256_lf:sourceHash(parentFile),dependencies:{'inner4_loop.inc.s':sourceHash(include)},files,
  unroll_elements:4,threshold_elements:8,changed_function:'renormalise_vector',additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-inner4.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,source,scalarStart,scalarEnd,transform,cModels,generate};if(require.main===module)generate(process.argv[2]);
