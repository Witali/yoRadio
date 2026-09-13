const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {specs,transform,instructions}=require('../tools/esp8266_opus_asm/hoist.cjs');
const {component}=require('../tools/esp8266_opus_asm/export.cjs');
const baseline=fs.readFileSync(path.join(component,'asm/lx106/gcc/upstream/celt/vq.c.s'),'utf8');
// Execute the actual reviewed instruction snippets, not an independent DSP
// rewrite. This models register/memory semantics, NOT LX106 cycles or IRQs.
function execute(source,initial,memory){
 const code=instructions(source),labels=new Map(code.map((v,i)=>[v,i]));
 const r=new Uint32Array(initial),mem=Buffer.from(memory);let sar=17,steps=0;
 for(let pc=0;pc<code.length;pc++){
  if(++steps>20000)throw Error('Runaway model');const line=code[pc];if(line.endsWith(':'))continue;
  const [opcode,...tail]=line.split(/\s+/),op=opcode.replace(/\.n$/,''),a=tail.join('').split(',');
  const ri=i=>{assert.match(a[i],/^a(?:[0-9]|1[0-5])$/);return Number(a[i].slice(1));},v=i=>r[ri(i)];
  const addr=(width)=>{const p=v(1)+Number(a[2]);assert.ok(p>=0&&p+width<=mem.length&&!(p%(width)));return p;};
  switch(op){
   case 'l32i':r[ri(0)]=mem.readUInt32LE(addr(4));break;
   case 'l16ui':r[ri(0)]=mem.readUInt16LE(addr(2));break;
   case 'mul16s':r[ri(0)]=Math.imul((v(1)<<16)>>16,(v(2)<<16)>>16);break;
   case 'addi':r[ri(0)]=v(1)+Number(a[2]);break;
   case 'add':r[ri(0)]=v(1)+v(2);break;
   case 'ssr':sar=v(0)&63;assert.ok(sar<32);break;
   case 'sra':r[ri(0)]=(v(1)|0)>>sar;break;
   case 's16i':mem.writeUInt16LE(v(0)&65535,addr(2));break;
   case 'blt':case 'bne':if(op==='blt'?(v(0)|0)<(v(1)|0):v(0)!==v(1)){assert.ok(labels.has(a[2]+':'));pc=labels.get(a[2]+':');}break;
   default:throw Error('Unmodelled '+line);
  }
 }
 return {r,mem,sar};
}
test('hoisted SAR keeps every register, store and exact rounding for 10000 cases',()=>{
 let seed=0x715ac;const random=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(const spec of specs){
  const t=transform(baseline,spec);const lengths=[1,2,3,8,16,32,64,120,176,240,480,960];
  for(let trial=0;trial<5000;trial++){
   const r=Uint32Array.from({length:16},random),mem=Buffer.alloc(8192),n=lengths[trial%lengths.length],shift=trial%32;
   for(let i=0;i<mem.length;i+=4)mem.writeUInt32LE(random(),i);
   const gain=trial<4?[0,32767,32768,65535][trial]:random()&65535,bias=shift?2**(shift-1):0;
   if(spec.fn==='alg_unquant'){r[3]=0;r[4]=0;r[5]=4096;r[6]=shift;r[8]=n;r[10]=gain;r[11]=bias;}
   else{r[12]=4096;r[14]=4096+2*n;r[4]=gain;r[5]=shift;r[6]=bias;}
   const a=execute(t.after,r,mem),b=execute(t.before,r,mem),label=spec.fn+' case '+trial;
   assert.ok(a.mem.equals(b.mem),label+' PCM');assert.deepEqual(a.r,b.r,label+' registers');assert.equal(a.sar,b.sar,label+' SAR');
  }
 }
});
test('transform refuses calls, new shift writes, invariant mutation and external entries',()=>{
 const s=specs[0];
 for(const instruction of ['call0 helper','ssl a9','addi.n a6, a6, 1','sra a7, a7']){
  const changed=baseline.replace(s.label+':',s.label+':\n\t'+instruction);
  assert.throws(()=>transform(changed,s));
 }
 assert.throws(()=>transform(baseline.replace('alg_unquant:','alg_unquant:\n j '+s.label),s));
});
test('LF and CRLF comments preserve every non-SSR instruction',()=>{
 for(const spec of specs){
  const lf=transform(baseline.replace(/\r\n/g,'\n'),spec);
  const crlf=transform(baseline.replace(/\r\n/g,'\n').replace(/\n/g,'\r\n'),spec);
  assert.equal(crlf.after,lf.after);
  assert.deepEqual(instructions(lf.after).filter(l=>!/^ssr\s/.test(l)),instructions(lf.before).filter(l=>!/^ssr\s/.test(l)));
 }
});
test('all three snapshots keep hashes, comments and independent entropy implementation',()=>{
 const {verify}=require('../tools/esp8266_opus_asm/verify.cjs');
 const r=verify('hoisted-asm');assert.equal(r.files.length,110);
 assert.ok(r.files.some(f=>f.replaceAll('\\','/').endsWith('/gcc/upstream/celt/entdec.c.s')));
 for(const spec of specs)assert.ok(r.files.some(f=>fs.readFileSync(f,'utf8').includes('Hoisted invariant SAR setup for '+spec.fn)));
});
