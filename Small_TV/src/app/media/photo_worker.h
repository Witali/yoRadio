#pragma once
#include "photo_codec.h"

/* Network submits an owned closure; only after successful enqueue does the
 * worker own its context. Queue rejection leaves cleanup to the caller. */
esp_err_t photo_worker_init(void);
esp_err_t photo_worker_submit(void (*function)(void *),void *context);
esp_err_t photo_worker_invalidate(unsigned slot,photo_diagnostic_t *diagnostic);
esp_err_t photo_worker_prepare(unsigned slot,uint32_t length,photo_diagnostic_t *diagnostic);
esp_err_t photo_worker_draw(unsigned slot,uint32_t length,bool blocking,
    int (*row)(void *,uint32_t,const uint16_t *,uint32_t),void *context);
void photo_worker_forget(unsigned slot);
void photo_worker_publish(unsigned slot,uint32_t length);
void photo_worker_request(unsigned slot);
uint32_t photo_worker_ready_mask(void);
uint32_t photo_worker_failed_mask(void);
bool photo_worker_idle(void);
