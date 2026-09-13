const assert=require('node:assert/strict');
// User priority: compare RELATIVE decode time, not CPU percentage-point deltas.
// This is only an experimental raw-codec performance gate, not live playback QA.
function selectHighBitrate(cases){
 const byName=new Map(cases.map(c=>[c.name,c]));
 const high=['stereo-128','stereo-192'],low=['mono-12','mono-24','stereo-64'];
 for(const name of [...low,...high]){
  const c=byName.get(name);assert.ok(c,'Missing bitrate '+name);
  assert.ok(Number.isFinite(c.median_task_reduction_percent));
  assert.ok(Number.isFinite(c.candidate.task_budget_percent.median));
 }
 const highGain=Math.min(...high.map(n=>byName.get(n).median_task_reduction_percent));
 const lowLoss=Math.max(0,...low.map(n=>-byName.get(n).median_task_reduction_percent));
 const budgetsOk=cases.every(c=>c.candidate.task_budget_percent.median<100);
 return {policy:'High bitrate relative time gains must exceed small lower-bitrate relative regressions; both 128/192 checked. Exactness/RAM checked separately.',
  minimum_high_bitrate_gain_percent:highGain,maximum_low_bitrate_slowdown_percent:lowLoss,
  all_median_raw_budgets_below_100:budgetsOk,accepted_for_experimental_asm:highGain>0&&highGain>lowLoss&&budgetsOk,
  target_192_cpu_at_most_70:byName.get('stereo-192').candidate.task_budget_percent.median<=70};
}
module.exports={selectHighBitrate};
