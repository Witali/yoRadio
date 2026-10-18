static bool embedded_script_size(const uint8_t *start, const uint8_t *end, ssize_t *length) {
    uintptr_t first = (uintptr_t)start, last = (uintptr_t)end;
    if (last < first || last - first > INT_MAX) return false;
    *length = (ssize_t)(last - first);
    return true;
}
static esp_err_t send_static_file(httpd_req_t *request, FILE *file) {
    char chunk[CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES];
    bool failed = false;
    for (;;) {
        size_t count = fread(chunk, 1, sizeof(chunk), file);
        if (count && httpd_resp_send_chunk(request, chunk, (ssize_t)count) != ESP_OK) {
            failed = true;
            break;
        }
        // A positive short read can already set EOF or a read error. Do not
        // issue another read while the stream position may be indeterminate.
        if (ferror(file)) { failed = true; break; }
        if (feof(file)) break;
        if (count < sizeof(chunk)) { failed = true; break; }
    }
    if (fclose(file) != 0) failed = true;
    if (failed) {
        // The request still owns its fd here; avoid a successful zero chunk or
        // a delayed fd-only close that could affect a later reused session.
        (void)shutdown(httpd_req_to_sockfd(request), SHUT_RDWR);
        return ESP_FAIL;
    }
    return finish_static_response(request, httpd_resp_send_chunk(request, NULL, 0));
}
