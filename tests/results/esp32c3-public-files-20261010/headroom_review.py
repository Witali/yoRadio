"""Explain the retained HE-AAC headroom case without changing its verdict."""
import collections, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
archive = Path('tests/results/esp32c3-quiet-health-20261010/physical/public')
health = json.loads((archive / 'health.json').read_text())
status = json.loads((archive / 'status.json').read_text())
batch = next(b for b in status if b['case'] == 'https:groovesalad-16-aac')
rows = [r for r in health if batch['started_at'] + 15 <= r['at'] <= batch['ended_at']]
low = [r for r in rows if r['largest'] < 8192]
paths = ['idf/esp32c3-oled-native/main/native_aac_decoder.c',
         'tests/native/esp32c3_aac_memory_test.c']
result = dict(original_case='https:groovesalad-16-aac', original_result='FAIL',
    original_budget_largest=8192, steady_samples=len(rows), below_budget_samples=len(low),
    below_budget_times_seconds=[r['at']-batch['started_at'] for r in low],
    largest_histogram=dict(collections.Counter(r['largest'] for r in rows)),
    minimum_heap=min(r['heap'] for r in rows),
    relevant_request=dict(function='native_aac_decoder.c:reserve_frame', maximum_bytes=8191,
        operation='realloc', same_capacity_reused=True,
        risk='May require a new contiguous block; in-place growth can sometimes succeed. This is not proof of an allocation failure.'),
    existing_test_scope='Host framing/allocator fault injection with a mocked codec and synthetic bytes; not valid large AAC audio on a memory-loaded board',
    next_test='Create a standards-valid frame-growth fixture, independently decode it, then test growth after HE-AAC has reached steady state with WebUI traffic.',
    invariants=['Retain AAC profile/rate/channel support', 'Do not discard queued or leased input',
                'Keep the original failed verdict and budget until allocation needs are verified'],
    sources={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},
    prior_evidence={str(archive/p):hashlib.sha256((archive/p).read_bytes()).hexdigest()
                    for p in ('status.json','health.json','report.json')})
(ROOT / 'headroom-review.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(dict(steady_samples=len(rows), below_budget_samples=len(low),
    interval_seconds=[round(low[0]['at']-batch['started_at'],3),round(low[-1]['at']-batch['started_at'],3)],
    minimum_largest=min(r['largest'] for r in rows), next_allocation_bound=8191)))
