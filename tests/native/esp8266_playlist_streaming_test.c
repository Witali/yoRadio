#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>
static uint32_t httpd_trace_clock(void) { return 0; }
static void httpd_trace_read(uint32_t start) { (void)start; }
typedef int esp_err_t;
typedef struct { int unused; } httpd_req_t;
enum { ESP_OK = 0, ESP_FAIL = -1 };
static const char *PLAYLIST_PATH;
static char s_static_scratch[512], s_async_message[1088];
static char received[65536], expected[65536];
static size_t size, largest, calls, fail_call;
static unsigned count = 1;
static const char *accept_encoding = "identity";
static const char *cache_path;
static char status_text[80];
static int httpd_req_get_hdr_value_str(httpd_req_t *r, const char *key, char *buffer, size_t capacity) {
    (void)r; (void)key;
    if (!accept_encoding || strlen(accept_encoding) >= capacity) return ESP_FAIL;
    strcpy(buffer, accept_encoding); return ESP_OK;
}
static size_t httpd_req_get_hdr_value_len(httpd_req_t *r, const char *key) {
    (void)r; (void)key; return accept_encoding ? strlen(accept_encoding) : 0;
}
static void httpd_resp_set_status(httpd_req_t *r, const char *value) {
    (void)r; strcpy(status_text, value);
}
static int send_string(httpd_req_t *r, const char *value) { (void)r; (void)value; return ESP_OK; }
static int playlist_web_cache_open(size_t *length) {
    if (!cache_path) return -1;
    int fd = open(cache_path, O_RDONLY);
    if (fd >= 0) { *length = (size_t)lseek(fd, 0, SEEK_END); lseek(fd, 0, SEEK_SET); }
    return fd;
}
static void prepare_short_response(httpd_req_t *r) { (void)r; }
static int finish_short_response(httpd_req_t *r, int result) { (void)r; return result; }
static int httpd_resp_send_404(httpd_req_t *r) { (void)r; return 404; }
static void httpd_resp_set_type(httpd_req_t *r, const char *s) { (void)r; (void)s; }
static void httpd_resp_set_hdr(httpd_req_t *r, const char *s, const char *v) { (void)r; (void)s; (void)v; }
static unsigned playlist_service_count(void) { return count; }
static int httpd_resp_send_chunk(httpd_req_t *r, const char *s, size_t n) {
    (void)r;
    if (++calls == fail_call) return ESP_FAIL;
    assert(n <= sizeof(s_static_scratch));
    if (n > largest) largest = n;
    assert(size + n < sizeof(received));
    if (n) memcpy(received + size, s, n);
    size += n;
    received[size] = 0;
    return ESP_OK;
}
/* IMPLEMENTATION */
int main(int argc, char **argv) {
    static const char *extensions[] = {".ogg", ".opus", ".flac", ".m3u", ".m3u8", ".pls", ".wav"};
    static const char *tails[] = {"", "?mp3=yes", "#fragment", "x", "/audio.mp3"};
    /* Compare against the previous extension algorithm including case,
     * short URLs, query/fragment boundaries and non-ASCII URL bytes. */
    for (unsigned ext=0; ext<7; ++ext) for (unsigned tail=0; tail<5; ++tail)
    for (unsigned mask=0; mask<32; ++mask) {
        char url[200]; snprintf(url,sizeof(url),"http://host/\xc3\xa9%s",extensions[ext]);
        size_t n=strlen(url), len=strlen(extensions[ext]);
        for(unsigned i=1;i<len;++i) if(mask&(1U<<i)) {
            char *c=&url[n-len+i]; if(*c>='a' && *c<='z') *c-='a'-'A';
        }
        strcat(url,tails[tail]);
        const char *suffix=strpbrk(url,"?#");
        size_t length=suffix?(size_t)(suffix-url):strlen(url);
        bool old=false;
        for(unsigned i=CONFIG_YORADIO_OGG_OPUS ? 2 : 0;i<7;++i) {
            size_t l=strlen(extensions[i]);
            if(length>=l && !strncasecmp(url+length-l,extensions[i],l)) old=true;
        }
        assert(has_unsupported_extension(url)==old);
    }
    assert(!has_unsupported_extension(""));
    assert(!has_unsupported_extension("http://h/?x=.ogg"));
    assert(station_supported("Radio", "http://host/mp3"));
    assert(station_supported("oGg radio", "http://host/mp3") == !!CONFIG_YORADIO_OGG_OPUS);
    assert(station_supported("Opus", "http://host/radio.opus") == !!CONFIG_YORADIO_OGG_OPUS);
    assert(!station_supported("Opus", "https://host/radio.opus"));
    assert(!station_supported("Radio", "HTTP://host/mp3"));
    assert(!station_supported("", "h"));
    assert(argc == 2); PLAYLIST_PATH = argv[1];
    FILE *f = fopen(PLAYLIST_PATH, "wb"); assert(f);
    for (unsigned i = 0; i < 71; ++i) {
        char row[672], url[512];
        memset(url, 'a', sizeof(url)); url[0]='/'; url[511]=0;
        snprintf(row, sizeof(row), "Station %u\thttp://host%s\t0\r\n", i, url);
        fputs(row, f); strcat(expected, row);
        fputs("Unsupported\thttps://host/stream.mp3\t0\n", f);
        fputs("Ogg radio\thttp://host/stream\t0\n", f);
#if CONFIG_YORADIO_OGG_OPUS
        strcat(expected, "Ogg radio\thttp://host/stream\t0\n");
#endif
        fputs("Unsupported\thttp://host/stream.opus?x=1\t0\n", f);
#if CONFIG_YORADIO_OGG_OPUS
        strcat(expected, "Unsupported\thttp://host/stream.opus?x=1\t0\n");
#endif
    }
    const char *last = "Last UTF-8: \xd1\x91\thttp://host/live.aac\t0";
    fputs(last,f); strcat(expected,last); fclose(f);
    httpd_req_t req = {0};
    assert(playlist_handler(&req) == ESP_OK);
    assert(largest == sizeof(s_static_scratch) && size == strlen(expected));
    assert(!strcmp(received, expected));
    size = calls = 0; fail_call = 3;
    assert(playlist_handler(&req) == ESP_FAIL);
    assert(calls == 3);
    fail_call = 0; size = calls = 0;
    count = 0; assert(playlist_handler(&req) == 404); count = 1;
    f = fopen(PLAYLIST_PATH, "wb"); assert(f); fclose(f);
    assert(playlist_handler(&req) == 404);
    /* Compare with the original fgets boundaries, including split UTF-8,
     * empty/overlong lines and lengths on both sides of the 1087-byte read. */
    f = fopen(PLAYLIST_PATH, "wb"); assert(f);
    for (unsigned n = 1; n < 2400; n += 37) {
        fputs("Boundary\thttp://host/", f);
        for (unsigned j = 0; j < n; ++j) fputc('a' + j % 26, f);
        fputs("\t0\r\n\n", f);
    }
    fclose(f);
    expected[0] = 0;
    f = fopen(PLAYLIST_PATH, "rb"); assert(f);
    char row[672];
    while (fgets(row, sizeof(row), f))
        if (playlist_service_entry_supported(row)) strcat(expected, row);
    fclose(f);
    size = calls = 0;
    assert(playlist_handler(&req) == ESP_OK);
    assert(size == strlen(expected) && !strcmp(received, expected));
    assert(remove(PLAYLIST_PATH) == 0);
    assert(playlist_handler(&req) == 404);
    /* Encoded bodies are opaque binary data (including NUL), streamed only
     * when gzip is acceptable; cached data does not bypass negotiation. */
    unsigned char compressed[2051];
    for (unsigned i=0;i<sizeof(compressed);++i) compressed[i]=(unsigned char)i;
    f=fopen(PLAYLIST_PATH,"wb");assert(f);
    assert(fwrite(compressed,1,sizeof(compressed),f)==sizeof(compressed));fclose(f);
    cache_path=PLAYLIST_PATH;accept_encoding="gzip, identity;q=0";size=calls=0;
    assert(playlist_handler(&req)==ESP_OK);
    assert(size==sizeof(compressed)&&!memcmp(received,compressed,size));
    size=calls=0;fail_call=2;assert(playlist_handler(&req)==ESP_FAIL);fail_call=0;
    accept_encoding="gzip;q=0, identity;q=0";size=calls=0;
    assert(playlist_handler(&req)==ESP_OK);assert(!strncmp(status_text,"406 ",4)&&size==0);
    char large[140];memset(large,'x',sizeof(large)-1);large[sizeof(large)-1]=0;
    accept_encoding=large;assert(playlist_handler(&req)==ESP_OK);assert(!strncmp(status_text,"431 ",4));
    assert(remove(PLAYLIST_PATH)==0);
    puts("streaming playlist passed");
}
