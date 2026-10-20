#include <assert.h>
#include <errno.h>
#include <inttypes.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "esp_log.h"
#include "http_header.h"

#define CHECK(c,m) do { if (!(c)) { fprintf(stderr,"SEMANTIC_FAILURE:%s:%u\n",m,__LINE__); exit(80); } } while(0)
enum { HTTP_METHOD_GET, HTTP_METHOD_HEAD, HTTP_METHOD_DELETE, HTTP_METHOD_POST };
enum { HTTP_STATE_UNINIT, HTTP_STATE_INIT, HTTP_STATE_CONNECTED,
       HTTP_STATE_REQ_COMPLETE_HEADER, HTTP_STATE_REQ_COMPLETE_DATA,
       HTTP_STATE_RES_COMPLETE_HEADER, HTTP_STATE_RES_ON_DATA_START };
enum { HTTP_EVENT_HEADERS_SENT, HTTP_EVENT_ERROR,
       ESP_ERR_HTTP_WRITE_DATA=100, ESP_ERR_HTTP_EAGAIN=101,
       ERR_TCP_TRANSPORT_CONNECTION_TIMEOUT=-2,
       ERR_TCP_TRANSPORT_CONNECTION_CLOSED_BY_FIN=-3 };
enum { ESP_LOG_WARN, ESP_LOG_DEBUG };
typedef int esp_log_level_t;
#define DEFAULT_HTTP_PROTOCOL "HTTP/1.1"
#define TAG "cyd-request-buffer-test"
static const char *HTTP_METHOD_MAPPING[]={"GET","HEAD","DELETE","POST"};
typedef struct { char *data,*orig_raw_data,*raw_data,*output_ptr; int raw_len; } esp_http_buffer_t;
typedef struct { esp_http_buffer_t *buffer; http_header_handle_t headers; } request_t;
typedef struct { esp_http_buffer_t *buffer; int64_t data_process,content_length; bool is_chunked; } response_t;
typedef struct client {
    request_t *request; response_t *response;
    struct { int method; const char *path,*query; } connection_info;
    int buffer_size_tx,buffer_size_rx,header_index,data_written_index,data_write_left,post_len,state,timeout_ms;
    bool first_line_prepared,is_async,is_chunk_complete;
    char *post_data;
    void *parser,*parser_settings;
    struct client *transport;
    char wire[65536]; size_t written;
    int write_limit,fail_write,events,closes;
} client_t,*esp_http_client_handle_t;
typedef struct { void *pointer; size_t size; bool live; } allocation_t;
static allocation_t allocations[256];
static unsigned allocated,released,live,requested_tx_bytes;
static size_t expected_tx_allocation;
static bool fail_malloc;

