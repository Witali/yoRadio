/* Execute the production media/settings/HTTP code with in-memory platform I/O.
 * These tests do not validate ESP-IDF timing, Wi-Fi, TLS or physical display. */
#include <assert.h>
#include <math.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "settings.h"
#include "display.h"
#include "media.h"
#include "network.h"
#include "services.h"
#include "web.h"
#include "dns_packet.h"
#include "factory_settings.h"
#include "esp_flash.h"
#include "esp_partition.h"
#include "nvs.h"
#include "freertos/semphr.h"

static unsigned checks;
#define CHECK(condition) do {++checks;if (!(condition)) {fprintf(stderr,"Check failed at %s:%d: %s\n",__FILE__,__LINE__,#condition);exit(1);}} while (0)
static uint8_t flash_bytes[0x1e7000],saved_nvs[1024];
static uint8_t factory_sector[4096];
static size_t saved_nvs_length;
static int64_t clock_us;
static unsigned rendered_pixels,registered_routes,restart_requests,weather_requests;
static unsigned route_success[48],route_errors[48];
static bool connected;
static uint16_t scan_count=1;
static esp_err_t scan_result=ESP_OK,write_result=ESP_OK;
static esp_err_t (*not_found)(httpd_req_t *,httpd_err_code_t);
static const esp_partition_t partition={ASSETS_BASE,sizeof(flash_bytes)};
static const httpd_uri_t *route_table[48];
extern const unsigned char web_setup[],web_settings[],web_photo[];
extern const size_t web_setup_length,web_settings_length,web_photo_length;

