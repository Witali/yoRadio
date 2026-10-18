static esp_err_t observed_handler(httpd_req_t *r) {
    ++handler_calls;pending_at_handler=session.pending_len;handler_started=esp_timer_get_time();
    esp_err_t result=!strcmp(r->uri,"/api/native/wifi")?(r->method==HTTP_GET?web_wifi_info_handler(r):web_wifi_edit_handler(r)):
        !strcmp(r->uri,"/upload")?
#ifdef TARGET_C3
        sleep_guarded_upload_handler(r):!strcmp(r->uri,"/webboard")?sleep_guarded_webboard_upload_handler(r):sleep_guarded_recovery_wifi_handler(r);
#else
        web_upload_handler(r):!strcmp(r->uri,"/webboard")?web_board_upload_handler(r):web_wifi_upload_handler(r);
#endif
    handler_ended=esp_timer_get_time();
    bool metadata=!strcmp(current_mode,"info");
    assert(result==(metadata?ESP_OK:
#ifdef NEGATIVE_WIFI_RETURN_OK
        ESP_OK
#else
        ESP_FAIL
#endif
        )&&workspace_allocations==workspace_frees&&!workspace);
    return result;
}
static esp_err_t observed_static(httpd_req_t *r) {
    ++handler_calls;return static_admission_boundary(r);
}
static bool match_uri(const char *route,const char *uri,size_t length) {
    return !strcmp(route,"*")|| (strlen(route)==length&&!strncmp(route,uri,length));
}
static void text_file(const char *path,const char *value) {FILE *file=mapped_open(path,"wb");assert(file&&fwrite(value,1,strlen(value),file)==strlen(value)&&!fclose(file));}
static void expect_file(const char *path,const char *value) {FILE *file=mapped_open(path,"rb");char buffer[800];assert(file);size_t n=fread(buffer,1,sizeof(buffer),file);assert(n==strlen(value)&&!memcmp(value,buffer,n)&&!fclose(file));}
static pid_t client(const char *script,const char *ca,const char *mode,const char *revision,unsigned port) {
    pid_t child=fork();assert(child>=0);if(!child){char text[16];snprintf(text,sizeof(text),"%u",port);
        execlp("python3","python3",script,"--port",text,"--mode",mode,"--revision",revision,
#ifdef INTEGRATION_TLS
            "--ca",ca,
#endif
            (char *)NULL);_exit(127);}return child;
}
static void serve(const char *script,const char *ca,const char *mode) {
    assert(session.fd<0&&!workspace);current_mode=mode;
    bool is_static=!strncmp(mode,"private:",8)||!strcmp(mode,"public")||!strcmp(mode,"head");
    bool success=!strcmp(mode,"success")||!strcmp(mode,"pause-2s")||!strcmp(mode,"response-oom")||!strcmp(mode,"publish-late")||
        (!strncmp(mode,"import-",7)&&strcmp(mode,"import-board-busy")&&strcmp(mode,"import-board-invalid"));
    bool import=!strncmp(mode,"import-",7);
    clock_offset=0;publications=workspace_allocations=workspace_frees=request_deletes=purge_receives=handler_calls=close_prepares=pending_at_handler=0;
    async_begins=async_completes=queued_static=foreign_frees=form_erases=chunk_erases=0;
    durable=false;fail_response=strstr(mode,"response-oom")!=NULL;reboot_busy=!strcmp(mode,"reboot-busy")||!strcmp(mode,"import-board-busy");advance_publication=strstr(mode,"publish-late")!=NULL;
    activity_count=0;
    mapped_remove("/spiffs/data/wifi.csv.tmp");mapped_remove("/spiffs/data/wifi.csv.bak");
    text_file("/spiffs/data/wifi.csv"," duplicate \tOLD_PRIVATE_A\n duplicate \tOLD_PRIVATE_B\n");
    text_file("/spiffs/data/playlist.csv","PUBLIC_PLAYLIST\n");text_file("/spiffs/www/theme.css.gz","OLD");
    s_wifi_store.ready=false;assert(network_service_storage_init()==ESP_OK);native_wifi_metadata_t meta;
    assert(network_service_wifi_metadata(&meta)==NATIVE_WIFI_OK&&meta.count==2);
#ifndef TARGET_C3
    s_pending=false;s_reserved_epoch=0;assert(web_reboot_start()==ESP_OK);web_wifi_activate();web_upload_activate();
    if(reboot_busy)web_reboot_request(0);
#else
    s_reboot_pending=false;s_reboot_reserved_epoch=0;atomic_store(&s_reboot_ready,true);
    if(reboot_busy)websocket_service_request_reboot(0);
#endif
    int listener=socket(AF_INET,SOCK_STREAM,0);assert(listener>=0);struct sockaddr_in address={.sin_family=AF_INET,.sin_addr.s_addr=htonl(INADDR_LOOPBACK)};
    assert(!bind(listener,(struct sockaddr *)&address,sizeof(address))&&!listen(listener,1));socklen_t size=sizeof(address);assert(!getsockname(listener,(struct sockaddr *)&address,&size));
    pid_t child=client(script,ca,mode,meta.revision,ntohs(address.sin_port));int fd=accept(listener,NULL,NULL);assert(fd>=0&&!close(listener));
    struct timeval receive_timeout={.tv_sec=1};assert(!setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&receive_timeout,sizeof(receive_timeout)));
    session=(struct sock_db){.fd=fd,.handle=&server,.send_fn=default_send,.recv_fn=default_receive};server.hd_sd_active_count=1;
    if(!strcmp(mode,"foreign")){session.ctx=malloc(32);assert(session.ctx);memset(session.ctx,0x51,32);session.free_ctx=foreign_free;}
