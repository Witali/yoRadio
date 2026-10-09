"""Verify driver-submitted PCM tails; this does not capture the analog output."""
import argparse
from contextlib import ExitStack
import json
import math
from pathlib import Path
import re
import time

from common import Board, Report, fixtures, require, check_file_runtime
from diagnostic import DiagnosticCapture
from staged_dma import parse as parse_dma
from audio_test_server.server import Server

DMA_FRAMES=512
OUTPUT_RATE=48000
STEREO_S16_FRAME_BYTES=4
END_OF_FILE=1  # AUDIO_END_EOF in main/audio_completion.h.
FLUSH=re.compile(r'PERF PCM_FLUSH: frames=(\d+) result=(-?\d+)$')
END=re.compile(r'PERF PCM_END: generation=(\d+) completion=(\d+) result=(-?\d+)$')


def terminal_records(rows):
    """Require ordered flush -> cumulative DMA -> EOF records, without repair."""
    terminals=[];flush=dma=None
    for row in rows:
        line=re.sub(r'\x1b\[[0-9;]*m','',row['line'])
        require(math.isfinite(float(row['at'])),'Invalid terminal timestamp')
        if 'PERF PCM_FLUSH' in line:
            match=FLUSH.search(line)
            require(match is not None and line.count('PERF ')==1,'Damaged PCM flush record')
            frames,result=map(int,match.groups())
            require(frames<DMA_FRAMES,'PCM tail exceeds a DMA block')
            flush=dict(at=row['at'],frames=frames,result=result);dma=None
        elif 'PERF PCM_END' in line:
            match=END.search(line)
            require(match is not None and line.count('PERF ')==1,'Damaged PCM end record')
            generation,completion,result=map(int,match.groups())
            require(generation<1<<32 and completion<1<<32,'PCM end fields out of range')
            require(flush is not None and dma is not None,'EOF missing ordered flush/DMA evidence')
            require(flush['at']<=dma['at']<=row['at'],'Out-of-order PCM terminal records')
            terminals.append(dict(at=row['at'],generation=generation,completion=completion,
                                  result=result,flush=flush,dma=dma))
            flush=dma=None
        else:
            point=parse_dma(row)
            if point is not None and flush is not None: dma=point
    return terminals


def check_submission(previous,current,frames,rate):
    require(frames>0 and 8000<=rate<=OUTPUT_RATE,'Invalid expected PCM shape')
    require(current['generation']>previous['generation'],'Stale/reset stream generation')
    require(current['completion']==END_OF_FILE,'Stream did not complete as EOF')
    require(current['result']==0 and current['flush']['result']==0,'PCM tail write failed')
    produced=1+(frames-1)*OUTPUT_RATE//rate
    expected_bytes=((produced+DMA_FRAMES-1)//DMA_FRAMES)*DMA_FRAMES*STEREO_S16_FRAME_BYTES
    require(current['flush']['frames']==produced%DMA_FRAMES,'Wrong remaining PCM frame count')
    a,b=previous['dma'],current['dma']
    require(all(b[k]>=a[k] for k in ('writes','written_bytes','errors')),'DMA counter reset')
    written=b['written_bytes']-a['written_bytes']
    require(written==expected_bytes,'Wrong complete PCM submission length')
    require(b['errors']==a['errors'],'Driver write error during short file')
    return dict(input_frames=frames,output_frames=produced,tail_frames=produced%DMA_FRAMES,
        expected_padded_bytes=expected_bytes,submitted_bytes=written,
        generation=current['generation'],driver_errors=0,analog_capture=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board',required=True);parser.add_argument('--host',required=True)
    parser.add_argument('--serial-port',required=True)
    parser.add_argument('--fixture-manifest',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--tls-cert');parser.add_argument('--tls-key')
    args=parser.parse_args()
    require(bool(args.tls_cert)==bool(args.tls_key),'Both TLS certificate and key are required')
    args.output.mkdir(parents=True,exist_ok=False)
    specs=fixtures(args.fixture_manifest)
    entries=json.loads(args.fixture_manifest.read_text())['fixtures']
    require(len(entries)==30 and all(e['round_trip_exact'] for e in entries),'Expected 30 verified tail fixtures')
    board=Board(args.board);report=Report(args.output/'report.json',board.info())
    report.data['scope']=__doc__
    capture=DiagnosticCapture(args.serial_port)
    previous=None;observations=[];http=tls=None
    report.data['fixtures']=entries
    def play(name,origin):
        nonlocal previous
        board.stop();time.sleep(.1)
        started=time.monotonic()
        observation=dict(name=name,protocol=origin.split(':',1)[0],started_at=started)
        observations.append(observation)
        board.play(origin+'/file/'+name,'flac')
        deadline=started+8
        terminals=[]
        while time.monotonic()<deadline:
            rows=capture.since(started)
            check_file_runtime(rows)
            terminals=terminal_records(rows)
            if terminals: break
            time.sleep(.02)
        require(len(terminals)==1,'Missing or multiple terminal records for one short file')
        current=terminals[0]
        observation['terminal']=current
        require(current['completion']==END_OF_FILE and current['result']==0,'Short-file EOF failed')
        state=board.status()
        deadline=time.monotonic()+2
        while state['audio'] and time.monotonic()<deadline:
            time.sleep(.05);state=board.status()
        require(not state['audio'],'Playback status remained active after EOF submission')
        evidence=dict(warmup=True) if previous is None else check_submission(previous,current,
            specs[name]['frames'],specs[name]['rate'])
        observation['status']=state
        previous=current
        (args.output/'status.json').write_text(json.dumps(observations,indent=2)+'\n')
        return evidence
    try:
        with ExitStack() as stack:
            http=stack.enter_context(Server(args.host,8770,specs,unpaced_files=True))
            origins=[('http','http://'+args.host+':8770')]
            if args.tls_cert:
                tls=stack.enter_context(Server(args.host,8771,specs,args.tls_cert,args.tls_key,unpaced_files=True))
                origins.append(('https','https://'+args.host+':8771'))
            report.case('warmup',lambda:play('tail-flac-48000-2ch-513frames',origins[0][1]))
            require(previous is not None,'Cannot measure PCM deltas without warmup EOF')
            for protocol,origin in origins:
                for entry in entries:
                    report.case(protocol+':'+entry['name'],lambda e=entry,o=origin:play(e['name'],o))
                    if report.data['cases'][-1]['result']!='PASS':
                        # Stop after a mismatch: do not use a failed case's
                        # unknown write count as the next case's baseline.
                        raise RuntimeError('Short-file submission failed; preserve first failure')
    finally:
        try:
            report.case('leave-stopped',lambda:board.stop())
        finally:
            capture.close()
            if http: report.data['server_events']=http.events
            if tls: report.data['tls_events']=tls.events
            (args.output/'status.json').write_text(json.dumps(observations,indent=2)+'\n')
            (args.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n')
            report.save()
    return report.exit_code()


if __name__=='__main__': raise SystemExit(main())
