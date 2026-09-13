const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {component,root}=require('../tools/esp8266_opus_asm/export.cjs');
const tell=require('../tools/esp8266_opus_asm/tell_inline.cjs'),update=require('../tools/esp8266_opus_asm/update_fast.cjs');
const combo=require('../tools/esp8266_opus_asm/tell_update.cjs'),{verify}=require('../tools/esp8266_opus_asm/verify.cjs');
test('absolute report distinguishes relative slowdown from CPU percentage points',()=>{
 const {absolute}=require('../tools/esp8266_opus_asm/report_tell_update.cjs');
 const c={name:'mono12',reference:{task_budget_percent:{median:20}},candidate:{task_budget_percent:{median:20.4}},median_task_reduction_percent:-2};
 const [v]=absolute([c]);
 assert.ok(Math.abs(v.cpu_percentage_points-0.4)<1e-10);
 assert.ok(Math.abs(v.delta_us_per_20ms_audio-80)<1e-9);
 assert.equal(v.relative_reduction_percent,-2);
});
test('tell/update composition changes only six exact sites and retains one shared table',()=>{
 const base=path.join(component,'asm/lx106'),source=combo.source;
 const original=fs.readFileSync(path.join(base,'gcc',source+'.s'),'utf8');
 const changed=combo.transform(original);
 assert.equal(changed,combo.transform(original.replace(/\r?\n/g,'\r\n')));
 assert.equal(changed,fs.readFileSync(path.join(base,'bands-tell-update',source+'.s'),'utf8').replace(/\r\n/g,'\n'));
 assert.throws(()=>combo.transform(changed));
 const strip=s=>['tell_inline.inc.s','update_fast.inc.s'].reduce((t,f)=>t.replace(fs.readFileSync(path.join(root,'tools/esp8266_opus_asm',f),'utf8').replace(/\r\n/g,'\n')+'\n',''),s);
 assert.equal(strip(changed),strip(tell.transform(update.transform(original),source)),'Composition order only changes macro-definition order');
 assert.equal((changed.match(/\tY_OPUS_TELL_FRAC\t/g)||[]).length,4);
 assert.equal((changed.match(/\tY_OPUS_UPDATE_FAST\t/g)||[]).length,2);
 const r=verify('bands-tell-update-asm');assert.equal(r.files.length,110);
 assert.equal(r.files.filter(p=>p.includes('bands-tell-update')).length,1);
 assert.equal(r.files.filter(p=>p.includes('bands-tell-inline')).length,1);
 assert.ok(r.files.some(p=>p.replaceAll('\\','/').endsWith('gcc/upstream/celt/entdec.c.s')));
});
