import json,statistics
from pathlib import Path
root=Path('.build/c3-production-radio-opus')
r=json.loads((root/'review.json').read_text());assert r['review']=='PASS' and r['restoration']
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-radio/manifest.json');manifest=json.loads(art.read_text())
manifest.update(opus_cycles_report='tests/results/esp32c3-production-radio-opus/review.json',opus_cycles=r['cycles'],production_qualified=False)
art.write_text(json.dumps(manifest,indent=2)+'\n')
recovery=json.loads((root/'physical/recovery.json').read_text())
med=lambda rows,k:statistics.median(v[k] for v in rows)
p=Path('docs/ESP32C3_HTTP_REQUEST_BUFFER.md');s=p.read_text(encoding='utf-8');heading='### Production Opus memory follow-up';assert heading not in s
lines=['',heading,'',
'The same production image ran three sequential AUTO Opus cycles on a',
'continuous 90-second synthetic 48 kHz stereo file (510 kbit/s CBR). FFmpeg',
'decoded the complete file without error before board testing. Each cycle',
'observed 60 seconds, using the unchanged 15-second warmup and memory gates.',
'After each Stop, idle recovery was measured against the initial idle window.',
'The final cycle additionally ran to EOF.','',
'| Cycle | First → last steady free-heap median, B | Minimum free / largest, B | Memory gate | Stop recovery |',
'|---|---:|---:|---|---|']
for name,c in r['cycles'].items():
    m=c['metrics'];lines.append(f"| {name.split(':')[-1]} | {m['heap']['first']:,} → {m['heap']['last']:,} | {m['heap']['minimum']:,} / {m['largest']['minimum']:,} | {c['checks']['memory']['result']} | {c['recovery']['result']} |")
lines+=['',
'All three cycles passed format, observation transport and steady output gates:',
'zero completion-queue increments and write errors. No allocation failures,',
'watchdog events or unexpected reboots were recorded. Final EOF passed.',
'Cycle 2 retains its **2,220-byte median decline**, exceeding the unchanged',
'2,048-byte threshold. This is not a fully passing memory qualification.',
'',
f"Initial → final idle heap medians: {med(recovery['initial'],'heap'):,.0f} → {med(recovery['final'],'heap'):,.0f} B; largest blocks: {med(recovery['initial'],'largest'):,.0f} → {med(recovery['final'],'largest'):,.0f} B.",
'The three cycles do not show accumulating post-stop memory loss. They do not',
'identify the owners responsible for active-playback fluctuations. Correlate',
'network receive queues and heap observations before attributing them to a',
'codec leak or changing the gate. The original short Opus failure also remains.',
'',
'Original firmware, station and settings were restored. The',
'[archive](../tests/results/esp32c3-production-radio-opus/) preserves the failed',
'gate, successful controls, fixture generation manifest and restoration.',
'`offline_replay.py` uses frozen test sources and reproduces the original review',
'without downloading or regenerating audio. Large fixture audio stays in `.build/`.','']
p.write_text(s+'\n'.join(lines),encoding='utf-8')
print('Saved Opus evidence and retained memory failure')
