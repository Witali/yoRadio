// Authenticate linked instructions, backing flash bounds and SAR liveness.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {root,component,hash,sourceHash}=require('./export.cjs'),{parsed}=require('./bits_fifth_proof.cjs');
const prior=require('./partition_frozen_proof.cjs'),{analyze}=require('./partition_decode.cjs'),{readAt}=require('./pvq_exp2_table32_proof.cjs');
const site=0x402484ab,end=site+3,helper=0x4024dd90,helperBytes=36,liveBytes=19,table=0x402d5b74,tableBytes=231;
const specs=[{site,bytes:3,helper}],definitions=()=>`allocation_read_byte = 0x${helper.toString(16)};`;
const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);},inStorage=a=>a>=helper&&a<helper+helperBytes;
function storageProof(functions){
 const file=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1/preflight.json');
 const original=JSON.parse(fs.readFileSync(file)).functions.quant_partition,p=prior.program(original),dead=new Set(analyze(p).dead.map(d=>p.rows[d.index].address));
 const rows=parsed(original),cover=rows.filter(r=>r.address<helper+helperBytes&&r.address+r.bytes>helper);
 assert.equal(cover[0].address,helper);assert.equal(cover.at(-1).address+cover.at(-1).bytes,helper+helperBytes);assert.ok(cover.every(r=>dead.has(r.address)));
 for(let i=1;i<cover.length;i++)assert.equal(cover[i-1].address+cover[i-1].bytes,cover[i].address);
 assert.ok(dead.has(rows.filter(r=>r.address<helper).at(-1).address));
 const incoming=rows.filter(r=>/^b|^j$|^call0$/.test(r.op)&&!inStorage(r.address)&&inStorage(prior.target(r)));assert.ok(incoming.every(r=>dead.has(r.address)));
 for(const fn of Object.values(functions))for(const r of parsed(fn)){assert.ok(!(r.address<helper+helperBytes&&r.address+r.bytes>helper),'Occupied storage');if(/^b|^j$|^call0$/.test(r.op))assert.ok(!inStorage(prior.target(r)),'Occupied entry');}
 return{address:helper,bytes:helperBytes,origin_sha256_lf:sourceHash(file),instructions:cover.length,incoming:incoming.map(r=>r.address),rule:'Original storage, fallthrough predecessor and incoming branches decoder-dead under encode=0; current tracked CFGs exclude this region.'};
}
function storageBytesProof(elf){
 const d=path.join(root,'firmware/development/esp8266-opus-pvq-byte-word-candidate-v1'),p=JSON.parse(fs.readFileSync(path.join(d,'preflight.json'))),a=zlib.gunzipSync(fs.readFileSync(path.join(d,'parent.elf.gz')));
 assert.equal(hash(a),p.parent_elf_sha256);assert.deepEqual(readAt(a,helper,helperBytes),readAt(elf,helper,helperBytes),'Storage already changed');return{address:helper,bytes:helperBytes,hex:readAt(a,helper,helperBytes).toString('hex')};
}
function allocationValues(){
 const file=path.join(component,'upstream/celt/modes.c'),text=fs.readFileSync(file,'utf8').replace(/\/\*[\s\S]*?\*\//g,'');
 const match=text.match(/static const unsigned char band_allocation\[\] = \{([\s\S]*?)\};/);assert.ok(match);const values=match[1].split(',').map(s=>s.trim()).filter(Boolean).map(Number);assert.equal(values.length,231);assert.ok(values.every(x=>Number.isInteger(x)&&x>=0&&x<=255));return values;
}
function sharedLeaf(){return JSON.parse(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-ebands-pair-candidate-v1/preflight.json')));}
function tableProof(elf){
 const raw=readAt(elf,table,tableBytes+1),p=sharedLeaf(),slot=p.patches.find(x=>x.address===0x4024dcc4);
 assert.equal(table%4,0);assert.deepEqual([...raw.subarray(0,tableBytes)],allocationValues());assert.equal(raw[231],0);assert.equal(table+232,0x402d5c5c);
 assert.equal(readAt(elf,0x402d3968+8,4).readUInt32LE(),21);assert.equal(readAt(elf,0x402d3968+40,4).readUInt32LE(),11);assert.equal(readAt(elf,0x402d3968+44,4).readUInt32LE(),table);
 assert.equal(readAt(elf,slot.address,slot.bytes).toString('hex'),slot.after_hex,'Intervening helper changed');
 assert.match(fs.readFileSync(path.join(component,'upstream/include/config.h'),'utf8'),/\/\* #undef CUSTOM_MODES \*\//);
 return{address:table,logical_bytes:231,backing_bytes:232,values:allocationValues(),padding:raw[231],next_object:table+232,shared_helper_sha256:hash(Buffer.from(slot.after_hex,'hex')),scope:'11 standard vectors x21 bands; aligned last word reads three array bytes plus one existing flash alignment byte, not the next object. No new storage; upper padding bits are discarded.'};
}
function findPatches(functions){
 storageProof(functions);const fn=functions.clt_compute_allocation,rs=parsed(fn);assert.equal(fn.address,0x402482b0);assert.equal(fn.bytes,0xa04);assert.equal(rs.find(r=>r.address===site)?.text,'l8ui a4, a5, 0');
 for(const r of rs)if(/^b|^j$|^call0$/.test(r.op)){const t=prior.target(r);assert.ok(!(t>site&&t<end),'Interior entry');}
 return[{address:site,bytes:3},{address:helper,bytes:helperBytes}];
}
function sarLiveness(fn,leaf=sharedLeaf().helperDisassembly){
 const rs=[...parsed(fn),...parsed({disassembly:leaf})],map=new Map(rs.map(r=>[r.address,r])),pending=[{pc:end,ret:null}],seen=new Set(),stops=[];
 while(pending.length){const s=pending.pop(),key=s.pc+':'+s.ret;if(seen.has(key))continue;seen.add(key);const r=map.get(s.pc);assert.ok(r,'Missing SAR successor');
  assert.ok(!['sll','sra','srl','src','rsr.sar','xsr.sar'].includes(r.op),'Live SAR at '+r.address.toString(16));
  if(['ssl','ssr','ssa8l','ssa8b','ssai','wsr.sar'].includes(r.op)){assert.equal(r.address,0x402484c0,'Unexpected SAR overwrite');assert.equal(r.text,'ssl a14');stops.push(r.address);continue;}
  if(r.op==='call0'){assert.equal(r.address,end);assert.equal(prior.target(r),0x4024dcc4);assert.equal(s.ret,null);pending.push({pc:prior.target(r),ret:s.pc+r.bytes});continue;}
  if(r.op==='ret'){assert.ok(s.ret);pending.push({pc:s.ret,ret:null});continue;}
  assert.ok(['nop','mull','sub','l32i','slli','srai','addi'].includes(r.op)||/^b|^j$/.test(r.op),'Unknown SAR instruction '+r.op);
  if(r.op==='j')pending.push({...s,pc:prior.target(r)});else if(/^b/.test(r.op))pending.push({...s,pc:prior.target(r)},{...s,pc:s.pc+r.bytes});else pending.push({...s,pc:s.pc+r.bytes});
 }assert.deepEqual([...new Set(stops)],[0x402484c0]);return{start:end,visited:[...seen].sort(),stops:[0x402484c0],a0:'Immediately overwritten by existing CALL0 at start',rule:'All paths, including both eBands helper paths, overwrite SAR before a variable shift/read. At this join all live GPRs, a0, SAR and memory agree.'};
}
function symbolic(text){
 const rs=parsed({disassembly:text});assert.deepEqual(rs.map(r=>r.text),['ssa8l a5','srli a4, a5, 2','slli a4, a4, 2','l32i a4, a4, 0','srl a4, a4','extui a4, a4, 0, 8','ret.n']);
 const records=[];
 for(let phase=0;phase<4;phase++){const r=Array.from({length:16},(_,i)=>'R'+i);r[5]=table+phase;const initial=r.slice(),word=Array.from({length:32},(_,i)=>'W'+i);let sar=-1,loads=0;
  for(const row of rs){const a=row.operands,op=row.op;if(op==='ret')continue;const d=reg(a[0]);
   if(op==='ssa8l')sar=(r[d]&3)*8;
   else if(op==='srli')r[d]=r[reg(a[1])]>>>Number(a[2]);else if(op==='slli')r[d]=(r[reg(a[1])]<<Number(a[2]))>>>0;
   else if(op==='l32i'){assert.equal(r[reg(a[1])]+Number(a[2]),table);r[d]=word;loads++;}
   else if(op==='srl')r[d]=r[reg(a[1])].slice(sar).concat(Array(sar).fill(0));
   else if(op==='extui')r[d]=r[reg(a[1])].slice(0,8).concat(Array(24).fill(0));else assert.fail(op);
  }assert.deepEqual(r[4],word.slice(phase*8,phase*8+8).concat(Array(24).fill(0)));for(let i=0;i<16;i++)if(i!==4)assert.equal(r[i],initial[i]);assert.equal(loads,1);records.push({phase,bits:r[4],sar,loads});
 }return records;
}
function execute(rows,initial,data,initialSar){
 const map=rows instanceof Map?rows:new Map(rows.map(r=>[r.address,r])),r=initial.slice();let pc=site,steps=0,sar=initialSar,words=0,bytes=0;
 assert.ok(r[5]>=table&&r[5]<table+tableBytes,'Invalid allocation pointer');assert.equal(data.length,232);
 while(pc!==end){const row=map.get(pc);assert.ok(row,'Missing byte instruction');assert.ok(++steps<12);const op=row.op,a=row.operands;let next=pc+row.bytes;
  if(op==='call0'){assert.equal(pc,site);assert.equal(prior.target(row),helper);r[0]=next;next=helper;}
  else if(op==='ret')next=r[0];else if(op==='ssa8l')sar=(r[reg(a[0])]&3)*8;
  else{const d=reg(a[0]),src=reg(a[1]);
   if(op==='srli')r[d]=r[src]>>>Number(a[2]);else if(op==='slli')r[d]=(r[src]<<Number(a[2]))>>>0;
   else if(op==='srl'){assert.ok(sar>=0&&sar<32);r[d]=r[src]>>>sar;}
   else if(op==='extui'){assert.equal(Number(a[2]),0);assert.equal(Number(a[3]),8);r[d]=r[src]&255;}
   else if(op==='l8ui'||op==='l32i'){const addr=r[src]+Number(a[2]),off=addr-table;if(op==='l32i'){assert.equal(addr%4,0);assert.ok(off>=0&&off+4<=data.length);r[d]=data.readUInt32LE(off);words++;}else{assert.ok(off>=0&&off<tableBytes);r[d]=data[off];bytes++;}}
   else assert.fail('Unknown '+op);
  }pc=next;
 }return{registers:r,sar,pc,steps,words,bytes};
}
function provenance(fn){
 const rs=parsed(fn),at=pc=>rs.find(r=>r.address===pc)?.text,checks={0x4024846f:'add a2, a4, a5',0x40248471:'srai a2, a2, 1',0x4024847a:'mull a2, a7, a2',0x4024848f:'l32i a5, a8, 44',0x40248491:'add a2, a2, a14',0x402484a4:'add a5, a5, a2',0x402484fb:'addi a5, a5, -1'};
 for(const [pc,t]of Object.entries(checks))assert.equal(at(+pc),t);return{checks,domain:'Untouched binary search lo=1,hi=nbAllocVectors-1 (10),mid=(lo+hi)>>1; reverse band loop j=end-1..start,0<=start<=end<=21. Offset mid*21+j in0..230; proof tests all231 offsets, not only fixture-observed indices.'};
}
function prove(functions,actual,helperDisassembly){
 const patches=findPatches(functions),a=parsed(functions.clt_compute_allocation),b=parsed(actual.clt_compute_allocation),hs=parsed({disassembly:helperDisassembly[0]});
 for(const n of Object.keys(functions))if(n!=='clt_compute_allocation')assert.deepEqual(actual[n],functions[n]);assert.deepEqual(a.filter(r=>r.address!==site),b.filter(r=>r.address!==site));
 assert.equal(b.find(r=>r.address===site).op,'call0');assert.equal(prior.target(b.find(r=>r.address===site)),helper);assert.equal(hs[0].address,helper);assert.equal(hs.at(-1).address+hs.at(-1).bytes,helper+liveBytes);
 const oldMap=new Map(a.map(r=>[r.address,r])),newMap=new Map([...b,...hs].map(r=>[r.address,r])),data=Buffer.alloc(232);let cases=0;
 const check=(offset,sar,seed)=>{const r=Array.from({length:16},(_,i)=>Math.imul(seed+i+1,0x45d9f3b)>>>0);r[5]=table+offset;const x=execute(oldMap,r,data,sar),y=execute(newMap,r,data,sar);assert.equal(y.registers[0],end);y.registers[0]=x.registers[0];assert.deepEqual(y.registers,x.registers);assert.equal(x.sar,sar);assert.equal(y.sar,(offset&3)*8);assert.equal(y.words,1);assert.equal(y.bytes,0);assert.equal(x.words,0);assert.equal(x.bytes,1);assert.equal(y.pc,x.pc);cases++;};
 for(let value=0;value<256;value++)for(let phase=0;phase<4;phase++)for(let sar=0;sar<64;sar++){data.writeUInt32LE(Math.imul(value+sar+1,0x45d9f3b)>>>0,0);data[phase]=value;check(phase,sar,value*256+sar);}
 allocationValues().forEach((v,i)=>data[i]=v);for(let offset=0;offset<tableBytes;offset++)for(let sar=0;sar<64;sar++){data[231]=(offset+sar)&255;check(offset,sar,offset*64+sar);}
 return{patches,symbolic:symbolic(helperDisassembly[0]),numeric_cases:cases,sar_liveness:sarLiveness(functions.clt_compute_allocation),provenance:provenance(functions.clt_compute_allocation),storage:storageProof(functions),frame_bytes:192,static_ram_delta:0,stack_delta:0};
}
module.exports={site,end,helper,helperBytes,liveBytes,table,tableBytes,specs,definitions,storageProof,storageBytesProof,allocationValues,sharedLeaf,tableProof,findPatches,sarLiveness,symbolic,execute,provenance,prove};
