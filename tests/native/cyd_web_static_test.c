#define _GNU_SOURCE
#include <assert.h>
#include <setjmp.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>

typedef int esp_err_t;
typedef void *QueueHandle_t, *TaskHandle_t;
typedef struct { char uri[256]; int fd, status; bool async, closed; } httpd_req_t;
enum { ESP_OK=0, ESP_FAIL=-1, ESP_ERR_INVALID_STATE=-2, ESP_ERR_NO_MEM=-3,
       HTTPD_400_BAD_REQUEST=400, HTTPD_404_NOT_FOUND=404, pdTRUE=1, pdPASS=1 };
#define CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES 1024
#define CONFIG_YORADIO_WEB_STATIC_WORKERS 2
#define portMAX_DELAY UINT32_MAX
#define ESP_LOGW(...) ((void)0)
static httpd_req_t *pending[2];
static unsigned queued, tasks, deleted_tasks, queue_live, complete_count, shutdown_count;
static unsigned task_attempts, fail_task, terminal_chunks, send_count, fail_send;
static bool fail_queue, fail_begin, fail_read, fail_complete;
static char body[20000], type[80], encoding[32], cache[32], fixture_root[512];
static size_t body_size;
static jmp_buf worker_exit;
static unsigned notifications;
static unsigned ulTaskNotifyTake(int clear, unsigned wait) {
    assert(clear==pdTRUE && wait==portMAX_DELAY && notifications==2);return 1;
}
static void xTaskNotifyGive(void *task) { assert(task);notifications++; }

static void *xQueueCreate(unsigned depth, size_t size) {
    assert(depth==2 && size==sizeof(httpd_req_t *));
    if (fail_queue) return NULL;
    queue_live++; return (void *)1;
}
static void vQueueDelete(void *queue) { assert(queue && queue_live); queue_live--; }
static int xTaskCreate(void (*entry)(void *), const char *name, unsigned stack,
                       void *arg, unsigned priority, void **handle) {
    (void)entry;(void)name;assert(stack==4096 && !arg && priority==2);
    if (++task_attempts==fail_task) return 0;
    *handle=(void *)(uintptr_t)(++tasks+1);return pdPASS;
}
static void vTaskDelete(void *task) { assert(task); deleted_tasks++; }
static int xQueueSend(void *queue, httpd_req_t **req, unsigned wait) {
    assert(queue && !wait);if (queued==2) return 0;
    pending[queued++]=*req;return pdTRUE;
}
static int xQueueReceive(void *queue, httpd_req_t **req, unsigned wait) {
    assert(queue && wait==portMAX_DELAY);
    if (!queued) longjmp(worker_exit, 1);
    *req=pending[0];pending[0]=pending[1];queued--;return pdTRUE;
}
static int httpd_req_to_sockfd(httpd_req_t *req) { assert(req->async); return req->fd; }
static int test_shutdown(int fd, int how) {
    assert(fd>=0 && how==SHUT_RDWR);shutdown_count++;return 0;
}
static int httpd_req_async_handler_begin(httpd_req_t *req, httpd_req_t **out) {
    if (fail_begin) return ESP_ERR_NO_MEM;
    *out=malloc(sizeof(**out));assert(*out);**out=*req;(*out)->async=true;return ESP_OK;
}
static int httpd_req_async_handler_complete(httpd_req_t *req) {
    assert(req->async && shutdown_count==complete_count+1);
    complete_count++;free(req);return fail_complete ? ESP_FAIL : ESP_OK;
}
static int httpd_resp_set_hdr(httpd_req_t *r, const char *key, const char *value) {
    (void)r;
    if (!strcmp(key,"Content-Encoding")) snprintf(encoding,sizeof(encoding),"%s",value);
    if (!strcmp(key,"Cache-Control")) snprintf(cache,sizeof(cache),"%s",value);
    return ESP_OK;
}
static int httpd_resp_set_type(httpd_req_t *r, const char *value) {
    (void)r;snprintf(type,sizeof(type),"%s",value);return ESP_OK;
}
static int httpd_resp_set_status(httpd_req_t *r, const char *value) { r->status=atoi(value);return 0; }
static int httpd_resp_send_chunk(httpd_req_t *r, const char *data, ssize_t size) {
    (void)r;assert(size>=0 && size<=CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES);
    if (++send_count==fail_send) return ESP_FAIL;
    if (!size) terminal_chunks++;
    else { assert(body_size+(size_t)size<sizeof(body));memcpy(body+body_size,data,(size_t)size);body_size+=(size_t)size;body[body_size]=0; }
    return ESP_OK;
}
static int httpd_resp_sendstr(httpd_req_t *r, const char *text) {
    (void)r;snprintf(body,sizeof(body),"%s",text);body_size=strlen(body);return ESP_OK;
}
static int httpd_resp_send_err(httpd_req_t *r, int status, const char *text) {
    r->status=status;return httpd_resp_sendstr(r,text);
}
static const char *web_native_page(void) { return "embedded native page"; }
static FILE *test_fopen(const char *path, const char *mode) {
    assert(!strncmp(path,"/spiffs/",8));char actual[1024];
    snprintf(actual,sizeof(actual),"%s/%s",fixture_root,path+8);return fopen(actual,mode);
}
static int test_ferror(FILE *file) { return fail_read || ferror(file); }
#define fopen test_fopen
#define ferror test_ferror
#define shutdown test_shutdown
#include "production.inc"
#undef fopen
#undef ferror

