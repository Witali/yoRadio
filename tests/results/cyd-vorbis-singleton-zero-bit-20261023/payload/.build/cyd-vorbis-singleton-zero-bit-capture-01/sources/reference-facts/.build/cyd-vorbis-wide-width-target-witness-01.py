"""Compare complete persisted target PCM; no codec or causal attribution."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent


def fact(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def load(folder, expected):
    report = ROOT / '.build' / folder / 'report.json'
    assert fact(report)['sha256'] == expected
    value = json.loads(report.read_bytes())
    assert value['completed'] and value['checked_decode_completed']
    assert all(row['exit_status'] == 0 and not row['timed_out'] and not row['interrupted'] for row in value['commands'])
    outputs = []
    for row in value['observed_pcm']:
        path = report.parent / row['path'].replace('\\', '/')
        f = fact(path)
        assert (f['bytes'], f['sha256']) == (row['bytes'], row['sha256'])
        outputs.append((row, path.read_bytes(), f))
    return fact(report), outputs


def main():
    previous, old = load('cyd-vorbis-format-expanded31-capture-01',
        '6f7f346df8c2185776fa8727977e363c284f8bdc459ef90c5ed28affc3b6d81d')
    current, new = load('cyd-vorbis-wide-width-capture-01',
        '7913274b872d5748ed50952e269a85b16a66929b6827824badb7a6a8524653ba')
    assert len(old) == 31 and len(new) == 12
    prefix = []
    for i in range(4):
        a, b = old[i + 8], new[i]
        assert a[0]['id'] == b[0]['id'] and a[2]['bytes'] == b[2]['bytes']
        prefix.append(dict(id=b[0]['id'], previous=a[2], current=b[2], pcm_equal=a[1] == b[1]))
    matrix_path = ROOT / '.build/cyd-vorbis-wide-width-generated-01/comparison12/matrix.json'
    matrix = json.loads(matrix_path.read_bytes())
    assert [row[0]['id'] for row in new] == [case['id'] for case in matrix['cases']]
    by_id = {row[0]['id']: row for row in new}
    groups = []
    for names in matrix['expected_same_decoder_pcm_equal_groups']:
        rows = [by_id[name] for name in names]
        assert len(rows) == 3 and len({row[2]['bytes'] for row in rows}) == 1
        groups.append(dict(cases=names, inputs=[row[2] for row in rows],
                           pcm_equal=all(row[1] == rows[0][1] for row in rows[1:])))
    result = dict(schema='wide-width-complete-target-PCM-relations-v1', source=fact(Path(__file__)),
        completed=True, previous=previous, current=current, matrix=fact(matrix_path),
        original_four_context_comparisons=prefix, declared_three_width_groups=groups,
        target_inputs_executed_by_this_witness=False, vendor_cause_attributed=False,
        numeric_reference_compared=False, full_G6_qualified=False)
    out = ROOT / '.build/cyd-vorbis-wide-width-target-witness-01.json'
    with out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(original_four_PCM_equal=[row['pcm_equal'] for row in prefix],
                         width_triples_equal=[row['pcm_equal'] for row in groups], report=fact(out))))


if __name__ == '__main__':
    main()
