#ifndef CYD_FAMILY1_REFERENCE_CONTRACT_H
#define CYD_FAMILY1_REFERENCE_CONTRACT_H
#include <stdbool.h>
#include <stddef.h>
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
enum { F1_REFERENCE_COUNT=13, F1_REFERENCE_DONE=8 };
typedef struct { bool complete;size_t bytes;char sha[65]; } f1_reference_t;
#ifdef __cplusplus
extern "C" {
#endif
extern f1_reference_t f1_references[F1_REFERENCE_COUNT];
extern EventGroupHandle_t f1_reference_events;
void f1_public_reference_worker(void *);
#ifdef __cplusplus
}
#endif
#endif
