"""Execute the actual C3 custom-decoder branches with guarded ownership stubs."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run

folder=ROOT/'.build/codec-recovery/host'
folder.mkdir(parents=True,exist_ok=True)
audio=ROOT/'idf/esp32c3-oled-native/main/audio_service.c'
harness=ROOT/'tests/native/custom_decoder_terminal_test.c'
text=audio.read_text()
start=text.index('#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM\n        if (codec == NATIVE_CODEC_FLAC)')
end=text.index('        if (!decoder && !aac_decoder)',start)
unit=folder/'test.c'
unit.write_text(harness.read_text().replace('/* PRODUCTION_CUSTOM_BRANCHES */',text[start:end]))
binary=folder/'test'
(folder/'build.log').write_bytes(run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror',
    '-fsanitize=address,undefined','-fno-pie','-no-pie',host(unit),'-o',host(binary)]))
log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)])
(folder/'run.log').write_bytes(log)
assert b'PASS custom terminal ownership cases=17 queued PCM unchanged' in log
paths=[audio,harness,Path(__file__)]
for p in paths:
    target=folder/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(p.read_bytes())
(folder/'report.json').write_text(json.dumps(dict(passed=True,cases=17,
    source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    scope='Actual custom service branches with stub decoder callbacks; ownership and copied PCM, not DSP/physical timing'),indent=2)+'\n')
print(log.decode())
