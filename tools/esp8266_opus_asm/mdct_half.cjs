// Frozen-layout experiment over saved GCC ASM, not a production default.
// Reorder signed-half extraction in MDCT: high half skips two redundant shifts.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {root,hash,sourceHash,run}=require('./export.cjs');
const f=require('./frozen_reloads.cjs'),{sections,inspectImage}=require('./frozen_div.cjs'),{inspect}=require('./report_layout.cjs');
const parent=f.parent,variant=t=>'esp8266-opus-mdct-half-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t)),build=t=>path.join(root,'.build',variant(t));
const names=['clt_mdct_backward_c'];
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe';
const esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const specs=[{ptr:'a4',mask:'a9',out:'a10',word:'a2'},{ptr:'a13',mask:'a4',out:'a9',word:'a2'},{ptr:'a12',mask:'a7',out:'a6',word:'a2'},
 {ptr:'a9',mask:'a10',out:'a8',word:'a5'},{ptr:'a11',mask:'a6',out:'a7',word:'a5'}];
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function save(p,b){if(typeof b==='string')b=Buffer.from(b);fs.mkdirSync(path.dirname(p),{recursive:true});if(fs.existsSync(p))assert.deepEqual(fs.readFileSync(p),b,'Existing evidence differs: '+p);else fs.writeFileSync(p,b);}
function target(r){const m=r.args.match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]+>$/);assert.ok(m,'Unresolved branch');return parseInt(m[1],16);}
function findPatch(fn,s){
 assert.equal(new Set(Object.values(s)).size,4);const rs=f.rows(fn.disassembly),hits=[];
 for(let i=0;i<rs.length-5;i++)if(rs[i].text===`movi ${s.mask}, 2`&&rs[i+1].text===`slli ${s.out}, ${s.word}, 16`)hits.push(i);
 assert.equal(hits.length,1,'Expected unique halfword sequence');const group=rs.slice(hits[0],hits[0]+6),address=group[0].address,end=address+17;
 assert.deepEqual(group.map(r=>r.bytes),[2,3,3,3,3,3]);group.slice(1).forEach((r,i)=>assert.equal(r.address,group[i].address+group[i].bytes));
 assert.equal(group[2].text,`srai ${s.out}, ${s.out}, 16`);assert.equal(group[3].op,'bnone');assert.ok(group[3].args.startsWith(`${s.ptr}, ${s.mask}, `));
 assert.equal(group[4].text,`srai ${s.out}, ${s.word}, 16`);assert.equal(group[5].op,'j');assert.equal(target(group[3]),end);assert.equal(target(group[5]),end);
 for(const r of rs.filter(r=>/^b|^j$/.test(r.op)))assert.ok(target(r)<=address||target(r)>=end,'Interior branch entry');
 return {...s,address,bytes:17,before:group};
}
function candidateOps(p,i){return [`movi.n ${p.mask}, 2`,`bbsi ${p.ptr}, 1, .Lhigh${i}`,`slli ${p.out}, ${p.word}, 16`,`srai ${p.out}, ${p.out}, 16`,`j .Lend${i}`,`.Lhigh${i}:`,`srai ${p.out}, ${p.word}, 16`,`.Lend${i}:`];}
function validateActual(before,after,patches){
 const a=f.rows(before),b=f.rows(after);const inside=r=>patches.some(p=>r.address>=p.address&&r.address<p.address+p.bytes);
 assert.deepEqual(a.filter(r=>!inside(r)),b.filter(r=>!inside(r)),'Instructions outside patches');
 for(const p of patches){const rs=b.filter(r=>r.address>=p.address&&r.address<p.address+p.bytes);assert.equal(rs.length,6);
  assert.deepEqual(rs.map(r=>r.address-p.address),[0,2,5,8,11,14]);assert.deepEqual(rs.map(r=>r.bytes),[2,3,3,3,3,3]);
  assert.equal(rs[0].text,`movi ${p.mask}, 2`);assert.ok(['bbsi','bbsi.l'].includes(rs[1].op));assert.ok(rs[1].args.startsWith(`${p.ptr}, 1, `));assert.equal(target(rs[1]),p.address+14);
  assert.equal(rs[2].text,`slli ${p.out}, ${p.word}, 16`);assert.equal(rs[3].text,`srai ${p.out}, ${p.out}, 16`);assert.equal(rs[4].op,'j');assert.equal(target(rs[4]),p.address+17);assert.equal(rs[5].text,`srai ${p.out}, ${p.word}, 16`);
 }
}
// Symbolically execute actual disassembled blocks using bit-origin vectors.
// Every bit of every other register is independent; only address bit1 is fixed.
// Both exits must preserve all 16 registers and SAR for every 32-bit loaded word.
function symbolic(rs,ptr,half){
 const start=rs[0].address,end=rs.at(-1).address+rs.at(-1).bytes,by=new Map(rs.map(r=>[r.address,r]));
 const state=Object.fromEntries(Array.from({length:16},(_,i)=>['a'+i,Array.from({length:32},(_,b)=>`a${i}.${b}`)]));state[ptr][1]=half;const initial=structuredClone(state);let pc=start,steps=0;
 const shift=(v,n,left)=>Array.from({length:32},(_,b)=>left?(b<n?0:v[b-n]):v[Math.min(31,b+n)]);
 while(pc!==end){assert.ok(++steps<=8,'Unexpected loop');const r=by.get(pc);assert.ok(r,'Instruction boundary');const args=r.args.split(/,\s*/),[d,s,n]=args;pc+=r.bytes;
  if(r.op.replace('.n','')==='movi'){assert.equal(Number(s),2);state[d]=Array.from({length:32},(_,b)=>b===1?1:0);}
  else if(r.op==='slli'||r.op==='srai'){assert.equal(Number(n),16);state[d]=shift(state[s],16,r.op==='slli');}
  else if(r.op==='bnone'){assert.deepEqual(state[s],Array.from({length:32},(_,b)=>b===1?1:0));assert.equal(typeof state[d][1],'number');if(!state[d][1])pc=target(r);}
  else if(r.op==='bbsi'){assert.equal(s,'1');assert.equal(typeof state[d][1],'number');if(state[d][1])pc=target(r);}
  else if(r.op==='j')pc=target(r);else throw Error('Unproved operation '+r.op);
 }
 return {state,initial,sar:'unchanged',steps};
}
function proofBlocks(before,after,patches){let paths=0;for(const p of patches){
 const select=text=>f.rows(text).filter(r=>r.address>=p.address&&r.address<p.address+p.bytes);
 for(const half of [0,1]){const a=symbolic(select(before),p.ptr,half),b=symbolic(select(after),p.ptr,half);assert.deepEqual(a.state,b.state);assert.equal(a.sar,b.sar);
  const expected=structuredClone(a.initial);expected[p.mask]=Array.from({length:32},(_,i)=>i===1?1:0);expected[p.out]=Array.from({length:32},(_,i)=>p.word+'.'+Math.min(half?31:15,i+(half?16:0)));assert.deepEqual(b.state,expected);
  assert.equal(a.steps,half?6:4);assert.equal(b.steps,half?3:5);paths++;}
 }return {symbolic_paths:paths,scope:'All register bits and both pointer parities; signed int16 exact, no memory/SAR/stack changes',old_low_high_instructions:[4,6],new_low_high_instructions:[5,3]};}
