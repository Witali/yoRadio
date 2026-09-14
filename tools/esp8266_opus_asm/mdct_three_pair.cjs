// Frozen-layout three-table MDCT ASM experiment, not production/default.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {root,hash,sourceHash,run}=require('./export.cjs'),base=require('./frozen_reloads.cjs'),pair=require('./mdct_bitrev_pair.cjs');
const {sections,inspectImage,wordOffset}=require('./frozen_div.cjs'),{inspect}=require('./report_layout.cjs');
const parent=pair.parent,variant=t=>'esp8266-opus-mdct-three-pair-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t)),build=t=>path.join(root,'.build',variant(t));
const names=pair.names,sourceFile=path.join(__dirname,'mdct_three_pair.s');
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe';
const esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function save(p,b){if(typeof b==='string')b=Buffer.from(b);fs.mkdirSync(path.dirname(p),{recursive:true});if(fs.existsSync(p))assert.deepEqual(fs.readFileSync(p),b,'Existing evidence differs: '+p);else fs.writeFileSync(p,b);}
function target(r){const m=r.args.match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]+>$/);assert.ok(m,'Unresolved branch');return parseInt(m[1],16);}
function findPatch(fn){const rs=base.rows(fn.disassembly),live=pair.liveness(fn,pair.findPatch(fn)),address=live.loop_entry,bytes=live.loop_back+3-address;
 assert.equal(bytes,193);assert.equal(address,0x40247268);assert.equal(rs.find(r=>r.address===address).text,'l32i a7, a1, 32');
 for(const r of rs.filter(r=>/^b|^j$/.test(r.op)))if(r.address<address||r.address>=address+bytes)assert.ok(target(r)<=address||target(r)>=address+bytes,'Interior entry');
 return {address,bytes};}
function validateOutside(before,after,p){const outside=r=>r.address<p.address||r.address>=p.address+p.bytes;assert.deepEqual(base.rows(before).filter(outside),base.rows(after).filter(outside));}
function tables(file,info){const proof=pair.tables(file,info),elf=fs.readFileSync(file),word=a=>elf.readUInt32LE(wordOffset(elf,a)),trig=word(proof.mode.address+80);
 let offset=0;for(const x of proof.supported_standard_transforms){const t0=trig+offset,t1=t0+2*x.n;assert.equal(t0%4,0);assert.equal(t1%4,0);assert.equal(x.n%2,0);
  for(const address of [t0,t1])assert.ok(sections(elf).some(s=>s.type===1&&s.address>=0x40200000&&address>=s.address&&address+x.n*2<=s.address+s.bytes));
  x.t0=t0;x.t1=t1;x.trig_sha256=hash(elf.subarray(wordOffset(elf,t0),wordOffset(elf,t0)+4*x.n));offset+=4*x.n;}
 return {...proof,trig,scope:proof.scope+' t0/t1 and bitrev begin at word boundaries and advance by2; even N4 guarantees shared phase and no overread.'};}
// Canonical modular32 sums: distribute only ADD/SUB/SLLI, NEVER SRAI.
// Every multiply/rounding remains an opaque atom; arbitrary32-bit PCM allowed.
const atom=s=>({[s]:1}),key=v=>typeof v==='number'?'#'+(v>>>0):JSON.stringify(v);
function scale(v,n){if(typeof v==='number')return Math.imul(v,n)>>>0;const out={};for(const k of Object.keys(v).sort()){const c=Math.imul(v[k],n)>>>0;if(c)out[k]=c;}return Object.keys(out).length?out:0;}
function add(a,b){if(typeof a==='number'&&typeof b==='number')return (a+b)>>>0;const out={};for(const v of [a,b])for(const [k,c]of Object.entries(typeof v==='number'?(v?{'1':v>>>0}:{}):v))out[k]=((out[k]||0)+c)>>>0;return scale(out,1);}
function binary(op,a,b){if(typeof a==='number'&&typeof b==='number'){if(op==='mull')return Math.imul(a,b)>>>0;if(op==='and')return (a&b)>>>0;}
 if(op==='mull'){const args=[key(a),key(b)].sort();return atom('mul32('+args.join(',')+')');}assert.fail('Unsupported symbolic binary '+op);}
