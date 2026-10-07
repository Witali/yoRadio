#include <assert.h>
#include <errno.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include "stream_http_reader.h"
#include "esp_tls_errors.h"
#include "http_parser.h"

enum { ERR_TCP_TRANSPORT_CONNECTION_FAILED=-2,
       ERR_TCP_TRANSPORT_CONNECTION_CLOSED_BY_FIN=-1,
       ERR_TCP_TRANSPORT_CONNECTION_TIMEOUT=0,
       ESP_LOG_WARN, ESP_LOG_DEBUG, HTTP_EVENT_ERROR, HTTP_EVENT_ON_DATA, HTTP_STATE_RES_ON_DATA_START };
typedef int esp_log_level_t;
#define TAG "http"
#define ESP_LOGD(tag,...) do { if(0)printf(__VA_ARGS__); } while(0)
#define ESP_LOGE(tag,...) ESP_LOGD(tag,__VA_ARGS__)
#define ESP_LOG_LEVEL(level,tag,...) do { (void)(level);ESP_LOGD(tag,__VA_ARGS__); } while(0)
typedef struct { char data[256], *raw_data, *orig_raw_data, *output_ptr; int raw_len; } esp_http_buffer_t;
typedef struct { esp_http_buffer_t *buffer; bool is_chunked; int64_t data_process, content_length; } response_t;
typedef struct { int bytes, tls_error; const char *data; } step_t;
typedef struct fake_client esp_http_client_t;
typedef struct { int64_t data_process; esp_http_client_handle_t client; } esp_http_client_on_data_t;
struct fake_client {
    response_t *response;
    bool is_chunk_complete;
    int buffer_size_rx, timeout_ms;
    struct fake_client *transport;
    http_parser parser_storage, *parser;
    http_parser_settings settings_storage, *parser_settings;
    step_t steps[256];
    bool cache_data_in_fetch_hdr;
    int state;
    unsigned next, calls, events, error_queries, closes;
    int tls_error, tls_code;
};
static void esp_http_client_cached_buf_cleanup(esp_http_buffer_t *b) { b->raw_data=NULL; }
/* SDK_HTTP_COMPLETE */
static int esp_transport_read(struct fake_client *c,char *buffer,int size,int timeout) {
    (void)timeout;++c->calls;assert(!c->closes && c->next<256);
    step_t step=c->steps[c->next++];assert(step.bytes<=size);
    if(step.bytes>0) {
        if(step.data)memcpy(buffer,step.data,(size_t)step.bytes);
        else memset(buffer,0x4b,(size_t)step.bytes);
    }
    if(step.tls_error) {c->tls_error=ESP_ERR_MBEDTLS_SSL_READ_FAILED;c->tls_code=step.tls_error;}
    return step.bytes;
}
esp_err_t esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t c,int *code,int *flags) {
    ++c->error_queries;if(code)*code=c->tls_code;if(flags)*flags=0;
    int result=c->tls_error;c->tls_error=c->tls_code=0;return result;
}
esp_err_t esp_http_client_close(esp_http_client_handle_t c) { ++c->closes; return ESP_OK; }
static int esp_transport_translate_error(int error) {return error;}
static const char *esp_err_to_name(int error) {(void)error;return "test";}
static void *esp_transport_get_error_handle(void *c) {return c;}
static void http_dispatch_event(esp_http_client_handle_t c,int event,void *data,int size) {
    (void)event;(void)data;(void)size;++c->events;
}
static void http_dispatch_event_to_event_loop(int event,void *data,size_t size) {
    (void)event;(void)data;(void)size;
}

/* SDK_HTTP_BODY */

