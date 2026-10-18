/* Actual SDK HTTP parser, all HTTPD parse callbacks/read pipeline, pending RX
 * functions and WS handshake/frame functions; only platform/network seams. */
#define NATIVE_TEST_WIRE 1
#define main native_function_suite_main
#include "test_host.c"
#undef main

#define PARSER_BLOCK_SIZE 128
#define HTTP_SERVER_EVENT_ON_HEADER 1
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
#define HTTPD_SOCK_ERR_FAIL (-2)
#define HTTPD_400_BAD_REQUEST 400
#define HTTPD_408_REQ_TIMEOUT 408
#define HTTPD_413_CONTENT_TOO_LARGE 413
#define HTTPD_414_URI_TOO_LONG 414
#define HTTPD_431_REQ_HDR_FIELDS_TOO_LARGE 431
#define HTTPD_500_INTERNAL_SERVER_ERROR 500
#define HTTPD_501_METHOD_NOT_IMPLEMENTED 501
#define HTTPD_505_VERSION_NOT_SUPPORTED 505
typedef int httpd_err_code_t;
static unsigned wire_cases;
static bool inspect_fold;
static bool plain_request;
static size_t plain_length;
static int httpd_uri(struct httpd_data *hd);
static int httpd_req_handle_err(httpd_req_t *req,int code) {
    (void)req;snprintf(response_status,sizeof(response_status),"%d",code);return ESP_FAIL;
}
static void esp_http_server_dispatch_event(int event,const void *data,size_t size) {
    assert(event==HTTP_SERVER_EVENT_ON_HEADER&&size==sizeof(int)&&*(const int *)data==42);
}
#include "parser-functions.inc"

static int httpd_uri(struct httpd_data *hd) {
    httpd_req_t *req=&hd->hd_req;
    if(plain_request){
        assert(req->method==HTTP_GET&&!strcmp(req->uri,"/plain")&&!aux.ws_handshake_detect);
        assert(req->content_len==plain_length&&aux.remaining_len==plain_length);
        native_httpd_headers_t hs=native_httpd_headers(req);native_httpd_header_t item;bool found=false;
        const char expected[]=" first\r\n second";
        while(native_httpd_next_header(&hs,&item)==1){
            if(native_httpd_header_is(&item,"X-Test")){
                assert((size_t)(item.end-item.value)==sizeof(expected)-1&&!memcmp(item.value,expected,sizeof(expected)-1));found=true;}
        }
        assert(found);return ESP_OK;
    }
    if(req->method!=HTTP_GET||strcmp(req->uri,"/ws")||!aux.ws_handshake_detect)
        return httpd_req_handle_err(req,400);
    if(inspect_fold){
        native_httpd_headers_t hs=native_httpd_headers(req);native_httpd_header_t item;bool found=false;
        const char expected[]=" permessage-deflate;\r\n client_max_window_bits = \"15\"";
        while(native_httpd_next_header(&hs,&item)==1){
            if(native_httpd_header_is(&item,"Sec-WebSocket-Extensions")){
                assert((size_t)(item.end-item.value)==sizeof(expected)-1 &&
                    !memcmp(item.value,expected,sizeof(expected)-1) && "SDK parser truncated folded field");found=true;}
        }
        assert(found);
    }
    int result=httpd_ws_respond_server_handshake(req,NULL);
    if(result==ESP_OK)session.ws_handshake_done=true;
    return result;
}

static void wire_case(const char *request,bool expected,int status) {
    const size_t size=strlen(request);
    assert(size+7<=sizeof(input));
    /* Every receive split position, including one byte per network read. The
     * actual HTTPD read_block() still imposes its independent 128-byte bound. */
    for(size_t step=1;step<=size+7;++step){
        httpd_req_t *req=reset();session.ws_handshake_done=false;
        aux.max_uri_len=512;aux.max_req_hdr_len=1024;aux.scratch_size_limit=aux.max_uri_len;
        socket_step=step;
        memcpy(input,request,size);input_size=size;
        /* First masked PING arrives in the same transport input as upgrade.
         * Its preservation exercises actual SDK pause/unrecv/pending RX. */
        const uint8_t ping[]={0x89,0x81,0x11,0x22,0x33,0x44,'z'^0x11};
        memcpy(input+input_size,ping,sizeof(ping));input_size+=sizeof(ping);
        bool ok=httpd_parse_req(&server)==ESP_OK;
        if(ok!=expected){
            fprintf(stderr,"wire mismatch step=%zu expected=%d status=%s\n%s",step,expected,response_status,request);
            native_httpd_headers_t hs=native_httpd_headers(req);native_httpd_header_t item;
            while(native_httpd_next_header(&hs,&item)==1){
                fprintf(stderr,"\nFIELD %.*s: ",(int)item.name_length,item.name);
                for(const char *p=item.value;p<item.end;++p){
                    unsigned char c=(unsigned char)*p;if(c<32||c>126)fprintf(stderr,"<%u>",c);else fputc(c,stderr);}
            }
            fputc('\n',stderr);abort();
        }
        if(expected){
            output[output_size]=0;
            assert(strstr((char *)output,"HTTP/1.1 101 Switching Protocols\r\n"));
            assert(strstr((char *)output,"Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n"));
            assert(!strstr((char *)output,"Sec-WebSocket-Protocol:")&&!strstr((char *)output,"Sec-WebSocket-Extensions:"));
            assert(httpd_ws_get_frame_type(req)==ESP_OK);
            uint8_t payload[125];httpd_ws_frame_t frame={.payload=payload};
            assert(httpd_ws_recv_frame(req,&frame,sizeof(payload))==ESP_OK);
            assert(frame.final&&frame.type==HTTPD_WS_TYPE_PING&&frame.len==1&&payload[0]=='z');
            assert(input_offset==input_size&&!session.pending_len);
        }else{
            assert(!output_size);
            if(status)assert(atoi(response_status)==status);
            if(status==426)assert(!strcmp(response_version,"13"));
        }
        free(aux.scratch);aux.scratch=NULL;++wire_cases;
    }
}

