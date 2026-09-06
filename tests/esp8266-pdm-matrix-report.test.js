const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {summarize}=require('../tools/esp8266_audio_profile/summarize_pdm_matrix');
const dir=path.join(__dirname,'../docs/benchmarks/esp8266-pdm-frequency-matrix-2026-09-06');
const result=JSON.parse(fs.readFileSync(path.join(dir,'results.json'),'utf8'));

test('saved tables use identical frequencies and rate-appropriate RC shifts',()=>{
  const report=summarize(result);
  assert.equal(report,fs.readFileSync(path.join(dir,'README.md'),'utf8').replace(/\r\n/g,'\n'));
  assert.equal((report.match(/^## \d,\d{3} МГц;/gm)||[]).length,5);
  const frequency=structuredClone(result);
  frequency.variants['simple64-a32'].bit_rate_hz=1536000;
  assert.throws(()=>summarize(frequency),/Frequency\/RC mismatch/);
  const coefficient=structuredClone(result);
  coefficient.variants['rc128-a64'].alpha=1/16;
  assert.throws(()=>summarize(coefficient),/Frequency\/RC mismatch/);
  const incomplete=structuredClone(result);incomplete.cases.pop();
  assert.throws(()=>summarize(incomplete),/Incomplete matrix/);
});