int64_t esp_timer_get_time(void) {return clock_us;}
SemaphoreHandle_t xSemaphoreCreateMutex(void) {return (void *)1;}
int xSemaphoreTake(SemaphoreHandle_t m,unsigned ticks) {(void)m;(void)ticks;return 1;}
int xSemaphoreGive(SemaphoreHandle_t m) {(void)m;return 1;}
int xTaskCreate(void (*task)(void *),const char *name,unsigned stack,void *argument,unsigned priority,void *handle)
{(void)task;(void)name;(void)stack;(void)argument;(void)priority;(void)handle;return 1;}
void vTaskDelay(unsigned ticks) {clock_us+=(int64_t)ticks*1000;}
esp_err_t nvs_open(const char *name,int mode,nvs_handle_t *handle) {(void)name;(void)mode;*handle=1;return ESP_OK;}
esp_err_t nvs_get_blob(nvs_handle_t handle,const char *key,void *data,size_t *length)
{(void)handle;(void)key;if (!saved_nvs_length) return ESP_ERR_NOT_FOUND;if (*length<saved_nvs_length)return ESP_ERR_INVALID_SIZE;memcpy(data,saved_nvs,saved_nvs_length);*length=saved_nvs_length;return ESP_OK;}
esp_err_t nvs_set_blob(nvs_handle_t handle,const char *key,const void *data,size_t length)
{(void)handle;(void)key;assert(length<=sizeof(saved_nvs));memcpy(saved_nvs,data,length);saved_nvs_length=length;return ESP_OK;}
esp_err_t nvs_commit(nvs_handle_t handle) {(void)handle;return ESP_OK;}
esp_err_t esp_flash_read(esp_flash_t *chip,void *data,uint32_t offset,uint32_t length)
{(void)chip;if(offset!=FACTORY_SETTINGS_OFFSET || length>sizeof(factory_sector))return ESP_ERR_INVALID_SIZE;memcpy(data,factory_sector,length);return ESP_OK;}
esp_err_t esp_flash_write(esp_flash_t *chip,const void *data,uint32_t offset,uint32_t length)
{(void)chip;if(write_result!=ESP_OK)return write_result;if(offset!=FACTORY_SETTINGS_OFFSET || length>sizeof(factory_sector))return ESP_ERR_INVALID_SIZE;memcpy(factory_sector,data,length);return ESP_OK;}
esp_err_t esp_flash_erase_region(esp_flash_t *chip,uint32_t offset,uint32_t length)
{(void)chip;assert(offset==FACTORY_SETTINGS_OFFSET && length==4096);memset(factory_sector,255,sizeof(factory_sector));return ESP_OK;}
const esp_partition_t *esp_partition_find_first(unsigned type,unsigned subtype,const char *label)
{(void)type;assert(subtype==0x40 && !strcmp(label,"assets"));return &partition;}
esp_err_t esp_partition_read(const esp_partition_t *p,size_t offset,void *data,size_t length)
{if (offset>p->size || length>p->size-offset) return ESP_ERR_INVALID_SIZE;memcpy(data,flash_bytes+offset,length);return ESP_OK;}
esp_err_t esp_partition_write(const esp_partition_t *p,size_t offset,const void *data,size_t length)
{if (offset>p->size || length>p->size-offset)return ESP_ERR_INVALID_SIZE;const uint8_t *bytes=data;for(size_t i=0;i<length;++i){assert((flash_bytes[offset+i]&bytes[i])==bytes[i]);flash_bytes[offset+i]&=bytes[i];}return ESP_OK;}
esp_err_t esp_partition_erase_range(const esp_partition_t *p,size_t offset,size_t length)
{if(offset>p->size || length>p->size-offset || offset%4096 || length%4096)return ESP_ERR_INVALID_SIZE;memset(flash_bytes+offset,255,length);return ESP_OK;}
void display_blit(int x,int y,int width,int height,const uint16_t *pixels)
{assert(x>=0 && y>=0 && width>0 && height>0 && x+width<=240 && y+height<=240 && pixels);rendered_pixels+=width*height;}
void display_fill(int x,int y,int width,int height,uint16_t color)
{
    /* Accept bounded JPEG error cleanup; the RV32 oracle checks actual pixels. */
    assert(x>=0 && y>=0 && width>0 && height>0 && x+width<=240 && y+height<=240 && color==0);
}
bool network_connected(void) {return connected;}
bool network_ap_active(void) {return true;}
void network_restart_later(void) {++restart_requests;}
void weather_request_update(void) {++weather_requests;}
esp_err_t network_scan(wifi_ap_record_t *records,uint16_t *count)
{if(scan_result!=ESP_OK)return scan_result;assert(*count>=scan_count);if(scan_count){strcpy((char *)records[0].ssid,"native test");records[0].rssi=-42;}*count=scan_count;return ESP_OK;}

