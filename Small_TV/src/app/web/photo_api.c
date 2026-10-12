#include "web.h"
#include "board.h"
#include "media.h"
#include "settings.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

static bool decimal(const uint8_t *value,size_t length,unsigned maximum,unsigned *out)
{
    if (!length || length>10) return false;
    unsigned number=0;
    for (size_t i=0;i<length;++i) {
        if (value[i]<'0' || value[i]>'9') return false;
        unsigned digit=value[i]-'0';
        if (digit>maximum || number>(maximum-digit)/10) return false;
        number=number*10+digit;
    }
    *out=number; return true;
}

esp_err_t web_photo_get(httpd_req_t *req)
{
    char query[160],value[16]; unsigned slot,chunk,size;
    if (httpd_req_get_url_query_str(req,query,sizeof(query))!=ESP_OK ||
        httpd_query_key_value(query,"file",value,sizeof(value))!=ESP_OK || !decimal((uint8_t *)value,strlen(value),5,&slot) || !slot ||
        httpd_query_key_value(query,"chunk",value,sizeof(value))!=ESP_OK || !decimal((uint8_t *)value,strlen(value),100,&chunk) ||
        httpd_query_key_value(query,"size",value,sizeof(value))!=ESP_OK || !decimal((uint8_t *)value,strlen(value),12288,&size)) return web_error(req,"Invalid photo query");
    tv_settings_t s; settings_snapshot(&s); uint32_t length=s.photo_size[slot-1];
    if (!size && !chunk) {
        cJSON *object=cJSON_CreateObject(); cJSON_AddBoolToObject(object,"exists",length>0); cJSON_AddNumberToObject(object,"size",length); return web_json(req,object);
    }
    uint32_t start=chunk*size;
    if (!size || start>=length) return web_error(req,"Photo chunk outside image");
    if (size>length-start) size=length-start;
    uint8_t *data=malloc(size); if (!data) return httpd_resp_send_err(req,HTTPD_500_INTERNAL_SERVER_ERROR,"Out of memory");
    esp_err_t result=media_read(ASSETS_BASE+(slot-1)*PHOTO_SLOT_BYTES+start,data,size);
    if (result==ESP_OK) {httpd_resp_set_type(req,"application/octet-stream"); result=httpd_resp_send(req,(const char *)data,size);}
    else result=web_error(req,"Image unavailable during upload");
    free(data); return result;
}

static uint8_t *find_bytes(uint8_t *data,size_t length,const char *needle,size_t needle_length)
{
    if (needle_length>length) return NULL;
    for (size_t i=0;i<=length-needle_length;++i) if (!memcmp(data+i,needle,needle_length)) return data+i;
    return NULL;
}

static bool multipart_boundary(httpd_req_t *req,char *boundary,size_t capacity)
{
    char content_type[192];
    if (httpd_req_get_hdr_value_str(req,"Content-Type",content_type,sizeof(content_type))!=ESP_OK || strncmp(content_type,"multipart/form-data;",20)) return false;
    const char *start=strstr(content_type,"boundary="); if (!start) return false; start+=9;
    bool quoted=*start=='"'; if (quoted) ++start;
    size_t length=strcspn(start,quoted?"\"":"; \t");
    if (!length || length>70 || length+1>capacity || (quoted && start[length]!='"')) return false;
    for (size_t i=0;i<length;++i) if ((unsigned char)start[i]<33 || (unsigned char)start[i]>126 || start[i]=='"') return false;
    memcpy(boundary,start,length); boundary[length]=0; return true;
}

static esp_err_t upload_multipart(httpd_req_t *req)
{
    char boundary[72],opening[80],separator[80];
    if (!multipart_boundary(req,boundary,sizeof(boundary))) return web_error(req,"Invalid multipart boundary");
    snprintf(opening,sizeof(opening),"--%s\r\n",boundary); snprintf(separator,sizeof(separator),"\r\n--%s",boundary);
    uint8_t *body=(uint8_t *)web_body(req,12288); if (!body) return web_error(req,"Invalid upload body");
    size_t opening_length=strlen(opening),separator_length=strlen(separator),position=opening_length;
    bool valid=req->content_len>=opening_length && !memcmp(body,opening,opening_length),closed=false;
    unsigned slot=0,index=0,total=0,fields=0; const uint8_t *chunk_data=NULL; size_t chunk_length=0;
    for (unsigned parts=0; valid && parts<4; ++parts) {
        uint8_t *headers_end=find_bytes(body+position,req->content_len-position,"\r\n\r\n",4);
        if (!headers_end || (size_t)(headers_end-(body+position))>1024) {valid=false; break;}
        *headers_end=0;
        char *name=strstr((char *)body+position,"name=\"");
        if (!name) {valid=false; break;} name+=6;
        char *name_end=strchr(name,'"'); if (!name_end) {valid=false; break;} *name_end=0;
        uint8_t *data=headers_end+4;
        uint8_t *end=find_bytes(data,req->content_len-(data-body),separator,separator_length);
        if (!end) {valid=false; break;}
        size_t length=end-data;
        unsigned mask=0;
        if (!strcmp(name,"chunk")) {mask=1; chunk_data=data; chunk_length=length; valid=length>0 && length<=PHOTO_CHUNK_BYTES;}
        else if (!strcmp(name,"file_number")) {mask=2; valid=decimal(data,length,PHOTO_COUNT,&slot) && slot>0;}
        else if (!strcmp(name,"chunk_index")) {mask=4; valid=decimal(data,length,24,&index);}
        else if (!strcmp(name,"total_chunks")) {mask=8; valid=decimal(data,length,25,&total) && total>0;}
        else valid=false;
        if (fields&mask) valid=false;
        fields|=mask;
        position=end-body+separator_length;
        if (req->content_len-position<2) {valid=false; break;}
        if (!memcmp(body+position,"--",2)) {
            position+=2;
            if (req->content_len-position==2 && !memcmp(body+position,"\r\n",2)) position+=2;
            closed=position==req->content_len; break;
        }
        if (memcmp(body+position,"\r\n",2)) {valid=false; break;} position+=2;
    }
    esp_err_t result=valid && closed && fields==15?photo_upload_chunk(slot-1,index,total,chunk_data,chunk_length):ESP_ERR_INVALID_ARG;
    free(body); return result==ESP_OK?web_ok(req):web_error(req,"Invalid or out-of-order upload chunk");
}

esp_err_t web_photo_post(httpd_req_t *req)
{
    if (!strcmp(req->uri,"/upload_chunk")) return upload_multipart(req);
    cJSON *object=web_parse_json(req); if (!object) return web_error(req,"Expected upload JSON");
    int slot; esp_err_t result=ESP_ERR_INVALID_ARG;
    if (web_integer(object,"file_number",1,PHOTO_COUNT,&slot)) {
        if (!strcmp(req->uri,"/start_upload")) {
            int length,chunks;
            if (web_integer(object,"file_size",4,PHOTO_SLOT_BYTES,&length) && web_integer(object,"total_chunks",1,25,&chunks)) result=photo_upload_start(slot-1,length,chunks);
        } else if (!strcmp(req->uri,"/finish_upload")) {
            const cJSON *name=cJSON_GetObjectItemCaseSensitive(object,"file_name"); char expected[16]; snprintf(expected,sizeof(expected),"file%d.jpg",slot);
            if (cJSON_IsString(name) && !strcmp(name->valuestring,expected)) result=photo_upload_finish(slot-1);
        }
    }
    cJSON_Delete(object);
    return result==ESP_OK?web_ok(req):web_error(req,"Invalid upload, busy session, or unsafe JPEG (requires baseline 240x240 without private metadata)");
}
