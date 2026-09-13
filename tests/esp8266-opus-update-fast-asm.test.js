const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component}=require('../tools/esp8266_opus_asm/export.cjs');
const {transform,source}=require('../tools/esp8266_opus_asm/update_fast.cjs');
const {verify}=require('../tools/esp8266_opus_asm/verify.cjs');
const macro=fs.readFileSync(path.join(root,'tools/esp8266_opus_asm/update_fast.inc.s'),'utf8').replace(/\r\n/g,'\n');
test('two decoder call sites only; protected baseline and shared function unchanged',()=>{
 const original=fs.readFileSync(path.join(component,'asm/lx106/gcc',source+'.s'),'utf8').replace(/\r\n/g,'\n');
 const changed=transform(original);
 assert.equal(changed,transform(original.replace(/\n/g,'\r\n')));
 assert.throws(()=>transform(changed));
 assert.equal((changed.match(/\tY_OPUS_UPDATE_FAST\t/g)||[]).length,2);
 assert.equal(changed.slice(macro.length+1).replace(/\tY_OPUS_UPDATE_FAST\t# No-normalize path; original cold call and ABI\./g,'\tcall0\tec_dec_update\t\t#'),original);
 const r=verify('bands-update-fast-asm');assert.equal(r.files.length,110);
 assert.equal(r.files.filter(f=>f.includes('bands-update-fast')).length,1);
 assert.doesNotMatch(macro,/\b(?:l8ui|l16ui|l16si|s8i|s16i|rsil|l32r|ssr|ssl)\b/);
});
const code=macro.split(/\r?\n/).map(l=>l.split('#')[0].trim()).filter(l=>l&&!/^\.(?:macro|endm)\b/.test(l)).map(l=>l.replaceAll(',',' ').split(/\s+/));
const labels=new Map(code.flatMap(([op],i)=>op.endsWith(':')?[[op.slice(0,-1),i]]:[]));
function simulate(ctx,fl,fh,ft){
 const r=Uint32Array.from({length:16},(_,i)=>0xc0000100+i);
 r[2]=0x1000;r[3]=fl;r[4]=fh;r[5]=ft;const before=r.slice(),w=ctx.slice();let cold=false,steps=0;
 const v=a=>r[Number(a.slice(1))],set=(a,x)=>r[Number(a.slice(1))]=x;
 const offset=(a,n)=>{const p=v(a)+Number(n)-0x1000;assert.ok(p>=0&&p<48&&!(p&3));return p/4;};
 for(let pc=0;pc<code.length;pc++){
  assert.ok(++steps<40);
  const [opcode,a,b,c]=code[pc],op=opcode.replace(/\.n$/,'');
  switch(op){
   case 'l32i':set(a,w[offset(b,c)]);break;
   case 's32i':w[offset(b,c)]=v(a);break;
   case 'movi':set(a,Number(b));break;
   case 'slli':set(a,v(b)<<Number(c));break;
   case 'sub':set(a,v(b)-v(c));break;
   case 'mull':set(a,Math.imul(v(b),v(c)));break;
   case 'beqz':if(v(a)===0)pc=labels.get(b);break;
   case 'bgeu':if(v(a)>=v(b))pc=labels.get(c);break;
   case 'j':pc=labels.get(a);break;
   case 'call0':
    assert.equal(a,'ec_dec_update');cold=true;
    assert.deepEqual(w,ctx,'fallback must observe UNCHANGED state');
    assert.deepEqual(r.slice(2,6),before.slice(2,6),'fallback must get ORIGINAL arguments');
    break;
   default:assert.ok(op.endsWith(':'),'Unknown instruction '+op);
  }
 }
 const wrap=n=>Number(BigInt.asUintN(32,n));
 const s=wrap(BigInt(ctx[9])*BigInt((ft-fh)>>>0));
 const rng=fl?wrap(BigInt(ctx[9])*BigInt((fh-fl)>>>0)):(ctx[7]-s)>>>0;
 assert.equal(cold,rng<=0x800000,'threshold equality must normalize');
 const expected=ctx.slice();if(!cold){expected[7]=rng;expected[8]=(ctx[8]-s)>>>0;}
 assert.deepEqual(w,expected);
 for(const i of [0,1,2,3,4,5,10,11,12,13,14,15])assert.equal(r[i],before[i],'preserved a'+i);
 return cold;
}
test('100000 real macro executions preserve uint32 math, registers and cold-path state',()=>{
 let seed=0x31415926,fast=0,cold=0;
 const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let k=0;k<100000;k++){
  const ctx=Uint32Array.from({length:12},rnd);
  ctx[7]=(rnd()&0x7fffffff)|0x800001;
  const ft=2+rnd()%65534,fl=k%3===0?0:rnd()%ft,fh=fl+1+rnd()%(ft-fl);
  ctx[9]=Math.floor(ctx[7]/ft);
  if(simulate(ctx,fl,fh,ft))cold++;else fast++;
 }
 for(const ext of [0x7fffff,0x800000,0x800001,0x1000000]){
  const ctx=new Uint32Array(12);ctx[7]=3*ext;ctx[8]=3*ext-1;ctx[9]=ext;
  simulate(ctx,1,2,3);simulate(ctx,0,1,3);
 }
 assert.ok(fast>0&&cold>0);
});
