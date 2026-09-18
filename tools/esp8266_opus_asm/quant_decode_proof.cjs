// Frozen-layout decoder specialization of quant_all_bands, not a C recompile.
// All arithmetic/data branches and the original 384-byte call0 frame survive.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,run,hash,sourceHash}=require('./export.cjs');
const {parsed}=require('./bits_fifth_proof.cjs'),{target}=require('./partition_frozen_proof.cjs');
const audit=require('./audit_quant_decode.cjs'),base=require('./frozen_reloads.cjs');
const {sections}=require('./frozen_div.cjs'),{readAt}=require('./pvq_exp2_table32_proof.cjs');
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const {entry,span}=audit,call=0x40244dbb;
function callerArguments(fn){
 const rows=parsed(fn),zero=rows.find(r=>r.address===0x40244d6a),move=rows.find(r=>r.address===0x40244da8);
 assert.equal(zero.text,'movi a8, 0');assert.equal(move.text,'mov a2, a8');
 for(const r of rows.filter(r=>r.address>zero.address&&r.address<call)){
  assert.ok(!/^call|^b|^j$|^ret/.test(r.op),'Argument setup has control flow');
  if(!/^s(?:8|16|32)i$/.test(r.op))assert.notEqual(r.operands[0],'a8','Zero overwritten');
  if(r.address>move.address&&!/^s(?:8|16|32)i$/.test(r.op))assert.notEqual(r.operands[0],'a2','Encode argument overwritten');
 }
 for(const r of rows.filter(r=>/^b|^j$/.test(r.op)))assert.ok(target(r)<=zero.address||target(r)>call,'Bypassed encode initializer');
 assert.equal(rows.find(r=>r.address===call).text,'call0 402507d8 <quant_all_bands>');
 return{call,zero:zero.address,move:move.address,argument:'a2=0',frame_private:'Valid caller objects cannot overlap the future callee private frame'};
}
function imageReferences(elf,fn){
 const bytes=fs.readFileSync(elf),dis=run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d',elf]);
 const rawCalls=base.rows(dis).filter(r=>r.op==='call0'&&target(r)>=entry&&target(r)<entry+span).map(r=>({from:r.address,to:target(r)}));
 // objdump -d also decodes the leading literal pools as fake instructions.
 // Classify only these exact two matches: map names plus unchanged base ELF
 // bytes and absence of a covering STT_FUNC. Do not silently ignore unknowns.
 const mapFile=path.join(root,'.build/esp8266-opus-folding-control-v1/yoradio_esp8266_helix_native.map');
 const map=fs.readFileSync(mapFile,'utf8'),original=fs.readFileSync(mapFile.replace(/\.map$/,'.elf'));
 const sym=run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-t',elf]);
 const functions=[...sym.matchAll(/^([0-9a-f]+)\s+\w+\s+F\s+\S+\s+([0-9a-f]+)\s+(\S+)$/gm)].map(m=>({address:parseInt(m[1],16),bytes:parseInt(m[2],16),name:m[3]}));assert.ok(functions.length>1000);
 const literalMatches=[];
 for(const [from,start,size,name]of[[0x40210ec5,0x40210ec4,20,'httpd_sess_new'],[0x40210ef9,0x40210ee4,28,'httpd_send_headers']]){
  const row=rawCalls.find(r=>r.from===from);assert.ok(row);
  assert.ok(!functions.some(f=>from>=f.address&&from<f.address+f.bytes));
  assert.match(map,new RegExp('\\.literal\\.'+name+'\\s+0x'+start.toString(16)+'\\s+0x'+size.toString(16)+'\\s+'));
  assert.deepEqual(readAt(bytes,start,size),readAt(original,start,size));
  literalMatches.push({...row,section:'.literal.'+name,start,bytes:size,sha256:hash(readAt(bytes,start,size))});
 }
 const calls=rawCalls.filter(r=>!literalMatches.some(l=>l.from===r.from));
 assert.deepEqual(calls,[{from:call,to:entry}]);const addresses=[];
 for(const s of sections(bytes).filter(s=>s.type===1&&(s.flags&2)))for(let i=0;i+4<=s.bytes;i++){
  const n=bytes.readUInt32LE(s.offset+i);if(n>=entry&&n<entry+span)addresses.push({section:s.name,address:s.address+i,value:n});
 }
 const instructionMatches=[];
 for(const [address,value,name,start,expected]of[
  [0x40102b78,0x40252a73,'lmac_set_status',0x40102b77,['s32i a6, a3, 28','add a2, a5, a2','addx4 a2, a2, a4']],
  [0x40256a05,0x40252172,'silk_PLC',0x40256a05,['l32i a7, a1, 148','extui a3, a4, 0, 16']]]){
  const match=addresses.find(a=>a.address===address&&a.value===value);assert.ok(match);
  const fn=functions.find(f=>f.name===name);assert.ok(fn&&start>=fn.address&&address+4<=fn.address+fn.bytes);
  const text=require('./report_layout.cjs').reachableDisassembly(elf,fn);
  const code=parsed({disassembly:text}),idx=code.findIndex(r=>r.address===start);assert.ok(idx>=0);
  const covering=code.slice(idx,idx+expected.length);assert.deepEqual(covering.map(r=>r.text),expected);
  for(let i=1;i<covering.length;i++)assert.equal(covering[i].address,covering[i-1].address+covering[i-1].bytes);
  assert.ok(covering.at(-1).address+covering.at(-1).bytes>=address+4);
  instructionMatches.push({...match,function:name,covering:covering.map(r=>({address:r.address,text:r.text}))});
 }
 assert.deepEqual(addresses.filter(a=>!instructionMatches.some(i=>a.address===i.address)),[],'Unclassified address-taken/internal entry requires audit');
 const rows=parsed(fn),indirect=[];
 for(const [i,r]of rows.entries())if(r.op==='callx0'){
  const prev=rows[i-1];assert.equal(r.args,'a0');assert.equal(prev.op,'l32r');assert.equal(prev.operands[0],'a0');assert.equal(prev.address+prev.bytes,r.address);
  for(const b of rows.filter(x=>/^b|^j$/.test(x.op)))assert.notEqual(target(b),r.address,'Bypassed ROM literal');
  const address=readAt(bytes,target(prev),4).readUInt32LE();assert.ok([0x4000dc88,0x4000e21c].includes(address));
  indirect.push({call:r.address,literal:target(prev),target:address});
 }
 assert.equal(indirect.length,11);
 const romFile='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp8266/ld/esp8266.rom.ld',rom=fs.readFileSync(romFile,'utf8');
 assert.match(rom,/__divsi3\s*=\s*0x4000dc88;/);assert.match(rom,/__udivsi3\s*=\s*0x4000e21c;/);
 return{elf_sha256:hash(bytes),direct_calls:calls,literal_false_matches:literalMatches,instruction_false_matches:instructionMatches,literal_map_sha256_lf:sourceHash(mapFile),base_elf_sha256:hash(original),address_references:[],indirect_calls:indirect,rom_linker_sha256:hash(fs.readFileSync(romFile))};
}
function sourceContract(){
 const files=['upstream/celt/bands.c','upstream/celt/celt_decoder.c','opus_memory.c','CMakeLists.txt'];
 const hashes=Object.fromEntries(files.map(f=>[f,sourceHash(path.join(component,f))]));
 const bands=fs.readFileSync(path.join(component,files[0]),'utf8'),decoder=fs.readFileSync(path.join(component,files[1]),'utf8');
 assert.match(decoder,/quant_all_bands\(0, mode, start, end,/);
 assert.deepEqual([...bands.matchAll(/ctx(?:\.|->)encode\s*=(?!=)[^;]*;/g)].map(m=>m[0]),['ctx.encode = encode;']);
 assert.deepEqual([...bands.matchAll(/ctx(?:\.|->)resynth\s*=(?!=)[^;]*;/g)].map(m=>m[0]),['ctx.resynth = resynth;']);
 assert.doesNotMatch(bands,/&\s*ctx(?:\.|->)(?:encode|resynth)\b/);
 const fields=bands.match(/struct band_ctx \{([\s\S]*?)\};/)[1].trim().split(/\r?\n/).map(x=>x.trim());
 assert.deepEqual(fields,['int encode;','int resynth;','const CELTMode *m;','int i;','int intensity;','int spread;','int tf_change;','ec_ctx *ec;','opus_int32 remaining_bits;','const celt_ener *bandE;','opus_uint32 seed;','int arch;','int theta_round;','int disable_inv;','int avoid_split_noise;']);
 assert.match(bands,/#ifndef YORADIO_OPUS_BOUNDED\s*\/\* Encoder-only RDO[\s\S]*?ctx_save = ctx;[\s\S]*?ctx = ctx_save;[\s\S]*?ctx = ctx_save2;[\s\S]*?#endif/);
 const refs=[];for(const dir of['src','celt','silk','silk/fixed'])for(const file of fs.readdirSync(path.join(component,'upstream',dir)).filter(f=>f.endsWith('.c'))){
  const text=fs.readFileSync(path.join(component,'upstream',dir,file),'utf8').replace(/\/\*[\s\S]*?\*\/|\/\/[^\r\n]*/g,'');for(const m of text.matchAll(/\bquant_all_bands\b/g))refs.push(dir+'/'+file);
 }
 assert.deepEqual(refs.sort(),['celt/bands.c','celt/celt_decoder.c']);
 return{hashes,fields,field_bytes:4,context_bytes:60,source_references:refs,
  contract:'Pinned 32-bit ABI, valid native decoder objects. Only &ctx at SP+32 escapes; ctx occupies SP+32..91. Encoder RDO copies are excluded in the bounded build. Callees can modify other ctx fields but never encode or resynth; array/entropy/scratch objects cannot overlap private scalar slots SP+92..363. Calls and indirect writes kill facts about outgoing, incoming and mutable ctx slots.'};
}
function contract(info,elf){
 const fn=info.functions.quant_all_bands,conditional=audit.analyze(fn),unknown=audit.analyze(fn,{encodeZero:false,immutableContext:false,immutableResynth:false});
 assert.equal(conditional.ctx_encode_at_store,0);assert.equal(unknown.removed_instructions,0);
 assert.ok(!conditional.calls_live.some(r=>/ec_enc|ec_encode|alg_quant|stereo_itheta/.test(r.text)));
 return{caller:callerArguments(info.functions.celt_decode_with_ec_dred),references:imageReferences(elf,fn),source:sourceContract(),conditional,unknown,decoder_only:true};
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
 let text='# Experimental decoder-only quant_all_bands, accepted GCC ASM.\n# LX106 call0 ABI; original384-byte frame, callee saves and all integer arithmetic.\n# encode=0 follows the checked private native decoder contract, not bitrate.\n# C and original saved GCC remain unchanged. RAM/stack/layout do not grow.\n# Removed encoder instructions remain documented at their original labels.\n.section .text.patch0,"ax",@progbits\n.begin no-transform\n';
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
 text+='quant_live_end:\n.space '+span+' - (. - pc'+entry.toString(16)+'), 0\n.end no-transform\n';
 const script=[...refs].map(([n,a])=>n+' = 0x'+a.toString(16)+';').join('\n')+'\nSECTIONS { .text.patch0 0x'+entry.toString(16)+' : { *(.text.patch0) } }\n';
 return{text,script,source_instructions:s.rows.length,kept_instructions:s.live.length,removed_dead:s.dead.size,removed_checks:s.rows.length-s.dead.size-s.live.length};
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
 const end=actual.at(-1).address+actual.at(-1).bytes;assert.ok(end<=entry+span);
 return{retained_instructions:actual.length,removed_unreachable_instructions:s.dead.size,removed_constant_checks:s.rows.length-s.dead.size-s.live.length,
  checks_replaced_with_jump:s.branches.size-(s.rows.length-s.dead.size-s.live.length),
  live_bytes:end-entry,padding_bytes:entry+span-end,frame_bytes:384,static_ram_delta:0,stack_delta:0,
  proof:'One-to-one retained linked instructions; exact branch successor mapping, external literals/calls and load/store widths. Only constant branches and unreachable instructions under the checked decoder/private-frame contract are removed.'};
}
module.exports={entry,span,callerArguments,imageReferences,sourceContract,contract,selection,compile,prove};
