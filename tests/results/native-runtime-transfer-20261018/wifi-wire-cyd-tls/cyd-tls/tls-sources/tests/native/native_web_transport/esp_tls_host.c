#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#define MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS
#include "mbedtls/net_sockets.h"
#include "mbedtls/pk.h"
#include "mbedtls/private/pk_private.h"
#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/version.h"
#include "psa/crypto.h"
#include "psa/crypto_extra.h"
#include "esp_err.h"
#define CONFIG_ESP_TLS_USING_MBEDTLS 1
#define CONFIG_MBEDTLS_TLS_SERVER 1
#include "sdk-tls-errors.h"
#ifdef HOST_ESP_TLS_UNIFIED_KEYS
#include "sdk-key-config.h"
#endif

// Host ABI field views replace SDK headers only. Their layout is deliberately
// not evidence for the ESP target ABI. Crypto and server configuration below
// are the pinned implementations, not acceptance or handshake substitutes.
typedef enum {ESP_TLS_INIT,ESP_TLS_CONNECTING,ESP_TLS_HANDSHAKE,ESP_TLS_FAIL,ESP_TLS_DONE} esp_tls_conn_state_t;
typedef enum {ESP_TLS_CLIENT,ESP_TLS_SERVER} esp_tls_role_t;
typedef enum {ESP_TLS_VER_ANY,ESP_TLS_VER_TLS_1_2,ESP_TLS_VER_TLS_1_3} esp_tls_proto_ver_t;
typedef struct {esp_tls_proto_ver_t tls_version;} esp_tls_cfg_t;
typedef struct {
    const unsigned char *servercert_buf,*serverkey_buf,*cacert_buf,*serverkey_password;
    unsigned servercert_bytes,serverkey_bytes,cacert_bytes,serverkey_password_len;
    bool use_secure_element,use_ecdsa_peripheral;
    void *userdata;
    const int *ciphersuites_list;
    esp_tls_proto_ver_t tls_version;
#ifdef HOST_ESP_TLS_UNIFIED_KEYS
    const esp_key_config_t *server_key;
#endif
} esp_tls_cfg_server_t;
typedef struct esp_tls esp_tls_t;
struct esp_tls {
    mbedtls_ssl_context ssl;mbedtls_ssl_config conf;mbedtls_net_context server_fd;
    mbedtls_x509_crt cacert,*cacert_ptr;
    union {mbedtls_x509_crt clientcert,servercert;};
    union {mbedtls_pk_context clientkey,serverkey;};
    int sockfd;
    ssize_t (*read)(esp_tls_t *,char *,size_t);
    ssize_t (*write)(esp_tls_t *,const char *,size_t);
    esp_tls_conn_state_t conn_state;esp_tls_role_t role;bool is_tls;
    bool opaque_key_is_external;
    esp_tls_error_handle_t error_handle;
};
typedef struct {
    mbedtls_x509_crt *public_cert;mbedtls_pk_context *pk_key;
    const unsigned char *publiccert_pem_buf,*privkey_pem_buf,*privkey_password;
    size_t publiccert_pem_bytes,privkey_pem_bytes,privkey_password_len;
} esp_tls_pki_t;
typedef struct {esp_err_t (*set_server_cfg)(esp_tls_cfg_server_t *,esp_tls_t *);} esp_tls_server_params_t;
typedef void *httpd_handle_t;
typedef int nvs_handle_t;
typedef int (*httpd_send_func_t)(httpd_handle_t,int,const char *,size_t,int);
typedef int (*httpd_recv_func_t)(httpd_handle_t,int,char *,size_t,int);
typedef int (*httpd_pending_func_t)(httpd_handle_t,int);
typedef struct {
    unsigned stack_size,max_open_sockets,task_priority;int core_id;unsigned server_port;
    esp_err_t (*open_fn)(httpd_handle_t,int);void (*close_fn)(httpd_handle_t,int);
} httpd_config_t;
#define HTTPD_SOCK_ERR_FAIL (-1)
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
#define ESP_ERR_NVS_NOT_FOUND 0x1102
#define NVS_READWRITE 1
#define NVS_READONLY 0
#define NEWLIB_NANO_SSIZE_T_COMPAT_FORMAT "zX"
#define NEWLIB_NANO_SIZE_T_COMPAT_FORMAT "zu"
#define NEWLIB_NANO_SIZE_T_COMPAT_CAST(value) (value)
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGD(...) ((void)0)
static void capture_error(esp_tls_error_handle_t handle,unsigned type,int code){if(!handle)return;if(type==ESP_TLS_ERR_TYPE_ESP)handle->last_error=code;else if(type==ESP_TLS_ERR_TYPE_MBEDTLS)handle->esp_tls_error_code=code;}
#define ESP_INT_EVENT_TRACKER_CAPTURE(handle,type,code) capture_error(handle,type,code)
static mbedtls_x509_crt *global_cacert;
static void mbedtls_print_error_msg(int error){(void)error;}
static esp_tls_error_handle_t esp_tls_internal_event_tracker_create(void){return calloc(1,sizeof(esp_tls_last_error_t));}
static void esp_tls_internal_event_tracker_destroy(esp_tls_error_handle_t handle){free(handle);}
static esp_err_t set_client_config(const char *hostname,size_t length,esp_tls_cfg_t *cfg,esp_tls_t *tls){(void)hostname;(void)length;(void)cfg;(void)tls;assert(!"Client configuration branch is outside this server test");return ESP_FAIL;}
static esp_err_t set_server_config(esp_tls_cfg_server_t *,esp_tls_t *);
void esp_mbedtls_cleanup(esp_tls_t *);
ssize_t esp_mbedtls_read(esp_tls_t *,char *,size_t);
ssize_t esp_mbedtls_write(esp_tls_t *,const char *,size_t);
#define _esp_tls_net_init esp_mbedtls_net_init
#define _esp_tls_server_session_init esp_mbedtls_server_session_init
#define _esp_tls_server_session_continue_async esp_mbedtls_server_session_continue_async
#define _esp_tls_server_session_delete esp_mbedtls_server_session_delete
#define _esp_tls_get_bytes_avail esp_mbedtls_get_bytes_avail
#define _esp_tls_get_ssl_context esp_mbedtls_get_ssl_context
// Keep the pinned SDK ternary in esp_mbedtls_write verbatim. Its signed/unsigned
// warning remains visible; the host tests verify the resulting WANT values.
#pragma GCC diagnostic push
#pragma GCC diagnostic warning "-Wsign-compare"
#include "sdk-functions.inc"
#pragma GCC diagnostic pop