#ifdef INTEGRATION_TLS
    assert(integration_tls_open(&server,fd)==ESP_OK&&session.transport_ctx);
#endif
    unsigned opened=file_opens;
    assert(httpd_sess_process(&server,&session)==((is_static||!strcmp(mode,"info"))?ESP_OK:ESP_FAIL));
    assert(!server.hd_req_aux.sd&&!server.hd_req_aux.scratch&&!server.hd_req.aux&&!server.hd_req.handle);
    assert(handler_calls==1&&close_prepares==(unsigned)(!is_static&&strcmp(mode,"info"))&&!workspace&&workspace_frees==workspace_allocations);
#ifdef NEGATIVE_WIFI_RETURN_OK
    assert(request_deletes==1&&purge_receives>0);
#else
    assert(request_deletes==(unsigned)(is_static||!strcmp(mode,"info"))&&!purge_receives);
#endif
    if(is_static){assert(!publications);if(strcmp(mode,"public"))assert(!async_begins&&!queued_static&&file_opens==opened);else assert(async_begins==1&&queued_static==1);}
    else {
#ifdef TARGET_C3
        assert(!s_reboot_reserved_epoch&&s_reboot_pending==(success||reboot_busy)&&activity_count==(unsigned)(success&&!import));
#else
        assert(!s_reserved_epoch&&s_pending==(success||reboot_busy));
#endif
        assert(publications==(unsigned)success);
        if(success){assert(pending_at_handler);expect_file("/spiffs/data/wifi.csv",import?" new \tIMPORT_REQUEST_CANARY\n":" duplicate \tOLD_PRIVATE_B\n new \tNEW_REQUEST_CANARY\n");}
        else expect_file("/spiffs/data/wifi.csv"," duplicate \tOLD_PRIVATE_A\n duplicate \tOLD_PRIVATE_B\n");
        if(import)assert(form_erases==1&&chunk_erases);
        if(!strcmp(mode,"import-board-busy"))expect_file("/spiffs/www/theme.css.gz","OLD");
    }
    if(!strcmp(mode,"pause-2s")||!strcmp(mode,"import-upload-pause"))assert(handler_ended-handler_started>=1900000);
    if(!strcmp(mode,"idle-10s"))assert(handler_ended-handler_started>=10000000&&handler_ended-handler_started<11500000);
    if(!strcmp(mode,"overall-30s"))assert(handler_ended-handler_started>=30000000&&handler_ended-handler_started<31500000);
    httpd_sess_delete(&server,&session);assert(session.fd==-1&&!session.ctx&&!session.transport_ctx&&!server.hd_sd_active_count&&!queued_close_calls);
    if(!strcmp(mode,"foreign"))assert(foreign_frees==1);else assert(!foreign_frees);
    int status;assert(waitpid(child,&status,0)==child&&WIFEXITED(status)&&WEXITSTATUS(status)==0);++cases;
}
int main(int argc,char **argv) {
    assert(argc==4&&mkdtemp(directory));signal(SIGPIPE,SIG_IGN);
    server.config=(httpd_config_t){.max_uri_handlers=7,.max_resp_headers=8,.uri_match_fn=match_uri};
#ifdef INTEGRATION_TLS
    integration_tls_prepare(argv[1]);server.config.close_fn=integration_tls_close;
#endif
    httpd_uri_t routes[]={
        {.uri="/api/native/wifi",.method=HTTP_GET,.handler=observed_handler},
        {.uri="/api/native/wifi",.method=HTTP_POST,.handler=observed_handler},
        {.uri="/upload",.method=HTTP_POST,.handler=observed_handler},
        {.uri="/webboard",.method=HTTP_POST,.handler=observed_handler},
        {.uri="/recovery/wifi",.method=HTTP_POST,.handler=observed_handler},
        {.uri="*",.method=HTTP_ANY,.handler=observed_static}};
    for(size_t i=0;i<sizeof(routes)/sizeof(*routes);++i)assert(httpd_register_uri_handler(&server,&routes[i])==ESP_OK);
    static_activate_boundary();
    const char *modes[]={"info","success","pause-2s","malformed","stale","get-body","foreign","reboot-busy","response-oom","publish-late","idle-10s","overall-30s",
        "import-upload","import-board","import-recovery","import-upload-pause","import-board-response-oom","import-recovery-publish-late","import-board-invalid","import-board-busy",
        "private:/data/wifi.csv","private:/data/wifi.csv.bak?download=1","private:/data/wifi.csv.tmp","private:/data/index.dat","private:/data/playlist.csv.bak","private:/%64ata/wifi.csv","private:/DATA/wifi.csv","private:/data//wifi.csv","private:/www/../data/wifi.csv","head","public"};
    for(size_t i=0;i<sizeof(modes)/sizeof(*modes);++i){
#ifdef NEGATIVE_WIFI_RETURN_OK
        if(strcmp(modes[i],"foreign"))continue;
#endif
        serve(argv[2],argv[3],modes[i]);
    }
    httpd_unregister_all_uri_handlers(&server);
#ifdef INTEGRATION_TLS
    integration_tls_release();
#endif
    mapped_remove("/spiffs/data/wifi.csv");mapped_remove("/spiffs/data/wifi.csv.tmp");mapped_remove("/spiffs/data/wifi.csv.bak");mapped_remove("/spiffs/data/playlist.csv");mapped_remove("/spiffs/www/theme.css.gz");assert(!rmdir(directory));
#ifdef NEGATIVE_WIFI_RETURN_OK
    fprintf(stderr,"NEGATIVE_CONTROL_FAIL: terminal ESP_OK entered actual SDK req_delete=%u body-purge-receives=%u after Wi-Fi rejection\n",request_deletes,purge_receives);
    return 1;
#else
    printf("PASS Wi-Fi wire integration: %u localhost HTTP cases; %u actual SDK session deletions; parser/URI/owner/JSON/import/private guards, pending body, 2s sender pause, real 10s idle/30s total, response OOM, reboot commit and full workspace wipes\n",cases,delete_count);return 0;
#endif
}
