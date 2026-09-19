// Frozen-layout N3 finite differences: real linked instructions and real U table.
// CPU benefit is intentionally not inferred from probe/instruction counts.
const assert=require('node:assert/strict');
const base=require('./frozen_reloads.cjs'),{hash}=require('./export.cjs');
const {readAt}=require('./pvq_exp2_table32_proof.cjs');
const qproof=require('./quant_decode_proof.cjs'),qaudit=require('./audit_quant_decode.cjs');
const {target}=require('./pvq_row_proof.cjs');
const site=0x40253329,siteBytes=43,done=0x40253361,helper=0x40251024,helperBytes=94;
const clean=r=>r.text.replace(/\s+<[^>]*>$/,'').replace(/\.n(?= |$)/,'');
const inside=fn=>base.rows(fn.disassembly).filter(r=>r.address>=site&&r.address<site+siteBytes);
const oldOps=['addi a15, a15, -4','l32i a8, a15, 0','bgeu a2, a8, 4025335d','addi a6, a15, -4','l32i a8, a6, 0','addi a6, a6, -4','addi a12, a12, -1','bltu a2, a8, 40253334','mov a3, a12','slli a9, a3, 16','srai a11, a9, 16','addi a6, a13, -1','j 40253361'];
function auditSite(fn,candidate=false){
 const rows=base.rows(fn.disassembly);
 assert.deepEqual(inside(fn).map(clean),candidate?['addi a15, a15, -4','l32i a8, a15, 0','bgeu a2, a8, 4025335d','beqi a13, 3, 40253351','addi a6, a15, -4','l32i a8, a6, 0','addi a6, a6, -4','addi a12, a12, -1','bltu a2, a8, 40253337','addi a6, a13, -1','j 40253354','call0 40251024']:oldOps);
 assert.equal(rows[0].text,'addi a1, a1, -48');
 assert.deepEqual(rows.filter(r=>/\ba0\b/.test(r.args)).map(r=>[r.address,r.text]),[[0x402531cd,'s32i a0, a1, 44'],[0x40253584,'l32i a0, a1, 44']]);
 assert.deepEqual(rows.filter(r=>/^call/.test(r.op)).map(r=>[r.address,clean(r)]),candidate?
  [[0x40253213,'call0 40246c20'],[site+40,'call0 40251024']]:[[0x40253213,'call0 40246c20']]);
 assert.deepEqual(rows.filter(r=>/^addi/.test(r.op)&&r.args.startsWith('a1,')).map(clean),['addi a1, a1, -48','addi a1, a1, 48']);
 for(const r of rows){
  assert.ok(!/^jx|^callx/.test(r.op));
  if(/^b|^j$/.test(r.op)){
   const t=target(r);assert.ok(Number.isFinite(t));
   if(r.address<site||r.address>=site+siteBytes)assert.ok(t<=site||t>=site+siteBytes,'Interior search entry');
   if(r.address>0x40253213)assert.ok(t>=0x40253216&&t<=0x40253597,'Bypasses a0 lifetime');
  }
 }
 const pre=rows.filter(r=>r.address>=0x40253235&&r.address<=0x4025325c).map(clean);
 assert.deepEqual(rows.filter(r=>r.address>=0x4025322c&&r.address<=0x40253232).map(clean),['slli a9, a12, 16','slli a3, a13, 2','srai a5, a9, 16']);
 assert.deepEqual(pre,['bge a12, a13, 4025323b','j 40253384','l32i a6, a7, 60','slli a15, a15, 2','add a15, a6, a15','l32i a8, a15, 0','movi a4, 1','bgeu a2, a8, 4025324c','movi a4, 0','neg a4, a4','add a11, a6, a3','and a8, a4, a8','l32i a11, a11, 0','sub a2, a2, a8','bltu a2, a11, 4025325f','j 40253329']);
 assert.deepEqual(rows.filter(r=>r.address>=done&&r.address<=0x40253367).map(clean),['slli a4, a4, 16','srai a4, a4, 16','add a3, a4, a5']);
 return rows;
}
function storage(info,elf,bytes){
 const contract=qproof.contract(info,elf),all=base.rows(info.functions.quant_all_bands.disassembly);
 const dead=new Set(qaudit.analyze(info.functions.quant_all_bands).dead.map(r=>r.address));
 const covered=all.filter(r=>r.address<helper+helperBytes&&r.address+r.bytes>helper);
 assert.equal(covered[0].address,helper);assert.equal(covered.at(-1).address+covered.at(-1).bytes,helper+helperBytes);
 for(let i=0;i<covered.length;i++){assert.ok(dead.has(covered[i].address),'Storage is decoder reachable');if(i)assert.equal(covered[i].address,covered[i-1].address+covered[i-1].bytes);}
 return{contract,storage:{address:helper,bytes:helperBytes,sha256:hash(readAt(bytes,helper,helperBytes)),dead_instructions:covered.length}};
}
function table(bytes){
 const ptr=0x402d7594,data=0x402d75d0,words=1272,offsets=[0,176,351,525,698,870,1041,1131,1178,1207,1226,1240,1248,1254,1257];
 const b=readAt(bytes,data,words*4),p=readAt(bytes,ptr,60);
 const rows=[];
 for(let n=0;n<offsets.length;n++)assert.equal(p.readUInt32LE(n*4),data+4*offsets[n]);
 for(let n=3;n<offsets.length;n++){
  const end=n+1<offsets.length?offsets[n+1]+n+1:words;
  const values=Array.from({length:end-offsets[n]-n},(_,i)=>b.readUInt32LE(4*(offsets[n]+n+i)));
  // N=14 has only its diagonal: no K>=N with a representable row[K+1].
  assert.ok(values.length>=1);for(let i=1;i<values.length;i++)assert.ok(values[i]>values[i-1],'Nonmonotone U row');
  rows.push({n,address:data+4*offsets[n],values});
 }
 return{address:data,pointers:ptr,sha256:hash(b),pointer_sha256:hash(p),rows};
}
function instructions(rows){return new Map(rows.map(row=>{
 const [op,...a]=clean(row).replaceAll(',','').split(' ');
 return[row.address,{...row,op,a,d:+a[0]?.slice(1),s:+a[1]?.slice(1),num:Number(a[2])}];
}));}
function emulate(rows,initial,memory,visited){
 const map=rows instanceof Map?rows:instructions(rows),r=initial.slice(),reads=[];let pc=site,steps=0;
 while(pc!==done){
  const row=map.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));assert.ok(++steps<10000);
  if(visited)visited.add(pc);
  const {op,a,d,s,num}=row;let next=pc+row.bytes;
  if(op==='addi')r[d]=(r[s]+num)>>>0;
  else if(op==='mov')r[d]=r[s];
  else if(op==='sub')r[d]=(r[s]-r[+a[2].slice(1)])>>>0;
  else if(op==='add')r[d]=(r[s]+r[+a[2].slice(1)])>>>0;
  else if(op==='addx4')r[d]=(r[s]*4+r[+a[2].slice(1)])>>>0;
  else if(op==='srli')r[d]=r[s]>>>num;
  else if(op==='slli')r[d]=(r[s]<<num)>>>0;
  else if(op==='srai')r[d]=(r[s]>>num)>>>0;
  else if(op==='l32i'){const at=(r[s]+num)>>>0;assert.ok(memory.has(at),'Out-of-range U read');r[d]=memory.get(at);reads.push(at);}
  else if(op==='bgeu'||op==='bltu'){if(op==='bgeu'?r[d]>=r[s]:r[d]<r[s])next=parseInt(a[2],16);}
  else if(op==='blti'){if((r[d]|0)<Number(a[1]))next=parseInt(a[2],16);}
  else if(op==='beqi'){if((r[d]|0)===Number(a[1]))next=parseInt(a[2],16);}
  else if(op==='j')next=parseInt(a[0],16);
  else if(op==='call0'){r[0]=next;next=parseInt(a[0],16);}
  else if(op==='ret')next=r[0];
  else assert.fail('Unproved operation '+op);
  pc=next;
 }
 return{registers:r,reads,steps};
}
function checkHelper(text){
 const rs=base.rows(text),ops=rs.map(clean);
 // Exact linked recurrence, no loads/stores/SAR. Preserve p, not only K.
 const expected=['slli a6, a12, 2','addi a6, a6, -4',
  'sub a8, a8, a6',null,'addi a6, a6, -4',
  'sub a8, a8, a6',null,'addi a6, a6, -4',
  'sub a8, a8, a6',null,'addi a6, a6, -4',
  'sub a8, a8, a6','addi a6, a6, -4','addi a12, a12, -4',null,
  'addi a6, a13, -1','ret','addi a12, a12, -1',null,'addi a12, a12, -2',null,'addi a12, a12, -3',null];
 assert.equal(rs.length,expected.length);assert.equal(rs[0].address,helper);
 expected[3]='bgeu a2, a8, '+rs[17].address.toString(16);
 expected[6]='bgeu a2, a8, '+rs[19].address.toString(16);
 expected[9]='bgeu a2, a8, '+rs[21].address.toString(16);
 expected[14]='bltu a2, a8, '+rs[2].address.toString(16);
 expected[18]=expected[20]=expected[22]='j '+rs[15].address.toString(16);
 assert.deepEqual(ops,expected);
 assert.ok(rs.at(-1).address+rs.at(-1).bytes<=helper+helperBytes);
 return rs;
}
function prove(before,after,helperText,t){
 const a=auditSite(before),b=auditSite(after,true),h=checkHelper(helperText);
 assert.deepEqual(a.filter(r=>r.address<site||r.address>=site+siteBytes),b.filter(r=>r.address<site||r.address>=site+siteBytes));
 const n3=t.rows.find(r=>r.n===3);assert.equal(n3.values.length,174);
 for(let i=0;i<n3.values.length;i++){const k=i+3;assert.equal(n3.values[i],2*k*k-2*k+1);}
 const ar=instructions(a.filter(r=>r.address>=site&&r.address<done)),br=instructions([...b.filter(r=>r.address>=site&&r.address<done),...h]);
 let cases=0,linearReads=0,binaryReads=0,maxSteps=0,arithmeticCases=0,fastCases=0;
 const visited=new Set();
 for(const {n,address:B,values}of t.rows){
  // Entire stored row, not merely fixture K or <=192 kb/s. Two adjacent
  // values must exist: the unchanged original sign path reads row[K+1].
  for(let K=n;K<n+values.length-1;K++){
   const memory=new Map(values.slice(0,K-n+1).map((v,i)=>[B+4*(n+i),v]));
   for(let tail=n;tail<=K;tail++){
    const low=values[tail-n],high=values[tail-n+1]-1;
    for(const index of new Set([low,high,low+Math.floor((high-low)/2)]))for(const seed of[0,0xffffffff]){
     const r=Array.from({length:16},(_,i)=>Math.imul(seed+i,0x45d9f3b)>>>0);
     r[2]=index;r[6]=B;r[9]=(K<<16)>>>0;r[11]=values[0];r[12]=K;r[13]=n;r[15]=B+4*(K+1);r[5]=K;
     const x=emulate(ar,r,memory),y=emulate(br,r,memory,visited);
     for(let i=1;i<16;i++)if(i!==3)assert.equal(y.registers[i],x.registers[i],'Register a'+i);
     assert.equal(y.registers[12],tail);assert.equal(y.registers[8],low);
     assert.equal(y.reads.length,n===3?1:x.reads.length);
     if(n===3&&tail<K)arithmeticCases++;
     if(tail===K){fastCases++;assert.equal(y.steps,x.steps);}
     linearReads+=x.reads.length;binaryReads+=y.reads.length;maxSteps=Math.max(maxSteps,y.steps);cases++;
    }
   }
  }
 }
 for(const r of h)assert.ok(visited.has(r.address),'Uncovered helper instruction');
 return{cases,arithmetic_cases:arithmeticCases,fast_cases:fastCases,helper_instructions:h.length,linear_reads:linearReads,candidate_reads:binaryReads,max_candidate_instructions:maxSteps,
  stack_bytes:48,stack_delta:0,static_ram_delta:0,stores:0,sar_writes:0,
  invariant:'Only N=3 after failed initial U(K) probe. At group entry p=U(3,K), delta=4*(K-1). Stage j computes exact U(3,K-j); early exits restore K-=j for j=1/2/3. Stage4 updates K-=4 and continues only if index<p. Original index>=13 prevents going below K=3; K<=175,p<=60901,delta<=696. No overflow/underflow, new tables, loads, stores or bitrate cap; other N and first fast return unchanged.',
  scope:'All intervals of every stored monotone U row N>2 at boundaries and midpoint, two arbitrary-register seeds. Exact linked instructions, not a CPU benchmark. a0 dead until original restore; a3 overwritten by shared continuation. Original K/N and entropy validation unchanged.'};
}
module.exports={site,siteBytes,done,helper,helperBytes,inside,auditSite,storage,table,emulate,checkHelper,prove};
