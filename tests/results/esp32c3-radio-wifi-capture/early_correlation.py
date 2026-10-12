import json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from web_tcp import window
from heap_receive_correlation import paired_metrics
root=Path('.build/c3-radio-wifi-capture/physical');batches=json.loads((root/'status.json').read_text());rows=json.loads((root/'performance.json').read_text())
b=next(v for v in batches if v['case']=='opus:1')
try:
    w=window(rows,b['started_at'],b['ended_at']);print('Opus1 TCP qualified',len(w['events']),'events',len(w['wifi']),'Wi-Fi changes')
except ValueError as e:print('TCP unqualified',str(e))
p=paired_metrics(rows,b['started_at']+15,b['ended_at'])
print(json.dumps({k:v for k,v in p.items() if k not in ('samples','bins')},indent=2))
