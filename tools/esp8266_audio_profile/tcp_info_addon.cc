// Read-only TCP_INFO for sockets owned by this Node event loop. No private
// Node/V8 pointers, foreign-process access, socket duplication or option writes.
#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <mstcpip.h>
#include <node_api.h>
#include <uv.h>
#include <stddef.h>

static_assert(sizeof(TCP_INFO_v0)==88, "Unexpected Windows TCP_INFO_v0 layout");
struct Walk { napi_env env; napi_value rows; uint32_t port, count; };
static void number(Walk *w,napi_value row,const char *key,double value) {
    napi_value v; napi_create_double(w->env,value,&v);
    napi_set_named_property(w->env,row,key,v);
}
static void sample(uv_handle_t *handle,void *opaque) {
    Walk *w=static_cast<Walk *>(opaque);
    if(handle->type!=UV_TCP||uv_is_closing(handle))return;
    sockaddr_in local={},peer={};int length=sizeof(local);
    if(uv_tcp_getsockname(reinterpret_cast<uv_tcp_t *>(handle),
            reinterpret_cast<sockaddr *>(&local),&length)||local.sin_family!=AF_INET||ntohs(local.sin_port)!=w->port)return;
    length=sizeof(peer);
    if(uv_tcp_getpeername(reinterpret_cast<uv_tcp_t *>(handle),
            reinterpret_cast<sockaddr *>(&peer),&length)||peer.sin_family!=AF_INET)return;
    uv_os_fd_t descriptor;
    if(uv_fileno(handle,&descriptor))return;
    napi_value row;napi_create_object(w->env,&row);
    number(w,row,"local_port",ntohs(local.sin_port));number(w,row,"peer_port",ntohs(peer.sin_port));
    char address[INET_ADDRSTRLEN]={};uv_ip4_name(&peer,address,sizeof(address));
    napi_value ip;napi_create_string_utf8(w->env,address,NAPI_AUTO_LENGTH,&ip);
    napi_set_named_property(w->env,row,"peer_address",ip);
    DWORD version=0,returned=0;TCP_INFO_v0 info={};
    int result=WSAIoctl(reinterpret_cast<SOCKET>(descriptor),SIO_TCP_INFO,
        &version,sizeof(version),&info,sizeof(info),&returned,nullptr,nullptr);
    if(result||returned!=sizeof(info))number(w,row,"error",result?WSAGetLastError():-1);
    else {
        number(w,row,"mss",info.Mss);number(w,row,"rtt_us",info.RttUs);
        number(w,row,"min_rtt_us",info.MinRttUs);number(w,row,"in_flight",info.BytesInFlight);
        number(w,row,"cwnd",info.Cwnd);number(w,row,"snd_wnd",info.SndWnd);
        number(w,row,"bytes_out",static_cast<double>(info.BytesOut));
        number(w,row,"bytes_in",static_cast<double>(info.BytesIn));
        number(w,row,"bytes_retrans",info.BytesRetrans);number(w,row,"fast_retrans",info.FastRetrans);
        number(w,row,"dup_acks",info.DupAcksIn);number(w,row,"rto_episodes",info.TimeoutEpisodes);
    }
    napi_set_element(w->env,w->rows,w->count++,row);
}
static napi_value read(napi_env env,napi_callback_info cb) {
    size_t count=1;napi_value arg;uint32_t port=0;
    if(napi_get_cb_info(env,cb,&count,&arg,nullptr,nullptr)!=napi_ok||count!=1||
       napi_get_value_uint32(env,arg,&port)!=napi_ok||port<1||port>65535) {
        napi_throw_type_error(env,nullptr,"Expected local TCP port 1..65535");return nullptr;
    }
    Walk walk={env,nullptr,port,0};uv_loop_t *loop=nullptr;
    if(napi_create_array(env,&walk.rows)!=napi_ok||napi_get_uv_event_loop(env,&loop)!=napi_ok)return nullptr;
    uv_walk(loop,sample,&walk);return walk.rows;
}
static napi_value keep_awake(napi_env env,napi_callback_info cb) {
    size_t count=1;napi_value arg;bool enable=false;
    if(napi_get_cb_info(env,cb,&count,&arg,nullptr,nullptr)!=napi_ok||count!=1||
       napi_get_value_bool(env,arg,&enable)!=napi_ok) {
        napi_throw_type_error(env,nullptr,"Expected keep-awake boolean");return nullptr;
    }
    EXECUTION_STATE previous=SetThreadExecutionState(ES_CONTINUOUS|(enable?ES_SYSTEM_REQUIRED:0));
    napi_value result;napi_get_boolean(env,previous!=0,&result);return result;
}
static napi_value init(napi_env env,napi_value exports) {
    napi_value fn;napi_create_function(env,"sample",NAPI_AUTO_LENGTH,read,nullptr,&fn);
    napi_set_named_property(env,exports,"sample",fn);
    napi_create_function(env,"keepAwake",NAPI_AUTO_LENGTH,keep_awake,nullptr,&fn);
    napi_set_named_property(env,exports,"keepAwake",fn);return exports;
}
NAPI_MODULE(NODE_GYP_MODULE_NAME,init)
