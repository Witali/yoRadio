// The production and SDK .inc files precede this file in the generated unit.
typedef struct { httpd_work_fn_t function; void *argument; } queued_t;
static struct sock_db sessions[32];
static queued_t queue[32];
static unsigned queue_count, shutdown_count, command_count, activity_count, http_errors;
static unsigned send_calls, recv_calls, select_calls, yields, cases;
static unsigned send_chunk, recv_chunk, send_advance, recv_advance;
static int send_script[32], recv_script[32], wait_script[32];
static size_t send_script_len, recv_script_len, wait_script_len;
static size_t send_script_at, recv_script_at, wait_script_at;
static uint8_t received_wire[131200], transmitted_wire[262400];
static size_t received_size, received_at, transmitted_size;
static int64_t now_us;
static bool queue_failure, context_failure, send_override_failure, recv_override_failure;
static bool registration_failure, task_failure, awake = true;
static bool transport_write_needs_read, transport_read_needs_write;
static bool last_wait_writable, last_shutdown_graceful;
static httpd_uri_t route;
static unsigned delivery_incarnation[32], delivery_count;
static char command_text[256];
static int foreign_context;

static int default_send(httpd_handle_t server, int socket, const char *data, size_t size, int flags) {
    (void)server;
    return (int)lwip_send(socket, data, size, flags);
}
static int default_receive(httpd_handle_t server, int socket, char *data, size_t size, int flags) {
    (void)server;
    return (int)lwip_recv(socket, data, size, flags);
}
int64_t esp_timer_get_time(void) { return now_us; }
void vTaskDelay(unsigned ticks) { ++yields; now_us += ticks * 1000; }
bool deep_sleep_clock_begin_activity(void) { if (awake) ++activity_count; return awake; }
void deep_sleep_clock_end_activity(void) { assert(activity_count); --activity_count; }
static void format_status(char *text, size_t size) { snprintf(text, size, "status"); }
static void status_task(void *argument) { (void)argument; }
static void handle_command(httpd_req_t *request, char *text) {
    (void)request; ++command_count; snprintf(command_text, sizeof(command_text), "%s", text);
}
int xTaskCreate(void (*function)(void *), const char *name, unsigned stack, void *arg, unsigned priority, void *handle) {
    assert(function == status_task && !strcmp(name,"websocket_status"));
    assert(stack == BOARD_TASK_STACK_WEBSOCKET_STATUS && !arg && priority == 2 && !handle);
    return task_failure ? 0 : pdPASS;
}
unsigned xEventGroupSetBits(EventGroupHandle_t event, unsigned bits) { (void)event; return bits; }
struct sock_db *httpd_sess_get(httpd_handle_t server, int socket) {
    assert(server == s_server);
    return socket >= 0 && socket < 32 && sessions[socket].live ? &sessions[socket] : NULL;
}
void *httpd_sess_get_ctx(httpd_handle_t server, int socket) {
    struct sock_db *session = httpd_sess_get(server, socket);
    return session ? session->context : NULL;
}
void httpd_sess_set_ctx(httpd_handle_t server, int socket, void *context, httpd_free_ctx_fn_t free_context) {
    struct sock_db *session = httpd_sess_get(server, socket);
    assert(session);
    if (context_failure) return;
    if (session->context != context && session->free_context) session->free_context(session->context);
    session->context = context; session->free_context = free_context;
}
esp_err_t httpd_sess_set_send_override(httpd_handle_t server, int socket, httpd_send_func_t function) {
    struct sock_db *session = httpd_sess_get(server,socket); assert(session);
    if (send_override_failure) return ESP_FAIL;
    session->send_fn=function; return ESP_OK;
}
esp_err_t httpd_sess_set_recv_override(httpd_handle_t server, int socket, httpd_recv_func_t function) {
    struct sock_db *session = httpd_sess_get(server,socket); assert(session);
    if (recv_override_failure) return ESP_FAIL;
    session->recv_fn=function; return ESP_OK;
}
httpd_ws_client_info_t httpd_ws_get_fd_info(httpd_handle_t server,int socket) {
    struct sock_db *session = httpd_sess_get(server,socket);
    if (!session) return HTTPD_WS_CLIENT_INVALID;
    return session->ws_handshake_done && !session->ws_close ? HTTPD_WS_CLIENT_WEBSOCKET : HTTPD_WS_CLIENT_HTTP;
}
int httpd_req_to_sockfd(httpd_req_t *request) { return request->aux->sd->fd; }
esp_err_t httpd_resp_send_err(httpd_req_t *request, int status, const char *message) {
    assert(status == HTTPD_400_BAD_REQUEST && strstr(message, "upgrade"));
    assert(!sessions[httpd_req_to_sockfd(request)].context && !activity_count);
    ++http_errors;
    return ESP_OK;
}
esp_err_t httpd_register_uri_handler(httpd_handle_t server, const httpd_uri_t *registered) {
    assert(server == s_server); if (registration_failure) return ESP_FAIL;
    route = *registered; return ESP_OK;
}
esp_err_t httpd_get_client_list(httpd_handle_t server,size_t *count,int *list) {
    assert(server == s_server); size_t capacity = *count; *count=0;
    for (int i=0;i<32;++i) if (sessions[i].live) { assert(*count<capacity); list[(*count)++]=i; }
    return ESP_OK;
}
esp_err_t httpd_queue_work(httpd_handle_t server,httpd_work_fn_t function,void *argument) {
    assert(server == s_server); if (queue_failure) return ESP_FAIL;
    assert(queue_count<32); queue[queue_count++] = (queued_t){function,argument}; return ESP_OK;
}
static void close_work(void *argument) {
    int socket = (int)(intptr_t)argument;
    // The dangerous old API queues only this fd; a later callback can close a
    // replacement. New code must never request it.
    (void)shutdown(socket,SHUT_RDWR);
}
esp_err_t httpd_sess_trigger_close(httpd_handle_t server,int socket) {
    return httpd_queue_work(server,close_work,(void *)(intptr_t)socket);
}
static void run_queue(void) {
    while (queue_count) {
        queued_t work=queue[0]; memmove(queue,queue+1,--queue_count*sizeof(*queue));
        work.function(work.argument);
    }
}
int shutdown(int socket,int how) {
    assert(how == SHUT_RDWR && socket >= 0 && socket < 32 && sessions[socket].live);
    ++shutdown_count; return 0;
}
ssize_t native_web_transport_send(httpd_handle_t server,int socket,const void *data,size_t size,int flags,bool *writable) {
    assert(server==s_server);*writable=!transport_write_needs_read;return lwip_send(socket,data,size,flags);
}
ssize_t native_web_transport_recv(httpd_handle_t server,int socket,void *data,size_t size,int flags,bool *writable) {
    assert(server==s_server);*writable=transport_read_needs_write;return lwip_recv(socket,data,size,flags);
}
void native_web_transport_shutdown(httpd_handle_t server,int socket,bool graceful) {
    assert(server==s_server);last_shutdown_graceful=graceful;(void)shutdown(socket,SHUT_RDWR);
}
static int next_action(int *script,size_t length,size_t *at) {
    return *at < length ? script[(*at)++] : INT_MAX;
}
ssize_t lwip_send(int socket,const void *data,size_t size,int flags) {
    assert(socket >= 0 && socket < 32 && sessions[socket].live && data);
#ifndef OLD_BASELINE
    assert(flags & MSG_DONTWAIT);
#else
    (void)flags;
#endif
    ++send_calls; now_us += send_advance;
    int action=next_action(send_script,send_script_len,&send_script_at);
    if (action<0) { errno=-action; return -1; }
    if (!action) return 0;
    if ((size_t)action<size) size=(size_t)action;
    if (send_chunk && size>send_chunk) size=send_chunk;
    assert(size<=sizeof(transmitted_wire)-transmitted_size);
    memcpy(transmitted_wire+transmitted_size,data,size); transmitted_size+=size;
    if (delivery_count<32) delivery_incarnation[delivery_count++]=sessions[socket].incarnation;
    return (ssize_t)size;
}
ssize_t lwip_recv(int socket,void *data,size_t size,int flags) {
    assert(socket>=0 && socket<32 && sessions[socket].live && data);
#ifndef OLD_BASELINE
    assert(flags & MSG_DONTWAIT);
#endif
    ++recv_calls; now_us += recv_advance;
    int action=next_action(recv_script,recv_script_len,&recv_script_at);
    if (action<0) { errno=-action; return -1; }
    if (!action) return 0;
    if ((size_t)action<size) size=(size_t)action;
    if (recv_chunk && size>recv_chunk) size=recv_chunk;
    if (size>received_size-received_at) size=received_size-received_at;
    memcpy(data,received_wire+received_at,size);
    if (!(flags & MSG_PEEK)) received_at+=size;
    return (ssize_t)size;
}
int lwip_select(int nfds,fd_set *readable,fd_set *writable,fd_set *exception,struct timeval *wait) {
    assert(nfds>0 && (readable || writable) && !exception && wait);
    ++select_calls;
    last_wait_writable=writable!=NULL;
    int result=next_action(wait_script,wait_script_len,&wait_script_at);
    if (result<0) { errno=-result; return -1; }
    if (!result) { now_us += wait->tv_sec*1000000LL+wait->tv_usec; return 0; }
    return 1;
}
static void close_session(int socket) {
    struct sock_db *session=&sessions[socket];
    if (session->free_context) session->free_context(session->context);
    unsigned next=session->incarnation+1;
    memset(session,0,sizeof(*session)); session->incarnation=next;
}
static void open_session(int socket,bool websocket) {
    unsigned incarnation=sessions[socket].incarnation+1;
    sessions[socket]=(struct sock_db){.fd=socket,.handle=s_server,.live=true,.ws_handshake_done=websocket,
        .incarnation=incarnation,.send_fn=default_send,.recv_fn=default_receive};
#ifndef OLD_BASELINE
    sessions[socket].ws_control_frames=true;
#endif
}
static httpd_req_t request_for(int socket,struct httpd_req_aux *aux) {
    *aux=(struct httpd_req_aux){.sd=&sessions[socket]};
    return (httpd_req_t){.method=3,.handle=s_server,.aux=aux};
}
static void ready_session(int socket) {
    open_session(socket,false);
#ifndef OLD_BASELINE
    struct httpd_req_aux aux;
    httpd_req_t req=request_for(socket,&aux);
    assert(websocket_pre_handshake(&req)==ESP_OK);
    sessions[socket].ws_handshake_done=true;
    assert(websocket_post_handshake(&req)==ESP_OK);
#else
    sessions[socket].ws_handshake_done=true;
#endif
}
static void reset(void) {
    run_queue();
    for (int i=0;i<32;++i) close_session(i);
    s_server=(void *)1;
    now_us=100; queue_count=shutdown_count=command_count=activity_count=http_errors=0;
    send_calls=recv_calls=select_calls=yields=0;
    send_chunk=recv_chunk=send_advance=recv_advance=0;
    send_script_len=recv_script_len=wait_script_len=0;
    send_script_at=recv_script_at=wait_script_at=0;
    received_size=received_at=transmitted_size=0;
    queue_failure=context_failure=send_override_failure=recv_override_failure=false;
    task_failure=registration_failure=false; awake=true; delivery_count=0;
    transport_write_needs_read=transport_read_needs_write=last_wait_writable=last_shutdown_graceful=false;
    memset(command_text,0,sizeof(command_text));
    atomic_store(&s_status_send_pending,0); atomic_store(&s_current_send_pending,0);
#ifndef OLD_BASELINE
    memset(s_clients,0,sizeof(s_clients));
    memset(&s_status_work,0,sizeof(s_status_work)); memset(&s_current_work,0,sizeof(s_current_work)); memset(&s_playlist_work,0,sizeof(s_playlist_work));
    atomic_store(&s_completed_deliveries,0);
    atomic_store(&s_fragmented_clients,0); atomic_store(&s_message_poll_pending,false);
#endif
}
static size_t frame_header(uint8_t *target,size_t size,httpd_ws_type_t type,bool masked,bool final,int encoding) {
    size_t length=2; target[0]=(uint8_t)type | (final?0x80:0);
    if (!encoding) encoding=size<126?7:(size<=65535?16:64);
    if (encoding==7) target[1]=(uint8_t)size;
    else if (encoding==16) { target[1]=126; target[2]=(uint8_t)(size>>8); target[3]=(uint8_t)size; length=4; }
    else { target[1]=127; for(unsigned i=0;i<8;++i) target[2+i]=(uint8_t)((uint64_t)size>>(56-8*i)); length=10; }
    if(masked) target[1]|=0x80;
    return length;
}
static void append_input(const uint8_t *payload,size_t size,httpd_ws_type_t type,bool final,int encoding) {
    size_t header=frame_header(received_wire+received_size,size,type,true,final,encoding);
    received_size+=header;
    const uint8_t mask[4]={0xaa,0xbb,0xcc,0xdd};
    memcpy(received_wire+received_size,mask,4); received_size+=4;
    for(size_t i=0;i<size;++i) received_wire[received_size++]=payload[i]^mask[i%4];
}
static bool same_output(const uint8_t *payload,size_t size,httpd_ws_type_t type) {
    uint8_t header[10]; size_t head=frame_header(header,size,type,false,true,0);
    return transmitted_size==head+size && !memcmp(header,transmitted_wire,head) &&
        !memcmp(payload,transmitted_wire+head,size);
}
static esp_err_t incoming(httpd_req_t *request) {
    esp_err_t result=httpd_ws_get_frame_type(request);
    if(result!=ESP_OK) return result;
    if(request->aux->ws_type==HTTPD_WS_TYPE_CLOSE) sessions[httpd_req_to_sockfd(request)].ws_close=true;
    if(request->aux->ws_type<HTTPD_WS_TYPE_CLOSE || request->aux->ws_type==HTTPD_WS_TYPE_PONG || request->aux->sd->ws_control_frames)
        return websocket_handler(request);
    return ESP_OK;
}

