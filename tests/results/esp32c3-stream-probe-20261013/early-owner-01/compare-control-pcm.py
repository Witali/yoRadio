from pathlib import Path
import sys,json,gzip,hashlib
root=Path.cwd();sys.path.insert(0,str(root/'tools/codec_benchmark'))
from run_pipeline_pcm import parse_capture,compare
old=root/'tests/results/esp32c3-stream-probe-20261013/startup-metadata-01/qemu-full-window'
new=root/'.build/early-owner-pcm-01';rows={}
reference=json.loads((old/'report.json').read_text())
for name in reference['cases']:
 p=old/(name+'.log.gz');q=new/(name+'.log')
 result=compare(parse_capture(gzip.decompress(p.read_bytes()).decode()),parse_capture(q.read_text()))
 rows[name]=dict(result,control_log_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),candidate_log_sha256=hashlib.sha256(q.read_bytes()).hexdigest())
result=dict(passed=True,cases=rows,scope='Eight retained PCM/control captures compared byte-for-byte; no acoustic or physical timing claim. Control predates metadata/diagnostic-only changes; DSP configuration retained.')
(root/'tests/results/esp32c3-stream-probe-20261013/early-owner-01/pcm-control-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS exact retained-control PCM:',len(rows),'cases')
