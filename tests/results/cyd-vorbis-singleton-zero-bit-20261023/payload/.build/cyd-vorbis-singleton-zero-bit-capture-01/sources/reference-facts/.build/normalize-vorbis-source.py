"""Normalize copied C source line endings and indentation, preserving tokens."""
from pathlib import Path
import re

base = Path.cwd() / 'idf/esp32-cyd2usb-native/main/vorbis_repair'
for name in ('setup.c', 'simple.c', 'output.c', 'COPYING'):
    path = base / name
    raw = path.read_bytes()
    text = raw.decode().replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
    lines = []
    for line in text.splitlines():
        prefix = re.match(r'[ \t]*', line)[0]
        lines.append((prefix.expandtabs(8) + line[len(prefix):]).rstrip(' \t'))
    clean = ('\n'.join(lines) + '\n').encode()
    # C tokens remain exactly identical modulo whitespace. These files contain
    # no multiline string literals; full source-bound gates run after this step.
    assert re.sub(rb'\s+', b'', raw) == re.sub(rb'\s+', b'', clean)
    path.write_bytes(clean)
    print('Normalized', name, len(raw), '->', len(clean))
