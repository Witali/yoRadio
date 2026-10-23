"""Prepare an unapplied Xtensa Vorbis candidate from the retained donor source."""
from pathlib import Path
import hashlib
import json

root = Path.cwd()
donor = root / 'idf/esp32c3-oled-native/main'
base = root / '.build/cyd-vorbis-port-draft-01'
candidate = base / 'candidate/main'
candidate.mkdir(parents=True, exist_ok=False)
identities = {}
for name in ('setup.c', 'simple.c', 'output.c', 'COPYING'):
    source = donor / 'vorbis_repair' / name
    data = source.read_bytes()
    identities[str(source)] = hashlib.sha256(data).hexdigest()
    text = data.decode().replace('pinned 2.6.2 RV32 objects', 'pinned 2.6.2 ESP32 Xtensa objects').replace('pinned RV32 Ogg ABI', 'pinned ESP32 Ogg ABI')
    target = candidate / 'vorbis_repair' / name
    target.parent.mkdir(exist_ok=True)
    target.write_text(text, encoding='utf-8')
source = donor / 'vorbis_repair_abi.h'
text = source.read_text().replace('Private RV32 ABI', 'Private ESP32 Xtensa ABI')
text = text.replace('#include <stdbool.h>', '#include "sdkconfig.h"\n#if !defined(CONFIG_IDF_TARGET_ESP32) || !CONFIG_IDF_TARGET_ESP32\n#error "The CYD Vorbis bridge requires the audited ESP32 target"\n#endif\n#include <stdbool.h>')
text = text.replace('VORBIS_ABI_SIZE(ogg_buffer, 16);', '_Static_assert(sizeof(void *) == 4 && sizeof(long) == 4, "ESP32 ILP32 ABI");\n_Static_assert(_Alignof(int64_t) == 8, "ESP32 int64 alignment");\n_Static_assert(_Alignof(ogg_packet) == 8, "ESP32 packet alignment");\n_Static_assert(_Alignof(vorbis_dsp_state) == 8, "ESP32 DSP alignment");\n_Static_assert(_Alignof(vorbis_wrapper) == 8, "ESP32 wrapper alignment");\nVORBIS_ABI_SIZE(ogg_buffer, 16);')
(candidate / 'vorbis_repair_abi.h').write_text(text, encoding='utf-8')
identities[str(source)] = hashlib.sha256(source.read_bytes()).hexdigest()
(base / 'donor-inputs.json').write_text(json.dumps(identities, indent=2) + '\n', encoding='utf-8')
print('Prepared unapplied candidate:', candidate)
