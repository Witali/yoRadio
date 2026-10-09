"""Reuse the established app-only OTA guard/restore controller."""
from pathlib import Path
import shutil
root = Path(__file__).resolve().parent
source = Path('tests/results/esp32c3-web-tcp-v2-20261009/physical.py').read_text()
source = source.replace('Continuous owner traces for expanded/control switching, EOF and TLS.', 'Matched integer-clock FLAC queue comparison with app-only OTA restoration.')
source = source.replace('.build/c3-web-tcp-v2-20261009', '.build/c3-flac-integer-20261009')
source = source.replace("paths={'probe':Path('firmware/development/esp32c3-idf-6.1-r9a97-web-tcp-v2/app.bin')}",
    "paths={str(n):Path(f'firmware/development/esp32c3-idf-6.1-r9a97-flac-integer{n}/app.bin') for n in (0,4)}")
source = source.replace("require(json.loads((ROOT/'build-audit.json').read_text())['result']=='PASS','Build unaudited')",
    "require(all(v['result']=='PASS' for v in json.loads((ROOT/'build-audit.json').read_text()).values()),'Build unaudited')")
source = source.replace('def run_trial(label,variant):', 'def run_trial(label,variant,aac=False):')
source = source.replace("started=time.monotonic();print('START',label,flush=True)",
    "if aac: command += ['--aac']\n    started=time.monotonic();print('START',label,flush=True)")
source = source.replace("require(report['cases'][0]['name']=='initial-idle-owner-capture' and report['cases'][0]['result']=='PASS','Owner probe failed to arm')",
    "require(report['cases'][0]['name']=='idle-before' and report['cases'][0]['result']=='PASS','Initial heap evidence missing')")
source = source.replace("install(paths[variant],'fractional',label)", "install(paths[variant],'integer',label)")
source = source.replace("for trial,variant in (('web-tcp-v2','probe'),):", "for trial,variant in (('control-before','0'),('expanded','4'),('control-after','0')):")
source = source.replace('run_trial(trial,variant)', "run_trial(trial,variant,aac=variant=='4')")
# Validate the real flash readback as well as the output divider on every boot.
source = source.replace('from pdm_clock import parse as parse_clock', 'from pdm_clock import parse as parse_clock\nfrom flash_mode import validate as validate_flash')
source = source.replace("return identity\n    finally:", "if capture:\n            save(label+'-flash.json',validate_flash('\\n'.join(r['line'] for r in capture.rows),image,'qio'))\n        return identity\n    finally:")
(root/'physical.py').write_text(source)
for name in ('ca.pem','server.pem'):
    shutil.copyfile(Path('.build/c3-switch-owner-20261009/trust')/name,root/name)
shutil.copyfile(Path('tests/results/esp32c3-flac-input-growth-20261009/flow_windows.py'),root/'flow_windows.py')
support = Path('tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py')
dest = root/'sources'/support
dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(support,dest)
