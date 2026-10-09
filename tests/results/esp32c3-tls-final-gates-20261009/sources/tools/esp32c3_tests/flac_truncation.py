"""Exercise FLAC network EOF at partial frames, then recover to AAC/FLAC."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from common import Board, Report, check_playback, check_recovery_heap, fixtures, require
from diagnostic import DiagnosticCapture
from memory import wait_ready
from ota import snapshot, verify_snapshot
from ota_diagnostic import serial_health
from run import Suite
from audio_test_server.server import Server


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board',required=True)
    parser.add_argument('--host',required=True)
    parser.add_argument('--serial-port',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    specs=fixtures(); base=specs['flac-level8']; data=base['data']
    offset=4
    while True:
        last=data[offset]&128
        offset+=4+int.from_bytes(data[offset+1:offset+4],'big')
        if last:break
    cuts={'flac-prefix-32':offset+32,'flac-prefix-4096':offset+4096,'flac-tail-1':len(data)-1}
    for name,limit in cuts.items():
        payload=data[:limit]
        specs[name]=dict(base,data=payload,sha256=hashlib.sha256(payload).hexdigest(),
                         seconds=base['seconds'] if name=='flac-tail-1' else 1)
    board=Board(args.board); identity=board.info(); settings=snapshot(board)
    report=Report(args.output/'report.json',identity)
    report.data['fixture_hashes']={name:specs[name]['sha256'] for name in (*cuts,'flac-level8','lc-48000-stereo')}
    capture=DiagnosticCapture(args.serial_port)
    suite=Suite(board,f'http://{args.host}:8770',specs,capture,args.output)
    baseline=[]
    try:
        def idle_before():
            baseline.extend(suite.idle_heap()); return dict(samples=baseline)
        report.case('idle-before',idle_before)
        with Server(args.host,8770,specs) as server:
            for name in cuts:
                def fault(n=name):
                    started=time.monotonic();suite.start(n,hint='flac')
                    rows=suite.observe(max(8,specs[n]['seconds']+5),n)
                    require(all(not r['audio'] for r in rows[-3:]),'Truncated FLAC did not leave playback')
                    require(board.info()['app_elf_sha256']==identity['app_elf_sha256'],'Image changed')
                    evidence=capture.since(started)
                    require(any('FLAC decode error -12' in r['line'] for r in evidence),
                            'Missing explicit bounded-reader truncation error')
                    require(not any(r['line'].startswith(('ESP-ROM:','rst:')) for r in evidence),
                            'Unexpected reboot during truncated FLAC')
                    require(serial_health(evidence)['result']=='PASS','Panic or incomplete serial capture')
                    return dict(stopped=True,terminal=rows[-1]['format'],truncation_reported=True)
                report.case(name+':bounded-eof',fault)
                def recovered():
                    values=suite.idle_heap(stop=False)
                    check_recovery_heap(baseline,values)
                    return dict(samples=values)
                report.case(name+':natural-recovery',recovered)
                for next_name in ('lc-48000-stereo','flac-level8'):
                    def play(n=next_name):
                        suite.start(n)
                        try:return check_playback(suite.observe(7,name+':recover:'+n),specs[n])
                        finally:board.stop()
                    report.case(name+':recover:'+next_name,play)
            report.data['server_events']=server.events
    finally:
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n')
        report.data['cases'].append(serial_health(capture.rows))
        def restore():
            board.stop();board.reboot();wait_ready(board,identity['app_elf_sha256'])
            return verify_snapshot(board,settings)
        report.case('restore-board',restore)
    return report.exit_code()


if __name__=='__main__':raise SystemExit(main())