#ifndef OLD_BASELINE
static void test_registration(void) {
    reset(); native_state_t state={0};
    assert(websocket_service_register(s_server,&state)==ESP_OK);
    assert(route.is_websocket && route.handle_ws_control_frames && route.handler==websocket_handler);
    assert(route.ws_post_handshake_cb==websocket_post_handshake && atomic_load(&s_reboot_ready));
    assert(route.ws_pre_handshake_cb==websocket_pre_handshake);
    open_session(3,true); struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
    assert(route.ws_post_handshake_cb(&req)!=ESP_OK);
    assert(route.ws_pre_handshake_cb(&req)==ESP_OK);
    assert(route.ws_post_handshake_cb(&req)==ESP_OK);
    assert(sessions[3].send_fn==ws_send_complete && sessions[3].recv_fn==ws_receive_complete);
    assert(route.ws_pre_handshake_cb(&req)==ESP_FAIL); ++cases;
    for(int mode=0;mode<4;++mode) {
        reset(); open_session(3,true); req=request_for(3,&aux);
        if(mode==0) { sessions[3].context=&foreign_context; }
        else if(mode==1) context_failure=true;
        else if(mode==2) send_override_failure=true;
        else recv_override_failure=true;
        assert(websocket_pre_handshake(&req)!=ESP_OK);
        assert(shutdown_count==(unsigned)(mode>=2));
        if(!mode) assert(sessions[3].context==&foreign_context);
        close_session(3); for(size_t i=0;i<CONFIG_LWIP_MAX_SOCKETS;++i) assert(!s_clients[i].used);
        ++cases;
    }
    reset(); for(int i=0;i<10;++i) ready_session(i);
    open_session(11,true); req=request_for(11,&aux); assert(websocket_pre_handshake(&req)==ESP_ERR_NO_MEM);
    assert(ws_session(s_server,-1)==NULL && ws_session(s_server,FD_SETSIZE)==NULL);
    close_session(4); assert(websocket_pre_handshake(&req)==ESP_OK); ++cases;
}
static void test_send_splits(void) {
    static const size_t lengths[]={0,1,7,125,126,255,1280,65536};
    static uint8_t payload[65537]; memset(payload,'q',sizeof(payload));
    for(size_t n=0;n<sizeof(lengths)/sizeof(*lengths);++n) for(unsigned chunk=1;chunk<=16;++chunk) {
        reset(); ready_session(3); send_chunk=chunk;
        httpd_ws_frame_t frame={.final=true,.type=HTTPD_WS_TYPE_TEXT,.payload=payload,.len=lengths[n]};
        assert(httpd_ws_send_frame_async(s_server,3,&frame)==ESP_OK);
        assert(same_output(payload,lengths[n],HTTPD_WS_TYPE_TEXT)); ++cases;
    }
}
static void test_receive_splits(void) {
    static const size_t lengths[]={0,1,7,125,126,255};
    uint8_t payload[256]; memset(payload,'q',255); payload[255]=0;
    for(size_t n=0;n<sizeof(lengths)/sizeof(*lengths);++n) for(unsigned chunk=1;chunk<=16;++chunk) {
        reset(); ready_session(3); recv_chunk=chunk;
        append_input(payload,lengths[n],HTTPD_WS_TYPE_TEXT,true,0);
        struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
        assert(incoming(&req)==ESP_OK && received_at==received_size);
        assert(command_count==(unsigned)(lengths[n]>0));
        assert(!memcmp(command_text,payload,lengths[n]) && !activity_count); ++cases;
    }
    // Exercise the SDK's 64-bit length and a split mask using the production
    // override, independently of the application's 255-byte command limit.
    for(unsigned chunk=1;chunk<=8;++chunk) {
        reset(); ready_session(3); recv_chunk=chunk;
        uint8_t *large=malloc(65536), *decoded=malloc(65536); assert(large && decoded); memset(large,0xf3,65536);
        append_input(large,65536,HTTPD_WS_TYPE_BINARY,true,64);
        struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
        assert(httpd_ws_get_frame_type(&req)==ESP_OK);
        ws_session(s_server,3)->receive_deadline_us=now_us+WS_FRAME_BUDGET_US;
        httpd_ws_frame_t frame={.payload=decoded};
        assert(httpd_ws_recv_frame(&req,&frame,65536)==ESP_OK && frame.len==65536);
        assert(!memcmp(large,decoded,65536) && received_at==received_size);
        free(large); free(decoded); ++cases;
    }
}
static void test_control_and_alignment(void) {
    static const uint8_t payload[]={0x01,0x7f,0,0xaa,0xff};
    for(unsigned chunk=1;chunk<=8;++chunk) {
        reset(); ready_session(3); send_chunk=recv_chunk=chunk;
        append_input(payload,sizeof(payload),HTTPD_WS_TYPE_PING,true,0);
        struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
        assert(incoming(&req)==ESP_OK && same_output(payload,sizeof(payload),HTTPD_WS_TYPE_PONG));
        assert(!command_count && received_at==received_size); ++cases;
        reset(); ready_session(3); send_chunk=recv_chunk=chunk;
        const uint8_t close_payload[]={3,0xe8};
        append_input(close_payload,2,HTTPD_WS_TYPE_CLOSE,true,0); req=request_for(3,&aux);
        assert(incoming(&req)==ESP_OK && same_output(close_payload,2,HTTPD_WS_TYPE_CLOSE));
        assert(received_at==received_size); ++cases;
    }
    for(unsigned type=10;type<=10;++type) for(size_t n=0;n<=sizeof(payload);++n) {
        reset(); ready_session(3); recv_chunk=1;
        append_input(payload,n,(httpd_ws_type_t)type,true,0);
        append_input((const uint8_t *)"ping",4,HTTPD_WS_TYPE_TEXT,true,0);
        struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
        assert(incoming(&req)==ESP_OK && !command_count);
        req=request_for(3,&aux); assert(incoming(&req)==ESP_OK);
        assert(command_count==1 && !strcmp(command_text,"ping") && received_at==received_size); ++cases;
    }
    for(int mode=0;mode<3;++mode) {
        reset(); ready_session(3); uint8_t payload256[256]; memset(payload256,'q',256);
        append_input(payload256,mode==0?256:4,mode==1?HTTPD_WS_TYPE_CONTINUE:HTTPD_WS_TYPE_TEXT,true,0);
        struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
        if(mode==2) awake=false;
        assert(incoming(&req)!=ESP_OK && !command_count && !activity_count);
        assert(shutdown_count==(unsigned)(mode!=2)); ++cases;
    }
}
static void test_retries_and_failures(void) {
    const int transient[]={-EAGAIN,-EWOULDBLOCK,-EINTR};
    for(unsigned sending=0;sending<2;++sending) for(unsigned n=0;n<3;++n) {
        reset(); ready_session(3); int *script=sending?send_script:recv_script;
        script[0]=transient[n]; script[1]=1; script[2]=transient[n];
        if(sending) send_script_len=3; else { recv_script_len=3; memcpy(received_wire,"data",4); received_size=4; }
        wait_script[0]=-EINTR; wait_script[1]=1; wait_script_len=2;
        char output[4]; int result=sending?ws_send_complete(s_server,3,"data",4,0):ws_receive_complete(s_server,3,output,4,0);
        assert(result==4 && select_calls==2 && yields==2);
        if(!sending) assert(!memcmp(output,"data",4));
        ++cases;
    }
    const int fatal[]={0,-EPIPE,-ECONNRESET};
    for(unsigned sending=0;sending<2;++sending) for(unsigned n=0;n<3;++n) {
        reset(); ready_session(3); int *script=sending?send_script:recv_script;
        script[0]=fatal[n]; if(sending) send_script_len=1; else recv_script_len=1;
        char output[4]; int result=sending?ws_send_complete(s_server,3,"data",4,0):ws_receive_complete(s_server,3,output,4,0);
        assert(result<=0 && !select_calls); ++cases;
    }
    for(unsigned sending=0;sending<2;++sending) for(int mode=0;mode<3;++mode) {
        reset(); ready_session(3); int *script=sending?send_script:recv_script;
        script[0]=-EAGAIN; if(sending) send_script_len=1; else recv_script_len=1;
        wait_script[0]=mode==0?0:-EBADF; wait_script_len=1;
        if(mode==2) {
            wait_script[0]=-EINTR;
            if(sending) send_advance=999500; else recv_advance=999500;
        }
        char output[4]; int result=sending?ws_send_complete(s_server,3,"data",4,0):ws_receive_complete(s_server,3,output,4,0);
        assert(result<=0 && select_calls); ++cases;
    }
    reset(); ready_session(3); memcpy(received_wire,"peek",4); received_size=4; recv_chunk=2;
    char output[8]={0}; assert(ws_receive_complete(s_server,3,output,4,MSG_PEEK)==2);
    assert(!memcmp(output,"pe",2) && !received_at && recv_calls==1); ++cases;
    reset(); ready_session(3); char tiny=0;
    assert(ws_send_complete(s_server,3,&tiny,(size_t)INT_MAX+1U,0)==HTTPD_SOCK_ERR_FAIL);
    assert(ws_receive_complete(s_server,3,&tiny,(size_t)INT_MAX+1U,0)==HTTPD_SOCK_ERR_FAIL);
    assert(!send_calls && !recv_calls); ++cases;
}
static void test_deadlines(void) {
    reset(); ready_session(3); struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
    send_advance=600000;
    assert(ws_send_request(&req,"ping")!=ESP_OK && shutdown_count==1);
    assert(now_us<=1200100 && !ws_session(s_server,3) && !s_clients[0].send_deadline_us); ++cases;
    reset(); ready_session(3); recv_chunk=1; recv_advance=200000;
    append_input((const uint8_t *)"ping",4,HTTPD_WS_TYPE_TEXT,true,0); req=request_for(3,&aux);
    assert(incoming(&req)!=ESP_OK && !command_count && shutdown_count==1);
    assert(now_us<=1400100 && !activity_count && !s_clients[0].receive_deadline_us); ++cases;
    for(unsigned sending=0;sending<2;++sending) {
        reset(); ready_session(3); int *script=sending?send_script:recv_script;
        for(unsigned i=0;i<32;++i) script[i]=-EAGAIN;
        if(sending) send_script_len=32; else recv_script_len=32;
        // Spurious readiness must yield until the shared deadline, then stop.
        now_us=1; char output[4];
        if(sending) send_advance=40000; else recv_advance=40000;
        int result=sending?ws_send_complete(s_server,3,"data",4,0):ws_receive_complete(s_server,3,output,4,0);
        assert(result==HTTPD_SOCK_ERR_TIMEOUT && yields>0 && now_us<=1041001); ++cases;
    }
    reset(); ready_session(3); recv_script[0]=-EAGAIN; recv_script_len=1; wait_script[0]=0; wait_script_len=1;
    struct httpd_req_aux opcode_aux; req=request_for(3,&opcode_aux);
    assert(httpd_ws_get_frame_type(&req)==ESP_OK && opcode_aux.ws_type==HTTPD_WS_TYPE_CLOSE);
    assert(now_us==1000100); ++cases;
}
static void test_broadcast_lifetime(void) {
    reset(); ready_session(3);
    assert(broadcast_text("status",&s_status_send_pending,&s_status_work));
    assert(queue_count==1 && atomic_load(&s_status_send_pending)==1 && !send_calls);
    assert(!broadcast_text("other",&s_status_send_pending,&s_status_work));
    close_session(3); open_session(3,false); run_queue();
    assert(!send_calls && !shutdown_count && !atomic_load(&s_status_send_pending)); ++cases;
    reset(); ready_session(3);
    assert(broadcast_text("status",&s_status_send_pending,&s_status_work));
    close_session(3); ready_session(3); unsigned expected=sessions[3].incarnation; run_queue();
    assert(same_output((const uint8_t *)"status",6,HTTPD_WS_TYPE_TEXT));
    for(unsigned i=0;i<delivery_count;++i) assert(delivery_incarnation[i]==expected);
    assert(atomic_load(&s_completed_deliveries)==1 && !queue_count); ++cases;
    reset(); ready_session(3); send_script[0]=-EPIPE; send_script_len=1;
    assert(broadcast_text("status",&s_status_send_pending,&s_status_work)); run_queue();
    assert(shutdown_count==1 && !queue_count && !atomic_load(&s_status_send_pending));
    close_session(3); open_session(3,false); run_queue(); assert(shutdown_count==1); ++cases;
    reset(); ready_session(3); queue_failure=true;
    assert(!broadcast_text("status",&s_status_send_pending,&s_status_work));
    assert(!queue_count && !atomic_load(&s_status_send_pending) && !atomic_load(&s_status_work.busy));
    queue_failure=false; assert(broadcast_text("status",&s_status_send_pending,&s_status_work)); run_queue(); ++cases;
    reset(); ready_session(3); ready_session(4); send_chunk=1;
    assert(broadcast_text("status",&s_status_send_pending,&s_status_work));
    assert(broadcast_text("current",&s_current_send_pending,&s_current_work));
    assert(broadcast_text("event",&s_status_send_pending,&s_playlist_work));
    assert(queue_count==3 && atomic_load(&s_status_send_pending)==2); run_queue();
    assert(atomic_load(&s_completed_deliveries)==6 && !atomic_load(&s_status_send_pending) && !atomic_load(&s_current_send_pending)); ++cases;
}

