// Decoder-only specialization of the accepted, linked GCC allocation function.
// Valid native decoder objects are required, just as for the unmodified C API.
// No timing inference from instruction count; C fallback and bitrate domain stay intact.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,run,hash,sourceHash}=require('./export.cjs');
const {parsed}=require('./bits_fifth_proof.cjs'),{target}=require('./partition_frozen_proof.cjs');
const audit=require('./audit_allocation_decode.cjs'),base=require('./frozen_reloads.cjs');
const {sections}=require('./frozen_div.cjs'),{readAt}=require('./pvq_exp2_table32_proof.cjs');
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const entry=0x402482b0,span=2564,call=0x40244c85;

function predecessors(rows){
 const by=new Map(rows.map((r,i)=>[r.address,i])),pred=rows.map(()=>[]);
 for(const [i,r]of rows.entries()){
  const next=r.op==='ret'?[]:r.op==='j'?[target(r)]:/^b/.test(r.op)?[target(r),r.address+r.bytes]:[r.address+r.bytes];
  for(const pc of next){assert.ok(by.has(pc),'External CFG edge');pred[by.get(pc)].push(i);}
 }
 return{by,pred};
}
// All backward CFG paths stop at the most recent explicit definition, not the
// nearest textual store. The pinned valid-C object contract excludes writes
// outside the pointed-to objects; no arbitrary invalid pointer is accepted.
function reachingStack(rows,pc,slot){
 const {by,pred}=predecessors(rows),pending=[...pred[by.get(pc)]],seen=new Set(),found=[];
 while(pending.length){const i=pending.pop();if(seen.has(i))continue;seen.add(i);const r=rows[i];
  if(/^s(?:8|16|32)i$/.test(r.op)&&r.operands[1]==='a1'){
   const n=+r.operands[2],width=+r.op.match(/\d+/)[0]/8;
   if(n<slot+4&&n+width>slot){assert.equal(r.op,'s32i');assert.equal(n,slot);found.push(r);continue;}
  }
  assert.ok(i!==0,'Uninitialized stack value on a reachable path');pending.push(...pred[i]);
 }
 assert.ok(found.length);return found.sort((a,b)=>a.address-b.address);
}
function previousValue(rows,at,register){
 const {by,pred}=predecessors(rows);let i=by.get(at);const chain=[];
 while(true){assert.equal(pred[i].length,1,'Ambiguous register provenance');i=pred[i][0];const r=rows[i];chain.push(r);
  assert.ok(!/^call|^ret/.test(r.op),'Register provenance crosses a call');
  if(!/^s(?:8|16|32)i$|^b|^j$|^ssl$|^ssr$/.test(r.op)&&r.operands[0]===register)
   return{row:r,chain};
 }
}
function callerPointers(fn){
 const rows=parsed(fn),baseStores=reachingStack(rows,0x40244c35,308);
 for(const r of baseStores){const def=previousValue(rows,r.address,r.operands[0]).row;
  assert.equal(def.text,'addi '+r.operands[0]+', a1, 80','Local base must be callerSP+80');}
 const block=rows.filter(r=>r.address>=0x40244c33&&r.address<call),values=new Map(),args={};
 // Only scalar output addresses are computed here; array results are separately
 // traced to bounded scratch allocation below. Unknown integers stay unknown.
 const val=r=>values.get(r),add=(x,y)=>x&&y&&x.kind==='stack'&&y.kind==='constant'?{kind:'stack',offset:x.offset+y.offset}:null;
 for(const r of block){const[d,s,t]=r.operands;
  if(r.op==='movi')values.set(d,{kind:'constant',offset:+s});
  else if(r.op==='l32i')values.set(d,s==='a1'&&+t===308?{kind:'stack',offset:80}:null);
  else if(r.op==='mov')values.set(d,val(s));
  else if(r.op==='add')values.set(d,add(val(s),val(t))||add(val(t),val(s)));
  else if(r.op==='addi')values.set(d,add(val(s),{kind:'constant',offset:+t}));
  else if(r.op==='s32i'&&s==='a1')args[+t]=val(d);
  else assert.fail('Unexpected argument-setup instruction '+r.text);
 }
 assert.deepEqual([args[0],args[4],args[12]],[236,232,180].map(offset=>({kind:'stack',offset})));
 const scratch=[];
 for(const [pc,slot,expectedStore]of[[0x40244c4a,240,0x40244bd7],[0x40244c4d,248,0x40244c26],[0x40244c5b,332,0x40244c3e]]){
  const defs=reachingStack(rows,pc,slot);assert.deepEqual(defs.map(r=>r.address),[expectedStore]);
  assert.equal(defs[0].operands[0],'a2');
  const index=rows.findIndex(r=>r.address===expectedStore);let i=index-1;
  for(;i>=0&&!/^call/.test(rows[i].op);i--){assert.notEqual(rows[i].operands[0],'a2');assert.ok(!/^b|^j$/.test(rows[i].op));}
  assert.equal(rows[i].text,'call0 402428ec <yoradio_opus_scratch_alloc>');
  scratch.push({slot,store:expectedStore,allocator_call:rows[i].address});
 }
 return{local_base_definitions:baseStores.map(r=>r.address),scalar_outputs:{intensity:236,dual_stereo:232,balance:180},
  protected_arguments:[40,44,48],scratch_arrays:scratch,
  valid_object_contract:'Scalars at callerSP+180/+232/+236; three arrays from bounded heap/IRAM scratch, not task stack. Entropy context is a valid external ec_dec or private _dec, never the outgoing arguments. Source range/bounds contract is unchanged.'};
}
function imageReferences(elf,fn){
 const bytes=fs.readFileSync(elf),calls=[];
 const dis=run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d',elf]);
 for(const r of base.rows(dis))if(r.op==='call0'&&target(r)>=fn.address&&target(r)<fn.address+fn.bytes)calls.push({from:r.address,to:target(r)});
 assert.deepEqual(calls,[{from:call,to:entry}]);
 const addresses=[];
 // Scan every byte alignment, not only naturally aligned pointer tables.
 for(const s of sections(bytes).filter(s=>s.type===1&&(s.flags&2)))for(let i=0;i+4<=s.bytes;i++){
  const n=bytes.readUInt32LE(s.offset+i);if(n>=entry&&n<entry+span)addresses.push({section:s.name,address:s.address+i,value:n});
 }
 assert.deepEqual(addresses,[],'New address-taken/internal entry requires audit');
 const rs=parsed(fn),indirect=[];
 for(const [i,r]of rs.entries())if(r.op==='callx0'){
  const prev=rs[i-1];assert.equal(r.args,'a0');assert.equal(prev.op,'l32r');assert.equal(prev.operands[0],'a0');assert.equal(prev.address+prev.bytes,r.address);
  assert.equal(readAt(bytes,target(prev),4).readUInt32LE(),0x4000e21c,'Only ROM unsigned integer division');
  for(const branch of rs.filter(x=>/^b|^j$/.test(x.op)))assert.notEqual(target(branch),r.address);
  indirect.push({call:r.address,literal:target(prev),target:0x4000e21c});
 }
 assert.equal(indirect.length,3);
 const sourceFiles=['upstream/celt/rate.c','upstream/celt/celt_decoder.c','upstream/celt/entdec.c','upstream/celt/entcode.h','opus_memory.c'];
 const sources=Object.fromEntries(sourceFiles.map(f=>[f,sourceHash(path.join(component,f))]));
 const rate=fs.readFileSync(path.join(component,sourceFiles[0]),'utf8');
 assert.doesNotMatch(rate,/&\s*encode\b|\bencode\s*=(?!=)|\+\+encode|encode\+\+|--encode|encode--/);
 const refs=[];for(const dir of['src','celt','silk','silk/fixed'])for(const f of fs.readdirSync(path.join(component,'upstream',dir)).filter(f=>f.endsWith('.c'))){
  const text=fs.readFileSync(path.join(component,'upstream',dir,f),'utf8');
  for(const m of text.matchAll(/\bclt_compute_allocation\b/g))refs.push(dir+'/'+f);
 }
 assert.deepEqual(refs.sort(),['celt/celt_decoder.c','celt/rate.c']);
 const romFile='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp8266/ld/esp8266.rom.ld';
 assert.match(fs.readFileSync(romFile,'utf8'),/__udivsi3\s*=\s*0x4000e21c;/);
 return{elf_sha256:hash(bytes),direct_calls:calls,address_references:addresses,indirect_calls:indirect,source_references:refs,
  source_hashes:sources,rom_linker_sha256:hash(fs.readFileSync(romFile)),
  scope:'Pinned native decoder image and valid C objects, not arbitrary ABI misuse or corrupted pointers. encode is a by-value unmodified C argument; no address escapes. All source references are definition and zero-valued decoder call.'};
}
function contract(info,elf){
 const fn=info.functions.clt_compute_allocation,caller=info.functions.celt_decode_with_ec_dred;
 const zero=audit.callerArguments(caller,fn),pointers=callerPointers(caller),references=imageReferences(elf,fn);
 const conditional=audit.analyze(fn);assert.equal(conditional.branches.length,3);
 return{zero,pointers,references,conditional,decoder_only:true};
}

