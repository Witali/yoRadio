"""Source-only terminal boundary revision; preserve prior source/check report."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    history = HERE / 'history01'
    history.mkdir(exist_ok=False)
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name != Path(__file__).name:
            (history / path.name).write_bytes(path.read_bytes())
    before = """need(terminal.get('schema') == 'direct-exec-tool-terminal-v1' and terminal.get('status') == 'TERMINAL' and
         type(terminal.get('exit_code')) is int and terminal['exit_code'] == 0 and
         type(terminal.get('session_id')) is int and terminal['session_id'] > 0 and terminal.get('chunk_id') and
         terminal.get('cwd') and terminal['report_sha256'] == sha(target_bytes) and
         terminal['original_entrypoint_sha256'] == RUNNER, 'Actual reviewed target outer terminal required')"""
    after = """need(terminal.get('schema') == 'direct-exec-tool-terminal-v1' and
         type(terminal.get('exit_code')) is int and terminal['exit_code'] == 0 and
         type(terminal.get('session_id')) is int and terminal['session_id'] > 0 and
         isinstance(terminal.get('terminal_chunk_id'), str) and terminal['terminal_chunk_id'] and
         terminal['report_sha256'] == sha(target_bytes) and terminal['entrypoint_sha256'] == RUNNER,
         'Actual reviewed target direct-tool terminal required; no invented outer argv/cwd/status')"""
    adapter = (HERE / 'compare_capture.py').read_bytes().decode()
    assert adapter.count(before) == 1
    adapter = adapter.replace(before, after, 1)
    ast.parse(adapter)
    (HERE / 'compare_capture.py').write_bytes(adapter.encode())
    relation = json.loads((HERE / 'source-relation.json').read_bytes())
    relation['allowed_edits'].append(dict(before=before, after=after))
    relation['adapter_proposed_sha256'] = sha(adapter.encode())
    (HERE / 'source-relation.json').write_bytes((json.dumps(relation, indent=2) + '\n').encode())
    original = (ROOT / '.build/cyd-vorbis-format-numeric-prep-01/compare_capture.py').read_bytes().decode()
    (HERE / 'adaptation.diff').write_bytes(''.join(difflib.unified_diff(original.splitlines(True), adapter.splitlines(True),
        fromfile='paired-numeric01/compare_capture.py', tofile='checked-numeric01/compare_capture.py')).encode())
    prepare = (HERE / 'prepare.py').read_bytes().decode()
    anchor = '    ]\n    new = old\n'
    assert prepare.count(anchor) == 1
    prepare = prepare.replace(anchor, '        (' + repr(before) + ',\n         ' + repr(after) + '),\n' + anchor, 1)
    ast.parse(prepare)
    (HERE / 'prepare.py').write_bytes(prepare.encode())
    pins = json.loads((HERE / 'source-pins.json').read_bytes())
    for name in ('report.json', '../cyd-vorbis-format-corpus-checked-acceptance-01-terminal.json'):
        path = (ROOT / '.build/cyd-vorbis-format-corpus-checked-acceptance-01' / name).resolve()
        raw = path.read_bytes()
        pins['local_source_inputs'].append(dict(path=path.relative_to(ROOT).as_posix(), bytes=len(raw), sha256=sha(raw)))
    pins['completed_target_metadata'] = dict(report_sha256='bdd5a9a3e76c2434db82c82896598947b70a985a197afcfbdce70eac7de28488',
        result='CHECKED_CORPUS_PCM_CAPTURED', terminal_session_id=45568, terminal_chunk_id='596431',
        actual_comparator_run=False, PCM_read_or_interpreted=False)
    (HERE / 'source-pins.json').write_bytes((json.dumps(pins, indent=2) + '\n').encode())
    # Keep the first actual source-only check receipt immutable in history01.
    (HERE / 'source-checks.json').unlink()
    print(json.dumps(dict(result='SOURCE_TERMINAL_BOUNDARY_REVISED',
        history_preserved=True, actual_comparator_run=False)))


if __name__ == '__main__':
    main()
