/* REQUESTED_CHANGE: low-priority codec owner, no HTTP or LCD implementation. */
#include "photo_worker.h"
#include "media_internal.h"
#include "media.h"
#include "settings.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_log.h"

#if configUSE_TIME_SLICING != 1
#error "Photo worker requires idle-priority time slicing for watchdog/idle fairness"
#endif

typedef struct {
    void (*function)(void *);
    void *context;
    unsigned slot;
    uint32_t length;
} photo_job_t;
static QueueHandle_t jobs;
static SemaphoreHandle_t codec_mutex;
static portMUX_TYPE state_lock=portMUX_INITIALIZER_UNLOCKED;
static uint32_t ready,pending,ready_lengths[PHOTO_COUNT],failed_lengths[PHOTO_COUNT];
static bool cancel_background,enabled;
static unsigned foreground_pending;

int photo_codec_cancelled(void)
{
    /* A foreground enqueue can stop a running background decode promptly. */
    portENTER_CRITICAL(&state_lock);bool cancelled=cancel_background || foreground_pending;portEXIT_CRITICAL(&state_lock);
    return cancelled;
}

static bool source_current_unlocked(unsigned slot,uint32_t length)
{
    /* FIXED_RECONSTRUCTION: a queued/caller length is only a snapshot. Recheck
     * under media_mutex before touching cache or publishing a delayed result.
     * Upload source writes additionally wait for the caller's codec_mutex. */
    if(slot>=PHOTO_COUNT || !length || photo_upload_active_unlocked())return false;
    tv_settings_t settings;settings_snapshot(&settings);
    return settings.photo_size[slot]==length;
}

static void record_result(unsigned slot,uint32_t length,bool success,bool permanent_failure)
{
    /* Never resurrect ready or suppress retries from an obsolete source job.
     * The worker publishes while still holding codec_mutex, before a waiting
     * upload can invalidate/replace the source and clear its failure state. */
    xSemaphoreTake(media_mutex,portMAX_DELAY);
    bool current=source_current_unlocked(slot,length);
    portENTER_CRITICAL(&state_lock);
    if(current && success){ready|=1u<<slot;ready_lengths[slot]=length;failed_lengths[slot]=0;}
    else if(current && permanent_failure)failed_lengths[slot]=length;
    portEXIT_CRITICAL(&state_lock);xSemaphoreGive(media_mutex);
}

static void run(void *argument)
{
    /* Idle priority + time slicing lets IDLE/watchdog, HTTP and the clock run
     * during CPU-heavy multi-scan decoding, without artificial decode delays. */
    (void)argument;photo_job_t job;
    for(;;) {
        if(xQueueReceive(jobs,&job,portMAX_DELAY)!=pdTRUE)continue;
        if(job.function) {
            job.function(job.context);
            portENTER_CRITICAL(&state_lock);--foreground_pending;portEXIT_CRITICAL(&state_lock);
            continue;
        }
        photo_diagnostic_t diagnostic={0};
        portENTER_CRITICAL(&state_lock);
        bool foreground=foreground_pending!=0;
        if(!foreground)cancel_background=false;
        portEXIT_CRITICAL(&state_lock);
        bool success=false;
        xSemaphoreTake(codec_mutex,portMAX_DELAY);
        xSemaphoreTake(media_mutex,portMAX_DELAY);
        bool current=source_current_unlocked(job.slot,job.length);
        xSemaphoreGive(media_mutex);
        if(!foreground && current)success=photo_codec_prepare(job.slot,job.length,true,&diagnostic)==ESP_OK;
        /* FIXED_RECONSTRUCTION: cache only stable input/fixed-capacity refusals.
         * A privacy read fault, allocator pressure or callback failure must not
         * suppress this source forever; the unchanged image can succeed later. */
        jpeg_decode_status_t status=diagnostic.decode.status;
        jpeg_privacy_result_t privacy=diagnostic.privacy.status;
        bool permanent=(diagnostic.status==PHOTO_PRIVACY &&
            privacy>=JPEG_PRIVACY_INVALID && privacy<=JPEG_PRIVACY_TRAILING) ||
            (diagnostic.status==PHOTO_DECODE && (status==JPEG_DECODE_INVALID ||
             status==JPEG_DECODE_TRUNCATED || status==JPEG_DECODE_UNSUPPORTED ||
             status==JPEG_DECODE_DIMENSIONS || status==JPEG_DECODE_POOL_LIMIT ||
             status==JPEG_DECODE_BACKING_LIMIT || status==JPEG_DECODE_BACKING_FILES));
        record_result(job.slot,job.length,success,permanent);
        portENTER_CRITICAL(&state_lock);
        pending&=~(1u<<job.slot);
        portEXIT_CRITICAL(&state_lock);
        xSemaphoreGive(codec_mutex);
    }
}

esp_err_t photo_worker_init(void)
{
    /* Fail closed for photo storage without preventing clocks/network startup.
     * An old/mismatched assets image must never grant scratch write permission. */
    codec_mutex=xSemaphoreCreateMutex();
    if(!codec_mutex)return ESP_ERR_NO_MEM;
    esp_err_t error=photo_codec_init();
    if(error!=ESP_OK){ESP_LOGW("photo","Photo storage guard failed: %d",error);return ESP_OK;}
    jobs=xQueueCreate(4,sizeof(photo_job_t));
    if(!jobs)return ESP_ERR_NO_MEM;
    if(xTaskCreate(run,"tv-photo",8192,NULL,tskIDLE_PRIORITY,NULL)!=pdPASS)return ESP_ERR_NO_MEM;
    enabled=true;return ESP_OK;
}

