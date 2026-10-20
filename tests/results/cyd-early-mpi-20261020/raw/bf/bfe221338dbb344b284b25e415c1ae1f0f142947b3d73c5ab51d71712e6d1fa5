#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "platform.h"
#include "sdkconfig.h"
#include "native_tls_early_mpi.h"
static unsigned phase,acquires,releases,tasks;
static bool held;
static void fail(const char *s) { fprintf(stderr,"EARLY_MPI_HOST_FAILURE %s\n",s); exit(2); }
void event(unsigned id) {
    if (CONFIG_YORADIO_TLS_EARLY_MPI_LOCK && phase != 2) fail("startup_before_warm");
    if (id != 3) fail("event_id");
}
void esp_crypto_mpi_lock_acquire(void) {
    if (held || phase) fail("acquire_order");
    held=true;phase=1;++acquires;
}
void esp_crypto_mpi_lock_release(void) {
    if (!held || phase!=1) fail("release_without_acquire");
    held=false;phase=2;++releases;
}
void error_check(int result) { if(result) fail("unexpected_startup_error"); }
int native_health_start(void) { event(3);return 1; }
void native_state_init(native_state_t *s) { event(3);s->network_mode=0; }
void native_state_snapshot(native_state_t *s,native_state_t *out) { *out=*s; }
void native_state_set_network(native_state_t *s,int m,int v) { (void)v;s->network_mode=m; }
int nvs_flash_init(void) { event(3);return 0; }
int native_audio_settings_init(void) { event(3);return 0; }
int network_settings_init(void) { event(3);return 0; }
int esp_vfs_spiffs_register(const esp_vfs_spiffs_conf_t *c) { event(3);if(c->format_if_mount_failed)fail("format_policy");return 0; }
int cyd_display_init(cyd_display_t *d) { (void)d;event(3);return 0; }
int time_service_start(void) { event(3);return 0; }
int audio_service_start(native_state_t *s) { (void)s;return 0; }
int radio_control_init(native_state_t *s) { (void)s;return 0; }
int network_service_start(native_state_t *s) { (void)s;return 0; }
int web_service_start(native_state_t *s) { (void)s;return 0; }
int cyd_display_rows_per_transfer(cyd_display_t *d) { (void)d;return 10; }
uint16_t *cyd_display_acquire_buffer(cyd_display_t *d) { (void)d;return NULL; }
int cyd_display_draw_bitmap(cyd_display_t *d,int a,int b,int c,int e,uint16_t *p) { (void)d;(void)a;(void)b;(void)c;(void)e;(void)p;return 0; }
void cyd_display_flush(cyd_display_t *d) { (void)d; }
void vTaskDelete(void *p) { (void)p; }
void vTaskDelay(unsigned t) { (void)t; }
int xTaskCreatePinnedToCore(void (*fn)(void *),const char *name,unsigned stack,void *arg,unsigned priority,void *handle,int core) {
    (void)fn;(void)arg;(void)handle;event(3);
    if(core!=0)fail("existing_core_affinity");
    if(!tasks && (strcmp(name,"display") || stack!=BOARD_TASK_STACK_DISPLAY || priority!=1))fail("display_profile");
    if(tasks==1 && (strcmp(name,"network") || stack!=BOARD_TASK_STACK_NETWORK || priority!=3))fail("network_profile");
    ++tasks;return 1;
}
const char *esp_err_to_name(int r) { (void)r;return "stub"; }
void app_main(void);
int main(void) {
    app_main();
    if(held || tasks!=2 || acquires!=(unsigned)CONFIG_YORADIO_TLS_EARLY_MPI_LOCK || releases!=acquires)fail("final_order");
    puts("EARLY_MPI_HOST_COMPLETE actual_module=1 actual_app_main_copy=1");
    return 0;
}
