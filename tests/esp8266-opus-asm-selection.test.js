const test=require('node:test'),assert=require('node:assert/strict');
const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs');
const values=(deltas,budgets=[23,55,65,80,90])=>['mono-12','mono-24','stereo-64','stereo-128','stereo-192'].map((name,i)=>({name,median_task_reduction_percent:deltas[i],candidate:{task_budget_percent:{median:budgets[i]}}}));
test('accepts smaller low-bitrate regressions when high-bitrate gains dominate',()=>{
 const a=selectHighBitrate(values([-.43,.15,-.63,2,2.37]));assert.equal(a.accepted_for_experimental_asm,true);assert.equal(a.target_192_cpu_at_most_70,false);
 assert.equal(a.maximum_low_bitrate_slowdown_percent,.63);
});
test('rejects high-bitrate slowdown, dominant low-bitrate loss and realtime budget failure',()=>{
 assert.equal(selectHighBitrate(values([0,0,0,1,-1])).accepted_for_experimental_asm,false);
 assert.equal(selectHighBitrate(values([0,0,-3,2,2.37])).accepted_for_experimental_asm,false);
 assert.equal(selectHighBitrate(values([0,0,0,2,3],[23,55,65,80,101])).accepted_for_experimental_asm,false);
 assert.throws(()=>selectHighBitrate([]));
});
