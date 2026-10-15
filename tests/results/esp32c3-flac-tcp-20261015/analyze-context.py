import hashlib,json
from pathlib import Path
base=Path('.build/c3-flac-tcp-20261015')
prior=Path('tests/results/esp32c3-flac-input12-20261015/matched')
result=dict(scope='Host write timing is not TCP acknowledgement or board-consumption timing',prior=[])
for variant in ('slots8','slots11'):
    r=json.loads((prior/variant/'pauses/report.json').read_text())
    e=r['server_events'][0];started=e['delivery']['started_at']
    windows=[]
    for w in e['delivery']['windows']:
        begin=w['started_at']-started;end=w['ended_at']-started
        if not 12<begin<29:continue
        duration=w['ended_at']-w['started_at']
        windows.append(dict(start_seconds=begin,end_seconds=end,bytes=w['bytes'],
            bytes_per_second=w['bytes']/duration,write_seconds=w['write_seconds'],
            outside_write_seconds=duration-w['write_seconds'],max_write_seconds=w['max_write_seconds']))
    result['prior'].append(dict(variant=variant,source=(prior/variant/'pauses/report.json').as_posix(),windows=windows))
p=json.loads((base/'flac-packets.json').read_text())['packets']
data=Path('.build/c3-input-tail-quiet-20261015/public-references/media/flac.flac').read_bytes()
source=Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_http_client/esp_http_client.c')
text=source.read_text();begin=text.index('int esp_http_client_read(');end=text.index('\nesp_err_t esp_http_client_perform(',begin)
(base/'physical/esp_http_client_read.txt').write_text(text[:text.index('*/')+2]+'\n\n'+text[begin:end]+'\n')
result.update(flac=dict(sha256=hashlib.sha256(data).hexdigest(),packets=len(p),
    durations={v:sum(x['duration_time']==v for x in p) for v in sorted({x['duration_time'] for x in p})},
    min_encoded_frame_bytes=min(int(x['size']) for x in p),max_encoded_frame_bytes=max(int(x['size']) for x in p)),
    idf_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    firmware_read_request_bytes=2048,firmware_read_timeout_ms=250,
    interpretation='Blocking read fills requested length or returns partial bytes on timeout/EOF/error. Candidate latency mechanism, not yet shown to cause the quiet FLAC fault.')
(base/'physical/context.json').write_text(json.dumps(result,indent=2)+'\n')
print('Saved host wait accounting and pinned HTTP-read source evidence')
