// Experimental saved-GCC ASM optimization, not production/default.
// Cache two immutable bitrev int16 entries in saved-return-address register a0.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {root,hash,sourceHash,run,component}=require('./export.cjs'),base=require('./frozen_reloads.cjs');
const {sections,inspectImage,wordOffset}=require('./frozen_div.cjs'),{inspect}=require('./report_layout.cjs');
const parent='esp8266-opus-mdct-half-candidate-v1',variant=t=>'esp8266-opus-mdct-bitrev-pair-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t)),build=t=>path.join(root,'.build',variant(t));
const names=['clt_mdct_backward_c','opus_custom_mode_create','celt_decoder_init'];
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe';
const esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function save(p,b){if(typeof b==='string')b=Buffer.from(b);fs.mkdirSync(path.dirname(p),{recursive:true});if(fs.existsSync(p))assert.deepEqual(fs.readFileSync(p),b,'Existing evidence differs: '+p);else fs.writeFileSync(p,b);}
function target(r){const m=r.args.match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]+>$/);assert.ok(m,'Unresolved branch');return parseInt(m[1],16);}
function findPatch(fn){const rs=base.rows(fn.disassembly),hits=rs.filter((r,i)=>r.text==='movi a5, -4'&&rs[i+1]?.text==='and a6, a12, a5');assert.equal(hits.length,1);
 const address=hits[0].address,bytes=24,before=rs.filter(r=>r.address>=address&&r.address<address+bytes);
 assert.deepEqual(before.map(r=>r.bytes),[2,3,2,2,3,3,3,3,3]);assert.deepEqual(before.map(r=>r.text).slice(0,4),['movi a5, -4','and a6, a12, a5','l32i a2, a6, 0','movi a7, 2']);
 assert.equal(before[4].op,'bbsi');assert.ok(before[4].args.startsWith('a12, 1, '));assert.equal(target(before[4]),address+21);
 assert.deepEqual(before.slice(5,7).map(r=>r.text),['slli a6, a2, 16','srai a6, a6, 16']);assert.equal(before[7].op,'j');assert.equal(target(before[7]),address+bytes);assert.equal(before[8].text,'srai a6, a2, 16');
 for(const r of rs.filter(r=>/^b|^j$/.test(r.op)))if(r.address<address||r.address>=address+bytes)assert.ok(target(r)<=address||target(r)>=address+bytes,'Interior branch entry');return {address,bytes,before};}
