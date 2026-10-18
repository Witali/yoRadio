#undef malloc
#undef calloc
#undef free
#undef fcntl
typedef struct { void *context;void (*free_context)(void *);httpd_send_func_t send;
    httpd_recv_func_t recv;httpd_pending_func_t pending;unsigned closed,shutdown; } sock_t;
static sock_t sockets[32];
static uint8_t nvs_blob[NATIVE_WEB_TLS_BUNDLE_MAX+1], staged[NATIVE_WEB_TLS_BUNDLE_MAX+1];
static size_t nvs_size, staged_size;
static bool nvs_present,context_fail,fcntl_fail,state_fail,session_init_fail;
static int nvs_open_error,nvs_get_error,nvs_set_error,nvs_commit_error,crypto_fail,override_fail;
static unsigned nvs_opens,nvs_closes,alloc_calls,fail_alloc,live_allocs,tls_live,tls_deleted;
static int handshake_script[32],read_script[32],write_script[32],close_script[32],select_script[32];
static size_t handshake_at,handshake_count,read_at,read_count,write_at,write_count,close_at,close_count,select_at,select_count;
static unsigned selects,yields,raw_writes,raw_reads,close_alerts,last_direction,cases;
static uint64_t now_us;
static uint64_t init_advance,handshake_advance,read_advance,write_advance;
static uint8_t wire[1024],sent[2048];static size_t wire_size,wire_at,sent_size;