function shift(op,a,n){assert.ok(n>=0&&n<=31);if(op==='slli')return scale(a,2**n);if(typeof a==='number')return (a>>n)>>>0;return atom('sar'+n+'('+key(a)+')');}
function interpret(rs,p,regs,memory,iterations){const state=structuredClone(regs),mem=new Map(memory),map=new Map(rs.map(r=>[r.address,r])),writes=[],loads=[],boundaries=[];let pc=p.address,steps=0;
 while(pc!==p.address+p.bytes){assert.ok(++steps<=iterations*100,'Unexpected loop');const r=map.get(pc);assert.ok(r,'Invalid instruction boundary');const a=r.args.split(/,\s*/),[d,s,n]=a;pc+=r.bytes;
  const address=(baseReg,off)=>{assert.equal(typeof state[baseReg],'number','Symbolic memory address');const x=(state[baseReg]+Number(off))>>>0;assert.equal(x%4,0,'Unaligned32 access');return x;};
  switch(r.op.replace('.n','')){
   case 'movi':state[d]=Number(s)>>>0;break;
   case 'l32i':{const x=address(s,n);assert.ok(mem.has(x),'Unmapped read '+x.toString(16));state[d]=structuredClone(mem.get(x));loads.push(x);break;}
   case 's32i':{const x=address(s,n);mem.set(x,structuredClone(state[d]));writes.push({address:x,value:structuredClone(state[d])});break;}
   case 'add':state[d]=add(state[s],state[n]);break;
   case 'sub':state[d]=add(state[s],scale(state[n],-1));break;
   case 'addi':state[d]=add(state[s],Number(n)>>>0);break;
   case 'and':case 'mull':state[d]=binary(r.op,state[s],state[n]);break;
   case 'slli':case 'srai':state[d]=shift(r.op,state[s],Number(n));break;
   case 'extui':{assert.equal(n,'0');assert.equal(a[3],'16');state[d]=typeof state[s]==='number'?state[s]&65535:atom('lo16('+key(state[s])+')');break;}
   case 'bbsi':assert.equal(s,'1');assert.equal(typeof state[d],'number');if(state[d]&2)pc=target(r);break;
   case 'beq':assert.equal(typeof state[d],'number');assert.equal(typeof state[s],'number');if(state[d]===state[s])pc=target(r);break;
   case 'j':pc=target(r);break;
   default:assert.fail('Unproved opcode '+r.op);
  }
  if(pc===p.address||pc===p.address+p.bytes)boundaries.push({state:structuredClone(state),steps,loads:loads.length});
 }assert.equal(boundaries.length,iterations);return {state,writes,loads,boundaries,steps};}
function prove(before,after,p,t){validateOutside(before,after,p);const select=s=>base.rows(s).filter(r=>r.address>=p.address&&r.address<p.address+p.bytes),a=select(before),b=select(after),phases=[];
 // Actual tables cover every transform. Prove each pair for arbitrary PCM,
 // not just a particular test packet. Stack and output values/sequence exact.
 let pairs=0;for(const transform of t.supported_standard_transforms)for(let i=0;i<transform.n;i+=2){
  const sp=0x3ffe0000,xp1=0x3ffe1000,xp2=0x3ffe1800,yp=0x3ffe2000,regs=Object.fromEntries(Array.from({length:16},(_,k)=>['a'+k,atom('R'+k)]));Object.assign(regs,{a1:sp,a3:xp1,a12:transform.address+i*2,a13:transform.t1+i*2});
  const memory=new Map([[sp+32,(-2*transform.n)>>>0],[sp+4,xp2],[sp+12,yp],[sp+24,(-8)>>>0],[sp+8,8],[sp+28,transform.address+(i+2)*2]]);
  for(let j=0;j<2;j++){memory.set(xp1+j*8,atom('X'+j));memory.set(xp2-j*8,atom('Y'+j));}
  const word=(transform.values[i]&65535)|((transform.values[i+1]&65535)<<16);memory.set(transform.address+i*2,word>>>0);
  memory.set(transform.t0+i*2,atom('T0'));memory.set(transform.t1+i*2,atom('T1'));
  const old=interpret(a,p,regs,memory,2),now=interpret(b,p,regs,memory,2);assert.deepEqual(now.writes,old.writes,'PCM or stack write differs');
  for(let j=0;j<2;j++)for(const r of ['a1','a3','a9','a12','a13'])assert.deepEqual(now.boundaries[j].state[r],old.boundaries[j].state[r],'Live loop register '+r);
  // Only invariant sp+32 is intentionally no longer read on the high half.
  assert.ok(!old.writes.some(w=>w.address===sp+32));assert.ok(!now.writes.some(w=>w.address===sp+32));
  assert.equal(old.loads.filter(v=>v===sp+32).length,2);assert.equal(now.loads.filter(v=>v===sp+32).length,1);
  const nonTable=xs=>xs.filter(v=>v<0x40200000&&v!==sp+32);assert.deepEqual(nonTable(now.loads),nonTable(old.loads),'Changed PCM/stack read order');
  assert.equal(old.loads.filter(v=>v>=0x40200000).length,6);assert.equal(now.loads.filter(v=>v>=0x40200000).length,3);pairs++;
  if(!phases.length)for(let j=0;j<2;j++)phases.push({half:j,old_instructions:old.boundaries[j].steps-(old.boundaries[j-1]?.steps||0),new_instructions:now.boundaries[j].steps-(now.boundaries[j-1]?.steps||0)});
 }
 // At exit a0 is killed by FFT CALL0. a14/a15 are old arithmetic scratch;
 // a15 becomes yp in original tail, a14 overwritten before post-FFT read.
 const rs=base.rows(after),tail=rs.filter(r=>r.address>=p.address+p.bytes&&r.address<=0x40247331);assert.deepEqual(tail.map(r=>r.text),['l32i a3, a1, 56','mov a15, a9','l32i a2, a3, 8','mov a3, a9','call0 40253834 <opus_fft_impl>']);
 assert.ok(rs.some(r=>r.text==='s32i a0, a1, 92'));assert.ok(rs.some(r=>r.text==='l32i a0, a1, 92'));
 const post=rs.filter(r=>r.address>=0x4024737d&&r.address<0x402473fa),first=post.find(r=>/\ba14\b/.test(r.args));assert.equal(first.text,'mull a14, a5, a4');
 return {pairs,phases,arbitrary_pcm32:true,arbitrary_trig32:true,pcm_and_stack_writes_exact:true,pcm_read_order_exact:true,table_loads_per_pair:{old:6,new:3},sar:'unchanged',frame_bytes:96};}
