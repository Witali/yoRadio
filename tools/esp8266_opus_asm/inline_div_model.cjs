// Execute the actual linked inline graph, not a hand-written quotient formula.
// ROM fallback is an exit with untouched arguments; division by zero is not
// assigned invented semantics. This model is not a hardware timing estimate.
const assert=require('node:assert/strict');
const {table}=require('./small_div.cjs');
function compile(graph){
 const ops=graph.map(s=>{const i=s.indexOf(' ');return [s.slice(0,i),...s.slice(i+1).split(/,\s*/)];});
 const supported=new Set(['movi','mov','neg','and','nsau','sub','add','addi','ssr','srl','srli','extui','mul16u','mull','addx4','l32r','l32i','bltu','bgeu','beqz','bnez','beqi','bnei','j','call0','ret']);
 for(const [op,...args]of ops){assert.ok(supported.has(op),'Unsupported '+op);for(const a of args)if(a.startsWith('instruction:'))assert.ok(+a.slice(12)<ops.length&&+a.slice(12)>=0);}
 return (n,d,initial)=>{
  const r=initial?Uint32Array.from(initial):new Uint32Array(16);r[2]=n;r[3]=d;
  const reg=s=>+s.slice(1),value=s=>s.startsWith('a')?r[reg(s)]:Number(s),target=s=>+s.slice(12);
  let pc=0,sar=0,count=0;
  while(count++<100){assert.ok(ops[pc],'Invalid PC');const [op,a,b,c,e]=ops[pc++],dst=reg(a);switch(op){
   case 'movi':r[dst]=Number(b);break;case 'mov':r[dst]=value(b);break;
   case 'neg':r[dst]=-value(b);break;case 'and':r[dst]=value(b)&value(c);break;
   case 'nsau':r[dst]=Math.clz32(value(b));break;
   case 'sub':r[dst]=value(b)-value(c);break;case 'add':case 'addi':r[dst]=value(b)+value(c);break;
   case 'ssr':sar=value(a)&31;break;case 'srl':r[dst]=value(b)>>>sar;break;
   case 'srli':r[dst]=value(b)>>>Number(c);break;
   // GAS encodes SRLI 16 as EXTUI 16,16 on LX106.
   case 'extui':assert.ok(c==='0'||c==='16');assert.equal(e,'16');r[dst]=(value(b)>>>Number(c))&65535;break;
   case 'mul16u':r[dst]=(value(b)&65535)*(value(c)&65535);break;
   case 'mull':r[dst]=Math.imul(value(b),value(c));break;
   case 'addx4':r[dst]=value(b)*4+value(c);break;
   case 'l32r':assert.equal(b,'literal:yoradio_opus_small_div_table');r[dst]=0x40200000;break;
   case 'l32i':{const address=value(b)+Number(c);assert.equal(address%4,0);const i=(address-0x40200000)/4;assert.ok(i>=0&&i<table.length);r[dst]=table[i];break;}
   case 'bltu':if(value(a)<value(b))pc=target(c);break;
   case 'bgeu':if(value(a)>=value(b))pc=target(c);break;
   case 'beqz':if(value(a)===0)pc=target(b);break;
   case 'bnez':if(value(a)!==0)pc=target(b);break;
   case 'beqi':if(value(a)===Number(b))pc=target(c);break;
   case 'bnei':if(value(a)!==Number(b))pc=target(c);break;
   case 'j':pc=target(a);break;
   case 'call0':assert.equal(a,'0x4000e21c');return {registers:r,count,fallback:true};
   case 'ret':return {result:r[2],registers:r,count,fallback:false};
  }}throw Error('Inline graph failed to terminate');
 };
}
function validate(graph){
 const exec=compile(graph);let seed=0x17593171,cases=0,fallbacks=0;
 const rand=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0;};
 const check=(n,d)=>{const initial=Array.from({length:16},rand),out=exec(n,d,initial);
  assert.equal(out.fallback,false);assert.equal(out.result,Number(BigInt(n)/BigInt(d)),n+'/'+d);
  for(const k of [0,1,12,13,14,15])assert.equal(out.registers[k],initial[k]);cases++;
 };
 for(let d=1;d<=256;d++){
  for(const n of [0,1,d-1,d,d+1,0x7fffffff,0x80000000,0xfffffffe,0xffffffff])check(n,d);
  for(let i=0;i<1024;i++){const n=rand();check(n,d);const p=Math.floor(n/d)*d;
   for(const k of [-1,0,1])if(p+k>=0&&p+k<=0xffffffff)check(p+k,d);
  }
 }
 for(const d of [0,257,65535,0x80000000,0xffffffff])for(const n of [0,1,0x80000000,0xffffffff]){
  const initial=Array.from({length:16},rand),out=exec(n,d,initial);assert.equal(out.fallback,true);
  assert.equal(out.registers[2],n);assert.equal(out.registers[3],d);
  for(const k of [0,1,12,13,14,15])assert.equal(out.registers[k],initial[k]);fallbacks++;
 }
 return {cases,fallbacks,passed:true,scope:'Instruction graph semantics and call0 ABI, not hardware speed'};
}
module.exports={compile,validate};
