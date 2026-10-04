// Independent fixed-address ASM candidate over the accepted eBands-final ELF.
// Build/package only: no serial, OTA, network or changes to production defaults.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {root,hash,sourceHash,run}=require('./export.cjs'),base=require('./frozen_reloads.cjs');
const previous=require('./ebands_final.cjs'),sem=require('./pvq_n4_prefix_proof.cjs');
const {sections,inspectImage}=require('./frozen_div.cjs'),layout=require('./report_layout.cjs');
const storageAudit=require('./pvq_prefix_word_proof.cjs');
const {n4Table}=require('./algorithm_candidates.cjs');
const parent=previous.variant('candidate'),variant=t=>'esp8266-opus-pvq-n4-prefix-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t)),build=t=>path.join(root,'.build',variant(t));
const read=previous.read,bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe';
const esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const names=[...new Set([...previous.names,'alg_quant','celt_decode_with_ec_dred'])];
const dependencies=()=>Object.fromEntries(['pvq_n4_prefix.cjs','pvq_n4_prefix.s','pvq_n4_prefix_proof.cjs','algorithm_candidates.cjs','analyze_n4_prefix.cjs','pvq_n3_diff_proof.cjs','pvq_prefix_word_proof.cjs','quant_decode_proof.cjs','audit_quant_decode.cjs','report_layout.cjs','frozen_reloads.cjs'].map(n=>[n,sourceHash(path.join(__dirname,n))]));
function write(file,data){fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,data);}
function save(file,data){if(typeof data==='string')data=Buffer.from(data);if(fs.existsSync(file))assert.deepEqual(fs.readFileSync(file),data,'Evidence already exists: '+file);else write(file,data);}
function sourceFor(){
 const asm=fs.readFileSync(path.join(__dirname,'pvq_n4_prefix.s'),'utf8').replace(/\r\n/g,'\n');
 return asm+'\n# Offline generated exact single-threshold buckets in unused encoder flash.\n.section .text.patch2,"ax",@progbits\n.global n4_literal\nn4_literal:\n.word 0x'+sem.tableAddress.toString(16)+'\n'+n4Table().entries.map(x=>'.word 0x'+x.toString(16)).join('\n')+'\n';
}
function reconstructParent(){
 const p=read(path.join(previous.art('candidate'),'preflight.json'));
 const raw=zlib.gunzipSync(fs.readFileSync(path.join(previous.art('candidate'),'parent.elf.gz')));assert.equal(hash(raw),p.parent_elf_sha256);
 const elf=base.patchElf(raw,p.patches);assert.equal(hash(elf),p.candidate_elf_sha256);return {elf,proof:p};
}
function generate(){
 const {elf:a,proof:inherited}=reconstructParent(),input=path.join(root,'.build',parent,base.elfName);
 // Older storage-contract checks inspect this exact ELF and the pinned linker map.
 save(input,a);const info=layout.inspect(parent,names,{internalCalls:['quant_partition']});
 for(const n of previous.names)assert.deepEqual(info.functions[n],inherited.actual_functions[n]);
 sem.auditSite(info.functions.decode_pulses);
 const audit=storageAudit.storage(info,input,a);
 assert.equal(audit.encoder_storage.address,sem.dataAddress);assert.ok(audit.encoder_storage.bytes>=sem.dataBytes);
 // The reused contract covers a larger untouched tail too; record the exact
 // subset replaced here, not the earlier prefix experiment's 1412-byte claim.
 const storage={contract:audit.contract,helper:audit.storage,encoder:audit.encoder_storage,replaced_encoder_bytes:sem.dataBytes};
 const source=sourceFor(),patches=[{address:sem.site,bytes:sem.siteBytes},{address:sem.helper,bytes:sem.helperBytes},{address:sem.dataAddress,bytes:sem.dataBytes}];
 const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o'),linked=path.join(build('candidate'),'patches.elf');
 const script='n4_fast = 0x4025335d;\nn4_flags = 0x40253354;\nSECTIONS {\n'+patches.map((p,i)=>` .text.patch${i} 0x${p.address.toString(16)} : { *(.text.patch${i}) }\n`).join('')+'}\n';
 write(asm,source);write(path.join(build('candidate'),'patches.ld'),script);
 run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);run(path.join(bin,'xtensa-lx106-elf-ld.exe'),['-e','0','-T',path.join(build('candidate'),'patches.ld'),'-o',linked,obj]);
 const object=fs.readFileSync(linked),ss=sections(object);
 patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,p.address);assert.equal(s.bytes,p.bytes);p.after_hex=object.subarray(s.offset,s.offset+s.bytes).toString('hex');const off=base.offsetAt(a,p.address,p.bytes);p.before_hex=a.subarray(off,off+p.bytes).toString('hex');});
 const b=base.patchElf(a,patches);
 write(path.join(build('candidate'),base.elfName),b);write(path.join(build('control'),base.elfName),a);
 const actual=layout.inspect(variant('candidate'),names.filter(n=>!['quant_all_bands','alg_quant'].includes(n)),{internalCalls:['quant_partition']});
 assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);
 for(const n of Object.keys(actual.functions).filter(n=>n!=='decode_pulses'))assert.deepEqual(actual.functions[n],info.functions[n]);
 const helperDisassembly=layout.reachableDisassembly(path.join(build('candidate'),base.elfName),{name:'n4_leaf',address:sem.helper,bytes:sem.helperBytes});
 const table=require('./pvq_n3_diff_proof.cjs').table(a);assert.deepEqual(require('./pvq_n3_diff_proof.cjs').table(b),table);
 console.log('Checking linked N4 instructions, all stored U intervals and every table-domain index');
 const semantic=sem.prove(info.functions.decode_pulses,actual.functions.decode_pulses,helperDisassembly,table);
 const images={},manifests={},logs={},m=read(path.join(previous.art('candidate'),'manifest.json'));
 for(const t of ['control','candidate']){
  logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),path.join(build(t),base.elfName)]);
  images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
  manifests[t]={...m,purpose:'Experimental fixed-address N4 prefix ASM '+t+'; offline validated only, not production',app_sha256:hash(images[t]),post_link_pvq_n4_prefix_variant:t,
   post_link_recipe_sha256_lf:sourceHash(__filename),post_link_bundle_dependencies:dependencies(),post_link_parent_elf_sha256:hash(a)};
 }
 assert.deepEqual(images.control,fs.readFileSync(path.join(previous.art('candidate'),'app.bin')));
 assert.equal(images.control.length,images.candidate.length);
 const proof={schema:1,parent,recipe_sha256_lf:sourceHash(__filename),dependencies:dependencies(),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),patches,storage,semantic,table,helperDisassembly,
  static_ram_delta:0,stack_delta:0,app_bytes:images.candidate.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,
  imageProof:base.compareApps(images.control,images.candidate,patches),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),logs},scope:'Experimental candidate; correctness only, hardware CPU and live I2S acceptance pending'};
 for(const t of ['control','candidate']){save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(previous.art('candidate'),'sdkconfig')));}
 save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.elf'),object);
 save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');
 console.log(JSON.stringify({passed:true,variant:variant('candidate'),semantic},null,2));return proof;
}
module.exports={parent,variant,art,build,dependencies,sourceFor,reconstructParent,generate};if(require.main===module)generate();
