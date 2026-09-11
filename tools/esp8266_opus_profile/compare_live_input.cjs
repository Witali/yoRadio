// Live input-capacity experiment. Retains failed windows; never presents wall
// time as decoder CPU or different broadcasts as identical PCM fixtures.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {summarize}=require('./run_stage_wall.cjs');
const {stats}=require('./compare_raw.cjs');
const {sha256}=require('./fixtures.cjs');
function summarizeSeries(reports) {
  assert.ok(reports.length>=10,'At least ten attempted windows are required');
  const windows=reports.map((r,i)=>({run:i+1,...summarize(r.samples,r.seconds)}));
  const observed=windows.filter(r=>Number.isFinite(r.continuity.underruns));
  const qualified=windows.filter(r=>r.continuity.pass&&!r.profile_error);
  const zeroPcm=observed.filter(r=>r.continuity.frames===0);
  const values=fn=>observed.length?stats(observed.map(fn)):null;
  return {attempted:windows.length,observed:observed.length,qualified:qualified.length,
    all_qualified:qualified.length===windows.length,windows,
    observed_only:{underruns:values(r=>r.continuity.underruns),
      ratio:values(r=>r.continuity.ratio),minimum_sampled_heap:values(r=>r.continuity.minHeap)},
    missing_windows:windows.filter(r=>!Number.isFinite(r.continuity.underruns)).map(r=>r.run),
    zero_pcm_windows:zeroPcm.map(r=>r.run),
    interpretation:'Observed counters include failed/stopped windows. Idle neutral DMA also increments underruns; zero-PCM windows are not decoder-speed measurements. No failures are removed.',
    invalid_timing_windows:windows.filter(r=>r.profile_error).map(r=>({run:r.run,error:r.profile_error}))};
}
function compareManifests(a,b) {
  assert.equal(a.opus_input_bytes,1024);assert.equal(b.opus_input_bytes,2048);
  for(const m of [a,b]) {
    assert.equal(m.diagnostic,true);assert.equal(m.opus_stream_test,true);
    assert.equal(m.opus_benchmark,false);assert.equal(m.opus_scratch_bytes,6144);
  }
  const allowed=['opus_input_bytes','config_sha256','app_sha256','bytes','built_utc'];
  for(const k of new Set([...Object.keys(a),...Object.keys(b)]))
    if(!allowed.includes(k))assert.deepEqual(b[k],a[k],`Unrelated build change: ${k}`);
}
function read(directory) {
  const parse=f=>JSON.parse(fs.readFileSync(path.join(directory,f),'utf8').replace(/^\uFEFF/,''));
  const manifest=parse('manifest.json'),app=fs.readFileSync(path.join(directory,'app.bin'));
  assert.equal(sha256(app),manifest.app_sha256.toLowerCase());assert.equal(app.length,manifest.bytes);
  const reports=[],inputs=[];
  for(let i=1;i<=10;i++) {
    const name=`run${i}.json`,text=fs.readFileSync(path.join(directory,name),'utf8');
    reports.push(JSON.parse(text));inputs.push({file:name,sha256_lf:sha256(Buffer.from(text.replace(/\r\n/g,'\n')))});
  }
  const config=fs.readFileSync(path.join(directory,'sdkconfig'),'utf8').replace(/\r\n/g,'\n');
  assert.equal(Number(config.match(/^CONFIG_YORADIO_OPUS_INPUT_BYTES=(\d+)$/m)?.[1]),manifest.opus_input_bytes);
  return {manifest,inputs,reports,config:config.replace(/^CONFIG_YORADIO_OPUS_INPUT_BYTES=\d+$/m,'CONFIG_YORADIO_OPUS_INPUT_BYTES=CAPACITY')};
}
function compareDirectories(reference,candidate,output) {
  const a=read(reference),b=read(candidate);compareManifests(a.manifest,b.manifest);
  assert.equal(a.config,b.config,'Unrelated sdkconfig difference');
  const result={scope:'Sequential live DLF24 broadcast, not identical audio content or isolated CPU A/B. Every attempted window retained.',
    reference:{manifest:a.manifest,inputs:a.inputs,...summarizeSeries(a.reports)},
    candidate:{manifest:b.manifest,inputs:b.inputs,...summarizeSeries(b.reports)}};
  fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({reference:result.reference.observed_only,candidate:result.candidate.observed_only,
    qualified:[result.reference.qualified,result.candidate.qualified],missing:[result.reference.missing_windows,result.candidate.missing_windows],
    zero_pcm:[result.reference.zero_pcm_windows,result.candidate.zero_pcm_windows]},null,2));
  return result;
}
module.exports={summarizeSeries,compareManifests,compareDirectories};
if(require.main===module){const [a,b,out]=process.argv.slice(2);assert.ok(a&&b&&out,'reference candidate output.json required');compareDirectories(a,b,out);}