static uint16_t close_code_output(void) {
    assert(transmitted_size>=4 && transmitted_wire[0]==0x88 && transmitted_wire[1]==2);
    return (uint16_t)((uint16_t)transmitted_wire[2]*256+transmitted_wire[3]);
}

static void test_fragmented_commands(void) {
    static const size_t lengths[]={0,1,7,125,126,255};
    uint8_t text[256]; memset(text,'a',sizeof(text));
    for(size_t n=0;n<sizeof(lengths)/sizeof(*lengths);++n) for(size_t split=0;split<=lengths[n];++split) {
        reset(); ready_session(3); send_chunk=recv_chunk=(unsigned)(split%7)+1;
        append_input(text,split,HTTPD_WS_TYPE_TEXT,false,0);
        append_input((const uint8_t *)"ping",4,HTTPD_WS_TYPE_PING,true,0);
        append_input((const uint8_t *)"pong",4,HTTPD_WS_TYPE_PONG,true,0);
        append_input(text+split,lengths[n]-split,HTTPD_WS_TYPE_CONTINUE,true,0);
        struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
        assert(incoming(&req)==ESP_OK && !command_count && atomic_load(&s_fragmented_clients)==1);
        req=request_for(3,&aux); assert(incoming(&req)==ESP_OK && !command_count && atomic_load(&s_fragmented_clients)==1);
        assert(same_output((const uint8_t *)"ping",4,HTTPD_WS_TYPE_PONG));
        req=request_for(3,&aux); assert(incoming(&req)==ESP_OK && !command_count && atomic_load(&s_fragmented_clients)==1);
        req=request_for(3,&aux); assert(incoming(&req)==ESP_OK && atomic_load(&s_fragmented_clients)==0);
        assert(command_count==(unsigned)(lengths[n]>0) && received_at==received_size);
        assert(!memcmp(command_text,text,lengths[n])); ++cases;
    }
    const uint8_t utf8[]={0xd0,0xbf,0xd0,0xb8,0xd0,0xbd,0xd0,0xb3};
    for(size_t split=0;split<=sizeof(utf8);++split) {
        reset(); ready_session(3); recv_chunk=1;
        append_input(utf8,split,HTTPD_WS_TYPE_TEXT,false,0);
        append_input(utf8+split,sizeof(utf8)-split,HTTPD_WS_TYPE_CONTINUE,true,0);
        struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
        assert(incoming(&req)==ESP_OK && !command_count); req=request_for(3,&aux);
        assert(incoming(&req)==ESP_OK && command_count==1 && !memcmp(command_text,utf8,sizeof(utf8))); ++cases;
    }
    for(int mode=0;mode<5;++mode) {
        reset(); ready_session(3);
        const uint8_t invalid[]={0xc0,0xaf};
        append_input(mode==0?invalid:(const uint8_t *)"a",mode==0?2:1,HTTPD_WS_TYPE_TEXT,false,0);
        append_input((const uint8_t *)"b",1,mode==1?HTTPD_WS_TYPE_TEXT:(mode==2?HTTPD_WS_TYPE_BINARY:HTTPD_WS_TYPE_CONTINUE),true,0);
        struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
        esp_err_t initial=incoming(&req);
        if(mode==0) {
            assert(initial!=ESP_OK && close_code_output()==1007 && !command_count && !atomic_load(&s_fragmented_clients));
            ++cases; continue;
        }
        assert(initial==ESP_OK && atomic_load(&s_fragmented_clients)==1);
        if(mode==3) now_us+=WS_MESSAGE_BUDGET_US;
        if(mode==4) { close_session(3); assert(!atomic_load(&s_fragmented_clients)); ++cases; continue; }
        req=request_for(3,&aux); assert(incoming(&req)!=ESP_OK && !command_count && !atomic_load(&s_fragmented_clients));
        assert(close_code_output()==(mode==0?1007:(mode==3?1008:1002))); ++cases;
    }
    reset(); ready_session(3); uint8_t huge[256]; memset(huge,'a',sizeof(huge));
    append_input(huge,255,HTTPD_WS_TYPE_TEXT,false,0); append_input(huge,1,HTTPD_WS_TYPE_CONTINUE,true,0);
    struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
    assert(incoming(&req)==ESP_OK); req=request_for(3,&aux);
    assert(incoming(&req)!=ESP_OK && close_code_output()==1009 && !atomic_load(&s_fragmented_clients)); ++cases;
    reset(); ready_session(3); append_input((const uint8_t *)"binary",6,HTTPD_WS_TYPE_BINARY,true,0); req=request_for(3,&aux);
    assert(incoming(&req)!=ESP_OK && close_code_output()==1003 && !command_count); ++cases;
    reset(); ready_session(3); const uint8_t nul_text[]={'r','e','b','o','o','t',0,'x'};
    append_input(nul_text,sizeof(nul_text),HTTPD_WS_TYPE_TEXT,true,0); req=request_for(3,&aux);
    assert(incoming(&req)==ESP_OK && !command_count && !shutdown_count);
    assert(same_output((const uint8_t *)"{\"commandError\":\"Command contains NUL\"}",39,HTTPD_WS_TYPE_TEXT)); ++cases;
}

