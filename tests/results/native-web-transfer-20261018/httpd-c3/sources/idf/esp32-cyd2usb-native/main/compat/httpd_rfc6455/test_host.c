/* Host seams execute extracted generated SDK functions unchanged. These structs
 * model fields, not target ABI; the real SDK build checks matching private ABI. */
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <limits.h>
#include <sys/types.h>
#include "http_parser.h"
#define CONFIG_HTTPD_WS_SUPPORT 1
#define CONFIG_HTTPD_WS_STRICTER_RFC6455 1
#define CONFIG_HTTPD_PURGE_BUF_LEN 32
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_INVALID_ARG 1
#define ESP_ERR_INVALID_STATE 2
#define ESP_ERR_INVALID_SIZE 3
#define ESP_ERR_INVALID_VERSION 4
#define ESP_ERR_NOT_FOUND 5
#define ESP_ERR_HTTPD_RESULT_TRUNC 6
#define HTTPD_RECV_OPT_NONE 0
#define HTTPD_RECV_OPT_HALT_AFTER_PENDING 1
#define HTTPD_RECV_OPT_BLOCKING 2
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
#define HTTPD_SOCK_ERR_FAIL (-2)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGD(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef int esp_err_t;
typedef void *httpd_handle_t;
typedef enum { HTTPD_WS_TYPE_CONTINUE=0, HTTPD_WS_TYPE_TEXT=1, HTTPD_WS_TYPE_BINARY=2,
    HTTPD_WS_TYPE_CLOSE=8, HTTPD_WS_TYPE_PING=9, HTTPD_WS_TYPE_PONG=10 } httpd_ws_type_t;
typedef struct { bool final, fragmented; httpd_ws_type_t type; uint8_t *payload; size_t len,left_len; } httpd_ws_frame_t;
struct sock_db { bool ws_close,ws_handshake_done,ws_control_frames,ignore_sess_ctx_changes;
    int fd; void *ctx,*handle; void (*free_ctx)(void *); int (*send_fn)(void *,int,const char *,size_t,int);
    int (*recv_fn)(void *,int,char *,size_t,int); uint8_t pending_data[128]; size_t pending_len; };
struct httpd_req_aux { struct sock_db *sd; char *scratch; size_t scratch_cur_size,scratch_size_limit;
    size_t remaining_len; unsigned req_hdrs_count; bool ws_final; httpd_ws_type_t ws_type; uint8_t mask_key[4];
    bool ws_handshake_detect; size_t max_uri_len,max_req_hdr_len; struct http_parser_url url_parse_res; };
typedef struct httpd_req { void *handle,*aux,*sess_ctx,*user_ctx; void (*free_ctx)(void *); bool ignore_sess_ctx_changes;
    int method; char uri[513]; size_t content_len; } httpd_req_t;
struct httpd_data { httpd_req_t hd_req; int http_server_state; };
static struct sock_db session;
static struct httpd_req_aux aux;
static struct httpd_data server;
static uint8_t input[2048],output[70000];
static size_t input_size,input_offset,output_size;
static unsigned queue_calls,cases;
static bool short_send;
static char response_status[64], response_version[8];

