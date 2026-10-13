from pathlib import Path
root=Path(__file__).resolve().parent
source=(root/'physical_observed.py').read_text()
source=source.replace("OUT=ROOT/'physical-observed'", "OUT=ROOT/'physical-cold-control'")
source=source.replace("for variant in ('baseline','released'):", "for variant in ('baseline',):")
dest=root/'physical_cold_control.py';assert not dest.exists();dest.write_text(source)
