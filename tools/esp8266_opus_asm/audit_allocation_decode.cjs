// Read-only preflight for a future decoder-only allocation specialization.
// Counts dead instructions UNDER encode==0; this is not an authorization to
// delete them. Caller-output aliasing/callee contracts still need review.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,hash,sourceHash}=require('./export.cjs');
const {parsed}=require('./bits_fifth_proof.cjs');
const {target}=require('./partition_frozen_proof.cjs');
const {inspect}=require('./report_layout.cjs');
const calleeName='clt_compute_allocation',callerName='celt_decode_with_ec_dred';
const variant='esp8266-opus-ebands-final-candidate-v2';
const reg=s=>/^a(?:[0-9]|1[0-5])$/.test(s)?+s.slice(1):-1;

function callerArguments(fn,callee){
 const rows=parsed(fn),calls=rows.filter(r=>r.op==='call0'&&target(r)===callee.address);
 assert.equal(calls.length,1,'Expected single direct caller');
 const call=calls[0],zero=rows.find(r=>r.address===0x40244c6c);
 assert.equal(zero?.text,'movi a8, 0');
 const block=rows.filter(r=>r.address>=zero.address&&r.address<call.address);
 const writes=[];
 for(const r of block){
  if(r===zero)continue;
  assert.ok(!/^(?:b|j|call|ret)/.test(r.op),'Control flow interrupts argument setup');
  if(!/^s(?:8|16|32)i$/.test(r.op))assert.notEqual(r.operands[0],'a8','Zero argument overwritten');
  if(/^s(?:8|16|32)i$/.test(r.op)&&r.operands[1]==='a1'){
   const offset=+r.operands[2],width=+r.op.match(/\d+/)[0]/8;
   if(offset<52&&offset+width>40){
    assert.equal(r.op,'s32i','Partial overwrite of protected arguments');
    assert.ok([40,44,48].includes(offset));
    assert.equal(r.operands[0],'a8');writes.push(offset);
   }
  }
 }
 assert.deepEqual(writes,[48,44,40]);
 for(const r of rows.filter(r=>/^b|^j$/.test(r.op)))
  assert.ok(target(r)<=zero.address||target(r)>call.address,'Branch bypasses zero arguments');
 assert.ok(!rows.some(r=>r.op==='jx'),'Computed jump requires separate audit');
 return{call:call.address,zero:zero.address,writes,block:block.map(r=>r.text),
  scope:'Zero encode/prev/signalBandwidth dominates the direct call; does not prove all pointer aliases'};
}

function analyze(fn,{encodeZero=true}={}){
 assert.equal(fn.address,0x402482b0);assert.equal(fn.bytes,2564);
 const rows=parsed(fn),byAddress=new Map(rows.map((r,i)=>[r.address,i]));
 assert.equal(rows[0].text,'movi a9, 192');
 assert.equal(rows[1].text,'sub a1, a1, a9');
 const incomingWrites=rows.filter(r=>/^s(?:8|16|32)i$/.test(r.op)&&r.operands[1]==='a1'&&+r.operands[2]>=192);
 assert.equal(incomingWrites.length,0,'Callee writes incoming stack arguments');
 const aliases=rows.filter(r=>['add','addi','addmi','sub','mov','or'].includes(r.op)&&r.operands.slice(1).includes('a1'));
 assert.deepEqual(aliases.map(r=>r.text),['sub a1, a1, a9','add a1, a1, a9']);
 for(const r of rows.filter(r=>r.operands[0]==='a1'&&!/^b|^s(?:8|16|32)i$/.test(r.op)))
  assert.ok(aliases.includes(r),'Unexpected stack-pointer write');
 const loads=rows.filter(r=>r.op==='l32i'&&r.operands[1]==='a1'&&+r.operands[2]===232);
 assert.deepEqual(loads.map(r=>r.address),[0x40248832,0x40248908,0x40248982]);
 const states=Array(rows.length),queue=[0],queued=new Set([0]);states[0]=Array(16).fill(false);
 const isBranch=r=>/^b/.test(r.op),isJump=r=>r.op==='j';
 const nextIndex=r=>{const i=byAddress.get(target(r));assert.ok(Number.isInteger(i),'External branch');return i;};
 const decisions=new Map();let iterations=0;
 while(queue.length){
  assert.ok(++iterations<rows.length*30,'Nonconverging analysis');
  const i=queue.shift();queued.delete(i);const r=rows[i],before=states[i],after=before.slice();
  const [a,b,c]=r.operands,d=reg(a);let take=null;
  if(['beqz','bnez'].includes(r.op)&&before[d])take=r.op==='beqz';
  if(take!==null)decisions.set(i,{address:r.address,text:r.text,taken:take,target:target(r)});
  else decisions.delete(i);
  if(r.op==='l32i')after[d]=encodeZero&&b==='a1'&&+c===232;
  else if(r.op==='mov')after[d]=before[reg(b)];
  else if(/^call/.test(r.op)){for(let k=0;k<=11;k++)if(k!==1)after[k]=false;}
  else if(!/^s(?:8|16|32)i$/.test(r.op)&&!isBranch(r)&&!isJump(r)&&
      !['ssl','ssr','ret','nop'].includes(r.op)){
   assert.ok(d>=0,'Unknown instruction '+r.text);after[d]=false;
  }
  let next;
  if(r.op==='ret')next=[];
  else if(isJump(r))next=[nextIndex(r)];
  else if(isBranch(r))next=take===true?[nextIndex(r)]:take===false?[i+1]:[i+1,nextIndex(r)];
  else next=[i+1];
  for(const n of next){
   assert.ok(n<rows.length,'Fallthrough outside function');
   const old=states[n],joined=old?old.map((v,k)=>v&&after[k]):after.slice();
   if(!old||joined.some((v,k)=>v!==old[k])){
    states[n]=joined;if(!queued.has(n)){queue.push(n);queued.add(n);}
   }
  }
 }
 const dead=rows.filter((r,i)=>!states[i]);
 return{assumption:encodeZero?'Incoming encode at callerSP+40 remains zero':'No encode assumption',
  frame_bytes:192,iterations,branches:[...decisions.values()],
  removed_instructions:dead.length,removed_bytes:dead.reduce((n,r)=>n+r.bytes,0),
  dead:dead.map(r=>({address:r.address,bytes:r.bytes,text:r.text})),
  direct_incoming_stack_writes:incomingWrites.length,frame_address_operations:aliases.map(r=>r.text)};
}

