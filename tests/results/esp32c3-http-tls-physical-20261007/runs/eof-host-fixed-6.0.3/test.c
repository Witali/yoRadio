#include <assert.h>
#include <errno.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include "stream_http_reader.h"
#include "esp_tls_errors.h"
#include "http_parser.h"
#include "mbedtls/ssl.h"

enum { ERR_TCP_TRANSPORT_CONNECTION_FAILED=-2,
       ERR_TCP_TRANSPORT_CONNECTION_CLOSED_BY_FIN=-1,
       ERR_TCP_TRANSPORT_CONNECTION_TIMEOUT=0,
       ESP_LOG_WARN, ESP_LOG_DEBUG, HTTP_EVENT_ERROR, HTTP_EVENT_ON_DATA, HTTP_STATE_RES_ON_DATA_START };
typedef int esp_log_level_t;
#define TAG "http"
#define ESP_LOGD(tag,...) do { if(0)printf(__VA_ARGS__); } while(0)
#define ESP_LOGE(tag,...) ESP_LOGD(tag,__VA_ARGS__)
#define ESP_LOG_LEVEL(level,tag,...) do { (void)(level);ESP_LOGD(tag,__VA_ARGS__); } while(0)
typedef struct { char data[256], *raw_data, *orig_raw_data, *output_ptr; int raw_len; } esp_http_buffer_t;
typedef struct { esp_http_buffer_t *buffer; bool is_chunked; int64_t data_process, content_length; } response_t;
typedef struct { int bytes, tls_error; const char *data; } step_t;
typedef struct fake_client esp_http_client_t;
typedef struct { int64_t data_process; esp_http_client_handle_t client; } esp_http_client_on_data_t;
struct fake_client {
    response_t *response;
    bool is_chunk_complete;
    int buffer_size_rx, timeout_ms;
    struct fake_client *transport;
    http_parser parser_storage, *parser;
    http_parser_settings settings_storage, *parser_settings;
    step_t steps[256];
    bool cache_data_in_fetch_hdr;
    int state;
    unsigned next, calls, events, error_queries, closes;
    int tls_error, tls_code;
};
static void esp_http_client_cached_buf_cleanup(esp_http_buffer_t *b) { b->raw_data=NULL; }
bool esp_http_client_is_complete_data_received(esp_http_client_handle_t client)
{
    if (client->response->is_chunked) {
        if (!client->is_chunk_complete) {
            ESP_LOGD(TAG, "Chunks were not completely read");
            return false;
        }
    } else {
        if (client->response->data_process != client->response->content_length) {
            ESP_LOGD(TAG, "Data processed %"PRId64" != Data specified in content length %"PRId64, client->response->data_process, client->response->content_length);
            return false;
        }
    }
    return true;
}


static int esp_transport_read(struct fake_client *c,char *buffer,int size,int timeout) {
    (void)timeout;++c->calls;assert(!c->closes && c->next<256);
    step_t step=c->steps[c->next++];assert(step.bytes<=size);
    if(step.bytes>0) {
        if(step.data)memcpy(buffer,step.data,(size_t)step.bytes);
        else memset(buffer,0x4b,(size_t)step.bytes);
    }
    if(step.tls_error) {c->tls_error=ESP_ERR_MBEDTLS_SSL_READ_FAILED;c->tls_code=step.tls_error;}
    return step.bytes;
}
esp_err_t esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t c,int *code,int *flags) {
    ++c->error_queries;if(code)*code=c->tls_code;if(flags)*flags=0;
    int result=c->tls_error;c->tls_error=c->tls_code=0;return result;
}
esp_err_t esp_http_client_close(esp_http_client_handle_t c) { ++c->closes; return ESP_OK; }
static int esp_transport_translate_error(int error) {return error;}
static const char *esp_err_to_name(int error) {(void)error;return "test";}
static void *esp_transport_get_error_handle(void *c) {return c;}
static void http_dispatch_event(esp_http_client_handle_t c,int event,void *data,int size) {
    (void)event;(void)data;(void)size;++c->events;
}
static void http_dispatch_event_to_event_loop(int event,void *data,size_t size) {
    (void)event;(void)data;(void)size;
}

