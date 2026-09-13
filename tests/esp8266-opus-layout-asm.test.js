const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component}=require('../tools/esp8266_opus_asm/export.cjs');
const {choices,prefix,transform,source,normalizeLiteral}=require('../tools/esp8266_opus_asm/layout.cjs');
const {verify}=require('../tools/esp8266_opus_asm/verify.cjs');
test('placement overlays change only unreachable prefix; parent, C and GCC stay pinned',()=>{
 const base=path.join(component,'asm/lx106'),parent=fs.readFileSync(path.join(base,'bands-tell-inline',source+'.s'),'utf8').replace(/\r\n/g,'\n');
 for(const bytes of choices){
  const changed=transform(parent,bytes);assert.equal(changed.replace(prefix(bytes),''),parent);
  assert.equal(changed,transform(parent.replace(/\n/g,'\r\n'),bytes));
  assert.throws(()=>transform(changed,bytes));assert.equal((changed.match(/Layout-only experiment/g)||[]).length,1);
  const checked=verify('bands-layout'+bytes+'-asm');assert.equal(checked.files.length,110);
  assert.equal(checked.files.filter(f=>f.includes('bands-layout'+bytes)).length,1);
  assert.equal(checked.files.filter(f=>f.includes('bands-tell-inline')).length,1);
  const r=JSON.parse(fs.readFileSync(path.join(base,'bands-layout'+bytes+'.json')));
  assert.equal(r.files[0].entry_after.address-r.files[0].entry_before.address,bytes);
  assert.equal(r.files[0].entry_after.bytes,r.files[0].entry_before.bytes);
  assert.equal(r.additional_static_ram_bytes,0);assert.equal(r.stack_change_bytes,0);
 }
 for(const bad of [0,1,16,64,256,NaN])assert.throws(()=>transform(parent,bad));
});
test('only relocated quant_partition entry literals normalize; numeric data remain checked',()=>{
 const a=Buffer.alloc(12);a.writeUInt32LE(0xfeed1234,0);a.writeUInt32LE(0x12345678,8);
 const b=Buffer.from(a);b.writeUInt32LE(32,4);
 const reloc='00000004 R_XTENSA_32 .text.quant_partition\n00000008 R_XTENSA_32 external\n';
 const n=normalizeLiteral(b,reloc,32);assert.deepEqual(n.bytes,a);assert.deepEqual(n.changed,[4]);
 assert.equal(b.readUInt32LE(4),32,'No mutation of source bytes');
 assert.throws(()=>normalizeLiteral(b,reloc,128));
 assert.deepEqual(normalizeLiteral(b,'00000004 R_XTENSA_32 .text.other\n',32).bytes,b);
 b.writeUInt32LE(0xfeed1235,0);assert.notDeepEqual(normalizeLiteral(b,reloc,32).bytes,a);
});
test('both placement modes exposed through build configuration',()=>{
 for(const p of ['tools/esp8266_audio_profile/build_i2s_pdm_production.ps1','esp8266/rtos-sdk-native/components/opus_decoder/CMakeLists.txt']){
  const s=fs.readFileSync(path.join(root,p),'utf8');for(const n of choices)assert.ok(s.includes('bands-layout'+n+'-asm'));
 }
});
