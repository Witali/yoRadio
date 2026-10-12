from pathlib import Path
root=Path(__file__).resolve().parent
base=Path('.build/c3-http-buffer-ota-soak/physical.py').read_text()
prefix=base[:base.index("with (OUT/'request-phases.jsonl')")]
prefix=prefix.replace('"""Candidate OTA regression and bounded HE-AAC HTTPS playback, with restoration."""', '"""Bounded public MP3 HTTP/HTTPS observations and independent host decoding."""')
prefix=prefix.replace('import json', 'import json\nimport subprocess')
prefix=prefix.replace('import ota\n','')
prefix=prefix.replace("reference_command=json.loads(Path('.build/c3-prefill1000-public-20261010/faad-reference-command.json').read_text())\n",'')
prefix=prefix.replace("source='https://ice5.somafm.com/groovesalad-64-aac'", "source='https://ice5.somafm.com/groovesalad-256-mp3'")
prefix=prefix.replace('progress(None,batch)', "progress(None,batch)\n                    if name.startswith('mp3:') and len(samples)>=5 and samples[-1]['seconds']>=15 and all(not s['audio'] for s in samples[-5:]):\n                        batch['stopped_early']=True\n                        break")
path=root/'physical.py';assert not path.exists();path.write_text(prefix+(root/'tail.txt').read_text())
