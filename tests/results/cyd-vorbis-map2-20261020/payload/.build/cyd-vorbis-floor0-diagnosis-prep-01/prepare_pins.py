"""Read-only local source identity capture; never run the inspection proposal."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FIXTURE = '.build/cyd-vorbis-floor0-prep-01/generated01'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    output = HERE / 'source-pins.json'
    if output.exists():
        raise RuntimeError('Preserve frozen pins')
    paths = [
        'idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c',
        'idf/esp32-cyd2usb-native/main/vorbis_repair_abi.h',
        'tests/vorbis_format_corpus/generate_floor0.py',
        'tests/vorbis_format_corpus/generate_books.py',
        'tests/vorbis_block_matrix/generate_minimal.py',
        '.build/cyd-vorbis-format-corpus-checked-acceptance-01/sources/candidate/vorbis_repair/setup.c',
        '.build/cyd-vorbis-format-corpus-checked-acceptance-01/sources/candidate/vorbis_repair_abi.h',
        '.build/cyd-vorbis-format-corpus-checked-acceptance-01/report.json',
        '.build/cyd-vorbis-format-corpus-checked-acceptance-01-terminal.json',
        '.build/cyd-vorbis-format-checked-numeric-measurement-02/report.json',
        '.build/cyd-vorbis-format-corpus-qualified-01/qualification.json',
        FIXTURE + '/matrix.json', FIXTURE + '/construction-fields.json', FIXTURE + '/manifest.json',
    ]
    matrix = json.loads((ROOT / FIXTURE / 'matrix.json').read_bytes())
    for case in matrix['cases']:
        for key in ('identification', 'setup', 'comment', 'audio', 'packet_metadata'):
            paths.append(FIXTURE + '/' + case[key])
    rows = []
    for path in paths:
        raw = (ROOT / path).read_bytes()
        rows.append(dict(path=path, bytes=len(raw), sha256=sha(raw)))
    report = json.loads((ROOT / '.build/cyd-vorbis-format-checked-numeric-measurement-02/report.json').read_bytes())
    assert rows[9]['sha256'] == '80ec50711edd6463b0e3420293729e47f1adf26d29f7e61f1a959c4ffcb2f11c'
    assert report['measurement_completed'] is True and report['bounded_corpus_pcm_qualified'] is False
    assert rows[0]['sha256'] == rows[5]['sha256'] == '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
    assert rows[1]['sha256'] == rows[6]['sha256']
    sources = [dict(url='https://xiph.org/vorbis/doc/Vorbis_I_spec.html', revision='July4 2020',
        sections=['1.1.5-6', '1.2.4', '6.2.1-3', '9.2.2'], raw_bytes_snapshotted=False)]
    base = 'https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/'
    for name, blob, lines in (
        ('floor0.c', '864af70bdaf05d4e65ccde227a17277b675d592c', '47-59,113-278,284-350'),
        ('codebook.c', '35aaeff81ed884aa02cd9232747bb7d8db5ec5d2', '86-102,680-744,783-805'),
        ('codec_internal.h', '5dd059986a3cd34f77d870c7d52649b30ddd6da5', '64-72')):
        sources.append(dict(url=base + name, revision='0ad0141e864cfbb130db4f22e279d421832e7336',
            gitiles_reported_blob=blob, reviewed_lines=lines, raw_bytes_snapshotted=False))
    for name, lines in (('floor0.c', '68-94,102-129,148-200'), ('lsp.c', '228-257')):
        sources.append(dict(url='https://github.com/xiph/vorbis/blob/v1.3.7/lib/' + name,
            revision='v1.3.7', reviewed_lines=lines, raw_bytes_snapshotted=False))
    value = dict(schema='floor0-public-source-audit-inputs-v1', fixture_root=FIXTURE, local_inputs=rows,
        primary_sources=sources, numeric_report_metadata_only=True, actual_PCM_read_or_remeasured=False,
        fixture_inspection_proposal_executed=False, decoder_arithmetic_diagnosed=False,
        original_full17_bounded_NONPASS_preserved=True, policy_changed=False)
    with output.open('xb') as stream:
        stream.write((json.dumps(value, indent=2) + '\n').encode())
    for path in HERE.glob('*.py'):
        ast.parse(path.read_bytes())
    print(json.dumps(dict(result='SOURCE_PINS_PREPARED', local_inputs=len(rows), inspection_executed=False)))


if __name__ == '__main__':
    main()
