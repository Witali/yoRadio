"""Pure exact binding identity with three explicitly same-byte helper relocations."""
from pathlib import Path

from pcm_metrics import need

RELOCATED_HELPERS = ('recorded_qualification.py', 'pins.json', 'carrier.py')


def verify_relocated_binding(saved, replayed, runtime, here, helper_hashes):
    need({k: v for k, v in saved.items() if k != 'proof_facts'} ==
         {k: v for k, v in replayed.items() if k != 'proof_facts'},
         'Complete mixed reference binding changed beyond declared helper paths')
    old, expected, observed = {}, {}, {}
    for row in saved['proof_facts']:
        path = str(Path(row['path']).resolve())
        need(path not in old and row['path'] == path, 'Distinct canonical original proof facts required')
        old[path] = row
    moves = {str((runtime / name).resolve()): str((here / name).resolve()) for name in RELOCATED_HELPERS}
    need(len(set(moves.values())) == 3 and not set(moves).intersection(moves.values()),
         'Exactly three distinct separate helper relocations required')
    for name in RELOCATED_HELPERS:
        row = old.get(str((runtime / name).resolve()))
        need(row is not None and row['sha256'] == helper_hashes[name], 'Exact old helper fact/hash required')
    for path, row in old.items():
        destination = moves.get(path, path)
        need(destination not in expected, 'Relocated helper fact collision')
        expected[destination] = dict(row, path=destination)
    for row in replayed['proof_facts']:
        path = str(Path(row['path']).resolve())
        need(path not in observed and row['path'] == path, 'Distinct canonical replay proof facts required')
        observed[path] = row
    need(observed == expected, 'Only three same-byte helper fact paths may relocate')
    return True
