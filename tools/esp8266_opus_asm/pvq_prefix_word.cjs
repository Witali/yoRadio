// Opt-in fixed-address ASM experiment; no production default is changed.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {root,component,hash,sourceHash,run}=require('./export.cjs'),base=require('./frozen_reloads.cjs');
const previous=require('./ebands_final.cjs'),sem=require('./pvq_prefix_word_proof.cjs');
const {sections,inspectImage}=require('./frozen_div.cjs'),layout=require('./report_layout.cjs');
const parent=previous.variant('candidate'),variant=t=>'esp8266-opus-pvq-prefix-word-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t)),build=t=>path.join(root,'.build',variant(t)),read=previous.read;
const names=[...new Set([...previous.names,'celt_decode_with_ec_dred','alg_quant'])];
const inspect=(v,ns=names)=>layout.inspect(v,ns,{internalCalls:['quant_partition']});
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe',esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const dependencies=['pvq_prefix_word.s','pvq_prefix_word_proof.cjs','pvq_binary_proof.cjs','quant_decode_proof.cjs','audit_quant_decode.cjs','ebands_final.cjs','report_layout.cjs','frozen_reloads.cjs'];
const depHashes=()=>Object.fromEntries(dependencies.map(n=>[n,sourceHash(path.join(__dirname,n))]));
const sourceFor=t=>{const words=sem.prefix(t);return fs.readFileSync(path.join(__dirname,'pvq_prefix_word.s'),'utf8').replace(/\r\n/g,'\n').replace('@TABLE_BYTES@',Array.from({length:11},(_,i)=>'    .long '+Array.from({length:32},(_,j)=>words.readUInt32LE((i*32+j)*4)).join(',')).join('\n'));};
function save(file,b){if(typeof b==='string')b=Buffer.from(b);fs.mkdirSync(path.dirname(file),{recursive:true});if(fs.existsSync(file))assert.deepEqual(fs.readFileSync(file),b,'Existing evidence differs: '+file);else fs.writeFileSync(file,b);}
function manifestPair(a,b){
 assert.equal(a.post_link_pvq_prefix_word_variant,'control');assert.equal(b.post_link_pvq_prefix_word_variant,'candidate');
 for(const k of new Set([...Object.keys(a),...Object.keys(b)]))if(!['purpose','app_sha256','post_link_pvq_prefix_word_variant'].includes(k))assert.deepEqual(a[k],b[k],k);
 for(const m of[a,b]){assert.equal(m.post_link_ebands_final_variant,'candidate');assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);}
}
function generate(){
 const dir=previous.art('candidate'),inherited={proof:read(path.join(dir,'preflight.json'))},m=read(path.join(dir,'manifest.json'));
 const inputFile=path.join(root,'.build',parent,base.elfName),a=fs.readFileSync(inputFile),app=fs.readFileSync(path.join(dir,'app.bin'));
 assert.equal(hash(a),inherited.proof.candidate_elf_sha256);assert.equal(hash(app),m.app_sha256);
 const info=inspect(parent);for(const n of previous.names)assert.deepEqual(info.functions[n],inherited.proof.actual_functions[n]);
 sem.auditSite(info.functions.decode_pulses);const storage=sem.storage(info,inputFile,a),table=sem.table(a);
 const patches=[{address:sem.site,bytes:sem.siteBytes},{address:sem.storageAddress,bytes:sem.storageBytes},{address:sem.dataAddress,bytes:sem.dataBytes}],source=sourceFor(table);
 const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o'),linked=path.join(build('candidate'),'patches.elf'),script=path.join(build('candidate'),'patches.ld');
 save(asm,source);save(script,'pvq_prefix_word_fast = 0x4025335d;\npvq_prefix_word_flags = 0x40253354;\nSECTIONS {\n'+patches.map((p,i)=>` .text.patch${i} 0x${p.address.toString(16)} : { *(.text.patch${i}) }\n`).join('')+'}\n');
 run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);run(path.join(bin,'xtensa-lx106-elf-ld.exe'),['-e','0','-T',script,'-o',linked,obj]);
 const object=fs.readFileSync(linked),ss=sections(object);
 patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,p.address);assert.equal(s.bytes,p.bytes);p.after_hex=object.subarray(s.offset,s.offset+s.bytes).toString('hex');const off=base.offsetAt(a,p.address,p.bytes);p.before_hex=a.subarray(off,off+p.bytes).toString('hex');});
 const b=base.patchElf(a,patches),images={},manifests={},logs={};
 for(const[t,elf]of[['control',a],['candidate',b]]){
  const file=path.join(build(t),base.elfName);save(file,elf);
  logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),file]);
  images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
  manifests[t]={...m,purpose:'Fixed-address '+t+' exact PVQ direct-word exponent-prefix row search raw ASM benchmark; not production',app_sha256:hash(images[t]),post_link_pvq_prefix_word_variant:t,
   post_link_recipe_sha256_lf:sourceHash(__filename),post_link_bundle_dependencies:depHashes(),post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(a)};
 }
 assert.deepEqual(images.control,app);manifestPair(manifests.control,manifests.candidate);
 // The helper replaces decoder-dead encoder instructions. Do not traverse
 // those old encoder branches as if they were a new valid decoder entry.
 const actual=inspect(variant('candidate'),names.filter(n=>!['quant_all_bands','alg_quant'].includes(n)));
 assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);
 for(const n of names.filter(n=>!['quant_all_bands','decode_pulses','alg_quant'].includes(n)))assert.deepEqual(actual.functions[n],info.functions[n]);
 const helperDisassembly=layout.reachableDisassembly(path.join(build('candidate'),base.elfName),{name:'pvq_prefix_word_leaf',address:sem.helper,bytes:sem.helperBytes});
 const semantic=sem.prove(info.functions.decode_pulses,actual.functions.decode_pulses,helperDisassembly,table);assert.deepEqual(sem.table(b),table);const prefix_table=sem.prefixProof(b,table);
 // Expensive recursive verification runs only after the new local proof is
 // valid, but still before any candidate is published for OTA.
 assert.deepEqual(previous.verifyPair().proof,inherited.proof);
 const proof={schema:1,parent,recipe_sha256_lf:sourceHash(__filename),dependencies:depHashes(),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),
  patches,storage,semantic,table,prefix_table,helperDisassembly,static_ram_delta:0,stack_delta:0,app_bytes:app.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,
  imageProof:base.compareApps(images.control,images.candidate,patches),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),logs}};
 for(const t of['control','candidate']){save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(dir,'sdkconfig')));}
 save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.elf'),object);
 save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');
 console.log(JSON.stringify({passed:true,sha256:manifests.candidate.app_sha256,app_bytes:app.length,semantic}));return proof;
}
function verifyPair(){
 const d=art('candidate'),p=read(path.join(d,'preflight.json'));assert.equal(p.recipe_sha256_lf,sourceHash(__filename));assert.deepEqual(p.dependencies,depHashes());
 const a=zlib.gunzipSync(fs.readFileSync(path.join(d,'parent.elf.gz'))),b=base.patchElf(a,p.patches);assert.equal(hash(a),p.parent_elf_sha256);assert.equal(hash(b),p.candidate_elf_sha256);
 assert.equal(fs.readFileSync(path.join(d,'patches.s'),'utf8').replace(/\r\n/g,'\n'),sourceFor(p.table));
 assert.deepEqual(p.patches.map(({address,bytes})=>({address,bytes})),[{address:sem.site,bytes:sem.siteBytes},{address:sem.storageAddress,bytes:sem.storageBytes},{address:sem.dataAddress,bytes:sem.dataBytes}]);
 const obj=fs.readFileSync(path.join(d,'patches.elf')),ss=sections(obj);
 p.patches.forEach((x,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,x.address);assert.equal(s.bytes,x.bytes);assert.equal(obj.subarray(s.offset,s.offset+s.bytes).toString('hex'),x.after_hex);});
 assert.deepEqual(sem.prove(p.functions.decode_pulses,p.actual_functions.decode_pulses,p.helperDisassembly,p.table),p.semantic);
 assert.deepEqual(sem.storage({functions:p.functions},path.join(root,'.build',parent,base.elfName),a),p.storage);
 assert.deepEqual(sem.table(a),p.table);assert.deepEqual(sem.table(b),p.table);assert.deepEqual(sem.prefixProof(b,p.table),p.prefix_table);
 const manifests={},apps={};for(const t of['control','candidate']){manifests[t]=read(path.join(art(t),'manifest.json'));apps[t]=fs.readFileSync(path.join(art(t),'app.bin'));
  assert.equal(hash(apps[t]),manifests[t].app_sha256);assert.equal(apps[t].length,manifests[t].bytes);assert.equal(manifests[t].post_link_recipe_sha256_lf,p.recipe_sha256_lf);assert.deepEqual(manifests[t].post_link_bundle_dependencies,p.dependencies);}
 manifestPair(manifests.control,manifests.candidate);assert.deepEqual(base.compareApps(apps.control,apps.candidate,p.patches),p.imageProof);
 const inherited=previous.verifyPair();assert.equal(hash(a),inherited.proof.candidate_elf_sha256);for(const n of previous.names)assert.deepEqual(p.functions[n],inherited.proof.actual_functions[n]);
 return{proof:p,manifests};
}
function cModels(){
 const models=previous.cModels(),dir=path.join(root,'.build/opus-bands-pvq-prefix-word');fs.mkdirSync(dir,{recursive:true});
 const source='upstream/celt/cwrs.c';assert.ok(!models.some(m=>m.source===source));
 let text=fs.readFileSync(path.join(component,source),'utf8').replace(/\r\n/g,'\n');
 const t=sem.table(fs.readFileSync(path.join(root,'.build',parent,base.elfName)));
 const words=sem.prefix(t);
 text='static const unsigned int y_pvq_prefix_word[352] = {'+Array.from({length:352},(_,i)=>words.readUInt32LE(i*4)).join(',')+'};\n'+text;
 const anchor='else for(p=row[_k];p>_i;p=row[_k])_k--;';assert.equal(text.split(anchor).length-1,1);
 text=text.replace(anchor,`else {
        if(_k-_n>=8){
          unsigned bound=y_pvq_prefix_word[(_n-3)*32+__builtin_clz(_i)];
          if(bound<(unsigned)_k)_k=(int)bound;
        }
        for(p=row[_k];p>_i;p=row[_k])_k--;
      }`);
 const file=path.join(dir,'cwrs.model.c');fs.writeFileSync(file,text);return[...models,{source,file}];
}
module.exports={parent,variant,art,build,names,read,depHashes,sourceFor,manifestPair,generate,verifyPair,cModels};if(require.main===module)generate();
