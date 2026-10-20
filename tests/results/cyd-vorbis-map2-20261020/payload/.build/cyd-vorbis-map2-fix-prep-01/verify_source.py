"""Read-only hash/projection check; does not compile or decode anything."""
from pathlib import Path
import difflib
import hashlib
import json

PREP = Path(__file__).resolve().parent
ROOT = PREP.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def outside(text):
    for start, end in (
        ('static int _make_words(', 'static int _make_decode_table('),
        ('static int repair_vorbis_book_unpack(', 'static void repair_floor0_free_info('),
    ):
        a = text.index(start)
        b = text.index(end, a)
        text = text[:a] + start + '<reviewed body>\n' + text[b:]
    return text


def verify():
    facts = json.loads((PREP / 'source-projection.json').read_text())
    readiness = json.loads((PREP / 'readiness.json').read_text())
    for rel, expected in readiness['files'].items():
        path = PREP / rel
        if digest(path) != expected['sha256'] or path.stat().st_size != expected['bytes']:
            raise ValueError('proposal drift: ' + rel)
    for rel, expected in readiness['external_inputs'].items():
        path = ROOT / rel
        if digest(path) != expected['sha256'] or path.stat().st_size != expected['bytes']:
            raise ValueError('external input drift: ' + rel)
    patch = []
    for name, row in facts['inputs'].items():
        rel = row['source']
        before = PREP / 'baseline' / rel
        after = PREP / 'candidate' / rel
        if digest(before) != row['baseline_sha256'] or digest(after) != row['candidate_sha256']:
            raise ValueError('projection pin drift: ' + name)
        if before.read_bytes() != (ROOT / rel).read_bytes():
            raise ValueError('canonical source differs from baseline: ' + name)
        a, b = before.read_text(), after.read_text()
        if outside(before.read_bytes().decode()) != outside(after.read_bytes().decode()):
            raise ValueError('change outside reviewed functions: ' + name)
        patch.extend(difflib.unified_diff(a.splitlines(keepends=True), b.splitlines(keepends=True),
                     fromfile='a/' + rel, tofile='b/' + rel, n=3))
    if ''.join(patch) != (PREP / 'setup-map2.patch').read_text():
        raise ValueError('patch differs from source copies')
    return {'status': 'SOURCE_PROJECTION_VERIFIED', 'platforms': len(facts['inputs']),
            'proposal_files': len(readiness['files']),
            'external_inputs': len(readiness['external_inputs']),
            'sdk_compiled': False, 'target_executed': False, 'numeric_qualification': False}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
