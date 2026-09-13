// Exact loop fusion; base GCC snapshot and C fallback remain unchanged.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const {once}=require('./bands.cjs');
const {canonical}=require('./disassembly.cjs');
const kind='fused',source='upstream/celt/vq.c';
function transform(text){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/Lasm_fused/);
 const body=text.match(/^alg_unquant:[\s\S]*?(?=^\s*\.size\s+alg_unquant,)/m)?.[0];assert.ok(body);
 assert.doesNotMatch(body,/\bsp, 72\b/,'The mask slot must remain unused in pinned frame');
 assert.match(body,/addi\s+sp, sp, -112/);assert.match(body,/s32i\s+a0, sp, 108/);
 let changed=once(body,'.L146:\n',fs.readFileSync(path.join(__dirname,'fused_normalize.inc.s'),'utf8').replace(/\r\n/g,'\n')+'\n.L146:\n');
 changed=once(changed,'\tblt\ta3, a8, .L146\t# i, N,\n','\tblt\ta3, a8, .L146\t# i, N,\n.Lasm_fused_after_normalize:\n');
 changed=once(changed,'\tbgei\ta9, 2, .L179\t# B,,\n\tj\t.L150\t\t#',
  '\tblti\ta9, 2, .L150\t# B<=1 original mask=1.\n'+
  '\tl32i\ta2, sp, 72\t# Fused mask survives every rotation branch/call.\n'+
  '\tbltz\ta2, .L179\t# Original late pass for unsupported shapes.\n'+
  '\tmov\ta12, a2\n\tj\t.L150');
 return text.replace(body,changed);
}
function cModels(){
 const dir=path.join(root,'.build/opus-bands-fused');fs.mkdirSync(dir,{recursive:true});
 let text=fs.readFileSync(path.join(component,source),'utf8').replace(/\r\n/g,'\n');
 const test=fs.readFileSync(path.join(root,'tests/native/esp8266_opus_fused_normalize_test.c'),'utf8').replace(/\r\n/g,'\n');
 let helper=test.match(/^static unsigned fused\([\s\S]*?(?=^int main\()/m)[0];
 // ASM specializes only valid power-of-two block counts <=8; others untouched.
 helper=once(helper,'B <= 1 || N % B','B <= 1 || B > 8 || (B & (B-1)) || N < B || N % B');
 text=once(text,'unsigned alg_unquant(',helper+'\nunsigned alg_unquant(');
 const body=text.match(/^unsigned alg_unquant\([\s\S]*?^}/m)[0];
 let change=once(body,'normalise_residual(iy, X, N, Ryy, gain);','collapse_mask = fused(iy, X, N, Ryy, gain, B);');
 change=once(change,'   collapse_mask = extract_collapse_mask(iy, N, B);\n','');
 text=text.replace(body,change);const file=path.join(dir,'vq.model.c');fs.writeFileSync(file,text);return [{source,file}];
}
function generate(compiler){
 const base=path.join(component,'asm/lx106'),mf=path.join(base,'manifest.json'),m=JSON.parse(fs.readFileSync(mf));
 const dir=path.join(root,'.build/opus-bands-fused');fs.mkdirSync(dir,{recursive:true});
 const entry=m.files.find(f=>f.source===source),original=path.join(base,entry.asm);assert.equal(sourceHash(original),entry.asm_sha256_lf);
 const overlay='bands-fused/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.writeFileSync(dest,transform(fs.readFileSync(original,'utf8')));
 const object=path.join(dir,'vq.o'),control=object+'.control',dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 for(const [s,o] of [[original,control],[dest,object]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
 const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const a=sizes(control),b=sizes(object);assert.deepEqual(Object.keys(a),Object.keys(b));
 for(const s of Object.keys(a).filter(s=>a[s]&&!s.startsWith('.xt.')&&s!=='.text.alg_unquant')){
  if(s.startsWith('.text.'))assert.deepEqual(canonical(run(dump,['-dr','-j',s,control])),canonical(run(dump,['-dr','-j',s,object])),s);
  else {assert.equal(a[s],b[s],s);assert.equal(run(dump,['-s','-j',s,control]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,object]).split('\n').slice(3).join('\n'),s);}
 }
 fs.writeFileSync(path.join(dir,'vq.disassembly.txt'),run(dump,['-dr',object]));
 const report={schema:1,candidate:'bands-fused-v1',base_manifest_sha256:sourceHash(mf),recipe_sha256_lf:sourceHash(__filename),
  dependencies:{'fused_normalize.inc.s':sourceHash(path.join(__dirname,'fused_normalize.inc.s')),'../../tests/native/esp8266_opus_fused_normalize_test.c':sourceHash(path.join(root,'tests/native/esp8266_opus_fused_normalize_test.c'))},
  files:[{source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:a,sections_after:b}],
  additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,stack_frame_bytes:112,mask_slot:72,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-fused.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,source,transform,cModels,generate};if(require.main===module)generate(process.argv[2]);
