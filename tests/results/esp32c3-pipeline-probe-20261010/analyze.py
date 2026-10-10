import json,sys
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'test-sources/tools/esp32c3_tests'))
from pipeline_probe import analyze_pipeline
from sustained_output import sustained_window
health=json.loads((root/'physical-walltime/records/health.json').read_text())
batches=json.loads((root/'physical-walltime/records/status.json').read_text())
report=json.loads((root/'physical-walltime/records/report.json').read_text())
result={}
for batch in batches:
    name=batch['case']
    if name.startswith('idle:'):continue
    rows=[h for h in health if batch['started_at']<=h['at']<=batch['ended_at']]
    _,measured=sustained_window(batch['samples'],rows,report['seconds'])
    result[name]=analyze_pipeline(measured)
    compact={k:v for k,v in result[name].items() if k!='events'}
    if result[name]['events']:
        compact['age_ranges_ms']={key:[min(e['ages_ms'][key] for e in result[name]['events']),
                                      max(e['ages_ms'][key] for e in result[name]['events'])]
                                 for key in result[name]['events'][0]['ages_ms']}
    print(name,json.dumps(compact))
encoded=json.dumps(result,indent=2)+'\n'
path=root/'pipeline-analysis.json'
if path.exists():assert path.read_text()==encoded
else:path.write_text(encoded)
