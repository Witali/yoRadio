"""Bracket host pauses with actual DMA samples; no inferred packet-arrival times."""
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'sources/tools/esp32c3_tests'))
from common import require
from staged_dma import parse, summarize

EXPECTED = [dict(after_bytes=3000000*(i+1), seconds=(.05,.10,.20)[i%3]) for i in range(6)]

def analyze(folder):
    report = json.loads((folder/'report.json').read_text())
    batch = next(b for b in json.loads((folder/'status.json').read_text()) if b['case'].startswith('load:stress-flac'))
    rows = json.loads((folder/'performance.json').read_text())
    selected = [e for e in report.get('server_events', []) if e.get('fixture')=='stress-flac-48000-2ch-16bit-610s']
    require(len(selected)==1, 'Exactly one FLAC response needed')
    event = selected[0]
    require(event.get('pause_schedule')==EXPECTED, 'Unexpected schedule')
    pauses = event.get('pauses', [])
    require(len(pauses)==6, 'Incomplete pause schedule')
    require(event.get('send_buffer_requested')==4096 and 0<event.get('send_buffer_actual',0)<=8192, 'Wrong send buffer')
    delivery = event['delivery']
    require(delivery['finished'] and not delivery['dropped_windows'], 'Incomplete host delivery')
    whole_dma = summarize(rows, batch['started_at'], batch['ended_at'])
    require(whole_dma['coverage_complete'], 'Incomplete FLAC DMA observation window')
    points = [v for r in rows if (v:=parse(r)) is not None and batch['started_at']<=v['at']<=batch['ended_at']]
    events = []
    for pause, expected in zip(pauses, EXPECTED):
        require(pause['after_bytes']==expected['after_bytes'] and pause['requested_seconds']==expected['seconds'], 'Pause differs')
        require(pause['completed'] and expected['seconds']-.002<=pause['elapsed_seconds']<=expected['seconds']+.050, 'Pause mistimed/interrupted')
        before = [v for v in points if v['at']<=pause['started_at']]
        # Allow a one-second tail for in-flight/receiver buffering. This remains
        # an observational association, not an attributed underrun count.
        after = [v for v in points if v['at']>=pause['ended_at']+1.]
        require(before and after, 'Pause lacks surrounding DMA observations')
        first, last = before[-1], after[0]
        require(0<=pause['started_at']-first['at']<=6 and 1<=last['at']-pause['ended_at']<=7, 'Sparse pause anchors')
        require(last['q_overruns']>=first['q_overruns'] and last['errors']>=first['errors'], 'Counter reset')
        events.append(dict(**pause, from_play_seconds=first['at']-batch['started_at'],
            to_play_seconds=last['at']-batch['started_at'],
            overruns=last['q_overruns']-first['q_overruns'], errors=last['errors']-first['errors'],
            delivery_windows=[w for w in delivery['windows'] if w['started_at']<last['at'] and w['ended_at']>first['at']]))
    return dict(result='PASS', pauses=events, whole_dma=whole_dma,
        send_buffer_actual=event['send_buffer_actual'],
        body_bytes_sent=event['sent'], host_delivery_seconds=event['seconds'],
        average_body_bytes_per_second=event['sent']/event['seconds'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'pauses.json');a=p.parse_args()
    result=dict(scope='Host pauses plus enclosing DMA intervals. Counters include any unrelated event within the interval; no acoustic or packet-arrival claim.',phases={})
    for name in ('control-before','expanded','control-after'):
        try: result['phases'][name]=analyze(ROOT/'physical'/name)
        except (AssertionError, ValueError, FileNotFoundError) as error:
            result['phases'][name]=dict(result='FAIL',reason=str(error))
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(phases={n:dict(result=v['result'],reason=v.get('reason'),
        actual_send_buffer=v.get('send_buffer_actual'),average_bps=v.get('average_body_bytes_per_second'),
        pauses=[{k:r[k] for k in ('after_bytes','requested_seconds','elapsed_seconds','overruns','errors')} for r in v.get('pauses',[])]) for n,v in result['phases'].items()}),indent=2))

if __name__=='__main__': main()
