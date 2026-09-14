// Exact modular32 interpreter for the linked MDCT post-rotation, not a CPU emulator.
const assert=require('node:assert/strict'),base=require('./frozen_reloads.cjs'),three=require('./mdct_three_pair.cjs');
const atom=s=>({[s]:1}),key=v=>typeof v==='number'?'#'+(v>>>0):JSON.stringify(v);
function scale(v,n){if(typeof v==='number')return Math.imul(v,n)>>>0;const out={};for(const k of Object.keys(v).sort()){const c=Math.imul(v[k],n)>>>0;if(c)out[k]=c;}return Object.keys(out).length?out:0;}
function add(a,b){if(typeof a==='number'&&typeof b==='number')return(a+b)>>>0;const out={};for(const v of [a,b])for(const[k,c]of Object.entries(typeof v==='number'?(v?{'1':v>>>0}:{}):v))out[k]=((out[k]||0)+c)>>>0;return scale(out,1);}
function op2(op,a,b){if(typeof a==='number'&&typeof b==='number'){if(op==='mull')return Math.imul(a,b)>>>0;if(op==='and')return(a&b)>>>0;}assert.equal(op,'mull');return atom('mul32('+[key(a),key(b)].sort().join(',')+')');}
function shift(op,a,n){assert.ok(n>=0&&n<32);if(op==='slli')return scale(a,2**n);return typeof a==='number'?(a>>n)>>>0:atom('sar'+n+'('+key(a)+')');}
function interpret(rs,p,regs,memory,iterations){const state=structuredClone(regs),mem=new Map(memory),map=new Map(rs.map(r=>[r.address,r])),events=[],boundaries=[];let pc=p.address,steps=0;
 while(pc!==p.address+p.bytes){assert.ok(++steps<=iterations*140,'Unexpected loop');const r=map.get(pc);assert.ok(r,'Invalid instruction boundary');const a=r.args.split(/,\s*/),[d,s,n]=a;pc+=r.bytes;
  const address=(r,o)=>{assert.equal(typeof state[r],'number','Symbolic memory address');const x=(state[r]+Number(o))>>>0;assert.equal(x%4,0,'Unaligned32 access');return x;};
  switch(r.op.replace('.n','')){
   case'l32i':{const x=address(s,n);assert.ok(mem.has(x),'Unmapped read '+x.toString(16));state[d]=structuredClone(mem.get(x));events.push({kind:'read',address:x,value:structuredClone(state[d])});break;}
   case's32i':{const x=address(s,n);mem.set(x,structuredClone(state[d]));events.push({kind:'write',address:x,value:structuredClone(state[d])});break;}
   case'movi':state[d]=Number(s)>>>0;break;
   case'add':state[d]=add(state[s],state[n]);break;
   case'sub':state[d]=add(state[s],scale(state[n],-1));break;
   case'addi':state[d]=add(state[s],Number(n)>>>0);break;
   case'and':case'mull':state[d]=op2(r.op,state[s],state[n]);break;
   case'slli':case'srai':state[d]=shift(r.op,state[s],Number(n));break;
   case'extui':assert.equal(n,'0');assert.equal(a[3],'16');state[d]=typeof state[s]==='number'?state[s]&65535:atom('lo16('+key(state[s])+')');break;
   case'bbsi':assert.equal(s,'1');assert.equal(typeof state[d],'number');if(state[d]&2)pc=three.target(r);break;
   case'bnone':assert.equal(typeof state[d],'number');assert.equal(typeof state[s],'number');if(!(state[d]&state[s]))pc=three.target(r);break;
   case'bge':assert.equal(typeof state[d],'number');assert.equal(typeof state[s],'number');if((state[d]|0)>=(state[s]|0))pc=three.target(r);break;
   case'j':pc=three.target(r);break;
   default:assert.fail('Unproved opcode '+r.op);
  }
  if(pc===p.address||pc===p.address+p.bytes)boundaries.push({state:structuredClone(state),steps,events:events.length});
 }assert.equal(boundaries.length,iterations);return{state,events,boundaries,steps};}
