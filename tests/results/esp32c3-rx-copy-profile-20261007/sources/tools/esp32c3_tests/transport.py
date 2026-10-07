"""Compare paced fixture delivery with TCP_NODELAY off/on on an unchanged C3.

Only the host's accepted audio socket changes. No firmware/settings are written;
the saved station is restored by software reboot at the end.
"""
import argparse
import json
from pathlib import Path
import re
import socket
import time

from common import Board, Report, fixtures, require
from memory import wait_ready
from ota import snapshot, verify_snapshot
from run import Capture, Suite
from audio_test_server.server import Server
from serial_lines import serial_lines


class DiagnosticCapture(Capture):
    def read(self):
        for line in serial_lines(self.port, self.closed):
            if re.search(r'PERF |Memory .*: free=|Wi-Fi power save:|decode (?:error|failed)|'
                         r'allocation failed|assert failed|Guru Meditation|CORRUPT HEAP|serial capture interrupted', line):
                self.rows.append(dict(at=time.monotonic(), line=line))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', type=int, default=8770)
    parser.add_argument('--serial-port', required=True)
    parser.add_argument('--case', default='flac-level8')
    parser.add_argument('--cycles', type=int, default=2)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    specs = fixtures()
    require(args.case in specs, 'Unknown fixture')
    require(args.cycles >= 1, 'At least one pair is required')
    board = Board(args.board)
    identity = board.info()
    before = snapshot(board)
    report = Report(args.output/'report.json', identity)
    report.data['fixture_hashes'] = {args.case: specs[args.case]['sha256']}
    report.data['socket_conditions'] = []
    capture = DiagnosticCapture(args.serial_port)
    suite = Suite(board, f'http://{args.host}:{args.port}', specs, capture, args.output)
    try:
        for cycle in range(args.cycles):
            # Reverse the order on alternate pairs to reduce a fixed order bias.
            for enabled in ((False, True) if cycle % 2 == 0 else (True, False)):
                server = Server(args.host, args.port, specs)
                original_accept = server.http.get_request
                accepted_values = []

                def accept():
                    connection, address = original_accept()
                    connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, int(enabled))
                    accepted_values.append(connection.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY))
                    return connection, address

                server.http.get_request = accept
                label = f'transport:{cycle}:nodelay-{int(enabled)}'
                with server:
                    report.case(label, lambda: suite.file(args.case, specs[args.case]['codec']))
                report.data['socket_conditions'].append(dict(case=label,
                    requested_nodelay=int(enabled), accepted_nodelay=accepted_values,
                    events=server.events))
                report.save()
    finally:
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')

        def restore():
            board.stop()
            board.reboot()
            wait_ready(board, identity['app_elf_sha256'])
            return verify_snapshot(board, before)

        report.case('restore-board', restore)
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
