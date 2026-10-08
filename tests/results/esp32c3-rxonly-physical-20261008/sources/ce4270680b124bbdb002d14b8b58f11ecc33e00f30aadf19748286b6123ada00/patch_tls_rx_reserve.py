"""Route audited dynamic TLS RX allocations through an application-owned slot.

Generate a build-local source copy. Shared SDK files and all TX allocations
remain unchanged. New SDK revisions require a fresh allocation/free audit.
"""
import argparse
import hashlib
from pathlib import Path


SOURCE_SHA256 = 'b783870fb5e7423a1fa44af78772151ddb931ee1480b954cf513cd877cda5070'
RX_FUNCTIONS = ('esp_mbedtls_dynamic_set_rx_buf_static',
                'esp_mbedtls_reset_add_rx_buffer',
                'esp_mbedtls_add_rx_buffer', 'esp_mbedtls_free_rx_buffer')
DECLARATION = ('\n/* Project RX allocation hook; matching frees use mbedtls_free. */\n'
               '#include <stddef.h>\n'
               'extern void *yoradio_tls_rx_calloc(size_t count, size_t size);\n')


def patch(source):
    text = source.decode('utf-8').replace('\r\n', '\n')
    if hashlib.sha256(text.encode()).hexdigest() != SOURCE_SHA256:
        raise ValueError('Unaudited dynamic TLS source; review all RX allocation/free paths')
    for name in RX_FUNCTIONS:
        start = text.index(name + '(mbedtls_ssl_context *ssl)')
        end = text.index('\n}\n', start) + 3
        body = text[start:end]
        if body.count('mbedtls_calloc(') != 1:
            raise ValueError('Expected exactly one RX allocation in ' + name)
        text = text[:start] + body.replace('mbedtls_calloc(', 'yoradio_tls_rx_calloc(') + text[end:]
    marker = '#include "esp_mbedtls_dynamic_impl.h"'
    if text.count(marker) != 1:
        raise ValueError('Missing dynamic TLS header')
    return text.replace(marker, marker + DECLARATION).encode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = patch(args.input.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not args.output.exists() or args.output.read_bytes() != data:
        args.output.write_bytes(data)
