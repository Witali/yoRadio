#include "native_wifi_public.h"
#ifdef TARGET_C3
#define s_pending s_reboot_pending
#define s_reserved_epoch s_reboot_reserved_epoch
#define web_reboot_request websocket_service_request_reboot
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
    fail_workspace=fail_response=fail_store=store_busy=committed_file=false;sleep_allowed=true;
    receive_wants_write=send_wants_read=false;receive_chunk=send_chunk=SIZE_MAX;
    source_size=source_offset=response_size=event_size=0;response[0]=events[0]=0;
    type="application/json";
    s_wifi_store.ready=false;assert(network_service_storage_init()==ESP_OK);
    mapped_remove("/spiffs/data/wifi.csv.tmp");mapped_remove("/spiffs/data/wifi.csv.bak");
    text_file("/spiffs/data/wifi.csv"," duplicate \tOLD_PRIVATE_A\n duplicate \tOLD_PRIVATE_B\n");
#ifdef TARGET_C3
    s_reboot_pending=false;s_reboot_reserved_epoch=0;s_reboot_next_epoch=0;atomic_store(&s_reboot_ready,true);
#else
    s_pending=false;s_reserved_epoch=0;s_next_epoch=0;assert(web_reboot_start()==ESP_OK);web_wifi_activate();
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
    assert(!strstr(response,"OLD_PRIVATE")&&!strstr(response,"NEW_REQUEST_CANARY"));
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
    for(unsigned mode=0;mode<15;++mode) {
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
    reset();wifi_http_io_t *io=workspace_calloc(1,sizeof(*io));
    strcpy((char *)io->body,"ABNORMAL_PRIVATE_CANARY");strcpy(io->edit.profiles[0].password,"ABNORMAL_PRIVATE_CANARY");
    httpd_sess_set_ctx(&hd,7,io,wifi_http_free);assert(hd.hd_req.sess_ctx==io);
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
    assert(mkdtemp(directory));uri_cases();success_cases();rejection_cases();metadata_cases();foreign_owner_case();
#ifdef TARGET_C3
    actual_static_cases();
#endif
    assert(workspace_allocations==workspace_frees);
    mapped_remove("/spiffs/data/wifi.csv");mapped_remove("/spiffs/data/wifi.csv.tmp");mapped_remove("/spiffs/data/wifi.csv.bak");assert(!rmdir(directory));
    printf("%u groups passed; %u HTTP secret workspaces erased; actual target owner+HTTPD pending/context/response+reboot lease\n",groups,workspace_frees);return 0;
}
