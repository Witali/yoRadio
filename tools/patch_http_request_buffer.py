"""Opt-in request-buffer release for the audited ESP-IDF HTTP client.

Generate a build-local SDK copy; never modify the shared framework. Reuse
allocates the original full capacity, preserving long URLs/header pagination.
"""
import argparse
import hashlib
from pathlib import Path

SOURCE_SHA256 = '152d658025205b1d0d090127a6d56d24726118c488d7d5bf5f85a98a15e87740'
REQUEST_START = '''esp_err_t esp_http_client_request_send(esp_http_client_handle_t client, int write_len)
{
    if (client == NULL) {
        return ESP_FAIL;
    }
'''
ENSURE_BUFFER = '''
    /* YoRadio: an explicitly released completed GET may reuse this handle.
     * Never replace an in-progress header buffer, including async retries. */
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
/* Called by the owning stream task after accepting final response headers.
 * RX, header dictionaries, TLS records and post_data retain their owners. */
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


def patch(source):
    text = source.decode().replace('\r\n','\n')
    if hashlib.sha256(text.encode()).hexdigest() != SOURCE_SHA256:
        raise ValueError('Unaudited HTTP client source: review request-buffer owners')
    if text.count(REQUEST_START) != 1:
        raise ValueError('Expected exactly one audited request sender')
    return (text.replace(REQUEST_START,REQUEST_START+ENSURE_BUFFER)+RELEASE).encode()


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=patch(args.input.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if not args.output.exists() or args.output.read_bytes()!=result:
        args.output.write_bytes(result)
