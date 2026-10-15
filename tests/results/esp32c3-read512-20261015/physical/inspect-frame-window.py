import hashlib,json,statistics
from pathlib import Path
base=Path('.build/c3-read512-20261015')
media=Path('.build/c3-input-tail-quiet-20261015/public-references/media/flac.flac')
packets=Path('tests/results/esp32c3-flac-tcp-20261015/flac-packets.json')
raw=media.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='920a6baa4f19ada7c8ed59383b22fa452612b555c9636c4f125ab798bebe2566'
assert raw[:4]==b'fLaC' and raw[4]&127==0 and int.from_bytes(raw[5:8],'big')==34
info=raw[8:42];maximum=int.from_bytes(info[7:10],'big')
rows=json.loads(packets.read_text())['packets'];sizes=[int(r['size']) for r in rows]
for row in rows:
    offset=int(row['pos']);assert raw[offset]==255 and raw[offset+1]&254==248
assert max(sizes)==maximum
extra=[maximum-size for size in sizes]
source=Path('idf/esp32c3-oled-native/components/custom_flac/custom_flac_adapter.cpp')
text=source.read_text()
assert 'decoder->input_size >= decoder->frame_window' in text
assert 'max_frame_size ? max_frame_size' in text
result=dict(reference_sha256=hashlib.sha256(raw).hexdigest(),packets_source=packets.as_posix(),
    packets_source_sha256=hashlib.sha256(packets.read_bytes()).hexdigest(),
    adapter_source=source.as_posix(),adapter_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    packets=len(rows),streaminfo_max_frame_bytes=maximum,
    actual_frame_bytes=dict(min=min(sizes),median=statistics.median(sizes),max=max(sizes)),
    additional_bytes_before_size_gate=dict(min=min(extra),median=statistics.median(extra),max=max(extra),
        frames_below_max=sum(n>0 for n in extra)),
    scope='Static complete-frame size comparison, excluding EOF gate bypass. No inference of actual stall duration or cause; the adapter cannot safely feed an incomplete frame to its stateful decoder and then treat truncation as retryable without further design.')
(base/'frame-window.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