esp_err_t photo_worker_submit(void (*function)(void *),void *context)
{
    /* Bound outstanding requests. On rejection the caller still owns context. */
    if(!enabled || !function)return ESP_ERR_INVALID_STATE;
    photo_job_t job={.function=function,.context=context};
    portENTER_CRITICAL(&state_lock);cancel_background=true;++foreground_pending;portEXIT_CRITICAL(&state_lock);
    if(xQueueSend(jobs,&job,0)==pdTRUE)return ESP_OK;
    portENTER_CRITICAL(&state_lock);--foreground_pending;portEXIT_CRITICAL(&state_lock);
    return ESP_ERR_NO_MEM;
}

esp_err_t photo_worker_invalidate(unsigned slot,photo_diagnostic_t *diagnostic)
{
    /* Source writers wait for the codec owner, then durably revoke the frame. */
    if(!enabled){if(diagnostic)diagnostic->status=PHOTO_STORAGE;return ESP_ERR_INVALID_STATE;}
    portENTER_CRITICAL(&state_lock);cancel_background=true;portEXIT_CRITICAL(&state_lock);
    xSemaphoreTake(codec_mutex,portMAX_DELAY);
    esp_err_t error=photo_codec_invalidate(slot,diagnostic);
    xSemaphoreGive(codec_mutex);return error;
}

esp_err_t photo_worker_prepare(unsigned slot,uint32_t length,photo_diagnostic_t *diagnostic)
{
    /* Foreground finish owns a stable uploaded source until settings publication. */
    if(!enabled){if(diagnostic)diagnostic->status=PHOTO_STORAGE;return ESP_ERR_INVALID_STATE;}
    xSemaphoreTake(codec_mutex,portMAX_DELAY);
    esp_err_t error=photo_codec_prepare(slot,length,false,diagnostic);
    xSemaphoreGive(codec_mutex);return error;
}

esp_err_t photo_worker_draw(unsigned slot,uint32_t length,bool blocking,
    int (*row)(void *,uint32_t,const uint16_t *,uint32_t),void *context)
{
    /* UI never waits for a slow producer; synchronous callers share the same
     * real prepare/cache path. Source updates are excluded while drawing. */
    if(!enabled)return ESP_ERR_INVALID_STATE;
    if(xSemaphoreTake(codec_mutex,blocking ? portMAX_DELAY:0)!=pdTRUE)return ESP_ERR_INVALID_STATE;
    if(xSemaphoreTake(media_mutex,blocking ? portMAX_DELAY:0)!=pdTRUE) {
        xSemaphoreGive(codec_mutex);return ESP_ERR_INVALID_STATE;
    }
    bool current=source_current_unlocked(slot,length);xSemaphoreGive(media_mutex);
    esp_err_t error=ESP_ERR_INVALID_STATE;photo_diagnostic_t diagnostic;
    if(current) {
        error=blocking ? photo_codec_prepare(slot,length,false,&diagnostic):ESP_OK;
        if(error==ESP_OK) {
            if(xSemaphoreTake(media_mutex,blocking ? portMAX_DELAY:0)==pdTRUE) {
                if(source_current_unlocked(slot,length))error=photo_codec_draw(slot,length,row,context,&diagnostic);
                else error=ESP_ERR_INVALID_STATE;
                xSemaphoreGive(media_mutex);
            } else error=ESP_ERR_INVALID_STATE;
        }
    }
    if(error==ESP_OK)record_result(slot,length,true,false);
    xSemaphoreGive(codec_mutex);
    return error;
}

void photo_worker_forget(unsigned slot)
{
    /* Called before source invalidation. Pending jobs cannot authorize stale data. */
    if(slot>=PHOTO_COUNT)return;
    portENTER_CRITICAL(&state_lock);ready&=~(1u<<slot);ready_lengths[slot]=0;failed_lengths[slot]=0;portEXIT_CRITICAL(&state_lock);
}

void photo_worker_publish(unsigned slot,uint32_t length)
{
    /* The source length was committed and upload ownership released first. */
    if(slot<PHOTO_COUNT)record_result(slot,length,true,false);
}

void photo_worker_request(unsigned slot)
{
    /* De-duplicate UI misses and permanent decode failures; queueing never waits. */
    if(!enabled || slot>=PHOTO_COUNT || media_upload_active())return;
    tv_settings_t settings;settings_snapshot(&settings);uint32_t length=settings.photo_size[slot];
    if(!length)return;
    portENTER_CRITICAL(&state_lock);
    bool needed=!(pending&(1u<<slot)) &&
        (!(ready&(1u<<slot)) || ready_lengths[slot]!=length) && failed_lengths[slot]!=length;
    if(needed)pending|=1u<<slot;
    portEXIT_CRITICAL(&state_lock);
    if(!needed)return;
    photo_job_t job={.slot=slot,.length=length};
    if(xQueueSend(jobs,&job,0)!=pdTRUE) {
        portENTER_CRITICAL(&state_lock);pending&=~(1u<<slot);portEXIT_CRITICAL(&state_lock);
    }
}

uint32_t photo_worker_ready_mask(void)
{
    /* Publish only lengths that still match the committed settings snapshot. */
    tv_settings_t settings;settings_snapshot(&settings);
    portENTER_CRITICAL(&state_lock);
    for(unsigned slot=0;slot<PHOTO_COUNT;++slot)
        if(ready_lengths[slot]!=settings.photo_size[slot])ready&=~(1u<<slot);
    uint32_t mask=ready;portEXIT_CRITICAL(&state_lock);return mask;
}

bool photo_worker_idle(void)
{
    /* Slideshow can retain its fade phase while the codec is busy; clock work
     * and immutable animations continue in their ordinary coordinator loop. */
    if(!enabled || media_upload_active() || xSemaphoreTake(codec_mutex,0)!=pdTRUE)return false;
    xSemaphoreGive(codec_mutex);return true;
}
