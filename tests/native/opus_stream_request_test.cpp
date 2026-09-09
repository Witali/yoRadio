#include <algorithm>
#include <cassert>
#include <cstring>
#include <string>
#include <cstdio>
#include <cstdint>
using esp_err_t = int;
static constexpr int ESP_OK = 0, ESP_FAIL = -1;
struct httpd_req_t {
    size_t content_len;
    std::string input, status, output;
    size_t offset = 0, fragment = 1;
    bool read_error = false;
};
static unsigned queued, named;
static int queue_result;
static std::string queued_url;
struct helix_opus_init_failure_t { uint32_t stage, free_dram, requested_bytes, reserve_bytes; int32_t detail; };
static helix_opus_init_failure_t diagnostic;
static void helix_codec_opus_init_failure_snapshot(helix_opus_init_failure_t *out) { *out = diagnostic; }
static constexpr unsigned MALLOC_CAP_8BIT = 4;
static size_t heap_caps_get_free_size(unsigned caps) { assert(caps == MALLOC_CAP_8BIT); return UINT32_MAX; }
static void prepare_short_response(httpd_req_t *) {}
static void httpd_resp_set_type(httpd_req_t *, const char *) {}
static void httpd_resp_set_hdr(httpd_req_t *, const char *, const char *) {}
static void httpd_resp_set_status(httpd_req_t *r, const char *status) { r->status = status; }
static int finish_short_response(httpd_req_t *, int result) { return result; }
static int send_string(httpd_req_t *r, const char *body) { r->output = body; return ESP_OK; }
static int httpd_req_recv(httpd_req_t *r, char *out, size_t wanted) {
    if (r->read_error) return ESP_FAIL;
    size_t n = std::min({wanted, r->fragment, r->input.size() - r->offset});
    memcpy(out, r->input.data() + r->offset, n); r->offset += n; return int(n);
}
static int audio_service_play(const char *url) { ++queued; queued_url = url; return queue_result; }
static void native_state_set_station(unsigned index, const char *name) {
    assert(index == 0 && strcmp(name, "OPUS TEST") == 0); ++named;
}
#include "handler.inc"
static httpd_req_t run(std::string input, bool error = false) {
    queued = named = 0; queued_url.clear();
    httpd_req_t r{input.size(), input, "", ""}; r.read_error = error;
    int result = opus_test_stream_handler(&r);
    assert(result == (error ? ESP_FAIL : ESP_OK));
    return r;
}
int main() {
    httpd_req_t status{0, "", "", ""};
    diagnostic = {UINT32_MAX, UINT32_MAX, UINT32_MAX, UINT32_MAX, INT32_MIN};
    assert(opus_test_stream_status_handler(&status) == ESP_OK);
    assert(status.output == "{\"stage\":4294967295,\"free_dram\":4294967295,\"requested_bytes\":4294967295,\"reserve_bytes\":4294967295,\"detail\":-2147483648,\"current_dram\":4294967295}");
    assert(!queued && !named);
    for (const std::string &input : {std::string(""), std::string("http://"),
            std::string("https://example.org/a"), std::string("http://a/\r\nX: a"),
            std::string("http://a/ "), std::string("http://a/\0x", 11),
            std::string("http://a/\x7f"), std::string(512, 'x')}) {
        auto r = run(input); assert(r.status == "400 Bad Request" && !queued && !named);
    }
    for (const std::string &url : {std::string("http://example.org/live.opus"),
            std::string("http://a/") + std::string(502, 'x')}) {
        auto r = run(url); assert(r.status == "202 Accepted");
        assert(queued == 1 && named == 1 && queued_url == url && r.offset == url.size());
    }
    run("http://example.org/live", true); assert(!queued && !named);
    queue_result = ESP_FAIL;
    auto r = run("http://example.org/live");
    assert(r.status == "503 Service Unavailable" && queued == 1 && !named);
    puts("Opus stream request PASS: fragmented body, bounds, injection, queue failure; no playlist mutation");
}
