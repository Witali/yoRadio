const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {parseRun}=require('./summarize_rcpdm_simple_board');
const MODES=['pdm','production','simple-u4','feedback'];
const median=x=>{const a=[...x].sort((a,b)=>a-b),n=a.length;return n%2?a[n>>1]:(a[n/2-1]+a[n/2])/2;};
function summarize(directory) {
  const runs=[];
  for(const mode of MODES) for(const round of [1,2]) {
    const file=`round-${round}-${mode}-uart.log`;
    runs.push({file,round,...parseRun(fs.readFileSync(path.join(directory,file),'utf8'),mode)});
  }
  const summary={};
  for(const mode of MODES) {
    const rows=runs.filter(r=>r.mode===mode),times=rows.flatMap(r=>r.pack_us);
    assert.equal(new Set(rows.map(r=>r.checksum)).size,1,'Checksum changed across resets');
    summary[mode]={pack_us_median:median(times),pack_us_range:[Math.min(...times),Math.max(...times)],
      pack_us_per_sample:median(times)/48000,nonwait_us_per_audio_second:median(rows.map(r=>r.nonwait_us_per_audio_second)),
      nonwait_us_per_audio_second_range:[Math.min(...rows.map(r=>r.nonwait_us_per_audio_second)),Math.max(...rows.map(r=>r.nonwait_us_per_audio_second))],
      heap_free:rows.map(r=>r.heap.free),heap_min:rows.map(r=>r.heap.min_free),underruns:0,fifo_empty:0};
  }
  for(const mode of MODES.filter(m=>m!=='feedback')) {
    summary.feedback[`pack_change_vs_${mode}_percent`]=(summary.feedback.pack_us_median/summary[mode].pack_us_median-1)*100;
    summary.feedback[`nonwait_change_vs_${mode}_percent`]=(summary.feedback.nonwait_us_per_audio_second/summary[mode].nonwait_us_per_audio_second-1)*100;
  }
  return {note:'Physical CPU160/QIO40, 48k PCM/32-bit output. No Wi-Fi/codec/normalization. Nonwait excludes DMA wait, not total CPU utilization.',summary,runs};
}
module.exports={MODES,summarize};
if(require.main===module) console.log(JSON.stringify(summarize(process.argv[2]),null,2));
