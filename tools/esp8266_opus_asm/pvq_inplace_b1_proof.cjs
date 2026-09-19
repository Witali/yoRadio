// Checks actual linked instructions, not merely the host C semantic mirror.
// This small ISA interpreter is a differential test, not a cycle simulator.
const assert=require('node:assert/strict');
const base=require('./frozen_reloads.cjs'),recipe=require('./pvq_inplace_b1.cjs');
const {readAt}=require('./pvq_exp2_table32_proof.cjs');
const {table}=require('./pvq_n3_diff_proof.cjs');
function plain(s){return base.normalized(s).replace(/\.n$/,'').replace(/\s+<[^>]*>$/,'');}
const flashWords=new WeakMap();
function flashRead(elf,at){
 let words=flashWords.get(elf);if(!words){words=new Map();flashWords.set(elf,words);}
 if(!words.has(at))words.set(at,readAt(elf,at,4).readUInt32LE());return words.get(at);
}
function program(dis){return new Map(base.rows(dis).map(r=>{
 const [op,...rest]=plain(r.text).split(' '),args=rest.join(' ').split(/,\s*/);
 return[r.address,{...r,op,args}];
}));}
function interpret(code,{registers,start,stop,read,write,call,limit=30000,visited=new Set()}){
 const r=registers.slice();let pc=start,sar=0,steps=0;const calls=[];
 const reg=s=>{assert.match(s,/^a(?:[0-9]|1[0-5])$/);return +s.slice(1);};
 while(pc!==stop){
  assert.ok(++steps<limit,'Instruction limit');const row=code.get(pc);assert.ok(row,'Unknown PC '+pc.toString(16));visited.add(pc);
  const {op,args:a}=row,v=i=>r[reg(a[i])],d=()=>reg(a[0]);let next=pc+row.bytes,x;
  if(op==='ret')next=r[0];
  else if(op==='j')next=parseInt(a[0],16);
  else if(op==='call0'){
   const target=parseInt(a[0],16);calls.push({target,args:r.slice(2,8)});r[0]=next;call(target,r);
  }else if(/^b/.test(op)){
   const u=v(0),s=u|0;
   if(op==='beqz')x=u===0;else if(op==='bnez')x=u!==0;else if(op==='bgez')x=s>=0;else if(op==='bltz')x=s<0;
   else if(op==='beqi')x=s===Number(a[1]);else if(op==='bnei')x=s!==Number(a[1]);
   else if(op==='blti')x=s<Number(a[1]);else if(op==='bgei')x=s>=Number(a[1]);
   else if(op==='beq')x=u===v(1);else if(op==='bne')x=u!==v(1);
   else if(op==='blt')x=s<(v(1)|0);else if(op==='bge')x=s>=(v(1)|0);
   else if(op==='bltu')x=u<v(1);else if(op==='bgeu')x=u>=v(1);else assert.fail(op);
   if(x)next=parseInt(a.at(-1),16);
  }else if(op==='ssr')sar=v(0)&31;
  else if(op==='ssl')sar=32-(v(0)&31);
  else if(op==='s32i'||op==='s16i')write((v(1)+Number(a[2]))>>>0,op==='s32i'?4:2,v(0));
  else{
   if(op==='mov')x=v(1);else if(op==='movi')x=Number(a[1]);
   else if(op==='addi'||op==='addmi')x=v(1)+Number(a[2]);
   else if(op==='add')x=v(1)+v(2);else if(op==='sub')x=v(1)-v(2);else if(op==='neg')x=-v(1);
   else if(op==='or')x=v(1)|v(2);else if(op==='and')x=v(1)&v(2);else if(op==='xor')x=v(1)^v(2);
   else if(op==='slli')x=v(1)<<Number(a[2]);else if(op==='srli')x=v(1)>>>Number(a[2]);else if(op==='srai')x=v(1)>>Number(a[2]);
   else if(op==='sra')x=sar>=32?(v(1)|0)<0?-1:0:v(1)>>sar;
   else if(op==='srl')x=sar>=32?0:v(1)>>>sar;else if(op==='sll')x=sar===0?0:v(1)<<(32-sar);
   else if(op==='nsau')x=Math.clz32(v(1));
   else if(op==='mull')x=Math.imul(v(1),v(2));
   else if(op==='mul16s')x=Math.imul((v(1)<<16)>>16,(v(2)<<16)>>16);
   else if(op==='l32r')x=read(parseInt(a[1],16),4);
   else if(op==='l32i'||op==='l16si'){x=read((v(1)+Number(a[2]))>>>0,op==='l32i'?4:2);if(op==='l16si')x=(x<<16)>>16;}
   else if(op==='extui')x=(v(1)>>>Number(a[2]))&(2**Number(a[3])-1);
   else if(op==='moveqz'||op==='movnez')x=(op==='moveqz'?v(2)===0:v(2)!==0)?v(1):v(0);
   else assert.fail('Unimplemented '+op);
   r[d()]=x>>>0;
  }
  pc=next;
 }
 return{r,sar,steps,calls,visited};
}
function structural({source,syms,dis,before,after}){
 let compared=0;const changes=[];
 for(const f of source.functions){
  const rows=base.rows(dis[f.name]),map=new Map(rows.map(r=>[r.address,r])),covered=new Set();
  for(const n of f.nodes){let pc=syms[recipe.label(n.old)];assert.ok(Number.isFinite(pc));
   for(const op of n.ops){
    const row=map.get(pc);assert.ok(row,'Missing instruction at '+pc.toString(16));
    const expected=op.replace(/\b(?:ip_[a-z0-9_]+|inplace_decode16)\b/g,name=>{assert.ok(Number.isFinite(syms[name]),name);return syms[name].toString(16);});
    assert.equal(plain(row.text),plain(expected));covered.add(pc);pc+=row.bytes;compared++;
   }
  }
  assert.equal(covered.size,rows.length,'Unaccounted instructions');
 }
 for(const[address,x]of source.literals){assert.equal(readAt(before,address,4).readUInt32LE(),x.value);assert.equal(readAt(after,syms[x.name],4).readUInt32LE(),x.value);}
 const guardOps=base.rows(dis.guard).map(r=>plain(r.text));
 assert.deepEqual(guardOps,[`bnei a6, 1, ${syms.ip_fallback.toString(16)}`,`blti a4, 1, ${syms.ip_fallback.toString(16)}`,'srli a8, a4, 15',`bnez a8, ${syms.ip_fallback.toString(16)}`,`j ${syms.inplace_unquant.toString(16)}`,'addi a1, a1, -112',`j ${(recipe.site+3).toString(16)}`]);
 assert.deepEqual(readAt(after,recipe.site+3,778-3),readAt(before,recipe.site+3,778-3),'Fallback body changed');
 for(const f of source.functions){
  const stack=base.rows(dis[f.name]).filter(r=>/^addi/.test(r.op)&&r.args.startsWith('a1,'));
  assert.deepEqual(stack.map(r=>plain(r.text)),['addi a1, a1, '+(f.name==='inplace_unquant'?-112:-48),'addi a1, a1, '+(f.name==='inplace_unquant'?112:48)]);
 }
 return{instructions_compared:compared,literals:source.literals.length,fallback_body_exact:true,stack_frames:[112,48]};
}
function memory(elf,n,width){
 const stackBase=0x3ffe1000,outputBase=0x3ffe2000,stack=Buffer.alloc(160,0xcd),output=Buffer.alloc(n*width,0xaa),writes=[];
 const region=(at,size)=>at>=stackBase&&at+size<=stackBase+stack.length?[stack,at-stackBase]:at>=outputBase&&at+size<=outputBase+output.length?[output,at-outputBase]:null;
 const read=(at,size)=>{
  assert.equal(at%size,0,'Unaligned read');const z=region(at,size);if(z)return size===2?z[0].readUInt16LE(z[1]):z[0].readUInt32LE(z[1]);
  assert.equal(size,4,'Halfword access outside DRAM');assert.ok(at>=0x40200000&&at<0x40300000,'Out-of-range read '+at.toString(16));return flashRead(elf,at);
 };
 const write=(at,size,v)=>{
  assert.equal(at%size,0,'Unaligned write');const z=region(at,size);assert.ok(z,'Out-of-range write '+at.toString(16));
  if(z[0]===output){assert.equal(size,width);writes.push(at);}
  if(size===2)z[0].writeUInt16LE(v&65535,z[1]);else z[0].writeUInt32LE(v>>>0,z[1]);
 };
 return{stackBase,outputBase,stack,output,writes,read,write};
}
function vectors({info,dis,before,after,syms}){
 const a=program(info.functions.decode_pulses.disassembly),b=program(dis.inplace_decode16),specs=[];
 const t=table(before);assert.deepEqual(table(after),t);
 // Unlike direct cwrsi host tests, the public decode_pulses also reads the
 // finite U table. K=32767 is a storage-bound test, NOT a valid table index.
 for(let k=1;k<=175;k++)specs.push([2,k,4*k]);
 for(const row of t.rows)for(let k=row.n;k<row.n+row.values.length-1;k++){
  const v=row.values[k-row.n]+row.values[k+1-row.n];if(v<=0xffffffff)specs.push([row.n,k,v]);
 }
 for(let n=3;n<=176;n++)for(let k=1;k<=2;k++)specs.push([n,k,k===1?2*n:2*n*n]);
 let seed=0x6b18cd32,cases=0,maxSteps=0;const va=new Set(),vb=new Set();
 for(const[n,k,bound]of specs)for(let trial=0;trial<67;trial++){
  seed=(Math.imul(seed,1664525)+1013904223)>>>0;const index=trial===0?0:trial===1?bound-1:trial===2?Math.floor(bound/2):seed%bound;
  const execute=(code,elf,width,start,visited)=>{
   const m=memory(elf,n,width),registers=Array.from({length:16},(_,i)=>Math.imul(seed+i,0x45d9f3b)>>>0);
   registers[0]=0x12345678;registers[1]=m.stackBase+128;registers[2]=m.outputBase;registers[3]=n;registers[4]=k;registers[5]=0x55555550;
   const e=interpret(code,{registers,start,stop:registers[0],read:m.read,write:m.write,visited,call:(target,r)=>{
    assert.equal(target,0x40246c20);assert.equal(r[2],registers[5]);assert.equal(r[3],bound);
    // A real call may destroy ALL caller-saved temporaries and SAR.
    for(let j=2;j<12;j++)r[j]=Math.imul(seed+j,0x27d4eb2d)>>>0;r[2]=index;
   }});
   assert.equal(e.calls.length,1);for(const j of[0,1,12,13,14,15])assert.equal(e.r[j],registers[j],'ABI a'+j);
   assert.equal(m.writes.length,n);assert.equal(new Set(m.writes).size,n);
   const output=Array.from({length:n},(_,i)=>width===2?m.output.readInt16LE(i*2):m.output.readInt32LE(i*4));
   assert.equal(output.reduce((s,v)=>s+Math.abs(v),0),k);maxSteps=Math.max(maxSteps,e.steps);return{output,ryy:e.r[2]};
  };
  assert.deepEqual(execute(a,before,4,info.functions.decode_pulses.address,va),execute(b,after,2,syms.inplace_decode16,vb));cases++;
 }
 return{cases,exact:true,redzones:true,callee_saved:true,entropy_call_arguments_exact:true,max_instructions:maxSteps,covered_original:va.size,covered_candidate:vb.size};
}
function guards({dis,syms}){
 const code=program(dis.guard);let cases=0;
 for(const b of[-1,0,1,2,4,8,16,2147483647])for(const k of[-2147483648,-1,0,1,2,128,32767,32768,65535,2147483647]){
  const registers=Array.from({length:16},(_,i)=>0x10000000+i*16);registers[6]=b>>>0;registers[4]=k>>>0;
  const fast=b===1&&k>0&&k<=32767,stop=fast?syms.inplace_unquant:recipe.site+3;
  const e=interpret(code,{registers,start:syms.ip_guard,stop,read:()=>assert.fail(),write:()=>assert.fail(),call:()=>assert.fail()});
  for(let j=0;j<16;j++)if(j!==8)assert.equal(e.r[j],j===1&&!fast?registers[1]-112:registers[j]);cases++;
 }
 return{cases,exact:true,no_extra_stack:true};
}
function normalisation({info,dis,before,after,syms}){
 const a=program(info.functions.alg_unquant.disassembly),b=program(dis.inplace_unquant);
 let seed=123,cases=0;
 for(let n=2;n<=176;n++)for(const gain of[0,1,37,16384,32767])for(const amplitude of[1,128,2047]){
  const raw=Array.from({length:n},()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed%(amplitude*2+1))-amplitude;});
  if(raw.every(x=>x===0))raw[0]=1;const energy=raw.reduce((s,x)=>s+x*x,0);
  const rsqrt=1+seed%32767,calls=[];
  const execute=(code,elf,width,start,stop)=>{
   const m=memory(elf,n,width),out=Buffer.alloc(n*2),rawBase=0x3ffe3000;
   raw.forEach((x,i)=>width===2?m.output.writeInt16LE(x,i*2):m.output.writeInt32LE(x,i*4));
   const registers=Array.from({length:16},(_,i)=>0x10000000+i*16);
   registers[1]=m.stackBase;registers[2]=energy;registers[12]=width===2?m.outputBase:rawBase;registers[13]=m.outputBase;
   m.stack.writeUInt32LE(n,16);m.stack.writeInt32LE(gain,20);m.stack.writeUInt32LE(1,68);
   const e=interpret(code,{registers,start,stop,call:(target,r)=>{assert.equal(target,0x40246e54);calls.push(r[2]);for(let j=2;j<12;j++)r[j]=Math.imul(seed+j,0x27d4eb2d)>>>0;r[2]=rsqrt;},
    read:m.read,write:(at,size,v)=>{if(width===4&&at>=rawBase&&at+size<=rawBase+n*2){assert.equal(size,2);out.writeUInt16LE(v&65535,at-rawBase);}else m.write(at,size,v);}});
   return width===2?m.output:out;
  };
  assert.deepEqual(execute(a,before,4,0x402493f4,0x40249472),execute(b,after,2,syms[recipe.label(0x402493f4)],syms[recipe.label(0x40249472)]));
  assert.equal(calls.length,2);assert.equal(calls[0],calls[1]);cases++;
 }
 return{cases,exact:true,scope:'Actual normalisation instructions with equal rsqrt result and caller-saved clobbers; full rsqrt/rotation arithmetic retained structurally, not replaced.'};
}
function prove(data){return{structural:structural(data),guards:guards(data),vectors:vectors(data),normalisation:normalisation(data),
 limitations:'Differential ISA interpreter is not timing evidence or exhaustive valid-packet validation; host full PCM suite and physical RAM-packet benchmark remain required.',
 scratch:'B=1 mask is constant 1. Cloned pulse decode, normalisation and original inline rotation have no arena calls; old path retained for other B/K. Global peak is unchanged.'};}
module.exports={plain,program,interpret,structural,vectors,guards,normalisation,prove};
