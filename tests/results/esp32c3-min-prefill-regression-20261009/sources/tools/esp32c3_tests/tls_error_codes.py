"""Keep numeric mbedTLS returns from known SDK messages, never arbitrary text."""
import re


def error_detail(component, body):
    """Return allowlisted operation and signed return, or no extra detail.

    ESP-IDF 6.1 esp_mbedtls_dynamic_impl.c logs -ret in decimal for
    fetch_input. esp_tls_mbedtls.c logs -ret in hex for read/write/handshake.
    Match the entire message: appended hosts, certificate subjects and
    unrelated numeric fields must never be copied or mistaken for codes.
    Unknown messages remain generic TLS failures in the caller.
    """
    operation = None
    magnitude = 0
    if component == 'Dynamic Impl':
        match = re.fullmatch(r'mbedtls_ssl_fetch_input error=([0-9]{1,10})', body)
        if match:
            operation, magnitude = 'fetch_input', int(match[1])
    elif component == 'esp-tls-mbedtls':
        match = re.fullmatch(r'(read|write) error :-0x([0-9A-Fa-f]{4,8})', body)
        if match:
            operation, magnitude = match[1], int(match[2], 16)
        else:
            match = re.fullmatch(r'mbedtls_ssl_handshake returned -0x([0-9A-Fa-f]{4,8})', body)
            if match:
                operation, magnitude = 'handshake', int(match[1], 16)
    if operation and 0 < magnitude <= 0x7fffffff:
        return f' operation={operation} mbedtls_return={-magnitude}'
    return ''
