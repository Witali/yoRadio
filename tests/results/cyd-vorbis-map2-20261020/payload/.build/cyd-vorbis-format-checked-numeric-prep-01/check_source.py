"""AST/projection and failed-metadata gate checks only; no actual PCM read."""
import ast
import hashlib
import json
from pathlib import Path
import compare_capture as adapter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    output = HERE / 'source-checks.json'
    if output.exists():
        raise RuntimeError('Preserve source checks')
    for name in ('prepare.py', 'revise_terminal.py', 'pcm_metrics.py', 'compare_capture.py', 'check_source.py'):
        ast.parse((HERE / name).read_bytes())
    relation = json.loads((HERE / 'source-relation.json').read_bytes())
    core = (HERE / 'pcm_metrics.py').read_bytes()
    assert sha(core) == relation['core_sha256'] == 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
    assert core == (ROOT / relation['core_original_path']).read_bytes()
    current = (HERE / 'compare_capture.py').read_bytes()
    assert sha(current) == relation['adapter_proposed_sha256']
    projected = current.decode()
    for edit in reversed(relation['allowed_edits']):
        assert projected.count(edit['after']) == 1
        projected = projected.replace(edit['after'], edit['before'], 1)
    original = (ROOT / '.build/cyd-vorbis-format-numeric-prep-01/compare_capture.py').read_bytes()
    assert projected.encode() == original and sha(original) == relation['adapter_original_sha256']
    pins = json.loads((HERE / 'source-pins.json').read_bytes())
    for row in pins['local_source_inputs']:
        raw = (ROOT / row['path']).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    failed = json.loads((ROOT / '.build/cyd-vorbis-format-corpus-checked-baseline-02/report.json').read_bytes())
    assert failed['result'] == 'NONPASS'
    try:
        adapter.complete_capture(failed)  # Guard only: this function performs no file access or PCM parsing.
    except RuntimeError:
        pass
    else:
        raise AssertionError('Failed baseline metadata accepted')
    target_root = ROOT / '.build/cyd-vorbis-format-corpus-checked-acceptance-01'
    target_raw = (target_root / 'report.json').read_bytes()
    complete = json.loads(target_raw)
    adapter.complete_capture(complete)  # Metadata gate only; no run/main or PCM access.
    terminal = json.loads((ROOT / '.build/cyd-vorbis-format-corpus-checked-acceptance-01-terminal.json').read_bytes())
    assert terminal['schema'] == 'direct-exec-tool-terminal-v1'
    assert terminal['session_id'] == 45568 and terminal['terminal_chunk_id'] == '596431' and terminal['exit_code'] == 0
    assert terminal['report_sha256'] == sha(target_raw) == pins['completed_target_metadata']['report_sha256']
    assert terminal['entrypoint_sha256'] == adapter.RUNNER
    text = current.decode()
    assert text.index('complete_capture(target)') < text.index("inputs.read('target/pcm/")
    assert text.index('complete_capture(target)') < text.index('wav_pcm(wav,')
    assert adapter.CONTRACT_FILE == pins['expected_capture']['contract_file_sha256']
    assert adapter.DATA_HEADER == pins['expected_capture']['data_header_sha256']
    assert "observed['paired_packets']" not in text and "observed['decoded_packets'] == 238" in text
    assert "terminal['terminal_chunk_id']" in text and "terminal['entrypoint_sha256'] == RUNNER" in text
    files = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in sorted(HERE.iterdir()) if p.is_file()}
    result = dict(result='SOURCE_ONLY_READY', python_ast_files=5, core_byte_identical=True,
        adapter_reverse_projection_exact=True, failed_baseline02_metadata_rejected_without_PCM=True,
        acceptance17_metadata_gate_accepted_without_PCM=True, actual_minimal_terminal_schema_bound=True,
        complete_gate_precedes_PCM_reads=True, files=files, actual_comparator_run=False,
        actual_PCM_read_or_interpreted=False, qualification_executed=False,
        SDK_compiler_QEMU_decoder_reference_Git_or_device_invoked=False, historical_campaigns_modified=False)
    raw = (json.dumps(result, indent=2) + '\n').encode()
    with output.open('xb') as stream:
        stream.write(raw)
    print(json.dumps(dict(result=result['result'], source_checks_sha256=sha(raw), actual_comparator_run=False,
                         failed_baseline02_metadata_rejected_without_PCM=True)))


if __name__ == '__main__':
    main()
