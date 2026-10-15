"""Summarize finite DMA diagnostic history without hiding overwritten events."""
from production_health import COUNTER_MASK, output_window, validate_pipeline
from common import require


def analyze_pipeline(samples):
    output = output_window(samples)
    histogram = [0] * 8
    events = []
    previous = None
    frequency = None
    version = None
    for row in samples:
        probe = validate_pipeline(row.get('pipeline'), row['output'])
        require(frequency is None or frequency == probe['timer_hz'],
                'Diagnostic timer frequency changed')
        frequency = probe['timer_hz']
        require(version is None or version == probe.get('event_version', 1),
                'Diagnostic event version changed')
        version = probe.get('event_version', 1)
        if previous is not None:
            old_row, old = previous
            delta = (probe['sequence'] - old['sequence']) & COUNTER_MASK
            phases = [(new - before) & COUNTER_MASK
                      for new, before in zip(probe['phase_drops'], old['phase_drops'])]
            require(sum(phases) == delta, 'Inconsistent pipeline interval counts')
            histogram = [a+b for a,b in zip(histogram,phases)]
            retained = []
            for event in probe['events']:
                if 0 < ((event[0] - old['sequence']) & COUNTER_MASK) <= delta:
                    detail = dict(sequence=event[0], timestamp_us=event[1], phases=event[2],
                        observed_uptime_ms=[old_row['uptime_ms'],row['uptime_ms']],
                        ages_ms={name:ticks*1000/frequency for name,ticks in
                            zip(('output_checkpoint','pcm_packet','encoded_packet','http_read'),event[3:7])})
                    if version == 2:
                        detail['decoder_work'] = dict(feed_active=bool(event[7] & 1),
                            pcm_wait_active=bool(event[7] & 2), feed_elapsed_ms=event[8]/1000,
                            pcm_wait_elapsed_ms=event[9]/1000,
                            last_completed_batch_process_max_ms=event[10]/1000)
                    retained.append(detail)
            require(len(retained) <= delta, 'Too many diagnostic events')
            events.extend(retained)
        previous = row, probe
    require(sum(histogram) == output['completion_queue_drops'], 'Output/probe delta mismatch')
    result = dict(output=output, timer_hz=frequency, phase_drops=histogram,
                retained_events=len(events),
                overwritten_events=output['completion_queue_drops']-len(events), events=events,
                scope='ISR checkpoints; call phases are not scheduler states or analog samples')
    if version == 2:
        result.update(event_version=version, process_max_since_boot_ms=previous[1]['process_max_us']/1000)
        result['scope'] += '; feed spans include PCM callbacks; process durations exclude callbacks but include preemption, not CPU utilization'
    return result
