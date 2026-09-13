const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const {root,component,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
test('host path counter keeps PCM and counts complete block distribution on pinned corpus',()=>{
 const source=path.join(component,'upstream/celt/vq.c'),before=sourceHash(source);
 const r=spawnSync(process.execPath,[path.join(root,'tools/esp8266_opus_asm/profile_shapes.cjs')],{encoding:'utf8'});
 assert.equal(r.status,0,r.stderr);assert.equal(sourceHash(source),before);
 const report=JSON.parse(fs.readFileSync(path.join(root,'.build/opus-shapes/result.json')));
 assert.equal(report.passed,true);assert.equal(report.source_sha256_lf,before);assert.equal(report.cases.length,5);
 for(const c of report.cases){assert.equal(c.pcm.exact,true);assert.equal(c.counts.blocks.reduce((s,b)=>s+b.calls,0),c.counts.calls);}
 const high=report.cases.find(c=>c.name==='stereo-192').counts;
 assert.equal(high.calls,1648);assert.equal(high.blocks.find(b=>b.B===1).calls,1360);
 assert.equal(high.fused_calls,288);assert.equal(high.fused_values,2324);assert.equal(high.rotation_calls,69);
 require('../tools/esp8266_opus_asm/verify.cjs').verify('gcc-asm');
});
