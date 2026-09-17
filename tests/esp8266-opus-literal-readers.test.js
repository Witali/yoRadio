const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const {root,run}=require('../tools/esp8266_opus_asm/export.cjs');
const {literalReader}=require('../tools/esp8266_opus_asm/literal_readers.cjs');
const elf=path.join(root,'.build/esp8266-opus-live-asm-rxdiag-base-20260917/yoradio_esp8266_helix_native.elf');
test('reachable audit rejects a padding-induced phantom SPIFFS literal load',()=>{
 const dis=run('C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin/xtensa-lx106-elf-objdump.exe',['-d',elf]);
 assert.equal(dis.split('\n').filter(l=>/l32r\s+[^,]+,\s*40211a28\b/.test(l)).length,2);
 const actual=literalReader(elf,0x40211a28);
 assert.equal(actual.length,1);assert.match(actual[0],/4024d04a:/);
});
test('a genuine shared mask literal remains shared and is not filtered',()=>{
 const actual=literalReader(elf,0x4021128c);
 assert.ok(actual.length>1);assert.ok(actual.some(l=>/4022b023:/.test(l)));
});
