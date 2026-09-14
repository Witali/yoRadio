// Diagnostic-only ASM overlay: replace eight redundant stack loads by copies.
// Preserve instruction sizes, all linked addresses, arithmetic, ABI and RAM.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {root,hash,sourceHash,run}=require('./export.cjs');
const {sections,inspectImage}=require('./frozen_div.cjs');
const {inspect}=require('./report_layout.cjs');
const parent='esp8266-opus-folding-control-v1',variant=t=>'esp8266-opus-frozen-reloads-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t)),build=t=>path.join(root,'.build',variant(t));
const elfName='yoradio_esp8266_helix_native.elf';
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe';
const esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const names=['quant_partition','quant_band','quant_all_bands','opus_fft_impl'];
const specs=[
 {fn:'quant_partition',ops:['l32i a7, a1, 28','l32i a5, a1, 56','addi a3, a7, 1','slli a3, a3, 1','sub a2, a3, a2','l32i a3, a1, 28'],copy:'a3, a7'},
 {fn:'quant_band',ops:['l32i a10, a1, 56','l32i a11, a1, 56'],copy:'a11, a10'},
 {fn:'quant_all_bands',ops:['l32i a8, a1, 280','slli a10, a10, 1','add a2, a2, a11','l32i a9, a1, 280'],copy:'a9, a8'},
 {fn:'quant_all_bands',ops:['l32i a12, a1, 192','l32i a14, a1, 192'],copy:'a14, a12'},
 {fn:'opus_fft_impl',ops:['l32i a11, a1, 68','l32i a3, a1, 68'],copy:'a3, a11'},
 {fn:'opus_fft_impl',ops:['l32i a9, a1, 56','l32i a10, a1, 56'],copy:'a10, a9'},
 {fn:'opus_fft_impl',ops:['l32i a10, a1, 180','add a8, a8, a9','l32i a11, a1, 180'],copy:'a11, a10'},
 {fn:'opus_fft_impl',ops:['l32i a2, a1, 32','l32i a3, a1, 32'],copy:'a3, a2'}
];
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function save(p,b){if(typeof b==='string')b=Buffer.from(b);fs.mkdirSync(path.dirname(p),{recursive:true});if(fs.existsSync(p))assert.deepEqual(fs.readFileSync(p),b,'Existing evidence differs: '+p);else fs.writeFileSync(p,b);}
function normalized(s){return s.trim().replace(/\s+/g,' ').replace(/^([a-z0-9]+)\.n /,'$1 ').replace(/\b0x[0-9a-f]+\b/g,n=>String(parseInt(n,16)));}
function rows(text){return text.split('\n').map(l=>l.match(/^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*?)\s*$/)).filter(Boolean).map(m=>({address:parseInt(m[1],16),bytes:m[2].length/2,op:m[3],args:m[4],text:normalized(m[3]+' '+m[4])}));}
// Symbolic private-stack proof for every uint32 input register/stack value.
// Calls, stores, branch entries and unknown operations are deliberately refused.
function symbolic(ops){
 const r=Array.from({length:16},(_,i)=>'R'+i),reg=n=>{assert.match(n,/^a(?:[0-9]|1[0-5])$/);return Number(n.slice(1));};
 for(const text of ops){const m=normalized(text).match(/^(\w+) (.+)$/);assert.ok(m);const op=m[1],a=m[2].split(', '),d=reg(a[0]);assert.notEqual(d,1,'Stack pointer write');
  if(op==='l32i'){assert.equal(a[1],'a1');assert.match(a[2],/^\d+$/);assert.equal(Number(a[2])%4,0);r[d]='STACK['+a[2]+']';}
  else if(op==='mov'){assert.equal(a.length,2);r[d]=r[reg(a[1])];}
  else if(['add','sub'].includes(op)){r[d]=op+'('+r[reg(a[1])]+','+r[reg(a[2])]+')';}
  else if(['addi','slli'].includes(op)){assert.match(a[2],/^-?\d+$/);if(op==='slli')assert.ok(Number(a[2])>=0&&Number(a[2])<=31);r[d]=op+'('+r[reg(a[1])]+','+a[2]+')';}
  else throw Error('Unproved operation: '+text);
 }return r;
}
function findPatch(fn,spec){
 const rs=rows(fn.disassembly),hits=[];
 for(let i=0;i<=rs.length-spec.ops.length;i++)if(spec.ops.every((o,j)=>rs[i+j].text===o))hits.push(i);
 assert.equal(hits.length,1,'Expected unique sequence '+spec.fn+' '+spec.ops[0]);
 const group=rs.slice(hits[0],hits[0]+spec.ops.length),last=group.at(-1);
 group.slice(1).forEach((r,i)=>assert.equal(r.address,group[i].address+group[i].bytes,'Non-contiguous source'));
 const targets=rs.filter(r=>/^b|^j$/.test(r.op)).map(r=>r.args.match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]+>$/)).filter(Boolean).map(m=>parseInt(m[1],16));
 for(const r of group.slice(1))assert.ok(!targets.includes(r.address),'Branch bypasses source load');
 const after=[...spec.ops.slice(0,-1),'mov '+spec.copy];assert.deepEqual(symbolic(spec.ops),symbolic(after),'Changed live registers');
 const [d,s]=spec.copy.split(', '),instruction=last.bytes===2?'mov.n '+d+', '+s:'or '+d+', '+s+', '+s;
 return {...spec,address:last.address,bytes:last.bytes,before:last.text,instruction,after,sequence_start:group[0].address};
}
function offsetAt(b,address,length){const ss=sections(b).filter(s=>s.type===1&&(s.flags&6)===6&&address>=s.address&&address+length<=s.address+s.bytes);assert.equal(ss.length,1,'Allocated executable range');return ss[0].offset+address-ss[0].address;}
function patchElf(a,patches){const b=Buffer.from(a),used=new Set();for(const p of patches){const off=offsetAt(a,p.address,p.bytes);assert.equal(a.subarray(off,off+p.bytes).toString('hex'),p.before_hex);const value=Buffer.from(p.after_hex,'hex');assert.equal(value.length,p.bytes);for(let i=0;i<p.bytes;i++){assert.ok(!used.has(off+i));used.add(off+i);}value.copy(b,off);}for(let i=0;i<a.length;i++)if(!used.has(i))assert.equal(b[i],a[i],'Outside patch');return b;}
function compareApps(a,b,patches){const x=inspectImage(a),y=inspectImage(b);assert.equal(a.length,b.length);assert.equal(x.header,y.header);assert.deepEqual(x.segments.map(({sha256,...s})=>s),y.segments.map(({sha256,...s})=>s));const allowed=new Set();for(const p of patches){const ss=x.segments.filter(s=>p.address>=s.address&&p.address+p.bytes<=s.address+s.bytes);assert.equal(ss.length,1);const off=ss[0].offset+p.address-ss[0].address;assert.equal(a.subarray(off,off+p.bytes).toString('hex'),p.before_hex);assert.equal(b.subarray(off,off+p.bytes).toString('hex'),p.after_hex);for(let i=0;i<p.bytes;i++)allowed.add(off+i);}let changed=0;for(let i=0;i<a.length;i++)if(a[i]!==b[i]){assert.ok(allowed.has(i)||i>=x.checksumOffset,'Unrelated app byte changed '+i);changed++;}return {reference:x,candidate:y,changed_bytes_including_checksum:changed};}
function manifestPair(a,b){
 assert.equal(a.post_link_reload_variant,'control');assert.equal(b.post_link_reload_variant,'candidate');
 for(const k of new Set([...Object.keys(a),...Object.keys(b)]))if(!['purpose','app_sha256','post_link_reload_variant'].includes(k))assert.deepEqual(a[k],b[k],k);
 for(const m of [a,b]){assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.diagnostic,true);assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_division_benchmark,false);}
}
function generate(){
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const parentDir=path.join(root,'firmware/development',parent),m=read(path.join(parentDir,'manifest.json')),elf=path.join(root,'.build',parent,elfName),a=fs.readFileSync(elf),app=fs.readFileSync(path.join(parentDir,'app.bin'));
 assert.equal(hash(app),m.app_sha256.toLowerCase());assert.equal(app.length,m.bytes);const info=inspect(parent,names);assert.equal(hash(a),info.elf_sha256);
 const patches=specs.map(s=>findPatch(info.functions[s.fn],s));
 const source='# Generated frozen-layout Opus ASM reload experiment. Not production/default.\n# LX106 call0: same destination values, a1/a12..a15/SAR and all memory preserved.\n# Only private task stack reads are removed; no MMIO, shared or DMA memory.\n'+patches.map((p,i)=>'\n# '+p.fn+': '+p.before+' -> '+p.instruction+' at 0x'+p.address.toString(16)+'\n# Proven straight-line source: '+p.ops.join('; ')+'\n.section .text.patch'+i+',"ax",@progbits\n.begin no-transform\n'+p.instruction+'\n.end no-transform\n').join('');
 fs.mkdirSync(build('candidate'),{recursive:true});const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o');save(asm,source);run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);const object=fs.readFileSync(obj),ss=sections(object);
 patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.ok(s);assert.equal(s.bytes,p.bytes);p.after_hex=object.subarray(s.offset,s.offset+s.bytes).toString('hex');const off=offsetAt(a,p.address,p.bytes);p.before_hex=a.subarray(off,off+p.bytes).toString('hex');});
 const b=patchElf(a,patches);const images={},manifests={},logs={};
 for(const [t,bytes]of [['control',a],['candidate',b]]){
  const to=path.join(build(t),elfName);save(to,bytes);logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),to]);images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
  manifests[t]={...m,purpose:'Frozen-layout '+t+' private-stack reload ASM benchmark; not production',app_sha256:hash(images[t]),post_link_reload_variant:t,post_link_recipe_sha256_lf:sourceHash(__filename),post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(a)};
 }
 assert.deepEqual(images.control,app,'Unmodified ELF repack must reproduce original app');manifestPair(manifests.control,manifests.candidate);
 const actual=inspect(variant('candidate'),names);assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);
 for(const n of names){const ar=rows(info.functions[n].disassembly),br=rows(actual.functions[n].disassembly);assert.equal(ar.length,br.length);ar.forEach((r,i)=>{const p=patches.find(p=>p.address===r.address);assert.equal(br[i].address,r.address);assert.equal(br[i].bytes,r.bytes);assert.equal(br[i].text,p?normalized(p.instruction):r.text);});}
 const proof={schema:1,parent,scope:'Eight exact load-to-register-copy replacements. All other ELF bytes, addresses, instruction widths/counts and RAM unchanged. No timing claim.',recipe_sha256_lf:sourceHash(__filename),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),parent_manifest_sha256:hash(fs.readFileSync(path.join(parentDir,'manifest.json'))),patches,static_ram_delta:0,stack_delta:0,app_bytes:app.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,imageProof:compareApps(images.control,images.candidate,patches),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),header_mode:'dio',sdk_mode:'QIO40',logs}};
 for(const t of ['control','candidate']){save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(parentDir,'sdkconfig')));}
 save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.o'),object);save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');
 console.log(JSON.stringify({passed:true,patches:patches.length,app_bytes:app.length,ram_delta:0,sha256:manifests.candidate.app_sha256}));return proof;
}
module.exports={parent,variant,art,build,elfName,names,specs,normalized,rows,symbolic,findPatch,offsetAt,patchElf,compareApps,manifestPair,generate};if(require.main===module)generate();
