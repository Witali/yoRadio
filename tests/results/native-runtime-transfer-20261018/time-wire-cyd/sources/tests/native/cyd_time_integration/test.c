static pid_t client(const char *script,const char *ca,const char *mode,unsigned port) {
    pid_t child=fork();assert(child>=0);
    if(!child){char value[16];snprintf(value,sizeof(value),"%u",port);
        execlp("python3","python3",script,"--port",value,"--mode",mode,"--ca",ca,(char *)NULL);_exit(127);}
    return child;
}
static void serve(const char *script,const char *ca,const char *mode,bool tls) {
    assert(session.fd<0&&!server.hd_sd_active_count);
    handler_calls=request_deletes=purge_calls=purge_positive_bytes=prepare_closes=save_calls=snapshot_calls=0;
    snapshot_available=strcmp(mode,"unavailable")!=0;fail_commit=!strcmp(mode,"commit-failure");
    snapshot_fields=(time_snapshot_t){.available=true,.last_sync_age_ms=-1};
    if(!strcmp(mode,"get-valid"))snapshot_fields=(time_snapshot_t){.available=true,.clock_valid=true,.network_ready=true,
        .synchronized_this_boot=true,.utc_epoch=1704067200,.last_sync_epoch=1704067100,.last_sync_age_ms=5000,
        .local_time={.tm_year=123,.tm_mon=11,.tm_mday=31,.tm_hour=23,.tm_min=30},.last_apply_error=ESP_ERR_TIMEOUT};
    time_settings_t before;uint32_t revision;assert(time_settings_snapshot(&before,&revision));
    uint8_t old_record[82];memcpy(old_record,stored_record,sizeof(old_record));unsigned commits=nvs_commits;
    int listener=socket(AF_INET,SOCK_STREAM,0);assert(listener>=0);
    struct sockaddr_in address={.sin_family=AF_INET,.sin_addr.s_addr=htonl(INADDR_LOOPBACK)};
    assert(!bind(listener,(struct sockaddr *)&address,sizeof(address))&&!listen(listener,1));
    socklen_t size=sizeof(address);assert(!getsockname(listener,(struct sockaddr *)&address,&size));
    pid_t child=client(script,ca,mode,ntohs(address.sin_port));
    int fd=accept(listener,NULL,NULL);assert(fd>=0&&!close(listener));
    struct timeval timeout={.tv_sec=2};assert(!setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout)));
    session=(struct sock_db){.fd=fd,.handle=&server,.send_fn=httpd_default_send,.recv_fn=httpd_default_recv};server.hd_sd_active_count=1;
    assert(integration_transport_open(&server,fd)==ESP_OK);
    assert((session.transport_ctx!=NULL)==tls);
    bool body=!strncmp(mode,"body-",5),parser_reject=!strcmp(mode,"uri-limit")||!strcmp(mode,"wrong-route")||!strcmp(mode,"wrong-method");
    unsigned requests=!strcmp(mode,"post-pending")?2U:1U;
    for(unsigned i=0;i<requests;i++){
        esp_err_t expected=body||parser_reject?ESP_FAIL:ESP_OK;
#ifdef NEGATIVE_TIME_RETURN_OK
        expected=ESP_OK;
#endif
        assert(httpd_sess_process(&server,&session)==expected);
        assert(!server.hd_req_aux.sd&&!server.hd_req_aux.scratch&&!server.hd_req.aux&&!server.hd_req.handle);
    }
    assert(handler_calls==(parser_reject?0U:requests));
#ifdef NEGATIVE_TIME_RETURN_OK
    assert(body&&request_deletes==1&&purge_calls==1&&purge_positive_bytes==1);
#else
    assert(request_deletes==(body||parser_reject?0U:requests)&&!purge_calls&&!purge_positive_bytes);
#endif
    assert(prepare_closes==(unsigned)body&&!queued_close_calls&&!session.ctx);
    bool saved=!strcmp(mode,"post-pending")||!strcmp(mode,"post-two");
    time_settings_t after;uint32_t next;assert(time_settings_snapshot(&after,&next));
    if(saved){assert(save_calls==1&&nvs_commits==commits+1&&next==revision+1&&after.utc_offset_minutes==345&&stored_size==82);}
    else{assert(next==revision&&!memcmp(&before,&after,sizeof(after))&&!memcmp(old_record,stored_record,sizeof(old_record)));}
    if(!strcmp(mode,"commit-failure"))assert(save_calls==1&&nvs_commits==commits+1);
    else if(!saved)assert(!save_calls&&nvs_commits==commits);
    if(body)assert(handler_ended-handler_started<1500000);
    httpd_sess_delete(&server,&session);
    assert(session.fd==-1&&!session.ctx&&!session.transport_ctx&&!server.hd_sd_active_count&&fcntl(fd,F_GETFD)==-1&&errno==EBADF);
    int result;assert(waitpid(child,&result,0)==child&&WIFEXITED(result)&&WEXITSTATUS(result)==0);
    ++cases;printf("CASE %s: requests=%u handler=%u req_delete=%u purge_calls=%u purge_bytes=%u commits=%u\n",
        mode,requests,handler_calls,request_deletes,purge_calls,purge_positive_bytes,nvs_commits-commits);
}
int main(int argc,char **argv) {
    assert(argc==5);setvbuf(stdout,NULL,_IONBF,0);signal(SIGPIPE,SIG_IGN);bool tls=!strcmp(argv[4],"tls");
    assert(tls||!strcmp(argv[4],"plain"));assert(time_settings_init()==ESP_OK);
    integration_transport_prepare(argv[1],tls);
    server.config=(httpd_config_t){.max_uri_handlers=2,.max_resp_headers=8,.close_fn=tls?integration_transport_close:NULL};
    httpd_uri_t route={.uri="/api/native/time",.method=HTTP_GET,.handler=observed_handler};
    assert(httpd_register_uri_handler(&server,&route)==ESP_OK);route.method=HTTP_POST;assert(httpd_register_uri_handler(&server,&route)==ESP_OK);
    const char *modes[]={"get-null","get-valid","post-pending","post-two","missing","duplicate","encoded-duplicate","nul","bad-percent",
        "unknown","numeric","bounds","host-limit","get-query","uri-limit","wrong-route","wrong-method","commit-failure","unavailable",
        "body-get","body-post","body-unread-large","body-slow"};
    for(unsigned i=0;i<sizeof(modes)/sizeof(*modes);i++){
#ifdef NEGATIVE_TIME_RETURN_OK
        if(strcmp(modes[i],"body-post"))continue;
#endif
        serve(argv[2],tls?argv[3]:"",modes[i],tls);
    }
    httpd_unregister_all_uri_handlers(&server);integration_transport_release();vSemaphoreDelete(setting_mutex);
#ifdef NEGATIVE_TIME_RETURN_OK
    fprintf(stderr,"NEGATIVE_CONTROL_FAIL: terminal ESP_OK caused actual SDK req_delete=%u purge_calls=%u purge_bytes=%u after time body rejection\n",request_deletes,purge_calls,purge_positive_bytes);
    return 1;
#endif
    assert(cases==23&&delete_count==23);
    printf("PASS CYD time wire: %u actual TCP/HTTPD/parser/session/native transport cases; plaintext or CA+hostname verified TLS; no SDK body purge\n",cases);return 0;
}
