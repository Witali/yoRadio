"""Validate frozen source/evidence references before loading shared analyzers."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
PRIOR = REPO/'tests/results/esp32c3-flac-input-growth-20261009'


def verify_references():
    refs = json.loads((ROOT/'references.json').read_text())
    for name, ref in refs.items():
        folder = (REPO/name).resolve()
        assert folder.is_relative_to(REPO)
        index = (folder/'index.json').read_bytes()
        assert hashlib.sha256(index).hexdigest() == ref['index_sha256'], name
        for name, expected in json.loads(index)['files'].items():
            path = (folder/name).resolve()
            assert path.is_relative_to(folder)
            blob = path.read_bytes()
            assert len(blob) == expected['bytes'], name
            assert hashlib.sha256(blob).hexdigest() == expected['sha256'], name