function validateActual(before,after,p){const a=base.rows(before),b=base.rows(after),inside=r=>r.address>=p.address&&r.address<p.address+p.bytes;assert.deepEqual(a.filter(r=>!inside(r)),b.filter(r=>!inside(r)));
 const rs=b.filter(inside);assert.deepEqual(rs.map(r=>r.address-p.address),[0,3,5,8,11,14,17]);assert.deepEqual(rs.map(r=>r.bytes),[3,2,3,3,3,3,3]);
 assert.equal(rs[0].op,'bbsi');assert.ok(rs[0].args.startsWith('a12, 1, '));assert.equal(target(rs[0]),p.address+14);
 assert.deepEqual(rs.slice(1,4).map(r=>r.text),['l32i a0, a12, 0','slli a6, a0, 16','srai a6, a6, 16']);assert.equal(rs[4].op,'j');assert.equal(rs[5].text,'srai a6, a0, 16');assert.equal(rs[6].op,'j');assert.equal(target(rs[4]),p.address+p.bytes);assert.equal(target(rs[6]),p.address+p.bytes);
 return rs;
}
function liveness(fn,p){const rs=base.rows(fn.disassembly),after=rs.filter(r=>r.address>=p.address+p.bytes);const live=new Set(['a2','a5','a7']),kills={};
 for(const r of after){if(!live.size)break;assert.ok(['l32i','l32i.n','srai','extui','mull'].includes(r.op),'Unexpected instruction before scratch kill');const args=r.args.split(/,\s*/);for(const a of args.slice(1))assert.ok(!live.has(a),'Scratch used before overwrite');if(live.delete(args[0]))kills[args[0]]=r.address;}
 assert.equal(live.size,0);assert.ok(rs.some(r=>r.text==='s32i a0, a1, 92'));assert.ok(rs.some(r=>r.text==='l32i a0, a1, 92'));
 const backs=rs.filter(r=>r.op==='j'&&r.address>p.address&&target(r)<p.address);assert.ok(backs.length);const back=backs[0],entry=target(back);
 const loop=rs.filter(r=>r.address>=entry&&r.address<=back.address);assert.ok(!loop.some(r=>/\ba0\b/.test(r.args)||/^call|^ret/.test(r.op)),'a0 must be unused throughout loop');
 const nextCall=rs.find(r=>r.address>back.address&&r.op==='call0');assert.ok(nextCall);assert.ok(nextCall.args.includes('<opus_fft_impl>'));
 const tail=rs.filter(r=>r.address>back.address&&r.address<nextCall.address);assert.ok(!tail.some(r=>/\ba0\b/.test(r.args)));
 const inc=loop.filter(r=>r.args.startsWith('a12,')&&!/^b/.test(r.op));assert.deepEqual(inc.map(r=>r.text),['addi a12, a12, 2']);
 assert.ok(!loop.some(r=>r.text==='s32i a0, a1, 92'));return {kills,loop_entry:entry,loop_back:back.address,return_slot:92,frame_bytes:96,next_call:nextCall.address,scope:'a2/a5/a7 dead before read; a0 unobserved by the loop and overwritten by CALL0, original return restored from sp+92'};
}
function tables(elfFile,info){const elf=fs.readFileSync(elfFile),symbols=Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',elfFile]).matchAll(/^([0-9a-f]+)\s+([0-9a-f]+)\s+\S\s+(.+)$/gm)].map(m=>[m[3],{address:parseInt(m[1],16),bytes:parseInt(m[2],16)}]));
 const mode=symbols.mode48000_960_120;assert.equal(mode.bytes,100);const word=a=>elf.readUInt32LE(wordOffset(elf,a));assert.equal(word(mode.address),48000);assert.equal(word(mode.address+56),1920);assert.equal(word(mode.address+60),3);
 assert.ok(info.functions.opus_custom_mode_create.graph.includes('l32r a2, literal:mode48000_960_120'));assert.ok(info.functions.celt_decoder_init.graph.includes('call0 opus_custom_mode_create'));
 const result=[];for(const [shift,n]of [480,240,120,60].entries()){const state=symbols['fft_state48000_960_'+shift],table=symbols['fft_bitrev'+n];assert.equal(state.bytes,60);assert.equal(word(mode.address+64+shift*4),state.address);assert.equal(word(state.address),n);assert.equal(word(state.address+48),table.address);assert.equal(table.address%4,0,'Initial bitrev must be word aligned');assert.equal(table.bytes,n*2);assert.equal(table.bytes%4,0);
  const sec=sections(elf).find(s=>s.type===1&&table.address>=s.address&&table.address+table.bytes<=s.address+s.bytes);assert.ok(sec);assert.ok(table.address>=0x40200000&&table.address<0x40300000,'Immutable flash table');
  const offset=sec.offset+table.address-sec.address,bytes=elf.subarray(offset,offset+table.bytes),values=[];for(let i=0;i<n;i++)values.push(bytes.readInt16LE(i*2));assert.equal(new Set(values).size,n);assert.ok(values.every(v=>v>=0&&v<n));
  result.push({shift,n,address:table.address,bytes:table.bytes,sha256:hash(bytes),old_loads:n,new_loads:n/2,values});}
 const modeSource=path.join(component,'upstream/celt/modes.c'),decoderSource=path.join(component,'upstream/celt/celt_decoder.c');const config=fs.readFileSync(path.join(component,'upstream/include/config.h'),'utf8');assert.doesNotMatch(config,/^\s*#define\s+CUSTOM_MODES(?:_ONLY)?\b/m);
 assert.match(fs.readFileSync(decoderSource,'utf8'),/opus_custom_decoder_init\(st, opus_custom_mode_create\(48000, 960, NULL\), channels\)/);
 return {mode,supported_standard_transforms:result,mode_source_sha256_lf:sourceHash(modeSource),decoder_source_sha256_lf:sourceHash(decoderSource),scope:'Pinned non-custom standard Opus mode; all packet/PLC durations and bitrates share four aligned immutable bitrev tables. No new runtime restriction.'};
}
const bits=n=>Array.from({length:32},(_,i)=>(n>>>i)&1),constant=v=>{assert.ok(v.every(b=>b===0||b===1),'Expected constant address/condition');return v.reduce((s,b,i)=>(s+(b?2**i:0))>>>0,0);};
function interpret(rs,end,registers,memory){const state=structuredClone(registers),map=new Map(rs.map(r=>[r.address,r]));let pc=rs[0].address,steps=0;const loads=[];
 while(pc!==end){assert.ok(++steps<=12,'Unexpected loop');const r=map.get(pc);assert.ok(r,'Invalid instruction boundary');const [d,s,n]=r.args.split(/,\s*/);pc+=r.bytes;
  switch(r.op.replace('.n','')){case 'movi':state[d]=bits(Number(s));break;
   case 'and':state[d]=state[s].map((v,i)=>state[n][i]===0||v===0?0:state[n][i]===1?v:v===1?state[n][i]:(assert.fail('Non-constant mask')));break;
   case 'l32i':{const a=(constant(state[s])+Number(n))>>>0;assert.equal(a%4,0);assert.ok(memory.has(a),'Outside table word');loads.push(a);state[d]=[...memory.get(a)];break;}
   case 'slli':assert.equal(Number(n),16);state[d]=Array.from({length:32},(_,i)=>i<16?0:state[s][i-16]);break;
   case 'srai':assert.equal(Number(n),16);state[d]=Array.from({length:32},(_,i)=>state[s][Math.min(31,i+16)]);break;
   case 'bbsi':assert.equal(s,'1');assert.ok([0,1].includes(state[d][1]));if(state[d][1])pc=target(r);break;
   case 'j':pc=target(r);break;default:throw Error('Unproved opcode '+r.op);
  }
 }return {state,steps,loads};
}
function prove(before,after,p){const select=s=>base.rows(s).filter(r=>r.address>=p.address&&r.address<p.address+p.bytes),old=select(before),now=select(after),end=p.address+p.bytes,word=Array.from({length:32},(_,i)=>'W'+i),address=0x402d0000;
 const original=Object.fromEntries(Array.from({length:16},(_,i)=>['a'+i,Array.from({length:32},(_,b)=>`R${i}.${b}`)]));let cached=original.a0;const phases=[];
 for(const half of [0,1]){const regs=structuredClone(original);regs.a12=bits(address+half*2);const candidate=structuredClone(regs);candidate.a0=cached;const memory=new Map([[address,word]]),a=interpret(old,end,regs,memory),b=interpret(now,end,candidate,memory);
  for(let i=0;i<16;i++)if(![0,2,5,7].includes(i))assert.deepEqual(a.state['a'+i],b.state['a'+i],'Changed live register');const expected=Array.from({length:32},(_,i)=>word[Math.min(half?31:15,i+(half?16:0))]);assert.deepEqual(b.state.a6,expected);assert.deepEqual(b.state.a0,word);cached=b.state.a0;
  assert.equal(a.loads.length,1);assert.equal(b.loads.length,half?0:1);assert.equal(a.steps,half?6:8);assert.equal(b.steps,half?3:5);phases.push({half,old_instructions:a.steps,new_instructions:b.steps,old_loads:a.loads.length,new_loads:b.loads.length});}
 return {phases,all_word_bits:true,sar:'unchanged',scope:'Induction over aligned immutable table: first low half loads a0; following high half reuses it; arbitrary signed16 values, no skipped arithmetic'};
}
function manifestPair(a,b){assert.equal(a.post_link_bitrev_pair_variant,'control');assert.equal(b.post_link_bitrev_pair_variant,'candidate');for(const k of new Set([...Object.keys(a),...Object.keys(b)]))if(!['purpose','app_sha256','post_link_bitrev_pair_variant'].includes(k))assert.deepEqual(a[k],b[k],k);
 for(const m of [a,b]){assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.post_link_mdct_variant,'candidate');assert.equal(m.diagnostic,true);assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_division_benchmark,false);}}
