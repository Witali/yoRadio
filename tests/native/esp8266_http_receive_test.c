#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#define HTTPD_SOCK_ERR_FAIL -1
#define HTTPD_SOCK_ERR_INVALID -2
#define HTTPD_SOCK_ERR_TIMEOUT -3
#define ESP_OK 0
#define LOG_FMT(s) s
static void fake_log(const char *format, ...) { (void)format; }
#define ESP_LOGW(tag, ...) fake_log(__VA_ARGS__)
#define ESP_LOGD(tag, ...) fake_log(__VA_ARGS__)
typedef uint32_t TickType_t;
typedef void *httpd_handle_t;
typedef struct { size_t content_len; void *aux; } httpd_req_t;
typedef struct { unsigned bytes; } web_multipart_t;
typedef void *mp_handler_t;
static uint32_t now;
static TickType_t xTaskGetTickCount(void) { return now; }
#define pdMS_TO_TICKS(ms) (ms)
static void vTaskDelay(unsigned ticks) { now += ticks; }
static uint32_t httpd_trace_clock(void) { return 0; }
static void httpd_trace_recv(uint32_t stamp) { (void)stamp; }
static bool httpd_valid_req(httpd_req_t *r) { return r && r->aux; }
static int httpd_req_get_hdr_value_str(httpd_req_t *r,const char *name,char *dst,size_t size) {
    (void)r; (void)name;
    snprintf(dst,size,"multipart/form-data; boundary=test"); return ESP_OK;
}
static bool mp_init(web_multipart_t *p,const char *b,mp_handler_t h,void *c) {
    (void)b; (void)h; (void)c; p->bytes=0; return true;
}
static unsigned fed;
static bool mp_feed(web_multipart_t *p,const uint8_t *s,size_t n) {
    (void)s; p->bytes+=(unsigned)n; fed+=(unsigned)n; return true;
}
static bool mp_complete(web_multipart_t *p) { return p->bytes==6; }
static uint8_t s_receive[512];
typedef struct { int result,error; unsigned elapsed; } event_t;
static event_t events[16];
static unsigned event_count,event_index;
static int fake_recv(int fd,char *dst,size_t length,int flags) {
    (void)fd; (void)flags;
    assert(event_index<event_count);
    event_t event=events[event_index++]; now+=event.elapsed; errno=event.error;
    if(event.result>0) {
        assert((size_t)event.result<=length);
        memset(dst,'x',(size_t)event.result);
    }
    return event.result;
}
static int fake_send(int fd,const char *src,size_t length,int flags) {
    (void)fd; (void)src; (void)length; (void)flags;
    errno=EAGAIN; return -1;
}
#define recv fake_recv
#define send fake_send
/* SOCKET_IMPLEMENTATION */
typedef struct {
    unsigned pending_len;
    int (*recv_fn)(httpd_handle_t,int,char*,size_t,int);
    httpd_handle_t handle; int fd;
} socket_t;
struct httpd_req_aux { socket_t *sd; size_t remaining_len; };
static size_t httpd_recv_pending(httpd_req_t *r,char *buf,size_t length) {
    struct httpd_req_aux *aux=r->aux;
    size_t n=length<aux->sd->pending_len?length:aux->sd->pending_len;
    aux->sd->pending_len-=(unsigned)n; memset(buf,'p',n); return n;
}
#ifdef _MSC_VER
/* Unmodified 32-bit SDK recv helpers return bounded size_t counts as int.
 * This host harness uses Win64 size_t; keep other /W4 diagnostics enabled. */
#pragma warning(push)
#pragma warning(disable:4267)
#endif
/* BUFFER_IMPLEMENTATION */
/* REQUEST_IMPLEMENTATION */
#ifdef _MSC_VER
#pragma warning(pop)
#endif
/* FORM_IMPLEMENTATION */
static void reset(void) { now=0; fed=event_count=event_index=0; }
static void add(int result,int error,unsigned elapsed) {
    assert(event_count<16); events[event_count++]=(event_t){result,error,elapsed};
}
int main(void) {
    char bytes[16];
    const int retry[]={EAGAIN,EWOULDBLOCK,EINTR};
    for(unsigned i=0;i<sizeof(retry)/sizeof(retry[0]);++i) {
        reset(); add(-1,retry[i],2000);
        assert(httpd_default_recv(NULL,3,bytes,sizeof(bytes),0)==HTTPD_SOCK_ERR_TIMEOUT);
    }
    reset();add(-1,EBADF,0);
    assert(httpd_default_recv(NULL,3,bytes,sizeof(bytes),0)==HTTPD_SOCK_ERR_INVALID);
    reset();add(-1,ECONNRESET,0);
    assert(httpd_default_recv(NULL,3,bytes,sizeof(bytes),0)==HTTPD_SOCK_ERR_FAIL);
    reset();add(0,0,0);
    assert(httpd_default_recv(NULL,3,bytes,sizeof(bytes),0)==0);
    assert(httpd_default_send(NULL,3,bytes,1,0)==HTTPD_SOCK_ERR_TIMEOUT);
    socket_t socket={0,httpd_default_recv,NULL,3};
    struct httpd_req_aux aux={&socket,6};
    httpd_req_t request={6,&aux};
    reset();add(2,0,0);add(4,0,0);
    assert(receive_form(&request,100,NULL,NULL)&&fed==6&&aux.remaining_len==0);
    /* Partial pending bytes must survive a timeout in the next socket read. */
    reset();socket.pending_len=2;aux.remaining_len=6;add(-1,EAGAIN,2000);add(4,0,0);
    assert(receive_form(&request,100,NULL,NULL)&&fed==6&&event_index==2);
    reset();aux.remaining_len=6;add(-1,EINTR,0);add(2,0,0);add(-1,EAGAIN,3000);add(4,0,0);
    assert(receive_form(&request,100,NULL,NULL)&&fed==6);
    reset();aux.remaining_len=6;for(unsigned i=0;i<5;i++)add(-1,EAGAIN,2000);
    assert(!receive_form(&request,100,NULL,NULL)&&fed==0&&event_index==5);
    /* Progress cannot renew the 120-second total upload deadline. */
    reset();aux.remaining_len=6;add(1,0,60000);add(1,0,60000);
    assert(!receive_form(&request,100,NULL,NULL)&&fed==2);
    reset();aux.remaining_len=6;add(2,0,0);add(0,0,0);
    assert(!receive_form(&request,100,NULL,NULL)&&fed==2);
    puts("HTTP receive/upload tests passed");
    return 0;
}