static int http_on_body(http_parser *parser, const char *at, size_t length)
{
    esp_http_client_t *client = parser->data;
    ESP_LOGD(TAG, "http_on_body %zu", length);

    if (client->response->buffer->output_ptr) {
        memcpy(client->response->buffer->output_ptr, (char *)at, length);
        client->response->buffer->output_ptr += length;
    } else {
        /* Do not cache body when http_on_body is called from esp_http_client_perform */
        if (client->state < HTTP_STATE_RES_ON_DATA_START && client->cache_data_in_fetch_hdr) {
            ESP_LOGD(TAG, "Body received in fetch header state, %p, %zu", at, length);
            esp_http_buffer_t *res_buffer = client->response->buffer;
            assert(res_buffer->orig_raw_data == res_buffer->raw_data);
            char *tmp = (char *)realloc(res_buffer->orig_raw_data, res_buffer->raw_len + length);
            if (tmp == NULL) {
                ESP_LOGE(TAG, "Failed to allocate memory for storing decoded data");
                free(res_buffer->orig_raw_data);
                res_buffer->orig_raw_data = NULL;
                res_buffer->raw_data = NULL;
                return -1;
            }
            res_buffer->orig_raw_data = tmp;
            memcpy(res_buffer->orig_raw_data + res_buffer->raw_len, at, length);
            res_buffer->raw_data = res_buffer->orig_raw_data;
        }
    }

    client->response->data_process += length;
    client->response->buffer->raw_len += length;
    http_dispatch_event(client, HTTP_EVENT_ON_DATA, (void *)at, length);
    esp_http_client_on_data_t evt_data = {};
    evt_data.data_process = client->response->data_process;
    evt_data.client = client;
    http_dispatch_event_to_event_loop(HTTP_EVENT_ON_DATA, &evt_data, sizeof(esp_http_client_on_data_t));
    return 0;
}

static int http_on_message_complete(http_parser *parser)
{
    ESP_LOGD(TAG, "http_on_message_complete, parser=%p", parser);
    esp_http_client_handle_t client = parser->data;
    client->is_chunk_complete = true;
    return 0;
}



static int on_headers(http_parser *p) {
    struct fake_client *c=p->data;
    c->response->content_length=(int64_t)p->content_length;
    // esp_http_client_fetch_headers also uses is_chunked for close-delimited
    // bodies. This seam covers framing, not the SDK's header-name callbacks.
    c->response->is_chunked=(p->flags & F_CHUNKED) || c->response->content_length<=0;
    return 0;
}
static void setup_headers(struct fake_client *c,response_t *r,esp_http_buffer_t *b,const char *headers) {
    memset(c,0,sizeof(*c));memset(r,0,sizeof(*r));memset(b,0,sizeof(*b));
    r->buffer=b;c->response=r;c->transport=c;c->buffer_size_rx=sizeof(b->data);
    c->parser=&c->parser_storage;c->parser_settings=&c->settings_storage;
    http_parser_init(c->parser,HTTP_RESPONSE);c->parser->data=c;
    c->settings_storage.on_headers_complete=on_headers;
    c->settings_storage.on_body=http_on_body;
    c->settings_storage.on_message_complete=http_on_message_complete;
    assert(http_parser_execute(c->parser,c->parser_settings,headers,strlen(headers))==strlen(headers));
    assert(HTTP_PARSER_ERRNO(c->parser)==HPE_OK);
}
static void setup(struct fake_client *c,response_t *r,esp_http_buffer_t *b) {
    setup_headers(c,r,b,"HTTP/1.1 200 OK\r\nContent-Length: 100000\r\n\r\n");
}

