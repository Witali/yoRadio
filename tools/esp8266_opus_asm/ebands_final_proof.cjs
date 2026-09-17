// Three exact signed pair loads; the third leaf uses two proven dead regions. Authenticate actual linked instructions and
// decoder-unreachable storage, not the appearance of the assembly source.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {root,hash,sourceHash}=require('./export.cjs'),old=require('./ebands_pair_proof.cjs');
const {parsed}=require('./bits_fifth_proof.cjs'),prior=require('./partition_frozen_proof.cjs'),{analyze}=require('./partition_decode.cjs');
const {readAt}=require('./pvq_exp2_table32_proof.cjs');
const specs=[
 {site:0x40248a05,bytes:6,helper:0x4024dcf0,span:36,p:4,low:10,high:3},
 {site:0x40248a21,bytes:6,helper:0x4024ddb4,span:36,p:12,low:4,high:2},
 {site:0x40248a6c,bytes:6,helper:0x4024dcb4,span:0x74,p:6,low:2,high:7}];
const regions=[{address:0x4024dcf0,bytes:36},{address:0x4024ddb4,bytes:36},{address:0x4024dcb4,bytes:16},{address:0x4024dd14,bytes:20}];
const definitions=()=>
 'ebands_final0 = 0x4024dcf0;\nebands_final1 = 0x4024ddb4;\nebands_final2 = 0x4024dcb4;\nebands_final_cross2 = 0x4024dd14;';
