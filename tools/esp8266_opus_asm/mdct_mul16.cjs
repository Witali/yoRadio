// Diagnostic-only saved-GCC ASM overlay: signed16 products, no precision loss.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {root,hash,sourceHash,run}=require('./export.cjs'),base=require('./frozen_reloads.cjs'),three=require('./mdct_three_pair.cjs');
const {sections,inspectImage}=require('./frozen_div.cjs'),{inspect}=require('./report_layout.cjs');
const parent=three.variant('candidate'),variant=t=>'esp8266-opus-mdct-mul16-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t)),build=t=>path.join(root,'.build',variant(t)),names=three.names,read=three.read;
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe',esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const expected=[0x402472a8,0x402472b6,0x402472c6,0x402472cc,0x402473d7,0x402473dd,0x402473e3,0x402473f7,0x4024745a,0x40247460,0x40247466,0x4024746c,0x402474ef,0x40247502,0x40247508,0x4024750e];
function save(p,b){if(typeof b==='string')b=Buffer.from(b);fs.mkdirSync(path.dirname(p),{recursive:true});if(fs.existsSync(p))assert.deepEqual(fs.readFileSync(p),b,'Existing evidence differs: '+p);else fs.writeFileSync(p,b);}
const reg=x=>{assert.match(x,/^a(?:[0-9]|1[0-5])$/);return Number(x.slice(1));};
// Width w means signed interval [-2^(w-1),2^(w-1)-1]. No assumptions about
// audio, bitrate, initial registers or memory: L32I always returns full32.
// Both branch successors are joined by MAX. Loops solved to a fixed point.
// Unknown instructions/targets fail, rather than silently preserving facts.
function widths(disassembly){const rs=base.rows(disassembly),index=new Map(rs.map((r,i)=>[r.address,i]));assert.ok(rs.length);assert.equal(index.size,rs.length);
 const states=new Map([[0,Array(16).fill(32)]]),queue=[0],queued=new Set([0]);let visits=0;
 while(queue.length){const i=queue.shift();queued.delete(i);assert.ok(++visits<rs.length*16*32+1);const r=rs[i],a=r.args.split(/,\s*/),op=r.op.replace('.n',''),s=[...states.get(i)];
  const value=x=>s[reg(x)],dest=()=>reg(a[0]),imm=(v,lo,hi)=>{assert.match(v,/^-?\d+$/);const n=Number(v);assert.ok(n>=lo&&n<=hi);return n;};
  if(op==='ret')continue;
  if(op==='call0'){assert.match(r.args,/^[0-9a-f]+ <opus_fft_impl>$/);for(let k=0;k<12;k++)if(k!==1)s[k]=32;}
  else if(op==='srai'){assert.equal(a.length,3);s[dest()]=Math.max(1,value(a[1])-imm(a[2],0,31));}
  else if(op==='slli'){assert.equal(a.length,3);s[dest()]=Math.min(32,value(a[1])+imm(a[2],0,31));}
  else if(op==='extui'){assert.equal(a.length,4);const shift=imm(a[2],0,31),count=imm(a[3],1,16);assert.ok(shift+count<=32);reg(a[1]);s[dest()]=count+1;}
  else if(op==='mov'){assert.equal(a.length,2);s[dest()]=value(a[1]);}
  else if(op==='or'&&a[1]===a[2])s[dest()]=value(a[1]);
  else if(['l32i','l32r','movi','mull','mul16s','and','or','add','addi','neg','sub'].includes(op))s[dest()]=32;
  else assert.ok(['s32i','bbsi','bnone','beq','bne','blti','bgei','bge','j'].includes(op),'Unproved opcode '+r.text);
  const branch=/^b|^j$/.test(op),next=branch?[index.get(three.target(r)),...(op==='j'?[]:[i+1])]:[i+1];
  for(const n of next){assert.ok(Number.isInteger(n)&&n>=0&&n<rs.length,'Nonlocal/invalid CFG successor');if(!branch)assert.equal(rs[n].address,r.address+r.bytes,'Unexplained fallthrough gap');
   const old=states.get(n),merged=old?s.map((v,k)=>Math.max(v,old[k])):s;assert.ok(merged.every(w=>Number.isInteger(w)&&w>=1&&w<=32));
   if(!old||merged.some((w,k)=>w!==old[k])){states.set(n,[...merged]);if(!queued.has(n)){queued.add(n);queue.push(n);}}
  }
 }assert.equal(states.size,rs.length,'Disassembly contains unreachable evidence');
 const products=rs.flatMap((r,i)=>{if(!['mull','mul16s'].includes(r.op))return[];const a=r.args.split(/,\s*/);assert.equal(a.length,3);const w=[states.get(i)[reg(a[1])],states.get(i)[reg(a[2])]];return [{address:r.address,instruction:r.text,widths:w,eligible:w.every(v=>v<=16)}];});
 return {visits,entry_widths:rs.map((r,i)=>({address:r.address,widths:states.get(i)})),products};}
function findPatches(fn){const analysis=widths(fn.disassembly),rs=base.rows(fn.disassembly),eligible=analysis.products.filter(p=>p.eligible);assert.deepEqual(eligible.map(p=>p.address),expected);
 const patches=eligible.map(p=>{const row=rs.find(r=>r.address===p.address);assert.equal(row.op,'mull');assert.equal(row.bytes,3);return {address:p.address,bytes:3,before:row.text,instruction:'mul16s '+row.args,widths:p.widths};});return {analysis,patches};}
