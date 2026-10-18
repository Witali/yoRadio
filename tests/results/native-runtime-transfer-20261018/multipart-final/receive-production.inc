#define WEB_UPLOAD_MAX (96U * 1024U)
#define WEB_UPLOAD_RECEIVE_BYTES 256U
#define WEB_UPLOAD_WRITE_BYTES 2048U
#define WEB_UPLOAD_TIMEOUT_US 120000000LL
#define WEB_UPLOAD_IDLE_US 10000000LL
static bool receive_form(httpd_req_t *request, web_file_form_t *form) {
    char type[192], boundary[71];
    size_t limit = form->mode == WEB_FORM_CREDENTIALS ? 4096U : WEB_UPLOAD_MAX;
    if (!request->content_len || request->content_len > limit ||
        httpd_req_get_hdr_value_str(request, "Content-Type", type, sizeof(type)) != ESP_OK ||
        !mp_form_data_boundary(type, boundary, sizeof(boundary))) return false;
    web_multipart_t parser;
    if (!mp_init(&parser, boundary, web_file_form_part, form)) return false;
    uint8_t chunk[WEB_UPLOAD_RECEIVE_BYTES] = {0};
    bool complete = false;
    size_t remaining = request->content_len;
    int64_t started = esp_timer_get_time(), last_data = started;
    while (remaining) {
        int64_t now = esp_timer_get_time();
        if (now - started >= WEB_UPLOAD_TIMEOUT_US || now - last_data >= WEB_UPLOAD_IDLE_US)
            goto done;
        size_t count = remaining < sizeof(chunk) ? remaining : sizeof(chunk);
        int received = httpd_req_recv(request, (char *)chunk, count);
        if (received == HTTPD_SOCK_ERR_TIMEOUT) { vTaskDelay(1); continue; }
        if (received <= 0 || (size_t)received > count) goto done;
        now = esp_timer_get_time();
        if (now - started >= WEB_UPLOAD_TIMEOUT_US || now - last_data >= WEB_UPLOAD_IDLE_US)
            goto done;
        if (!mp_feed(&parser, chunk, (size_t)received)) goto done;
        // Staging may synchronously write/flush flash. Exclude that controlled
        // work only from idle time; never extend the absolute receive budget.
        last_data = esp_timer_get_time();
        if (last_data - started >= WEB_UPLOAD_TIMEOUT_US ||
            !native_wifi_request_io_progress(request)) goto done;
        native_wifi_erase(chunk, sizeof(chunk));
        remaining -= (size_t)received;
        vTaskDelay(1);
    }
    complete = mp_complete(&parser);
done:
    native_wifi_erase(chunk, sizeof(chunk));
    return complete;
}
