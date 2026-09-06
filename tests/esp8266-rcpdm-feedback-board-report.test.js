const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {MODES,summarize}=require('../tools/esp8266_audio_profile/summarize_rcpdm_feedback_board');
const dir=path.join(__dirname,'../docs/benchmarks/esp8266-rcpdm-feedback-board-2026-09-06');
test('archived physical feedback measurements reproduce summaries and matching carrier conditions',()=>{
  const report=JSON.parse(fs.readFileSync(path.join(dir,'results.json'),'utf8'));
  assert.deepEqual(summarize(dir).summary,report.summary);
  assert.deepEqual(report.order,['1:pdm','1:production','1:simple-u4','1:feedback','2:feedback','2:simple-u4','2:production','2:pdm']);
  assert.equal(report.restore.full_flash_verified,true);
  assert.equal(report.restore.boot_verified,true);
  for(const mode of MODES) {
    const m=report.builds[mode].manifest;
    assert.equal(m.mode,mode);assert.equal(m.bits,32);assert.equal(m.pcm_rate,48000);
    assert.equal(m.bit_rate_hz,1536000);assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');
    assert.equal(report.summary[mode].underruns,0);assert.equal(report.summary[mode].fifo_empty,0);
  }
  for(const key of ['feedback_source_sha256','output_source_sha256','benchmark_source_sha256'])
    assert.equal(new Set(MODES.map(m=>report.builds[m].manifest[key])).size,1);
  const http=JSON.parse(fs.readFileSync(path.join(dir,'restore-http.json'),'utf8'));
  assert.equal(http.status,200);assert.ok(http.bytes>1000);
});