esp_err_t httpd_resp_set_status(httpd_req_t *req,const char *status) {req->status=strtoul(status,NULL,10);return ESP_OK;}
esp_err_t httpd_resp_set_type(httpd_req_t *req,const char *type) {strcpy(req->response_type,type);return ESP_OK;}
esp_err_t httpd_resp_set_hdr(httpd_req_t *req,const char *name,const char *value)
{if(!strcmp(name,"Location"))strcpy(req->location,value);if(!strcmp(name,"Cache-Control"))strcpy(req->cache_control,value);return ESP_OK;}
esp_err_t httpd_resp_send(httpd_req_t *req,const char *data,int length)
{if(length<0)length=(int)strlen(data);assert((size_t)length<sizeof(req->response));memcpy(req->response,data,length);req->response[length]=0;req->response_length=length;return ESP_OK;}
esp_err_t httpd_resp_send_err(httpd_req_t *req,httpd_err_code_t code,const char *message) {req->status=code;return httpd_resp_send(req,message,-1);}
static const char *header(httpd_req_t *req,const char *name)
{if(!strcmp(name,"Content-Type"))return req->content_type;if(!strcmp(name,"Origin"))return req->origin;if(!strcmp(name,"Host"))return req->host;return NULL;}
size_t httpd_req_get_hdr_value_len(httpd_req_t *req,const char *name) {const char *value=header(req,name);return value?strlen(value):0;}
esp_err_t httpd_req_get_hdr_value_str(httpd_req_t *req,const char *name,char *out,size_t capacity)
{const char *value=header(req,name);if(!value || strlen(value)>=capacity)return ESP_ERR_INVALID_SIZE;strcpy(out,value);return ESP_OK;}
int httpd_req_recv(httpd_req_t *req,char *out,size_t length)
{if(req->recv_timeouts){--req->recv_timeouts;return HTTPD_SOCK_ERR_TIMEOUT;}if(req->recv_disconnect)return 0;if(length>req->content_len-req->position)length=req->content_len-req->position;if(length>137)length=137;memcpy(out,req->input+req->position,length);req->position+=length;return (int)length;}
esp_err_t httpd_req_get_url_query_str(httpd_req_t *req,char *out,size_t capacity)
{const char *query=strchr(req->uri,'?');if(!query || strlen(query+1)>=capacity)return ESP_ERR_INVALID_SIZE;strcpy(out,query+1);return ESP_OK;}
esp_err_t httpd_query_key_value(const char *query,const char *key,char *out,size_t capacity)
{size_t n=strlen(key);for(const char *p=query;*p;){if(!strncmp(p,key,n) && p[n]=='='){p+=n+1;size_t length=strcspn(p,"&");if(length>=capacity)return ESP_ERR_INVALID_SIZE;memcpy(out,p,length);out[length]=0;return ESP_OK;}p=strchr(p,'&');if(!p)break;++p;}return ESP_ERR_NOT_FOUND;}
esp_err_t httpd_start(httpd_handle_t *server,const httpd_config_t *config) {(void)config;*server=(void *)1;return ESP_OK;}
esp_err_t httpd_stop(httpd_handle_t server) {(void)server;return ESP_OK;}
esp_err_t httpd_register_uri_handler(httpd_handle_t server,const httpd_uri_t *uri)
{(void)server;assert(registered_routes<48);route_table[registered_routes++]=uri;return ESP_OK;}
esp_err_t httpd_register_err_handler(httpd_handle_t server,httpd_err_code_t code,esp_err_t (*handler)(httpd_req_t *,httpd_err_code_t))
{(void)server;assert(code==HTTPD_404_NOT_FOUND);not_found=handler;return ESP_OK;}

static httpd_req_t request;
static void prepare(const char *uri,const void *body,size_t length,const char *type)
{memset(&request,0,sizeof(request));request.uri=uri;request.input=body;request.content_len=length;request.content_type=type;request.host="192.168.43.1";request.status=200;}
static void dispatch(httpd_method_t method)
{
    /* Exercise the registered method/URI handler, retaining successful/error coverage. */
    size_t length=strcspn(request.uri,"?");
    for(unsigned i=0;i<registered_routes;++i)
        if(route_table[i]->method==method && strlen(route_table[i]->uri)==length && !memcmp(route_table[i]->uri,request.uri,length))
        {
            route_table[i]->handler(&request);
            if(request.status==200)++route_success[i];else ++route_errors[i];
            return;
        }
    CHECK(not_found!=NULL);not_found(&request,HTTPD_404_NOT_FOUND);
}
static const char *post(const char *uri,const char *json,unsigned expected)
{prepare(uri,json,strlen(json),"application/json");dispatch(HTTP_POST);CHECK(request.status==expected);return request.response;}
static const char *get(const char *uri)
{prepare(uri,"",0,NULL);dispatch(HTTP_GET);CHECK(request.status==200);return request.response;}

