"""Save the isolated bridge and raw gate; leave radio registration unchanged."""
from pathlib import Path
import shutil

root = Path.cwd()
draft = root / '.build/cyd-vorbis-port-draft-01'
main = root / 'idf/esp32-cyd2usb-native/main'
for name in ('vorbis_repair/setup.c', 'vorbis_repair/simple.c', 'vorbis_repair/output.c',
             'vorbis_repair/COPYING', 'vorbis_repair_abi.h', 'compat/vorbis_repair/enable.cmake'):
    source = draft / 'candidate/main' / name
    dest = main / name
    assert not dest.exists(), dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    if name == 'vorbis_repair_abi.h':
        data = data.replace(b'// Private ESP32 Xtensa ABI of esp_audio_codec 2.6.2, checked against the pinned objects.',
            b'// ESP32 Xtensa bridge for pinned esp_audio_codec 2.6.2.\n// Field consumers and one raw fixture are checked; complete format/ABI coverage\n// and production integration remain separate qualification gates.')
    dest.write_bytes(data)
fixture = root / 'tests/target/cyd_vorbis_qemu'
assert not fixture.exists()
shutil.copytree(draft / 'project', fixture)
shutil.copyfile(draft / 'sdk-build.ps1', fixture / 'sdk-build.ps1')
runner = (draft / 'run_probe.py').read_text()
runner = runner.replace('from pathlib import Path', 'import argparse\nfrom pathlib import Path', 1)
runner = runner.replace("D = Path(__file__).resolve().parent\nROOT = D.parent.parent", "ROOT = Path(__file__).resolve().parents[1]\nMAIN = ROOT / 'idf/esp32-cyd2usb-native/main'\nHARNESS = ROOT / 'tests/target/cyd_vorbis_qemu'")
runner = runner.replace("OUT = D / 'raw-probe-02'\nOUT.mkdir(exist_ok=False)", "parser = argparse.ArgumentParser(description=__doc__)\nparser.add_argument('--output', type=Path, required=True)\nargs = parser.parse_args()\nOUT = args.output.resolve()\nif OUT == ROOT / '.build' or not OUT.is_relative_to((ROOT / '.build').resolve()):\n    parser.error('Use a fresh output strictly inside repository .build')\nOUT.mkdir(parents=True, exist_ok=False)")
start = runner.index("    for top in ('candidate', 'project'):")
end = runner.index("    fixture = ROOT / 'tests/fixtures", start)
runner = runner[:start] + '''    for name in ('vorbis_repair/setup.c', 'vorbis_repair/simple.c', 'vorbis_repair/output.c',
                 'vorbis_repair/COPYING', 'vorbis_repair_abi.h', 'compat/vorbis_repair/enable.cmake'):
        freeze(MAIN / name, Path('candidate/main') / name)
    for path in HARNESS.rglob('*'):
        if path.is_file() and path.name != 'sdk-build.ps1':
            freeze(path, Path('project') / path.relative_to(HARNESS))
    freeze(HARNESS / 'sdk-build.ps1', Path('helpers/sdk-build.ps1'))
    freeze(Path(__file__).resolve(), Path('helpers/run_probe.py'))
''' + runner[end:]
runner = runner.replace('Unapplied Xtensa Vorbis candidate: actual raw PCM and retry prototype gate.',
    'Isolated canonical Xtensa Vorbis bridge: raw PCM and retry gate. Radio integration, Ogg/OOM/format gates remain pending.')
runner = runner.replace("'production_integration': False", "'production_radio_integration': False, 'canonical_bridge_sources': True")
runner = runner.replace("def current():\n    return all(sha(name) == row['sha256'] == sha(OUT / row['snapshot']) for name, row in report['inputs'].items())", "def current():\n    return (all(sha(name) == row['sha256'] == sha(OUT / row['snapshot']) for name, row in report['inputs'].items())\n            and all(sha(path) == digest for path, digest in report['tools'].items()))")
runner = runner.replace("    from vorbis_packets import packets", "    freeze(ROOT / 'tools/codec_benchmark/vorbis_packets.py', Path('helpers/vorbis_packets.py'))\n    freeze(ROOT / 'tools/codec_benchmark/run_vorbis_lifecycle.py', Path('helpers/run_vorbis_lifecycle.py'))\n    from vorbis_packets import packets")
runner = runner.replace("Raw fixture PCM/retry prototype only; Ogg, OOM, broader formats, actual radio pipeline, guard controls and production integration are pending.",
    "Single raw fixture PCM/retry gate only; Ogg, OOM, broader formats, actual radio pipeline, exact controls and production integration are pending.")
dest = root / 'tests/run-cyd-vorbis-qemu.py'
assert not dest.exists()
dest.write_text(runner, encoding='utf-8')
print('Saved isolated canonical Vorbis bridge and raw gate; radio source/config unchanged')