static void test_fragment_deadline_poll(void) {
    reset(); ready_session(3); poll_message_deadlines(); assert(!queue_count);
    append_input((const uint8_t *)"unfinished",10,HTTPD_WS_TYPE_TEXT,false,0);
    struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
    assert(incoming(&req)==ESP_OK && atomic_load(&s_fragmented_clients)==1);
    poll_message_deadlines(); poll_message_deadlines(); assert(queue_count==1);
    run_queue(); assert(!shutdown_count && atomic_load(&s_fragmented_clients)==1);
    now_us+=WS_MESSAGE_BUDGET_US;
    queue_failure=true; poll_message_deadlines(); assert(!queue_count && !atomic_load(&s_message_poll_pending));
    queue_failure=false; poll_message_deadlines(); run_queue();
    assert(shutdown_count==1 && !atomic_load(&s_fragmented_clients) && close_code_output()==1008 && !command_count); ++cases;
    close_session(3); open_session(3,false); poll_message_deadlines(); run_queue(); assert(shutdown_count==1); ++cases;
    reset(); ready_session(3); append_input((const uint8_t *)"a",1,HTTPD_WS_TYPE_TEXT,false,0); req=request_for(3,&aux);
    assert(incoming(&req)==ESP_OK); poll_message_deadlines(); close_session(3); open_session(3,false);
    now_us+=WS_MESSAGE_BUDGET_US; run_queue(); assert(!shutdown_count && !atomic_load(&s_fragmented_clients)); ++cases;
}

