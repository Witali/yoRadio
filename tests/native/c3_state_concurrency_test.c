#include <assert.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native_state.h"
#ifndef C3_HAS_STREAM_TITLE
// Compile the pre-fix state API for the negative-control run as well. The
// deterministic preemption assertion fails before reaching contention tests.
#define native_state_set_stream_title(state,generation,title) native_state_set_title(state,title)
#endif

static native_state_t state;
static native_state_t *s_state=&state;
static atomic_uint s_generation;
static void (*before_take)(void);
#define ESP_LOGI(...) ((void)0)
#include "production.inc"

SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    pthread_mutex_t *mutex=malloc(sizeof(*mutex));
    assert(mutex && !pthread_mutex_init(mutex,NULL));return mutex;
}
int xSemaphoreTake(SemaphoreHandle_t mutex,unsigned timeout) {
    (void)timeout;
    if (before_take) {void (*hook)(void)=before_take;before_take=NULL;hook();}
    assert(!pthread_mutex_lock(mutex));return pdTRUE;
}
void xSemaphoreGive(SemaphoreHandle_t mutex) {assert(!pthread_mutex_unlock(mutex));}
size_t strlcpy(char *to,const char *from,size_t capacity) {
    size_t size=strlen(from),copy=size<capacity ? size : capacity-1;
    if (capacity) {memcpy(to,from,copy);to[copy]=0;}return size;
}
static void change_station_before_title_lock(void) {
    atomic_store(&s_generation,2);
    native_state_begin_stream(&state,2);
    // This is the new stream's valid metadata. An old callback must neither
    // overwrite it nor clear it in a subsequent generation recheck.
    publish_icy_title(2,"current title");
}
static void *stale_writer(void *unused) {
    (void)unused;
    for (unsigned i=0;i<10000;++i) {
        // Deliberately pass the old identity directly to the state function,
        // including empty titles which previously could clear newer metadata.
        native_state_set_stream_title(&state,1,i&1 ? "stale title" : "");
    }
    return NULL;
}
static void *current_writer(void *unused) {
    (void)unused;
    for (unsigned i=0;i<10000;++i) {
        native_state_set_stream_title(&state,2,"current title");
        native_state_t snapshot;native_state_snapshot(&state,&snapshot);
        assert(snapshot.audio_generation==2 && !strcmp(snapshot.title,"current title"));
    }
    return NULL;
}
int main(void) {
    native_state_init(&state);atomic_init(&s_generation,1);
    native_state_begin_stream(&state,1);
    publish_icy_title(1,"old title");assert(!strcmp(state.title,"old title"));
    before_take=change_station_before_title_lock;
    publish_icy_title(1,"late old title");
    assert(state.audio_generation==2 && !strcmp(state.title,"current title"));
    publish_icy_title(1,"");publish_icy_title(1,"stale");publish_icy_title(2,NULL);
    assert(!strcmp(state.title,"current title"));
    pthread_t stale,current;
    assert(!pthread_create(&stale,NULL,stale_writer,NULL));
    assert(!pthread_create(&current,NULL,current_writer,NULL));
    assert(!pthread_join(stale,NULL) && !pthread_join(current,NULL));
    char long_title[512];memset(long_title,'a',sizeof(long_title)-1);long_title[511]=0;
    native_state_set_stream_title(&state,2,long_title);
    assert(strlen(state.title)==sizeof(state.title)-1);
    native_state_set_stream_title(&state,2,"");assert(!state.title[0]);
    // The identity comparison is equality, including UINT32_MAX -> zero wrap.
    state.audio_generation=UINT32_MAX;atomic_store(&s_generation,0);
    native_state_begin_stream(&state,0);publish_icy_title(0,"wrapped");
    native_state_set_stream_title(&state,UINT32_MAX,"stale");
    assert(!strcmp(state.title,"wrapped"));
    pthread_mutex_destroy(state.lock);free(state.lock);
    puts("PASS C3 title: preemption before state lock preserves newer metadata; stale clear rejected; 20000 contended updates, bounds and generation wrap; ASan/UBSan");
    return 0;
}