static void reset_response(void) {
    body[0]=type[0]=encoding[0]=cache[0]=0;body_size=terminal_chunks=send_count=fail_send=0;fail_read=false;
}
static httpd_req_t request(const char *uri) { httpd_req_t r={.fd=7};snprintf(r.uri,sizeof(r.uri),"%s",uri);return r; }
static void serve(const char *uri, int status) {
    reset_response();httpd_req_t r=request(uri);assert(serve_static(&r)==ESP_OK);assert(r.status==status);
}
static void run_worker(void) { if (!setjmp(worker_exit)) static_worker(NULL); }
int main(int argc, char **argv) {
    assert(argc==2);snprintf(fixture_root,sizeof(fixture_root),"%s",argv[1]);
    httpd_req_t r=request("/");
    assert(web_static_handler(&r)==ESP_OK && r.status==503 && !queued);
    fail_queue=true;assert(web_static_start()==ESP_ERR_NO_MEM && !queue_live);fail_queue=false;
    for (unsigned i=1;i<=2;++i) {
        fail_task=i;task_attempts=tasks=deleted_tasks=0;
        assert(web_static_start()==ESP_ERR_NO_MEM && !queue_live);
        assert(deleted_tasks==i-1);
    }
    fail_task=0;assert(web_static_start()==ESP_OK && queue_live==1);
    assert(web_static_start()==ESP_ERR_INVALID_STATE);
    serve("/",0);assert(!strcmp(body,"embedded native page") && !strcmp(cache,"no-store"));
    serve("/settings.html?test=1",0);assert(!strcmp(body,"embedded native page"));
    serve("/theme.css",0);assert(!strcmp(body,"raw css") && !strcmp(type,"text/css; charset=utf-8") && !*encoding);
    serve("/empty.js",0);assert(!strcmp(body,"compressed") && !strcmp(encoding,"gzip"));
    serve("/empty.js.gz",0);assert(!strcmp(type,"application/javascript; charset=utf-8") && !strcmp(encoding,"gzip"));
    serve("/data/playlist.csv",0);assert(!strcmp(body,"station\thttps://example.test/audio\n") && !*encoding);
    serve("/data/wifi.csv",404);serve("/not-found",404);
    const char *bad[]={"/../wifi.csv","/%2e%2e/wifi.csv","/foo\\bar","//foo","/foo\nbar","/bad name","relative"};
    for (unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);++i) serve(bad[i],400);
    serve("/large.css",0);assert(body_size==5100 && terminal_chunks==1 && send_count==6);
    reset_response();r=request("/large.css");fail_send=2;
    assert(serve_static(&r)==ESP_FAIL && body_size==1024 && !terminal_chunks);
    reset_response();fail_read=true;assert(serve_static(&r)==ESP_FAIL && !terminal_chunks);
    reset_response();web_static_activate();
    fail_begin=true;r=request("/");assert(web_static_handler(&r)==ESP_OK && r.status==503 && !queued);fail_begin=false;
    r=request("/theme.css");assert(web_static_handler(&r)==ESP_OK && queued==1 && !send_count);
    r=request("/empty.js");assert(web_static_handler(&r)==ESP_OK && queued==2 && !send_count);
    r=request("/");assert(web_static_handler(&r)==ESP_OK && queued==2 && complete_count==1);
    assert(strstr(body,"queue full"));
    run_worker();assert(!queued && complete_count==3 && shutdown_count==3);
    fail_complete=true;r=request("/");web_static_handler(&r);run_worker();assert(complete_count==4);
    // Abort has only startup semantics; stop accepting before test cleanup.
    atomic_store(&s_active,false);web_static_abort();assert(!queue_live);
    puts("PASS static workers: allocation/task rollback, bounded dispatch, two pending requests, shutdown ownership, raw/gzip/data, path rejection, send/read failure");
    return 0;
}