static void test_pre_upgrade_transport(void) {
    reset(); open_session(3,false); struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
    assert(websocket_pre_handshake(&req)==ESP_OK && !sessions[3].ws_handshake_done);
    send_chunk=1;
    const char upgrade[]="HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n";
    assert(sessions[3].send_fn(s_server,3,upgrade,sizeof(upgrade)-1,0)==(int)sizeof(upgrade)-1);
    assert(transmitted_size==sizeof(upgrade)-1 && !memcmp(transmitted_wire,upgrade,sizeof(upgrade)-1));
    // Simulate a rejected/incomplete upgrade: HTTPD session free releases the
    // caller-owned protocol state before the descriptor can become HTTP again.
    close_session(3); open_session(3,false); assert(!ws_session(s_server,3)); ++cases;
}

static void test_outbound_utf8_and_close_validation(void) {
    const uint8_t close_payloads[][6]={{1},{3,0xe7},{3,0xec},{3,0xed},{3,0xee},{3,0xf7},{0x13,0x88},{3,0xe8,0xc0,0xaf},{3,0xe8,'o','k'}};
    const size_t lengths[]={1,2,2,2,2,2,2,4,4};
    for(size_t i=0;i<sizeof(lengths)/sizeof(*lengths);++i) {
        reset();ready_session(3);recv_chunk=send_chunk=1;
        append_input(close_payloads[i],lengths[i],HTTPD_WS_TYPE_CLOSE,true,0);
        struct httpd_req_aux aux;httpd_req_t req=request_for(3,&aux);
        esp_err_t result=incoming(&req);
        if(i+1==sizeof(lengths)/sizeof(*lengths)) {
            assert(result==ESP_OK && same_output(close_payloads[i],lengths[i],HTTPD_WS_TYPE_CLOSE));
        } else assert(result!=ESP_OK && close_code_output()==(i==7?1007:1002));
        assert(!command_count && shutdown_count==1 && ws_send_request(&req,"late")!=ESP_OK);
        size_t sent=transmitted_size;assert(broadcast_text("late",&s_status_send_pending,&s_status_work));run_queue();assert(transmitted_size==sent);++cases;
    }
    for(unsigned type=9;type<=10;++type) for(unsigned mode=0;mode<2;++mode) {
        reset();ready_session(3);uint8_t payload[126];memset(payload,'x',sizeof(payload));
        append_input(payload,mode?126:1,(httpd_ws_type_t)type,mode!=0,0);
        struct httpd_req_aux aux;httpd_req_t req=request_for(3,&aux);
        assert(incoming(&req)!=ESP_OK && close_code_output()==1002 && !command_count);++cases;
    }
    for(unsigned value=1;value<256;++value) for(size_t capacity=0;capacity<=16;++capacity) {
        char source[2]={(char)value,0}, escaped[32];memset(escaped,0xa5,sizeof(escaped));
        json_escape(source,escaped+4,capacity);
        for(unsigned i=0;i<4;++i)assert((unsigned char)escaped[i]==0xa5);
        for(size_t i=4+capacity;i<sizeof(escaped);++i)assert((unsigned char)escaped[i]==0xa5);
        if(capacity)assert(websocket_message_utf8_valid((const uint8_t *)escaped+4,strlen(escaped+4)));
        ++cases;
    }
    char raw[192], escaped[400];memset(raw,0xff,sizeof(raw)-1);raw[sizeof(raw)-1]=0;
    json_escape(raw,escaped,sizeof(escaped)); assert(strlen(escaped)==396);
    printf("JSON_SAMPLE=\"%s\"\n",escaped); ++cases;
    reset();ready_session(3);struct httpd_req_aux aux;httpd_req_t req=request_for(3,&aux);
    const char invalid[]={(char)0xff,0};assert(ws_send_request(&req,invalid)!=ESP_OK && close_code_output()==1011);++cases;
    reset();ready_session(3);assert(broadcast_text(invalid,&s_status_send_pending,&s_status_work));run_queue();assert(close_code_output()==1011 && !atomic_load(&s_completed_deliveries));++cases;
}