function selection(fn){
 const rows=parsed(fn),a=audit.analyze(fn),dead=new Set(a.dead.map(r=>r.address)),branches=new Map(a.branches.map(b=>[b.address,b]));
 const kept=rows.filter(r=>!dead.has(r.address)).filter(r=>!branches.has(r.address)||branches.get(r.address).taken);
 const next=pc=>{const r=kept.find(r=>r.address>=pc);assert.ok(r);return r.address;};
 const removedBranches=new Set();
 for(const [i,r]of kept.entries())if(branches.has(r.address)&&target(r)===kept[i+1]?.address)removedBranches.add(r.address);
 const live=kept.filter(r=>!removedBranches.has(r.address));
 return{rows,live,dead,branches,removedBranches,analysis:a};
}
function compile(fn){
 const s=selection(fn),refs=new Map(),kept=new Set(s.live.map(r=>r.address));
 let text='# Experimental decoder-only clt_compute_allocation, accepted GCC ASM.\n# LX106 call0 ABI; original192-byte frame, callee saves and all integer arithmetic.\n# encode=0 follows the checked private native decoder contract, not bitrate.\n# C and original saved GCC remain unchanged. RAM/stack/layout do not grow.\n# Removed encoder instructions remain documented at their original labels.\n.section .text.patch0,"ax",@progbits\n.begin no-transform\n';
 for(const r of base.rows(fn.disassembly)){
  text+='pc'+r.address.toString(16)+':\n';
  if(!kept.has(r.address)){text+='# decoder-unreachable/check: '+r.text+'\n';continue;}
  let op=s.branches.has(r.address)?'j':r.op,args=r.args.replace(/\s+<[^>]*>$/,'');
  if(/^b|^j$/.test(op))args=s.branches.has(r.address)?'pc'+target(r).toString(16):args.replace(/[0-9a-f]+$/,'pc'+target(r).toString(16));
  else if(op==='call0'||op==='l32r'){
   const address=target(r);assert.ok(address<entry||address>=entry+span);const name='fixed_'+address.toString(16);refs.set(name,address);args=args.replace(/[0-9a-f]+$/,name);
  }
  text+=op+' '+args+' # original0x'+r.address.toString(16)+'\n';
 }
 text+='allocation_live_end:\n.space '+span+' - (. - pc'+entry.toString(16)+'), 0\n.end no-transform\n';
 const script=[...refs].map(([n,a])=>n+' = 0x'+a.toString(16)+';').join('\n')+'\nSECTIONS { .text.patch0 0x'+entry.toString(16)+' : { *(.text.patch0) } }\n';
 return{text,script,source_instructions:s.rows.length,kept_instructions:s.live.length,removed_dead:s.dead.size,removed_checks:s.removedBranches.size};
}
// Independent comparison after assembly: every retained opcode/operand, branch
// destination, literal and call must correspond one-to-one to original rows.
function prove(before,after){
 const s=selection(before),actual=parsed(after),lookup=new Map(s.live.map((r,i)=>[r.address,i]));
 assert.equal(before.address,after.address);assert.equal(before.bytes,after.bytes);assert.equal(actual.length,s.live.length);
 const resolve=pc=>{const r=s.live.find(r=>r.address>=pc);assert.ok(r);return lookup.get(r.address);};
 const newIndex=new Map(actual.map((r,i)=>[r.address,i]));
 const normalize=(r,original)=>{
  const b=original&&s.branches.get(r.address),op=b?'j':r.op;
  if(/^b|^j$/.test(op)){const args=b?'':r.operands.slice(0,-1).join(', ');const index=original?resolve(target(r)):newIndex.get(target(r));assert.ok(Number.isInteger(index));return op+' '+args+' -> '+index;}
  if(op==='call0'||op==='l32r')return op+' '+(op==='l32r'?r.operands[0]+', ':'')+target(r);
  return r.text.replace(/\s+<[^>]*>$/,'');
 };
 assert.deepEqual(actual.map(r=>normalize(r,false)),s.live.map(r=>normalize(r,true)),'Retained opcode/operand/CFG/reference differs');
 const end=actual.at(-1).address+actual.at(-1).bytes;assert.equal(actual.at(-1).op,'ret');assert.ok(end<=entry+span);
 return{retained_instructions:actual.length,removed_encoder_instructions:s.dead.size,removed_constant_checks:s.removedBranches.size,
  live_bytes:end-entry,padding_bytes:entry+span-end,frame_bytes:192,static_ram_delta:0,stack_delta:0,
  proof:'One-to-one retained linked instructions; exact branch successor mapping, external literals/calls and load/store widths. Only checked encode=0 branches and unreachable instructions omitted.'};
}
module.exports={entry,span,predecessors,reachingStack,previousValue,callerPointers,imageReferences,contract,selection,compile,prove};
