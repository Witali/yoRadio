// Pure placement overlay on the best tell-inline. The zero bytes are before
// the entry symbol, never instructions on the execution path. No new tables,
// arithmetic, stack slots or RAM. Final link addresses/relaxation need auditing.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const {once}=require('./bands.cjs'),{canonical}=require('./disassembly.cjs');
const source='upstream/celt/bands.c',symbol='quant_partition',choices=[32,128];
function sectionBytes(file,name){
 const b=fs.readFileSync(file);assert.equal(b.subarray(0,6).toString('hex'),'7f454c460101');
 const start=b.readUInt32LE(32),stride=b.readUInt16LE(46),count=b.readUInt16LE(48);
 const names=start+b.readUInt16LE(50)*stride,strings=b.readUInt32LE(names+16);
 for(let i=0;i<count;i++){
  const p=start+i*stride,n=strings+b.readUInt32LE(p);
  if(b.toString('utf8',n,b.indexOf(0,n))!==name)continue;
  assert.ok([1,7].includes(b.readUInt32LE(p+4)),'Expected PROGBITS/NOTE '+name);
  return Buffer.from(b.subarray(b.readUInt32LE(p+16),b.readUInt32LE(p+16)+b.readUInt32LE(p+20)));
 }
 throw Error('Missing ELF section '+name);
}
function normalizeLiteral(data,relocations,pad){
 const b=Buffer.from(data),changed=[];
 for(const m of relocations.matchAll(/^([0-9a-f]+)\s+R_XTENSA_32\s+\.text\.quant_partition\s*$/gm)){
  const at=parseInt(m[1],16);assert.equal(at%4,0);
  // REL addend is in the literal word. Only pointers to the moved entry
  // may differ; numeric constants and all other relocations stay exact.
  assert.equal(b.readUInt32LE(at),pad,'Unexpected relocated entry addend');
  b.writeUInt32LE(0,at);changed.push(at);
 }
 return {bytes:b,changed};
}
function prefix(bytes){assert.ok(choices.includes(bytes));return [
 '# Layout-only experiment: '+bytes+' unreachable bytes BEFORE quant_partition.',
 '# ABI/registers/SAR/stack and every instruction after the symbol are unchanged.',
 '# This is not a cache-line-size claim. All later linked addresses may move.',
 '\t.space '+bytes+', 0',''].join('\n');}
function transform(text,bytes){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/Layout-only experiment/);
 assert.match(text,/Y_OPUS_TELL_FRAC/);return once(text,'\n'+symbol+':\n','\n'+prefix(bytes)+symbol+':\n');
}
function generate(compiler,bytes){
 assert.ok(choices.includes(bytes));require('./verify.cjs').verify('bands-tell-inline-asm');
 const base=path.join(component,'asm/lx106'),parentPath=path.join(base,'bands-tell-inline.json'),parent=JSON.parse(fs.readFileSync(parentPath));
 const kind='layout'+bytes,dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe'),nm=path.join(path.dirname(compiler),'xtensa-lx106-elf-nm.exe');
 const files=parent.files.map(e=>{
  if(e.source!==source)return {source:e.source,overlay:e.overlay,overlay_sha256_lf:e.overlay_sha256_lf};
  const original=path.join(base,e.overlay),overlay='bands-'+kind+'/'+source+'.s',dest=path.join(base,overlay);
  fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,transform(fs.readFileSync(original,'utf8'),bytes));
  const object=path.join(dir,'bands.o'),control=object+'.tell';
  for(const [s,o] of [[original,control],[dest,object]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
  const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
  const a=sizes(control),b=sizes(object);assert.deepEqual(Object.keys(a),Object.keys(b));
  const sym=p=>{const m=run(nm,['-S',p]).match(new RegExp('^([0-9a-f]+)\\s+([0-9a-f]+)\\s+\\S\\s+'+symbol+'$','m'));assert.ok(m);return {address:parseInt(m[1],16),bytes:parseInt(m[2],16)};};
  const sa=sym(control),sb=sym(object);assert.equal(sb.address-sa.address,bytes);assert.equal(sb.bytes,sa.bytes);
  const relocatedLiterals=[];
  for(const s of Object.keys(a).filter(s=>a[s]&&!s.startsWith('.xt.'))){
   if(s.startsWith('.text.')){
    const opts=s==='.text.'+symbol?['--start-address='+sa.address,'--stop-address='+(sa.address+sa.bytes)]:[];
    const optsB=s==='.text.'+symbol?['--start-address='+sb.address,'--stop-address='+(sb.address+sb.bytes)]:[];
    const graph=(p,opts)=>canonical(run(dump,['-dr','-j',s,...opts,p])).map(op=>
     s==='.text.'+symbol&&op==='call0 .text.'+symbol?'call0 instruction:0':op);
    assert.deepEqual(graph(control,opts),graph(object,optsB),s);
   }else{
    assert.equal(b[s],a[s],s);
    const ra=run(dump,['-r','-j',s,control]).split('\n').slice(3).join('\n'),rb=run(dump,['-r','-j',s,object]).split('\n').slice(3).join('\n');
    assert.equal(rb,ra,'Literal relocation targets changed: '+s);
    const na=normalizeLiteral(sectionBytes(control,s),ra,0),nb=normalizeLiteral(sectionBytes(object,s),rb,bytes);
    assert.deepEqual(nb.changed,na.changed);assert.deepEqual(nb.bytes,na.bytes,s);
    for(const offset of nb.changed)relocatedLiterals.push({section:s,offset,delta:bytes});
   }
  }
  assert.equal(b['.text.'+symbol]-a['.text.'+symbol],bytes);
  fs.writeFileSync(path.join(dir,'disassembly.txt'),run(dump,['-dr',object]));
  return {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:a,sections_after:b,entry_before:sa,entry_after:sb,relocated_literals:relocatedLiterals,object_instruction_graph_exact:true};
 });
 const report={schema:1,candidate:'bands-'+kind+'-v1',pad_bytes:bytes,pad_before:symbol,base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),
  recipe_sha256_lf:sourceHash(__filename),parent_sha256_lf:sourceHash(parentPath),files,additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-'+kind+'.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({candidate:report.candidate,entry:files[0].entry_after,graph_exact:true}));return report;
}
module.exports={choices,source,symbol,prefix,transform,generate,sectionBytes,normalizeLiteral};if(require.main===module)generate(process.argv[2],Number(process.argv[3]));
