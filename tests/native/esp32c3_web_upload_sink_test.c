#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

static unsigned allocations, opened, closed, writes;
static size_t written, sizes[16];
static uint8_t output[8192];
static bool no_memory, open_error, write_error, sync_error;
static void *allocate(size_t size) {
    ++allocations;
    assert(size == 2048);
    return no_memory ? NULL : malloc(size);
}
static int create(const char *path, int flags, int mode) {
    (void)mode;
    assert(strstr(path, "/spiffs/data/web-upload-"));
    assert(flags == (O_WRONLY | O_CREAT | O_TRUNC));
    ++opened;
    return open_error ? -1 : 7;
}
static ssize_t emit(int fd, const void *data, size_t size) {
    assert(fd == 7);
    if (write_error) { errno = ENOSPC; return -1; }
    assert(writes < 16 && written + size <= sizeof(output));
    sizes[writes++] = size;
    memcpy(output + written, data, size); written += size;
    return (ssize_t)size;
}
static int sync_file(int fd) { assert(fd == 7); return sync_error ? -1 : 0; }
static int close_file(int fd) { assert(fd == 7); ++closed; return 0; }
#define malloc allocate
#define open create
#define write emit
#define fsync sync_file
#define close close_file
// Generated verbatim from web_upload.c by the runner; no alternate sink code.
#include "sink-under-test.h"
#undef malloc
#undef open
#undef write
#undef fsync
#undef close

static void reset(void) {
    allocations = opened = closed = writes = 0; written = 0;
    no_memory = open_error = write_error = sync_error = false;
}
int main(void) {
    uint8_t input[5000];
    for (size_t i = 0; i < sizeof(input); ++i) input[i] = (uint8_t)i;
    const size_t steps[] = {1,17,256,512,2048,5000};
    for (size_t trial = 0; trial < sizeof(steps)/sizeof(steps[0]); ++trial) {
        reset();
        upload_sink_t sink = {.fd = -1};
        assert(!sink.buffer && allocations == 0);
        assert(begin_file(0, &sink));
        for (size_t i = 0; i < sizeof(input); i += steps[trial]) {
            size_t n = sizeof(input) - i;
            if (n > steps[trial]) n = steps[trial];
            assert(write_file(input + i, n, &sink));
        }
        assert(end_file(&sink));
        assert(allocations == 1 && opened == 1 && closed == 1);
        assert(writes == 3 && sizes[0] == 2048 && sizes[1] == 2048 && sizes[2] == 904);
        assert(written == sizeof(input) && !memcmp(input, output, written));
        assert(begin_file(1, &sink));
        assert(allocations == 1); // Reuse the same buffer across multipart files.
        assert(write_file(input, 3, &sink) && end_file(&sink));
        free(sink.buffer);
    }
    reset(); no_memory = true;
    upload_sink_t sink = {.fd = -1};
    assert(!begin_file(0, &sink) && opened == 0 && writes == 0 && !sink.buffer);
    reset(); open_error = true;
    assert(!begin_file(0, &sink) && sink.buffer && sink.fd == -1);
    free(sink.buffer); sink = (upload_sink_t){.fd = -1};
    reset(); assert(begin_file(0, &sink)); write_error = true;
    assert(!write_file(input, 2048, &sink) && writes == 0);
    close_file(sink.fd); free(sink.buffer); sink = (upload_sink_t){.fd = -1};
    reset(); assert(begin_file(0, &sink));
    assert(write_file(input, 3, &sink)); sync_error = true;
    assert(!end_file(&sink) && closed == 1 && sink.fd == -1);
    free(sink.buffer);
    puts("Upload sink passed: lazy 2048-byte allocation, reuse, exact block sizes, tail, OOM and IO failures");
    return 0;
}
