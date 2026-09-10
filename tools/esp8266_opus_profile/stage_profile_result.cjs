const names=['off','SILK indices','SILK pulses','SILK parameters','SILK core','SILK resampler',
  'CELT energy (coarse/fine/final)','CELT allocation (TF/dynamic/static)','CELT bands/PVQ',
  'CELT synthesis','CELT postfilter','CELT deemphasis'];
function analyzeStage(status,item) {
  if(!status.profile_stage)return null;
  if(!Number.isInteger(status.profile_stage)||status.profile_stage<1||status.profile_stage>11||status.stage_clock_hz!==1000000)
    throw Error('Invalid Opus stage/clock metadata');
  for(const name of ['stage_ticks_lo','stage_ticks_hi','stage_calls','stage_max_ticks'])
    if(!Number.isSafeInteger(item[name])||item[name]<0)throw Error('Invalid '+name);
  if(item.stage_ticks_lo>0xffffffff||item.stage_ticks_hi>0xffffffff)throw Error('Invalid cycle word');
  const ticks=item.stage_ticks_hi*4294967296+item.stage_ticks_lo;
  if(!Number.isSafeInteger(ticks)||item.stage_max_ticks>ticks||(!item.stage_calls&&ticks))throw Error('Inconsistent stage counters');
  const us=ticks/(status.stage_clock_hz/1000000);
  if(!Number.isFinite(item.wall_us)||item.wall_us<0||us>item.wall_us+item.stage_calls ||
     (item.max_wall_us!==undefined && item.stage_max_ticks>item.max_wall_us+1))
    throw Error('Stage exceeds outer decode window: invalid clock or counter');
  return {name:names[status.profile_stage],wall_us:us,wall_percent_of_decode:item.wall_us?100*us/item.wall_us:null,
    max_wall_us:item.stage_max_ticks/(status.stage_clock_hz/1000000),
    warning:'Inclusive wall ticks with interrupts/preemption, NOT exclusive task CPU; no overhead subtracted'};
}
module.exports={analyzeStage,names};
