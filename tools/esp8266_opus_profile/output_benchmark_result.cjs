// A completed diagnostic run is not necessarily continuous physical audio.
function analyzeOutput(item) {
  const fields = ['samples','output_samples','pipeline_wall_us','pipeline_task_us',
    'output_wall_us','dma_eofs','dma_misses','wall_us','packets','min_dram'];
  const errors = [];
  if (!item || fields.some(k => !Number.isSafeInteger(item[k]) || item[k] < 0))
    return {pass:false,errors:['missing or invalid physical-output counters']};
  const audio_us = item.output_samples * 1000000 / 48000;
  if (item.error !== 0) errors.push('decoder/output error');
  if (audio_us < 20000000 || item.pipeline_wall_us < 20000000) errors.push('window shorter than 20 seconds');
  if (!item.packets || item.output_samples !== item.samples) errors.push('PCM was not fully submitted');
  if (!item.dma_eofs) errors.push('DMA did not progress');
  if (item.dma_misses) errors.push('DMA underruns');
  const ratio = item.pipeline_wall_us ? audio_us / item.pipeline_wall_us : 0;
  if (ratio < 0.98 || ratio > 1.03) errors.push('PCM duration does not match elapsed time');
  if (item.pipeline_task_us > item.pipeline_wall_us) errors.push('invalid task runtime');
  return {pass:!errors.length,errors,audio_us,ratio,
    pipeline_cpu_budget_percent:audio_us ? item.pipeline_task_us * 100 / audio_us : null,
    pipeline_cpu_elapsed_percent:item.pipeline_wall_us ? item.pipeline_task_us * 100 / item.pipeline_wall_us : null,
    decode_wall_budget_percent:audio_us ? item.wall_us * 100 / audio_us : null,
    output_wall_budget_percent:audio_us ? item.output_wall_us * 100 / audio_us : null,
    timing:'pipeline task CPU includes flash copy/hash/output/ISR charged to task; output wall includes DMA waits; no audio network or Ogg demux'};
}
module.exports = {analyzeOutput};
