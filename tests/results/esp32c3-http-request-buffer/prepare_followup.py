from pathlib import Path
root=Path(__file__).resolve().parent
source=(root/'physical.py').read_text()
source=source.replace("OUT=ROOT/'physical'", "OUT=ROOT/'physical-repeat'")
source=source.replace("states=suite.observe(60,name)", "try:\n                    states=suite.observe(60,name)\n                finally:\n                    (folder/'health.json').write_text(json.dumps(b.health_samples,indent=2)+'\\n')\n                    (folder/'server.json').write_text(json.dumps(server.events,indent=2)+'\\n')")
path=root/'physical_repeat.py'
assert not path.exists()
path.write_text(source)