static int on_headers(http_parser *p) {
    struct fake_client *c=p->data;
    c->response->content_length=(int64_t)p->content_length;
    // esp_http_client_fetch_headers also uses is_chunked for close-delimited
    // bodies. This seam covers framing, not the SDK's header-name callbacks.
    c->response->is_chunked=(p->flags & F_CHUNKED) || c->response->content_length<=0;
    return 0;
}
static void setup_headers(struct fake_client *c,response_t *r,esp_http_buffer_t *b,const char *headers) {
    memset(c,0,sizeof(*c));memset(r,0,sizeof(*r));memset(b,0,sizeof(*b));
    r->buffer=b;c->response=r;c->transport=c;c->buffer_size_rx=sizeof(b->data);
    c->parser=&c->parser_storage;c->parser_settings=&c->settings_storage;
    http_parser_init(c->parser,HTTP_RESPONSE);c->parser->data=c;
    c->settings_storage.on_headers_complete=on_headers;
    c->settings_storage.on_body=http_on_body;
    c->settings_storage.on_message_complete=http_on_message_complete;
    assert(http_parser_execute(c->parser,c->parser_settings,headers,strlen(headers))==strlen(headers));
    assert(HTTP_PARSER_ERRNO(c->parser)==HPE_OK);
}
static void setup(struct fake_client *c,response_t *r,esp_http_buffer_t *b) {
    setup_headers(c,r,b,"HTTP/1.1 200 OK\r\nContent-Length: 100000\r\n\r\n");
}

/* SDK_HTTP_CLIENT_READ */

// The actual ESP-TLS adapter, with TLS cryptography represented by a scripted
// mbedTLS result. Exercise the current TLS 1.2 configuration explicitly.
typedef struct { int esp_error, tls_code; } test_tls_error_t;
typedef struct { int ssl; test_tls_error_t *error_handle; } esp_tls_t;
enum { ESP_TLS_ERR_TYPE_MBEDTLS, ESP_TLS_ERR_TYPE_ESP };
#define NEWLIB_NANO_SSIZE_T_COMPAT_FORMAT "zx"
#define ESP_INT_EVENT_TRACKER_CAPTURE(handle,kind,value) do { \
    if((kind)==ESP_TLS_ERR_TYPE_ESP)(handle)->esp_error=(value); \
    else (handle)->tls_code=(value); \
} while(0)
static int mbedtls_ssl_read(int *ssl,unsigned char *data,size_t size) { (void)data;(void)size;return *ssl; }
static void mbedtls_print_error_msg(int error) { (void)error; }
/* SDK_TLS_READ */