function validateActual(before,after,patches){const a=base.rows(before),b=base.rows(after);assert.equal(a.length,b.length);a.forEach((r,i)=>{const p=patches.find(p=>p.address===r.address);assert.equal(b[i].address,r.address);assert.equal(b[i].bytes,r.bytes);assert.equal(b[i].text,p?p.instruction:r.text);});
 const x=widths(before),y=widths(after);assert.deepEqual(x.entry_widths,y.entry_widths);assert.deepEqual(x.products.map(({instruction,...v})=>v),y.products.map(({instruction,...v})=>v));
 for(const p of patches){const state=x.entry_widths.find(s=>s.address===p.address),a=base.rows(before).find(r=>r.address===p.address).args.split(/,\s*/);assert.ok(state.widths[reg(a[1])]<=16&&state.widths[reg(a[2])]<=16);}
 return y;}
function numericProof(){const values=[-32768,-32767,-16384,-1,0,1,16383,32766,32767];let cases=0;for(let x=-32768;x<=32767;x++)for(const y of values){const wide=Math.imul(x,y),narrow=Math.imul((x<<16)>>16,(y<<16)>>16);assert.equal(wide,narrow);assert.equal(BigInt(wide),BigInt(x)*BigInt(y));cases++;}
 return {cases,second_operand_edges:values,full_domain_argument:'For sign-extended16 a/b, int16(a)=a and int16(b)=b. Their product range[-1073709056,1073741824] fits int32. MULL low32 and MUL16S are therefore identical for every pair, not only tested edges.',sar:'unchanged',registers:'same destination; sources and all other registers unchanged'};}
function manifestPair(a,b){assert.equal(a.post_link_mul16_variant,'control');assert.equal(b.post_link_mul16_variant,'candidate');for(const k of new Set([...Object.keys(a),...Object.keys(b)]))if(!['purpose','app_sha256','post_link_mul16_variant'].includes(k))assert.deepEqual(a[k],b[k],k);
 for(const m of [a,b]){assert.equal(m.post_link_three_pair_variant,'candidate');assert.equal(m.post_link_mdct_variant,'candidate');assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.diagnostic,true);assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_division_benchmark,false);}}
function generate(){const prior=require('./report_mdct_three_pair.cjs').verifyPair(),dir=path.join(root,'firmware/development',parent),m=read(path.join(dir,'manifest.json')),file=path.join(root,'.build',parent,base.elfName),a=fs.readFileSync(file),app=fs.readFileSync(path.join(dir,'app.bin'));assert.equal(hash(a),prior.proof.candidate_elf_sha256);assert.equal(hash(app),m.app_sha256);
 const info=inspect(parent,names),{analysis,patches}=findPatches(info.functions[names[0]]),numeric=numericProof();
 const source='# clt_mdct_backward_c signed16 products, Xtensa LX106 call0.\n# Both operands sign-extended16 on every CFG path; product fits int32.\n# MULL -> MUL16S keeps all32 result bits, same3-byte width and destination.\n# No changed loads/stores/branches/SAR/ABI/frame, no new RAM or bitrate limit.\n# Unsigned low16 products intentionally remain MULL. C fallback unchanged.\n'+patches.map((p,i)=>'\n# 0x'+p.address.toString(16)+': '+p.before+'; operand signed widths '+p.widths.join(',')+'\n.section .text.patch'+i+',"ax",@progbits\n.begin no-transform\n'+p.instruction+'\n.end no-transform\n').join('');
 fs.mkdirSync(build('candidate'),{recursive:true});const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o');save(asm,source);run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);const object=fs.readFileSync(obj),ss=sections(object);patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.bytes,3);p.after_hex=object.subarray(s.offset,s.offset+s.bytes).toString('hex');const off=base.offsetAt(a,p.address,p.bytes);p.before_hex=a.subarray(off,off+p.bytes).toString('hex');});
 const b=base.patchElf(a,patches),images={},manifests={},logs={};for(const [t,bytes]of [['control',a],['candidate',b]]){const to=path.join(build(t),base.elfName);save(to,bytes);logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),to]);images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
  manifests[t]={...m,purpose:'Frozen-layout '+t+' MDCT signed16 multiply ASM benchmark; not production',app_sha256:hash(images[t]),post_link_mul16_variant:t,post_link_recipe_sha256_lf:sourceHash(__filename),post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(a)};}
 assert.deepEqual(images.control,app);manifestPair(manifests.control,manifests.candidate);const actual=inspect(variant('candidate'),names);assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);const actualAnalysis=validateActual(info.functions[names[0]].disassembly,actual.functions[names[0]].disassembly,patches);for(const n of names.slice(1))assert.deepEqual(actual.functions[n],info.functions[n]);
 const proof={schema:1,parent,recipe_sha256_lf:sourceHash(__filename),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),patches,analysis,actualAnalysis,numeric,static_ram_delta:0,stack_delta:0,app_bytes:app.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,imageProof:base.compareApps(images.control,images.candidate,patches),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),logs}};
 for(const t of ['control','candidate']){save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(dir,'sdkconfig')));}save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.o'),object);save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify({passed:true,sha256:manifests.candidate.app_sha256,bytes:app.length,ram_delta:0,patches:patches.length,range_proof:numeric}));return proof;}
module.exports={parent,variant,art,build,names,read,widths,findPatches,validateActual,numericProof,manifestPair,generate};if(require.main===module)generate();
