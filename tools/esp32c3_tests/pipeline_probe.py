"""Summarize finite DMA diagnostic history without hiding overwritten events."""
from production_health import COUNTER_MASK, output_window, validate_pipeline
from common import require


def analyze_pipeline(samples):
    output = output_window(samples)
    histogram = [0] * 8
    events = []
    previous = None
    frequency = None
    for row in samples:
        probe = validate_pipeline(row.get('pipeline'), row['output'])
        require(frequency is None or frequency == probe['timer_hz'],
                'Diagnostic timer frequency changed')
        frequency = probe['timer_hz']
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
                    retained.append(dict(sequence=event[0], timestamp_us=event[1], phases=event[2],
                        observed_uptime_ms=[old_row['uptime_ms'],row['uptime_ms']],
                        ages_ms={name:ticks*1000/frequency for name,ticks in
                            zip(('output_checkpoint','pcm_packet','encoded_packet','http_read'),event[3:])}))
            require(len(retained) <= delta, 'Too many diagnostic events')
            events.extend(retained)
        previous = row, probe
    require(sum(histogram) == output['completion_queue_drops'], 'Output/probe delta mismatch')
    return dict(output=output, timer_hz=frequency, phase_drops=histogram,
                retained_events=len(events),
                overwritten_events=output['completion_queue_drops']-len(events), events=events,
                scope='ISR checkpoints; call phases are not scheduler states or analog samples')
