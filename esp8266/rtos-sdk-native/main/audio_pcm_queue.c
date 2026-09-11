#include "audio_pcm_queue.h"
#include "native_audio_output.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <string.h>

enum { SLOT_FREE, SLOT_FILLING, SLOT_READY, SLOT_READING };
typedef struct { uint16_t offset, count; uint8_t state; } pcm_slot_t;
static pcm_slot_t s_slots[AUDIO_PCM_QUEUE_SLOTS];
static uint8_t s_ready[AUDIO_PCM_QUEUE_SLOTS], s_head, s_count;
static int16_t *s_pool;
static uint32_t s_generation;
static bool s_running, s_busy;
static TaskHandle_t s_worker, s_producer;
static audio_pcm_generation_fn s_valid;
static audio_pcm_progress_fn s_progress;
static audio_pcm_queue_health_t s_health;

/* Only call with the scheduler critical section held. No waits/PCM work in it. */
static void discard_ready(void) {
    while (s_count) {
        unsigned index = s_ready[s_head];
        s_head = (s_head + 1U) % AUDIO_PCM_QUEUE_SLOTS;
        --s_count;
        s_slots[index].state = SLOT_FREE;
    }
}
static void notify_producer(void) {
    taskENTER_CRITICAL();
    TaskHandle_t producer = s_producer;
    taskEXIT_CRITICAL();
    if (producer) xTaskNotifyGive(producer);
}
static void output_task(void *unused) {
    (void)unused;
    for (;;) {
        unsigned index = AUDIO_PCM_QUEUE_SLOTS;
        int16_t *pcm = NULL;
        uint16_t count = 0;
        uint32_t generation = 0;
        taskENTER_CRITICAL();
        if (!s_running) discard_ready();
        if (s_running && s_count) {
            index = s_ready[s_head];
            s_head = (s_head + 1U) % AUDIO_PCM_QUEUE_SLOTS;
            --s_count;
            s_slots[index].state = SLOT_READING;
            pcm = s_pool + index * AUDIO_PCM_QUEUE_FRAMES + s_slots[index].offset;
            count = s_slots[index].count;
            generation = s_generation;
            s_busy = true;
        }
        taskEXIT_CRITICAL();
        if (!pcm) {
            notify_producer();
            ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
            continue;
        }
        esp_err_t result = ESP_OK;
        /* Preserve the old callback boundaries (512 plus remainder), including
         * normalization/gain semantics. DMA256 is filled inside each call. */
        for (size_t offset = 0; offset < count; offset += 512U) {
            taskENTER_CRITICAL();
            bool running = s_running;
            taskEXIT_CRITICAL();
            if (!running || !s_valid(generation)) break;
            size_t frames = count - offset;
            if (frames > 512U) frames = 512U;
            int64_t started = esp_timer_get_time();
            result = native_audio_output_write(pcm + offset, frames, 48000U, 1);
            uint32_t elapsed = (uint32_t)(esp_timer_get_time() - started);
            taskENTER_CRITICAL();
            ++s_health.output_calls;
            s_health.output_us += elapsed;
            if (result == ESP_OK) s_health.output_frames += frames;
            taskEXIT_CRITICAL();
            if (result != ESP_OK) break;
            s_progress(generation, frames);
        }
        taskENTER_CRITICAL();
        if (result != ESP_OK) { s_health.error = (uint32_t)result; s_running = false; }
        s_slots[index].state = SLOT_FREE;
        s_busy = false;
        if (!s_running) discard_ready();
        taskEXIT_CRITICAL();
        notify_producer();
    }
}
esp_err_t audio_pcm_queue_init(audio_pcm_generation_fn valid, audio_pcm_progress_fn progress) {
    if (!valid || !progress || s_worker) return ESP_ERR_INVALID_STATE;
    s_valid = valid; s_progress = progress;
    if (xTaskCreate(output_task, "pcm-output", AUDIO_PCM_QUEUE_STACK_BYTES, NULL,
                    6U, &s_worker) != pdPASS) { s_worker = NULL; return ESP_ERR_NO_MEM; }
    return ESP_OK;
}
void audio_pcm_queue_deinit(void) {
    if (!s_worker) return;
    audio_pcm_queue_stop();
    vTaskDelete(s_worker);
    s_worker = NULL;
}
esp_err_t audio_pcm_queue_begin(int16_t *pool, size_t samples, uint32_t generation) {
    if (!s_worker || !pool || ((uintptr_t)pool & 1U) ||
        samples != AUDIO_PCM_QUEUE_SLOTS * AUDIO_PCM_QUEUE_FRAMES) return ESP_ERR_INVALID_ARG;
    taskENTER_CRITICAL();
    if (s_pool || s_busy || s_running) { taskEXIT_CRITICAL(); return ESP_ERR_INVALID_STATE; }
    memset(s_slots, 0, sizeof(s_slots));
    memset(&s_health, 0, sizeof(s_health));
    s_head = s_count = 0;
    s_pool = pool; s_generation = generation;
    s_producer = xTaskGetCurrentTaskHandle();
    s_running = true;
    taskEXIT_CRITICAL();
    return ESP_OK;
}
int audio_pcm_queue_acquire(void *unused, int16_t **pcm, int samples) {
    (void)unused;
    if (!pcm || samples <= 0 || samples > (int)AUDIO_PCM_QUEUE_FRAMES) return -108;
    *pcm = NULL;
    for (;;) {
        taskENTER_CRITICAL();
        bool running = s_running && s_pool && !s_health.error;
        uint32_t generation = s_generation;
        taskEXIT_CRITICAL();
        if (!running || !s_valid(generation)) return -108;
        taskENTER_CRITICAL();
        if (!s_running || !s_pool || s_health.error) {
            taskEXIT_CRITICAL();
            return -108;
        }
        for (unsigned i = 0; i < AUDIO_PCM_QUEUE_SLOTS; ++i) {
            if (s_slots[i].state != SLOT_FREE) continue;
            s_slots[i].state = SLOT_FILLING;
            *pcm = s_pool + i * AUDIO_PCM_QUEUE_FRAMES;
            break;
        }
        taskEXIT_CRITICAL();
        if (*pcm) return 0;
        /* Predicate is rechecked even on timeout/spurious DMA notifications. */
        ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(20U));
    }
}
void audio_pcm_queue_release(void *unused, int16_t *pcm) {
    (void)unused;
    taskENTER_CRITICAL();
    for (unsigned i = 0; s_pool && i < AUDIO_PCM_QUEUE_SLOTS; ++i)
        if (pcm == s_pool + i * AUDIO_PCM_QUEUE_FRAMES && s_slots[i].state == SLOT_FILLING)
            s_slots[i].state = SLOT_FREE;
    taskEXIT_CRITICAL();
}
bool audio_pcm_queue_submit(int16_t *pcm, size_t samples) {
    bool accepted = false;
    taskENTER_CRITICAL();
    if (s_running && s_pool && samples && s_count < AUDIO_PCM_QUEUE_SLOTS && !s_health.error) {
        uintptr_t address = (uintptr_t)pcm, base = (uintptr_t)s_pool;
        size_t bytes = AUDIO_PCM_QUEUE_SLOTS * AUDIO_PCM_QUEUE_FRAMES * sizeof(int16_t);
        if (!(address & 1U) && address >= base && address - base < bytes) {
            size_t offset = (address - base) / sizeof(int16_t);
            unsigned index = offset / AUDIO_PCM_QUEUE_FRAMES;
            offset %= AUDIO_PCM_QUEUE_FRAMES;
            if (samples <= AUDIO_PCM_QUEUE_FRAMES - offset && s_slots[index].state == SLOT_FILLING) {
                s_slots[index].offset = offset; s_slots[index].count = samples;
                s_slots[index].state = SLOT_READY;
                s_ready[(s_head + s_count) % AUDIO_PCM_QUEUE_SLOTS] = index;
                ++s_count; s_health.submitted_frames += samples;
                accepted = true;
            }
        }
    }
    taskEXIT_CRITICAL();
    if (accepted) xTaskNotifyGive(s_worker);
    return accepted;
}
void audio_pcm_queue_stop(void) {
    if (!s_worker) return;
    taskENTER_CRITICAL();
    s_running = false;
    discard_ready();
    taskEXIT_CRITICAL();
    xTaskNotifyGive(s_worker);
    for (;;) {
        taskENTER_CRITICAL();
        bool owned = s_busy;
        for (unsigned i = 0; i < AUDIO_PCM_QUEUE_SLOTS; ++i)
            owned = owned || s_slots[i].state == SLOT_FILLING || s_slots[i].state == SLOT_READING;
        if (!owned) { s_pool = NULL; s_producer = NULL; }
        taskEXIT_CRITICAL();
        if (!owned) return;
        /* Never free/reset still-owned PCM after a timeout. The DMA write has
         * its own bounded timeout; this owner sleeps until its acknowledgement. */
        ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(20U));
    }
}
void audio_pcm_queue_drain(void) {
    for (;;) {
        taskENTER_CRITICAL();
        bool pending = s_running && (s_busy || s_count);
        uint32_t generation = s_generation;
        taskEXIT_CRITICAL();
        if (!pending || !s_valid(generation)) return;
        ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(20U));
    }
}
void audio_pcm_queue_health(audio_pcm_queue_health_t *health) {
    if (!health) return;
    taskENTER_CRITICAL();
    *health = s_health;
    health->ready_frames = 0;
    for (unsigned i = 0; i < AUDIO_PCM_QUEUE_SLOTS; ++i)
        if (s_slots[i].state == SLOT_READY) health->ready_frames += s_slots[i].count;
    taskEXIT_CRITICAL();
    health->stack_free = s_worker ? uxTaskGetStackHighWaterMark(s_worker) : 0;
}
