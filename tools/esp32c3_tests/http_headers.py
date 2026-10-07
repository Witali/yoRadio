"""Check ESP-IDF 6.0.3+ request-length rejection on the native OTA endpoint.

Only short headers and one invalid body byte are sent. Declared lengths are
not allocated or transmitted. The application image and saved settings must
remain unchanged; reboot restores the saved station after the checks.
"""
import argparse
import http.client
from pathlib import Path
import socket
import time
from urllib.parse import urlsplit

from common import Board, Report, require
from ota import image_info, snapshot, verify_snapshot, wait_image


HEADER_CASES = (
    ('uint32-overflow', ('4294967296',), 413),
    ('uint32-overflow-with-low-bits', ('4294968320',), 413),
    ('negative', ('-1',), 400),
    ('non-numeric', ('invalid',), 400),
    ('conflicting-duplicates', ('1', '2'), 400),
)


def request_bytes(host, lengths):
    headers = ['POST /update HTTP/1.1', 'Host: ' + host,
               'Content-Type: application/octet-stream', 'Connection: close']
    headers.extend('Content-Length: ' + value for value in lengths)
    return ('\r\n'.join(headers) + '\r\n\r\nx').encode('ascii')


def request_status(origin, lengths):
    url = urlsplit(origin)
    require(url.scheme == 'http' and url.hostname and not url.username and
            not url.password and url.path in ('', '/'), 'Use the native HTTP board origin')
    with socket.create_connection((url.hostname, url.port or 80), timeout=10) as connection:
        connection.sendall(request_bytes(url.netloc, lengths))
        response = http.client.HTTPResponse(connection)
        try:
            response.begin()
            # The status is the evidence. Bound reads even for an invalid response.
            response.read(4096)
            return response.status
        finally:
            response.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Choose a new report path')
    board = Board(args.board)
    initial = board.info()
    require(initial['app_elf_sha256'] == image_info(args.firmware.read_bytes())['app_elf_sha256'],
            'Wrong installed application')
    board.stop()
    before = snapshot(board)
    report = Report(args.output, initial)
    report.data['minimum_sdk_for_uint32_rejection'] = '6.0.3'
    try:
        for name, lengths, expected in HEADER_CASES:
            def check(lengths=lengths, expected=expected):
                status = request_status(board.origin, lengths)
                require(status == expected, f'Expected HTTP {expected}, received {status}')
                wait_image(board, initial['app_elf_sha256'], initial['partition'])
                return dict(http=status, request_bytes=len(request_bytes(urlsplit(board.origin).netloc, lengths)),
                            active_image_unchanged=True, **verify_snapshot(board, before))
            report.case('http-content-length:' + name, check)
    finally:
        def restore():
            board.reboot()
            time.sleep(3)
            wait_image(board, initial['app_elf_sha256'], initial['partition'])
            return verify_snapshot(board, before)
        report.case('restore-saved-station', restore)
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
