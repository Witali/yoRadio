"""Prepare a listening image from the installed production source plus clock setup.

Run from the repository root. Never edit the live checkout or the shared SDK.
The saved production sdkconfig contains build options, not board NVS/settings.
"""
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

REPO = Path.cwd()
EVIDENCE = Path(__file__).resolve().parent
ROOT = REPO / '.build/c3-pdm-listening-20261010'
SOURCE = ROOT / 'source'
BASE = '8c1f2d2d2a2c75a0f2819ae32412a29a22cda23c'
BASE_IMAGE = REPO / 'firmware/development/esp32c3-idf-6.1-r9a97-production-qio80'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if ROOT.exists():
        raise RuntimeError('Use the retained prepared source; do not overwrite evidence')
    SOURCE.mkdir(parents=True)
    data = subprocess.check_output(['git', 'archive', BASE, '--',
        'idf/esp32c3-oled-native', 'idf/components', 'yoRadio', 'tools', 'playlist.csv'])
    original = {}
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            path = SOURCE / member.name
            if not path.resolve().is_relative_to(SOURCE.resolve()):
                raise ValueError('Archive path escapes source root')
            blob = archive.extractfile(member).read()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
            original[member.name] = sha(blob)
    patcher = Path('tools/patch_i2s_pdm_clock.py')
    for name in ('idf/esp32c3-oled-native/CMakeLists.txt',
                 'idf/esp32c3-oled-native/main/Kconfig.projbuild', patcher.as_posix()):
        shutil.copyfile(EVIDENCE / 'overlay' / name, SOURCE / name)
    build = ROOT / 'build'
    build.mkdir()
    config = (BASE_IMAGE / 'sdkconfig').read_text(encoding='utf-8')
    assert 'CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK=' not in config
    (build / 'sdkconfig').write_text(config.rstrip() + '\nCONFIG_YORADIO_PDM_FRACTIONAL_CLOCK=y\n', encoding='utf-8')
    changed = {}
    for name, digest in original.items():
        if sha((SOURCE / name).read_bytes()) != digest:
            changed[name] = sha((SOURCE / name).read_bytes())
    assert set(changed) == {'idf/esp32c3-oled-native/CMakeLists.txt',
                            'idf/esp32c3-oled-native/main/Kconfig.projbuild'}
    changed[patcher.as_posix()] = sha((SOURCE / patcher).read_bytes())
    manifest = dict(base_commit=BASE, original_source_sha256=original,
        changed_or_added_source_sha256=changed,
        base_config_sha256=sha((BASE_IMAGE / 'sdkconfig').read_bytes()),
        prepared_config_sha256=sha((build / 'sdkconfig').read_bytes()),
        audio_source_unchanged=True, codec_source_unchanged=True,
        purpose='Only fractional PDM clock setup differs from the installed source')
    (EVIDENCE / 'source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'source_files': len(original), 'overlays': list(changed), 'build': str(build)}, indent=2))


if __name__ == '__main__':
    main()
