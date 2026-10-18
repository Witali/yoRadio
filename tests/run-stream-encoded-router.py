"""Exercise actual send_stream_audio and queue adapter with a bounded lease stub."""
import hashlib
import json
from pathlib import Path
import sys
from native_source import source_closure

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
main=ROOT/'idf/esp32c3-oled-native/main'
out=ROOT/'.build/stream-encoded-router';out.mkdir(parents=True,exist_ok=True)
source=main/'audio_service.c';harness=ROOT/'tests/native/stream_encoded_router_test.c'
text=source.read_text();start=text.index('static bool send_encoded(')
end=text.index('static void stream_bitrate_add(',start)
unit=out/'test.c';unit.write_text(harness.read_text().replace('/* PRODUCTION_SEND */',text[start:end]))
binary=out/'test'
(out/'build.log').write_bytes(run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror',
    '-fsanitize=address,undefined','-fno-pie','-no-pie','-I',host(main),host(unit),'-o',host(binary)]))
try:
    log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
        'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
except Exception as e:
    if hasattr(e,'output'):(out/'failure.log').write_bytes(e.output);print(e.output.decode())
    raise
(out/'run.log').write_bytes(log)
def fixture(folder,name):
    manifest=json.loads((folder/'manifest.json').read_text())
    entry=(manifest['files'][name] if 'files' in manifest else
           next(row for row in manifest['fixtures'] if row['file']==name))
    data=(folder/name).read_bytes();assert hashlib.sha256(data).hexdigest()==entry['sha256']
    while data[:3]==b'ID3':
        size=10+(data[6]<<21)+(data[7]<<14)+(data[8]<<7)+data[9]
        if data[3]==4 and data[5]&16:size+=10
        data=data[size:]
    return data
mp3=fixture(ROOT/'tests/fixtures/esp32c3_calibration','mp3-320.mp3')
aac=[fixture(ROOT/'tests/fixtures/aac_stream_format',name) for name in
     ('lc-48000-stereo.aac','he-48000-stereo.aac','hev2-44100-stereo.aac')]
segments=[mp3,*aac,mp3];expected=b''.join(segments)
tag=b'ID3\x04\0\0\0\0\0\0'
cases=[]
tail=b'TAG'+(b'ID3\xff\xfb\x90\x00\xff\xf1'*14)[:125].ljust(125,b'\0')
for variant, payload in (
    ('id3v2', tag.join(segments)),
    ('id3v1-tails', tag.join([mp3+tail,*aac,mp3+tail])),
):
    input_path=out/f'real-mixed-{variant}.bin';input_path.write_bytes(payload)
    for chunk in (1,7,2048):
        destination=out/f'replayed-{variant}-{chunk}.bin'
        result=run([host(binary),host(input_path),host(destination),str(chunk)])
        assert destination.read_bytes()==expected
        markers=[tuple(map(int,line.split()[1:])) for line in result.decode().splitlines() if line.startswith('MARKER ')]
        assert markers==[(len(mp3),1),(len(mp3)+sum(map(len,aac)),2)],markers
        (out/f'corpus-{variant}-{chunk}.log').write_bytes(result)
        cases.append(dict(variant=variant,chunk=chunk,result='PASS',bytes=len(expected),markers=markers,
                          input_sha256=hashlib.sha256(input_path.read_bytes()).hexdigest(),
                          replay_sha256=hashlib.sha256(expected).hexdigest()))
sources=[source,harness,Path(__file__).resolve()]+[main/name for name in
    ('stream_encoded_router.h','stream_frames.h','stream_tags.h','stream_probe.h','audio_completion.h')]
sources=source_closure(sources)
(out/'report.json').write_text(json.dumps(dict(passed=True,corpus=cases,
    scope='Actual send path and router; synthetic and real MP3/AAC-LC/HE/HEv2 bytes with bounded lease stubs, no decoder or hardware',
    source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')
print(log.decode(),end='')
print('PASS real mixed MP3/AAC-LC/HE-AAC/HE-AACv2 with ID3v2 and ID3v1 tails: exact bytes and two ordered drain markers, chunks 1/7/2048')