static int64_t esp_timer_get_time(void){struct timespec now;assert(!clock_gettime(CLOCK_MONOTONIC,&now));return (int64_t)now.tv_sec*1000000+now.tv_nsec/1000;}
static void vTaskDelay(unsigned ticks){assert(ticks==1);struct timespec delay={.tv_nsec=1000000};nanosleep(&delay,NULL);}
static ssize_t lwip_send(int fd,const void *data,size_t size,int flags){return send(fd,data,size,flags);}
static ssize_t lwip_recv(int fd,void *data,size_t size,int flags){return recv(fd,data,size,flags);}
static unsigned read_waits,write_waits,raw_closes;
static int lwip_select(int count,fd_set *reads,fd_set *writes,fd_set *errors,struct timeval *timeout){if(reads)++read_waits;if(writes)++write_waits;return select(count,reads,writes,errors,timeout);}
static int lwip_close(int fd){++raw_closes;return close(fd);}
static struct {int socket;void *transport;void (*free_transport)(void *);httpd_send_func_t send;httpd_recv_func_t recv;httpd_pending_func_t pending;} httpd;
static void *httpd_sess_get_transport_ctx(httpd_handle_t server,int fd){assert(server==&httpd&&fd==httpd.socket);return httpd.transport;}
static void httpd_sess_set_transport_ctx(httpd_handle_t server,int fd,void *context,void (*release)(void *)){assert(server==&httpd&&fd==httpd.socket&&!httpd.transport);httpd.transport=context;httpd.free_transport=release;}
static esp_err_t httpd_sess_set_send_override(httpd_handle_t server,int fd,httpd_send_func_t send_fn){assert(server==&httpd&&fd==httpd.socket);httpd.send=send_fn;return ESP_OK;}
static esp_err_t httpd_sess_set_recv_override(httpd_handle_t server,int fd,httpd_recv_func_t recv_fn){assert(server==&httpd&&fd==httpd.socket);httpd.recv=recv_fn;return ESP_OK;}
static esp_err_t httpd_sess_set_pending_override(httpd_handle_t server,int fd,httpd_pending_func_t pending_fn){assert(server==&httpd&&fd==httpd.socket);httpd.pending=pending_fn;return ESP_OK;}
static uint8_t *nvs_blob;
static size_t nvs_size;
static unsigned nvs_commits;
static esp_err_t nvs_open(const char *name,int mode,nvs_handle_t *handle){assert(!strcmp(name,"web_tls"));if(mode==NVS_READONLY&&!nvs_blob)return ESP_ERR_NVS_NOT_FOUND;*handle=1;return ESP_OK;}
static void nvs_close(nvs_handle_t handle){assert(handle==1);}
static esp_err_t nvs_get_blob(nvs_handle_t handle,const char *name,void *data,size_t *size){assert(handle==1&&!strcmp(name,"bundle"));if(!nvs_blob)return ESP_ERR_NVS_NOT_FOUND;if(!data){*size=nvs_size;return ESP_OK;}assert(*size>=nvs_size);memcpy(data,nvs_blob,nvs_size);*size=nvs_size;return ESP_OK;}
static esp_err_t nvs_set_blob(nvs_handle_t handle,const char *name,const void *data,size_t size){assert(handle==1&&!strcmp(name,"bundle"));uint8_t *copy=malloc(size);assert(copy);memcpy(copy,data,size);if(nvs_blob){memset(nvs_blob,0,nvs_size);free(nvs_blob);}nvs_blob=copy;nvs_size=size;return ESP_OK;}
static esp_err_t nvs_commit(nvs_handle_t handle){assert(handle==1);++nvs_commits;return ESP_OK;}
#include "transport-production.inc"

