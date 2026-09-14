const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const recipe=require('../tools/esp8266_opus_asm/logp.cjs'),{parse}=require('../tools/esp8266_opus_asm/logp_model.cjs');
const original=recipe.baseline(),candidate=recipe.transform(original);
function machine(text){
 const {ops,labels,literals}=parse(text);
 return (initial,packet,logp)=>{
  const w=initial.slice(),r=Array.from({length:16},(_,i)=>(0x76543000+i)>>>0),stack=new Map();
  r[1]=4096;r[2]=256;r[3]=logp;let pc=0,sar=0,steps=0,stackWrites=0,reads=0;
  const val=x=>/^a\d+$/.test(x)?r[+x.slice(1)]:Number(x),set=(x,v)=>r[+x.slice(1)]=v>>>0;
  while(pc<ops.length){
   assert.ok(++steps<400,'nonterminating normalization');const {op,args:[d,x,y,z]}=ops[pc++];
   if(op==='mov'||op==='movi')set(d,val(x));
   else if(op==='l32r')set(d,literals[x]);
   else if(op==='ssr')sar=val(d)&31;
   else if(op==='srl')set(d,val(x)>>>sar);
   else if(op==='slli')set(d,val(x)<<val(y));
   else if(op==='srai')set(d,(val(x)|0)>>val(y));
   else if(op==='extui')set(d,(val(x)>>>val(y))&((1<<val(z))-1));
   else if(op==='add'||op==='addi')set(d,val(x)+val(y));
   else if(op==='sub')set(d,val(x)-val(y));
   else if(op==='or')set(d,val(x)|val(y));
   else if(op==='xor')set(d,val(x)^val(y));
   else if(op==='and')set(d,val(x)&val(y));
   else if(op==='l32i'||op==='s32i'){
    const a=val(x)+val(y);assert.equal(a&3,0);
    if(a>=256&&a<304){if(op==='l32i')set(d,w[(a-256)/4]);else w[(a-256)/4]=val(d);}
    else {assert.ok(a>=4080&&a<4096,'outside stack frame');assert.equal(r[1],4080,'frame not allocated');
     if(op==='s32i'){stack.set(a,val(d));stackWrites++;}else {assert.ok(stack.has(a));set(d,stack.get(a));}}
   }else if(op==='l8ui'){
    const a=val(x)+val(y)-65536;assert.ok(a>=0&&a<packet.length,'outside input');reads++;set(d,packet[a]);
   }else if(op==='bltu'||op==='bgeu'){
    if(op==='bltu'?val(d)<val(x):val(d)>=val(x)){assert.ok(Object.hasOwn(labels,y));pc=labels[y];}
   }else if(op==='j')pc=labels[d];
   else if(op==='ret')break;
   else throw Error('Unsupported '+op);
  }
  assert.equal(r[0],0x76543000);assert.equal(r[1],4096);
  for(let i=12;i<16;i++)assert.equal(r[i],0x76543000+i,'callee a'+i);
  return {w,result:r[2],sar,steps,stackWrites,reads};
 };
}
function reference(initial,packet,logp){
 const w=initial.slice(),s=w[7]>>>logp,bit=Number(w[8]<s);
 if(!bit)w[8]=(w[8]-s)>>>0;w[7]=bit?s:(w[7]-s)>>>0;
 while(w[7]<=0x800000){
  w[5]=(w[5]+8)>>>0;w[7]=(w[7]<<8)>>>0;
  const prev=w[10];w[10]=w[6]<w[1]?packet[w[6]++]:0;
  const sym=((prev<<8)|w[10])>>1;
  w[8]=(((w[8]<<8)+(255&~sym))&0x7fffffff)>>>0;
 }
 return {w,result:bit};
}
test('logp complete ASM matches scalar math, padding and call0 ABI on 100000 states',()=>{
 const a=machine(original),b=machine(candidate);let seed=0xabcdef01,fast=0,cold=0;
 const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let n=0;n<100000;n++){
  const logp=n%32,range=n%4===0?0x1000000:n%4===1?0x80000000:0x800001+(rnd()%(0x80000000-0x800001));
  const split=range>>>logp,value=n%4===0?0:n%4===1?range-1:rnd()%range;
  const length=n%9,packet=Array.from({length},()=>rnd()&255),offset=n%3===0?length:length?rnd()%length:0;
  const w=Array.from({length:12},()=>rnd());w[0]=65536;w[1]=length;w[5]=rnd()&0xffff;w[6]=offset;w[7]=range;w[8]=value;w[10]=n%7===0?0xffffffff:rnd()&255;
  const aa=a(w,packet,logp),bb=b(w,packet,logp),ref=reference(w,packet,logp);
  assert.deepEqual(aa.w,ref.w);assert.deepEqual(bb.w,ref.w);assert.equal(aa.result,ref.result);assert.equal(bb.result,ref.result);
  assert.equal(bb.sar,aa.sar);assert.equal(bb.reads,aa.reads);assert.equal(aa.stackWrites,4);
  const rangeUpdated=value<split?split:range-split;
  if(rangeUpdated>0x800000){fast++;assert.equal(bb.stackWrites,0);assert.equal(aa.steps-bb.steps,11);}
  else {cold++;assert.equal(bb.stackWrites,4);assert.equal(bb.steps,aa.steps);}
 }
 assert.ok(fast>0&&cold>0);console.log({states:100000,fast,cold,scope:'actual ASM semantics; not cycles'});
});
test('only prefix changed; normalization identical, C default intact and generated overlay pinned',()=>{
 const a=recipe.body(original),b=recipe.body(candidate);
 assert.equal(a.slice(a.indexOf(recipe.cold)),b.slice(b.indexOf(recipe.cold)));
 assert.equal(candidate.replace(b,a),original);assert.throws(()=>recipe.transform(candidate));
 require('../tools/esp8266_opus_asm/verify.cjs').verify('bands-logp-asm');
 const {component}=require('../tools/esp8266_opus_asm/export.cjs');
 assert.match(fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8'),/set\(YORADIO_OPUS_BACKEND "c"/);
});