function generate(){const oldProof=require('./report_mdct_half.cjs').verifyPair();require('./verify.cjs').verify('bands-tell-inline-asm');const dir=path.join(root,'firmware/development',parent),m=read(path.join(dir,'manifest.json')),file=path.join(root,'.build',parent,base.elfName),a=fs.readFileSync(file),app=fs.readFileSync(path.join(dir,'app.bin'));
 assert.equal(hash(a),oldProof.proof.candidate_elf_sha256);assert.equal(hash(app),m.app_sha256);assert.equal(app.length,m.bytes);const info=inspect(parent,names),fn=info.functions[names[0]],p=findPatch(fn),live=liveness(fn,p),tableProof=tables(file,info);
 const source='# clt_mdct_backward_c bitrev pair cache, Xtensa LX106 call0.\n# Original return address is saved at sp+92 in the unchanged96-byte frame.\n# a0 unused until FFT CALL0: cache one immutable aligned32-bit word for two iterations.\n# a2/a5/a7 old temporary values dead before any read; all other registers and SAR exact.\n# Pinned standard mode tables start word aligned; a12 advances by2, first iteration loads low half.\n# No custom-mode behavior is silently changed: generator validates linked tables and parent.\n# No new RAM, stack or buffer, no scalar16-bit flash load. C fallback/snapshot unchanged.\n.section .text.patch0,"ax",@progbits\n.begin no-transform\nbbsi a12, 1, .Lhigh\nl32i.n a0, a12, 0\nslli a6, a0, 16\nsrai a6, a6, 16\nj .Lend\n.Lhigh:\nsrai a6, a0, 16\nj .Lend\n.space 4, 0\n.Lend:\n.end no-transform\n';
 fs.mkdirSync(build('candidate'),{recursive:true});const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o'),linked=path.join(build('candidate'),'patches.elf'),script=path.join(build('candidate'),'patches.ld');save(asm,source);save(script,`SECTIONS { .text.patch0 0x${p.address.toString(16)} : { *(.text.patch0) } }\n`);
 run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);run(path.join(bin,'xtensa-lx106-elf-ld.exe'),['-e','0','-T',script,'-o',linked,obj]);const object=fs.readFileSync(linked),sec=sections(object).find(s=>s.name==='.text.patch0');assert.equal(sec.address,p.address);assert.equal(sec.bytes,p.bytes);p.after_hex=object.subarray(sec.offset,sec.offset+sec.bytes).toString('hex');const off=base.offsetAt(a,p.address,p.bytes);p.before_hex=a.subarray(off,off+p.bytes).toString('hex');
 const b=base.patchElf(a,[p]),images={},manifests={},logs={};for(const [t,bytes]of [['control',a],['candidate',b]]){const to=path.join(build(t),base.elfName);save(to,bytes);logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),to]);images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
  manifests[t]={...m,purpose:'Frozen-layout '+t+' MDCT bitrev pair ASM benchmark; not production',app_sha256:hash(images[t]),post_link_bitrev_pair_variant:t,post_link_recipe_sha256_lf:sourceHash(__filename),post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(a)};}
 assert.deepEqual(images.control,app);manifestPair(manifests.control,manifests.candidate);const actual=inspect(variant('candidate'),names);assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);validateActual(fn.disassembly,actual.functions[names[0]].disassembly,p);const symbolicProof=prove(fn.disassembly,actual.functions[names[0]].disassembly,p);for(const name of names.slice(1))assert.deepEqual(actual.functions[name],info.functions[name]);assert.deepEqual(tables(path.join(build('candidate'),base.elfName),actual),tableProof);
 const proof={schema:1,parent,recipe_sha256_lf:sourceHash(__filename),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),patches:[p],liveness:live,tables:tableProof,symbolicProof,static_ram_delta:0,stack_delta:0,app_bytes:app.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,imageProof:base.compareApps(images.control,images.candidate,[p]),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),logs}};
 for(const t of ['control','candidate']){save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(dir,'sdkconfig')));}
 save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.elf'),object);save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify({passed:true,sha256:manifests.candidate.app_sha256,app_bytes:app.length,ram_delta:0,symbolicProof,transforms:tableProof.supported_standard_transforms.map(({values,...r})=>r)}));return proof;}
module.exports={parent,variant,art,build,names,findPatch,validateActual,liveness,tables,interpret,prove,manifestPair,generate};if(require.main===module)generate();
