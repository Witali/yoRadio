const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const {macro,tableText,transform}=require('../tools/esp8266_opus_asm/small_div_inline.cjs');
const {compile}=require('../tools/esp8266_opus_asm/inline_div_model.cjs');
const {collapse,candidate}=require('../tools/esp8266_opus_asm/report_small_div_inline.cjs');
const proofFile=path.join(root,'firmware/development',candidate,'preflight.json');
test('only three pinned rng/ft calls expand; original C/ASM and other instructions are preserved',()=>{
 const source=fs.readFileSync(path.join(component,'asm/lx106/gcc/upstream/celt/entdec.c.s'),'utf8').replace(/\r\n/g,'\n');
 const changed=transform(source);assert.equal((changed.match(/Y_OPUS_SMALL_DIV [012]\b/g)||[]).length,3);
 const restored=changed.slice((macro+'\n').length).replace('\n# One shared exact reciprocal table.\n'+tableText,'')
  .replace('\t.literal .Ly_inline_table, yoradio_opus_small_div_table\n','').replace(/Y_OPUS_SMALL_DIV [012]/g,'call0\t__udivsi3');
 assert.equal(restored,source);assert.throws(()=>transform(changed));
 assert.throws(()=>transform(source.replace('call0\t__udivsi3','call0\tother')));
 assert.doesNotMatch(macro,/\bs(?:8|16|32)i\b|\bret(?:\.n)?\b/);
});
test('inline build selection verifies pinned source and generator hashes',()=>{
 require('../tools/esp8266_opus_asm/verify.cjs').verify('bands-small-div-inline-asm');
 const cmake=fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8');
 assert.match(cmake,/bands-small-div-inline-asm/);assert.match(cmake,/set\(YORADIO_OPUS_BACKEND "c" CACHE/);
});
test('collapse refuses external branches into an expansion or missing boundaries',()=>{
 const r=[{start:3,end:8}];
 assert.throws(()=>collapse('0: 000086 j 6 <middle>\n3: 000000 movi a4, 256\n6: 0000 mov a2, a2\n8: f00d ret.n',r));
 assert.throws(()=>collapse('0: 000086 j 3 <start>\n3: 000000 movi a4, 256',r));
 const s=collapse('0: 000086 j 3 <start>\n3: 000000 movi a4, 256\n6: 0000 mov a2, a2\n8: f00d ret.n',r);
 assert.match(s,/3: 000005 call0 4000e21c/);assert.doesNotMatch(s,/6:/);
});
test('model rejects stores, unknown instructions and branches outside graph',()=>{
 assert.throws(()=>compile(['s32i a2, a1, 0']));assert.throws(()=>compile(['j instruction:99','ret ']));
 assert.throws(()=>compile(['unknown a2']));
 const extract=compile(['extui a2, a2, 16, 16','ret ']);assert.equal(extract(0x98761234,1).result,0x9876);
});
test('actual linked expansions have identical semantics, no RAM growth and unchanged host PCM through 510',()=>{
 assert.ok(fs.existsSync(proofFile),'Run preflight first; do not silently skip linked proof');
 const p=JSON.parse(fs.readFileSync(proofFile));assert.equal(p.passed,true);assert.equal(p.static_ram_delta,0);
 assert.equal(p.model_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/inline_div_model.cjs')));
 assert.equal(p.checker_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/report_small_div_inline.cjs')));
 assert.equal(p.expansions.length,3);assert.ok(p.model.cases>1000000);assert.equal(p.model.fallbacks,20);
 for(const e of p.expansions){assert.deepEqual(e.graph,p.expansions[0].graph);const exec=compile(e.graph);
  for(const d of [1,2,3,7,127,128,255,256])for(const n of [0,1,0x7fffffff,0x80000000,0xffffffff]){
   const initial=Array.from({length:16},(_,i)=>0x87650000+i),o=exec(n,d,initial);
   assert.equal(o.result,Number(BigInt(n)/BigInt(d)));for(const i of [0,1,12,13,14,15])assert.equal(o.registers[i],initial[i]);
  }
 }
 const g=p.expansions[0].graph.map(s=>s==='add a5, a5, a10'?'sub a5, a5, a10':s);assert.notDeepEqual(g,p.expansions[0].graph);
 const bad=compile(g);assert.notEqual(bad(0xffffffff,7).result,Number(0xffffffffn/7n));
 assert.equal(p.host.passed,true);assert.ok(p.host.cases.some(c=>c.name==='stereo-510'));
});
