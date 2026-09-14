const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const {macro,coefficients,transform}=require('../tools/esp8266_opus_asm/folding8.cjs');
const {instrument,standardSizes}=require('../tools/esp8266_opus_asm/profile_folding.cjs');
const {compileModel,candidate}=require('../tools/esp8266_opus_asm/report_folding8.cjs');
const census=require('../tools/esp8266_opus_asm/folding-census-results.json');
test('coefficients use original integer sqrt, not the system floating sqrt',()=>{
 assert.equal(census.fixed_point,true);assert.equal(census.recipe_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/profile_folding.cjs')));
 assert.equal(census.config_sha256_lf,sourceHash(path.join(component,'upstream/include/config.h')));
 assert.equal(census.all_values[8],5793);assert.notEqual(census.all_values[8],Math.floor(Math.sqrt(8*2**22)));
 assert.equal(census.all_values[256],32767);assert.equal(census.all_values[511],32767);
 assert.deepEqual(coefficients(),Array.from({length:23},(_,i)=>census.all_values[i*8]));assert.equal(coefficients().length*4,92);
});
test('84 standard band/LM combinations are preserved and census is exact PCM through 510',()=>{
 const s=standardSizes(fs.readFileSync(path.join(component,'upstream/celt/modes.c'),'utf8'));
 assert.deepEqual(s,census.standard);assert.equal(s.rows.length,84);assert.equal(s.sizes.length,20);
 assert.equal(census.cases.length,10);for(const c of census.cases){assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);}
 const high=census.cases.find(c=>c.name==='stereo-192');assert.equal(high.calls,260);assert.equal(high.audio_duration_ms,240);
 assert.ok(high.counts.every(c=>c.N%8===0&&c.N<=176));assert.ok(census.cases.some(c=>c.name==='stereo-510'));
 const source=fs.readFileSync(path.join(component,'upstream/celt/bands.c'),'utf8');assert.throws(()=>instrument(instrument(source)));
});
test('ASM changes only the dynamic folding call; constant-N2 and C fallback remain',()=>{
 const source=fs.readFileSync(path.join(component,'asm/lx106/bands-tell-inline/upstream/celt/bands.c.s'),'utf8').replace(/\r\n/g,'\n');
 const changed=transform(source);assert.equal((changed.match(/\tY_FOLD8\t/g)||[]).length,1);
 const restored=changed.slice((macro+'\n').length).split('\n# Values computed by the pinned original fixed-point sqrt.\n')[0]
 .replace('\t.literal .Lfold8_table, yoradio_opus_folding8_table\n','')
 .replace('\tY_FOLD8\t# Exact multiples-of-eight folding scale; fallback unchanged.','\tcall0\tcelt_sqrt\t\t#');
 assert.equal(restored,source);assert.throws(()=>transform(changed));
 assert.doesNotMatch(macro,/\bs(?:8|16|32)i\b|\bret(?:\.n)?\b/);
 require('../tools/esp8266_opus_asm/verify.cjs').verify('bands-folding8-asm');
});
test('actual linked graph has valid table bounds, original fallback arguments and no RAM growth',()=>{
 const p=JSON.parse(fs.readFileSync(path.join(root,'firmware/development',candidate,'preflight.json')));assert.equal(p.passed,true);
 assert.equal(p.checker_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/report_folding8.cjs')));assert.equal(p.static_ram_delta,0);assert.ok(p.model.cases>=100000);
 const exec=compileModel(p.expansion.graph,coefficients());
 for(const {N}of census.standard.rows){const r=exec(N,new Uint32Array(16));assert.equal(r.fallback,!!(N%8));if(!r.fallback)assert.equal(r.result,census.all_values[N]);else assert.equal(r.registers[2],N<<22);}
 for(const N of [-1,177,192,256,511,0x7fffffff,0xffffffff]){const r=exec(N,new Uint32Array(16));assert.equal(r.fallback,true);assert.equal(r.registers[2],(N<<22)>>>0);}
 assert.equal(p.host.passed,true);assert.ok(p.host.cases.some(c=>c.name==='stereo-510'));
 assert.throws(()=>compileModel(['s32i a2, a1, 0'],coefficients()));assert.throws(()=>compileModel(['j instruction:50'],coefficients()));
});
