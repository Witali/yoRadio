import json,re
from pathlib import Path
from summarize import summarize

root=Path('.build/c3-flac-rice-20261008')
result=summarize(root)
assert result['restored']=='PASS'
assert result['phases_complete'] and len(result['cases'])==8
(root/'summary.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
for mode in ('control','bytewise'):
    cases=[case for case in result['cases'] if case['mode']==mode]
    artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-rice-'+mode)
    manifest=json.loads((artifact/'manifest.json').read_text())
    manifest['qualification']='NOT_QUALIFIED: physical Rice screening retained runtime/memory failures; bytewise reader remains default-off.'
    (artifact/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    qualification=dict(result='NOT_QUALIFIED',physical_tests=True,production_qualified=False,
        laboratory_only=True,case_count=len(cases),
        telemetry_complete=all(case['telemetry_complete'] for case in cases),
        original_gates_passed=all(case['original_gates_passed'] for case in cases),
        restored=result['restored'],evidence='tests/results/esp32c3-flac-rice-physical-20261008/summary.json',
        note='CPU informational. Original failures retained. No acoustic capture. Experimental Rice switch remains off.')
    (artifact/'qualification.json').write_bytes((json.dumps(qualification,indent=2)+'\n').encode())
for case in result['cases']:
    watchdog=[int(match[1]) for row in case['fault_rows']
              if (match:=re.search(r'events=(\d+)',row['line']))]
    print(json.dumps(dict(mode=case['mode'],case=case['case'],
        cpu=case['cpu']['busy_mean_percent'],decoder_cpu=case['cpu']['decode_mean_percent'],
        elapsed=case['elapsed_decode_ms_per_audio_second'],ratio=case['decoded_audio_wall_ratio'],
        dma=case.get('dma'),rssi=case['median_rssi'],heap=case.get('heap'),
        watchdog_values=watchdog,seconds=case['seconds'],
        interrupted=case['interrupted'],failures=[dict(name=row['name'],reason=row.get('reason'))
            for row in case['original_acceptance'] if row['result']!='PASS'])))
