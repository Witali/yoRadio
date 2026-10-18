#define NEGATIVE_TIME_RETURN_OK 1
#define INTEGRATION_TLS 1
#include "model.h"
#include "psa/crypto.h"
#include "mbedtls/base64.h"
#include "native_httpd_headers.h"
#include "time_service.h"
#include "web_time.h"
#include "platform.c"
#include "sdk-ws.inc"
#define httpd_req_recv sdk_req_recv
#include "sdk-txrx.inc"
#undef httpd_req_recv
int httpd_req_recv(httpd_req_t *r,char *data,size_t n) {int count=sdk_req_recv(r,data,n);if(in_purge){++purge_calls;if(count>0)purge_positive_bytes+=(unsigned)count;}return count;}
#include "sdk-response.inc"
#include "sdk-default-io.inc"
#define httpd_req_delete sdk_req_delete
#include "sdk-parse.inc"
#undef httpd_req_delete
esp_err_t httpd_req_delete(struct httpd_data *hd) {++request_deletes;in_purge=true;esp_err_t result=sdk_req_delete(hd);in_purge=false;return result;}
#include "sdk-query.inc"
#include "sdk-sess.inc"
#include "sdk-uri.inc"
#include "time_settings.c"
#define native_web_transport_prepare_close observed_prepare_close
#include "web-time-return-ok.inc"
#undef native_web_transport_prepare_close
#include "test.c"