int esp_http_client_read(esp_http_client_handle_t client, char *buffer, int len)
{
    esp_http_buffer_t *res_buffer = client->response->buffer;

    int rlen = ESP_FAIL, ridx = 0;
    if (res_buffer->raw_len) {
        int remain_len = client->response->buffer->raw_len;
        if (remain_len > len) {
            remain_len = len;
        }
        memcpy(buffer, res_buffer->raw_data, remain_len);
        res_buffer->raw_len -= remain_len;
        res_buffer->raw_data += remain_len;
        ridx = remain_len;
        if (res_buffer->raw_len == 0) {
            esp_http_client_cached_buf_cleanup(res_buffer);
        }
    }
    int need_read = len - ridx;
    bool is_data_remain = true;
    while (need_read > 0 && is_data_remain) {
        if (client->response->is_chunked) {
            is_data_remain = !client->is_chunk_complete;
        } else {
            is_data_remain = client->response->data_process < client->response->content_length;
        }
        ESP_LOGD(TAG, "is_data_remain=%d, is_chunked=%d, content_length=%"PRId64, is_data_remain, client->response->is_chunked, client->response->content_length);
        if (!is_data_remain) {
            break;
        }
        int byte_to_read = need_read;
        if (byte_to_read > client->buffer_size_rx) {
            byte_to_read = client->buffer_size_rx;
        }
        errno = 0;
        rlen = esp_transport_read(client->transport, res_buffer->data, byte_to_read, client->timeout_ms);
        ESP_LOGD(TAG, "need_read=%d, byte_to_read=%d, rlen=%d, ridx=%d", need_read, byte_to_read, rlen, ridx);

        if (rlen <= 0) {
            esp_log_level_t sev = ESP_LOG_WARN;
            /* Check for cleanly closed connection */
            if (rlen == ERR_TCP_TRANSPORT_CONNECTION_CLOSED_BY_FIN && client->response->is_chunked) {
                /* Explicit call to parser for invoking `message_complete` callback */
                http_parser_execute(client->parser, client->parser_settings, res_buffer->data, 0);
                /* ...and lowering the message severity, as closed connection from server side is expected in chunked transport */
                sev = ESP_LOG_DEBUG;
            }
            if (errno != 0) {
                ESP_LOG_LEVEL(sev, TAG, "esp_transport_read returned:%d and errno:%d ", rlen, errno);
            }

            if (rlen == ERR_TCP_TRANSPORT_CONNECTION_TIMEOUT) {
                ESP_LOGD(TAG, "Connection timed out before data was ready!");
                /* Returning the number of bytes read upto the point where connection timed out */
                if (ridx) {
                    return ridx;
                }
                return -ESP_ERR_HTTP_EAGAIN;
            }

            if (rlen != ERR_TCP_TRANSPORT_CONNECTION_CLOSED_BY_FIN) {
                esp_err_t err = esp_transport_translate_error(rlen);
                ESP_LOGE(TAG, "transport_read: error - %d | %s", err, esp_err_to_name(err));
            }

            if (rlen < 0 && ridx == 0 && !esp_http_client_is_complete_data_received(client)) {
                http_dispatch_event(client, HTTP_EVENT_ERROR, esp_transport_get_error_handle(client->transport), 0);
                http_dispatch_event_to_event_loop(HTTP_EVENT_ERROR, &client, sizeof(esp_http_client_handle_t));
                return ESP_FAIL;
            }
            return ridx;
        }
        res_buffer->output_ptr = buffer + ridx;
        http_parser_execute(client->parser, client->parser_settings, res_buffer->data, rlen);
        ridx += res_buffer->raw_len;
        need_read -= res_buffer->raw_len;

        res_buffer->raw_len = 0; //clear
        res_buffer->output_ptr = NULL;
    }

    return ridx;
}