const tableProof=old.tableProof,reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
const inStorage=a=>regions.some(r=>a>=r.address&&a<r.address+r.bytes);
function storageProof(functions){
 const file=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1/preflight.json');
 const original=JSON.parse(fs.readFileSync(file)).functions.quant_partition,p=prior.program(original),dead=new Set(analyze(p).dead.map(d=>p.rows[d.index].address)),rows=parsed(original);
 const records=regions.map(({address:lo,bytes})=>{
  const hi=lo+bytes,cover=rows.filter(r=>r.address<hi&&r.address+r.bytes>lo);
  assert.ok(cover.length&&cover[0].address<=lo&&cover.at(-1).address+cover.at(-1).bytes>=hi);assert.ok(cover.every(r=>dead.has(r.address)));
  for(let i=1;i<cover.length;i++)assert.equal(cover[i-1].address+cover[i-1].bytes,cover[i].address);
  assert.ok(dead.has(rows.filter(r=>r.address<cover[0].address).at(-1).address));
  const incoming=rows.filter(r=>/^b|^j$|^call0$/.test(r.op)&&!inStorage(r.address)&&prior.target(r)>=lo&&prior.target(r)<hi);assert.ok(incoming.every(r=>dead.has(r.address)));
  for(const fn of Object.values(functions))for(const r of parsed(fn)){
   assert.ok(!(r.address<hi&&r.address+r.bytes>lo),'Occupied storage');
   if(/^b|^j$|^call0$|^l32r$/.test(r.op)){const t=prior.target(r);assert.ok(!(t>=lo&&t<hi),'Occupied entry or literal');}
  }
  return{address:lo,bytes,original_instructions:cover.length,incoming:incoming.map(r=>r.address)};
 });
 return{origin_sha256_lf:sourceHash(file),regions:records,rule:'All overlapping instructions, predecessors and incoming branches decoder-dead with encode=0; every current tracked CFG and L32R excludes storage.'};
}
function storageBytesProof(elf){
 const d=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1'),p=JSON.parse(fs.readFileSync(path.join(d,'preflight.json'))),a=zlib.gunzipSync(fs.readFileSync(path.join(d,'parent.elf.gz')));
 assert.equal(hash(a),p.parent_elf_sha256);
 return{parent_elf_sha256:hash(a),regions:regions.map(({address,bytes})=>{assert.deepEqual(readAt(a,address,bytes),readAt(elf,address,bytes),'Storage already changed');return{address,bytes,hex:readAt(a,address,bytes).toString('hex')};})};
}
function deadReturn(fn,s){
 const rs=parsed(fn),map=new Map(rs.map(r=>[r.address,r])),pending=[s.site+s.bytes],seen=new Set(),stops=[];
 const defs=new Set('addi addmi add sub mull mul16s slli srai srli sll sra srl and or xor neg extui nsau l32r movi mov l32i l16si l16ui l8ui'.split(' '));
 while(pending.length){const pc=pending.pop();if(seen.has(pc))continue;seen.add(pc);const r=map.get(pc);assert.ok(r,'Missing successor');const a=r.operands;
  if(/^call/.test(r.op)){assert.ok(!a.includes('a0'));stops.push({pc,kind:'call'});continue;}
  const reads=defs.has(r.op)?a.slice(1):a;assert.ok(!reads.includes('a0')&&r.op!=='ret','Live a0 at '+pc.toString(16));
  if(defs.has(r.op)&&a[0]==='a0'){stops.push({pc,kind:'definition'});continue;}
  assert.ok(defs.has(r.op)||/^b|^j$|^s(?:8|16|32)i$|^ssr$|^ssl$|^mov(?:ltz|gez|eqz|nez)$/.test(r.op),'Unknown liveness '+r.op);
  if(r.op==='j')pending.push(prior.target(r));else if(/^b/.test(r.op))pending.push(prior.target(r),pc+r.bytes);else pending.push(pc+r.bytes);
 }return{start:s.site+s.bytes,visited:[...seen].sort((a,b)=>a-b),stops};
}
function findPatches(functions){
 storageProof(functions);const fn=functions.clt_compute_allocation,rs=parsed(fn);assert.equal(fn.address,0x402482b0);assert.equal(fn.bytes,0xa04);
 const expected=[['l16si a3, a4, 2','l16si a10, a4, 0'],['l16si a2, a12, 2','l16si a4, a12, 0'],['l16si a2, a6, 0','l16si a7, a6, 2']];
 specs.forEach((s,i)=>{assert.deepEqual(rs.filter(r=>r.address>=s.site&&r.address<s.site+s.bytes).map(r=>r.text),expected[i]);
  for(const r of rs)if(/^b|^j$|^call0$/.test(r.op)){const t=prior.target(r);assert.ok(!(t>s.site&&t<s.site+s.bytes),'Interior entry');}
 });return[...specs.map(s=>({address:s.site,bytes:s.bytes})),...regions.map(r=>({...r}))];
}
function execute(rows,s,initial,data,sar,stackValue){
 const map=rows instanceof Map?rows:new Map(rows.map(r=>[r.address,r])),r=initial.slice();let pc=s.site,steps=0,words=0,shorts=0,stack=0;
 assert.ok(r[s.p]>=old.table&&r[s.p]<=old.table+40&&r[s.p]%2===0,'Invalid pair pointer');
 while(pc!==s.site+s.bytes){assert.ok(++steps<20);const row=map.get(pc);assert.ok(row);const op=row.op,a=row.operands;let next=pc+row.bytes;
  if(op==='call0'){assert.equal(pc,s.site);assert.equal(prior.target(row),s.helper);r[0]=next;next=s.helper;}
  else if(op==='ret')next=r[0];else if(op==='nop'){}
  else if(op==='bbsi'){if(r[reg(a[0])]&(1<<Number(a[1])))next=prior.target(row);}
  else{const d=reg(a[0]),src=reg(a[1]);
   if(op==='addi')r[d]=(r[src]+Number(a[2]))>>>0;
   else if(op==='slli')r[d]=(r[src]<<Number(a[2]))>>>0;else if(op==='srai')r[d]=(r[src]>>Number(a[2]))>>>0;
   else if(op==='l32i'&&src===1){assert.equal(d,14);assert.equal(Number(a[2]),68);r[d]=stackValue>>>0;stack++;}
   else if(op==='l32i'||op==='l16si'){const bytes=op==='l32i'?4:2,address=r[src]+Number(a[2]),off=address-old.table;assert.equal(address%bytes,0);assert.ok(off>=0&&off+bytes<=44);
    r[d]=(bytes===4?data.readUInt32LE(off):data.readInt16LE(off))>>>0;if(bytes===4)words++;else shorts++;
   }else assert.fail('Unmodeled '+op);
  }pc=next;
 }return{registers:r,sar,pc,steps,words,shorts,stack};
}
function symbolic(helperDisassembly,s){
 // Rename the actual three GPRs, map actual addresses (including the split
 // third leaf) into a contiguous equivalent graph, then apply the independent
 // arbitrary-bit signed-pair proof. Every branch target must be a known row.
 const rows=parsed({disassembly:helperDisassembly}),rename=new Map([[s.p,3],[s.low,11],[s.high,2]]),addresses=new Map();let pc=old.helper;
 for(const r of rows){addresses.set(r.address,pc);pc+=r.bytes;for(const a of r.operands.filter(x=>/^a\d+$/.test(x)))assert.ok(rename.has(reg(a)),'Unexpected helper GPR');}
 assert.equal(pc-old.helper,36);
 const renamed=helperDisassembly.replace(/\ba(\d+)\b/g,(m,n)=>'a'+rename.get(+n));
 const rebased=renamed.replace(/\b402[0-9a-f]{5}\b/g,x=>{const n=addresses.get(parseInt(x,16));assert.ok(n,'Unknown helper address');return n.toString(16);});
 return old.symbolic(rebased);
}
function provenance(fn){
 const rs=parsed(fn),at=pc=>rs.find(r=>r.address===pc)?.text;
 const checks={0x402489b7:'l32i a15, a8, 24',0x402489b9:'l32i a8, a1, 64',0x402489c0:'add a12, a15, a8',0x402489fd:'mov a6, a12',0x40248a01:'mov a4, a12',0x402489f6:'l32i a8, a1, 60',0x402489fa:'slli a3, a8, 1',0x402489ff:'add a15, a15, a3',0x40248a13:'addi a4, a4, 2',0x40248a1b:'bne a4, a15, 40248a05 <clt_compute_allocation+1877>',0x40248a27:'addi a12, a12, 2',0x40248a3c:'bne a12, a15, 40248a21 <clt_compute_allocation+1905>'};
 for(const [pc,text]of Object.entries(checks))assert.equal(at(+pc),text);
 assert.ok(rs.some(r=>r.text==='addi a6, a6, 2'));
 return{checks,domain:'Three unchanged interp_bits2pulses loops start<=j<codedBands<=end<=nbEBands=21; all adjacent pairs j0..20. Mode.eBands+24, stack64=2*start inherited from allocation setup. a4/a12/a6 advance2. No custom mode or bitrate limit.'};
}
function prove(functions,actual,helperDisassembly){
 const patches=findPatches(functions),a=parsed(functions.clt_compute_allocation),b=parsed(actual.clt_compute_allocation),inside=pc=>specs.some(s=>pc>=s.site&&pc<s.site+s.bytes);
 for(const n of Object.keys(functions))if(n!=='clt_compute_allocation')assert.deepEqual(actual[n],functions[n]);
 assert.deepEqual(a.filter(r=>!inside(r.address)),b.filter(r=>!inside(r.address)));
 const cases=[];
 for(let i=0;i<specs.length;i++){const s=specs[i],hs=parsed({disassembly:helperDisassembly[i]}),seq=b.filter(r=>r.address>=s.site&&r.address<s.site+s.bytes);
  assert.equal(seq[0].op,'call0');assert.equal(prior.target(seq[0]),s.helper);assert.equal(seq.at(-1).op,'nop');assert.equal(seq.at(-1).bytes,3);
  assert.equal(hs[0].address,s.helper);assert.equal(hs.at(-1).op,'ret');assert.equal(hs.reduce((n,r)=>n+r.bytes,0),36);assert.equal(hs.at(-1).address+hs.at(-1).bytes,s.helper+s.span);
  const oldMap=new Map(a.map(r=>[r.address,r])),newMap=new Map([...b,...hs].map(r=>[r.address,r])),data=Buffer.alloc(44);let numeric=0;
  const check=(index,sar,seed)=>{const r=Array.from({length:16},(_,j)=>Math.imul(seed+j+1,0x45d9f3b)>>>0);r[s.p]=old.table+2*index;const stackValue=Math.imul(seed,0x9e3779b9);
   const x=execute(oldMap,s,r,data,sar,stackValue),y=execute(newMap,s,r,data,sar,stackValue);assert.equal(y.registers[0],s.site+3);y.registers[0]=x.registers[0];assert.deepEqual(y.registers,x.registers);assert.equal(y.sar,x.sar);assert.equal(y.pc,x.pc);assert.equal(y.shorts,0);assert.equal(x.shorts,2);assert.equal(y.words,index%2?2:1);assert.equal(y.stack,0);assert.equal(x.stack,0);numeric++;};
  for(let n=0;n<65536;n++)for(const index of[0,1]){data.writeUInt32LE(Math.imul(n+1,0x45d9f3b)>>>0,0);data.writeUInt32LE(Math.imul(n+2,0x45d9f3b)>>>0,4);data.writeUInt16LE(n,2*index);check(index,n&63,n);}
  old.values.forEach((v,j)=>data.writeInt16LE(v,2*j));for(let j=0;j<21;j++)for(let sar=0;sar<64;sar++)check(j,sar,j*64+sar);
  cases.push({site:s.site,numeric_cases:numeric,symbolic:symbolic(helperDisassembly[i],s),dead_return:deadReturn(functions.clt_compute_allocation,s)});
 }
 return{patches,cases,storage:storageProof(functions),provenance:provenance(functions.clt_compute_allocation),numeric_cases:cases.reduce((n,c)=>n+c.numeric_cases,0),frame_bytes:192,static_ram_delta:0,stack_delta:0};
}
module.exports={specs,regions,definitions,tableProof,storageProof,storageBytesProof,findPatches,execute,symbolic,provenance,deadReturn,prove};