static void test_tls_transport_delegation(void) {
    reset();ready_session(3);transport_write_needs_read=true;
    send_script[0]=-EAGAIN;send_script_len=1;
    struct httpd_req_aux aux;httpd_req_t req=request_for(3,&aux);
    assert(ws_send_request(&req,"ping")==ESP_OK && select_calls==1 && !last_wait_writable);++cases;
    reset();ready_session(3);transport_read_needs_write=true;
    append_input((const uint8_t *)"ping",4,HTTPD_WS_TYPE_TEXT,true,0);
    recv_script[0]=-EAGAIN;recv_script_len=1;req=request_for(3,&aux);
    assert(incoming(&req)==ESP_OK && select_calls==1 && last_wait_writable && command_count==1);++cases;
    reset();ready_session(3);const uint8_t close_payload[]={3,0xe8};
    append_input(close_payload,2,HTTPD_WS_TYPE_CLOSE,true,0);req=request_for(3,&aux);
    assert(incoming(&req)==ESP_OK && last_shutdown_graceful);++cases;
}
#endif

int main(int argc,char **argv) {
    assert(argc==2);
#ifdef OLD_BASELINE
    reset(); ready_session(3); struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
    bool passed=false;
    if(!strcmp(argv[1],"short-send")) {
        send_chunk=1; esp_err_t result=ws_send_request(&req,"ping");
        passed=result!=ESP_OK || same_output((const uint8_t *)"ping",4,HTTPD_WS_TYPE_TEXT);
    } else if(!strcmp(argv[1],"deadline")) {
        send_advance=600000; passed=ws_send_request(&req,"ping")!=ESP_OK;
    } else if(!strcmp(argv[1],"pong")) {
        append_input((const uint8_t *)"pong",4,HTTPD_WS_TYPE_PONG,true,0);
        passed=incoming(&req)==ESP_OK && received_at==received_size;
    } else if(!strcmp(argv[1],"fd-reuse")) {
        (void)broadcast_text("status",&s_status_send_pending);
        close_session(3); open_session(3,false); run_queue(); passed=!send_calls;
    } else assert(false);
    run_queue();
    if(!passed) fprintf(stderr,"NEGATIVE_CONTROL_FAIL: %s\n",argv[1]);
    return passed?0:1;
#else
    assert(!strcmp(argv[1],"all"));
    {
        reset(); open_session(3,false);
        struct httpd_req_aux aux; httpd_req_t req=request_for(3,&aux);
        req.method=HTTP_GET;
        assert(websocket_handler(&req)==ESP_OK && http_errors==1);
        assert(!sessions[3].context && !activity_count && !command_count && !send_calls);
        ++cases;
    }
    test_registration(); test_send_splits(); test_receive_splits();
    test_control_and_alignment(); test_retries_and_failures(); test_deadlines(); test_broadcast_lifetime();
    test_fragmented_commands(); test_fragment_deadline_poll(); test_pre_upgrade_transport();
    test_outbound_utf8_and_close_validation();
    test_tls_transport_delegation();
    reset(); printf("PASS: %u C3 WebSocket IO/session/framing cases; four historic negative controls required\n",cases);
    printf("WS_LAYOUT={\"client_bytes\":%zu,\"all_clients_bytes\":%zu,\"message_state_bytes\":%zu,\"command_capacity\":256}\n",sizeof(ws_client_t),sizeof(s_clients),sizeof(websocket_message_t)); return 0;
#endif
}
