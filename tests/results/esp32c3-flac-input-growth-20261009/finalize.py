"""Attach original results to saved laboratory artifacts without promoting them."""
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
restored=json.loads((ROOT/'physical/restoration.json').read_text())
assert restored['identity']['app_elf_sha256']=='54ec71b493261f3c00f86a649625c83e8c772b00eb2af5a3aae594c25e937094'
assert all(v is True for v in restored['persistence'].values())
for variant in ('0','4'):
    folder=Path(f'firmware/development/esp32c3-idf-6.1-r9a97-flac-input{variant}')
    path=folder/'manifest.json';m=json.loads(path.read_text())
    m.update(report='docs/ESP32C3_FLAC_INPUT_GROWTH_20261009.md',
        evidence='tests/results/esp32c3-flac-input-growth-20261009',
        measurement_source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        hardware_tested=True,physical_restoration_verified=True,
        qualification='Laboratory experiment only, default disabled. Full campaign 22/24 original entries pass; first control progressive-heap gate and candidate switching largest-block recovery fail. FLAC whole-observed DMA events 82/24/12 for extra slots 0/4/0; no repeatable continuity benefit established. Nine playback switches and four exact EOF cases pass; subsequent HE-AACv2 TLS record growth passes with zero DMA events but only 5632 B largest free block. Quiet firmware/private settings restored. Production and analog qualification remain open.')
    path.write_text(json.dumps(m,indent=2)+'\n')
    target=ROOT/'artifacts'/variant;target.mkdir(parents=True,exist_ok=True)
    for name in ('manifest.json','sdkconfig'):(target/name).write_bytes((folder/name).read_bytes())
print('Saved measured manifests; production qualification remains false')
