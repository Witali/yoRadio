#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned getc_calls;
static int traced_getc(FILE *file) {++getc_calls;return fgetc(file);}
#define fgetc traced_getc
#include "credential_line.h"
#undef fgetc

typedef struct {struct {uint8_t ssid[32],password[64];}sta;} wifi_config_t;
static const char *fixture;
static const uint8_t *cookie_data;
static size_t cookie_size,cookie_position,cookie_fragment,cookie_error_at;
static bool use_cookie,missing;
static unsigned cases;
static unsigned cookie_read_calls;
static ssize_t cookie_read(void *context,char *buffer,size_t capacity) {
    (void)context;
    ++cookie_read_calls;
    if(cookie_position>=cookie_error_at){errno=EIO;return -1;}
    size_t count=cookie_size-cookie_position;
    if(count>capacity)count=capacity;
    if(count>cookie_fragment)count=cookie_fragment;
    if(count>cookie_error_at-cookie_position)count=cookie_error_at-cookie_position;
    memcpy(buffer,cookie_data+cookie_position,count);cookie_position+=count;return (ssize_t)count;
}
static FILE *mapped_open(const char *path,const char *mode) {
    assert(!strcmp(path,"/spiffs/data/wifi.csv")&&!strcmp(mode,"r"));
    if(missing){errno=ENOENT;return NULL;}
    if(!use_cookie)return fopen(fixture,"rb");
    cookie_position=0;cookie_io_functions_t functions={.read=cookie_read};return fopencookie(NULL,"r",functions);
}
static size_t strlcpy(char *target,const char *source,size_t capacity){size_t length=strlen(source);if(capacity){size_t count=length<capacity-1?length:capacity-1;memcpy(target,source,count);target[count]=0;}return length;}
#define web_upload_open_file(path) mapped_open(path,"r")
#define fopen(...) mapped_open(__VA_ARGS__)
#include "cyd-wifi-production.inc"
#undef fopen
#undef web_upload_open_file

static void put(const void *data,size_t size) {
    FILE *file=fopen(fixture,"wb");assert(file);assert(fwrite(data,1,size,file)==size);assert(!fclose(file));
    use_cookie=missing=false;cookie_error_at=SIZE_MAX;cookie_fragment=SIZE_MAX;++cases;
}
static bool expect(bool accepted,const char *ssid,const char *password) {
    struct {uint64_t before;wifi_config_t config;uint64_t after;} guarded={.before=UINT64_C(0x123456789abcdef0),.after=UINT64_C(0xfedcba9876543210)};
    memset(&guarded.config,0xa5,sizeof(guarded.config));wifi_config_t initial=guarded.config;
    bool result=read_credentials(&guarded.config);assert(result==accepted);
    assert(guarded.before==UINT64_C(0x123456789abcdef0)&&guarded.after==UINT64_C(0xfedcba9876543210));
    if(result){assert(!strcmp((char *)guarded.config.sta.ssid,ssid)&&!strcmp((char *)guarded.config.sta.password,password));}
    else assert(!memcmp(&guarded.config,&initial,sizeof(initial)));
    return result;
}
static void text(const char *data){put(data,strlen(data));}

