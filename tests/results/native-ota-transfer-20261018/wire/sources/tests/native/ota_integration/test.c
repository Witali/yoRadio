#ifdef INTEGRATION_TLS
void integration_tls_prepare(const char *);
int integration_tls_open(void *,int);
void integration_tls_close(void *,int);
void integration_tls_release(void);
#endif
static pid_t client(const char *script,const char *ca,const char *file,const char *mode,unsigned port) {
    pid_t child=fork();assert(child>=0);
    if(!child){char text[16];snprintf(text,sizeof(text),"%u",port);
#ifdef INTEGRATION_TLS
        execlp("python3","python3",script,"--port",text,"--ca",ca,"--image",file,"--mode",mode,
#else
        (void)ca;execlp("python3","python3",script,"--port",text,"--image",file,"--mode",mode,
#endif
#ifdef TARGET_C3
            "--c3",
#endif
            (char *)NULL);_exit(127);
    }
    return child;
}
static void serve(const char *script,const char *ca,const char *file,const char *mode) {
    assert(session.fd<0&&!workspace&&!handle_owned);
    ota_begins=ota_ends=ota_aborts=ota_verifies=ota_activations=audio_begins=audio_ends=0;
    workspace_allocations=workspace_frees=request_deletes=purge_receives=handler_calls=shutdown_calls=pending_at_handler=0;
    flash_size=0;maintenance=selected=false;fail_response=!strcmp(mode,"response-oom");fail_maintenance=!strcmp(mode,"maintenance-failure");
    // A successful previous case holds maintenance/activity through restart.
    // Each case below models the next boot, not a second upload before reboot.
    activity_count=0;
#ifndef TARGET_C3
    s_pending=false;s_reserved_epoch=0;assert(web_reboot_start()==ESP_OK);web_ota_activate();
    if(!strcmp(mode,"unread-body"))web_reboot_request(0);
#else
    s_reboot_pending=false;s_reboot_reserved_epoch=0;atomic_store(&s_reboot_ready,true);
    if(!strcmp(mode,"unread-body"))websocket_service_request_reboot(0);
#endif
    int listener=socket(AF_INET,SOCK_STREAM,0);assert(listener>=0);
    struct sockaddr_in address={.sin_family=AF_INET,.sin_addr.s_addr=htonl(INADDR_LOOPBACK)};
    assert(!bind(listener,(struct sockaddr *)&address,sizeof(address))&&!listen(listener,1));
    socklen_t size=sizeof(address);assert(!getsockname(listener,(struct sockaddr *)&address,&size));
    pid_t child=client(script,ca,file,mode,ntohs(address.sin_port));
    int fd=accept(listener,NULL,NULL);assert(fd>=0&&!close(listener));
    struct timeval receive_timeout={.tv_sec=1};assert(!setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&receive_timeout,sizeof(receive_timeout)));
    session=(struct sock_db){.fd=fd,.handle=&server,.send_fn=default_send,.recv_fn=default_receive};server.hd_sd_active_count=1;
#ifdef INTEGRATION_TLS
    assert(integration_tls_open(&server,fd)==ESP_OK&&session.transport_ctx);
#endif
    // Real sess_process drives the whole pinned HTTP parser, URI dispatch,
    // handler and error cleanup. ESP_FAIL must skip req_delete/body purge.
    bool info=!strcmp(mode,"info");
    assert(httpd_sess_process(&server,&session)==(info?ESP_OK:ESP_FAIL));
    assert(!server.hd_req_aux.sd&&!server.hd_req_aux.scratch&&!server.hd_req.aux&&!server.hd_req.handle);
    assert(handler_calls==1&&shutdown_calls==(unsigned)!info&&!session.ctx&&!workspace&&workspace_frees==workspace_allocations);
#ifdef NEGATIVE_OTA_RETURN_OK
    assert(!info&&request_deletes==1&&purge_receives>0);
#else
    assert(request_deletes==(unsigned)info&&!purge_receives);
#endif
    assert(!handle_owned);
    bool success=!strcmp(mode,"success")||!strcmp(mode,"pause-2s")||!strcmp(mode,"response-oom");
#ifdef TARGET_C3
    assert(selected==success&&!s_reboot_reserved_epoch&&activity_count==(unsigned)success);
    bool pending=s_reboot_pending;
#else
    assert(selected==success&&!s_reserved_epoch);
    bool pending=s_pending;
#endif
    if(success){assert(ota_begins==1&&ota_ends==1&&ota_verifies==1&&ota_activations==1&&pending&&maintenance&&!audio_ends&&pending_at_handler);}
    else {assert(!maintenance);if(!strcmp(mode,"bad-footer")||!strcmp(mode,"idle-10s"))assert(ota_begins==1&&ota_aborts==1&&audio_ends==1);else assert(!ota_begins);}
    if(!strcmp(mode,"pause-2s"))assert(handler_ended-handler_started>=1900000);
    if(!strcmp(mode,"idle-10s"))assert(handler_ended-handler_started>=NATIVE_OTA_IDLE_US&&handler_ended-handler_started<NATIVE_OTA_IDLE_US+1500000);
    if(!strcmp(mode,"unread-body"))assert(handler_ended-handler_started<1500000);
    httpd_sess_delete(&server,&session);
    assert(session.fd==-1&&!session.ctx&&!session.transport_ctx&&!server.hd_sd_active_count&&!queued_close_calls);
    int status;assert(waitpid(child,&status,0)==child&&WIFEXITED(status)&&WEXITSTATUS(status)==0);++cases;
}
int main(int argc,char **argv) {
    assert(argc==5);signal(SIGPIPE,SIG_IGN);
    strcpy(current_app.project_name,"native-radio");strcpy(current_app.version,"integration");
    for(size_t i=0;i<sizeof(image);++i)image[i]=(uint8_t)(i*37U);
    esp_image_header_t h={.magic=ESP_IMAGE_HEADER_MAGIC,.segment_count=1,.hash_appended=1,
#ifdef TARGET_C3
        .chip_id=ESP_CHIP_ID_ESP32C3
#else
        .chip_id=ESP_CHIP_ID_ESP32
#endif
    };
    esp_image_segment_header_t segment={.load_addr=0x3f400020,.data_len=sizeof(esp_app_desc_t)};
    current_app.magic_word=ESP_APP_DESC_MAGIC_WORD;
    memcpy(image,&h,sizeof(h));memcpy(image+sizeof(h),&segment,sizeof(segment));memcpy(image+sizeof(h)+sizeof(segment),&current_app,sizeof(current_app));
    FILE *file=fopen(argv[4],"wb");assert(file&&fwrite(image,1,sizeof(image),file)==sizeof(image)&&!fclose(file));
    server.config=(httpd_config_t){.max_uri_handlers=2,.max_resp_headers=8};
#ifdef INTEGRATION_TLS
    integration_tls_prepare(argv[1]);server.config.close_fn=integration_tls_close;
#endif
    httpd_uri_t route={.uri="/update",.method=HTTP_POST,.handler=observed_handler};assert(httpd_register_uri_handler(&server,&route)==ESP_OK);
    route=(httpd_uri_t){.uri="/api/native/ota",.method=HTTP_GET,.handler=observed_info};assert(httpd_register_uri_handler(&server,&route)==ESP_OK);
    const char *modes[]={"info","success","pause-2s","x-boundary","duplicate-boundary","wrong-project","bad-footer","maintenance-failure","unread-body","response-oom","idle-10s"};
    for(size_t i=0;i<sizeof(modes)/sizeof(*modes);++i){
#ifdef NEGATIVE_OTA_RETURN_OK
        if(strcmp(modes[i],"unread-body"))continue;
#endif
        serve(argv[2],argv[3],argv[4],modes[i]);
    }
    httpd_unregister_all_uri_handlers(&server);
#ifdef INTEGRATION_TLS
    integration_tls_release();
#endif
#ifdef NEGATIVE_OTA_RETURN_OK
    fprintf(stderr,"NEGATIVE_CONTROL_FAIL: terminal ESP_OK entered actual SDK req_delete=%u body-purge-receives=%u after OTA rejection\n",request_deletes,purge_receives);
    return 1;
#endif
    printf("PASS OTA wire integration: %u localhost HTTP cases; %u actual SDK session deletions; whole parser/URI/handler/ESP_FAIL/no-purge and workspace singlefree\n",cases,delete_count);
    return 0;
}
