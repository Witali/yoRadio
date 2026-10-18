/* Platform adapters only. HTTPD algorithms are in generated SDK .inc files. */
static int64_t esp_timer_get_time(void) {
    struct timespec ts;assert(clock_gettime(CLOCK_MONOTONIC,&ts)==0);
    return (int64_t)ts.tv_sec*1000000+ts.tv_nsec/1000;
}
static void vTaskDelay(unsigned ticks) {
    struct timespec ts={.tv_nsec=(long)ticks*1000000};nanosleep(&ts,NULL);
}
static int lwip_select(int n,fd_set *r,fd_set *w,fd_set *e,struct timeval *t) {return select(n,r,w,e,t);}
static bool deep_sleep_clock_begin_activity(void) {++activity_count;return true;}
static void deep_sleep_clock_end_activity(void) {assert(activity_count);--activity_count;}
static void status_task(void *arg) {(void)arg;}
static int xTaskCreate(void (*fn)(void *),const char *name,unsigned stack,void *arg,unsigned priority,void *task) {
    assert(fn==status_task&&!strcmp(name,"websocket_status")&&stack==BOARD_TASK_STACK_WEBSOCKET_STATUS);
    assert(!arg&&priority==2&&!task);return pdPASS; // no status producer in this protocol gate
}
static bool httpd_valid_req(httpd_req_t *r) {
    return r&&r->handle==&server&&r->aux==&server.hd_req_aux&&server.hd_req_aux.sd==&session;
}
static struct sock_db *httpd_sess_get(httpd_handle_t hd,int fd) {
    assert(hd==&server);return fd>=0&&session.fd==fd?&session:NULL;
}
#ifndef INTEGRATION_TLS
static ssize_t native_web_transport_send(httpd_handle_t hd,int fd,const void *data,size_t size,int flags,bool *writable) {
    assert(hd==&server&&fd==session.fd);*writable=true;++send_calls;
    if(size>io_chunk)size=io_chunk;
    return send(fd,data,size,flags|MSG_NOSIGNAL);
}
static ssize_t native_web_transport_recv(httpd_handle_t hd,int fd,void *data,size_t size,int flags,bool *writable) {
    assert(hd==&server&&fd==session.fd);*writable=false;++recv_calls;
    if(size>io_chunk)size=io_chunk;
    return recv(fd,data,size,flags);
}
static void native_web_transport_shutdown(httpd_handle_t hd,int fd,bool graceful) {
    assert(hd==&server&&fd==session.fd);(void)graceful;assert(shutdown(fd,SHUT_RDWR)==0);
}
#endif
static int default_send(httpd_handle_t hd,int fd,const char *data,size_t size,int flags) {
    assert(hd==&server);return (int)send(fd,data,size,flags|MSG_NOSIGNAL);
}
static int default_receive(httpd_handle_t hd,int fd,char *data,size_t size,int flags) {
    assert(hd==&server);if(size>io_chunk)size=io_chunk;return (int)recv(fd,data,size,flags);
}
static esp_err_t httpd_sess_trigger_close(httpd_handle_t hd,int fd) {
    assert(hd==&server&&fd==session.fd);++queued_close_calls;return ESP_OK;
}
static esp_err_t httpd_queue_work(httpd_handle_t hd,httpd_work_fn_t fn,void *arg) {
    (void)fn;(void)arg;assert(hd==&server);assert(!"unexpected background work in foreground protocol gate");return ESP_FAIL;
}
static int httpd_req_handle_err(httpd_req_t *r,int status) {
    (void)r;snprintf(response_status,sizeof(response_status),"%d",status);return ESP_FAIL;
}
static int httpd_resp_set_hdr(httpd_req_t *r,const char *name,const char *value) {
    (void)r;assert(!strcmp(name,"Sec-WebSocket-Version"));snprintf(response_version,sizeof(response_version),"%s",value);return ESP_OK;
}
static int httpd_resp_send_custom_err(httpd_req_t *r,const char *status,const char *message) {
    (void)r;(void)message;snprintf(response_status,sizeof(response_status),"%s",status);return ESP_OK;
}
static int httpd_resp_send_err(httpd_req_t *r,httpd_err_code_t code,const char *message) {
    (void)message;assert(code==HTTPD_400_BAD_REQUEST);
    /* Formatting is a documented seam. Assert the application rejects an
     * ordinary HTTP request before creating a WS context or entering sleep. */
    assert(!session.ctx&&!r->sess_ctx&&!activity_count);
    for(size_t i=0;i<sizeof(s_clients)/sizeof(*s_clients);++i)assert(!s_clients[i].used);
    snprintf(response_status,sizeof(response_status),"%d",code);
    static const char wire[]="HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nConnection: close\r\n\r\n";
    return httpd_send(r,wire,sizeof(wire)-1)==sizeof(wire)-1?ESP_OK:ESP_FAIL;
}
static void esp_http_server_dispatch_event(int event,const void *data,size_t size) {
    assert(event==HTTP_SERVER_EVENT_ON_HEADER||event==HTTP_SERVER_EVENT_DISCONNECTED||event==HTTP_SERVER_EVENT_ON_DATA);
    assert(data&&size);if(event==HTTP_SERVER_EVENT_DISCONNECTED)++delete_count;
}
static size_t strlcpy(char *dst,const char *src,size_t cap) {
    size_t len=strlen(src);if(cap){size_t count=MIN(cap-1,len);memcpy(dst,src,count);dst[count]=0;}return len;
}

/* This seam observes the exact reassembled UTF-8 command delivered by the
 * actual service. Radio/settings command dispatch is verified elsewhere. */
#ifdef TARGET_C3
static void handle_command(httpd_req_t *r,char *command) {
    (void)r;++command_calls;command_size=strlen(command);assert(command_size<sizeof(command_bytes));
    memcpy(command_bytes,command,command_size+1);
}
#else
static esp_err_t handle_command(ws_client_t *client,char *command) {
    (void)client;++command_calls;command_size=strlen(command);assert(command_size<sizeof(command_bytes));
    memcpy(command_bytes,command,command_size+1);return ESP_OK;
}
static bool prepare_status(void) {assert(!"status path must not run for an upgraded frame");return false;}
static esp_err_t send_status(ws_client_t *client,bool force) {(void)client;(void)force;assert(false);return ESP_FAIL;}
#endif
