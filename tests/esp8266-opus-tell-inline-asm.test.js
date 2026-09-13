const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component}=require('../tools/esp8266_opus_asm/export.cjs');
const {sources,transform}=require('../tools/esp8266_opus_asm/tell_inline.cjs');
const {verify}=require('../tools/esp8266_opus_asm/verify.cjs');
const base=path.join(component,'asm/lx106'),macro=fs.readFileSync(path.join(root,'tools/esp8266_opus_asm/tell_inline.inc.s'),'utf8').replace(/\r\n/g,'\n');
const original=fs.readFileSync(path.join(base,'gcc/upstream/celt/entcode.c.s'),'utf8').replace(/\r\n/g,'\n');
const asmLines=s=>s.split('\n').map(l=>l.split('#')[0].trim()).filter(l=>l&&!/^\.(?:macro|endm)\b/.test(l));
test('macro arithmetic is the exact GCC leaf body without return',()=>{
 const body=original.match(/^ec_tell_frac:\n([\s\S]*?)^\s*\.size\s+ec_tell_frac,/m)[1];
 const normalized=s=>asmLines(s).filter(l=>l!=='ret.n').map(l=>l.replace('.LC0','.Lasm_tell_table').replace(/\.L2\b/g,'.Lasm_tell_done\\@').replace(/\s+/g,' '));
 assert.deepEqual(normalized(macro),normalized(body));
 assert.doesNotMatch(macro,/^\s*(call\w*|s32i\S*|s16i\S*|s8i\S*|l8ui|l16[su]i|rsil)\s/gm);
});
test('only four pinned quant_partition calls are expanded and baseline stays exact',()=>{
 for(const source of sources){
  const text=fs.readFileSync(path.join(base,'gcc',source+'.s'),'utf8').replace(/\r\n/g,'\n');
  const changed=transform(text,source);
  assert.equal(changed,fs.readFileSync(path.join(base,'bands-tell-inline',source+'.s'),'utf8').replace(/\r\n/g,'\n'));
  assert.throws(()=>transform(changed,source));
  if(source===sources[0]){
   let reverted=changed.slice(macro.length+1).replace('\t.literal .Lasm_tell_table, y_opus_tell_correction\n','');
   assert.equal((reverted.match(/\tY_OPUS_TELL_FRAC\t/g)||[]).length,4);
   reverted=reverted.replace(/\tY_OPUS_TELL_FRAC\t# Exact inlining; original call0 ABI and state\./g,'\tcall0\tec_tell_frac\t\t#');
   assert.equal(reverted,text);
   const q=changed.match(/^quant_partition:[\s\S]*?(?=^\s*\.size\s+quant_partition,)/m)[0];
   assert.equal((q.match(/\tcall0\tec_tell_frac\t/g)||[]).length,2);
  }
 }
 const r=verify('bands-tell-inline-asm');assert.equal(r.files.length,110);
 assert.equal(r.files.filter(f=>f.includes('bands-tell-inline')).length,2);
});
const correction=[35733,38967,42495,46340,50535,55109,60097,65535];
const instructions=asmLines(macro).map(l=>l.replaceAll(',',' ').split(/\s+/));
const done=instructions.findIndex(t=>t[0]==='.Lasm_tell_done\\@:');
function simulate(rng,nbits){
 const r=Uint32Array.from({length:16},(_,i)=>0xc0000100+i),before=r.slice();r[2]=0x1000;
 const ix=x=>Number(x.slice(1)),v=x=>r[ix(x)],set=(x,n)=>r[ix(x)]=n;
 let sar=0;
 for(let pc=0;pc<instructions.length;pc++){
  const [opcode,a,b,c]=instructions[pc],op=opcode.replace(/\.n$/,'');
  switch(op){
   case 'l32i':{const address=v(b)+Number(c);assert.equal(address&3,0);
    if(address===0x101c)set(a,rng);else if(address===0x1014)set(a,nbits);
    else {assert.ok(address>=0x2000&&address<0x2020);set(a,correction[(address-0x2000)/4]);}break;}
   case 'movi':set(a,Number(b));break;
   case 'l32r':assert.equal(b,'.Lasm_tell_table');set(a,0x2000);break;
   case 'nsau':set(a,Math.clz32(v(b)));break;
   case 'sub':set(a,v(b)-v(c));break;
   case 'add':set(a,v(b)+v(c));break;
   case 'addi':set(a,v(b)+Number(c));break;
   case 'slli':set(a,v(b)<<Number(c));break;
   case 'ssr':sar=v(a)&31;break;
   case 'srl':set(a,v(b)>>>sar);break;
   case 'srli':set(a,v(b)>>>Number(c));break;
   case 'bltu':if(v(a)<v(b)){assert.equal(c,'.Lasm_tell_done\\@');pc=done;}break;
   case '.Lasm_tell_done\\@:':break;
   default:assert.fail('Unknown instruction '+op);
  }
 }
 for(const i of [0,1,7,8,9,10,11,12,13,14,15])assert.equal(r[i],before[i]);
 const l=32-Math.clz32(rng),normalized=rng>>> (l-16),b=(normalized>>>12)-8;
 assert.equal(r[2],(nbits*8-(l*8+b+Number(normalized>correction[b])))>>>0);
}
test('actual macro preserves results and live registers at every normalized threshold',()=>{
 let count=0;
 for(let r=32768;r<=65535;r++)for(const tail of [0,1]){
  const shift=r%17,rng=r*2**shift+(tail?2**shift-1:0);
  simulate(rng,33+r);count++;
 }
 for(let shift=0;shift<=16;shift++)for(const c of correction)for(const d of [-1,0,1]){
  const r=c+d;if(r<32768||r>65535)continue;
  for(const n of [0,33,2147483647,2147483648,4294967295])simulate(r*2**shift,n);
 }
 assert.equal(count,65536);
});
