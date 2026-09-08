#include "playlist_web_cache.h"
#include "playlist_service.h"
#include "small_gzip.h"
#include "file_replace.h"
#include "esp_log.h"
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>

#define CACHE_PATH PLAYLIST_PATH ".web.gz"
#define CACHE_TEMP CACHE_PATH ".tmp"
/* Bump when the station-filter policy or representation changes. */
#define CACHE_MAGIC 0x31575a47U
typedef struct {
    uint32_t magic, version, source_size, source_crc, body_size, body_crc;
} cache_header_t;
_Static_assert(sizeof(cache_header_t) == 24, "Stable cache header layout");
typedef struct {
    small_gzip_t gzip;
    unsigned char input[1024];
    char line[672];
    FILE *output;
    cache_header_t header;
} cache_workspace_t;
static bool s_ready;
static cache_header_t s_header;
static const char *TAG = "playlist_web";

void playlist_web_cache_invalidate(void) { s_ready = false; }

static bool checksum(int fd, unsigned char *buffer, size_t capacity,
                     uint32_t *size, uint32_t *crc) {
    *size = 0; *crc = UINT32_MAX;
    ssize_t n;
    while ((n = read(fd, buffer, capacity)) > 0) {
        if ((uint32_t)n > UINT32_MAX - *size) return false;
        *size += (uint32_t)n;
        *crc = small_gzip_crc32(*crc, buffer, (size_t)n);
    }
    *crc ^= UINT32_MAX;
    return n == 0;
}
static bool cached(cache_workspace_t *w) {
    if (!file_recover(CACHE_PATH)) return false;
    int fd = open(CACHE_PATH, O_RDONLY);
    if (fd < 0) return false;
    cache_header_t h;
    bool valid = read(fd, &h, sizeof(h)) == sizeof(h) &&
        h.magic == CACHE_MAGIC && h.version == 1 &&
        h.source_size == w->header.source_size && h.source_crc == w->header.source_crc &&
        h.body_size >= 20 && h.body_size < h.source_size;
    uint32_t size, crc;
    if (valid) valid = checksum(fd, w->input, sizeof(w->input), &size, &crc) &&
                       size == h.body_size && crc == h.body_crc;
    close(fd);
    if (valid) w->header = h;
    return valid;
}
static bool write_body(void *context, const unsigned char *data, size_t size) {
    cache_workspace_t *w = context;
    if (size > UINT32_MAX - w->header.body_size ||
        fwrite(data, 1, size, w->output) != size) return false;
    w->header.body_size += (uint32_t)size;
    w->header.body_crc = small_gzip_crc32(w->header.body_crc, data, size);
    return true;
}
static bool create(cache_workspace_t *w) {
    FILE *input = fopen(PLAYLIST_PATH, "rb");
    if (!input) return false;
    /* Read-ahead is explicit and borrowed from the transient workspace. */
    if (setvbuf(input, (char *)w->input, _IOFBF, sizeof(w->input)) != 0) {
        fclose(input); return false;
    }
    w->output = fopen(CACHE_TEMP, "wb+");
    if (!w->output) { fclose(input); return false; }
    bool ok = fwrite(&w->header, 1, sizeof(w->header), w->output) == sizeof(w->header);
    w->header.body_crc = UINT32_MAX;
    small_gzip_init(&w->gzip, write_body, w);
    while (ok && fgets(w->line, sizeof(w->line), input)) {
        /* Identical row boundaries/filter/strlen behavior to raw WebUI CSV. */
        if (playlist_service_entry_supported(w->line))
            ok = small_gzip_feed(&w->gzip, w->line, strlen(w->line));
    }
    ok = ok && !ferror(input) && small_gzip_finish(&w->gzip);
    if (fclose(input) != 0) ok = false;
    w->header.body_crc ^= UINT32_MAX;
    /* Incompressible/small lists keep the ordinary bounded streaming path. */
    ok = ok && w->header.body_size < w->gzip.supplied;
    if (ok) ok = fseek(w->output, 0, SEEK_SET) == 0 &&
                 fwrite(&w->header, 1, sizeof(w->header), w->output) == sizeof(w->header) &&
                 fflush(w->output) == 0;
    if (fclose(w->output) != 0) ok = false;
    if (ok) ok = file_replace(CACHE_TEMP, CACHE_PATH);
    if (!ok) (void)remove(CACHE_TEMP);
    return ok;
}
void playlist_web_cache_refresh(void) {
    s_ready = false;
    cache_workspace_t *w = calloc(1, sizeof(*w));
    if (!w) { ESP_LOGW(TAG, "Cache skipped: no transient workspace"); return; }
    w->header.magic = CACHE_MAGIC; w->header.version = 1;
    int fd = open(PLAYLIST_PATH, O_RDONLY);
    bool ok = fd >= 0 && checksum(fd, w->input, sizeof(w->input),
                                  &w->header.source_size, &w->header.source_crc);
    if (fd >= 0) close(fd);
    bool reused = ok && cached(w);
    if (ok && !reused) ok = create(w);
    if (ok) {
        s_header = w->header;
        s_ready = true;
        ESP_LOGI(TAG, "%s gzip: %u -> %u bytes, temporary RAM %u",
                 reused ? "Validated" : "Built", (unsigned)s_header.source_size,
                 (unsigned)s_header.body_size, (unsigned)sizeof(*w));
    } else ESP_LOGW(TAG, "Gzip cache unavailable; using raw CSV");
    free(w);
}
int playlist_web_cache_open(size_t *length) {
    if (!s_ready || !length) return -1;
    int fd = open(CACHE_PATH, O_RDONLY);
    if (fd < 0) return -1;
    cache_header_t h;
    struct stat st;
    if (read(fd, &h, sizeof(h)) != sizeof(h) || memcmp(&h, &s_header, sizeof(h)) ||
        fstat(fd, &st) || st.st_size != (off_t)(sizeof(h) + h.body_size)) {
        close(fd); s_ready = false; return -1;
    }
    *length = h.body_size;
    return fd;
}
