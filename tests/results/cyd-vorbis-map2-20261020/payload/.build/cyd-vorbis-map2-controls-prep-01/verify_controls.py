"""Pure source/identity checks; never invokes a compiler, codec or emulator."""
from pathlib import Path
import difflib
import hashlib
import json

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def body(data, start, end):
    a = data.index(start)
    return data[a:data.index(end, a)]


def main():
    facts = json.loads((P / 'controls.json').read_text())
    fixed = (P / 'fixed/vorbis_repair/setup.c').read_bytes()
    if sha(fixed) != facts['fixed_sha256']:
        raise ValueError('fixed source pin')
    functions = (
        (b'static int _make_words(', b'static int _make_decode_table('),
        (b'static int repair_vorbis_book_unpack(', b'static void repair_floor0_free_info('),
    )
    for name, row in facts['controls'].items():
        folder = P / 'controls' / name
        data = (folder / 'candidate/vorbis_repair/setup.c').read_bytes()
        if sha(data) != row['setup_sha256'] or len(data) != row['setup_bytes']:
            raise ValueError('control source pin: ' + name)
        a, b = fixed, data
        for start, end in functions:
            if start.decode().split('(')[0].split()[-1] != row['changed_function']:
                if body(a, start, end) != body(b, start, end):
                    raise ValueError('other function changed: ' + name)
            a = a.replace(body(a, start, end), start + b'<body>\n', 1)
            b = b.replace(body(b, start, end), start + b'<body>\n', 1)
        if a != b:
            raise ValueError('outside function changed: ' + name)
        if (b'Errata 20150226' in data) != (name != 'mapped-single-v1'):
            raise ValueError('single branch isolation: ' + name)
        if (b'Lookup 2 carries a full row' in data) != (name != 'packed-skip-v1'):
            raise ValueError('packed skip isolation: ' + name)
        if (b'Read all original rows' in data) != (name != 'wide-rows-v1'):
            raise ValueError('wide block isolation: ' + name)
        for rel in facts['modules']:
            if rel != 'vorbis_repair/setup.c' and (folder / 'candidate' / rel).read_bytes() != (P / 'fixed' / rel).read_bytes():
                raise ValueError('support module changed: ' + name + '/' + rel)
        for x, y, first, last, filename in (
            (fixed, data, 'fixed', name, 'fixed-to-control.patch'),
            (data, fixed, name, 'fixed', 'control-to-fixed.patch'),
        ):
            patch = ''.join(difflib.unified_diff(x.decode().splitlines(keepends=True),
                y.decode().splitlines(keepends=True), fromfile=first + '/vorbis_repair/setup.c',
                tofile=last + '/vorbis_repair/setup.c', n=3))
            if patch.encode() != (folder / filename).read_bytes():
                raise ValueError('directional patch differs: ' + name + '/' + filename)
    return {'status': 'SOURCE_CONTROL_PROJECTIONS_VERIFIED', 'controls': 3,
            'source_only': True, 'target_executed': False, 'control_effective': False}


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True))
