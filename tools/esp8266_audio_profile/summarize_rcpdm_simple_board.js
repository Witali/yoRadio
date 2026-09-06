const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const median=values=>{const a=[...values].sort((x,y)=>x-y),i=Math.floor(a.length/2);return a.length%2?a[i]:(a[i-1]+a[i])/2;};
function parseRun(text,mode) {
  assert.ok(['production','simple'].includes(mode));
  assert.match(text,/audio_output_bench: complete/); assert.match(text,/stalled producer.*PASS/);
  assert.doesNotMatch(text,/invalid=[1-9]|PCM write failed|bit-exact FAIL|stalled producer.*FAIL/);
  const label=mode==='simple'?'RCPDM-Simple':'RCPDM';
  assert.ok(text.includes(`${label} bit-exact PASS: 493216 words and states`));
  assert.ok(text.includes(`${label} batch bit-exact PASS: 2144 words`));
  const fields=prefix=>{
    const line=text.split(/\r?\n/).find(s=>s.includes(`audio_output_bench: ${prefix}`));
    assert.ok(line,`Missing ${prefix}`);
    return Object.fromEntries([...line.matchAll(/(\w+)=(\d+(?:\.\d+)?)/g)].map(m=>[m[1],Number(m[2])]));
  };
  const packed=[...text.matchAll(/pack_only round=(\d+) samples=(\d+) elapsed=(\d+) us checksum=([0-9a-f]+) DMA=off/g)];
  assert.equal(packed.length,3); assert.equal(new Set(packed.map(m=>m[4])).size,1);
  packed.forEach(m=>assert.equal(Number(m[2]),48000));
  const result=fields('result '),wait=fields('spi_wait='),active=fields('producer_nonwait='),dma=fields('dma ');
  assert.ok(result.audio>0 && result.wall>0 && result.write>=wait.spi_wait);
  assert.equal(result.write-wait.spi_wait,active.producer_nonwait);
  for(const key of ['partial_start','blocked_partial','fifo_empty']) assert.equal(dma[key],0);
  const underruns=fields('spi_gap ').empty; assert.equal(underruns,0);
  return {mode,pack_us:packed.map(m=>Number(m[3])),checksum:packed[0][4],result,wait,dma,underruns,
    nonwait_us_per_audio_second:active.producer_nonwait*1e6/result.audio,heap:fields('heap ')};
}
function summarize(directory) {
  const runs=[];
  for(const file of fs.readdirSync(directory).sort()) {
    const match=file.match(/^round-(\d+)-(production|simple)-uart\.log$/); if(!match) continue;
    runs.push({file,round:Number(match[1]),...parseRun(fs.readFileSync(path.join(directory,file),'utf8'),match[2])});
  }
  const summary={};
  for(const mode of ['production','simple']) {
    const selected=runs.filter(r=>r.mode===mode); assert.equal(selected.length,2,'Need exactly two valid runs per mode');
    assert.equal(new Set(selected.map(r=>r.checksum)).size,1,'Checksum changed across resets');
    const times=selected.flatMap(r=>r.pack_us);
    summary[mode]={runs:selected.length,pack_us_median:median(times),pack_us_range:[Math.min(...times),Math.max(...times)],
      microseconds_per_sample:median(times)/48000,
      nonwait_us_per_audio_second:median(selected.map(r=>r.nonwait_us_per_audio_second)),
      heap_free:selected.map(r=>r.heap.free),heap_min:selected.map(r=>r.heap.min_free),underruns:0,fifo_empty:0};
  }
  summary.simple_pack_change_percent=(summary.simple.pack_us_median/summary.production.pack_us_median-1)*100;
  summary.simple_nonwait_change_percent=(summary.simple.nonwait_us_per_audio_second/summary.production.nonwait_us_per_audio_second-1)*100;
  return {note:'48k PCM; no Wi-Fi or codecs. Nonwait is write minus DMA wait, not total CPU utilization.',summary,runs};
}
module.exports={parseRun,summarize};
if(require.main===module) console.log(JSON.stringify(summarize(process.argv[2]),null,2));
