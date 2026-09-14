const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {table,helper,transform,compileModel}=require('../tools/esp8266_opus_asm/small_div.cjs');
const {component}=require('../tools/esp8266_opus_asm/export.cjs');
test('coefficients exactly match the original Xiph odd-divisor table',()=>{
 const src=fs.readFileSync(path.join(component,'upstream/celt/entcode.c'),'utf8');
 const body=src.match(/SMALL_DIV_TABLE\[129\] = \{([\s\S]*?)\};/)[1];
 const initialized=[...body.matchAll(/0x[0-9a-f]+/gi)].map(m=>Number(m[0]));
 assert.equal(initialized.length,128);assert.deepEqual([...initialized,0],table);
});
test('helper CFG follows fallback branch over padding and rejects reachable garbage',()=>{
 const {helperDisassembly}=require('../tools/esp8266_opus_asm/small_div_link.cjs');
 const blocks={0:'0: 000000 beqz a3, 8 <helper+8>\n3: f00d ret.n\n5: be .byte 0xbe',8:'8: 000041 l32r a4, 0 <literal>\nb: 0004a0 jx a4'};
 const d=helperDisassembly(0,14,s=>blocks[s]);assert.doesNotMatch(d,/\.byte/);assert.match(d,/jx a4/);
 assert.throws(()=>helperDisassembly(0,14,s=>blocks[s].replace('jx a4','jx a5')));
 assert.throws(()=>helperDisassembly(0,14,s=>blocks[s].replace('f00d ret.n','be .byte 0xbe')));
});
test('LX106 exact small division: boundaries, quotient edges and ABI',()=>{
 const exec=compileModel();let seed=0x94251731,cases=0;
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
 }assert.ok(cases>1000000);
});
test('large/zero divisors retain original args and tail-call libgcc',()=>{
 const exec=compileModel();for(const d of [0,257,65535,0x80000000,0xffffffff])for(const n of [0,1,0x80000000,0xffffffff]){
  const r=exec(n,d);assert.equal(r.fallback,true);assert.equal(r.registers[2],n);assert.equal(r.registers[3],d);
 }
});
test('only rng/ft sites change; ext division and other functions stay intact',()=>{
 const original=fs.readFileSync(path.join(component,'asm/lx106/gcc/upstream/celt/entdec.c.s'),'utf8').replace(/\r\n/g,'\n');
 const changed=transform(original);assert.equal((changed.match(/call0\s+yoradio_opus_small_udiv/g)||[]).length,3);
 assert.equal(changed.split('\n# Exact small-div overlay;')[0].replaceAll('call0\tyoradio_opus_small_udiv','call0\t__udivsi3'),original);
 assert.equal(table.length*4,516);assert.doesNotMatch(helper,/^\s*(?:call0|s32i|s16i|s8i|l8ui|l16ui|l16si|muluh|mulsh)\b/m);
});
