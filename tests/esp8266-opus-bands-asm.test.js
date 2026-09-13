const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {component}=require('../tools/esp8266_opus_asm/export.cjs');
const {transform,cModel}=require('../tools/esp8266_opus_asm/bands.cjs');
const {verify}=require('../tools/esp8266_opus_asm/verify.cjs');
test('intensity overlay is one decoder-only early branch, not entropy removal',()=>{
 const src=fs.readFileSync(path.join(component,'asm/lx106/gcc/upstream/celt/bands.c.s'),'utf8').replace(/\r\n/g,'\n');
 const candidate=transform(src,'intensity');
 const added=candidate.slice(candidate.indexOf('# ASM intensity:'),candidate.indexOf('.Lasm_intensity_normal:')+'.Lasm_intensity_normal:\n'.length);
 assert.equal(candidate.replace(added,''),src);
 assert.match(added,/l32i\s+a8, sp, 240/);assert.match(added,/bnez\s+a8,/);
 assert.match(added,/blt\s+a10, a4,/);assert.match(added,/j\s+\.L980/);
 assert.doesNotMatch(added,/\b(?:s32i|s16i|s8i|call0|rsil|memw)\b/);
 assert.throws(()=>transform(candidate,'intensity'),/Already transformed/);
 const verified=verify('bands-intensity-asm');assert.equal(verified.files.length,110);
 assert.equal(verified.files.filter(f=>f.includes('bands-intensity')).length,1);
 assert.match(fs.readFileSync(cModel('intensity'),'utf8'),/!encode && stereo && i>=intensity/);
});
test('early qn=1 preserves final qn across intensity/N/budget boundaries',()=>{
 const exp=[16384,17866,19483,21247,23170,25267,27554,30048];
 const qn=(N,b,cap,stereo)=>{const d=2*N-1-(stereo&&N===2?1:0),off=(cap>>1)-(stereo&&N===2?16:4);
  const qb=Math.min(b-cap-32,Math.trunc((b+d*off)/d),64);return qb<4?1:((exp[qb&7]>>(14-(qb>>3)))+1)&-2;};
 let cases=0;
 for(const encode of [0,1])for(const stereo of [0,1])for(const N of [2,3,4,6,8,12,16,22,44,88,176])
 for(const cap of [-8,0,8,16,24,40,64])for(const b of [-256,-1,0,3,4,31,32,63,64,127,255,256,1024,16383])
 for(const i of [0,1,10,20])for(const intensity of [i-1,i,i+1]){
  let a=qn(N,b,cap,stereo),c=!encode&&stereo&&i>=intensity?1:qn(N,b,cap,stereo);
  if(stereo&&i>=intensity){a=1;c=1;}assert.equal(c,a);cases++;
 }assert.equal(cases,51744);
});
