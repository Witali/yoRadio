"""Preserve first comparison; create a fresh post-close verification run."""
from pathlib import Path

root=Path(__file__).resolve().parent
repo=next(p for p in root.parents if (p/'tools/esp32c3_tests/common.py').is_file())
source=(root/'trial-fixed.py').read_text()
needle="                case('owners-complete',owners)"
assert source.count(needle)==1
source=source.replace(needle,"                case('runtime-after-capture-close',lambda:no_runtime_faults(capture.rows))\n"+needle)
(root/'trial-final.py').write_text(source)
source=(root/'physical-fixed.py').read_text()
source=source.replace("OUT = ROOT/'physical-fixed'","OUT = ROOT/'physical-confirmed'")
source=source.replace('trial-fixed.py','trial-final.py')
source=source.replace("(('original-growth','before'),('retained-growth','after'))","(('retained-confirmed','after'),)")
(root/'physical-confirmed.py').write_text(source)
for name in ('tools/esp32c3_tests/serial_lines.py','tests/test-serial-telemetry.py'):
    target=root/'capture-sources'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes((repo/name).read_bytes())
for name in ('trial-final.py','physical-confirmed.py'):
    compile((root/name).read_text(),name,'exec')