static void *owned_alloc(size_t size) {
    void *pointer=malloc(size);CHECK(pointer&&allocated<256,"fixture_allocation");
    allocations[allocated++]=(allocation_t){pointer,size,true};++live;
    return pointer;
}
static allocation_t *find_live(void *pointer) {
    for(unsigned i=allocated;i>0;--i)
        if(allocations[i-1].pointer==pointer&&allocations[i-1].live)return &allocations[i-1];
    return NULL;
}
static void checked_free(void *pointer) {
    if(!pointer)return;
    allocation_t *entry=find_live(pointer);
    CHECK(entry,"free_only_once_and_owned");entry->live=false;--live;++released;free(pointer);
}
static void *checked_malloc(size_t size) {
    CHECK(size==expected_tx_allocation,"requested_capacity_restored");
    requested_tx_bytes+=(unsigned)size;
    if(fail_malloc){fail_malloc=false;return NULL;}
    return owned_alloc(size);
}
static int checked_snprintf(char *buffer,size_t size,const char *format,...) {
    bool valid=false;
    for(unsigned i=0;i<allocated;++i){allocation_t *a=&allocations[i];
        uintptr_t at=(uintptr_t)buffer,start=(uintptr_t)a->pointer;
        if(a->live&&at>=start&&at-start<a->size&&size<=a->size-(at-start))valid=true;
    }
    CHECK(valid,"tx_buffer_live_before_request_write");
    va_list args;va_start(args,format);int result=vsnprintf(buffer,size,format,args);va_end(args);return result;
}
static int esp_transport_write(client_t *c,const char *data,int size,int timeout) {
    (void)timeout;
    if(c->fail_write){errno=EAGAIN;return -1;}
    if(c->write_limit&&size>c->write_limit)size=c->write_limit;
    CHECK(size>=0&&c->written+(size_t)size<sizeof(c->wire),"wire_capacity");
    memcpy(c->wire+c->written,data,(size_t)size);c->written+=(size_t)size;c->wire[c->written]=0;return size;
}
static int esp_http_client_write(client_t *c,const char *data,int size){return esp_transport_write(c,data,size,0);}
static int esp_http_client_close(client_t *c){++c->closes;c->state=HTTP_STATE_INIT;return ESP_OK;}
static int esp_http_client_set_header(client_t *c,const char *key,const char *value){return http_header_set(c->request->headers,key,value);}
esp_err_t yoradio_http_client_release_request_buffer(client_t *c);
static void http_dispatch_event(client_t *c,int event,void *data,int size) {
    (void)data;(void)size;++c->events;
    if(event==HTTP_EVENT_HEADERS_SENT){
        CHECK(yoradio_http_client_release_request_buffer(c)==ESP_ERR_INVALID_STATE,
              "headers_sent_cannot_release_tx");
        CHECK(c->request->buffer->data,"headers_sent_keeps_request_storage");
    }
}
static void http_dispatch_event_to_event_loop(int event,void *data,size_t size){(void)event;(void)data;(void)size;}
static int esp_transport_read(client_t *c,char *data,int bytes,int timeout){(void)c;(void)data;(void)bytes;(void)timeout;CHECK(false,"cached_body_needs_no_transport_read");return -1;}
static int http_parser_execute(void *parser,void *settings,const char *data,size_t size){(void)parser;(void)settings;(void)data;(void)size;CHECK(false,"cached_body_needs_no_parser");return 0;}
static int esp_transport_translate_error(int code){return code;}
static const char *esp_err_to_name(int code){(void)code;return "fixture";}
static void *esp_transport_get_error_handle(client_t *c){(void)c;return NULL;}

#define malloc checked_malloc
#define free checked_free
#define snprintf checked_snprintf
#include "sdk-functions.inc"
#undef snprintf
#undef free
#undef malloc

static void setup(client_t *c,unsigned tx_size) {
    memset(c,0,sizeof(*c));expected_tx_allocation=tx_size;
    c->request=owned_alloc(sizeof(*c->request));memset(c->request,0,sizeof(*c->request));
    c->request->buffer=owned_alloc(sizeof(*c->request->buffer));memset(c->request->buffer,0,sizeof(*c->request->buffer));
    c->request->buffer->data=checked_malloc(tx_size);
    c->request->headers=http_header_init();CHECK(c->request->headers,"real_header_dictionary");
    c->response=owned_alloc(sizeof(*c->response));memset(c->response,0,sizeof(*c->response));
    c->response->buffer=owned_alloc(sizeof(*c->response->buffer));memset(c->response->buffer,0,sizeof(*c->response->buffer));
    c->response->buffer->data=owned_alloc(2048);
    c->transport=c;c->buffer_size_tx=(int)tx_size;c->buffer_size_rx=2048;c->state=HTTP_STATE_CONNECTED;
    c->connection_info.path="/radio";c->write_limit=17;
    CHECK(http_header_set(c->request->headers,"Host","example.test")==ESP_OK,"host_header");
}
static void destroy(client_t *c) {
    // Exact request-buffer free portion of the real SDK cleanup function.
    cleanup_sdk_request(c);c->request=NULL;
    esp_http_client_cached_buf_cleanup(c->response->buffer);
    checked_free(c->response->buffer->data);checked_free(c->response->buffer);checked_free(c->response);c->response=NULL;
    CHECK(!live&&allocated==released,"every_owned_allocation_freed_once");
}
static void accepted(client_t *c){c->state=HTTP_STATE_RES_ON_DATA_START;c->data_write_left=0;c->post_len=0;}
static void prepare_retry(client_t *c) {
    // Response/auth/redirect preparation is a state seam; the full SDK prepare
    // and auth handlers remain byte-identical, not claimed executed here.
    c->state=HTTP_STATE_CONNECTED;c->first_line_prepared=false;c->written=0;c->wire[0]=0;
}

