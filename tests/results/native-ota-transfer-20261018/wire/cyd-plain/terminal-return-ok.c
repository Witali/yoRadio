#define NEGATIVE_OTA_RETURN_OK 1
#include "model.h"
#include "crypto.inc"
#include "native_httpd_headers.h"
#include "web_ota.h"
#include "web_reboot.h"
#include "reboot.inc"
#include "sdk-ws.inc"
#include "platform-declarations.h"
#define httpd_req_recv sdk_req_recv
#include "sdk-txrx.inc"
#undef httpd_req_recv
int httpd_req_recv(httpd_req_t *request,char *data,size_t size) {if(request_deletes&&!workspace)++purge_receives;return sdk_req_recv(request,data,size);}
#define malloc response_malloc
#include "sdk-response.inc"
#undef malloc
#define httpd_req_delete sdk_req_delete
#include "sdk-parse.inc"
#undef httpd_req_delete
esp_err_t httpd_req_delete(struct httpd_data *hd) {++request_deletes;return sdk_req_delete(hd);}
#include "sdk-sess.inc"
#include "sdk-uri.inc"
#include "native_ota_sink.c"
#include "native_ota_form.c"
#define calloc workspace_calloc
#define free workspace_free
#define native_web_transport_prepare_close observed_prepare_close
#include "terminal-return-ok.inc"
#undef native_web_transport_prepare_close
#undef free
#undef calloc
#include "target.inc"
#include "platform.c"
#include "test.c"
