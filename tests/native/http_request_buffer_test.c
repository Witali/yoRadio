#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "esp_log.h"
#include "http_header.h"

enum { HTTP_METHOD_GET, HTTP_METHOD_HEAD, HTTP_METHOD_DELETE, HTTP_METHOD_POST };
enum { HTTP_STATE_INIT, HTTP_STATE_CONNECTED, HTTP_STATE_REQ_COMPLETE_HEADER,
       HTTP_STATE_REQ_COMPLETE_DATA, HTTP_STATE_RES_COMPLETE_HEADER, HTTP_STATE_RES_ON_DATA_START };
enum { HTTP_EVENT_HEADERS_SENT, ESP_ERR_HTTP_WRITE_DATA=100, ESP_ERR_HTTP_HEADER_TOO_LONG=101 };
#define CONFIG_ESP_HTTP_CLIENT_STRICT_HEADER_BUFFER 1
#define DEFAULT_HTTP_PROTOCOL "HTTP/1.1"
#define TAG "request-buffer-test"
static const char *HTTP_METHOD_MAPPING[] = {"GET","HEAD","DELETE","POST"};
typedef struct { char *data; } buffer_t;
typedef struct { buffer_t *buffer; http_header_handle_t headers; } request_t;
typedef struct client {
    request_t *request;
    struct { int method; const char *path, *query; } connection_info;
    int buffer_size_tx, header_index, data_written_index, data_write_left, post_len, state, timeout_ms;
    bool first_line_prepared, is_async;
    struct client *transport;
    char wire[32768]; size_t written;
    int write_limit, fail_write, closes, events;
} client_t, *esp_http_client_handle_t;
static bool fail_malloc;
static unsigned live, allocations, frees, cases;
static void *tracked_malloc(size_t size) {
    assert(size==4096);
    if(fail_malloc) { fail_malloc=false; return NULL; }
    void *result=malloc(size); assert(result); ++live; ++allocations; return result;
}
static void tracked_free(void *p) { if(p) { assert(live);--live;++frees; } free(p); }
static int esp_transport_write(client_t *c,const char *data,int size,int timeout) {
    (void)timeout;
    if(c->fail_write) {errno=EAGAIN;return -1;}
    if(c->write_limit && size>c->write_limit)size=c->write_limit;
    assert(c->written+(size_t)size<sizeof(c->wire));
    memcpy(c->wire+c->written,data,size);c->written+=size;c->wire[c->written]=0;
    return size;
}
static int esp_http_client_write(client_t *c,const char *data,int size) {return esp_transport_write(c,data,size,0);}
static int esp_http_client_close(client_t *c) {++c->closes;c->state=HTTP_STATE_INIT;return ESP_OK;}
static int esp_http_client_set_header(client_t *c,const char *key,const char *value) {return http_header_set(c->request->headers,key,value);}
esp_err_t yoradio_http_client_release_request_buffer(client_t *c);
static void http_dispatch_event(client_t *c,int event,void *data,int size) {
    (void)event;(void)data;(void)size;++c->events;
    assert(yoradio_http_client_release_request_buffer(c)==ESP_ERR_INVALID_STATE);
    assert(c->request->buffer->data); /* Too early at HEADERS_SENT. */
}
static void http_dispatch_event_to_event_loop(int event,void *data,size_t size) {(void)event;(void)data;(void)size;}
#define malloc tracked_malloc
#define free tracked_free
/* SDK_REQUEST_FUNCTIONS */
/* SDK_RELEASE_FUNCTION */
#undef malloc
#undef free

static void setup(client_t *c,request_t *r,buffer_t *b) {
    memset(c,0,sizeof(*c));
    b->data=tracked_malloc(4096);r->buffer=b;r->headers=http_header_init();assert(r->headers);
    c->request=r;c->transport=c;c->buffer_size_tx=4096;c->state=HTTP_STATE_CONNECTED;
    c->connection_info.path="/radio";c->write_limit=17;
    assert(http_header_set(r->headers,"Host","example.test")==ESP_OK);
}
static void destroy(client_t *c) {tracked_free(c->request->buffer->data);c->request->buffer->data=NULL;http_header_destroy(c->request->headers);assert(live==0);}
static void accepted(client_t *c) {c->state=HTTP_STATE_RES_ON_DATA_START;c->data_write_left=0;c->post_len=0;}