static void test_settings(void)
{
    CHECK(settings_init()==ESP_OK);tv_settings_t s;settings_snapshot(&s);CHECK(settings_valid(&s));
    CHECK(!strcmp(get("/getclocktype"),"0"));
    post("/setclocktype","{\"clocktype\":\"3\"}",200);CHECK(!strcmp(get("/getclocktype"),"3"));
    post("/setclocktype","{\"clocktype\":4}",400);CHECK(!strcmp(get("/getclocktype"),"3"));
    post("/setclocktype","{\"clocktype\":2.1}",400);
    post("/setclocktype","{\"clocktype\":\"99999999999999999999999999\"}",400);
    post("/set_clock_color","{\"index\":0,\"color\":\"#123456\"}",200);CHECK(strstr(get("/get_clock_colors"),"#103452")!=NULL);
    post("/set_clock_color","{\"index\":3,\"color\":\"#ffffff\"}",400);
    post("/set_led_brightness","ledBrightness=73",200);CHECK(strstr(get("/get_led_brightness"),"73")!=NULL);
    post("/set_night_brightness","NightBrightness=19",200);CHECK(strstr(get("/get_night_brightness"),"19")!=NULL);
    post("/set_led_brightness","ledBrightness=101",400);
    post("/settings","{\"tempUnit\":1,\"hourFormat\":1,\"mileDisplay\":1,\"timeSync\":0,\"nightmode\":1}",200);
    post("/settings","{\"tempUnit\":0,\"hourFormat\":2}",400);settings_snapshot(&s);CHECK(s.fahrenheit==1);
    post("/set_checkbox_state","{\"checkbox_id\":\"file2-switch\",\"checked\":false}",200);CHECK(strstr(get("/get_checkbox_state"),"\"file2_switch\":false")!=NULL);
    post("/updateCity","{\"city\":\"London,gb\"}",200);settings_snapshot(&s);CHECK(!strcmp(s.city,"London") && !strcmp(s.country,"GB"));
    post("/updateCity","{\"city\":\"London\"}",400);
    post("/advancedset","{\"ntp\":\"pool.ntp.org\",\"openweathermapKey\":\"\",\"clickCount\":0}",200);CHECK(weather_requests==2);
    post("/set_display_time","{\"display_time\":60}",200);post("/set_display_time","{\"display_time\":61}",400);
    post("/SetNightStartTime","{\"StartTime\":18}",200);post("/SetNightStopTime","{\"StopTime\":12}",200);
    prepare("/settings","{\"hourFormat\":0}",16,"application/json");request.origin="http://evil.example";web_settings_post(&request);CHECK(request.status==400);
    post("/configure","{\"ssid\":\"Home\",\"password\":\"12345678\"}",200);CHECK(restart_requests==1);
    CHECK(settings_flush()==ESP_OK);CHECK(settings_init()==ESP_OK);settings_snapshot(&s);CHECK(!strcmp(s.ssid,"Home") && s.wifi_mode==1);
    CHECK(rgb888_from_rgb565(rgb565_from_rgb888(0xffffff))==0xffffff);
    CHECK(rgb888_from_rgb565(rgb565_from_rgb888(0xff0000))==0xff0000);
}

