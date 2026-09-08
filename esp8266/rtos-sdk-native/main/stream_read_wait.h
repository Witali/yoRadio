/* Internal helper: included after http_stream_t and generation_current().
 * The reader owns the socket throughout this bounded wait. No close/reopen
 * is performed here, and ready sockets are never delayed before recv(). */
static bool stream_wait_after_empty(http_stream_t *stream, uint32_t generation,
                                    uint32_t wait_ms) {
    if (!generation_current(generation)) { errno = ECANCELED; return false; }
    if (!wait_ms) {
        vTaskDelay(pdMS_TO_TICKS(1)); /* Legacy A/B control. */
        if (!generation_current(generation)) { errno = ECANCELED; return false; }
        return true;
    }
    TickType_t elapsed = xTaskGetTickCount() - stream->last_receive_tick;
    TickType_t limit = pdMS_TO_TICKS(STREAM_IDLE_TIMEOUT_MS);
    if (elapsed >= limit) { errno = ETIMEDOUT; return false; }
    uint32_t remaining_ms = (limit - elapsed) * portTICK_PERIOD_MS;
    if (wait_ms > remaining_ms) wait_ms = remaining_ms;
    fd_set readable, errors;
    FD_ZERO(&readable); FD_SET(stream->socket, &readable);
    FD_ZERO(&errors); FD_SET(stream->socket, &errors);
    struct timeval timeout = { .tv_sec = 0, .tv_usec = (long)wait_ms * 1000L };
    int ready = select(stream->socket + 1, &readable, NULL, &errors, &timeout);
    int wait_errno = errno;
    if (!generation_current(generation)) { errno = ECANCELED; return false; }
    if (ready < 0 && wait_errno != EINTR) { errno = wait_errno; return false; }
    if (ready <= 0 && http_stream_idle_expired(xTaskGetTickCount(),
            stream->last_receive_tick, limit)) {
        errno = ETIMEDOUT; return false;
    }
    /* Readiness is only a hint: the caller still handles EAGAIN/EOF/errors.
     * Neither a timeout nor a spurious wake refreshes last_receive_tick. */
    return true;
}