int main(void) {
    client_t c; request_t r; buffer_t b;
    assert(yoradio_http_client_release_request_buffer(NULL)==ESP_ERR_INVALID_ARG);++cases;
    setup(&c,&r,&b);
    char path[3002];memset(path,'a',sizeof(path)-1);path[0]='/';path[sizeof(path)-1]=0;c.connection_info.path=path;
    char value[901];memset(value,'b',900);value[900]=0;
    for(int i=0;i<6;++i) {char key[32];snprintf(key,sizeof(key),"X-Test-%d",i);assert(http_header_set(r.headers,key,value)==ESP_OK);}
    assert(esp_http_client_request_send(&c,0)==ESP_OK && c.written>8000 && c.events==1);
    char expected[sizeof(c.wire)];strcpy(expected,c.wire);
    accepted(&c);assert(yoradio_http_client_release_request_buffer(&c)==ESP_OK && !b.data && live==0);++cases;
    unsigned released=frees;assert(yoradio_http_client_release_request_buffer(&c)==ESP_OK && frees==released);++cases;
    /* Reopen/redirect preparation retains the original full request capacity. */
    for(int i=0;i<20;++i) {
        c.state=HTTP_STATE_CONNECTED;c.first_line_prepared=false;c.written=0;
        assert(esp_http_client_request_send(&c,0)==ESP_OK && live==1);
        assert(strcmp(c.wire,expected)==0);
        accepted(&c);assert(yoradio_http_client_release_request_buffer(&c)==ESP_OK && live==0);++cases;
    }
    c.state=HTTP_STATE_CONNECTED;fail_malloc=true;errno=EAGAIN;c.written=0;
    assert(esp_http_client_request_send(&c,0)==ESP_ERR_NO_MEM && !b.data && !c.written && errno==0);++cases;
    assert(esp_http_client_request_send(&c,0)==ESP_OK);accepted(&c);
    assert(yoradio_http_client_release_request_buffer(&c)==ESP_OK);
    c.first_line_prepared=true;assert(esp_http_client_request_send(&c,0)==ESP_ERR_INVALID_STATE && !b.data);++cases;
    c.first_line_prepared=false;destroy(&c);

    for(int state=HTTP_STATE_INIT;state<HTTP_STATE_RES_ON_DATA_START;++state) {
        setup(&c,&r,&b);c.state=state;
        assert(yoradio_http_client_release_request_buffer(&c)==ESP_ERR_INVALID_STATE && b.data && live==1);destroy(&c);++cases;
    }
    for(int variant=0;variant<4;++variant) {
        setup(&c,&r,&b);accepted(&c);
        if(variant==0)c.is_async=true;
        if(variant==1)c.connection_info.method=HTTP_METHOD_POST;
        if(variant==2)c.post_len=128;
        if(variant==3)c.data_write_left=1;
        assert(yoradio_http_client_release_request_buffer(&c)==ESP_ERR_INVALID_STATE && b.data);destroy(&c);++cases;
    }
    setup(&c,&r,&b);c.fail_write=1;
    assert(esp_http_client_request_send(&c,0)==ESP_ERR_HTTP_WRITE_DATA && b.data && live==1);
    assert(yoradio_http_client_release_request_buffer(&c)==ESP_ERR_INVALID_STATE);destroy(&c);++cases;
    /* Existing asynchronous leftover bytes must not be reallocated/released. */
    setup(&c,&r,&b);c.is_async=true;c.first_line_prepared=true;c.data_write_left=4;
    memcpy(b.data,"GET ",4);c.write_limit=2;char *owned=b.data;unsigned count=allocations;
    assert(esp_http_client_request_send(&c,0)==ESP_ERR_HTTP_WRITE_DATA && b.data==owned && allocations==count);
    assert(c.data_write_left==2);destroy(&c);++cases;
    assert(allocations==frees);
    printf("HTTP_REQUEST_BUFFER_PASS cases=%u released_bytes=4096\n",cases);
}
