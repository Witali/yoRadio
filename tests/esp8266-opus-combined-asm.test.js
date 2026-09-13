const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {component}=require('../tools/esp8266_opus_asm/export.cjs');
const {transform}=require('../tools/esp8266_opus_asm/bands.cjs');
const {verify}=require('../tools/esp8266_opus_asm/verify.cjs');
test('combined ASM is precisely intensity on block shifts, with unchanged vq overlay',()=>{
 const base=path.join(component,'asm/lx106');
 const blocks=fs.readFileSync(path.join(base,'bands-blocks/upstream/celt/bands.c.s'),'utf8');
 const combined=fs.readFileSync(path.join(base,'bands-combined/upstream/celt/bands.c.s'),'utf8').replace(/\r\n/g,'\n');
 assert.equal(combined,transform(blocks,'intensity'));
 const verified=verify('bands-combined-asm');assert.equal(verified.files.length,110);
 assert.equal(verified.files.filter(f=>f.includes('bands-combined')).length,1);
 assert.equal(verified.files.filter(f=>f.includes('bands-blocks')).length,1);
});
