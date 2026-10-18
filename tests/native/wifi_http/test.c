#include "native_wifi_public.h"
#ifdef TARGET_C3
#define s_pending s_reboot_pending
#define s_reserved_epoch s_reboot_reserved_epoch
#define web_reboot_request websocket_service_request_reboot
#define web_reboot_lease_t websocket_reboot_lease_t
#define web_reboot_reserve websocket_service_reboot_reserve
#define web_reboot_cancel websocket_service_reboot_cancel
#endif
static void text_file(const char *path,const char *text) {
    FILE *file=mapped_open(path,"wb");assert(file&&fwrite(text,1,strlen(text),file)==strlen(text)&&!fclose(file));
}
static void expect_file(const char *text) {
    FILE *file=mapped_open("/spiffs/data/wifi.csv","rb");assert(file);char data[800];size_t size=fread(data,1,sizeof(data),file);
    assert(size==strlen(text)&&!memcmp(data,text,size)&&!fclose(file));
}
static void reset(void) {
    assert(!http_workspace);++groups;
    memset(&hd,0,sizeof(hd));memset(&sd,0,sizeof(sd));
    hd.config.max_resp_headers=8;hd.hd_req=(httpd_req_t){.handle=&hd,.aux=&hd.hd_req_aux,.method=HTTP_POST,.uri="/api/native/wifi"};
    hd.hd_req_aux=(struct httpd_req_aux){.sd=&sd,.max_req_hdr_len=2048,.status="200 OK",.content_type="text/plain"};
    sd.handle=&hd;sd.fd=7;sd.send_fn=default_send;sd.recv_fn=default_receive;
    clock_us=1000000;receive_ready=send_ready=receive_step=publish_delay=0;
    receives=sends=wait_read=wait_write=close_prepares=activity=publications=0;
    async_begins=async_completes=queued_static=file_opens=0;
    form_erases=chunk_erases=playlist_notifications=0;
    fail_workspace=fail_response=fail_store=store_busy=committed_file=fail_io_allocation=false;sleep_allowed=true;
    lookup_count=lookup_fault_mask=0;
    receive_wants_write=send_wants_read=false;receive_chunk=send_chunk=SIZE_MAX;
    source_size=source_offset=response_size=event_size=0;response[0]=events[0]=0;
    type="application/json";
    s_wifi_store.ready=false;assert(network_service_storage_init()==ESP_OK);
    mapped_remove("/spiffs/data/wifi.csv.tmp");mapped_remove("/spiffs/data/wifi.csv.bak");
    text_file("/spiffs/data/wifi.csv"," duplicate \tOLD_PRIVATE_A\n duplicate \tOLD_PRIVATE_B\n");
#ifdef TARGET_C3
    s_reboot_pending=false;s_reboot_reserved_epoch=0;s_reboot_next_epoch=0;atomic_store(&s_reboot_ready,true);
#else
    s_pending=false;s_reserved_epoch=0;s_next_epoch=0;assert(web_reboot_start()==ESP_OK);web_wifi_activate();web_upload_activate();
#endif
}
static void body(const char *text) {
    source_size=strlen(text);assert(source_size<sizeof(source));memcpy(source,text,source_size);
    hd.hd_req.content_len=hd.hd_req_aux.remaining_len=source_size;
}
static void make_edit(void) {
    native_wifi_metadata_t meta;assert(network_service_wifi_metadata(&meta)==NATIVE_WIFI_OK&&meta.count==2);
    char value[1024];snprintf(value,sizeof(value),
        "{\"revision\":\"%s\",\"profiles\":[{\"id\":\"r2\",\"password_action\":\"keep\"},{\"ssid\":\" new \",\"password_action\":\"set\",\"password\":\"NEW_REQUEST_CANARY\"}]}",meta.revision);
    body(value);
}
static void closed(void) {
    assert(close_prepares==1&&!http_workspace&&!hd.hd_req.sess_ctx);
    if(sd.recv_fn!=default_receive)assert(sd.recv_fn(&hd,7,(char *)source,1,0)==HTTPD_SOCK_ERR_FAIL);
    if(sd.send_fn!=default_send)assert(sd.send_fn(&hd,7,"x",1,0)==HTTPD_SOCK_ERR_FAIL);
    httpd_req_cleanup(&hd.hd_req);assert(!sd.ctx&&!sd.free_ctx);
    assert(!strstr(response,"OLD_PRIVATE")&&!strstr(response,"NEW_REQUEST_CANARY")&&!strstr(response,"IMPORT_REQUEST_CANARY"));
}
static void make_import(unsigned kind,bool asset,bool invalid) {
    const char *csv=invalid?"invalid":" new \tIMPORT_REQUEST_CANARY\n";
    int count;
    if(kind==2)count=snprintf((char *)source,sizeof(source),
        "--wifi\r\nContent-Disposition: form-data; name=\"ssid\"\r\n\r\n new \r\n"
        "--wifi\r\nContent-Disposition: form-data; name=\"pass\"\r\n\r\nIMPORT_REQUEST_CANARY\r\n--wifi--\r\n");
    else count=snprintf((char *)source,sizeof(source),
        "%s--wifi\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"wifi.csv\"\r\n\r\n%s\r\n--wifi--\r\n",
        asset?"--wifi\r\nContent-Disposition: form-data; name=\"www\"; filename=\"theme.css.gz\"\r\n\r\nNEW\r\n":"",
        kind==0?"wifile":"data",csv);
    assert(count>0&&(size_t)count<sizeof(source));source_size=(size_t)count;
    hd.hd_req.content_len=hd.hd_req_aux.remaining_len=source_size;type="multipart/form-data; boundary=wifi";
}
static esp_err_t import_handler(unsigned kind) {
    return kind==0?web_upload_handler(&hd.hd_req):kind==1?web_board_upload_handler(&hd.hd_req):web_wifi_upload_handler(&hd.hd_req);
}
static void import_cases(void) {
    for(unsigned kind=0;kind<3;++kind)for(unsigned mode=0;mode<6;++mode) {
        reset();make_import(kind,false,false);receive_chunk=mode+1;send_chunk=7;
        if(mode==0){assert(httpd_unrecv(&hd.hd_req,(char *)source,37)==37);source_offset=37;}
        if(mode==1)fail_response=true;
        if(mode==2){receive_ready=clock_us+2000000U;receive_wants_write=true;}
        if(mode==3)publish_delay=130000000U;
        if(mode==4){send_ready=clock_us+2000000U;send_wants_read=true;}
        assert(import_handler(kind)==ESP_FAIL);closed();
        assert(publications==1&&s_pending&&!s_reserved_epoch&&form_erases==1&&chunk_erases);
        expect_file(" new \tIMPORT_REQUEST_CANARY\n");
        if(!fail_response&&mode!=4)assert(strstr(response,kind?"303 See Other":"200 OK"));
        if(mode==2)assert(wait_write);
        if(mode==4)assert(wait_read);
    }
    for(unsigned mode=0;mode<9;++mode) {
        reset();make_import(1,true,mode==2);text_file("/spiffs/www/theme.css.gz","OLD");
        web_reboot_lease_t foreign={0};
        if(mode==0)web_reboot_request(0);
        if(mode==1)assert(web_reboot_reserve(&foreign)==ESP_OK);
        if(mode==3)fail_store=true;
        if(mode==4)receive_ready=clock_us+10000001U;
        if(mode==5){receive_step=9000000;receive_chunk=1;}
        if(mode==6)fail_io_allocation=true;
        if(mode==7){type="multipart/form-data; x-boundary=wifi";}
        if(mode==8){
#ifdef TARGET_C3
            atomic_store(&s_reboot_ready,false);
#else
            web_upload_deactivate();
#endif
        }
        assert(import_handler(1)==ESP_FAIL);closed();
        assert(!publications&&!activity);expect_file(" duplicate \tOLD_PRIVATE_A\n duplicate \tOLD_PRIVATE_B\n");
        FILE *file=mapped_open("/spiffs/www/theme.css.gz","rb");char asset[4]={0};assert(file&&fread(asset,1,3,file)==3&&!fclose(file)&&!strcmp(asset,"OLD"));
        if(mode<2)assert(strstr(response,"503 Service Unavailable"));
        if(mode==0)assert(s_pending);else assert(!s_pending);
        if(mode==1){assert(s_reserved_epoch==foreign.epoch);web_reboot_cancel(&foreign);}
        assert(!s_reserved_epoch);
        mapped_remove("/spiffs/www/theme.css.gz");mapped_remove("/spiffs/www/theme.css.gz.bak");
    }
}
static void success_cases(void) {
    for(size_t chunk=1;chunk<=85;chunk+=7) {
        reset();make_edit();receive_chunk=chunk;send_chunk=5;
        assert(httpd_unrecv(&hd.hd_req,(char *)source,37)==37);source_offset=37;
        assert(web_wifi_edit_handler(&hd.hd_req)==ESP_FAIL);closed();
        assert(publications==1&&s_pending&&!s_reserved_epoch&&strstr(response,"200 OK")&&strstr(response,"no-store"));
        expect_file(" duplicate \tOLD_PRIVATE_B\n new \tNEW_REQUEST_CANARY\n");
        assert(strstr(events,"TF")&&strchr(events,'C')&&strchr(events,'C')>strchr(events,'F'));
#ifdef TARGET_C3
        assert(activity==1);
#endif
    }
    for(unsigned mode=0;mode<5;++mode) {
        reset();make_edit();
        if(mode==0)fail_response=true;
        if(mode==1)send_ready=clock_us+40000000U;
        if(mode==2){receive_ready=clock_us+2000000U;receive_wants_write=true;}
        if(mode==3)publish_delay=40000000U; // Durable publication past receive budget still commits reboot.
        if(mode==4){send_ready=clock_us+500000U;send_wants_read=true;}
        assert(web_wifi_edit_handler(&hd.hd_req)==ESP_FAIL);closed();
        assert(publications==1&&s_pending&&!s_reserved_epoch);
        if(mode==2)assert(wait_write);
        if(mode==4)assert(wait_read);
        expect_file(" duplicate \tOLD_PRIVATE_B\n new \tNEW_REQUEST_CANARY\n");
    }
}
static void rejection_cases(void) {
    for(unsigned mode=0;mode<16;++mode) {
        reset();make_edit();
        switch(mode) {
        case 0:body("{\"password\":\"NEW_REQUEST_CANARY\"}");break;
        case 1:type="text/plain";break;
        case 2:type=NULL;break;
        case 3:hd.hd_req.content_len=0;break;
        case 4:hd.hd_req.content_len=4097;break;
        case 5:fail_workspace=true;break;
        case 6:web_reboot_request(0);break;
        case 7:fail_store=true;break;
        case 8:store_busy=true;break;
        case 9:source[14]=source[14]=='0'?'1':'0';break; // Matching schema, stale revision.
        case 10:receive_ready=clock_us+10000001U;break;
        case 11:receive_step=9000000;receive_chunk=1;break;
        case 12:hd.hd_req.method=HTTP_GET;break;
        case 13:
#ifdef TARGET_C3
            sleep_allowed=false;
#else
            web_wifi_deactivate();
#endif
            break;
        case 14:hd.config.max_resp_headers=1;break;
        case 15:fail_io_allocation=true;break;
        }
        assert(web_wifi_edit_handler(&hd.hd_req)==ESP_FAIL);closed();
        assert(!publications&&!s_reserved_epoch&&!activity);
        expect_file(" duplicate \tOLD_PRIVATE_A\n duplicate \tOLD_PRIVATE_B\n");
        if(mode==9)assert(strstr(response,"409 Conflict"));
        if(mode==10||mode==11)assert(strstr(response,"408 Request Timeout"));
        if(mode==6)assert(s_pending);else assert(!s_pending);
    }
}
static void metadata_cases(void) {
    reset();hd.hd_req.method=HTTP_GET;
    assert(web_wifi_info_handler(&hd.hd_req)==ESP_OK&&!close_prepares&&!activity);
    assert(strstr(response,"200 OK")&&strstr(response,"no-store")&&strstr(response,"duplicate")&&!strstr(response,"OLD_PRIVATE")&&!strstr(response,"password"));
    httpd_req_cleanup(&hd.hd_req);
    reset();text_file("/spiffs/data/wifi.csv","invalid");hd.hd_req.method=HTTP_GET;
    assert(web_wifi_info_handler(&hd.hd_req)==ESP_OK&&!activity&&strstr(response,"503 Service Unavailable")&&strstr(response,"no-store"));
    httpd_req_cleanup(&hd.hd_req);
    reset();hd.hd_req.method=HTTP_GET;hd.hd_req.content_len=hd.hd_req_aux.remaining_len=1000000;
    assert(web_wifi_info_handler(&hd.hd_req)==ESP_FAIL&&close_prepares==1&&!activity&&!receives&&!publications&&strstr(response,"400 Bad Request"));
    httpd_req_cleanup(&hd.hd_req);
    reset();wifi_http_payload_t *payload=workspace_calloc(1,sizeof(*payload));
    strcpy((char *)payload->body,"ABNORMAL_PRIVATE_CANARY");strcpy(payload->edit.profiles[0].password,"ABNORMAL_PRIVATE_CANARY");
    native_wifi_request_io_t *io=native_wifi_request_io_open(&hd.hd_req,10000000,30000000,payload,wifi_http_free);
    assert(io&&hd.hd_req.sess_ctx==io);
    httpd_req_cleanup(&hd.hd_req);assert(sd.ctx==io);
    httpd_sess_free_ctx(&sd.ctx,sd.free_ctx);assert(!sd.ctx&&!http_workspace);
}
static unsigned foreign_frees;
static void foreign_free(void *context) {assert(context);++foreign_frees;memset(context,0,32);free(context);}
static void foreign_owner_case(void) {
    reset();make_edit();void *foreign=malloc(32);assert(foreign);memset(foreign,0x51,32);
    httpd_sess_set_ctx(&hd,7,foreign,foreign_free);
    assert(web_wifi_edit_handler(&hd.hd_req)==ESP_FAIL&&close_prepares==1&&!publications&&!activity&&!http_workspace);
    assert(hd.hd_req.sess_ctx==foreign&&!foreign_frees&&strstr(response,"503 Service Unavailable"));
    httpd_req_cleanup(&hd.hd_req);assert(sd.ctx==foreign&&!foreign_frees);
    httpd_sess_free_ctx(&sd.ctx,sd.free_ctx);assert(!sd.ctx&&foreign_frees==1);
}
static void inactive_info_cases(void) {
    for(unsigned mode=0;mode<3;++mode) {
        reset();hd.hd_req.method=HTTP_GET;
#ifdef TARGET_C3
        sleep_allowed=false;
#else
        web_wifi_deactivate();
#endif
        if(mode)hd.hd_req.content_len=hd.hd_req_aux.remaining_len=1000000;
        void *foreign=NULL;unsigned freed=foreign_frees;
        if(mode==2){foreign=malloc(32);assert(foreign);httpd_sess_set_ctx(&hd,7,foreign,foreign_free);}
        assert(web_wifi_info_handler(&hd.hd_req)==ESP_FAIL&&close_prepares==1&&!receives&&!activity&&!publications);
        assert(strstr(response,"503 Service Unavailable")&&strstr(response,"Connection: close")&&hd.hd_req.sess_ctx==foreign);
        httpd_req_cleanup(&hd.hd_req);
        if(foreign){assert(sd.ctx==foreign&&foreign_frees==freed);httpd_sess_free_ctx(&sd.ctx,sd.free_ctx);assert(foreign_frees==freed+1);}
    }
}
static void io_attachment_cases(void) {
    for(unsigned lookup=1;lookup<=3;++lookup) {
        reset();make_edit();lookup_fault_mask=1U<<lookup;
        assert(web_wifi_edit_handler(&hd.hd_req)==ESP_FAIL);closed();
        assert(!publications&&!s_reserved_epoch&&!activity&&strstr(response,"503 Service Unavailable"));
    }
    reset();make_edit();lookup_fault_mask=(1U<<3)|(1U<<4); // Override failure AND failed API detach.
    assert(web_wifi_edit_handler(&hd.hd_req)==ESP_FAIL&&close_prepares==1&&!publications&&!s_reserved_epoch&&!activity);
    assert(hd.hd_req.sess_ctx&&http_workspace); // SDK still owns both blocks; no manual double free.
    httpd_req_cleanup(&hd.hd_req);assert(sd.ctx&&http_workspace);
    httpd_sess_free_ctx(&sd.ctx,sd.free_ctx);assert(!sd.ctx&&!http_workspace);
}
static void uri_cases(void) {
    const char *bad[]={"/data/wifi.csv","/data/wifi.csv.bak","/data/wifi.csv.tmp","/data/playlist.csv.bak","/data/index.dat","/data","/DATA/wifi.csv","/DaTa/playlist.csv","/data/%77ifi.csv","/%64ata/wifi.csv","/data//playlist.csv","/./data/playlist.csv","/www/../data/wifi.csv","/data\\wifi.csv","//data/playlist.csv","/data/wifi.csv?download=1","/data/playlist.csv#x","/data/playlist.csv x","relative"};
    for(size_t i=0;i<sizeof(bad)/sizeof(*bad);++i){assert(!native_wifi_public_static_uri(bad[i],true));++groups;}
    const char *good[]={"/data/playlist.csv","/data/playlist.csv?download=1","/","/script.js","/options.html.gz"};
    for(size_t i=0;i<sizeof(good)/sizeof(*good);++i){assert(native_wifi_public_static_uri(good[i],true)&&!native_wifi_public_static_uri(good[i],false));++groups;}
}
#ifdef TARGET_C3
static void actual_static_cases(void) {
    const char *bad[]={"/data/wifi.csv","/data/wifi.csv.bak?download=1","/data/wifi.csv.tmp","/%64ata/wifi.csv","/DATA/wifi.csv","/data/playlist.csv.bak","/data/index.dat","/www/../data/wifi.csv"};
    for(size_t i=0;i<sizeof(bad)/sizeof(*bad);++i) {
        reset();unsigned opened=file_opens;hd.hd_req.method=HTTP_GET;hd.hd_req.uri=bad[i];
        assert(static_handler(&hd.hd_req)==ESP_OK&&!async_begins&&!async_completes&&!queued_static&&file_opens==opened);
        assert(strstr(response,"404 Not Found")&&!strstr(response,"OLD_PRIVATE"));httpd_req_cleanup(&hd.hd_req);
    }
    reset();hd.hd_req.method=HTTP_HEAD;hd.hd_req.uri="/data/playlist.csv";
    assert(static_handler(&hd.hd_req)==ESP_OK&&!async_begins&&!queued_static&&strstr(response,"404 Not Found"));httpd_req_cleanup(&hd.hd_req);
    reset();hd.hd_req.method=HTTP_GET;hd.hd_req.uri="/data/playlist.csv?download=1";
    assert(static_handler(&hd.hd_req)==ESP_OK&&async_begins==1&&queued_static==1&&!async_completes);httpd_req_cleanup(&hd.hd_req);
}
#endif
int main(void) {
    assert(mkdtemp(directory));uri_cases();success_cases();rejection_cases();metadata_cases();foreign_owner_case();io_attachment_cases();inactive_info_cases();import_cases();
#ifdef TARGET_C3
    actual_static_cases();
#endif
    assert(workspace_allocations==workspace_frees);
    mapped_remove("/spiffs/data/wifi.csv");mapped_remove("/spiffs/data/wifi.csv.tmp");mapped_remove("/spiffs/data/wifi.csv.bak");assert(!rmdir(directory));
    printf("%u groups passed; %u HTTP secret workspaces erased; actual target owner+HTTPD pending/context/response+reboot lease\n",groups,workspace_frees);return 0;
}
