import datetime
import hashlib
import json
from pathlib import Path
import subprocess

root = Path.cwd()
out = root / '.build/cyd-flac-runtime-review-01'
out.mkdir(exist_ok=False)
sha = lambda data: hashlib.sha256(data).hexdigest()
revision = '985e96f7fa87af13af3315f043596df64ce2857d'
main = 'idf/esp32-cyd2usb-native/main/'
paths = [main + name for name in ['audio_service.c', 'decoder_registration.c',
    'Kconfig.projbuild', 'CMakeLists.txt', 'native_state.c', 'native_state.h',
    'native_audio_output.c', 'board_config.h']]
paths += ['idf/components/custom_flac/custom_flac_adapter.cpp',
          'idf/components/custom_flac/custom_flac_adapter.h',
          'idf/components/custom_flac/CMakeLists.txt',
          'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp',
          'yoRadio/src/audioI2S/flac_decoder/flac_decoder.h',
          'tests/run-cyd-flac-runtime.py',
          'tests/native/cyd_flac_runtime/task.c',
          'tests/native/cyd_flac_runtime/allocations.cpp',
          'tests/native/cyd_flac_runtime/registration.c',
          'docs/CYD_FLAC_TRANSFER_DESIGN.md']
inputs = {}
for name in paths:
    data = (root / name).read_bytes()
    target = out / 'current-sources' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    committed = subprocess.check_output(['git', 'show', revision + ':' + name], cwd=root)
    target = out / 'commit-sources' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(committed)
    inputs[name] = dict(current_sha256=sha(data), committed_sha256=sha(committed),
        current_equals_commit_ignoring_crlf=data.replace(b'\r\n', b'\n') == committed.replace(b'\r\n', b'\n'))
package = Path('C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec')
sdk_inputs = {}
for name in ['README.md', 'src/simple_decoder_reg.c', 'src/audio_decoder_reg.c',
             'include/simple_dec/esp_audio_simple_dec.h',
             'include/decoder/impl/esp_flac_dec.h']:
    data = (package / name).read_bytes()
    target = out / 'vendor-sources' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    sdk_inputs[name] = sha(data)
archive = root / 'tests/results/cyd-flac-runtime-20261019'
manifest = json.loads((archive / 'archive-manifest.json').read_text(encoding='utf-8'))
assert manifest['passed']
for name, entry in manifest['files'].items():
    data = (archive / name).read_bytes()
    assert sha(data) == entry['sha256'] and len(data) == entry['bytes'], name
qualification = json.loads((archive / 'qualification.json').read_text(encoding='utf-8'))
assert qualification['passed']
for name, expected in qualification['reports'].items():
    assert sha((archive / name).read_bytes()) == expected, name
host = json.loads((archive / 'host/report.json').read_text(encoding='utf-8'))
assert host['passed'] and host['exact_pcm_comparisons'] == 520
for name, expected in host['source_sha256'].items():
    assert sha((archive / 'host/sources' / name).read_bytes()) == expected, name
for name, expected in host['generated_sha256'].items():
    assert sha((archive / 'host' / name).read_bytes()) == expected, name
for mode in ['custom', 'vendor']:
    report = json.loads((archive / 'sdk' / mode / 'integration-compile.json').read_text(encoding='utf-8'))
    assert report['passed'] and all(unit['exit_code'] == 0 for unit in report['units'])
review = dict(
    read_only=True, target_commit=revision, captured_utc=datetime.datetime.now(datetime.UTC).isoformat(),
    scope='Code and recorded-evidence review; no new decoder execution, target ABI test or hardware test performed.',
    source_inputs=inputs, vendor_source_sha256=sdk_inputs,
    evidence_verified=dict(archive_files=len(manifest['files']), linked_reports=len(qualification['reports']),
        host_sources=len(host['source_sha256']), generated_fragments=len(host['generated_sha256']),
        recorded_exact_pcm_comparisons=520, recorded_lifecycle_groups=len(host['lifecycle'])),
    actionable_new_defects=[],
    conclusions=[
        'Custom callback preserves encoded 4-24-bit source depth separately from its explicitly checked PCM16 callback and queue layout.',
        'Actual production adapter/core entry points are confined to the one guarded decoder task; replacement, generation failure, terminal completion and maintenance release the singleton before successor use or ACK.',
        'Vendor selection remains Kconfig default. Actual simple_decoder_reg.c only registers selected containers and does not re-register the omitted vendor FLAC frame decoder.',
        'Pinned vendor public simple-dec info describes playback properties; vendor README advertises a broader source capability profile than this optional custom implementation.',
        'Host cancellation/maintenance schedules are scripted seams. Their claims do not imply that no stale generation packet can ever be committed between a successful acquire and queue completion; real output generation checks and producer ACK barriers own that cancellation boundary.',
        'Full application link/export, custom Xtensa PCM execution or QEMU, and physical CYD memory/stack/DMA/watchdog/performance qualification remain open as the existing design already states.',
        'Existing CRC/MD5, metadata/profile and mid-stream format limitations were not relabeled as new port regressions or full conformance.'
    ])
(out / 'review.json').write_text(json.dumps(review, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(new_actionable_defects=0, **review['evidence_verified']), indent=2))
