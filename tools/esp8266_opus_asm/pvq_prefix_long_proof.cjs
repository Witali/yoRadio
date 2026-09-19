// Frozen-layout PVQ exponent-prefix search: real linked instructions and real U table.
// CPU benefit is intentionally not inferred from probe/instruction counts.
const assert=require('node:assert/strict');
const base=require('./frozen_reloads.cjs'),{hash}=require('./export.cjs');
const {readAt}=require('./pvq_exp2_table32_proof.cjs');
const qproof=require('./quant_decode_proof.cjs'),qaudit=require('./audit_quant_decode.cjs');
const {target}=require('./pvq_row_proof.cjs');
const fs=require('node:fs'),path=require('node:path'),{root,component,run}=require('./export.cjs');
const {sections}=require('./frozen_div.cjs');
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const site=0x40253329,siteBytes=43,done=0x40253361,helper=0x40251024,helperBytes=94,storageAddress=helper,storageBytes=helperBytes;
const dataAddress=0x40248cb4,prefixAddress=dataAddress+4,prefixBytes=352,dataBytes=prefixBytes+4,algBytes=0x6fc;
const clean=r=>r.text.replace(/\s+<[^>]*>$/,'').replace(/\.n(?= |$)/,'');
const inside=fn=>base.rows(fn.disassembly).filter(r=>r.address>=site&&r.address<site+siteBytes);
const oldOps=['addi a15, a15, -4','l32i a8, a15, 0','bgeu a2, a8, 4025335d','addi a6, a15, -4','l32i a8, a6, 0','addi a6, a6, -4','addi a12, a12, -1','bltu a2, a8, 40253334','mov a3, a12','slli a9, a3, 16','srai a11, a9, 16','addi a6, a13, -1','j 40253361'];
function auditSite(fn,candidate=false){
 const rows=base.rows(fn.disassembly);
 assert.deepEqual(inside(fn).map(clean),candidate?['addi a15, a15, -4','sub a8, a12, a13','bgei a8, 8, 40253349','l32i a8, a15, 0','bgeu a2, a8, 4025335d','addi a6, a15, -4','l32i a8, a6, 0','addi a6, a6, -4','addi a12, a12, -1','bltu a2, a8, 4025333a','addi a6, a13, -1','j 40253354','addi a3, a15, -16','l32i a8, a3, 0','bgeu a2, a8, 40253332','call0 40251024']:oldOps);
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
 assert.equal(info.functions.alg_quant.address,dataAddress);assert.equal(info.functions.alg_quant.bytes,algBytes);
 const contract=qproof.contract(info,elf),all=base.rows(info.functions.quant_all_bands.disassembly);
 const dead=new Set(qaudit.analyze(info.functions.quant_all_bands).dead.map(r=>r.address));
 const covered=all.filter(r=>r.address<storageAddress+storageBytes&&r.address+r.bytes>storageAddress);
 assert.equal(covered[0].address,storageAddress);assert.equal(covered.at(-1).address+covered.at(-1).bytes,storageAddress+storageBytes);
 for(let i=0;i<covered.length;i++){assert.ok(dead.has(covered[i].address),'Storage is decoder reachable');if(i)assert.equal(covered[i].address,covered[i-1].address+covered[i-1].bytes);}
 const dis=run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d',elf]),code=base.rows(dis);
 const contains=pc=>pc>=dataAddress&&pc<dataAddress+algBytes;
 const calls=code.filter(r=>r.op==='call0'&&contains(target(r))).map(r=>({from:r.address,to:target(r)}));
 assert.deepEqual(calls,[{from:0x402518fa,to:dataAddress}]);assert.ok(dead.has(0x402518fa),'Encoder call is reachable');
 const jumps=code.filter(r=>/^b|^j$/.test(r.op)&&!contains(r.address)&&contains(target(r)));
 assert.deepEqual(jumps,[],'External branch into unused encoder');
 const pointers=[];
 for(const sec of sections(bytes).filter(s=>s.type===1&&(s.flags&2)))for(let i=0;i+4<=sec.bytes;i++){
   const v=bytes.readUInt32LE(sec.offset+i);if(contains(v))pointers.push({address:sec.address+i,value:v});
 }
 assert.deepEqual(pointers,[],'Address-taken encoder or internal entry');
 const sourceRefs=[];
 for(const dir of['src','celt','silk','silk/fixed'])for(const file of fs.readdirSync(path.join(component,'upstream',dir)).filter(f=>f.endsWith('.c'))){
   const source=fs.readFileSync(path.join(component,'upstream',dir,file),'utf8')
     .replace(/\/\*[\s\S]*?\*\/|\/\/[^\r\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g,'');
   for(const match of source.matchAll(/\balg_quant\b/g))sourceRefs.push(dir+'/'+file);
 }
 assert.deepEqual(sourceRefs.sort(),['celt/bands.c','celt/vq.c']);
 return{contract,storage:{address:storageAddress,bytes:storageBytes,sha256:hash(readAt(bytes,storageAddress,storageBytes)),dead_instructions:covered.length},
 encoder_storage:{address:dataAddress,bytes:dataBytes,function_bytes:algBytes,sha256:hash(readAt(bytes,dataAddress,dataBytes)),calls,external_jumps:[],pointers,source_refs:sourceRefs,
 invariant:'The sole linked alg_quant call is in the proven encode=0 dead set. No allocated address-taken reference or external jump enters its function. Only its first356 bytes are replaced by a literal and flash data; valid decoder flow cannot execute them.'}};

}
const table=require('./pvq_binary_proof.cjs').table;
function prefix(t){
 const rows=t.rows.filter(r=>r.n>=3&&r.n<=13);assert.equal(rows.length,11);
 const bytes=Buffer.alloc(prefixBytes);
 for(const row of rows)for(let z=0;z<32;z++){
   const high=2**(32-z)-1;let k=row.n;
   while(k-row.n+1<row.values.length&&row.values[k-row.n+1]<=high)k++;
   assert.ok(k>=row.n&&k<=255);
   bytes[(row.n-3)*32+z]=k;
 }
 return bytes;
}
function prefixProof(bytes,t){
 const p=prefix(t);assert.equal(readAt(bytes,dataAddress,4).readUInt32LE(),prefixAddress-96);
 assert.deepEqual(readAt(bytes,prefixAddress,prefixBytes),p);
 return{literal:dataAddress,address:prefixAddress,bytes:prefixBytes,sha256:hash(p),rows:11,order:'(N-3)*32+CLZ(index)',word_load_only:true};
}
function instructions(rows){return new Map(rows.map(row=>{
 const [op,...a]=clean(row).replaceAll(',','').split(' ');
 return[row.address,{...row,op,a,d:+a[0]?.slice(1),s:+a[1]?.slice(1),num:Number(a[2])}];
}));}
function emulate(rows,initial,memory,visited,initialSar=0){
 const map=rows instanceof Map?rows:instructions(rows),r=initial.slice(),reads=[];let pc=site,steps=0,sar=initialSar;
 while(pc!==done){
  const row=map.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));assert.ok(++steps<10000);
  if(visited)visited.add(pc);
  const {op,a,d,s,num}=row;let next=pc+row.bytes;
  if(op==='addi')r[d]=(r[s]+num)>>>0;
  else if(op==='mov')r[d]=r[s];
  else if(op==='sub')r[d]=(r[s]-r[+a[2].slice(1)])>>>0;
  else if(op==='add')r[d]=(r[s]+r[+a[2].slice(1)])>>>0;
  else if(op==='addx4')r[d]=(r[s]*4+r[+a[2].slice(1)])>>>0;
  else if(op==='nsau')r[d]=Math.clz32(r[s]);
  else if(op==='extui')r[d]=(r[s]>>>num)&((1<<Number(a[3]))-1);
  else if(op==='rsr.sar')r[d]=sar;
  else if(op==='wsr.sar')sar=r[d]&63;
  else if(op==='ssr')sar=r[d]&31;
  else if(op==='srl')r[d]=sar>=32?0:r[s]>>>sar;
  else if(op==='l32r'){const at=parseInt(a[1],16);assert.equal(at,dataAddress);assert.ok(memory.has(at));r[d]=memory.get(at);reads.push(at);}
  else if(op==='srli')r[d]=r[s]>>>num;
  else if(op==='slli')r[d]=(r[s]<<num)>>>0;
  else if(op==='srai')r[d]=(r[s]>>num)>>>0;
  else if(op==='l32i'){const at=(r[s]+num)>>>0;assert.ok(memory.has(at),'Out-of-range U read');r[d]=memory.get(at);reads.push(at);}
  else if(op==='bgeu'||op==='bltu'){if(op==='bgeu'?r[d]>=r[s]:r[d]<r[s])next=parseInt(a[2],16);}
  else if(op==='blti'||op==='bgei'){if(op==='blti'?(r[d]|0)<Number(a[1]):(r[d]|0)>=Number(a[1]))next=parseInt(a[2],16);}
  else if(op==='j')next=parseInt(a[0],16);
  else if(op==='call0'){r[0]=next;next=parseInt(a[0],16);}
  else if(op==='ret')next=r[0];
  else assert.fail('Unproved operation '+op);
  pc=next;
 }
 return{registers:r,reads,steps,sar};
}
function checkHelper(text){
 const rs=base.rows(text),labels=new Map(),spec=[];
 for(const line of `
nsau a8, a2
slli a3, a13, 5
add a8, a8, a3
extui a3, a8, 0, 2
srli a8, a8, 2
l32r a11, 40248cb4
addx4 a8, a8, a11
l32i a8, a8, 0
rsr.sar a9
slli a3, a3, 3
ssr a3
srl a8, a8
wsr.sar a9
extui a8, a8, 0, 8
bltu a12, a8, @bounded
mov a12, a8
bounded:
addx4 a6, a12, a6
l32i a8, a6, 0
bgeu a2, a8, @done
addi a6, a6, -4
linear:
l32i a8, a6, 0
addi a6, a6, -4
addi a12, a12, -1
bltu a2, a8, @linear
done:
addi a6, a13, -1
ret
`.trim().split('\n')){
   if(line.endsWith(':'))labels.set(line.slice(0,-1),spec.length);else spec.push(line);
 }
 assert.equal(rs.length,spec.length);assert.equal(rs[0].address,helper);
 for(let i=1;i<rs.length;i++)assert.equal(rs[i].address,rs[i-1].address+rs[i-1].bytes);
 const expected=spec.map(s=>s.replace(/@(\w+)/g,(_,label)=>{assert.ok(labels.has(label));return rs[labels.get(label)].address.toString(16);}));
 assert.deepEqual(rs.map(clean),expected);assert.ok(rs.at(-1).address+rs.at(-1).bytes<=helper+helperBytes);
 return rs;
}
function prove(before,after,helperText,t){
 const a=auditSite(before),b=auditSite(after,true),h=checkHelper(helperText);
 assert.deepEqual(a.filter(r=>r.address<site||r.address>=site+siteBytes),b.filter(r=>r.address<site||r.address>=site+siteBytes));
 const ar=instructions(a.filter(r=>r.address>=site&&r.address<done)),br=instructions([...b.filter(r=>r.address>=site&&r.address<done),...h]);
 const packed=prefix(t),extra=new Map([[dataAddress,prefixAddress-96]]);
 for(let off=0;off<prefixBytes;off+=4)extra.set(prefixAddress+off,packed.readUInt32LE(off));
 const visited=new Set(),witnesses=new Map();let cases=0,linearReads=0,prefixReads=0,maxSteps=0,extraSarCases=0;
 const guard={wide_cases:0,prefix_cases:0,fallback_cases:0,equal_cases:0};
 function check(r,memory,sar){
   const x=emulate(ar,r,memory,undefined,sar),y=emulate(br,r,memory,visited,sar);
   for(let i=1;i<16;i++)if(i!==3)assert.equal(y.registers[i],x.registers[i],'Register a'+i);
   assert.equal(y.sar,x.sar,'SAR changed');assert.equal(x.registers[8],memory.get(memory.rowBase+4*x.registers[12]));
   return{x,y};
 }
 for(const {n,address:B,values}of t.rows)for(let K=n;K<n+values.length-1;K++){
   const memory=new Map([...extra,...values.slice(0,K-n+1).map((v,i)=>[B+4*(n+i),v])]);memory.rowBase=B;
   for(let tail=n;tail<=K;tail++){
     const low=values[tail-n],high=values[tail-n+1]-1,points=new Set([low,high,low+Math.floor((high-low)/2)]);
     // CLZ may change INSIDE an answer interval. Cover both sides of every
     // power-of-two boundary, not just the original U interval endpoints.
     for(let e=0;e<=32;e++)for(const v of[2**e-1,2**e])if(v>=low&&v<=high)points.add(v);
     for(const index of points)for(const seed of[0,0xffffffff]){
       const r=Array.from({length:16},(_,i)=>Math.imul(seed+i,0x45d9f3b)>>>0);
       r[2]=index;r[6]=B;r[9]=(K<<16)>>>0;r[11]=values[0];r[12]=K;r[13]=n;r[15]=B+4*(K+1);r[5]=K;
       const {x,y}=check(r,memory,(seed+K+n)&63);assert.equal(y.registers[12],tail);assert.equal(y.registers[8],low);
       linearReads+=x.reads.length;prefixReads+=y.reads.length;maxSteps=Math.max(maxSteps,y.steps);cases++;
       const calls=y.reads.filter(at=>at===dataAddress).length;
       if(K-n>=8){
         guard.wide_cases++;const threshold=values[K-4-n];
         assert.equal(index<threshold,tail<=K-5);
         assert.equal(calls,index<threshold?1:0,'Guard chooses wrong path');
         if(index<threshold){guard.prefix_cases++;const phase=Math.clz32(index)&3;if(!witnesses.has(phase))witnesses.set(phase,{r,memory});}
         else guard.fallback_cases++;
         if(index===threshold)guard.equal_cases++;
       }else assert.equal(calls,0,'Short search must stay linear');
     }
   }
 }
 assert.equal(witnesses.size,4);
 for(const {r,memory}of witnesses.values())for(let sar=0;sar<64;sar++){check(r,memory,sar);extraSarCases++;}
 for(const row of h)assert.ok(visited.has(row.address),'Uncovered helper instruction');
 assert.ok(guard.prefix_cases>0&&guard.fallback_cases>0&&guard.equal_cases>0);
 return{cases,guard,extra_sar_cases:extraSarCases,helper_instructions_covered:h.length,linear_reads:linearReads,prefix_reads_including_literal:prefixReads,max_candidate_instructions:maxSteps,
 stack_bytes:48,stack_delta:0,static_ram_delta:0,stores:0,sar_preserved:true,
 invariant:'K-N>=8 proves U(N,K-4) is in range. Only index<U(N,K-4), equivalent to answer<=K-5, enters the prefix helper; equality stays linear. For e=floor(log2(index)), table[N,e] is the greatest stored j with U(N,j)<=2^(e+1)-1, >= the true answer. MIN with original K preserves that bound; exact descending search terminates at unchanged index>=U(N,N). Packed reads are aligned32-bit and SAR is restored before any data branch. Short K-N<8 searches remain linear.',
 scope:'Every U interval at boundaries/midpoint AND both sides of every CLZ boundary, two register seeds; all64 SAR states for every packed-byte phase. Actual linked instructions, not CPU timings. a0/a3 dead at join; all other GPRs/SAR match. Prefix table may contain conservative extra row-end bounds, clamped by original K.'};
}
module.exports={site,siteBytes,done,helper,helperBytes,storageAddress,storageBytes,dataAddress,dataBytes,prefixAddress,prefixBytes,inside,auditSite,storage,table,prefix,prefixProof,emulate,checkHelper,prove};
