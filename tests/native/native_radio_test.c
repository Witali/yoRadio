#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "audio_service.h"
#include "native_state.h"
#include "file_transaction.h"

static bool lock_timeout,fail_play,fail_commit,fail_index;
static unsigned plays,stops,resets;
static uint32_t generation;
static native_state_t state;
static int saved_station=-1,saved_smartstart=-1,pending_station,pending_smartstart;
static const char *mapped(const char *path) {
    assert(!strncmp(path,"/spiffs/data/",13));return path+13;
}
static FILE *test_fopen(const char *path,const char *mode) {return fopen(mapped(path),mode);}
static int test_remove(const char *path) {return remove(mapped(path));}
static int test_rename(const char *from,const char *to) {
    if(fail_index && strstr(from,"index.dat.tmp")) {errno=EIO;return -1;}
    if (!access(mapped(to),F_OK)) {errno=EEXIST;return -1;}
    return rename(mapped(from),mapped(to));
}
static int test_stat(const char *path,struct stat *info) {return stat(mapped(path),info);}
#define fopen(...) test_fopen(__VA_ARGS__)
#define remove(...) test_remove(__VA_ARGS__)
#define rename(...) test_rename(__VA_ARGS__)
#define stat(...) test_stat(__VA_ARGS__)
#include "file_transaction.c"
#include "radio-under-test.inc"
#undef fopen
#undef remove
#undef rename
#undef stat

SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    SemaphoreHandle_t result=malloc(sizeof(*result));assert(result);assert(!pthread_mutex_init(result,NULL));return result;
}
int xSemaphoreTake(SemaphoreHandle_t lock,unsigned wait) {(void)wait;if (lock_timeout)return 0;assert(!pthread_mutex_lock(lock));return 1;}
void xSemaphoreGive(SemaphoreHandle_t lock) {assert(!pthread_mutex_unlock(lock));}
size_t strlcpy(char *out,const char *in,size_t size) {size_t n=strlen(in);if (size){size_t k=n<size-1?n:size-1;memcpy(out,in,k);out[k]=0;}return n;}
int64_t esp_timer_get_time(void) {return 0;}
const char *esp_err_to_name(esp_err_t result) {(void)result;return "test";}
esp_err_t nvs_open(const char *name,int mode,nvs_handle_t *handle) {
    assert(!strcmp(name,"radio"));*handle=1;
    if (mode==NVS_READONLY && saved_station<0 && saved_smartstart<0) return ESP_ERR_NVS_NOT_FOUND;
    pending_station=saved_station;pending_smartstart=saved_smartstart;return ESP_OK;
}
void nvs_close(nvs_handle_t handle) {assert(handle==1);}
esp_err_t nvs_get_u16(nvs_handle_t handle,const char *key,uint16_t *out) {
    assert(handle==1 && !strcmp(key,"last_station"));if(saved_station<0)return ESP_ERR_NVS_NOT_FOUND;*out=(uint16_t)saved_station;return ESP_OK;
}
esp_err_t nvs_get_u8(nvs_handle_t handle,const char *key,uint8_t *out) {
    assert(handle==1 && !strcmp(key,"smartstart"));if(saved_smartstart<0)return ESP_ERR_NVS_NOT_FOUND;*out=(uint8_t)saved_smartstart;return ESP_OK;
}
esp_err_t nvs_set_u16(nvs_handle_t handle,const char *key,uint16_t value) {
    assert(handle==1 && !strcmp(key,"last_station"));pending_station=value;return ESP_OK;
}
esp_err_t nvs_set_u8(nvs_handle_t handle,const char *key,uint8_t value) {
    assert(handle==1 && !strcmp(key,"smartstart"));pending_smartstart=value;return ESP_OK;
}
esp_err_t nvs_commit(nvs_handle_t handle) {
    assert(handle==1);if(fail_commit)return ESP_FAIL;saved_station=pending_station;saved_smartstart=pending_smartstart;return ESP_OK;
}
static void begin_audio(const char *url,const char *status) {
    ++generation;
#ifdef TEST_CYD
    native_state_begin_audio(&state,generation,url,status);
#else
    native_state_begin_stream(&state,generation);if(url)native_state_set_station(&state,url);
    native_state_set_audio(&state,generation,false,status);
#endif
}
esp_err_t audio_service_play(const char *url,native_codec_t codec) {
    assert(url && !strncmp(url,"http",4) && codec==NATIVE_CODEC_AUTO);
    if(fail_play)return ESP_FAIL;
    ++plays;begin_audio(url,"connecting");native_state_set_pending(&state,generation,true);return ESP_OK;
}
void audio_service_stop(void) {++stops;begin_audio(NULL,"stopped");}
void native_audio_output_request_normalizer_reset(void) {++resets;}
static void boot(void) {
    s_state=NULL;s_current_item=1;s_smartstart=SMARTSTART_DISABLED;s_playlist_count=0;
    strcpy(s_current_name,"yoRadio native");s_current_url[0]=0;
    assert(radio_control_init(&state)==ESP_OK);
}
static void *stress(void *arg) {
    for (unsigned i=0;i<250;++i) {
        assert(((i+(uintptr_t)arg)%3==0 ? radio_control_toggle() :
            (i+(uintptr_t)arg)%3==1 ? radio_control_next() : radio_control_previous())==ESP_OK);
    }
    return NULL;
}
int main(void) {
    char directory[]="/tmp/yoradio-radio-XXXXXX";assert(mkdtemp(directory));assert(!chdir(directory));
    native_state_init(&state);
    assert(radio_control_play(1)==ESP_ERR_INVALID_STATE);assert(radio_control_init(NULL)==ESP_ERR_INVALID_ARG);
    boot();assert(!radio_control_playlist_count() && radio_control_play(1)==ESP_ERR_NOT_FOUND);
    FILE *csv=fopen("playlist.csv","wb");assert(csv);
    assert(fputs("One\thttp://one.example/live\t128\nTwo\thttps://two.example/live\t64\nThree\thttp://three.example/live\t64\n",csv)>=0);assert(!fclose(csv));
    assert(radio_control_reindex_playlist()==ESP_OK && radio_control_playlist_count()==3);
    fail_index=true;
    assert(radio_control_reindex_playlist()==ESP_FAIL && radio_control_playlist_count()==3);
    csv=fopen("playlist.csv","wb");assert(csv);
    assert(fputs("Changed first station\thttp://changed.example/live\t128\nTwo\thttps://two.example/live\t64\n",csv)>=0);assert(!fclose(csv));
    assert(radio_control_reindex_playlist()==ESP_FAIL && !radio_control_playlist_count());
    assert(radio_control_play(2)==ESP_ERR_NOT_FOUND && !plays);
    fail_index=false;saved_station=2;saved_smartstart=SMARTSTART_PLAYING;
    boot();assert(radio_control_playlist_count()==2 && !strcmp(state.station,"Two"));
    csv=fopen("playlist.csv","wb");assert(csv);
    assert(fputs("One\thttp://one.example/live\t128\nTwo\thttps://two.example/live\t64\nThree\thttp://three.example/live\t64\n",csv)>=0);assert(!fclose(csv));
    assert(radio_control_reindex_playlist()==ESP_OK);saved_smartstart=SMARTSTART_DISABLED;
    boot();plays=stops=0;
    assert(radio_control_play(2)==ESP_OK && plays==1 && state.audio_pending && !state.audio_running);
    assert(!strcmp(state.station,"Two") && saved_station==2);
    assert(radio_control_toggle()==ESP_OK && stops==1 && !state.audio_pending && !state.audio_running);
    assert(radio_control_next()==ESP_OK && radio_control_current_item()==3);
    assert(radio_control_next()==ESP_OK && radio_control_current_item()==1);
    assert(radio_control_previous()==ESP_OK && radio_control_current_item()==3);
    fail_play=true;assert(radio_control_play(1)==ESP_FAIL && radio_control_current_item()==3);fail_play=false;
    native_state_set_pending(&state,generation-1,false);assert(state.audio_pending);
    native_state_set_audio(&state,generation-1,true,"stale");assert(state.audio_pending && !state.audio_running);
    native_state_set_audio(&state,generation,true,"PCM");assert(state.audio_running && !state.audio_pending);
    native_state_set_audio(&state,generation,false,"EOF");assert(!state.audio_pending);
    assert(radio_control_toggle()==ESP_OK && state.audio_pending);
    fail_commit=true;assert(radio_control_set_smartstart_enabled(true)==ESP_FAIL);
    assert(!radio_control_smartstart_enabled());fail_commit=false;
    assert(radio_control_set_smartstart_enabled(true)==ESP_OK && saved_smartstart==SMARTSTART_PLAYING);
    assert(radio_control_stop()==ESP_OK && saved_smartstart==SMARTSTART_STOPPED);
    assert(radio_control_smartstart_enabled());
    fail_commit=true;assert(radio_control_play(2)==ESP_OK && radio_control_current_item()==2);fail_commit=false;
    saved_station=2;saved_smartstart=SMARTSTART_PLAYING;unsigned before=plays;
    boot();assert(plays==before+1 && radio_control_current_item()==2 && !strcmp(state.station,"Two"));
    saved_station=99;saved_smartstart=SMARTSTART_DISABLED;boot();assert(radio_control_current_item()==1);
    lock_timeout=true;assert(radio_control_play(1)==ESP_ERR_TIMEOUT && !radio_control_playlist_count());lock_timeout=false;
    pthread_t first,second;assert(!pthread_create(&first,NULL,stress,(void *)0));assert(!pthread_create(&second,NULL,stress,(void *)1));
    assert(!pthread_join(first,NULL) && !pthread_join(second,NULL));
    char name[144];radio_control_current_name(name,sizeof(name));assert(name[0]);
    radio_control_snapshot_t snapshot;assert(radio_control_snapshot(&snapshot));
    assert(snapshot.item==radio_control_current_item() && snapshot.count==3 && !strcmp(snapshot.name,name));
    assert(!radio_control_snapshot(NULL));
    memset(&snapshot,1,sizeof(snapshot));lock_timeout=true;assert(!radio_control_snapshot(&snapshot));lock_timeout=false;
    assert(!snapshot.item && !snapshot.name[0]);
#ifdef TEST_CYD
    assert(!resets);
#else
    assert(resets);
#endif
    assert(!pthread_mutex_destroy(s_lock));free(s_lock);
    assert(!pthread_mutex_destroy(state.lock));free(state.lock);
    remove("playlist.csv");remove("index.dat");remove("index.dat.tmp");remove("index.dat.bak");
    assert(!chdir("/"));assert(!rmdir(directory));
    puts("PASS shared radio: pending Toggle/PCM/EOF/stale callbacks; indexed Play/Next/Prev/wrap; boot restore/SmartStart; NVS failure; 500 concurrent commands; ASan/UBSan");
    return 0;
}