int main(int argc,char **argv) {
    assert(argc==2);fixture=argv[1];
    char oversized[512];memset(oversized,'x',159);strcpy(oversized+159,"phantom\tfixture\nallowed\tfixture\n");
    text(oversized);expect(true,"allowed","fixture");
    const size_t fragments[]={1,2,3,7,31,159,512};
    for(size_t i=0;i<sizeof(fragments)/sizeof(fragments[0]);++i){
        ++cases;use_cookie=true;cookie_data=(const uint8_t *)oversized;cookie_size=strlen(oversized);cookie_fragment=fragments[i];cookie_error_at=SIZE_MAX;
        expect(true,"allowed","fixture");
    }
    char ssid31[32],ssid32[33],pass63[64],pass64[65],row[256];
    memset(ssid31,'s',31);ssid31[31]=0;memset(ssid32,'s',32);ssid32[32]=0;
    memset(pass63,'p',63);pass63[63]=0;memset(pass64,'p',64);pass64[64]=0;
    snprintf(row,sizeof(row),"%s\t%s\n",ssid31,pass63);text(row);expect(true,ssid31,pass63);
    snprintf(row,sizeof(row),"%s\tfixture\nallowed\tfixture\n",ssid32);text(row);expect(true,"allowed","fixture");
    snprintf(row,sizeof(row),"invalid\t%s\nallowed\tfixture\n",pass64);text(row);expect(true,"allowed","fixture");
    const char embedded[]="invalid\tfixture\0ignored\nallowed\tfixture\n";
    put(embedded,sizeof(embedded)-1);expect(true,"allowed","fixture");
    text("bad\rssid\tfixture\nallowed\tfixture\n");expect(true,"allowed","fixture");
    text("invalid\tfix\rture\nallowed\tfixture\n");expect(true,"allowed","fixture");
    text("invalid\tfixture\textra\nallowed\tfixture\n");expect(true,"allowed","fixture");
    text(" allowed \t pass \r\nsecond\tsecond\n");expect(true," allowed "," pass ");
    text("\r\n\n\tignored\nallowed\t\r\n");expect(true,"allowed","");
    text("allowed\tfixture");expect(true,"allowed","fixture");
    text("");expect(false,NULL,NULL);
    text("no separator\n\tfixture\n");expect(false,NULL,NULL);
    text("allowed\tfixture\n");missing=true;expect(false,NULL,NULL);
    text("allowed\tfixture");use_cookie=true;cookie_data=(const uint8_t *)"allowed\tfixture";cookie_size=strlen((const char *)cookie_data);cookie_fragment=2;cookie_error_at=5;
    expect(false,NULL,NULL);
    ++cases;cookie_error_at=0;expect(false,NULL,NULL);
    ++cases;cookie_error_at=cookie_size;expect(false,NULL,NULL); // Error replaces EOF after a partial final row.
    text("allowed\tfixture\nsecond\tfixture\n");use_cookie=true;cookie_data=(const uint8_t *)"allowed\tfixture\nsecond\tfixture\n";cookie_size=strlen((const char *)cookie_data);
    cookie_fragment=1;cookie_error_at=strlen("allowed\tfixture\n");expect(true,"allowed","fixture"); // Preserve first-valid CYD policy.
    FILE *file=tmpfile();assert(file);fputs("invalid suffix to discard\nvalid\n",file);rewind(file);
    struct {char line[8];uint64_t canary;} bounded={.canary=UINT64_C(0x123456789abcdef0)};
    assert(native_credential_next_row(file,bounded.line,sizeof(bounded.line))&&!strcmp(bounded.line,"valid"));
    assert(bounded.canary==UINT64_C(0x123456789abcdef0));
    assert(!native_credential_next_row(file,bounded.line,sizeof(bounded.line)));
    assert(!native_credential_next_row(NULL,bounded.line,sizeof(bounded.line)));
    assert(!native_credential_next_row(file,NULL,sizeof(bounded.line)));
    assert(!native_credential_next_row(file,bounded.line,0));fclose(file);++cases;
    use_cookie=true;cookie_data=(const uint8_t *)"last\tfixture";cookie_size=strlen((const char *)cookie_data);cookie_fragment=2;cookie_error_at=SIZE_MAX;
    file=mapped_open("/spiffs/data/wifi.csv","r");assert(file);char final_line[32];
    assert(native_credential_next_row(file,final_line,sizeof(final_line))&&feof(file));
    unsigned before_getc=getc_calls,before_cookie=cookie_read_calls;
    for(unsigned repeat=0;repeat<3;++repeat)assert(!native_credential_next_row(file,final_line,sizeof(final_line)));
    assert(getc_calls==before_getc&&cookie_read_calls==before_cookie);fclose(file);++cases;
    cookie_error_at=3;file=mapped_open("/spiffs/data/wifi.csv","r");assert(file);
    assert(!native_credential_next_row(file,final_line,sizeof(final_line))&&ferror(file));
    before_getc=getc_calls;before_cookie=cookie_read_calls;
    for(unsigned repeat=0;repeat<3;++repeat)assert(!native_credential_next_row(file,final_line,sizeof(final_line)));
    assert(getc_calls==before_getc&&cookie_read_calls==before_cookie);fclose(file);++cases;
    printf("PASS CYD credentials: %u fixtures, physical rows/read splits, 32/64 bounds, NUL/CR/tabs, first-valid/whitespace, EOF/read errors; no credentials logged\n",cases);
    return 0;
}
