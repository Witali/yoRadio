#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
typedef int esp_err_t;
typedef ptrdiff_t ssize_t;
typedef struct {const char *uri;} httpd_req_t;
#define ESP_OK 0
#define ESP_FAIL -1
static char s_static_scratch[1024], received[8192];
static size_t file_size, sent, offset;
static unsigned opened, closed, terminal, chunks;
static int open_errno, fail_read, fail_send, fail_close, status;
static bool selected_previous, prepared, finished;
static void prepare_short_response(httpd_req_t *r){(void)r;prepared=true;}
static esp_err_t finish_short_response(httpd_req_t *r,esp_err_t result){(void)r;finished=true;return result;}
static void httpd_resp_set_type(httpd_req_t *r,const char *s){(void)r;assert(!strcmp(s,"text/plain; charset=utf-8"));}
static void httpd_resp_set_hdr(httpd_req_t *r,const char *a,const char *b){(void)r;(void)a;(void)b;}
static void httpd_resp_set_status(httpd_req_t *r,const char *s){(void)r;status=s[0]-'0';}
static bool request_path_equals(httpd_req_t *r,const char *s){size_t n=strcspn(r->uri,"?");return strlen(s)==n&&!memcmp(r->uri,s,n);}
static esp_err_t send_string(httpd_req_t *r,const char *s){(void)r;assert(strlen(s)<80);return ESP_OK;}
static int spiffs_log_read_open(bool previous,size_t *length){
    selected_previous=previous;*length=0;if(open_errno){errno=open_errno;return -1;}++opened;*length=file_size;return 7;
}
static int spiffs_log_read_close(int fd){assert(fd==7&&opened==1&&closed==0);++closed;return fail_close?-1:0;}
static ssize_t read(int fd,char *data,size_t n){
    assert(fd==7&&opened==1&&closed==0&&n<=sizeof(s_static_scratch));
    if(fail_read==1){errno=EIO;return -1;}if(fail_read==2)return 0;
    if(fail_read==3){fail_read=0;errno=EINTR;return -1;}
    if(n>173)n=173; // Exercise short reads, not just full scratch blocks.
    for(size_t i=0;i<n;++i)data[i]=(char)((offset+i)%251);
    offset+=n;return (ssize_t)n;
}
static esp_err_t httpd_resp_send_chunk(httpd_req_t *r,const char *data,size_t n){
    (void)r;if(!n){assert(closed==1);++terminal;return fail_send==2?ESP_FAIL:ESP_OK;}
    assert(closed==0&&n<=sizeof(s_static_scratch));++chunks;
    if(fail_send==1)return ESP_FAIL;assert(sent+n<=sizeof(received));memcpy(received+sent,data,n);sent+=n;return ESP_OK;
}
/* HANDLER */
static void reset(void){file_size=8192;sent=offset=0;opened=closed=terminal=chunks=0;open_errno=fail_read=fail_send=fail_close=status=0;selected_previous=prepared=finished=false;}
int main(void){
    httpd_req_t request={"/api/native/log"};
    for(unsigned previous=0;previous<2;++previous){
        reset();request.uri=previous?"/api/native/log/previous?x=1":"/api/native/log?x=1";
        assert(spiffs_log_handler(&request)==ESP_OK&&prepared&&finished&&opened==closed&&terminal==1&&sent==8192);
        assert(selected_previous==(bool)previous);
        for(size_t i=0;i<sent;++i)assert((unsigned char)received[i]==i%251);
    }
    reset();file_size=0;assert(spiffs_log_handler(&request)==ESP_OK&&closed==1&&terminal==1&&!chunks);
    for(unsigned failure=0;failure<5;++failure){
        reset();if(failure<2)fail_read=(int)failure+1;else if(failure<4)fail_send=(int)failure-1;else fail_close=1;
        assert(spiffs_log_handler(&request)==ESP_FAIL&&closed==1&&finished);
        if(fail_send!=2)assert(terminal==0);
    }
    reset();fail_read=3;assert(spiffs_log_handler(&request)==ESP_OK&&sent==8192&&closed==1);
    for(unsigned missing=0;missing<2;++missing){reset();open_errno=missing?ENOENT:EBUSY;
        assert(spiffs_log_handler(&request)==ESP_OK&&finished&&!opened&&!closed&&!terminal&&status==(missing?4:5));}
    puts("HTTP log PASS: bounded short reads, empty/missing/busy, query, read/send/close failures and fd cleanup");return 0;
}