// The actual ESP-TLS adapter, with TLS cryptography represented by a scripted
// mbedTLS result. Exercise the current TLS 1.2 configuration explicitly.
typedef struct { int esp_error, tls_code; } test_tls_error_t;
typedef struct { int ssl; test_tls_error_t *error_handle; } esp_tls_t;
enum { ESP_TLS_ERR_TYPE_MBEDTLS, ESP_TLS_ERR_TYPE_ESP };
#define NEWLIB_NANO_SSIZE_T_COMPAT_FORMAT "zx"
#define ESP_INT_EVENT_TRACKER_CAPTURE(handle,kind,value) do { \
    if((kind)==ESP_TLS_ERR_TYPE_ESP)(handle)->esp_error=(value); \
    else (handle)->tls_code=(value); \
} while(0)
static bool preserve_tls_eof;
int mbedtls_ssl_read(mbedtls_ssl_context *ssl,unsigned char *data,size_t size) { (void)data;(void)size;return *ssl; }
static int adapter_mbedtls_ssl_read(mbedtls_ssl_context *ssl,unsigned char *data,size_t size) {
    return preserve_tls_eof ? yoradio_mbedtls_ssl_read(ssl,data,size) : mbedtls_ssl_read(ssl,data,size);
}
static void mbedtls_print_error_msg(int error) { (void)error; }
#define mbedtls_ssl_read adapter_mbedtls_ssl_read
ssize_t esp_mbedtls_read(esp_tls_t *tls, char *data, size_t datalen)
{

    ssize_t ret = mbedtls_ssl_read(&tls->ssl, (unsigned char *)data, datalen);
#if defined(CONFIG_MBEDTLS_SSL_PROTO_TLS1_3)
    /*
     * As per RFC 8446, section 4.6.1 the server may send a NewSessionTicket message at any time after the
     * client Finished message.
     * If a post-handshake message is received, connection state is changed to `MBEDTLS_SSL_TLS1_3_NEW_SESSION_TICKET`
     * Call mbedtls_ssl_read() till state is `MBEDTLS_SSL_TLS1_3_NEW_SESSION_TICKET` or return code is `MBEDTLS_ERR_SSL_RECEIVED_NEW_SESSION_TICKET`
     * to process session tickets in TLS 1.3 connection.
     * This handshake message should be processed by mbedTLS and not by the application.
     */
    if (mbedtls_ssl_get_version_number(&tls->ssl) == MBEDTLS_SSL_VERSION_TLS1_3) {
        while (ret == MBEDTLS_ERR_SSL_RECEIVED_NEW_SESSION_TICKET || tls->ssl.MBEDTLS_PRIVATE(state) == MBEDTLS_SSL_TLS1_3_NEW_SESSION_TICKET) {
            ESP_LOGD(TAG, "got session ticket in TLS 1.3 connection, retry read");
#if CONFIG_ESP_TLS_CLIENT_SESSION_TICKETS
            if (ret == MBEDTLS_ERR_SSL_RECEIVED_NEW_SESSION_TICKET) {
                esp_tls_client_session_t *tls13_saved_client_session = calloc(1, sizeof(esp_tls_client_session_t));
                if (tls13_saved_client_session == NULL) {
                    ESP_LOGE(TAG, "Failed to allocate memory for client session ctx");
                    return ESP_ERR_NO_MEM;
                }

                ret = mbedtls_ssl_get_session(&tls->ssl, &tls13_saved_client_session->saved_session);
                if (ret != 0) {
                    ESP_LOGE(TAG, "Error in getting the client ssl session");
                    free(tls13_saved_client_session);
                    tls13_saved_client_session = NULL;
                    return ESP_ERR_MBEDTLS_SSL_HANDSHAKE_FAILED;
                }
                ESP_LOGD(TAG, "Session ticket received");

                size_t session_ticket_len = 0;
                ret = mbedtls_ssl_session_save(&tls13_saved_client_session->saved_session, NULL, 0, &session_ticket_len);
                if (ret != MBEDTLS_ERR_SSL_BUFFER_TOO_SMALL) {
                    ESP_LOGE(TAG, "Error in getting the client ssl session length");
                    free(tls13_saved_client_session);
                    tls13_saved_client_session = NULL;
                    return ESP_ERR_MBEDTLS_SSL_HANDSHAKE_FAILED;
                }

                ESP_LOGD(TAG, "Session ticket length: %zu", session_ticket_len);
                if (tls->client_session != NULL) {
                    free(tls->client_session);
                    tls->client_session = NULL;
                }
                /* Allocate memory for the session ticket */
                tls->client_session = calloc(1, session_ticket_len);
                if (tls->client_session == NULL) {
                    ESP_LOGE(TAG, "Failed to allocate memory for client session ctx");
                    free(tls13_saved_client_session);
                    tls13_saved_client_session = NULL;
                    return ESP_ERR_NO_MEM;
                }
                ret = mbedtls_ssl_session_save(&tls13_saved_client_session->saved_session, (unsigned char *)tls->client_session, session_ticket_len, &session_ticket_len);
                if (ret != 0) {
                    ESP_LOGE(TAG, "Error in saving the client ssl session");
                    mbedtls_print_error_msg(ret);
                    free(tls->client_session);
                    tls->client_session = NULL;
                    free(tls13_saved_client_session);
                    tls13_saved_client_session = NULL;
                    return ESP_ERR_MBEDTLS_SSL_HANDSHAKE_FAILED;
                }

                ESP_LOGD(TAG, "Session ticket saved in the client session context");
                tls->client_session_len = session_ticket_len;
                mbedtls_ssl_session_free(&tls13_saved_client_session->saved_session);
                free(tls13_saved_client_session);
                tls13_saved_client_session = NULL;
            }
#endif // CONFIG_ESP_TLS_CLIENT_SESSION_TICKETS
            /* After handling the session ticket, we need to attempt to read again
             * to either get application data or process another ticket */
            ret = mbedtls_ssl_read(&tls->ssl, (unsigned char *)data, datalen);
        }
    }
#endif // CONFIG_MBEDTLS_SSL_PROTO_TLS1_3
    if (ret < 0) {
        if (ret == MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY) {
            return 0;
        }
        if (ret != ESP_TLS_ERR_SSL_WANT_READ  && ret != ESP_TLS_ERR_SSL_WANT_WRITE) {
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, ESP_ERR_MBEDTLS_SSL_READ_FAILED);
            ESP_LOGE(TAG, "read error :-0x%04"NEWLIB_NANO_SSIZE_T_COMPAT_FORMAT, -ret);
            mbedtls_print_error_msg(ret);
        }
    }
    return ret;
}