static uint32_t le32(const uint8_t *data) {return data[0]|((uint32_t)data[1]<<8)|((uint32_t)data[2]<<16)|((uint32_t)data[3]<<24);}
static void test_factory_settings(void)
{
    /* Exercise an independent original-sector fixture, including mode 2 with
     * an existing SSID: it must stay in setup after a failed station attempt. */
    CHECK(sizeof(tv_settings_t)==344);
    CHECK(offsetof(tv_settings_t,wifi_mode)==323);
    CHECK(offsetof(tv_settings_t,photo_size)==324);
    tv_settings_t s; settings_snapshot(&s);
    uint8_t raw[FACTORY_SETTINGS_BYTES]; memset(raw,255,sizeof(raw));
    CHECK(!factory_settings_decode(raw,&s));
    memcpy(raw+4,"synthetic-ap\0",13);
    memcpy(raw+0x45,"\0",1);
    memcpy(raw+0x86,"10.0.2.2\0",9);
    memcpy(raw+0xc7,"GB\0",3);
    memcpy(raw+0xdb,"London\0",7);
    memcpy(raw+0x11c,"fixture-key\0",12);
    raw[0x160]=2; raw[0x161]=raw[0x162]=raw[0x163]=0;
    raw[0x168]=1; raw[0x169]=raw[0x16a]=raw[0x16b]=0;
    raw[0x1a4]=5; raw[0x1a5]=raw[0x1a6]=raw[0x1a7]=0;
    memcpy(factory_sector,raw,sizeof(raw));
    CHECK(settings_init()==ESP_OK); settings_snapshot(&s);
    CHECK(!strcmp(s.ssid,"synthetic-ap") && !s.password[0] && s.wifi_mode==2);
    CHECK(!strcmp(s.ntp,"10.0.2.2") && !strcmp(s.country,"GB") && !strcmp(s.city,"London"));
    CHECK(!strcmp(s.weather_key,"fixture-key") && s.theme==1 && s.photo_mask==5);
    CHECK(s.colors[0]==0xf800 && s.photo_seconds==5); /* erased fields use defaults */
    s.theme=3; CHECK(settings_replace(&s)==ESP_OK); CHECK(settings_flush()==ESP_OK);
    CHECK(le32(factory_sector+0x160)==2 && le32(factory_sector+0x168)==3);
    CHECK(le32(factory_sector)==5 && le32(factory_sector+0x1a4)==5);
    CHECK(le32(factory_sector+0x1a8)==s.photo_size[0]);
    CHECK(!strcmp((char *)factory_sector+0xdb,"London"));
    CHECK(factory_sector[FACTORY_SETTINGS_BYTES]==255);
    /* Legacy NVS uses the same blob size but had no explicit mode byte. */
    memset(factory_sector,255,sizeof(factory_sector));
    saved_nvs[323]=0;
    CHECK(settings_init()==ESP_OK); settings_snapshot(&s); CHECK(s.wifi_mode==1);
}

