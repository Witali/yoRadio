"""Reuse the established app-only install/restore controller for isolated reboots."""
from pathlib import Path
root = Path(__file__).resolve().parent
previous = root.parent/'c3-min250-tls-ota-20261009/physical.py'
source = previous.read_text().replace('c3-min250-tls-ota-20261009','c3-reboot-tls-20261009')
start = source.index("    run_phase('framing'")
end = source.index("    save('settings-after-tests.json'",start)
source = source[:start]+'''    run_phase('reboot-control','tools/esp32c3_tests/reboot_tls.py',[
        *shared,*tls,'--cycles','3','--output',OUT/'reboot-control'],600)
'''+source[end:]
(root/'physical.py').write_text(source)
compile(source,str(root/'physical.py'),'exec')
print('Prepared three active/stopped pairs with application-only restoration')
