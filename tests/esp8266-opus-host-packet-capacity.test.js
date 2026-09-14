const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root}=require('../tools/esp8266_opus_asm/export.cjs');
test('desktop fixture reader accepts the complete uint16 packet container',()=>{
 const text=fs.readFileSync(path.join(root,'tools/esp8266_opus_profile/probe.c'),'utf8');
 assert.match(text,/#define OPUS_PROBE_PACKET_CAPACITY UINT16_MAX/);
 assert.equal((text.match(/packet\[OPUS_PROBE_PACKET_CAPACITY\]/g)||[]).length,3);
 assert.doesNotMatch(text,/packet\[4096\]/);
 assert.match(text,/size && size <= sizeof\(packet\)/);
});
