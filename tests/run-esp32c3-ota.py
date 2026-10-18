"""Compatibility entry point for the current shared/C3 OTA qualification.

The canonical runner includes the actual current C3 handler and shared image
sink/form/HTTP layer, with explicit acknowledged-audio and flash fault seams.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
def run(output):
    subprocess.run([sys.executable, str(root/'tests/run-native-ota-http.py'),
                    '--target', 'c3', '--output', str(output)], check=True)
if args.output:
    run(args.output)
else:
    with tempfile.TemporaryDirectory(prefix='yoradio-c3-ota-') as temporary:
        run(Path(temporary)/'evidence')
