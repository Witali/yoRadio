#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
typedef int esp_err_t;
typedef struct { void *handle; int socket; } httpd_req_t;
enum { ESP_OK=0, ESP_FAIL=-1, SHUT_RDWR=2 };
static bool owns_session;
static unsigned shutdowns, queued_closes, completions;
static int httpd_req_to_sockfd(httpd_req_t *request) { assert(owns_session);return request->socket; }
static int shutdown(int socket,int how) {
    assert(owns_session && socket==7 && how==SHUT_RDWR);++shutdowns;return 0;
}
static int httpd_sess_trigger_close(void *server,int socket) {
    assert(server && socket==7);++queued_closes;
    // Exercise a permitted interleaving: HTTPD executes the queued callback
    // immediately, before the async worker releases its request/session.
    owns_session=false;
    return 0;
}
static void complete(void) { assert(owns_session);owns_session=false;++completions; }
#include "close-production.inc"
int main(void) {
    for(int result=ESP_OK;result>=ESP_FAIL;--result) {
        owns_session=true;shutdowns=queued_closes=completions=0;
        httpd_req_t request={.handle=(void *)1,.socket=7};
        assert(finish_static_response(&request,result)==result);
        assert(owns_session && shutdowns==1 && !queued_closes);
        complete();assert(!owns_session && completions==1);
    }
    puts("PASS static session: successful and failed responses shut down while owned, complete before session reuse");
}
