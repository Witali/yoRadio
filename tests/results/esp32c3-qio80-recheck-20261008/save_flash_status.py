"""Retain only the public Flash status values from private esptool logs."""
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parent
values = {}
for label in ('before', 'after'):
    text = (root / 'private' / ('flash-status-' + label + '.log')).read_text()
    matches = re.findall(r'^Flash memory status: (0x[0-9a-fA-F]+)$', text, re.M)
    if len(matches) != 1:
        raise ValueError('Expected one successful Flash status read: ' + label)
    values[label] = int(matches[0], 16)
(root / 'physical/flash-status-restoration.json').write_text(
    json.dumps(values, indent=2) + '\n')
print('Flash status before/after:', *(hex(values[key]) for key in ('before', 'after')))
