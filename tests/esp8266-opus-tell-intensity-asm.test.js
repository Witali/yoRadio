const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {component}=require('../tools/esp8266_opus_asm/export.cjs');
const intensity=require('../tools/esp8266_opus_asm/bands.cjs'),tell=require('../tools/esp8266_opus_asm/tell_inline.cjs');
const {verify}=require('../tools/esp8266_opus_asm/verify.cjs');
test('tell + intensity is exactly either composition order, with one correction table',()=>{
 const base=path.join(component,'asm/lx106'),source='upstream/celt/bands.c';
 const original=fs.readFileSync(path.join(base,'gcc',source+'.s'),'utf8');
 const combined=fs.readFileSync(path.join(base,'bands-tell-intensity',source+'.s'),'utf8').replace(/\r\n/g,'\n');
 assert.equal(combined,tell.transform(intensity.transform(original,'intensity'),source));
 assert.equal(combined,intensity.transform(tell.transform(original,source),'intensity'));
 const r=verify('bands-tell-intensity-asm');assert.equal(r.files.length,110);
 assert.equal(r.files.filter(p=>p.includes('bands-tell-intensity')).length,1);
 assert.equal(r.files.filter(p=>p.includes('bands-tell-inline')).length,1);
 assert.ok(r.files.some(p=>p.replaceAll('\\','/').endsWith('gcc/upstream/celt/vq.c.s')));
 assert.doesNotMatch(combined,/^\s*\.(?:byte|short|word)\s+35733/m);
});
