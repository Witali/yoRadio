
#include <stdint.h>
#include <stddef.h>
#include <limits.h>
#include <stdio.h>
#include <inttypes.h>
#define ESP_LOGW(...) ((void)0)
#define HTTPD_413_CONTENT_TOO_LARGE 413
#define PARSING_FAILED 7
#define ESP_FAIL -1
struct parser { uint64_t content_length; };
/* Simulate the target's 32-bit size_t even on a 64-bit host. */
struct request { uint32_t content_len; };
struct state { int error, status; };
static int convert(struct parser *parser, struct request *r, struct state *parser_data) {
    /* In absence of body/chunked encoding, http_parser sets content_len to -1 */
    r->content_len = ((int)parser->content_length != -1 ?
                      parser->content_length : 0);

return 0;
}
int main(void) {
    const uint64_t lengths[] = {0, 1, 1024, INT32_MAX, (uint64_t)INT32_MAX+1,
        (uint64_t)UINT32_MAX-1, UINT32_MAX, (uint64_t)UINT32_MAX+1,
        (uint64_t)UINT32_MAX+1025, UINT64_MAX-1, UINT64_MAX};
    int failures = 0;
    for (unsigned i = 0; i < sizeof(lengths)/sizeof(lengths[0]); ++i) {
        struct parser parser = { lengths[i] };
        struct request request = { 12345 };
        struct state state = { 0, 0 };
        int result = convert(&parser, &request, &state);
        int reject = lengths[i] > UINT32_MAX && lengths[i] != UINT64_MAX;
        int valid = reject ? result == ESP_FAIL && state.error == 413 &&
            state.status == PARSING_FAILED && request.content_len == 12345 :
            result == 0 && state.error == 0 && state.status == 0 &&
            request.content_len == (lengths[i] == UINT64_MAX ? 0 : lengths[i]);
        printf("length=%" PRIu64 " result=%s\n", lengths[i], valid ? "PASS" : "FAIL");
        failures += !valid;
    }
    return failures;
}
