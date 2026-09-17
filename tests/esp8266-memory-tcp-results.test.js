const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {report,analyze}=require('../tools/esp8266_opus_profile/report_memory_probe.cjs');
test('all ten live memory attempts and recovery remain independently reproducible',()=>{
 const r=report(),saved=JSON.parse(fs.readFileSync(path.join(__dirname,'../firmware/development/esp8266-opus-live-memory-diag-v1/observations.json')));
 assert.deepEqual(r,saved);assert.equal(r.runs.length,10);assert.ok(r.totals.requests_failed>0);
 assert.ok(r.totals.closing_only_ooseq_observations>0);
 assert.equal(r.runs.every(r=>r.heap_valid),true);
 assert.match(r.scope,/Not ASM CPU/);assert.match(r.limitations.join(' '),/not allocated pbuf RAM/);
});
test('a group containing an established PCB does not identify OOO as closing-only',()=>{
 const m={tcp_valid:true,tcp_age_ms:1,client:{pcbs:2,states:(1<<4)|(1<<5),ooseq:1072}};
 const r=analyze({samples:[{memory:{http:200,body:m}}]});
 assert.equal(r.closing_only_ooseq_samples.length,0);
 m.client.states=1<<5;
 assert.equal(analyze({samples:[{memory:{http:200,body:m}}]}).closing_only_ooseq_samples.length,1);
});