static int wire_send(void *handle,int fd,const char *data,size_t size,int flags) {
    (void)handle;(void)flags; assert(fd==42 && size<=sizeof(output)-output_size);
    if(short_send && size) --size;
    memcpy(output+output_size,data,size);output_size+=size;return (int)size;
}
static int httpd_send(httpd_req_t *req,const char *data,size_t size) {return wire_send(req->handle,42,data,size,0);}
static struct sock_db *httpd_sess_get(void *hd,int fd) {(void)hd;return fd==42?&session:NULL;}
static int httpd_req_to_sockfd(httpd_req_t *req) {(void)req;return 42;}
#ifdef NATIVE_TEST_WIRE
typedef int httpd_recv_opt_t;
static size_t socket_step;
static int wire_receive(void *handle,int fd,char *data,size_t size,int flags) {
    (void)handle;(void)flags;assert(fd==42 && input_offset<=input_size);
    if(size>input_size-input_offset)size=input_size-input_offset;
    if(size>socket_step)size=socket_step;
    memcpy(data,input+input_offset,size);input_offset+=size;return (int)size;
}
#include "txrx-functions.inc"
#else
static int httpd_recv_with_opt(httpd_req_t *req,char *data,size_t size,int flags) {
    (void)req;
    if(size>input_size-input_offset)size=input_size-input_offset;
    if(flags==HTTPD_RECV_OPT_NONE && size>3)size=3;
    memcpy(data,input+input_offset,size);input_offset+=size;return (int)size;
}
#endif
static int httpd_req_recv(httpd_req_t *req,char *data,size_t size) {return httpd_recv_with_opt(req,data,size,0);}
static void httpd_sess_free_ctx(void **context,void (*free_fn)(void *)) {if(free_fn)free_fn(*context);*context=NULL;}
static int httpd_sess_trigger_close(void *hd,int fd) {(void)hd;(void)fd;++queue_calls;return ESP_OK;}
static int httpd_resp_set_hdr(httpd_req_t *req,const char *name,const char *value) {
    (void)req;assert(!strcmp(name,"Sec-WebSocket-Version"));snprintf(response_version,sizeof(response_version),"%s",value);return ESP_OK;
}
static int httpd_resp_send_custom_err(httpd_req_t *req,const char *status,const char *message) {
    (void)req;(void)message;snprintf(response_status,sizeof(response_status),"%s",status);return ESP_OK;
}

/* SDK SHA implementation is outside this host seam. Validate the precise input
 * and use the RFC sample digest; Base64 encoder/decoder below is actual SDK C. */
#define PSA_HASH_OPERATION_INIT 0
#define PSA_ALG_SHA_1 1
#define PSA_SUCCESS 0
typedef int psa_status_t;
typedef int psa_hash_operation_t;
static int psa_hash_setup(psa_hash_operation_t *op,int algorithm) {assert(algorithm==1);*op=1;return 0;}
static int psa_hash_update(psa_hash_operation_t *op,const uint8_t *data,size_t size) {
    static const char expected[]="dGhlIHNhbXBsZSBub25jZQ==258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
    assert(*op==1 && size==sizeof(expected)-1 && !memcmp(data,expected,size));return 0;
}
static int psa_hash_finish(psa_hash_operation_t *op,uint8_t *data,size_t cap,size_t *size) {
    static const uint8_t digest[]={0xb3,0x7a,0x4f,0x2c,0xc0,0x62,0x4f,0x16,0x90,0xf6,0x46,0x06,0xcf,0x38,0x59,0x45,0xb2,0xbe,0xc4,0xea};
    assert(*op==1 && cap>=sizeof(digest));memcpy(data,digest,sizeof(digest));*size=sizeof(digest);return 0;
}
static void psa_hash_abort(psa_hash_operation_t *op) {*op=0;}
#include "sdk-base64.inc"
#include "native_httpd_headers.h"
static size_t httpd_req_get_hdr_value_len(httpd_req_t *req,const char *name) {
    struct httpd_req_aux *a=req->aux;const char *p=a->scratch;
    for(unsigned i=0;i<a->req_hdrs_count;++i){while(!*p)++p;const char *colon=strchr(p,':');assert(colon);
        if((size_t)(colon-p)==strlen(name)&&!strncasecmp(p,name,strlen(name))){
            p=colon+1;while(*p==' ')++p;return strlen(p);}
        p+=strlen(p)+1;}
    return 0;
}
static int httpd_req_get_hdr_value_str(httpd_req_t *req,const char *name,char *out,size_t size) {
    struct httpd_req_aux *a=req->aux;const char *p=a->scratch;
    for(unsigned i=0;i<a->req_hdrs_count;++i){while(!*p)++p;const char *colon=strchr(p,':');assert(colon);
        if((size_t)(colon-p)==strlen(name)&&!strncasecmp(p,name,strlen(name))){
            p=colon+1;while(*p==' ')++p;
            if(strlen(p)>=size)return ESP_ERR_HTTPD_RESULT_TRUNC;strcpy(out,p);return ESP_OK;}
        p+=strlen(p)+1;}
    return ESP_ERR_NOT_FOUND;
}
esp_err_t httpd_ws_send_frame(httpd_req_t *,httpd_ws_frame_t *);
esp_err_t httpd_ws_send_frame_async(httpd_handle_t,int,httpd_ws_frame_t *);
esp_err_t httpd_ws_recv_frame(httpd_req_t *,httpd_ws_frame_t *,size_t);
#ifdef NATIVE_TEST_TARGET_SIZE32
/* Exercise the actual SDK branch with the target's size cap. Structs and
 * size_t remain host-native: this validates the bound, not the target ABI. */
