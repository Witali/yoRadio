from pathlib import Path
root=Path(__file__).resolve().parent
source=Path('.build/c3-http-request-buffer/physical_observed.py').read_text()
source=source.replace("OUT=ROOT/'physical-observed'", "OUT=ROOT/'vorbis-physical'")
source=source.replace("ROOT/'quiet-http-txrelease/build-audit.json'", "Path('.build/c3-http-request-buffer/quiet-http-txrelease/build-audit.json')")
source=source.replace('specs=fixtures()', "specs=fixtures(ROOT/'vorbis-stress/manifest.json')")
source=source.replace("for local in (True,False):", "for local in (True,):")
source=source.replace("':local-he'", "':vorbis'")
source=source.replace("specs['he-44100-stereo']", "specs['stress-vorbis-48000-2ch-16bit-90s']")
source=source.replace('http://192.168.100.253:8772/stream/he-44100-stereo', 'http://192.168.100.253:8772/file/stress-vorbis-48000-2ch-16bit-90s')
assert 'for local in (True,False)' not in source
dest=root/'vorbis.py';assert not dest.exists();dest.write_text(source)
