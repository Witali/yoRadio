"""Offline exact replay of the archived residue and coupling observations."""
import hashlib
import json
from pathlib import Path
import types
import zipfile

directory = Path(__file__).resolve().parent
manifest = json.loads((directory / 'manifest.json').read_bytes())
capture = directory / 'captures.zip'
assert hashlib.sha256(capture.read_bytes()).hexdigest() == manifest['zip_sha256']
with zipfile.ZipFile(capture) as archive:
    assert set(archive.namelist()) == set(manifest['files'])
    for name, pin in manifest['files'].items():
        body = archive.read(name)
        assert len(body) == pin['bytes'] and hashlib.sha256(body).hexdigest() == pin['sha256']
    def module(name, member):
        result = types.ModuleType(name)
        result.__file__ = str(directory / 'virtual' / member)
        exec(compile(archive.read(member), result.__file__, 'exec'), result.__dict__)
        return result
    oracle = module('archived_residue_oracle', 'host/sources/test-vorbis-residue.py')
    reference = archive.read('host/sources/reference-setup.py')
    assert hashlib.sha256(reference).hexdigest() == oracle.REFERENCE_SHA
    oracle.REFERENCE = module('archived_setup_reference', 'host/sources/reference-setup.py')
    model = json.loads(archive.read('host/cases.json'))
    inputs = archive.read('host/inputs.bin')
    assert oracle.decode_input(inputs) == model and oracle.encode_input(model) == inputs
    observed = oracle.decode_output(archive.read('host/outputs.bin'), model)
    checked = oracle.compare_all(model, observed['rows'])
    assert checked['passed'] and observed['metadata_controls'] == 37
    target_model = json.loads(archive.read('host/target-cases/cases.json'))
    expected = json.loads(archive.read('host/target-cases/expected.json'))
    targets = {}
    for target in ('esp32', 'esp32c3'):
        report = json.loads(archive.read(target + '/report.json'))
        assert report['completed'] and report['math_capture_completed']
        result = oracle.compare_target_rows(target_model, expected, report['rows'])
        assert result['passed']
        targets[target] = result['cases']
print(json.dumps({'passed': True, 'host_cases': checked['cases'], 'native_cases': targets,
                  'compiler_or_QEMU_executed': False, 'PCM_qualified': False}))
