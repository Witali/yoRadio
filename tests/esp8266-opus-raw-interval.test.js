const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
test('raw-series default observation interval matches the physical evidence validator',()=>{
 const root=path.resolve(__dirname,'..');
 const runner=fs.readFileSync(path.join(root,'tools/esp8266_opus_profile/run_raw_series.ps1'),'utf8');
 const validator=fs.readFileSync(path.join(root,'tools/esp8266_opus_asm/report_small_div_tail.cjs'),'utf8');
 const a=Number(runner.match(/\$IntervalMs=(\d+)/)[1]),b=Number(validator.match(/assert.equal\(r.interval_ms,(\d+)\)/)[1]);
 assert.equal(a,15000);assert.equal(a,b);assert.match(runner,/--interval-ms \$IntervalMs/);
});