static void make_request(char *out,size_t cap,const char *method,const char *version,
                          const char *host,const char *ws_version,const char *key,
                          const char *upgrade,const char *connection,const char *extra) {
    int n=snprintf(out,cap,"%s /ws HTTP/%s\r\n%s%s%s%s%s%s%s\r\n",method,version,host,ws_version,key,upgrade,connection,extra,"");
    assert(n>0&&(size_t)n<cap);
}
#define HOST "Host: fixture.invalid\r\n"
#define VERSION "Sec-WebSocket-Version: 13\r\n"
#define KEY "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
#define UPGRADE "Upgrade: websocket\r\n"
#define CONNECTION "Connection: Upgrade\r\n"
int main(int argc,char **argv) {
    char request[1536];
    if(argc>1){
        inspect_fold=!strcmp(argv[1],"fold");
        const char *extra=!strcmp(argv[1],"empty-length")?"Content-Length: \r\n":
            inspect_fold?"Sec-WebSocket-Extensions: permessage-deflate;\r\n client_max_window_bits = \"15\"\r\n":
            !strcmp(argv[1],"extensions")?"Sec-WebSocket-Extensions: permessage-deflate; p=\"two words\"\r\n":
            "Sec-WebSocket-Protocol: chat, superchat, chat\r\n";
        make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,CONNECTION,extra);
        wire_case(request,inspect_fold,inspect_fold?0:400);return 0;
    }
    const char *good[]={
        "", "Sec-WebSocket-Protocol: chat, superchat\r\n",
        "Sec-WebSocket-Protocol: chat\r\nSec-WebSocket-Protocol: Chat,superchat\r\n",
        "Sec-WebSocket-Protocol: chat,\r\n superchat\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits=15\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate;\r\n client_max_window_bits = \"15\"\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate\r\nSec-WebSocket-Extensions: private-extension; flag\r\n",
        "Sec-WebSocket-Extensions: private-extension; p=\"a\\-b\"\r\n",
        "Sec-WebSocket-Protocol: , chat ,, superchat,\r\n",
        "Sec-WebSocket-Extensions: , permessage-deflate ,, private-extension,\r\n"
    };
    for(size_t i=0;i<sizeof(good)/sizeof(*good);++i){
        make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,CONNECTION,good[i]);wire_case(request,true,0);
    }
    const char *bad[]={
        "Sec-WebSocket-Protocol:\r\n", "Sec-WebSocket-Protocol: , ,\r\n", "Sec-WebSocket-Protocol: chat,chat\r\n",
        "Sec-WebSocket-Protocol: chat\r\nSec-WebSocket-Protocol: superchat,chat\r\n",
        "Sec-WebSocket-Protocol: \"chat\"\r\n", "Sec-WebSocket-Protocol: chat,super chat\r\n",
        "Sec-WebSocket-Protocol: chat; x=1\r\n", "Sec-WebSocket-Protocol: chat/2\r\n",
        "Sec-WebSocket-Extensions:\r\n", "Sec-WebSocket-Extensions: , ,\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; p=\"two words\"\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; p=\"\"\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; p=\"a\\\\b\"\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; p=\"a\\\"b\"\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; p=\"done\"oops\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; p=\"broken\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; p=\"\xc3\xb6\"\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate;\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; =value\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; p=\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate; p=value/other\r\n",
        "Sec-WebSocket-Extensions: permessage-deflate\r\nSec-WebSocket-Extensions: private-extension; p=\r\n",
        "Sec-WebSocket-Version: 13\r\n", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n", "Host: fixture.invalid\r\n"
    };
    for(size_t i=0;i<sizeof(bad)/sizeof(*bad);++i){
        make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,CONNECTION,bad[i]);wire_case(request,false,400);
    }
    make_request(request,sizeof(request),"GET","1.0",HOST,VERSION,KEY,UPGRADE,CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","2.0",HOST,VERSION,KEY,UPGRADE,CONNECTION,"");wire_case(request,false,505);
    make_request(request,sizeof(request),"POST","1.1",HOST,VERSION,KEY,UPGRADE,CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1","",VERSION,KEY,UPGRADE,CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,"",KEY,UPGRADE,CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,"",UPGRADE,CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,"",CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,"","");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,"Sec-WebSocket-Version: 12\r\n",KEY,UPGRADE,CONNECTION,"");wire_case(request,false,426);
    make_request(request,sizeof(request),"GET","1.1",HOST,"Sec-WebSocket-Version: 013\r\n",KEY,UPGRADE,CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,"Sec-WebSocket-Version: 256\r\n",KEY,UPGRADE,CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,"Sec-WebSocket-Key: invalid\r\n",UPGRADE,CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1","Host: user@fixture.invalid\r\n",VERSION,KEY,UPGRADE,CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,"Upgrade: h2c/1, WebSocket\r\n","Connection: keep-alive, Upgrade\r\n","");wire_case(request,true,0);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,"Upgrade: h2c\r\nUpgrade: WebSocket\r\n","Connection: keep-alive\r\nConnection: Upgrade\r\n","");wire_case(request,true,0);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,"Connection: keep-alive,\r\n Upgrade\r\n","");wire_case(request,true,0);
    make_request(request,sizeof(request),"GET","1.1",HOST,"Sec-WebSocket-Version:\r\n 13 \t\r\n","Sec-WebSocket-Key:\r\n dGhlIHNhbXBsZSBub25jZQ== \t\r\n",UPGRADE,CONNECTION,"");wire_case(request,true,0);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,"Upgrade: WebSocket, websocket/13\r\n",CONNECTION,"");wire_case(request,true,0);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,"Upgrade: websocket/13\r\n",CONNECTION,"");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,"Connection: Upgrade, broken@token\r\n","");wire_case(request,false,400);
    const char *bad_lengths[]={"-1","+1","1x","", "18446744073709551615", "18446744073709551616"};
    for(size_t i=0;i<sizeof(bad_lengths)/sizeof(*bad_lengths);++i){
        char extra[128];snprintf(extra,sizeof(extra),"Content-Length: %s\r\n",bad_lengths[i]);
        make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,CONNECTION,extra);wire_case(request,false,400);
    }
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,CONNECTION,"Content-Length: 0\r\nContent-Length: 0\r\n");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,CONNECTION,"Content-Length: 0\r\nContent-Length: 1\r\n");wire_case(request,false,400);
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,CONNECTION,"Content-Length: 4294967296\r\n");wire_case(request,false,413);
    inspect_fold=true;
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,CONNECTION,
        "Sec-WebSocket-Extensions: permessage-deflate;\r\n client_max_window_bits = \"15\"\r\n");wire_case(request,true,0);
    inspect_fold=false;
    char oversized[1080];
    strcpy(oversized,"Sec-WebSocket-Protocol: ");size_t prefix=strlen(oversized);
    memset(oversized+prefix,'a',1000);strcpy(oversized+prefix+1000,"\r\n");
    make_request(request,sizeof(request),"GET","1.1",HOST,VERSION,KEY,UPGRADE,CONNECTION,oversized);wire_case(request,false,431);
    /* The parser overlay also serves ordinary HTTP requests: preserve folded
     * fields and the SDK's existing HTTP/1.0 compatibility outside upgrades. */
    plain_request=true;
    plain_length=0;
    for(unsigned minor=0;minor<=1;++minor){
        int n=snprintf(request,sizeof(request),"GET /plain HTTP/1.%u\r\nHost: fixture.invalid\r\nX-Test: first\r\n second\r\n\r\n",minor);
        assert(n>0&&(size_t)n<sizeof(request));
        for(size_t step=1;step<=(size_t)n;++step){
            reset();session.ws_handshake_done=false;aux.max_uri_len=512;aux.max_req_hdr_len=1024;aux.scratch_size_limit=512;
            socket_step=step;memcpy(input,request,(size_t)n);input_size=(size_t)n;
            assert(httpd_parse_req(&server)==ESP_OK&&!output_size);
            free(aux.scratch);aux.scratch=NULL;++wire_cases;
        }
    }
    const uint64_t lengths[]={0,1,UINT64_C(2147483648),UINT32_MAX};
    for(size_t i=0;i<sizeof(lengths)/sizeof(*lengths);++i){
        plain_length=(size_t)lengths[i];
        int n=snprintf(request,sizeof(request),"GET /plain HTTP/1.1\r\nHost: fixture.invalid\r\nX-Test: first\r\n second\r\nContent-Length: %llu\r\n\r\n%s",
            (unsigned long long)lengths[i],lengths[i]?"x":"");
        assert(n>0&&(size_t)n<sizeof(request));
        for(size_t step=1;step<=(size_t)n;++step){
            reset();session.ws_handshake_done=false;aux.max_uri_len=512;aux.max_req_hdr_len=1024;aux.scratch_size_limit=512;
            socket_step=step;memcpy(input,request,(size_t)n);input_size=(size_t)n;
            assert(httpd_parse_req(&server)==ESP_OK&&!output_size);
            free(aux.scratch);aux.scratch=NULL;++wire_cases;
        }
    }
    printf("PASS whole SDK HTTP parser: %u receive split checks; handshake plus first frame and folded values preserved\n",wire_cases);
    return 0;
}