#undef mbedtls_ssl_read

static unsigned cases;
static void test_partial_fatal(unsigned initial,bool cached,int tls_error) {
    struct fake_client c;response_t r;esp_http_buffer_t b;setup(&c,&r,&b);
    stream_http_reader_t reader={0};char output[128]={0},cache[64];memset(cache,0x4b,sizeof(cache));
    if(cached) {b.raw_len=(int)initial;b.raw_data=cache;}
    else if(initial)c.steps[0]=(step_t){.bytes=(int)initial,.tls_error=0};
    c.steps[!cached && initial ? 1:0]=(step_t){.bytes=ERR_TCP_TRANSPORT_CONNECTION_FAILED,.tls_error=tls_error};
    int result=stream_http_read(&reader,&c,output,sizeof(output));
    assert(result==(initial?(int)initial:ESP_FAIL));assert(reader.failed && c.closes==1);
    for(unsigned i=0;i<initial;++i)assert(output[i]==0x4b);
    unsigned calls=c.calls,queries=c.error_queries;
    for(unsigned i=0;i<3;++i)assert(stream_http_read(&reader,&c,output,sizeof(output))==ESP_FAIL);
    assert(c.calls==calls && c.error_queries==queries);++cases;
}
static void test_retry(int temporary,unsigned initial) {
    struct fake_client c;response_t r;esp_http_buffer_t b;setup(&c,&r,&b);
    stream_http_reader_t reader={0};char output[128];
    if(initial)c.steps[0]=(step_t){.bytes=(int)initial,.tls_error=0};
    c.steps[initial?1:0]=(step_t){.bytes=ERR_TCP_TRANSPORT_CONNECTION_TIMEOUT,.tls_error=temporary};
    c.steps[initial?2:1]=(step_t){.bytes=128,.tls_error=0};
    assert(stream_http_read(&reader,&c,output,sizeof(output))==(initial?(int)initial:-ESP_ERR_HTTP_EAGAIN));
    assert(!reader.failed && !c.closes);
    assert(stream_http_read(&reader,&c,output,sizeof(output))==128);assert(!reader.failed && !c.closes);++cases;
}
static void test_framing(const char *headers,const char *wire,const char *expected,
                         bool complete,unsigned fragment,int transport_error,int tls_error) {
    struct fake_client c;response_t r;esp_http_buffer_t b;setup_headers(&c,&r,&b,headers);
    stream_http_reader_t reader={0};char output[128],all[256]={0};size_t total=0;
    unsigned count=0;
    for(size_t at=0;at<strlen(wire);) {
        size_t size=strlen(wire)-at;if(size>fragment)size=fragment;
        c.steps[count++]=(step_t){.bytes=(int)size,.data=wire+at};at+=size;
    }
    // FIN/error may follow partial valid bytes. Repeat it only if the SDK
    // returns those bytes before it surfaces the incomplete body.
    for(unsigned i=0;i<3;++i)c.steps[count++]=(step_t){.bytes=transport_error,.tls_error=tls_error};
    int result=0;
    for(unsigned call=0;call<8;++call) {
        result=stream_http_read(&reader,&c,output,sizeof(output));
        if(result<=0)break;
        assert(total+(size_t)result<sizeof(all));memcpy(all+total,output,(size_t)result);total+=(size_t)result;
    }
    assert(total==strlen(expected) && !memcmp(all,expected,total));
    assert(complete ? result==0 && !reader.failed : result==ESP_FAIL && reader.failed);
    unsigned calls=c.calls;
    if(reader.failed)assert(stream_http_read(&reader,&c,output,sizeof(output))==ESP_FAIL && c.calls==calls);
    ++cases;
}
static void test_tls_adapter(void) {
    const int results[]={MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY,0,MBEDTLS_ERR_SSL_ALLOC_FAILED,
        MBEDTLS_ERR_SSL_INVALID_MAC,ESP_TLS_ERR_SSL_TIMEOUT,ESP_TLS_ERR_SSL_WANT_READ,
        ESP_TLS_ERR_SSL_WANT_WRITE};
    for(unsigned i=0;i<sizeof(results)/sizeof(results[0]);++i) {
        test_tls_error_t errors={0};esp_tls_t tls={.ssl=results[i],.error_handle=&errors};char data[8];
        ssize_t result=esp_mbedtls_read(&tls,data,sizeof(data));
        assert(result==(i==0?0:results[i]));
        bool recorded=i>=2 && i<=4;
        assert(errors.esp_error==(recorded?ESP_ERR_MBEDTLS_SSL_READ_FAILED:0));
        assert(errors.tls_code==(recorded?-results[i]:0));++cases;
    }
    puts("TLS_ADAPTER_PASS close_alert_and_raw_EOF_collapse_to_zero; timeout_records_read_failed; WANT_codes_not_recorded");
}
static void test_tls_eof_fix(void) {
    preserve_tls_eof=true;
    const int results[]={MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY,0,MBEDTLS_ERR_SSL_ALLOC_FAILED,
        MBEDTLS_ERR_SSL_INVALID_MAC,ESP_TLS_ERR_SSL_TIMEOUT,ESP_TLS_ERR_SSL_WANT_READ,
        ESP_TLS_ERR_SSL_WANT_WRITE,5};
    for(unsigned i=0;i<sizeof(results)/sizeof(results[0]);++i) {
        test_tls_error_t errors={0};esp_tls_t tls={.ssl=results[i],.error_handle=&errors};char data[8];
        ssize_t expected=results[i]==0?MBEDTLS_ERR_SSL_CONN_EOF:results[i];
        if(results[i]==MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY)expected=0;
        assert(esp_mbedtls_read(&tls,data,sizeof(data))==expected);
        if(results[i]==0)assert(errors.esp_error==ESP_ERR_MBEDTLS_SSL_READ_FAILED && errors.tls_code==-MBEDTLS_ERR_SSL_CONN_EOF);
        if(results[i]==MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY)assert(errors.esp_error==0 && errors.tls_code==0);
        ++cases;
    }
    mbedtls_ssl_context empty=0;unsigned char buffer[1];
    assert(yoradio_mbedtls_ssl_read(&empty,buffer,0)==0);++cases;
    // Drive the actual SDK adapter result into its HTTP transport seam.
    for(unsigned clean=0;clean<2;++clean) {
        test_tls_error_t errors={0};esp_tls_t tls={.ssl=clean?MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY:0,.error_handle=&errors};
        char buffer[8];int transport=(int)esp_mbedtls_read(&tls,buffer,sizeof(buffer));
        if(transport==0)transport=ERR_TCP_TRANSPORT_CONNECTION_CLOSED_BY_FIN;
        const char *closed="HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n";
        test_framing(closed,"ABCDEFGH","ABCDEFGH",clean,1,transport,errors.tls_code);
        // A completed, explicitly framed message must not be rejected merely
        // because the peer would subsequently close without an alert.
        test_framing("HTTP/1.1 200 OK\r\nContent-Length: 8\r\n\r\n","ABCDEFGH","ABCDEFGH",true,1,transport,errors.tls_code);
        test_framing("HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n","8\r\nABCDEFGH\r\n0\r\n\r\n","ABCDEFGH",true,1,transport,errors.tls_code);
    }
    preserve_tls_eof=false;
    puts("TLS_EOF_FIX_PASS raw_EOF_fails_unframed_body; close_notify_completes; explicit_framing_preserved; no_extra_allocation");
}