static void test_weather(void)
{
    /* Values come from a synthetic OpenWeather Kelvin payload, not live data. */
    tv_settings_t s; settings_snapshot(&s);
    const char body[]={"{\"main\":{\"temp\":293.99,\"humidity\":73,\"temp_min\":292.2,\"temp_max\":295.8},"
        "\"wind\":{\"speed\":3.7,\"deg\":350},\"timezone\":3600,"
        "\"weather\":[{\"icon\":\"02d\",\"main\":\"Clouds\",\"description\":\"scattered clouds\"}]}"};
    weather_snapshot_t weather;
    CHECK(weather_parse_response(body,strlen(body),&s,&weather));
    CHECK(weather.valid && weather.temperature_c==20 && weather.humidity==73);
    CHECK(fabs(weather.temperature_min_c-19.05)<0.000001 && fabs(weather.temperature_max_c-22.65)<0.000001);
    CHECK(weather.wind_mps==3.7 && weather.timezone_seconds==3600);
    CHECK(!strcmp(weather.main,"Clouds") && !strcmp(weather.description,"scattered cloud"));
    CHECK(!strcmp(weather.wind_direction,"North") && !strcmp(weather.icon,"02d"));
    CHECK(!strcmp(weather.city,"London") && !strcmp(weather.country,"GB"));
    CHECK(!weather_parse_response("{}",2,&s,&weather));
    CHECK(!weather_parse_response(body,10,&s,&weather));
    const char invalid[]={"{\"main\":{\"temp\":293,\"humidity\":101},\"wind\":{\"speed\":1},\"weather\":[{\"icon\":\"02d\"}]}"};
    CHECK(!weather_parse_response(invalid,strlen(invalid),&s,&weather));
    const char cold[]={"{\"main\":{\"temp\":270.9,\"humidity\":0},\"wind\":{\"speed\":0,\"deg\":90},\"weather\":[{\"icon\":\"13n\"}]}"};
    CHECK(weather_parse_response(cold,strlen(cold),&s,&weather));
    CHECK(weather.temperature_c==-2 && !strcmp(weather.wind_direction,"East"));
    /* Literal factory strings and all half-open sector boundaries, including
     * 348.75/360 wrapping to North. A Ghidra symbol name hides its hyphen. */
    static const char *directions[]={"North","North-Northeast","Northeast","East-Northeast",
        "East","East-Southeast","Southeast","South-Southeast","South","South-Southwest",
        "Southwest","West-Southwest","West","West-Northwest","Northwest","North-Northwest"};
    char directional[256];
    for(unsigned i=0;i<16;++i){
        const double angles[]={i*22.5, i*22.5+11.25, i*22.5+11.25-0.00001};
        for(unsigned j=0;j<3;++j){
            snprintf(directional,sizeof(directional),"{\"main\":{\"temp\":293,\"humidity\":50},"
                "\"wind\":{\"speed\":1,\"deg\":%.5f},\"weather\":[{\"icon\":\"02d\"}]}",angles[j]);
            CHECK(weather_parse_response(directional,strlen(directional),&s,&weather));
            CHECK(!strcmp(weather.wind_direction,directions[j==1?(i+1)%16:i]));
        }
    }
}
static void test_assets(void)
{
    CHECK(media_init()==ESP_OK);tv_settings_t s;settings_snapshot(&s);
    for(unsigned i=0;i<PHOTO_COUNT;++i){rendered_pixels=0;CHECK(media_draw_photo(i)==ESP_OK);CHECK(rendered_pixels==240*240);}
    unsigned frames=0;const unsigned counts[]={19,15,25,16,23};
    for(unsigned animation=0;animation<5;++animation){CHECK(media_animation_frames(animation)==counts[animation]);for(unsigned frame=0;frame<counts[animation];++frame){rendered_pixels=0;CHECK(media_draw_animation(animation,frame,83,143)==ESP_OK);CHECK(rendered_pixels==74*74);++frames;}}
    CHECK(frames==98);CHECK(media_draw_animation(0,19,0,0)!=ESP_OK);
    static const char *const codes[]={"01d","01n","02d","02n","03d","03n","04d","04n","09d","09n","10d","10n","11d","11n","13d","13n","50d","50n"};
    for(unsigned i=0;i<18;++i){rendered_pixels=0;CHECK(media_draw_weather(codes[i],178,155)==ESP_OK);CHECK(rendered_pixels==3600);}
    const unsigned offsets[]={0x3ba800,0x3be400,0x3c2000,0x3c5c00};
    for(unsigned i=0;i<4;++i)CHECK(media_draw_jpeg(offsets[i],WEATHER_SLOT_BYTES,0,0)==ESP_OK);
    uint8_t data[4];CHECK(media_read(ASSETS_BASE-1,data,4)!=ESP_OK);CHECK(media_read(ASSETS_BASE+partition.size-2,data,4)!=ESP_OK);
    CHECK(le32(flash_bytes+ANIMATION_BASE-ASSETS_BASE+3)<=ANIMATION_SLOT_BYTES);
}

static void upload_entire(unsigned slot,const uint8_t *photo,size_t length,bool valid)
{
    unsigned chunks=(unsigned)(length+4095)/4096;
    CHECK(photo_upload_start(slot,(uint32_t)length,chunks)==ESP_OK);
    CHECK(media_draw_photo(0)!=ESP_OK);
    for(unsigned i=0;i<chunks;++i){size_t block=length-i*4096;if(block>4096)block=4096;CHECK(photo_upload_chunk(slot,i,chunks,photo+i*4096,block)==ESP_OK);}
    CHECK((photo_upload_finish(slot)==ESP_OK)==valid);
}

