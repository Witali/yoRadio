"""Retain ESP-IDF 6.0.3's length guard in the project's 6.1 HTTP server.

Generate a local source copy; never modify the shared SDK. Unknown sources
fail closed so a future SDK must be reviewed before this backport is reused.
"""
import argparse
import hashlib
from pathlib import Path


# Hash after normalizing only Git's CRLF/LF checkout conversion.
SOURCE_SHA256 = {
    'd733639df6561f2879f668aacb16c12749d9516fe80a00d1c3781e1750c6dcd4': '6.0.2',
    '9ec387ffc4f42a6b572d54aa8a9231d2cc05d809a82810759a7d595b1dc99349': '6.0.3',
    'e71ab6fb21dccc1138e3cf8afb54871f38d215c292c66bc894e506c495a9f864': '6.1',
    # release/v6.1 9a97f6c54ec6 already contains the identical upstream guard.
    '2121bc06c00656fd2ad85b1a8a7eb3fe5d6010ccf3756b57d5520c3b8286df3e': '6.1-9a97f6c54ec6',
}

OLD = '''    /* In absence of body/chunked encoding, http_parser sets content_len to -1 */
    r->content_len = ((int)parser->content_length != -1 ?
                      parser->content_length : 0);
'''

# SPDX-License-Identifier: Apache-2.0
# Backported verbatim from ESP-IDF v6.0.3 components/esp_http_server/src/httpd_parse.c.
# Copyright 2018-2025 Espressif Systems (Shanghai) CO LTD.
GUARD = '''    /* In absence of body/chunked encoding, http_parser sets content_len to ULLONG_MAX */
    if (parser->content_length != ULLONG_MAX) {
        /* Content-Length was specified. Reject any value above UINT32_MAX: it is
         * the largest body length the server can represent in r->content_len on
         * every target, and rejecting larger values prevents the 64->32-bit
         * truncation that would otherwise enable request smuggling (CWE-681). */
        if (parser->content_length > UINT32_MAX) {
            ESP_LOGW(TAG, LOG_FMT("Content-Length %" PRIu64
                                  " exceeds UINT32_MAX; rejecting with 413"),
                     (uint64_t)parser->content_length);
            parser_data->error = HTTPD_413_CONTENT_TOO_LARGE;
            parser_data->status = PARSING_FAILED;
            return ESP_FAIL;
        }
        r->content_len = (size_t)parser->content_length;
    } else {
        r->content_len = 0;
    }
'''


def patch(source):
    text = source.decode('utf-8').replace('\r\n', '\n')
    version = SOURCE_SHA256.get(hashlib.sha256(text.encode('utf-8')).hexdigest())
    if version is None:
        raise ValueError('Unaudited HTTP server source: review the Content-Length guard')
    if version in ('6.0.3', '6.1-9a97f6c54ec6'):
        if text.count(GUARD) != 1:
            raise ValueError('Expected the audited native Content-Length guard')
        return source
    if text.count(OLD) != 1:
        raise ValueError('Expected exactly one legacy Content-Length assignment')
    text = text.replace(OLD, GUARD)
    # ULLONG_MAX must have an explicit declaration, independent of SDK includes.
    text = text.replace('#include <stdlib.h>', '#include <limits.h>\n#include <stdlib.h>', 1)
    return text.encode('utf-8')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = patch(a.input.read_bytes())
    a.output.parent.mkdir(parents=True, exist_ok=True)
    if not a.output.exists() or a.output.read_bytes() != result:
        a.output.write_bytes(result)