void *tracked_malloc(size_t size) {
    ++alloc_calls;if(fail_alloc && alloc_calls==fail_alloc)return NULL;
    void *result=malloc(size?size:1);assert(result);++live_allocs;return result;
}
void *tracked_calloc(size_t count,size_t size) { void *p=tracked_malloc(count*size);if(p)memset(p,0,count*size);return p; }
void tracked_free(void *pointer) { if(pointer){assert(live_allocs);--live_allocs;free(pointer);} }
int mock_fcntl(int socket,int command,...) { assert(socket>=0 && socket<32);(void)command;return fcntl_fail?-1:0; }
int64_t esp_timer_get_time(void) { return (int64_t)now_us; }
void vTaskDelay(unsigned ticks) { ++yields;now_us+=ticks*1000U; }
ssize_t lwip_send(int socket,const void *data,size_t size,int flags) { (void)socket;(void)data;assert(flags&MSG_DONTWAIT);++raw_writes;return (ssize_t)size; }
ssize_t lwip_recv(int socket,void *data,size_t size,int flags) { (void)socket;assert(flags&MSG_DONTWAIT);++raw_reads;if(size>wire_size-wire_at)size=wire_size-wire_at;memcpy(data,wire+wire_at,size);if(!(flags&MSG_PEEK))wire_at+=size;return (ssize_t)size; }
int lwip_select(int count,fd_set *readable,fd_set *writable,fd_set *exception,struct timeval *timeout) {
    assert(count>0 && (readable!=NULL)!=(writable!=NULL) && !exception && timeout);
    ++selects;last_direction=writable!=NULL;
    int result=select_at<select_count?select_script[select_at++]:1;
    if(result<0){errno=-result;return -1;}
    if(!result)now_us+=(uint64_t)timeout->tv_sec*1000000U+(uint64_t)timeout->tv_usec;
    return result;
}
int lwip_close(int socket) { ++sockets[socket].closed;return 0; }
int shutdown(int socket,int how) { assert(how==SHUT_RDWR);++sockets[socket].shutdown;return 0; }
void *httpd_sess_get_transport_ctx(httpd_handle_t server,int socket) { assert(server==(void *)1);return sockets[socket].context; }
void httpd_sess_set_transport_ctx(httpd_handle_t server,int socket,void *context,void (*cleanup)(void *)) { assert(server==(void *)1);if(context_fail)return;sockets[socket].context=context;sockets[socket].free_context=cleanup; }
esp_err_t httpd_sess_set_send_override(httpd_handle_t server,int socket,httpd_send_func_t fn) { assert(server==(void *)1);if(override_fail==1)return ESP_FAIL;sockets[socket].send=fn;return ESP_OK; }
esp_err_t httpd_sess_set_recv_override(httpd_handle_t server,int socket,httpd_recv_func_t fn) { assert(server==(void *)1);if(override_fail==2)return ESP_FAIL;sockets[socket].recv=fn;return ESP_OK; }
esp_err_t httpd_sess_set_pending_override(httpd_handle_t server,int socket,httpd_pending_func_t fn) { assert(server==(void *)1);if(override_fail==3)return ESP_FAIL;sockets[socket].pending=fn;return ESP_OK; }
esp_err_t nvs_open(const char *name,int mode,nvs_handle_t *handle) { assert(!strcmp(name,"web_tls"));++nvs_opens;if(nvs_open_error)return nvs_open_error;if(!nvs_present && mode==NVS_READONLY)return ESP_ERR_NVS_NOT_FOUND;*handle=1;return ESP_OK; }
void nvs_close(nvs_handle_t handle) { assert(handle==1);++nvs_closes; }
esp_err_t nvs_get_blob(nvs_handle_t handle,const char *key,void *data,size_t *size) { assert(handle==1 && !strcmp(key,"bundle"));if(nvs_get_error)return nvs_get_error;if(!nvs_present)return ESP_ERR_NVS_NOT_FOUND;if(data){if(*size<nvs_size)return ESP_ERR_INVALID_SIZE;memcpy(data,nvs_blob,nvs_size);}*size=nvs_size;return ESP_OK; }
esp_err_t nvs_set_blob(nvs_handle_t handle,const char *key,const void *data,size_t size) { assert(handle==1 && !strcmp(key,"bundle") && size<=sizeof(staged));if(nvs_set_error)return nvs_set_error;memcpy(staged,data,size);staged_size=size;return ESP_OK; }
esp_err_t nvs_commit(nvs_handle_t handle) { assert(handle==1);if(nvs_commit_error)return nvs_commit_error;memcpy(nvs_blob,staged,staged_size);nvs_size=staged_size;nvs_present=true;return ESP_OK; }
int psa_crypto_init(void) { return crypto_fail==1?-1:0; }
void mbedtls_x509_crt_init(mbedtls_x509_crt *cert) { memset(cert,0,sizeof(*cert)); }
int mbedtls_x509_crt_parse(mbedtls_x509_crt *cert,const unsigned char *data,size_t size) { (void)cert;assert(size && !data[size-1]);return crypto_fail==2?-1:0; }
void mbedtls_x509_crt_free(mbedtls_x509_crt *cert) { (void)cert; }
void mbedtls_pk_init(mbedtls_pk_context *key) { memset(key,0,sizeof(*key)); }
int mbedtls_pk_parse_key(mbedtls_pk_context *key,const unsigned char *data,size_t size,const unsigned char *pass,size_t pass_size) { (void)key;assert(size && !data[size-1] && !pass && !pass_size);return crypto_fail==3?-1:0; }
int mbedtls_pk_check_pair(const mbedtls_pk_context *pub,const mbedtls_pk_context *key) { assert(pub && key);return crypto_fail==4?-1:0; }
void mbedtls_pk_free(mbedtls_pk_context *key) { (void)key; }
static int action(int *script,size_t count,size_t *at,int default_action) { return *at<count?script[(*at)++]:default_action; }
int mbedtls_ssl_close_notify(mbedtls_ssl_context *ssl) { assert(ssl);++close_alerts;return action(close_script,close_count,&close_at,0); }
esp_tls_t *esp_tls_init(void) { esp_tls_t *tls=tracked_calloc(1,sizeof(*tls));if(tls)++tls_live;return tls; }
esp_err_t esp_tls_server_session_init(esp_tls_cfg_server_t *config,int socket,esp_tls_t *tls) { assert(config->tls_version==ESP_TLS_VER_TLS_1_2 && tls);tls->socket=socket;now_us+=init_advance;return session_init_fail?ESP_FAIL:ESP_OK; }
int esp_tls_server_session_continue_async(esp_tls_t *tls) { assert(tls);now_us+=handshake_advance;return action(handshake_script,handshake_count,&handshake_at,0); }
esp_err_t esp_tls_set_conn_state(esp_tls_t *tls,int state) { assert(tls && state==ESP_TLS_DONE);return state_fail?ESP_FAIL:ESP_OK; }
void esp_tls_server_session_delete(esp_tls_t *tls) { assert(tls && tls_live);--tls_live;++tls_deleted;tracked_free(tls); }
ssize_t esp_tls_conn_write(esp_tls_t *tls,const void *data,size_t size) { assert(tls);now_us+=write_advance;int count=action(write_script,write_count,&write_at,INT_MAX);if(count<=0)return count;if((size_t)count<size)size=(size_t)count;assert(size<=sizeof(sent)-sent_size);memcpy(sent+sent_size,data,size);sent_size+=size;return (ssize_t)size; }
ssize_t esp_tls_conn_read(esp_tls_t *tls,void *data,size_t size) { assert(tls);now_us+=read_advance;int count=action(read_script,read_count,&read_at,INT_MAX);if(count<=0)return count;if((size_t)count<size)size=(size_t)count;if(size>wire_size-wire_at)size=wire_size-wire_at;memcpy(data,wire+wire_at,size);wire_at+=size;return (ssize_t)size; }
ssize_t esp_tls_get_bytes_avail(esp_tls_t *tls) { assert(tls);return (ssize_t)(wire_size-wire_at); }
void *esp_tls_get_ssl_context(esp_tls_t *tls) { assert(tls);return &tls->ssl; }

