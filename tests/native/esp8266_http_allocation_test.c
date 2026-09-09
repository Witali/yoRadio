#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_INVALID_ARG -2
#define ESP_ERR_HTTPD_ALLOC_MEM -3
#define ESP_ERR_HTTPD_HANDLER_EXISTS -4
#define ESP_ERR_HTTPD_HANDLERS_FULL -5
#define ESP_ERR_HTTPD_TASK -6
#define ESP_LOGD(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
typedef int esp_err_t;
typedef int httpd_method_t;
typedef void *httpd_handle_t;
typedef struct { const char *uri; int method, handler; void *user_ctx; } httpd_uri_t;
typedef struct { uint16_t max_uri_handlers; int stack_size, task_priority; } httpd_config_t;
struct httpd_data {
    httpd_config_t config;
    httpd_uri_t **hd_calls;
    int msg_fd, ctrl_fd, listen_fd;
    struct { void *handle; } hd_td;
};
static int live, fail_after = -1;
static void *owned[16];
static void *test_malloc(size_t n) {
    if (fail_after == 0) return NULL;
    if (fail_after > 0) --fail_after;
    void *p = malloc(n); assert(p);
    for (unsigned i=0; i<16; ++i) if (!owned[i]) {owned[i]=p; ++live; return p;}
    assert(0); return NULL;
}
static void test_free(void *p) {
    if (!p) return;
    for(unsigned i=0; i<16; ++i) if(owned[i]==p) {owned[i]=NULL; --live; free(p); return;}
    assert(0); /* double free or non-owned pointer */
}
static char *test_strdup(const char *p) {
    size_t n=strlen(p)+1; char *q=test_malloc(n); if(q)memcpy(q,p,n); return q;
}
#define malloc test_malloc
#define free test_free
#define strdup test_strdup
/* URI_IMPLEMENTATION */

static struct httpd_data server;
static bool sockets[3];
static struct httpd_data *httpd_create(const httpd_config_t *config) {
    server.config=*config; return &server;
}
static int httpd_server_init(struct httpd_data *hd) {
    hd->msg_fd=0; hd->ctrl_fd=1; hd->listen_fd=2;
    sockets[0]=sockets[1]=sockets[2]=true; return ESP_OK;
}
static int test_close(int fd) {assert(fd>=0&&fd<3&&sockets[fd]); sockets[fd]=false;return 0;}
#define close test_close
static void cs_free_ctrl_sock(int fd) {assert(fd==1);test_close(fd);}
static void httpd_delete(struct httpd_data *hd) {
    (void)hd; assert(!sockets[0]&&!sockets[1]&&!sockets[2]);
}
static void httpd_sess_init(struct httpd_data *hd) {(void)hd;}
static void httpd_thread(void *arg) {(void)arg;}
static int httpd_os_thread_create(void **h,const char *n,int s,int p,void (*f)(void *),void *a) {
    (void)h;(void)n;(void)s;(void)p;(void)f;(void)a;return ESP_FAIL;
}
/* START_IMPLEMENTATION */

typedef uint32_t TickType_t;
typedef struct {void *handle; int fd;} httpd_req_t;
#define WEB_MAX_OPEN_SOCKETS 4
#define SHUT_WR 1
#define pdMS_TO_TICKS(n) (n)
static TickType_t tick;
static int queued, queued_fd;
static bool queue_fail, shutdown_fail;
static httpd_handle_t s_server=&server;
static TickType_t xTaskGetTickCount(void) {return tick;}
static int httpd_req_to_sockfd(httpd_req_t *r) {return r->fd;}
static int shutdown(int fd,int how) {(void)fd;assert(how==SHUT_WR);return shutdown_fail?-1:0;}
static int httpd_sess_trigger_close(void *h,int fd) {
    assert(h==s_server);if(queue_fail)return ESP_FAIL;++queued;queued_fd=fd;return ESP_OK;
}
/* CLOSE_IMPLEMENTATION */

static void test_bounded_close(void) {
    httpd_req_t r={s_server,7};
    assert(web_service_finish_response(&r,ESP_OK)==ESP_OK);
    tick=4999;web_close_poll();assert(queued==0);
    queue_fail=true;tick=5000;web_close_poll();assert(queued==0);
    queue_fail=false;web_close_poll();assert(queued==1&&queued_fd==7);
    web_close_poll();assert(queued==1);
    assert(web_service_finish_response(&r,ESP_OK)==ESP_OK);
    web_close_forget(7);tick+=5001;web_close_poll();assert(queued==1);
    // A new connection with the same fd must not inherit a pending timeout.
    tick=UINT32_MAX-100;
    assert(web_service_finish_response(&r,ESP_OK)==ESP_OK);
    tick+=5000;web_close_poll();assert(queued==2);
    shutdown_fail=true;
    assert(web_service_finish_response(&r,ESP_OK)==ESP_FAIL&&queued==3);
    shutdown_fail=false;
    assert(web_service_finish_response(&r,ESP_FAIL)==ESP_FAIL&&queued==4);
}

int main(void) {
    httpd_uri_t *slots[2]={0};
    struct httpd_data hd={0};hd.hd_calls=slots;hd.config.max_uri_handlers=2;
    const httpd_uri_t uri={"/",1,0,NULL};
    for(int fail=0;fail<2;++fail) {
        fail_after=fail;
        assert(httpd_register_uri_handler(&hd,&uri)==ESP_ERR_HTTPD_ALLOC_MEM);
        assert(!slots[0]&&!slots[1]&&live==0);
        httpd_unregister_all_uri_handlers(&hd);
    }
    fail_after=-1;
    assert(httpd_register_uri_handler(&hd,&uri)==ESP_OK);
    assert(live==2);
    httpd_unregister_all_uri_handlers(&hd);
    httpd_unregister_all_uri_handlers(&hd); // cleanup is safe when repeated
    assert(!slots[0]&&live==0);
    httpd_config_t config={0};httpd_handle_t handle=NULL;
    assert(httpd_start(&handle,&config)==ESP_ERR_HTTPD_TASK);
    assert(!handle&&!sockets[0]&&!sockets[1]&&!sockets[2]);
    test_bounded_close();
    puts("HTTP allocation cleanup tests passed");
}
