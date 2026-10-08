import json, re, statistics
from pathlib import Path
root = Path('.build/c3-idf-head-20261008')
summary = {}
for directory in ('physical/framing','physical/formats','physical/transitions','physical/public','soak/tls-alternate','mp3-followup/public-mp3'):
    p = root/directory
    if not (p/'performance.json').exists(): continue
    report = json.loads((p/'report.json').read_text())
    rows = json.loads((p/'performance.json').read_text())
    allocations = [r for r in rows if 'allocation failed' in r['line']]
    faults = [r for r in rows if re.search(r'allocation failed|decode (?:error|failed)|TLS failure:|PANIC|assert failed|CORRUPT HEAP|serial capture interrupted|watchdog|^ESP-ROM:|^rst:|^waiting for download',r['line'])]
    # Reboots requested by a test's restoration phase are deliberately retained
    # here; the original report applies phase-specific acceptance criteria.
    batches = json.loads((p/'status.json').read_text())
    summary[directory] = dict(
        cases=[{k:c[k] for k in ('name','result','reason','seconds','evidence') if k in c} for c in report['cases']],
        allocation_failures=len(allocations), all_phase_fault_lines=faults,
        status=[dict(case=b['case'],samples=len(b['samples']),
            duration=b['ended_at']-b['started_at'],interrupted=b.get('interrupted'),
            rssi_min=min((s['rssi'] for s in b['samples'] if 'rssi' in s),default=None),
            rssi_max=max((s['rssi'] for s in b['samples'] if 'rssi' in s),default=None)) for b in batches])
    phases=[]
    for b in batches:
        if b['case']=='settled-idle': continue
        cpu=[]
        for row in rows:
            if b['started_at'] <= row['at'] <= b['ended_at'] and 'PERF CPU:' in row['line']:
                f={k:float(v) for k,v in re.findall(r'(busy|heap|largest)=([\d.]+)',row['line'])}
                f['seconds']=row['at']-b['started_at'];cpu.append(f)
        if cpu:
            phases.append(dict(case=b['case'],windows=len(cpu),
                mean_busy=statistics.mean(v['busy'] for v in cpu),peak_busy=max(v['busy'] for v in cpu),
                minimum_heap=min(v['heap'] for v in cpu),minimum_largest=min(v['largest'] for v in cpu),
                first_three_medians={k:statistics.median(v[k] for v in cpu[:3]) for k in ('heap','largest')},
                last_three_medians={k:statistics.median(v[k] for v in cpu[-3:]) for k in ('heap','largest')}))
    summary[directory]['observed_cpu_including_startup']=phases
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:dict(cases=len(v['cases']),failed=[c['name'] for c in v['cases'] if c['result']!='PASS'],allocation_failures=v['allocation_failures']) for k,v in summary.items()},indent=2))