static unsigned cases;
static void test_partial_fatal(unsigned initial,bool cached,int tls_error) {
    struct fake_client c;response_t r;esp_http_buffer_t b;setup(&c,&r,&b);
    stream_http_reader_t reader={0};char output[128]={0},cache[64];memset(cache,0x4b,sizeof(cache));
    if(cached) {b.raw_len=(int)initial;b.raw_data=cache;}
    else if(initial)c.steps[0]=(step_t){.bytes=(int)initial,.tls_error=0};
    c.steps[!cached && initial ? 1:0]=(step_t){.bytes=ERR_TCP_TRANSPORT_CONNECTION_FAILED,.tls_error=tls_error};
    int result=stream_http_read(&reader,&c,output,sizeof(output));
    assert(result==(initial?(int)initial:ESP_FAIL));assert(reader.failed && c.closes==1);
    for(unsigned i=0;i<initial;++i)assert(output[i]==0x4b);
    unsigned calls=c.calls,queries=c.error_queries;
    for(unsigned i=0;i<3;++i)assert(stream_http_read(&reader,&c,output,sizeof(output))==ESP_FAIL);
    assert(c.calls==calls && c.error_queries==queries);++cases;
}
static void test_retry(int temporary,unsigned initial) {
    struct fake_client c;response_t r;esp_http_buffer_t b;setup(&c,&r,&b);
    stream_http_reader_t reader={0};char output[128];
    if(initial)c.steps[0]=(step_t){.bytes=(int)initial,.tls_error=0};
    c.steps[initial?1:0]=(step_t){.bytes=ERR_TCP_TRANSPORT_CONNECTION_TIMEOUT,.tls_error=temporary};
    c.steps[initial?2:1]=(step_t){.bytes=128,.tls_error=0};
    assert(stream_http_read(&reader,&c,output,sizeof(output))==(initial?(int)initial:-ESP_ERR_HTTP_EAGAIN));
    assert(!reader.failed && !c.closes);
    assert(stream_http_read(&reader,&c,output,sizeof(output))==128);assert(!reader.failed && !c.closes);++cases;
}
static void test_framing(const char *headers,const char *wire,const char *expected,
                         bool complete,unsigned fragment,int transport_error,int tls_error) {
    struct fake_client c;response_t r;esp_http_buffer_t b;setup_headers(&c,&r,&b,headers);
    stream_http_reader_t reader={0};char output[128],all[256]={0};size_t total=0;
    unsigned count=0;
    for(size_t at=0;at<strlen(wire);) {
        size_t size=strlen(wire)-at;if(size>fragment)size=fragment;
        c.steps[count++]=(step_t){.bytes=(int)size,.data=wire+at};at+=size;
    }
    // FIN/error may follow partial valid bytes. Repeat it only if the SDK
    // returns those bytes before it surfaces the incomplete body.
    for(unsigned i=0;i<3;++i)c.steps[count++]=(step_t){.bytes=transport_error,.tls_error=tls_error};
    int result=0;
    for(unsigned call=0;call<8;++call) {
        result=stream_http_read(&reader,&c,output,sizeof(output));
        if(result<=0)break;
        assert(total+(size_t)result<sizeof(all));memcpy(all+total,output,(size_t)result);total+=(size_t)result;
    }
    assert(total==strlen(expected) && !memcmp(all,expected,total));
    assert(complete ? result==0 && !reader.failed : result==ESP_FAIL && reader.failed);
    unsigned calls=c.calls;
    if(reader.failed)assert(stream_http_read(&reader,&c,output,sizeof(output))==ESP_FAIL && c.calls==calls);
    ++cases;
}
static void test_tls_adapter(void) {
    const int results[]={MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY,0,MBEDTLS_ERR_SSL_ALLOC_FAILED,
        MBEDTLS_ERR_SSL_INVALID_MAC,ESP_TLS_ERR_SSL_TIMEOUT,ESP_TLS_ERR_SSL_WANT_READ,
        ESP_TLS_ERR_SSL_WANT_WRITE};
    for(unsigned i=0;i<sizeof(results)/sizeof(results[0]);++i) {
        test_tls_error_t errors={0};esp_tls_t tls={.ssl=results[i],.error_handle=&errors};char data[8];
        ssize_t result=esp_mbedtls_read(&tls,data,sizeof(data));
        assert(result==(i==0?0:results[i]));
        bool recorded=i>=2 && i<=4;
        assert(errors.esp_error==(recorded?ESP_ERR_MBEDTLS_SSL_READ_FAILED:0));
        assert(errors.tls_code==(recorded?-results[i]:0));++cases;
    }
    puts("TLS_ADAPTER_PASS close_alert_and_raw_EOF_collapse_to_zero; timeout_records_read_failed; WANT_codes_not_recorded");
}
static void test_chunked_timeout(void) {
    struct fake_client c;response_t r;esp_http_buffer_t b;
    setup_headers(&c,&r,&b,"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n");
    c.steps[0]=(step_t){.bytes=5,.data="3\r\nAB"};
    c.steps[1]=(step_t){.bytes=0,.tls_error=-ESP_TLS_ERR_SSL_TIMEOUT};
    c.steps[2]=(step_t){.bytes=8,.data="C\r\n0\r\n\r\n"};
    stream_http_reader_t reader={0};char output[128];
    assert(stream_http_read(&reader,&c,output,sizeof(output))==2 && !memcmp(output,"AB",2));
    assert(!reader.failed && !c.closes);
    assert(stream_http_read(&reader,&c,output,sizeof(output))==1 && output[0]=='C');
    assert(stream_http_read(&reader,&c,output,sizeof(output))==0 && !reader.failed);++cases;
}

