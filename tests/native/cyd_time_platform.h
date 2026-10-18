#pragma once
#include "native_time_platform.h"

typedef unsigned nvs_handle_t;
#define ESP_ERR_NVS_TYPE_MISMATCH 0x1103
#define NVS_READONLY 0
#define NVS_READWRITE 1
static uint8_t flash_record[128], staged_record[128];
static size_t flash_size, staged_size;
static bool flash_present;
static bool flash_wrong_type;
static unsigned nvs_opens,nvs_closes,nvs_reads,nvs_sets,nvs_commits;
static unsigned fail_nvs_open,fail_nvs_get,fail_nvs_set,fail_nvs_commit;
static pthread_mutex_t commit_mutex=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t commit_cond=PTHREAD_COND_INITIALIZER;
static bool hold_commit,commit_waiting,release_commit;
static esp_err_t nvs_open(const char *ns,int mode,nvs_handle_t *out){assert(!strcmp(ns,"native_time"));nvs_opens++;if(fail_nvs_open)return ESP_FAIL;if(mode==NVS_READONLY&&!flash_present)return ESP_ERR_NVS_NOT_FOUND;*out=42;return ESP_OK;}
static void nvs_close(nvs_handle_t h){assert(h==42);nvs_closes++;}
static esp_err_t nvs_get_blob(nvs_handle_t h,const char *key,void *out,size_t *size){assert(h==42&&!strcmp(key,"cfg"));nvs_reads++;if(nvs_reads==fail_nvs_get)return ESP_FAIL;if(!flash_present)return ESP_ERR_NVS_NOT_FOUND;if(flash_wrong_type)return ESP_ERR_NVS_TYPE_MISMATCH;if(!out){*size=flash_size;return ESP_OK;}if(*size<flash_size){*size=flash_size;return ESP_ERR_NVS_INVALID_LENGTH;}memcpy(out,flash_record,flash_size);*size=flash_size;return ESP_OK;}
static esp_err_t nvs_set_blob(nvs_handle_t h,const char *key,const void *data,size_t n){assert(h==42&&!strcmp(key,"cfg")&&n<=128);nvs_sets++;if(fail_nvs_set)return ESP_FAIL;memcpy(staged_record,data,n);staged_size=n;return ESP_OK;}
static esp_err_t nvs_commit(nvs_handle_t h){assert(h==42);nvs_commits++;assert(!pthread_mutex_lock(&commit_mutex));if(hold_commit){commit_waiting=true;pthread_cond_broadcast(&commit_cond);while(!release_commit)pthread_cond_wait(&commit_cond,&commit_mutex);}pthread_mutex_unlock(&commit_mutex);if(fail_nvs_commit)return ESP_FAIL;memcpy(flash_record,staged_record,staged_size);flash_size=staged_size;flash_present=true;return ESP_OK;}

static int64_t monotonic_us;
static int64_t esp_timer_get_time(void){return monotonic_us;}
static time_t host_time(time_t *out){if(out)*out=wall_epoch;return wall_epoch;}
typedef void(*TaskFunction_t)(void*);
typedef struct host_task {pthread_t thread;pthread_mutex_t mutex;pthread_cond_t cond;TaskFunction_t fn;void *arg;unsigned credits,parks;uint32_t events;bool stop;} *TaskHandle_t;
static TaskHandle_t created_task;
static _Thread_local TaskHandle_t current_task;
static bool fail_task;
static unsigned task_creates;
static void *task_entry(void *p){current_task=p;current_task->fn(current_task->arg);return NULL;}
static int xTaskCreate(TaskFunction_t fn,const char *name,unsigned stack,void *arg,unsigned priority,TaskHandle_t *out){task_creates++;assert(!strcmp(name,"time_sync")&&stack==2048&&priority==1);if(fail_task)return pdFALSE;TaskHandle_t t=calloc(1,sizeof(*t));assert(t);pthread_mutex_init(&t->mutex,NULL);pthread_cond_init(&t->cond,NULL);t->fn=fn;t->arg=arg;*out=t;created_task=t;assert(!pthread_create(&t->thread,NULL,task_entry,t));return pdPASS;}
#define eSetBits 0
static int xTaskNotify(TaskHandle_t t,uint32_t bits,int mode){assert(mode==eSetBits);pthread_mutex_lock(&t->mutex);t->events|=bits;pthread_cond_broadcast(&t->cond);pthread_mutex_unlock(&t->mutex);return pdTRUE;}
static int xTaskNotifyWait(uint32_t clear_entry,uint32_t clear_exit,uint32_t *events,unsigned ticks){assert(!clear_entry&&clear_exit==UINT32_MAX&&ticks==1000);TaskHandle_t t=current_task;pthread_mutex_lock(&t->mutex);t->parks++;pthread_cond_broadcast(&t->cond);while(!t->credits&&!t->stop)pthread_cond_wait(&t->cond,&t->mutex);if(t->stop){pthread_mutex_unlock(&t->mutex);pthread_exit(NULL);}t->credits--;*events=t->events;t->events=0;pthread_mutex_unlock(&t->mutex);return pdTRUE;}
static void step(void){TaskHandle_t t=created_task;assert(t);pthread_mutex_lock(&t->mutex);while(!t->parks)pthread_cond_wait(&t->cond,&t->mutex);unsigned before=t->parks;t->credits++;pthread_cond_broadcast(&t->cond);while(t->parks==before)pthread_cond_wait(&t->cond,&t->mutex);pthread_mutex_unlock(&t->mutex);}
static void stop_task(void){TaskHandle_t t=created_task;if(!t)return;pthread_mutex_lock(&t->mutex);t->stop=true;pthread_cond_broadcast(&t->cond);pthread_mutex_unlock(&t->mutex);assert(!pthread_join(t->thread,NULL));pthread_mutex_destroy(&t->mutex);pthread_cond_destroy(&t->cond);free(t);created_task=NULL;}
