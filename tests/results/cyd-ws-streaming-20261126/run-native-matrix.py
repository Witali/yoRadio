"""Collect all three unchanged strict controller verdicts, preserving NONPASS."""
import json
import hashlib
from pathlib import Path
import subprocess
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
SDK=Path('C:/Work/yoRadio/.idf/tools-v6.0.2/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin')
load=lambda p:json.loads(p.read_bytes())
def pin(path):
 body=path.read_bytes();return dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
for backend in ('legacy','pdm','continuous'):
 q=load(BASE/'target/sdk'/backend/'qualification.json')
 assert q['passed'] and q['source_commit']=='799f6787b152ef588b6f0c6c77195eca2eb4bdf0'
results=[]
for backend in ('legacy','pdm','continuous'):
 label='run-he-ws2-stream-01'
 child=subprocess.run([sys.executable,'-u','-B',str(BASE/'run-native.py'),backend,label])
 assert child.returncode==0,'Wrapper failed; raw evidence retained'
 run=BASE/'native'/backend/label
 folder=BASE/'target/sdk'/backend
 q=load(folder/'qualification.json')
 links=[path for path in folder.glob('link-qualification*.json')if pin(path)==q['linked_report']]
 assert len(links)==1 and load(links[0])['passed'],'Exact qualified linked proof required'
 command=[sys.executable,'-B',str(ROOT/'.build/cpbuf24/analyse-pbuf-native.py'),
  '--run',str(run),'--elf',str(folder/'compiled/yoradio_cyd2usb_native.elf'),
  '--addr2line',str(SDK/'xtensa-esp32-elf-addr2line.exe'),'--objdump',str(SDK/'xtensa-esp32-elf-objdump.exe'),
  '--link-report',str(links[0]),'--output',str(run/'pbuf-analysis.json')]
 with (run/'pbuf-analysis-terminal.log').open('xb') as log:
  parsed=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 assert parsed.returncode==0,'Attribution parser failed; evidence retained'
 report=load(run/'report.json'); pbuf=load(run/'pbuf-analysis.json')
 final=report.get('post_eof_health') or report.get('last_reachable_health') or {}
 row=dict(backend=backend,label=label,state=report['state'],reason=report.get('reason'),
  final_allocation_failures=final.get('allocation_failures'),minimum_heap=final.get('minimum_heap'),
  pbuf_prefix=pbuf['pbuf_pcm_flush_prefix'],pcm_sha256=report.get('pcm_sha256'),
  pcm_flushes=report.get('pcm_probe_flushes'),webui_after_eof=bool(report.get('web_asset_after_eof')),
  final_post_eof_health=bool(report.get('post_eof_health')))
 if report['passed']:
  assert report['state']=='TERMINAL_PASS' and row['final_allocation_failures']==0
  assert pbuf['attribution_available'] and row['pbuf_prefix']['total']==0
  assert row['pcm_sha256']=='44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362'
  assert row['pcm_flushes']==[dict(frames=614400,status=0)]
  assert row['webui_after_eof'] and row['final_post_eof_health']
 results.append(row)
 (BASE/'native-matrix-progress.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps(row),flush=True)
print(json.dumps(dict(all_passed=all(r['state']=='TERMINAL_PASS'for r in results),profiles=len(results))),flush=True)
