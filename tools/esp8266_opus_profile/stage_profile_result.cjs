const names=['off','SILK indices','SILK pulses','SILK parameters','SILK core','SILK resampler',
  'CELT energy (coarse/fine/final)','CELT allocation (TF/dynamic/static)','CELT bands/PVQ',
  'CELT synthesis','CELT postfilter','CELT deemphasis'];
function analyzeStage(status,item) {
  if(!status.profile_stage)return null;
  if(!Number.isInteger(status.profile_stage)||status.profile_stage<1||status.profile_stage>11||status.stage_clock_hz!==160000000)
    throw Error('Invalid Opus stage/clock metadata');
  for(const name of ['stage_cycles_lo','stage_cycles_hi','stage_calls','stage_max_cycles'])
    if(!Number.isSafeInteger(item[name])||item[name]<0)throw Error('Invalid '+name);
  if(item.stage_cycles_lo>0xffffffff||item.stage_cycles_hi>0xffffffff)throw Error('Invalid cycle word');
  const cycles=item.stage_cycles_hi*4294967296+item.stage_cycles_lo;
  if(!Number.isSafeInteger(cycles)||item.stage_max_cycles>cycles||(!item.stage_calls&&cycles))throw Error('Inconsistent stage counters');
  const us=cycles/(status.stage_clock_hz/1000000);
  return {name:names[status.profile_stage],wall_us:us,wall_percent_of_decode:item.wall_us?100*us/item.wall_us:null,
    max_wall_us:item.stage_max_cycles/(status.stage_clock_hz/1000000),
    warning:'Inclusive wall cycles with interrupts/preemption, NOT exclusive task CPU; no overhead subtracted'};
}
module.exports={analyzeStage,names};