int main(int argc,char **argv) {
    CHECK(argc==2,"case_argument");const char *name=argv[1];client_t c;
    if(!strcmp(name,"invalid")){
        CHECK(yoradio_http_client_release_request_buffer(NULL)==ESP_ERR_INVALID_ARG,"null_rejected");
        memset(&c,0,sizeof(c));CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_ERR_INVALID_ARG,"null_request_rejected");
        request_t request={0};c.request=&request;CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_ERR_INVALID_ARG,"null_buffer_rejected");
    }else if(!strcmp(name,"long-reuse")||!strcmp(name,"capacity8192")){
        unsigned capacity=!strcmp(name,"capacity8192")?8192:4096;setup(&c,capacity);
        char path[3002],query[400],value[901];memset(path,'a',sizeof(path)-1);path[0]='/';path[sizeof(path)-1]=0;
        memset(query,'q',sizeof(query)-1);query[sizeof(query)-1]=0;memset(value,'b',900);value[900]=0;
        c.connection_info.path=path;c.connection_info.query=query;
        for(int i=0;i<6;++i){char key[32];snprintf(key,sizeof(key),"X-Test-%d",i);CHECK(http_header_set(c.request->headers,key,value)==ESP_OK,"large_header");}
        CHECK(esp_http_client_request_send(&c,0)==ESP_OK&&c.written>8000,"real_sdk_paginates_long_request");
        char expected[sizeof(c.wire)];strcpy(expected,c.wire);accepted(&c);
        CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_OK&&!c.request->buffer->data,"completed_get_releases_tx");
        for(unsigned i=0;i<20;++i){prepare_retry(&c);CHECK(esp_http_client_request_send(&c,0)==ESP_OK,"released_get_can_reuse_handle");
            CHECK(!strcmp(c.wire,expected),"full_request_wire_identical_after_reuse");accepted(&c);
            CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_OK&&!c.request->buffer->data,"reused_get_releases_again");}
        destroy(&c);
    }else if(!strcmp(name,"idempotent")){
        setup(&c,4096);accepted(&c);unsigned before=released;
        CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_OK&&!c.request->buffer->data,"release_nulls_pointer");
        CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_OK&&released==before+1,"idempotent_release_no_double_free");destroy(&c);
    }else if(!strcmp(name,"oom")){
        setup(&c,4096);accepted(&c);CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_OK,"release_before_oom");prepare_retry(&c);
        fail_malloc=true;errno=EAGAIN;
        CHECK(esp_http_client_request_send(&c,0)==ESP_ERR_NO_MEM&&!c.request->buffer->data&&!c.written&&errno==0,"oom_keeps_reuse_retryable_without_wire");
        CHECK(esp_http_client_request_send(&c,0)==ESP_OK&&c.request->buffer->data,"oom_retry_restores_original_capacity");destroy(&c);
    }else if(!strcmp(name,"partial-null")){
        setup(&c,4096);accepted(&c);CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_OK,"release_before_invalid_partial");
        c.first_line_prepared=true;unsigned count=allocated;
        CHECK(esp_http_client_request_send(&c,0)==ESP_ERR_INVALID_STATE&&!c.request->buffer->data&&allocated==count&&!c.written,"unknown_partial_state_never_reallocated");destroy(&c);
    }else if(!strcmp(name,"states")){
        setup(&c,4096);for(int state=HTTP_STATE_UNINIT;state<HTTP_STATE_RES_ON_DATA_START;++state){c.state=state;char *pointer=c.request->buffer->data;
            CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_ERR_INVALID_STATE&&c.request->buffer->data==pointer,"incomplete_state_preserves_tx");}
        destroy(&c);
    }else if(!strcmp(name,"async")||!strcmp(name,"body-pending")||!strcmp(name,"write-pending")||!strcmp(name,"post")||!strcmp(name,"head")){
        setup(&c,4096);accepted(&c);char *pointer=c.request->buffer->data;
        if(!strcmp(name,"async"))c.is_async=true;else if(!strcmp(name,"body-pending"))c.post_len=1;
        else if(!strcmp(name,"write-pending"))c.data_write_left=1;else c.connection_info.method=!strcmp(name,"post")?HTTP_METHOD_POST:HTTP_METHOD_HEAD;
        CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_ERR_INVALID_STATE&&c.request->buffer->data==pointer,"nonfinal_get_rejected_without_free");destroy(&c);
    }else if(!strcmp(name,"write-failure")||!strcmp(name,"async-partial")){
        setup(&c,4096);char *pointer=c.request->buffer->data;unsigned count=allocated;
        if(!strcmp(name,"write-failure"))c.fail_write=1;
        else {c.is_async=true;c.first_line_prepared=true;c.data_write_left=4;memcpy(pointer,"GET ",4);c.write_limit=2;}
        CHECK(esp_http_client_request_send(&c,0)==ESP_ERR_HTTP_WRITE_DATA&&c.request->buffer->data==pointer&&allocated==count,"failed_or_partial_write_keeps_same_storage");
        CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_ERR_INVALID_STATE&&c.request->buffer->data==pointer,"failed_or_partial_write_cannot_release");destroy(&c);
    }else if(!strcmp(name,"borrowed-body")){
        setup(&c,4096);char body[]="borrowed-body";c.post_data=body;accepted(&c);
        CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_OK&&c.post_data==body&&!strcmp(body,"borrowed-body"),"release_preserves_borrowed_post_data");
        prepare_retry(&c);c.connection_info.method=HTTP_METHOD_POST;c.post_len=(int)strlen(body);
        CHECK(esp_http_client_request_send(&c,c.post_len)==ESP_OK,"released_get_reuses_for_post_headers");size_t headers=c.written;
        c.write_limit=0;CHECK(esp_http_client_send_post_data(&c)==ESP_OK&&c.state==HTTP_STATE_REQ_COMPLETE_DATA,"actual_sdk_sends_borrowed_body");
        CHECK(c.post_data==body&&!strcmp(c.wire+headers,body),"post_body_wire_and_owner_preserved");destroy(&c);
    }else if(!strcmp(name,"authorization")){
        setup(&c,4096);CHECK(http_header_set(c.request->headers,"Authorization","Basic dGVzdDp0ZXN0")==ESP_OK,"auth_header");
        CHECK(esp_http_client_request_send(&c,0)==ESP_OK,"initial_authorized_send");accepted(&c);
        CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_OK,"release_authorized_get");prepare_retry(&c);c.connection_info.path="/redirected";
        CHECK(http_header_set(c.request->headers,"Authorization","Digest username=\"fixture\", response=\"retained\"")==ESP_OK,"retry_auth_header_update");
        CHECK(esp_http_client_request_send(&c,0)==ESP_OK&&strstr(c.wire,"GET /redirected HTTP/1.1\r\n")&&strstr(c.wire,"Digest username=\"fixture\", response=\"retained\""),"auth_dictionary_and_redirected_path_remain_reusable");destroy(&c);
    }else if(!strcmp(name,"cached-body")){
        setup(&c,4096);const char expected[]="cached response body";esp_http_buffer_t *buffer=c.response->buffer;
        buffer->orig_raw_data=owned_alloc(sizeof(expected));memcpy(buffer->orig_raw_data,expected,sizeof(expected));buffer->raw_data=buffer->orig_raw_data;buffer->raw_len=(int)strlen(expected);
        c.response->content_length=c.response->data_process=(int64_t)strlen(expected);accepted(&c);char *rx=buffer->data;
        CHECK(yoradio_http_client_release_request_buffer(&c)==ESP_OK&&buffer->data==rx&&buffer->raw_data==buffer->orig_raw_data,"release_preserves_response_and_cached_body");
        char output[sizeof(expected)]={0};CHECK(esp_http_client_read(&c,output,6)==6&&!memcmp(output,expected,6),"actual_sdk_reads_retained_cached_prefix");
        int remaining=(int)strlen(expected)-6;CHECK(esp_http_client_read(&c,output+6,remaining)==remaining&&!strcmp(output,expected),"actual_sdk_reads_retained_cached_suffix");
        CHECK(!buffer->orig_raw_data&&!buffer->raw_data&&!buffer->raw_len&&buffer->data==rx,"cached_rx_cleanup_stays_independent_of_tx");destroy(&c);
    }else CHECK(false,"known_case");
    CHECK(!live,"case_leak_free");printf("PASS:%s requested_tx_payload_bytes=%u\n",name,requested_tx_bytes);return 0;
}
