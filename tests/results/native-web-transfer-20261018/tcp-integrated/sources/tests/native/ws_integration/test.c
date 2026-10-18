/* Each connection is a real 127.0.0.1 TCP socket. The foreground adapter runs
 * SDK sess_process directly; FreeRTOS/select main-loop scheduling is a seam. */
static int peer=-1;
static const char handshake_request[]=
    "GET /ws HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
    "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n\r\n";

static void client_write(const void *data,size_t size) {
    const uint8_t *p=data;
    while(size){ssize_t n=send(peer,p,size,MSG_NOSIGNAL);assert(n>0);p+=n;size-=(size_t)n;}
}
static void client_read(void *data,size_t size) {
    uint8_t *p=data;
    while(size){ssize_t n=recv(peer,p,size,0);assert(n>0);p+=n;size-=(size_t)n;}
}
static void no_output(void) {
    uint8_t data;ssize_t n=recv(peer,&data,1,MSG_DONTWAIT);
    assert(n<0&&(errno==EAGAIN||errno==EWOULDBLOCK));
}
static size_t packet(uint8_t *out,uint8_t opcode,bool fin,const void *data,size_t size) {
    assert(size<65536);size_t n=0;out[n++]=opcode|(fin?128:0);
    if(size<126)out[n++]=128|(uint8_t)size;
    else{out[n++]=128|126;out[n++]=(uint8_t)(size>>8);out[n++]=(uint8_t)size;}
    static const uint8_t key[]={0x13,0x37,0x00,0xff};
    memcpy(out+n,key,4);n+=4;
    for(size_t i=0;i<size;++i)out[n++]=((const uint8_t *)data)[i]^key[i%4];return n;
}
static void client_frame(uint8_t op,bool fin,const void *data,size_t size) {
    uint8_t wire[1024];size_t n=packet(wire,op,fin,data,size);client_write(wire,n);
}
static void expect_frame(uint8_t op,const void *data,size_t size) {
    uint8_t first[2];client_read(first,2);assert(first[0]==(128|op)&&first[1]==size);
    uint8_t body[125];assert(size<=sizeof(body));client_read(body,size);assert(!size||!memcmp(body,data,size));
}
static void expect_close(unsigned code) {
    uint8_t payload[]={(uint8_t)(code>>8),(uint8_t)code};expect_frame(8,payload,2);
}
static void close_session(void) {
    if(session.fd>=0)httpd_sess_delete(&server,&session);
    assert(session.fd==-1&&!session.ctx&&!session.transport_ctx);
    for(size_t i=0;i<sizeof(s_clients)/sizeof(*s_clients);++i)
        assert(!s_clients[i].used&&!s_clients[i].message.active);
    assert(!activity_count&&!server.hd_sd_active_count&&!queued_close_calls);
#ifdef TARGET_C3
    assert(!atomic_load(&s_fragmented_clients));
#endif
    if(peer>=0){assert(close(peer)==0);peer=-1;}
}
static int connect_session(void) {
    assert(peer<0&&session.fd<0&&!server.hd_req_aux.sd);
    int listener=socket(AF_INET,SOCK_STREAM,0);assert(listener>=0);
    struct sockaddr_in address={.sin_family=AF_INET,.sin_addr.s_addr=htonl(INADDR_LOOPBACK)};
    assert(bind(listener,(struct sockaddr *)&address,sizeof(address))==0&&listen(listener,1)==0);
    socklen_t len=sizeof(address);assert(getsockname(listener,(struct sockaddr *)&address,&len)==0);
    peer=socket(AF_INET,SOCK_STREAM,0);assert(peer>=0);
    assert(connect(peer,(struct sockaddr *)&address,sizeof(address))==0);
    int fd=accept(listener,NULL,NULL);assert(fd>=0&&close(listener)==0);
    int enabled=1;assert(setsockopt(peer,IPPROTO_TCP,TCP_NODELAY,&enabled,sizeof(enabled))==0);
    assert(setsockopt(fd,IPPROTO_TCP,TCP_NODELAY,&enabled,sizeof(enabled))==0);
    struct timeval timeout={.tv_sec=2};
    assert(setsockopt(peer,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout))==0);
    assert(setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout))==0);
    session=(struct sock_db){.fd=fd,.handle=&server,.send_fn=default_send,.recv_fn=default_receive};
    server.hd_sd_active_count=1;command_calls=0;command_size=0;command_bytes[0]=0;
    response_status[0]=response_version[0]=0;return fd;
}
static bool process(void) {
    assert(session.fd>=0&&!server.hd_req_aux.sd);
    int result=httpd_sess_process(&server,&session);
    /* Actual req_new cleans error paths; actual req_delete cleans success
     * paths, including ws_close. Its ra->sd contract is established by new. */
    assert(!server.hd_req_aux.sd&&!server.hd_req_aux.scratch);
    assert(!server.hd_req.handle&&!server.hd_req.aux);
    if(result!=ESP_OK)httpd_sess_delete(&server,&session);
    return result==ESP_OK;
}
static void upgrade_with(const uint8_t *first,size_t size) {
    connect_session();uint8_t together[2048];size_t header=sizeof(handshake_request)-1;
    memcpy(together,handshake_request,header);if(size)memcpy(together+header,first,size);
    client_write(together,header+size);assert(process());assert(session.ws_handshake_done&&session.ws_control_frames);
    assert(session.ctx&&session.free_ctx&&session.ws_handler==websocket_handler);
    char response[512];size_t n=0;
    do{assert(n<sizeof(response)-1);client_read(response+n,1);response[++n]=0;}while(!strstr(response,"\r\n\r\n"));
    assert(strstr(response,"HTTP/1.1 101 Switching Protocols\r\n"));
    assert(strstr(response,"Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n"));
    assert(!strstr(response,"Sec-WebSocket-Extensions:")&&!strstr(response,"Sec-WebSocket-Protocol:"));
    if(size&&io_chunk>=128)assert(session.pending_len); // actual parser pause/unrecv preserved next frame
}
static void upgrade(void) {upgrade_with(NULL,0);}
static void expect_command(const void *data,size_t size) {
    assert(command_calls==1&&command_size==size&&!memcmp(command_bytes,data,size));
}
static void invalid_message(uint8_t op,bool fin,const void *data,size_t size,unsigned code) {
    upgrade();client_frame(op,fin,data,size);assert(!process());expect_close(code);assert(!command_calls);close_session();++cases;
}
static void same_buffer_and_controls(void) {
    uint8_t first[32];size_t n=packet(first,1,true,"ping",4);upgrade_with(first,n);
    assert(process());expect_command("ping",4);no_output();
    client_frame(9,true,"",0);client_frame(10,true,"ignored",7);client_frame(1,true,"next",4);
    assert(process());expect_frame(10,NULL,0);assert(process());assert(process());
    assert(command_calls==2&&!strcmp((char *)command_bytes,"next"));no_output();close_session();++cases;
}
static void fragment_and_controls(void) {
    upgrade();client_frame(1,false,"pi",2);assert(process());assert(!command_calls);
    client_frame(9,true,"\x00\xff",2);assert(process());expect_frame(10,"\x00\xff",2);
    client_frame(10,true,"pong",4);assert(process());assert(!command_calls);
    client_frame(0,false,"",0);assert(process());assert(!command_calls);
    client_frame(0,true,"ng",2);assert(process());expect_command("ping",4);no_output();close_session();++cases;
}
static void utf8_and_limits(void) {
    upgrade();client_frame(1,false,"A\xe2",2);assert(process());client_frame(0,false,"\x82",1);assert(process());
    client_frame(0,true,"\xacZ",2);assert(process());expect_command("A\xe2\x82\xacZ",5);close_session();++cases;
    invalid_message(1,true,"\xc0\xaf",2,1007);
    invalid_message(1,true,"\xed\xa0\x80",3,1007);
    upgrade();client_frame(1,false,"\xf0\x9f",2);assert(process());client_frame(0,true,"",0);
    assert(!process());expect_close(1007);close_session();++cases;
    invalid_message(0,true,"x",1,1002);
    upgrade();client_frame(1,false,"p",1);assert(process());client_frame(1,true,"x",1);
    assert(!process());expect_close(1002);close_session();++cases;
    invalid_message(2,true,"\xff",1,1003);
    uint8_t large[300];memset(large,'x',sizeof(large));invalid_message(1,true,large,sizeof(large),1009);
    /* Accumulated fragments fit frame limits but exceed message storage. */
    upgrade();
#ifdef TARGET_C3
    size_t piece=128;
#else
    size_t piece=49;
#endif
    client_frame(1,false,large,piece);assert(process());client_frame(0,true,large,piece);
    assert(!process());expect_close(1009);close_session();++cases;
}
static void accepted_boundaries(void) {
    uint8_t text[255];memset(text,'x',sizeof(text));
#ifdef TARGET_C3
    size_t limit=255;
#else
    size_t limit=96;
#endif
    upgrade();client_frame(1,true,text,limit);assert(process());expect_command(text,limit);close_session();++cases;
    upgrade();client_frame(1,false,text,limit-1);assert(process());client_frame(0,true,text,1);
    assert(process());expect_command(text,limit);close_session();++cases;
    upgrade();uint8_t ping[125];for(size_t i=0;i<sizeof(ping);++i)ping[i]=(uint8_t)i;
    client_frame(9,true,ping,sizeof(ping));assert(process());expect_frame(10,ping,sizeof(ping));
    client_frame(1,true,"after-ping",10);assert(process());expect_command("after-ping",10);close_session();++cases;
    /* Empty text is legal RFC data. The two services have distinct ordinary
     * command UX: CYD returns a fixed error, C3 consumes it quietly. */
    upgrade();client_frame(1,true,NULL,0);assert(process());assert(!command_calls);
#ifndef TARGET_C3
    static const char empty[]="{\"commandError\":\"Empty command\"}";
    expect_frame(1,empty,sizeof(empty)-1);
#else
    no_output();
#endif
    client_frame(1,true,"next",4);assert(process());expect_command("next",4);close_session();++cases;
    upgrade();client_frame(1,true,"x\0y",3);assert(process());assert(!command_calls);
#ifdef TARGET_C3
    static const char nul[]="{\"commandError\":\"Command contains NUL\"}";
#else
    static const char nul[]="{\"commandError\":\"Invalid command\"}";
#endif
    expect_frame(1,nul,sizeof(nul)-1);close_session();++cases;
}
static void close_matrix(void) {
    const uint8_t good[]={0x03,0xe8,'b','y','e'};upgrade();client_frame(8,true,good,sizeof(good));
    assert(!process());expect_frame(8,good,sizeof(good));assert(!command_calls);close_session();++cases;
    upgrade();client_frame(8,true,NULL,0);assert(!process());expect_frame(8,NULL,0);close_session();++cases;
    invalid_message(8,true,"x",1,1002);
    invalid_message(8,true,"\x03\xed",2,1002); // 1005 is reserved, never on wire
    invalid_message(8,true,"\x03\xe8\xff",3,1007);
    /* Data queued after Close must never reach the application. */
    upgrade();client_frame(8,true,NULL,0);client_frame(1,true,"forbidden",9);
    assert(!process());expect_frame(8,NULL,0);assert(!command_calls);close_session();++cases;
}
static void strict_frame_matrix(void) {
    static const uint8_t bad[][12]={
        {0xc1,0x80,1,2,3,4}, // RSV1 without extension
        {0x83,0x80,1,2,3,4}, // reserved opcode
        {0x09,0x80,1,2,3,4}, // fragmented Ping
        {0x81,0}, // client frame unmasked
        {0x81,0xfe,0,1,1,2,3,4,'x'^1}, // nonminimal 16-bit length
        {0x81,0xff,0,0,0,0,0,0,0,1,1,2}, // nonminimal 64-bit
        {0x81,0xff,0x80,0,0,0,0,0,0,0}, // forbidden 64-bit MSB
        {0x89,0xfe,0,126,1,2,3,4}, // oversized control
    };
    const size_t lengths[]={6,6,6,2,9,12,10,8};
    for(size_t i=0;i<sizeof(lengths)/sizeof(*lengths);++i){
        upgrade();client_write(bad[i],lengths[i]);assert(!process());expect_close(1002);assert(!command_calls);close_session();++cases;
    }
}
static void reuse_and_error_cleanup(void) {
    upgrade();int old=session.fd;client_frame(1,false,"old",3);assert(process());assert(session.ctx);
    client_frame(8,true,NULL,0);assert(!process());expect_frame(8,NULL,0);close_session();
    upgrade();assert(session.fd==old);client_frame(1,true,"new",3);assert(process());expect_command("new",3);
    assert(!queued_close_calls);close_session();++cases;
    /* Network truncation reaches req_new's actual error cleanup and frees the
     * session before descriptor reuse, rather than calling req_delete twice. */
    upgrade();client_write("\x81",1);assert(shutdown(peer,SHUT_WR)==0);assert(!process());close_session();++cases;
}
static bool offered_request(const char *extra) {
    connect_session();char request[1024];size_t prefix=sizeof(handshake_request)-3;
    memcpy(request,handshake_request,prefix);strcpy(request+prefix,extra);strcat(request,"\r\n");
    client_write(request,strlen(request));return process();
}
static void handshake_errors(void) {
    const char *bad[]={"Sec-WebSocket-Extensions: private; p=\"two words\"\r\n",
        "Sec-WebSocket-Protocol: chat, chat\r\n","Content-Length: \r\n","Content-Length: 4294967296\r\n"};
    for(size_t i=0;i<sizeof(bad)/sizeof(*bad);++i){
        assert(!offered_request(bad[i]));assert(!command_calls);assert(atoi(response_status)==(i==3?413:400));
        close_session();++cases;
    }
}
static void ordinary_http_requests(void) {
    const char *extra[]={"","Connection: Upgrade\r\n","Upgrade: h2c\r\nConnection: Upgrade\r\n",
        "Upgrade: websocket\r\n","Upgrade: websocket\r\nConnection: keep-alive\r\n"};
    for(size_t i=0;i<sizeof(extra)/sizeof(*extra);++i){
        connect_session();char request[512];int n=snprintf(request,sizeof(request),
            "GET /ws HTTP/1.1\r\nHost: localhost\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n%s\r\n",extra[i]);
        assert(n>0&&(size_t)n<sizeof(request));client_write(request,(size_t)n);(void)process();
        assert(atoi(response_status)==400&&!command_calls&&!session.ctx&&!session.ws_handshake_done);
        /* The actual HTTP parser requires both Upgrade and Connection flags
         * before attempting an upgrade. Missing/wrong tokens reach HTTP400
         * without ever reserving a WS context. */
        assert(!server.hd_req.sess_ctx);close_session();++cases;
    }
}
int main(int argc,char **argv) {
    server.config=(httpd_config_t){.max_uri_handlers=2,.max_resp_headers=2};
    assert(websocket_service_register(&server,&state)==ESP_OK);
#ifndef TARGET_C3
    atomic_store(&s_running,true);
#endif
    if(argc>1&&!strcmp(argv[1],"ordinary-http")){
        ordinary_http_requests();httpd_unregister_all_uri_handlers(&server);return 0;
    }
    if(argc>1){
        const char *extra=!strcmp(argv[1],"extensions")?"Sec-WebSocket-Extensions: private; p=\"two words\"\r\n":
            !strcmp(argv[1],"protocol")?"Sec-WebSocket-Protocol: chat, chat\r\n":"Content-Length: \r\n";
        bool wrongly_accepted=offered_request(extra);close_session();httpd_unregister_all_uri_handlers(&server);
        if(wrongly_accepted){fprintf(stderr,"NEGATIVE_CONTROL_FAIL: original SDK accepted %s through actual application route\n",argv[1]);return 1;}
        return 0;
    }
    const size_t chunks[]={1,3,128,4096};
    for(size_t i=0;i<sizeof(chunks)/sizeof(*chunks);++i){
        io_chunk=chunks[i];same_buffer_and_controls();fragment_and_controls();utf8_and_limits();
        accepted_boundaries();close_matrix();strict_frame_matrix();reuse_and_error_cleanup();handshake_errors();ordinary_http_requests();
    }
    httpd_unregister_all_uri_handlers(&server);
    assert(!queued_close_calls&&!activity_count&&delete_count);
    printf("PASS %u integrated localhost TCP cases; %u real SDK session deletions; transport calls send=%u recv=%u\n",
        cases,delete_count,send_calls,recv_calls);return 0;
}
