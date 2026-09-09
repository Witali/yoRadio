/* HTTP-task owned, bounded storage: no per-response heap allocation. */
#define WEB_CLOSE_GRACE_MS 5000U
static struct {
    int fd;
    TickType_t started;
    bool pending;
} s_closing[WEB_MAX_OPEN_SOCKETS];

static void web_close_forget(int fd) {
    for (unsigned i = 0; i < WEB_MAX_OPEN_SOCKETS; ++i)
        if (s_closing[i].pending && s_closing[i].fd == fd)
            s_closing[i].pending = false;
}

static void web_close_poll(void) {
    TickType_t now = xTaskGetTickCount();
    for (unsigned i = 0; i < WEB_MAX_OPEN_SOCKETS; ++i) {
        if (!s_closing[i].pending ||
            (TickType_t)(now - s_closing[i].started) < pdMS_TO_TICKS(WEB_CLOSE_GRACE_MS))
            continue;
        if (httpd_sess_trigger_close(s_server, s_closing[i].fd) == ESP_OK)
            s_closing[i].pending = false;
    }
}

esp_err_t web_service_finish_response(httpd_req_t *request, esp_err_t result) {
    int fd = httpd_req_to_sockfd(request);
    if (result != ESP_OK || shutdown(fd, SHUT_WR) != 0) {
        (void)httpd_sess_trigger_close(request->handle, fd);
        return result == ESP_OK ? ESP_FAIL : result;
    }
    /* RFC 9112 9.6: send response + FIN, then wait for peer EOF, but not
     * forever. The normal server loop closes on EOF; this is the fallback
     * for disconnected peers. session_closed clears records before fd reuse. */
    for (unsigned i = 0; i < WEB_MAX_OPEN_SOCKETS; ++i) {
        if (!s_closing[i].pending || s_closing[i].fd == fd) {
            s_closing[i].fd = fd;
            s_closing[i].started = xTaskGetTickCount();
            s_closing[i].pending = true;
            return result;
        }
    }
    (void)httpd_sess_trigger_close(request->handle, fd);
    return result;
}