static void test_protocol(void) {
    const char *length="HTTP/1.1 200 OK\r\nContent-Length: 8\r\n\r\n";
    const char *chunked="HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n";
    const char *closed="HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n";
    for(unsigned fragment=1;fragment<=8;fragment*=2) {
        test_framing(length,"ABCDEFGH","ABCDEFGH",true,fragment,-1,0);
        test_framing(length,"ABC","ABC",false,fragment,-1,0);
        test_framing(chunked,"3;foo=bar\r\nABC\r\n5\r\nDEFGH\r\n0\r\nX-Trailer: ok\r\n\r\n","ABCDEFGH",true,fragment,-1,0);
        test_framing(chunked,"3\r\nABC\r\n","ABC",false,fragment,-1,0);
        test_framing(chunked,"3\r\nAB","AB",false,fragment,-1,0);
        test_framing(chunked,"3\r\nABC\r\nZ\r\n","ABC",false,fragment,-1,0);
        test_framing(closed,"ABCDEFGH","ABCDEFGH",true,fragment,-1,0);
        test_framing(closed,"ABCDEFGH","ABCDEFGH",false,fragment,-2,-MBEDTLS_ERR_SSL_INVALID_MAC);
    }
    // Both explicit message boundaries are complete even without a peer FIN:
    // a transport read after the boundary would hit a deliberately fatal step.
    test_framing(length,"ABCDEFGH","ABCDEFGH",true,8,-2,-MBEDTLS_ERR_SSL_INVALID_MAC);
    test_framing(chunked,"8\r\nABCDEFGH\r\n0\r\n\r\n","ABCDEFGH",true,1,-2,-MBEDTLS_ERR_SSL_INVALID_MAC);
    puts("HTTP_FRAMING_PASS content_length chunked extensions trailers truncated malformed fragmented close_delimited");
    puts("KNOWN_SDK_LIMITATION close_notify_and_bare_TLS_EOF_are_indistinguishable_at_HTTP_API");
}

int main(void) {
    // TLS allocation failure and invalid authenticated record: valid preceding
    // bytes survive, but the damaged connection is never read a second time.
    for(unsigned initial=0;initial<=64;initial+=32)
        for(unsigned cached=0;cached<2;++cached)
            for(unsigned error=0;error<2;++error)
                test_partial_fatal(initial,cached,error?-MBEDTLS_ERR_SSL_INVALID_MAC:-MBEDTLS_ERR_SSL_ALLOC_FAILED);
    for(unsigned initial=0;initial<=64;initial+=32) {
        test_retry(0,initial);
        test_retry(-ESP_TLS_ERR_SSL_TIMEOUT,initial);
        test_retry(-ESP_TLS_ERR_SSL_WANT_READ,initial);
        test_retry(-ESP_TLS_ERR_SSL_WANT_WRITE,initial);
    }
    struct fake_client c;response_t r;esp_http_buffer_t b;setup(&c,&r,&b);
    stream_http_reader_t reader={0};char output[128];
    c.steps[0]=(step_t){.bytes=64,.tls_error=0};c.steps[1]=(step_t){.bytes=64,.tls_error=0};
    assert(stream_http_read(&reader,&c,output,sizeof(output))==128 && !reader.failed);++cases;
    r.content_length=r.data_process;
    assert(stream_http_read(&reader,&c,output,sizeof(output))==0 && !reader.failed);++cases;
    // A stale fatal TLS error must not be relabelled as a clean completed EOF.
    c.tls_error=ESP_ERR_MBEDTLS_SSL_READ_FAILED;c.tls_code=-MBEDTLS_ERR_SSL_ALLOC_FAILED;
    assert(stream_http_read(&reader,&c,output,sizeof(output))==ESP_FAIL && reader.failed);++cases;
    // Demonstrate the SDK behavior without the wrapper as a negative control.
    setup(&c,&r,&b);c.steps[0]=(step_t){.bytes=32,.tls_error=0};c.steps[1]=(step_t){.bytes=-2,.tls_error=-MBEDTLS_ERR_SSL_ALLOC_FAILED};
    assert(esp_http_client_read(&c,output,sizeof(output))==32 && c.calls==2);
    c.steps[2]=(step_t){.bytes=-2,.tls_error=-MBEDTLS_ERR_SSL_ALLOC_FAILED};assert(esp_http_client_read(&c,output,sizeof(output))==ESP_FAIL && c.calls==3);++cases;
    test_protocol();
    test_chunked_timeout();
    test_tls_adapter();
    printf("STREAM_HTTP_READER_PASS cases=%u partial_bytes_preserved=true fatal_retry=false temporary_retry=true sdk_control_retries=true\n",cases);
}
