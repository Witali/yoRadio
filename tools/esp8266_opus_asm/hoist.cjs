// Mechanical transformation of two reviewed GCC loops, not approximate math.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {component,root,sourceHash,hash,run}=require('./export.cjs');
const specs=[{fn:'alg_unquant',label:'.L146',reg:'a6'},{fn:'renormalise_vector',label:'.L185',reg:'a5'}];
const escape=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
function instructions(s){return s.split(/\r?\n/).map(l=>l.split('#')[0].trim()).filter(l=>l&&!l.startsWith('.type'));}
function transform(text,spec){
 text=text.replace(/\r\n/g,'\n');
 const {fn,label,reg}=spec;
 const fnBody=text.match(new RegExp('^'+fn+':[\\s\\S]*?(?=^\\s*\\.size\\s+'+fn+',)','m'))?.[0];assert.ok(fnBody,'Missing function');
 const start=fnBody.indexOf(label+':');assert.ok(start>=0);
 const tail=fnBody.slice(start),branch=new RegExp('^\\s*(blt|bne)\\s+[^#\\n]*,\\s*'+escape(label)+'(?:\\s*#[^\\n]*)?$','m');
 const end=tail.match(branch);assert.ok(end,'Missing loop back-edge');
 const loop=tail.slice(0,end.index+end[0].length),ops=instructions(loop).slice(1);
 // Straight-line body, single entry/back-edge, invariant shift register.
 assert.equal((fnBody.match(new RegExp(escape(label)+'(?=[\\s:#,]|$)','g'))||[]).length,2,'External entry into loop');
 assert.equal(ops.filter(l=>/^ssr\s/.test(l)).length,1);
 assert.ok(ops.some(l=>new RegExp('^ssr\\s+'+reg+'$').test(l)));
 assert.ok(ops.slice(0,-1).every(l=>/^(l32i\.n|l16ui|mul16s|addi\.n|add\.n|ssr|sra|s16i)\s/.test(l)),'Unexpected instruction/SAR writer/call');
 const beforeSsr=ops.slice(0,ops.findIndex(l=>/^ssr\s/.test(l)));
 assert.ok(beforeSsr.every(l=>!/^sra\s/.test(l)),'SAR used before setup');
 for(const l of ops)if(!/^(ssr|s16i|blt|bne)\s/.test(l))
   assert.notEqual(l.split(/\s+/)[1].split(',')[0],reg,'Loop changes shift register');
 const removed=loop.replace(new RegExp('^[ \\t]*ssr[ \\t]+'+reg+'(?:[ \\t]*#[^\\n]*)?\\n','m'),'');
 assert.notEqual(removed,loop);
 const prefix=`# Hoisted invariant SAR setup for ${fn}; no calls/SAR writers in loop.\n# Same loads/stores, multiply, rounding, arithmetic shift and final SAR value.\n# SDK context save/restore preserves SAR across interrupts; IRQs stay enabled.\n\tssr\t${reg}\n`;
 assert.deepEqual(instructions(removed),instructions(loop).filter(l=>!/^ssr\s/.test(l)),'Removal changed another instruction/comment boundary');
 return {text:text.replace(loop,prefix+removed),before:loop,after:prefix+removed,spec};
}
function generate(compiler){
 const base=path.join(component,'asm/lx106'),m=JSON.parse(fs.readFileSync(path.join(base,'manifest.json')));
 const f=m.files.find(f=>f.source==='upstream/celt/vq.c'),original=path.join(base,f.asm);
 assert.equal(sourceHash(original),f.asm_sha256_lf);let text=fs.readFileSync(original,'utf8');const loops=[];
 for(const spec of specs){const t=transform(text,spec);text=t.text;loops.push({spec,before:t.before,after:t.after});}
 const overlay='hoisted/'+f.source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,text);
 const dir=path.join(root,'.build/opus-asm-hoist'),artifact=path.join(root,'firmware/development/esp8266-opus-hoisted-asm-library');
 fs.mkdirSync(dir,{recursive:true});fs.mkdirSync(artifact,{recursive:true});
 const obj=path.join(dir,'upstream__celt__vq.c.o');run(compiler,['-mlongcalls','-c','-x','assembler',dest,'-o',obj]);
 const bin=path.dirname(compiler),objdump=path.join(bin,'xtensa-lx106-elf-objdump.exe');
 const control=path.join(dir,'control.o');run(compiler,['-mlongcalls','-c','-x','assembler',original,'-o',control]);
 const sizes=p=>Object.fromEntries([...run(objdump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const a=sizes(control),b=sizes(obj);assert.deepEqual(Object.keys(a),Object.keys(b));
 for(const section of Object.keys(a)){
   // GAS can widen density instructions/pad the relocated loop by up to3B.
   // This is flash alignment, not additional algorithm steps or RAM.
   if(specs.some(v=>section==='.text.'+v.fn))assert.ok(b[section]<=a[section]+3,'Unexpected code growth: '+section);
   else assert.equal(b[section],a[section],'Non-code section grew: '+section);
 }
 // No other function or data section may change. Relocations must remain exact too.
 for(const section of Object.keys(a).filter(s=>a[s]&&!s.startsWith('.xt.')&&!specs.some(v=>s==='.text.'+v.fn))){
   const dump=(p,args)=>run(objdump,[...args,'-j',section,p]).split('\n').slice(3).join('\n');
   assert.equal(dump(obj,['-dr']),dump(control,['-dr']),section);
   assert.equal(dump(obj,['-s']),dump(control,['-s']),section);
 }
 const library=path.join(artifact,'libopus-hoisted-asm.a');fs.copyFileSync(path.join(root,'firmware/development/esp8266-opus-asm-library/libopus-gcc-asm.a'),library);
 const ar=path.join(bin,'xtensa-lx106-elf-ar.exe');run(ar,['rD',library,obj]);run(ar,['sD',library]);
 const manifest={schema:1,candidate:'vq-invariant-sar-v1',source:f.source,base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),overlay,overlay_sha256_lf:sourceHash(dest),recipe_sha256_lf:sourceHash(__filename),functions:specs.map(v=>v.fn),additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,sections_before:a,sections_after:b,physical_speed_measured:false,library_sha256:hash(fs.readFileSync(library)),library_bytes:fs.statSync(library).size};
 fs.writeFileSync(path.join(base,'hoisted.json'),JSON.stringify(manifest,null,2)+'\n');
 fs.writeFileSync(path.join(artifact,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
 fs.writeFileSync(path.join(dir,'loops.json'),JSON.stringify(loops,null,2)+'\n');
 fs.writeFileSync(path.join(artifact,'vq-disassembly.txt'),run(objdump,['-dr','-j','.text.alg_unquant','-j','.text.renormalise_vector',obj]));
 console.log(JSON.stringify(manifest,null,2));return manifest;
}
module.exports={specs,transform,instructions,generate};
if(require.main===module)generate(process.argv[2]);