#undef SIZE_MAX
#define SIZE_MAX UINT32_MAX
#endif
#include "generated-functions.inc"

static httpd_req_t *reset(void) {
    memset(&session,0,sizeof(session));memset(&aux,0,sizeof(aux));memset(&server,0,sizeof(server));
    session.ws_handshake_done=true;session.ws_control_frames=true;session.fd=42;session.send_fn=wire_send;
    session.handle=&server;
#ifdef NATIVE_TEST_WIRE
    session.recv_fn=wire_receive;
#endif
    aux.sd=&session;server.hd_req=(httpd_req_t){.handle=&server,.aux=&aux};
    input_size=input_offset=output_size=queue_calls=0;short_send=false;
    response_status[0]=response_version[0]=0;return &server.hd_req;
}
static void headers(const char *host,const char *version,const char *key,const char *extra) {
    char buffer[2048];int n=snprintf(buffer,sizeof(buffer),"Host:%s\nSec-WebSocket-Version:%s\nSec-WebSocket-Key:%s\nUpgrade:h2c, WebSocket\nConnection:keep-alive, Upgrade\n%s",host,version,key,extra);
    assert(n>0 && (size_t)n<sizeof(buffer));aux.scratch=malloc((size_t)n+1);assert(aux.scratch);
    memcpy(aux.scratch,buffer,(size_t)n+1);aux.scratch_cur_size=(size_t)n+1;
    for(int i=0;i<n;++i)if(aux.scratch[i]=='\n'){aux.scratch[i]=0;++aux.req_hdrs_count;}
}
static void handshake(const char *host,const char *version,const char *key,const char *extra,bool expected) {
    httpd_req_t *req=reset();session.ws_handshake_done=false;headers(host,version,key,extra);
    bool ok=httpd_ws_respond_server_handshake(req,NULL)==ESP_OK;assert(ok==expected);
    if(ok){output[output_size]=0;assert(strstr((char *)output,"Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n"));}
    if(ok)assert(!strstr((char *)output,"Sec-WebSocket-Protocol:")&&!strstr((char *)output,"Sec-WebSocket-Extensions:"));
    free(aux.scratch);aux.scratch=NULL;++cases;
}
static void frame(uint8_t first,uint8_t second,uint64_t length,int code) {
    httpd_req_t *req=reset();input[input_size++]=first;input[input_size++]=second;
    unsigned bytes=(second&127)==126?2:(second&127)==127?8:0;
    for(unsigned i=0;i<bytes;++i)input[input_size++]=(uint8_t)(length>>(8*(bytes-i-1)));
    if(second&128)for(unsigned i=0;i<4;++i)input[input_size++]=(uint8_t)(11+i);
    size_t actual=length<=512?(size_t)length:0;
    for(size_t i=0;i<actual;++i)input[input_size++]=(uint8_t)('a'^(11+i%4));
    httpd_ws_frame_t packet={0};
    int result=httpd_ws_get_frame_type(req);
    if(result==ESP_OK)result=httpd_ws_recv_frame(req,&packet,0);
    if(code){assert(result!=ESP_OK);assert(output_size==4 && output[0]==0x88 && output[1]==2);
        assert(((unsigned)output[2]<<8|output[3])==(unsigned)code);assert(session.ws_close);
        httpd_req_cleanup(req);assert(queue_calls==0); /* Current owner may now delete. */
    }else{assert(result==ESP_OK && packet.len==length);uint8_t payload[512];
        packet.payload=payload;if(length)assert(httpd_ws_recv_frame(req,&packet,sizeof(payload))==ESP_OK);
        for(size_t i=0;i<actual;++i)assert(payload[i]=='a');}
    ++cases;
}
int main(void) {
    const char *key="dGhlIHNhbXBsZSBub25jZQ==";
    handshake("fixture.invalid","13",key,"",true);
    handshake(" fixture.invalid\t","\t13 "," \tdGhlIHNhbXBsZSBub25jZQ== \t","",true);
    handshake("","13",key,"",false);
    handshake("fixture.invalid","12",key,"",false);assert(!strcmp(response_version,"13"));
    handshake("fixture.invalid","13","invalid-key","",false);
    handshake("fixture.invalid","13","dGhlIHNhbXBsZSBub25jZ!==","",false);
    handshake("fixture.invalid","13",key,"Sec-WebSocket-Key:dGhlIHNhbXBsZSBub25jZQ==\n",false);
    handshake("fixture.invalid","13",key,"Sec-WebSocket-Version:13\n",false);
    handshake("fixture.invalid","13",key,"Host:fixture.invalid\n",false);
    const char *good_extensions[]={
        "permessage-deflate", "permessage-deflate; client_max_window_bits", "permessage-deflate; client_max_window_bits=15",
        "permessage-deflate ; client_max_window_bits = \"15\"; server_no_context_takeover",
        "private-extension; flag; parameter=token", "private-extension; parameter=\"a\\-b\"",
        "private-extension, permessage-deflate", ", private-extension ,, permessage-deflate,"
    };
    for(size_t i=0;i<sizeof(good_extensions)/sizeof(*good_extensions);++i){
        char extra[512];snprintf(extra,sizeof(extra),"Sec-WebSocket-Extensions:%s\n",good_extensions[i]);
        handshake("fixture.invalid","13",key,extra,true);
    }
    const char *bad_extensions[]={"",", ,",";x", "foo;", "foo;=x", "foo; x=", "foo; x=\"\"", "foo; x=\"a b\"",
        "foo; x=\"a;b\"", "foo; x=\"a,b\"", "foo; x=\"a\\\"b\"", "foo; x=\"a\\\\b\"", "foo; x=\"unfinished",
        "foo; x=\"done\"tail", "foo; x=a/b", "foo bar", "foo; x=\x7f", "foo; x=\"\xc3\xb6\"", "foo; x=\"a\tb\""};
    for(size_t i=0;i<sizeof(bad_extensions)/sizeof(*bad_extensions);++i){
        char extra[512];snprintf(extra,sizeof(extra),"Sec-WebSocket-Extensions:%s\n",bad_extensions[i]);
        handshake("fixture.invalid","13",key,extra,false);
    }
    const char *good_protocols[]={"chat", "chat, superchat", "chat, Chat", "chat.v2, superchat-x", ", chat, , superchat,",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"};
    for(size_t i=0;i<sizeof(good_protocols)/sizeof(*good_protocols);++i){
        char extra[512];snprintf(extra,sizeof(extra),"Sec-WebSocket-Protocol:%s\n",good_protocols[i]);
        handshake("fixture.invalid","13",key,extra,true);
    }
    const char *bad_protocols[]={"",", ,", "chat,chat", "chat, superchat, chat", "chat name", "\"chat\"", "chat/foo", "chat;param=1", "chat,\x7f"};
    for(size_t i=0;i<sizeof(bad_protocols)/sizeof(*bad_protocols);++i){
        char extra[512];snprintf(extra,sizeof(extra),"Sec-WebSocket-Protocol:%s\n",bad_protocols[i]);
        handshake("fixture.invalid","13",key,extra,false);
    }
    handshake("fixture.invalid","13",key,"Sec-WebSocket-Protocol:chat\nSec-WebSocket-Protocol:superchat\n",true);
    handshake("fixture.invalid","13",key,"Sec-WebSocket-Protocol:chat\nSec-WebSocket-Protocol:superchat,chat\n",false);
    handshake("fixture.invalid","13",key,"Sec-WebSocket-Extensions:permessage-deflate\nSec-WebSocket-Extensions:private-extension; flag\n",true);
    handshake("fixture.invalid","13",key,"Sec-WebSocket-Extensions:permessage-deflate\nSec-WebSocket-Extensions:private-extension; flag=\n",false);
    handshake("fixture.invalid","013",key,"",false);
    handshake("fixture.invalid","256",key,"",false);
    handshake("fixture.invalid","abc",key,"",false);
    handshake("fixture.invalid/path","13",key,"",false);
    handshake("fixture.invalid?query","13",key,"",false);
    handshake("user@fixture.invalid","13",key,"",false);
    handshake("[::1]:80","13",key,"",true);
    handshake("fixture.invalid:80","13",key,"",true);
    /* All non-NUL byte values through the actual handshake. The expected RFC
     * token class is independent of the production helper implementation. */
    for(unsigned c=1;c<=255;++c){
        bool token=c>=33&&c<=126&&!strchr("()<>@,;:\\\"/[]?={} ", (int)c);
        char extra[128];
        snprintf(extra,sizeof(extra),"Sec-WebSocket-Protocol: a%ca\n",(int)c);
        handshake("fixture.invalid","13",key,extra,token);
        if(c=='\\'||c=='"')snprintf(extra,sizeof(extra),"Sec-WebSocket-Extensions: private; p=\"a\\%cb\"\n",(int)c);
        else snprintf(extra,sizeof(extra),"Sec-WebSocket-Extensions: private; p=\"a%cb\"\n",(int)c);
        handshake("fixture.invalid","13",key,extra,token);
    }
    for(unsigned rsv=1;rsv<8;++rsv)frame((uint8_t)(0x81|(rsv<<4)),0x80,0,1002);
    for(unsigned opcode=0;opcode<16;++opcode){
        bool valid=opcode==0||opcode==1||opcode==2||opcode==8||opcode==9||opcode==10;
        frame((uint8_t)(0x80|opcode),0x80,0,valid?0:1002);
    }
    for(unsigned opcode=8;opcode<=10;++opcode){
        frame((uint8_t)opcode,0x80,0,1002);
        frame((uint8_t)(0x80|opcode),0xfe,126,1002);
        frame((uint8_t)(0x80|opcode),0xff,65536,1002);
        frame((uint8_t)(0x80|opcode),0xfd,125,0);
    }
    frame(0x81,0x00,0,1002);frame(0x81,0xfe,125,1002);frame(0x81,0xff,65535,1002);
    frame(0x81,0xff,UINT64_C(0x8000000000000000),1002);
#ifdef NATIVE_TEST_TARGET_SIZE32
    frame(0x81,0xff,UINT64_C(0x100000000),1009);
#endif
    frame(0x81,0x85,5,0);frame(0x81,0xfe,126,0);frame(0x82,0xfe,512,0);
    httpd_req_t *req=reset();session.ws_close=true;assert(httpd_req_delete(&server)==ESP_FAIL && queue_calls==0);++cases;
    req=reset();assert(httpd_req_delete(&server)==ESP_OK && queue_calls==0);++cases;
    req=reset();httpd_ws_frame_t packet={.type=HTTPD_WS_TYPE_TEXT,.payload=(uint8_t *)"x",.len=1};
    short_send=true;assert(httpd_ws_send_frame(req,&packet)!=ESP_OK);++cases;
    req=reset();session.ws_close=true;assert(httpd_ws_send_frame(req,&packet)!=ESP_OK);++cases;
    const size_t sizes[]={125,126,65535,65536};
    for(size_t i=0;i<sizeof(sizes)/sizeof(*sizes);++i){
        req=reset();uint8_t *payload=calloc(sizes[i],1);assert(payload);
        packet=(httpd_ws_frame_t){.type=HTTPD_WS_TYPE_BINARY,.payload=payload,.len=sizes[i]};
        assert(httpd_ws_send_frame(req,&packet)==ESP_OK);
        assert(output[0]==0x82 && output[1]==(sizes[i]<126?sizes[i]:sizes[i]<=65535?126:127));
        size_t header=sizes[i]<126?2:sizes[i]<=65535?4:10;
        assert(output_size==sizes[i]+header);free(payload);++cases;
    }
    printf("PASS generated SDK HTTPD: %u header/frame/cleanup checks; no deferred close queued\n",cases);
    return 0;
}