static uint8_t *read_ephemeral(const char *path,size_t *size){FILE *file=fopen(path,"rb");assert(file&&!fseek(file,0,SEEK_END));long count=ftell(file);assert(count>0&&count<16384&&!fseek(file,0,SEEK_SET));uint8_t *data=malloc((size_t)count+1U);assert(data&&fread(data,1,(size_t)count,file)==(size_t)count&&!fclose(file));data[count]=0;*size=(size_t)count;return data;}
static void store_u32(uint8_t *data,size_t value){for(unsigned index=0;index<4;++index)data[index]=(uint8_t)(value>>(index*8U));}
static uint8_t *bundle(const uint8_t *cert,size_t cert_size,const uint8_t *key,size_t key_size,size_t *size){*size=16U+cert_size+key_size;uint8_t *data=calloc(1,*size);assert(data);memcpy(data,"NTLS",4);data[4]=1;data[6]=1;store_u32(data+8,cert_size);store_u32(data+12,key_size);memcpy(data+16,cert,cert_size);memcpy(data+16+cert_size,key,key_size);return data;}
static void ready_socket(int fd,bool writable){fd_set set;FD_ZERO(&set);FD_SET(fd,&set);struct timeval timeout={.tv_sec=3};int result=select(fd+1,writable?NULL:&set,writable?&set:NULL,NULL,&timeout);assert(result>0);}
static void receive_exact(int fd,void *out,size_t size){size_t offset=0;while(offset<size){bool writable;ssize_t result=native_web_transport_recv(&httpd,fd,(uint8_t *)out+offset,size-offset,0,&writable);if(result>0)offset+=(size_t)result;else{assert(result<0&&errno==EAGAIN);ready_socket(fd,writable);}}}
static int listener(unsigned *port){int fd=socket(AF_INET,SOCK_STREAM,0);assert(fd>=0);struct sockaddr_in address={.sin_family=AF_INET,.sin_addr.s_addr=htonl(INADDR_LOOPBACK)};assert(!bind(fd,(struct sockaddr *)&address,sizeof(address))&&!listen(fd,1));socklen_t size=sizeof(address);assert(!getsockname(fd,(struct sockaddr *)&address,&size));*port=ntohs(address.sin_port);return fd;}
static pid_t start_client(unsigned port,const char *ca,const char *script,const char *mode,int *control){int pipefd[2];assert(!pipe(pipefd));pid_t child=fork();assert(child>=0);if(!child){close(pipefd[1]);char port_text[16],control_text[16];snprintf(port_text,sizeof(port_text),"%u",port);snprintf(control_text,sizeof(control_text),"%d",pipefd[0]);execlp("python3","python3",script,"--port",port_text,"--ca",ca,"--mode",mode,"--control",control_text,(char *)NULL);_exit(127);}close(pipefd[0]);*control=pipefd[1];return child;}
static void finish_session(httpd_config_t *config,int fd){assert(httpd.transport&&httpd.free_transport);unsigned before=raw_closes;config->close_fn(&httpd,fd);assert(raw_closes==before+1U&&fcntl(fd,F_GETFD)==-1&&errno==EBADF);httpd.free_transport(httpd.transport);memset(&httpd,0,sizeof(httpd));assert(native_web_transport_release()==ESP_OK);}
static void require_provisioned(const uint8_t *packed,size_t packed_size,const uint8_t *certificate,size_t cert_size,const uint8_t *private_key,size_t key_size){
    esp_err_t result=native_web_transport_provision(packed,packed_size);
    if(result!=ESP_OK){mbedtls_x509_crt chain;mbedtls_pk_context key;mbedtls_x509_crt_init(&chain);mbedtls_pk_init(&key);int init=(int)psa_crypto_init(),parsed_cert=mbedtls_x509_crt_parse(&chain,certificate,cert_size+1U),parsed_key=mbedtls_pk_parse_key(&key,private_key,key_size+1U,NULL,0);int pair=parsed_cert||parsed_key?0:mbedtls_pk_check_pair(&chain.pk,&key);fprintf(stderr,"Provisioning failed: result=%d PSA=%d certificate=%d private-key-parser=%d pair=%d (no credential contents logged)\n",result,init,parsed_cert,parsed_key,pair);mbedtls_pk_free(&key);mbedtls_x509_crt_free(&chain);}
    assert(result==ESP_OK&&nvs_commits==1);
}

