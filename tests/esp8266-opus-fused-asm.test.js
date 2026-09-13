const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {component,root}=require('../tools/esp8266_opus_asm/export.cjs');
const {transform}=require('../tools/esp8266_opus_asm/fused.cjs');
const {instructions}=require('../tools/esp8266_opus_asm/hoist.cjs');
const original=fs.readFileSync(path.join(component,'asm/lx106/gcc/upstream/celt/vq.c.s'),'utf8').replace(/\r\n/g,'\n');
const changed=transform(original),fn=s=>s.match(/^alg_unquant:[\s\S]*?(?=^\s*\.size\s+alg_unquant,)/m)[0];
const before=fn(original),after=fn(changed);
const snippet=fs.readFileSync(path.join(root,'tools/esp8266_opus_asm/fused_normalize.inc.s'),'utf8');
const originalLoop=before.slice(before.indexOf('.L146:'),before.indexOf('\tblt\ta3, a8, .L146')+'\tblt\ta3, a8, .L146'.length);
const code=instructions(snippet+'\n'+originalLoop+'\n.Lasm_fused_after_normalize:');
// Interpret the actual ASM instructions; this is NOT a cycle predictor.
function execute(initial,memory){
 const labels=new Map(code.map((s,i)=>[s,i])),r=new Uint32Array(initial),mem=Buffer.from(memory);
 let sar=0,steps=0,reads=0;
 for(let pc=0;pc<code.length;pc++){
  assert.ok(++steps<50000);const line=code[pc];if(line.endsWith(':'))continue;
  const [opcode,...tail]=line.split(/\s+/),op=opcode.replace(/\.n$/,''),a=tail.join('').split(',');
  const idx=s=>s==='sp'?1:Number(s.slice(1)),v=s=>r[idx(s)],set=(s,n)=>r[idx(s)]=n;
  const jump=label=>{assert.ok(labels.has(label+':'),label);pc=labels.get(label+':');};
  const addr=w=>{const p=v(a[1])+Number(a[2]);assert.ok(p>=0&&p+w<=mem.length&&p%w===0);return p;};
  switch(op){
   case 'mov':set(a[0],v(a[1]));break;
   case 'movi':set(a[0],Number(a[1]));break;
   case 'addi':set(a[0],v(a[1])+Number(a[2]));break;
   case 'add':set(a[0],v(a[1])+v(a[2]));break;
   case 'sub':set(a[0],v(a[1])-v(a[2]));break;
   case 'and':set(a[0],v(a[1])&v(a[2]));break;
   case 'or':set(a[0],v(a[1])|v(a[2]));break;
   case 'nsau':set(a[0],Math.clz32(v(a[1])));break;
   case 'ssr':sar=v(a[0])&31;break;
   case 'srl':set(a[0],v(a[1])>>>sar);break;
   case 'sra':set(a[0],(v(a[1])|0)>>sar);break;
   case 'slli':set(a[0],v(a[1])<<Number(a[2]));break;
   case 'mul16s':set(a[0],Math.imul((v(a[1])<<16)>>16,(v(a[2])<<16)>>16));break;
   case 'movnez':if(v(a[2]))set(a[0],v(a[1]));break;
   case 'l32i':{const p=addr(4);if(p<4096)reads++;set(a[0],mem.readUInt32LE(p));break;}
   case 's32i':mem.writeUInt32LE(v(a[0]),addr(4));break;
   case 's16i':mem.writeUInt16LE(v(a[0])&65535,addr(2));break;
   case 'blti':if((v(a[0])|0)<Number(a[1]))jump(a[2]);break;
   case 'bgei':if((v(a[0])|0)>=Number(a[1]))jump(a[2]);break;
   case 'blt':if((v(a[0])|0)<(v(a[1])|0))jump(a[2]);break;
   case 'bnez':if(v(a[0]))jump(a[1]);break;
   case 'j':jump(a[0]);break;
   default:throw Error('Unmodelled instruction '+line);
  }
 }
 return {r,mem,reads};
}
test('10000 exact ASM loops: raw iy, PCM, mask, live registers, guards and word loads',()=>{
 let seed=0x541ada;const random=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 const lengths=[2,3,4,6,8,12,16,24,32,44,64,88,128,176,240,480,960],blocks=[1,2,3,4,6,8,12];
 let fused=0,fallback=0,zero=0;
 for(let trial=0;trial<10000;trial++){
  const N=lengths[trial%lengths.length],B=blocks[(trial/lengths.length|0)%blocks.length];if(B>N)continue;
  const r=Uint32Array.from({length:16},random),mem=Buffer.alloc(8192,0x65),gain=trial%9===0?0:random()&65535,shift=trial%31+1;
  r[1]=7168;r[3]=0;r[4]=0;r[5]=4096;r[6]=shift;r[7]=4096;r[8]=N;r[9]=B;r[10]=gain;r[11]=2**(shift-1);r[12]=4096;r[13]=0;
  mem.writeUInt32LE(B,r[1]+68);
  for(let i=0;i<N;i++)mem.writeUInt32LE(trial%5===0?(i===N-1?0xffff0000:0):random(),i*4);
  const expected=Buffer.from(mem),eligible=B>1&&B<=8&&!(B&(B-1))&&N%B===0;
  for(let i=0;i<N;i++){
   const iy=mem.readInt32LE(i*4),mul=Math.imul((iy<<16)>>16,(gain<<16)>>16);
   expected.writeUInt16LE(((mul+r[11]|0)>>shift)&65535,4096+2*i);
  }
  let mask=0;for(let b=0;b<B;b++){let bits=0;for(let j=0;j<(N/B|0);j++)bits|=mem.readInt32LE((b*(N/B|0)+j)*4);if(bits)mask|=1<<b;}
  expected.writeInt32LE(eligible?mask:-1,r[1]+72);
  const result=execute(r,mem);assert.deepEqual(result.mem,expected,'memory '+trial);
  assert.equal(result.reads,N,'one aligned iy read per coefficient');
  for(const k of [1,6,7,9,10,11,12,13,14])assert.equal(result.r[k],r[k],'live a'+k+' trial '+trial);
  assert.equal(result.r[4],N*4);assert.equal(result.r[5],4096+N*2);
  if(eligible){fused++;if(gain===0&&mask)zero++;}else fallback++;
 }
 assert.ok(fused>1000&&fallback>1000&&zero>0);
});
test('scope/hash/frame guards and original rotation/fallback stay unchanged',()=>{
 const verified=require('../tools/esp8266_opus_asm/verify.cjs').verify('bands-fused-asm');
 assert.equal(verified.files.length,110);assert.equal(verified.files.filter(p=>p.includes('bands-fused')).length,1);
 assert.equal(changed,fs.readFileSync(verified.files.find(p=>p.includes('bands-fused')),'utf8').replace(/\r\n/g,'\n'));
 assert.equal(original.replace(before,''),changed.replace(after,''));
 assert.equal(before.slice(before.indexOf('.L147:'),before.indexOf('.L179:')),after.slice(after.indexOf('.L147:'),after.indexOf('.L179:')));
 assert.equal(before.slice(before.indexOf('.L179:')),after.slice(after.indexOf('.L179:')));
 assert.throws(()=>transform(changed));assert.throws(()=>transform(original.replace('alg_unquant:','alg_unquant:\n s32i a3, sp, 72')));
 assert.doesNotMatch(snippet,/^\s*(call\w*|rsil|l8ui|l16si|l16ui)\s/gm);
 assert.equal((after.match(/addi\s+sp, sp, -112/g)||[]).length,1);
});
