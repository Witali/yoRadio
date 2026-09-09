#include <assert.h>
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "spiffs_log.h"
typedef uint32_t TickType_t;
typedef void *TaskHandle_t;
typedef ptrdiff_t ssize_t;
typedef int (*putchar_like_t)(int);
#define ESP_OK 0
#define O_WRONLY 1
#define O_RDONLY 0
#define O_CREAT 2
#define O_APPEND 4
#define pdMS_TO_TICKS(ms) (ms)
static unsigned critical, tick, fs_calls, opens, closes, hooks;
static TaskHandle_t current_task = (void *)1;
#define taskENTER_CRITICAL() (++critical)
#define taskEXIT_CRITICAL() do { assert(critical); --critical; } while (0)
static TickType_t xTaskGetTickCount(void) {return tick;}
static TaskHandle_t xTaskGetCurrentTaskHandle(void) {return current_task;}
static char current_file[9000], previous_file[9000], uart[50000];
static size_t current_size, previous_size, uart_size, disk_used;
static bool current_exists, previous_exists, live_fd;
static bool fail_info, fail_open, fail_write, fail_close, fail_stat, fail_rename, fail_unlink;
static bool recursive_write, concurrent_write;
static size_t short_write;
static putchar_like_t hook;
static int test_uart(int ch) {assert(!critical); if(uart_size<sizeof(uart))uart[uart_size++]=(char)ch;return ch;}
static putchar_like_t esp_log_set_putchar(putchar_like_t next) {
    ++hooks; putchar_like_t old=hook?hook:test_uart;hook=next;return old;
}
static void emit(const char *s) {while(*s)assert(hook(*s++)>=0);}
static void filesystem(void) {assert(!critical);++fs_calls;}
static int esp_spiffs_info(const char *label,size_t *total,size_t *used) {
    filesystem();assert(!strcmp(label,"spiffs"));*total=262144;*used=disk_used;return fail_info?-1:0;
}
struct test_stat {int st_size;};
static int test_stat(const char *path,struct test_stat *st) {
    filesystem();assert(!strcmp(path,SPIFFS_LOG_PATH));
    if(fail_stat){errno=EIO;return -1;}if(!current_exists){errno=ENOENT;return -1;}
    st->st_size=(int)current_size;return 0;
}
static int test_unlink(const char *path) {
    filesystem();assert(!strcmp(path,SPIFFS_LOG_PREVIOUS_PATH));
    if(fail_unlink){errno=EIO;return -1;}if(!previous_exists){errno=ENOENT;return -1;}
    previous_exists=false;previous_size=0;return 0;
}
static int test_rename(const char *from,const char *to) {
    filesystem();assert(!strcmp(from,SPIFFS_LOG_PATH)&&!strcmp(to,SPIFFS_LOG_PREVIOUS_PATH));
    if(fail_rename){errno=EIO;return -1;}assert(current_exists&&!previous_exists);
    memcpy(previous_file,current_file,current_size);previous_size=current_size;previous_exists=true;
    current_size=0;current_exists=false;return 0;
}
static int test_open(const char *path,int flags,int mode) {
    filesystem();
#if YORADIO_ESP8266_SPIFFS_LOG_HTTP
    if(flags==O_RDONLY) {
        bool previous=!strcmp(path,SPIFFS_LOG_PREVIOUS_PATH);
        assert(previous||!strcmp(path,SPIFFS_LOG_PATH));
        if(fail_open){errno=EMFILE;return -1;}
        if(previous?!previous_exists:!current_exists){errno=ENOENT;return -1;}
        assert(!live_fd);live_fd=true;++opens;return previous?8:7;
    }
#endif
    assert(!strcmp(path,SPIFFS_LOG_PATH));assert(flags==(O_WRONLY|O_CREAT|O_APPEND)&&mode==0600);
    if(fail_open){errno=EMFILE;return -1;}assert(!live_fd);live_fd=true;++opens;current_exists=true;return 7;
}
static ssize_t test_write(int fd,const void *data,size_t n) {
    filesystem();assert(fd==7&&live_fd&&n<=256);
    if(fail_write){errno=EIO;return -1;}
    if(short_write&&n>short_write)n=short_write;
    assert(current_size+n<=SPIFFS_LOG_FILE_BYTES);
    if(recursive_write)emit("recursive FS error\n");
    if(concurrent_write){current_task=(void *)2;emit("parallel log\n");current_task=(void *)1;}
    memcpy(current_file+current_size,data,n);current_size+=n;return (ssize_t)n;
}
static int test_close(int fd) {
    filesystem();assert((fd==7||fd==8)&&live_fd);live_fd=false;++closes;
    if(fail_close){errno=EIO;return -1;}return 0;
}
#define stat test_stat
#define unlink test_unlink
#define rename test_rename
#define open test_open
#define write test_write
#define close test_close
#if YORADIO_ESP8266_SPIFFS_LOG_HTTP
static int test_fstat(int fd,struct test_stat *st) {
    filesystem();assert(live_fd&&(fd==7||fd==8));
    if(fail_stat){errno=EIO;return -1;}
    st->st_size=(int)(fd==7?current_size:previous_size);return 0;
}
#define fstat test_fstat
#endif
/* LOGGER_IMPLEMENTATION */
#undef stat
#undef unlink
#undef rename
#undef open
#undef write
#undef close
static void advance(unsigned ms){tick+=ms;spiffs_log_poll();assert(!critical);}
static void reset(void) {
    memset(s_queue,0,sizeof(s_queue));s_head=s_count=0;
    s_dropped=s_reported_dropped=s_io_errors=0;s_installed=s_mounted=s_low_space=s_storage_fault=false;
    s_io_owner=NULL;s_last_poll=0;s_interval_ms=1000;s_previous=test_uart;
    current_size=previous_size=uart_size=disk_used=0;current_exists=previous_exists=live_fd=false;
    fs_calls=opens=closes=hooks=tick=critical=0;hook=NULL;
    fail_info=fail_open=fail_write=fail_close=fail_stat=fail_rename=fail_unlink=false;
    recursive_write=concurrent_write=false;short_write=0;current_task=(void *)1;
    spiffs_log_init();
}
static void ready_empty(void){reset();spiffs_log_mount_ready();advance(1000);s_head=s_count=0;current_size=0;}
int main(void) {
    reset();spiffs_log_init();assert(hooks==1);
    emit("before mount\n");assert(!fs_calls);advance(3000);assert(!fs_calls);
    spiffs_log_mount_ready();advance(1000);assert(opens==closes&&!live_fd);
    current_file[current_size]=0;assert(strstr(current_file,"application start")&&strstr(current_file,"before mount"));

    ready_empty();unsigned before=fs_calls;emit("hello\n");assert(fs_calls==before&&s_count==6);
    advance(999);assert(fs_calls==before);advance(1);assert(current_size==6&&!memcmp(current_file,"hello\n",6));
    assert(opens==closes);spiffs_log_status_t status;spiffs_log_get_status(&status);assert(!status.pending_bytes);

    ready_empty();for(unsigned i=0;i<700;++i)hook('a');assert(s_count==512&&s_dropped==188);
    advance(1000);advance(1000);advance(1000);advance(1000);
    current_file[current_size]=0;assert(strstr(current_file,"dropped 188 bytes total"));assert(!s_count);

    ready_empty();current_exists=true;current_size=8190;memset(current_file,'x',current_size);
    emit("rotate\n");advance(1000);assert(previous_size==8190&&current_size==7&&opens==closes);
    for(unsigned i=0;i<100;++i){for(unsigned j=0;j<200;++j)hook('z');advance(1000);}
    assert(current_size<=8192&&previous_size<=8192&&opens==closes);

    ready_empty();disk_used=250000;emit("keep\n");before=opens;advance(1000);
    assert(opens==before&&s_count==5&&s_low_space);disk_used=1000;advance(29999);assert(opens==before);
    advance(1);assert(opens==before+1&&s_count==0&&!s_low_space);

    bool *failures[]={&fail_info,&fail_open,&fail_write,&fail_stat,&fail_rename,&fail_unlink};
    for(unsigned i=0;i<sizeof(failures)/sizeof(failures[0]);++i){
        ready_empty();if(i>=4){current_size=8192;previous_exists=true;}
        emit("retry\n");*failures[i]=true;advance(1000);
        assert(s_count==6&&s_io_errors==1&&opens==closes&&!live_fd);
        *failures[i]=false;advance(30000);assert(s_count==0&&opens==closes);
    }
    ready_empty();emit("abcdef");short_write=2;advance(1000);assert(s_count==4&&current_size==2);
    short_write=0;advance(30000);assert(!s_count&&current_size==6&&!memcmp(current_file,"abcdef",6));

    ready_empty();emit("normal\n");recursive_write=true;advance(1000);
    assert(s_dropped==19&&s_count==0&&opens==closes);recursive_write=false;advance(1000);
    assert(s_reported_dropped==19); /* no self-replicating filesystem log */

    ready_empty();emit("first\n");concurrent_write=true;advance(1000);assert(s_count==13);
    concurrent_write=false;advance(1000);assert(!s_count);
    current_file[current_size]=0;assert(!strcmp(current_file,"first\nparallel log\n"));

    ready_empty();emit("fault\n");fail_close=true;advance(1000);assert(s_storage_fault&&opens==closes);
    before=opens;fail_close=false;emit("after fault\n");advance(60000);assert(opens==before);

    ready_empty();s_last_poll=UINT32_MAX-500;tick=499;emit("wrap\n");spiffs_log_poll();assert(!s_count);
#if YORADIO_ESP8266_SPIFFS_LOG_HTTP
    size_t length=99;
    reset();assert(spiffs_log_read_open(false,&length)<0&&errno==EBUSY&&length==0&&!s_io_owner);
    ready_empty();previous_exists=false;
    assert(spiffs_log_read_open(true,&length)<0&&errno==ENOENT&&!s_io_owner);
    current_size=9000;int fd=spiffs_log_read_open(false,&length);
    assert(fd==7&&length==8192&&s_io_owner==current_task);
    assert(spiffs_log_read_open(true,&length)<0&&errno==EBUSY&&s_io_owner==current_task);
    current_task=(void *)2;emit("while reading\n");before=fs_calls;advance(1000);
    assert(fs_calls==before&&s_count==14); // Writer must not rotate an open download.
    current_task=(void *)1;assert(spiffs_log_read_close(fd)==0&&!s_io_owner&&opens==closes);
    current_size=0;advance(1000);assert(s_count==0);
    previous_exists=true;previous_size=321;
    fd=spiffs_log_read_open(true,&length);assert(fd==8&&length==321);
    assert(spiffs_log_read_close(fd)==0&&opens==closes);
    for(unsigned i=0;i<2;++i) {
        ready_empty();if(i)fail_stat=true;else fail_open=true;
        assert(spiffs_log_read_open(false,&length)<0&&!s_io_owner&&opens==closes&&!live_fd);
    }
    ready_empty();fd=spiffs_log_read_open(false,&length);fail_close=true;
    assert(spiffs_log_read_close(fd)<0&&s_storage_fault&&!s_io_owner&&opens==closes);
    before=opens;assert(spiffs_log_read_open(false,&length)<0&&errno==EBUSY&&opens==before);
#endif
    puts("SPIFFS log PASS: deferred/bounded/rotation/low-space/I-O failures/recursion/concurrency/tick-wrap");
    return 0;
}
