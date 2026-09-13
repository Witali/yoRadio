const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {component}=require('../tools/esp8266_opus_asm/export.cjs');
const {specs,transform}=require('../tools/esp8266_opus_asm/blocks.cjs');
const {canonical}=require('../tools/esp8266_opus_asm/disassembly.cjs');
const {verify}=require('../tools/esp8266_opus_asm/verify.cjs');
test('only three reviewed block-count division sites change; arbitrary entropy division stays',()=>{
 for(const spec of specs){const s=fs.readFileSync(path.join(component,'asm/lx106/gcc',spec.source+'.s'),'utf8').replace(/\r\n/g,'\n'),v=transform(s,spec);
  assert.equal((v.match(/# ASM block division:/g)||[]).length,spec.calls);
  assert.equal((v.match(/call0\s+__udivsi3/g)||[]).length,(s.match(/call0\s+__udivsi3/g)||[]).length);
  assert.throws(()=>transform(v,spec));
 }assert.equal(verify('bands-blocks-asm').files.filter(f=>f.includes('bands-blocks')).length,2);
});
test('NSAU-based unsigned shift equals integer division, including uint32 high bit',()=>{
 let seed=73;
 for(let j=0;j<100000;j++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;const n=seed;
  for(let k=0;k<32;k++){const d=2**k;assert.equal(n>>>(31-Math.clz32(d)),Math.floor(n/d));}
  for(const d of [3,5,6,7,9,11,15,17,31,0xffffffff]){assert.notEqual((d&(d-1))>>>0,0);assert.equal(Math.floor(n/d),Math.trunc(n/d));}
 }
});
test('assembly equivalence check retains operands and branch graph, permits density encodings',()=>{
 const a=' 0: 000000 or a2, a3, a3\n 3: f00d ret.n\n';
 const b=' 0: 0000 mov.n a2, a3\n 2: f00d ret.n\n';
 assert.deepEqual(canonical(a),canonical(b));assert.notDeepEqual(canonical(a),canonical(b.replace('a3','a4')));
 assert.throws(()=>canonical(' 0: 0000 mov.n a2, a3\n 2: 00 .byte 00\n'));
});
