"""Resolve immutable source bytes used by a historical measurement.

Current sources can evolve independently of old measurement records. Archived
bytes remain checked against the original record's SHA-256 by the caller.
"""
import hashlib


def historical_source(root, relative_path, expected_sha256):
    current = (root / relative_path).read_bytes()
    if hashlib.sha256(current).hexdigest() == expected_sha256:
        return current
    snapshot = root / 'tests/fixtures/historical_sources' / (expected_sha256 + '.txt')
    return snapshot.read_bytes() if snapshot.is_file() else current
