const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component}=require('../tools/esp8266_opus_asm/export.cjs');
const {tables,cModels,transform}=require('../tools/esp8266_opus_asm/pulse_lookup.cjs');
const {execute,hostPath}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {verify}=require('../tools/esp8266_opus_asm/verify.cjs');
const {reference}=require('../tools/esp8266_opus_asm/pulse_inverse.cjs');
const source=fs.readFileSync(path.join(root,'tools/esp8266_opus_asm/pulse_lookup.inc.s'),'utf8');
// Execute the actual reviewed snippet's integer operations, not a second lookup.
// This tests register/pointer/shift semantics, NOT instruction latency or cache.
function simulate(pointer,bits,t) {
 const lines=source.split(/\r?\n/).map(x=>x.split('#')[0].trim()).filter(Boolean);
 const literals={'.Lasm_pulse_base':0x40200000,'.Lasm_pulse_map':0x40300000,'.Lasm_pulse_inverse':0x40400000};
 const r=Uint32Array.from({length:16},(_,i)=>0xa5000000+i),before=r.slice();r[2]=pointer;r[14]=bits;
 const idx=x=>Number(x.slice(1)),v=x=>r[idx(x)],set=(x,n)=>r[idx(x)]=n;
 let sar=0,exit;
 const jump=target=>{assert.ok(['.L60','.L61','.Lasm_pulse_fallback'].includes(target));exit=target;};
 for(const line of lines){
  if(exit)break;
  if(line.endsWith(':')){jump(line.slice(0,-1));break;}
  const [op,...args]=line.replaceAll(',',' ').split(/\s+/),[a,b,c,d]=args;
  switch(op){
   case 'l32r': assert.ok(Object.hasOwn(literals,b));set(a,literals[b]);break;
   case 'movi':set(a,Number(b));break;
   case 'mov':set(a,v(b));break;
   case 'sub':set(a,v(b)-v(c));break;
   case 'add':set(a,v(b)+v(c));break;
   case 'addx4':set(a,v(b)*4+v(c));break;
   case 'and':set(a,v(b)&v(c));break;
   case 'extui':set(a,(v(b)>>>Number(c))&((1<<Number(d))-1));break;
   case 'slli':set(a,v(b)<<Number(c));break;
   case 'ssr':sar=v(a)&31;break;
   case 'srl':set(a,v(b)>>>sar);break;
   case 'bgeu':if(v(a)>=v(b))jump(c);break;
   case 'bltu':if(v(a)<v(b))jump(c);break;
   case 'beq':if(v(a)===v(b))jump(c);break;
   case 'beqz':if(v(a)===0)jump(b);break;
   case 'j':jump(a);break;
   case 'l32i': {
    const address=(v(b)+Number(c))>>>0;assert.equal(address&3,0);
    const base=address>=literals['.Lasm_pulse_inverse']?literals['.Lasm_pulse_inverse']:literals['.Lasm_pulse_map'];
    const words=base===literals['.Lasm_pulse_inverse']?t.inverseWords:t.mapWords;
    const offset=(address-base)/4;assert.ok(offset>=0&&offset<words.length);set(a,words[offset]);break;
   }
   default:assert.fail('Unsupported instruction: '+op);
  }
 }
 for(const i of [0,1,3,5,6,7,11,12,13,15])assert.equal(r[i],before[i],'Preserve a'+i);
 assert.equal(r[2],pointer>>>0);assert.equal(r[14],bits>>>0);assert.ok(exit);
 if(exit==='.L60')assert.equal(r[10],r[4]);if(exit==='.L61')assert.equal(r[4],0);
 return {exit,q:r[4]};
}
test('actual ASM snippet has exact lookup/guards and preserves live registers',()=>{
 const t=tables();assert.equal(t.map.length+t.rows.flat().length,6372);
 for(const off of t.offsets)for(let b=0;b<=256;b++){
  const result=simulate(0x40200000+off,b,t),q=reference(t.bits.slice(off),b);
  assert.equal(result.exit,q?'.L60':'.L61');assert.equal(result.q,q);
 }
 for(const off of [-1,392,4096,...Array.from({length:392},(_,i)=>i).filter(i=>!t.offsets.includes(i))])
  assert.equal(simulate(0x40200000+off,64,t).exit,'.Lasm_pulse_fallback');
 for(const b of [-2147483648,-256,-1,257,16384,2147483647])assert.equal(simulate(0x40200000,b,t).exit,'.Lasm_pulse_fallback');
 assert.doesNotMatch(source,/^\s*(call\w*|s32i\S*|s16i\S*|s8i\S*|l8ui|l16[su]i)\s/gm);
});
test('C mirror matches original rate.h including custom pointer and budget fallback',()=>{
 cModels();const dir=path.join(root,'.build/opus-bands-pulse-lookup'),bin=path.join(dir,'guard-test');
 execute('gcc',['-O2','-fwrapv','-fsanitize=address,undefined','-fno-sanitize-recover=all',
  '-I'+hostPath(dir),...['upstream/celt','','upstream/include'].map(d=>'-I'+hostPath(path.join(component,d))),
  hostPath(path.join(root,'tests/native/esp8266_opus_pulse_lookup_test.c')),'-o',hostPath(bin)]);
 const result=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(bin)]));
 assert.equal(result.passed,true);assert.equal(result.combinations,382720);assert.equal(result.lookup_hits,5911);
});
test('ASM overlays are reproducible and baseline remains protected',()=>{
 const base=path.join(component,'asm/lx106'),m=JSON.parse(fs.readFileSync(path.join(base,'manifest.json')));
 for(const source of ['upstream/celt/bands.c','upstream/celt/modes.c']){
  const e=m.files.find(f=>f.source===source),original=fs.readFileSync(path.join(base,e.asm),'utf8');
  assert.equal(fs.readFileSync(path.join(base,'bands-pulse-lookup',source+'.s'),'utf8').replace(/\r\n/g,'\n'),transform(original,source));
 }
 assert.equal(verify('bands-pulse-lookup-asm').files.length,110);
});
