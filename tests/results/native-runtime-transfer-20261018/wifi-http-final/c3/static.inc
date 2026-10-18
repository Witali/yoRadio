static void *s_static_request_queue=(void *)1;
static esp_err_t static_handler(httpd_req_t *request) {
    if (!native_wifi_public_static_uri(request->uri, request->method == HTTP_GET))
        return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND, "Public file not found");
    httpd_req_t *async_request = NULL;
    esp_err_t result =
        httpd_req_async_handler_begin(request, &async_request);
    if (result != ESP_OK) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        httpd_resp_set_hdr(request, "Connection", "close");
        return httpd_resp_sendstr(request, "Static worker unavailable");
    }
    if (xQueueSend(s_static_request_queue, &async_request, 0) != pdTRUE) {
        httpd_resp_set_status(async_request, "503 Service Unavailable");
        httpd_resp_set_hdr(async_request, "Connection", "close");
        httpd_resp_sendstr(async_request, "Static worker queue full");
        httpd_req_async_handler_complete(async_request);
    }
    return ESP_OK;
}