static void test_uploads(void)
{
    tv_settings_t s;settings_snapshot(&s);size_t length=s.photo_size[0];uint8_t *photo=malloc(length);CHECK(photo!=NULL);memcpy(photo,flash_bytes,length);
    CHECK(photo_upload_start(0,PHOTO_SLOT_BYTES+1,26)!=ESP_OK);CHECK(photo_upload_start(5,100,1)!=ESP_OK);CHECK(photo_upload_start(0,100,2)!=ESP_OK);
    unsigned chunks=(unsigned)(length+4095)/4096;
    CHECK(photo_upload_start(0,(uint32_t)length,chunks)==ESP_OK);CHECK(photo_upload_start(1,100,1)!=ESP_OK);
    CHECK(photo_upload_chunk(0,1,chunks,photo+4096,4096)!=ESP_OK);
    CHECK(photo_upload_chunk(0,0,chunks,photo,4096)==ESP_OK);CHECK(photo_upload_chunk(0,0,chunks,photo,4096)==ESP_OK);
    photo[0]^=1;CHECK(photo_upload_chunk(0,0,chunks,photo,4096)!=ESP_OK);photo[0]^=1;
    CHECK(photo_upload_finish(0)!=ESP_OK);
    for(unsigned i=1;i<chunks;++i){size_t block=length-i*4096;if(block>4096)block=4096;CHECK(photo_upload_chunk(0,i,chunks,photo+i*4096,block)==ESP_OK);}
    CHECK(photo_upload_finish(0)==ESP_OK);CHECK(!memcmp(photo,flash_bytes,length));
    uint8_t *unsafe=malloc(length+8);CHECK(unsafe!=NULL);memcpy(unsafe,photo,2);const uint8_t exif[]={255,0xe1,0,6,'E','X','I','F'};memcpy(unsafe+2,exif,8);memcpy(unsafe+10,photo+2,length-2);
    upload_entire(1,unsafe,length+8,false);settings_snapshot(&s);CHECK(s.photo_size[1]==0);
    memcpy(unsafe,photo,length);memcpy(unsafe+length,exif,8);unsafe[length+6]=255;unsafe[length+7]=0xd9;
    upload_entire(1,unsafe,length+8,false); /* A decoder alone ignores trailing metadata. */
    uint8_t wrong_size[]={255,0xd8,255,0xc0,0,8,8,0,100,0,100,3,255,0xda,0,2,255,0xd9};upload_entire(1,wrong_size,sizeof(wrong_size),false);
    CHECK(photo_upload_start(2,100,1)==ESP_OK);clock_us+=120000001;CHECK(!media_upload_active());CHECK(photo_upload_start(2,100,1)==ESP_OK);clock_us+=120000001;
    free(unsafe);free(photo);
}

static size_t append_part(char *body,size_t pos,const char *name,const void *data,size_t length)
{pos+=sprintf(body+pos,"--test-boundary\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n",name);memcpy(body+pos,data,length);pos+=length;memcpy(body+pos,"\r\n",2);return pos+2;}
static void test_multipart(void)
{
    char body[6000];uint8_t binary[20]={255,0xd8,0,'-', '-', '-',13,10};size_t pos=0;
    CHECK(photo_upload_start(4,sizeof(binary),1)==ESP_OK);
    pos=append_part(body,pos,"chunk",binary,sizeof(binary));pos=append_part(body,pos,"file_number","5",1);pos=append_part(body,pos,"chunk_index","0",1);pos=append_part(body,pos,"total_chunks","1",1);pos+=sprintf(body+pos,"--test-boundary--\r\n");
    prepare("/upload_chunk",body,pos,"multipart/form-data; boundary=test-boundary");web_photo_post(&request);CHECK(request.status==200);CHECK(!memcmp(flash_bytes+4*PHOTO_SLOT_BYTES,binary,sizeof(binary)));
    prepare("/upload_chunk",body,pos-4,"multipart/form-data; boundary=test-boundary");web_photo_post(&request);CHECK(request.status==400);
    prepare("/upload_chunk",body,pos,"multipart/form-data; boundary=incorrect");web_photo_post(&request);CHECK(request.status==400);
    clock_us+=120000001;
    prepare("/get_Photo_File?file=1&chunk=0&size=10240","",0,NULL);web_photo_get(&request);CHECK(request.status==200 && request.response_length==10240);
    prepare("/get_Photo_File?file=1&chunk=100&size=12288","",0,NULL);web_photo_get(&request);CHECK(request.status==400);
}