static void test_chunked_timeout(void) {
    struct fake_client c;response_t r;esp_http_buffer_t b;
    setup_headers(&c,&r,&b,"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n");
    c.steps[0]=(step_t){.bytes=5,.data="3\r\nAB"};
    c.steps[1]=(step_t){.bytes=0,.tls_error=-ESP_TLS_ERR_SSL_TIMEOUT};
    c.steps[2]=(step_t){.bytes=8,.data="C\r\n0\r\n\r\n"};
    stream_http_reader_t reader={0};char output[128];
    assert(stream_http_read(&reader,&c,output,sizeof(output))==2 && !memcmp(output,"AB",2));
    assert(!reader.failed && !c.closes);
    assert(stream_http_read(&reader,&c,output,sizeof(output))==1 && output[0]=='C');
    assert(stream_http_read(&reader,&c,output,sizeof(output))==0 && !reader.failed);++cases;
}

static void test_protocol(void) {
    const char *length="HTTP/1.1 200 OK\r\nContent-Length: 8\r\n\r\n";
    const char *chunked="HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n";
    const char *closed="HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n";
    for(unsigned fragment=1;fragment<=8;fragment*=2) {
        test_framing(length,"ABCDEFGH","ABCDEFGH",true,fragment,-1,0);
        test_framing(length,"ABC","ABC",false,fragment,-1,0);
        test_framing(chunked,"3;foo=bar\r\nABC\r\n5\r\nDEFGH\r\n0\r\nX-Trailer: ok\r\n\r\n","ABCDEFGH",true,fragment,-1,0);
        test_framing(chunked,"3\r\nABC\r\n","ABC",false,fragment,-1,0);
        test_framing(chunked,"3\r\nAB","AB",false,fragment,-1,0);
        test_framing(chunked,"3\r\nABC\r\nZ\r\n","ABC",false,fragment,-1,0);
        test_framing(closed,"ABCDEFGH","ABCDEFGH",true,fragment,-1,0);
        test_framing(closed,"ABCDEFGH","ABCDEFGH",false,fragment,-2,-MBEDTLS_ERR_SSL_INVALID_MAC);
    }
    // Both explicit message boundaries are complete even without a peer FIN:
    // a transport read after the boundary would hit a deliberately fatal step.
    test_framing(length,"ABCDEFGH","ABCDEFGH",true,8,-2,-MBEDTLS_ERR_SSL_INVALID_MAC);
    test_framing(chunked,"8\r\nABCDEFGH\r\n0\r\n\r\n","ABCDEFGH",true,1,-2,-MBEDTLS_ERR_SSL_INVALID_MAC);
    puts("HTTP_FRAMING_PASS content_length chunked extensions trailers truncated malformed fragmented close_delimited");
    puts("UNMODIFIED_SDK_LIMITATION close_notify_and_bare_TLS_EOF_are_indistinguishable_at_HTTP_API");
}

