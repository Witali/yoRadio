#define WEB_UPLOAD_MAX (96U * 1024U)
#define WEB_UPLOAD_RECEIVE_BYTES 256U
#define WEB_UPLOAD_WRITE_BYTES 2048U
#define WEB_UPLOAD_TIMEOUT_US 120000000LL
#define WEB_UPLOAD_IDLE_US 10000000LL
// All three routes run synchronously in the same HTTP server task. Its stack
// is reserved at startup. Staging uses flash, never request-sized heap memory.
typedef struct {
    int fd;
    size_t buffered;
    uint8_t *buffer;
} upload_sink_t;

static void temporary_path(unsigned slot, char *path, size_t capacity) {
    snprintf(path, capacity, "/spiffs/data/web-upload-%02u.tmp", slot);
}
static bool begin_file(unsigned slot, void *context) {
    upload_sink_t *sink = context;
    char path[64];
    temporary_path(slot, path, sizeof(path));
    if (!sink->buffer) sink->buffer = malloc(WEB_UPLOAD_WRITE_BYTES);
    if (!sink->buffer) return false; // No live file has been removed.
    sink->buffered = 0;
    sink->fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0666);
    return sink->fd >= 0;
}
static bool flush_buffer(upload_sink_t *sink) {
    size_t offset = 0;
    // POSIX write reaches SPIFFS directly. Do not add a hidden stdio buffer
    // which could allocate heap and split these coalesced 2 KiB writes again.
    while (offset < sink->buffered) {
        ssize_t count = write(sink->fd, sink->buffer + offset, sink->buffered - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) return false;
        offset += (size_t)count;
    }
    sink->buffered = 0;
    return true;
}
static bool write_file(const uint8_t *data, size_t size, void *context) {
    upload_sink_t *sink = context;
    if (sink->fd < 0) return false;
    while (size) {
        size_t count = WEB_UPLOAD_WRITE_BYTES - sink->buffered;
        if (count > size) count = size;
        memcpy(sink->buffer + sink->buffered, data, count);
        sink->buffered += count; data += count; size -= count;
        if (sink->buffered == WEB_UPLOAD_WRITE_BYTES) {
            if (!flush_buffer(sink)) return false;
        }
    }
    return true;
}
static bool end_file(void *context) {
    upload_sink_t *sink = context;
    if (sink->fd < 0) return false;
    bool ok = flush_buffer(sink);
    if (fsync(sink->fd) != 0) ok = false;
    if (close(sink->fd) != 0) ok = false;
    sink->fd = -1;
    return ok;
}

