#include "native_ota_form.h"
#ifdef TARGET_C3
#include "ota_upload.h"
#define s_pending s_reboot_pending
#define s_reserved_epoch s_reboot_reserved_epoch
#define web_reboot_request websocket_service_request_reboot
#define WEB_OTA_MAX_BODY_BYTES (0x1B0000U+4096U)
static void web_ota_deactivate(void) {atomic_store(&s_reboot_ready,false);}
#endif
static void reset(void) {
    assert(!owned&&(!hd.hd_req.handle||!hd.hd_req.sess_ctx));++groups;
    memset(&hd,0,sizeof(hd));memset(&sd,0,sizeof(sd));
    hd.config.max_resp_headers=8;hd.hd_req=(httpd_req_t){.handle=&hd,.aux=&hd.hd_req_aux};
    hd.hd_req_aux=(struct httpd_req_aux){.sd=&sd,.max_req_hdr_len=2048,.status="200 OK",.content_type="text/html"};
    sd.handle=&hd;sd.fd=7;sd.send_fn=default_send;sd.recv_fn=default_receive;
    now_us=1000000;receive_ready=send_ready=maintenance_delay=verify_delay=receive_step=0;
    reads=sends=wait_read=wait_write=lookup_count=lookup_fail=0;
    begins=writes=ends=aborts=verifies=activations=maintenance_begins=maintenance_ends=shutdowns=activity=0;
    maintenance=selected=graceful_shutdown=direct_form=no_partition=no_running=fail_calloc=fail_malloc=false;
    fail_maintenance=fail_begin=fail_write=fail_end=fail_verify=fail_activate=false;
    reboot_during_maintenance=false;sleep_allowed=true;recv_fault=send_fault=select_fault=0;
    receive_chunk=send_chunk=SIZE_MAX;source_offset=source_size=flash_size=response_size=event_size=0;
    wire_response[0]=events[0]=0;expected_size=sizeof(image);
    content_type="multipart/form-data; boundary=ota-boundary";
    memset(&current_app,0,sizeof(current_app));strcpy(current_app.project_name,"native-radio");strcpy(current_app.version,"test\"\\\n");
    for(size_t i=0;i<sizeof(current_app.app_elf_sha256);++i)current_app.app_elf_sha256[i]=(uint8_t)i;
#ifdef TARGET_C3
    s_reboot_pending=false;s_reboot_reserved_epoch=0;s_reboot_next_epoch=0;atomic_store(&s_reboot_ready,true);
#else
    s_pending=false;s_reserved_epoch=0;s_next_epoch=0;assert(web_reboot_start()==ESP_OK);web_ota_activate();
#endif
}
static void make_image(void) {
    for(size_t i=0;i<sizeof(image);++i)image[i]=(uint8_t)(i*37U);
    esp_image_header_t header={.magic=ESP_IMAGE_HEADER_MAGIC,.segment_count=1,.hash_appended=1,
#ifdef TARGET_C3
        .chip_id=ESP_CHIP_ID_ESP32C3
#else
        .chip_id=ESP_CHIP_ID_ESP32
#endif
    };
    esp_image_segment_header_t segment={.load_addr=0x3f400020,.data_len=sizeof(esp_app_desc_t)};
    esp_app_desc_t descriptor={.magic_word=ESP_APP_DESC_MAGIC_WORD};memcpy(descriptor.project_name,current_app.project_name,sizeof(descriptor.project_name));
    memcpy(image,&header,sizeof(header));memcpy(image+sizeof(header),&segment,sizeof(segment));
    memcpy(image+sizeof(header)+sizeof(segment),&descriptor,sizeof(descriptor));
    // A binary delimiter prefix with a non-delimiter continuation is data.
    memcpy(image+2048,"\r\n--ota-boundaryX\0\xff",19);
}
static void append(const void *data,size_t size) {assert(source_size+size<sizeof(source));memcpy(source+source_size,data,size);source_size+=size;source[source_size]=0;}
static void text(const char *value) {append(value,strlen(value));}
static void make_body(const char *target,const char *filename,const char *suffix) {
    make_image();text("--ota-boundary\r\nContent-Disposition: form-data; name=\"updatetarget\"\r\n\r\n");text(target);
    text("\r\n--ota-boundary\r\nContent-Disposition: form-data; name=\"update\"");
    if(filename){text("; filename=\"");text(filename);text("\"");}
    text("\r\nContent-Type: application/octet-stream\r\n\r\n");append(image,sizeof(image));text(suffix);
    hd.hd_req.content_len=hd.hd_req_aux.remaining_len=source_size;
}
static esp_err_t direct_before(void *context) {(void)context;++maintenance_begins;maintenance=true;event('M');return fail_maintenance?ESP_FAIL:ESP_OK;}
static native_ota_policy_t policy(void) {
    native_ota_policy_t result={.expected_chip=
#ifdef TARGET_C3
        ESP_CHIP_ID_ESP32C3,
#else
        ESP_CHIP_ID_ESP32,
#endif
        .image_limit=0x1b0000,.before_flash=direct_before};
    memcpy(result.expected_project,current_app.project_name,sizeof(result.expected_project));return result;
}
static bool form_run(const uint8_t *body,size_t size,size_t chunk) {
    native_ota_form_t form;native_ota_policy_t p=policy();direct_form=true;
    assert(native_ota_form_init(&form,"ota-boundary",&p));bool ok=true;
    for(size_t offset=0;offset<size&&ok;){size_t count=size-offset;if(count>chunk)count=chunk;ok=native_ota_form_feed(&form,body+offset,count);offset+=count;}
    ok=ok&&native_ota_form_finish(&form)&&native_ota_form_activate(&form);
    native_ota_form_abort(&form);native_ota_form_abort(&form);assert(!owned);
    return ok;
}
static void test_forms(void) {
    for(size_t chunk=1;chunk<=160;++chunk){
        reset();make_body("fw","app.bin","\r\n--ota-boundary--\r\n");
        assert(form_run(source,source_size,chunk));assert(selected&&begins==1&&maintenance_begins==1&&ends==1&&verifies==1);
        assert(flash_size==sizeof(image)&&!memcmp(image,flash,sizeof(image)));
    }
    reset();make_body("firmware","app.bin","\r\n--ota-boundary--\r\n");assert(form_run(source,source_size,1024));
    const char *bad_target[]={"","fs","FW","fw ","abcdefghijklmnop"};
    for(size_t i=0;i<sizeof(bad_target)/sizeof(*bad_target);++i){reset();make_body(bad_target[i],"app.bin","\r\n--ota-boundary--\r\n");assert(!form_run(source,source_size,137)&&!begins&&!maintenance_begins);}
    for(unsigned mode=0;mode<9;++mode){
        reset();make_body("fw",mode==0?NULL:mode==1?"":"app.bin","\r\n--ota-boundary--\r\n");
        if(mode==2){uint8_t *p=(uint8_t *)strstr((char *)source,"\r\n\r\nfw");assert(p);p[4]=0;}
        if(mode==3){source_size-=5;hd.hd_req.content_len=hd.hd_req_aux.remaining_len=source_size;}
        if(mode==4){source_size=0;text("--ota-boundary\r\nContent-Disposition: form-data; name=update; filename=x\r\n\r\n");append(image,sizeof(image));text("\r\n--ota-boundary--\r\n");}
        if(mode==5){char *p=strstr((char *)source,"name=\"update\"");assert(p);memcpy(p,"name=\"decoyx\"",13);}
        if(mode==6){source_size-=4;text("\r\nContent-Disposition: form-data; name=update; filename=x\r\n\r\nx\r\n--ota-boundary--\r\n");}
        if(mode==7){uint8_t *p=(uint8_t *)memmem(source,source_size,image,288);assert(p);p[0]=0;}
        if(mode==8){uint8_t *p=(uint8_t *)memmem(source,source_size,image,288);assert(p);p[32+48]='X';}
        assert(!form_run(source,source_size,59)&&!selected);
        if(mode<3||mode==4||mode==5||mode>=7)assert(!begins&&!maintenance_begins);
    }
    reset();make_body("fw","app.bin","\r\n--ota-boundary--\r\n");expected_size--;
    assert(!form_run(source,source_size,16384)&&verifies==1&&!selected);
#ifdef TARGET_C3
    reset();native_ota_policy_t p=policy();ota_upload_t legacy;assert(ota_upload_init(&legacy,"ota-boundary",&p));ota_upload_abort(&legacy);
#endif
}
static void assert_closed(void) {
    assert(shutdowns==1&&!owned&&!hd.hd_req.sess_ctx);
    if(sd.recv_fn!=default_receive)assert(sd.recv_fn(&hd,7,(char *)source,1,0)==HTTPD_SOCK_ERR_FAIL);
    if(sd.send_fn!=default_send)assert(sd.send_fn(&hd,7,"x",1,0)==HTTPD_SOCK_ERR_FAIL);
    httpd_req_cleanup(&hd.hd_req);
    assert(!sd.ctx&&!sd.free_ctx&&!hd.hd_req.handle&&!hd.hd_req.aux);
}
static unsigned foreign_frees;
static void foreign_free(void *context) {assert(context);++foreign_frees;free(context);}
static void test_target(void) {
    // Actual target adapter, shared form/image/HTTP, SDK buffered receive/send.
    for(size_t chunk=1;chunk<=73;chunk+=3){
        reset();make_body("fw","app.bin","\r\n--ota-boundary--\r\n");receive_chunk=chunk;send_chunk=7;
        assert(httpd_unrecv(&hd.hd_req,(const char *)source,37)==37);source_offset=37;
        assert(web_ota_handler(&hd.hd_req)==ESP_FAIL);assert_closed();
        assert(selected&&s_pending&&!s_reserved_epoch&&maintenance&&!maintenance_ends&&graceful_shutdown);
        assert(strstr(wire_response,"200 OK")&&strstr(wire_response,"Connection: close")&&response_size>=2&&!strcmp(wire_response+response_size-2,"OK"));
        assert(!hd.hd_req_aux.remaining_len&&flash_size==sizeof(image)&&!memcmp(image,flash,sizeof(image)));
        assert(strstr(events,"FVAR")&&strstr(events,"SC"));
#ifdef TARGET_C3
        assert(activity==1); // Activity stays held through the scheduled reboot.
#endif
    }
    for(unsigned fault=0;fault<28;++fault){
        reset();make_body("fw","app.bin","\r\n--ota-boundary--\r\n");
        switch(fault){
            case 0:content_type="multipart/form-data; x-boundary=ota-boundary";break;
            case 1:content_type="multipart/form-data; boundary=ota-boundary; boundary=evil";break;
            case 2:content_type=NULL;break;
            case 3:hd.hd_req.content_len=0;break;
            case 4:hd.hd_req.content_len=WEB_OTA_MAX_BODY_BYTES+1U;break;
            case 5:fail_calloc=true;break;
            case 6:no_partition=true;break;
            case 7:web_reboot_request(0);break;
            case 8:web_ota_deactivate();break;
            case 9:fail_maintenance=true;break;
            case 10:fail_begin=true;break;
            case 11:fail_write=true;break;
            case 12:fail_end=true;break;
            case 13:fail_verify=true;break;
            case 14:fail_activate=true;break;
            case 15:recv_fault=1;break;
            case 16:recv_fault=2;break;
            case 17:recv_fault=3;break;
            case 18:lookup_fail=4;break;
            case 19:lookup_fail=5;break;
            case 20:receive_ready=now_us+NATIVE_OTA_IDLE_US;break;
            case 21:receive_ready=now_us+NATIVE_OTA_IDLE_US+1;recv_fault=4;break;
            case 22:maintenance_delay=NATIVE_OTA_OVERALL_US;break;
            case 23:verify_delay=NATIVE_OTA_OVERALL_US;break;
            case 24:receive_step=20000;receive_chunk=1;break;
            case 25:select_fault=2;receive_ready=now_us+2000000U;break;
            case 26:lookup_fail=2;break;
            case 27:hd.config.max_resp_headers=1;break;
        }
        assert(web_ota_handler(&hd.hd_req)==ESP_FAIL);assert_closed();
        assert(!selected&&!s_reserved_epoch&&!maintenance);
        assert(!activity);
        if(fault<=9||(fault>=15&&fault<=22)||fault>=25)assert(!begins);
        if(fault==11)assert(aborts==1&&!ends);
        if(fault==12||fault==13)assert(ends==1&&!aborts);
        if(fault>=20&&fault<=24)assert(strstr(wire_response,fault==22?"Cannot enter OTA maintenance":"408 Request Timeout"));
        if(fault==20)assert(wait_read);
        if(fault==21)assert(wait_write);
    }
    for(unsigned fault=0;fault<9;++fault){
        reset();make_body("fw","app.bin","\r\n--ota-boundary--\r\n");
        switch(fault){
            case 0:fail_malloc=true;break; // actual SDK response allocation AFTER activation
            case 1:send_fault=1;break; // SDK send-all must not spin on a zero write
            case 2:send_fault=2;break;
            case 3:send_fault=3;break;
            case 4:send_ready=now_us+200000000U;break;
            case 5:receive_ready=now_us+2000000U;recv_fault=4;break;
            case 6:maintenance_delay=20000000U;break; // controlled processing is not sender idle
            case 7:reboot_during_maintenance=true;break;
            case 8:select_fault=1;receive_ready=now_us+2000000U;break;
        }
        assert(web_ota_handler(&hd.hd_req)==ESP_FAIL);assert_closed();
        assert(selected&&s_pending&&!s_reserved_epoch&&maintenance&&!maintenance_ends&&strstr(events,"SC"));
        if(fault<=4)assert(!graceful_shutdown);else assert(graceful_shutdown);
        if(fault==5)assert(wait_write);
        if(fault==8)assert(wait_read);
    }
    reset();make_body("fw","app.bin","\r\n--ota-boundary--\r\n");content_type="MuLtIpArT/FoRm-DaTa; BOUNDARY=\"ota-boundary\"";
    assert(web_ota_handler(&hd.hd_req)==ESP_FAIL);assert_closed();assert(selected);
#ifdef TARGET_C3
    reset();make_body("fw","app.bin","\r\n--ota-boundary--\r\n");sleep_allowed=false;
    assert(web_ota_handler(&hd.hd_req)==ESP_FAIL);assert_closed();assert(!selected&&!activity&&!s_reserved_epoch&&strstr(wire_response,"503 Service Unavailable"));
#endif
    reset();make_body("fw","app.bin","\r\n--ota-boundary--\r\n");
    void *foreign=malloc(1);assert(foreign);foreign_frees=0;
    sd.ctx=hd.hd_req.sess_ctx=foreign;sd.free_ctx=hd.hd_req.free_ctx=foreign_free;
    assert(web_ota_handler(&hd.hd_req)==ESP_FAIL&&strstr(wire_response,"503 Service Unavailable"));
    assert(hd.hd_req.sess_ctx==foreign&&sd.ctx==foreign&&!foreign_frees&&!begins&&shutdowns==1);
    httpd_req_cleanup(&hd.hd_req);assert(sd.ctx==foreign&&!foreign_frees);
    httpd_sess_free_ctx(&sd.ctx,sd.free_ctx);assert(!sd.ctx&&foreign_frees==1);
    reset();assert(web_ota_info_handler(&hd.hd_req)==ESP_OK&&!activity);
    assert(strstr(wire_response,"application/json")&&strstr(wire_response,"test\\\"\\\\\\u000a")&&strstr(wire_response,"000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"));
    reset();no_partition=true;assert(web_ota_info_handler(&hd.hd_req)==ESP_OK&&strstr(wire_response,"\"max_size\":0,\"max_body_size\":0"));
    reset();no_running=true;assert(web_ota_info_handler(&hd.hd_req)==ESP_OK&&strstr(wire_response,"\"max_size\":0,\"max_body_size\":0"));
#ifdef TARGET_C3
    reset();sleep_allowed=false;assert(web_ota_info_handler(&hd.hd_req)==ESP_OK&&strstr(wire_response,"503 Service Unavailable"));
#endif
}
int main(void) {test_forms();test_target();printf("PASS native OTA HTTP: %u groups; actual shared form/sink/HTTP and target adapter, pinned SDK receive/send/context functions; flash/audio/network/scheduler field seams\n",groups);return 0;}
