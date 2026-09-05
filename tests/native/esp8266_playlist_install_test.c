#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
/* FILE_HELPERS */
typedef int esp_err_t;
enum { ESP_OK=0, ESP_FAIL=-1, ESP_ERR_INVALID_STATE=-2 };
#define PLAYLIST_PATH "playlist.csv"
#define PLAYLIST_INDEX_PATH "playlist.idx"
#define portMAX_DELAY 0
static int s_lock=1, s_count, builds, fail_once;
static char s_line[672];
static void xSemaphoreTake(int lock, int timeout) { (void)lock; (void)timeout; }
static void xSemaphoreGive(int lock) { (void)lock; }
/* INSTALLER */
static void put(const char *path, const char *text) {
    FILE *f=fopen(path,"wb"); assert(f);
    assert(fwrite(text,1,strlen(text),f)==strlen(text));
    assert(!fclose(f));
}
static esp_err_t rebuild_locked(void) {
    ++builds;
    if(fail_once) { fail_once=0; return ESP_FAIL; }
    put(PLAYLIST_INDEX_PATH,"index"); s_count=1; return ESP_OK;
}
static void expect(const char *value) {
    char text[32]={0}; FILE *f=fopen(PLAYLIST_PATH,"rb"); assert(f);
    fread(text,1,sizeof(text)-1,f); fclose(f); assert(!strcmp(text,value));
}
int main(void) {
    bool changed=true;
    put(PLAYLIST_PATH,"old row\n"); put("upload.tmp","old row\n");
    assert(playlist_service_install("upload.tmp",&changed)==ESP_OK);
    assert(!changed && !builds && !file_exists("upload.tmp")); expect("old row\n");
    put("upload.tmp","new row\n");
    assert(playlist_service_install("upload.tmp",&changed)==ESP_OK);
    assert(changed && builds==1 && !file_exists(PLAYLIST_PATH ".bak")); expect("new row\n");
    put("upload.tmp","bad row\n"); fail_once=1;
    assert(playlist_service_install("upload.tmp",&changed)==ESP_FAIL);
    assert(!changed && builds==3 && s_count==1); expect("new row\n");
    assert(file_exists(PLAYLIST_INDEX_PATH) && !file_exists(PLAYLIST_PATH ".bak"));
    s_lock=0; changed=true;
    assert(playlist_service_install("missing",&changed)==ESP_ERR_INVALID_STATE && !changed);
    puts("Playlist install tests passed");
}
