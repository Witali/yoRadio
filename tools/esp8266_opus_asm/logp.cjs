// Shared ec_dec_bit_logp shrink-wrap over the best tell-inline parent.
// No caller duplication: fast return uses only caller-saved registers.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const tell=require('./tell_inline.cjs'),{canonical}=require('./disassembly.cjs');
const kind='logp',source='upstream/celt/entdec.c',include=path.join(__dirname,'logp_prefix.inc.s');
const cold='\tl32i.n\ta8, a2, 20\t# _this_6(D)->nbits_total, _this_6(D)->nbits_total';
const body=text=>text.match(/^ec_dec_bit_logp:[\s\S]*?(?=^\s*\.size\s+ec_dec_bit_logp,)/m)[0];
const baseline=()=>fs.readFileSync(path.join(component,'asm/lx106/gcc/'+source+'.s'),'utf8').replace(/\r\n/g,'\n');
function transform(text){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/Llogp_/);
 const b=body(text),at=b.indexOf(cold);assert.ok(at>0);assert.equal(b.indexOf(cold,at+1),-1);
 return text.replace(b,'ec_dec_bit_logp:\n'+fs.readFileSync(include,'utf8').replace(/\r\n/g,'\n')+b.slice(at));
}
function cModels(){
 const dir=path.join(root,'.build/opus-bands-logp');fs.mkdirSync(dir,{recursive:true});
 const asm=transform(baseline());
 const text=fs.readFileSync(path.join(component,source),'utf8').replace(/\r\n/g,'\n');
 const old=text.match(/int ec_dec_bit_logp\(ec_dec \*_this,unsigned _logp\)\{[\s\S]*?^\}/m)[0];
 const file=path.join(dir,'entdec.model.c');
 fs.writeFileSync(file,text.replace(old,require('./logp_model.cjs').cModel(asm)));
 return [...tell.cModels(),{source,file}];
}
function generate(compiler){
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const base=path.join(component,'asm/lx106'),pf=path.join(base,'bands-tell-inline.json'),parent=JSON.parse(fs.readFileSync(pf));
 const manifest=JSON.parse(fs.readFileSync(path.join(base,'manifest.json'))),entry=manifest.files.find(f=>f.source===source);
 const original=path.join(base,entry.asm);assert.equal(sourceHash(original),entry.asm_sha256_lf);
 const dir=path.join(root,'.build/opus-bands-logp');fs.mkdirSync(dir,{recursive:true});
 const overlay='bands-logp/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.writeFileSync(dest,transform(baseline()));
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const a=path.join(dir,'control.o'),b=path.join(dir,'candidate.o');
 for(const [s,o]of [[original,a],[dest,b]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
 const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const sa=sizes(a),sb=sizes(b);assert.deepEqual(Object.keys(sa),Object.keys(sb));
 for(const s of Object.keys(sa).filter(s=>sa[s]&&!s.startsWith('.xt.')&&s!=='.text.ec_dec_bit_logp')){
  if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,b])),canonical(run(dump,['-dr','-j',s,a])),s);
  else {assert.equal(sb[s],sa[s],s);assert.equal(run(dump,['-s','-j',s,b]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,a]).split('\n').slice(3).join('\n'),s);}
 }
 for(const [name,o]of [['control',a],['candidate',b]])fs.writeFileSync(path.join(dir,name+'.disassembly.txt'),run(dump,['-dr',o]));
 const files=[...parent.files.map(e=>({source:e.source,overlay:e.overlay,overlay_sha256_lf:e.overlay_sha256_lf})),
  {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:sa,sections_after:sb}];
 const report={schema:1,candidate:'bands-logp-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),
  recipe_sha256_lf:sourceHash(__filename),parent_sha256_lf:sourceHash(pf),dependencies:{'logp_prefix.inc.s':sourceHash(include)},files,
  changed_function:'ec_dec_bit_logp',additional_static_ram_bytes:0,stack_before_bytes:16,stack_fast_bytes:0,stack_cold_bytes:16,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-logp.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,source,cold,body,baseline,transform,cModels,generate};if(require.main===module)generate(process.argv[2]);
