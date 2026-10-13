from pathlib import Path
root=Path(__file__).resolve().parent
base=Path('.build/c3-http-request-buffer/physical_observed.py').read_text()
prefix=base[:base.index("with (OUT/'request-phases.jsonl')")]
prefix=prefix.replace("OUT=ROOT/'physical-observed'", "OUT=ROOT/'physical'")
prefix=prefix.replace("ROOT/'quiet-http-txrelease/build-audit.json'", "Path('.build/c3-http-request-buffer/quiet-http-txrelease/build-audit.json')")
prefix=prefix.replace('import json', 'import json\nimport ota')
prefix=prefix.replace("save('progress.json',dict(case=batch['case'],status=batch['samples'][-1]))", "save('progress.json',dict(case=batch['case'],status=batch['samples'][-1],health=b.health_samples[-1] if 'b' in globals() else None))")
tail=(root/'tail.txt').read_text()
dest=root/'physical.py';assert not dest.exists();dest.write_text(prefix+tail)
