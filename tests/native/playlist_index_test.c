#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "file_transaction.h"

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_NOT_FOUND -2
#define ESP_ERR_INVALID_SIZE -3
#define ESP_LOGI(...) ((void)0)
#define PLAYLIST_PATH "playlist.csv"
#define PLAYLIST_INDEX_PATH "index.dat"
#define PLAYLIST_INDEX_TEMP_PATH "index.dat.tmp"
#define PLAYLIST_INDEX_BACKUP_PATH "index.dat.bak"
static uint16_t s_playlist_count;
static char s_playlist_line[768];
static bool fail_publish,fail_write,fail_flush,fail_close;
static int64_t esp_timer_get_time(void) {return 0;}
static size_t strlcpy(char *out,const char *in,size_t size) {
    size_t n=strlen(in);if (size) {size_t copy=n<size-1 ? n : size-1;memcpy(out,in,copy);out[copy]=0;}return n;
}
static int test_rename(const char *from,const char *to) {
    if (fail_publish && !strcmp(from,PLAYLIST_INDEX_TEMP_PATH)) {errno=EIO;return -1;}
    return rename(from,to);
}
static size_t test_fwrite(const void *data,size_t size,size_t count,FILE *file) {
    if (fail_write) {errno=EIO;return 0;}return fwrite(data,size,count,file);
}
static int test_fflush(FILE *file) {int result=fflush(file);return fail_flush ? EOF : result;}
static int test_fclose(FILE *file) {int result=fclose(file);return fail_close ? EOF : result;}
// Exercise the helper with the same real files and injected publication error.
// Only rename's mutation is a seam; all I/O and rollback remain production code.
#define rename(...) test_rename(__VA_ARGS__)
#define native_file_replace tested_file_replace
#define native_file_recover tested_file_recover
#include "file_transaction.c"
#define fwrite(...) test_fwrite(__VA_ARGS__)
#define fflush(...) test_fflush(__VA_ARGS__)
#define fclose(...) test_fclose(__VA_ARGS__)
#include "production.inc"
#undef fwrite
#undef fflush
#undef fclose
#undef rename

static void contents(const char *path,const char *text) {
    FILE *file=fopen(path,"wb");assert(file);assert(fwrite(text,1,strlen(text),file)==strlen(text));assert(!fclose(file));
}
static void original_index(void) {
    FILE *file=fopen(PLAYLIST_INDEX_PATH,"rb");assert(file);
    uint32_t offsets[3];assert(fread(offsets,sizeof(offsets[0]),3,file)==2);assert(!fclose(file));
    assert(offsets[0]==0 && offsets[1]==strlen("One\thttp://one.example/live\t128\n"));
}
static void normal(void) {
    contents(PLAYLIST_PATH,"One\thttp://one.example/live\t128\nTwo\thttps://two.example/live\t64\n");
    assert(build_playlist_index_locked()==ESP_OK && s_playlist_count==2);
    original_index();
    char name[144],url[512];
    assert(playlist_station(2,name,sizeof(name),url,sizeof(url)));
    assert(!strcmp(name,"Two") && !strcmp(url,"https://two.example/live"));
    assert(!playlist_station(0,name,sizeof(name),url,sizeof(url)));
    assert(!playlist_station(3,name,sizeof(name),url,sizeof(url)));
}
int main(void) {
    char directory[]="/tmp/yoradio-playlist-XXXXXX";assert(mkdtemp(directory));assert(!chdir(directory));
    normal();
    fail_publish=true;
    assert(build_playlist_index_locked()==ESP_FAIL);original_index();assert(s_playlist_count==2);
    fail_publish=false;
    fail_write=true;assert(build_playlist_index_locked()==ESP_FAIL);original_index();fail_write=false;
    fail_flush=true;assert(build_playlist_index_locked()==ESP_FAIL);original_index();fail_flush=false;
    fail_close=true;assert(build_playlist_index_locked()==ESP_FAIL);original_index();fail_close=false;
    assert(!rename(PLAYLIST_INDEX_PATH,PLAYLIST_INDEX_BACKUP_PATH));
    assert(load_playlist_index_locked()==ESP_OK && s_playlist_count==2);original_index();
    assert(!remove(PLAYLIST_PATH));
    assert(build_playlist_index_locked()==ESP_ERR_NOT_FOUND);original_index();
    normal();
    // A truncated fgets chunk must never become a second, invented CSV row.
    FILE *csv=fopen(PLAYLIST_PATH,"wb");assert(csv);
    for (unsigned i=0;i<767;++i) assert(fputc('x',csv)!=EOF);
    assert(fputs("Phantom\thttp://phantom.example/live\t64\nReal\thttp://real.example/live\t64\n",csv)>=0);
    assert(!fclose(csv));
    assert(build_playlist_index_locked()==ESP_OK && s_playlist_count==1);
    char name[144],url[512];assert(playlist_station(1,name,sizeof(name),url,sizeof(url)));
    assert(!strcmp(name,"Real"));
    // Zero stations and a final line without a newline are valid inputs.
    contents(PLAYLIST_PATH,"invalid\nNoTabs\n");assert(build_playlist_index_locked()==ESP_OK && !s_playlist_count);
    contents(PLAYLIST_PATH,"Last\thttp://last.example/live\t64");assert(build_playlist_index_locked()==ESP_OK && s_playlist_count==1);
    // Corrupt raw index size is rejected without publishing a new count.
    contents(PLAYLIST_INDEX_PATH,"x");assert(load_playlist_index_locked()==ESP_ERR_INVALID_SIZE);
    assert(s_playlist_count==1);
    remove(PLAYLIST_PATH);remove(PLAYLIST_INDEX_PATH);remove(PLAYLIST_INDEX_TEMP_PATH);remove(PLAYLIST_INDEX_BACKUP_PATH);
    assert(!chdir("/"));assert(!rmdir(directory));
    puts("PASS playlist index: exact offsets/lookup; rename/write failure retains old index/count; missing CSV; overlong row fragments; final line/empty/corrupt index; ASan/UBSan");
    return 0;
}