int main(void) {
    // TLS allocation failure and invalid authenticated record: valid preceding
    // bytes survive, but the damaged connection is never read a second time.
    for(unsigned initial=0;initial<=64;initial+=32)
        for(unsigned cached=0;cached<2;++cached)
            for(unsigned error=0;error<2;++error)
                test_partial_fatal(initial,cached,error?-MBEDTLS_ERR_SSL_INVALID_MAC:-MBEDTLS_ERR_SSL_ALLOC_FAILED);
    for(unsigned initial=0;initial<=64;initial+=32) {
        test_retry(0,initial);
        test_retry(-ESP_TLS_ERR_SSL_TIMEOUT,initial);
        test_retry(-ESP_TLS_ERR_SSL_WANT_READ,initial);
        test_retry(-ESP_TLS_ERR_SSL_WANT_WRITE,initial);
    }
    struct fake_client c;response_t r;esp_http_buffer_t b;setup(&c,&r,&b);
    stream_http_reader_t reader={0};char output[128];
    c.steps[0]=(step_t){.bytes=64,.tls_error=0};c.steps[1]=(step_t){.bytes=64,.tls_error=0};
    assert(stream_http_read(&reader,&c,output,sizeof(output))==128 && !reader.failed);++cases;
    r.content_length=r.data_process;
    assert(stream_http_read(&reader,&c,output,sizeof(output))==0 && !reader.failed);++cases;
    // A stale fatal TLS error must not be relabelled as a clean completed EOF.
    c.tls_error=ESP_ERR_MBEDTLS_SSL_READ_FAILED;c.tls_code=-MBEDTLS_ERR_SSL_ALLOC_FAILED;
    assert(stream_http_read(&reader,&c,output,sizeof(output))==ESP_FAIL && reader.failed);++cases;
    // Demonstrate the SDK behavior without the wrapper as a negative control.
    setup(&c,&r,&b);c.steps[0]=(step_t){.bytes=32,.tls_error=0};c.steps[1]=(step_t){.bytes=-2,.tls_error=-MBEDTLS_ERR_SSL_ALLOC_FAILED};
    assert(esp_http_client_read(&c,output,sizeof(output))==32 && c.calls==2);
    c.steps[2]=(step_t){.bytes=-2,.tls_error=-MBEDTLS_ERR_SSL_ALLOC_FAILED};assert(esp_http_client_read(&c,output,sizeof(output))==ESP_FAIL && c.calls==3);++cases;
    test_protocol();
    test_chunked_timeout();
    test_tls_adapter();
    test_tls_eof_fix();
    printf("STREAM_HTTP_READER_PASS cases=%u partial_bytes_preserved=true fatal_retry=false temporary_retry=true sdk_control_retries=true\n",cases);
}