static void close_socket(int socket) {
    if(sockets[socket].context) {
        httpd_close_tls((void *)1,socket);
        sockets[socket].free_context(sockets[socket].context);
        sockets[socket].context=NULL;sockets[socket].free_context=NULL;
    }
}
static void reset(void) {
    for(int i=0;i<32;++i)close_socket(i);
    assert(native_web_transport_release()==ESP_OK && !live_allocs && !tls_live);
    memset(sockets,0,sizeof(sockets));nvs_size=staged_size=0;nvs_present=false;
    context_fail=fcntl_fail=state_fail=session_init_fail=false;
    nvs_open_error=nvs_get_error=nvs_set_error=nvs_commit_error=crypto_fail=override_fail=0;
    nvs_opens=nvs_closes=alloc_calls=fail_alloc=tls_deleted=0;
    handshake_at=handshake_count=read_at=read_count=write_at=write_count=close_at=close_count=select_at=select_count=0;
    selects=yields=raw_writes=raw_reads=close_alerts=last_direction=0;now_us=100;
    init_advance=handshake_advance=read_advance=write_advance=0;
    wire_size=wire_at=sent_size=0;
}
static httpd_config_t config(void) { return (httpd_config_t){.server_port=80,.stack_size=6144,.max_open_sockets=5,.task_priority=5,.core_id=-1}; }
static void secure_blob(void) {
    memcpy(nvs_blob,"NTLS\1\0\1\0",8);nvs_blob[8]=4;nvs_blob[12]=4;
    memset(nvs_blob+9,0,3);memset(nvs_blob+13,0,3);memcpy(nvs_blob+16,"CERTKEY!",8);nvs_size=24;nvs_present=true;
}
static void ready(void) {
    secure_blob();httpd_config_t cfg=config();assert(native_web_transport_prepare(&cfg)==ESP_OK && native_web_transport_secure());
    assert(cfg.server_port==443 && cfg.max_open_sockets==3 && cfg.stack_size==10240 && cfg.task_priority==5 && cfg.core_id==-1);
    assert(cfg.open_fn==httpd_open_tls && cfg.close_fn==httpd_close_tls);
    assert(cfg.open_fn((void *)1,3)==ESP_OK && sockets[3].send && sockets[3].recv && sockets[3].pending);
}
static void credentials(void) {
    reset();httpd_config_t cfg=config();assert(native_web_transport_prepare(&cfg)==ESP_OK && !native_web_transport_secure());assert(cfg.server_port==80 && cfg.max_open_sockets==5 && !cfg.open_fn);++cases;
    reset();secure_blob();nvs_blob[6]=0;memset(nvs_blob+8,0,8);nvs_size=16;cfg=config();assert(native_web_transport_prepare(&cfg)==ESP_OK && !native_web_transport_secure());++cases;
    for(unsigned mode=0;mode<12;++mode) {
        reset();secure_blob();
        if(mode==0)nvs_blob[0]='X';else if(mode==1)nvs_blob[4]=2;else if(mode==2)nvs_blob[6]=2;else if(mode==3)nvs_blob[7]=1;else if(mode==4)nvs_size=15;
        else if(mode==5)nvs_size=25;else if(mode==6)nvs_blob[8]=0;else if(mode==7)nvs_blob[16]=0;else if(mode==8)nvs_blob[20]=0;else if(mode==9)nvs_get_error=ESP_FAIL;
        else if(mode==10)fail_alloc=1;else nvs_open_error=ESP_FAIL;
        cfg=config();assert(native_web_transport_prepare(&cfg)!=ESP_OK && !native_web_transport_secure());assert(!s_bundle && !live_allocs);++cases;
    }
    for(int failure=1;failure<=4;++failure) { reset();secure_blob();crypto_fail=failure;cfg=config();assert(native_web_transport_prepare(&cfg)!=ESP_OK && !live_allocs);++cases; }
    for(unsigned mode=0;mode<3;++mode) {
        reset();secure_blob();uint8_t original[24];memcpy(original,nvs_blob,24);
        if(mode==0)nvs_set_error=ESP_FAIL;else if(mode==1)nvs_commit_error=ESP_FAIL;
        assert(native_web_transport_provision(original,sizeof(original))==(mode<2?ESP_FAIL:ESP_OK));
        assert(!memcmp(nvs_blob,original,sizeof(original)) && !live_allocs);++cases;
    }
}
static void open_failures(void) {
    for(unsigned mode=0;mode<10;++mode) {
        reset();secure_blob();httpd_config_t cfg=config();assert(native_web_transport_prepare(&cfg)==ESP_OK);
        if(mode==0)fail_alloc=alloc_calls+1;else if(mode==1)fail_alloc=alloc_calls+2;else if(mode==2)context_fail=true;else if(mode==3)fcntl_fail=true;
        else if(mode==4)session_init_fail=true;else if(mode==5)state_fail=true;else if(mode<9)override_fail=(int)mode-5;
        else { handshake_script[0]=ESP_TLS_ERR_SSL_WANT_READ;handshake_count=1;select_script[0]=0;select_count=1; }
        assert(cfg.open_fn((void *)1,3)!=ESP_OK);close_socket(3);assert(!tls_live && live_allocs==1);assert(native_web_transport_release()==ESP_OK && !live_allocs);++cases;
    }
    reset();ready();assert(native_web_transport_release()==ESP_ERR_INVALID_STATE);
    assert(httpd_open_tls((void *)1,4)==ESP_OK && httpd_open_tls((void *)1,5)==ESP_OK);
    assert(httpd_open_tls((void *)1,6)==ESP_ERR_NO_MEM);close_socket(4);assert(httpd_open_tls((void *)1,6)==ESP_OK);++cases;
}
static void io(void) {
    reset();ready();bool writable=false;char data[32];memcpy(wire,"abcdef",6);wire_size=6;
    write_script[0]=ESP_TLS_ERR_SSL_WANT_READ;write_count=1;
    assert(native_web_transport_send((void *)1,3,"x",1,0,&writable)==-1 && errno==EAGAIN && !writable && !raw_writes);++cases;
    read_script[0]=ESP_TLS_ERR_SSL_WANT_WRITE;read_count=1;
    assert(native_web_transport_recv((void *)1,3,data,1,0,&writable)==-1 && errno==EAGAIN && writable && !raw_reads);++cases;
    assert(native_web_transport_recv((void *)1,3,data,4,MSG_PEEK,&writable)==4 && !memcmp(data,"abcd",4));
    assert(sockets[3].pending((void *)1,3)==4);
    assert(native_web_transport_recv((void *)1,3,data,2,MSG_PEEK,&writable)==2 && !memcmp(data,"ab",2));
    assert(native_web_transport_recv((void *)1,3,data,2,0,&writable)==2 && !memcmp(data,"ab",2));
    assert(native_web_transport_recv((void *)1,3,data,4,0,&writable)==2 && !memcmp(data,"cd",2));
    assert(native_web_transport_recv((void *)1,3,data,4,0,&writable)==2 && !memcmp(data,"ef",2) && !raw_reads);++cases;
    write_at=0;write_count=3;write_script[0]=1;write_script[1]=ESP_TLS_ERR_SSL_WANT_READ;write_script[2]=1;
    assert(sockets[3].send((void *)1,3,"abcdef",6,0)==6 && sent_size==6 && !memcmp(sent,"abcdef",6) && selects && !last_direction);++cases;
    read_at=0;read_count=1;read_script[0]=ESP_TLS_ERR_SSL_WANT_WRITE;wire_at=0;
    assert(sockets[3].recv((void *)1,3,data,6,0)==6 && last_direction);++cases;
    write_at=0;write_count=1;write_script[0]=ESP_TLS_ERR_SSL_WANT_READ;select_at=0;select_count=1;select_script[0]=0;
    assert(sockets[3].send((void *)1,3,"x",1,0)==HTTPD_SOCK_ERR_TIMEOUT);++cases;
    reset();ready();close_script[0]=ESP_TLS_ERR_SSL_WANT_WRITE;close_script[1]=0;close_count=2;
    native_web_transport_shutdown((void *)1,3,true);assert(close_alerts==2 && sockets[3].shutdown==1);
    close_socket(3);assert(sockets[3].closed==1 && close_alerts==2 && tls_deleted==1);++cases;
    reset();ready();native_web_transport_shutdown((void *)1,3,false);close_socket(3);assert(!close_alerts && sockets[3].closed==1 && tls_deleted==1);++cases;
    reset();ready();for(unsigned i=0;i<32;++i)close_script[i]=ESP_TLS_ERR_SSL_WANT_READ;close_count=32;select_script[0]=0;select_count=1;
    native_web_transport_shutdown((void *)1,3,true);assert(now_us<=200100 && sockets[3].shutdown==1);++cases;
    reset();bool direction;assert(native_web_transport_send((void *)1,3,"plain",5,0,&direction)==5 && raw_writes==1);++cases;
}
static void boundaries_and_failures(void) {
    reset();httpd_config_t cfg=config();assert(native_web_transport_prepare(&cfg)==ESP_OK);
    httpd_config_t second=config();assert(native_web_transport_prepare(&second)==ESP_ERR_INVALID_STATE);++cases;
    reset();assert(native_web_transport_prepare(NULL)==ESP_ERR_INVALID_ARG);++cases;
    for(unsigned field=0;field<2;++field)for(unsigned count=0;count<4;++count) {
        reset();secure_blob();uint8_t *p=nvs_blob+(field?12:8);memset(p,0,4);
        if(!count){p[1]=0x40;}else if(count==1){p[3]=0xff;}else if(count==2){p[0]=1;}else{p[0]=0xff;p[1]=0xff;p[2]=0xff;p[3]=0xff;}
        cfg=config();assert(native_web_transport_prepare(&cfg)!=ESP_OK && !live_allocs);++cases;
    }
    reset();secure_blob();nvs_size=NATIVE_WEB_TLS_BUNDLE_MAX+1U;cfg=config();assert(native_web_transport_prepare(&cfg)==ESP_ERR_INVALID_SIZE && !live_allocs);++cases;
    reset();assert(native_web_transport_provision(NULL,0)!=ESP_OK && native_web_transport_provision(nvs_blob,SIZE_MAX)!=ESP_OK && !live_allocs);++cases;
    for(unsigned writing=0;writing<2;++writing)for(unsigned want=0;want<2;++want) {
        reset();ready();bool writable=!writing;char output[8];memcpy(wire,"data",4);wire_size=4;
        int code=want?ESP_TLS_ERR_SSL_WANT_WRITE:ESP_TLS_ERR_SSL_WANT_READ;
        if(writing){write_script[0]=code;write_count=1;assert(native_web_transport_send((void *)1,3,"x",1,0,&writable)==-1);}
        else{read_script[0]=code;read_count=1;assert(native_web_transport_recv((void *)1,3,output,4,0,&writable)==-1);}
        assert(errno==EAGAIN && writable==(want!=0));++cases;
    }
    for(unsigned writing=0;writing<2;++writing) {
        reset();ready();bool writable;char out[8];
        if(writing){write_script[0]=-123;write_count=1;assert(native_web_transport_send((void *)1,3,"x",1,0,&writable)==-1);}
        else{read_script[0]=-123;read_count=1;assert(native_web_transport_recv((void *)1,3,out,1,0,&writable)==-1);}
        assert(errno==EIO);close_socket(3);assert(!close_alerts && tls_deleted==1);++cases;
    }
    reset();ready();write_script[0]=1;write_script[1]=1;write_script[2]=1;write_count=3;write_advance=400000;
    assert(sockets[3].send((void *)1,3,"data",4,0)==HTTPD_SOCK_ERR_TIMEOUT);close_socket(3);assert(!close_alerts && !raw_writes);++cases;
    reset();ready();memcpy(wire,"data",4);wire_size=4;read_advance=1000001;
    char out[8];assert(sockets[3].recv((void *)1,3,out,4,0)==HTTPD_SOCK_ERR_TIMEOUT);close_socket(3);assert(!close_alerts);++cases;
    reset();secure_blob();cfg=config();assert(native_web_transport_prepare(&cfg)==ESP_OK);handshake_advance=3000001;
    assert(cfg.open_fn((void *)1,3)==ESP_ERR_TIMEOUT);close_socket(3);assert(!close_alerts && tls_deleted==1);++cases;
    reset();secure_blob();cfg=config();assert(native_web_transport_prepare(&cfg)==ESP_OK);init_advance=3000001;
    assert(cfg.open_fn((void *)1,3)==ESP_ERR_TIMEOUT);close_socket(3);assert(!close_alerts && tls_deleted==1 && !handshake_at);++cases;
    reset();ready();close_socket(3);assert(sockets[3].closed==1 && close_alerts==1 && tls_deleted==1);
    assert(httpd_open_tls((void *)1,3)==ESP_OK);assert(!session((void *)1,4));++cases;
}
int main(void) { credentials();open_failures();io();boundaries_and_failures();reset();printf("PASS: %u native TLS transport credential/ownership/IO fault groups\n",cases);return 0; }
