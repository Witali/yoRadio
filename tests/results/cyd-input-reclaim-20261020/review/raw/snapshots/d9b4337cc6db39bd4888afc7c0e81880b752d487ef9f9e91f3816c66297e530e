"""Add opt-in completed-GET TX release to the audited CYD ESP-IDF6.0.2 source.

Only two spans are inserted into a build-local copy. Existing SDK bytes,
including request pagination, redirects, authentication and body handling,
remain unchanged. The owning task must finish final response headers before
calling the extension; HTTP handles must never be used concurrently.
"""
import argparse
import hashlib
from pathlib import Path

SOURCE_SHA256 = 'df008c18eb9a5c469edc6a84b8c0b78b720b3010d687838e06e001344d557488'
REQUEST_START = '''esp_err_t esp_http_client_request_send(esp_http_client_handle_t client, int write_len)
{
    if (client == NULL) {
        return ESP_FAIL;
    }
'''
ENSURE_BUFFER = '''
    /* YoRadio: only an explicitly released completed GET has a NULL TX buffer.
     * Reuse always restores the original configured capacity. */
    if (client->request->buffer->data == NULL) {
        if (client->first_line_prepared) {
            return ESP_ERR_INVALID_STATE;
        }
        client->request->buffer->data = malloc(client->buffer_size_tx);
        if (client->request->buffer->data == NULL) {
            errno = 0;
            return ESP_ERR_NO_MEM;
        }
    }
'''
RELEASE = '''
/* Same owning task, after accepting final synchronous GET response headers.
 * Request dictionaries, borrowed post_data and response/RX buffers retain their
 * existing SDK owners. This releases requested TX payload, not measured usable
 * allocator bytes; subsequent requests restore the complete configured size. */
esp_err_t yoradio_http_client_release_request_buffer(esp_http_client_handle_t client)
{
    if (client == NULL || client->request == NULL || client->request->buffer == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    if (client->is_async || client->connection_info.method != HTTP_METHOD_GET ||
        client->post_len != 0 || client->data_write_left != 0 ||
        client->state != HTTP_STATE_RES_ON_DATA_START) {
        return ESP_ERR_INVALID_STATE;
    }
    free(client->request->buffer->data);
    client->request->buffer->data = NULL;
    client->first_line_prepared = false;
    return ESP_OK;
}
'''


def patch(source: bytes) -> bytes:
    """Accept only the pinned source with uniform LF or CRLF line endings."""
    normalized = source.replace(b'\r\n', b'\n')
    if hashlib.sha256(normalized).hexdigest() != SOURCE_SHA256:
        raise ValueError('Unaudited CYD SDK6.0.2 HTTP source; review request-buffer ownership')
    if source == normalized:
        newline = b'\n'
    elif source == normalized.replace(b'\n', b'\r\n'):
        newline = b'\r\n'
    else:
        raise ValueError('Mixed HTTP source line endings are not audited')
    encode = lambda text: text.encode('utf-8').replace(b'\n', newline)
    anchor = encode(REQUEST_START)
    if source.count(anchor) != 1:
        raise ValueError('Expected exactly one audited request sender')
    return source.replace(anchor, anchor + encode(ENSURE_BUFFER), 1) + encode(RELEASE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Write a build-local copy; the input SDK source must stay unchanged')
    result = patch(args.input.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not args.output.exists() or args.output.read_bytes() != result:
        args.output.write_bytes(result)


if __name__ == '__main__':
    main()
