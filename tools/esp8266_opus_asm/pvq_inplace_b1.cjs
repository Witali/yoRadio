// Experimental fixed-layout clone of the ACCEPTED linked ASM, not a C rebuild.
// B=1 writes bounded signed pulses to X before exact in-place normalisation.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {root,hash,sourceHash,run}=require('./export.cjs');
const base=require('./frozen_reloads.cjs'),previous=require('./ebands_final.cjs'),layout=require('./report_layout.cjs');
const {sections,inspectImage}=require('./frozen_div.cjs');
const {readAt}=require('./pvq_exp2_table32_proof.cjs');
const storageAudit=require('./pvq_prefix_word_proof.cjs');
const variant=t=>'esp8266-opus-pvq-inplace-b1-'+t+'-v1';
const parent=previous.variant('candidate'),build=t=>path.join(root,'.build',variant(t)),art=t=>path.join(root,'firmware/development',variant(t));
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe',esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const site=0x402493b0,storage=0x40248cb4,capacity=1788,guard=0x40251024,guardCapacity=94;
const clean=r=>r.text.replace(/\s+<[^>]*>$/,'');
const label=a=>'ip_'+a.toString(16),target=r=>parseInt(r.args.replace(/\s+<[^>]*>$/,'').split(/,\s*/).at(-1),16);
const read=previous.read;
function save(p,b){fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,b);}
function dependencies(){return Object.fromEntries(['pvq_inplace_b1.cjs','pvq_inplace_b1_proof.cjs','pvq_prefix_word_proof.cjs','ebands_final.cjs','report_layout.cjs'].map(n=>[n,sourceHash(path.join(__dirname,n))]));}
function edits(fn){
 const rows=base.rows(fn.disassembly),m=new Map();
 const change=(pc,old,next)=>{assert.equal(clean(rows.find(r=>r.address===pc)),old);m.set(pc,next);};
 if(fn.name==='decode_pulses'){
  // Only output addresses shrink. All U-table loads/strides remain 32 bit.
  change(0x4025337d,'s32i a3, a5, 0',['s16i a3, a5, 0']);
  change(0x402533a9,'s32i a4, a3, 0',['s16i a4, a3, 0']);
  change(0x402534fb,'s32i a3, a4, 0',['s16i a3, a4, 0']);
  change(0x40253501,'addi a5, a5, 4',['addi.n a5, a5, 2']);
  // sp+8 retains 4*N-60 for the U-row pointer; halve ONLY its final X offset.
  change(0x40253514,'addi a3, a4, 52',['addi a3, a4, 52','srli a3, a3, 1']);
  change(0x40253590,'s32i a4, a5, 0',['s16i a4, a5, 0']);
  change(0x40253592,'s32i a3, a5, 4',['s16i a3, a5, 2']);
 }else{
  assert.equal(fn.name,'alg_unquant');
  const remove=(lo,hi,expected)=>{
   const selected=rows.filter(r=>r.address>=lo&&r.address<hi);
   if(expected)assert.deepEqual(selected.map(clean),expected);
   selected.forEach(r=>m.set(r.address,[]));
  };
  remove(0x402493d9,0x402493e9,['call0 402428c4','s32i a2, a1, 0','l32i a2, a1, 16','s32i a3, a1, 4','movi a4, 1','movi a3, 4','call0 402428ec']);
  change(0x402493ef,'mov a13, a2',['mov.n a13, a12','mov.n a2, a12']);
  change(0x402493f1,'call0 402531c0',['call0 inplace_decode16']);
  change(0x40249459,'l32i a2, a4, 0',['l16si a2, a4, 0']);
  change(0x40249460,'addi a4, a4, 4',['addi.n a4, a4, 2']);
  remove(0x4024948a,0x40249490,['blti a9, 2, 40249490','j 40249655']);
  // B=1: collapse mask is 1 even if gain=0; no scan after overwriting raw X.
  remove(0x40249655,0x4024969a);
  remove(0x4024969c,0x402496a4,['l32i a2, a1, 0','l32i a3, a1, 4','call0 402428d8']);
 }
 return m;
}
function sourceFor(info,elf){
 const literals=new Map(),externals=new Map(),functions=[],literal=address=>{
  if(!literals.has(address))literals.set(address,{name:'ip_literal_'+address.toString(16),value:readAt(elf,address,4).readUInt32LE()});
  return literals.get(address).name;
 };
 function emit(fn,name){
  const changes=edits(fn),rows=base.rows(fn.disassembly),nodes=[];
  for(const r of rows){
   let ops;
   if(changes.has(r.address))ops=changes.get(r.address);
   else {
    let args=r.args.replace(/\s+<[^>]*>$/,'');
    if(/^b|^j$/.test(r.op))args=args.replace(/[0-9a-f]+$/,label(target(r)));
    else if(r.op==='l32r')args=args.replace(/[0-9a-f]+$/,literal(target(r)));
    else if(r.op==='call0'){
     const t=target(r),n='ip_call_'+t.toString(16);externals.set(n,t);args=n;
    }
    ops=[r.op+' '+args];
   }
   nodes.push({old:r.address,ops});
  }
  functions.push({name,original:fn.name,nodes});
 }
 emit(info.functions.alg_unquant,'inplace_unquant');emit(info.functions.decode_pulses,'inplace_decode16');
 const head=`# Generated from accepted linked ASM. Original Opus licensing applies.
# call0 ABI; original 112/48-byte frames, same callees and inline rotation.
# B=1 and 0<K<=32767: |pulse|<=K fits int16. X is halfword-writable DRAM.
# No arena mark/alloc/restore: all remaining callees have no scratch lifetime.
# Fallback leaves the accepted decoder body intact after displaced prologue.
.begin no-transform
.section .text.patch0,"ax",@progbits
 j ip_guard
.section .text.patch1,"ax",@progbits
`;
 let text=head+[...literals.values()].map(x=>x.name+':\n .word 0x'+x.value.toString(16)).join('\n')+'\n';
 for(const f of functions){text+=`.align 4\n.global ${f.name}\n.type ${f.name},@function\n${f.name}:\n`;
  for(const n of f.nodes)text+=`.global ${label(n.old)}\n${label(n.old)}:\n`+n.ops.map(x=>' '+x+'\n').join('');
  text+=`.size ${f.name},.-${f.name}\n`;
 }
 text+=`.global ip_used_end\nip_used_end:\n.space ${capacity}-(.-ip_pool_start),0\n`;
 // The pool label must precede its first word, not the first function.
 text=text.replace('.section .text.patch1,"ax",@progbits\n','.section .text.patch1,"ax",@progbits\nip_pool_start:\n');
 text+=`.section .text.patch2,"ax",@progbits
.global ip_guard
ip_guard:
 bnei a6,1,ip_fallback
 blti a4,1,ip_fallback
 srli a8,a4,15
 bnez a8,ip_fallback
 j inplace_unquant
.global ip_fallback
ip_fallback:
 addi a1,a1,-112
 j ip_resume
.global ip_guard_end
ip_guard_end:
.space ${guardCapacity}-(.-ip_guard),0
.end no-transform
`;
 const script=[...externals].map(([n,a])=>`${n} = 0x${a.toString(16)};`).join('\n')+`\nip_resume = 0x${(site+3).toString(16)};\nSECTIONS {\n`+
  [site,storage,guard].map((a,i)=>` .text.patch${i} 0x${a.toString(16)} : { *(.text.patch${i}) }`).join('\n')+'\n}\n';
 return{text,script,functions,literals:[...literals],externals:[...externals]};
}
function symbols(file){return Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-a',file]).matchAll(/^([0-9a-f]+)\s+\S\s+(.+)$/gm)].map(m=>[m[2],parseInt(m[1],16)]));}
function prepare(){
 const dir=previous.art('candidate'),p=read(path.join(dir,'preflight.json')),m=read(path.join(dir,'manifest.json'));
 const input=path.join(root,'.build',parent,base.elfName),a=fs.readFileSync(input),app=fs.readFileSync(path.join(dir,'app.bin'));
 assert.equal(hash(a),p.candidate_elf_sha256);assert.equal(hash(app),m.app_sha256);
 const info=layout.inspect(parent,[...new Set([...previous.names,'alg_unquant','alg_quant'])],{internalCalls:['quant_partition']});
 for(const n of previous.names)assert.deepEqual(info.functions[n],p.actual_functions[n]);
 const audit=storageAudit.storage(info,input,a);assert.equal(audit.encoder_storage.function_bytes,capacity);
 const source=sourceFor(info,a),d=build('candidate');save(path.join(d,'patches.s'),source.text);save(path.join(d,'patches.ld'),source.script);
 run(path.join(bin,'xtensa-lx106-elf-as.exe'),[path.join(d,'patches.s'),'-o',path.join(d,'patches.o')]);
 const linked=path.join(d,'patches.elf');run(path.join(bin,'xtensa-lx106-elf-ld.exe'),['-e','0','-T',path.join(d,'patches.ld'),'-o',linked,path.join(d,'patches.o')]);
 const object=fs.readFileSync(linked),ss=sections(object),patches=[];
 for(const[i,address,bytes]of[[0,site,3],[1,storage,capacity],[2,guard,guardCapacity]]){
  const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,address);assert.equal(s.bytes,bytes);
  patches.push({address,bytes,before_hex:readAt(a,address,bytes).toString('hex'),after_hex:object.subarray(s.offset,s.offset+bytes).toString('hex')});
 }
 const b=base.patchElf(a,patches);save(path.join(d,base.elfName),b);save(path.join(build('control'),base.elfName),a);
 const syms=symbols(linked);assert.ok(syms.ip_used_end<=storage+capacity);
 const dis=Object.fromEntries(source.functions.map(f=>[f.name,layout.reachableDisassembly(linked,{name:f.name,address:syms[f.name],bytes:(f.name==='inplace_unquant'?syms.inplace_decode16:syms.ip_used_end)-syms[f.name]})]));
 dis.guard=run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d','--start-address=0x'+guard.toString(16),'--stop-address=0x'+syms.ip_guard_end.toString(16),linked]);
 const proof=require('./pvq_inplace_b1_proof.cjs').prove({info,source,syms,dis,before:a,after:b});
 const local={schema:1,parent,dependencies:dependencies(),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),patches,source,syms,dis,functions:info.functions,
  storage:{...audit,encoder_storage:{...audit.encoder_storage,bytes:capacity,used_bytes:syms.ip_used_end-storage,sha256:hash(readAt(a,storage,capacity)),invariant:'Entire encoder function has no decoder-reachable entry; fixed-slot clone and literals use this storage. See inherited full-function call/jump/pointer audit.'}},
  semantic:proof,static_ram_delta:0,stack_delta:0,sections:info.sections};
 save(path.join(d,'local-proof.json'),JSON.stringify(local,null,2)+'\n');
 console.log(JSON.stringify({prepared:true,used_bytes:syms.ip_used_end-storage,capacity,semantic:proof}));return local;
}
function publish(){
 const local=read(path.join(build('candidate'),'local-proof.json'));assert.deepEqual(local.dependencies,dependencies());
 // Expensive complete lineage validation is mandatory before OTA publication.
 const verified=previous.verifyPair();assert.equal(verified.proof.candidate_elf_sha256,local.parent_elf_sha256);
 const dir=previous.art('candidate'),m=read(path.join(dir,'manifest.json')),images={},manifests={};
 for(const t of['control','candidate']){
  const file=path.join(build(t),base.elfName),elf=fs.readFileSync(file);assert.equal(hash(elf),local[t==='control'?'parent_elf_sha256':'candidate_elf_sha256']);
  run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),file]);
  images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.equal(images[t].length,m.bytes);
  manifests[t]={...m,purpose:'Experimental in-place B1 PVQ raw ASM benchmark, not production',app_sha256:hash(images[t]),post_link_inplace_b1_variant:t,post_link_recipe_sha256_lf:sourceHash(__filename),post_link_bundle_dependencies:dependencies(),post_link_parent_app_sha256:m.app_sha256};
 }
 assert.deepEqual(images.control,fs.readFileSync(path.join(dir,'app.bin')));
 local.imageProof=base.compareApps(images.control,images.candidate,local.patches);local.parent_lineage_verified=true;
 for(const t of['control','candidate']){
  save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(dir,'sdkconfig')));
 }
 save(path.join(art('candidate'),'preflight.json'),JSON.stringify(local,null,2)+'\n');
 for(const file of['patches.s','patches.elf'])save(path.join(art('candidate'),file),fs.readFileSync(path.join(build('candidate'),file)));
 save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(fs.readFileSync(path.join(build('control'),base.elfName)),{level:9}));
 console.log('PUBLISHED',manifests.candidate.app_sha256);return local;
}
function verifyPair(){
 const p=read(path.join(art('candidate'),'preflight.json'));assert.deepEqual(p.dependencies,dependencies());assert.equal(p.parent_lineage_verified,true);
 const a=zlib.gunzipSync(fs.readFileSync(path.join(art('candidate'),'parent.elf.gz'))),b=base.patchElf(a,p.patches);
 assert.equal(hash(a),p.parent_elf_sha256);assert.equal(hash(b),p.candidate_elf_sha256);
 assert.deepEqual(p.patches.map(({address,bytes})=>({address,bytes})),[{address:site,bytes:3},{address:storage,bytes:capacity},{address:guard,bytes:guardCapacity}]);
 assert.deepEqual(sourceFor({functions:p.functions},a),p.source);
 assert.equal(fs.readFileSync(path.join(art('candidate'),'patches.s'),'utf8'),p.source.text);
 const objectFile=path.join(art('candidate'),'patches.elf'),object=fs.readFileSync(objectFile),ss=sections(object);
 assert.deepEqual(symbols(objectFile),p.syms);
 for(const[i,x]of p.patches.entries()){
  const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,x.address);assert.equal(s.bytes,x.bytes);
  assert.equal(object.subarray(s.offset,s.offset+s.bytes).toString('hex'),x.after_hex);
 }
 for(const f of p.source.functions){
  const end=f.name==='inplace_unquant'?p.syms.inplace_decode16:p.syms.ip_used_end;
  assert.equal(layout.reachableDisassembly(objectFile,{name:f.name,address:p.syms[f.name],bytes:end-p.syms[f.name]}),p.dis[f.name]);
 }
 const guardDis=run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d','--start-address=0x'+guard.toString(16),'--stop-address=0x'+p.syms.ip_guard_end.toString(16),objectFile]);
 assert.deepEqual(base.rows(guardDis),base.rows(p.dis.guard));
 assert.deepEqual(require('./pvq_inplace_b1_proof.cjs').prove({info:{functions:p.functions},source:p.source,syms:p.syms,dis:p.dis,before:a,after:b}),p.semantic);
 const verified=previous.verifyPair();assert.equal(verified.proof.candidate_elf_sha256,p.parent_elf_sha256);
 for(const n of previous.names)assert.deepEqual(p.functions[n],verified.proof.actual_functions[n]);
 const manifests={},apps={};for(const t of['control','candidate']){
  manifests[t]=read(path.join(art(t),'manifest.json'));apps[t]=fs.readFileSync(path.join(art(t),'app.bin'));
  assert.equal(hash(apps[t]),manifests[t].app_sha256);assert.equal(apps[t].length,manifests[t].bytes);
  assert.deepEqual(manifests[t].post_link_bundle_dependencies,dependencies());assert.equal(manifests[t].post_link_inplace_b1_variant,t);
 }
 for(const k of new Set([...Object.keys(manifests.control),...Object.keys(manifests.candidate)]))if(!['app_sha256','post_link_inplace_b1_variant'].includes(k))assert.deepEqual(manifests.control[k],manifests.candidate[k]);
 assert.deepEqual(apps.control,fs.readFileSync(path.join(previous.art('candidate'),'app.bin')));
 assert.deepEqual(base.compareApps(apps.control,apps.candidate,p.patches),p.imageProof);
 return{proof:p,manifests};
}
module.exports={variant,parent,build,art,site,storage,capacity,guard,guardCapacity,label,clean,edits,sourceFor,prepare,publish,verifyPair,dependencies,read};
if(require.main===module){if(process.argv.includes('--publish'))publish();else if(process.argv.includes('--verify')){verifyPair();console.log('VERIFIED');}else prepare();}
