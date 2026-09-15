// Fourth-step PVQ shortcut on the accepted baseline; not production.
// Preserve outside instruction addresses, stack and table storage.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {root,hash,sourceHash,run}=require('./export.cjs');
const base=require('./frozen_reloads.cjs'),previous=require('./bits_fifth.cjs');
const sem=require('./bits_fourth_proof.cjs');
const {sections,inspectImage}=require('./frozen_div.cjs'),{inspect}=require('./report_layout.cjs');
const parent=previous.variant('candidate'),variant=t=>'esp8266-opus-bits-fourth-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t)),build=t=>path.join(root,'.build',variant(t)),read=previous.read;
const names=[...new Set(['quant_partition','quant_band','quant_all_bands','celt_decode_with_ec_dred',...previous.names])];
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe',esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const dependencies=['bits_fourth_proof.cjs','bits_fourth.s','bits_fifth_proof.cjs','partition_frozen_proof.cjs','partition_decode.cjs','pulse_lookup.cjs','pulse_inverse.cjs'];
const depHashes=()=>Object.fromEntries(dependencies.map(n=>[n,sourceHash(path.join(__dirname,n))]));
function save(file,b){if(typeof b==='string')b=Buffer.from(b);fs.mkdirSync(path.dirname(file),{recursive:true});if(fs.existsSync(file))assert.deepEqual(fs.readFileSync(file),b,'Existing evidence differs: '+file);else fs.writeFileSync(file,b);}
function disjoint(patches){
 const ordered=[...patches].sort((a,b)=>a.address-b.address);
 for(let i=0;i<ordered.length;i++){const p=ordered[i];assert.ok(Number.isInteger(p.address)&&Number.isInteger(p.bytes)&&p.bytes>0);
  if(i)assert.ok(ordered[i-1].address+ordered[i-1].bytes<=p.address,'Overlapping patches');}
}
function findPatches(functions){const patches=sem.findPatches(functions.quant_partition);disjoint(patches);return patches;}
function sourceFor(){return fs.readFileSync(path.join(__dirname,'bits_fourth.s'),'utf8').replace(/\r\n/g,'\n');}
function prove(functions,actual,patches){
 const search=sem.prove(functions.quant_partition,actual.quant_partition);
 const contract={scope:'Unchanged caller chain and pure-register search replacement; inherit the independently verified bits-fifth private encode=0 contract.'};
 for(const n of names.slice(1))assert.deepEqual(actual[n],functions[n]);
 return{search,contract};
}
function manifestPair(a,b){
 assert.equal(a.post_link_bits_fourth_variant,'control');assert.equal(b.post_link_bits_fourth_variant,'candidate');
 for(const k of new Set([...Object.keys(a),...Object.keys(b)]))if(!['purpose','app_sha256','post_link_bits_fourth_variant'].includes(k))assert.deepEqual(a[k],b[k],k);
 for(const m of[a,b]){
  assert.equal(m.post_link_bits_fifth_variant,'candidate');assert.equal(m.post_link_pvq_row_loop_variant,'candidate');assert.equal(m.post_link_post_pair_variant,'candidate');
  assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.diagnostic,true);assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');
  assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);
  assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_division_benchmark,false);
 }
}
function generate(){
 const prior=previous.verifyPair(),dir=previous.art('candidate'),m=read(path.join(dir,'manifest.json'));
 const a=fs.readFileSync(path.join(root,'.build',parent,base.elfName)),app=fs.readFileSync(path.join(dir,'app.bin'));
 assert.equal(hash(a),prior.proof.candidate_elf_sha256);assert.equal(hash(app),m.app_sha256);
 const info=inspect(parent,names);assert.deepEqual(info.functions,prior.proof.actual_functions);
 const patches=findPatches(info.functions),source=sourceFor(patches);
 const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o'),linked=path.join(build('candidate'),'patches.elf'),script=path.join(build('candidate'),'patches.ld');
 save(asm,source);save(script,sem.definitions()+'\nSECTIONS {\n'+patches.map((p,i)=>' .text.patch'+i+' 0x'+p.address.toString(16)+' : { *(.text.patch'+i+') }\n').join('')+'}\n');
 run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);run(path.join(bin,'xtensa-lx106-elf-ld.exe'),['-e','0','-T',script,'-o',linked,obj]);
 const object=fs.readFileSync(linked),ss=sections(object);
 patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,p.address);assert.equal(s.bytes,p.bytes);
  p.after_hex=object.subarray(s.offset,s.offset+s.bytes).toString('hex');const off=base.offsetAt(a,p.address,p.bytes);p.before_hex=a.subarray(off,off+p.bytes).toString('hex');});
 const b=base.patchElf(a,patches),images={},manifests={},logs={};
 for(const[t,elf]of[['control',a],['candidate',b]]){
  const file=path.join(build(t),base.elfName);save(file,elf);
  logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),file]);
  images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
  manifests[t]={...m,purpose:'Frozen-layout '+t+' fourth-step PVQ shortcut ASM raw benchmark; not production',app_sha256:hash(images[t]),post_link_bits_fourth_variant:t,post_link_recipe_sha256_lf:sourceHash(__filename),post_link_bundle_dependencies:depHashes(),post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(a)};
 }
 assert.deepEqual(images.control,app);manifestPair(manifests.control,manifests.candidate);
 const actual=inspect(variant('candidate'),names);assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);
 const semantic=prove(info.functions,actual.functions,patches);
 const proof={schema:1,parent,recipe_sha256_lf:sourceHash(__filename),dependencies:depHashes(),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),patches,semantic,static_ram_delta:0,stack_delta:0,app_bytes:app.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,imageProof:base.compareApps(images.control,images.candidate,patches),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),logs}};
 for(const t of['control','candidate']){save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(dir,'sdkconfig')));}
 save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.elf'),object);save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');
 console.log(JSON.stringify({passed:true,sha256:manifests.candidate.app_sha256,app_bytes:app.length,ram_delta:0,patches:patches.length,search:semantic.search.numeric}));return proof;
}
function verifyPair(){
 const dest=art('candidate'),proof=read(path.join(dest,'preflight.json'));
 assert.equal(proof.recipe_sha256_lf,sourceHash(__filename));assert.deepEqual(proof.dependencies,depHashes());
 const a=zlib.gunzipSync(fs.readFileSync(path.join(dest,'parent.elf.gz')));assert.equal(hash(a),proof.parent_elf_sha256);
 const b=base.patchElf(a,proof.patches);assert.equal(hash(b),proof.candidate_elf_sha256);
 assert.equal(fs.readFileSync(path.join(dest,'patches.s'),'utf8').replace(/\r\n/g,'\n'),sourceFor(proof.patches));
 const object=fs.readFileSync(path.join(dest,'patches.elf')),ss=sections(object);
 proof.patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,p.address);assert.equal(s.bytes,p.bytes);assert.equal(object.subarray(s.offset,s.offset+s.bytes).toString('hex'),p.after_hex);});
 assert.deepEqual(prove(proof.functions,proof.actual_functions,proof.patches),proof.semantic);
 const manifests={},apps={};for(const t of['control','candidate']){
  manifests[t]=read(path.join(art(t),'manifest.json'));apps[t]=fs.readFileSync(path.join(art(t),'app.bin'));
  assert.equal(hash(apps[t]),manifests[t].app_sha256);assert.equal(apps[t].length,manifests[t].bytes);
  assert.equal(manifests[t].post_link_recipe_sha256_lf,proof.recipe_sha256_lf);assert.deepEqual(manifests[t].post_link_bundle_dependencies,proof.dependencies);
 }
 manifestPair(manifests.control,manifests.candidate);assert.deepEqual(base.compareApps(apps.control,apps.candidate,proof.patches),proof.imageProof);
 const prior=previous.verifyPair();assert.equal(hash(apps.control),prior.manifests.candidate.app_sha256);
 assert.deepEqual(proof.functions,prior.proof.actual_functions);
 return{proof,manifests};
}
// Actual C semantic shortcut, only a host correctness model; not target timing.
function cModels(){
 const dir=path.join(root,'.build/opus-bands-bits-fourth');fs.mkdirSync(dir,{recursive:true});
 const {once}=require('./bands.cjs');
 return require('./tell_inline.cjs').cModels().map(model=>{
  let text=fs.readFileSync(model.file,'utf8').replace(/\r\n/g,'\n');
  text=once(text,'#include "rate.h"\n','#include "rate.h"\n'+[
   'static int y_bits_fourth(const CELTMode *m,int band,int LM,int bits) {',
   ' const unsigned char *cache=m->cache.bits+m->cache.index[(LM+1)*m->nbEBands+band];',
   ' int lo=0,hi=cache[0];bits--;',
   ' for(int i=0;i<4;i++){int mid=(lo+hi+1)>>1;if(cache[mid]>=bits)hi=mid;else lo=mid;}',
   ' if(hi-lo>1){int mid=(lo+hi+1)>>1;if(cache[mid]>=bits)hi=mid;else lo=mid;',
   '  if(hi-lo>1){mid=(lo+hi+1)>>1;if(cache[mid]>=bits)hi=mid;else lo=mid;}}',
   ' return bits-(lo==0?-1:(int)cache[lo])<=(int)cache[hi]-bits?lo:hi;',
   '}'].join('\n')+'\n');
  text=once(text,'      q = bits2pulses(m, i, LM, b);','      q = y_bits_fourth(m, i, LM, b);');
  const file=path.join(dir,'bands.model.c');fs.writeFileSync(file,text);return {source:model.source,file};
 });
}
module.exports={parent,variant,art,build,names,read,depHashes,disjoint,findPatches,sourceFor,prove,manifestPair,generate,verifyPair,cModels};
if(require.main===module)generate();