static void test_dns(void)
{
    const uint8_t question[]={0x12,0x34,1,0,0,1,0,0,0,0,0,0,3,'w','w','w',7,'e','x','a','m','p','l','e',3,'c','o','m',0,0,1,0,1};
    uint8_t packet[514];memset(packet,0x5a,sizeof(packet));memcpy(packet,question,sizeof(question));
    size_t length=captive_dns_reply(packet,sizeof(question),512);CHECK(length==sizeof(question)+16);CHECK(packet[0]==0x12 && packet[1]==0x34 && packet[7]==1);CHECK(!memcmp(packet+length-4,"\xc0\xa8\x2b\x01",4));CHECK(packet[512]==0x5a && packet[513]==0x5a);
    for(size_t n=0;n<sizeof(question);++n){memcpy(packet,question,sizeof(question));CHECK(captive_dns_reply(packet,n,512)==0);}
    memcpy(packet,question,sizeof(question));CHECK(captive_dns_reply(packet,sizeof(question),sizeof(question)+15)==0);
    memcpy(packet,question,sizeof(question));packet[12]=0xc0;CHECK(captive_dns_reply(packet,sizeof(question),512)==0);
    memcpy(packet,question,sizeof(question));packet[12]=64;CHECK(captive_dns_reply(packet,sizeof(question),512)==0);
    memcpy(packet,question,sizeof(question));packet[5]=2;CHECK(captive_dns_reply(packet,sizeof(question),512)==0);
    memcpy(packet,question,sizeof(question));packet[30]=28;CHECK(captive_dns_reply(packet,sizeof(question),512)==sizeof(question));CHECK(packet[7]==0);
    memset(packet,0,512);packet[5]=1;size_t pos=12;for(unsigned i=0;i<4;++i){packet[pos++]=63;memset(packet+pos,'a',63);pos+=63;}packet[pos++]=0;packet[pos++]=0;packet[pos++]=1;packet[pos++]=0;packet[pos++]=1;CHECK(captive_dns_reply(packet,pos,512)==0);
    CHECK(captive_dns_reply(packet,513,512)==0);
}

#include "http_contracts.inc"

int main(int argc,char **argv)
{
    memset(factory_sector,255,sizeof(factory_sector));
    CHECK(argc==2 || argc==3);FILE *file=fopen(argv[1],"rb");CHECK(file!=NULL);CHECK(fread(flash_bytes,1,sizeof(flash_bytes),file)==sizeof(flash_bytes));CHECK(fgetc(file)==EOF);fclose(file);
    CHECK(web_start()==ESP_OK);CHECK(registered_routes==40);
    for(unsigned i=0;i<registered_routes;++i)for(unsigned j=i+1;j<registered_routes;++j)CHECK(route_table[i]->method!=route_table[j]->method || strcmp(route_table[i]->uri,route_table[j]->uri));
    test_settings();test_factory_settings();test_weather();test_assets();test_http_contracts();test_uploads();test_multipart();test_dns();
    for(unsigned i=0;i<registered_routes;++i)CHECK(route_success[i]>0);
    if(argc==3)write_native_report(argv[2]);
    printf("PASS: %u checks; 107 JPEGs, 98 animation frames, 18 BMPs; factory settings, Kelvin weather, flash uploads and HTTP handlers\n",checks);
    return 0;
}
