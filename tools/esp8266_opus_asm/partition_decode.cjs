// Decoder-only specialization of the saved GCC quant_partition, not a C rebuild.
// The proof tracks just ctx and its immutable zero encode member. Unknown audio
// values stay unknown; both successors of every data-dependent branch survive.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const source='upstream/celt/bands.c',base=path.join(component,'asm/lx106');
const parentFile=path.join(base,'bands-tell-inline/upstream/celt/bands.c.s');
function parse(text){
 const start=text.indexOf('quant_partition:\n'),end=text.indexOf('\t.size\tquant_partition,',start);
 assert.ok(start>=0&&end>start);const body=text.slice(start,end),rows=body.split('\n'),labels={},ops=[];
 rows.forEach((line,row)=>{const clean=line.split('#')[0].trim();if(!clean)return;
  if(clean.endsWith(':')){assert.equal(labels[clean.slice(0,-1)],undefined);labels[clean.slice(0,-1)]=ops.length;return;}
  assert.ok(!clean.startsWith('.'),'Unexpected directive in function: '+clean);
  const [op,...tail]=clean.split(/\s+/);ops.push({op:op.replace(/\.n$/,''),args:tail.join(' ').split(/,\s*/),row,text:clean});
 });
 return {start,end,body,rows,labels,ops};
}
const reg=s=>s==='sp'?1:/^a(?:[0-9]|1[0-5])$/.test(s)?Number(s.slice(1)):-1;
const copy=s=>({r:s.r.slice(),mem:{...s.mem}});
function merge(old,value){
 if(!old)return copy(value);
 const out={r:old.r.map((v,i)=>v===value.r[i]?v:null),mem:{}};
 for(const [k,v]of Object.entries(old.mem))if(value.mem[k]===v)out.mem[k]=v;
 return out;
}
const destOnly=new Set('addi addmi add sub mull mul16s slli srai srli sll sra srl and or xor neg extui nsau l32r movi movltz movgez moveqz movnez'.split(' '));
const conditional=new Set('beqz bnez bltz bgez beqi bnei blti bgei blt bge bltu bgeu beq bne bany bnone ball bnall bbsi bbci'.split(' '));
function analyze(program,{encodeZero=true}={}){
 const {ops,labels}=program,states=Array(ops.length),queue=[0],queued=new Set([0]);
 states[0]={r:Array(16).fill(null),mem:{}};states[0].r[2]='ctx';
 let iterations=0;
 const target=o=>{const t=labels[o.args.at(-1)];assert.ok(Number.isInteger(t)&&t<ops.length,'Unresolved local branch '+o.text);return t;};
 const decision=(o,s)=>{
  if(!['beqz','bnez','bltz','bgez'].includes(o.op)||s.r[reg(o.args[0])]!=='encode0')return null;
  return o.op==='beqz'||o.op==='bgez';
 };
 const transfer=(o,input)=>{
  const s=copy(input),[a,b,c]=o.args,d=reg(a),br=reg(b),offset=Number(c);
  if(o.op==='mov'){assert.ok(d>=0&&br>=0);s.r[d]=s.r[br];}
  else if(/^l(8u|16u|16s|32)i$/.test(o.op)){
   assert.ok(d>=0&&br>=0&&Number.isInteger(offset));
   s.r[d]=o.op==='l32i'?(br===1?s.mem[offset]??null:s.r[br]==='ctx'&&offset===0&&encodeZero?'encode0':null):null;
  }else if(/^s(8|16|32)i$/.test(o.op)){
   assert.ok(d>=0&&br>=0&&Number.isInteger(offset));
   const width=Number(o.op.match(/\d+/)[0])/8;
   if(br===1){for(const key of Object.keys(s.mem))if(+key<offset+width&&+key+4>offset)delete s.mem[key];if(width===4&&s.r[d])s.mem[offset]=s.r[d];}
   // This frame never escapes: ordinary argument/output pointers cannot alias
   // its private slots on a valid call. ctx writes must not touch encode.
   else if(s.r[br]==='ctx')assert.ok(offset>=4,'Write to immutable encode member');
  }else if(o.op==='call0'){
   // call0 callees may write incoming by-value argument slots 0..15, but no
   // address into this private frame is formed or passed. Callee-saved regs
   // retain ctx; recursion receives the same ctx and cannot modify encode.
   for(let i=0;i<=11;i++)if(i!==1)s.r[i]=null;
   for(const key of Object.keys(s.mem))if(+key<16)delete s.mem[key];
  }else if(o.op==='Y_OPUS_TELL_FRAC'){
   for(let i=2;i<=6;i++)s.r[i]=null; // Pinned, exact macro: no stores.
  }else if(destOnly.has(o.op)){assert.ok(d>=0);s.r[d]=null;}
  else assert.ok(['ssr','ssl','j','ret'].includes(o.op)||conditional.has(o.op),'Unmodelled opcode '+o.op);
  return s;
 };
 // Fail closed if the private stack can escape or has unexpected adjustments.
 for(const [i,o]of ops.entries())if(o.args.some(a=>reg(a)===1)){
  if(/^([ls])(8u|16u|16s|8|16|32)i$/.test(o.op)){
   assert.equal(reg(o.args[1]),1,'Stack used as load/store value');
   assert.notEqual(reg(o.args[0]),1,'Stack pointer stored or overwritten');
  }
  else {assert.equal(o.op,'addi');assert.deepEqual(o.args.slice(0,2).map(reg),[1,1]);assert.ok((i===0&&+o.args[2]===-112)||(i===ops.length-2&&+o.args[2]===112));}
 }
 while(queue.length){assert.ok(++iterations<ops.length*30,'Non-converging analysis');const i=queue.shift();queued.delete(i);const o=ops[i],input=states[i],out=transfer(o,input);
  let next=[];
  if(o.op==='j')next=[target(o)];else if(o.op==='ret')next=[];
  else if(conditional.has(o.op)){const take=decision(o,input);if(take!==true)next.push(i+1);if(take!==false)next.push(target(o));}
  else next=[i+1];
  for(const j of next){assert.ok(j<ops.length);const merged=merge(states[j],out);if(JSON.stringify(states[j])!==JSON.stringify(merged)){states[j]=merged;if(!queued.has(j)){queue.push(j);queued.add(j);}}}
 }
 const branches=ops.flatMap((o,i)=>states[i]&&decision(o,states[i])!==null?[{index:i,row:o.row,original:o.text,taken:decision(o,states[i]),target:target(o)}]:[]);
 const dead=ops.flatMap((o,i)=>states[i]?[]:[{index:i,row:o.row,original:o.text}]);
 return {states,branches,dead,iterations};
}
function specialize(text){
 text=text.replace(/\r\n/g,'\n');const p=parse(text),a=analyze(p);assert.equal(a.branches.length,3);assert.ok(a.dead.length>100);
 const dead=new Set(a.dead.map(d=>d.index)),branches=new Map(a.branches.map(b=>[b.index,b]));
 const nextLive=i=>{while(i<p.ops.length&&dead.has(i))i++;return i;};
 const replacements=new Map();
 p.ops.forEach((o,i)=>{
  if(dead.has(i)){replacements.set(o.row,'# decoder-only: unreachable instruction removed');return;}
  const branch=branches.get(i);
  if(branch){const fall=nextLive(i+1);replacements.set(o.row,!branch.taken||branch.target===fall?'# decoder-only: encode=0 branch removed':'\tj\t'+o.args.at(-1)+'\t# decoder-only: encode=0, same successor');}
 });
 const body=p.rows.map((row,i)=>replacements.get(i)??row).join('\n');
 const note='# Decoder-only quant_partition: ctx.encode is immutable zero in this radio.\n# Only three proven encoder tests and unreachable instructions are removed.\n# Original 112-byte stack, registers, calls, arithmetic and widths retained.\n# Proof: tools/esp8266_opus_asm/partition_decode.cjs; C backend unchanged.\n';
 return {text:text.slice(0,p.start)+note+body+text.slice(p.end),proof:{branches:a.branches,removed_instructions:a.dead.length,iterations:a.iterations}};
}
function cModels(){
 const model=require('./tell_inline.cjs').cModels().find(m=>m.source===source);
 let text=fs.readFileSync(model.file,'utf8').replace(/\r\n/g,'\n');
 const begin=text.indexOf('static unsigned quant_partition('),body=text.indexOf('{',begin);
 assert.ok(begin>0&&body>begin);
 // Validate the invocation contract under ASan/UBSan. This host mirror does
 // not execute Xtensa; deletion equivalence is proved on the linked CFG.
 text=text.slice(0,body+1)+'\n   if (ctx->encode != 0) abort(); /* decoder-only invariant */\n'+text.slice(body+1);
 text='#include <stdlib.h>\n'+text;
 const dir=path.join(root,'.build/opus-bands-partition-decode');fs.mkdirSync(dir,{recursive:true});
 const file=path.join(dir,'bands.model.c');fs.writeFileSync(file,text);return [{source,file}];
}
function generate(compiler){
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const pf=path.join(base,'bands-tell-inline.json'),parent=JSON.parse(fs.readFileSync(pf));
 const entry=parent.files.find(f=>f.source===source);assert.equal(sourceHash(parentFile),entry.overlay_sha256_lf);
 const result=specialize(fs.readFileSync(parentFile,'utf8'));
 const overlay='bands-partition-decode/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,result.text);
 const dir=path.join(root,'.build/opus-bands-partition-decode');fs.mkdirSync(dir,{recursive:true});
 const object=path.join(dir,'candidate.o');run(compiler,['-mlongcalls','-x','assembler','-c',dest,'-o',object]);
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');fs.writeFileSync(path.join(dir,'candidate.disassembly.txt'),run(dump,['-dr',object]));
 const files=parent.files.map(f=>f.source===source?{source,overlay,overlay_sha256_lf:sourceHash(dest)}:f);
 const report={schema:1,candidate:'bands-partition-decode-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),parent_sha256_lf:sourceHash(pf),recipe_sha256_lf:sourceHash(__filename),files,proof:result.proof,additional_static_ram_bytes:0,stack_change_bytes:0,scope:'Only quant_partition; immutable decoder encode=0 precondition requires independent call-chain audit; physical speed not yet known'};
 fs.writeFileSync(path.join(base,'bands-partition-decode.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));return report;
}
module.exports={parse,analyze,specialize,parentFile,cModels,generate};
if(require.main===module)generate(process.argv[2]);
