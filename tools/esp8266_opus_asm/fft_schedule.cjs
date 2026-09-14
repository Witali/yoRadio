// Independent frozen-layout ASM experiment; never edits C or saved GCC ASM.
const fs = require('node:fs'), path = require('node:path'), zlib = require('node:zlib'), assert = require('node:assert/strict');
const {root,hash,sourceHash,run} = require('./export.cjs');
const base = require('./frozen_reloads.cjs'), post = require('./mdct_post_pair.cjs');
const {sections,inspectImage} = require('./frozen_div.cjs'), {inspect} = require('./report_layout.cjs');
const parent = post.variant('candidate'), variant = t => 'esp8266-opus-fft-schedule-'+t+'-v1';
const art = t => path.join(root,'firmware/development',variant(t)), build = t => path.join(root,'.build',variant(t));
const names = [...new Set([...post.names,'opus_fft_impl'])], read = post.read;
const sourceFile = path.join(__dirname,'fft_schedule.s');
const bin = 'C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python = 'C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe';
const esptool = 'C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const original = ['l32i a2, a1, 32','l32i a3, a1, 32','l32i a2, a2, 0','l32i a3, a3, 4','s32i a2, a1, 156','s32i a3, a1, 164','l32i a4, a1, 100','l32i a6, a4, 0'];
const replacement = ['l32i a3, a1, 32','l32i a4, a1, 100','l32i a2, a3, 0','l32i a3, a3, 4','s32i a2, a1, 156','s32i a3, a1, 164','l32i a6, a4, 0'];
function save(file,bytes) {
  if (typeof bytes==='string') bytes=Buffer.from(bytes);
  fs.mkdirSync(path.dirname(file),{recursive:true});
  if(fs.existsSync(file)) assert.deepEqual(fs.readFileSync(file),bytes,'Existing evidence differs: '+file);
  else fs.writeFileSync(file,bytes);
}
// The only stores are to distinct PRIVATE stack words. Model possible aliasing
// of PCM/twiddle pointers with those words: reads after stores use explicit ITE.
// Moving sp+100 before stores is safe because 100 != 156 and 100 != 164.
function decode(text) {
  const m=base.normalized(text).match(/^(l32i|s32i) a(\d+), a(\d+), (\d+)$/);
  assert.ok(m,'Unexpected instruction: '+text);
  const [d,s,n]=m.slice(2).map(Number); assert.ok(d<16&&s<16);assert.equal(n%4,0);
  if(m[1]==='l32i')assert.notEqual(d,1);else assert.equal(s,1,'Only private stack stores allowed');
  return {op:m[1],d,s,n};
}
function distinctStack(a,b) {
  return /^R1\+\d+$/.test(a)&&/^R1\+\d+$/.test(b)&&a!==b;
}
function symbolic(ops) {
  const registers=Array.from({length:16},(_,i)=>'R'+i),events=[],stores=[];
  for(const text of ops) {
    const {op,d,s,n}=decode(text),address=registers[s]+'+'+n;
    if(op==='s32i') {const v={address,value:registers[d]};stores.push(v);events.push({op,...v});}
    else {
      let value='MEM['+address+']';
      for(const w of stores)if(!distinctStack(address,w.address))
        value=address===w.address?w.value:'ITE('+address+'=='+w.address+','+w.value+','+value+')';
      registers[d]=value;events.push({op,address,value});
    }
  }
  return {registers,events,stores};
}
function dataEvents(events) {
  return events.filter(e=>!(e.op==='l32i'&&['R1+32','R1+100'].includes(e.address)));
}
function prove(before,after) {
  const a=symbolic(before),b=symbolic(after);
  assert.equal(a.events.length,8);assert.equal(b.events.length,7);
  assert.deepEqual(a.registers,b.registers,'Live registers or aliased reads changed');
  assert.deepEqual(a.stores,b.stores,'Stack writes changed');
  assert.deepEqual(dataEvents(a.events),dataEvents(b.events),'PCM/twiddle/store event order changed');
  const counts=x=>['R1+32','R1+100'].map(address=>x.events.filter(e=>e.op==='l32i'&&e.address===address).length);
  assert.deepEqual(counts(a),[2,1]);assert.deepEqual(counts(b),[1,1]);
  return {scope:'All uint32 registers/data; possible PCM/twiddle alias with private stores. Only stable stack32/100 read order changes.',before:a,after:b,removed_private_stack_reads:1,old_instructions:8,new_instructions:7};
}
function numeric(ops,initial) {
  const registers=initial.registers.map(x=>x>>>0),memory=new Map(initial.memory),events=[];
  const read=address=>memory.has(address)?memory.get(address):(Math.imul(address^initial.seed,0x45d9f3b)>>>0);
  for(const text of ops) {
    const {op,d,s,n}=decode(text),address=(registers[s]+n)>>>0;assert.equal(address%4,0);
    if(op==='l32i'){registers[d]=read(address);events.push({op,address,value:registers[d]});}
    else {memory.set(address,registers[d]);events.push({op,address,value:registers[d]});}
  }
  return {registers,memory:[...memory].sort((a,b)=>a[0]-b[0]),events};
}
function numericProof(before,after) {
  let cases=0;const stack=0x3ffe8000;
  const addresses=[stack,stack+28,stack+32,stack+96,stack+100,stack+152,stack+156,stack+164,0x3fff1000];
  for(const pcm of addresses)for(const twiddle of addresses)for(const seed of[0,1,0xffffffff,7349,0x80000000,0x7fffffff,0x55555555,0xaaaaaaaa]){
    const registers=Array.from({length:16},(_,i)=>Math.imul(seed+i+1,0x45d9f3b)>>>0);registers[1]=stack;
    const initial={registers,memory:[[stack+32,pcm],[stack+100,twiddle]],seed};
    const a=numeric(before,initial),b=numeric(after,initial);
    assert.deepEqual(a.registers,b.registers);assert.deepEqual(a.memory,b.memory);
    const keep=events=>events.filter(e=>!(e.op==='l32i'&&[stack+32,stack+100].includes(e.address)));
    // Aliased data reads may share these addresses. Symbolic proof, rather than
    // this numeric filter, establishes their semantic identities/order.
    assert.deepEqual(keep(a.events),keep(b.events));cases++;
  }
  return {cases,pcm_addresses:addresses,twiddle_addresses:addresses,scope:'Numeric alias/edge regression, supplemental to symbolic proof.'};
}
function findPatch(fn) {
  const rs=base.rows(fn.disassembly),hits=[];
  for(let i=0;i<rs.length;i++) if(original.every((op,j)=>rs[i+j]?.text===op)) hits.push(i);
  assert.equal(hits.length,1,'Unique pinned FFT load group');
  const group=rs.slice(hits[0],hits[0]+8),address=group[0].address,bytes=19;
  assert.equal(address,0x40254126);
  const widths=[2,2,2,2,3,3,3,2];let cursor=address;group.forEach((r,i)=>{assert.equal(r.bytes,widths[i]);assert.equal(r.address,cursor);cursor+=r.bytes;});
  for(const r of rs) {
    assert.ok(!['jx','callx0','callx4','callx8','callx12'].includes(r.op),'Indirect target needs a separate proof');
    if(/^b|^j$|^call/.test(r.op)) {
      const m=r.args.match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]+>$/);
      if(m) {const target=parseInt(m[1],16);assert.ok(target<=address||target>=address+bytes,'Interior entry');}
    }
  }
  prove(original,replacement);
  return {address,bytes};
}
function manifestPair(a,b) {
  assert.equal(a.post_link_fft_schedule_variant,'control');assert.equal(b.post_link_fft_schedule_variant,'candidate');
  for(const key of new Set([...Object.keys(a),...Object.keys(b)]))
    if(!['purpose','app_sha256','post_link_fft_schedule_variant'].includes(key)) assert.deepEqual(a[key],b[key],key);
  for(const m of[a,b]) {
    assert.equal(m.post_link_post_pair_variant,'candidate');assert.equal(m.opus_backend,'bands-tell-inline-asm');
    assert.equal(m.diagnostic,true);assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');
    assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);
    assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_division_benchmark,false);
  }
}
function generate() {
  const prior=require('./report_mdct_post_pair.cjs').verifyPair(),dir=post.art('candidate');
  const m=read(path.join(dir,'manifest.json')),a=fs.readFileSync(path.join(root,'.build',parent,base.elfName)),app=fs.readFileSync(path.join(dir,'app.bin'));
  assert.equal(hash(a),prior.proof.candidate_elf_sha256);assert.equal(hash(app),m.app_sha256);
  const info=inspect(parent,names),p=findPatch(info.functions.opus_fft_impl);
  const source=fs.readFileSync(sourceFile,'utf8').replace(/\r\n/g,'\n');
  const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o');
  save(asm,source);run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);
  const object=fs.readFileSync(obj),s=sections(object).find(s=>s.name==='.text.patch0');assert.equal(s.bytes,p.bytes);
  p.after_hex=object.subarray(s.offset,s.offset+s.bytes).toString('hex');const off=base.offsetAt(a,p.address,p.bytes);p.before_hex=a.subarray(off,off+p.bytes).toString('hex');
  const b=base.patchElf(a,[p]),images={},manifests={},logs={};
  for(const[t,elf]of[['control',a],['candidate',b]]) {
    const file=path.join(build(t),base.elfName);save(file,elf);
    logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),file]);
    images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
    manifests[t]={...m,purpose:'Frozen-layout '+t+' FFT scheduled-load ASM raw benchmark; not production',app_sha256:hash(images[t]),post_link_fft_schedule_variant:t,post_link_recipe_sha256_lf:sourceHash(__filename),post_link_asm_sha256_lf:sourceHash(sourceFile),post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(a)};
  }
  assert.deepEqual(images.control,app);manifestPair(manifests.control,manifests.candidate);
  const actual=inspect(variant('candidate'),names),ar=base.rows(info.functions.opus_fft_impl.disassembly),br=base.rows(actual.functions.opus_fft_impl.disassembly);
  const outside=rs=>rs.filter(r=>r.address<p.address||r.address>=p.address+p.bytes);
  assert.deepEqual(outside(ar),outside(br));const inner=br.filter(r=>r.address>=p.address&&r.address<p.address+p.bytes);
  assert.deepEqual(inner.map(r=>r.bytes),[3,3,2,3,3,3,2]);assert.deepEqual(inner.map(r=>r.text),replacement);
  const symbolicProof=prove(ar.filter(r=>r.address>=p.address&&r.address<p.address+p.bytes).map(r=>r.text),inner.map(r=>r.text));
  assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);
  for(const n of names.filter(n=>n!=='opus_fft_impl')) assert.deepEqual(actual.functions[n],info.functions[n]);
  const proof={schema:1,parent,recipe_sha256_lf:sourceHash(__filename),asm_sha256_lf:sourceHash(sourceFile),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),patches:[p],symbolic:symbolicProof,numeric:numericProof(original,inner.map(r=>r.text)),static_ram_delta:0,stack_delta:0,app_bytes:app.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,imageProof:base.compareApps(images.control,images.candidate,[p]),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),logs}};
  for(const t of['control','candidate']) {save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(dir,'sdkconfig')));}
  save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.o'),object);save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');
  console.log(JSON.stringify({passed:true,sha256:manifests.candidate.app_sha256,bytes:app.length,ram_delta:0,instructions:'8 -> 7, independent load before dereference',patch:p}));return proof;
}
module.exports={parent,variant,art,build,names,read,sourceFile,original,replacement,symbolic,prove,numeric,numericProof,findPatch,manifestPair,generate};
if(require.main===module)generate();
