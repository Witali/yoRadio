// Reviewed, fail-closed transformations of the pinned GCC assembly, not a new
// compiler export. Every unrelated instruction and every data section is kept.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const kinds=['intensity'];
function once(text,before,after){assert.equal(text.split(before).length,2,'Expected one exact anchor');return text.replace(before,after);}
function transform(text,kind){
 assert.ok(kinds.includes(kind));text=text.replace(/\r\n/g,'\n');
 assert.doesNotMatch(text,/# ASM intensity:/,'Already transformed');
 // This is the stereo-only compute_theta clone inside quant_all_bands.
 // m/i/bandE have already been saved for later inversion/resynthesis. a14=ec.
 // No new stack slots or calls. a8 is dead (bandE saved at sp+140).
 // Preserve the encoder path; .L980 is the original qn=1 decoder continuation.
 // It initializes tell, inv and qalloc, including decoding the inversion bit.
 return once(text,'\tl32i.n\ta4, sp, 48\t# ctx.intensity, intensity\n',
  '\tl32i.n\ta4, sp, 48\t# ctx.intensity, intensity\n'+
  '# ASM intensity: skip unused compute_qn only in the decoder stereo clone.\n'+
  '# Inputs: a10=i, a4=intensity, sp+240=encode; a8 is dead here.\n'+
  '# Preserve a14=ec and all saved m/i/bandE/N/b fields. Entropy is NOT skipped.\n'+
  '\tl32i\ta8, sp, 240\n\tbnez\ta8, .Lasm_intensity_normal\n'+
  '\tblt\ta10, a4, .Lasm_intensity_normal\n\tj\t.L980\n.Lasm_intensity_normal:\n');
}
function cModel(kind){
 assert.ok(kinds.includes(kind));
 let text=fs.readFileSync(path.join(component,'upstream/celt/bands.c'),'utf8').replace(/\r\n/g,'\n');
 text=once(text,'   qn = compute_qn(N, *b, offset, pulse_cap, stereo);',
  '   /* Semantic mirror of the ASM early decoder-only intensity branch. */\n'+
  '   qn = (!encode && stereo && i>=intensity) ? 1 : compute_qn(N, *b, offset, pulse_cap, stereo);');
 const dest=path.join(root,'.build/opus-bands-'+kind,'bands.model.c');
 fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,text);return dest;
}
function generate(kind,compiler){
 const base=path.join(component,'asm/lx106'),manifestFile=path.join(base,'manifest.json');
 const manifest=JSON.parse(fs.readFileSync(manifestFile));
 const source='upstream/celt/bands.c',entry=manifest.files.find(f=>f.source===source);
 const original=path.join(base,entry.asm);assert.equal(sourceHash(original),entry.asm_sha256_lf);
 const overlay='bands-'+kind+'/'+source+'.s',dest=path.join(base,overlay);
 const text=transform(fs.readFileSync(original,'utf8'),kind);
 fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,text);
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const obj=path.join(dir,'candidate.o'),control=path.join(dir,'control.o');
 for(const [src,out] of [[dest,obj],[original,control]])run(compiler,['-mlongcalls','-x','assembler','-c',src,'-o',out]);
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const a=sizes(control),b=sizes(obj);assert.deepEqual(Object.keys(a),Object.keys(b));
 for(const s of Object.keys(a).filter(s=>a[s]&&!s.startsWith('.xt.')&&s!=='.text.quant_all_bands')){
  assert.equal(a[s],b[s],s);
  for(const arg of ['-dr','-s'])assert.equal(run(dump,[arg,'-j',s,control]).split('\n').slice(3).join('\n'),run(dump,[arg,'-j',s,obj]).split('\n').slice(3).join('\n'),s);
 }
 const report={schema:1,candidate:'bands-'+kind+'-v1',source,base_manifest_sha256:sourceHash(manifestFile),overlay,overlay_sha256_lf:sourceHash(dest),recipe_sha256_lf:sourceHash(__filename),additional_heap_bytes:0,additional_static_ram_bytes:0,stack_change_bytes:0,sections_before:a,sections_after:b,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-'+kind+'.json'),JSON.stringify(report,null,2)+'\n');
 fs.writeFileSync(path.join(dir,'disassembly.txt'),run(dump,['-dr','-j','.text.quant_all_bands',obj]));
 console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kinds,once,transform,cModel,generate};
if(require.main===module)generate(process.argv[2],process.argv[3]);