function exitLiveness(disassembly,p){const rs=base.rows(disassembly),index=new Map(rs.map((r,i)=>[r.address,i])),first=index.get(p.address+p.bytes),initial=['a0','a2','a3','a4','a5','a6','a7','a8','a10','a11','a12','a13','a14'];assert.ok(Number.isInteger(first));const states=new Map([[first,new Set(initial)]]),queue=[first];let visits=0;
 while(queue.length){assert.ok(++visits<5000);const i=queue.shift(),r=rs[i],op=r.op.replace('.n',''),args=r.args.split(/,\s*/),pending=new Set(states.get(i));let reads=[],dest;
  if(op==='ret')reads=['a0'];else if(/^b|^j$/.test(op))reads=args.filter(x=>/^a\d+$/.test(x));else if(op==='s32i')reads=args.filter(x=>/^a\d+$/.test(x));
  else{assert.ok(['movi','l32i','l32r','slli','srai','extui','add','addi','sub','and','mull','mov'].includes(op),'Unexpected tail op '+r.text);dest=args[0];reads=args.slice(1).filter(x=>/^a\d+$/.test(x));}
  for(const x of reads)assert.ok(!pending.has(x),'Changed loop scratch read before overwrite: '+r.text);if(dest)pending.delete(dest);if(op==='ret')continue;
  const branch=/^b|^j$/.test(op),next=branch?[index.get(three.target(r)),...(op==='j'?[]:[i+1])]:[i+1];
  for(const n of next){assert.ok(Number.isInteger(n)&&n>=0&&n<rs.length);const prior=states.get(n),merged=new Set([...(prior||[]),...pending]);if(!prior||merged.size!==prior.size){states.set(n,merged);queue.push(n);}}
 }return {entry:p.address+p.bytes,changed_registers:initial,visited_instructions:states.size,return_restored:true};}
function fixture(t,i,limit,symbolic=true,baseAddress=0x3ffe1000){const sp=0x3ffe0000,front=baseAddress+i*8,back=baseAddress+(t.n-i-1)*8,regs=Object.fromEntries(Array.from({length:16},(_,k)=>['a'+k,symbolic?atom('R'+k):0]));Object.assign(regs,{a1:sp,a9:t.t0+2*i,a15:front,a11:2,a12:0xfffffffc});
 const memory=new Map([[sp,back],[sp+4,i],[sp+8,(2*t.t0+2*t.n-2)>>>0],[sp+12,(2*t.t0+4*t.n-2)>>>0],[sp+16,2*t.n],[sp+20,limit]]);return{regs,memory,sp,baseAddress};}
function prove(before,after,p,t){three.validateOutside(before,after,p);const select=s=>base.rows(s).filter(r=>r.address>=p.address&&r.address<p.address+p.bytes),a=select(before),b=select(after);let pairs=0;const phases=[];
 for(const x of t.supported_standard_transforms){assert.equal(x.n%4,0);assert.equal(x.t0%4,0);for(let i=0;i<x.n/2;i+=2){const{regs,memory,sp}=fixture(x,i,i+2);for(let j=0;j<2;j++)for(const [side,ptr]of [['F',regs.a15+j*8],['B',memory.get(sp)-j*8]]){memory.set(ptr,atom(side+j+'re'));memory.set(ptr+4,atom(side+j+'im'));}
  for(const[address,name]of [[x.t0+2*i,'T0'],[x.t1+2*i,'T1'],[x.t0+2*(x.n-i-2),'R0'],[x.t0+2*(2*x.n-i-2),'R1']]){assert.equal(address%4,0);assert.ok(!memory.has(address));memory.set(address,atom(name));}
  const old=interpret(a,p,regs,memory,2),now=interpret(b,p,regs,memory,2),mutable=e=>e.address<0x40200000&&![sp+8,sp+12,sp+16].includes(e.address);assert.deepEqual(now.events.filter(mutable),old.events.filter(mutable),'PCM/stack event order or value differs');
  for(const offset of [8,12,16]){assert.ok(!old.events.some(e=>e.kind==='write'&&e.address===sp+offset));assert.ok(!now.events.some(e=>e.kind==='write'&&e.address===sp+offset));assert.equal(old.events.filter(e=>e.address===sp+offset).length,2);assert.equal(now.events.filter(e=>e.address===sp+offset).length,1);}
  assert.equal(old.events.filter(e=>e.address>=0x40200000).length,8);assert.equal(now.events.filter(e=>e.address>=0x40200000).length,4);
  for(let j=0;j<2;j++)for(const r of ['a1','a9','a15'])assert.deepEqual(now.boundaries[j].state[r],old.boundaries[j].state[r]);
  if(!phases.length)for(let j=0;j<2;j++)phases.push({half:j,old_instructions:old.boundaries[j].steps-(old.boundaries[j-1]?.steps||0),new_instructions:now.boundaries[j].steps-(now.boundaries[j-1]?.steps||0)});pairs++;}}
 const liveness=exitLiveness(after,p);return{pairs,phases,arbitrary_pcm32:true,arbitrary_table_words:true,in_place_events_exact:true,table_loads_per_pair:{old:8,new:4},invariant_stack_loads_per_pair:{old:6,new:3},sar:'unchanged',frame_bytes:96,liveness};}
module.exports={atom,interpret,fixture,prove,exitLiveness};
