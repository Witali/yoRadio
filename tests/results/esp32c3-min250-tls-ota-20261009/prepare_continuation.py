"""Continue unrun phases in a separate capture; preserve the aborted campaign."""
from pathlib import Path
root = Path(__file__).resolve().parent
source = (root/'physical.py').read_text()
source = source.replace("OUT = ROOT/'physical'", "OUT = ROOT/'continuation'")
start = source.index("    run_phase('framing'")
end = source.index("    run_phase('eof-https-all'",start)
source = source[:start]+source[end:]
source = source.replace("attempted=False\ntry:",
    "from failure_monitor import FailureMonitor\nmonitor=FailureMonitor(OUT)\nattempted=False\ntry:")
# Nest the entire hardware try/finally so monitoring always stops, even if restoration fails.
start = source.index('attempted=False\ntry:')
source = source[:start]+'try:\n'+''.join('    '+line+'\n' for line in source[start:].splitlines())+'finally:\n    monitor.close()\n'
(root/'continue_physical.py').write_text(source)
compile(source,str(root/'continue_physical.py'),'exec')
print('Prepared continuation: exact HTTPS EOF, OTA, then growing TLS records')
