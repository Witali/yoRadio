const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/ebands_pair.cjs'),s=require('../tools/esp8266_opus_asm/ebands_pair_proof.cjs');
const {sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n));
test('linked eBands pair preserves exact signed data, all live GPRs/SAR and RAM across both word phases',()=>{
 const p=f.verifyPair().proof;assert.equal(p.semantic.numeric_cases,132416);assert.equal(p.semantic.frame_bytes,192);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.deepEqual(p.semantic.symbolic.map(x=>x.loads),[1,2]);assert.equal(p.table.bytes,44);assert.ok(p.semantic.dead_return.visited.length>0);assert.ok(p.semantic.dead_return.stops.length>0);
 const parse=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs').parsed;
 for(const row of parse({disassembly:p.helperDisassembly}))for(const operand of row.operands.filter(x=>/^a\d+$/.test(x)))assert.ok(['a2','a3','a11'].includes(operand));
});
test('eBands proof rejects wrong signedness, overwritten pointer, unexpected a0 use and table corruption',()=>{
 const p=read('preflight.json');
 assert.throws(()=>s.symbolic(p.helperDisassembly.replace('srai\ta11, a11, 16','srai\ta11, a11, 15')));
 assert.throws(()=>s.symbolic(p.helperDisassembly.replace('addi\ta11, a3, -2','addi\ta11, a3, 2')));
 const fn=p.functions.clt_compute_allocation;
 const bad={...fn,disassembly:fn.disassembly.split('\n').map(l=>l.trimStart().startsWith(s.end.toString(16)+':')?l.replace('a4, a4, a14','a4, a0, a14'):l).join('\n')};assert.notEqual(bad.disassembly,fn.disassembly);assert.throws(()=>s.deadReturn(bad),/Live return address/);
 const data=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs').readAt(data,s.table+42,2)[0]^=1;assert.throws(()=>s.tableProof(data));
});
test('eBands target reads stay within the22-element table, including its last pair',()=>{
 const p=read('preflight.json'),parse=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs').parsed,rows=[...parse(p.actual_functions.clt_compute_allocation),...parse({disassembly:p.helperDisassembly})],data=Buffer.alloc(44);
 for(const pointer of[s.table-2,s.table+42,s.table+1]){const r=Array(16).fill(0);r[3]=pointer;assert.throws(()=>s.execute(rows,r,data,0,true),/Invalid pair pointer/);}
 const r=Array(16).fill(0);r[3]=s.table+40;data.writeInt16LE(-32768,40);data.writeInt16LE(32767,42);const out=s.execute(rows,r,data,63,true);assert.equal(out.registers[11],0xffff8000);assert.equal(out.registers[2],32767);assert.equal(out.sar,63);assert.equal(out.words,1);
});
test('host eBands model retains24 exact PCM/state/PLC/reset/OOM scenarios through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'ebands-pair');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/ebands_pair.cjs')));
});
test('the frozen profile uses the single standard44-byte eBands table, not custom modes',()=>{
 const {component}=require('../tools/esp8266_opus_asm/export.cjs');
 assert.match(fs.readFileSync(path.join(component,'upstream/include/config.h'),'utf8'),/\/\* #undef CUSTOM_MODES \*\//);
 const modes=fs.readFileSync(path.join(component,'upstream/celt/static_modes_fixed.h'),'utf8');assert.match(modes,/#define TOTAL_MODES 1/);assert.match(modes,/static_mode_list\[TOTAL_MODES\] = \{\s*&mode48000_960_120,/);
 const a=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz'))),readAt=require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs').readAt;
 assert.equal(readAt(a,0x402d3968,4).readUInt32LE(),48000);assert.equal(readAt(a,0x402d3968+8,4).readUInt32LE(),21);assert.deepEqual(s.tableProof(a),read('preflight.json').table);
});
