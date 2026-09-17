// Relink the accepted frozen ASM chain into ordinary radio, not a benchmark.
// No arithmetic edits: same assembly sources, rebased symbols/literal only.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {root,hash,sourceHash,run}=require('./export.cjs');
const f=require('./frozen_reloads.cjs'),accepted=require('./ebands_final.cjs');
const {sections,inspectImage}=require('./frozen_div.cjs');
const layout=require('./report_layout.cjs');
const {target}=require('./partition_frozen_proof.cjs');
const {parsed}=require('./bits_fifth_proof.cjs');
const baseVariant='esp8266-opus-live-asm-base-20260917';
const variant='esp8266-opus-live-asm-ebands-final-20260917';
const names=['clt_compute_allocation','quant_partition','decode_pulses','clt_mdct_backward_c'];
const rawBase='esp8266-opus-folding-control-v1';
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe';
const esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const art=v=>path.join(root,'firmware/development',v),build=v=>path.join(root,'.build',v),read=accepted.read;
function save(file,bytes){if(typeof bytes==='string')bytes=Buffer.from(bytes);fs.mkdirSync(path.dirname(file),{recursive:true});if(fs.existsSync(file))assert.deepEqual(fs.readFileSync(file),bytes,'Refuse changed evidence '+file);else fs.writeFileSync(file,bytes);}
function chain(){const rows=[];let v=accepted.variant('candidate');while(v!==rawBase){const d=art(v),p=read(path.join(d,'preflight.json'));rows.push({variant:v,proof:p});v=p.parent;assert.ok(rows.length<=30);}return rows.reverse();}
function mapping(a,b){
 const ranges=names.map(name=>{const x=a.functions[name],y=b.functions[name];assert.equal(x.bytes,y.bytes,name+' size');assert.deepEqual(x.graph,y.graph,name+' baseline graph');return{name,old:x.address,new:y.address,bytes:x.bytes};});
 const literals=new Map();
 for(const name of names){const x=parsed(a.functions[name]),y=parsed(b.functions[name]);assert.equal(x.length,y.length);
  for(let i=0;i<x.length;i++){assert.equal(x[i].address-a.functions[name].address,y[i].address-b.functions[name].address);assert.equal(x[i].bytes,y[i].bytes);assert.equal(x[i].op,y[i].op);
   if(x[i].op==='l32r'){const from=target(x[i]),to=target(y[i]);if(literals.has(from))assert.equal(literals.get(from),to);literals.set(from,to);}}
 }
 const move=address=>{const inside=ranges.filter(r=>address>=r.old&&address<r.old+r.bytes);if(inside.length){assert.equal(inside.length,1);return inside[0].new+address-inside[0].old;}assert.ok(literals.has(address),'Unmapped address '+address.toString(16));return literals.get(address);};
 return {ranges,literals,move};
}
function symbols(file){return [...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-n',file]).matchAll(/^([0-9a-f]+)\s+A\s+(\S+)$/gm)].map(m=>({address:parseInt(m[1],16),name:m[2]}));}
function literalReader(file,address){return run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d',file]).split('\n').filter(s=>new RegExp('l32r\\s+[^,]+,\\s*'+address.toString(16)+'\\b').test(s));}
function generate(){
 const initial=fs.readFileSync(path.join(build(baseVariant),f.elfName));
 const m=read(path.join(art(baseVariant),'manifest.json'));
 assert.equal(m.opus_benchmark,false);assert.equal(m.opus_benchmark_output,false);assert.equal(m.freertos_runtime_stats,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.i2s,true);assert.equal(m.data_gpio,3);
 const old=layout.inspect(rawBase,names),ordinary=layout.inspect(baseVariant,names),map=mapping(old,ordinary);
 const oldElf=path.join(build(rawBase),f.elfName),newElf=path.join(build(baseVariant),f.elfName);
 // This one changed literal must remain private to the same instruction.
 const literal=0x40211a9c,readersA=literalReader(oldElf,literal),readersB=literalReader(newElf,map.move(literal));
 assert.equal(readersA.length,1);assert.equal(readersB.length,1);
 let live=initial;const records=[];
 for(const entry of chain()){
  const d=art(entry.variant),p=entry.proof,source=fs.readFileSync(path.join(d,'patches.s'),'utf8');
  assert.ok(!source.split(/\r?\n/).some(s=>!s.trim().startsWith('#')&&/0x[0-9a-f]{8}/i.test(s)),'Unrelocated absolute operand');
  const originalObject=fs.readFileSync(path.join(d,'patches.elf')),originalSections=sections(originalObject);
  p.patches.forEach((x,i)=>{const s=originalSections.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,x.address);assert.equal(s.bytes,x.bytes);assert.equal(originalObject.subarray(s.offset,s.offset+s.bytes).toString('hex'),x.after_hex);});
  const defs=symbols(path.join(d,'patches.elf'));
  const ld=defs.map(s=>s.name+' = 0x'+map.move(s.address).toString(16)+';').join('\n')+'\nSECTIONS {\n'+p.patches.map((x,i)=>'.text.patch'+i+' 0x'+map.move(x.address).toString(16)+' : { *(.text.patch'+i+') }').join('\n')+'\n}\n';
  const out=path.join(build(variant),entry.variant);save(path.join(out,'patches.s'),source);save(path.join(out,'patches.ld'),ld);
  run(path.join(bin,'xtensa-lx106-elf-as.exe'),[path.join(out,'patches.s'),'-o',path.join(out,'patches.o')]);
  run(path.join(bin,'xtensa-lx106-elf-ld.exe'),['-e','0','-T',path.join(out,'patches.ld'),'-o',path.join(out,'patches.elf'),path.join(out,'patches.o')]);
  const object=fs.readFileSync(path.join(out,'patches.elf')),ss=sections(object);
  const patches=p.patches.map((x,i)=>{const address=map.move(x.address),s=ss.find(s=>s.name==='.text.patch'+i),off=f.offsetAt(live,address,x.bytes);assert.equal(s.address,address);assert.equal(s.bytes,x.bytes);return{address,bytes:x.bytes,before_hex:live.subarray(off,off+x.bytes).toString('hex'),after_hex:object.subarray(s.offset,s.offset+s.bytes).toString('hex')};});
  live=f.patchElf(live,patches);
  records.push({variant:entry.variant,source_sha256_lf:sourceHash(path.join(d,'patches.s')),original_proof_sha256_lf:sourceHash(path.join(d,'preflight.json')),original_object_sha256:hash(originalObject),definitions:defs.map(s=>({...s,relocated:map.move(s.address)})),linker_script:ld,patches,relocated_object_sha256:hash(object)});
 }
 save(path.join(build(variant),f.elfName),live);
 const actual=layout.inspect(variant,names,{internalCalls:['quant_partition']}),expected=layout.inspect(accepted.variant('candidate'),names,{internalCalls:['quant_partition']});
 assert.deepEqual(actual.sections,ordinary.sections);assert.deepEqual(actual.function_sizes,ordinary.function_sizes);
 for(const name of names)assert.deepEqual(actual.functions[name].graph,expected.functions[name].graph,'Accepted graph differs: '+name);
 // Check every byte outside the union of patch regions, including unchanged
 // literal words and other decoder functions. Only app checksum is repacked.
 const touched=new Set();for(const r of records)for(const p of r.patches)for(let i=0;i<p.bytes;i++)touched.add(f.offsetAt(initial,p.address,p.bytes)+i);
 for(let i=0;i<initial.length;i++)if(!touched.has(i))assert.equal(initial[i],live[i]);
 const last=records.find(r=>r.variant==='esp8266-opus-pvq-exp2-table32-candidate-v1');
 const table=last.patches[3],pointer=last.patches[2];assert.equal(Buffer.from(pointer.after_hex,'hex').readUInt32LE(),table.address);assert.equal(table.after_hex,chain().find(r=>r.variant===last.variant).proof.patches[3].after_hex);
 console.log('Relocated all18 stages; checking inherited semantic proofs');
 const inherited=accepted.verifyPair();
 const image=path.join(build(variant),'app.bin');const log=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',image,path.join(build(variant),f.elfName)]);
 const app=fs.readFileSync(image);inspectImage(app);assert.equal(app.length,m.bytes);assert.ok(app.length<=0xf0000);
 const manifest={...m,purpose:'Ordinary radio with the full accepted eBands-final ASM chain, I2S PDM and WebUI; no benchmark; awaiting live qualification',app_sha256:hash(app),post_link_live_accepted:true,accepted_asm_variant:accepted.variant('candidate'),accepted_asm_sha256:inherited.manifests.candidate.app_sha256,post_link_recipe_sha256_lf:sourceHash(__filename),unpatched_radio_app_sha256:m.app_sha256,post_link_static_ram_delta:0};
 const proof={recipe_sha256_lf:sourceHash(__filename),baseVariant,variant,acceptedVariant:accepted.variant('candidate'),base_elf_sha256:hash(initial),candidate_elf_sha256:hash(live),accepted_elf_sha256:inherited.proof.candidate_elf_sha256,mapping:{ranges:map.ranges,literals:[...map.literals]},records,literal_readers:{before:readersA,after:readersB},before:ordinary,after:actual,accepted:expected,static_ram_delta:0,stack_delta:0,changed_storage_bytes:touched.size,app_sha256:hash(app),app_bytes:app.length};
 save(path.join(art(variant),'app.bin'),app);save(path.join(art(variant),'manifest.json'),JSON.stringify(manifest,null,2)+'\n');save(path.join(art(variant),'preflight.json'),JSON.stringify(proof,null,2)+'\n');save(path.join(art(variant),'base.elf.gz'),zlib.gzipSync(initial,{level:9}));save(path.join(art(variant),'app.elf.gz'),zlib.gzipSync(live,{level:9}));save(path.join(art(variant),'sdkconfig'),fs.readFileSync(path.join(art(baseVariant),'sdkconfig')));save(path.join(art(variant),'packaging.log'),log);
 console.log(JSON.stringify({passed:true,variant,app_bytes:app.length,sha256:hash(app),chain:records.length,static_ram_delta:0,graphs_exact:true}));return proof;
}
module.exports={variant,baseVariant,names,chain,mapping,generate};
if(require.main===module)generate();