int main(int argc,char **argv){assert(argc==7);signal(SIGPIPE,SIG_IGN);size_t cert_size,key_size,other_size;uint8_t *cert=read_ephemeral(argv[1],&cert_size),*key=read_ephemeral(argv[2],&key_size),*other=read_ephemeral(argv[3],&other_size);size_t size,packed_size;uint8_t *good=bundle(cert,cert_size,key,key_size,&size),*packed=read_ephemeral(argv[5],&packed_size);assert(packed_size==size&&!memcmp(packed,good,size));require_provisioned(packed,packed_size,cert,cert_size,key,key_size);wipe(packed,packed_size);free(packed);size_t bad_size;uint8_t *bad=bundle(cert,cert_size,other,other_size,&bad_size);assert(native_web_transport_provision(bad,bad_size)==ESP_ERR_INVALID_ARG&&nvs_commits==1&&nvs_size==size&&!memcmp(nvs_blob,good,size));wipe(bad,bad_size);free(bad);
    // The same RSA key also exists in OpenSSL's default PKCS8 container. Both
    // pinned parsers accept it, but their strict pair check rejects the missing
    // derived public-key field. Keep that real limitation visible and verify
    // rejection cannot replace the already working PKCS1 identity.
    size_t pkcs8_size;uint8_t *pkcs8=read_ephemeral(argv[6],&pkcs8_size);mbedtls_x509_crt chain;mbedtls_pk_context pkcs8_context;mbedtls_x509_crt_init(&chain);mbedtls_pk_init(&pkcs8_context);assert(!mbedtls_x509_crt_parse(&chain,cert,cert_size+1U)&&!mbedtls_pk_parse_key(&pkcs8_context,pkcs8,pkcs8_size+1U,NULL,0));assert(mbedtls_pk_check_pair(&chain.pk,&pkcs8_context)!=0);mbedtls_pk_free(&pkcs8_context);mbedtls_x509_crt_free(&chain);bad=bundle(cert,cert_size,pkcs8,pkcs8_size,&bad_size);assert(native_web_transport_provision(bad,bad_size)==ESP_ERR_INVALID_ARG&&nvs_commits==1&&nvs_size==size&&!memcmp(nvs_blob,good,size));wipe(bad,bad_size);free(bad);wipe(pkcs8,pkcs8_size);free(pkcs8);
    wipe(other,other_size);free(other);wipe(key,key_size);free(key);wipe(cert,cert_size);free(cert);wipe(good,size);free(good);
    unsigned cases=1,want_reads=0,want_writes=0,partial_writes=0;
    const char *modes[]={"data","peer-close","untrusted","hostname","version","fatal","silent"};
    for(size_t mode=0;mode<sizeof(modes)/sizeof(modes[0]);++mode){httpd_config_t config={.stack_size=6144,.task_priority=5,.core_id=-1};assert(native_web_transport_prepare(&config)==ESP_OK&&native_web_transport_secure()&&config.server_port==443&&config.stack_size==10240&&config.max_open_sockets==3&&config.task_priority==5&&config.core_id==-1);unsigned port;int listening=listener(&port),control;pid_t child=start_client(port,argv[1],argv[4],modes[mode],&control);int fd=accept(listening,NULL,NULL);assert(fd>=0);close(listening);memset(&httpd,0,sizeof(httpd));httpd.socket=fd;int send_buffer=4096;assert(!setsockopt(fd,SOL_SOCKET,SO_SNDBUF,&send_buffer,sizeof(send_buffer)));int64_t started=esp_timer_get_time();esp_err_t result=config.open_fn(&httpd,fd);
        if(!strcmp(modes[mode],"untrusted")||!strcmp(modes[mode],"hostname")||!strcmp(modes[mode],"version")){assert(result!=ESP_OK&&httpd.transport&&!httpd.send);}
        else if(!strcmp(modes[mode],"silent")){assert(result==ESP_ERR_TIMEOUT&&esp_timer_get_time()-started>=2800000&&esp_timer_get_time()-started<6000000);}
        else{assert(result==ESP_OK&&httpd.send&&httpd.recv&&httpd.pending&&native_web_transport_release()==ESP_ERR_INVALID_STATE);assert(!strcmp(mbedtls_ssl_get_version(esp_tls_get_ssl_context(session(&httpd,fd)->tls)),"TLSv1.2"));
            if(!strcmp(modes[mode],"data")){uint8_t contents[257],peeked[4];bool writable;
                for(;;){ssize_t count=native_web_transport_recv(&httpd,fd,peeked,sizeof(peeked),MSG_PEEK,&writable);if(count==4)break;assert(count<0&&errno==EAGAIN&&!writable);++want_reads;ready_socket(fd,writable);}
                for(unsigned index=0;index<4;++index)assert(peeked[index]==index);
                assert(httpd.pending(&httpd,fd)==4&&native_web_transport_recv(&httpd,fd,contents,2,MSG_PEEK,&writable)==2&&contents[0]==0&&contents[1]==1);
                assert(native_web_transport_recv(&httpd,fd,contents,2,0,&writable)==2&&httpd.pending(&httpd,fd)==2);
                assert(native_web_transport_recv(&httpd,fd,contents+2,2,0,&writable)==2&&httpd.pending(&httpd,fd)==253);
                receive_exact(fd,contents+4,253);for(unsigned index=0;index<257;++index)assert(contents[index]==(uint8_t)index);
                assert(native_web_transport_recv(&httpd,fd,peeked,1,0,&writable)==-1&&errno==EAGAIN&&!writable);++want_reads;
                uint8_t *payload=malloc(131072);assert(payload);for(size_t index=0;index<131072;++index)payload[index]=(uint8_t)(index%251U);size_t sent=0;bool released=false;
                while(sent<131072){ssize_t count=native_web_transport_send(&httpd,fd,payload+sent,131072-sent,0,&writable);if(count>0){if((size_t)count<131072-sent)++partial_writes;sent+=(size_t)count;}else{assert(count<0&&errno==EAGAIN&&writable);++want_writes;if(!released){assert(write(control,"R",1)==1);released=true;}ready_socket(fd,writable);}}
                assert(released&&partial_writes&&want_writes);free(payload);assert(httpd.send(&httpd,fd,"TAIL",4,0)==4);char ack[3];assert(httpd.recv(&httpd,fd,ack,sizeof(ack),0)==3&&!memcmp(ack,"ACK",3));native_web_transport_shutdown(&httpd,fd,true);}
            else if(!strcmp(modes[mode],"peer-close")){char peer[4];receive_exact(fd,peer,4);assert(!memcmp(peer,"PEER",4));bool writable;for(;;){char byte;ssize_t count=native_web_transport_recv(&httpd,fd,&byte,1,0,&writable);if(!count)break;assert(count<0&&errno==EAGAIN);ready_socket(fd,writable);}native_web_transport_shutdown(&httpd,fd,true);}
            else{char ready[5];receive_exact(fd,ready,5);assert(!memcmp(ready,"READY",5));native_web_transport_shutdown(&httpd,fd,false);}
        }
        finish_session(&config,fd);close(control);int status;assert(waitpid(child,&status,0)==child&&WIFEXITED(status)&&WEXITSTATUS(status)==0);++cases;
    }
    assert(want_reads&&want_writes&&partial_writes&&read_waits);wipe(nvs_blob,nvs_size);free(nvs_blob);nvs_blob=NULL;nvs_size=0;mbedtls_psa_crypto_free();
    printf("PASS real TLS: %u cases; %s, trusted OpenSSL TLS1.2 client/hostname verification, real PK mismatch and matching PKCS8 rejection without NVS mutation, WANT_READ=%u/WANT_WRITE=%u/partial=%u, binary peek/pending/data, both close_notify directions, fatal raw EOF, handshake timeout, one HTTPD fd close\n",cases,MBEDTLS_VERSION_STRING_FULL,want_reads,want_writes,partial_writes);return 0;}
