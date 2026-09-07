#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <stdint.h>
typedef int esp_err_t;
enum { ESP_OK, ESP_ERR_INVALID_ARG, ESP_ERR_HTTPD_INVALID_REQ,
       ESP_ERR_HTTPD_RESP_HDR, ESP_ERR_HTTPD_RESP_SEND };
struct resp_hdr { const char *field, *value; };
struct httpd_req_aux {
    char alignment_skew;
    char scratch[1513];
    unsigned req_hdrs_count, resp_hdrs_count;
    const char *status, *content_type;
    struct resp_hdr resp_hdrs[4];
    bool first_chunk_sent;
};
typedef struct {struct httpd_req_aux *aux;} httpd_req_t;
static bool httpd_valid_req(httpd_req_t *r) { return r->aux != NULL; }
static char output[16384];
static size_t size;
static int calls, fail_call;
static bool check_body;
static esp_err_t httpd_send_all(httpd_req_t *r, const char *b, size_t n) {
    (void)r;
    if (++calls == fail_call) return -1;
    if (check_body && calls > 1) assert(n <= 1024 && ((uintptr_t)b & 3U) == 0);
    assert(size + n < sizeof(output));
    memcpy(output + size, b, n);
    size += n;
    output[size] = 0;
    return ESP_OK;
}
/* RESPONSE_IMPLEMENTATION */
int main(void) {
    struct httpd_req_aux aux = {.status="200 OK", .content_type="text/plain",
        .resp_hdrs_count=1, .resp_hdrs={{"Connection","close"}}};
    httpd_req_t r = {&aux};
    assert(httpd_resp_send(&r, "abc", 3) == ESP_OK);
    assert(calls == 2);
    assert(!strcmp(output, "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 3\r\nConnection: close\r\n\r\nabc"));
    size = 0; calls = 0;
    char block[2048]; memset(block, 'x', sizeof(block));
    assert(httpd_resp_send_chunk(&r, block, 512) == ESP_OK);
    assert(calls == 2);
    assert(strstr(output, "\r\n\r\n200\r\n") != NULL);
    assert(httpd_resp_send_chunk(&r, NULL, 0) == ESP_OK);
    assert(calls == 3 && !strcmp(output + size - 7, "\r\n0\r\n\r\n"));
    aux.first_chunk_sent = false; size = 0; calls = 0;
    assert(httpd_resp_send_chunk(&r, block, sizeof(block)) == ESP_OK);
    assert(calls == 4);
    assert(strstr(output, "\r\n\r\n800\r\n") != NULL);
    assert(httpd_resp_send_chunk(&r, NULL, 2) == ESP_ERR_INVALID_ARG);
    assert(httpd_resp_send_chunk(&r, block, -2) == ESP_ERR_INVALID_ARG);
    fail_call = calls + 1;
    assert(httpd_resp_send_chunk(&r, "x", 1) == ESP_ERR_HTTPD_RESP_SEND);
    char huge[2000]; memset(huge, 'a', sizeof(huge)-1); huge[1999]=0;
    aux.resp_hdrs[0].value = huge;
    assert(httpd_resp_send(&r, "x", 1) == ESP_ERR_HTTPD_RESP_HDR);
    aux.resp_hdrs[0].value = "close";
    static char binary[8193];
    for (unsigned i=0;i<sizeof(binary);++i) binary[i]=(char)(i*131U);
    size = calls = fail_call = 0; check_body = true;
    assert(httpd_resp_send(&r, binary, sizeof(binary)) == ESP_OK);
    const char *body = strstr(output,"\r\n\r\n"); assert(body); body+=4;
    assert(strstr(output,"Content-Length: 8193\r\n"));
    assert(size-(size_t)(body-output)==sizeof(binary));
    assert(!memcmp(body,binary,sizeof(binary)) && calls==10);
    size = calls = 0; fail_call = 4;
    assert(httpd_resp_send(&r,binary,sizeof(binary))==ESP_ERR_HTTPD_RESP_SEND);
    assert(calls==4);
    puts("HTTP response framing passed");
}
