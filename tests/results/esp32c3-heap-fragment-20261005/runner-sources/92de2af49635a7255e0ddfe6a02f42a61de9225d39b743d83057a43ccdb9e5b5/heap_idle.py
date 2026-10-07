"""Observe an already stopped C3 without HTTP polling, then compare polled idle."""
import argparse
import json
from pathlib import Path
import time
from common import Board, Report, require
from diagnostic import DiagnosticCapture
from ota_diagnostic import serial_health
from run import Suite


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board',required=True)
    parser.add_argument('--serial-port',required=True)
    parser.add_argument('--quiet-seconds',type=int,default=130)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    require(args.quiet_seconds>=15,'Observe at least three diagnostic periods')
    board=Board(args.board)
    identity=board.info()
    require(not board.status()['audio'],'Stop playback before passive idle observation')
    report=Report(args.output/'report.json',identity)
    capture=DiagnosticCapture(args.serial_port)
    suite=Suite(board,'',{},capture,args.output)
    try:
        started=time.monotonic()
        deadline=started+args.quiet_seconds
        while time.monotonic()<deadline:
            time.sleep(min(10,deadline-time.monotonic()))
        report.data['quiet_window']=dict(started_at=started,ended_at=time.monotonic(),http_polls=0)
        def polled():
            samples=suite.observe(12,'polled-idle')
            require(all(not s['audio'] for s in samples),'Unexpected audio during idle measurement')
            require(board.info()['app_elf_sha256']==identity['app_elf_sha256'],'Image changed during idle')
            return dict(samples=len(samples))
        report.case('idle-with-http-polling',polled)
    finally:
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n')
        report.data['cases'].append(serial_health(capture.rows))
        report.save()
    return report.exit_code()


if __name__=='__main__':raise SystemExit(main())
