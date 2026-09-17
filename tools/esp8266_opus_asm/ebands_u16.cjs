// Frozen-layout ASM experiment over accepted ebands-final; not production.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {root,component,hash,sourceHash,run}=require('./export.cjs'),base=require('./frozen_reloads.cjs');
const previous=require('./ebands_final.cjs'),sem=require('./ebands_u16_proof.cjs');
const {sections,inspectImage}=require('./frozen_div.cjs'),layout=require('./report_layout.cjs');
const parent=previous.variant('candidate'),variant=t=>'esp8266-opus-ebands-u16-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t)),build=t=>path.join(root,'.build',variant(t)),read=previous.read;
const names=previous.names,inspect=v=>layout.inspect(v,names,{internalCalls:['quant_partition']});
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe',esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const dependencies=['ebands_u16_proof.cjs','ebands_u16.s','ebands_final.cjs','ebands_final_proof.cjs','ebands_pair_proof.cjs','report_layout.cjs','frozen_reloads.cjs'];
const depHashes=()=>Object.fromEntries(dependencies.map(n=>[n,sourceHash(path.join(__dirname,n))]));
function save(file,b){if(typeof b==='string')b=Buffer.from(b);fs.mkdirSync(path.dirname(file),{recursive:true});if(fs.existsSync(file))assert.deepEqual(fs.readFileSync(file),b,'Existing evidence differs: '+file);else fs.writeFileSync(file,b);}
const sourceFor=()=>fs.readFileSync(path.join(__dirname,'ebands_u16.s'),'utf8').replace(/\r\n/g,'\n');
function manifestPair(a,b){
 assert.equal(a.post_link_ebands_u16_variant,'control');assert.equal(b.post_link_ebands_u16_variant,'candidate');
 for(const k of new Set([...Object.keys(a),...Object.keys(b)]))if(!['purpose','app_sha256','post_link_ebands_u16_variant'].includes(k))assert.deepEqual(a[k],b[k],k);
 for(const m of[a,b]){assert.equal(m.post_link_ebands_final_variant,'candidate');assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);}
}
function generate(){
 const inherited=previous.verifyPair(),dir=previous.art('candidate'),m=read(path.join(dir,'manifest.json'));
 const a=fs.readFileSync(path.join(root,'.build',parent,base.elfName)),app=fs.readFileSync(path.join(dir,'app.bin'));assert.equal(hash(a),inherited.proof.candidate_elf_sha256);assert.equal(hash(app),m.app_sha256);
 const info=inspect(parent);for(const n of previous.names)assert.deepEqual(info.functions[n],inherited.proof.actual_functions[n]);
 const patches=sem.findPatches(info.functions),source=sourceFor();require('./pvq_exp2_table32.cjs').disjoint(patches);
 const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o'),linked=path.join(build('candidate'),'patches.elf'),script=path.join(build('candidate'),'patches.ld');
 save(asm,source);save(script,sem.definitions()+'\nSECTIONS {\n'+patches.map((p,i)=>` .text.patch${i} 0x${p.address.toString(16)} : { *(.text.patch${i}) }\n`).join('')+'}\n');
 run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);run(path.join(bin,'xtensa-lx106-elf-ld.exe'),['-e','0','-T',script,'-o',linked,obj]);
 const object=fs.readFileSync(linked),ss=sections(object);
 patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,p.address);assert.equal(s.bytes,p.bytes);p.after_hex=object.subarray(s.offset,s.offset+s.bytes).toString('hex');p.before_hex=a.subarray(base.offsetAt(a,p.address,p.bytes),base.offsetAt(a,p.address,p.bytes)+p.bytes).toString('hex');});
 const b=base.patchElf(a,patches),images={},manifests={},logs={};
 for(const[t,elf]of[['control',a],['candidate',b]]){
  const file=path.join(build(t),base.elfName);save(file,elf);
  logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),file]);
  images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
  manifests[t]={...m,purpose:'Frozen-layout '+t+' nonnegative eBands extraction raw benchmark; not production',app_sha256:hash(images[t]),post_link_ebands_u16_variant:t,post_link_recipe_sha256_lf:sourceHash(__filename),post_link_bundle_dependencies:depHashes(),post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(a)};
 }
 assert.deepEqual(images.control,app);manifestPair(manifests.control,manifests.candidate);
 const actual=inspect(variant('candidate'));assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);
 const helperDisassembly=sem.specs.map((s,i)=>layout.reachableDisassembly(path.join(build('candidate'),base.elfName),{name:'ebands_u16_'+i,address:s.helper,bytes:s.span}));
 const semantic=sem.prove(info.functions,actual.functions,helperDisassembly),table=sem.tableProof(a);assert.deepEqual(sem.tableProof(b),table);
 const proof={schema:1,parent,recipe_sha256_lf:sourceHash(__filename),dependencies:depHashes(),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),original_storage:sem.storageBytesProof(a),patches,semantic,table,helperDisassembly,static_ram_delta:0,stack_delta:0,app_bytes:app.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,imageProof:base.compareApps(images.control,images.candidate,patches),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),logs}};
 for(const t of['control','candidate']){save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(dir,'sdkconfig')));}
 save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.elf'),object);save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');
 console.log(JSON.stringify({passed:true,sha256:manifests.candidate.app_sha256,app_bytes:app.length,ram_delta:0,cases:semantic.numeric_cases}));return proof;
}
function verifyPair(){
 const d=art('candidate'),p=read(path.join(d,'preflight.json'));assert.equal(p.recipe_sha256_lf,sourceHash(__filename));assert.deepEqual(p.dependencies,depHashes());
 const a=zlib.gunzipSync(fs.readFileSync(path.join(d,'parent.elf.gz'))),b=base.patchElf(a,p.patches);assert.equal(hash(a),p.parent_elf_sha256);assert.equal(hash(b),p.candidate_elf_sha256);
 assert.equal(fs.readFileSync(path.join(d,'patches.s'),'utf8').replace(/\r\n/g,'\n'),sourceFor());
 const obj=fs.readFileSync(path.join(d,'patches.elf')),ss=sections(obj);p.patches.forEach((x,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,x.address);assert.equal(s.bytes,x.bytes);assert.equal(obj.subarray(s.offset,s.offset+s.bytes).toString('hex'),x.after_hex);});
 assert.deepEqual(sem.prove(p.functions,p.actual_functions,p.helperDisassembly),p.semantic);assert.deepEqual(sem.tableProof(a),p.table);assert.deepEqual(sem.tableProof(b),p.table);
 assert.deepEqual(sem.storageBytesProof(a),p.original_storage);
 const manifests={},apps={};for(const t of['control','candidate']){manifests[t]=read(path.join(art(t),'manifest.json'));apps[t]=fs.readFileSync(path.join(art(t),'app.bin'));assert.equal(hash(apps[t]),manifests[t].app_sha256);assert.equal(apps[t].length,manifests[t].bytes);assert.equal(manifests[t].post_link_recipe_sha256_lf,p.recipe_sha256_lf);assert.deepEqual(manifests[t].post_link_bundle_dependencies,p.dependencies);}
 manifestPair(manifests.control,manifests.candidate);assert.deepEqual(base.compareApps(apps.control,apps.candidate,p.patches),p.imageProof);
 const inherited=previous.verifyPair();assert.equal(hash(a),inherited.proof.candidate_elf_sha256);for(const n of previous.names)assert.deepEqual(p.functions[n],inherited.proof.actual_functions[n]);
 return{proof:p,manifests};
}
function cModels(){
 const models=previous.cModels(),dir=path.join(root,'.build/opus-bands-ebands-u16');fs.mkdirSync(dir,{recursive:true});
 const source='upstream/celt/rate.c',old=models.find(m=>m.source===source);assert.ok(old);
 let text=fs.readFileSync(old.file,'utf8').replace(/\r\n/g,'\n');
 const {once}=require('./bands.cjs');
 text=once(text,'return (b<32768?(int)b:(int)b-65536)-(a<32768?(int)a:(int)a-65536);','celt_assert(a<=100 && b<=100);\n  return (int)b-(int)a;');
 const file=path.join(dir,'rate.model.c');fs.writeFileSync(file,text);return models.map(m=>m.source===source?{source,file}:m);
}

module.exports={parent,variant,art,build,names,read,depHashes,sourceFor,manifestPair,generate,verifyPair,cModels};if(require.main===module)generate();
