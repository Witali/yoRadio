// Exact small unsigned division for the LX106 entropy decoder.
// Candidate only: no production configuration changes here.
const assert=require('node:assert/strict');
// Same odd-divisor coefficients as upstream SMALL_DIV_TABLE. Generation is
// integer-only; the target needs 129 aligned uint32 words, no mutable RAM.
const table=Array.from({length:129},(_,i)=>{
 // Upstream declares 129 words but initializes 128: final word is zero.
 // d<=256 implies (d>>ctz(d))>>1 <=127, so this sentinel is never loaded.
 if(i===128)return 0;
 const v=(1n<<32n)/BigInt(2*i+1);return Number(v>0xffffffffn?0xffffffffn:v);
});
const helper=`
\t.section .text.yoradio_opus_small_udiv,"ax",@progbits
\t.literal_position
\t.literal .Ly_small_table, yoradio_opus_small_div_table
\t.literal .Ly_small_fallback, __udivsi3
\t.align 4
\t.global yoradio_opus_small_udiv
\t.type yoradio_opus_small_udiv,@function
# Exact unsigned n/d: a2=n, a3=d, result a2. LX106 call0 leaf.
# Clobbers a2..a11/SAR, preserves a0/a1/a12..a15, no stack or writable RAM.
# For d=0 or d>256, tail-call the original __udivsi3 with original a2/a3.
# d=2^t*odd; q=high32((n>>t)*floor(2^32/odd)), then exact remainder fix.
# odd=1 uses UINT32_MAX, hence the same correction. q never exceeds n/d.
# All products below are 16x16 unsigned except the final exact q*d.
# Mid sum <= 65535^2+65534+65535 = UINT32_MAX-1, so no carry is lost.
yoradio_opus_small_udiv:
\tmovi a4,256
\tbltu a4,a3,.Ly_small_slow
\tbeqz a3,.Ly_small_slow
\tbeqi a3,1,.Ly_small_ret
\tneg a4,a3
\tand a4,a4,a3
\tnsau a4,a4
\tmovi a5,31
\tsub a4,a5,a4
\tssr a4
\tsrl a5,a2
\tsrl a6,a3
\tsrli a6,a6,1
\tl32r a7,.Ly_small_table
\taddx4 a6,a6,a7
\tl32i a6,a6,0
\textui a7,a5,0,16
\tsrli a5,a5,16
\textui a8,a6,0,16
\tsrli a6,a6,16
\tmul16u a9,a7,a8
\tsrli a9,a9,16
\tmul16u a10,a5,a8
\tadd a9,a9,a10
\tmul16u a10,a7,a6
\textui a11,a10,0,16
\tadd a9,a9,a11
\tsrli a9,a9,16
\tsrli a10,a10,16
\tmul16u a5,a5,a6
\tadd a5,a5,a9
\tadd a5,a5,a10
\tmull a6,a5,a3
\tsub a6,a2,a6
\taddi a2,a5,1
\tbgeu a6,a3,.Ly_small_ret
\tmov a2,a5
.Ly_small_ret:
\tret.n
.Ly_small_slow:
\tl32r a4,.Ly_small_fallback
\tjx a4
\t.size yoradio_opus_small_udiv,.-yoradio_opus_small_udiv
\t.section .rodata.yoradio_opus_small_div_table,"a",@progbits
\t.balign 4
\t.type yoradio_opus_small_div_table,@object
yoradio_opus_small_div_table:
${table.map(v=>'\t.word 0x'+v.toString(16).padStart(8,'0')).join('\n')}
\t.size yoradio_opus_small_div_table,.-yoradio_opus_small_div_table
`;
function transform(original){
 let changes=0;
 const source=original.replace(/\r\n/g,'\n').replace(/^(ec_decode|ec_dec_uint):[\s\S]*?(?=^\s*\.size\s+\1,)/gm,body=>{
  let i=0;const name=body.startsWith('ec_decode:')?'ec_decode':'ec_dec_uint';
  const expected=name==='ec_decode'?2:4;
  const result=body.replace(/\bcall0\s+__udivsi3\b/g,call=>{
   const index=i++;if(index%2)return call;
   changes++;return 'call0\tyoradio_opus_small_udiv';
  });assert.equal(i,expected,name+' division sites');return result;
 });assert.equal(changes,3,'Only three rng/ft divisions may change');
 return source+'\n# Exact small-div overlay; original GCC snapshot remains unchanged.\n'+helper;
}
// Instruction-level executable model of the actual helper text above. Memory
// reads are aligned words only. Large/zero divisor fallback is reported, not
// modelled as a claim about libgcc's undefined divide-by-zero behaviour.
function compileModel(){
 const lines=helper.split('\n'),ops=[],labels=new Map();let active=false;
 for(const line of lines){const s=line.split('#')[0].trim();
  if(s==='yoradio_opus_small_udiv:')active=true;
  if(active&&s.startsWith('.size '))break;
  if(!active||!s)continue;
  if(s.endsWith(':'))labels.set(s.slice(0,-1),ops.length);
  else if(!s.startsWith('.')){const [op,...parts]=s.split(/\s+/);ops.push([op,...parts.join('').split(',')]);}
 }
 return function execute(n,d,initial){
  const r=initial?Uint32Array.from(initial):new Uint32Array(16);r[2]=n;r[3]=d;
  const reg=s=>+s.slice(1),value=s=>s.startsWith('a')?r[reg(s)]:Number(s);
  let pc=0,sar=0,count=0;
  while(count++<100){const [op,a,b,c,e]=ops[pc++],dst=reg(a);switch(op){
   case 'movi':r[dst]=Number(b);break;case 'mov':r[dst]=value(b);break;
   case 'neg':r[dst]=-value(b);break;case 'and':r[dst]=value(b)&value(c);break;
   case 'nsau':r[dst]=Math.clz32(value(b));break;
   case 'sub':r[dst]=value(b)-value(c);break;case 'add':case 'addi':r[dst]=value(b)+value(c);break;
   case 'ssr':sar=value(a)&31;break;case 'srl':r[dst]=value(b)>>>sar;break;
   case 'srli':r[dst]=value(b)>>>Number(c);break;
   case 'extui':assert.equal(c,'0');assert.equal(e,'16');r[dst]=value(b)&65535;break;
   case 'mul16u':r[dst]=(value(b)&65535)*(value(c)&65535);break;
   case 'mull':r[dst]=Math.imul(value(b),value(c));break;
   case 'addx4':r[dst]=value(b)*4+value(c);break;
   case 'l32r':r[dst]=b==='.Ly_small_table'?0x40200000:0x40001000;break;
   case 'l32i':{const address=value(b)+Number(c);assert.equal(address%4,0);const i=(address-0x40200000)/4;assert.ok(i>=0&&i<table.length);r[dst]=table[i];break;}
   case 'bltu':if(value(a)<value(b))pc=labels.get(c);break;
   case 'bgeu':if(value(a)>=value(b))pc=labels.get(c);break;
   case 'beqz':if(value(a)===0)pc=labels.get(b);break;
   case 'beqi':if(value(a)===Number(b))pc=labels.get(c);break;
   case 'ret.n':return {result:r[2],registers:r,count,fallback:false};
   case 'jx':assert.equal(value(a),0x40001000);return {registers:r,count,fallback:true};
   default:throw Error('Unsupported '+op);
  }}throw Error('Helper failed to terminate');
 };
}
function cModels(){
 const fs=require('node:fs'),path=require('node:path'),{root,component}=require('./export.cjs');
 const dir=path.join(root,'.build/opus-bands-small-div');fs.mkdirSync(dir,{recursive:true});
 const source='upstream/celt/entdec.c',text=fs.readFileSync(path.join(component,source),'utf8').replace(/\r\n/g,'\n');
 const needle='_this->ext=celt_udiv(_this->rng,_ft);';assert.equal(text.split(needle).length,2);
 const model=`
/* Semantic mirror of the ASM helper; host only, unsigned exact arithmetic. */
static const opus_uint32 y_small_table[129]={${table.map(v=>v+'U').join(',')}};
static opus_uint32 y_small_udiv(opus_uint32 n,opus_uint32 d){
 if(d>256||d==0)return n/d;
 if(d==1)return n;
 unsigned t=0;opus_uint32 odd=d;
 while(!(odd&1)){t++;odd>>=1;}
 opus_uint32 a=n>>t,b=y_small_table[odd>>1];
 opus_uint32 al=a&65535,ah=a>>16,bl=b&65535,bh=b>>16;
 opus_uint32 lh=al*bh,mid=(al*bl>>16)+ah*bl+(lh&65535);
 opus_uint32 q=ah*bh+(mid>>16)+(lh>>16);
 return q+(n-q*d>=d);
}
`;
 const file=path.join(dir,'entdec.model.c');
 fs.writeFileSync(file,text.replace('unsigned ec_decode(',model+'\nunsigned ec_decode(').replace(needle,'_this->ext=y_small_udiv(_this->rng,_ft);'));
 return [...require('./tell_inline.cjs').cModels(),{source,file}];
}
function generate(compiler){
 const fs=require('node:fs'),path=require('node:path');
 const {root,component,sourceHash,run}=require('./export.cjs');
 const {canonical}=require('./disassembly.cjs');
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const source='upstream/celt/entdec.c',base=path.join(component,'asm/lx106');
 const parentFile=path.join(base,'bands-tell-inline.json'),parent=JSON.parse(fs.readFileSync(parentFile));
 const manifest=JSON.parse(fs.readFileSync(path.join(base,'manifest.json'))),entry=manifest.files.find(f=>f.source===source);
 const original=path.join(base,entry.asm);assert.equal(sourceHash(original),entry.asm_sha256_lf);
 const dir=path.join(root,'.build/opus-bands-small-div');fs.mkdirSync(dir,{recursive:true});
 const overlay='bands-small-div/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.writeFileSync(dest,transform(fs.readFileSync(original,'utf8')));
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const a=path.join(dir,'control.o'),b=path.join(dir,'candidate.o');
 for(const [s,o]of [[original,a],[dest,b]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
 const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const sa=sizes(a),sb=sizes(b),checked=[];
 for(const s of Object.keys(sa).filter(s=>sa[s]&&s.startsWith('.text.'))){
  const ga=canonical(run(dump,['-dr','-j',s,a])),gb=canonical(run(dump,['-dr','-j',s,b]));
  // Literal offsets may differ when one previously shared __udivsi3 literal
  // splits into two distinct callees. Validate text instructions separately;
  // explicit relocations and linked callees are checked before flashing.
  const normalize=g=>g.map(v=>v.replace(/\.literal\.[^ ,]+(?:\+0x[0-9a-f]+)?/g,'LITERAL'));
  assert.deepEqual(normalize(gb),normalize(ga),s+' instructions/branches');checked.push(s);
 }
 assert.equal(sb['.rodata.yoradio_opus_small_div_table'],516);
 for(const prefix of ['.data','.bss'])for(const [s,n]of Object.entries(sb).filter(([s])=>s.startsWith(prefix)))assert.equal(n,sa[s]||0,s);
 const dis=run(dump,['-dr','-j','.text.yoradio_opus_small_udiv',b]);
 assert.equal((dis.match(/\bmul16u\b/g)||[]).length,4);assert.doesNotMatch(dis,/\b(?:muluh|mulsh|s32i|s16i|s8i|call0|callx0)\b/);
 for(const [name,o]of [['control',a],['candidate',b]])fs.writeFileSync(path.join(dir,name+'.disassembly.txt'),run(dump,['-dr',o]));
 const files=[...parent.files.map(e=>({source:e.source,overlay:e.overlay,overlay_sha256_lf:e.overlay_sha256_lf})),
  {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:sa,sections_after:sb}];
 const report={schema:1,candidate:'bands-small-div-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),
  recipe_sha256_lf:sourceHash(__filename),parent_sha256_lf:sourceHash(parentFile),files,
  changed_calls:3,table_bytes:516,additional_static_ram_bytes:0,stack_change_bytes:0,
  object_instruction_sections_checked:checked,linked_callees_verified:false,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-small-div.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));return report;
}
module.exports={table,helper,transform,compileModel,cModels,generate};
if(require.main===module)generate(process.argv[2]);