function manifestPair(a,b){assert.equal(a.post_link_mdct_variant,'control');assert.equal(b.post_link_mdct_variant,'candidate');
 for(const k of new Set([...Object.keys(a),...Object.keys(b)]))if(!['purpose','app_sha256','post_link_mdct_variant'].includes(k))assert.deepEqual(a[k],b[k],k);
 for(const m of [a,b]){assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.diagnostic,true);assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_division_benchmark,false);}}
function generate(){
 require('./verify.cjs').verify('bands-tell-inline-asm');const dir=path.join(root,'firmware/development',parent),m=read(path.join(dir,'manifest.json'));
 const a=fs.readFileSync(path.join(root,'.build',parent,f.elfName)),app=fs.readFileSync(path.join(dir,'app.bin'));assert.equal(hash(app),m.app_sha256.toLowerCase());assert.equal(app.length,m.bytes);
 const info=inspect(parent,names);assert.equal(hash(a),info.elf_sha256);const fn=info.functions[names[0]],patches=specs.map(s=>findPatch(fn,s));
 const source='# MDCT signed-half selection, saved GCC ASM / Xtensa LX106 call0.\n# Same17-byte slots; registers, SAR, aligned L32I accesses, stack96 and all other code unchanged.\n# Preserve mask=2. High half:3 instructions instead of6; low:5 instead of4.\n# No new alignment/size assumptions; works for either half including signed extremes.\n# Baseline C and GCC snapshot unchanged; this post-link diagnostic is OFF by default.\n'+patches.map((p,i)=>`\n# clt_mdct_backward_c: pointer ${p.ptr}, loaded word ${p.word}, result ${p.out}.\n.section .text.patch${i},"ax",@progbits\n.begin no-transform\n${candidateOps(p,i).join('\n')}\n.end no-transform\n`).join('');
 fs.mkdirSync(build('candidate'),{recursive:true});const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o'),linked=path.join(build('candidate'),'patches.elf');save(asm,source);
 const script=path.join(build('candidate'),'patches.ld');save(script,'SECTIONS {\n'+patches.map((p,i)=>`.text.patch${i} 0x${p.address.toString(16)} : { *(.text.patch${i}) }`).join('\n')+'\n}\n');
 run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);run(path.join(bin,'xtensa-lx106-elf-ld.exe'),['-e','0','-T',script,'-o',linked,obj]);
 const object=fs.readFileSync(linked),ss=sections(object);patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.ok(s);assert.equal(s.bytes,p.bytes);assert.equal(s.address,p.address);p.after_hex=object.subarray(s.offset,s.offset+s.bytes).toString('hex');const off=f.offsetAt(a,p.address,p.bytes);p.before_hex=a.subarray(off,off+p.bytes).toString('hex');});
 const b=f.patchElf(a,patches),images={},manifests={},logs={};for(const [t,bytes]of [['control',a],['candidate',b]]){
  const to=path.join(build(t),f.elfName);save(to,bytes);logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),to]);images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
  manifests[t]={...m,purpose:'Frozen-layout '+t+' MDCT halfword ASM benchmark; not production',app_sha256:hash(images[t]),post_link_mdct_variant:t,post_link_recipe_sha256_lf:sourceHash(__filename),post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(a)};
 }
 assert.deepEqual(images.control,app);manifestPair(manifests.control,manifests.candidate);const actual=inspect(variant('candidate'),names);assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);
 validateActual(fn.disassembly,actual.functions[names[0]].disassembly,patches);const symbolicProof=proofBlocks(fn.disassembly,actual.functions[names[0]].disassembly,patches);
 const proof={schema:1,parent,recipe_sha256_lf:sourceHash(__filename),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),patches,symbolicProof,static_ram_delta:0,stack_delta:0,app_bytes:app.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,imageProof:f.compareApps(images.control,images.candidate,patches),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),logs}};
 for(const t of ['control','candidate']){save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(dir,'sdkconfig')));}
 save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.elf'),object);save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');
 console.log(JSON.stringify({passed:true,patches:patches.length,symbolicProof,app_bytes:app.length,ram_delta:0,sha256:manifests.candidate.app_sha256}));return proof;
}
module.exports={parent,variant,art,build,names,specs,findPatch,validateActual,symbolic,proofBlocks,manifestPair,generate};if(require.main===module)generate();