function manifestPair(a,b){assert.equal(a.post_link_three_pair_variant,'control');assert.equal(b.post_link_three_pair_variant,'candidate');for(const k of new Set([...Object.keys(a),...Object.keys(b)]))if(!['purpose','app_sha256','post_link_three_pair_variant'].includes(k))assert.deepEqual(a[k],b[k],k);
 for(const m of [a,b]){assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.post_link_mdct_variant,'candidate');assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_division_benchmark,false);}}
function generate(){const oldProof=require('./report_mdct_half.cjs').verifyPair();require('./verify.cjs').verify('bands-tell-inline-asm');const dir=path.join(root,'firmware/development',parent),m=read(path.join(dir,'manifest.json')),file=path.join(root,'.build',parent,base.elfName),a=fs.readFileSync(file),app=fs.readFileSync(path.join(dir,'app.bin'));assert.equal(hash(a),oldProof.proof.candidate_elf_sha256);assert.equal(hash(app),m.app_sha256);
 const info=inspect(parent,names),fn=info.functions[names[0]],p=findPatch(fn),tableProof=tables(file,info),source=fs.readFileSync(sourceFile,'utf8').replace(/\r\n/g,'\n');
 fs.mkdirSync(build('candidate'),{recursive:true});const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o'),linked=path.join(build('candidate'),'patches.elf'),script=path.join(build('candidate'),'patches.ld');save(asm,source);save(script,`SECTIONS { .text.patch0 0x${p.address.toString(16)} : { *(.text.patch0) } }\n`);
 run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);run(path.join(bin,'xtensa-lx106-elf-ld.exe'),['-e','0','-T',script,'-o',linked,obj]);const object=fs.readFileSync(linked),sec=sections(object).find(s=>s.name==='.text.patch0');assert.equal(sec.address,p.address);assert.equal(sec.bytes,p.bytes);p.after_hex=object.subarray(sec.offset,sec.offset+sec.bytes).toString('hex');const off=base.offsetAt(a,p.address,p.bytes);p.before_hex=a.subarray(off,off+p.bytes).toString('hex');
 const b=base.patchElf(a,[p]),images={},manifests={},logs={};for(const [t,bytes]of [['control',a],['candidate',b]]){const to=path.join(build(t),base.elfName);save(to,bytes);logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),to]);images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
  manifests[t]={...m,purpose:'Frozen-layout '+t+' MDCT three-table pair ASM benchmark; not production',app_sha256:hash(images[t]),post_link_three_pair_variant:t,post_link_recipe_sha256_lf:sourceHash(__filename),post_link_asm_sha256_lf:sourceHash(sourceFile),post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(a)};}
 assert.deepEqual(images.control,app);manifestPair(manifests.control,manifests.candidate);const actual=inspect(variant('candidate'),names);assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);const symbolicProof=prove(fn.disassembly,actual.functions[names[0]].disassembly,p,tableProof);for(const n of names.slice(1))assert.deepEqual(actual.functions[n],info.functions[n]);assert.deepEqual(tables(path.join(build('candidate'),base.elfName),actual),tableProof);
 const proof={schema:1,parent,recipe_sha256_lf:sourceHash(__filename),asm_sha256_lf:sourceHash(sourceFile),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),patches:[p],tables:tableProof,symbolicProof,static_ram_delta:0,stack_delta:0,app_bytes:app.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,imageProof:base.compareApps(images.control,images.candidate,[p]),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),logs}};
 for(const t of ['control','candidate']){save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(dir,'sdkconfig')));}
 save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.elf'),object);save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify({passed:true,sha256:manifests.candidate.app_sha256,app_bytes:app.length,ram_delta:0,symbolicProof}));return proof;}
module.exports={parent,variant,art,build,names,sourceFile,target,findPatch,validateOutside,tables,interpret,prove,manifestPair,generate,read};if(require.main===module)generate();
