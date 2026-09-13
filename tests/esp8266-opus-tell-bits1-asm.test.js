const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component}=require('../tools/esp8266_opus_asm/export.cjs');
const {transform,addBits,source}=require('../tools/esp8266_opus_asm/tell_bits1.cjs');
const tell=require('../tools/esp8266_opus_asm/tell_inline.cjs'),{verify}=require('../tools/esp8266_opus_asm/verify.cjs');
const macro=fs.readFileSync(path.join(root,'tools/esp8266_opus_asm/bits1_fast.inc.s'),'utf8').replace(/\r\n/g,'\n');
test('only three constant-one sites added to pinned tell-inline; C/GCC remain protected',()=>{
 const original=fs.readFileSync(path.join(component,'asm/lx106/gcc',source+'.s'),'utf8').replace(/\r\n/g,'\n');
 const parent=tell.transform(original,source),changed=transform(original);
 assert.equal(changed,addBits(parent));assert.equal(changed,transform(original.replace(/\n/g,'\r\n')));assert.throws(()=>addBits(changed));
 assert.equal((changed.match(/\tY_OPUS_BITS1_FAST\t/g)||[]).length,3);
 assert.equal(changed.slice(macro.length+1).replace(/\tY_OPUS_BITS1_FAST\t# Exact constant-one sign decode; original cold call\./g,'\tcall0\tec_dec_bits\t\t#'),parent);
 assert.equal((original.match(/ec_dec_bits\(ec, 1\)/g)||[]).length,3);
 // The one non-immediate site: a12=N, guarded by N==1, no intervening write
 // on the decoder branch; encoder mutation jumps over .L141.
 assert.match(original,/bnei\ta12, 1, \.L136/);assert.match(original,/\.L141:\n\tmov.n\ta3, a12/);
 const r=verify('bands-tell-bits1-asm');assert.equal(r.files.length,110);
 assert.equal(r.files.filter(f=>f.includes('bands-tell-bits1')).length,1);
 assert.doesNotMatch(macro,/\b(?:l8ui|l16ui|l16si|s8i|s16i|rsil|l32r|ssr|ssl)\b/);
});
const code=macro.split('\n').map(l=>l.split('#')[0].trim()).filter(l=>l&&!/^\.(?:macro|endm)\b/.test(l)).map(l=>l.replaceAll(',',' ').split(/\s+/));
const labels=new Map(code.flatMap(([op],i)=>op.endsWith(':')?[[op.slice(0,-1),i]]:[]));
function simulate(ctx){
 const r=Uint32Array.from({length:16},(_,i)=>0xc0000100+i);r[2]=0x1000;r[3]=1;
 const before=r.slice(),w=ctx.slice();let cold=false,steps=0;
 const v=a=>r[Number(a.slice(1))],set=(a,n)=>r[Number(a.slice(1))]=n;
 const offset=(a,n)=>{const p=v(a)+Number(n)-0x1000;assert.ok(p>=0&&p<48&&!(p&3));return p/4;};
 for(let pc=0;pc<code.length;pc++){
  assert.ok(++steps<24);const [opcode,a,b,c,d]=code[pc],op=opcode.replace(/\.n$/,'');
  switch(op){
   case 'l32i':set(a,w[offset(b,c)]);break;
   case 's32i':w[offset(b,c)]=v(a);break;
   case 'addi':set(a,v(b)+Number(c));break;
   case 'srli':set(a,v(b)>>>Number(c));break;
   case 'extui':set(a,(v(b)>>>Number(c))&((1<<Number(d))-1));break;
   case 'beqz':if(v(a)===0)pc=labels.get(b);break;
   case 'j':pc=labels.get(a);break;
   case 'call0':assert.equal(a,'ec_dec_bits');cold=true;assert.deepEqual(w,ctx);assert.deepEqual(r.slice(2,4),before.slice(2,4));break;
   default:assert.ok(op.endsWith(':'),'Unknown instruction '+op);
  }
 }
 assert.equal(cold,ctx[4]===0);const expected=ctx.slice();
 if(!cold){expected[3]=ctx[3]>>>1;expected[4]=(ctx[4]-1)>>>0;expected[5]=(ctx[5]+1)>>>0;assert.equal(r[2],ctx[3]&1);}
 assert.deepEqual(w,expected);
 for(const i of [0,1,3,8,9,10,11,12,13,14,15])assert.equal(r[i],before[i],'preserved a'+i);
}
test('100000 interpreted macro executions: bit, counters, cold state and preserved registers',()=>{
 let seed=0x31415926;const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<100000;i++){const ctx=Uint32Array.from({length:12},rnd);ctx[4]=i%33;simulate(ctx);}
 for(const available of [0,1,31,32,0xffffffff])for(const window of [0,1,0x80000000,0xffffffff]){
  const ctx=new Uint32Array(12);ctx[3]=window;ctx[4]=available;ctx[5]=0xffffffff;simulate(ctx);
 }
});
