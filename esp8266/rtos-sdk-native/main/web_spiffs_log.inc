/* Diagnostic HTTP-task reader. Reuses its existing scratch and excludes
 * logger writer/rotation until close, including disconnected/failed sends.
 * No full-file heap buffer, flash writes, arbitrary paths or delete route. */
static esp_err_t spiffs_log_handler(httpd_req_t *request) {
    prepare_short_response(request);
    httpd_resp_set_type(request, "text/plain; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    httpd_resp_set_hdr(request, "X-Content-Type-Options", "nosniff");
    bool previous = request_path_equals(request, "/api/native/log/previous");
    size_t remaining = 0;
    int fd = spiffs_log_read_open(previous, &remaining);
    if (fd < 0) {
        if (errno == ENOENT) {
            httpd_resp_set_status(request, "404 Not Found");
            return finish_short_response(request, send_string(request, "Log file not created yet\n"));
        }
        httpd_resp_set_status(request, "503 Service Unavailable");
        httpd_resp_set_hdr(request, "Retry-After", "1");
        return finish_short_response(request, send_string(request, "Log storage busy or unavailable\n"));
    }
    httpd_resp_set_hdr(request, "Content-Disposition", previous
        ? "attachment; filename=yoradio-previous.txt" : "attachment; filename=yoradio-current.txt");
    esp_err_t result = ESP_OK;
    while (remaining) {
        size_t count = remaining < sizeof(s_static_scratch) ? remaining : sizeof(s_static_scratch);
        ssize_t n = read(fd, s_static_scratch, count);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) { result = ESP_FAIL; break; }
        remaining -= (size_t)n;
        result = httpd_resp_send_chunk(request, s_static_scratch, (size_t)n);
        if (result != ESP_OK) break;
    }
    if (spiffs_log_read_close(fd) != 0) result = ESP_FAIL;
    /* Never terminate a truncated download as if it succeeded. */
    if (result == ESP_OK) result = httpd_resp_send_chunk(request, NULL, 0);
    return finish_short_response(request, result);
}
