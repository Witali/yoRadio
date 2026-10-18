#define _GNU_SOURCE
#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
typedef int esp_err_t;
typedef struct {int socket;} httpd_req_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES 32
#define SHUT_RDWR 2
static unsigned reads,invalid_reads,terminators,shutdowns,delivered,chunk_calls;
static bool read_error,send_error,close_error;
static size_t available;
static ssize_t cookie_read(void *cookie,char *buffer,size_t size) {(void)cookie;if(available){size_t n=available<size?available:size;memset(buffer,'x',n);available-=n;return (ssize_t)n;}return read_error?-1:0;}
static size_t traced_read(void *data,size_t size,size_t count,FILE *file) {++reads;if(ferror(file)||feof(file))++invalid_reads;return fread(data,size,count,file);}
static int traced_close(FILE *file) {int result=fclose(file);return close_error?-1:result;}
static esp_err_t httpd_resp_send_chunk(httpd_req_t *request,const char *data,ssize_t size) {(void)request;if(!data){assert(!size);++terminators;return ESP_OK;}++chunk_calls;if(send_error)return ESP_FAIL;delivered+=(unsigned)size;return ESP_OK;}
static esp_err_t httpd_resp_sendstr_chunk(httpd_req_t *request,const char *text) {assert(!text);return httpd_resp_send_chunk(request,NULL,0);}
static esp_err_t finish_static_response(httpd_req_t *request,esp_err_t result) {(void)request;return result;}
static int httpd_req_to_sockfd(httpd_req_t *request) {return request->socket;}
static int shutdown(int socket,int how) {assert(socket==7&&how==SHUT_RDWR);++shutdowns;return 0;}
#define fread traced_read
#define fclose traced_close
#include "static-production.inc"
#undef fread
#undef fclose
static esp_err_t run(size_t size,bool error,bool sending_error,bool closing_error) {
    reads=invalid_reads=terminators=shutdowns=delivered=chunk_calls=0;available=size;read_error=error;send_error=sending_error;close_error=closing_error;
    cookie_io_functions_t functions={.read=cookie_read};FILE *file=fopencookie(NULL,"r",functions);assert(file);
    httpd_req_t request={.socket=7};return send_static_file(&request,file);
}
int main(void) {
    assert(run(3,true,false,false)==ESP_FAIL&&!invalid_reads&&!terminators&&shutdowns==1&&delivered==3);
    assert(run(3,false,false,false)==ESP_OK&&!invalid_reads&&terminators==1&&!shutdowns&&delivered==3);
    assert(run(67,false,false,false)==ESP_OK&&!invalid_reads&&terminators==1&&delivered==67);
    assert(run(64,false,false,false)==ESP_OK&&!invalid_reads&&terminators==1&&delivered==64);
    assert(run(3,false,true,false)==ESP_FAIL&&!terminators&&shutdowns==1);
    assert(run(0,true,false,false)==ESP_FAIL&&!terminators&&shutdowns==1);
    assert(run(3,false,false,true)==ESP_FAIL&&!terminators&&shutdowns==1);
#ifndef BASELINE
    ssize_t size;
    assert(embedded_script_size((const uint8_t *)(uintptr_t)100,(const uint8_t *)(uintptr_t)132,&size)&&size==32);
    assert(!embedded_script_size((const uint8_t *)(uintptr_t)132,(const uint8_t *)(uintptr_t)100,&size));
    assert(!embedded_script_size((const uint8_t *)(uintptr_t)1,(const uint8_t *)(uintptr_t)(1ULL+INT_MAX+1ULL),&size));
#endif
    puts("PASS C3 static reads: EOF/error stop, no false chunk terminator, socket shutdown, checked embedded span");
    return 0;
}
