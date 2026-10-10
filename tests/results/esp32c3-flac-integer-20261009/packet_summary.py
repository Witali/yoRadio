"""Compare measured fixture frame sizes with encoded queue capacity."""
import json
from pathlib import Path
import statistics

root = Path(__file__).resolve().parent
packets = json.loads((root/'flac-packets.json').read_text())['packets']
sizes = [int(p['size']) for p in packets]
durations = [float(p['duration_time']) for p in packets]
result = dict(frames=len(packets), min_bytes=min(sizes), max_bytes=max(sizes),
    median_bytes=statistics.median(sizes), mean_bytes=statistics.mean(sizes),
    duration_seconds=sorted(set(durations)),
    queues={str(count): dict(encoded_capacity_bytes=count*2048,
        frames_larger_than_capacity=sum(size > count*2048 for size in sizes)) for count in (4,8)},
    note='Queue holds encoded input independently of the decoder frame window. Frame-size comparison is a scheduling/burst hypothesis, not proof that a whole frame must reside in the queue.')
(root/'packet-summary.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
