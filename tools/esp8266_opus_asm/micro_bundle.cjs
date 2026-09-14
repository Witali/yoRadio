// Three exact micro-optimizations on the accepted PVQ baseline; not production.
// Composition is checked against current linked instructions, not old offsets.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {root,hash,sourceHash,run}=require('./export.cjs');
const base=require('./frozen_reloads.cjs'),pvq=require('./pvq_row_loop.cjs');
const ec=require('./ec_bits.cjs'),entropy=require('./ec_bits_proof.cjs'),fft=require('./fft_load3.cjs'),mul=require('./mdct_mul16.cjs');
const {sections,inspectImage}=require('./frozen_div.cjs'),{inspect}=require('./report_layout.cjs');
const parent=pvq.variant('candidate'),variant=t=>'esp8266-opus-micro-bundle-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t)),build=t=>path.join(root,'.build',variant(t)),read=pvq.read;
const names=[...new Set(['ec_dec_bits','opus_fft_impl','clt_mdct_backward_c',...pvq.names])];
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe',esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const expectedMul=[0x402472a8,0x402472b6,0x402472c6,0x402472cc,0x402473e4,0x402473f2,0x40247402,0x40247408,0x4024744f,0x4024745d,0x4024746d,0x40247473,0x402474ef,0x40247502,0x40247508,0x4024750e];
const dependencies=['ec_bits.cjs','ec_bits_proof.cjs','ec_bits.s','fft_load3.cjs','fft_load3.s','mdct_mul16.cjs'];
const depHashes=()=>Object.fromEntries(dependencies.map(n=>[n,sourceHash(path.join(__dirname,n))]));
function save(file,b){if(typeof b==='string')b=Buffer.from(b);fs.mkdirSync(path.dirname(file),{recursive:true});if(fs.existsSync(file))assert.deepEqual(fs.readFileSync(file),b,'Existing evidence differs: '+file);else fs.writeFileSync(file,b);}
function disjoint(patches){
 const ordered=[...patches].sort((a,b)=>a.address-b.address);
 for(let i=0;i<ordered.length;i++){
  const p=ordered[i];assert.ok(Number.isInteger(p.address)&&Number.isInteger(p.bytes)&&p.bytes>0);
  if(i)assert.ok(ordered[i-1].address+ordered[i-1].bytes<=p.address,'Overlapping patches');
 }
}
function findPatches(functions){
 const analysis=mul.widths(functions.clt_mdct_backward_c.disassembly);
 const eligible=analysis.products.filter(p=>p.eligible);
 assert.deepEqual(eligible.map(p=>p.address),expectedMul,'Re-audit MDCT layout');
 const rows=base.rows(functions.clt_mdct_backward_c.disassembly);
 const products=eligible.map(p=>{const r=rows.find(r=>r.address===p.address);assert.equal(r.op,'mull');assert.equal(r.bytes,3);
  return{address:r.address,bytes:3,before:r.text,instruction:'mul16s '+r.args,widths:p.widths};});
 const patches=[ec.findPatch(functions.ec_dec_bits),fft.findPatch(functions.opus_fft_impl),...products];
 disjoint(patches);return patches;
}
function sourceFor(patches){
 const text=n=>fs.readFileSync(path.join(__dirname,n),'utf8').replace(/\r\n/g,'\n');
 return '# Combined exact LX106 call0 micro-optimizations; C fallback unchanged.\n'+
 text('ec_bits.s')+'\n'+text('fft_load3.s').replaceAll('.text.patch0','.text.patch1')+
 '\n# clt_mdct_backward_c: both operands sign-extended16 on every CFG path.\n'+
 '# MULL -> MUL16S: same exact int32 product, destination, 3-byte width and SAR.\n'+
 '# No extra register, call, spill, buffer or stack. Unsigned low16 stays MULL.\n'+
 patches.slice(2).map((p,i)=>'\n# 0x'+p.address.toString(16)+': '+p.before+'; signed widths '+p.widths.join(',')+
 '\n.section .text.patch'+(i+2)+',"ax",@progbits\n.begin no-transform\n '+p.instruction+'\n.end no-transform\n').join('');
}
function prove(functions,actual,patches){
 assert.deepEqual(patches.map(({before_hex,after_hex,...p})=>p),findPatches(functions));
 const entropyProof=entropy.prove(functions.ec_dec_bits,actual.ec_dec_bits);
 const p=patches[1],a=base.rows(functions.opus_fft_impl.disassembly),b=base.rows(actual.opus_fft_impl.disassembly);
 const inside=rs=>rs.filter(r=>r.address>=p.address&&r.address<p.address+p.bytes);
 const outside=rs=>rs.filter(r=>r.address<p.address||r.address>=p.address+p.bytes);
 assert.deepEqual(outside(a),outside(b));assert.deepEqual(inside(b).map(r=>r.bytes),[3,2,3]);
 assert.deepEqual(inside(b).map(r=>r.text),fft.replacement);
 const fftProof=fft.prove(inside(a).map(r=>r.text),inside(b).map(r=>r.text));
 const widths=mul.validateActual(functions.clt_mdct_backward_c.disassembly,actual.clt_mdct_backward_c.disassembly,patches.slice(2));
 for(const n of names.slice(3))assert.deepEqual(actual[n],functions[n]);
 return{entropy:entropyProof,fft:fftProof,mul_widths:widths,numeric:mul.numericProof(),components:3,patch_count:18};
}
function manifestPair(a,b){
 assert.equal(a.post_link_micro_bundle_variant,'control');assert.equal(b.post_link_micro_bundle_variant,'candidate');
 for(const k of new Set([...Object.keys(a),...Object.keys(b)]))if(!['purpose','app_sha256','post_link_micro_bundle_variant'].includes(k))assert.deepEqual(a[k],b[k],k);
 for(const m of[a,b]){
  assert.equal(m.post_link_pvq_row_loop_variant,'candidate');assert.equal(m.post_link_post_pair_variant,'candidate');
  assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(m.diagnostic,true);assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');
  assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);
  assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_division_benchmark,false);
 }
}
function generate(){
 const prior=require('./report_pvq_row_loop.cjs').verifyPair(),dir=pvq.art('candidate'),m=read(path.join(dir,'manifest.json'));
 const a=fs.readFileSync(path.join(root,'.build',parent,base.elfName)),app=fs.readFileSync(path.join(dir,'app.bin'));
 assert.equal(hash(a),prior.proof.candidate_elf_sha256);assert.equal(hash(app),m.app_sha256);
 const info=inspect(parent,names),patches=findPatches(info.functions),source=sourceFor(patches);
 const asm=path.join(build('candidate'),'patches.s'),obj=path.join(build('candidate'),'patches.o'),linked=path.join(build('candidate'),'patches.elf'),script=path.join(build('candidate'),'patches.ld');
 save(asm,source);save(script,'SECTIONS {\n'+patches.map((p,i)=>' .text.patch'+i+' 0x'+p.address.toString(16)+' : { *(.text.patch'+i+') }\n').join('')+'}\n');
 run(path.join(bin,'xtensa-lx106-elf-as.exe'),[asm,'-o',obj]);run(path.join(bin,'xtensa-lx106-elf-ld.exe'),['-e','0','-T',script,'-o',linked,obj]);
 const object=fs.readFileSync(linked),ss=sections(object);
 patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,p.address);assert.equal(s.bytes,p.bytes);
  p.after_hex=object.subarray(s.offset,s.offset+s.bytes).toString('hex');const off=base.offsetAt(a,p.address,p.bytes);p.before_hex=a.subarray(off,off+p.bytes).toString('hex');});
 const b=base.patchElf(a,patches),images={},manifests={},logs={};
 for(const[t,elf]of[['control',a],['candidate',b]]){
  const file=path.join(build(t),base.elfName);save(file,elf);
  logs[t]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',path.join(build(t),'app.bin'),file]);
  images[t]=fs.readFileSync(path.join(build(t),'app.bin'));inspectImage(images[t]);assert.ok(images[t].length<=0xf0000);
  manifests[t]={...m,purpose:'Frozen-layout '+t+' three-component ASM micro-bundle raw benchmark; not production',app_sha256:hash(images[t]),post_link_micro_bundle_variant:t,post_link_recipe_sha256_lf:sourceHash(__filename),post_link_bundle_dependencies:depHashes(),post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(a)};
 }
 assert.deepEqual(images.control,app);manifestPair(manifests.control,manifests.candidate);
 const actual=inspect(variant('candidate'),names);assert.deepEqual(actual.sections,info.sections);assert.deepEqual(actual.function_sizes,info.function_sizes);
 const semantic=prove(info.functions,actual.functions,patches);
 const proof={schema:1,parent,recipe_sha256_lf:sourceHash(__filename),dependencies:depHashes(),parent_elf_sha256:hash(a),candidate_elf_sha256:hash(b),patches,semantic,static_ram_delta:0,stack_delta:0,app_bytes:app.length,sections:actual.sections,functions:info.functions,actual_functions:actual.functions,imageProof:base.compareApps(images.control,images.candidate,patches),packaging:{esptool_sha256:hash(fs.readFileSync(esptool)),logs}};
 for(const t of['control','candidate']){save(path.join(art(t),'app.bin'),images[t]);save(path.join(art(t),'manifest.json'),JSON.stringify(manifests[t],null,2)+'\n');save(path.join(art(t),'sdkconfig'),fs.readFileSync(path.join(dir,'sdkconfig')));}
 save(path.join(art('candidate'),'parent.elf.gz'),zlib.gzipSync(a,{level:9}));save(path.join(art('candidate'),'patches.s'),source);save(path.join(art('candidate'),'patches.elf'),object);save(path.join(art('candidate'),'preflight.json'),JSON.stringify(proof,null,2)+'\n');
 console.log(JSON.stringify({passed:true,sha256:manifests.candidate.app_sha256,app_bytes:app.length,ram_delta:0,components:3,patches:patches.length}));return proof;
}
function verifyPair(){
 const dest=art('candidate'),proof=read(path.join(dest,'preflight.json'));
 assert.equal(proof.recipe_sha256_lf,sourceHash(__filename));assert.deepEqual(proof.dependencies,depHashes());
 const a=zlib.gunzipSync(fs.readFileSync(path.join(dest,'parent.elf.gz')));assert.equal(hash(a),proof.parent_elf_sha256);
 const b=base.patchElf(a,proof.patches);assert.equal(hash(b),proof.candidate_elf_sha256);
 assert.equal(fs.readFileSync(path.join(dest,'patches.s'),'utf8').replace(/\r\n/g,'\n'),sourceFor(proof.patches));
 const object=fs.readFileSync(path.join(dest,'patches.elf')),ss=sections(object);
 proof.patches.forEach((p,i)=>{const s=ss.find(s=>s.name==='.text.patch'+i);assert.equal(s.address,p.address);assert.equal(s.bytes,p.bytes);assert.equal(object.subarray(s.offset,s.offset+s.bytes).toString('hex'),p.after_hex);});
 assert.deepEqual(prove(proof.functions,proof.actual_functions,proof.patches),proof.semantic);
 const manifests={},apps={};for(const t of['control','candidate']){
  manifests[t]=read(path.join(art(t),'manifest.json'));apps[t]=fs.readFileSync(path.join(art(t),'app.bin'));
  assert.equal(hash(apps[t]),manifests[t].app_sha256);assert.equal(apps[t].length,manifests[t].bytes);
  assert.equal(manifests[t].post_link_recipe_sha256_lf,proof.recipe_sha256_lf);assert.deepEqual(manifests[t].post_link_bundle_dependencies,proof.dependencies);
 }
 manifestPair(manifests.control,manifests.candidate);assert.deepEqual(base.compareApps(apps.control,apps.candidate,proof.patches),proof.imageProof);
 assert.equal(hash(apps.control),require('./report_pvq_row_loop.cjs').verifyPair().manifests.candidate.app_sha256);
 return{proof,manifests};
}
// FFT removes only a duplicate read; signed16 products are algebraic identities.
// Host changes only the entropy expression. Linked proofs above cover all three;
// the host executable is not an LX106 timing or instruction-execution emulator.
const cModels=()=>ec.cModels();
module.exports={parent,variant,art,build,names,read,expectedMul,depHashes,disjoint,findPatches,sourceFor,prove,manifestPair,generate,verifyPair,cModels};
if(require.main===module)generate();

