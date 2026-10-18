/* Execute actual SDK cleanup/queue/callback code with a deterministic session
 * recycle between the owning loop's deletion and delivery of queued work. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#define CONFIG_HTTPD_WS_SUPPORT 1
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NOT_FOUND 5
#define ESP_LOGD(...) ((void)0)
#define HTTP_SERVER_EVENT_DISCONNECTED 1
typedef int esp_err_t;
typedef void *httpd_handle_t;
struct sock_db { bool ws_close,lru_socket,ignore_sess_ctx_changes;
    int fd; unsigned lru_counter; void *handle,*ctx; void (*free_ctx)(void *); };
struct httpd_req_aux { struct sock_db *sd; char *scratch; size_t scratch_cur_size,scratch_size_limit; };
typedef struct { void *handle,*aux,*sess_ctx,*user_ctx; void (*free_ctx)(void *); bool ignore_sess_ctx_changes; } httpd_req_t;
struct httpd_data { int http_server_state; };
static struct sock_db session;
static struct httpd_data server;
static void (*queued)(void *);
static void *queued_arg;
static int deleted_fd=-1;
static struct sock_db *httpd_sess_get(void *handle,int fd) {(void)handle;return session.fd==fd?&session:NULL;}
static void httpd_sess_delete(struct httpd_data *hd,struct sock_db *sd) {(void)hd;deleted_fd=sd->fd;memset(sd,0,sizeof(*sd));}
static int httpd_queue_work(void *handle,void (*fn)(void *),void *arg) {(void)handle;assert(!queued);queued=fn;queued_arg=arg;return ESP_OK;}
static void httpd_sess_free_ctx(void **context,void (*free_fn)(void *)) {if(free_fn)free_fn(*context);*context=NULL;}
#include "close-functions.inc"
int main(void) {
    session=(struct sock_db){.ws_close=true,.fd=42,.lru_counter=1,.handle=&server};
    struct httpd_req_aux aux={.sd=&session};
    httpd_req_t req={.handle=&server,.aux=&aux};
    httpd_req_cleanup(&req); /* Error return -> owning loop deletes this slot. */
    httpd_sess_delete(&server,&session);assert(deleted_fd==42);
    session=(struct sock_db){.fd=43,.lru_counter=2,.handle=&server};
    if(queued)queued(queued_arg); /* A permitted later HTTPD queue delivery. */
    assert(deleted_fd==42 && "queued close deleted the recycled session");
    puts("PASS actual SDK Close cleanup/callback ordering: recycled session survives");
    return 0;
}
