"""Bind the final isolated raw PCM/control/configuration gates without rerunning them."""
from pathlib import Path
import hashlib
import json
import struct

root = Path.cwd()
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
output = root / '.build/cyd-vorbis-bridge-qualification-01'
output.mkdir(exist_ok=False)
reports = {}
for name in ('cyd-vorbis-raw-02', 'cyd-vorbis-raw-control-02', 'cyd-vorbis-config-02'):
    folder = root / '.build' / name
    path = folder / 'report.json'
    report = json.loads(path.read_bytes())
    assert report['passed'], name
    for source, value in report['inputs'].items():
        assert sha(source) == value['sha256'] == sha(folder / value['snapshot']), (name, source)
    assert all(sha(path) == digest for path, digest in report['tools'].items())
    if 'raw' in name:
        assert len(report['actual_module_rows']) == 3 and report['all_sources_current']
        assert all(sha(folder / path) == digest for path, digest in report['variant_sources'].items())
        bundle = report['execution_bundle']
        assert all(sha(folder / path) == digest for path, digest in bundle['generated'].items())
        assert sha(folder / 'qemu-flash.bin') == bundle['flash_sha256']
        description = json.loads((folder / 'build/project_description.json').read_bytes())
        elf = folder / 'build' / description['app_elf']
        assert sha(elf) == report['elf_sha256'] == bundle['elf_sha256']
        assert struct.unpack_from('<H', elf.read_bytes(), 18)[0] == 94
        assert report['canonical_bridge_sources'] and report['production_radio_integration'] is False
    else:
        assert len(report['cases']) == 21 and all(value['passed'] for value in report['cases'].values())
        assert not report['compiler_invoked'] and not report['runtime_invoked']
        assert all(sha(folder / path) == digest for path, digest in report['generated_inputs_before_cmake'].items())
    reports[name] = {'path': str(path), 'sha256': sha(path), 'inputs': len(report['inputs']), 'passed': True}
positive = json.loads((root / '.build/cyd-vorbis-raw-02/report.json').read_bytes())
control = json.loads((root / '.build/cyd-vorbis-raw-control-02/report.json').read_bytes())
assert positive['actual_result'] == ['535', '1602', '2112000']
assert control['exact_failure'] == 'rejected_dsp_unchanged' and control['actual_result'] is None
result = {'passed': True, 'qualification_scope': __doc__, 'reports': reports,
    'raw_audio_packets': 535, 'rejected_retries': 1602, 'per_packet_exact_pcm_bytes': 2112000,
    'exact_controls': {'skip-preflight': 'rejected_dsp_unchanged'}, 'cmake_profiles': 21,
    'canonical_source': True, 'current_bound_sources_tools_variants_elf_and_flash': True,
    'production_radio_integration': False, 'physical_tested': False,
    'pending': ['Ogg ownership/EOF/reset', 'allocation failures/lifetime', 'broader codebook/format coverage',
                'concurrent task-local scopes', 'all final callback bindings', 'actual audio-service integration',
                'full static analysis/application exports', 'physical resources/standards conformance']}
(output / 'report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
