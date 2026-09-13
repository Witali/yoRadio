const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {component,root,sourceHash,hash,run}=require('./export.cjs');
const base=path.join(component,'asm/lx106');
function optimize({compiler}) {
  const manifest=JSON.parse(fs.readFileSync(path.join(base,'manifest.json'),'utf8'));
  const f=manifest.files.find(f=>f.source==='upstream/celt/entdec.c');
  const original=path.join(base,f.asm);
  assert.equal(sourceHash(original),f.asm_sha256_lf,'Baseline changed; do not patch an unknown compiler output');
  let text=fs.readFileSync(original,'utf8');
  const replacement=fs.readFileSync(path.join(__dirname,'ec_dec_update.inc.s'),'utf8');
  assert.equal((text.match(/^ec_dec_update:/gm)||[]).length,1);
  text=text.replace(/^ec_dec_update:[\s\S]*?(?=^\s*\.size\s+ec_dec_update,)/m,replacement+'\n');
  const dest=path.join(base,'optimized',f.source+'.s');fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,text);
  const artifact=path.join(root,'firmware/development/esp8266-opus-asm-library');
  const obj=path.join(root,'.build/opus-asm-export/optimized-entdec.o');
  run(compiler,['-mlongcalls','-x','assembler','-c',dest,'-o',obj]);
  const bin=path.dirname(compiler),dump=path.join(bin,'xtensa-lx106-elf-objdump.exe');
  const disasm=run(dump,['-dr','-j','.text.ec_dec_update',obj]);
  assert.doesNotMatch(disasm,/\b(?:a1|a12|a13|a14|a15)\b|\s(?:call\w*|rsil|memw)\s/);
  const lib=path.join(artifact,'libopus-optimized-asm.a');fs.copyFileSync(path.join(artifact,'libopus-gcc-asm.a'),lib);
  // Replace exact member name, never append a second ec_dec_update definition.
  const member='upstream__celt__entdec.c.o',named=path.join(root,'.build/opus-asm-export/optimized',member);
  fs.mkdirSync(path.dirname(named),{recursive:true});fs.copyFileSync(obj,named);
  const ar=path.join(bin,'xtensa-lx106-elf-ar.exe');run(ar,['rD',lib,named]);run(ar,['sD',lib]);
  const members=run(ar,['t',lib]).trim().split(/\r?\n/);assert.equal(members.length,manifest.files.length);assert.equal(members.filter(m=>m===member).length,1);
  const report={schema:1,candidate:'ec-dec-update-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),overlay:'optimized/'+f.source+'.s',overlay_sha256_lf:sourceHash(dest),recipe_sha256_lf:sourceHash(path.join(__dirname,'ec_dec_update.inc.s')),function:'ec_dec_update',stack_bytes_before:16,stack_bytes_after:0,additional_heap_bytes:0,additional_static_ram_bytes:0,physical_speed_measured:false,library_sha256:hash(fs.readFileSync(lib)),library_bytes:fs.statSync(lib).size};
  fs.writeFileSync(path.join(base,'optimized.json'),JSON.stringify(report,null,2)+'\n');
  fs.copyFileSync(path.join(base,'optimized.json'),path.join(artifact,'optimized.json'));
  fs.writeFileSync(path.join(artifact,'ec_dec_update.asm'),disasm);
  console.log(report);return report;
}
module.exports={optimize,base};
if(require.main===module){const i=process.argv.indexOf('--compiler');assert.ok(i>=0,'--compiler required');optimize({compiler:process.argv[i+1]});}
