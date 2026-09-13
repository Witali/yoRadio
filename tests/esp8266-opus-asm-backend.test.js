const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {words,annotate,component,root}=require('../tools/esp8266_opus_asm/export.cjs');
const {verify}=require('../tools/esp8266_opus_asm/verify.cjs');
test('compiler command parser does not invoke a shell and keeps quoted definitions',()=>{
 assert.deepEqual(words('gcc -DIDF_VER=\\"v3.4\\" -I"path with spaces" -c file.c'),['gcc','-DIDF_VER="v3.4"','-Ipath with spaces','-c','file.c']);
 assert.throws(()=>words('gcc "unclosed'));
});
test('full ASM snapshot covers every upstream unit and both variants verify',()=>{
 for(const backend of ['gcc-asm','optimized-asm']){
  const r=verify(backend);assert.equal(r.files.length,110);assert.ok(r.manifest.files.every(f=>f.roundtrip_exact));
  for(const f of r.files){const text=fs.readFileSync(f,'utf8');for(const m of text.matchAll(/^\s*\.type\s+([^,\s]+),\s*@function/gm))assert.ok(text.includes('# Function: '+m[1]));}
 }
 assert.throws(()=>verify('not-a-backend'));
});
test('annotations preserve comments and describe the function ABI',()=>{
 const a=annotate('.type f, @function\nf:\n ret.n\n','upstream/celt/entdec.c','/* Decode a symbol. */\nint f(int x){return x;}');
 assert.match(a,/# Function: f/);assert.match(a,/ABI: LX106 call0/);assert.match(a,/Decode a symbol/);
});
test('stale source hashes and a different exported feature set fail closed',()=>{
 const m=JSON.parse(fs.readFileSync(path.join(component,'asm/lx106/manifest.json'),'utf8'));
 const parent=path.join(root,'.build');fs.mkdirSync(parent,{recursive:true});
 const dir=fs.mkdtempSync(path.join(parent,'asm-guard-negative-'));
 const copy=JSON.parse(JSON.stringify(m));copy.feature_defines.push('YORADIO_OPUS_LOW_RAM=1');
 fs.writeFileSync(path.join(dir,'manifest.json'),JSON.stringify(copy));
 assert.throws(()=>verify('gcc-asm',dir),/feature set is incompatible/);
 m.protected_sources[Object.keys(m.protected_sources)[0]]='0'.repeat(64);
 fs.writeFileSync(path.join(dir,'manifest.json'),JSON.stringify(m));
 assert.throws(()=>verify('gcc-asm',dir),/Stale ASM source\/header/);
});
test('ASM backend is opt-in, diagnostic only and ABI-incompatible features are rejected',()=>{
 const cmake=fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8'),guard=fs.readFileSync(path.join(component,'asm/select.cmake'),'utf8');
 assert.match(cmake,/set\(YORADIO_OPUS_BACKEND "c" CACHE/);
 assert.match(cmake,/COMPILE_LANGUAGE:ASM>:-mlongcalls/);
 assert.match(guard,/NOT YORADIO_ESP8266_DIAGNOSTIC/);
 for(const flag of ['LOW_RAM','PCM_LEASES','ROTATION_LX106','DIV_ONCE'])assert.ok(guard.includes('YORADIO_OPUS_'+flag));
 assert.match(guard,/CMAKE_CONFIGURE_DEPENDS/);
});