function audit(){
 const linked=inspect(variant,[callerName,calleeName]);
 const source=fs.readFileSync(path.join(component,'upstream/celt/celt_decoder.c'),'utf8');
 assert.match(source,/clt_compute_allocation\(mode, start, end, offsets, cap,\s*alloc_trim, &intensity, &dual_stereo, bits, &balance, pulses,\s*fine_quant, fine_priority, C, LM, dec, 0, 0, 0\);/);
 const caller=callerArguments(linked.functions[callerName],linked.functions[calleeName]);
 const conditional=analyze(linked.functions[calleeName]),unknown=analyze(linked.functions[calleeName],{encodeZero:false});
 assert.equal(conditional.branches.length,3);assert.equal(unknown.branches.length,0);assert.equal(unknown.removed_instructions,0);
 const mapFile=path.join(root,'.build/esp8266-opus-folding-control-v1/yoradio_esp8266_helix_native.map');
 const cross=fs.readFileSync(mapFile,'utf8').match(/^clt_compute_allocation\s+[^\r\n]+\r?\n(?:[ \t]+[^\r\n]+\r?\n)*/m)?.[0];
 assert.ok(cross);assert.deepEqual(cross.trim().split(/\r?\n/).map(l=>l.trim().split(/\s+/).at(-1)),
  ['esp-idf/opus_decoder/libopus_decoder.a(rate.c.obj)','esp-idf/opus_decoder/libopus_decoder.a(celt_decoder.c.obj)']);
 const elf=path.join(root,'.build',variant,'yoradio_esp8266_helix_native.elf');
 const result={date:new Date().toISOString(),variant,checker_sha256_lf:sourceHash(__filename),
  elf_sha256:hash(fs.readFileSync(elf)),caller,conditional,unknown,cross_reference:cross,
  historical_map_sha256:hash(fs.readFileSync(mapFile)),
  linked,ready_for_specialization:false,
  remaining:['Prove all caller output-pointer ranges cannot alias callerSP+40..52, including earlier stack aliases',
    'Audit indirect callees and all linked references against the accepted ELF, not only the historical linker map',
    'Only then generate compact code and independently compare projected CFG/literals/call targets; host PCM and physical A/B/A remain mandatory'],
  scope:'Read-only conditional reachability audit; no firmware change, no speed or universal dead-code claim'};
 const out=path.join(root,'docs/results/esp8266-opus-allocation-decode-audit-20260918.json');
 fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({conditional_instructions:conditional.removed_instructions,conditional_bytes:conditional.removed_bytes,ready_for_specialization:false}));
 return result;
}
module.exports={callerArguments,analyze,audit};if(require.main===module)audit();
