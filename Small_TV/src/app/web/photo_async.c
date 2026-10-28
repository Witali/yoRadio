/* REQUESTED_CHANGE: actual ESP-IDF async ownership for slow photo operations. */
#include "web.h"
#include "media.h"
#include "../media/photo_worker.h"
#include <stdlib.h>

typedef struct {
    httpd_req_t *request;
    unsigned slot,chunks;
    uint32_t length;
    bool finish;
} photo_http_job_t;

static void execute(void *context)
{
    /* Every successful async begin has exactly one complete, even if the
     * client disconnected or flash/metadata/decoder/settings returned failure. */
    photo_http_job_t *job=context;photo_diagnostic_t diagnostic={0};
    esp_err_t error=job->finish ? photo_upload_finish_detailed(job->slot,&diagnostic):
        photo_upload_start_detailed(job->slot,job->length,job->chunks,&diagnostic);
    if(error==ESP_OK)web_ok(job->request);
    else {
        char reason[192];photo_diagnostic_describe(&diagnostic,reason,sizeof(reason));
        web_error(job->request,reason);
    }
    (void)httpd_req_async_handler_complete(job->request);free(job);
}

esp_err_t web_photo_async(httpd_req_t *request,bool finish,unsigned slot,uint32_t length,unsigned chunks)
{
    /* Parse/body validation stays in the HTTP task; the bounded closure owns
     * only copied arguments and SDK's supported request clone, not a stack req. */
    photo_http_job_t *job=calloc(1,sizeof(*job));
    if(!job)return httpd_resp_send_err(request,HTTPD_500_INTERNAL_SERVER_ERROR,"Out of memory");
    esp_err_t error=httpd_req_async_handler_begin(request,&job->request);
    if(error!=ESP_OK){free(job);return httpd_resp_send_err(request,HTTPD_500_INTERNAL_SERVER_ERROR,"Async request unavailable");}
    job->slot=slot;job->length=length;job->chunks=chunks;job->finish=finish;
    error=photo_worker_submit(execute,job);
    if(error!=ESP_OK) {
        /* The pinned SDK's error enum has no503 entry; ordinary response APIs
         * support the standard status without inventing a platform constant. */
        (void)httpd_resp_set_status(job->request,"503 Service Unavailable");
        (void)httpd_resp_set_type(job->request,"text/plain; charset=utf-8");
        (void)httpd_resp_send(job->request,"Photo worker unavailable or busy",HTTPD_RESP_USE_STRLEN);
        (void)httpd_req_async_handler_complete(job->request);free(job);
    }
    return ESP_OK;
}
