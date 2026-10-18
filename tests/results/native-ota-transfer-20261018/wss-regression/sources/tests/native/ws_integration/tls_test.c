#include <signal.h>
#include <sys/wait.h>
void integration_tls_prepare(const char *);
int integration_tls_open(void *,int);
void integration_tls_close(void *,int);
void integration_tls_release(void);

static pid_t ssl_client(const char *script,const char *ca,const char *mode,unsigned port) {
    pid_t child=fork();assert(child>=0);
    if(!child){char text[16];snprintf(text,sizeof(text),"%u",port);
        execlp("python3","python3",script,"--port",text,"--ca",ca,"--mode",mode,(char *)NULL);_exit(127);}
    return child;
}
static void serve_tls_case(const char *script,const char *ca,const char *mode) {
    int listener=socket(AF_INET,SOCK_STREAM,0);assert(listener>=0);
    struct sockaddr_in address={.sin_family=AF_INET,.sin_addr.s_addr=htonl(INADDR_LOOPBACK)};
    assert(!bind(listener,(struct sockaddr *)&address,sizeof(address))&&!listen(listener,1));
    socklen_t length=sizeof(address);assert(!getsockname(listener,(struct sockaddr *)&address,&length));
    pid_t child=ssl_client(script,ca,mode,ntohs(address.sin_port));
    int fd=accept(listener,NULL,NULL);assert(fd>=0&&!close(listener));
    session=(struct sock_db){.fd=fd,.handle=&server};server.hd_sd_active_count=1;
    command_calls=0;command_bytes[0]=0;command_size=0;response_status[0]=response_version[0]=0;
    assert(integration_tls_open(&server,fd)==ESP_OK);
    assert(session.transport_ctx&&session.free_transport_ctx&&session.send_fn&&session.recv_fn&&session.pending_fn);
    bool upgraded=false;unsigned requests=0;
    while(true){
        assert(!server.hd_req_aux.sd&&!server.hd_req.handle);int result=httpd_sess_process(&server,&session);++requests;
        assert(!server.hd_req_aux.sd&&!server.hd_req_aux.scratch&&!server.hd_req.aux&&!server.hd_req.handle);
        if(result!=ESP_OK||(!session.ws_handshake_done&&atoi(response_status)==400))break;
        assert(session.ws_handshake_done&&session.ctx&&session.ws_control_frames);
        if(!upgraded){upgraded=true;assert(session.send_fn!=NULL&&session.recv_fn!=NULL);}
        assert(requests<16);
    }
    bool invalid_handshake=!strcmp(mode,"extensions")||!strcmp(mode,"protocol")||!strcmp(mode,"empty-length")||!strncmp(mode,"http-",5);
    assert(upgraded!=invalid_handshake);
    if(invalid_handshake)assert(!command_calls&&atoi(response_status)==400&&requests==1);
    else if(!strcmp(mode,"fragment-ping"))assert(command_calls==1&&command_size==4&&!memcmp(command_bytes,"ping",4)&&requests==6);
    else if(!strcmp(mode,"utf8-fragments"))assert(command_calls==1&&command_size==5&&!memcmp(command_bytes,"A\xe2\x82\xacZ",5)&&requests==7);
    else assert(!command_calls);
    httpd_sess_delete(&server,&session);
    assert(session.fd==-1&&!session.ctx&&!session.transport_ctx&&!server.hd_sd_active_count&&!queued_close_calls&&!activity_count);
    for(size_t i=0;i<sizeof(s_clients)/sizeof(*s_clients);++i)assert(!s_clients[i].used&&!s_clients[i].message.active);
#ifdef TARGET_C3
    assert(!atomic_load(&s_fragmented_clients));
#endif
    int status;assert(waitpid(child,&status,0)==child&&WIFEXITED(status)&&WEXITSTATUS(status)==0);++cases;
}
int main(int argc,char **argv) {
    assert(argc==4);signal(SIGPIPE,SIG_IGN);
    integration_tls_prepare(argv[1]);
    server.config=(httpd_config_t){.max_uri_handlers=2,.max_resp_headers=2,.close_fn=integration_tls_close};
    assert(websocket_service_register(&server,&state)==ESP_OK);
#ifndef TARGET_C3
    atomic_store(&s_running,true);
#endif
    const char *modes[]={"fragment-ping","utf8-fragments","invalid-utf8","rsv","close-reason",
        "close-tail","extensions","protocol","empty-length","http-plain","http-connection",
        "http-other","http-upgrade-only","http-keepalive"};
    for(size_t i=0;i<sizeof(modes)/sizeof(*modes);++i)serve_tls_case(argv[2],argv[3],modes[i]);
    httpd_unregister_all_uri_handlers(&server);integration_tls_release();
    printf("PASS integrated WSS: %u trusted localhost TLS1.2 cases; %u actual HTTPD/TLS session deletions; actual PSA WS accept\n",cases,delete_count);
    return 0;
}
